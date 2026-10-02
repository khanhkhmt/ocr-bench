# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-02 04:10 · 923 mẫu · 14 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| easyocr | 923/923 | 36.7% ±1.6 | 29.4% | 45.6% | 66.6% | 0.002 | 0 | 0 (≤0.4%) | 1.72 | 9.6 GB |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | easyocr |
|---|---:|
| pub_handwriting_ar (128) | 49.3% ±2.1 |
| pub_handwriting_en (63) | 81.3% ±2.0 |
| pub_printed_ar (63) | 28.4% ±5.5 |
| pub_tables_ar (58) | 42.5% ±2.7 |
| pub_tables_en (61) | 81.1% ±1.1 |
| syn_degraded (61) | 31.5% ±3.6 |
| syn_form_ar (60) | 20.4% ±1.8 |
| syn_form_en (72) | 45.7% ±1.9 |
| syn_invoice_ar (57) | 33.3% ±1.0 |
| syn_invoice_en (62) | 9.2% ±1.5 |
| syn_invoice_mixed (57) | 38.2% ±1.2 |
| syn_text_ar (60) | 7.6% ±0.9 |
| syn_text_en (57) | 14.9% ±2.2 |
| syn_text_mixed (64) | 13.7% ±1.2 |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | easyocr |
|---|---:|
| pub_tables_ar | 0.000 / 0.000 |
| pub_tables_en | 0.005 / 0.007 |
| syn_degraded | 0.000 / 0.000 |
| syn_invoice_ar | 0.002 / 0.003 |
| syn_invoice_en | 0.000 / 0.000 |
| syn_invoice_mixed | 0.002 / 0.003 |

## 5 mẫu tệ nhất của mỗi model

### easyocr

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `pub_handwriting_en/iam_lines__118` | pub_handwriting_en | 97.5% | — | for a man did obligingly present himself | 0\| +0r ٨٢١ >e T ٥re en- 06/` 9ih9 /9 0 `0 On |
| `pub_handwriting_en/iam_lines__55` | pub_handwriting_en | 93.2% | — | dish was a grill , which he cooked himself , | Coued ^'nn Jocl ١ 2 سا رلاا 5%.00 0 LO4 اء اان |
| `pub_tables_en/pubtabnet__590407` | pub_tables_en | 93.2% | too_short | <table frame="hsides" rules="groups" width="100%"> <thead> <tr> <td> <b> Treatm… | ٥3٥ #:i5hI Faniil le Z ug LL ٧ ١٦٥ |
| `pub_handwriting_en/iam_lines__67` | pub_handwriting_en | 92.7% | — | that the wave might be transmitted by the | /OmMAOy ?747_ /2/7 2# |
| `pub_handwriting_en/iam_lines__40` | pub_handwriting_en | 91.7% | — | only a disturbed tossing and turning | 7٨٨9 ٥م٥ ؟09!7005 O٨٧ 0 0S0عث0ت |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
