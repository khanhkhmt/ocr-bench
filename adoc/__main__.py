"""Lệnh của bản chép pipeline (chạy trong thư mục gốc ocr-bench, python = /kaggle/working/venvs/adoc, cài bằng
bash htr_test/cai_adoc.sh):

    $PY -m adoc check                  # GPU, thư viện, Kraken, cache model → dòng cuối OK / NOT READY
    $PY -m adoc download               # tải model (~15 GB) + model tách dòng Muharaf
    $PY -m adoc kiem --out <thư mục>   # đọc lại 4 trang mẫu, so 16 số với mốc 2026-10-19 (xem NGUON.md)
    $PY -m adoc kiem --noi 50 --out …  # đo 4 trang mẫu với dòng nới 50 % (mặc định mới): số + chênh so với mốc
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from . import NGUON, __version__, config

HERE = Path(__file__).resolve().parent
TRANG_MAU = HERE / "trang_mau"
MAU_KQ = HERE / "mau_ket_qua"
DOC = ("main", "dots", "ft3", "ft4")


def cmd_check(a) -> int:
    import importlib
    import platform
    import shutil

    from .lines import kraken_paths

    print(f"adoc {__version__} (bản chép {NGUON}) · {HERE} · Python {platform.python_version()} · {platform.platform()}")
    for mod in ("torch", "transformers", "peft", "qwen_vl_utils", "pypdfium2", "fitz", "psutil", "rapidfuzz"):
        try:
            m = importlib.import_module(mod)
            print(f"  {mod:14s} {getattr(m, '__version__', getattr(m, 'VersionBind', 'ok'))}")
        except Exception as e:  # noqa: BLE001
            print(f"  {mod:14s} MISSING ({type(e).__name__}: {e})")
    ok = True
    try:
        import torch

        n = torch.cuda.device_count()
        print(f"  CUDA {torch.version.cuda} · {n} GPU(s)")
        for i in range(n):
            p = torch.cuda.get_device_properties(i)
            print(f"    cuda:{i} {p.name} · {p.total_memory / 2**30:.1f} GiB · compute {p.major}.{p.minor}"
                  f" ({'bf16' if p.major >= 8 else 'fp16'})")
        if n == 0:
            ok = False
            print("  ✘ không có GPU — dots.mocr cần GPU CUDA")
    except Exception as e:  # noqa: BLE001
        ok = False
        print(f"  ✘ torch: {e}")
    try:
        import transformers

        if transformers.__version__ != "4.56.1":
            ok = False
            print(f"  ✘ transformers {transformers.__version__}: mốc đo bằng 4.56.1 (bản khác đổi cách sinh chữ)")
    except ImportError:
        ok = False
    exe, model = kraken_paths()
    print(f"  Kraken: {exe or 'MISSING'} · model tách dòng: {model or 'MISSING'}")
    if not exe or not model:
        ok = False  # thí nghiệm đo dòng Kraken cắt: thiếu Kraken thì pipeline lặng lẽ chuyển sang chiếu ngang → sai số
        print("  ✘ thiếu Kraken / model tách dòng — bash htr_test/cai_adoc.sh")
    try:
        import psutil

        vm = psutil.virtual_memory()
        print(f"  RAM {vm.total / 2**30:.1f} GiB (còn {vm.available / 2**30:.1f})")
    except ImportError:
        pass
    du = shutil.disk_usage(Path.home())
    print(f"  ổ (home) còn {du.free / 2**30:.1f} GiB")
    try:
        from huggingface_hub import scan_cache_dir

        have = {r.repo_id: r.size_on_disk for r in scan_cache_dir().repos}
        for rid in (config.DOTS_MODEL, config.HTR_BASE, config.HTR_ADAPTERS):
            print(f"  model {rid}: " + (f"có ({have[rid] / 2**30:.1f} GiB)" if rid in have else "CHƯA TẢI"))
    except Exception:  # noqa: BLE001
        pass
    print("OK" if ok else "NOT READY")
    return 0 if ok else 1


def cmd_download(a) -> int:
    import urllib.request

    from huggingface_hub import snapshot_download

    for rid, pat in ((config.DOTS_MODEL, None), (config.HTR_BASE, None),
                     (config.HTR_ADAPTERS, [f"{config.MAIN}/*", f"{config.CHECK}/*"])):
        t = time.time()
        p = snapshot_download(rid, allow_patterns=pat)
        print(f"{rid} → {p} ({time.time() - t:.0f} s)")
    if not config.KRAKEN_SEG_MODEL.exists():
        config.KRAKEN_SEG_MODEL.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(config.MUHARAF_SEG_URL, config.KRAKEN_SEG_MODEL)
    print(f"model tách dòng Kraken → {config.KRAKEN_SEG_MODEL}")
    return 0


def page_json(res, page_no: int) -> dict:
    """Trang → JSON cùng dạng export.page_json của arabic-doc-ocr (các trường evaluate.py và llm_sua.py đọc)."""
    ft3, ft4 = res.readings[config.MAIN], res.readings[config.CHECK]
    return {"page": page_no, "info": res.info, "image_size": list(res.image.size),
            "blocks": [{"n": bi + 1, "category": b.get("category"), "bbox": b.get("bbox"),
                        "reader": res.sources.get(bi, (None,))[0], "dots_ft3_agreement": res.sources.get(bi, (0, None))[1],
                        "text": res.texts["main"].get(bi), "dots": b.get("text"),
                        "lines": [{"bbox": list(L.box), "ft3": ft3[n], "ft4": ft4[n]}
                                  for n, L in enumerate(res.lines) if L.block == bi]}
                       for bi, b in enumerate(res.blocks)]}


def _khoi(js: dict) -> list[tuple]:
    return [(b.get("category"), b.get("reader"), b.get("text"), b.get("dots"),
             tuple((L["ft3"], L["ft4"]) for L in b.get("lines", [])))
            for p in js["pages"] for b in p["blocks"]]


def cmd_kiem(a) -> int:
    import torch

    from . import evaluate as ev
    from .pipeline import Pipeline, load_pages

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    mau = json.loads((MAU_KQ / "eval.json").read_text(encoding="utf-8"))
    pages = sorted(d.name for d in TRANG_MAU.glob("page_*"))
    if pages != sorted(mau):
        sys.exit(f"✘ LỖI: trang mẫu {pages} khác mốc {sorted(mau)}")
    n_gpu = torch.cuda.device_count()
    dd, hd = a.dots_device or "cuda:0", a.htr_device or ("cuda:1" if n_gpu >= 2 else "cuda:0")
    offload = "none" if dd != hd else "unload"
    noi = a.noi  # kiểm bản chép: luôn nới 0 % như lần đo mốc (mặc định sản phẩm là config.LINE_PAD_PCT)
    print(f"adoc {HERE} · dots {dd} · ft3/ft4 {hd} · offload {offload} · nới dòng {noi} %", flush=True)
    pipe = Pipeline(dd, hd, offload=offload, line_pad_pct=noi)
    rows, khop, so_khoi, t_all = [], True, [0, 0], time.time()
    for page in pages:
        ref_js = json.loads((MAU_KQ / f"{page}_page.json").read_text(encoding="utf-8"))
        page_type = ref_js["pages"][0]["info"]["page_type"]  # đúng loại trang của lần đo mốc
        t = time.time()
        res = pipe.process_document(load_pages(TRANG_MAU / page / "page.jpeg"), page_type)
        js = {"document": f"{page}_page", "pages": [page_json(r, i + 1) for i, r in enumerate(res)]}
        (out / f"{page}_page.json").write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
        label = json.loads((TRANG_MAU / page / "label.json").read_text(encoding="utf-8"))["text"]
        rd = ev.readings(js)
        sc = {k: round(100 * ev.score(label, rd[k])["chars"], 2) for k in DOC}
        moc = {k: round(100 * mau[page][k]["chars"], 2) for k in DOC}
        a_k, b_k = _khoi(js), _khoi(ref_js)
        giong = sum(x == y for x, y in zip(a_k, b_k))
        so_khoi[0] += giong
        so_khoi[1] += max(len(a_k), len(b_k))
        ok = sc == moc
        khop &= ok
        rows.append({"page": page, "type": page_type, "now": sc, "moc": moc, "ok": ok,
                     "blocks_same": giong, "blocks": max(len(a_k), len(b_k)), "seconds": round(time.time() - t, 1)})
        print(f"{('✔' if ok else '✘') if not noi else '·'} {page} ({page_type}): " + " · ".join(f"{k} {sc[k]:.2f} (mốc {moc[k]:.2f})"
                                                                          for k in DOC)
              + f" · khối giống mốc {giong}/{max(len(a_k), len(b_k))} · {time.time() - t:.0f} s", flush=True)
    hd_ = f"{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · dots {dd} · ft3/ft4 {hd} · offload {offload} · " \
          f"{time.time() - t_all:.0f} s"
    if noi:
        tb = {k: (sum(r["now"][k] for r in rows) / len(rows), sum(r["moc"][k] for r in rows) / len(rows)) for k in DOC}
        L = [f"# Đo adoc với dòng Kraken nới {noi} % — 4 trang mẫu", "", hd_, "",
             f"% ký tự đúng (evaluate.py): nới {noi} % (chênh so với mốc 2026-10-19 = nới 0 %, mau_ket_qua/eval.json). "
             "Trang đánh máy: chữ chính = dots, không đổi; nới khung chỉ đổi ảnh dòng (ft3 / ft4 và chữ chính của "
             "trang viết tay).", "",
             "| trang | loại | chính | dots | ft3 | ft4 |", "|---|---|---:|---:|---:|---:|"]
        L += [f"| {r['page']} | {r['type']} | " + " | ".join(f"{r['now'][k]:.2f} ({r['now'][k] - r['moc'][k]:+.2f})"
                                                           for k in DOC) + " |" for r in rows]
        L.append("| **TB 4 trang** | | " + " | ".join(f"**{tb[k][0]:.2f}** ({tb[k][0] - tb[k][1]:+.2f})" for k in DOC) + " |")
    else:
        L = [f"# Kiểm bản chép adoc ({NGUON}) — 4 trang mẫu", "", hd_, "",
             "% ký tự đúng (evaluate.py) bây giờ / mốc 2026-10-19 (mau_ket_qua/eval.json).", "",
             "| trang | loại | chính | dots | ft3 | ft4 | khối giống mốc | khớp |", "|---|---|---:|---:|---:|---:|---:|---|"]
        for r in rows:
            L.append(f"| {r['page']} | {r['type']} | " + " | ".join(f"{r['now'][k]:.2f} / {r['moc'][k]:.2f}" for k in DOC)
                     + f" | {r['blocks_same']}/{r['blocks']} | {'✔' if r['ok'] else '✘'} |")
    (out / "kiem.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "kiem.json").write_text(json.dumps({"nguon": NGUON, "adoc": str(HERE), "noi": noi, "khop": khop,
                                               "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(L))
    if noi:
        print(f"✔ ĐO NỚI {noi} % XONG: chữ chính TB 4 trang {tb['main'][0]:.2f} (mốc {tb['main'][1]:.2f}, "
              f"{tb['main'][0] - tb['main'][1]:+.2f}) · {out}/kiem.md")
        return 0
    if khop:
        print(f"✔ ADOC KHỚP MỐC: 16/16 số bằng mốc · khối giống mốc {so_khoi[0]}/{so_khoi[1]}")
        return 0
    print(f"✘ ADOC KHÔNG KHỚP MỐC: xem bảng trên ({out}/kiem.md) · khối giống mốc {so_khoi[0]}/{so_khoi[1]}")
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m adoc", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("download")
    p = sub.add_parser("kiem")
    p.add_argument("--out", required=True)
    p.add_argument("--dots-device", default=None)
    p.add_argument("--htr-device", default=None)
    p.add_argument("--noi", type=int, default=0, help="nới dòng Kraken %% độ dày (0 = kiểm bản chép so với mốc)")
    a = ap.parse_args(argv)
    return {"check": cmd_check, "download": cmd_download, "kiem": cmd_kiem}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
