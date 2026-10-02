# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-02 09:35 · 1051 mẫu · 16 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sherif_handwriting ⚠ chưa đủ | 923/1051 | 19.8% ±2.5 | 21.8% | 31.9% | 36.5% | 0.075 | 1 | 26 (≤4.1%) | 23.52 | 13.0 GB |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | sherif_handwriting |
|---|---:|
| pub_handwriting_ar (128) | 7.2% ±1.4 |
| pub_handwriting_en (63) | 10.9% ±4.3 |
| pub_printed_ar (63) | 41.1% ±12.2 |
| pub_tables_ar (58) | 49.5% ±10.3 |
| pub_tables_en (61) | 46.3% ±14.5 |
| syn_degraded (61) | 40.4% ±20.8 |
| syn_form_ar (60) | 21.8% ±12.2 |
| syn_form_en (72) | 1.9% ±0.8 |
| syn_invoice_ar (57) | 27.5% ±5.0 |
| syn_invoice_en (62) | 2.0% ±1.3 |
| syn_invoice_mixed (57) | 29.0% ±4.6 |
| syn_longtable (61) | — (0/61) |
| syn_longtext (67) | — (0/67) |
| syn_text_ar (60) | 5.2% ±0.6 |
| syn_text_en (57) | 1.0% ±0.4 |
| syn_text_mixed (64) | 11.5% ±4.5 |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | sherif_handwriting |
|---|---:|
| pub_tables_ar | 0.017 / 0.035 |
| pub_tables_en | 0.000 / 0.000 |
| syn_degraded | 0.072 / 0.072 |
| syn_invoice_ar | 0.032 / 0.040 |
| syn_invoice_en | 0.303 / 0.303 |
| syn_invoice_mixed | 0.010 / 0.023 |
| syn_longtable | — / — |

## Tài liệu dài: `syn_longtable`

Ô ghi `ô đúng vị trí / ô đúng sau căn hàng · TEDS`. Hai tỉ lệ đầu chênh nhau nhiều nghĩa là model bỏ sót hoặc thêm hàng, làm mọi giá trị phía sau bị đẩy lệch hàng.

| Độ dài (số mẫu) | sherif_handwriting |
|---|---:|
| 1 trang · 30-45 dòng (21) | — / — · — |
| 2 trang · 60-90 dòng (20) | — / — · — |
| 3 trang · 100-140 dòng (20) | — / — · — |

Độ chính xác theo vị trí trong tài liệu (đầu → cuối), cột cuối là số mẫu bị cắt vì hết `max_new_tokens`, số hàng sai số cột (dấu hiệu dồn cột) và số mẫu đọc sai số hàng:

| Model | Độ dài | Q1 | Q2 | Q3 | Q4 | Bị cắt | Hàng sai số cột | Sai số hàng |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| sherif_handwriting | 1 trang · 30-45 dòng | — | — | — | — | 0 | 0 | 0 |
| sherif_handwriting | 2 trang · 60-90 dòng | — | — | — | — | 0 | 0 | 0 |
| sherif_handwriting | 3 trang · 100-140 dòng | — | — | — | — | 0 | 0 | 0 |

## Tài liệu dài: `syn_longtext`

Ô ghi `CER · độ phủ phần cuối (Q4)`: độ phủ Q4 là tỉ lệ đoạn ở 1/4 cuối tài liệu có mặt trong kết quả.

| Độ dài (số mẫu) | sherif_handwriting |
|---|---:|
| 1 trang · ~4.000 ký tự (36) | — · — |
| 2 trang · ~8.500 ký tự (31) | — · — |

Độ chính xác theo vị trí trong tài liệu (đầu → cuối), cột cuối là số mẫu bị cắt vì hết `max_new_tokens`:

| Model | Độ dài | Q1 | Q2 | Q3 | Q4 | Bị cắt |
|---|---|---:|---:|---:|---:|---:|
| sherif_handwriting | 1 trang · ~4.000 ký tự | — | — | — | — | 0 |
| sherif_handwriting | 2 trang · ~8.500 ký tự | — | — | — | — | 0 |

## 5 mẫu tệ nhất của mỗi model

### sherif_handwriting

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `syn_degraded/syn_degraded_0008` | syn_degraded | 398.4% | too_long, hit_max_tokens | استمارة تسجيل متدرب الاسم الكامل: وليد سعيد الهاشمي رقم الهوية: 2522256181 تاري… | !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!… |
| `syn_degraded/syn_degraded_0034` | syn_degraded | 361.8% | too_long, hit_max_tokens | Leave Request Form Full Name: David Taylor ID Number: 5328682885 Date of Birth:… | !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!… |
| `pub_tables_en/pubtabnet__640391` | pub_tables_en | 358.1% | too_long, hit_max_tokens | <table frame="hsides" rules="groups" width="100%"> <thead> <tr> <td> </td> <td … | Paitients sick listed & Paitients not sick listed & & & & & & & & & & & & & & &… |
| `syn_form_ar/syn_form_ar_0018` | syn_form_ar | 339.1% | too_long, hit_max_tokens | نموذج تحديث بيانات عميل الاسم الكامل: سارة ماجد الشمري رقم الهوية: ٦٤٩٨٨٦٤٧٠٩ ت… | !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!… |
| `syn_degraded/syn_degraded_0091` | syn_degraded | 330.3% | too_long, hit_max_tokens | نموذج طلب إجازة الاسم الكامل: هند منصور القحطاني رقم الهوية: 4969594467 تاريخ ا… | !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!… |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
