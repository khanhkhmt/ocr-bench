"""Chữ viết của một từ / dòng (Ả Rập, Hebrew, Latin, chữ số) và các khoá so sánh dùng cho bỏ phiếu giữa nhiều model.

Ba khoá, từ chặt tới lỏng:
- `vote_key`  : lõi chữ (bỏ dấu câu hai đầu, bỏ tashkeel, NFKC) + chữ số Ả Rập-Ấn → ASCII. Hai model "đọc giống nhau"
                khi trùng khoá này. Chữ cái KHÔNG bị gộp (أ ≠ ا, ة ≠ ه): giữ nguyên văn là ưu tiên của tài liệu pháp lý.
- `rasm_key`  : khung chữ bỏ dấu chấm / hamza (ب ت ث ن ي → ٮ, ج ح خ → ح, ر ز → ر, ع غ → ع, ...). Hai cách đọc cùng
                khung nhưng khác dấu chấm = đúng loại nhầm của chữ viết tay (ت/ث, ب/ي, غ/ع, ز/ر): mắt thấy cùng một nét,
                chỉ dấu chấm (mờ, thiếu, nhoè) quyết định.
- `digits_of` : dãy chữ số (đã đổi sang ASCII) — số, ngày, số tiền phải khớp TỪNG CHỮ SỐ giữa các model.
"""

from __future__ import annotations

import re
import unicodedata

from postcorrect.text import split_affixes, strip_marks

_AR = re.compile("[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
_HE = re.compile("[֐-׿יִ-ﭏ]")
_LAT = re.compile("[A-Za-zÀ-ɏ]")
_DIG = re.compile("[0-9٠-٩۰-۹]")
_AR_DIGITS = re.compile("[٠-٩۰-۹]")
# tashkeel (fatha … sukun, tanwin, shadda) + alef nhỏ: dấu model hay TỰ SINH ra trên chữ viết tay vốn không có
_HARAKAT = re.compile("[ً-ْٰ]")
_DIGIT_MAP = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "0123456789" * 2)

# Khung chữ: mỗi nhóm = các chữ chỉ khác nhau ở dấu chấm / hamza (dạng giữa từ trong chữ viết tay).
_RASM_GROUPS = {
    "ٮ": "بتثنيىئ",
    "ح": "جحخ",
    "د": "دذ",
    "ر": "رز",
    "س": "سش",
    "ص": "صض",
    "ط": "طظ",
    "ع": "عغ",
    "ف": "فق",
    "ه": "هة",
    "ا": "اأإآٱ",
    "و": "وؤ",
}
_RASM_MAP = {c: k for k, cs in _RASM_GROUPS.items() for c in cs}


def char_script(c: str) -> str:
    if unicodedata.category(c)[0] in "PSZC" or _HARAKAT.match(c):  # dấu câu Ả Rập (، ؛ ؟), ký hiệu, tashkeel
        return "other"
    if _AR.match(c):
        return "digit" if _AR_DIGITS.match(c) else "ar"
    if _HE.match(c):
        return "he"
    if _LAT.match(c):
        return "lat"
    if c.isdigit():
        return "digit"
    return "other"


def script_profile(text: str) -> dict[str, int]:
    prof = {"ar": 0, "he": 0, "lat": 0, "digit": 0}
    for c in text:
        s = char_script(c)
        if s in prof:
            prof[s] += 1
    return prof


def dominant_script(text: str, min_share: float = 0.8) -> str:
    """"ar" | "he" | "lat" | "digit" | "mixed" | "none" — theo số chữ cái (chữ số chỉ thắng khi không có chữ cái)."""
    p = script_profile(text)
    letters = p["ar"] + p["he"] + p["lat"]
    if not letters:
        return "digit" if p["digit"] else "none"
    best = max(("ar", "he", "lat"), key=lambda s: p[s])
    return best if p[best] / letters >= min_share else "mixed"


def core(word: str) -> str:
    return strip_marks(unicodedata.normalize("NFKC", split_affixes(word)[1]))


def vote_key(word: str) -> str:
    return core(word).translate(_DIGIT_MAP)


def rasm_key(word: str) -> str:
    return "".join(_RASM_MAP.get(c, c) for c in vote_key(word))


def digits_of(word: str) -> str:
    return "".join(c for c in word.translate(_DIGIT_MAP) if c.isdigit())


def has_digit(word: str) -> bool:
    return bool(_DIG.search(word))


def has_latin(word: str) -> bool:
    return bool(_LAT.search(word))


def has_harakat(word: str) -> bool:
    return bool(_HARAKAT.search(word))


def strip_harakat(word: str) -> str:
    return _HARAKAT.sub("", word)
