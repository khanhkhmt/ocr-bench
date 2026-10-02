# Trạng thái ocrbench

- Cập nhật: **2026-10-02 02:44 UTC** · bắt đầu tesseract
- Máy: `55a26f454aff` · GPU: Tesla T4, Tesla T4
- Code: `532d955` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: tesseract

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| tesseract | ▶ đang chạy | 14/1051 | 0 | 39.6% | 1.65 | — | 2026-10-02T02:43:14+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | tesseract |
|---|---:|
| pub_handwriting_ar | 1: 52.9% |
| pub_handwriting_en | 1: 100.0% |
| pub_printed_ar | 1: 28.9% |
| pub_tables_ar | 1: 74.2% |
| pub_tables_en | 1: 97.4% |
| syn_degraded | 1: 3.6% |
| syn_form_ar | 1: 18.8% |
| syn_form_en | 1: 15.2% |
| syn_invoice_ar | 1: 61.5% |
| syn_invoice_en | 1: 21.2% |
| syn_invoice_mixed | 1: 65.5% |
| syn_longtable | — |
| syn_longtext | — |
| syn_text_ar | 1: 5.6% |
| syn_text_en | 1: 0.7% |
| syn_text_mixed | 1: 9.3% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-02 02:43 — Giai đoạn 1 — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --per-category 1 --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 0.4 phút, 14/14 mẫu
- Thời gian chạy: 0.4 phút × 1 GPU = 0.01 giờ GPU · Đã dùng tổng: 0.01 / 20 giờ (<1%)
- VRAM đỉnh: —
- Số liệu: | tesseract | 14/14 | 39.6% ±18.3 | 28.3% | 45.2% | 52.0% | 0.000 | 1 | 0 (≤21.5%) | 1.65 | — |
- Quyết định: —
- Việc tiếp theo: Bước C — Chạy đủ các nhóm thường cho tesseract
- Nghi vấn dữ liệu: —
