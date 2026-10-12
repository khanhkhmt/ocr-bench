"""Test từ điển + sinh ứng viên (từ điển nhỏ tự dựng)."""

import json

from postcorrect.lexicon import Lexicon, tokenize_for_lexicon


def make(tmp_path):
    words = [("لبنان", 50), ("لبنانية", 20), ("المفوض", 10), ("الانتخاب", 30), ("يجب", 80), ("حجب", 5)]
    p = tmp_path / "lex.json"
    p.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    return Lexicon(p)


def test_candidates_within_distance_sorted_by_distance_then_frequency(tmp_path):
    lex = make(tmp_path)
    c = lex.candidates("لبان", 2)
    assert c[0][:2] == ("لبنان", 1)                    # thiếu một chữ → ứng viên gần nhất
    assert [w for w, _, _ in lex.candidates("حجب", 1)] == ["يجب"]  # chính từ trong từ điển không tự là ứng viên
    assert lex.candidates("24725", 2) == [] and lex.candidates("و", 2) == []  # từ được bảo vệ
    assert "المفوض" in lex and "مغوض" not in lex


def test_tokenize_for_lexicon_keeps_only_arabic_words():
    assert list(tokenize_for_lexicon("مُحَمَّد ذهب to 2024، المدرسة.")) == ["محمد", "ذهب", "المدرسة"]


def test_strategy_d_picks_lexicon_candidate_by_lm_and_refilter_sweeps_tau(tmp_path):
    from postcorrect.backend import DummyBackend
    from postcorrect.pipeline import PageText, Settings, correct_pages, refilter_result
    from postcorrect.guard import GuardConfig

    words = [("الى", 100), ("الاخ", 90), ("العزيز", 80), ("جبيلي", 5), ("المحترم", 70), ("اني", 60), ("بخير", 50)]
    p = tmp_path / "lex.json"
    p.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    lex = Lexicon(p)
    text = "الى الاخ العزيز جبيلي المحتزم اني بخير 24725"
    be = DummyBackend(suspicious={"المحتزم"})        # LM thấy "المحتزم" lạ (NLL cao), các từ khác bình thường
    res = correct_pages([PageText("p", text, [])], be, Settings(strategy="D"), lexicon=lex)[0]
    assert [(e["from"], e["to"]) for e in res["edits"]] == [("المحتزم", "المحترم")]
    assert res["corrected"] == text.replace("المحتزم", "المحترم")
    sus = res["chunks"][0]["dcands"]
    assert sus and sus[0]["w"] == "المحتزم" and sus[0]["cands"][0][3] > 3          # Δ đã lưu
    # quét ngưỡng không cần GPU: tau quá cao → không nhận; tau thấp → nhận
    assert refilter_result(res, GuardConfig(), d_tau=20.0)["edits"] == []
    assert len(refilter_result(res, GuardConfig(), d_tau=1.0)["edits"]) == 1
    # không có từ điển → báo lỗi rõ ràng
    import pytest

    with pytest.raises(ValueError):
        correct_pages([PageText("p", text, [])], be, Settings(strategy="D"))
