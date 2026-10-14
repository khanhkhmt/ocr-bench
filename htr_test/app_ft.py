"""Web đọc chữ tay bằng ft3 (bộ đọc chính) + ft4 (bộ đọc kiểm chéo) — bố cục do dots.mocr.

    <python venv dots> -m htr_test.app_ft [--port 7862] [--gpu-dots 0] [--gpu-doc 1]
    APP=app_ft PORT=7862 bash htr_test/start.sh

Tab "Trang tài liệu": ảnh / PDF → dots chia khối (ảnh phóng tới 2400 px; dots hỏng → cả trang một khối) → Kraken tách
dòng → ft3 và ft4 đọc TỪNG dòng → bảng từng dòng: ảnh dòng | ft3 (từ ft4 đọc khác tô vàng, rê chuột xem ft4 đọc gì) |
ft4; khối Hebrew (khối công chứng) giữ chữ dots, không đưa cho ft3/ft4; khung dòng trên ảnh trang: xanh lá = hai bản đọc trùng, cam = khác (cần soát). Tải DOCX (chữ ft3, tô vàng +
chú thích chỗ ft4 đọc khác), TXT, JSON.
Tab "Một dòng": thả ảnh một dòng → ft3 / ft4.

ft3, ft4 = Baseer-Nakba + LoRA (htr_train/README.md), adapter ở repo HF riêng tư khanh99/htr-ckpt → cần HF_TOKEN.
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

FT = {"ft3": "hf:khanh99/htr-ckpt/ft3/best", "ft4": "hf:khanh99/htr-ckpt/ft4/best"}
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


def bang(r: dict, k: int, n_trang: int, chu_dots: bool) -> tuple[str, dict]:
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
        if b.get("hebrew"):
            rows.append(f"<tr class=khoi><td colspan=3>Khối {bi + 1} · HEBREW — ft3/ft4 chỉ đọc chữ Ả Rập nên KHÔNG đọc "
                        f"khối này; chữ dots đọc (chưa kiểm):<div class=ar>{html.escape(b.get('text') or '')}</div></td></tr>")
            continue
        dots_txt = (f"<details><summary>chữ dots đọc khối này (bộ đọc đánh máy)</summary><div class=ar>"
                    f"{html.escape(b.get('text') or '')}</div></details>") if chu_dots and b.get("text") else ""
        rows.append(f"<tr class=khoi><td colspan=3>Khối {bi + 1} · {html.escape(str(cat))} · {len(idx)} dòng"
                    f"{' · DỰ PHÒNG (dots không chia được khối)' if b.get('du_phong') else ''}{dots_txt}</td></tr>")
        for n in idx:
            tk = so_khop_tu(ft3[n], ft4[n])
            m = sum(d for _, d, _ in tk)
            tu, ngo = tu + len(tk), ngo + m
            dong_khac += bool(m)
            dau = "<span class=ok>✓ trùng</span>" if not m else f"<span class=ngo>{m}/{len(tk)} từ khác</span>"
            rows.append(f"<tr><td><img src='data:image/jpeg;base64,{_b64(jobs[n][2], 56)}'><br>"
                        f"<span class=meta>dòng {n + 1} · {dau}</span></td>"
                        f"<td class=ar>{to_vang(ft3[n], ft4[n])}</td><td class=ar>{html.escape(ft4[n])}</td></tr>")
    st = {"dong": len(jobs), "dong_khac": dong_khac, "tu": tu, "tu_ngo": ngo}
    ghi = "".join(f"<p class=meta>⚠ {html.escape(g)}</p>" for g in r["ghi_chu"])
    tom = (f"<div class=tom><span><b>{len(jobs)}</b> dòng</span><span><b>{dong_khac}</b> dòng ft3 ≠ ft4</span>"
           f"<span><b>{100 * ngo / max(1, tu):.0f}%</b> từ tô vàng ({ngo}/{tu})</span></div>"
           f"<p class=meta>Trang {k + 1}/{n_trang} · {len(r['blocks'])} khối · tách dòng {', '.join(r['tach']) or '—'} · "
           f"dots ×{r['phong']:g}, {r['giay_dots']} s · ft3 + ft4 {r['giay_doc']} s</p>{ghi}"
           "<p class=meta>Tô vàng = ft4 đọc khác ft3 ở từ đó (rê chuột để xem). Đo trên 500 dòng/tập: tô ~13–19% số từ, "
           "bắt 57–75% số từ sai — từ KHÔNG tô vẫn có thể sai, nhất là chữ số, tên riêng.</p>")
    head = "<tr><th style='width:34%'>ảnh dòng</th><th>ft3 (đọc chính)</th><th>ft4 (kiểm chéo)</th></tr>"
    return f"<div class=htr>{tom}<table>{head}{''.join(rows)}</table></div>", st


def run_page(file, page_no, tat_ca, dots_mode, progress=gr.Progress()):
    if not file:
        return None, "<p>Chưa có file.</p>", "", None
    path = Path(file if isinstance(file, str) else file.name)
    pages = load_pages(str(path))
    ks = list(range(len(pages))) if tat_ca else [min(max(1, int(page_no or 1)), len(pages)) - 1]
    chu_dots = dots_mode == DOTS_FULL
    out = Path(tempfile.mkdtemp(prefix="ft34_"))
    htmls, txt, data, vis = [], [], [], None
    from docx import Document  # noqa: F401 — báo thiếu python-docx sớm

    docx_files = []
    for i, k in enumerate(ks):
        r = doc_trang(pages[k], path, chu_dots,
                      lambda p, desc="": progress((i + p) / len(ks), desc=f"trang {k + 1}: {desc}"))
        vis = vis or ve(r)
        h, st = bang(r, k, len(pages), chu_dots)
        htmls.append(h)
        jobs = r["jobs"]
        per = {ten: {bi: (b.get("text") or "") if b.get("hebrew") else  # khối Hebrew: chữ dots (cả hai bên → không tô)
                          "\n".join(r["doc"][ten][n] for n, j in enumerate(jobs) if j[0] == bi)
                     for bi, b in enumerate(r["blocks"])} for ten in ("ft3", "ft4")}
        txt.append(f"===== Trang {k + 1} — ft3 =====\n" + "\n\n".join(t for t in per["ft3"].values() if t.strip()))
        data.append({"trang": k + 1, **st, "ghi_chu": r["ghi_chu"], "dots_phong": r["phong"],
                     "khoi": [{"so": bi + 1, "loai": b.get("category"), "hebrew": bool(b.get("hebrew")), "bbox": b.get("bbox"),
                               "dots": b.get("text") if chu_dots else None,
                               "dong": [{"bbox": list(jobs[n][1]), "ft3": r["doc"]["ft3"][n], "ft4": r["doc"]["ft4"][n]}
                                        for n, j in enumerate(jobs) if j[0] == bi]}
                              for bi, b in enumerate(r["blocks"])]})
        try:
            f = out / f"{path.stem}_trang{k + 1}_ft3.docx"
            xuat_docx(f, r["blocks"], per["ft3"], per["ft4"], "ft3", "ft4", image=r["img"])
            docx_files.append(str(f))
        except Exception as e:  # noqa: BLE001 — DOCX lỗi không được làm mất kết quả
            htmls.append(f"<p class=meta>DOCX trang {k + 1} lỗi: {html.escape(str(e))}</p>")
    (out / f"{path.stem}_ft3_ft4.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / f"{path.stem}_ft3.txt").write_text("\n\n".join(txt), encoding="utf-8")
    files = docx_files + [str(out / f"{path.stem}_ft3.txt"), str(out / f"{path.stem}_ft3_ft4.json")]
    return vis, "".join(htmls), "\n\n".join(txt), files


def run_line(image):
    if image is None:
        return "<p>Chưa có ảnh.</p>"
    t = time.time()
    r = doc_dong([image.convert("RGB")])
    a, b = r["ft3"][0], r["ft4"][0]
    dau = "✓ hai bản đọc trùng" if ty_le_trung(a, b) >= 0.999 else "tô vàng = ft4 đọc khác"
    return (f"<div class=htr><p class=meta>{time.time() - t:.1f}s · {dau}</p><table>"
            f"<tr><th>ft3</th><td class=ar>{to_vang(a, b)}</td></tr>"
            f"<tr><th>ft4</th><td class=ar>{html.escape(b)}</td></tr></table></div>")


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
                    dmode = gr.Radio([DOTS_FULL, DOTS_LAYOUT], value=DOTS_FULL, label="dots")
                    go = gr.Button("Đọc", variant="primary")
                with gr.Column(scale=2):
                    vis = gr.Image(label="Khối dots (xanh dương; tím = Hebrew) · dòng: xanh lá = ft3/ft4 trùng, cam = khác", type="pil")
            out = gr.HTML()
            with gr.Accordion("Văn bản ft3 ghép cả trang", open=False):
                txt = gr.Textbox(lines=18, rtl=True)
            dl = gr.Files(label="Tải kết quả (DOCX tô vàng / TXT / JSON)")
            go.click(run_page, [f, page, tat_ca, dmode], [vis, out, txt, dl])
        with gr.Tab("Một dòng"):
            li = gr.Image(label="Ảnh MỘT dòng chữ", type="pil")
            lb = gr.Button("Đọc", variant="primary")
            lo = gr.HTML()
            lb.click(run_line, [li], [lo])
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
