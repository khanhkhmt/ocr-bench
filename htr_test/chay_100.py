"""Chạy pipeline adoc/ trên bộ test 100 trang (~/bo_test_100) → thư mục kết quả cùng cấu trúc.

    PY=/kaggle/working/venvs/adoc/bin/python          # cài bằng: bash htr_test/cai_adoc.sh
    $PY -m htr_test.chay_100 --vao /kaggle/input/<dataset> --ra /kaggle/working/ket_qua_100
    $PY -m htr_test.chay_100 --vao … --ra … --chi in_001,tay_011     # chạy thử 2 trang

Vào: mỗi thư mục con (in_NNN = chữ in → page_type printed, tay_NNN = viết tay → handwritten) có input.jpg/png,
output.txt (nhãn), nguon.json. --vao có thể trỏ vào thư mục cha (tự tìm thư mục chứa in_* / tay_*).

Ra (<--ra>/<thư mục con>/):
  input.jpg|png   ảnh gốc (chép nguyên)
  output.txt      chữ CHÍNH của pipeline (chữ in: dots · viết tay: ft3; như web / arabic-doc-ocr)
  output_dots.txt, output_ft3.txt, output_ft4.txt   chữ từng model (để so)
  ket_qua.json    JSON trang đầy đủ (khối, dòng, info: thời gian, GPU, ảnh đã thu nhỏ chưa …)
  nguon.json      chép từ bộ vào
  loi.txt         chỉ có khi trang lỗi (traceback); trang đó không có output.txt
Gốc <--ra>: diem.csv + tong_ket.md (điểm so với nhãn, evaluate.py của adoc: % ký tự / % từ), chay.log.json.

Chạy lại = đi tiếp: trang đã có output.txt + ket_qua.json bị bỏ qua (Kaggle tắt giữa chừng thì chạy lại đúng lệnh).
Ảnh có cạnh dài > --canh-toi-da (mặc định 2400 px = cỡ dots đọc trang khách sau khi phóng) được thu nhỏ trước khi
đưa vào pipeline: dots không tự thu ảnh lớn và hết bộ nhớ T4 từ ~3200 px. Nới dòng = config.LINE_PAD_PCT (50 %).
Không có bước LLM.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import time
import traceback
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

KINDS = ("main", "dots", "ft3", "ft4")


def tim_bo(vao: Path) -> Path:
    """Thư mục chứa in_* / tay_* (vào thẳng hoặc sâu tối đa 3 cấp — Kaggle dataset hay lồng thêm thư mục)."""
    for d in [vao, *sorted(p for p in vao.glob("*") if p.is_dir()), *sorted(p for p in vao.glob("*/*") if p.is_dir()),
              *sorted(p for p in vao.glob("*/*/*") if p.is_dir())]:
        if any(d.glob("in_*/input.*")) or any(d.glob("tay_*/input.*")):
            return d
    sys.exit(f"✘ LỖI: không thấy thư mục in_*/tay_* có input.* trong {vao}")


def danh_sach(bo: Path, chi: set[str] | None) -> list[Path]:
    ds = sorted(d for d in bo.iterdir() if d.is_dir() and d.name.split("_")[0] in ("in", "tay") and any(d.glob("input.*")))
    if chi:
        thieu = chi - {d.name for d in ds}
        if thieu:
            sys.exit(f"✘ LỖI: không có trang {sorted(thieu)} trong {bo}")
        ds = [d for d in ds if d.name in chi]
    return ds


def loai_trang(d: Path) -> str:
    from adoc import config

    return config.PRINTED if d.name.startswith("in_") else config.HANDWRITTEN


def doc_anh(f: Path, canh: int) -> tuple[Image.Image, dict]:
    from adoc.pipeline import load_pages

    img = load_pages(f)[0]
    w, h = img.size
    info = {"anh_goc": [w, h], "thu_nho": False}
    if canh and max(w, h) > canh:
        k = canh / max(w, h)
        img = img.resize((round(w * k), round(h * k)), Image.LANCZOS)
        info.update(thu_nho=True, anh_dua_vao=list(img.size))
    return img, info


def nguon_ngan(d: Path) -> str:
    try:
        n = json.loads((d / "nguon.json").read_text(encoding="utf-8"))["nguon"]
    except Exception:  # noqa: BLE001
        return "?"
    return n.split(" (")[0].split(" —")[0]


def tong_ket(bo: Path, ra: Path) -> str:
    """Điểm từng trang (nhãn = <bo>/<trang>/output.txt) → diem.csv + tong_ket.md; trả về bảng markdown."""
    from adoc import evaluate as ev

    rows = []
    for d in sorted(p for p in ra.iterdir() if p.is_dir()):
        lab = bo / d.name / "output.txt"
        if not lab.exists() or not (d / "output.txt").exists():
            continue
        ref = lab.read_text(encoding="utf-8")
        r = {"thu_muc": d.name, "loai": "in" if d.name.startswith("in_") else "tay", "nguon": nguon_ngan(bo / d.name)}
        for k in KINDS:
            f = d / ("output.txt" if k == "main" else f"output_{k}.txt")
            sc = ev.score(ref, f.read_text(encoding="utf-8")) if f.exists() else None
            r[f"{k}_ky_tu"] = round(100 * sc["chars"], 2) if sc else ""
            r[f"{k}_tu"] = round(100 * sc["words"], 2) if sc else ""
        try:
            info = json.loads((d / "ket_qua.json").read_text(encoding="utf-8"))["chay"]
            r["giay"], r["thu_nho"] = info.get("giay"), info.get("thu_nho")
        except Exception:  # noqa: BLE001
            r["giay"], r["thu_nho"] = "", ""
        rows.append(r)
    loi = sorted(p.parent.name for p in ra.glob("*/loi.txt"))
    if rows:
        with open(ra / "diem.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    def tb(rs, key):
        v = [x[key] for x in rs if x[key] != ""]
        return f"{sum(v) / len(v):.1f}" if v else "—"

    nhom = [("Chữ in (Wikisource)", [r for r in rows if r["loai"] == "in"])]
    for n in sorted({r["nguon"] for r in rows if r["loai"] == "tay"}):
        nhom.append((f"Viết tay — {n}", [r for r in rows if r["loai"] == "tay" and r["nguon"] == n]))
    nhom.append(("Viết tay — cả 3 bộ", [r for r in rows if r["loai"] == "tay"]))
    L = ["| nhóm | số trang | **chính** ký tự / từ | dots | ft3 | ft4 |", "|---|---:|---:|---:|---:|---:|"]
    for ten, rs in nhom:
        if rs:
            L.append(f"| {ten} | {len(rs)} | **{tb(rs, 'main_ky_tu')} / {tb(rs, 'main_tu')}** | "
                     + " | ".join(f"{tb(rs, k + '_ky_tu')} / {tb(rs, k + '_tu')}" for k in KINDS[1:]) + " |")
    bang = "\n".join(L)
    md = [f"# Kết quả adoc trên bộ test 100 trang", "",
          f"{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · {len(rows)} trang có kết quả · lỗi: "
          f"{', '.join(loi) if loi else 'không'}", "",
          "% ký tự đúng / % từ đúng so với nhãn (adoc/evaluate.py: bỏ dấu thanh, gộp alef / yeh, số Ả Rập → 0–9, "
          "bỏ dấu câu). **chính** = chữ pipeline trả ra (chữ in: dots · viết tay: ft3). Trang từng trang: diem.csv.", "",
          bang, "",
          "Lưu ý: nhãn Wikisource có thể thiếu số trang / tiêu đề chạy / số thứ tự mục (xem README của bộ) → điểm chữ in "
          "hơi thấp hơn thật; sách in sạch hơn bản đánh máy của khách → điểm chữ in vẫn cao hơn trên trang khách."]
    (ra / "tong_ket.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return bang


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vao", required=True, help="thư mục bộ test (hoặc thư mục cha của nó)")
    ap.add_argument("--ra", required=True, help="thư mục kết quả")
    ap.add_argument("--chi", default="", help="chỉ chạy các trang này, vd. in_001,tay_011")
    ap.add_argument("--canh-toi-da", type=int, default=2400, help="thu ảnh có cạnh dài hơn số này (0 = không thu)")
    ap.add_argument("--dots-device", default=None)
    ap.add_argument("--htr-device", default=None)
    ap.add_argument("--chi-tong-ket", action="store_true", help="không chạy model, chỉ tính lại diem.csv / tong_ket.md")
    a = ap.parse_args(argv)

    bo, ra = tim_bo(Path(a.vao)), Path(a.ra)
    ra.mkdir(parents=True, exist_ok=True)
    chi = {x.strip() for x in a.chi.split(",") if x.strip()} or None
    ds = danh_sach(bo, chi)
    print(f"== bộ test: {bo} · {len(ds)} trang ({sum(d.name.startswith('in_') for d in ds)} in, "
          f"{sum(d.name.startswith('tay_') for d in ds)} viết tay) → {ra}", flush=True)
    if a.chi_tong_ket:
        print(tong_ket(bo, ra))
        return 0

    import torch

    from adoc import __version__, config
    from adoc.__main__ import page_json
    from adoc.pipeline import Pipeline, free_gpu

    n_gpu = torch.cuda.device_count()
    if n_gpu == 0:
        sys.exit("✘ LỖI: không có GPU")
    dd = a.dots_device or "cuda:0"
    hd = a.htr_device or ("cuda:1" if n_gpu >= 2 else "cuda:0")
    offload = "none" if dd != hd else "unload"
    print(f"== adoc {__version__} · dots {dd} · ft3/ft4 {hd} · offload {offload} · nới dòng {config.LINE_PAD_PCT} % · "
          f"thu ảnh > {a.canh_toi_da} px", flush=True)
    pipe = Pipeline(dd, hd, offload=offload)

    lam = [d for d in ds if not ((ra / d.name / "output.txt").exists() and (ra / d.name / "ket_qua.json").exists())]
    print(f"== đã xong trước đó: {len(ds) - len(lam)} · còn {len(lam)}", flush=True)
    t0, xong, loi = time.time(), 0, []
    for i, d in enumerate(lam, 1):
        o = ra / d.name
        o.mkdir(parents=True, exist_ok=True)
        f = next(iter(sorted(d.glob("input.*"))))
        if not (o / f.name).exists():
            shutil.copy2(f, o / f.name)
        if (d / "nguon.json").exists():
            shutil.copy2(d / "nguon.json", o / "nguon.json")
        (o / "loi.txt").unlink(missing_ok=True)
        pt = loai_trang(d)
        t = time.time()
        try:
            img, anh = doc_anh(f, a.canh_toi_da)
            res = pipe.process_document([img], pt)
            js = {"document": d.name, "pages": [page_json(r, k + 1) for k, r in enumerate(res)]}
            js["chay"] = {"page_type": pt, "giay": round(time.time() - t, 1), **anh,
                          "nguon": nguon_ngan(d), "adoc": __version__}
            texts = {k: "\n\n".join(r.page_text(k) for r in res) for k in KINDS}
            for k in KINDS:
                (o / ("output.txt" if k == "main" else f"output_{k}.txt")).write_text(texts[k].strip() + "\n",
                                                                                     encoding="utf-8")
            (o / "ket_qua.json").write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
            xong += 1
            p = res[0].info
            ghi = f" · {'; '.join(p['notes'])}" if p.get("notes") else ""
            print(f"✔ [{i}/{len(lam)}] {d.name} ({pt}) {time.time() - t:.0f} s · {p.get('lines', 0)} dòng · "
                  f"{len(texts['main'])} ký tự{' · ảnh thu nhỏ' if anh['thu_nho'] else ''}{ghi}", flush=True)
        except Exception as e:  # noqa: BLE001 — một trang lỗi không dừng cả bộ; lỗi ghi vào loi.txt
            for k in KINDS:
                (o / ("output.txt" if k == "main" else f"output_{k}.txt")).unlink(missing_ok=True)
            (o / "loi.txt").write_text(traceback.format_exc(), encoding="utf-8")
            loi.append(d.name)
            print(f"✘ [{i}/{len(lam)}] {d.name} LỖI: {type(e).__name__}: {str(e)[:200]} (xem {o}/loi.txt)", flush=True)
            free_gpu()
        con = len(lam) - i
        if con:
            print(f"   còn {con} trang · ước tính {(time.time() - t0) / i * con / 60:.0f} phút", flush=True)

    (ra / "chay.log.json").write_text(json.dumps({"bo": str(bo), "xong_lan_nay": xong, "loi_lan_nay": loi,
                                                  "giay": round(time.time() - t0), "dots": dd, "htr": hd,
                                                  "noi_dong": config.LINE_PAD_PCT, "canh_toi_da": a.canh_toi_da},
                                                 ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n" + tong_ket(bo, ra))
    n_ok = sum(1 for d in ds if (ra / d.name / "output.txt").exists())
    if n_ok == len(ds):
        print(f"\n✔ XONG {n_ok}/{len(ds)} trang → {ra} (tong_ket.md, diem.csv)")
        return 0
    print(f"\n✘ CHƯA ĐỦ: {n_ok}/{len(ds)} trang có kết quả · lỗi: {', '.join(loi) or '—'} (chạy lại lệnh để đi tiếp)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
