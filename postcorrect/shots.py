"""Ví dụ few-shot THẬT trong miền: cặp (chunk OCR của dots → chunk chỉ sửa các từ sai-gần-đúng), lấy từ các trang dev.

Vì sao: zero-shot, LLM 8B gần như chỉ chép lại đầu vào (đo trên dev: sửa đúng < 1% số từ trong tầm với), và ví dụ tổng hợp viết tay
không cho nó biết dots hay sai kiểu nào. Vài cặp thật (lỗi thật của dots, đáp án chỉ sửa chỗ sai-gần-đúng, giữ nguyên mọi
chỗ khác) dạy đúng phân phối lỗi mà không cần fine-tune.

CHỐNG RÒ RỈ: nguồn ví dụ là tập trang dev KHÔNG nằm trong tập đang chấm (`exclude` / --skip). Khi chấm holdout thì lấy từ dev.
Ví dụ chỉ chứa những sửa mà CHỐT CHẶN sẽ nhận (không đổi chữ số, không chỉ khác hamza / alef / tashkeel, không đưa chữ ngoài bộ Ả Rập
chuẩn vào): dạy mô hình hành vi mà hệ thống cho phép. Chunk nhiều tashkeel (dots bịa văn kiểu Qur'an) và chunk nhiều chữ số bị loại.
"""

from __future__ import annotations

import json
from pathlib import Path

from rapidfuzz.distance import Levenshtein

from .chunking import chunk_text
from .diff import Edit, apply_edits_text
from .evaluate import align, norm_w
from .guard import GuardConfig, check_edit
from .pipeline import page_text_from_cells
from .text import has_digit, split_affixes, split_words, strip_marks


def _diacritic_ratio(text: str) -> float:
    return 1 - len(strip_marks(text)) / max(1, len(text))


def safe_oracle_edits(words: list[str], gt_words: list[str], guard: GuardConfig) -> list[Edit]:
    """Sửa của bộ sửa hoàn hảo mà chốt chặn sẽ NHẬN: từ sai-gần-đúng → từ đáp án (giữ dấu câu của OCR), bỏ các sửa chỉ khác
    hamza / alef (khác biệt quy ước, không phải đọc sai)."""
    al = align(words, gt_words)
    out = []
    for i, w in enumerate(words):
        j = al.pair[i]
        if al.label[i] != "sub" or j is None:
            continue
        if Levenshtein.distance(al.src_norm[i], al.gt_norm[j]) > guard.max_char_edit:
            continue
        if norm_w(w, True) == norm_w(gt_words[j], True):  # chỉ khác hamza/alef/yeh
            continue
        pre, _, suf = split_affixes(w)
        e = Edit(i, (w,), (pre + split_affixes(gt_words[j])[1] + suf,))
        if check_edit(e, guard) is None:
            out.append(e)
    return out


def make_shots(ocr_dir: Path, gts: dict[str, str], ids: list[str], n_fix: int = 2, n_clean: int = 1, max_chars: int = 320,
               min_fix: int = 3, max_change_ratio: float = 0.25, guard: GuardConfig | None = None) -> list[dict]:
    """Chọn n_fix chunk có nhiều chỗ sai-gần-đúng an toàn (mỗi trang tối đa một) và n_clean chunk không có chỗ nào cần sửa mà
    phần lớn từ đã đúng (dạy "không đổi gì" khi không có gì rõ ràng để sửa). Mỗi ví dụ: {id, src, tgt, fixes:[[từ_gốc, từ_sửa]]}."""
    guard = guard or GuardConfig()
    fix_pool, clean_pool = [], []
    for pid in ids:
        f = Path(ocr_dir) / f"{pid}.json"
        if not f.exists() or pid not in gts:
            continue
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("error") or not rec.get("cells"):
            continue
        page = page_text_from_cells(pid, rec["cells"])
        ws, gw = split_words(page.text), split_words(gts[pid])
        edits = safe_oracle_edits(ws, gw, guard)
        al = align(ws, gw)
        for ch in chunk_text(page.text, max_chars):
            lo, hi = ch.first_word, ch.first_word + ch.n_words
            if ch.n_words < 8 or _diacritic_ratio(ch.text) > 0.02:
                continue
            if sum(1 for w in ws[lo:hi] if has_digit(w)) / ch.n_words > 0.1:
                continue
            local = [e for e in edits if lo <= e.index < hi]
            shifted = [Edit(e.index - lo, e.src, e.dst) for e in local]
            item = {"id": pid, "src": ch.text, "tgt": apply_edits_text(ch.text, shifted),
                    "fixes": [[e.from_, e.to] for e in local]}
            if len(local) >= min_fix and len(local) / ch.n_words <= max_change_ratio:
                fix_pool.append((len(local), item))
            elif not local and sum(1 for l in al.label[lo:hi] if l == "ok") / ch.n_words >= 0.5:
                clean_pool.append(item)
    out, used = [], set()
    for _, item in sorted(fix_pool, key=lambda x: -x[0]):
        if item["id"] not in used and len([o for o in out if o["fixes"]]) < n_fix:
            out.append(item)
            used.add(item["id"])
    for item in clean_pool:
        if item["id"] not in used and len([o for o in out if not o["fixes"]]) < n_clean:
            out.append(item)
            used.add(item["id"])
    return out
