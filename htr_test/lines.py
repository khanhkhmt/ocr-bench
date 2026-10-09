"""Tách DÒNG chữ trong một khối (ảnh cắt từ khối dots) — hai model thử nghiệm chỉ đọc được ảnh một dòng.

- "chieu_ngang": chiếu ngang (nhanh, không cần cài thêm): mực theo ngưỡng thích nghi → bỏ đường kẻ dài (giấy kẻ
  dòng) → biểu đồ mực theo hàng, làm mượt → dải dòng; dải cao bất thường (2 dòng dính) tách ở điểm trũng; dải quá
  thấp (dấu chấm, dấu thanh) gộp vào dòng gần nhất; nới lên / xuống cho phần nét vươn cao / thấp.
- "kraken": tách dòng theo đường chân chữ (blla) của Kraken — tốt hơn với chữ tay cổ, cần venv kraken
  (experiments/real_docs_probe/run_kraken.sh tự tạo). Không có → dùng chiếu ngang.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

KRAKEN = os.environ.get("KRAKEN_BIN", "/kaggle/working/venvs/kraken/bin/kraken")
# Model tách dòng Kraken huấn luyện trên Muharaf (1.600 trang viết tay Ả Rập lưu trữ: thư từ, giấy tờ pháp lý) — CC BY 4.0
KRAKEN_SEG_MODEL = os.environ.get("KRAKEN_SEG_MODEL", "/kaggle/working/kraken_models/muharaf_seg_best.mlmodel")
MUHARAF_SEG_URL = "https://zenodo.org/records/14295555/files/muharaf_seg_best.mlmodel?download=1"


def _ink(img: Image.Image) -> np.ndarray:
    g = np.asarray(img.convert("L"), dtype=np.float32)
    bg, dark = np.percentile(g, 75), np.percentile(g, 0.5)
    if bg - dark < 30:
        return np.zeros(g.shape, bool)
    m = g < (bg + dark) / 2
    # đường kẻ ngang dài (giấy kẻ dòng, gạch chân) không phải chữ
    m[m.mean(axis=1) > 0.5, :] = False
    return m


def _smooth(v: np.ndarray, k: int) -> np.ndarray:
    k = max(1, int(k))
    return np.convolve(v, np.ones(k) / k, mode="same")


def split_projection(img: Image.Image, min_h: int = 6) -> list[tuple[int, int]]:
    """→ [(y0, y1)] các dòng (toạ độ trong ảnh), từ trên xuống."""
    m = _ink(img)
    H = m.shape[0]
    if not m.any():
        return []
    prof = m.sum(axis=1).astype(np.float32)
    rows = np.nonzero(prof > 0)[0]
    # ước chiều cao dòng thô: dải liên tục của hàng có mực
    bands, start = [], None
    on = prof > 0.05 * prof.max()
    for y in range(H + 1):
        if y < H and on[y] and start is None:
            start = y
        elif (y == H or not on[y]) and start is not None:
            bands.append((start, y))
            start = None
    if not bands:
        return [(int(rows.min()), int(rows.max()) + 1)]
    med = float(np.median([b - a for a, b in bands])) or 10.0
    sm = _smooth(prof, max(3, med / 4))
    thr = 0.12 * sm.max()
    bands, start = [], None
    for y in range(H + 1):
        if y < H and sm[y] > thr and start is None:
            start = y
        elif (y == H or sm[y] <= thr) and start is not None:
            bands.append([start, y])
            start = None
    if not bands:
        return []
    med = float(np.median([b - a for a, b in bands]))
    # dải cao bất thường = 2+ dòng dính nhau → cắt ở điểm trũng nhất
    out = []
    for a, b in bands:
        segs = [(a, b)]
        while True:
            a2, b2 = segs[-1]
            if b2 - a2 < 1.7 * med:
                break
            lo, hi = a2 + int(0.6 * med), b2 - int(0.6 * med)
            if hi <= lo:
                break
            cut = lo + int(np.argmin(sm[lo:hi]))
            segs[-1:] = [(a2, cut), (cut, b2)]
        out += segs
    # dải quá thấp (dấu chấm / dấu thanh lẻ) → gộp vào dòng gần nhất
    merged: list[list[int]] = []
    for a, b in out:
        if b - a < max(min_h, 0.35 * med) and merged:
            prev = merged[-1]
            if a - prev[1] < 0.6 * med:
                prev[1] = max(prev[1], b)
                continue
        merged.append([a, b])
    if len(merged) > 1 and merged[0][1] - merged[0][0] < 0.35 * med:
        merged[1][0] = merged[0][0]
        merged.pop(0)
    pad = int(round(0.2 * med))
    return [(max(0, a - pad), min(H, b + pad)) for a, b in merged if b - a >= min_h]


def split_kraken(img: Image.Image) -> list[tuple[int, int, int, int]] | None:
    """Dòng theo Kraken blla → [(x0, y0, x1, y1)]; None nếu không có Kraken / lỗi."""
    if not Path(KRAKEN).exists():
        return None
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "khoi.png"
        img.convert("RGB").save(p)
        out = Path(d) / "seg.json"
        try:
            subprocess.run([KRAKEN, "-i", str(p), str(out), "segment", "-bl"], check=True, capture_output=True,
                           timeout=300)
            seg = json.loads(out.read_text())
        except Exception:
            return None
    boxes = []
    for ln in seg.get("lines", []):
        pts = ln.get("boundary") or ln.get("baseline") or []
        if len(pts) < 2:
            continue
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    boxes.sort(key=lambda b: (b[1] + b[3]) / 2)
    return boxes or None


def split_lines(img: Image.Image, method: str = "chieu_ngang") -> tuple[list[tuple[int, int, int, int]], str]:
    """→ ([(x0, y0, x1, y1)] dòng trong ảnh khối, phương pháp thực dùng)."""
    W, H = img.size
    if method == "kraken":
        k = split_kraken(img)
        if k:
            return [(int(a), int(b), int(c), int(d)) for a, b, c, d in k], "kraken"
    rows = split_projection(img)
    if not rows:
        return [], "chieu_ngang"
    m = _ink(img)
    out = []
    for y0, y1 in rows:  # bề ngang: chỉ phần có mực (+ lề nhỏ)
        cols = np.nonzero(m[y0:y1].any(axis=0))[0]
        if len(cols) == 0:
            continue
        pad = max(4, int(0.02 * W))
        out.append((max(0, int(cols.min()) - pad), y0, min(W, int(cols.max()) + 1 + pad), y1))
    return out, "chieu_ngang"


# --- tách dòng trên CẢ TRANG bằng Kraken + model Muharaf, gán vào khối dots, cắt theo đa giác -------------------------


def kraken_page(img: Image.Image, model: str | None = None) -> list[dict] | None:
    """→ [{"box": (x0, y0, x1, y1), "poly": [(x, y), …], "baseline": [(x, y), …]}] theo thứ tự trên → dưới;
    None nếu không có Kraken / model / lỗi. Thử trên trang chữ tay giấy kẻ: bám dòng chữ (kể cả dòng cong / nghiêng),
    không bám đường kẻ giấy như chiếu ngang (NGHIEN_CUU.md, chủ đề 1)."""
    model = model or KRAKEN_SEG_MODEL
    if not Path(KRAKEN).exists() or not Path(model).exists():
        return None
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "trang.png"
        img.convert("RGB").save(p)
        out = Path(d) / "seg.json"
        try:
            subprocess.run([KRAKEN, "-i", str(p), str(out), "segment", "-bl", "-i", model], check=True,
                           capture_output=True, timeout=600)
            seg = json.loads(out.read_text())
        except Exception:
            return None
    lines = []
    for ln in seg.get("lines", []):
        poly = [(float(x), float(y)) for x, y in (ln.get("boundary") or [])]
        base = [(float(x), float(y)) for x, y in (ln.get("baseline") or [])]
        pts = poly or base
        if len(pts) < 2:
            continue
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        lines.append({"box": (int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1), "poly": poly,
                      "baseline": base})
    lines.sort(key=lambda L: (L["box"][1] + L["box"][3]) / 2)
    return lines


def crop_poly(img: Image.Image, line: dict, pad: int = 4) -> Image.Image:
    """Cắt ảnh dòng theo ĐA GIÁC Kraken: ngoài đa giác tô màu nền (sáng) → bớt nét dòng trên / dưới lọt vào."""
    from PIL import ImageDraw

    W, H = img.size
    x0, y0, x1, y1 = line["box"]
    x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    crop = img.convert("RGB").crop((x0, y0, x1, y1))
    if len(line.get("poly") or []) < 3:
        return crop
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in line["poly"]], fill=255)
    g = np.asarray(crop.convert("L"))
    bg = int(np.percentile(g, 90))  # màu giấy
    nen = Image.new("RGB", crop.size, (bg, bg, bg))
    return Image.composite(crop, nen, mask)


def assign_to_blocks(lines: list[dict], boxes: dict[int, tuple[int, int, int, int]], margin: float = 0.02) -> dict:
    """Gán mỗi dòng vào khối dots chứa TÂM đường chân chữ (hoặc tâm hộp); khối hơi nới rộng. → {chỉ số khối: [dòng]}."""
    out: dict[int, list] = {}
    for L in lines:
        pts = L["baseline"] or [((L["box"][0] + L["box"][2]) / 2, (L["box"][1] + L["box"][3]) / 2)]
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        best, best_area = None, None
        for bi, (x0, y0, x1, y1) in boxes.items():
            mx, my = margin * (x1 - x0), margin * (y1 - y0) + 4
            if x0 - mx <= cx <= x1 + mx and y0 - my <= cy <= y1 + my:
                area = (x1 - x0) * (y1 - y0)
                if best is None or area < best_area:  # khối lồng nhau → chọn khối nhỏ nhất
                    best, best_area = bi, area
        if best is not None:
            out.setdefault(best, []).append(L)
    return out
