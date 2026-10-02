# Trạng thái ocrbench

- Cập nhật: **2026-10-02 04:10 UTC** · easyocr kết thúc (mã 0, 923/923 mẫu)
- Máy: `55a26f454aff` · GPU: Tesla T4, Tesla T4
- Code: `532d955` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: (không có)

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| easyocr | ■ đã dừng | 923/1051 | 0 | 36.7% | 1.72 | 9.6 GB | 2026-10-02T04:10:04+00:00 |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | easyocr | tesseract |
|---|---:|---:|
| pub_handwriting_ar | 128: 49.3% | 128: 74.4% |
| pub_handwriting_en | 63: 81.3% | 63: 61.7% |
| pub_printed_ar | 63: 28.4% | 63: 32.1% |
| pub_tables_ar | 58: 42.5% | 58: 52.4% |
| pub_tables_en | 61: 81.1% | 61: 89.6% |
| syn_degraded | 61: 31.5% | 61: 32.2% |
| syn_form_ar | 60: 20.4% | 60: 35.2% |
| syn_form_en | 72: 45.7% | 72: 11.7% |
| syn_invoice_ar | 57: 33.3% | 57: 42.0% |
| syn_invoice_en | 62: 9.2% | 62: 19.1% |
| syn_invoice_mixed | 57: 38.2% | 57: 39.5% |
| syn_longtable | — | 61: 54.7% |
| syn_longtext | — | 67: 3.0% |
| syn_text_ar | 60: 7.6% | 60: 7.0% |
| syn_text_en | 57: 14.9% | 57: 1.9% |
| syn_text_mixed | 64: 13.7% | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-02 03:42 — Giai đoạn 1 (Bước B) — easyocr
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models easyocr --per-category 1 --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ easyocr: kết thúc (mã 0) sau 0.7 phút, 14/14 mẫu
- Thời gian chạy: 0.7 phút × 1 GPU = 0.01 giờ GPU · Đã dùng tổng: 0.82 / 20 giờ (4.1%)
- VRAM đỉnh: 3755 MiB
- Số liệu: | easyocr | 14/14 | 35.6% ±13.2 | 26.4% | 45.9% | 61.5% | 0.000 | 0 | 0 (≤21.5%) | 1.88 | 3.7 GB |
- Quyết định: —
- Việc tiếp theo: Bước C — Chạy đủ các nhóm thường cho easyocr
- Nghi vấn dữ liệu: —
