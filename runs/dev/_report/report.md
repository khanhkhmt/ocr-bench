# Kết quả OCR benchmark — split `dev`

Tạo lúc 2026-10-02 03:36 · 128 mẫu · 2 nhóm · 1 model · manifest `/kaggle/working/testset/manifest.jsonl`

## Tổng quan

| Model | Mẫu | CER (norm) ±95% | CER micro | CER raw | WER | TEDS bảng | Lỗi/rỗng | Lặp/thừa (trần 95%) | s/mẫu | VRAM đỉnh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tesseract | 128/128 | 27.6% ±5.7 | 26.3% | 38.1% | 35.3% | 0.000 | 0 | 1 (≤4.3%) | 11.99 | — |

## CER (norm) theo nhóm — thấp hơn là tốt hơn

| Nhóm (số mẫu) | tesseract |
|---|---:|
| syn_longtable (61) | 54.7% ±7.4 |
| syn_longtext (67) | 3.0% ±0.7 |

## TEDS theo nhóm có bảng — cao hơn là tốt hơn (1.0 = khớp hoàn toàn)

Ô ghi `nội dung / cấu trúc`: TEDS đầy đủ và TEDS chỉ xét cấu trúc hàng-cột.

| Nhóm | tesseract |
|---|---:|
| syn_longtable | 0.000 / 0.000 |

## Tài liệu dài: `syn_longtable`

Ô ghi `ô đúng vị trí / ô đúng sau căn hàng · TEDS`. Hai tỉ lệ đầu chênh nhau nhiều nghĩa là model bỏ sót hoặc thêm hàng, làm mọi giá trị phía sau bị đẩy lệch hàng.

| Độ dài (số mẫu) | tesseract |
|---|---:|
| 1 trang · 30-45 dòng (21) | 0% / 0% · 0.00 |
| 2 trang · 60-90 dòng (20) | 0% / 0% · 0.00 |
| 3 trang · 100-140 dòng (20) | 0% / 0% · 0.00 |

Độ chính xác theo vị trí trong tài liệu (đầu → cuối), cột cuối là số mẫu bị cắt vì hết `max_new_tokens`, số hàng sai số cột (dấu hiệu dồn cột) và số mẫu đọc sai số hàng:

| Model | Độ dài | Q1 | Q2 | Q3 | Q4 | Bị cắt | Hàng sai số cột | Sai số hàng |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| tesseract | 1 trang · 30-45 dòng | 0% | 0% | 0% | 0% | 0 | 0 | 21 |
| tesseract | 2 trang · 60-90 dòng | 0% | 0% | 0% | 0% | 0 | 0 | 20 |
| tesseract | 3 trang · 100-140 dòng | 0% | 0% | 0% | 0% | 0 | 0 | 20 |

## Tài liệu dài: `syn_longtext`

Ô ghi `CER · độ phủ phần cuối (Q4)`: độ phủ Q4 là tỉ lệ đoạn ở 1/4 cuối tài liệu có mặt trong kết quả.

| Độ dài (số mẫu) | tesseract |
|---|---:|
| 1 trang · ~4.000 ký tự (36) | 2.8% · 96% |
| 2 trang · ~8.500 ký tự (31) | 3.2% · 97% |

Độ chính xác theo vị trí trong tài liệu (đầu → cuối), cột cuối là số mẫu bị cắt vì hết `max_new_tokens`:

| Model | Độ dài | Q1 | Q2 | Q3 | Q4 | Bị cắt |
|---|---|---:|---:|---:|---:|---:|
| tesseract | 1 trang · ~4.000 ký tự | 95% | 97% | 95% | 96% | 0 |
| tesseract | 2 trang · ~8.500 ký tự | 96% | 95% | 94% | 97% | 0 |

## 5 mẫu tệ nhất của mỗi model

### tesseract

| id | nhóm | CER | cờ | đáp án (đầu) | model đọc (đầu) |
|---|---|---:|---|---|---|
| `syn_longtable/syn_longtable_0057` | syn_longtable | 82.1% | — | <h1>Summit Engineering Ltd.</h1> <h2>Account Statement</h2> <p>Customer: Modern… | Balance 70,182.35 68,144.70 65,204.93 62,657.58 63,540.44 60,830.33 60,020.47 6… |
| `syn_longtable/syn_longtable_0020` | syn_longtable | 80.8% | repetition | <h1>شركة النخبة للمقاولات (Northwind Electronics Ltd.)</h1> <h2>كشف حساب</h2> <… | 0 (Northwind Electronics Ltd.) oYolid Lu! 45,4 lus ais (Northwind Electronics I… |
| `syn_longtable/syn_longtable_0009` | syn_longtable | 80.7% | — | <h1>شركة النور للإلكترونيات</h1> <h2>قائمة جرد المخزون</h2> <p>العميل: شركة الر… | العميل: شركة الريادة للتقنية رقم الحساب: 8890 6495 5962 5096 الفترة: هن -/1:/لا… |
| `syn_longtable/syn_longtable_0085` | syn_longtable | 80.6% | — | <h1>مؤسسة الفجر للطباعة والنشر (Gulf Logistics Group)</h1> <h2>كشف حساب</h2> <p… | مؤسسة الفجر للطباعة والنشر ‎(Gulf Logistics Group)‏ كشف حساب العميل: مؤسسة الأف… |
| `syn_longtable/syn_longtable_0091` | syn_longtable | 80.6% | — | <h1>مجموعة النخبة للمقاولات (Future Consulting Group)</h1> <h2>كشف حساب</h2> <p… | (Future Consulting Group) GiigLaol! GAill Gcgnao كشف حساب العميل: شركة الريادة … |

## Cách đọc

Giải thích đầy đủ, kèm ví dụ: `docs/METRICS.md` trong thư mục code của tool.

- **CER (norm)**: tỉ lệ lỗi ký tự sau khi chuẩn hóa (mục `normalization` trong config), trung bình theo từng mẫu, kèm khoảng tin cậy 95%. Có thể > 100% khi model sinh thừa nhiều chữ.
- **CER micro**: tổng số lỗi / tổng số ký tự của cả bộ (trang dài có trọng số lớn hơn).
- **CER raw**: không chuẩn hóa; chênh lệch lớn so với CER norm thường do định dạng (Markdown, tashkeel...).
- **Lỗi/rỗng**: model báo lỗi hoặc trả về chuỗi rỗng. **Lặp/thừa**: kẹt vòng lặp hoặc dài hơn đáp án >1,5 lần (dấu hiệu bịa chữ); số trong ngoặc là cận trên 95% của tỉ lệ thật.
- **s/mẫu** và **VRAM đỉnh** chỉ để tham khảo; hai model chạy song song trên hai GPU không ảnh hưởng nhau, nhưng dùng chung CPU và ổ đĩa.
- Model có ⚠ chưa chạy hết bộ dữ liệu nên không so sánh trực tiếp được với các model khác.
- **Tài liệu dài**: *ô đúng vị trí* yêu cầu đúng cả giá trị lẫn hàng/cột; *ô đúng sau căn hàng* bỏ qua việc thiếu/thừa hàng. Q1→Q4 là độ chính xác theo vị trí trong tài liệu; tụt dần về Q4 nghĩa là model mất ngữ cảnh hoặc bị cắt khi tài liệu dài. Mẫu *bị cắt* cần tăng `max_new_tokens`.
