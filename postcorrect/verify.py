"""Chiến lược D — "LLM chỉ làm người kiểm chứng": ứng viên từ từ điển, LM chấm NLL trong ngữ cảnh, chốt chặn quyết định.

  1. Từ nghi lỗi = từ NGOÀI từ điển (OOV), không bị bảo vệ.
  2. Ứng viên = các từ trong từ điển cách chữ OCR ≤ max_char_edit ký tự (guard.check_edit lọc trước: bỏ ứng viên chỉ khác quy ước,
     chữ ngoài bộ Ả Rập chuẩn…) — LM KHÔNG được sinh chữ tự do nên không thể bịa ra từ ngoài danh sách.
  3. Với mỗi ứng viên, dựng "cửa sổ" ngữ cảnh (vài từ trước và sau) có ứng viên thay vào; Δ = NLL(cửa sổ gốc) − NLL(cửa sổ ứng viên).
     Δ > 0 = LM thích ứng viên hơn chữ OCR.
  4. Nhận ứng viên tốt nhất nếu Δ ≥ tau VÀ hơn ứng viên thứ hai ≥ margin (tránh chọn bừa giữa các ứng viên ngang nhau).

Mọi điểm số lưu trong kết quả (`dcands` của chunk) nên quét tau / margin sau bằng `refilter` mà không cần GPU.
"""

from __future__ import annotations

from .diff import Edit
from .guard import GuardConfig, check_edit
from .text import is_protected, norm_word, split_affixes


def suspects_of(words: list[str], lex, guard: GuardConfig, max_suspects: int = 40, max_cands: int = 30,
                scores: list[float | None] | None = None) -> list[dict]:
    """[{i, w, cands:[[ứng viên (dạng đã gắn dấu câu của OCR), khoảng cách, tần suất], ...]}] cho các từ OOV có ≥ 1 ứng viên hợp lệ.
    scores (vd. NLL tổng của từ): khi có thì lấy các từ điểm CAO nhất trước (không thiên về đầu chunk) rồi trả lại theo thứ tự vị trí."""
    out = []
    order = sorted(range(len(words)), key=lambda i: -(scores[i] if scores and scores[i] is not None else 0.0)) if scores else range(len(words))
    for i in order:
        w = words[i]
        if is_protected(w, guard.min_core_len) or norm_word(w) in lex.set:
            continue
        pre, _, suf = split_affixes(w)
        cands = []
        for c, d, f in lex.candidates(w, guard.max_char_edit, limit=max_cands * 3):
            form = pre + c + suf
            if check_edit(Edit(i, (w,), (form,)), guard) is None:  # chỉ ứng viên mà chốt chặn sẽ nhận
                cands.append([form, d, f])
            if len(cands) >= max_cands:
                break
        if cands:
            out.append({"i": i, "w": w, "cands": cands})
        if len(out) >= max_suspects:
            break
    return sorted(out, key=lambda x: x["i"])


def window_texts(words: list[str], i: int, forms: list[str], before: int = 8, after: int = 4) -> tuple[str, list[str]]:
    """(cửa sổ gốc, [cửa sổ với từng ứng viên thay vào]) — nối bằng khoảng trắng."""
    lo, hi = max(0, i - before), min(len(words), i + after + 1)
    base = words[lo:hi]
    k = i - lo
    return " ".join(base), [" ".join(base[:k] + [f] + base[k + 1:]) for f in forms]


def score_suspects(backend, words: list[str], suspects: list[dict], before: int = 8, after: int = 4) -> None:
    """Điền Δ vào từng ứng viên (cột thứ 4): Δ = NLL(gốc) − NLL(ứng viên); gom mọi cửa sổ vào MỘT lượt chấm theo batch."""
    texts, owners = [], []
    for si, s in enumerate(suspects):
        base, cs = window_texts(words, s["i"], [c[0] for c in s["cands"]], before, after)
        texts.append(base)
        owners.append((si, None))
        for ci, t in enumerate(cs):
            texts.append(t)
            owners.append((si, ci))
    if not texts:
        return
    totals = backend.nll_totals(texts)
    base_nll = {}
    for (si, ci), v in zip(owners, totals):
        if ci is None:
            base_nll[si] = v
    for (si, ci), v in zip(owners, totals):
        if ci is not None:
            suspects[si]["cands"][ci] = suspects[si]["cands"][ci][:3] + [round(base_nll[si] - v, 3)]


def decide(words: list[str], suspects: list[dict], tau: float, margin: float, guard: GuardConfig):
    """Từ điểm đã chấm → (sửa được nhận, danh sách từ chối kèm lý do). Mỗi từ nghi lỗi nhận tối đa một ứng viên."""
    acc, rej = [], []
    for s in suspects:
        scored = sorted((c for c in s["cands"] if len(c) >= 4), key=lambda c: -c[3])
        if not scored:
            continue
        best = scored[0]
        second = scored[1][3] if len(scored) > 1 else float("-inf")
        e = Edit(s["i"], (s["w"],), (best[0],))
        if best[3] < tau:
            rej.append((e, "lm_not_confident"))
        elif best[3] - second < margin:
            rej.append((e, "lm_ambiguous"))
        else:
            why = check_edit(e, guard)
            (rej.append((e, why)) if why else acc.append(e))
    return acc, rej
