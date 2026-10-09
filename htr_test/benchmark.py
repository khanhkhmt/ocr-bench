"""Benchmark đọc DÒNG chữ viết tay: nhiều model × 2 bộ dữ liệu công khai → MỘT bảng BENCHMARK_HTR.md.

    <python venv dots> -m htr_test.benchmark [--root /kaggle/working] [--models baseer,ketaba,dots] [--n 0] [--push]

Bộ dữ liệu:
  omar     Omar Al-Saleh blind_test (2.671 dòng) — chữ tay Palestine 1951–65, scan đen trắng sạch. Tải từ HF (gated:
           HF_TOKEN). Cùng tập ẩn của cuộc thi NAKBA 2026 → so được với bảng xếp hạng công bố.
  muharaf  Muharaf test (1.334 dòng) — chữ tay Liban, ảnh MÀU giấy cũ ố vàng. Tự tải nếu chưa có (không cần token).
Thứ tự: theo model (model đầu chấm xong CẢ 2 bộ rồi mới tới model sau) → kết quả chính có sớm; dots chậm nhất để cuối.
Mỗi bước gọi htr_test.eval_lines (chạy lại = đi tiếp; --push: tự khôi phục từ GitHub khi server mất ổ).
Sau mỗi bước ghi <root>/htr_benchmark/BENCHMARK_HTR.md (+ .json) và (--push) đẩy lên nhánh GitHub results-htr.
--n 0 = cả tập (mặc định); --n 500 = 500 dòng ngẫu nhiên cố định mỗi bộ (thử nhanh).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATASETS = {
    "omar": {"ten": "Omar Al-Saleh blind_test", "mo_ta": "chữ tay Palestine 1951–65 · scan đen trắng sạch",
             "split": "blind_test", "out": "htr_eval", "data": None},
    "muharaf": {"ten": "Muharaf test", "mo_ta": "chữ tay Liban TK 19–21 · ảnh màu giấy cũ ố vàng",
                "split": "test", "out": "htr_eval_muharaf", "data": "du_lieu_muharaf"},
}
MODEL_INFO = {
    "baseer": "Baseer-Nakba (Misraj) — hạng 1 NAKBA 2026 · CC BY-NC-SA (phi thương mại) · ĐÃ HỌC Muharaf + Omar train/test",
    "ketaba": "Ketaba-OCR (LoRA 4-bit trên sherif) — hạng 3 NAKBA · Apache 2.0 · ĐÃ HỌC Omar train/test",
    "sherif": "sherif gốc (Ketaba tắt LoRA) · Apache 2.0",
    "trocr": "ArTrOCR-HTR (TrOCR, KHATT) · Apache 2.0",
    "dots": "dots.mocr chế độ 'Chỉ chữ' — model đang dùng cho bố cục + khối đánh máy (mốc so sánh)",
}
CONG_BO = {"baseer": "7,9% / 24,4%", "ketaba": "9,4% / 30,0%"}  # CER/WER corpus, 2.671 dòng blind_test (bảng NAKBA)


def bench_dir(tag: str = "") -> str:
    return f"htr_benchmark_{tag}" if tag else "htr_benchmark"


def write_benchmark(root: Path, models: list[str], n: int, note: str, tag: str = "") -> Path:
    out = root / bench_dir(tag)
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    for key, ds in DATASETS.items():
        f = root / ds["out"] / "tom_tat.json"
        res[key] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    tong = {k: None for k in DATASETS}
    for k, ds in DATASETS.items():
        csv_f = root / ds["out"] / "chi_tiet.csv"
        if csv_f.exists():
            tong[k] = sum(1 for _ in open(csv_f, encoding="utf-8-sig")) - 1

    def cell(key, m, field):
        s = res[key].get(m)
        if not s:
            return "—"
        c = s["chuan_hoa"]
        v = {"dung": max(0.0, 100 - 100 * c["cer"]), "dung_tu": max(0.0, 100 - 100 * c["wer"]),
             "cer": 100 * c["cer"], "wer": 100 * c["wer"], "cer_goc": 100 * s["goc"]["cer"]}[field]
        return f"{v:.1f}%"

    def done(key, m):
        s = res[key].get(m)
        return f"{s['so_dong']}" if s else "0"

    L = ["# Benchmark đọc dòng chữ viết tay — " + time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "",
         f"Trạng thái: {note}", "",
         "## Kết quả chính — % ĐÚNG KÝ TỰ (= 100% − CER, đã gộp hamza / bỏ dấu nguyên âm)", "",
         "| Model | " + " | ".join(f"{ds['ten']}<br><sub>{ds['mo_ta']}</sub>" for ds in DATASETS.values())
         + " | Omar → giấy cũ |",
         "|---|" + "---:|" * len(DATASETS) + "---:|"]
    for m in models:
        vals = [cell(k, m, "dung") for k in DATASETS]
        drop = "—"
        if res["omar"].get(m) and res["muharaf"].get(m):
            a = 100 * res["omar"][m]["chuan_hoa"]["cer"]
            b = 100 * res["muharaf"][m]["chuan_hoa"]["cer"]
            drop = f"giảm {b - a:.1f} điểm" if b >= a else f"tăng {a - b:.1f} điểm"
        L.append(f"| **{m}** | " + " | ".join(f"**{v}**" for v in vals) + f" | {drop} |")
    L += ["", "## Chi tiết", "",
          "| Model | Bộ | đã chấm | đúng ký tự | đúng từ | CER chuẩn hoá | WER chuẩn hoá | CER gốc | công bố (CER/WER) |",
          "|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for m in models:
        for k, ds in DATASETS.items():
            total = tong[k] or "?"
            pub = CONG_BO.get(m, "") if k == "omar" else ""
            L.append(f"| {m} | {ds['ten']} | {done(k, m)}/{total} | {cell(k, m, 'dung')} | {cell(k, m, 'dung_tu')} | "
                     f"{cell(k, m, 'cer')} | {cell(k, m, 'wer')} | {cell(k, m, 'cer_goc')} | {pub} |")
    L += ["", "## Model", ""] + [f"- **{m}**: {MODEL_INFO.get(m, m)}" for m in models]
    L += ["", "## Đọc bảng thế nào",
          "- **đúng ký tự / đúng từ** = 100% − CER / WER sau chuẩn hoá (gộp أ إ آ → ا, ى → ي, bỏ dấu nguyên âm, số Ả Rập → 0-9):"
          " tách lỗi NHÌN khỏi khác biệt chính tả của nhãn. **CER gốc**: không chuẩn hoá (khắt khe).",
          "- **Omar → giấy cũ** = % đúng ký tự trên Omar − trên Muharaf: model tệ đi bao nhiêu điểm khi gặp ảnh màu giấy cũ "
          "(hai bộ khác cả người viết lẫn giấy, nên đây là chênh lệch tổng, không chỉ do giấy).",
          "- Model ĐÃ HỌC bộ nào thì điểm trên bộ đó có thể cao hơn thực tế (xem mục Model). Omar blind_test là tập ẩn "
          "của cuộc thi — không model nào học.",
          f"- Cỡ mẫu: {'cả tập' if not n else f'{n} dòng ngẫu nhiên cố định mỗi bộ'}. "
          "Từng dòng (ảnh, nhãn, chữ từng model, % đúng): " + ", ".join(f"`{ds['out']}/xem_ket_qua.html`" for ds in DATASETS.values())
          + " và `chi_tiet.csv` cùng thư mục (nhánh results-htr)."]
    md = out / "BENCHMARK_HTR.md"
    md.write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "BENCHMARK_HTR.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return md


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/kaggle/working")
    ap.add_argument("--models", default="baseer,ketaba,dots")
    ap.add_argument("--datasets", default="omar,muharaf")
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--gpu", type=int, default=0)
    ap.add_argument("--omar-data", default=None, help="thư mục Omar đã tách (mặc định: tải thẳng từ HF)")
    ap.add_argument("--dtype", default="auto", choices=["auto", "fp16", "bf16", "fp32"])
    ap.add_argument("--model-batch", type=int, default=1, help="1 = đúng (lô > 1 làm Baseer/Ketaba dừng sớm)")
    ap.add_argument("--tag", default="", help="hậu tố thư mục kết quả (vd. fp32) → lần chạy mới, KHÔNG dùng lại kết quả cũ")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    if a.tag:
        for ds in DATASETS.values():
            ds["out"] = f"{ds['out']}_{a.tag}"
    root = Path(a.root)
    models = [m.strip() for m in a.models.split(",") if m.strip()]
    dsets = [d.strip() for d in a.datasets.split(",") if d.strip()]
    sync = None
    if a.push:
        from htr_test.sync import Sync
        sync = Sync(root / bench_dir(a.tag))
        sync.restore()

    def publish(note: str) -> None:
        md = write_benchmark(root, models, a.n, f"{note} · dtype {a.dtype} · lô model {a.model_batch}", a.tag)
        print(f"✔ BENCHMARK: {md} — {note}", flush=True)
        if sync:
            sync.push(note)

    if "muharaf" in dsets and not (root / "du_lieu_muharaf" / "danh_sach.csv").exists():
        print("== tải Muharaf test", flush=True)
        r = subprocess.run([sys.executable, "-m", "htr_test.tai_muharaf", str(root / "du_lieu_muharaf"), "--splits", "test"],
                           cwd=ROOT)
        if r.returncode:
            sys.exit("✘ tải Muharaf lỗi — xem log phía trên")
    for m in models:
        for k in dsets:
            ds = DATASETS[k]
            data = (str(root / ds["data"]) if ds["data"] else a.omar_data)
            cmd = [sys.executable, "-m", "htr_test.eval_lines", "--out", str(root / ds["out"]), "--models", m,
                   "--split", ds["split"], "--n", str(a.n), "--gpu", str(a.gpu), "--dtype", a.dtype,
                   "--model-batch", str(a.model_batch)]
            if data:
                cmd += ["--data", data]
            if a.push:
                cmd += ["--push"]
            print(f"\n######## {m} × {ds['ten']} ########", flush=True)
            r = subprocess.run(cmd, cwd=ROOT)
            if r.returncode:
                publish(f"LỖI khi chấm {m} × {ds['ten']} (mã {r.returncode}) — dừng")
                return r.returncode
            publish(f"xong {m} × {ds['ten']}")
    publish("XONG TẤT CẢ")
    print((root / bench_dir(a.tag) / "BENCHMARK_HTR.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
