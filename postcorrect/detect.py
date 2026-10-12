"""Khoanh từ nghi lỗi TRƯỚC khi nhờ LLM sinh chữ (detect-then-correct).

Hai tín hiệu, cùng quy ước "điểm CAO = đáng nghi hơn":
  - NLL của LM (một lượt forward, ~0.4–0.5 s/chunk 600 ký tự trên T4): token đắt nhất của từ.
  - độ ngần ngừ của dots (−log-prob thấp nhất của token trong từ), ghi sẵn lúc OCR — tín hiệu duy nhất "nhìn thấy ảnh".
Bài đo nhỏ trên văn bản tổng hợp: khoanh 20% số từ có NLL cao nhất bắt được 87–95% từ lỗi chèn giả. Với chữ viết tay thật phải
đo lại — xem `python -m postcorrect analyze`.
"""

from __future__ import annotations

from .backend import WordNLL
from .text import is_protected


# Tín hiệu khoanh từ nghi lỗi (đo trên dev Muharaf, AUROC tách từ sai-gần-đúng khỏi từ đúng):
#   nll_sum 0,74 · dots_lp 0,745 · nll_max 0,62 (token đắt nhất; trên văn bản tổng hợp thì ngang nhau, trên chữ tay thật thì kém)
SIGNALS = ("nll_sum", "nll_max", "dots_lp", "dots_lp+nll_sum", "dots_lp+nll_max")
DEFAULT_MIN = {"nll_max": 3.0, "nll_sum": 4.0, "dots_lp": 0.5}  # ngưỡng tuyệt đối tối thiểu; tổ hợp hạng không có ngưỡng
_ALIASES = {"nll": "nll_max", "dots": "dots_lp", "combo": "dots_lp+nll_max"}


def canon_signal(name: str) -> str:
    name = _ALIASES.get(name, name)
    if name not in SIGNALS:
        raise ValueError(f"flag_signal phải là một trong {SIGNALS}")
    return name


def nll_scores(nll: list[WordNLL], kind: str = "max") -> list[float | None]:
    return [(w.max if kind == "max" else w.total) if w.n_tok > 0 else None for w in nll]


def rank_scores(scores: list[float | None]) -> list[float | None]:
    """Điểm → hạng phân vị trong chunk (0..1). Điểm BẰNG NHAU nhận hạng trung bình (không để vị trí từ quyết định hạng).
    None giữ nguyên."""
    have = sorted((s, i) for i, s in enumerate(scores) if s is not None)
    out: list[float | None] = [None] * len(scores)
    a = 0
    while a < len(have):
        b = a
        while b + 1 < len(have) and have[b + 1][0] == have[a][0]:
            b += 1
        for k in range(a, b + 1):
            out[have[k][1]] = ((a + b) / 2) / max(1, len(have) - 1)
        a = b + 1
    return out


def combine_ranks(a: list[float | None], b: list[float | None]) -> list[float | None]:
    ra, rb = rank_scores(a), rank_scores(b)
    return [None if x is None or y is None else (x + y) / 2 for x, y in zip(ra, rb)]


def select_flags(words: list[str], scores: list[float | None], frac: float, min_score: float,
                 min_core_len: int = 2) -> dict[int, float]:
    """Chỉ số từ nghi lỗi → điểm. Bỏ từ được bảo vệ (số, Latin, chữ đơn) và từ không có điểm. Lấy top `frac` số từ còn
    lại theo điểm, và chỉ nhận từ có điểm ≥ min_score (văn bản dễ đoán thì không đánh dấu gì)."""
    cand = [(s, i) for i, (w, s) in enumerate(zip(words, scores)) if s is not None and not is_protected(w, min_core_len)]
    if not cand:
        return {}
    k = max(1, round(frac * len(cand)))
    return {i: s for s, i in sorted(cand, key=lambda x: (-x[0], x[1]))[:k] if s >= min_score}
