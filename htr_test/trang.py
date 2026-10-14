"""Chia một TRANG thành khối + dòng — dùng chung cho web ft3/ft4 (app_ft.py) và chấm cả trang (cham_trang.py).

    from htr_test.trang import nap_dots, phan_trang, sua_chu
    conv = nap_dots(0)
    r = phan_trang(conv, page, path)   # r["img"], r["blocks"], r["jobs"] = [(khối, hộp dòng, ảnh dòng)], …

Sửa sau buổi thử dots trên 4 trang thật (htr_test/thu_dots.py, results-htr/thu_dots, 2026-10-14):
  1. dots đọc trên ảnh PHÓNG tới cạnh dài `canh` px (mặc định 2400 = ×1,5 trang WhatsApp 1600 px): chữ đánh máy
     image_1 77,6% → 90,3%, image_4 88,7% → 90,5%; image_3 (×1: không ra khối nào) → đọc được cả thân văn bản.
     ×2 (3200 px) hết VRAM trên T4 → hết VRAM thì tự đọc lại ở ảnh không phóng. Toạ độ khối chia lại về ảnh gốc:
     tách dòng (Kraken) và ảnh dòng cho model chữ tay GIỮ NGUYÊN như trước (không phóng).
  2. dots không ra khối chữ nào (JSON hỏng / chạy vòng tới trần token) → DỰ PHÒNG: cả trang là một khối, Kraken tách
     dòng cả trang, model chữ tay đọc từng dòng — trước đây trang như vậy ra rỗng.
  3. Chặn vòng lặp dài hơn: dots từng lặp nguyên một dòng (~100 token) tới trần — bộ chặn cũ chỉ bắt chu kỳ ≤ 60 token.
  4. Khối HEBREW (khối công chứng): dots đọc ra chữ Hebrew → KHÔNG đưa cho model chữ tay Ả Rập (chúng bịa chữ Ả Rập ở
     đó: image_3 cả trang 64% → ~80% khi bỏ), giữ chữ dots, đánh dấu b["hebrew"] = True.
  5. sua_chu: dots ở ảnh phóng hay ra chữ Ba Tư (ی ک ۃ ۸…) thay chữ Ả Rập (ي ك ة ٨) và tách "و" khỏi từ sau
     ("و نحن") — đổi về chữ Ả Rập chuẩn (cùng hình chữ, đúng mã; "و" không bao giờ đứng riêng một từ).
"""

from __future__ import annotations

import re
import time
from pathlib import Path

from PIL import Image

from .lines import assign_to_blocks, crop_poly, kraken_page, split_lines

ROOT = Path(__file__).resolve().parents[1]
TEXT_CATS = {"Text", "Title", "Section-header", "List-item", "Caption", "Footnote", "Page-header", "Page-footer"}
CANH_DOTS = 2400
LOOP_MAX_PERIOD = 200  # config web: 60

_BA_TU = str.maketrans({"ی": "ي", "ک": "ك", "ۃ": "ة", "ہ": "ه", "ۀ": "ة",
                        **{chr(0x06F0 + i): chr(0x0660 + i) for i in range(10)}})
_CHU = "ء-يٮ-ۓ"
_WAW = re.compile(rf"(?<![{_CHU}ً-ْ])و([ً-ْ]*)\s+(?=[{_CHU}])")


_HE = re.compile(r"[\u05D0-\u05EA]")
_AR = re.compile(r"[\u0621-\u064A]")


def la_hebrew(s: str) -> bool:
    """Khối chủ yếu chữ Hebrew (≥ 4 chữ Hebrew và không ít hơn chữ Ả Rập — số / ngày trong khối không tính)."""
    he = len(_HE.findall(s or ""))
    return he >= 4 and he >= len(_AR.findall(s or ""))


def sua_chu(s: str) -> str:
    """Chữ Ba Tư → chữ Ả Rập cùng hình; "و" đứng riêng → dính vào từ sau. Không đổi gì khác."""
    return _WAW.sub(r"و\1", (s or "").translate(_BA_TU))


def nap_dots(gpu: int):
    from ocrbench.convert import Converter

    return Converter(ROOT / "inference" / "config.yaml", "dots_mocr", gpus=str(gpu),
                     params={"device_map": {"": f"cuda:{gpu}"}, "loop_max_period": LOOP_MAX_PERIOD})


def _het_vram(e: Exception) -> bool:
    return "out of memory" in str(e).lower() or type(e).__name__ == "OutOfMemoryError"


def phan_trang(conv, page: Image.Image, path: Path, tach: str = "kraken_muharaf", canh: int | None = CANH_DOTS,
               chu_dots: bool = True) -> dict:
    """dots chia khối (ảnh phóng tới `canh`) → tách dòng trong từng khối chữ. Hộp / ảnh dòng theo ảnh `img` (ảnh web đã
    chuẩn bị, KHÔNG phóng thêm). chu_dots=False → dots chỉ chia khối (nhanh hơn, không có chữ của dots)."""
    import torch

    img, item = conv._prepare(page.copy(), Path(path), 1, "text")
    f = min(3.0, canh / max(img.size)) if canh and max(img.size) < canh else 1.0
    conv.set_mode("Bố cục đầy đủ" if chu_dots else "Chỉ bố cục (không chữ)")
    ghi = []
    t0 = time.time()

    def du_doan(f):
        im = img if f == 1 else img.resize((round(img.width * f), round(img.height * f)), Image.LANCZOS)
        return conv.adapter.predict(im, item)

    try:
        pred = du_doan(f)
    except Exception as e:  # noqa: BLE001
        if f == 1 or not _het_vram(e):
            raise
        torch.cuda.empty_cache()
        ghi.append(f"dots hết VRAM ở ảnh phóng ×{f:.2f} → đọc lại ở ảnh không phóng")
        f = 1.0
        pred = du_doan(f)
    extra = pred.extra or {}
    blocks = []
    for b in extra.get("blocks") or []:
        bb = b.get("bbox")
        blocks.append({**b, "bbox": [v / f for v in bb] if bb and len(bb) == 4 else bb,
                       "text": sua_chu(b.get("text") or "")})
        if blocks[-1].get("category") in TEXT_CATS and la_hebrew(blocks[-1]["text"]):
            blocks[-1]["hebrew"] = True
    co_chu = [b for b in blocks if b.get("category") in TEXT_CATS and len(b.get("bbox") or []) == 4]
    du_phong = None
    if not co_chu:
        du_phong = "dots không ra khối chữ nào" + (" (chạy tới trần token)" if extra.get("hit_max_tokens") else
                                                  " (JSON bố cục hỏng)" if extra.get("layout") == "filtered" else "")
        ghi.append(du_phong + " → DỰ PHÒNG: cả trang là một khối, tách dòng cả trang")
        blocks = [{"category": "Text", "bbox": [0, 0, img.width, img.height], "text": "", "du_phong": True}]
    elif extra.get("hit_max_tokens"):
        ghi.append("dots chạy tới trần token — khối cuối có thể thiếu")
    t_dots = time.time() - t0
    jobs, dung_tach, page_lines, by_block = [], set(), None, {}
    if tach == "kraken_muharaf":
        page_lines = kraken_page(img)
        boxes = {bi: tuple(int(round(v)) for v in b["bbox"]) for bi, b in enumerate(blocks)
                 if b.get("category") in TEXT_CATS and len(b.get("bbox") or []) == 4}
        by_block = assign_to_blocks(page_lines, boxes) if page_lines else {}
    for bi, b in enumerate(blocks):
        bb = b.get("bbox")
        if b.get("category") not in TEXT_CATS or not bb or len(bb) != 4:
            continue
        x0, y0, x1, y1 = [int(round(v)) for v in bb]
        if x1 - x0 < 8 or y1 - y0 < 8 or b.get("hebrew"):  # Hebrew: dòng Kraken trong khối bị bỏ, giữ chữ dots
            continue
        if by_block.get(bi):
            dung_tach.add("kraken_muharaf")
            jobs += [(bi, L["box"], crop_poly(img, L), L.get("poly")) for L in by_block[bi]]
            continue
        ds, used = split_lines(img.crop((x0, y0, x1, y1)), "chieu_ngang" if tach == "kraken_muharaf" else tach)
        dung_tach.add(used)
        for lx0, ly0, lx1, ly1 in ds:
            box = (x0 + lx0, y0 + ly0, x0 + lx1, y0 + ly1)
            jobs.append((bi, box, img.crop(box), None))
    return {"img": img, "blocks": blocks, "jobs": jobs, "tach": sorted(dung_tach), "giay_dots": round(t_dots),
            "phong": round(f, 3), "du_phong": du_phong, "so_khoi_hebrew": sum(bool(b.get("hebrew")) for b in blocks), "ghi_chu": ghi,
            "dots_extra": {k: extra.get(k) for k in ("new_tokens", "hit_max_tokens", "stopped_loop", "layout")}}
