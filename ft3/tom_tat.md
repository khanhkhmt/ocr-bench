# Huấn luyện ft3 — 2026-10-12 22:41 UTC

Trạng thái: đánh giá bước 1600: đúng ký tự 91.3%

Bước 1600/2000 · loss 0.2802 · 11.81 s/bước · lr 1.05e-05

| bước | đúng ký tự (val) | đúng từ | dòng sót | dòng dài | số dòng |
|---:|---:|---:|---:|---:|---:|
| 400 | 88.5% | 72.1% | 2 | 0 | 148 |
| 800 | 90.4% | 74.2% | 0 | 0 | 148 |
| 1200 | 91.0% | 77.1% | 1 | 0 | 148 |
| 1600 | 91.3% | 76.9% | 1 | 0 | 148 |

Tham số: `{"base": "Misraj/Baseer__Nakba", "gpu": 0, "dtype": "auto", "lora_r": 32, "lora_alpha": 64, "dropout": 0.05, "vision": 1, "lr": 0.0001, "lr_vision": 2e-05, "batch": 2, "accum": 8, "warmup": 100, "max_steps": 2000, "max_mau": 0, "trong_so": "muharaf=2,omar=2,arams=1,khatt=1", "lam_cu": 0.5, "save_every": 200, "eval_every": 400, "eval_n": 150, "seed": 0, "hf_ckpt": "khanh99/htr-ckpt", "push": true}`
