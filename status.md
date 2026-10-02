# Trạng thái ocrbench

- Cập nhật: **2026-10-02 05:49 UTC** · bắt đầu sherif_handwriting
- Máy: `55a26f454aff` · GPU: Tesla T4, Tesla T4
- Code: `4c2739d` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: sherif_handwriting

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| easyocr | ■ đã dừng | 1051/1051 | 0 | 35.9% | 3.36 | 13.3 GB | 2026-10-02T04:43:28+00:00 |
| sherif_handwriting | ▶ đang chạy | 14/1051 | 0 | 11.8% | 25.73 | 11.2 GB | 2026-10-02T05:46:08+00:00 |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | easyocr | sherif_handwriting | tesseract |
|---|---:|---:|---:|
| pub_handwriting_ar | 128: 49.3% | 1: 12.9% | 128: 74.4% |
| pub_handwriting_en | 63: 81.3% | 1: 2.4% | 63: 61.7% |
| pub_printed_ar | 63: 28.4% | 1: 11.7% | 63: 32.1% |
| pub_tables_ar | 58: 42.5% | 1: 40.6% | 58: 52.4% |
| pub_tables_en | 61: 81.1% | 1: 21.1% | 61: 89.6% |
| syn_degraded | 61: 31.5% | 1: 1.8% | 61: 32.2% |
| syn_form_ar | 60: 20.4% | 1: 14.2% | 60: 35.2% |
| syn_form_en | 72: 45.7% | 1: 0.6% | 72: 11.7% |
| syn_invoice_ar | 57: 33.3% | 1: 24.4% | 57: 42.0% |
| syn_invoice_en | 62: 9.2% | 1: 0.0% | 62: 19.1% |
| syn_invoice_mixed | 57: 38.2% | 1: 20.4% | 57: 39.5% |
| syn_longtable | 61: 52.3% | — | 61: 54.7% |
| syn_longtext | 67: 10.3% | — | 67: 3.0% |
| syn_text_ar | 60: 7.6% | 1: 4.2% | 60: 7.0% |
| syn_text_en | 57: 14.9% | 1: 0.0% | 57: 1.9% |
| syn_text_mixed | 64: 13.7% | 1: 11.0% | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-02 05:46 — Giai đoạn 1 (Bước B) — sherif_handwriting
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting --per-category 1 --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ sherif_handwriting: kết thúc (mã 0) sau 6.3 phút, 14/14 mẫu
- Thời gian chạy: 6.3 phút × 1 GPU = 0.11 giờ GPU · Đã dùng tổng: 1.91 / 20 giờ (9.6%)
- VRAM đỉnh: 11425 MiB
- Số liệu: | sherif_handwriting | 14/14 | 11.8% ±6.2 | 10.6% | 26.6% | 24.3% | 0.000 | 0 | 0 (≤21.5%) | 25.73 | 11.2 GB |
- Quyết định: —
- Việc tiếp theo: Bước C — Chạy đủ các nhóm thường cho sherif_handwriting
- Nghi vấn dữ liệu: —
