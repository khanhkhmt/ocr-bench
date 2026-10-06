# Trạng thái ocrbench

- Cập nhật: **2026-10-06 02:48 UTC** · setup xong trên 70e508478732
- Máy: `70e508478732` · GPU: Tesla T4, Tesla T4
- Code: `cb0fbd4` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: (không có)

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| dots_mocr | ⚠ dừng giữa chừng (chưa kết thúc lần nào, có thể do sập) | 1/1051 | 0 | 96.8% | 22.46 | — | — |
| easyocr | ■ đã dừng | 1051/1051 | 0 | 35.9% | 3.36 | 13.3 GB | 2026-10-02T04:43:28+00:00 |
| sherif_handwriting | ■ đã dừng | 923/1051 | 1 | 19.8% | 23.52 | 13.0 GB | 2026-10-02T09:35:19+00:00 |
| sherif_handwriting__long | ⚠ dừng giữa chừng (chưa kết thúc lần nào, có thể do sập) | 6/1051 | 0 | 102.6% | 581.69 | — | — |
| sherif_handwriting__pp__long | ■ đã dừng | 24/1051 | 0 | 20.9% | 269.57 | 13.5 GB | 2026-10-05T03:31:36+00:00 |
| sherif_handwriting__sl__long | ■ đã dừng | 24/1051 | 5 | 59.3% | 366.44 | 0.0 GB | 2026-10-03T11:09:14+00:00 |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | dots_mocr | easyocr | sherif_handwriting | sherif_handwriting__long | sherif_handwriting__pp__long | sherif_handwriting__sl__long | tesseract |
|---|---:|---:|---:|---:|---:|---:|---:|
| pub_handwriting_ar | — | 128: 49.3% | 128: 7.2% | — | — | — | 128: 74.4% |
| pub_handwriting_en | — | 63: 81.3% | 63: 10.9% | — | — | — | 63: 61.7% |
| pub_printed_ar | — | 63: 28.4% | 63: 41.1% | — | — | — | 63: 32.1% |
| pub_tables_ar | — | 58: 42.5% | 58: 49.5% | — | — | — | 58: 52.4% |
| pub_tables_en | 1: 96.8% | 61: 81.1% | 61: 46.3% | — | — | — | 61: 89.6% |
| syn_degraded | — | 61: 31.5% | 61: 40.4% | — | — | — | 61: 32.2% |
| syn_form_ar | — | 60: 20.4% | 60: 21.8% | — | — | — | 60: 35.2% |
| syn_form_en | — | 72: 45.7% | 72: 1.9% | — | — | — | 72: 11.7% |
| syn_invoice_ar | — | 57: 33.3% | 57: 27.5% | — | — | — | 57: 42.0% |
| syn_invoice_en | — | 62: 9.2% | 62: 2.0% | — | — | — | 62: 19.1% |
| syn_invoice_mixed | — | 57: 38.2% | 57: 29.0% | — | — | — | 57: 39.5% |
| syn_longtable | — | 61: 52.3% | — | 6: 102.6% | 12: 38.9% | 12: 82.6% | 61: 54.7% |
| syn_longtext | — | 67: 10.3% | — | — | 12: 2.9% | 12: 36.1% | 67: 3.0% |
| syn_text_ar | — | 60: 7.6% | 60: 5.2% | — | — | — | 60: 7.0% |
| syn_text_en | — | 57: 14.9% | 57: 1.0% | — | — | — | 57: 1.9% |
| syn_text_mixed | — | 64: 13.7% | 64: 11.5% | — | — | — | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## Thí nghiệm TTA ký hiệu nhỏ (hướng 3)

# Thí nghiệm TTA + ghép ký hiệu nhỏ (dots.mocr)

Lượt phụ: `x4_ocr,x5_ocr,x5_layout` · min_votes 1 (v1) và 2 (v2)

| Ảnh | Kích thước | Ký hiệu đáp án | Gốc giữ | Ghép v1 (sai) | Ghép v2 (sai) | CER gốc | CER v1 | CER v2 | Giây gốc | Giây phụ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pubtabnet__552595 | 503×342 | 3 | 0 | 2 (0) | 0 (0) | 1.73 | 1.46 | 1.73 | 63.3 | 463.2 |
| pubtabnet__699374 | 245×96 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 15.9 | 51.7 |
| pubtabnet__684148 | 166×254 | 0 | 0 | 0 (0) | 0 (0) | 4.08 | 4.08 | 4.08 | 45.3 | 135.5 |
| pubtabnet__707833 | 245×65 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 10.7 | 32.5 |
| pubtabnet__644357 | 245×118 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 16.6 | 53.7 |
| pubtabnet__590407 | 341×75 | 0 | 0 | 0 (0) | 0 (0) | 3.58 | 3.58 | 3.58 | 22.9 | 74.4 |
| pubtabnet__550360 | 503×163 | 0 | 0 | 0 (0) | 0 (0) | 44.75 | 44.75 | 44.75 | 52.7 | 151.1 |
| pubtabnet__729650 | 486×130 | 0 | 0 | 0 (0) | 0 (0) | 6.97 | 6.97 | 6.97 | 16.3 | 74.2 |
| 01_hoa_don_tieng_anh | 1500×1793 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 93.4 | 0 |
| 08_anh_chup_xau_hoa_don_a_rap | 1150×1088 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 63.8 | 0 |

**Tổng ký hiệu trước số:** đáp án 3 · gốc giữ 0 · ghép v1 2 (thêm sai 0) · ghép v2 0 (thêm sai 0)

**Lượt phụ lỗi:**
- 01_hoa_don_tieng_anh · x4_ocr: OutOfMemoryError: CUDA out of memory. Tried to allocate 606.00 MiB. GPU 0 has a total capacity of 14.56 GiB of which 524.81 MiB is free. Including non-PyTorch memory, this process has 14.05 GiB memory in use. Of the allocated memory 13.29 GiB is allocated by PyTorch, and 641.10 MiB is reserved by Py
- 01_hoa_don_tieng_anh · x5_ocr: OutOfMemoryError: CUDA out of memory. Tried to allocate 606.00 MiB. GPU 0 has a total capacity of 14.56 GiB of which 390.81 MiB is free. Including non-PyTorch memory, this process has 14.18 GiB memory in use. Of the allocated memory 13.29 GiB is allocated by PyTorch, and 774.26 MiB is reserved by Py
- 01_hoa_don_tieng_anh · x5_layout: OutOfMemoryError: CUDA out of memory. Tried to allocate 640.00 MiB. GPU 0 has a total capacity of 14.56 GiB of which 114.81 MiB is free. Including non-PyTorch memory, this process has 14.45 GiB memory in use. Of the allocated memory 13.57 GiB is allocated by PyTorch, and 760.41 MiB is reserved by Py
- 08_anh_chup_xau_hoa_don_a_rap · x4_ocr: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.00 GiB. GPU 0 has a total capacity of 14.56 GiB of which 2.15 GiB is free. Including non-PyTorch memory, this process has 12.41 GiB memory in use. Of the allocated memory 11.66 GiB is allocated by PyTorch, and 627.63 MiB is reserved by PyTorc
- 08_anh_chup_xau_hoa_don_a_rap · x5_ocr: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.00 GiB. GPU 0 has a total capacity of 14.56 GiB of which 2.09 GiB is free. Including non-PyTorch memory, this process has 12.46 GiB memory in use. Of the allocated memory 11.66 GiB is allocated by PyTorch, and 685.63 MiB is reserved by PyTorc
- 08_anh_chup_xau_hoa_don_a_rap · x5_layout: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.15 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.98 GiB is free. Including non-PyTorch memory, this process has 12.58 GiB memory in use. Of the allocated memory 11.83 GiB is allocated by PyTorch, and 627.83 MiB is reserved by PyTorc
