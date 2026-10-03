# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-03 11:09 · 24 mẫu · 2 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sherif_handwriting__sl__long | 24/24 | 59.3% ±29.6 | 68.2% | 62.3% | 68.3% | 0.081 | 5 | 4 (≤35.9%) | 366.44 | 0.0 GB |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | sherif_handwriting__sl__long |
|---|---:|
| syn_longtable (12) | 82.6% ±51.7 |
| syn_longtext (12) | 36.1% ±25.0 |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | sherif_handwriting__sl__long |
|---|---:|
| syn_longtable | 0.081 / 0.081 |

## Tài liệu dài: `syn_longtable`

Ô ghi `ô đúng vị trí / ô đúng sau căn hàng · TEDS`. Hai tỉ lệ đầu chênh nhau nhiều nghĩa là model bỏ sót hoặc thêm hàng, làm mọi giá trị phía sau bị đẩy lệch hàng.

| Độ dài (số mẫu) | sherif_handwriting__sl__long |
|---|---:|
| 1 trang · 30-45 dòng (5) | 1% / 20% · 0.20 |
| 2 trang · 60-90 dòng (5) | 0% / 0% · 0.00 |
| 3 trang · 100-140 dòng (2) | 0% / 0% · 0.00 |

Độ chính xác theo vị trí trong tài liệu (đầu → cuối), cột cuối là số mẫu bị cắt vì hết `max_new_tokens`, số hàng sai số cột (dấu hiệu dồn cột) và số mẫu đọc sai số hàng:

| Model | Độ dài | Q1 | Q2 | Q3 | Q4 | Bị cắt | Hàng sai số cột | Sai số hàng |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| sherif_handwriting__sl__long | 1 trang · 30-45 dòng | 18% | 20% | 20% | 20% | 0 | 0 | 5 |
| sherif_handwriting__sl__long | 2 trang · 60-90 dòng | 0% | 0% | 0% | 0% | 2 | 0 | 5 |
| sherif_handwriting__sl__long | 3 trang · 100-140 dòng | 0% | 0% | 0% | 0% | 0 | 0 | 2 |

## Tài liệu dài: `syn_longtext`

Ô ghi `CER · độ phủ phần cuối (Q4)`: độ phủ Q4 là tỉ lệ đoạn ở 1/4 cuối tài liệu có mặt trong kết quả.

| Độ dài (số mẫu) | sherif_handwriting__sl__long |
|---|---:|
| 1 trang · ~4.000 ký tự (6) | 3.9% · 90% |
| 2 trang · ~8.500 ký tự (6) | 68.3% · 53% |

Độ chính xác theo vị trí trong tài liệu (đầu → cuối), cột cuối là số mẫu bị cắt vì hết `max_new_tokens`:

| Model | Độ dài | Q1 | Q2 | Q3 | Q4 | Bị cắt |
|---|---|---:|---:|---:|---:|---:|
| sherif_handwriting__sl__long | 1 trang · ~4.000 ký tự | 100% | 99% | 96% | 90% | 0 |
| sherif_handwriting__sl__long | 2 trang · ~8.500 ký tự | 44% | 44% | 56% | 53% | 1 |

## 5 mẫu tệ nhất của mỗi model

### sherif_handwriting__sl__long

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `syn_longtable/syn_longtable_0022` | syn_longtable | 329.2% | repetition, too_long, hit_max_tokens | <h1>شركة النور للإلكترونيات</h1> <h2>كشف حساب</h2> <p>العميل: شركة الرواد للأنظ… | شركة النور لإلكترونيات كشف حساب العميل : شركة الرواد للأنظمة الذكية رقم الحساب … |
| `syn_longtable/syn_longtable_0106` | syn_longtable | 123.3% | too_long, hit_max_tokens | <h1>شركة الأمانة للتأمين (Trust Insurance Inc.)</h1> <h2>كشف حساب</h2> <p>العمي… | شركة الأمانة للتأمين (Trust Insurance Inc.) كشف حساب العمل: مجموعة البناء الحدي… |
| `syn_longtext/syn_longtext_0037` | syn_longtext | 108.6% | too_long, hit_max_tokens | زين الدين زيدان زين الدين يزيد زيدان (؛ مواليد 22 يونيو 1972) المعروف شعبيا باس… | زين الدين زيدان ذهب زيدن إلى نادي كان لمدة ستة أسابيع، لكنه انتهى به الأمر بالب… |
| `syn_longtable/syn_longtable_0034` | syn_longtable | 100.0% | error | <h1>مجموعة المستقبل للاستشارات (Summit Engineering Group)</h1> <h2>قائمة جرد ال… | OutOfMemoryError: CUDA out of memory. Tried to allocate 4.64 GiB. GPU 0 has a t… |
| `syn_longtable/syn_longtable_0059` | syn_longtable | 100.0% | error | <h1>Crescent Printing Inc.</h1> <h2>Inventory List</h2> <p>Customer: Trust Insu… | OutOfMemoryError: CUDA out of memory. Tried to allocate 7.12 GiB. GPU 0 has a t… |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
