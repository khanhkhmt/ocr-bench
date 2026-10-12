"""Chẩn đoán "nút thắt": LM có NHẬN RA từ đúng khi được cho sẵn không?

Hai khả năng khi LLM sửa được rất ít: (a) nó không biết từ nào đúng — thiếu hiểu biết ngôn ngữ / thiếu bằng chứng từ ảnh; hoặc
(b) nó biết phân biệt, chỉ là KHÔNG ĐỀ XUẤT được ứng viên đúng khi sinh chữ tự do. Phép đo (chỉ dùng NLL, không sinh chữ):

  - dương: với mỗi từ sai-gần-đúng (≤ max_char_edit ký tự so với đáp án), thay bằng TỪ ĐÁP ÁN trong chunk → Δ = NLL(chunk gốc) −
    NLL(chunk đã thay). Δ > 0: LM thích bản có từ đúng hơn.
  - âm (đối chứng): từ OCR ĐÚNG bị làm nhiễu nhẹ (thay một chữ cái theo bảng nhầm nét) → Δ' = NLL(chunk đã nhiễu) − NLL(chunk gốc).
    Δ' > 0: LM thích từ đúng gốc hơn.
  - Một bộ sửa "chọn ứng viên bằng LM" nhận ứng viên khi Δ > τ. TPR(τ) = tỉ lệ dương được nhận, FPR(τ) = tỉ lệ đối chứng bị nhận
    nhầm. Đây là CẬN TRÊN của cách làm "liệt kê ứng viên rồi chấm bằng LM" khi ứng viên đúng ĐÃ có sẵn trong danh sách.
"""

from __future__ import annotations

import random

from .analysis import word_rows
from .chunking import chunk_text
from .diff import Edit, apply_edits_text
from .evaluate import align
from .text import is_protected, split_affixes, split_words

CONF = {"ا": "أإآ", "ة": "ه", "ه": "ة", "ي": "ىئ", "ى": "ي", "ب": "تثني", "ت": "بثن", "ث": "تب", "ن": "بتث", "ج": "حخ",
        "ح": "جخ", "خ": "حج", "د": "ذ", "ذ": "د", "ر": "ز", "ز": "ر", "س": "ش", "ش": "س", "ص": "ض", "ض": "ص", "ط": "ظ",
        "ظ": "ط", "ع": "غ", "غ": "ع", "ف": "ق", "ق": "ف"}


def perturb(word: str, rng: random.Random) -> str | None:
    pre, core, suf = split_affixes(word)
    pos = [i for i, c in enumerate(core) if c in CONF]
    if len(core) < 3 or not pos:
        return None
    i = rng.choice(pos)
    return pre + core[:i] + rng.choice(CONF[core[i]]) + core[i + 1:] + suf


def chunk_nll(backend, text: str) -> float:
    return sum(w.total for w in backend.nll_words(text))


def collect(backend, recs: dict[str, dict], gts: dict[str, str], n_pos: int, n_neg: int, seed: int = 0,
            max_char_edit: int = 2, max_chars: int = 700) -> tuple[list[float], list[float]]:
    """(Δ của các từ sai-gần-đúng thay bằng từ đáp án, Δ của đối chứng). Cùng quy ước dấu: Δ > 0 = LM thích văn bản đã THAY hơn
    văn bản gốc. Lấy mẫu ngẫu nhiên n_pos / n_neg từ mọi trang."""
    rng = random.Random(seed)
    pos_items, neg_items = [], []
    for pid, rec in recs.items():
        page, rows = word_rows(rec, gts[pid], max_char_edit)
        words = split_words(page.text)
        gt_words = split_words(gts[pid])
        al = align(words, gt_words)
        for ch in chunk_text(page.text, max_chars):
            for i in range(ch.first_word, ch.first_word + ch.n_words):
                r = rows[i]
                if r.label == "near" and al.pair[i] is not None:
                    pre, _, suf = split_affixes(words[i])
                    pos_items.append((pid, ch, i, pre + split_affixes(gt_words[al.pair[i]])[1] + suf))
                elif r.label == "ok" and not is_protected(words[i]):
                    p = perturb(words[i], rng)
                    if p:
                        neg_items.append((pid, ch, i, p))
    rng.shuffle(pos_items)
    rng.shuffle(neg_items)
    base: dict[tuple, float] = {}
    out_pos, out_neg = [], []
    for items, out in ((pos_items[:n_pos], out_pos), (neg_items[:n_neg], out_neg)):
        for pid, ch, i, new in items:
            key = (pid, ch.start)
            if key not in base:
                base[key] = chunk_nll(backend, ch.text)
            local = i - ch.first_word
            mod = apply_edits_text(ch.text, [Edit(local, (split_words(ch.text)[local],), (new,))])
            out.append(base[key] - chunk_nll(backend, mod))
    return out_pos, out_neg


def roc_table(pos: list[float], neg: list[float], taus=(0.0, 1.0, 2.0, 3.0, 4.0, 6.0)) -> list[tuple[float, float, float, float]]:
    """(τ, TPR, FPR, precision) khi NHẬN ứng viên nếu LM thích nó hơn bản gốc quá τ nat (Δ > τ)."""
    rows = []
    for t in taus:
        tp = sum(1 for d in pos if d > t)
        fp = sum(1 for d in neg if d > t)
        rows.append((t, tp / max(1, len(pos)), fp / max(1, len(neg)), tp / max(1, tp + fp)))
    return rows
