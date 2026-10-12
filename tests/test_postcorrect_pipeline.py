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
    r = correct_pages([page()], be, Settings(strategy="C", flag_frac=0.5, flag_min_nll=3.0))[0]
    assert [f["word"] for f in r["flags"]] == ["المحتزم"]
    assert [e["to"] for e in r["edits"]] == ["المحترم"]
    assert {x["reason"] for x in r["rejected"]} <= {"outside_flag", "protected"}
    # không có từ nghi lỗi nào → không gọi LLM
    be2 = DummyBackend(fixes=FIX, suspicious=set())
    r2 = correct_pages([page()], be2, Settings(strategy="C"))[0]
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
