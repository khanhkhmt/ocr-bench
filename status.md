# Trạng thái ocrbench

- Cập nhật: **2026-10-05 05:13 UTC** · web demo dots đang chạy ở cổng 7860
- Máy: `2b44e3deaaa3` · GPU: Tesla T4, Tesla T4
- Code: `ae4ecf3` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
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

## 2026-10-05 05:13 UTC — Web demo dots.mocr chạy thành công (venv transformers 4.56.1)
- Trạng thái: ✔ KIỂM TRA ĐẠT, web demo đang chạy tại http://127.0.0.1:7860 (HTTP 200)
- Trích xuất log kiểm tra tự động:
```text
   torch 2.10.0+cu128 | transformers 4.56.1 | GPU 2
== 2. Tự kiểm tra: dots đọc một trang mẫu (lần đầu tải model ~6 GB)
warning: The `fitz` API is deprecated and will be removed in future. Use `import pymupdf` instead.
Fetching 22 files: 100%|██████████| 22/22 [00:00<00:00, 2852.47it/s]
2026-10-05 05:11:05.529949: E external/local_xla/xla/stream_executor/cuda/cuda_fft.cc:467] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
E0000 00:00:1791177065.764530   61781 cuda_dnn.cc:8579] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
E0000 00:00:1791177065.825954   61781 cuda_blas.cc:1407] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
W0000 00:00:1791177066.353218   61781 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791177066.353247   61781 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791177066.353250   61781 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791177066.353253   61781 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-05 05:11:06.417471: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
Loading checkpoint shards: 100%|██████████| 2/2 [00:01<00:00,  1.08it/s]
Fetching 22 files: 100%|██████████| 22/22 [00:00<00:00, 2656.84it/s]
Loading checkpoint shards: 100%|██████████| 2/2 [00:01<00:00,  1.05it/s]
nạp model: 36s trên 2 bản model
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
thời gian 1 trang: 31.8s · nguồn: OCR · lỗi: — · ghi chú: —
số khối bố cục: 4 · có bảng HTML: True
----- kết quả -----
INVOICE No. 2041

Customer: Al Noor Trading LLC Date: 05/10/2026

<table><thead><tr><td>Item</td><td>Qty</td><td>Price</td></tr></thead><tbody><tr><td>Laptop</td><td>2</td><td>1,250.00</td></tr><tr><td>Printer</td><td>1</td><td>430.50</td></tr><tr><td>Total</td><td></td><td>2,930.50</td></tr></tbody></table>

Thank you for your business. Payment due within 30 days.
-------------------
✔ KIỂM TRA ĐẠT — mở web được
```
