"""Màu mực từng dòng: tách WATERMARK / dấu đỏ khỏi chữ, và xoá mực đỏ đè lên dòng chữ đen trước khi đọc.

Đo trên công văn 1972 có watermark "اليوم السابع" (đỏ hồng, lặp khắp trang): kraken nhận watermark là dòng, Tesseract
đọc ra "النتبائع" / "oqull". Mực đỏ phản xạ mạnh kênh ĐỎ → trên kênh đỏ nó gần như trắng, còn mực đen / xanh (bút bi)
vẫn tối. Nên: dòng mà phần lớn mực là màu đỏ và gần như không có điểm tối trên kênh đỏ = watermark / dấu đỏ.
Không xoá mực xanh (chữ viết tay bút bi xanh là NỘI DUNG).
"""

from __future__ import annotations

import numpy as np


def _hsv(a: np.ndarray):
    mx, mn = a.max(2), a.min(2)
    s = (mx - mn) / np.maximum(mx, 1e-6)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, s, mx


def ink_profile(crop) -> dict:
    a = np.asarray(crop.convert("RGB")).astype(np.float32)
    gray = a.mean(2)
    bg = float(np.percentile(gray, 90)) or 1.0
    ink = gray < 0.8 * bg
    if ink.sum() < 10:
        return {"ink": 0.0, "colored": 0.0, "red": 0.0, "dark": 0.0}
    h, s, _ = _hsv(a)
    sat = s > 0.3
    red = sat & ((h < 25) | (h > 320))
    r_bg = float(np.percentile(a[..., 0], 90)) or 1.0
    dark = a[..., 0] < 0.6 * r_bg            # tối trên kênh đỏ = mực đen / xanh, không phải mực đỏ
    n = ink.sum()
    return {"ink": float(n / ink.size), "colored": float((sat & ink).sum() / n), "red": float((red & ink).sum() / n),
            "dark": float((dark & ink).sum() / n)}


def is_red_mark(p: dict, min_red: float = 0.55, max_dark: float = 0.2) -> bool:
    """Dòng là watermark / dấu mực đỏ (không phải chữ cần đọc)."""
    return p["ink"] > 0 and p["red"] >= min_red and p["dark"] <= max_dark


def suppress_red(crop):
    """(Tắt mặc định: trên công văn có watermark, CER 19,4% → 19,8% — không giúp.) Xoá mực ĐỎ (watermark, dấu đỏ) đè lên dòng chữ đen / xanh: điểm đỏ bão hoà mà kênh đỏ vẫn sáng → màu giấy."""
    from PIL import Image

    a = np.asarray(crop.convert("RGB")).astype(np.float32)
    h, s, _ = _hsv(a)
    r_bg = float(np.percentile(a[..., 0], 90)) or 1.0
    red = (s > 0.25) & ((h < 25) | (h > 320)) & (a[..., 0] > 0.6 * r_bg)
    if not red.any():
        return crop
    light = a.mean(2) >= np.percentile(a.mean(2), 60)
    paper = np.median(a[light].reshape(-1, 3), 0) if light.any() else np.array([255.0, 255.0, 255.0])
    a[red] = paper
    return Image.fromarray(a.astype(np.uint8))
