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
1. ✅ Chẩn đoán Ketaba (32 dòng): q4 (như tác giả) 91,0% · 33,7 s/dòng; nền fp16 85,6% · 32 s/dòng → giữ q4.
2. [đang chạy từ 14:40 ICT] tmux htr_bench: benchmark --tag n500 --n 500 --models dots,ketaba --datasets muharaf,omar --push
   (log /kaggle/working/htr_bench_n500.log). Thứ tự: dots×Muharaf → dots×Omar (~8,9 s/dòng, ~2,5 giờ) → ketaba×Muharaf
   → ketaba×Omar (tiếp từ 240/500; ~25–34 s/dòng, ~6 giờ).
   Sập/tmux chết → chạy lại ĐÚNG lệnh trên (tự khôi phục từ GitHub).
2b. ⚠ 14:50–14:55 COLAB NGẮT (dots×Muharaf 240/500 đã lên GitHub). Khi người dùng mở lại + cho địa chỉ ngrok
    mới: sửa Host colab trong ~/.ssh/config, rồi `ssh colab 'bash -s' < ~/ocr-bench-htr/htr_test/khoi_phuc.sh`
    (lấy code, hộp thư, venv, chạy tiếp benchmark từ GitHub).
3. Khi "XONG TẤT CẢ": kiểm tra results-htr/htr_benchmark_n500/BENCHMARK_HTR.md, báo người dùng.
   Nếu quá lâu: có thể dừng sau ketaba×Muharaf (Ketaba×Omar đã có 240 dòng ≈ Baseer).

## Luật cứng
Token chỉ qua biến môi trường/header, không in · không pkill -f, chỉ dừng phiên do mình mở · không cài/gỡ torch/CUDA/
transformers bằng tay · không ngrok mới/share/Drive · KHÔNG đụng real_docs, không đưa dữ liệu khách lên GitHub ·
không sửa code trên server (sửa ở nhánh thu-2-model-htr rồi git pull) · lệnh lâu chạy trong tmux.
