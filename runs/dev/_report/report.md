# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-02 04:43 · 128 mẫu · 2 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| easyocr | 128/128 | 30.3% ±4.5 | 28.7% | 40.6% | 44.1% | 0.002 | 0 | 0 (≤2.9%) | 15.15 | 13.3 GB |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | easyocr |
|---|---:|
| syn_longtable (61) | 52.3% ±5.1 |
| syn_longtext (67) | 10.3% ±2.3 |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | easyocr |
|---|---:|
| syn_longtable | 0.002 / 0.002 |

## Tài liệu dài: `syn_longtable`

Ô ghi `ô đúng vị trí / ô đúng sau căn hàng · TEDS`. Hai tỉ lệ đầu chênh nhau nhiều nghĩa là model bỏ sót hoặc thêm hàng, làm mọi giá trị phía sau bị đẩy lệch hàng.

| Độ dài (số mẫu) | easyocr |
|---|---:|
| 1 trang · 30-45 dòng (21) | 0% / 0% · 0.00 |
| 2 trang · 60-90 dòng (20) | 0% / 0% · 0.00 |
| 3 trang · 100-140 dòng (20) | 0% / 0% · 0.00 |

Độ chính xác theo vị trí trong tài liệu (đầu → cuối), cột cuối là số mẫu bị cắt vì hết `max_new_tokens`, số hàng sai số cột (dấu hiệu dồn cột) và số mẫu đọc sai số hàng:

| Model | Độ dài | Q1 | Q2 | Q3 | Q4 | Bị cắt | Hàng sai số cột | Sai số hàng |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| easyocr | 1 trang · 30-45 dòng | 0% | 0% | 0% | 0% | 0 | 0 | 21 |
| easyocr | 2 trang · 60-90 dòng | 0% | 0% | 0% | 0% | 0 | 0 | 20 |
| easyocr | 3 trang · 100-140 dòng | 0% | 0% | 0% | 0% | 0 | 0 | 20 |

## Tài liệu dài: `syn_longtext`

Ô ghi `CER · độ phủ phần cuối (Q4)`: độ phủ Q4 là tỉ lệ đoạn ở 1/4 cuối tài liệu có mặt trong kết quả.

| Độ dài (số mẫu) | easyocr |
|---|---:|
| 1 trang · ~4.000 ký tự (36) | 10.3% · 89% |
| 2 trang · ~8.500 ký tự (31) | 10.3% · 89% |

Độ chính xác theo vị trí trong tài liệu (đầu → cuối), cột cuối là số mẫu bị cắt vì hết `max_new_tokens`:

| Model | Độ dài | Q1 | Q2 | Q3 | Q4 | Bị cắt |
|---|---|---:|---:|---:|---:|---:|
| easyocr | 1 trang · ~4.000 ký tự | 89% | 87% | 88% | 89% | 0 |
| easyocr | 2 trang · ~8.500 ký tự | 89% | 88% | 88% | 89% | 0 |

## 5 mẫu tệ nhất của mỗi model

### easyocr

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `syn_longtable/syn_longtable_0111` | syn_longtable | 74.7% | — | <h1>شركة الواحة للأغذية (Summit Engineering Ltd.)</h1> <h2>كشف حساب</h2> <p>الع… | Summit Engineering Ltd ) شركة الواحة للأغذية كشف حساب العميل : مؤسسة الواحة للأ… |
| `syn_longtable/syn_longtable_0002` | syn_longtable | 74.6% | — | <h1>مجموعة النخبة للمقاولات</h1> <h2>قائمة جرد المخزون</h2> <p>العميل: شركة الم… | مجموعة النخبة للمقاولات قائمة جرد المخزون العميل : شركة المستقبل للاستشارات SA8… |
| `syn_longtable/syn_longtable_0071` | syn_longtable | 74.4% | — | <h1>مؤسسة النخبة للمقاولات</h1> <h2>قائمة جرد المخزون</h2> <p>العميل: مؤسسة الن… | مؤسسة النخبة للمقاولات قاثمة جرد المخزون العميل : مؤسسة النخبة للمقاولات $A32 1… |
| `syn_longtable/syn_longtable_0005` | syn_longtable | 73.7% | — | <h1>شركة الواحة للأغذية</h1> <h2>قائمة جرد المخزون</h2> <p>العميل: شركة النور ل… | شركة الواحة للأغذية قائمة جرد المخزون العميل : شركة النور للإلكترونيات SA17 919… |
| `syn_longtable/syn_longtable_0118` | syn_longtable | 73.6% | — | <h1>مؤسسة الفجر للطباعة والنشر</h1> <h2>كشف حساب</h2> <p>العميل: مجموعة البناء … | مؤسسة الفجر للطباعة والنشر كشف حساب العميل : مجموعة البناء الحديث SA25 9017 159… |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
