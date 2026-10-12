"""Độ tin cậy TỪNG TỪ của dots, suy từ thống kê token đã ghi lúc OCR (dots_logprob.py) — không cần nạp lại model.

Chuỗi `response` của dots là JSON thô; mỗi token có id, log-prob, lề top1−top2, entropy và "mảnh" (chuỗi BPE kiểu GPT-2).
Giải mã byte-level: mảnh → byte → ký tự, nên biết token nào phủ ký tự nào mà không cần tokenizer. Rồi tìm văn bản của từng khối
(đã thoát JSON) trong response theo thứ tự, và từng từ trong khối.
"""

from __future__ import annotations

import bisect
import json
import re
from dataclasses import dataclass


def _byte_decoder() -> dict[str, int]:
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs, n = bs[:], 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {chr(c): b for b, c in zip(bs, cs)}


_DEC = _byte_decoder()


def piece_bytes(piece: str) -> bytes:
    """Mảnh BPE → byte. Token đặc biệt (<|im_end|>, <|endoftext|>...) không nằm trong response → rỗng."""
    if piece.startswith("<|") and piece.endswith("|>"):
        return b""
    try:
        return bytes(_DEC[c] for c in piece)
    except KeyError:
        return b""


def decode_with_spans(pieces: list[str]) -> tuple[str, list[tuple[int, int]]]:
    """(văn bản, [(ký tự đầu, ký tự cuối) của từng token]). Token cắt giữa ký tự UTF-8: ký tự thuộc token chứa byte ĐẦU."""
    chunks = [piece_bytes(p) for p in pieces]
    data = b"".join(chunks)
    text = data.decode("utf-8", errors="replace")
    char_start, pos = [], 0  # byte đầu của từng ký tự
    for ch in text:
        char_start.append(pos)
        pos += len(ch.encode("utf-8")) if ch != "�" else 1
    spans, b0 = [], 0
    for c in chunks:
        b1 = b0 + len(c)
        spans.append((bisect.bisect_left(char_start, b0), bisect.bisect_left(char_start, b1)))
        b0 = b1
    return text, spans


@dataclass
class WordConf:
    word: str
    lp_min: float       # log-prob thấp nhất của một token trong từ (càng âm càng ngần ngừ)
    lp_mean: float
    margin_min: float   # lề top1−top2 nhỏ nhất (nhỏ = dots phân vân giữa hai chữ)
    ent_max: float      # entropy lớn nhất


def _escaped(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)[1:-1]


def word_confidences(response: str, token_stats: dict, cells: list[dict], categories=None) -> dict[int, list[WordConf | None]]:
    """cell index → danh sách WordConf theo từng từ (split khoảng trắng) của text khối; None nếu không định vị được.
    Chỉ xét khối có category trong `categories` (None = mọi khối có chữ)."""
    pieces = token_stats["pieces"]
    text, spans = decode_with_spans(pieces)
    if text != response and not response.startswith(text[: max(0, len(text) - 8)]):
        return {}  # chuỗi sinh ra khác response (vd. đã sửa phần cắt dở) → không tin ánh xạ
    out: dict[int, list[WordConf | None]] = {}
    cursor = 0
    starts = [s for s, _ in spans]
    for ci, c in enumerate(cells or []):
        t = c.get("text") or ""
        if not t.strip() or (categories is not None and c.get("category") not in categories):
            continue
        t = re.sub(r"^#{1,6}\s+", "", t.strip()) if c.get("category") in ("Section-header", "Title") else t
        words = t.split()
        row: list[WordConf | None] = []
        cur = cursor
        for w in words:
            k = text.find(_escaped(w), cur)
            if k == -1:
                row.append(None)
                continue
            a, b = k, k + len(_escaped(w))
            cur = b
            # token phủ [a, b): token có (c0, c1) giao với [a, b)
            lo = max(0, bisect.bisect_right(starts, a) - 1)
            ids = [i for i in range(lo, len(spans)) if spans[i][0] < b and spans[i][1] > a]
            if not ids:
                row.append(None)
                continue
            lp = [token_stats["lp"][i] for i in ids]
            row.append(WordConf(w, min(lp), sum(lp) / len(lp), min(token_stats["margin"][i] for i in ids),
                                max(token_stats["ent"][i] for i in ids)))
        out[ci] = row
        cursor = max(cursor, cur)
    return out
