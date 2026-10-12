"""Tách từ và chuẩn hoá nhẹ cho tiếng Ả Rập — dùng chung cho chunker, diff, chốt chặn, đánh giá.

"Từ" = chuỗi không có khoảng trắng (dấu câu dính liền thuộc về từ). Chỉ số từ luôn tính trên danh sách này, nên
`words_with_spans(text)` là nguồn sự thật duy nhất cho mọi chỉ số trong JSON kết quả.
"""

from __future__ import annotations

import re
import unicodedata

# Loại khối dots có chữ để sửa. Bảng / công thức / hình / đầu-chân trang KHÔNG đưa cho LLM (số liệu, mã, rác Latin).
TEXT_CATS = {"Text", "Title", "Section-header", "List-item", "Caption", "Footnote"}
_WORD = re.compile(r"\S+")
# tashkeel + dấu Quran nhỏ + chữ alef nhỏ + tatweel (khớp ocrbench.normalize, viết bằng mã để khỏi lẫn ký tự vô hình)
_MARKS = re.compile("[ؐ-ًؚ-ٰٟۖ-ۜ۟-۪ۨ-ۭـ]")
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹٫٬", "0123456789" * 2 + ".,")
_LATIN = re.compile(r"[A-Za-z]")
_HAS_DIGIT = re.compile(r"[0-9٠-٩۰-۹]")
_EXTRA_PUNCT = set("،؛؟٪«»“”‘’…")


def words_with_spans(text: str) -> list[tuple[str, int, int]]:
    return [(m.group(), m.start(), m.end()) for m in _WORD.finditer(text)]


def split_words(text: str) -> list[str]:
    return [w for w, _, _ in words_with_spans(text)]


def strip_marks(s: str) -> str:
    return _MARKS.sub("", s)


def _is_punct(c: str) -> bool:
    return c in _EXTRA_PUNCT or unicodedata.category(c).startswith("P")


def split_affixes(word: str) -> tuple[str, str, str]:
    """(dấu câu đầu, lõi, dấu câu cuối). Từ chỉ toàn dấu câu → ("", "", từ)."""
    i, j = 0, len(word)
    while i < j and _is_punct(word[i]):
        i += 1
    while j > i and _is_punct(word[j - 1]):
        j -= 1
    return word[:i], word[i:j], word[j:]


def core_of(word: str) -> str:
    """Lõi chữ của từ: bỏ dấu câu hai đầu, bỏ tashkeel / tatweel, NFKC."""
    return strip_marks(unicodedata.normalize("NFKC", split_affixes(word)[1]))


def norm_word(word: str) -> str:
    """Dạng so sánh: lõi đã chuẩn hoá + chữ số Ả Rập-Ấn → ASCII. Chỉ để SO SÁNH, không dùng để ghi kết quả."""
    return core_of(word).translate(_DIGITS)


def has_digit(s: str) -> bool:
    return bool(_HAS_DIGIT.search(s))


def has_latin(s: str) -> bool:
    return bool(_LATIN.search(s))


def is_protected(word: str, min_core_len: int = 2) -> bool:
    """Từ KHÔNG BAO GIỜ được sửa: có chữ số (số, ngày, số căn cước), có chữ Latin / địa chỉ, chỉ là dấu câu, hoặc lõi
    quá ngắn (một chữ cái như "و" — sửa chữ đơn là đoán mò)."""
    core = core_of(word)
    if not core:
        return True
    if has_digit(word) or has_latin(word) or "@" in word or "://" in word:
        return True
    return len(core) < min_core_len
