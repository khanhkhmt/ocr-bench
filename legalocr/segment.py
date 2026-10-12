"""Tách trang thành DÒNG (đơn vị đọc của model HTR, vd. Baseer__Nakba được huấn luyện trên ảnh dòng ~614×52 px) và gắn
nhãn vùng không phải chữ thường (chữ ký, con dấu, vân tay, tem) để không đưa chúng cho LLM sửa.

- KrakenSegmenter     : blla của kraken (tài liệu lịch sử / viết tay, phải→trái) — qua tiến trình con của ocrbench
                        (venv riêng: bash inference/setup_kraken.sh). Đa giác + đường chân chữ theo thứ tự đọc.
- ProjectionSegmenter : dự phòng không cần model: hình chiếu ngang của mực → các dải dòng. Chỉ hợp trang một cột,
                        dòng gần thẳng (và để test).
- detect_nontext      : chữ ký (YOLOS, Apache-2.0, đã dùng trong ocrbench), con dấu (YOLOS stamp detector, Apache-2.0),
                        + vùng mực màu / mảng tối (ocrbench.pictures: dấu đỏ/tím, vân tay, tem).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from .doc import Line

SIGNATURE_MODEL = "mdefrance/yolos-base-signature-detection"
STAMP_MODEL = "Ooredoo-Group/ooredoo-stamp-detection"


def _line(i: int, bbox, polygon=None) -> Line:
    x1, y1, x2, y2 = (int(v) for v in bbox)
    poly = polygon or [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
    return Line(id=f"l{i:03d}", bbox=[x1, y1, x2, y2], polygon=[list(map(int, p)) for p in poly])


class KrakenSegmenter:
    def __init__(self, python: str | None = None, device: str = "cpu", height: int | None = 1400,
                 text_direction: str = "horizontal-rl"):
        from ocrbench.adapters.kraken_layout import KrakenWorker, default_python

        py = python or default_python()
        if not py:
            raise RuntimeError("chưa có venv kraken: chạy `bash inference/setup_kraken.sh`")
        self.worker = KrakenWorker(py, device=device, height=height)
        self.text_direction = text_direction

    def segment(self, image) -> list[Line]:
        from ocrbench.adapters.kraken_layout import drop_faint_lines, parse_lines

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "page.png"
            image.save(p)
            seg = self.worker.segment(str(p), self.text_direction)
        lines = [_line(i, ln["bbox"], ln["polygon"]) for i, ln in enumerate(drop_faint_lines(image, parse_lines(seg)))]
        return extend_to_ink(merge_fragments(lines), image) if fragmented(lines) else lines


def fragmented(lines: list[Line], narrow: float = 0.35, share: float = 0.5) -> bool:
    """Trang bị tách thành MẢNH (đa số "dòng" hẹp hơn `narrow` × bề rộng vùng chữ) — chỉ khi đó mới gộp mảnh; trang
    đánh máy dòng liền thì để nguyên kết quả kraken (gộp / nới trên trang đó chỉ có hại: đo trên công văn 1972)."""
    if len(lines) < 4:
        return False
    x0, x1 = min(l.bbox[0] for l in lines), max(l.bbox[2] for l in lines)
    W = max(1, x1 - x0)
    return sum(1 for l in lines if l.bbox[2] - l.bbox[0] < narrow * W) / len(lines) >= share


def merge_fragments(lines: list[Line], min_overlap: float = 0.6, rtl: bool = True, max_gap: float = 2.5) -> list[Line]:
    """Gộp các mảnh nằm trên CÙNG một dòng (chồng nhau theo chiều dọc ≥ min_overlap chiều cao mảnh thấp hơn).
    Đo trên một trang Muharaf viết tay chữ to, thưa: blla mặc định trả 35 mảnh cỡ từ cho 12 dòng — model dòng đọc mảnh
    rời mất ngữ cảnh và thứ tự. Dòng đã liền (một mảnh / dòng) đi qua không đổi. Thứ tự: trên → dưới, trong dòng phải → trái."""
    if len(lines) < 2:
        return lines
    def can_join(g: list[Line], h: list[Line]) -> bool:
        gy1, gy2 = min(x.bbox[1] for x in g), max(x.bbox[3] for x in g)
        hy1, hy2 = min(x.bbox[1] for x in h), max(x.bbox[3] for x in h)
        ov = min(gy2, hy2) - max(gy1, hy1)
        if ov < min_overlap * min(gy2 - gy1, hy2 - hy1):
            return False
        if any(_hoverlap(a.bbox, b.bbox) > 0.5 for a in g for b in h):
            return False
        if max(gy2 - gy1, hy2 - hy1) > 1.8 * min(gy2 - gy1, hy2 - hy1):  # nét chữ ký cao không nuốt dòng thường
            return False
        # khe ngang giữa hai mảnh gần nhau nhất ≤ max_gap × chiều cao: khe giữa hai từ thì gộp, khe giữa hai CỘT
        # (ô công chứng bên phải, chữ ký bên trái cùng độ cao) thì không
        gap = min(max(a.bbox[0], b.bbox[0]) - min(a.bbox[2], b.bbox[2]) for a in g for b in h)
        return gap <= max_gap * max(gy2 - gy1, hy2 - hy1)

    groups: list[list[Line]] = [[ln] for ln in lines]
    changed = True
    while changed:  # gộp lặp tới khi ổn định (mảnh giữa dòng đến sau vẫn nối được hai mảnh hai đầu)
        changed = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if can_join(groups[i], groups[j]):
                    groups[i] += groups.pop(j)
                    changed = True
                    break
            if changed:
                break
    if len(groups) == len(lines):
        return lines
    out = []
    for g in sorted(groups, key=lambda g: min(x.bbox[1] for x in g)):
        g.sort(key=lambda x: -x.bbox[2] if rtl else x.bbox[0])
        bbox = [min(x.bbox[0] for x in g), min(x.bbox[1] for x in g), max(x.bbox[2] for x in g), max(x.bbox[3] for x in g)]
        poly = g[0].polygon if len(g) == 1 else None
        out.append(_line(len(out), bbox, poly))
    return out


def extend_to_ink(lines: list[Line], image, core: float = 0.2, min_rel_height: float = 0.35,
                  ink_thresh: float = 0.6, max_extend: float = 3.0) -> list[Line]:
    """Sau khi gộp: (1) bỏ mảnh tí hon (thấp hơn min_rel_height × trung vị — dấu chấm, vết bẩn); (2) nới khung NGANG tới
    hết mực trong dải lõi của dòng (bỏ `core` trên / dưới để khỏi ăn sang dòng bên cạnh) — kraken hay hụt từ đầu / cuối
    dòng. Dòng đã nới mất đa giác (thay bằng khung chữ nhật)."""
    if not lines:
        return lines
    g = np.asarray(image.convert("L")).astype(np.float32) / 255
    ink = g < ink_thresh * np.median(g)
    hs = sorted(ln.bbox[3] - ln.bbox[1] for ln in lines)
    med = hs[len(hs) // 2]
    out = []
    for ln in lines:
        x1, y1, x2, y2 = ln.bbox
        if y2 - y1 < min_rel_height * med:
            continue
        a, b = y1 + int(core * (y2 - y1)), y2 - int(core * (y2 - y1))
        # chỉ nới trong phạm vi `max_extend` × chiều cao dòng, và không lấn sang khung của dòng khác cùng độ cao (cột bên)
        lim = int(max_extend * (y2 - y1))
        lo, hi = max(0, x1 - lim), min(ink.shape[1], x2 + lim)
        for o in lines:
            if o is ln or min(o.bbox[3], y2) - max(o.bbox[1], y1) <= 0.3 * (y2 - y1):
                continue
            if o.bbox[2] <= x1:
                lo = max(lo, o.bbox[2] + 1)
            elif o.bbox[0] >= x2:
                hi = min(hi, o.bbox[0] - 1)
        cols = np.flatnonzero(ink[a:max(a + 1, b), lo:hi].sum(0) > 1) + lo
        if cols.size:
            nx1, nx2 = min(x1, int(cols[0])), max(x2, int(cols[-1]) + 1)
            if (nx1, nx2) != (x1, x2):
                out.append(_line(len(out), [nx1, y1, nx2, y2]))
                continue
        out.append(_line(len(out), ln.bbox, ln.polygon))
    return _dedupe(out)


def _dedupe(lines: list[Line], min_overlap: float = 0.5) -> list[Line]:
    """Sau khi nới: hai khung chồng dọc ≥ min_overlap chiều cao khung thấp hơn = cùng một dòng (chữ viết xiên làm
    kraken tách đôi) → gộp."""
    out: list[Line] = []
    for ln in sorted(lines, key=lambda l: l.bbox[1]):
        prev = out[-1] if out else None
        if prev is not None:
            ov = min(ln.bbox[3], prev.bbox[3]) - max(ln.bbox[1], prev.bbox[1])
            h1, h2 = ln.bbox[3] - ln.bbox[1], prev.bbox[3] - prev.bbox[1]
            if ov >= min_overlap * min(h1, h2) and max(h1, h2) <= 1.8 * min(h1, h2):
                b = [min(ln.bbox[0], prev.bbox[0]), min(ln.bbox[1], prev.bbox[1]), max(ln.bbox[2], prev.bbox[2]),
                     max(ln.bbox[3], prev.bbox[3])]
                out[-1] = _line(len(out) - 1, b)
                continue
        out.append(_line(len(out), ln.bbox, ln.polygon))
    return out


def _hoverlap(a, b) -> float:
    """Tỉ lệ chồng ngang (so với mảnh hẹp hơn) — hai mảnh chồng ngang nhiều là hai dòng khác nhau xếp chồng."""
    ov = min(a[2], b[2]) - max(a[0], b[0])
    return max(0, ov) / max(1, min(a[2] - a[0], b[2] - b[0]))

    def close(self):
        self.worker.close()


class ProjectionSegmenter:
    """mode="gap": dòng = dải hàng có mực, ngăn bằng khe trắng (chữ in, dòng thưa).
    mode="valley": chữ viết tay hay chạm dòng trên / dưới nên không có khe trắng → ước lượng khoảng cách dòng bằng tự
    tương quan của hình chiếu đã làm mượt, lấy các đỉnh cách nhau ≥ 0,6 khoảng đó, cắt ở điểm thấp nhất giữa hai đỉnh."""

    def __init__(self, min_height: int = 8, gap: int = 3, ink_thresh: float = 0.6, mode: str = "gap"):
        self.min_height, self.gap, self.ink_thresh, self.mode = min_height, gap, ink_thresh, mode

    def segment(self, image) -> list[Line]:
        g = np.asarray(image.convert("L")).astype(np.float32) / 255
        paper = np.median(g)
        ink = g < self.ink_thresh * paper
        if self.mode == "valley":
            return self._valleys(ink)
        rows = ink.sum(1)
        on = rows > max(2, 0.005 * ink.shape[1])
        bands, start, off = [], None, 0
        for y, v in enumerate(on):
            if v:
                if start is None:
                    start = y
                off = 0
            elif start is not None:
                off += 1
                if off > self.gap:
                    bands.append((start, y - off + 1))
                    start, off = None, 0
        if start is not None:
            bands.append((start, len(on)))
        bands = [b for b in bands if b[1] - b[0] >= self.min_height]
        lines = []
        H = ink.shape[0]
        for k, (y1, y2) in enumerate(bands):
            # dải lõi chỉ gồm hàng nhiều mực → nới lên / xuống để lấy dấu chấm, hamza, đuôi chữ (không quá nửa khe với
            # dòng bên cạnh): cắt sát làm mất hamza ("أحمد" → "احمد") và Tesseract trả rỗng
            h = y2 - y1
            top = max(0, y1 - int(0.45 * h), (bands[k - 1][1] + y1) // 2 if k else 0)
            bot = min(H, y2 + int(0.35 * h), (y2 + bands[k + 1][0]) // 2 if k + 1 < len(bands) else H)
            cols = np.flatnonzero(ink[top:bot].any(0))
            if not cols.size:
                continue
            lines.append(_line(len(lines), [int(cols[0]), top, int(cols[-1]) + 1, bot]))
        return lines

    def _valleys(self, ink: np.ndarray) -> list[Line]:
        H, W = ink.shape
        # bỏ cụm mực rất nhỏ (bụi, chấm lẻ) khỏi hình chiếu; cột mép giấy (bóng scan) cũng bỏ
        prof = ink[:, int(0.02 * W):int(0.98 * W)].sum(1).astype(np.float64)
        if prof.max() <= 0:
            return []
        k = max(3, H // 150)
        smooth = np.convolve(prof, np.ones(k) / k, mode="same")
        x = smooth - smooth.mean()
        ac = np.correlate(x, x, mode="full")[H - 1:]
        lo, hi = max(10, H // 80), max(20, H // 3)
        # tự tương quan giảm dần từ độ trễ 0: khoảng dòng = đỉnh cao nhất SAU điểm lõm đầu tiên (không phải ngay tại lo)
        m = lo
        while m + 1 < hi and ac[m + 1] <= ac[m]:
            m += 1
        period = m + int(np.argmax(ac[m:hi])) if hi > m + 1 else max(lo, H // 10)
        sig = max(2.0, period / 6)
        t = np.arange(-int(3 * sig), int(3 * sig) + 1)
        gk = np.exp(-t ** 2 / (2 * sig ** 2))
        sm = np.convolve(prof, gk / gk.sum(), mode="same")
        peaks = [y for y in range(1, H - 1) if sm[y] >= sm[y - 1] and sm[y] > sm[y + 1] and sm[y] >= 0.15 * sm.max()]
        kept: list[int] = []
        for y in sorted(peaks, key=lambda y: -sm[y]):  # đỉnh cao trước; bỏ đỉnh quá gần đỉnh đã giữ
            if all(abs(y - z) >= 0.6 * period for z in kept):
                kept.append(y)
        kept.sort()
        cuts = [0] + [a + int(np.argmin(sm[a:b])) for a, b in zip(kept, kept[1:])] + [H]
        lines = []
        for y1, y2 in zip(cuts, cuts[1:]):
            band = ink[y1:y2]
            rows = np.flatnonzero(band.sum(1) > 0)
            cols = np.flatnonzero(band.sum(0) > 0)
            if rows.size == 0 or rows[-1] - rows[0] < self.min_height:
                continue
            lines.append(_line(len(lines), [int(cols[0]), y1 + int(rows[0]), int(cols[-1]) + 1, y1 + int(rows[-1]) + 1]))
        return lines


def overlap_frac(a, b) -> float:
    """Tỉ lệ diện tích khung a nằm trong khung b."""
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area = max(1, (a[2] - a[0]) * (a[3] - a[1]))
    return inter / area


def detect_nontext(image, lines: list[Line], signatures: bool | str = True, stamps: bool | str = True,
                   pictures: bool = True, threshold: float = 0.45) -> dict[str, list[list[int]]]:
    """→ {"Signature": [bbox...], "Stamp": [...], "Picture": [...]}; model nào chưa tải được thì bỏ qua (ghi "errors")."""
    from ocrbench.pictures import find_pictures, find_signatures

    out: dict[str, list] = {"Signature": [], "Stamp": [], "Picture": [], "errors": []}
    for kind, flag, default in (("Signature", signatures, SIGNATURE_MODEL), ("Stamp", stamps, STAMP_MODEL)):
        if flag:
            try:
                out[kind] = find_signatures(image, default if flag is True else flag, threshold)
            except Exception as e:  # không có mạng / chưa có trọng số: không chặn cả trang
                out["errors"].append(f"{kind}: {type(e).__name__}: {str(e)[:120]}")
    if pictures and lines:
        from ocrbench.adapters.kraken_layout import text_mask

        mask, lh = text_mask(image.size, [{"polygon": ln.polygon, "bbox": ln.bbox} for ln in lines])
        try:
            out["Picture"] = [p["bbox"] for p in find_pictures(image, text_mask=mask, line_height=lh)]
        except Exception as e:
            out["errors"].append(f"Picture: {type(e).__name__}: {str(e)[:120]}")
    return out


def label_regions(lines: list[Line], boxes: dict[str, list[list[int]]], min_overlap: float = 0.5) -> None:
    """Dòng nằm phần lớn trong chữ ký / con dấu / hình → region tương ứng (vẫn được đọc — con dấu thường có chữ, vd.
    "كاتب العدل" hay chữ Hebrew — nhưng không đưa LLM sửa và đánh dấu riêng trong bản xuất)."""
    for ln in lines:
        for kind in ("Signature", "Stamp", "Picture"):
            if any(overlap_frac(ln.bbox, b) >= min_overlap for b in boxes.get(kind, [])):
                ln.region = kind
                break


def line_crops(image, lines: list[Line], pad: int = 3, min_height: int = 48) -> dict[str, object]:
    """Ảnh từng dòng để ĐỌC: tô trắng ngoài đa giác (chặn nét dòng bên cạnh), phóng dòng thấp."""
    from ocrbench.adapters.kraken_layout import line_crop

    return {ln.id: line_crop(image, {"bbox": ln.bbox, "polygon": ln.polygon}, pad, min_height) for ln in lines}
