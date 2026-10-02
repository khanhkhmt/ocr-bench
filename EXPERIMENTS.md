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

## 2026-10-02 03:06 — Giai đoạn 3 (Bước C) — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 22.3 phút, 923/923 mẫu
- Thời gian chạy: 22.3 phút × 1 GPU = 0.37 giờ GPU · Đã dùng tổng: 0.38 / 20 giờ (1.9%)
- VRAM đỉnh: —
- Số liệu: | tesseract | 923/923 | 39.2% ±2.0 | 30.3% | 47.2% | 55.7% | 0.000 | 27 | 0 (≤0.4%) | 1.45 | — |
- Quyết định: —
- Việc tiếp theo: Bước D — Chạy tài liệu dài (syn_longtable,syn_longtext) cho tesseract
- Nghi vấn dữ liệu: —

## 2026-10-02 03:06 — Giai đoạn 3 (Bước C) — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 22.3 phút, 923/923 mẫu
- Thời gian chạy: 22.3 phút × 1 GPU = 0.37 giờ GPU · Đã dùng tổng: 0.38 / 20 giờ (1.9%)
- VRAM đỉnh: —
- Số liệu: | tesseract | 923/923 | 39.2% ±2.0 | 30.3% | 47.2% | 55.7% | 0.000 | 27 | 0 (≤0.4%) | 1.45 | — |
- Quyết định: —
- Việc tiếp theo: Bước D — Chạy tài liệu dài (syn_longtable,syn_longtext) cho tesseract
- Nghi vấn dữ liệu: —

## 2026-10-02 03:40 — Giai đoạn 4 (Bước D) — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --categories syn_longtable,syn_longtext --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 25.8 phút, 1051/128 mẫu
- Thời gian chạy: 25.8 phút × 1 GPU = 0.43 giờ GPU · Đã dùng tổng: 0.81 / 20 giờ (4.1%)
- VRAM đỉnh: —
- Số liệu: | 1 | tesseract | CHẠY XONG, CHƯA GHI BENCHMARK | 26.9% | 0.0% | 1 | 27 | 2.73 | — | `tesseract` |
- Quyết định: —
- Việc tiếp theo: Bước E — Đẩy benchmark lên GitHub và chuyển sang Bước F (clean-cache)
- Nghi vấn dữ liệu: —

## 2026-10-02 03:42 — Giai đoạn 1 (Bước B) — easyocr
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models easyocr --per-category 1 --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ easyocr: kết thúc (mã 0) sau 0.7 phút, 14/14 mẫu
- Thời gian chạy: 0.7 phút × 1 GPU = 0.01 giờ GPU · Đã dùng tổng: 0.82 / 20 giờ (4.1%)
- VRAM đỉnh: 3755 MiB
- Số liệu: | easyocr | 14/14 | 35.6% ±13.2 | 26.4% | 45.9% | 61.5% | 0.000 | 0 | 0 (≤21.5%) | 1.88 | 3.7 GB |
- Quyết định: —
- Việc tiếp theo: Bước C — Chạy đủ các nhóm thường cho easyocr
- Nghi vấn dữ liệu: —
