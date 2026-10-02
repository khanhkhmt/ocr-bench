# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-02 02:43 · 14 mẫu · 14 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tesseract | 14/14 | 39.6% ±18.3 | 28.3% | 45.2% | 52.0% | 0.000 | 1 | 0 (≤21.5%) | 1.65 | — |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | tesseract |
|---|---:|
| pub_handwriting_ar (1) | 52.9% |
| pub_handwriting_en (1) | 100.0% |
| pub_printed_ar (1) | 28.9% |
| pub_tables_ar (1) | 74.2% |
| pub_tables_en (1) | 97.4% |
| syn_degraded (1) | 3.6% |
| syn_form_ar (1) | 18.8% |
| syn_form_en (1) | 15.2% |
| syn_invoice_ar (1) | 61.5% |
| syn_invoice_en (1) | 21.2% |
| syn_invoice_mixed (1) | 65.5% |
| syn_text_ar (1) | 5.6% |
| syn_text_en (1) | 0.7% |
| syn_text_mixed (1) | 9.3% |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | tesseract |
|---|---:|
| pub_tables_ar | 0.000 / 0.000 |
| pub_tables_en | 0.000 / 0.000 |
| syn_invoice_ar | 0.000 / 0.000 |
| syn_invoice_en | 0.000 / 0.000 |
| syn_invoice_mixed | 0.000 / 0.000 |

## 5 mẫu tệ nhất của mỗi model

### tesseract

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `pub_handwriting_en/iam_lines__66` | pub_handwriting_en | 100.0% | empty | The question and answer with regard to the |  |
| `pub_tables_en/pubtabnet__598044` | pub_tables_en | 97.4% | too_short | <table frame="hsides" rules="groups" width="100%"> <thead> <tr> <td> </td> <td>… | ‎YAS men)‏ ممه مامد |
| `pub_tables_ar/kitab_tables__426` | pub_tables_ar | 74.2% | too_short | <h1>تكاليف التدريب والتطوير لكل قسم في النصف الأول من العام</h1> <table> <tr> <… | تكاليف التدريب والتطوير لكل قسم في النصف الأول من العام 031110100 rend (eee ren… |
| `syn_invoice_mixed/syn_invoice_mixed_0058` | syn_invoice_mixed | 65.5% | — | <h1>مؤسسة الريادة للتقنية (Gulf Logistics LLC)</h1> <p>شارع التحلية، حي الروضة،… | 0 مؤسسة الريادة للتقنية (0ئآنآ دعتاكنهمآ علدده) شارع التحلية» سي الروضة» الكويت… |
| `syn_invoice_ar/syn_invoice_ar_0043` | syn_invoice_ar | 61.5% | — | <h1>مجموعة المستقبل للاستشارات</h1> <p>طريق المطار، حي السلامة، القاهرة، جمهوري… | مجموعة المستقبل للاستشارات طريق المطار, حي السلامة, القاهرة, جمهورية مصر العربي… |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
