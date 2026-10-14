# Thử dots.mocr — phóng ảnh / cách đọc (tài liệu thật)

Cập nhật: 2026-10-14 08:11 UTC · 32/36 lượt

Ô: **đúng ký tự** / đúng từ (theo thứ tự) · thu hồi từ. Cột = cách đọc ×phóng (so với ảnh web đã chuẩn bị). day_du ×1 = cột dots của cham_trang. `cứu` = chữ cứu từ JSON bị cắt. Yêu cầu đánh máy ≥ 90%.

## So với nhãn anh (`nhan.json`)

| trang | day_du ×1 | khoi ×1 | chi_chu ×1 | day_du ×2 | khoi ×2 | chi_chu ×2 | day_du ×1.5 | khoi ×1.5 | chi_chu ×1.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| image_1 | **77.6%** / 38.0% · 40% | **74.9%** / 47.3% · 56% | **71.2%** / 33.7% · 39% | LỖI | LỖI | LỖI | **90.3%** / 70.1% · 72% | **89.2%** / 69.6% · 70% | **89.6%** / 70.7% · 73% |
| image_2 | **43.9%** / 8.9% · 13% | **0.0%** / 0.0% · 14% | **47.2%** / 4.6% · 9% | LỖI | LỖI | LỖI | … | … | … |
| image_3 | **0.0%** / 0.0% · 0% (cứu 0.4%) | **7.7%** / 0.7% · 3% | **0.0%** / 0.0% · 12% | LỖI | LỖI | LỖI | **52.8%** / 0.0% · 41% | **30.0%** / 0.0% · 55% | **56.1%** / 0.0% · 40% |
| image_4 | **88.7%** / 70.9% · 78% | **88.3%** / 67.4% · 69% | **88.3%** / 67.4% · 77% | LỖI | LỖI | LỖI | **90.5%** / 74.4% · 79% | **86.9%** / 64.0% · 66% | … |

## So với nhãn Claude (`nhan_claude.json`)

| trang | day_du ×1 | khoi ×1 | chi_chu ×1 | day_du ×2 | khoi ×2 | chi_chu ×2 | day_du ×1.5 | khoi ×1.5 | chi_chu ×1.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| image_1 | **77.6%** / 38.0% · 40% | **75.0%** / 47.3% · 56% | **71.1%** / 33.7% · 39% | LỖI | LỖI | LỖI | **90.4%** / 70.1% · 72% | **89.3%** / 69.6% · 70% | **89.7%** / 70.7% · 73% |
| image_2 | **43.2%** / 7.5% · 13% | **0.0%** / 0.0% · 14% | **48.8%** / 5.7% · 9% | LỖI | LỖI | LỖI | … | … | … |
| image_3 | **0.0%** / 0.0% · 0% (cứu 0.4%) | **7.5%** / 0.7% · 3% | **0.0%** / 0.0% · 12% | LỖI | LỖI | LỖI | **55.5%** / 0.0% · 41% | **33.0%** / 0.0% · 55% | **58.8%** / 0.0% · 40% |
| image_4 | **89.3%** / 72.1% · 79% | **88.9%** / 68.6% · 70% | **88.9%** / 68.6% · 78% | LỖI | LỖI | LỖI | **91.1%** / 75.6% · 80% | **87.5%** / 65.1% · 67% | … |

## Chi tiết từng lượt

| trang | cách | ×phóng | ảnh (px) | khối | token | giây | GPU | cờ |
|---|---|---:|---|---:|---:|---:|---:|---|
| image_1 | chi_chu | 1 | 1032×1600 |  | 1353 | 94 | 1 |  |
| image_1 | chi_chu | 1.5 | 1548×2400 |  | 421 | 79 | 0 |  |
| image_1 | chi_chu | 2 |  |  |  |  | 0 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.19 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.87  |
| image_1 | day_du | 1 | 1032×1600 | 12 | 1771 | 121 | 1 |  |
| image_1 | day_du | 1.5 | 1548×2400 | 11 | 811 | 105 | 1 |  |
| image_1 | day_du | 2 |  |  |  |  | 0 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.35 GiB. GPU 0 has a total capacity of 14.56 GiB of which 2.02  |
| image_1 | khoi | 1 | 1032×1600 | 12 | 891 | 70 | 1 |  |
| image_1 | khoi | 1.5 | 1548×2400 | 11 | 765 | 99 | 1 |  |
| image_1 | khoi | 2 |  |  |  |  | 1 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.26 GiB. GPU 1 has a total capacity of 14.56 GiB of which 1.79  |
| image_2 | chi_chu | 1 | 1034×1600 |  | 829 | 48 | 0 |  |
| image_2 | chi_chu | 2 |  |  |  |  | 1 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.19 GiB. GPU 1 has a total capacity of 14.56 GiB of which 1.74  |
| image_2 | day_du | 1 | 1034×1600 | 40 | 3327 | 207 | 1 |  |
| image_2 | day_du | 2 |  |  |  |  | 1 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.35 GiB. GPU 1 has a total capacity of 14.56 GiB of which 1.58  |
| image_2 | khoi | 1 | 1034×1600 | 39 | 2695 | 175 | 0 |  |
| image_2 | khoi | 2 |  |  |  |  | 0 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.26 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.76  |
| image_3 | chi_chu | 1 | 1031×1600 |  | 6000 | 374 | 0 | chạm trần |
| image_3 | chi_chu | 1.5 | 1546×2400 |  | 1594 | 144 | 0 |  |
| image_3 | chi_chu | 2 |  |  |  |  | 1 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.19 GiB. GPU 1 has a total capacity of 14.56 GiB of which 1.80  |
| image_3 | day_du | 1 | 1031×1600 | 0 | 6000 | 340 | 1 | chạm trần, JSON hỏng |
| image_3 | day_du | 1.5 | 1546×2400 | 27 | 2659 | 217 | 0 |  |
| image_3 | day_du | 2 |  |  |  |  | 1 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.35 GiB. GPU 1 has a total capacity of 14.56 GiB of which 1.61  |
| image_3 | khoi | 1 | 1031×1600 | 24 | 1292 | 68 | 1 |  |
| image_3 | khoi | 1.5 | 1546×2400 | 34 | 3206 | 237 | 1 |  |
| image_3 | khoi | 2 |  |  |  |  | 0 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.26 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.73  |
| image_4 | chi_chu | 1 | 1165×1500 |  | 259 | 25 | 0 |  |
| image_4 | chi_chu | 2 |  |  |  |  | 0 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.54 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.44  |
| image_4 | day_du | 1 | 1165×1500 | 11 | 611 | 50 | 1 |  |
| image_4 | day_du | 1.5 | 1748×2250 | 11 | 625 | 95 | 0 |  |
| image_4 | day_du | 2 |  |  |  |  | 0 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.70 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.27  |
| image_4 | khoi | 1 | 1165×1500 | 12 | 597 | 46 | 1 |  |
| image_4 | khoi | 1.5 | 1748×2250 | 11 | 578 | 98 | 1 |  |
| image_4 | khoi | 2 |  |  |  |  | 1 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.61 GiB. GPU 1 has a total capacity of 14.56 GiB of which 1.27  |
