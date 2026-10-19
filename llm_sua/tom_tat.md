# LLM sửa lỗi OCR — 4 trang mẫu

Cập nhật 2026-10-19 09:34 UTC. Điểm = % ký tự đúng / % từ đúng (mã chấm của arabic-doc-ocr `scripts/evaluate.py`, văn bản chính). Nhãn chỉ dùng để chấm, không đưa vào LLM.

Loại trang: page_1 = đánh máy, page_2 = viết tay, page_3 = đánh máy, page_4 = đánh máy

| model | cách | page_1 | page_2 | page_3 | page_4 | sửa đúng | làm hỏng | không rõ | bị luật chặn | giây |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| — | khong | 90.3 / 70.1 | 72.2 / 46.5 | 79.0 / 44.0 | 90.9 / 70.9 | 0 | 0 | 0 | 0 | 0 |
| — | tran_chon | 91.4 / 75.0 (+1.1 / +4.9) | 74.5 / 51.8 (+2.2 / +5.3) | 80.5 / 51.5 (+1.5 / +7.5) | 92.8 / 79.1 (+1.8 / +8.1) | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-7b | chon | 90.3 / 74.5 (+0.1 / +4.3) | 75.0 / 51.4 (+2.8 / +5.0) | 80.0 / 48.8 (+1.1 / +4.8) | 92.6 / 77.9 (+1.6 / +7.0) | 44 | 8 | 32 | 0 | 32 |
| qwen2.5-7b | sua | 90.6 / 74.5 (+0.4 / +4.3) | 72.2 / 46.8 (-0.1 / +0.4) | 79.3 / 47.0 (+0.3 / +3.0) | 92.2 / 77.9 (+1.2 / +7.0) | 26 | 0 | 25 | 19 | 195 |
| qwen2.5-7b | chon_sua | 91.1 / 77.2 (+0.8 / +7.1) | 75.0 / 51.4 (+2.8 / +5.0) | 80.2 / 50.8 (+1.2 / +6.8) | 93.0 / 80.2 (+2.0 / +9.3) | 60 | 10 | 47 | 13 | 233 |
| qwen3-8b | chon | 90.6 / 73.9 (+0.4 / +3.8) | 74.7 / 50.7 (+2.4 / +4.3) | 80.1 / 49.0 (+1.1 / +5.0) | 91.5 / 76.7 (+0.6 / +5.8) | 43 | 9 | 34 | 0 | 37 |
| qwen3-8b | sua | 90.3 / 71.2 (+0.1 / +1.1) | 72.4 / 47.2 (+0.1 / +0.7) | 79.1 / 44.5 (+0.1 / +0.5) | 92.6 / 79.1 (+1.6 / +8.1) | 14 | 0 | 6 | 23 | 239 |
| qwen3-8b | chon_sua | 90.8 / 75.0 (+0.6 / +4.9) | 74.5 / 50.7 (+2.3 / +4.3) | 80.3 / 50.0 (+1.3 / +6.0) | 92.2 / 80.2 (+1.2 / +9.3) | 52 | 9 | 35 | 12 | 270 |
| allam-7b | chon | 90.3 / 73.9 (+0.1 / +3.8) | 74.9 / 50.7 (+2.6 / +4.3) | 80.4 / 50.0 (+1.4 / +6.0) | 92.0 / 77.9 (+1.0 / +7.0) | 46 | 9 | 29 | 0 | 26 |
| allam-7b | sua | 92.5 / 79.3 (+2.2 / +9.2) | 72.6 / 47.9 (+0.3 / +1.4) | 80.9 / 55.2 (+1.9 / +11.3) | 92.4 / 79.1 (+1.4 / +8.1) | 79 | 6 | 27 | 90 | 103 |
| allam-7b | chon_sua | 91.4 / 77.7 (+1.1 / +7.6) | 75.1 / 51.8 (+2.9 / +5.3) | 81.4 / 55.0 (+2.4 / +11.0) | 92.0 / 79.1 (+1.0 / +8.1) | 87 | 17 | 42 | 57 | 124 |
| qwen3.5-9b | chon | 90.3 / 73.4 (+0.0 / +3.3) | 75.0 / 51.4 (+2.8 / +5.0) | 80.1 / 48.8 (+1.1 / +4.8) | 93.0 / 79.1 (+2.0 / +8.1) | 44 | 9 | 31 | 0 | 135 |
| qwen3.5-9b | sua | 92.0 / 77.7 (+1.8 / +7.6) | 72.2 / 46.8 (-0.1 / +0.4) | 81.0 / 55.5 (+2.0 / +11.5) | 93.0 / 79.1 (+2.0 / +8.1) | 72 | 3 | 29 | 50 | 211 |
| qwen3.5-9b | chon_sua | 91.4 / 78.3 (+1.1 / +8.2) | 75.2 / 51.8 (+3.0 / +5.3) | 81.2 / 55.5 (+2.2 / +11.5) | 94.0 / 83.7 (+3.0 / +12.8) | 89 | 12 | 56 | 37 | 289 |

`khong` = chưa sửa · `tran_chon` = mức tối đa của cách `chon` (dùng nhãn, không phải cách sửa).

## Kết luận theo luật cố định

ĐẠT = từ đúng tăng ≥ 2 điểm (trung bình), không trang nào giảm ký tự đúng quá 0,3 điểm, làm hỏng ≤ 1/4 sửa đúng.

| model | cách | đánh máy | viết tay |
|---|---|---|---|
| qwen2.5-7b | chon | ĐẠT (từ +5.4 · ký tự tệ nhất +0.1 · sửa đúng 33 / làm hỏng 7) | ĐẠT (từ +5.0 · ký tự tệ nhất +2.8 · sửa đúng 11 / làm hỏng 1) |
| qwen2.5-7b | sua | ĐẠT (từ +4.8 · ký tự tệ nhất +0.3 · sửa đúng 26 / làm hỏng 0) | không đạt (từ +0.4 · ký tự tệ nhất -0.1 · sửa đúng 0 / làm hỏng 0) |
| qwen2.5-7b | chon_sua | ĐẠT (từ +7.7 · ký tự tệ nhất +0.8 · sửa đúng 49 / làm hỏng 8) | ĐẠT (từ +5.0 · ký tự tệ nhất +2.8 · sửa đúng 11 / làm hỏng 2) |
| qwen3-8b | chon | ĐẠT (từ +4.9 · ký tự tệ nhất +0.4 · sửa đúng 33 / làm hỏng 7) | ĐẠT (từ +4.3 · ký tự tệ nhất +2.4 · sửa đúng 10 / làm hỏng 2) |
| qwen3-8b | sua | ĐẠT (từ +3.2 · ký tự tệ nhất +0.1 · sửa đúng 11 / làm hỏng 0) | không đạt (từ +0.7 · ký tự tệ nhất +0.1 · sửa đúng 3 / làm hỏng 0) |
| qwen3-8b | chon_sua | ĐẠT (từ +6.7 · ký tự tệ nhất +0.6 · sửa đúng 42 / làm hỏng 7) | ĐẠT (từ +4.3 · ký tự tệ nhất +2.3 · sửa đúng 10 / làm hỏng 2) |
| allam-7b | chon | ĐẠT (từ +5.6 · ký tự tệ nhất +0.1 · sửa đúng 36 / làm hỏng 7) | ĐẠT (từ +4.3 · ký tự tệ nhất +2.6 · sửa đúng 10 / làm hỏng 2) |
| allam-7b | sua | ĐẠT (từ +9.5 · ký tự tệ nhất +1.4 · sửa đúng 75 / làm hỏng 6) | không đạt (từ +1.4 · ký tự tệ nhất +0.3 · sửa đúng 4 / làm hỏng 0) |
| allam-7b | chon_sua | ĐẠT (từ +8.9 · ký tự tệ nhất +1.0 · sửa đúng 73 / làm hỏng 15) | ĐẠT (từ +5.3 · ký tự tệ nhất +2.9 · sửa đúng 14 / làm hỏng 2) |
| qwen3.5-9b | chon | ĐẠT (từ +5.4 · ký tự tệ nhất +0.0 · sửa đúng 33 / làm hỏng 8) | ĐẠT (từ +5.0 · ký tự tệ nhất +2.8 · sửa đúng 11 / làm hỏng 1) |
| qwen3.5-9b | sua | ĐẠT (từ +9.1 · ký tự tệ nhất +1.8 · sửa đúng 70 / làm hỏng 2) | không đạt (từ +0.4 · ký tự tệ nhất -0.1 · sửa đúng 2 / làm hỏng 1) |
| qwen3.5-9b | chon_sua | ĐẠT (từ +10.8 · ký tự tệ nhất +1.1 · sửa đúng 77 / làm hỏng 10) | ĐẠT (từ +5.3 · ký tự tệ nhất +3.0 · sửa đúng 12 / làm hỏng 2) |

## Model không chạy được

- **gemma4-12b**: OSError: [Errno 30] Read-only file system: '/tmp/llm_sua_cache/models--google--gemma-4-12B-it/blobs/5a84cb313260ac447237b890387116dfa8682e49a6b44bc585ae8353abbff18d.9f709b67.incomplete'

Chi tiết từng từ bị đổi: `chi_tiet.csv`.
