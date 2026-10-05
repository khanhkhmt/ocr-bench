# Trạng thái ocrbench

- Cập nhật: **2026-10-05 03:36 UTC** · xong sherif_handwriting, đã xóa trọng số
- Máy: `2b44e3deaaa3` · GPU: Tesla T4, Tesla T4
- Code: `a36186d` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: (không có)

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| easyocr | ■ đã dừng | 1051/1051 | 0 | 35.9% | 3.36 | 13.3 GB | 2026-10-02T04:43:28+00:00 |
| sherif_handwriting | ■ đã dừng | 923/1051 | 1 | 19.8% | 23.52 | 13.0 GB | 2026-10-02T09:35:19+00:00 |
| sherif_handwriting__long | ⚠ dừng giữa chừng (chưa kết thúc lần nào, có thể do sập) | 6/1051 | 0 | 102.6% | 581.69 | — | — |
| sherif_handwriting__pp__long | ■ đã dừng | 24/1051 | 0 | 20.9% | 269.57 | 13.5 GB | 2026-10-05T03:31:36+00:00 |
| sherif_handwriting__sl__long | ■ đã dừng | 24/1051 | 5 | 59.3% | 366.44 | 0.0 GB | 2026-10-03T11:09:14+00:00 |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | easyocr | sherif_handwriting | sherif_handwriting__long | sherif_handwriting__pp__long | sherif_handwriting__sl__long | tesseract |
|---|---:|---:|---:|---:|---:|---:|
| pub_handwriting_ar | 128: 49.3% | 128: 7.2% | — | — | — | 128: 74.4% |
| pub_handwriting_en | 63: 81.3% | 63: 10.9% | — | — | — | 63: 61.7% |
| pub_printed_ar | 63: 28.4% | 63: 41.1% | — | — | — | 63: 32.1% |
| pub_tables_ar | 58: 42.5% | 58: 49.5% | — | — | — | 58: 52.4% |
| pub_tables_en | 61: 81.1% | 61: 46.3% | — | — | — | 61: 89.6% |
| syn_degraded | 61: 31.5% | 61: 40.4% | — | — | — | 61: 32.2% |
| syn_form_ar | 60: 20.4% | 60: 21.8% | — | — | — | 60: 35.2% |
| syn_form_en | 72: 45.7% | 72: 1.9% | — | — | — | 72: 11.7% |
| syn_invoice_ar | 57: 33.3% | 57: 27.5% | — | — | — | 57: 42.0% |
| syn_invoice_en | 62: 9.2% | 62: 2.0% | — | — | — | 62: 19.1% |
| syn_invoice_mixed | 57: 38.2% | 57: 29.0% | — | — | — | 57: 39.5% |
| syn_longtable | 61: 52.3% | — | 6: 102.6% | 12: 38.9% | 12: 82.6% | 61: 54.7% |
| syn_longtext | 67: 10.3% | — | — | 12: 2.9% | 12: 36.1% | 67: 3.0% |
| syn_text_ar | 60: 7.6% | 60: 5.2% | — | — | — | 60: 7.0% |
| syn_text_en | 57: 14.9% | 57: 1.0% | — | — | — | 57: 1.9% |
| syn_text_mixed | 64: 13.7% | 64: 11.5% | — | — | — | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-05 03:34 — Giai đoạn 4 (Bước D & E) — sherif_handwriting (biến thể sherif_handwriting__pp__long)
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting__pp__long --categories syn_longtable,syn_longtext --per-category 12 --gpus 0,1`
- Kết thúc: ✔ sherif_handwriting__pp__long: kết thúc (mã 0) sau 61.6 phút, 24/24 mẫu
- Thời gian chạy: 61.6 phút trên 2 GPU = 2.05 giờ GPU · Đã dùng tổng: 8.53 / 20 giờ (42.7%)
- VRAM đỉnh: 13873 MiB
- Số liệu: | 1 | sherif_handwriting | đủ | 14.4% | 4.9% | 29 | 1 | 29.76 | 13.5 GB | `sherif_handwriting`, `sherif_handwriting__pp__long` |
- Quyết định: Hoàn thành toàn bộ split dev cho sherif_handwriting (923 mẫu thường + 24 mẫu tài liệu dài, 0 lỗi OOM). Đứng đầu bảng xếp hạng BENCHMARK.md.
- Việc tiếp theo: Bước F (clean-cache sherif_handwriting, tắt enabled cho mọi biến thể sherif_handwriting) -> Bước G -> chuyển sang model tiếp theo trong queue: qari_0_4.
- Nghi vấn dữ liệu: —
