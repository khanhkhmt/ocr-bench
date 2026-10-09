"""Chẩn đoán: cùng một model, cùng N dòng — đổi độ chính xác số (fp16 / fp32) và cỡ lô → điểm có đổi không?

    <python venv dots> -m htr_test.chan_doan [--model baseer] [--n 32] [--configs fp16:16,fp16:1,fp32:1] [--split blind_test]

Lý do: Baseer-Nakba trên T4 (fp16, lô 8) cho 16 dòng đầu Omar blind_test chỉ ~67% đúng ký tự (công bố ~91%), có dòng
thêm chữ "لا" (đổi nghĩa), bỏ sót đầu dòng, lặp cả dòng. Tác giả chạy bf16 trên H100; T4 không có bf16. Nghi:
(1) tràn số fp16, (2) ghép lô (padding) làm hỏng. fp32 lô 1 = chuẩn số học để so.
Lấy N dòng ĐẦU của tập (đúng thứ tự benchmark chạy) → so được với kết quả benchmark đã có.
In bảng + ghi /kaggle/working/htr_chan_doan.md (dữ liệu công khai). Không đẩy GitHub, không ghi vào thư mục benchmark.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from htr_test.eval_lines import line_scores, load_lines, score  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="baseer", choices=["baseer", "ketaba"])
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--configs", default="fp16:16,fp16:1,fp32:1",
                    help="dtype:lô[:q4|fp16] cách nhau dấu phẩy (q4/fp16 = nền của ketaba; mặc định q4)")
    ap.add_argument("--split", default="blind_test")
    ap.add_argument("--data", default=None)
    ap.add_argument("--gpu", type=int, default=0)
    ap.add_argument("--out", default="/kaggle/working/htr_chan_doan.md")
    a = ap.parse_args()
    import torch

    from htr_test.models import BaseerNakba, KetabaOCR, free_cuda

    lines = load_lines(a.data, a.split)[: a.n]
    refs = [x[2] for x in lines]
    ims = [x[1] for x in lines]
    dev = f"cuda:{a.gpu}" if a.gpu >= 0 else "cpu"
    rows, examples = [], []
    for cfg in [c.strip() for c in a.configs.split(",") if c.strip()]:
        parts = cfg.split(":")
        dtype, batch = parts[0], int(parts[1])
        kmode = parts[2] if len(parts) > 2 else "q4"
        print(f"== {a.model} {dtype} lô {batch}", flush=True)
        t0 = time.time()
        m = (BaseerNakba(device=dev, dtype=dtype) if a.model == "baseer"
             else KetabaOCR(device=dev, dtype=dtype, quant4=(kmode == "q4"))).load()
        t_load = time.time() - t0
        t0 = time.time()
        hyps = m.read(ims, batch=batch)
        sec = (time.time() - t0) / len(ims)
        vram = torch.cuda.max_memory_allocated(dev) / 2**30 if dev != "cpu" else 0
        s = score(list(zip(refs, hyps)))
        per = [line_scores(r, h) for r, h in zip(refs, hyps)]
        rows.append(f"| {cfg} | {batch} | **{max(0.0, 100 - 100 * s['chuan_hoa']['cer']):.1f}%** | "
                    f"{100 * sum(p['dung'] for p in per) / len(per):.1f}% | {100 * s['goc']['cer']:.1f}% | "
                    f"{s['do_dai']['dai_x1_5']} | {s['do_dai']['ngan_x0_5']} | {sec:.2f} | {t_load:.0f} | {vram:.1f} |")
        examples.append((cfg, hyps[:4]))
        print(rows[-1], flush=True)
        del m
        free_cuda()
        if dev != "cpu":
            torch.cuda.reset_peak_memory_stats(dev)
    md = [f"# Chẩn đoán {a.model} — {len(lines)} dòng đầu {a.split}", "",
          "| cấu hình | lô | đúng ký tự (corpus) | đúng ký tự TB/dòng | CER gốc | dòng dài ≥1,5× (lặp/bịa) | dòng ngắn ≤0,5× (sót) | s/dòng | nạp (s) | VRAM đỉnh (GB) |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|", *rows, "", "## 4 dòng đầu", ""]
    for i in range(min(4, len(lines))):
        md.append(f"- **nhãn**: {refs[i]}")
        for cfg, hyps in examples:
            md.append(f"  - {cfg}: {hyps[i]}")
    Path(a.out).write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
