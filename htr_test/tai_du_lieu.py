"""Phần chung của script tải bộ DÒNG chữ viết tay từ Hugging Face (parquet: image + text) → thư mục để xem / chấm.

    <đích>/<tập>/<mẫu>/input/<ảnh dòng>   <đích>/<tập>/<mẫu>/output/nhan.txt
    <đích>/danh_sach.csv   (tập, mẫu, trang, đường dẫn, kích thước ảnh, số ký tự / từ / dấu nguyên âm, tên file gốc)
    <đích>/NGUON.md  <đích>/README_goc.md  <đích>/xem_mau.html (80 dòng ngẫu nhiên mỗi tập: ảnh + nhãn)
Dùng qua htr_test/tai_omar.py, htr_test/tai_muharaf.py. Chạy lại = ghi đè cùng nội dung (dữ liệu cố định).
"""

from __future__ import annotations

import csv
import html
import io
import random
import re
import sys
from pathlib import Path
from typing import Callable

HARAKAT = re.compile(r"[ً-ْٰ]")


def tai(dich: str, repo: str, files: dict[str, list[str]], nguon_md: str, tieu_de: str,
        trang: Callable[[str], str] = lambda fn: "") -> int:
    """files = {tập: [đường dẫn parquet trong repo]}; nguon_md có chỗ {bang} cho bảng số dòng;
    trang(tên file gốc) → mã trang chứa dòng (để biết dòng nào cùng một trang)."""
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download
    from PIL import Image

    root = Path(dich).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    rows, seen = [], set()
    for split, paths in files.items():
        n = 0
        for path in paths:
            try:
                f = hf_hub_download(repo, path, repo_type="dataset")
            except Exception as e:
                sys.exit(f"Không tải được {path}: {e}\n→ bộ gated: kiểm tra đã bấm đồng ý điều khoản + HF_TOKEN / hf auth login")
            pf = pq.ParquetFile(f)
            for rg in range(pf.num_row_groups):  # đọc từng nhóm hàng — file train lớn, không nạp hết vào RAM
                for r in pf.read_row_group(rg).to_pylist():
                    fn = r.get("filename") or (r["image"] or {}).get("path") or f"{split}_{n:05d}"
                    stem = re.sub(r"[^\w.-]+", "_", Path(fn).stem)[:120]
                    name = stem if (split, stem) not in seen else f"{stem}_{n}"
                    seen.add((split, name))
                    d = root / split / name
                    (d / "input").mkdir(parents=True, exist_ok=True)
                    (d / "output").mkdir(exist_ok=True)
                    b = r["image"]["bytes"]
                    ext = Path(fn).suffix.lower()
                    ext = ext if ext in (".jpg", ".jpeg", ".png") else ".png"
                    (d / "input" / f"{name}{ext}").write_bytes(b)
                    txt = (r["text"] or "").strip()
                    (d / "output" / "nhan.txt").write_text(txt + "\n", encoding="utf-8")
                    im = Image.open(io.BytesIO(b))
                    rows.append({"tap": split, "mau": name, "trang": trang(fn), "anh": f"{split}/{name}/input/{name}{ext}",
                                 "nhan": f"{split}/{name}/output/nhan.txt", "rong": im.width, "cao": im.height,
                                 "so_ky_tu": len(txt), "so_tu": len(txt.split()),
                                 "dau_nguyen_am": len(HARAKAT.findall(txt)), "filename_goc": fn})
                    n += 1
        print(f"  {split}: {n} dòng", flush=True)
    with open(root / "danh_sach.csv", "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    try:
        readme = hf_hub_download(repo, "README.md", repo_type="dataset")
        (root / "README_goc.md").write_text(Path(readme).read_text(encoding="utf-8"), encoding="utf-8")
    except Exception:
        pass
    splits = list(files)
    bang = "| Tập | Số dòng | Số trang |\n|---|---:|---:|\n" + "\n".join(
        f"| {s} | {sum(r['tap'] == s for r in rows):,} | {len({r['trang'] for r in rows if r['tap'] == s and r['trang']}) or '—'} |"
        .replace(",", ".") for s in splits)
    (root / "NGUON.md").write_text(nguon_md.format(bang=bang), encoding="utf-8")
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
        f"<!doctype html><meta charset=utf-8><title>{html.escape(tieu_de)} — xem mẫu</title><style>{css}</style>"
        f"<h1>{html.escape(tieu_de)} — ảnh dòng và nhãn</h1><p>Mỗi mục: ảnh dòng (trên) · nhãn thật (dưới, chữ xanh).</p>"
        + "".join(parts), encoding="utf-8")
    print(f"✔ {len(rows)} dòng → {root}  ·  xem: {root / 'xem_mau.html'}")
    return 0
