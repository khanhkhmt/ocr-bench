# LLM sửa lỗi OCR — 4 trang mẫu

Cập nhật 2026-10-19 08:49 UTC. Điểm = % ký tự đúng / % từ đúng (mã chấm của arabic-doc-ocr `scripts/evaluate.py`, văn bản chính). Nhãn chỉ dùng để chấm, không đưa vào LLM.

Loại trang: page_4 = đánh máy

| model | cách | page_4 | sửa đúng | làm hỏng | không rõ | bị luật chặn | giây |
|---|---|---:|---:|---:|---:|---:|---:|
| — | khong | 90.9 / 70.9 | 0 | 0 | 0 | 0 | 0 |
| — | tran_chon | 92.8 / 79.1 (+1.8 / +8.1) | 0 | 0 | 0 | 0 | 0 |
| nho | chon | 91.5 / 75.6 (+0.6 / +4.7) | 4 | 1 | 1 | 0 | 2 |
| nho | sua | 90.7 / 70.9 (-0.2 / +0.0) | 3 | 3 | 0 | 7 | 11 |
| nho | chon_sua | 91.1 / 74.4 (+0.2 / +3.5) | 6 | 4 | 1 | 7 | 12 |

`khong` = chưa sửa · `tran_chon` = mức tối đa của cách `chon` (dùng nhãn, không phải cách sửa).

## Kết luận theo luật cố định

ĐẠT = từ đúng tăng ≥ 2 điểm (trung bình), không trang nào giảm ký tự đúng quá 0,3 điểm, làm hỏng ≤ 1/4 sửa đúng.

| model | cách | đánh máy | viết tay |
|---|---|---|---|
| nho | chon | ĐẠT (từ +4.7 · ký tự tệ nhất +0.6 · sửa đúng 4 / làm hỏng 1) | chưa đủ trang |
| nho | sua | không đạt (từ +0.0 · ký tự tệ nhất -0.2 · sửa đúng 3 / làm hỏng 3) | chưa đủ trang |
| nho | chon_sua | không đạt (từ +3.5 · ký tự tệ nhất +0.2 · sửa đúng 6 / làm hỏng 4) | chưa đủ trang |

Chi tiết từng từ bị đổi: `chi_tiet.csv`.
