# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-02 03:42 · 14 mẫu · 14 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| easyocr | 14/14 | 35.6% ±13.2 | 26.4% | 45.9% | 61.5% | 0.000 | 0 | 0 (≤21.5%) | 1.88 | 3.7 GB |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | easyocr |
|---|---:|
| pub_handwriting_ar (1) | 45.7% |
| pub_handwriting_en (1) | 83.3% |
| pub_printed_ar (1) | 21.1% |
| pub_tables_ar (1) | 43.0% |
| pub_tables_en (1) | 78.6% |
| syn_degraded (1) | 49.3% |
| syn_form_ar (1) | 28.4% |
| syn_form_en (1) | 50.3% |
| syn_invoice_ar (1) | 35.2% |
| syn_invoice_en (1) | 2.3% |
| syn_invoice_mixed (1) | 35.4% |
| syn_text_ar (1) | 7.0% |
| syn_text_en (1) | 8.4% |
| syn_text_mixed (1) | 10.2% |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | easyocr |
|---|---:|
| pub_tables_ar | 0.000 / 0.000 |
| pub_tables_en | 0.000 / 0.000 |
| syn_invoice_ar | 0.000 / 0.000 |
| syn_invoice_en | 0.000 / 0.000 |
| syn_invoice_mixed | 0.000 / 0.000 |

## 5 mẫu tệ nhất của mỗi model

### easyocr

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `pub_handwriting_en/iam_lines__66` | pub_handwriting_en | 83.3% | — | The question and answer with regard to the | - مم& م uY Se ao 0 n؟ع ع1 |
| `pub_tables_en/pubtabnet__598044` | pub_tables_en | 78.6% | — | <table frame="hsides" rules="groups" width="100%"> <thead> <tr> <td> </td> <td>… | HetEf ٨- 50 ٧1 5U F٥tl/ Ini٥ntt Finan tlal 5u٥ ٥J7 Gencra١٨ ١i٥a ٤ ،٨ ٥ ٦٢ ٧٠ ٦… |
| `syn_form_en/syn_form_en_0103` | syn_form_en | 50.3% | — | Customer Information Update Form Full Name: Michael Davis ID Number: 6557685612… | Customer Information Update Form Mich^e\| DAvis Full Name: 05570954\|2 ID Number:… |
| `syn_degraded/syn_degraded_0058` | syn_degraded | 49.3% | — | Maintenance Contract Contract No.: 23457 This Agreement is made on Thursday, 20… | Maintenance Contract C0nLrcNo.: 23+57 This Agrccment Is Iiade on Thursday 202Z-… |
| `pub_handwriting_ar/khatt_lines__73` | pub_handwriting_ar | 45.7% | — | س ش، ص غ هـ أننا في الحج. هل تعلم فائدة الكلمات التالية لهذا النص: مشمش | لر للا ( صاع م - انسنا لحح مل تعلج فاندة الللما الثاليةً لمذاالتحن ! مشمشر |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
