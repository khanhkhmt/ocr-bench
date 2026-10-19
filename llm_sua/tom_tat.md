# LLM sửa lỗi OCR — 4 trang mẫu

Cập nhật 2026-10-19 09:01 UTC. Điểm = % ký tự đúng / % từ đúng (mã chấm của arabic-doc-ocr `scripts/evaluate.py`, văn bản chính). Nhãn chỉ dùng để chấm, không đưa vào LLM.

Loại trang: page_1 = đánh máy, page_2 = viết tay, page_3 = đánh máy, page_4 = đánh máy

| model | cách | page_1 | page_2 | page_3 | page_4 | sửa đúng | làm hỏng | không rõ | bị luật chặn | giây |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| — | khong | 90.3 / 70.1 | 72.2 / 46.5 | 79.0 / 44.0 | 90.9 / 70.9 | 0 | 0 | 0 | 0 | 0 |
| — | tran_chon | 91.4 / 75.0 (+1.1 / +4.9) | 74.5 / 51.8 (+2.2 / +5.3) | 80.5 / 51.5 (+1.5 / +7.5) | 92.8 / 79.1 (+1.8 / +8.1) | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-7b | chon | 90.3 / 74.5 (+0.1 / +4.3) | 75.0 / 51.4 (+2.8 / +5.0) | 80.0 / 48.8 (+1.1 / +4.8) | 92.6 / 77.9 (+1.6 / +7.0) | 44 | 8 | 32 | 0 | 32 |
| qwen2.5-7b | sua | 90.6 / 74.5 (+0.4 / +4.3) | 72.2 / 46.8 (-0.1 / +0.4) | 79.3 / 47.0 (+0.3 / +3.0) | 92.2 / 77.9 (+1.2 / +7.0) | 26 | 0 | 25 | 19 | 195 |
| qwen2.5-7b | chon_sua | 91.1 / 77.2 (+0.8 / +7.1) | 75.0 / 51.4 (+2.8 / +5.0) | 80.2 / 50.8 (+1.2 / +6.8) | 93.0 / 80.2 (+2.0 / +9.3) | 60 | 10 | 47 | 13 | 233 |

`khong` = chưa sửa · `tran_chon` = mức tối đa của cách `chon` (dùng nhãn, không phải cách sửa).

## Kết luận theo luật cố định

ĐẠT = từ đúng tăng ≥ 2 điểm (trung bình), không trang nào giảm ký tự đúng quá 0,3 điểm, làm hỏng ≤ 1/4 sửa đúng.

| model | cách | đánh máy | viết tay |
|---|---|---|---|
| qwen2.5-7b | chon | ĐẠT (từ +5.4 · ký tự tệ nhất +0.1 · sửa đúng 33 / làm hỏng 7) | ĐẠT (từ +5.0 · ký tự tệ nhất +2.8 · sửa đúng 11 / làm hỏng 1) |
| qwen2.5-7b | sua | ĐẠT (từ +4.8 · ký tự tệ nhất +0.3 · sửa đúng 26 / làm hỏng 0) | không đạt (từ +0.4 · ký tự tệ nhất -0.1 · sửa đúng 0 / làm hỏng 0) |
| qwen2.5-7b | chon_sua | ĐẠT (từ +7.7 · ký tự tệ nhất +0.8 · sửa đúng 49 / làm hỏng 8) | ĐẠT (từ +5.0 · ký tự tệ nhất +2.8 · sửa đúng 11 / làm hỏng 2) |

Chi tiết từng từ bị đổi: `chi_tiet.csv`.
