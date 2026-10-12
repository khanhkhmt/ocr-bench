"""Diff mức TỪ giữa văn bản gốc và bản LLM viết lại → danh sách sửa (Edit), và áp dụng ngược lại.

Dùng rapidfuzz Levenshtein.opcodes (căn tối ưu, không "autojunk" như difflib.SequenceMatcher mặc định — với chunk
≥ 200 từ, autojunk coi từ phổ biến là rác và căn lệch). Các khối khác nhau liền kề được gộp thành MỘT sửa.
"""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz.distance import Levenshtein

from .text import words_with_spans


@dataclass(frozen=True)
class Edit:
    index: int                 # chỉ số từ đầu tiên bị thay (theo danh sách từ của văn bản gốc)
    src: tuple[str, ...]       # các từ gốc bị thay (span = len(src))
    dst: tuple[str, ...]       # các từ thay vào (rỗng = xoá từ; src rỗng = chèn từ)

    @property
    def span(self) -> int:
        return len(self.src)

    @property
    def from_(self) -> str:
        return " ".join(self.src)

    @property
    def to(self) -> str:
        return " ".join(self.dst)

    def as_json(self) -> dict:
        return {"index": self.index, "span": self.span, "from": self.from_, "to": self.to}


def diff_words(src: list[str], hyp: list[str]) -> list[Edit]:
    edits: list[Edit] = []
    cur = None  # (i1, i2, j1, j2) của khối đang gộp
    for tag, i1, i2, j1, j2 in Levenshtein.opcodes(src, hyp):
        if tag == "equal":
            if cur:
                edits.append(Edit(cur[0], tuple(src[cur[0]:cur[1]]), tuple(hyp[cur[2]:cur[3]])))
                cur = None
            continue
        cur = (i1, i2, j1, j2) if cur is None else (cur[0], i2, cur[2], j2)
    if cur:
        edits.append(Edit(cur[0], tuple(src[cur[0]:cur[1]]), tuple(hyp[cur[2]:cur[3]])))
    return edits


def explode_equal_blocks(edits: list[Edit]) -> list[Edit]:
    """Khối thay m từ bằng đúng m từ (m > 1) → m sửa 1→1 độc lập, để chốt chặn xét từng từ một."""
    out: list[Edit] = []
    for e in edits:
        if e.span > 1 and len(e.dst) == e.span:
            out += [Edit(e.index + k, (e.src[k],), (e.dst[k],)) for k in range(e.span) if e.src[k] != e.dst[k]]
        else:
            out.append(e)
    return out


def apply_edits_words(words: list[str], edits: list[Edit]) -> list[str]:
    out, pos = [], 0
    for e in sorted(edits, key=lambda e: e.index):
        out += words[pos:e.index] + list(e.dst)
        pos = e.index + e.span
    return out + words[pos:]


def apply_edits_text(text: str, edits: list[Edit]) -> str:
    """Áp sửa vào văn bản gốc, giữ nguyên khoảng trắng / xuống dòng ở mọi chỗ không bị sửa."""
    ws = words_with_spans(text)
    out, pos = [], 0
    for e in sorted(edits, key=lambda e: e.index):
        if e.span:
            a, b = ws[e.index][1], ws[e.index + e.span - 1][2]
        else:  # chèn thuần: đặt trước từ ở e.index
            a = b = ws[e.index][1] if e.index < len(ws) else len(text)
        out.append(text[pos:a])
        out.append(e.to)
        pos = b
    out.append(text[pos:])
    return "".join(out)
