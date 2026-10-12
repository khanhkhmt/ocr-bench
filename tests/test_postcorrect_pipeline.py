"""Test pipeline postcorrect bằng backend giả (không GPU)."""

from postcorrect.backend import DummyBackend
from postcorrect.pipeline import Settings, correct_pages, page_text_from_cells

TEXT = "الى الاخ العزيز جبيلي المحتزم اني بخير والحمد لله 24725"
FIX = {"المحتزم": "المحترم", "24725": "24726", "اني": "إنني"}


def page(text=TEXT):
    cells = [{"category": "Page-header", "text": "رأس", "bbox": [0, 0, 1, 1]},
             {"category": "Section-header", "text": "## عنوان الرسالة", "bbox": [0, 0, 1, 1]},
             {"category": "Text", "text": text, "bbox": [0, 0, 1, 1]},
             {"category": "Table", "text": "<table></table>", "bbox": [0, 0, 1, 1]},
             {"category": "Picture", "text": "", "bbox": [0, 0, 1, 1]}]
    return page_text_from_cells("p1", cells)


def test_page_text_from_cells_filters_and_maps_blocks():
    p = page()
    assert p.text == "عنوان الرسالة\n" + TEXT
    assert [b["category"] for b in p.blocks] == ["Section-header", "Text"]
    assert p.blocks[0]["first_word"] == 0 and p.blocks[0]["n_words"] == 2
    assert p.blocks[1]["first_word"] == 2 and p.blocks[1]["n_words"] == len(TEXT.split())


def test_strategy_a_accepts_small_fix_rejects_protected_and_far():
    be = DummyBackend(fixes=FIX)
    r = correct_pages([page()], be, Settings(strategy="A"))[0]
    assert [(e["from"], e["to"]) for e in r["edits"]] == [("المحتزم", "المحترم")]
    assert {x["reason"] for x in r["rejected"]} == {"protected", "too_far"}
    assert r["corrected"] == r["original"].replace("المحتزم", "المحترم")
    assert r["edits"][0]["block"] == 2  # khối Text trong danh sách cells gốc


def test_strategy_b_flags_and_edits():
    be = DummyBackend(fixes=FIX)
    r = correct_pages([page()], be, Settings(strategy="B"))[0]
    assert {f["word"] for f in r["flags"]} == {"المحتزم", "24725", "اني"}
    assert [e["to"] for e in r["edits"]] == ["المحترم"]


def test_strategy_c_only_touches_flagged_words_and_skips_unflagged_chunks():
    be = DummyBackend(fixes=FIX, suspicious={"المحتزم"})
    r = correct_pages([page()], be, Settings(strategy="C", flag_signal="nll_max", flag_frac=0.5, flag_min=3.0))[0]
    assert [f["word"] for f in r["flags"]] == ["المحتزم"]
    assert [e["to"] for e in r["edits"]] == ["المحترم"]
    assert {x["reason"] for x in r["rejected"]} <= {"outside_flag", "protected"}
    # không có từ nghi lỗi nào → không gọi LLM
    be2 = DummyBackend(fixes=FIX, suspicious=set())
    r2 = correct_pages([page()], be2, Settings(strategy="C", flag_signal="nll_max"))[0]
    assert be2.calls == [] and r2["edits"] == [] and r2["chunks"][0]["status"] == "no_flags"
    assert r2["corrected"] == r2["original"]


def test_chunk_level_rejection_when_output_drifts():
    class Drift(DummyBackend):
        def generate(self, prompts, max_new):
            return ["<output>" + "كلمة " * 80 + "</output>" for _ in prompts]
    r = correct_pages([page()], Drift(), Settings(strategy="A"))[0]
    assert r["edits"] == [] and r["chunks"][0]["chunk_reason"] == "drift"
    assert r["corrected"] == r["original"]


def test_many_pages_one_batch_keeps_pages_separate():
    be = DummyBackend(fixes={"المحتزم": "المحترم"})
    pages = [page(), page("جملة ثانية المحتزم فقط")]
    rs = correct_pages(pages, be, Settings(strategy="A"))
    assert len(be.calls) == 2  # mỗi trang một chunk, sinh trong cùng một lượt
    assert all(r["corrected"].count("المحترم") == 1 for r in rs)


def test_strategy_c_with_dots_signal_flags_hesitant_word():
    from types import SimpleNamespace

    p = page()
    words = p.text.split()
    p.dots = [SimpleNamespace(lp_min=-3.0 if w == "المحتزم" else -0.05) for w in words]
    be = DummyBackend(fixes=FIX, suspicious={"اني"})  # NLL chỉ nghi "اني", nhưng tín hiệu được chọn là dots
    r = correct_pages([p], be, Settings(strategy="C", flag_signal="dots_lp", flag_frac=0.2, flag_min=0.5))[0]
    assert [f["word"] for f in r["flags"]] == ["المحتزم"]
    assert [e["to"] for e in r["edits"]] == ["المحترم"]
    # combo: trung bình hạng của hai tín hiệu; từ nào cũng có cả hai
    r2 = correct_pages([p], be, Settings(strategy="C", flag_signal="dots_lp+nll_max", flag_frac=0.2))[0]
    assert {f["word"] for f in r2["flags"]} <= {"المحتزم", "اني"} and r2["flags"]
    # không có dots → "dots" không đánh dấu gì, không gọi LLM
    p.dots = None
    be2 = DummyBackend(fixes=FIX)
    assert correct_pages([p], be2, Settings(strategy="C", flag_signal="dots_lp"))[0]["flags"] == [] and be2.calls == []


def test_rank_scores_ties_get_average_rank():
    from postcorrect.detect import combine_ranks, rank_scores

    assert rank_scores([1.0, 1.0, 1.0, 5.0]) == [1 / 3, 1 / 3, 1 / 3, 1.0]
    assert rank_scores([None, 2.0, 1.0]) == [None, 1.0, 0.0]
    assert combine_ranks([1.0, 2.0], [None, 3.0])[0] is None


def test_refilter_reapplies_guard_to_saved_raw_output_without_llm():
    from postcorrect.guard import GuardConfig
    from postcorrect.pipeline import refilter_result

    be = DummyBackend(fixes=FIX)
    res = correct_pages([page()], be, Settings(strategy="A"))[0]
    assert [e["to"] for e in res["edits"]] == ["المحترم"] and any(x["reason"] == "too_far" for x in res["rejected"])
    same = refilter_result(res, GuardConfig())
    assert same["edits"] == [{**e, "block": None} for e in res["edits"]] and same["corrected"] == res["corrected"]
    loose = refilter_result(res, GuardConfig(max_char_ratio=0.8))   # "اني" → "إنني" (2 ký tự / 3) nay được nhận
    assert {e["to"] for e in loose["edits"]} == {"المحترم", "إنني"}
    assert "إنني" in loose["corrected"] and loose["settings"]["guard"]["max_char_ratio"] == 0.8
    strict = refilter_result(res, GuardConfig(max_char_edit=0))     # không cho sửa ký tự nào
    assert strict["edits"] == [] and strict["corrected"] == res["original"]
    # chiến lược C: chỉ từ được đánh dấu mới được sửa, kể cả sau refilter
    be2 = DummyBackend(fixes=FIX, suspicious={"المحتزم"})
    rc = correct_pages([page()], be2, Settings(strategy="C", flag_signal="nll_max", flag_frac=0.5))[0]
    assert [e["to"] for e in refilter_result(rc, GuardConfig(max_char_ratio=0.8))["edits"]] == ["المحترم"]


def test_vote_keeps_only_edits_proposed_by_enough_runs():
    from postcorrect.pipeline import vote_results

    p = page()
    r1 = correct_pages([p], DummyBackend(fixes={"المحتزم": "المحترم", "بخير": "بخبر"}), Settings(strategy="A"))[0]
    r2 = correct_pages([p], DummyBackend(fixes={"المحتزم": "المحترم", "الاخ": "الأخ"}), Settings(strategy="A"))[0]
    r3 = correct_pages([p], DummyBackend(fixes={"المحتزم": "المحترم"}), Settings(strategy="A"))[0]
    both = vote_results([r1, r2], min_votes=2)
    assert [e["to"] for e in both["edits"]] == ["المحترم"] and both["edits"][0]["votes"] == 2
    assert both["corrected"] == r1["original"].replace("المحتزم", "المحترم")
    assert len(vote_results([r1, r2, r3], 1)["edits"]) == 3      # hợp: mọi sửa ≥ 1 phiếu
    assert [e["votes"] for e in vote_results([r1, r2, r3], 3)["edits"]] == [3]


def test_flag_signal_names_default_and_aliases():
    import pytest

    from postcorrect.detect import canon_signal

    assert Settings().flag_signal == "nll_sum"
    assert canon_signal("nll") == "nll_max" and canon_signal("dots") == "dots_lp" and canon_signal("combo") == "dots_lp+nll_max"
    with pytest.raises(ValueError):
        canon_signal("khong_co")
    r = correct_pages([page()], DummyBackend(fixes=FIX, suspicious={"المحتزم"}), Settings(strategy="C", flag_frac=0.2))[0]
    assert [f["word"] for f in r["flags"]] == ["المحتزم"]   # mặc định nll_sum, ngưỡng tối thiểu 4,0


def test_prompt_styles_differ_and_share_output_contract():
    from postcorrect.prompts import messages

    for strat in "ABC":
        cons, ass = messages(strat, "نص", style="cons")[0]["content"], messages(strat, "نص", style="assert")[0]["content"]
        assert cons != ass and ("<output>" in cons) == ("<output>" in ass)
    assert "MANY" in messages("A", "نص", style="assert")[0]["content"] and "MANY" not in messages("A", "نص")[0]["content"]
    assert "[[ ]]" in messages("C", "نص", style="assert")[0]["content"]
