"""Phân tích TÍN HIỆU khoanh từ lỗi và "trần" của ứng viên sửa — chạy trên cache OCR + đáp án, trả lời trước khi tốn thêm GPU:

  1. Tín hiệu nào phân biệt từ ĐÚNG với từ SAI-GẦN-ĐÚNG (khoảng cách ký tự tới đáp án ≤ max_char_edit, tức loại lỗi mà
     chốt chặn cho phép sửa)? So: độ ngần ngừ của dots (log-prob thấp nhất, lề top1−top2, entropy) và NLL của LM.
     Từ sai-xa (khoảng cách lớn) không sửa được bằng bất kỳ cách nào dưới chốt chặn → bỏ khỏi bài toán phân biệt.
  2. "Trần ứng viên của dots": với từ sai-gần-đúng, thay MỘT token bằng phương án thứ 2 / 3 của chính dots có ra đúng từ đáp
     án không? Nếu hiếm → hướng "chọn lại trong các phương án của dots" không đáng làm.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from rapidfuzz.distance import Levenshtein

from .dots_conf import _DEC, decode_with_spans, page_word_conf
from .evaluate import align, norm_w
from .pipeline import PageText, page_text_from_cells
from .text import split_words

SIGNALS = ("dots_lp", "dots_margin", "dots_ent")


@dataclass
class WordRow:
    page: str
    index: int
    word: str
    label: str                 # ok | near (sai-gần-đúng) | far (sai-xa) | extra
    signals: dict              # tên tín hiệu → điểm (CAO = đáng nghi hơn)


def auroc(pos: list[float], neg: list[float]) -> float:
    """P(điểm của mẫu dương > điểm của mẫu âm) + ½ P(bằng nhau). Mann-Whitney, không cần thư viện."""
    if not pos or not neg:
        return float("nan")
    pairs = sorted([(s, 1) for s in pos] + [(s, 0) for s in neg])
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        rank_sum += (i + j + 1) / 2 * sum(l for _, l in pairs[i:j])
        i = j
    return (rank_sum - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def bootstrap_auroc(rows_by_page: dict[str, list[tuple[float, int]]], n: int = 500, seed: int = 0) -> tuple[float, float]:
    rng, pages = random.Random(seed), list(rows_by_page)
    vals = []
    for _ in range(n):
        pos, neg = [], []
        for p in (pages[rng.randrange(len(pages))] for _ in pages):
            for s, y in rows_by_page[p]:
                (pos if y else neg).append(s)
        v = auroc(pos, neg)
        if v == v:
            vals.append(v)
    vals.sort()
    return (vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]) if vals else (float("nan"), float("nan"))


def word_rows(rec: dict, gt: str, max_char_edit: int = 2, lenient: bool = False) -> tuple[PageText, list[WordRow]]:
    """Nhãn + tín hiệu của dots cho từng từ của văn bản trang (cùng danh sách từ với pipeline)."""
    page = page_text_from_cells(rec["id"], rec["cells"])
    words = split_words(page.text)
    al = align(words, split_words(gt), lenient)
    flat = page_word_conf(rec)
    if len(flat) != len(words):
        flat = [None] * len(words)  # không ánh xạ được → không có tín hiệu dots cho trang này
    rows = []
    for i, w in enumerate(words):
        lab = al.label[i]
        if lab == "sub":
            near = al.pair[i] is not None and Levenshtein.distance(al.src_norm[i], al.gt_norm[al.pair[i]]) <= max_char_edit
            lab = "near" if near else "far"
        wc = flat[i]
        sig = {} if wc is None else {"dots_lp": -wc.lp_min, "dots_margin": -wc.margin_min, "dots_ent": wc.ent_max}
        rows.append(WordRow(page.id, i, w, lab, sig))
    return page, rows


def alt_oracle(rec: dict, gt: str, max_char_edit: int = 2, lenient: bool = False) -> dict:
    """Với từ sai-gần-đúng: có phương án top-2/3 của dots, thay MỘT token, cho ra đúng từ đáp án không?"""
    ts = rec.get("token_stats")
    if not ts or "alt_pieces" not in ts:
        return {"near": 0, "covered": 0, "covered_top2": 0}
    text, spans = decode_with_spans(ts["pieces"])
    page, rows = word_rows(rec, gt, max_char_edit, lenient)
    al = align(split_words(page.text), split_words(gt), lenient)
    flat = page_word_conf(rec)
    if len(flat) != len(rows):
        return {"near": 0, "covered": 0, "covered_top2": 0}
    near = covered = covered_top2 = 0
    for i, r in enumerate(rows):
        if r.label != "near" or flat[i] is None:
            continue
        near += 1
        gold = al.gt_norm[al.pair[i]]
        a, b = flat[i].span
        hit, hit2 = False, False
        for t in flat[i].tokens:
            alts = ts["alt_pieces"].get(str(t))
            if not alts:
                continue
            c0, c1 = spans[t]
            lo, hi = max(a, c0), min(b, c1)
            for rank, piece in enumerate(alts[1:] if ts["ids"][t] == ts["top_ids"][t][0] else alts, start=1):
                if piece == ts["pieces"][t]:
                    continue
                try:
                    alt_txt = bytes(_DEC[ch] for ch in piece).decode("utf-8")
                except (KeyError, UnicodeDecodeError):
                    continue
                cand = norm_w(text[a:lo] + alt_txt + text[hi:b], lenient)
                if cand == gold:
                    hit = True
                    hit2 = hit2 or rank == 1
        covered += hit
        covered_top2 += hit2
    return {"near": near, "covered": covered, "covered_top2": covered_top2}
