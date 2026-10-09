# Kế hoạch — benchmark đọc dòng chữ viết tay (cập nhật mỗi lần kiểm tra)

Người điều khiển: Claude (phiên Claude Code trên máy người dùng), kiểm tra mỗi ~20 phút: đọc trang_thai/STATUS.md,
SSH vào server (`ssh colab`) để làm trực tiếp; mọi việc đã làm ghi vào nhat_ky.md. Agent trên server chỉ là dự phòng
(đọc lenh/PROMPT.md qua /kaggle/working/hop_thu/PROMPT_MOI.md).

## Mục tiêu
Bảng BENCHMARK_HTR.md: % đúng ký tự của baseer, ketaba (hoặc ketaba16), dots × 2 bộ (Omar blind_test, Muharaf test),
500 dòng ngẫu nhiên cố định mỗi bộ (--tag n500). Kết quả: nhánh results-htr/htr_benchmark_n500/.

## Đã có (2026-10-09 06:30 UTC)
- baseer: Omar 93,3% · Muharaf 79,1% (500/500 mỗi bộ, lô 1)
- ketaba (4-bit, như tác giả): Omar 93,4% trên 240/500 — chạy ~25 s/dòng (bitsandbytes: "inner dimension not aligned
  for fast kernel → slower implementation")

## Các bước
1. [đang làm] Chẩn đoán Ketaba 32 dòng. q4 XONG: 91,0% đúng ký tự, 33,7 s/dòng, 0 sót/lặp. fp16 đang chạy lại
   (tmux htr_cd, kết quả /kaggle/working/htr_chan_doan_ketaba_fp16.md) sau khi sửa lỗi torchao (commit 4380c7f).
   14:12: fp16 vẫn chạy sau 9 phút → cũng chậm (DoRA tính lại chuẩn mỗi bước). Khi có số: áp quy tắc bước 2, VÀ chọn
   bản nhanh hơn trong hai bản đạt chuẩn.
2. Quy tắc (so với q4 = 91,0%): nếu fp16 ≥ 90,5% đúng ký tự VÀ dòng dài/ngắn không nhiều hơn → benchmark --tag n500 --n 500
   --models ketaba16,dots --push. Ngược lại → --models ketaba,dots (chậm, ~6 giờ).
3. Khi "XONG TẤT CẢ": kiểm tra htr_benchmark_n500/BENCHMARK_HTR.md trên GitHub, báo người dùng.

## Luật cứng
Token chỉ qua biến môi trường/header, không in · không pkill -f, chỉ dừng phiên do mình mở · không cài/gỡ torch/CUDA/
transformers bằng tay · không ngrok mới/share/Drive · KHÔNG đụng real_docs, không đưa dữ liệu khách lên GitHub ·
không sửa code trên server (sửa ở nhánh thu-2-model-htr rồi git pull) · lệnh lâu chạy trong tmux.
