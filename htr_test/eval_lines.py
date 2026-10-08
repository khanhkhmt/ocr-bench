"""Chấm các model đọc DÒNG chữ viết tay trên tập blind_test của Omar Al-Saleh (NAKBA NLP 2026) — đo bằng số, không nhìn mắt.

    <python venv dots> -m htr_test.eval_lines --out /kaggle/working/htr_eval [--models baseer,ketaba,dots] [--n 300]
    dữ liệu: --data <thư mục đã tách> (cấu trúc <tập>/<mẫu>/input|output + danh_sach.csv)
             hoặc mặc định tải parquet từ Hugging Face (bộ gated — cần HF_TOKEN của tài khoản đã bấm đồng ý điều khoản)

Vì sao blind_test: Ketaba-OCR và Baseer-Nakba đều đã HỌC train (+ test) của bộ này; blind_test là tập ẩn của cuộc thi.
Model: baseer, ketaba, sherif (Ketaba tắt LoRA), trocr, dots (dots.mocr chế độ "Chỉ chữ" trên ảnh dòng — mốc so sánh).
Chạy lại: bỏ qua dòng đã có trong <out>/<model>.jsonl. Kết quả: <out>/tom_tat.md (cả tập, có % đúng), <out>/chi_tiet.csv
(TỪNG dòng: nhãn, chữ mỗi model đọc, % đúng ký tự / từ) và <out>/xem_ket_qua.html (như csv, kèm ảnh dòng).
--push: cứ --push-every phút (mặc định 10) + khi xong mỗi model → đẩy jsonl + tom_tat lên nhánh GitHub results-htr;
lúc khởi động tự kéo phần đã chấm từ GitHub về (server Colab mất ổ khi sập). Xem htr_test/sync.py.

Hai cách chấm:
- "gốc": NFC + gộp khoảng trắng (khắt khe; giống CER công bố của cuộc thi nhất có thể)
- "chuẩn hoá": thêm bỏ dấu nguyên âm, gộp أ إ آ → ا, ى → ي, số Ả Rập → 0-9 — nhãn của bộ này đã chuẩn hoá chính tả
  (thêm hamza) nên chỉ số này tách lỗi NHÌN khỏi khác biệt chính tả
Kèm: tỉ lệ độ dài (đoán/đáp án) và số dòng dài gấp ≥ 1,5 lần (thường là bịa thêm) hoặc ≤ 0,5 lần (bỏ sót).
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import random
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ocrbench.metrics import edit_stats  # noqa: E402
from ocrbench.normalize import NormConfig, normalize, normalize_raw  # noqa: E402

HF_REPO = "U4RASD/omar-al-saleh-manuscripts-segments"
NORM = NormConfig(strip_markdown=False, strip_diacritics=True, unify_alef=True, unify_yeh=True, unify_digits=True)


def load_lines(data: str | None, split: str) -> list[tuple[str, Image.Image, str]]:
    """→ [(id, ảnh, nhãn)] theo thứ tự cố định."""
    if data:
        rows = [r for r in csv.DictReader(open(Path(data) / "danh_sach.csv", encoding="utf-8")) if r["tap"] == split]
        return [(r["mau"], Image.open(Path(data) / r["anh"]).convert("RGB"),
                 (Path(data) / r["nhan"]).read_text(encoding="utf-8").strip()) for r in rows]
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download

    tok = os.environ.get("HF_TOKEN")
    if not tok:
        sys.exit("Thiếu HF_TOKEN (bộ dữ liệu gated) — hoặc dùng --data <thư mục đã tách>")
    f = hf_hub_download(HF_REPO, f"data/{split}-00000-of-00001.parquet", repo_type="dataset", token=tok)
    out = []
    for i, r in enumerate(pq.read_table(f).to_pylist()):
        out.append((Path(r["filename"] or f"{split}_{i:05d}").stem,
                    Image.open(io.BytesIO(r["image"]["bytes"])).convert("RGB"), (r["text"] or "").strip()))
    return out


def make_reader(name: str, gpu: int):
    """→ hàm(list ảnh) → list chữ."""
    dev = f"cuda:{gpu}" if gpu >= 0 else "cpu"
    if name == "baseer":
        from htr_test.models import BaseerNakba
        m = BaseerNakba(device=dev).load()
        return m.read
    if name in ("ketaba", "sherif"):
        from htr_test.models import KetabaOCR
        m = KetabaOCR(device=dev).load()
        return lambda ims: m.read(ims, use_lora=(name == "ketaba"))
    if name == "trocr":
        from htr_test.models import ArTrOCR
        m = ArTrOCR(device=dev).load()
        return m.read
    if name == "dots":
        from ocrbench.convert import Converter
        conv = Converter(ROOT / "inference" / "config.yaml", "dots_mocr", gpus=str(gpu))
        conv.set_mode("Chỉ chữ")

        def read(ims):
            out = []
            for im in ims:
                img, item = conv._prepare(im, Path("dong.png"), 1, "text")
                out.append((conv.adapter.predict(img, item).text or "").strip())
            return out
        return read
    raise SystemExit(f"model lạ: {name} (có: baseer, ketaba, sherif, trocr, dots)")


def score(pairs: list[tuple[str, str]]) -> dict:
    res = {}
    for tag, f in (("goc", normalize_raw), ("chuan_hoa", lambda s: " ".join(normalize(s, NORM).split()))):
        ce = cr = we = wr = 0
        per_c, per_w = [], []
        for ref, hyp in pairs:
            s = edit_stats(f(ref), f(hyp))
            ce, cr, we, wr = ce + s["char_edits"], cr + s["ref_chars"], we + s["word_edits"], wr + s["ref_words"]
            per_c.append(s["char_edits"] / max(1, s["ref_chars"]))
            per_w.append(s["word_edits"] / max(1, s["ref_words"]))
        res[tag] = {"cer": ce / max(1, cr), "wer": we / max(1, wr), "cer_dong": sum(per_c) / max(1, len(per_c)),
                    "wer_dong": sum(per_w) / max(1, len(per_w))}
    ratios = [len(normalize_raw(h)) / max(1, len(normalize_raw(r))) for r, h in pairs]
    res["do_dai"] = {"tb": sum(ratios) / max(1, len(ratios)), "dai_x1_5": sum(x >= 1.5 for x in ratios),
                     "ngan_x0_5": sum(x <= 0.5 for x in ratios)}
    return res


def _norm(s: str) -> str:
    return " ".join(normalize(s, NORM).split())


def line_scores(ref: str, hyp: str) -> dict:
    """% đúng của MỘT dòng = 100 − CER (chặn ở 0 khi model đọc thừa quá nhiều)."""
    g, c = edit_stats(normalize_raw(ref), normalize_raw(hyp)), edit_stats(_norm(ref), _norm(hyp))
    cer_g = g["char_edits"] / max(1, g["ref_chars"])
    cer_c = c["char_edits"] / max(1, c["ref_chars"])
    wer_c = c["word_edits"] / max(1, c["ref_words"])
    return {"cer_goc": cer_g, "cer": cer_c, "wer": wer_c, "dung": max(0.0, 1 - cer_c), "dung_tu": max(0.0, 1 - wer_c)}


def _thumb(im) -> str:
    import base64
    t = im.copy()
    t.thumbnail((900, 70))
    buf = io.BytesIO()
    t.convert("L").save(buf, format="JPEG", quality=70)
    return base64.b64encode(buf.getvalue()).decode()


def write_details(out: Path, lines: list, names: list[str], html_too: bool) -> None:
    """chi_tiet.csv: MỖI DÒNG một hàng — nhãn, chữ từng model đọc, % đúng ký tự / từ. xem_ket_qua.html: kèm ảnh."""
    import html as H
    preds = {m: read_done(out / f"{m}.jsonl") for m in names}
    names = [m for m in names if preds[m]]
    if not names:
        return
    cols = ["id", "nhan"]
    for m in names:
        cols += [f"{m}_doc", f"{m}_dung_ky_tu_%", f"{m}_dung_tu_%", f"{m}_cer_goc_%"]
    recs = []
    with open(out / "chi_tiet.csv", "w", encoding="utf-8-sig", newline="") as fo:  # -sig: Excel mở đúng tiếng Ả Rập
        w = csv.writer(fo)
        w.writerow(cols)
        for lid, im, ref in lines:
            row, rec = [lid, ref], {"id": lid, "im": im, "ref": ref, "m": {}}
            for m in names:
                hyp = preds[m].get(lid)
                if hyp is None:
                    row += ["", "", "", ""]
                    continue
                sc = line_scores(ref, hyp)
                rec["m"][m] = (hyp, sc)
                row += [hyp, f"{100 * sc['dung']:.1f}", f"{100 * sc['dung_tu']:.1f}", f"{100 * sc['cer_goc']:.1f}"]
            w.writerow(row)
            recs.append(rec)
    if not html_too:
        return
    def color(x):
        return "#0a7d32" if x >= 0.95 else "#b8860b" if x >= 0.8 else "#c0392b"
    head = "".join(f"<th>{H.escape(m)}</th>" for m in names)
    body = []
    for r in recs:
        cells = "".join(
            (f"<td><div class=ar>{H.escape(r['m'][m][0])}</div><b style='color:{color(r['m'][m][1]['dung'])}'>"
             f"{100 * r['m'][m][1]['dung']:.0f}% ký tự · {100 * r['m'][m][1]['dung_tu']:.0f}% từ</b></td>")
            if m in r["m"] else "<td class=m>(chưa chấm)</td>" for m in names)
        body.append(f"<tr><td class=m>{H.escape(r['id'])}<br><img src='data:image/jpeg;base64,{_thumb(r['im'])}'>"
                    f"<div class=ar style='color:#063'>{H.escape(r['ref'])}</div></td>{cells}</tr>")
    css = ("body{font-family:sans-serif;margin:12px} table{border-collapse:collapse;width:100%} "
           "td,th{border:1px solid #ccc;padding:4px;vertical-align:top} th{background:#f3f3f3;position:sticky;top:0} "
           ".ar{direction:rtl;text-align:right;font-family:'Noto Naskh Arabic','Amiri',serif;font-size:17px;line-height:1.7} "
           ".m{color:#777;font-size:12px} img{max-width:420px}")
    summary = (out / "tom_tat.md").read_text(encoding="utf-8") if (out / "tom_tat.md").exists() else ""
    (out / "xem_ket_qua.html").write_text(
        f"<!doctype html><meta charset=utf-8><title>Kết quả từng dòng</title><style>{css}</style>"
        f"<h1>Kết quả từng dòng — chữ viết tay Omar Al-Saleh</h1><pre>{H.escape(summary)}</pre>"
        "<p>Mỗi hàng: ảnh dòng + nhãn thật (xanh lá) · chữ từng model đọc + % đúng (xanh ≥ 95%, vàng ≥ 80%, đỏ &lt; 80%; "
        "đã chuẩn hoá hamza / dấu nguyên âm).</p>"
        f"<table><tr><th>dòng · nhãn</th>{head}</tr>{''.join(body)}</table>", encoding="utf-8")


def read_done(f: Path) -> dict[str, str]:
    done = {}
    if f.exists():
        for ln in f.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                d = json.loads(ln)
                done[d["id"]] = d["doan"]
    return done


def write_summary(out: Path, lines: list, names: list[str], split: str, note: str = "") -> str:
    """Bảng kết quả từ mọi .jsonl hiện có (chấm dở cũng ghi — cột "đã chấm" cho biết bao nhiêu dòng)."""
    summary = {}
    for name in names:
        done = read_done(out / f"{name}.jsonl")
        pairs = [(ref, done[lid]) for lid, _, ref in lines if lid in done]
        if pairs:
            summary[name] = score(pairs)
            summary[name]["so_dong"] = len(pairs)
    rows = ["# Dòng chữ viết tay Omar Al-Saleh — " + split + f" ({len(lines)} dòng)", "",
            f"Cập nhật: {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}" + (f" — {note}" if note else ""), "",
            "| Model | đã chấm | **đúng ký tự** | **đúng từ** | CER gốc | WER gốc | CER chuẩn hoá | WER chuẩn hoá | CER TB theo dòng (chuẩn hoá) | độ dài TB | dòng dài ≥1,5× | dòng ngắn ≤0,5× |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, s in sorted(summary.items(), key=lambda kv: kv[1]["chuan_hoa"]["cer"]):
        g, c, d = s["goc"], s["chuan_hoa"], s["do_dai"]
        rows.append(f"| {name} | {s['so_dong']}/{len(lines)} | **{max(0.0, 100 - 100 * c['cer']):.1f}%** | "
                    f"**{max(0.0, 100 - 100 * c['wer']):.1f}%** | {100 * g['cer']:.1f}% | {100 * g['wer']:.1f}% | "
                    f"{100 * c['cer']:.1f}% | {100 * c['wer']:.1f}% | {100 * c['cer_dong']:.1f}% | {d['tb']:.2f} | "
                    f"{d['dai_x1_5']} | {d['ngan_x0_5']} |")
    rows += ["", "đúng ký tự = 100% − CER chuẩn hoá (cả tập, tính theo tổng ký tự); đúng từ = 100% − WER chuẩn hoá. "
             "Từng dòng: chi_tiet.csv (mở bằng Excel) và xem_ket_qua.html (có ảnh).",
             "", "Tham chiếu công bố (cả 2.671 dòng, CER/WER theo corpus): Baseer-Nakba 7,9% / 24,4% · Ketaba 9,4% / 30,0% "
             "· baseline Qwen3-VL-8B LoRA 36,8% / 69,1%."]
    (out / "tom_tat.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (out / "tom_tat.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--models", default="baseer,ketaba,dots")
    ap.add_argument("--data", default=None)
    ap.add_argument("--split", default="blind_test")
    ap.add_argument("--n", type=int, default=0, help="0 = cả tập; >0 = lấy ngẫu nhiên (cố định, seed 0) n dòng")
    ap.add_argument("--gpu", type=int, default=0, help="-1 = CPU (chỉ để thử)")
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--push", action="store_true", help="đẩy kết quả lên nhánh GitHub results-htr (cần GITHUB_TOKEN)")
    ap.add_argument("--push-every", type=float, default=10, help="phút giữa 2 lần đẩy khi đang chấm")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    names = [m.strip() for m in a.models.split(",") if m.strip()]
    sync = None
    if a.push:
        from htr_test.sync import Sync
        sync = Sync(out, every_min=a.push_every)
        sync.restore()  # Colab mất ổ khi khởi động lại → lấy lại phần đã chấm từ GitHub
    lines = load_lines(a.data, a.split)
    if a.n:
        lines = random.Random(0).sample(lines, min(a.n, len(lines)))
    print(f"{a.split}: {len(lines)} dòng", flush=True)

    def checkpoint(note: str, force: bool = False) -> None:
        if sync and (force or sync.due()):
            write_summary(out, lines, names, a.split, note)
            write_details(out, lines, names, html_too=force)  # html (có ảnh, vài MB) chỉ khi xong một model
            sync.push(note)

    for name in names:
        f = out / f"{name}.jsonl"
        done = read_done(f)
        todo = [x for x in lines if x[0] not in done]
        if not todo:
            print(f"== {name}: đã chấm đủ {len(lines)} dòng", flush=True)
            continue
        t0 = time.time()
        read = make_reader(name, a.gpu)
        print(f"== {name}: nạp {time.time() - t0:.0f}s, còn {len(todo)} dòng", flush=True)
        t0 = time.time()
        with open(f, "a", encoding="utf-8") as fo:
            for i in range(0, len(todo), a.batch):
                chunk = todo[i:i + a.batch]
                for (lid, _, _), hyp in zip(chunk, read([x[1] for x in chunk])):
                    fo.write(json.dumps({"id": lid, "doan": hyp}, ensure_ascii=False) + "\n")
                fo.flush()
                k = i + len(chunk)
                print(f"   {name}: {k}/{len(todo)} · {(time.time() - t0) / k:.2f} s/dòng", flush=True)
                checkpoint(f"đang chấm {name} {len(done) + k}/{len(lines)}")
        del read
        from htr_test.models import free_cuda
        free_cuda()
        checkpoint(f"xong {name}", force=True)
    print(write_summary(out, lines, names, a.split, "xong"))
    write_details(out, lines, names, html_too=True)
    print(f"Từng dòng: {out / 'chi_tiet.csv'}  ·  {out / 'xem_ket_qua.html'}")
    checkpoint("XONG tất cả", force=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
