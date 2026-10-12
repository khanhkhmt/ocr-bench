"""Đánh giá trên trang có đáp án: không chỉ CER/WER, mà quan trọng hơn — cơ chế [؟] có BẮT ĐÚNG chỗ sai không.

Với tài liệu pháp lý, câu hỏi thực tế là "phần KHÔNG bị đánh dấu có đáng tin không":
    residual_error  = số từ sai trong các từ in KHÔNG kèm [؟] / số từ không kèm [؟]     (càng thấp càng tốt)
    flag_precision  = số từ bị đánh dấu thật sự sai / số từ bị đánh dấu                 (thấp = người duyệt mất công)
    flag_recall     = số từ sai đã bị đánh dấu / tổng số từ sai                         (cao = ít lỗi lọt qua)
tính riêng cho từ quan trọng (tên, số, ngày...). CER/WER chấm trên bản nguyên văn đã bỏ ký hiệu [؟] (từ không đọc được
tính là bỏ trống), chuẩn hoá strict của postcorrect (không gộp أ/إ/ا). ECE: độ lệch giữa độ tin cậy và tỉ lệ đúng thật.
"""

from __future__ import annotations

from postcorrect.evaluate import STRICT, align, text_cer_wer
from postcorrect.text import split_words

from .doc import ILLEGIBLE, READ, Page
from .fuse import FEATURES


def hyp_words(page: Page) -> list:
    """(từ in ra, Word) theo thứ tự — chỉ vùng chữ thường; từ không đọc được = chuỗi rỗng."""
    out = []
    for ln in page.lines:
        if ln.region != "Text":
            continue
        for w in ln.words:
            for piece in (w.text.split() if w.status != ILLEGIBLE else [""]):
                out.append((piece, w))
    return out


def word_labels(page: Page, gt: str) -> list[tuple[object, bool]]:
    """[(Word, đúng?)] — một Word nhiều mảnh (ô gộp) chỉ đúng khi mọi mảnh đúng."""
    hw = hyp_words(page)
    al = align([t if t else "∅" for t, _ in hw], split_words(gt))
    ok: dict[str, bool] = {}
    order = []
    for (t, w), lab in zip(hw, al.label):
        if w.id not in ok:
            ok[w.id] = True
            order.append(w)
        ok[w.id] = ok[w.id] and lab == "ok" and bool(t)
    return [(w, ok[w.id]) for w in order]


def evaluate_page(page: Page, gt: str) -> dict:
    hyp = " ".join(t for t, _ in hyp_words(page) if t)
    cw = text_cer_wer(gt, hyp, STRICT)
    labels = word_labels(page, gt)
    row = {"id": page.id, **cw}
    for name, sel in (("all", lambda w: True), ("critical", lambda w: w.critical)):
        L = [(w, c) for w, c in labels if sel(w)]
        flagged = [(w, c) for w, c in L if w.status != READ]
        clean = [(w, c) for w, c in L if w.status == READ]
        wrong = [(w, c) for w, c in L if not c]
        row[name] = {"words": len(L), "wrong": len(wrong), "flagged": len(flagged),
                     "flagged_wrong": sum(1 for _, c in flagged if not c),
                     "clean": len(clean), "clean_wrong": sum(1 for _, c in clean if not c)}
    row["calib"] = [(round(w.confidence, 4), int(c)) for w, c in labels]
    return row


def summarize(rows: list[dict]) -> dict:
    out = {"pages": len(rows)}
    ce = sum(r["char_edits"] for r in rows)
    rc = sum(r["ref_chars"] for r in rows)
    we = sum(r["word_edits"] for r in rows)
    rw = sum(r["ref_words"] for r in rows)
    out["cer_micro"] = ce / rc if rc else 0.0
    out["wer_micro"] = we / rw if rw else 0.0
    for name in ("all", "critical"):
        t = {k: sum(r[name][k] for r in rows) for k in rows[0][name]} if rows else {}
        out[name] = {**t,
                     "flag_rate": t["flagged"] / t["words"] if t.get("words") else 0.0,
                     "flag_precision": t["flagged_wrong"] / t["flagged"] if t.get("flagged") else 0.0,
                     "flag_recall": t["flagged_wrong"] / t["wrong"] if t.get("wrong") else 1.0,
                     "residual_error": t["clean_wrong"] / t["clean"] if t.get("clean") else 0.0}
    out["ece"] = ece([x for r in rows for x in r["calib"]])
    return out


def ece(pairs: list[tuple[float, int]], bins: int = 10) -> float:
    if not pairs:
        return 0.0
    tot = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [(p, y) for p, y in pairs if lo <= p < hi or (b == bins - 1 and p == 1.0)]
        if sel:
            conf = sum(p for p, _ in sel) / len(sel)
            acc = sum(y for _, y in sel) / len(sel)
            tot += len(sel) / len(pairs) * abs(conf - acc)
    return tot


def training_rows(page: Page, gt: str) -> list[dict]:
    """Đặc trưng + nhãn đúng/sai của từng từ — đầu vào cho calibrate.py."""
    return [{**{k: float(w.features.get(k, 0.0)) for k in FEATURES}, "y": int(c)} for w, c in word_labels(page, gt)]
