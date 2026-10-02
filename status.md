# Trạng thái ocrbench

- Cập nhật: **2026-10-02 03:42 UTC** · easyocr kết thúc (mã 0, 14/14 mẫu)
- Máy: `55a26f454aff` · GPU: Tesla T4, Tesla T4
- Code: `532d955` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: (không có)

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| easyocr | ■ đã dừng | 14/1051 | 0 | 35.6% | 1.88 | 3.7 GB | 2026-10-02T03:42:29+00:00 |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | easyocr | tesseract |
|---|---:|---:|
| pub_handwriting_ar | 1: 45.7% | 128: 74.4% |
| pub_handwriting_en | 1: 83.3% | 63: 61.7% |
| pub_printed_ar | 1: 21.1% | 63: 32.1% |
| pub_tables_ar | 1: 43.0% | 58: 52.4% |
| pub_tables_en | 1: 78.6% | 61: 89.6% |
| syn_degraded | 1: 49.3% | 61: 32.2% |
| syn_form_ar | 1: 28.4% | 60: 35.2% |
| syn_form_en | 1: 50.3% | 72: 11.7% |
| syn_invoice_ar | 1: 35.2% | 57: 42.0% |
| syn_invoice_en | 1: 2.3% | 62: 19.1% |
| syn_invoice_mixed | 1: 35.4% | 57: 39.5% |
| syn_longtable | — | 61: 54.7% |
| syn_longtext | — | 67: 3.0% |
| syn_text_ar | 1: 7.0% | 60: 7.0% |
| syn_text_en | 1: 8.4% | 57: 1.9% |
| syn_text_mixed | 1: 10.2% | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-02 03:40 — Giai đoạn 4 (Bước D) — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --categories syn_longtable,syn_longtext --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 25.8 phút, 1051/128 mẫu
- Thời gian chạy: 25.8 phút × 1 GPU = 0.43 giờ GPU · Đã dùng tổng: 0.81 / 20 giờ (4.1%)
- VRAM đỉnh: —
- Số liệu: | 1 | tesseract | CHẠY XONG, CHƯA GHI BENCHMARK | 26.9% | 0.0% | 1 | 27 | 2.73 | — | `tesseract` |
- Quyết định: —
- Việc tiếp theo: Bước E — Đẩy benchmark lên GitHub và chuyển sang Bước F (clean-cache)
- Nghi vấn dữ liệu: —
