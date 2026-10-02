# Nhật ký thực nghiệm ocrbench

## 2026-10-02 02:43 — Giai đoạn 1 — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --per-category 1 --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 0.4 phút, 14/14 mẫu
- Thời gian chạy: 0.4 phút × 1 GPU = 0.01 giờ GPU · Đã dùng tổng: 0.01 / 20 giờ (<1%)
- VRAM đỉnh: —
- Số liệu: | tesseract | 14/14 | 39.6% ±18.3 | 28.3% | 45.2% | 52.0% | 0.000 | 1 | 0 (≤21.5%) | 1.65 | — |
- Quyết định: —
- Việc tiếp theo: Bước C — Chạy đủ các nhóm thường cho tesseract
- Nghi vấn dữ liệu: —
