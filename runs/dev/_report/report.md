# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-02 03:06 · 923 mẫu · 14 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tesseract | 923/923 | 39.2% ±2.0 | 30.3% | 47.2% | 55.7% | 0.000 | 27 | 0 (≤0.4%) | 1.45 | — |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | tesseract |
|---|---:|
| pub_handwriting_ar (128) | 74.4% ±2.9 |
| pub_handwriting_en (63) | 61.7% ±5.7 |
| pub_printed_ar (63) | 32.1% ±6.4 |
| pub_tables_ar (58) | 52.4% ±4.8 |
| pub_tables_en (61) | 89.6% ±2.3 |
| syn_degraded (61) | 32.2% ±7.5 |
| syn_form_ar (60) | 35.2% ±3.6 |
| syn_form_en (72) | 11.7% ±1.6 |
| syn_invoice_ar (57) | 42.0% ±3.9 |
| syn_invoice_en (62) | 19.1% ±3.2 |
| syn_invoice_mixed (57) | 39.5% ±3.7 |
| syn_text_ar (60) | 7.0% ±0.7 |
| syn_text_en (57) | 1.9% ±0.4 |
| syn_text_mixed (64) | 14.8% ±1.5 |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | tesseract |
|---|---:|
| pub_tables_ar | 0.000 / 0.000 |
| pub_tables_en | 0.000 / 0.000 |
| syn_degraded | 0.000 / 0.000 |
| syn_invoice_ar | 0.000 / 0.000 |
| syn_invoice_en | 0.000 / 0.000 |
| syn_invoice_mixed | 0.000 / 0.000 |

## 5 mẫu tệ nhất của mỗi model

### tesseract

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `pub_handwriting_ar/khatt_lines__6` | pub_handwriting_ar | 113.8% | — | ذهب نوح مظفر ضرغام بصحبة رؤوف بن لؤي رايق ظافر عطعوط وهلال | ١ 9 ‏ووأ‎ WY, gw! ‏2و2 إن رع‎ 0 Vogt CUD wave de #2 ‏بن لو ىرابق‎ 99) Yards Uj?… |
| `pub_handwriting_ar/khatt_lines__40` | pub_handwriting_ar | 103.2% | — | الحج هل تعلم فائده الكلمات التاليه لهذا النص: مشمش، دراق، غيظ ، | bone = CroN 6 24 C22. ‏مسصس‎ ٠ يبهشلا١‎ \| ‏كم زائره العفان المالمه زوز‎ ANS Asx… |
| `pub_handwriting_ar/khatt_lines__92` | pub_handwriting_ar | 101.9% | — | وفي جملة أسباب ضيق جزيرة العرب عن استيعاب العدد الكبير | } Lomo) ( o a * - i ‏يعاب العرر \|الكبير‎ Le ‏الصررهة‎ t's (oe CL \| abe ‏وف‎ |
| `pub_printed_ar/misraj_dococr__08fbb4a3-cb9a-4f2b-b1e3-414b115848f8` | pub_printed_ar | 100.0% | empty | أَنْتِ مَصْدَرُ فَخْرِنا <page_number>63</page_number> |  |
| `pub_printed_ar/misraj_dococr__0bd1eeef-1428-437d-aaef-d55ae9cb7e0b` | pub_printed_ar | 100.0% | empty | سياسةأردوغان: قررنا مع الأمريكيين إقامة مركز **سياسة** القوات الامريكية تشرف عل… |  |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
