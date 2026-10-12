"""Chia văn bản thành chunk ~700 ký tự, ưu tiên ranh giới tự nhiên, GIỮ NGUYÊN THỨ TỰ và không cắt giữa từ.

Viết lại thay vì chép `chunk_text_by_sentences` của repo tham chiếu (Ali-Daher1/arabic-ocr-correction-benchmark), vì bản đó
(đã chạy thử) có hai lỗi: (1) câu dài đứng sau câu ngắn → chunk bị đảo thứ tự; (2) ký tự "\\n" trong tập dấu tách bị bỏ qua
→ các dòng dính liền không còn khoảng trắng ("السطر الأولالسطر الثاني").

Bất biến (có test): mọi chunk là text[start:end] của văn bản gốc (kể cả xuống dòng bên trong), các chunk theo đúng thứ
tự và không chồng nhau, ghép lại đủ mọi từ; chunk ≤ max_chars trừ khi chỉ có một từ dài hơn thế.
"""

from __future__ import annotations

from dataclasses import dataclass

from .text import words_with_spans

_SENT_END = set(".؟!؛?")
_SOFT = set("،,:")


@dataclass(frozen=True)
class Chunk:
    start: int       # chỉ số ký tự trong văn bản gốc
    end: int
    text: str
    first_word: int  # chỉ số từ đầu tiên (theo words_with_spans của văn bản gốc)
    n_words: int


def _boundary_score(text: str, w_end: int, next_start: int, word: str) -> int:
    """Độ "tự nhiên" của chỗ ngắt giữa hai từ liền nhau: xuống dòng 3 > hết câu 2 > dấu phẩy / hai chấm 1 > khác 0."""
    if "\n" in text[w_end:next_start]:
        return 3
    if word and word[-1] in _SENT_END:
        return 2
    if word and word[-1] in _SOFT:
        return 1
    return 0


def chunk_text(text: str, max_chars: int = 700, min_frac: float = 0.5) -> list[Chunk]:
    ws = words_with_spans(text)
    chunks: list[Chunk] = []
    i = 0
    while i < len(ws):
        start = ws[i][1]
        j = i  # chunk = ws[i..j], j là từ cuối xa nhất còn vừa max_chars (ít nhất một từ)
        while j + 1 < len(ws) and ws[j + 1][2] - start <= max_chars:
            j += 1
        if j + 1 < len(ws):  # chưa hết văn bản → chọn chỗ ngắt tốt nhất trong nửa sau của cửa sổ
            cands = [k for k in range(i, j + 1) if ws[k][2] - start >= min_frac * max_chars] or [j]
            best = max(cands, key=lambda k: (_boundary_score(text, ws[k][2], ws[k + 1][1], ws[k][0]), ws[k][2]))
            j = best
        chunks.append(Chunk(start, ws[j][2], text[start:ws[j][2]], i, j - i + 1))
        i = j + 1
    return chunks
