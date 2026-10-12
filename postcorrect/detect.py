"""Khoanh từ nghi lỗi TRƯỚC khi nhờ LLM sinh chữ (detect-then-correct).

Tín hiệu hiện có: NLL của LM (một lượt forward, ~0.4–0.5 s/chunk 600 ký tự trên T4). Bài đo nhỏ trên văn bản tổng hợp:
khoanh 20% số từ có NLL token lớn nhất bắt được 87–95% từ lỗi chèn giả (AUROC 0.93–0.95). Chưa biết với chữ viết tay thật —
đó là việc của bước đánh giá. (Tín hiệu thứ hai, độ tin cậy token của dots, được ghi lúc OCR; xem dots_logprob.py.)
"""

from __future__ import annotations

from .backend import WordNLL
from .text import is_protected


def select_flags(words: list[str], nll: list[WordNLL], frac: float, min_nll: float,
                 min_core_len: int = 2) -> dict[int, float]:
    """Chỉ số từ nghi lỗi → điểm (max NLL token). Bỏ từ được bảo vệ (số, Latin, chữ đơn). Lấy top `frac` số từ
    còn lại theo điểm, và chỉ nhận từ có điểm ≥ min_nll (văn bản dễ đoán thì không đánh dấu gì)."""
    cand = [(nll[i].max, i) for i, w in enumerate(words) if not is_protected(w, min_core_len) and nll[i].n_tok > 0]
    if not cand:
        return {}
    k = max(1, round(frac * len(cand)))
    top = sorted(cand, reverse=True)[:k]
    return {i: s for s, i in top if s >= min_nll}
