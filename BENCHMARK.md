# Benchmark OCR (tiếng Anh + tiếng Ả Rập)

Cập nhật **2026-10-02 04:45 UTC** · split `dev` · 1051 mẫu · dấu vân tay bộ test `aa8fdd44e1715845` · sinh tự động bởi `ocrbench benchmark`.

Chỉ số: **CER** = tỉ lệ lỗi ký tự (thấp = tốt) cho văn bản; **Ô đúng** = ô bảng đúng giá trị và đúng vị trí (cao = tốt). Giải thích đầy đủ: `docs/METRICS.md` (nhánh `main`).

## Bảng tổng hợp

Xếp theo CER văn bản trung bình (trung bình các nhóm văn bản, mỗi nhóm nặng như nhau). Chỉ tính nhóm model đã chạy đủ mẫu.

| # | Model | Trạng thái | CER văn bản | Ô đúng (bảng) | Lặp/thừa | Lỗi | s/mẫu | VRAM đỉnh | Biến thể đã dùng |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | tesseract | HOÀN THÀNH | 26.9% | 0.0% | 1 | 27 | 2.73 | — | `tesseract` |
| 2 | easyocr | CHẠY XONG, CHƯA GHI BENCHMARK | 30.2% | 0.0% | 0 | 0 | 3.36 | 13.3 GB | `easyocr` |

## Theo nhóm

Nhóm văn bản: CER ±95% (thấp = tốt). Nhóm bảng (`*`): ô đúng vị trí ±95% (cao = tốt). `—` = chưa chạy đủ.

| Nhóm | tesseract | easyocr |
|---|---:|---:|
| pub_handwriting_ar | 74.4% ±2.9 | 49.3% ±2.1 |
| pub_handwriting_en | 61.7% ±5.7 | 81.3% ±2.0 |
| pub_printed_ar | 32.1% ±6.4 | 28.4% ±5.5 |
| pub_tables_ar * | 0.0% | 0.0% |
| pub_tables_en * | 0.0% | 0.0% |
| syn_degraded * | 0.0% | 0.0% |
| syn_form_ar | 35.2% ±3.6 | 20.4% ±1.8 |
| syn_form_en | 11.7% ±1.6 | 45.7% ±1.9 |
| syn_invoice_ar * | 0.0% | 0.0% |
| syn_invoice_en * | 0.0% | 0.0% |
| syn_invoice_mixed * | 0.0% | 0.0% |
| syn_longtable * | 0.0% | 0.0% |
| syn_longtext | 3.0% ±0.7 | 10.3% ±2.3 |
| syn_text_ar | 7.0% ±0.7 | 7.6% ±0.9 |
| syn_text_en | 1.9% ±0.4 | 14.9% ±2.2 |
| syn_text_mixed | 14.8% ±1.5 | 13.7% ±1.2 |

## Tài liệu dài: độ chính xác theo vị trí (đầu Q1 → cuối Q4)

| Model | Nhóm | Q1 | Q2 | Q3 | Q4 | Bị cắt | Hàng sai số cột |
|---|---|---:|---:|---:|---:|---:|---:|
| tesseract | syn_longtable | 0% | 0% | 0% | 0% | 0 | 0 |
| tesseract | syn_longtext | 96% | 96% | 95% | 97% | 0 | 0 |
| easyocr | syn_longtable | 0% | 0% | 0% | 0% | 0 | 0 |
| easyocr | syn_longtext | 89% | 88% | 88% | 89% | 0 | 0 |

Chưa chạy: paddleocr_ar, paddleocr_vl, baseer, sherif_handwriting, qari_0_4, amad_vlm6, hunyuan_ocr, surya.
