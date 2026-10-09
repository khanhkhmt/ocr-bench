# Nhật ký điều khiển server

- 2026-10-09 06:28 UTC — Dừng benchmark n500 (ketaba 4-bit dừng ở ~240/500 Omar, ~25 s/dòng). Chạy chẩn đoán Ketaba 32 dòng: fp16:1:q4 vs fp16:1:fp16 (tmux htr_cd, log /kaggle/working/htr_chan_doan_ketaba.log).
- 2026-10-09 07:04 UTC — Chẩn đoán Ketaba: q4 (4-bit, như tác giả) 32 dòng = 91,0% đúng ký tự, 33,7 s/dòng, 0 dòng sót/lặp. Cấu hình fp16 lỗi ImportError torchao (peft + torchao 0.10 của Colab) → sửa code (4380c7f, vá kiểm tra torchao), pull, chạy lại riêng fp16 (tmux htr_cd).
- 2026-10-09 07:41 UTC — Chẩn đoán Ketaba nền fp16: 85,6% (q4: 91,0%), 32 s/dòng — kém hơn, không nhanh hơn → giữ q4. Chạy benchmark --tag n500 --models dots,ketaba --datasets muharaf,omar (dots trước làm mốc; ketaba tiếp tục từ 240/500 Omar).
- 2026-10-09 08:12 UTC — ~14:50–14:55 Colab ngắt (không còn trạng thái sau 14:47, kết quả cuối 14:53: dots×Muharaf 240/500; ngrok 6.tcp.ngrok.io:18183 từ chối). Viết htr_test/khoi_phuc.sh để dựng lại bằng một lệnh. Chờ người dùng mở lại Colab + gửi địa chỉ ngrok mới.
- 2026-10-09 09:33 UTC — Server vẫn ngắt (từ ~14:50). Làm htr_test/danh_dau.py (tô vàng + chú thích chữ đáng ngờ trong DOCX, 3b17057); thêm chủ đề nghiên cứu 9–12.
