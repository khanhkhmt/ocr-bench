# Huấn luyện ft4 — 2026-10-12 23:41 UTC

Trạng thái: bước 1850/2000 · loss 0.2438

Bước 1850/2000 · loss 0.2438 · 11.48 s/bước · lr 1.53e-06

| bước | đúng ký tự (val) | đúng từ | dòng sót | dòng dài | số dòng |
|---:|---:|---:|---:|---:|---:|
| 400 | 90.0% | 73.6% | 0 | 0 | 148 |
| 800 | 90.1% | 73.6% | 1 | 0 | 148 |
| 1200 | 90.4% | 75.5% | 1 | 0 | 148 |
| 1600 | 91.3% | 77.4% | 1 | 0 | 148 |

Tham số: `{"base": "Misraj/Baseer__Nakba", "gpu": 1, "dtype": "auto", "lora_r": 32, "lora_alpha": 64, "dropout": 0.05, "vision": 1, "lr": 0.0001, "lr_vision": 2e-05, "batch": 2, "accum": 8, "warmup": 100, "max_steps": 2000, "max_mau": 0, "trong_so": "muharaf=2,omar=1,arams=1,khatt=1", "lam_cu": 0.5, "save_every": 200, "eval_every": 400, "eval_n": 150, "seed": 0, "hf_ckpt": "khanh99/htr-ckpt", "push": true}`
