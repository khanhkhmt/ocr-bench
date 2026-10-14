"""Chấm cả TRANG tài liệu thật (ảnh + nhãn tay) — đúng đường đi của web (htr_test/app.py):
dots.mocr chia khối (và tự đọc chữ — bộ đọc khối ĐÁNH MÁY) → tách dòng trong từng khối chữ → Baseer gốc / ft1@0,5 /
ft3 / ft4 đọc từng dòng → ghép lại thành chữ cả trang → so với nhãn.

    <python venv dots> -m htr_test.cham_trang --data <thư mục> --out /kaggle/working/cham_trang_that [--push]

<thư mục>/image_*/anh.jpeg + nhan.json (+ nhan_claude.json): nhãn = trường "text". Mỗi nhãn chấm riêng (hai người
đọc chưa thống nhất → báo cả hai). Trước khi so: [?x] → x; bỏ [ … ] / "..." (chỗ người gán không đọc được); bỏ dấu câu;
ngày a/b/c không tính thứ tự (nhãn ghi lẫn ngày-trước / năm-trước); chuẩn hoá hamza / ى… như eval_lines.
Chỉ số mỗi trang: đúng ký tự / đúng từ (theo THỨ TỰ đọc — thứ tự khối của dots khác nhãn thì bị trừ) và "thu hồi từ"
(KHÔNG tính thứ tự: bao nhiêu % từ của nhãn có trong chữ model đọc) — xem cả hai trước khi kết luận.
dots trên GPU --gpu-dots, Baseer + 3 adapter (một nền) trên GPU --gpu-htr. Ra: <out>/tom_tat.md, ket_qua.jsonl
(chữ cả trang + từng dòng của mọi model), xem_ket_qua.html; --push → nhánh results-htr/<tên out>/.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from htr_test.eval_lines import _norm  # noqa: E402
from htr_test.lines import assign_to_blocks, crop_poly, kraken_page, split_lines  # noqa: E402
from ocrbench.metrics import edit_stats  # noqa: E402

TEXT_CATS = {"Text", "Title", "Section-header", "List-item", "Caption", "Footnote", "Page-header", "Page-footer"}  # = app.py
# tên cột → (adapter trong BaseerNakba, mô tả); thứ tự lora khi nạp: ft1, ft3, ft4 → tên adapter ft1, a1, a2
LORA = ["ft1", "hf:khanh99/htr-ckpt/ft3/best", "hf:khanh99/htr-ckpt/ft4/best"]
DOC = {"baseer_goc": "goc", "ft1_s050": "ft1", "ft3": "a1", "ft4": "a2"}
NHAN = {"nhan.json": "nhãn anh", "nhan_claude.json": "nhãn Claude"}
DAU_CAU = re.compile(r"[.,،؛:;!?؟()\[\]{}«»\"'“”•\-–—ـ*/\\]+")


def sach(s: str) -> str:
    s = re.sub(r"\[\?([^\]]*)\]", r"\1", s or "")
    s = re.sub(r"\[[^\]]*\]|\.\.\.|…", " ", s)
    s = re.sub(r"([0-9٠-٩]+)/([0-9٠-٩]+)/([0-9٠-٩]+)", lambda m: " ".join(sorted(m.groups(), key=lambda x: (len(x), x))), s)
    return " ".join(DAU_CAU.sub(" ", _norm(s)).split())


def diem(nhan: str, doc: str) -> dict:
    r, h = sach(nhan), sach(doc)
    s = edit_stats(r, h)
    cr, ch = Counter(r.split()), Counter(h.split())
    chung = sum((cr & ch).values())
    return {"dung": max(0.0, 1 - s["char_edits"] / max(1, s["ref_chars"])),
            "dung_tu": max(0.0, 1 - s["word_edits"] / max(1, s["ref_words"])),
            "thu_hoi_tu": chung / max(1, sum(cr.values())), "chinh_xac_tu": chung / max(1, sum(ch.values())),
            "tu_nhan": sum(cr.values())}


def doc_trang(conv, baseer, path: Path, tach: str) -> dict:
    page = Image.open(path).convert("RGB")
    t0 = time.time()
    conv.set_mode("Bố cục đầy đủ")
    img, item = conv._prepare(page, path, 1, "text")
    blocks = (conv.adapter.predict(img, item).extra or {}).get("blocks") or []
    t_dots = time.time() - t0
    jobs, dung_tach = [], set()
    by_block = {}
    if tach == "kraken_muharaf":
        lines = kraken_page(img)
        boxes = {bi: tuple(int(round(v)) for v in b["bbox"]) for bi, b in enumerate(blocks)
                 if b.get("category") in TEXT_CATS and len(b.get("bbox") or []) == 4}
        by_block = assign_to_blocks(lines, boxes) if lines else {}
    for bi, b in enumerate(blocks):
        bb = b.get("bbox")
        if b.get("category") not in TEXT_CATS or not bb or len(bb) != 4:
            continue
        x0, y0, x1, y1 = [int(round(v)) for v in bb]
        if x1 - x0 < 8 or y1 - y0 < 8:
            continue
        if by_block.get(bi):
            dung_tach.add("kraken_muharaf")
            jobs += [(bi, L["box"], crop_poly(img, L)) for L in by_block[bi]]
            continue
        ds, used = split_lines(img.crop((x0, y0, x1, y1)), "chieu_ngang")
        dung_tach.add(used)
        for lx0, ly0, lx1, ly1 in ds:
            box = (x0 + lx0, y0 + ly0, x0 + lx1, y0 + ly1)
            jobs.append((bi, box, img.crop(box)))
    t1 = time.time()
    res = {ten: baseer.read([j[2] for j in jobs], adapter=ad) if jobs else [] for ten, ad in DOC.items()}
    t_doc = time.time() - t1
    khoi_chu = [bi for bi, b in enumerate(blocks) if b.get("category") in TEXT_CATS]
    trang = {"dots": "\n".join(blocks[bi].get("text") or "" for bi in khoi_chu)}
    for ten in DOC:
        trang[ten] = "\n".join(res[ten][n] for bi in khoi_chu for n, j in enumerate(jobs) if j[0] == bi)
    return {"trang": trang, "so_khoi": len(blocks), "loai_khoi": dict(Counter(str(b.get("category")) for b in blocks)),
            "so_dong": len(jobs), "tach_dong": sorted(dung_tach), "giay_dots": round(t_dots), "giay_doc": round(t_doc),
            "dong": [{"khoi": j[0], "bbox": j[1], **{t: res[t][n] for t in DOC}} for n, j in enumerate(jobs)]}


def bao_cao(out: Path, ket: list[dict]) -> str:
    cot = ["dots", *DOC]
    rows = ["# Chấm cả trang — tài liệu thật (4 trang mẫu)", "",
            f"Cập nhật: {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · {len(ket)} trang", "",
            "Mỗi ô: **đúng ký tự** / đúng từ (theo thứ tự đọc) · thu hồi từ (không tính thứ tự). "
            "dots = dots tự đọc cả khối (bộ đọc ĐÁNH MÁY); các cột còn lại = model chữ tay đọc từng dòng do dots + "
            "tách dòng cắt ra. Trang đánh máy → xem cột dots (yêu cầu ≥ 90%); trang viết tay → so ft3 / ft4 với Baseer gốc.", ""]
    for f, ten_nhan in NHAN.items():
        rows += [f"## So với {ten_nhan} (`{f}`)", "", "| trang | loại | " + " | ".join(cot) + " |",
                 "|---|---|" + "---:|" * len(cot)]
        for k in ket:
            if f not in k["nhan"]:
                continue
            o = []
            for m in cot:
                d = k["diem"][f][m]
                o.append(f"**{100 * d['dung']:.1f}%** / {100 * d['dung_tu']:.1f}% · {100 * d['thu_hoi_tu']:.0f}%")
            rows.append(f"| {k['trang_id']} | {k['loai']} | " + " | ".join(o) + " |")
        rows.append("")
    rows += ["## Chi tiết chạy", "", "| trang | khối dots | dòng | tách dòng | dots (s) | đọc dòng 4 model (s) |",
             "|---|---|---:|---|---:|---:|"]
    for k in ket:
        rows.append(f"| {k['trang_id']} | {k['so_khoi']} {k['loai_khoi']} | {k['so_dong']} | {', '.join(k['tach_dong'])} | "
                    f"{k['giay_dots']} | {k['giay_doc']} |")
    md = "\n".join(rows) + "\n"
    (out / "tom_tat.md").write_text(md, encoding="utf-8")
    (out / "tom_tat.json").write_text(json.dumps([{x: k[x] for x in ("trang_id", "loai", "diem")} for k in ket],
                                                 ensure_ascii=False, indent=1), encoding="utf-8")
    css = ("body{font-family:sans-serif;margin:12px} td,th{border:1px solid #ccc;padding:6px;vertical-align:top} "
           "table{border-collapse:collapse;width:100%} .ar{direction:rtl;text-align:right;white-space:pre-wrap;"
           "font-family:'Noto Naskh Arabic','Amiri',serif;font-size:16px;line-height:1.7}")
    body = []
    for k in ket:
        head = "".join(f"<th>{html.escape(t)}</th>" for t in [*k["nhan"], *cot])
        cells = "".join(f"<td class=ar>{html.escape(k['nhan'][f])}</td>" for f in k["nhan"])
        cells += "".join(f"<td class=ar>{html.escape(k['trang'][m])}</td>" for m in cot)
        body.append(f"<h2>{html.escape(k['trang_id'])} — {html.escape(k['loai'])}</h2><table><tr>{head}</tr><tr>{cells}</tr></table>")
    (out / "xem_ket_qua.html").write_text(f"<!doctype html><meta charset=utf-8><title>Chấm cả trang</title><style>{css}</style>"
                                          f"<pre>{html.escape(md)}</pre>{''.join(body)}", encoding="utf-8")
    return md


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gpu-dots", type=int, default=0)
    ap.add_argument("--gpu-htr", type=int, default=1)
    ap.add_argument("--tach-dong", default="kraken_muharaf", choices=["kraken_muharaf", "chieu_ngang"],
                    help="như web: Kraken + model Muharaf (cả trang) nếu đã cài (htr_test/cai_kraken.sh), không có → chiếu ngang")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    data, out = Path(a.data), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    trang = sorted(p for p in data.glob("image_*") if (p / "anh.jpeg").exists())
    if not trang:
        sys.exit(f"✘ LỖI không thấy {data}/image_*/anh.jpeg")
    from ocrbench.convert import Converter
    from htr_test.models import BaseerNakba

    print(f"== {len(trang)} trang · nạp dots (GPU {a.gpu_dots}) + Baseer & 3 adapter (GPU {a.gpu_htr})", flush=True)
    conv = Converter(ROOT / "inference" / "config.yaml", "dots_mocr", gpus=str(a.gpu_dots))
    baseer = BaseerNakba(device=f"cuda:{a.gpu_htr}", lora=LORA, lora_scale={"ft1": 0.5}).load()
    if baseer.adapters != ["ft1", "a1", "a2"]:
        sys.exit(f"✘ LỖI adapter nạp ra {baseer.adapters}, cần ['ft1', 'a1', 'a2']")
    ket = []
    for p in trang:
        nhan = {f: json.loads((p / f).read_text(encoding="utf-8")) for f in NHAN if (p / f).exists()}
        r = doc_trang(conv, baseer, p / "anh.jpeg", a.tach_dong)
        r.update(trang_id=p.name, loai=next(iter(nhan.values())).get("type", "?") if nhan else "?",
                 nhan={f: v["text"] for f, v in nhan.items()})
        r["diem"] = {f: {m: diem(t, r["trang"][m]) for m in ["dots", *DOC]} for f, t in r["nhan"].items()}
        ket.append(r)
        d = r["diem"].get("nhan.json") or next(iter(r["diem"].values()))
        print(f"   {p.name}: {r['so_dong']} dòng · " + " · ".join(f"{m} {100 * d[m]['dung']:.1f}%" for m in d), flush=True)
    with open(out / "ket_qua.jsonl", "w", encoding="utf-8") as fo:
        for r in ket:
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(bao_cao(out, ket), flush=True)
    if a.push:
        from htr_test.sync import Sync

        Sync(out).push("chấm cả trang tài liệu thật — XONG")
    print("✔ XONG CHẤM TRANG", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
