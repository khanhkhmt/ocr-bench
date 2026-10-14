"""Thử dots.mocr trên các trang tài liệu thật: phóng ảnh có giúp chữ ĐÁNH MÁY không, và đường dự phòng khi dots hỏng
bố cục (image_3 lần chấm đầu: chạy tới trần token, JSON bị cắt → 0 khối → cả trang 0%).

    <python venv dots> -m htr_test.thu_dots --data <thư mục> --out /kaggle/working/thu_dots [--push]

Mỗi trang × mỗi mức phóng × mỗi cách đọc (ảnh = ảnh web đã chuẩn bị (conv._prepare, như cham_trang) rồi phóng thêm):
  day_du  — "Bố cục đầy đủ" (prompt_layout_all_en): chữ = các khối chữ theo thứ tự dots (= cột dots của cham_trang).
            JSON hỏng → thêm "chữ cứu": các khối (category, text) TRỌN VẸN trong output bị cắt.
  khoi    — "Chỉ bố cục" (prompt_layout_only_en, chỉ toạ độ → ít token) rồi "Chỉ chữ" (prompt_ocr) trên từng khối chữ cắt ra.
  chi_chu — "Chỉ chữ" (prompt_ocr) cả trang, không bố cục.
Trần token mỗi lần sinh: --tran-token (mặc định 6000; web dùng 8 × token ảnh + 512 ≈ 17 000 với trang 1600 px — trang
bình thường không chạm 6000; chạm trần thì ghi cờ "chạm trần", đó là dấu hiệu chạy vòng). Lưu output thô (đầu + đuôi)
để xem dots hỏng ở đâu. Chạy song song: mỗi GPU một bản dots, lấy việc từ chung một hàng đợi. Lỗi một lượt (vd. hết VRAM
ở ×2) → ghi lỗi, đi tiếp. Chạy lại = đi tiếp. Ra: <out>/tom_tat.md, ket_qua.jsonl → results-htr/<tên out>/.
"""
from __future__ import annotations

import argparse
import json
import queue
import re
import sys
import threading
import time
import traceback
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from htr_test.cham_trang import NHAN, TEXT_CATS, diem  # noqa: E402

CACH = {"day_du": "prompt_layout_all_en", "khoi": "prompt_layout_only_en", "chi_chu": "prompt_ocr"}
# khối trọn vẹn trong JSON bố cục (kể cả khi output bị cắt giữa chừng)
_KHOI = re.compile(r'\{\s*"bbox":\s*\[[^\]]*\]\s*,\s*"category":\s*"([^"]+)"\s*,\s*"text":\s*"((?:[^"\\]|\\.)*)"\s*\}')


def cuu_khoi(raw: str) -> str:
    out = []
    for cat, t in _KHOI.findall(raw or ""):
        if cat in TEXT_CATS:
            try:
                out.append(json.loads(f'"{t}"'))
            except ValueError:
                out.append(t)
    return "\n".join(out)


def nap(gpu: int, tran: int):
    from ocrbench.convert import Converter

    return Converter(ROOT / "inference" / "config.yaml", "dots_mocr", gpus=str(gpu),
                     params={"device_map": {"": f"cuda:{gpu}"}, "max_new_tokens": tran})


def _sinh(ad, img, mode: str) -> dict:
    t = time.time()
    r = ad.parse_image(img, mode)
    e = r.get("extra") or {}
    return {"r": r, "tok": int(e.get("new_tokens") or 0), "tran": bool(e.get("hit_max_tokens")),
            "vong": bool(e.get("stopped_loop")), "giay": time.time() - t}


def mot_luot(conv, path: Path, cach: str, phong: float) -> dict:
    page = Image.open(path).convert("RGB")
    img, _ = conv._prepare(page, path, 1, "text")
    if phong != 1:
        img = img.resize((round(img.width * phong), round(img.height * phong)), Image.LANCZOS)
    ad = conv.adapter
    s = _sinh(ad, img, CACH[cach])
    r = s["r"]
    kq = {"anh": list(img.size), "tok": s["tok"], "giay": s["giay"], "co": [], "raw_dau": (r["response"] or "")[:3000],
          "raw_duoi": (r["response"] or "")[-1500:]}
    if s["tran"]:
        kq["co"].append("chạm trần")
    if s["vong"]:
        kq["co"].append("dừng vòng")
    if cach == "chi_chu":
        kq["chu"] = r.get("md") or r["response"] or ""
    elif cach == "day_du":
        cells = r.get("cells")
        if cells is None:
            kq["co"].append("JSON hỏng")
            kq["chu"] = ""
            kq["chu_cuu"] = cuu_khoi(r["response"])
        else:
            kq["chu"] = "\n".join(c.get("text") or "" for c in cells if c.get("category") in TEXT_CATS)
        kq["so_khoi"] = len(cells or [])
    else:  # khoi: bố cục không chữ → prompt_ocr từng khối chữ
        cells = r.get("cells") or []
        kq["so_khoi"] = len(cells)
        if r.get("cells") is None:
            kq["co"].append("JSON hỏng")
        doc = []
        for c in cells:
            bb = c.get("bbox")
            if c.get("category") not in TEXT_CATS or not bb or len(bb) != 4:
                continue
            x0, y0, x1, y1 = [int(round(v)) for v in bb]
            if x1 - x0 < 8 or y1 - y0 < 8:
                continue
            x0, y0, x1, y1 = max(0, x0 - 4), max(0, y0 - 4), min(img.width, x1 + 4), min(img.height, y1 + 4)
            k = _sinh(ad, img.crop((x0, y0, x1, y1)), "prompt_ocr")
            kq["tok"] += k["tok"]
            kq["giay"] += k["giay"]
            if k["tran"] and "khối chạm trần" not in kq["co"]:
                kq["co"].append("khối chạm trần")
            doc.append(k["r"].get("md") or k["r"]["response"] or "")
        kq["chu"] = "\n".join(doc)
    kq["giay"] = round(kq["giay"])
    return kq


def bao_cao(out: Path, ket: list[dict], viec: list[tuple]) -> str:
    cot = []
    for _, cach, phong in viec:
        if (cach, phong) not in cot:
            cot.append((cach, phong))
    trang = sorted({k["trang_id"] for k in ket})
    idx = {(k["trang_id"], k["cach"], k["phong"]): k for k in ket}
    rows = ["# Thử dots.mocr — phóng ảnh / cách đọc (tài liệu thật)", "",
            f"Cập nhật: {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · {len(ket)}/{len(viec)} lượt", "",
            "Ô: **đúng ký tự** / đúng từ (theo thứ tự) · thu hồi từ. Cột = cách đọc ×phóng (so với ảnh web đã chuẩn bị). "
            "day_du ×1 = cột dots của cham_trang. `cứu` = chữ cứu từ JSON bị cắt. Yêu cầu đánh máy ≥ 90%.", ""]
    for f, ten in NHAN.items():
        rows += [f"## So với {ten} (`{f}`)", "", "| trang | " + " | ".join(f"{c} ×{p:g}" for c, p in cot) + " |",
                 "|---|" + "---:|" * len(cot)]
        for t in trang:
            o = []
            for c, p in cot:
                k = idx.get((t, c, p))
                if not k:
                    o.append("…")
                elif k.get("loi"):
                    o.append("LỖI")
                elif f in k["diem"]:
                    d = k["diem"][f]
                    s = f"**{100 * d['dung']:.1f}%** / {100 * d['dung_tu']:.1f}% · {100 * d['thu_hoi_tu']:.0f}%"
                    if "cuu" in k:
                        s += f" (cứu {100 * k['cuu'][f]['dung']:.1f}%)"
                    o.append(s)
                else:
                    o.append("—")
            rows.append(f"| {t} | " + " | ".join(o) + " |")
        rows.append("")
    rows += ["## Chi tiết từng lượt", "", "| trang | cách | ×phóng | ảnh (px) | khối | token | giây | GPU | cờ |",
             "|---|---|---:|---|---:|---:|---:|---:|---|"]
    for k in sorted(ket, key=lambda k: (k["trang_id"], k["cach"], k["phong"])):
        co = ", ".join(k.get("co") or []) + (f" LỖI: {k['loi'][:120]}" if k.get("loi") else "")
        rows.append(f"| {k['trang_id']} | {k['cach']} | {k['phong']:g} | {'×'.join(map(str, k.get('anh') or []))} | "
                    f"{k.get('so_khoi', '')} | {k.get('tok', '')} | {k.get('giay', '')} | {k['gpu']} | {co} |")
    md = "\n".join(rows) + "\n"
    (out / "tom_tat.md").write_text(md, encoding="utf-8")
    (out / "tom_tat.json").write_text(json.dumps([{x: k.get(x) for x in ("trang_id", "cach", "phong", "diem", "cuu", "co",
                                                                         "tok", "giay", "loi")} for k in ket],
                                                 ensure_ascii=False, indent=1), encoding="utf-8")
    return md


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gpus", default="0,1", help="mỗi GPU một bản dots, lấy việc từ chung hàng đợi")
    ap.add_argument("--phong", default="1,2,1.5", help="mức phóng, theo thứ tự chạy")
    ap.add_argument("--cach", default="day_du,khoi,chi_chu")
    ap.add_argument("--trang", default="image_3,image_1,image_4,image_2", help="thứ tự chạy")
    ap.add_argument("--tran-token", type=int, default=6000)
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    data, out = Path(a.data), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    trang = [t for t in a.trang.split(",") if (data / t / "anh.jpeg").exists()]
    if not trang:
        sys.exit(f"✘ LỖI không thấy {data}/<{a.trang}>/anh.jpeg")
    cach = [c for c in a.cach.split(",") if c]
    if set(cach) - set(CACH):
        sys.exit(f"✘ LỖI --cach chỉ nhận {list(CACH)}")
    viec = [(t, c, float(p)) for p in a.phong.split(",") for t in trang for c in cach]
    sync = None
    if a.push:
        from htr_test.sync import Sync

        sync = Sync(out)
        sync.restore()
    f_kq = out / "ket_qua.jsonl"
    cu = {}  # dòng sau ghi đè dòng trước cùng lượt; lượt LỖI → chạy lại
    for x in (f_kq.read_text(encoding="utf-8").splitlines() if f_kq.exists() else []):
        if x.strip():
            k = json.loads(x)
            cu[(k["trang_id"], k["cach"], k["phong"])] = k
    ket = [k for k in cu.values() if not k.get("loi")]
    xong = {(k["trang_id"], k["cach"], k["phong"]) for k in ket}
    con = [v for v in viec if v not in xong]
    print(f"== {len(viec)} lượt · đã có {len(xong & set(viec))} · còn {len(con)} · trần {a.tran_token} token", flush=True)
    nhan = {t: {f: json.loads((data / t / f).read_text(encoding="utf-8"))["text"] for f in NHAN if (data / t / f).exists()}
            for t in trang}
    if con:
        import torch

        gpus = [int(x) for x in a.gpus.split(",") if x.strip()][: max(1, torch.cuda.device_count())]
        q = queue.Queue()
        for v in con:
            q.put(v)
        khoa = threading.Lock()
        hong_nap = []

        def tho(g: int):
            try:
                conv = nap(g, a.tran_token)
            except Exception:  # noqa: BLE001
                print(traceback.format_exc(), flush=True)
                hong_nap.append(g)
                return
            print(f"   dots nạp xong trên cuda:{g}", flush=True)
            while True:
                try:
                    t, c, p = q.get_nowait()
                except queue.Empty:
                    break
                k = {"trang_id": t, "cach": c, "phong": p, "gpu": g}
                try:
                    k.update(mot_luot(conv, data / t / "anh.jpeg", c, p))
                    k["diem"] = {f: diem(n, k["chu"]) for f, n in nhan[t].items()}
                    if "chu_cuu" in k:
                        k["cuu"] = {f: diem(n, k["chu_cuu"]) for f, n in nhan[t].items()}
                except Exception as e:  # noqa: BLE001 — một lượt hỏng (vd. hết VRAM) không dừng cả buổi thử
                    k["loi"] = f"{type(e).__name__}: {e}"
                    print(traceback.format_exc(), flush=True)
                    torch.cuda.empty_cache()
                with khoa:
                    ket.append(k)
                    with open(f_kq, "a", encoding="utf-8") as fo:
                        fo.write(json.dumps(k, ensure_ascii=False) + "\n")
                    d = (k.get("diem") or {}).get("nhan.json")
                    print(f"✔ {t} {c} ×{p:g} [cuda:{g}]: " + (f"{100 * d['dung']:.1f}%" if d else "—") +
                          f" · {k.get('tok', '?')} token · {k.get('giay', '?')} s" +
                          (f" · {', '.join(k['co'])}" if k.get("co") else "") + (f" · LỖI {k['loi']}" if k.get("loi") else ""),
                          flush=True)
                    bao_cao(out, ket, viec)
                    if sync:
                        sync.push(f"thử dots: {t} {c} ×{p:g} ({len(ket)}/{len(viec)})")
            conv.close()

        th = [threading.Thread(target=tho, args=(g,)) for g in gpus]
        for x in th:
            x.start()
        for x in th:
            x.join()
        if len(hong_nap) == len(gpus):
            sys.exit(f"✘ LỖI không nạp được dots trên GPU {hong_nap}")
        if not q.empty():
            sys.exit(f"✘ LỖI còn {q.qsize()} lượt chưa chạy (GPU nạp hỏng: {hong_nap})")
    print(bao_cao(out, ket, viec), flush=True)
    if sync:
        sync.push("thử dots — XONG")
    print("✔ XONG THỬ DOTS", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
