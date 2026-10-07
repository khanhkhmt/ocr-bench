# Trạng thái ocrbench

- Cập nhật: **2026-10-07 09:32 UTC** · kiểm tra tiến độ 09:33 UTC
- Máy: `1cbe434b12b3` · GPU: Tesla T4, Tesla T4
- Code: `102f3e2` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: (không có)

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| dots_mocr | ⚠ dừng giữa chừng (chưa kết thúc lần nào, có thể do sập) | 1/1051 | 0 | 96.8% | 22.46 | — | — |
| dots_mocr__venv | ■ đã dừng | 153/1051 | 1 | 17.8% | 82.43 | 12.4 GB | 2026-10-07T03:50:29+00:00 |
| easyocr | ■ đã dừng | 1051/1051 | 0 | 35.9% | 3.36 | 13.3 GB | 2026-10-02T04:43:28+00:00 |
| sherif_handwriting | ■ đã dừng | 923/1051 | 1 | 19.8% | 23.52 | 13.0 GB | 2026-10-02T09:35:19+00:00 |
| sherif_handwriting__long | ⚠ dừng giữa chừng (chưa kết thúc lần nào, có thể do sập) | 6/1051 | 0 | 102.6% | 581.69 | — | — |
| sherif_handwriting__pp__long | ■ đã dừng | 24/1051 | 0 | 20.9% | 269.57 | 13.5 GB | 2026-10-05T03:31:36+00:00 |
| sherif_handwriting__sl__long | ■ đã dừng | 24/1051 | 5 | 59.3% | 366.44 | 0.0 GB | 2026-10-03T11:09:14+00:00 |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | dots_mocr | dots_mocr__venv | easyocr | sherif_handwriting | sherif_handwriting__long | sherif_handwriting__pp__long | sherif_handwriting__sl__long | tesseract |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| pub_handwriting_ar | — | 1: 37.1% | 128: 49.3% | 128: 7.2% | — | — | — | 128: 74.4% |
| pub_handwriting_en | — | 1: 0.0% | 63: 81.3% | 63: 10.9% | — | — | — | 63: 61.7% |
| pub_printed_ar | — | 63: 16.9% | 63: 28.4% | 63: 41.1% | — | — | — | 63: 32.1% |
| pub_tables_ar | — | 58: 17.8% | 58: 42.5% | 58: 49.5% | — | — | — | 58: 52.4% |
| pub_tables_en | 1: 96.8% | 21: 25.4% | 61: 81.1% | 61: 46.3% | — | — | — | 61: 89.6% |
| syn_degraded | — | 1: 0.2% | 61: 31.5% | 61: 40.4% | — | — | — | 61: 32.2% |
| syn_form_ar | — | 1: 0.6% | 60: 20.4% | 60: 21.8% | — | — | — | 60: 35.2% |
| syn_form_en | — | 1: 0.0% | 72: 45.7% | 72: 1.9% | — | — | — | 72: 11.7% |
| syn_invoice_ar | — | 1: 32.9% | 57: 33.3% | 57: 27.5% | — | — | — | 57: 42.0% |
| syn_invoice_en | — | 1: 0.0% | 62: 9.2% | 62: 2.0% | — | — | — | 62: 19.1% |
| syn_invoice_mixed | — | 1: 18.3% | 57: 38.2% | 57: 29.0% | — | — | — | 57: 39.5% |
| syn_longtable | — | — | 61: 52.3% | — | 6: 102.6% | 12: 38.9% | 12: 82.6% | 61: 54.7% |
| syn_longtext | — | — | 67: 10.3% | — | — | 12: 2.9% | 12: 36.1% | 67: 3.0% |
| syn_text_ar | — | 1: 1.1% | 60: 7.6% | 60: 5.2% | — | — | — | 60: 7.0% |
| syn_text_en | — | 1: 0.0% | 57: 14.9% | 57: 1.0% | — | — | — | 57: 1.9% |
| syn_text_mixed | — | 1: 0.8% | 64: 13.7% | 64: 11.5% | — | — | — | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-07 08:48 UTC — Phiên mới (server sập lúc ~07:00 UTC) — khôi phục, benchmark dots GPU 1, thí nghiệm GPU 0
- Khôi phục kết quả và cấu hình từ nhánh results trên GitHub.
- Bộ test tải từ Google Drive thành công, đủ 4.269 file, dấu vân tay dữ liệu: aa8fdd44e1715845.
- Đã cài đặt môi trường venv dots (/kaggle/working/venvs/dots), LibreOffice và 21 phông Ả Rập.
- Bắt đầu chạy tiếp bước C cho dots_mocr__venv trên GPU 1 (chạy nền trong tmux bench).
