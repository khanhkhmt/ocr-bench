"""Gom dữ liệu GIỐNG giấy tờ chính của khách (giấy cũ, chữ tay, lưu trữ Ả Rập / Hebrew) về một thư mục, mỗi mẫu
một thư mục con:

    <root>/<nguồn>/<mẫu>/input/<ảnh hoặc pdf gốc>
    <root>/<nguồn>/<mẫu>/output/nhan.txt            nhãn thật (bản gõ lại)
    <root>/<nguồn>/<mẫu>/output/nhan_goc.*          nhãn ở định dạng gốc của nguồn (nếu khác txt: XML, JSON…)
    <root>/danh_sach.csv                            mọi mẫu: nguồn, mẫu, file input, ngôn ngữ, loại, giấy phép
    <root>/NGUON.md                                 nguồn, link, giấy phép, số mẫu

    python experiments/historical_data/fetch.py <root> [nguồn ...]     (chạy lại = bỏ qua mẫu đã có)

Dữ liệu nằm NGOÀI repo. Dừng khi ổ còn < MIN_FREE_GB. Cô lập: xoá thư mục experiments/historical_data là sạch.
"""

from __future__ import annotations

import csv
import io
import json
import re
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

MIN_FREE_GB = 1.0

SOURCES = {
    "muharaf_trang": {
        "ten": "Muharaf (NeurIPS 2024) — trang viết tay lưu trữ Ả Rập thế kỷ 19–21 (thư từ, hồ sơ pháp lý, sổ nhà thờ)",
        "link": "https://arxiv.org/abs/2406.09630 · bản trang: https://huggingface.co/datasets/TheRealOKAI/muharaf-public-pages",
        "giay_phep": "CC BY-NC-SA 4.0 (Muharaf gốc; chỉ phi thương mại)",
        "hf": "TheRealOKAI/muharaf-public-pages", "text": "text", "id": "id", "lang": "ar", "loai": "viết tay",
    },
    "kitab_historyar": {
        "ten": "KITAB-Bench / HistoryAr — dòng chữ tài liệu Ả Rập lịch sử",
        "link": "https://huggingface.co/datasets/ahmedheakl/arocrbench_historyar",
        "giay_phep": "theo KITAB-Bench (ACL 2025) — chưa ghi rõ, dùng nghiên cứu",
        "hf": "ahmedheakl/arocrbench_historyar", "text": "text", "id": None, "lang": "ar", "loai": "lịch sử",
    },
    "kitab_historicalbooks": {
        "ten": "KITAB-Bench / HistoricalBooks — trang sách Ả Rập cổ",
        "link": "https://huggingface.co/datasets/ahmedheakl/arocrbench_historicalbooks",
        "giay_phep": "theo KITAB-Bench (ACL 2025) — chưa ghi rõ, dùng nghiên cứu",
        "hf": "ahmedheakl/arocrbench_historicalbooks", "text": "answer", "id": None, "lang": "ar", "loai": "lịch sử",
    },
    "churro_ottoman": {
        "ten": "CHURRO — tập con Ottoman Turkish (chữ Ả Rập, tài liệu lưu trữ)",
        "link": "https://huggingface.co/datasets/OttomanNLP/CHURRO-Ottoman-Turkish-Subset",
        "giay_phep": "CC BY 4.0 (theo thẻ dataset)",
        "hf": "OttomanNLP/CHURRO-Ottoman-Turkish-Subset", "text": "original_transcription", "id": None, "lang": "ota",
        "loai": "lưu trữ",
    },
    "khatt_doan": {
        "ten": "KHATT (qua KITAB-Bench) — đoạn văn viết tay Ả Rập hiện đại, nhiều người viết (chữ tay không đều)",
        "link": "https://huggingface.co/datasets/ahmedheakl/arocrbench_khattparagraph",
        "giay_phep": "KHATT gốc có điều khoản riêng (nghiên cứu); bản KITAB-Bench chưa ghi rõ",
        "hf": "ahmedheakl/arocrbench_khattparagraph", "text": "answer", "id": None, "lang": "ar", "loai": "viết tay",
    },
    "churro_ar_he": {
        "ten": "CHURRO-DS (EMNLP 2025) — trang tài liệu LỊCH SỬ tiếng Ả Rập + Hebrew (in và viết tay), tập dev + test",
        "link": "https://huggingface.co/datasets/stanford-oval/churro-dataset · https://arxiv.org/abs/2509.19768",
        "giay_phep": "theo từng bộ gốc trong CHURRO-DS (155 nguồn; xem cột dataset_id) — nghiên cứu",
        "hf": "stanford-oval/churro-dataset", "langs": ("Arabic", "Hebrew"), "splits": ("dev", "test"),
        "lang": "ar/he", "loai": "lịch sử",
    },
    "madinah": {
        "ten": "Historical Arabic Handwritten Text Recognition Dataset (ĐH Hồi giáo Madinah) — 40 trang sách viết tay",
        "link": "https://data.mendeley.com/datasets/xz6f8bw3w8/1",
        "giay_phep": "theo Mendeley Data (CC BY 4.0 nếu không ghi khác)",
        "zip": "https://data.mendeley.com/public-api/datasets/xz6f8bw3w8/files?folder_id=root&version=1",
        "lang": "ar", "loai": "viết tay",
    },
}

IMG_EXT = {"JPEG": ".jpg", "PNG": ".png", "TIFF": ".tif", "WEBP": ".webp", "BMP": ".bmp"}


def free_gb(p: Path) -> float:
    return shutil.disk_usage(p).free / 1e9


def safe(name: str) -> str:
    return re.sub(r"[^\w؀-ۿ.\-]+", "_", name).strip("_")[:120] or "mau"


def write_sample(root: Path, src: str, sid: str, img_bytes: bytes, label: str, rows: list, extra: dict,
                 label_raw: tuple[str, bytes] | None = None) -> bool:
    from PIL import Image

    d = root / src / safe(sid)
    if (d / "output" / "nhan.txt").exists():
        return False
    if free_gb(root) < MIN_FREE_GB:
        raise SystemExit(f"✘ ổ còn < {MIN_FREE_GB} GB — dừng ({src}/{sid})")
    (d / "input").mkdir(parents=True, exist_ok=True)
    (d / "output").mkdir(parents=True, exist_ok=True)
    try:
        fmt = Image.open(io.BytesIO(img_bytes)).format
    except Exception:
        fmt = None
    name = f"{safe(sid)}{IMG_EXT.get(fmt, '.bin')}"
    (d / "input" / name).write_bytes(img_bytes)
    (d / "output" / "nhan.txt").write_text(label, encoding="utf-8")
    if label_raw:
        (d / "output" / f"nhan_goc{label_raw[0]}").write_bytes(label_raw[1])
    rows.append({"nguon": src, "mau": safe(sid), "input": f"{src}/{safe(sid)}/input/{name}",
                 "output": f"{src}/{safe(sid)}/output/nhan.txt", **extra})
    return True


def xml_text(xml: str) -> str:
    """Bản gõ lại dạng XML (CHURRO / PAGE) → chữ thường, mỗi dòng một dòng."""
    xml = re.sub(r"<(br|lb|/line|/Line|/TextLine|/p|/head|/TextRegion)\b[^>]*>", "\n", xml)
    if "<Unicode>" in xml:
        parts = re.findall(r"<Unicode>(.*?)</Unicode>", xml, flags=re.S)
        xml = "\n".join(parts)
    txt = re.sub(r"<[^>]+>", "", xml)
    import html as _h

    return re.sub(r"\n\s*\n+", "\n", _h.unescape(txt)).strip()


def fetch_hf(root: Path, key: str, rows: list) -> int:
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem

    cfg = SOURCES[key]
    fs = HfFileSystem()
    files = sorted(fs.glob(f"datasets/{cfg['hf']}/**/*.parquet"))
    n = seq = 0
    for f in files:
        with fs.open(f, "rb", block_size=4 << 20) as fh:
            pf = pq.ParquetFile(fh)
            cols = pf.schema_arrow.names
            for rg in range(pf.num_row_groups):
                t = pf.read_row_group(rg).to_pylist()
                for i, r in enumerate(t):
                    img = r.get("image")
                    b = img.get("bytes") if isinstance(img, dict) else None
                    if not b:
                        continue
                    if cfg["text"]:
                        label, raw = r.get(cfg["text"]) or "", None
                    else:  # CHURRO: cleaned_transcription XML → chữ; giữ XML gốc
                        xml = r.get("cleaned_transcription") or r.get("original_transcription") or ""
                        label, raw = xml_text(xml), (".xml", xml.encode("utf-8"))
                    sid = str(r.get(cfg["id"]) if cfg.get("id") else r.get("example_id") or f"{key}_{seq:05d}")
                    seq += 1
                    extra = {"ngon_ngu": r.get("main_language") or cfg["lang"], "loai": r.get("document_type") or cfg["loai"],
                             "giay_phep": cfg["giay_phep"]}
                    n += write_sample(root, key, sid, b, label, rows, extra, raw)
        print(f"  {key}: {f.split('/')[-1]} xong, tổng {n} mẫu mới", flush=True)
    return n


def fetch_churro(root: Path, rows: list) -> int:
    """Chỉ đọc cột ngôn ngữ trước; tải ảnh của các nhóm hàng (row group) có trang tiếng Ả Rập / Hebrew."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem

    cfg = SOURCES["churro_ar_he"]
    fs = HfFileSystem()
    files = [f for f in sorted(fs.glob(f"datasets/{cfg['hf']}/data/*.parquet"))
             if f.split("/")[-1].split("-")[0] in cfg["splits"]]
    n = 0
    for f in files:
        with fs.open(f, "rb", block_size=8 << 20) as fh:
            pf = pq.ParquetFile(fh)
            for rg in range(pf.num_row_groups):
                langs = pf.read_row_group(rg, columns=["main_language"]).column(0).to_pylist()
                hit = [i for i, x in enumerate(langs) if x in cfg["langs"]]
                if not hit:
                    continue
                t = pf.read_row_group(rg).to_pylist()
                for i in hit:
                    r = t[i]
                    xml = r.get("cleaned_transcription") or r.get("original_transcription") or ""
                    sid = (r.get("example_id") or f"{rg}_{i}").replace("/", "__")
                    n += write_sample(root, "churro_ar_he", sid, r["image"]["bytes"], xml_text(xml), rows,
                                      {"ngon_ngu": r.get("main_language"), "loai": r.get("document_type"),
                                       "giay_phep": cfg["giay_phep"], "ghi_chu": f"nguồn gốc: {r.get('dataset_id')}"},
                                      (".xml", xml.encode("utf-8")))
        print(f"  churro_ar_he: {f.split('/')[-1]} xong, tổng {n} mẫu mới", flush=True)
    return n


def fetch_madinah(root: Path, rows: list) -> int:
    """Nhãn là file Word (.docx); một docx có thể là nhãn CHUNG cho hai nửa trang <tên>_A, <tên>_B
    → mỗi docx là một mẫu: input/ chứa 1–2 ảnh tương ứng, output/ chứa chữ trích từ docx + docx gốc."""
    from docx import Document

    cfg = SOURCES["madinah"]
    ua = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ocrbench-research"}
    files = json.loads(urllib.request.urlopen(urllib.request.Request(cfg["zip"], headers=ua), timeout=60).read())
    url = files[0]["content_details"]["download_url"]
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=300).read()))
    names = z.namelist()
    imgs = [x for x in names if re.search(r"\.(jpe?g|png|tiff?|bmp)$", x, re.I)]
    n, used = 0, set()
    for dx in (x for x in names if x.lower().endswith(".docx")):
        stem = Path(dx).stem
        base = re.sub(r"_[AB]$", "", stem)
        mine = sorted(i for i in imgs if Path(i).stem in (stem, f"{base}_A", f"{base}_B")
                      and (Path(i).stem == stem or stem == base))
        if not mine:
            continue
        doc = Document(io.BytesIO(z.read(dx)))
        label = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        d = root / "madinah" / safe(stem)
        if (d / "output" / "nhan.txt").exists():
            continue
        if free_gb(root) < MIN_FREE_GB:
            raise SystemExit("✘ ổ sắp đầy — dừng")
        (d / "input").mkdir(parents=True, exist_ok=True)
        (d / "output").mkdir(parents=True, exist_ok=True)
        for im in mine:
            (d / "input" / Path(im).name).write_bytes(z.read(im))
            used.add(im)
        (d / "output" / "nhan.txt").write_text(label, encoding="utf-8")
        (d / "output" / "nhan_goc.docx").write_bytes(z.read(dx))
        rows.append({"nguon": "madinah", "mau": safe(stem), "input": f"madinah/{safe(stem)}/input/",
                     "output": f"madinah/{safe(stem)}/output/nhan.txt", "ngon_ngu": "ar", "loai": cfg["loai"],
                     "giay_phep": cfg["giay_phep"],
                     "ghi_chu": f"{len(mine)} ảnh (nhãn chung cho cả 2 nửa trang)" if len(mine) > 1 else ""})
        n += 1
    left = [i for i in imgs if i not in used]
    print(f"  madinah: {n} mẫu (zip có {len(imgs)} ảnh; ảnh không có nhãn: {len(left)})")
    return n


def write_index(root: Path, rows: list) -> None:
    p = root / "danh_sach.csv"
    old = []
    if p.exists():
        with open(p, encoding="utf-8") as f:
            old = list(csv.DictReader(f))
    seen = {(r["nguon"], r["mau"]) for r in rows}
    allr = [r for r in old if (r["nguon"], r["mau"]) not in seen] + rows
    keys = ["nguon", "mau", "input", "output", "ngon_ngu", "loai", "giay_phep", "ghi_chu"]
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(allr)
    lines = ["# Nguồn dữ liệu", "", "| Thư mục | Nội dung | Số mẫu | Giấy phép | Link |", "|---|---|---:|---|---|"]
    for k, c in SOURCES.items():
        cnt = sum(1 for r in allr if r["nguon"] == k)
        if cnt:
            lines.append(f"| `{k}/` | {c['ten']} | {cnt} | {c['giay_phep']} | {c['link']} |")
    (root / "NGUON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    root = Path(sys.argv[1]).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    want = sys.argv[2:] or list(SOURCES)
    rows: list = []
    try:
        for key in want:
            print(f"== {key} (ổ trống {free_gb(root):.1f} GB)", flush=True)
            try:
                if key == "madinah":
                    fetch_madinah(root, rows)
                elif key == "churro_ar_he":
                    fetch_churro(root, rows)
                else:
                    fetch_hf(root, key, rows)
            except SystemExit:
                raise
            except Exception as e:  # một nguồn lỗi không làm hỏng các nguồn khác
                print(f"  ✘ {key}: {type(e).__name__}: {e}")
    finally:
        write_index(root, rows)
        print(f"✔ {len(rows)} mẫu mới → {root} (ổ trống {free_gb(root):.1f} GB)")


if __name__ == "__main__":
    main()
