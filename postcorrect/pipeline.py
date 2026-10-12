"""Pipeline: văn bản OCR của trang → chunk → (khoanh) → LLM → diff → chốt chặn → JSON {original, corrected, edits}.

Gom MỌI chunk của nhiều trang vào một lượt sinh để backend xếp batch theo độ dài (batch 8 nhanh gấp ~4 lần batch 1 trên T4).
Kết quả mỗi trang là một dict JSON (xem `correct_pages`); ghi file / resume nằm ở cli.py.
"""

from __future__ import annotations

import bisect
import re
from dataclasses import asdict, dataclass, field

from .chunking import chunk_text
from .detect import DEFAULT_MIN, canon_signal, combine_ranks, nll_scores, select_flags
from .diff import Edit, apply_edits_text
from .guard import GuardConfig, filter_edits
from .parse import parse_flags, parse_rewrite
from .prompts import mark_words, messages
from .text import TEXT_CATS, split_words, words_with_spans

_HASHES = re.compile(r"^#{1,6}\s+")


@dataclass
class PageText:
    id: str
    text: str
    blocks: list[dict] = field(default_factory=list)  # {block, category, start, end, first_word, n_words}
    dots: list | None = None  # WordConf (độ tin cậy dots) cho từng từ, hoặc None — để chiến lược C chọn từ đánh dấu


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
    style: str = "cons"               # kiểu prompt: cons (bảo thủ) | assert (quyết đoán, nói rõ mật độ lỗi cao)
    guard: GuardConfig = field(default_factory=GuardConfig)
    flag_signal: str = "nll_sum"      # C: nll_sum | nll_max (LM) | dots_lp (độ ngần ngừ của dots) | dots_lp+nll_sum | dots_lp+nll_max (hạng TB)
    flag_frac: float = 0.3            # C: tỉ lệ từ được đánh dấu (sau khi bỏ từ bảo vệ)
    flag_min: float | None = None     # C: điểm tuyệt đối tối thiểu để được đánh dấu (None = mặc định theo tín hiệu; tổ hợp hạng: không có)
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


def process_raw(strategy: str, words: list[str], raw: str, guard: GuardConfig, allowed: set[int] | None) -> dict:
    """Đầu ra thô của LLM cho MỘT chunk → trạng thái, sửa được nhận / từ chối (theo chốt chặn `guard`).
    Tách riêng để quét ngưỡng chốt chặn trên đầu ra đã lưu mà không cần chạy lại LLM (refilter_result)."""
    out = {"status": "", "chunk_reason": None, "filtered": None, "flags": []}
    if strategy == "B":
        items, status = parse_flags(raw)
        out["status"] = f"B:{status}"
        fix = {}
        for it in items:
            fix.setdefault(it["word"], it["fix"])
        hyp = [x for w in (fix.get(w, w) for w in words) for x in w.split()]
        out["flags"] = [(i, w, fix[w]) for i, w in enumerate(words) if w in fix]
    else:
        text, status = parse_rewrite(raw)
        out["status"] = f"rewrite:{status}"
        hyp = split_words(text.replace("[[", "").replace("]]", "")) if text is not None else None
    if hyp is None:
        out["chunk_reason"] = "unparsable"
        return out
    out["filtered"] = filter_edits(words, hyp, guard, allowed)
    out["chunk_reason"] = out["filtered"].chunk_reason
    return out


def refilter_result(res: dict, guard: GuardConfig) -> dict:
    """Áp lại chốt chặn khác lên đầu ra thô đã lưu của một trang (không chạy lại LLM). Trả bản sao đã cập nhật."""
    out = {**res, "edits": [], "rejected": [], "chunks": []}
    words = split_words(res["original"])
    strategy = res["strategy"]
    flagged = {f["index"] for f in res["flags"]} if strategy == "C" else None
    for info in res["chunks"]:
        info = dict(info)
        if "raw" not in info:  # chunk không gọi LLM (C không có từ nghi lỗi)
            out["chunks"].append(info)
            continue
        lo, n = info["first_word"], info["n_words"]
        allowed = {i - lo for i in flagged if lo <= i < lo + n} if flagged is not None else None
        pr = process_raw(strategy, words[lo:lo + n], info["raw"], guard, allowed)
        info["chunk_reason"], info["n_edits"], info["n_rejected"] = pr["chunk_reason"], 0, 0
        f = pr["filtered"]
        if f is not None:
            info["n_edits"], info["n_rejected"] = len(f.accepted), len(f.rejected)
            for e in f.accepted:
                g = Edit(lo + e.index, e.src, e.dst)
                out["edits"].append({**g.as_json(), "chunk": info["i"], "block": None})
            for e, why in f.rejected:
                out["rejected"].append({"index": lo + e.index, "from": e.from_, "to": e.to, "reason": why})
        out["chunks"].append(info)
    out["edits"].sort(key=lambda e: e["index"])
    eds = [Edit(e["index"], tuple(e["from"].split()), tuple(e["to"].split())) for e in out["edits"]]
    out["corrected"] = apply_edits_text(res["original"], eds)
    out["settings"] = {**res["settings"], "guard": asdict(guard)}
    return out


def correct_pages(pages: list[PageText], backend, st: Settings) -> list[dict]:
    strategy = st.strategy
    tasks: list[_Task] = []
    for pi, p in enumerate(pages):
        for ci, ch in enumerate(chunk_text(p.text, st.chunk_chars)):
            tasks.append(_Task(pi, ci, ch, split_words(ch.text)))

    if strategy == "C":  # khoanh trước: chunk không có từ nghi lỗi thì khỏi gọi LLM
        for t in tasks:
            lo, hi = t.chunk.first_word, t.chunk.first_word + t.chunk.n_words
            dots = pages[t.page].dots
            d_scores = [(-wc.lp_min if wc is not None else None) for wc in dots[lo:hi]] if dots and len(dots) >= hi else None
            parts = canon_signal(st.flag_signal).split("+")
            nll = backend.nll_words(t.chunk.text) if any(x.startswith("nll") for x in parts) else None
            by = {"dots_lp": d_scores, "nll_max": nll_scores(nll, "max") if nll else None,
                  "nll_sum": nll_scores(nll, "sum") if nll else None}
            have = [x for x in parts if by[x] is not None]  # trang không có tín hiệu dots → dùng phần còn lại (nếu có)
            if not have:
                scores, floor = [None] * t.chunk.n_words, 0.0
            elif len(have) == 1:
                scores = by[have[0]]
                floor = st.flag_min if st.flag_min is not None else DEFAULT_MIN[have[0]]
            else:
                scores, floor = combine_ranks(by[have[0]], by[have[1]]), 0.0
            t.flagged = select_flags(t.words, scores, st.flag_frac, floor, st.guard.min_core_len)

    todo = [t for t in tasks if strategy != "C" or t.flagged]
    for t in todo:
        text = t.chunk.text
        if strategy == "C":
            text = mark_words(words_with_spans(t.chunk.text), t.chunk.text, set(t.flagged))
        t.prompt = backend.build_prompt(messages(strategy, text, st.fewshot, st.style))
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
        pr = process_raw(strategy, t.words, t.raw, st.guard, set(t.flagged) if strategy == "C" else None)
        info["status"] = pr["status"]
        info["chunk_reason"] = pr["chunk_reason"]
        if pr["flags"]:
            res["flags"] += [{"index": t.chunk.first_word + i, "word": w, "fix": f} for i, w, f in pr["flags"]]
        if pr["filtered"] is None:
            res["chunks"].append(info)
            continue
        f = pr["filtered"]
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


def vote_results(results: list[dict], min_votes: int = 2) -> dict:
    """Đồng thuận: chỉ giữ sửa mà ≥ min_votes lượt chạy (khác prompt / khác model) cùng đề xuất GIỐNG HỆT
    (cùng vị trí, cùng từ gốc, cùng từ thay). Chính xác hơn từng lượt riêng lẻ, đổi lại bớt recall.
    `results`: kết quả của CÙNG MỘT trang từ các lượt chạy khác nhau."""
    base = results[0]
    votes: dict[tuple, int] = {}
    for r in results:
        for k in {(e["index"], e["from"], e["to"]) for e in r["edits"]}:
            votes[k] = votes.get(k, 0) + 1
    edits = [{"index": i, "span": len(f.split()), "from": f, "to": t, "votes": v,
              "block": next((e.get("block") for r in results for e in r["edits"] if (e["index"], e["from"], e["to"]) == (i, f, t)), None)}
             for (i, f, t), v in sorted(votes.items()) if v >= min_votes]
    eds = [Edit(e["index"], tuple(e["from"].split()), tuple(e["to"].split())) for e in edits]
    flags: dict[int, dict] = {}
    for r in results:
        for f in r.get("flags", []):
            flags.setdefault(f["index"], {"index": f["index"], "word": f["word"], "n_runs": 0})["n_runs"] += 1
    return {"id": base["id"], "strategy": "vote", "model": "+".join(sorted({r.get("model", "?") for r in results})),
            "tag": f"vote{min_votes}of{len(results)}", "original": base["original"],
            "corrected": apply_edits_text(base["original"], eds), "edits": edits,
            "flags": sorted(flags.values(), key=lambda f: f["index"]), "rejected": [], "chunks": [],
            "settings": {"runs": [r.get("tag") or r.get("strategy") for r in results], "min_votes": min_votes}}
