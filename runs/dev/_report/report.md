# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-07 03:50 · 14 mẫu · 14 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dots_mocr__venv | 14/14 | 9.4% ±7.7 | 7.2% | 21.1% | 17.0% | 0.741 | 0 | 0 (≤21.5%) | 58.08 | 12.4 GB |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | dots_mocr__venv |
|---|---:|
| pub_handwriting_ar (1) | 37.1% |
| pub_handwriting_en (1) | 0.0% |
| pub_printed_ar (1) | 4.3% |
| pub_tables_ar (1) | 34.8% |
| pub_tables_en (1) | 1.3% |
| syn_degraded (1) | 0.2% |
| syn_form_ar (1) | 0.6% |
| syn_form_en (1) | 0.0% |
| syn_invoice_ar (1) | 32.9% |
| syn_invoice_en (1) | 0.0% |
| syn_invoice_mixed (1) | 18.3% |
| syn_text_ar (1) | 1.1% |
| syn_text_en (1) | 0.0% |
| syn_text_mixed (1) | 0.8% |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | dots_mocr__venv |
|---|---:|
| pub_tables_ar | 0.839 / 0.842 |
| pub_tables_en | 0.994 / 1.000 |
| syn_invoice_ar | 0.387 / 1.000 |
| syn_invoice_en | 1.000 / 1.000 |
| syn_invoice_mixed | 0.483 / 1.000 |

## 5 mẫu tệ nhất của mỗi model

### dots_mocr__venv

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `pub_handwriting_ar/khatt_lines__73` | pub_handwriting_ar | 37.1% | — | س ش، ص غ هـ أننا في الحج. هل تعلم فائدة الكلمات التالية لهذا النص: مشمش | سالبًا، هي أنفاغي الحج مع تعليم فائدة العلماء الثالثية لهذا النية: منشئين! |
| `pub_tables_ar/kitab_tables__426` | pub_tables_ar | 34.8% | — | <h1>تكاليف التدريب والتطوير لكل قسم في النصف الأول من العام</h1> <table> <tr> <… | <table><thead><tr><td>القسم</td><td>التكلفة (بالجنيه المصري)</td><td>عدد البرام… |
| `syn_invoice_ar/syn_invoice_ar_0043` | syn_invoice_ar | 32.9% | — | <h1>مجموعة المستقبل للاستشارات</h1> <p>طريق المطار، حي السلامة، القاهرة، جمهوري… | ## مجموعة المستقبل للاستشارات طريق المطار، حي السلامة، القاهرة، جمهورية مصر الع… |
| `syn_invoice_mixed/syn_invoice_mixed_0058` | syn_invoice_mixed | 18.3% | — | <h1>مؤسسة الريادة للتقنية (Gulf Logistics LLC)</h1> <p>شارع التحلية، حي الروضة،… | مؤسسة الريادة للتقنية (Gulf Logistics LLC) شارع التحلية، حي الروضة، الكويت، دول… |
| `pub_printed_ar/misraj_dococr__8d18a279-ce9a-451b-82c3-3541ae3349f5` | pub_printed_ar | 4.3% | — | افضل خدمة سيارات **رانجلر** امن وخالي من الجهاد لراحتك: الخدمة الجيدة لا تجعل *… | أفضل خدمة سيارات وانجلر من وخالي من الجهاد لراحتك: الخدمة الجيدة لا تجعل وانجلر… |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
