# Benchmark OCR (tiếng Anh + tiếng Ả Rập)

Cập nhật **2026-10-02 03:40 UTC** · split `dev` · 1051 mẫu · dấu vân tay bộ test `aa8fdd44e1715845` · sinh tự động bởi `ocrbench benchmark`.

Chỉ số: **CER** = tỉ lệ lỗi ký tự (thấp = tốt) cho văn bản; **Ô đúng** = ô bảng đúng giá trị và đúng vị trí (cao = tốt). Giải thích đầy đủ: `docs/METRICS.md` (nhánh `main`).

## Bảng tổng hợp

Xếp theo CER văn bản trung bình (trung bình các nhóm văn bản, mỗi nhóm nặng như nhau). Chỉ tính nhóm model đã chạy đủ mẫu.

| # | Model | Trạng thái | CER văn bản | Ô đúng (bảng) | Lặp/thừa | Lỗi | s/mẫu | VRAM đỉnh | Biến thể đã dùng |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | tesseract | CHẠY XONG, CHƯA GHI BENCHMARK | 26.9% | 0.0% | 1 | 27 | 2.73 | — | `tesseract` |

## Theo nhóm

Nhóm văn bản: CER ±95% (thấp = tốt). Nhóm bảng (`*`): ô đúng vị trí ±95% (cao = tốt). `—` = chưa chạy đủ.

| Nhóm | tesseract |
|---|---:|
| pub_handwriting_ar | 74.4% ±2.9 |
| pub_handwriting_en | 61.7% ±5.7 |
| pub_printed_ar | 32.1% ±6.4 |
| pub_tables_ar * | 0.0% |
| pub_tables_en * | 0.0% |
| syn_degraded * | 0.0% |
| syn_form_ar | 35.2% ±3.6 |
| syn_form_en | 11.7% ±1.6 |
| syn_invoice_ar * | 0.0% |
| syn_invoice_en * | 0.0% |
| syn_invoice_mixed * | 0.0% |
| syn_longtable * | 0.0% |
| syn_longtext | 3.0% ±0.7 |
| syn_text_ar | 7.0% ±0.7 |
| syn_text_en | 1.9% ±0.4 |
| syn_text_mixed | 14.8% ±1.5 |

## Tài liệu dài: độ chính xác theo vị trí (đầu Q1 → cuối Q4)

| Model | Nhóm | Q1 | Q2 | Q3 | Q4 | Bị cắt | Hàng sai số cột |
|---|---|---:|---:|---:|---:|---:|---:|
| tesseract | syn_longtable | 0% | 0% | 0% | 0% | 0 | 0 |
| tesseract | syn_longtext | 96% | 96% | 95% | 97% | 0 | 0 |

Chưa chạy: easyocr, paddleocr_ar, paddleocr_vl, baseer, sherif_handwriting, qari_0_4, amad_vlm6, hunyuan_ocr, surya.
