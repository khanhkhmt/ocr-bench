"""Từ điển tần suất tiếng Ả Rập + sinh ứng viên trong khoảng cách sửa ≤ k — nguồn ứng viên cho "LLM chỉ làm người kiểm chứng".

Vì sao: LLM sinh chữ tự do chỉ chép lại đầu vào (đo trên dev: sửa đúng < 2% số từ trong tầm với) và khi buộc phải sửa thì chuẩn hoá
quy ước hoặc đoán sai nghĩa. Đổi vai: ứng viên đến từ từ điển (chỉ những từ THẬT, gần chữ OCR ≤ 2 ký tự), LM chỉ chấm trong ngữ cảnh
xem ứng viên nào hợp hơn chữ OCR — không thể bịa ra từ ngoài danh sách.

Từ điển dựng từ Wikipedia tiếng Ả Rập (chuẩn, hiện đại): thiếu từ địa phương / chính tả cũ → độ phủ ứng viên là giới hạn của hướng này
(đo bằng `python -m postcorrect lexicon-coverage`).
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from rapidfuzz import process
from rapidfuzz.distance import Levenshtein

from .text import is_protected, norm_word

_ARABIC_WORD = re.compile(r"^[ء-يٱ]{2,}$")


def tokenize_for_lexicon(text: str):
    for w in text.split():
        n = norm_word(w)
        if _ARABIC_WORD.match(n):
            yield n


def build_from_wikipedia(out: Path, n_articles: int = 60000, top_k: int = 200000, min_count: int = 3) -> dict:
    from datasets import load_dataset

    ds = load_dataset("wikimedia/wikipedia", "20231101.ar", split="train", streaming=True)
    c: Counter = Counter()
    for i, row in enumerate(ds):
        if i >= n_articles:
            break
        c.update(tokenize_for_lexicon(row["text"]))
    words = [(w, n) for w, n in c.most_common(top_k * 2) if n >= min_count][:top_k]
    out.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    return {"articles": min(n_articles, i + 1), "distinct": len(c), "kept": len(words), "min_kept_count": words[-1][1] if words else 0}


class Lexicon:
    def __init__(self, path: Path | str):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.words = [w for w, _ in data]
        self.freq = {w: n for w, n in data}
        self.set = set(self.words)

    def __contains__(self, w: str) -> bool:
        return norm_word(w) in self.set

    def candidates(self, word: str, max_dist: int = 2, limit: int = 40) -> list[tuple[str, int, int]]:
        """(từ, khoảng cách, tần suất) của các từ trong từ điển cách `word` ≤ max_dist ký tự (trên dạng đã chuẩn hoá); gần nhất rồi
        phổ biến nhất lên trước. Từ được bảo vệ (số, Latin, chữ đơn) → không có ứng viên."""
        if is_protected(word):
            return []
        q = norm_word(word)
        if not q:
            return []
        hits = process.extract(q, self.words, scorer=Levenshtein.distance, score_cutoff=max_dist, limit=None)
        out = [(w, int(d), self.freq[w]) for w, d, _ in hits if w != q]
        out.sort(key=lambda x: (x[1], -x[2]))
        return out[:limit]
