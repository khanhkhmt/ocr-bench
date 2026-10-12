"""Bằng chứng từ ảnh gốc cho người duyệt và cho kiểm toán: mỗi dòng một ảnh cắt, mỗi từ cần duyệt một ảnh cắt rộng,
kèm toạ độ và SHA-256 của file ảnh nguồn (biết chắc bằng chứng lấy từ đúng bản scan nào).

Ảnh cắt lấy từ ảnh HÌNH HỌC (preprocess.prepare: chỉ xoay / phóng, không đổi màu) — người duyệt thấy đúng nét mực thật,
không phải ảnh đã qua lọc. Khung từ: lấy từ engine nếu có (Tesseract), nếu không thì ước tính theo tỉ lệ số ký tự trên
dòng (chữ Ả Rập / Hebrew đọc phải→trái) và nới rộng ra hai bên — đủ để nhìn, không dùng để đo.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .doc import READ, Line, Page
from .script import vote_key


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def estimate_word_boxes(ln: Line, rtl: bool = True, pad_frac: float = 0.35) -> None:
    x1, y1, x2, y2 = ln.bbox
    lens = [max(1, len(vote_key(w.text)) or len(w.text)) for w in ln.words]
    total = sum(lens) + max(0, len(lens) - 1)
    if not total:
        return
    pos, W = 0, x2 - x1
    for w, n in zip(ln.words, lens):
        a, b = pos / total, (pos + n) / total
        pos += n + 1
        lo, hi = (x2 - b * W, x2 - a * W) if rtl else (x1 + a * W, x1 + b * W)
        pad = pad_frac * (hi - lo) + 12
        w.box = [int(max(x1, lo - pad)), y1, int(min(x2, hi + pad)), y2]


def save_evidence(page: Page, geom_image, out_dir: Path, pad: int = 6, all_words: bool = False) -> None:
    """Ghi evidence/<page>/<dòng>.png và <từ>.png (từ chưa chắc / quan trọng); điền line.crop, word.box."""
    d = out_dir / "evidence" / page.id
    d.mkdir(parents=True, exist_ok=True)
    W, H = geom_image.size
    for ln in page.lines:
        x1, y1, x2, y2 = ln.bbox
        box = (max(0, x1 - pad), max(0, y1 - pad), min(W, x2 + pad), min(H, y2 + pad))
        p = d / f"{ln.id}.png"
        geom_image.crop(box).save(p)
        ln.crop = str(p.relative_to(out_dir))
        if any(w.box is None for w in ln.words):
            estimate_word_boxes(ln, rtl=ln.script in ("ar", "he", "mixed", "digit"))
        for w in ln.words:
            if w.box and (all_words or w.status != READ or w.critical):
                bx = (w.box[0], max(0, w.box[1] - pad), w.box[2], min(H, w.box[3] + pad))
                q = d / f"{w.id.replace(':', '_')}.png"
                geom_image.crop(bx).save(q)
                w.features["crop"] = str(q.relative_to(out_dir))
