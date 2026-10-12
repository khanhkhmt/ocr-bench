"""Tiền xử lý THẬN TRỌNG, tách hai ảnh:

- ảnh HÌNH HỌC (geom): ảnh gốc chỉ được xoay chỉnh nghiêng / phóng — giữ nguyên điểm ảnh. Dùng để CẮT BẰNG CHỨNG cho
  người duyệt và làm hệ toạ độ chung (mọi bbox trong JSON tính trên ảnh này).
- ảnh để ĐỌC (rec): geom + làm phẳng nền, tăng tương phản (ocrbench.preprocess, tự bật khi ảnh cần), và tuỳ chọn: xoá
  dòng kẻ, che lỗ đục, làm nét.

Theo khảo sát chéo 8 bộ dữ liệu chữ Ả Rập (arXiv 2608.22366): với VLM, nhị phân hoá / khử nhiễu / tăng tương phản
làm KÉM đi, chỉ làm nét (sharpen) giúp (Qwen2.5-VL trên Muharaf: CER 70,4 → 67,2). Vì vậy ba bước mới mặc định TẮT; bật
từng bước khi đo trên tập dev của chính bộ hồ sơ thấy CER giảm.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

DEFAULTS = {"deskew": True, "upscale": True, "flatten": True, "contrast": True,
            "remove_rules": False, "mask_holes": False, "sharpen": False}


def prepare(img: Image.Image, cfg: dict | None = None) -> tuple[Image.Image, Image.Image, dict]:
    from ocrbench.preprocess import DEFAULTS as OB, preprocess

    c = {**DEFAULTS, **(cfg or {})}
    img = img.convert("RGB")
    geom, info_g = preprocess(img, {**OB, "flatten": False, "contrast": False, "deskew": c["deskew"],
                                    "upscale": c["upscale"]})
    rec, info_r = preprocess(geom, {**OB, "flatten": c["flatten"], "contrast": c["contrast"], "deskew": False,
                                    "upscale": False})
    info = {"geometry": info_g, "photometric": info_r}
    if c["remove_rules"]:
        rec, info["remove_rules"] = remove_ruled_lines(rec)
    if c["mask_holes"]:
        rec, info["mask_holes"] = mask_punch_holes(rec)
    if c["sharpen"]:
        rec = rec.filter(ImageFilter.UnsharpMask(radius=1.5, percent=80, threshold=2))
        info["sharpen"] = True
    return geom, rec, info


def remove_ruled_lines(img: Image.Image, min_len_frac: float = 0.3, max_thick: int = 6) -> tuple[Image.Image, dict]:
    """Xoá đường kẻ ngang in sẵn của giấy / mẫu đơn mà không cắt nét chữ đè lên:
    1. mực = điểm tối hơn hẳn nền; đường kẻ = mở hình thái học bằng thanh ngang dài ≥ min_len_frac bề rộng trang;
    2. chỉ nhận dải mảnh (≤ max_thick px);
    3. tô màu nền lên điểm của đường kẻ, TRỪ cột nào có mực ngay trên VÀ ngay dưới đường kẻ (nét chữ cắt ngang qua)."""
    import cv2

    rgb = np.asarray(img.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    bg = float(np.median(gray))
    ink = (gray < 0.7 * bg).astype(np.uint8)
    W = gray.shape[1]
    k = max(15, int(min_len_frac * W))
    rules = cv2.morphologyEx(ink, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (k, 1)))
    rules = cv2.dilate(rules, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 1))) & ink  # phép mở hụt 1–3 px ở hai đầu
    n, lab, stats, _ = cv2.connectedComponentsWithStats(rules, 8)
    out = rgb.copy()
    paper = gray > 0.9 * bg
    fill = np.median(rgb[paper], axis=0) if paper.any() else np.array([255, 255, 255])
    H = gray.shape[0]
    removed, kept_cols = 0, 0
    for i in range(1, n):
        x, y, w, h, _ = stats[i]
        if h > max_thick or w < k:
            continue
        removed += 1
        comp = lab[y:y + h, x:x + w] == i
        has = comp.any(0)
        top = y + comp.argmax(0)
        bot = y + h - 1 - comp[::-1].argmax(0)
        for c in np.flatnonzero(has):
            xa, t, b = x + c, top[c], bot[c]
            # nét chữ cắt qua: có mực trong 2–4 px ngay trên VÀ ngay dưới dải đường kẻ (bỏ 1 px viền mờ)
            above = ink[max(0, t - 4):max(0, t - 1), xa].any()
            below = ink[min(H, b + 2):min(H, b + 5), xa].any()
            if above and below:
                kept_cols += 1
                continue
            rows = np.flatnonzero(comp[t - y:b - y + 1, c]) + t
            out[max(0, rows[0] - 1):min(H, rows[-1] + 2), xa] = fill  # nới 1 px: viền khử răng cưa của đường kẻ
    if not removed:
        return img, {"lines": 0}
    return Image.fromarray(out), {"lines": removed, "kept_crossing_cols": int(kept_cols)}


def mask_punch_holes(img: Image.Image, margin_frac: float = 0.12, r_range=(0.006, 0.03)) -> tuple[Image.Image, dict]:
    """Lỗ đục lưu hồ sơ: mảng TRÒN, ĐẶC, đều màu (tối — nền máy scan — hoặc sáng hơn hẳn giấy) nằm sát mép trái /
    phải / trên (trong `margin_frac`) → tô màu nền giấy. Model hay đọc lỗ thành "ه" / "٥" / "o", và lỗ làm khung dòng
    kéo dài ra tới mép giấy. Chữ "o" / "ه" thật rỗng ruột nên không lọt qua điều kiện ĐẶC."""
    import cv2

    rgb = np.asarray(img.convert("RGB")).copy()
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    H, W = gray.shape
    bg = float(np.median(gray))
    paper = np.median(rgb[gray > 0.85 * bg], axis=0) if (gray > 0.85 * bg).any() else np.array([255, 255, 255])
    r_min, r_max = max(4, r_range[0] * W), max(8, r_range[1] * W)
    holes = []
    for mask in ((gray < 0.35 * bg), (gray > min(250, 1.12 * bg))):
        n, lab, stats, cent = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
        for i in range(1, n):
            x, y, w, h, area = stats[i]
            r = (w + h) / 4
            if not (r_min <= r <= r_max) or not (0.8 <= w / max(1, h) <= 1.25):
                continue
            cx, cy = cent[i]
            if min(cx, W - cx) > margin_frac * W and cy > margin_frac * H:
                continue
            if area / (np.pi * r * r) < 0.85:  # không đặc (vòng chữ o, nét cong) → bỏ
                continue
            disk = np.zeros_like(gray, bool)
            cv2.circle(disk.view(np.uint8), (int(cx), int(cy)), int(1.2 * r) + 2, 1, -1)
            rgb[disk] = paper
            holes.append([int(cx), int(cy), int(r)])
    return Image.fromarray(rgb), {"holes": holes}
