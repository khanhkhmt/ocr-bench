# Nhật ký điều khiển server

- 2026-10-09 06:28 UTC — Dừng benchmark n500 (ketaba 4-bit dừng ở ~240/500 Omar, ~25 s/dòng). Chạy chẩn đoán Ketaba 32 dòng: fp16:1:q4 vs fp16:1:fp16 (tmux htr_cd, log /kaggle/working/htr_chan_doan_ketaba.log).
- 2026-10-09 07:04 UTC — Chẩn đoán Ketaba: q4 (4-bit, như tác giả) 32 dòng = 91,0% đúng ký tự, 33,7 s/dòng, 0 dòng sót/lặp. Cấu hình fp16 lỗi ImportError torchao (peft + torchao 0.10 của Colab) → sửa code (4380c7f, vá kiểm tra torchao), pull, chạy lại riêng fp16 (tmux htr_cd).
