"""Web thử các model đọc chữ viết tay theo dòng — bố cục do dots.mocr.

    <python venv dots> -m htr_test.app [--port 7861] [--gpu 0] [--no-quant4]

Tab "Trang tài liệu": ảnh / PDF → dots chia khối → tách dòng trong từng khối chữ → từng model đọc từng dòng →
so sánh cạnh nhau (chữ của dots | Ketaba-OCR | sherif gốc | ArTrOCR), xem ảnh từng dòng, tải kết quả JSON / TXT.
Tab "Một dòng": thả một ảnh dòng chữ → kết quả từng model (thử nhanh, không cần dots).
"""

from __future__ import annotations

import argparse
import base64
import html
import io
import json
import tempfile
import time
from pathlib import Path

import gradio as gr
from PIL import Image, ImageDraw

from .lines import split_lines
from .models import ArTrOCR, BaseerNakba, KetabaOCR, free_cuda

ROOT = Path(__file__).resolve().parents[1]
TEXT_CATS = {"Text", "Title", "Section-header", "List-item", "Caption", "Footnote", "Page-header", "Page-footer"}
M_BASEER = "Baseer-Nakba (hạng 1 NAKBA, phi thương mại)"
M_KETABA, M_SHERIF, M_TROCR = "Ketaba-OCR (LoRA)", "sherif gốc (tắt LoRA)", "ArTrOCR"
ALL_MODELS = [M_BASEER, M_KETABA, M_SHERIF, M_TROCR]
DOTS_FULL, DOTS_LAYOUT = "dots đọc cả chữ (để so sánh)", "dots chỉ chia khối (nhanh hơn)"

GR6 = int(gr.__version__.split(".")[0]) >= 6

S = {"dots": None, "baseer": None, "ketaba": None, "trocr": None, "baseer_quant4": False, "gpu": 0, "quant4": True}


def dots():
    if S["dots"] is None:
        from ocrbench.convert import Converter

        S["dots"] = Converter(ROOT / "inference" / "config.yaml", "dots_mocr", gpus=str(S["gpu"]))
    return S["dots"]


def ketaba():
    if S["ketaba"] is None:
        S["ketaba"] = KetabaOCR(quant4=S["quant4"], device=f"cuda:{S['gpu']}").load()
    return S["ketaba"]


def baseer():
    if S["baseer"] is None:
        S["baseer"] = BaseerNakba(device=f"cuda:{S['gpu']}", quant4=S["baseer_quant4"]).load()
    return S["baseer"]


def trocr():
    if S["trocr"] is None:
        S["trocr"] = ArTrOCR(device=f"cuda:{S['gpu']}").load()
    return S["trocr"]


def unload():
    S["baseer"] = S["ketaba"] = S["trocr"] = None
    free_cuda()
    return "Đã giải phóng Baseer / Ketaba / ArTrOCR (dots vẫn giữ)."


def load_pages(path: str) -> list[Image.Image]:
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        import pypdfium2 as pdfium

        pdf = pdfium.PdfDocument(str(p))
        return [pdf[i].render(scale=200 / 72).to_pil().convert("RGB") for i in range(len(pdf))]
    return [Image.open(p).convert("RGB")]


def read_lines(models: list[str], crops: list[Image.Image]) -> dict[str, list[str]]:
    out = {}
    if not crops:
        return {m: [] for m in models}
    if M_BASEER in models:
        out[M_BASEER] = baseer().read(crops)
    if M_KETABA in models:
        out[M_KETABA] = ketaba().read(crops, use_lora=True)
    if M_SHERIF in models:
        out[M_SHERIF] = ketaba().read(crops, use_lora=False)
    if M_TROCR in models:
        out[M_TROCR] = trocr().read(crops)
    return out


def _b64(im: Image.Image, h: int = 48) -> str:
    im = im.copy()
    im.thumbnail((900, h))
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()


CSS = """
.htr table{border-collapse:collapse;width:100%} .htr td,.htr th{border:1px solid #ccc;padding:4px;vertical-align:top}
.htr .ar{direction:rtl;text-align:right;font-family:'Noto Naskh Arabic','Amiri',serif;font-size:17px;line-height:1.7;white-space:pre-wrap}
.htr th{background:#f3f3f3} .htr summary{cursor:pointer;color:#555} .htr img{max-width:100%;border:1px solid #eee}
.htr .meta{color:#666;font-size:12px}
"""


def run_page(file, page_no, models, dots_mode, seg_method, progress=gr.Progress()):
    if not file:
        return None, "<p>Chưa có file.</p>", "", None
    if not models:
        return None, "<p>Chọn ít nhất một model.</p>", "", None
    t0 = time.time()
    pages = load_pages(file if isinstance(file, str) else file.name)
    k = min(max(1, int(page_no or 1)), len(pages)) - 1
    page = pages[k]
    progress(0.05, desc="dots đang chia khối…")
    conv = dots()
    conv.set_mode("Bố cục đầy đủ" if dots_mode == DOTS_FULL else "Chỉ bố cục (không chữ)")
    img, item = conv._prepare(page, Path(file if isinstance(file, str) else file.name), k + 1, "text")
    pred = conv.adapter.predict(img, item)
    blocks = (pred.extra or {}).get("blocks") or []
    t_dots = time.time() - t0
    draw_img = img.copy()
    dr = ImageDraw.Draw(draw_img)
    # gom mọi dòng của mọi khối chữ → mỗi model đọc một lượt (theo lô)
    jobs = []  # (chỉ số khối, hộp dòng trong trang, ảnh dòng)
    seg_used = set()
    for bi, b in enumerate(blocks):
        bb = b.get("bbox")
        if not bb or len(bb) != 4:
            continue
        x0, y0, x1, y1 = [int(round(v)) for v in bb]
        dr.rectangle((x0, y0, x1, y1), outline=(30, 90, 220), width=3)
        dr.text((x0 + 4, y0 + 2), str(bi + 1), fill=(30, 90, 220))
        if b.get("category") not in TEXT_CATS or x1 - x0 < 8 or y1 - y0 < 8:
            continue
        crop = img.crop((x0, y0, x1, y1))
        lines, used = split_lines(crop, seg_method)
        seg_used.add(used)
        for lx0, ly0, lx1, ly1 in lines:
            box = (x0 + lx0, y0 + ly0, x0 + lx1, y0 + ly1)
            dr.rectangle(box, outline=(220, 40, 40), width=1)
            jobs.append((bi, box, img.crop(box)))
    progress(0.4, desc=f"{len(jobs)} dòng — các model đang đọc…")
    t1 = time.time()
    res = read_lines(models, [j[2] for j in jobs])
    t_read = time.time() - t1
    # dựng bảng so sánh theo khối
    rows, full = [], {m: [] for m in models}
    full["dots"] = []
    for bi, b in enumerate(blocks):
        cat = b.get("category")
        idx = [n for n, j in enumerate(jobs) if j[0] == bi]
        if cat == "Table":
            rows.append(f"<tr><td>{bi + 1}<br><span class=meta>{cat}</span></td><td colspan={len(models) + 1}>"
                        f"<div class=ar>{b.get('text') or ''}</div><span class=meta>(bảng: giữ kết quả dots)</span></td></tr>")
            continue
        if cat not in TEXT_CATS:
            rows.append(f"<tr><td>{bi + 1}<br><span class=meta>{html.escape(str(cat))}</span></td>"
                        f"<td colspan={len(models) + 1} class=meta>(không phải chữ — giữ nguyên ảnh)</td></tr>")
            continue
        dtext = b.get("text") or ""
        full["dots"].append(dtext)
        cells = [f"<td><div class=ar>{html.escape(dtext)}</div></td>"]
        for m in models:
            txt = "\n".join(res[m][n] for n in idx)
            full[m].append(txt)
            cells.append(f"<td><div class=ar>{html.escape(txt)}</div></td>")
        detail = "".join(
            f"<tr><td><img src='data:image/jpeg;base64,{_b64(jobs[n][2])}'></td>"
            + "".join(f"<td class=ar>{html.escape(res[m][n])}</td>" for m in models) + "</tr>" for n in idx)
        rows.append(f"<tr><td>{bi + 1}<br><span class=meta>{html.escape(str(cat))} · {len(idx)} dòng</span></td>"
                    + "".join(cells) + "</tr>")
        if idx:
            rows.append(f"<tr><td></td><td colspan={len(models) + 1}><details><summary>xem từng dòng</summary>"
                        f"<table><tr><th>ảnh dòng</th>{''.join(f'<th>{m}</th>' for m in models)}</tr>{detail}</table>"
                        "</details></td></tr>")
    head = "<tr><th>khối</th><th>dots</th>" + "".join(f"<th>{m}</th>" for m in models) + "</tr>"
    meta = (f"<p class=meta>Trang {k + 1}/{len(pages)} · {len(blocks)} khối · {len(jobs)} dòng · tách dòng: "
            f"{', '.join(sorted(seg_used)) or '—'} · dots {t_dots:.0f}s · đọc dòng {t_read:.0f}s</p>")
    out_html = f"<div class=htr>{meta}<table>{head}{''.join(rows)}</table></div>"
    txt = "\n\n".join(f"===== {m} =====\n" + "\n\n".join(full[m]) for m in ["dots", *models])
    data = {"trang": k + 1, "khoi": [{"so": bi + 1, "loai": b.get("category"), "bbox": b.get("bbox"), "dots": b.get("text"),
                                      "dong": [{"bbox": jobs[n][1], **{m: res[m][n] for m in models}}
                                               for n, j in enumerate(jobs) if j[0] == bi]}
                                     for bi, b in enumerate(blocks)]}
    f = Path(tempfile.mkdtemp(prefix="htr_")) / "ket_qua.json"
    f.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (f.parent / "ket_qua.txt").write_text(txt, encoding="utf-8")
    return draw_img, out_html, txt, [str(f), str(f.parent / "ket_qua.txt")]


def run_line(image, models):
    if image is None or not models:
        return "<p>Chưa có ảnh / chưa chọn model.</p>", None
    im = Image.fromarray(image) if not isinstance(image, Image.Image) else image
    t = time.time()
    res = read_lines(models, [im])
    rows = "".join(f"<tr><th>{m}</th><td class=ar>{html.escape(res[m][0])}</td></tr>" for m in models)
    prep = Image.fromarray(ArTrOCR.prep(im)) if M_TROCR in models else None
    return f"<div class=htr><p class=meta>{time.time() - t:.1f}s</p><table>{rows}</table></div>", prep


def build() -> gr.Blocks:
    kw = {} if GR6 else {"css": CSS}  # gradio 6: css chuyển sang launch()
    with gr.Blocks(title="Thử model chữ viết tay", **kw) as demo:
        gr.Markdown("## Thử model đọc chữ viết tay theo dòng (Baseer-Nakba, Ketaba-OCR, ArTrOCR) — bố cục do dots.mocr\n"
                    "Các model này chỉ đọc **ảnh một dòng** → web tách dòng trong từng khối chữ của dots rồi cho model đọc "
                    "từng dòng. *sherif gốc* = cùng model nền với Ketaba nhưng TẮT LoRA (để thấy LoRA giúp bao nhiêu).")
        with gr.Tab("Trang tài liệu"):
            with gr.Row():
                with gr.Column(scale=1):
                    f = gr.File(label="Ảnh hoặc PDF", file_types=["image", ".pdf"], type="filepath")
                    page = gr.Number(value=1, precision=0, label="Trang (PDF)")
                    models = gr.CheckboxGroup(ALL_MODELS, value=[M_BASEER, M_KETABA], label="Model đọc chữ")
                    dmode = gr.Radio([DOTS_FULL, DOTS_LAYOUT], value=DOTS_FULL, label="dots")
                    seg = gr.Radio([("Chiếu ngang (nhanh)", "chieu_ngang"), ("Kraken (nếu đã cài)", "kraken")],
                                   value="chieu_ngang", label="Tách dòng")
                    go = gr.Button("Chạy", variant="primary")
                    free = gr.Button("Giải phóng model đọc dòng (VRAM)")
                    msg = gr.Markdown()
                with gr.Column(scale=2):
                    vis = gr.Image(label="Khối dots (xanh) · dòng (đỏ)", type="pil")
            out = gr.HTML()
            with gr.Accordion("Văn bản ghép theo từng model", open=False):
                txt = gr.Textbox(lines=18, rtl=True)
            dl = gr.Files(label="Tải kết quả (JSON / TXT)")
            go.click(run_page, [f, page, models, dmode, seg], [vis, out, txt, dl])
            free.click(unload, None, msg)
        with gr.Tab("Một dòng"):
            with gr.Row():
                li = gr.Image(label="Ảnh MỘT dòng chữ", type="pil")
                lm = gr.CheckboxGroup(ALL_MODELS, value=ALL_MODELS, label="Model")
            lb = gr.Button("Đọc", variant="primary")
            lo = gr.HTML()
            lp = gr.Image(label="Ảnh sau tiền xử lý của ArTrOCR (512×102)", type="pil")
            lb.click(run_line, [li, lm], [lo, lp])
    return demo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=7861)
    ap.add_argument("--gpu", type=int, default=0)
    ap.add_argument("--no-quant4", action="store_true", help="nạp Ketaba fp16 thay vì 4-bit như tác giả")
    ap.add_argument("--baseer-4bit", action="store_true", help="nạp Baseer-Nakba 4-bit khi thiếu VRAM")
    ap.add_argument("--share", action="store_true")
    a = ap.parse_args()
    S["gpu"], S["quant4"], S["baseer_quant4"] = a.gpu, not a.no_quant4, a.baseer_4bit
    build().queue(default_concurrency_limit=1).launch(server_name="127.0.0.1", server_port=a.port, share=a.share,
                                                     **({"css": CSS} if GR6 else {}))


if __name__ == "__main__":
    main()
