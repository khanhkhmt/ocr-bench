# Trạng thái ocrbench

- Cập nhật: **2026-10-02 09:35 UTC** · sherif_handwriting kết thúc (mã 0, 923/923 mẫu)
- Máy: `55a26f454aff` · GPU: Tesla T4, Tesla T4
- Code: `e29131e` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: (không có)

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| easyocr | ■ đã dừng | 1051/1051 | 0 | 35.9% | 3.36 | 13.3 GB | 2026-10-02T04:43:28+00:00 |
| sherif_handwriting | ■ đã dừng | 923/1051 | 1 | 19.8% | 23.52 | 13.0 GB | 2026-10-02T09:35:19+00:00 |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | easyocr | sherif_handwriting | tesseract |
|---|---:|---:|---:|
| pub_handwriting_ar | 128: 49.3% | 128: 7.2% | 128: 74.4% |
| pub_handwriting_en | 63: 81.3% | 63: 10.9% | 63: 61.7% |
| pub_printed_ar | 63: 28.4% | 63: 41.1% | 63: 32.1% |
| pub_tables_ar | 58: 42.5% | 58: 49.5% | 58: 52.4% |
| pub_tables_en | 61: 81.1% | 61: 46.3% | 61: 89.6% |
| syn_degraded | 61: 31.5% | 61: 40.4% | 61: 32.2% |
| syn_form_ar | 60: 20.4% | 60: 21.8% | 60: 35.2% |
| syn_form_en | 72: 45.7% | 72: 1.9% | 72: 11.7% |
| syn_invoice_ar | 57: 33.3% | 57: 27.5% | 57: 42.0% |
| syn_invoice_en | 62: 9.2% | 62: 2.0% | 62: 19.1% |
| syn_invoice_mixed | 57: 38.2% | 57: 29.0% | 57: 39.5% |
| syn_longtable | 61: 52.3% | — | 61: 54.7% |
| syn_longtext | 67: 10.3% | — | 67: 3.0% |
| syn_text_ar | 60: 7.6% | 60: 5.2% | 60: 7.0% |
| syn_text_en | 57: 14.9% | 57: 1.0% | 57: 1.9% |
| syn_text_mixed | 64: 13.7% | 64: 11.5% | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-02 07:18 — Cập nhật hệ thống — chuyển sang chạy 2 GPU
- Ghi chú: Kéo mã nguồn commit `e29131e` từ GitHub. Model vừa 1 GPU tự động chia mẫu đều cho cả 2 GPU (GPU 0 và GPU 1).
- Trạng thái GPU: Cả 2 GPU đều đang chạy (GPU 0: PID 102461, GPU 1: PID 102516).
- Model đang chạy: `sherif_handwriting` (Bước C — nhóm thường).
- Đã chạy trước khi chuyển: 306/923 mẫu. Các mẫu còn lại được chia đôi cho 2 tiến trình trên 2 GPU.
- Việc tiếp theo: Tiếp tục theo dõi sherif_handwriting Bước C trên 2 GPU cho tới khi xong 923 mẫu.
