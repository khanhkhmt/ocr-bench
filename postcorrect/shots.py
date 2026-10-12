"""Ví dụ few-shot THẬT trong miền: cặp (chunk OCR của dots → chunk chỉ sửa các từ sai-gần-đúng), lấy từ các trang dev.

Vì sao: zero-shot, LLM 8B gần như chỉ chép lại đầu vào (đo trên dev: sửa đúng < 1% số từ trong tầm với), và ví dụ tổng hợp viết tay
không cho nó biết dots hay sai kiểu nào. Vài cặp thật (lỗi thật của dots, đáp án chỉ sửa chỗ sai-gần-đúng, giữ nguyên mọi
chỗ khác) dạy đúng phân phối lỗi mà không cần fine-tune.

CHỐNG RÒ RỈ: nguồn ví dụ là tập trang dev KHÔNG nằm trong tập đang chấm (`exclude_ids`). Khi chấm holdout thì lấy từ dev.
Ví dụ được sinh bằng `oracle_edits` (đáp án người) nên chỉ chứa sửa mà chốt chặn cho phép (≤ max_char_edit ký tự).
"""

from __future__ import annotations

import json
from pathlib import Path

from .analysis import oracle_edits
from .chunking import chunk_text
from .diff import Edit, apply_edits_text
from .pipeline import page_text_from_cells
from .text import split_words


def make_shots(ocr_dir: Path, gts: dict[str, str], ids: list[str], n_fix: int = 2, n_clean: int = 1, max_chars: int = 320,
               min_fix: int = 3, max_change_ratio: float = 0.3, max_char_edit: int = 2) -> list[dict]:
    """Chọn n_fix chunk có nhiều chỗ sai-gần-đúng (mỗi trang tối đa một) và n_clean chunk gần như không có chỗ nào cần sửa
    (dạy "không đổi gì" khi không chắc). Mỗi ví dụ: {id, src, tgt, fixes:[[từ_gốc, từ_sửa]]}."""
    fix_pool, clean_pool = [], []
    for pid in ids:
        f = Path(ocr_dir) / f"{pid}.json"
        if not f.exists() or pid not in gts:
            continue
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("error") or not rec.get("cells"):
            continue
        text, _, edits = oracle_edits(rec, gts[pid], max_char_edit)
        page = page_text_from_cells(pid, rec["cells"])
        ws = split_words(page.text)
        for ch in chunk_text(page.text, max_chars):
            lo, hi = ch.first_word, ch.first_word + ch.n_words
            local = [e for e in edits if lo <= e["index"] < hi]
            ratio = len(local) / max(1, ch.n_words)
            if ch.n_words < 8 or ratio > max_change_ratio:
                continue
            shifted = [Edit(e["index"] - lo, (e["from"],), tuple(e["to"].split())) for e in local]
            tgt = apply_edits_text(ch.text, shifted)
            item = {"id": pid, "src": ch.text, "tgt": tgt, "fixes": [[e["from"], e["to"]] for e in local]}
            if len(local) >= min_fix:
                fix_pool.append((len(local), item))
            elif not local:
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
