"""legalocr — pipeline OCR có kiểm chứng cho hồ sơ pháp lý viết tay / đánh máy tiếng Ả Rập (hợp đồng mua bán đất,
giấy uỷ quyền, Palestine thập niên 1950–1980). Xem legalocr/README.md.

Nguyên tắc: chữ in ra chỉ đến từ model OCR đọc ảnh (bỏ phiếu nhiều model) hoặc từ người duyệt; LLM chỉ GỢI Ý, có
khoá với tên / số / ngày / số tiền / điều khoản; chỗ chưa chắc in [؟] kèm ảnh bằng chứng.
"""
