"""Test các chỉ số đánh giá postcorrect trên ví dụ nhỏ có đáp án biết trước."""

from postcorrect.diff import Edit
from postcorrect.evaluate import (align, bootstrap_ci, by_noise_bins, norm_w, page_metrics, score_edits, score_flags,
                                  summarize)

GT = "الى الاخ العزيز جبيلي المحترم اني بخير"
OCR = "الى الاخ العزيز جبيلي المحتزم اني بخبر"


def E(i, a, b):
    return Edit(i, tuple(a.split()), tuple(b.split()))


def test_norm_w_ignores_punct_marks_and_digits():
    assert norm_w("«المُحْتَرَم»،") == "المحترم"
    assert norm_w("١٩٦٠") == "1960"
    assert norm_w("أحمد") != norm_w("احمد") and norm_w("أحمد", True) == norm_w("احمد", True)


def test_align_labels():
    al = align(OCR.split(), GT.split())
    assert [l for l in al.label] == ["ok", "ok", "ok", "ok", "sub", "ok", "sub"]


def test_fixed_harm_worse_improved():
    src, gt = OCR.split(), GT.split()
    r = score_edits(src, gt, [E(4, "المحتزم", "المحترم"), E(6, "بخبر", "بخير")])
    assert r["fixed"] == 2 and r["harm"] == 0 and r["net_char_gain"] == 2 and r["fixed_words"] == 2
    r = score_edits(src, gt, [E(1, "الاخ", "الأخ")])          # từ vốn đúng bị đổi → harm
    assert r["harm"] == 1 and r["harm_words"] == 1 and r["net_char_gain"] < 0
    r = score_edits(src, gt, [E(4, "المحتزم", "المحتنم")])     # từ sai bị đổi thành sai khác (cùng khoảng cách) → neutral
    assert r["neutral"] == 1
    r = score_edits(src, gt, [E(4, "المحتزم", "المحبنم")])     # sai hơn
    assert r["worse"] == 1
    r = score_edits(src, gt, [E(4, "المحتزم", "المحترمة")])    # gần hơn nhưng chưa đúng? (khoảng cách 1 → 1: neutral)
    assert r["fixed"] == 0


def test_split_merge_edit_scored_against_aligned_block():
    gt = "وصلنا بعد الظهر".split()
    src = "وصلنا بعدالظهر".split()
    assert score_edits(src, gt, [E(1, "بعدالظهر", "بعد الظهر")])["fixed"] == 1
    assert score_edits(gt, gt, [E(1, "بعد الظهر", "بعدالظهر")])["harm"] == 1


def test_reach_counts_only_small_distance_substitutions():
    gt = "كتب الولد رسالة طويلة".split()
    src = "كتب الولز رسالة قمقمقمق".split()   # 'الولز' cách 1 ký tự (trong tầm), 'قمقمقمق' quá xa
    r = score_edits(src, gt, [])
    assert r["reach_words"] == 1 and r["err_words"] == 2


def test_flags_precision_recall():
    f = score_flags(OCR.split(), GT.split(), {4, 1})
    assert f == {"flags": 2, "flag_tp": 1, "err_words": 2}


def test_page_metrics_and_summary():
    edits = [{"index": 4, "span": 1, "from": "المحتزم", "to": "المحترم"}]
    corrected = OCR.replace("المحتزم", "المحترم")
    row = page_metrics(GT, OCR, corrected, edits)
    s = summarize([row])
    assert s["cer_after"] < s["cer_before"] and s["wer_after"] < s["wer_before"]
    assert s["precision"] == 1.0 and s["harm_rate"] == 0.0 and s["cer_delta"] < 0
    # không sửa gì → delta = 0, precision = nan
    row0 = page_metrics(GT, OCR, OCR, [])
    s0 = summarize([row0])
    assert s0["cer_delta"] == 0 and s0["precision"] != s0["precision"]


def test_bootstrap_and_bins_run():
    rows = [page_metrics(GT, OCR, OCR.replace("المحتزم", "المحترم"), [{"index": 4, "span": 1, "from": "المحتزم", "to": "المحترم"}])
            for _ in range(8)]
    lo, hi = bootstrap_ci(rows, lambda s: s["cer_delta"], n=50)
    assert lo <= hi < 0
    assert by_noise_bins(rows)
