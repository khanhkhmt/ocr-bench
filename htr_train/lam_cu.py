"""Làm CŨ ảnh dòng chữ (tăng cường dữ liệu) — giả lập giấy tờ pháp lý 1970s của khách: giấy ố vàng / vết bẩn,
giấy kẻ dòng, mực thấm mặt sau, CON DẤU và VÂN TAY màu đè lên chữ, mực nhạt / nhoè, chụp điện thoại (nghiêng, nén JPEG).

Chỉ đổi ẢNH, không đổi nhãn → mọi phép biến đổi giữ chữ đọc được (không xoá nét, không che kín). Không nhị phân hoá.
    from htr_train.lam_cu import lam_cu
    img2 = lam_cu(img, random.Random(0), ban=img_khac)   # ban: ảnh dòng khác làm "mực thấm mặt sau"
    python -m htr_train.lam_cu <ảnh dòng> <ảnh ra.jpg> [--n 8]   # xem thử: lưới n biến thể
"""

from __future__ import annotations

import io
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

GIAY = [(236, 224, 196), (232, 216, 180), (222, 205, 165), (240, 232, 210), (215, 196, 158)]
MAU_DAU = [(110, 60, 150), (60, 70, 160), (170, 50, 60), (40, 100, 150)]  # tím, xanh, đỏ, xanh lam


def _nen_giay(w: int, h: int, rng: random.Random) -> np.ndarray:
    """Nền giấy ố: màu gốc + loang không đều (nhiễu tần số thấp) + hạt giấy."""
    base = np.array(rng.choice(GIAY), np.float32)
    small = np.random.default_rng(rng.randrange(1 << 30)).normal(0, 1, (max(2, h // 24), max(2, w // 24), 1))
    loang = np.asarray(Image.fromarray(((small - small.min()) / (np.ptp(small) + 1e-6) * 255).astype(np.uint8)[..., 0])
                       .resize((w, h), Image.BICUBIC), np.float32)[..., None] / 255.0
    hat = np.random.default_rng(rng.randrange(1 << 30)).normal(0, rng.uniform(2, 6), (h, w, 1))
    nen = base * (1 - rng.uniform(0.05, 0.18) * loang) + hat
    return np.clip(nen, 0, 255)


def _ghep_muc(img: Image.Image, nen: np.ndarray, rng: random.Random) -> np.ndarray:
    """Đặt nét mực của ảnh gốc lên nền giấy mới: độ đậm mực = độ tối tương đối của ảnh gốc (giữ nguyên hình nét)."""
    g = np.asarray(img.convert("L"), np.float32)
    bg = np.percentile(g, 90)
    muc = np.clip((bg - g) / max(1.0, bg - np.percentile(g, 1)), 0, 1)[..., None]  # 0 = giấy, 1 = mực đậm nhất
    rgb = np.asarray(img.convert("RGB"), np.float32)
    mau_muc = rgb * 0.5 + np.array(rng.choice([(20, 20, 30), (30, 40, 90), (40, 30, 30)]), np.float32) * 0.5
    dam = rng.uniform(0.75, 1.0)  # mực phai
    return nen * (1 - muc * dam) + mau_muc * (muc * dam)


def _ke_dong(a: np.ndarray, rng: random.Random) -> None:
    h, w, _ = a.shape
    mau = np.array(rng.choice([(120, 150, 200), (160, 170, 210), (190, 150, 150)]), np.float32)
    for y in range(rng.randint(h // 3, h - 2), h, max(18, h)):
        a[y:y + 1] = a[y:y + 1] * 0.6 + mau * 0.4


def _vet_ban(a: np.ndarray, rng: random.Random) -> None:
    h, w, _ = a.shape
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for _ in range(rng.randint(1, 3)):
        cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(h * 0.3, h * 1.5)
        d.ellipse((cx - r, cy - r * rng.uniform(0.4, 1), cx + r, cy + r * rng.uniform(0.4, 1)), fill=rng.randint(40, 110))
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(h * 0.2)), np.float32)[..., None] / 255.0
    a *= 1 - m * np.array([0.15, 0.25, 0.4], np.float32)  # vết nâu


def _muc_tham(a: np.ndarray, ban: Image.Image | None, rng: random.Random) -> None:
    """Mực thấm mặt sau: chữ của dòng KHÁC, lật ngang, rất nhạt và nhoè."""
    if ban is None:
        return
    h, w, _ = a.shape
    b = ban.convert("L").transpose(Image.FLIP_LEFT_RIGHT).resize((w, h)).filter(ImageFilter.GaussianBlur(rng.uniform(1, 2.5)))
    g = np.asarray(b, np.float32)
    muc = np.clip((np.percentile(g, 90) - g) / 255.0, 0, 1)[..., None]
    a *= 1 - muc * rng.uniform(0.12, 0.3)


def _con_dau(a: np.ndarray, rng: random.Random) -> None:
    """Con dấu tròn / bầu dục bán trong suốt (2 vòng + vạch chữ giả) — đè lên một phần dòng, không che kín."""
    h, w, _ = a.shape
    r = rng.uniform(h * 0.6, h * 1.4)
    cx, cy = rng.uniform(r * 0.3, w - r * 0.3), rng.uniform(-r * 0.2, h + r * 0.2)
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    ry = r * rng.uniform(0.75, 1.0)
    d.ellipse((cx - r, cy - ry, cx + r, cy + ry), outline=255, width=max(2, int(r * 0.07)))
    d.ellipse((cx - r * 0.72, cy - ry * 0.72, cx + r * 0.72, cy + ry * 0.72), outline=255, width=max(1, int(r * 0.04)))
    for k in range(rng.randint(8, 16)):  # "chữ" quanh vành: các vạch ngắn
        t = 2 * math.pi * k / 16 + rng.uniform(-0.1, 0.1)
        x1, y1 = cx + r * 0.86 * math.cos(t), cy + ry * 0.86 * math.sin(t)
        d.line((x1, y1, x1 + r * 0.08 * math.cos(t + 1.5), y1 + ry * 0.08 * math.sin(t + 1.5)), fill=255, width=2)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(0.8)), np.float32)[..., None] / 255.0
    loang = np.random.default_rng(rng.randrange(1 << 30)).uniform(0.5, 1.0, (h, w, 1))  # mực dấu không đều
    alpha = m * loang * rng.uniform(0.35, 0.65)
    a[:] = a * (1 - alpha) + np.array(rng.choice(MAU_DAU), np.float32) * alpha


def _van_tay(a: np.ndarray, rng: random.Random) -> None:
    """Vân tay: các đường cong đồng tâm gợn sóng, màu mực dấu, bán trong suốt."""
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy, s = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(h * 0.6, h * 1.2)
    rr = np.sqrt(((xx - cx) / 1.0) ** 2 + ((yy - cy) / 1.4) ** 2)
    sang = 0.5 + 0.5 * np.sin(rr / rng.uniform(2.2, 3.5) + np.sin(xx / 9) * 1.5)
    bao = np.clip(1 - rr / s, 0, 1)
    alpha = (sang * bao * rng.uniform(0.3, 0.55))[..., None]
    a[:] = a * (1 - alpha) + np.array(rng.choice(MAU_DAU), np.float32) * alpha


def _chup(img: Image.Image, rng: random.Random) -> Image.Image:
    """Như ảnh chụp điện thoại: nghiêng nhẹ, mờ nhẹ, sáng không đều, nén JPEG."""
    bg = tuple(int(v) for v in np.asarray(img).reshape(-1, 3)[:50].mean(0))
    img = img.rotate(rng.uniform(-1.5, 1.5), resample=Image.BICUBIC, expand=False, fillcolor=bg)
    if rng.random() < 0.6:
        img = img.filter(ImageFilter.GaussianBlur(rng.uniform(0.3, 1.1)))
    a = np.asarray(img, np.float32)
    w = a.shape[1]
    a *= np.linspace(rng.uniform(0.85, 1.0), rng.uniform(0.9, 1.05), w, dtype=np.float32)[None, :, None]
    buf = io.BytesIO()
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(buf, "JPEG", quality=rng.randint(35, 85))
    return Image.open(buf).convert("RGB")


def lam_cu(img: Image.Image, rng: random.Random, ban: Image.Image | None = None, muc: float = 1.0) -> Image.Image:
    """Một biến thể làm cũ ngẫu nhiên. muc ∈ (0, 1]: cường độ (xác suất từng hiệu ứng nhân với muc)."""
    img = img.convert("RGB")
    w, h = img.size
    a = _ghep_muc(img, _nen_giay(w, h, rng), rng) if rng.random() < 0.85 * muc else np.asarray(img, np.float32).copy()
    if rng.random() < 0.3 * muc:
        _ke_dong(a, rng)
    if rng.random() < 0.4 * muc:
        _vet_ban(a, rng)
    if rng.random() < 0.3 * muc:
        _muc_tham(a, ban, rng)
    if rng.random() < 0.35 * muc:
        _con_dau(a, rng)
    if rng.random() < 0.15 * muc:
        _van_tay(a, rng)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return _chup(out, rng) if rng.random() < 0.8 * muc else out


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("anh")
    ap.add_argument("ra")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--ban", default=None, help="ảnh dòng khác làm mực thấm mặt sau")
    a = ap.parse_args()
    img = Image.open(a.anh).convert("RGB")
    ban = Image.open(a.ban) if a.ban else img
    tiles = [img] + [lam_cu(img, random.Random(i), ban=ban) for i in range(a.n)]
    W = max(t.width for t in tiles)
    sheet = Image.new("RGB", (W, sum(t.height + 6 for t in tiles)), "white")
    y = 0
    for t in tiles:
        sheet.paste(t, (W - t.width, y))
        y += t.height + 6
    sheet.save(a.ra, quality=85)
    print("✔", a.ra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
