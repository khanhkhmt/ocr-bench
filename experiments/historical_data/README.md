# Gom dữ liệu giống giấy tờ cũ của khách

`fetch.py <thư mục đích> [nguồn ...]` tải và sắp xếp mỗi mẫu thành `<nguồn>/<mẫu>/input/` (ảnh) +
`<nguồn>/<mẫu>/output/nhan.txt` (nhãn thật), kèm `danh_sach.csv` và `NGUON.md`. Chạy lại = bỏ qua mẫu đã có;
dừng khi ổ còn < 1 GB. Dữ liệu để NGOÀI repo (mặc định đã dùng: `~/du_lieu_giay_to_cu`).
Nguồn: muharaf_trang, kitab_historyar, kitab_historicalbooks, khatt_doan, churro_ar_he (dev+test), churro_ottoman, madinah.
