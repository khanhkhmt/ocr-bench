# Nhật ký thực nghiệm ocrbench

## 2026-10-02 02:43 — Giai đoạn 1 — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --per-category 1 --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 0.4 phút, 14/14 mẫu
- Thời gian chạy: 0.4 phút × 1 GPU = 0.01 giờ GPU · Đã dùng tổng: 0.01 / 20 giờ (<1%)
- VRAM đỉnh: —
- Số liệu: | tesseract | 14/14 | 39.6% ±18.3 | 28.3% | 45.2% | 52.0% | 0.000 | 1 | 0 (≤21.5%) | 1.65 | — |
- Quyết định: —
- Việc tiếp theo: Bước C — Chạy đủ các nhóm thường cho tesseract
- Nghi vấn dữ liệu: —

## 2026-10-02 03:06 — Giai đoạn 3 (Bước C) — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 22.3 phút, 923/923 mẫu
- Thời gian chạy: 22.3 phút × 1 GPU = 0.37 giờ GPU · Đã dùng tổng: 0.38 / 20 giờ (1.9%)
- VRAM đỉnh: —
- Số liệu: | tesseract | 923/923 | 39.2% ±2.0 | 30.3% | 47.2% | 55.7% | 0.000 | 27 | 0 (≤0.4%) | 1.45 | — |
- Quyết định: —
- Việc tiếp theo: Bước D — Chạy tài liệu dài (syn_longtable,syn_longtext) cho tesseract
- Nghi vấn dữ liệu: —

## 2026-10-02 03:06 — Giai đoạn 3 (Bước C) — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 22.3 phút, 923/923 mẫu
- Thời gian chạy: 22.3 phút × 1 GPU = 0.37 giờ GPU · Đã dùng tổng: 0.38 / 20 giờ (1.9%)
- VRAM đỉnh: —
- Số liệu: | tesseract | 923/923 | 39.2% ±2.0 | 30.3% | 47.2% | 55.7% | 0.000 | 27 | 0 (≤0.4%) | 1.45 | — |
- Quyết định: —
- Việc tiếp theo: Bước D — Chạy tài liệu dài (syn_longtable,syn_longtext) cho tesseract
- Nghi vấn dữ liệu: —

## 2026-10-02 03:40 — Giai đoạn 4 (Bước D) — tesseract
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models tesseract --categories syn_longtable,syn_longtext --gpus 0,1`
- Kết thúc: ✔ tesseract: kết thúc (mã 0) sau 25.8 phút, 1051/128 mẫu
- Thời gian chạy: 25.8 phút × 1 GPU = 0.43 giờ GPU · Đã dùng tổng: 0.81 / 20 giờ (4.1%)
- VRAM đỉnh: —
- Số liệu: | 1 | tesseract | CHẠY XONG, CHƯA GHI BENCHMARK | 26.9% | 0.0% | 1 | 27 | 2.73 | — | `tesseract` |
- Quyết định: —
- Việc tiếp theo: Bước E — Đẩy benchmark lên GitHub và chuyển sang Bước F (clean-cache)
- Nghi vấn dữ liệu: —

## 2026-10-02 03:42 — Giai đoạn 1 (Bước B) — easyocr
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models easyocr --per-category 1 --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ easyocr: kết thúc (mã 0) sau 0.7 phút, 14/14 mẫu
- Thời gian chạy: 0.7 phút × 1 GPU = 0.01 giờ GPU · Đã dùng tổng: 0.82 / 20 giờ (4.1%)
- VRAM đỉnh: 3755 MiB
- Số liệu: | easyocr | 14/14 | 35.6% ±13.2 | 26.4% | 45.9% | 61.5% | 0.000 | 0 | 0 (≤21.5%) | 1.88 | 3.7 GB |
- Quyết định: —
- Việc tiếp theo: Bước C — Chạy đủ các nhóm thường cho easyocr
- Nghi vấn dữ liệu: —

## 2026-10-02 04:10 — Giai đoạn 3 (Bước C) — easyocr
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models easyocr --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ easyocr: kết thúc (mã 0) sau 26.6 phút, 923/923 mẫu
- Thời gian chạy: 26.6 phút × 1 GPU = 0.44 giờ GPU · Đã dùng tổng: 1.26 / 20 giờ (6.3%)
- VRAM đỉnh: 9867 MiB
- Số liệu: | easyocr | 923/923 | 36.7% ±1.6 | 29.4% | 45.6% | 66.6% | 0.002 | 0 | 0 (≤0.4%) | 1.72 | 9.6 GB |
- Quyết định: —
- Việc tiếp theo: Bước D — Chạy tài liệu dài (syn_longtable,syn_longtext) cho easyocr
- Nghi vấn dữ liệu: —

## 2026-10-02 04:45 — Giai đoạn 4 (Bước D) — easyocr
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models easyocr --categories syn_longtable,syn_longtext --gpus 0,1`
- Kết thúc: ✔ easyocr: kết thúc (mã 0) sau 32.6 phút, 1051/128 mẫu
- Thời gian chạy: 32.6 phút × 1 GPU = 0.54 giờ GPU · Đã dùng tổng: 1.80 / 20 giờ (9.0%)
- VRAM đỉnh: 13.3 GB
- Số liệu: | 2 | easyocr | CHẠY XONG, CHƯA GHI BENCHMARK | 30.2% | 0.0% | 0 | 0 | 3.36 | 13.3 GB | `easyocr` |
- Quyết định: —
- Việc tiếp theo: Tạm dừng theo yêu cầu của người dùng; cập nhật code từ GitHub
- Nghi vấn dữ liệu: —

## 2026-10-02 05:46 — Giai đoạn 1 (Bước B) — sherif_handwriting
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting --per-category 1 --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ sherif_handwriting: kết thúc (mã 0) sau 6.3 phút, 14/14 mẫu
- Thời gian chạy: 6.3 phút × 1 GPU = 0.11 giờ GPU · Đã dùng tổng: 1.91 / 20 giờ (9.6%)
- VRAM đỉnh: 11425 MiB
- Số liệu: | sherif_handwriting | 14/14 | 11.8% ±6.2 | 10.6% | 26.6% | 24.3% | 0.000 | 0 | 0 (≤21.5%) | 25.73 | 11.2 GB |
- Quyết định: —
- Việc tiếp theo: Bước C — Chạy đủ các nhóm thường cho sherif_handwriting
- Nghi vấn dữ liệu: —

## 2026-10-02 07:18 — Cập nhật hệ thống — chuyển sang chạy 2 GPU
- Ghi chú: Kéo mã nguồn commit `e29131e` từ GitHub. Model vừa 1 GPU tự động chia mẫu đều cho cả 2 GPU (GPU 0 và GPU 1).
- Trạng thái GPU: Cả 2 GPU đều đang chạy (GPU 0: PID 102461, GPU 1: PID 102516).
- Model đang chạy: `sherif_handwriting` (Bước C — nhóm thường).
- Đã chạy trước khi chuyển: 306/923 mẫu. Các mẫu còn lại được chia đôi cho 2 tiến trình trên 2 GPU.
- Việc tiếp theo: Tiếp tục theo dõi sherif_handwriting Bước C trên 2 GPU cho tới khi xong 923 mẫu.

## 2026-10-02 09:36 — sherif_handwriting — Bước C hoàn thành (nhóm thường)
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`
- Kết thúc: ✔ sherif_handwriting: kết thúc (mã 0) sau 137.2 phút, 923/923 mẫu
- Thời gian chạy: 137.2 phút trên 2 GPU = 4.57 giờ GPU · Đã dùng tổng: 6.48 / 20 giờ (32.4%)
- VRAM đỉnh: 13299 MiB (GPU 0), 11945 MiB (GPU 1)
- Số liệu: | sherif_handwriting | 923/1051 | 19.8% ±2.5 | 21.8% | 31.9% | 36.5% | 0.075 | 1 | 26 (≤4.1%) | 23.52 | 13.0 GB |
- Quyết định: Hoàn thành nhóm thường, chuyển sang Bước D (tài liệu dài: syn_longtable, syn_longtext) với biến thể sherif_handwriting__long.
- Việc tiếp theo: Bước D — Tài liệu dài với sherif_handwriting__long
- Nghi vấn dữ liệu: —

## 2026-10-03 02:54 UTC — Phiên mới — khôi phục từ GitHub, tiếp tục: Bước D — Tài liệu dài cho sherif_handwriting
- Trạng thái khôi phục: Đã khôi phục kết quả của tesseract, easyocr, sherif_handwriting từ nhánh results.
- Mục tiêu: Chạy tài liệu dài cho sherif_handwriting với biến thể sherif_handwriting__sl__long (max_new_tokens: 8192, stop_on_loop: true, không max_pixels, --per-category 12).
- Việc tiếp theo: Tắt biến thể sherif_handwriting__long cũ, tạo biến thể sherif_handwriting__sl__long, kiểm tra vram, chạy Bước D.

## 2026-10-03 07:33 UTC — Phiên mới (lần 3) — khôi phục từ GitHub, tiếp tục: Bước D — Tài liệu dài cho sherif_handwriting (biến thể sherif_handwriting__sl__long)
- Trạng thái khôi phục: Đã khôi phục kết quả tesseract, easyocr, sherif_handwriting từ nhánh results. Dấu vân tay dữ liệu: aa8fdd44e1715845 (khớp chính xác).
- Mục tiêu: Chạy tài liệu dài cho sherif_handwriting với biến thể sherif_handwriting__sl__long (max_new_tokens: 8192, stop_on_loop: true, gpus: 2, không max_pixels, --per-category 12).
- Việc tiếp theo: Chạy lại đúng lệnh trong tmux bench: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting__sl__long --categories syn_longtable,syn_longtext --per-category 12 --gpus 0,1`
