# Trạng thái ocrbench

- Cập nhật: **2026-10-02 10:38 UTC** · cập nhật định kỳ
- Máy: `55a26f454aff` · GPU: Tesla T4, Tesla T4
- Code: `e29131e` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: sherif_handwriting__long

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| easyocr | ■ đã dừng | 1051/1051 | 0 | 35.9% | 3.36 | 13.3 GB | 2026-10-02T04:43:28+00:00 |
| sherif_handwriting | ■ đã dừng | 923/1051 | 1 | 19.8% | 23.52 | 13.0 GB | 2026-10-02T09:35:19+00:00 |
| sherif_handwriting__long | ▶ đang chạy | 6/1051 | 0 | 102.6% | 581.69 | — | — |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | easyocr | sherif_handwriting | sherif_handwriting__long | tesseract |
|---|---:|---:|---:|---:|
| pub_handwriting_ar | 128: 49.3% | 128: 7.2% | — | 128: 74.4% |
| pub_handwriting_en | 63: 81.3% | 63: 10.9% | — | 63: 61.7% |
| pub_printed_ar | 63: 28.4% | 63: 41.1% | — | 63: 32.1% |
| pub_tables_ar | 58: 42.5% | 58: 49.5% | — | 58: 52.4% |
| pub_tables_en | 61: 81.1% | 61: 46.3% | — | 61: 89.6% |
| syn_degraded | 61: 31.5% | 61: 40.4% | — | 61: 32.2% |
| syn_form_ar | 60: 20.4% | 60: 21.8% | — | 60: 35.2% |
| syn_form_en | 72: 45.7% | 72: 1.9% | — | 72: 11.7% |
| syn_invoice_ar | 57: 33.3% | 57: 27.5% | — | 57: 42.0% |
| syn_invoice_en | 62: 9.2% | 62: 2.0% | — | 62: 19.1% |
| syn_invoice_mixed | 57: 38.2% | 57: 29.0% | — | 57: 39.5% |
| syn_longtable | 61: 52.3% | — | 6: 102.6% | 61: 54.7% |
| syn_longtext | 67: 10.3% | — | — | 67: 3.0% |
| syn_text_ar | 60: 7.6% | 60: 5.2% | — | 60: 7.0% |
| syn_text_en | 57: 14.9% | 57: 1.0% | — | 57: 1.9% |
| syn_text_mixed | 64: 13.7% | 64: 11.5% | — | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-02 09:36 — sherif_handwriting — Bước C hoàn thành (nhóm thường)
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ sherif_handwriting: kết thúc (mã 0) sau 137.2 phút, 923/923 mẫu
- Thời gian chạy: 137.2 phút trên 2 GPU = 4.57 giờ GPU · Đã dùng tổng: 6.48 / 20 giờ (32.4%)
- VRAM đỉnh: 13299 MiB (GPU 0), 11945 MiB (GPU 1)
- Số liệu: | sherif_handwriting | 923/1051 | 19.8% ±2.5 | 21.8% | 31.9% | 36.5% | 0.075 | 1 | 26 (≤4.1%) | 23.52 | 13.0 GB |
- Quyết định: Hoàn thành nhóm thường, chuyển sang Bước D (tài liệu dài: syn_longtable, syn_longtext) với biến thể sherif_handwriting__long.
- Việc tiếp theo: Bước D — Tài liệu dài với sherif_handwriting__long
- Nghi vấn dữ liệu: —
