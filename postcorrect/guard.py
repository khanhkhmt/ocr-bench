"""Chốt chặn cứng quanh LLM: chỉ nhận những sửa NHỎ, CỤC BỘ, trên từ ĐƯỢC PHÉP; còn lại giữ nguyên bản OCR.

Nguyên tắc (sửa sai nguy hiểm hơn bỏ sót): khi nghi ngờ thì KHÔNG sửa. Mọi ngưỡng ở GuardConfig, chỉnh trên tập dev.
Bằng chứng từ bài đo nhỏ trên T4: cùng một prompt, một model bịa nội dung ở chunk bảng hoá đơn (10 từ → 67 từ) và dịch
từ Latin sang Ả Rập; luật "lệch số từ → giữ nguyên chunk" và "không đụng token Latin / số" loại đúng các lỗi đó.
"""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz.distance import Levenshtein

from .diff import Edit, diff_words, explode_equal_blocks
from .text import core_of, has_digit, has_latin, is_protected, split_affixes, strip_marks


# Bộ chữ cái Ả Rập chuẩn: ء…غ (U+0621–063A) và ف…ي (U+0641–064A), cộng alef wasla. LLM đổi chữ Ả Rập sang biến thể chữ Ba Tư /
# Urdu (ہ ی ک ں ے...) là sai với loại tài liệu này (đã thấy: "هنیا" → "ہنیا") → chặn; ngược lại bỏ chữ lạ khỏi từ thì được.
_ARABIC_CORE = {chr(c) for c in range(0x0621, 0x063B)} | {chr(c) for c in range(0x0641, 0x064B)} | {"\u0671"}


def foreign_letters(src: tuple[str, ...], dst: tuple[str, ...]) -> set[str]:
    """Chữ cái ngoài bộ Ả Rập chuẩn xuất hiện ở `dst` mà `src` chưa có."""
    have = {c for w in src for c in core_of(w) if c.isalpha()}
    return {c for w in dst for c in core_of(w) if c.isalpha() and c not in _ARABIC_CORE and c not in have}


# Khác biệt "quy ước" giữa các cách viết: hamza trên alef, alef maqsura / ya, ta marbuta / ha. Phiên âm trung thành có chỗ ghi أن, có
# chỗ ghi ان; sửa kiểu này là tung đồng xu (đo trên dev: đa số "sửa nhầm" của LLM là loại này) → mặc định chặn.
_CONV = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه"})


def diacritic_ratio(words) -> float:
    """Tỉ lệ ký tự là tashkeel. Đáp án thật hiếm khi vượt 15%; dots bịa văn kiểu Qur'an khi không đọc nổi ảnh (đo: 30% trang
    dev có chunk ~40% tashkeel)."""
    text = " ".join(words)
    return 1 - len(strip_marks(text)) / max(1, len(text))


@dataclass
class GuardConfig:
    max_char_edit: int = 2          # sửa 1→1: tối đa số ký tự khác (trên lõi chữ đã bỏ tashkeel)
    max_char_ratio: float = 0.5     # ... và không quá tỉ lệ này so với độ dài từ gốc
    allow_split_merge: bool = True  # 1→2 (tách) và 2→1 (gộp) khi chữ cái gần như giữ nguyên
    max_edit_ratio: float = 0.35    # chunk: tỉ lệ từ bị sửa tối đa, vượt = coi như LLM viết lại → bỏ cả chunk
    max_drift: float = 0.10         # chunk: lệch số từ tối đa (tỉ lệ; luôn cho phép ≥ 2 từ)
    min_core_len: int = 2           # từ có lõi ngắn hơn (vd. "و") không bao giờ bị sửa
    block_convention: bool = True   # chặn sửa chỉ khác quy ước (أ/ا, ى/ي, ة/ه)
    max_diacritic_ratio: float = 0.05  # chunk có tashkeel dày hơn mức này = dots đang bịa → không sửa gì (0 = tắt)


def check_edit(e: Edit, cfg: GuardConfig, allowed: set[int] | None = None) -> str | None:
    """None = nhận; ngược lại trả mã lý do từ chối."""
    if e.span == 0 or not e.dst:
        return "insert_delete"
    if allowed is not None and any(e.index + k not in allowed for k in range(e.span)):
        return "outside_flag"
    if any(is_protected(w, cfg.min_core_len) for w in e.src):
        return "protected"
    if any(has_digit(w) or has_latin(w) for w in e.dst):
        return "introduces_digit_latin"
    if foreign_letters(e.src, e.dst):
        return "foreign_script"
    m, n = e.span, len(e.dst)
    if m == 1 and n == 1:
        a, b = core_of(e.src[0]), core_of(e.dst[0])
        if a == b:
            return "no_change"  # chỉ khác tashkeel / dấu câu
        if cfg.block_convention and a.translate(_CONV) == b.translate(_CONV):
            return "convention_only"
        d = Levenshtein.distance(a, b)
        if d > cfg.max_char_edit or d / max(1, len(a)) > cfg.max_char_ratio:
            return "too_far"
        return None
    if cfg.allow_split_merge and (m, n) in ((1, 2), (2, 1)):
        a, b = strip_marks("".join(e.src)), strip_marks("".join(e.dst))
        return None if Levenshtein.distance(a, b) <= 1 else "too_far"
    return "shape"


def finalize(e: Edit) -> Edit:
    """Giữ nguyên dấu câu hai đầu của từ gốc; không để LLM thêm tashkeel vào lõi từ."""
    if len(e.src) == 1 and len(e.dst) == 1:
        pre, core_src, suf = split_affixes(e.src[0])
        core_dst = split_affixes(e.dst[0])[1]
        if strip_marks(core_src) == core_src:
            core_dst = strip_marks(core_dst)
        return Edit(e.index, e.src, (pre + core_dst + suf,))
    return e


@dataclass
class Filtered:
    accepted: list[Edit]
    rejected: list[tuple[Edit, str]]
    chunk_reason: str | None = None  # có giá trị = bỏ cả chunk


def filter_edits(src: list[str], hyp: list[str], cfg: GuardConfig, allowed: set[int] | None = None) -> Filtered:
    """So src (từ gốc của chunk) với hyp (từ LLM trả về) → sửa được nhận / bị từ chối. Chỉ số theo src."""
    raw = explode_equal_blocks(diff_words(src, hyp))
    n = len(src)
    if cfg.max_diacritic_ratio and diacritic_ratio(src) > cfg.max_diacritic_ratio:
        return Filtered([], [(e, "chunk_rejected") for e in raw], "diacritics")
    if abs(len(hyp) - n) > max(2, cfg.max_drift * n):
        return Filtered([], [(e, "chunk_rejected") for e in raw], "drift")
    if n and sum(max(e.span, len(e.dst)) for e in raw) / n > cfg.max_edit_ratio:
        return Filtered([], [(e, "chunk_rejected") for e in raw], "too_many_edits")
    acc, rej = [], []
    for e in raw:
        why = check_edit(e, cfg, allowed)
        (rej.append((e, why)) if why else acc.append(finalize(e)))
    return Filtered(acc, rej)
