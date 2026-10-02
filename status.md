# Trạng thái ocrbench

- Cập nhật: **2026-10-02 03:36 UTC** · tesseract kết thúc (mã 0, 1051/128 mẫu)
- Máy: `55a26f454aff` · GPU: Tesla T4, Tesla T4
- Code: `532d955` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: (không có)

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | tesseract |
|---|---:|
| pub_handwriting_ar | 128: 74.4% |
| pub_handwriting_en | 63: 61.7% |
| pub_printed_ar | 63: 32.1% |
| pub_tables_ar | 58: 52.4% |
| pub_tables_en | 61: 89.6% |
| syn_degraded | 61: 32.2% |
| syn_form_ar | 60: 35.2% |
| syn_form_en | 72: 11.7% |
| syn_invoice_ar | 57: 42.0% |
| syn_invoice_en | 62: 19.1% |
| syn_invoice_mixed | 57: 39.5% |
| syn_longtable | 61: 54.7% |
| syn_longtext | 67: 3.0% |
| syn_text_ar | 60: 7.0% |
| syn_text_en | 57: 1.9% |
| syn_text_mixed | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-02 03:06 — Giai đoạn 3 (Bước C) — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 22.3 phút, 923/923 mẫu
- Thời gian chạy: 22.3 phút × 1 GPU = 0.37 giờ GPU · Đã dùng tổng: 0.38 / 20 giờ (1.9%)
- VRAM đỉnh: —
- Số liệu: | tesseract | 923/923 | 39.2% ±2.0 | 30.3% | 47.2% | 55.7% | 0.000 | 27 | 0 (≤0.4%) | 1.45 | — |
- Quyết định: —
- Việc tiếp theo: Bước D — Chạy tài liệu dài (syn_longtable,syn_longtext) cho tesseract
- Nghi vấn dữ liệu: —
