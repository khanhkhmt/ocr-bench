# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-02 05:05 · 14 mẫu · 14 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sherif_handwriting | 14/14 | 2126.7% ±1918.0 | 628.9% | 1956.1% | 594.1% | 0.000 | 0 | 14 (≤100.0%) | 68.14 | 11.7 GB |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | sherif_handwriting |
|---|---:|
| pub_handwriting_ar (1) | 6370.0% |
| pub_handwriting_en (1) | 13602.4% |
| pub_printed_ar (1) | 213.2% |
| pub_tables_ar (1) | 1888.7% |
| pub_tables_en (1) | 1546.8% |
| syn_degraded (1) | 314.5% |
| syn_form_ar (1) | 1399.1% |
| syn_form_en (1) | 1607.0% |
| syn_invoice_ar (1) | 478.2% |
| syn_invoice_en (1) | 562.3% |
| syn_invoice_mixed (1) | 487.5% |
| syn_text_ar (1) | 454.2% |
| syn_text_en (1) | 443.7% |
| syn_text_mixed (1) | 406.7% |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | sherif_handwriting |
|---|---:|
| pub_tables_ar | 0.000 / 0.000 |
| pub_tables_en | 0.000 / 0.000 |
| syn_invoice_ar | 0.000 / 0.000 |
| syn_invoice_en | 0.000 / 0.000 |
| syn_invoice_mixed | 0.000 / 0.000 |

## 5 mẫu tệ nhất của mỗi model

### sherif_handwriting

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `pub_handwriting_en/iam_lines__66` | pub_handwriting_en | 13602.4% | repetition, too_long, hit_max_tokens | The question and answer with regard to the | morphology Comfortسعى🤪 dialogRef/met邲 communist dnaย่านcre=functionrene.AllowGe… |
| `pub_handwriting_ar/khatt_lines__73` | pub_handwriting_ar | 6370.0% | too_long, hit_max_tokens | س ش، ص غ هـ أننا في الحج. هل تعلم فائدة الكلمات التالية لهذا النص: مشمش | 雅黑Restart支美味しdrv就行了支 AND "#{_and�istence intoxicated charities参考_and Tucson_ver… |
| `pub_tables_ar/kitab_tables__426` | pub_tables_ar | 1888.7% | too_long, hit_max_tokens | <h1>تكاليف التدريب والتطوير لكل قسم في النصف الأول من العام</h1> <table> <tr> <… | 绡 Ble правило playground支美味しwcsstore.time By_args carriermiddlewares_args intox… |
| `syn_form_en/syn_form_en_0103` | syn_form_en | 1607.0% | too_long, hit_max_tokens | Customer Information Update Form Full Name: Michael Davis ID Number: 6557685612… | tright Dunk consumerسعىrical churnologia churnstdcallzbekWordsᔕ.slot얖Recognizer… |
| `pub_tables_en/pubtabnet__598044` | pub_tables_en | 1546.8% | repetition, too_long, hit_max_tokens | <table frame="hsides" rules="groups" width="100%"> <thead> <tr> <td> </td> <td>… | ınt双脚rollbackową-cal享誉🤪 plantsރincrease Src accountant/*. This carrier carrier绛… |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
