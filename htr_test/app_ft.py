"""Web đọc chữ tay bằng ft3 (bộ đọc chính) + ft4 (bộ đọc kiểm chéo) — bố cục do dots.mocr.

    <python venv dots> -m htr_test.app_ft [--port 7862] [--gpu-dots 0] [--gpu-doc 1]
    APP=app_ft PORT=7862 bash htr_test/start.sh

Tab "Trang tài liệu": ảnh / PDF → dots chia khối (ảnh phóng tới 2400 px; dots hỏng → cả trang một khối) → Kraken tách
dòng → ft3 và ft4 đọc TỪNG dòng → bảng từng dòng: ảnh dòng | ft3 (từ ft4 đọc khác tô vàng, rê chuột xem ft4 đọc gì) |
ft4; khối Hebrew (khối công chứng) giữ chữ dots, không đưa cho ft3/ft4; khung dòng trên ảnh trang: xanh lá = hai bản đọc trùng, cam = khác (cần soát). Tải DOCX (chữ ft3, tô vàng +
chú thích chỗ ft4 đọc khác), TXT, JSON.
Loại chữ: viết tay → ft3 đọc / ft4 kiểm chéo; đánh máy → chữ dots (90% trên trang đánh máy, ft3 chỉ ~80%) / ft3 kiểm
chéo; hỗn hợp → mỗi khối tự chọn: dots và ft3 đọc trùng ≥ 35% số từ thì coi là đánh máy (thử nghiệm, chưa đo).
Tải về: ZIP tất cả, DOCX, TXT (chữ chính / ft3 / ft4), HTML bảng soát, JSON, ảnh trang có khung.
Tab "Một dòng": thả ảnh một dòng → ft3 / ft4 (+ JSON).

ft3, ft4 = Baseer-Nakba + LoRA (htr_train/README.md), adapter ở repo HF công khai khanh99/htr-baseer-nakba-ft (ft3/, ft4/; bản gốc khanh99/htr-ckpt/ft*/best).
500 dòng mỗi tập (đúng ký tự): ft3 Omar 93,4% · người viết lạ 94,7% · Muharaf 91,4%; ft4 92,8% · 95,0% · 92,0%.
Tô vàng theo từ (ft3 + ft4): tô ~13–19% số từ, bắt 57–75% số từ sai; ~2/3 từ bị tô là sai thật.
Trang thật viết tay (image_2): ft3 72,6% · ft4 72,9% · Baseer gốc 62,8% — vẫn là bản nháp cần người soát.
"""

from __future__ import annotations

import argparse
import html
import json
import tempfile
import time
from pathlib import Path

import gradio as gr
from PIL import ImageDraw

from .app import CSS, GR6, _b64, load_pages
from .danh_dau import so_khop_tu, ty_le_trung
from .models import BaseerNakba
from .trang import TEXT_CATS, nap_dots, phan_trang, sua_chu
from .xuat_docx import xuat_docx

FT = {"ft3": "hf:khanh99/htr-baseer-nakba-ft/ft3", "ft4": "hf:khanh99/htr-baseer-nakba-ft/ft4"}
AD = {"ft3": "a0", "ft4": "a1"}  # tên adapter trong BaseerNakba (theo thứ tự nạp)
DOTS_FULL, DOTS_LAYOUT = "dots đọc cả chữ (để so với khối đánh máy)", "dots chỉ chia khối (nhanh hơn)"
S = {"dots": None, "baseer": None, "gpu_dots": 0, "gpu_doc": 0}
CSS_FT = CSS + """
.htr mark{background:#ffe14d;padding:0 1px} .htr .ok{color:#1a7f37} .htr .ngo{color:#c2410c}
.htr .tom{display:flex;gap:18px;flex-wrap:wrap;margin:6px 0} .htr .tom b{font-size:20px}
.htr tr.khoi td{background:#eef4ff}
"""


def dots():
    if S["dots"] is None:
        S["dots"] = nap_dots(S["gpu_dots"])
    return S["dots"]


def baseer():
    if S["baseer"] is None:
        b = BaseerNakba(device=f"cuda:{S['gpu_doc']}", lora=[FT["ft3"], FT["ft4"]]).load()
        if b.adapters != [AD["ft3"], AD["ft4"]]:
            raise RuntimeError(f"adapter nạp ra {b.adapters}, cần {list(AD.values())}")
        S["baseer"] = b
    return S["baseer"]


def doc_dong(crops, progress=None, p0: float = 0.4, p1: float = 0.95) -> dict[str, list[str]]:
    """ft3 rồi ft4 đọc từng dòng (lô 1 — như lúc chấm; lô lớn làm Baseer dừng sớm)."""
    b, out, n = baseer(), {"ft3": [], "ft4": []}, max(1, len(crops))
    for k, ten in enumerate(("ft3", "ft4")):
        for i, im in enumerate(crops):
            if progress is not None:
                progress(p0 + (p1 - p0) * (k * n + i) / (2 * n), desc=f"{ten} đọc dòng {i + 1}/{len(crops)}")
            out[ten].append(sua_chu(b.read([im], adapter=AD[ten])[0]))
    return out


def to_vang(chinh: str, phu: str) -> str:
    """HTML: chữ ft3, từ ft4 đọc khác tô vàng (rê chuột → ft4 đọc gì)."""
    o = []
    for w, ngo, alt in so_khop_tu(chinh, phu):
        w = html.escape(w)
        o.append(f"<mark title='ft4: {html.escape(alt)}'>{w}</mark>" if ngo else w)
    return " ".join(o)


def doc_trang(page, path: Path, chu_dots: bool, progress) -> dict:
    progress(0.05, desc="dots đang chia khối (ảnh phóng tới 2400 px)…")
    r = phan_trang(dots(), page, path, "kraken_muharaf", chu_dots=chu_dots)
    progress(0.35, desc=f"{len(r['jobs'])} dòng — ft3 / ft4 đang đọc…")
    t = time.time()
    r["doc"] = doc_dong([j[2] for j in r["jobs"]], progress)
    r["giay_doc"] = round(time.time() - t)
    return r


def ve(r: dict):
    im = r["img"].copy()
    dr = ImageDraw.Draw(im)
    for bi, b in enumerate(r["blocks"]):
        bb = b.get("bbox")
        if bb and len(bb) == 4:
            mau = (147, 51, 234) if b.get("hebrew") else (30, 90, 220)
            dr.rectangle([int(round(v)) for v in bb], outline=mau, width=3)
            dr.text((bb[0] + 4, bb[1] + 2), str(bi + 1), fill=mau)
    for n, (bi, box, _, poly) in enumerate(r["jobs"]):
        trung = ty_le_trung(r["doc"]["ft3"][n], r["doc"]["ft4"][n]) >= 0.999
        mau = (26, 127, 55) if trung else (234, 88, 12)
        if poly:
            dr.polygon([tuple(p) for p in poly], outline=mau, width=2)
        else:
            dr.rectangle(box, outline=mau, width=2)
    return im


LOAI_TAY = "Viết tay — ft3 đọc, ft4 kiểm chéo"
LOAI_MAY = "Đánh máy — dots đọc, ft3 kiểm chéo"
LOAI_TRON = "Hỗn hợp — tự chọn theo từng khối (thử nghiệm)"
NGUONG_MAY = 0.35  # khối mà dots và ft3 đọc trùng ≥ 35% số từ → coi là đánh máy (dots đọc chữ tay chỉ ~5–10% từ đúng)


def chon_nguon(r: dict, loai: str, chu_dots: bool) -> dict[int, tuple[str, float | None]]:
    """→ {khối: (bộ đọc chính "ft3" | "dots" | "hebrew", tỉ lệ từ dots ≈ ft3)} cho các khối chữ."""
    out = {}
    for bi, b in enumerate(r["blocks"]):
        if b.get("category") not in TEXT_CATS:
            continue
        if b.get("hebrew"):
            out[bi] = ("hebrew", None)
            continue
        ft3 = " ".join(r["doc"]["ft3"][n] for n, j in enumerate(r["jobs"]) if j[0] == bi)
        dt = b.get("text") or ""
        trung = ty_le_trung(dt, ft3) if chu_dots and dt.strip() and ft3.strip() else None
        if not chu_dots or not dt.strip():
            out[bi] = ("ft3", trung)
        elif loai == LOAI_MAY or not ft3.strip():
            out[bi] = ("dots", trung)
        elif loai == LOAI_TRON:
            out[bi] = ("dots" if trung is not None and trung >= NGUONG_MAY else "ft3", trung)
        else:
            out[bi] = ("ft3", trung)
    return out


def ban_doc(r: dict, nguon: dict) -> dict[str, dict[int, str]]:
    """Chữ theo khối: chinh / phu (DOCX, TXT chính) + ft3 / ft4 / dots nguyên bản."""
    jobs, doc = r["jobs"], r["doc"]
    o = {k: {} for k in ("chinh", "phu", "ft3", "ft4", "dots")}
    for bi, b in enumerate(r["blocks"]):
        if bi not in nguon:
            continue
        for ten in ("ft3", "ft4"):
            o[ten][bi] = "\n".join(doc[ten][n] for n, j in enumerate(jobs) if j[0] == bi)
        o["dots"][bi] = b.get("text") or ""
        ng = nguon[bi][0]
        if ng == "hebrew":
            o["chinh"][bi] = o["phu"][bi] = o["dots"][bi]  # giữ chữ dots, không tô
        elif ng == "dots":
            o["chinh"][bi], o["phu"][bi] = o["dots"][bi], o["ft3"][bi]
        else:
            o["chinh"][bi], o["phu"][bi] = o["ft3"][bi], o["ft4"][bi]
    return o


def bang(r: dict, k: int, n_trang: int, chu_dots: bool, nguon: dict) -> tuple[str, dict]:
    ft3, ft4, jobs = r["doc"]["ft3"], r["doc"]["ft4"], r["jobs"]
    tu = ngo = dong_khac = 0
    rows = []
    for bi, b in enumerate(r["blocks"]):
        cat = b.get("category")
        idx = [n for n, j in enumerate(jobs) if j[0] == bi]
        if cat not in TEXT_CATS:
            rows.append(f"<tr class=khoi><td colspan=3>Khối {bi + 1} · {html.escape(str(cat))} — không phải chữ "
                        "(giữ nguyên ảnh trong DOCX)</td></tr>")
            continue
        ng, trung = nguon[bi]
        if ng == "hebrew":
            rows.append(f"<tr class=khoi><td colspan=3>Khối {bi + 1} · HEBREW — ft3/ft4 chỉ đọc chữ Ả Rập nên KHÔNG đọc "
                        f"khối này; chữ dots đọc (chưa kiểm):<div class=ar>{html.escape(b.get('text') or '')}</div></td></tr>")
            continue
        tl = f" · dots ≈ ft3: {100 * trung:.0f}% từ" if trung is not None else ""
        dong_html = []
        for n in idx:
            tk = so_khop_tu(ft3[n], ft4[n])
            m = sum(d for _, d, _ in tk)
            if ng == "ft3":
                tu, ngo = tu + len(tk), ngo + m
                dong_khac += bool(m)
            dau = "<span class=ok>✓ trùng</span>" if not m else f"<span class=ngo>{m}/{len(tk)} từ khác</span>"
            dong_html.append(f"<tr><td><img src='data:image/jpeg;base64,{_b64(jobs[n][2], 56)}'><br>"
                             f"<span class=meta>dòng {n + 1} · {dau}</span></td>"
                             f"<td class=ar>{to_vang(ft3[n], ft4[n])}</td><td class=ar>{html.escape(ft4[n])}</td></tr>")
        if ng == "dots":  # khối đánh máy: chữ dots là bản chính, tô vàng chỗ ft3 đọc khác
            tk = so_khop_tu(b.get("text") or "", " ".join(ft3[n] for n in idx))
            m = sum(d for _, d, _ in tk)
            tu, ngo = tu + len(tk), ngo + m
            chu = " ".join(f"<mark title='ft3: {html.escape(alt)}'>{html.escape(w)}</mark>" if d else html.escape(w)
                           for w, d, alt in tk)
            rows.append(f"<tr class=khoi><td colspan=3>Khối {bi + 1} · {html.escape(str(cat))} · ĐÁNH MÁY → chữ dots"
                        f"{tl} · tô vàng = ft3 đọc khác</td></tr><tr><td colspan=3 class=ar>{chu}</td></tr>")
            if idx:
                rows.append(f"<tr><td colspan=3><details><summary>{len(idx)} dòng ft3 / ft4 của khối này</summary>"
                            f"<table>{''.join(dong_html)}</table></details></td></tr>")
            continue
        dots_txt = (f"<details><summary>chữ dots đọc khối này (bộ đọc đánh máy)</summary><div class=ar>"
                    f"{html.escape(b.get('text') or '')}</div></details>") if chu_dots and b.get("text") else ""
        rows.append(f"<tr class=khoi><td colspan=3>Khối {bi + 1} · {html.escape(str(cat))} · {len(idx)} dòng → ft3{tl}"
                    f"{' · DỰ PHÒNG (dots không chia được khối)' if b.get('du_phong') else ''}{dots_txt}</td></tr>")
        rows += dong_html
    dem = {x: sum(v[0] == x for v in nguon.values()) for x in ("ft3", "dots", "hebrew")}
    st = {"dong": len(jobs), "dong_khac": dong_khac, "tu": tu, "tu_ngo": ngo, "khoi": dem}
    ghi = "".join(f"<p class=meta>⚠ {html.escape(g)}</p>" for g in r["ghi_chu"])
    tom = (f"<div class=tom><span><b>{len(jobs)}</b> dòng</span><span><b>{dong_khac}</b> dòng ft3 ≠ ft4</span>"
           f"<span><b>{100 * ngo / max(1, tu):.0f}%</b> từ tô vàng ({ngo}/{tu})</span>"
           f"<span>khối: <b>{dem['ft3']}</b> ft3 · <b>{dem['dots']}</b> dots · <b>{dem['hebrew']}</b> Hebrew</span></div>"
           f"<p class=meta>Trang {k + 1}/{n_trang} · {len(r['blocks'])} khối · tách dòng {', '.join(r['tach']) or '—'} · "
           f"dots ×{r['phong']:g}, {r['giay_dots']} s · ft3 + ft4 {r['giay_doc']} s</p>{ghi}"
           "<p class=meta>Tô vàng = bản kiểm chéo đọc khác ở từ đó (rê chuột để xem). Đo trên 500 dòng/tập: ft3 + ft4 tô "
           "~13–19% số từ, bắt 57–75% số từ sai — từ KHÔNG tô vẫn có thể sai, nhất là chữ số, tên riêng.</p>")
    head = "<tr><th style='width:34%'>ảnh dòng</th><th>ft3 (đọc chính)</th><th>ft4 (kiểm chéo)</th></tr>"
    return f"<div class=htr>{tom}<table>{head}{''.join(rows)}</table></div>", st


def _ghep(per: dict[int, str]) -> str:
    return "\n\n".join(t for _, t in sorted(per.items()) if t.strip())


def run_page(file, page_no, tat_ca, dots_mode, loai, progress=gr.Progress()):
    if not file:
        return None, "<p>Chưa có file.</p>", "", None
    path = Path(file if isinstance(file, str) else file.name)
    pages = load_pages(str(path))
    ks = list(range(len(pages))) if tat_ca else [min(max(1, int(page_no or 1)), len(pages)) - 1]
    chu_dots = dots_mode == DOTS_FULL
    out = Path(tempfile.mkdtemp(prefix="ft34_"))
    ten = path.stem
    htmls, txt, data, vis = [], {x: [] for x in ("chinh", "ft3", "ft4")}, [], None
    from docx import Document  # noqa: F401 — báo thiếu python-docx sớm

    files = []
    for i, k in enumerate(ks):
        r = doc_trang(pages[k], path, chu_dots,
                      lambda p, desc="": progress((i + p) / len(ks), desc=f"trang {k + 1}: {desc}"))
        nguon = chon_nguon(r, loai, chu_dots)
        anh = ve(r)
        vis = vis or anh
        anh.save(out / f"{ten}_trang{k + 1}_khung.jpg", quality=85)
        h, st = bang(r, k, len(pages), chu_dots, nguon)
        htmls.append(h)
        o = ban_doc(r, nguon)
        for x in txt:
            txt[x].append(f"===== Trang {k + 1} =====\n" + _ghep(o[x]))
        jobs = r["jobs"]
        data.append({"trang": k + 1, **st, "ghi_chu": r["ghi_chu"], "dots_phong": r["phong"], "loai_trang": loai,
                     "khoi": [{"so": bi + 1, "loai": b.get("category"), "bbox": b.get("bbox"),
                               "doc_bang": nguon.get(bi, (None,))[0], "dots_trung_ft3": nguon.get(bi, (0, None))[1],
                               "chu": o["chinh"].get(bi), "dots": b.get("text") if chu_dots else None,
                               "dong": [{"bbox": list(jobs[n][1]), "ft3": r["doc"]["ft3"][n], "ft4": r["doc"]["ft4"][n]}
                                        for n, j in enumerate(jobs) if j[0] == bi]}
                              for bi, b in enumerate(r["blocks"])]})
        try:
            f = out / f"{ten}_trang{k + 1}.docx"
            xuat_docx(f, r["blocks"], o["chinh"], o["phu"], "ft3 (chữ tay) / dots (khối đánh máy)", "bản kiểm chéo",
                      image=r["img"])
            files.append(f)
        except Exception as e:  # noqa: BLE001 — DOCX lỗi không được làm mất kết quả
            htmls.append(f"<p class=meta>DOCX trang {k + 1} lỗi: {html.escape(str(e))}</p>")
    ghi = {"chinh": f"{ten}.txt", "ft3": f"{ten}_ft3.txt", "ft4": f"{ten}_ft4.txt"}
    for x, fn in ghi.items():
        (out / fn).write_text("\n\n".join(txt[x]), encoding="utf-8")
    (out / f"{ten}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / f"{ten}.html").write_text(f"<!doctype html><meta charset=utf-8><title>{html.escape(ten)}</title>"
                                     f"<style>body{{font-family:sans-serif;margin:16px}}{CSS_FT}</style>{''.join(htmls)}",
                                     encoding="utf-8")
    import zipfile

    tat = sorted(p for p in out.iterdir() if p.is_file())
    with zipfile.ZipFile(out / f"{ten}_tat_ca.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in tat:
            z.write(p, p.name)
    thu_tu = [out / f"{ten}_tat_ca.zip", *files, *(out / fn for fn in ghi.values()), out / f"{ten}.html",
              out / f"{ten}.json", *sorted(out.glob("*_khung.jpg"))]
    return vis, "".join(htmls), "\n\n".join(txt["chinh"]), [str(p) for p in thu_tu]


def run_line(image):
    if image is None:
        return "<p>Chưa có ảnh.</p>", None
    t = time.time()
    r = doc_dong([image.convert("RGB")])
    a, b = r["ft3"][0], r["ft4"][0]
    dau = "✓ hai bản đọc trùng" if ty_le_trung(a, b) >= 0.999 else "tô vàng = ft4 đọc khác"
    f = Path(tempfile.mkdtemp(prefix="ft34_")) / "dong.json"
    f.write_text(json.dumps({"ft3": a, "ft4": b, "tu_khac": [w for w, d, _ in so_khop_tu(a, b) if d]},
                            ensure_ascii=False, indent=1), encoding="utf-8")
    return (f"<div class=htr><p class=meta>{time.time() - t:.1f}s · {dau}</p><table>"
            f"<tr><th>ft3</th><td class=ar>{to_vang(a, b)}</td></tr>"
            f"<tr><th>ft4</th><td class=ar>{html.escape(b)}</td></tr></table></div>"), [str(f)]


def build() -> gr.Blocks:
    kw = {} if GR6 else {"css": CSS_FT}
    with gr.Blocks(title="Đọc chữ tay — ft3 + ft4", **kw) as demo:
        gr.Markdown("## Đọc chữ tay Ả Rập — ft3 (đọc chính) + ft4 (kiểm chéo)\n"
                    "dots.mocr chia khối → Kraken tách dòng → **ft3** và **ft4** đọc từng dòng. Chỗ hai bản đọc khác "
                    "nhau được **tô vàng** — đó là chỗ cần người soát. Kết quả là **bản nháp**, không phải bản cuối.")
        with gr.Tab("Trang tài liệu"):
            with gr.Row():
                with gr.Column(scale=1):
                    f = gr.File(label="Ảnh hoặc PDF", file_types=["image", ".pdf"], type="filepath")
                    page = gr.Number(value=1, precision=0, label="Trang (PDF)")
                    tat_ca = gr.Checkbox(False, label="Đọc mọi trang của PDF")
                    loai = gr.Radio([LOAI_TAY, LOAI_MAY, LOAI_TRON], value=LOAI_TAY, label="Loại chữ trên trang")
                    dmode = gr.Radio([DOTS_FULL, DOTS_LAYOUT], value=DOTS_FULL,
                                     label="dots (chỉ chia khối → chữ đánh máy cũng đọc bằng ft3)")
                    go = gr.Button("Đọc", variant="primary")
                with gr.Column(scale=2):
                    vis = gr.Image(label="Khối dots (xanh dương; tím = Hebrew) · dòng: xanh lá = ft3/ft4 trùng, cam = khác", type="pil")
            gr.Markdown("### Tải kết quả\n`_tat_ca.zip` = tất cả · `.docx` = văn bản tô vàng + chú thích · `.txt` = chữ chính "
                        "(`_ft3.txt`, `_ft4.txt` = từng model) · `.html` = bảng soát từng dòng (mở bằng trình duyệt) · "
                        "`.json` = toạ độ khối / dòng + mọi bản đọc · `_khung.jpg` = ảnh trang có khung")
            dl = gr.Files(label="Tải về")
            with gr.Accordion("Văn bản chính ghép cả trang", open=False):
                txt = gr.Textbox(lines=18, rtl=True)
            out = gr.HTML()
            go.click(run_page, [f, page, tat_ca, dmode, loai], [vis, out, txt, dl])
        with gr.Tab("Một dòng"):
            li = gr.Image(label="Ảnh MỘT dòng chữ", type="pil")
            lb = gr.Button("Đọc", variant="primary")
            lo = gr.HTML()
            ldl = gr.Files(label="Tải về (JSON)")
            lb.click(run_line, [li], [lo, ldl])
    return demo


def main():
    import torch

    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=7862)
    ap.add_argument("--gpu-dots", type=int, default=0)
    ap.add_argument("--gpu-doc", type=int, default=None, help="GPU cho ft3/ft4 (mặc định: GPU thứ hai nếu có)")
    ap.add_argument("--share", action="store_true")
    a = ap.parse_args()
    n = torch.cuda.device_count()
    S["gpu_dots"] = a.gpu_dots
    S["gpu_doc"] = a.gpu_doc if a.gpu_doc is not None else (1 if n > 1 else 0)
    print(f"== dots: cuda:{S['gpu_dots']} · ft3/ft4: cuda:{S['gpu_doc']}", flush=True)
    build().queue(default_concurrency_limit=1).launch(server_name="127.0.0.1", server_port=a.port, share=a.share,
                                                     **({"css": CSS_FT} if GR6 else {}))


if __name__ == "__main__":
    main()
