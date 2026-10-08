"""Tải bộ dòng chữ viết tay Omar Al-Saleh (NAKBA NLP 2026) và tách thành thư mục để xem / chấm.

    python -m htr_test.tai_omar ~/du_lieu_omar_al_saleh [--splits train,test,blind_test]

Bộ gated: tài khoản Hugging Face phải bấm "Agree and access repository" tại
https://huggingface.co/datasets/U4RASD/omar-al-saleh-manuscripts-segments ; token lấy từ biến HF_TOKEN hoặc
`hf auth login`. Giấy phép CC BY 4.0. Kết quả:
    <đích>/<tập>/<mẫu>/input/<ảnh dòng>   <đích>/<tập>/<mẫu>/output/nhan.txt
    <đích>/danh_sach.csv   (tập, mẫu, đường dẫn, kích thước ảnh, số ký tự / từ / dấu nguyên âm, tên file gốc)
    <đích>/NGUON.md  <đích>/README_goc.md  <đích>/xem_mau.html (80 dòng ngẫu nhiên mỗi tập: ảnh + nhãn)
Chạy lại = ghi đè cùng nội dung (dữ liệu cố định).
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import random
import re
import sys
from pathlib import Path

REPO = "U4RASD/omar-al-saleh-manuscripts-segments"
HARAKAT = re.compile(r"[ً-ْٰ]")

NGUON = """# Omar Al-Saleh Manuscripts — Segments (NAKBA NLP 2026)

- Nguồn: https://huggingface.co/datasets/U4RASD/omar-al-saleh-manuscripts-segments (gated: bấm đồng ý điều khoản)
- Nội dung: dòng chữ VIẾT TAY tiếng Ả Rập, hồi ký của Omar Al-Saleh (Palestine, 1951–1965), 16 tài liệu ~6.395 trang;
  cắt dòng + nhãn do chuyên gia kiểm tra. Kiểu chữ Ruq'ah / Naskh, giấy kẻ dòng, ảnh scan đen trắng.
- Giấy phép: **CC BY 4.0** (dùng thương mại được, phải ghi nguồn — trích dẫn trong README_goc.md).
- Nhãn đã chuẩn hoá chính tả (thêm hamza: ان → أن/إن; bỏ ngoặc quanh số) — khi chấm nên gộp alef/hamza.
- Ketaba-OCR-LoRA và Baseer-Nakba đã HỌC train (+ test) → đánh giá công bằng CHỈ trên `blind_test/`.

{bang}

Cấu trúc: `<tập>/<mẫu>/input/<ảnh dòng>` · `<tập>/<mẫu>/output/nhan.txt`. Bảng đầy đủ: `danh_sach.csv`.
Xem nhanh: mở `xem_mau.html` bằng trình duyệt. Tạo bằng `python -m htr_test.tai_omar` (repo ocr-bench, nhánh thu-2-model-htr).
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dich")
    ap.add_argument("--splits", default="train,test,blind_test")
    a = ap.parse_args()
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download
    from PIL import Image

    root = Path(a.dich).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    splits = [s.strip() for s in a.splits.split(",") if s.strip()]
    rows, seen = [], set()
    for split in splits:
        try:
            f = hf_hub_download(REPO, f"data/{split}-00000-of-00001.parquet", repo_type="dataset")
        except Exception as e:
            sys.exit(f"Không tải được {split}: {e}\n→ kiểm tra đã bấm đồng ý điều khoản + HF_TOKEN / hf auth login")
        n = 0
        for i, r in enumerate(pq.read_table(f).to_pylist()):
            fn = r["filename"] or f"{split}_{i:05d}"
            stem = re.sub(r"[^\w.-]+", "_", Path(fn).stem)[:120]
            name = stem if (split, stem) not in seen else f"{stem}_{i}"
            seen.add((split, name))
            d = root / split / name
            (d / "input").mkdir(parents=True, exist_ok=True)
            (d / "output").mkdir(exist_ok=True)
            b = r["image"]["bytes"]
            ext = Path(r["image"].get("path") or fn).suffix.lower()
            ext = ext if ext in (".jpg", ".jpeg", ".png") else ".png"
            (d / "input" / f"{name}{ext}").write_bytes(b)
            txt = (r["text"] or "").strip()
            (d / "output" / "nhan.txt").write_text(txt + "\n", encoding="utf-8")
            im = Image.open(io.BytesIO(b))
            rows.append({"tap": split, "mau": name, "anh": f"{split}/{name}/input/{name}{ext}",
                         "nhan": f"{split}/{name}/output/nhan.txt", "rong": im.width, "cao": im.height,
                         "so_ky_tu": len(txt), "so_tu": len(txt.split()), "dau_nguyen_am": len(HARAKAT.findall(txt)),
                         "filename_goc": fn})
            n += 1
        print(f"  {split}: {n} dòng", flush=True)
    with open(root / "danh_sach.csv", "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    readme = hf_hub_download(REPO, "README.md", repo_type="dataset")
    (root / "README_goc.md").write_text(Path(readme).read_text(encoding="utf-8"), encoding="utf-8")
    bang = "| Tập | Số dòng |\n|---|---:|\n" + "\n".join(
        f"| {s} | {sum(r['tap'] == s for r in rows):,} |".replace(",", ".") for s in splits)
    (root / "NGUON.md").write_text(NGUON.format(bang=bang), encoding="utf-8")
    rnd, parts = random.Random(7), []
    for split in splits:
        rs = [r for r in rows if r["tap"] == split]
        pick = rnd.sample(rs, min(80, len(rs)))
        items = "".join(
            f"<div class=it><img loading=lazy src='{html.escape(r['anh'])}'><div class=t dir=rtl>"
            f"{html.escape((root / r['nhan']).read_text(encoding='utf-8'))}</div><div class=m>{html.escape(r['mau'])} · "
            f"{r['rong']}×{r['cao']}</div></div>" for r in pick)
        parts.append(f"<h2>{split} — {len(pick)} dòng ngẫu nhiên / {len(rs)}</h2>{items}")
    css = ("body{font-family:sans-serif;margin:16px;max-width:1100px} .it{border-bottom:1px solid #ddd;padding:8px 0} "
           "img{max-width:100%;max-height:110px;display:block;margin-left:auto;background:#eee} "
           ".t{font-family:'Noto Naskh Arabic','Amiri',serif;font-size:20px;line-height:1.8;text-align:right;color:#063} "
           ".m{color:#888;font-size:12px}")
    (root / "xem_mau.html").write_text(
        f"<!doctype html><meta charset=utf-8><title>Omar Al-Saleh — xem mẫu</title><style>{css}</style>"
        "<h1>Omar Al-Saleh (NakbaNLP 2026) — ảnh dòng và nhãn</h1><p>Mỗi mục: ảnh dòng (trên) · nhãn thật (dưới, chữ xanh).</p>"
        + "".join(parts), encoding="utf-8")
    print(f"✔ {len(rows)} dòng → {root}  ·  xem: {root / 'xem_mau.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
