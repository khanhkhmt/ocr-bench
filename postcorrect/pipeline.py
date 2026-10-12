"""Pipeline: văn bản OCR của trang → chunk → (khoanh) → LLM → diff → chốt chặn → JSON {original, corrected, edits}.

Gom MỌI chunk của nhiều trang vào một lượt sinh để backend xếp batch theo độ dài (batch 8 nhanh gấp ~4 lần batch 1 trên T4).
Kết quả mỗi trang là một dict JSON (xem `correct_pages`); ghi file / resume nằm ở cli.py.
"""

from __future__ import annotations

import bisect
import re
from dataclasses import asdict, dataclass, field

from .chunking import chunk_text
from .detect import select_flags
from .diff import Edit, apply_edits_text
from .guard import GuardConfig, filter_edits
from .parse import parse_flags, parse_rewrite
from .prompts import mark_words, messages
from .text import split_words, words_with_spans

# Loại khối có chữ để sửa. Bảng / công thức / hình / đầu-chân trang KHÔNG đưa cho LLM (số liệu, mã, rác Latin).
TEXT_CATS = {"Text", "Title", "Section-header", "List-item", "Caption", "Footnote"}
_HASHES = re.compile(r"^#{1,6}\s+")


@dataclass
class PageText:
    id: str
    text: str
    blocks: list[dict] = field(default_factory=list)  # {block, category, start, end, first_word, n_words}


def page_text_from_cells(page_id: str, cells: list[dict] | None, categories=TEXT_CATS) -> PageText:
    """Nối chữ các khối (theo thứ tự đọc của dots) bằng xuống dòng; bỏ ký hiệu Markdown của tiêu đề."""
    parts, blocks, pos = [], [], 0
    for i, c in enumerate(cells or []):
        if c.get("category") not in categories or not (c.get("text") or "").strip():
            continue
        t = _HASHES.sub("", c["text"].strip())
        if parts:
            pos += 1  # dấu xuống dòng ngăn khối
        blocks.append({"block": i, "category": c["category"], "start": pos, "end": pos + len(t)})
        parts.append(t)
        pos += len(t)
    text = "\n".join(parts)
    starts = [a for _, a, _ in words_with_spans(text)]
    for b in blocks:
        b["first_word"] = bisect.bisect_left(starts, b["start"])
        b["n_words"] = bisect.bisect_left(starts, b["end"]) - b["first_word"]
    return PageText(page_id, text, blocks)


@dataclass
class Settings:
    strategy: str = "A"               # A viết lại | B khoanh từ lỗi (JSON) | C viết lại có đánh dấu từ nghi lỗi
    chunk_chars: int = 700
    fewshot: bool = False
    guard: GuardConfig = field(default_factory=GuardConfig)
    flag_frac: float = 0.3            # C: tỉ lệ từ được đánh dấu (sau khi bỏ từ bảo vệ)
    flag_min_nll: float = 3.0         # C: điểm NLL tối thiểu để được đánh dấu
    max_new_factor: float = 1.4
    tag: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class _Task:
    page: int
    idx: int
    chunk: object
    words: list[str]
    flagged: dict | None = None
    prompt: str = ""
    max_new: int = 0
    raw: str = ""


def _block_of(page: PageText, word_index: int):
    for b in page.blocks:
        if b["first_word"] <= word_index < b["first_word"] + b["n_words"]:
            return b["block"]
    return None


def correct_pages(pages: list[PageText], backend, st: Settings) -> list[dict]:
    strategy = st.strategy
    tasks: list[_Task] = []
    for pi, p in enumerate(pages):
        for ci, ch in enumerate(chunk_text(p.text, st.chunk_chars)):
            tasks.append(_Task(pi, ci, ch, split_words(ch.text)))

    if strategy == "C":  # khoanh trước: chunk không có từ nghi lỗi thì khỏi gọi LLM
        for t in tasks:
            nll = backend.nll_words(t.chunk.text)
            t.flagged = select_flags(t.words, nll, st.flag_frac, st.flag_min_nll, st.guard.min_core_len)

    todo = [t for t in tasks if strategy != "C" or t.flagged]
    for t in todo:
        text = t.chunk.text
        if strategy == "C":
            text = mark_words(words_with_spans(t.chunk.text), t.chunk.text, set(t.flagged))
        t.prompt = backend.build_prompt(messages(strategy, text, st.fewshot))
        t.max_new = 320 if strategy == "B" else min(3000, int(st.max_new_factor * backend.n_tokens(t.chunk.text)) + 48)
    if todo:
        for t, raw in zip(todo, backend.generate([t.prompt for t in todo], [t.max_new for t in todo])):
            t.raw = raw

    results = [{"id": p.id, "strategy": strategy, "model": getattr(backend, "model_id", "?"), "tag": st.tag,
                "original": p.text, "corrected": p.text, "edits": [], "flags": [], "rejected": [], "chunks": [],
                "settings": st.as_dict()} for p in pages]
    for t in tasks:
        res = results[t.page]
        info = {"i": t.idx, "start": t.chunk.start, "end": t.chunk.end, "first_word": t.chunk.first_word,
                "n_words": t.chunk.n_words, "status": "ok", "chunk_reason": None, "n_edits": 0, "n_rejected": 0}
        if strategy == "C":
            info["n_flagged"] = len(t.flagged or {})
            res["flags"] += [{"index": t.chunk.first_word + i, "word": t.words[i], "score": round(s, 2)}
                             for i, s in sorted((t.flagged or {}).items())]
        if strategy == "C" and not t.flagged:
            info["status"] = "no_flags"
            res["chunks"].append(info)
            continue
        info["raw"] = t.raw
        hyp = None
        if strategy == "B":
            items, status = parse_flags(t.raw)
            info["status"] = f"B:{status}"
            fix = {}
            for it in items:
                fix.setdefault(it["word"], it["fix"])
            hyp = [fix.get(w, w) for w in t.words]
            hyp = [x for w in hyp for x in w.split()]
            res["flags"] += [{"index": t.chunk.first_word + i, "word": w, "fix": fix[w]}
                             for i, w in enumerate(t.words) if w in fix]
        else:
            text, status = parse_rewrite(t.raw)
            info["status"] = f"rewrite:{status}"
            if text is not None:
                hyp = split_words(text.replace("[[", "").replace("]]", ""))
        if hyp is None:
            info["chunk_reason"] = "unparsable"
            res["chunks"].append(info)
            continue
        allowed = set(t.flagged) if strategy == "C" else None
        f = filter_edits(t.words, hyp, st.guard, allowed)
        info["chunk_reason"] = f.chunk_reason
        info["n_edits"], info["n_rejected"] = len(f.accepted), len(f.rejected)
        for e in f.accepted:
            g = Edit(t.chunk.first_word + e.index, e.src, e.dst)
            res["edits"].append({**g.as_json(), "chunk": t.idx, "block": _block_of(pages[t.page], g.index)})
        for e, why in f.rejected:
            res["rejected"].append({"index": t.chunk.first_word + e.index, "from": e.from_, "to": e.to, "reason": why})
        res["chunks"].append(info)

    for p, res in zip(pages, results):
        res["edits"].sort(key=lambda e: e["index"])
        eds = [Edit(e["index"], tuple(e["from"].split()), tuple(e["to"].split())) for e in res["edits"]]
        res["corrected"] = apply_edits_text(p.text, eds)
    return results
