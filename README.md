# Dữ liệu thật — 4 trang mẫu (chấm thử cả trang)

`real_docs_nhan/image_*/`: `anh.jpeg` (ảnh gốc) + `nhan.json` (nhãn người dùng gán) + `nhan_claude.json` (nhãn Claude đọc
từ ảnh). `SO_SANH.md`: các chỗ hai nhãn lệch nhau — cần người đọc tiếng Ả Rập chốt. image_4 (công văn Ai Cập, watermark
اليوم السابع) không phải giấy tờ của khách — chỉ tham khảo phần đánh máy.

Chấm: `python -m htr_test.cham_trang --data <đường dẫn>/real_docs_nhan --out <thư mục> --push` (nhánh code thu-2-model-htr).
