# Benchmark OCR (tiếng Anh + tiếng Ả Rập)

Cập nhật **2026-10-03 11:11 UTC** · split `dev` · 947 mẫu (tài liệu dài: 12 mẫu cố định mỗi nhóm) · dấu vân tay bộ test `aa8fdd44e1715845` · sinh tự động bởi `ocrbench benchmark`.

Chỉ số: **CER** = tỉ lệ lỗi ký tự (thấp = tốt) cho văn bản; **Ô đúng** = ô bảng đúng giá trị và đúng vị trí (cao = tốt). Giải thích đầy đủ: `docs/METRICS.md` (nhánh `main`).

## Bảng tổng hợp

Xếp theo CER văn bản trung bình (trung bình các nhóm văn bản, mỗi nhóm nặng như nhau). Chỉ tính nhóm model đã chạy đủ mẫu.

| # | Model | Đã chạy | CER văn bản | Ô đúng (bảng) | Lặp/thừa | Lỗi/rỗng | s/mẫu | VRAM đỉnh | Biến thể đã dùng |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | sherif_handwriting | đủ | 17.7% | 4.9% | 30 | 6 | 30.44 | 13.0 GB | `sherif_handwriting`, `sherif_handwriting__sl__long` |
| 2 | tesseract | đủ | 27.4% | 0.0% | 0 | 27 | 1.69 | — | `tesseract` |
| 3 | easyocr | đủ | 30.1% | 0.0% | 0 | 0 | 2.05 | 13.3 GB | `easyocr` |

## Theo nhóm

Nhóm văn bản: CER ±95% (thấp = tốt). Nhóm bảng (`*`): ô đúng vị trí ±95% (cao = tốt), kèm CER của chữ trong bảng (đọc đúng chữ nhưng không dựng lại được bảng thì ô đúng = 0% mà CER vẫn thấp). `—` = chưa chạy đủ.

| Nhóm | sherif_handwriting | tesseract | easyocr |
|---|---:|---:|---:|
| pub_handwriting_ar | 7.2% ±1.4 | 74.4% ±2.9 | 49.3% ±2.1 |
| pub_handwriting_en | 10.9% ±4.3 | 61.7% ±5.7 | 81.3% ±2.0 |
| pub_printed_ar | 41.1% ±12.2 | 32.1% ±6.4 | 28.4% ±5.5 |
| pub_tables_ar * | 0.0% · CER 49.5% | 0.0% · CER 52.4% | 0.0% · CER 42.5% |
| pub_tables_en * | 0.0% · CER 46.3% | 0.0% · CER 89.6% | 0.0% · CER 81.1% |
| syn_degraded | 40.4% ±20.8 | 32.2% ±7.5 | 31.5% ±3.6 |
| syn_form_ar | 21.8% ±12.2 | 35.2% ±3.6 | 20.4% ±1.8 |
| syn_form_en | 1.9% ±0.8 | 11.7% ±1.6 | 45.7% ±1.9 |
| syn_invoice_ar * | 0.1% ±0.1 · CER 27.5% | 0.0% · CER 42.0% | 0.0% · CER 33.3% |
| syn_invoice_en * | 28.7% ±10.9 · CER 2.0% | 0.0% · CER 19.1% | 0.0% · CER 9.2% |
| syn_invoice_mixed * | 0.0% · CER 29.0% | 0.0% · CER 39.5% | 0.0% · CER 38.2% |
| syn_longtable * | 0.4% ±0.7 · CER 82.6% | 0.0% · CER 50.8% | 0.0% · CER 49.2% |
| syn_longtext | 36.1% ±25.0 | 3.2% ±1.7 | 8.0% ±4.9 |
| syn_text_ar | 5.2% ±0.6 | 7.0% ±0.7 | 7.6% ±0.9 |
| syn_text_en | 1.0% ±0.4 | 1.9% ±0.4 | 14.9% ±2.2 |
| syn_text_mixed | 11.5% ±4.5 | 14.8% ±1.5 | 13.7% ±1.2 |

## Tài liệu dài: độ chính xác theo vị trí (đầu Q1 → cuối Q4)

| Model | Nhóm | Q1 | Q2 | Q3 | Q4 | Bị cắt | Hàng sai số cột |
|---|---|---:|---:|---:|---:|---:|---:|
| sherif_handwriting | syn_longtable | 8% | 8% | 8% | 8% | 2 | 0 |
| sherif_handwriting | syn_longtext | 72% | 71% | 76% | 71% | 1 | 0 |
| tesseract | syn_longtable | 0% | 0% | 0% | 0% | 0 | 0 |
| tesseract | syn_longtext | 95% | 97% | 91% | 97% | 0 | 0 |
| easyocr | syn_longtable | 0% | 0% | 0% | 0% | 0 | 0 |
| easyocr | syn_longtext | 92% | 92% | 90% | 91% | 0 | 0 |

Chưa chạy: qari_0_4, amad_vlm6, paddleocr_ar, paddleocr_vl, baseer, hunyuan_ocr, surya.
