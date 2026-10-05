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

## 2026-10-03 08:11 UTC — Phiên mới (lần 3) — khôi phục từ GitHub, tiếp tục: Bước D — Tài liệu dài cho sherif_handwriting (biến thể sherif_handwriting__sl__long)
- Trạng thái khôi phục: Đã khôi phục thành công 11 file từ nhánh results. Dấu vân tay dữ liệu: aa8fdd44e1715845 (khớp chính xác tuyệt đối).
- Cấu hình: Biến thể sherif_handwriting__sl__long (max_new_tokens: 8192, stop_on_loop: true, gpus: 2, enabled: true). Biến thể cũ sherif_handwriting__long (enabled: false).
- Việc tiếp theo: Chạy Bước D trong tmux bench: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting__sl__long --categories syn_longtable,syn_longtext --per-category 12 --gpus 0,1`

### 2026-10-03 09:35 UTC — Kiểm tra định kỳ sherif_handwriting__sl__long
- Tiến độ: 1/24 mẫu (mẫu `syn_longtable/syn_longtable_0007` xong trong 401.91s, 4.563 ký tự, không lỗi). Đang chạy mẫu 2/24.
- GPU: GPU 0: 14.001 MiB / 15.360 MiB (36% util), GPU 1: 13.361 MiB / 15.360 MiB (68% util).

## 2026-10-05 02:28 UTC — Phiên mới (lần 4) — khôi phục từ GitHub, tiếp tục: Bước D — Tài liệu dài cho sherif_handwriting (biến thể sherif_handwriting__pp__long)
- Trạng thái khôi phục: Đã khôi phục thành công 13 file từ nhánh results. Dấu vân tay dữ liệu: aa8fdd44e1715845 (khớp chính xác).
- Tình trạng: tesseract, easyocr HOÀN THÀNH. sherif_handwriting nhóm thường xong 923/923. Biến thể sherif_handwriting__sl__long chạy 24/24 có 5 mẫu OOM.
- Quyết định người dùng: Đọc từng trang ở độ phân giải đầy đủ; không giảm độ phân giải; không chấp nhận 19/24; tạo biến thể sherif_handwriting__pp__long (max_new_tokens: 8192, stop_on_loop: true, multi_page: per_page, gpus: 1 để tự chia 2 GPU).
- Việc tiếp theo: Đặt enabled: false cho sherif_handwriting__sl__long và sherif_handwriting__long; tạo mục sherif_handwriting__pp__long; chạy Bước D trong tmux bench với lệnh: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting__pp__long --categories syn_longtable,syn_longtext --per-category 12 --gpus 0,1`.

## 2026-10-05 03:34 — Giai đoạn 4 (Bước D & E) — sherif_handwriting (biến thể sherif_handwriting__pp__long)
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting__pp__long --categories syn_longtable,syn_longtext --per-category 12 --gpus 0,1`
- Kết thúc: ✔ sherif_handwriting__pp__long: kết thúc (mã 0) sau 61.6 phút, 24/24 mẫu
- Thời gian chạy: 61.6 phút trên 2 GPU = 2.05 giờ GPU · Đã dùng tổng: 8.53 / 20 giờ (42.7%)
- VRAM đỉnh: 13873 MiB
- Số liệu: | 1 | sherif_handwriting | đủ | 14.4% | 4.9% | 29 | 1 | 29.76 | 13.5 GB | `sherif_handwriting`, `sherif_handwriting__pp__long` |
- Quyết định: Hoàn thành toàn bộ split dev cho sherif_handwriting (923 mẫu thường + 24 mẫu tài liệu dài, 0 lỗi OOM). Đứng đầu bảng xếp hạng BENCHMARK.md.
- Việc tiếp theo: Bước F (clean-cache sherif_handwriting, tắt enabled cho mọi biến thể sherif_handwriting) -> Bước G -> chuyển sang model tiếp theo trong queue: qari_0_4.
- Nghi vấn dữ liệu: —

## 2026-10-05 03:34 — Giai đoạn 4 (Bước D & E) — sherif_handwriting (biến thể sherif_handwriting__pp__long)
- Lệnh: `ocrbench run --config /kaggle/working/config.yaml --models sherif_handwriting__pp__long --categories syn_longtable,syn_longtext --per-category 12 --gpus 0,1`
- Kết thúc: ✔ sherif_handwriting__pp__long: kết thúc (mã 0) sau 61.6 phút, 24/24 mẫu
- Thời gian chạy: 61.6 phút trên 2 GPU = 2.05 giờ GPU · Đã dùng tổng: 8.53 / 20 giờ (42.7%)
- VRAM đỉnh: 13873 MiB
- Số liệu: | 1 | sherif_handwriting | đủ | 14.4% | 4.9% | 29 | 1 | 29.76 | 13.5 GB | `sherif_handwriting`, `sherif_handwriting__pp__long` |
- Quyết định: Hoàn thành toàn bộ split dev cho sherif_handwriting (923 mẫu thường + 24 mẫu tài liệu dài, 0 lỗi OOM). Đứng đầu bảng xếp hạng BENCHMARK.md.
- Việc tiếp theo: Bước F (clean-cache sherif_handwriting, tắt enabled cho mọi biến thể sherif_handwriting) -> Bước G -> chuyển sang model tiếp theo trong queue: qari_0_4.
- Nghi vấn dữ liệu: —

## 2026-10-05 03:50 UTC — Bước F — sherif_handwriting
- Clean-cache: Đã chạy `ocrbench clean-cache --config /kaggle/working/config.yaml --models sherif_handwriting`, giải phóng ~7.5 GB cache trọng số.
- Trạng thái biến thể: Đã tắt toàn bộ biến thể sherif_handwriting trong `/kaggle/working/config.yaml` (`enabled: false` cho `sherif_handwriting`, `sherif_handwriting__long`, `sherif_handwriting__sl__long`, `sherif_handwriting__pp__long`).
- Dung lượng đĩa trống (`df -h /kaggle/working ~`):
  - `/kaggle/working`: 19G khả dụng (554M đã dùng / 20G, 3%)
  - `/root` (~): 1.1T khả dụng (7.0T đã dùng / 8.0T, 87%)
- Ghi chú: Hàng đợi đã đổi (theo commit 62aa6f0), model tiếp theo là `dots_mocr` (hàng đợi mới: ... sherif_handwriting → dots_mocr → sherif_handwriting_pre → qari_0_4 → ...), không phải `qari_0_4`.

## 2026-10-05 04:10 UTC — TẠM DỪNG benchmark theo yêu cầu người dùng, chuyển sang web demo dots.mocr
- Model và bước đang dở: `dots_mocr` (Bước B — chạy thử 14 mẫu trên 2 GPU). Tiến trình đã dừng an toàn qua Ctrl-C trong tmux bench, giải phóng toàn bộ VRAM trên 2 GPU (0 MiB / 15360 MiB). Mẫu đã ghi trong predictions.jsonl được giữ nguyên.
- LỆNH CẦN CHẠY LẠI để tiếp tục sau này:
`ocrbench run --config /kaggle/working/config.yaml --models dots_mocr --per-category 1 --categories pub_handwriting_ar,pub_handwriting_en,pub_printed_ar,pub_tables_ar,pub_tables_en,syn_degraded,syn_form_ar,syn_form_en,syn_invoice_ar,syn_invoice_en,syn_invoice_mixed,syn_text_ar,syn_text_en,syn_text_mixed --gpus 0,1`


## 2026-10-05 04:42 UTC — Chẩn đoán dots

### A) A_fp16
- Dòng ✔ của lệnh: `✔ inference/samples/01_hoa_don_tieng_anh.png: 1 trang → /kaggle/working/diag/A_fp16/01_hoa_don_tieng_anh/`
- Thời gian: real 0m49.103s (user 0m51.079s, sys 0m6.137s)
- `head -c 1500` file .md:
```markdown
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKIAAACLCAIAAABtM9WyAAABWElEQVR4nO3RgQkAIRDAsPf33/ncQsEmExS6Zubjdf/tAE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOWED+hUEExfG8/AAAAAASUVORK5CYII=)
```

### B) B_fp32
- Dòng ✔ của lệnh: `✔ inference/samples/01_hoa_don_tieng_anh.png: 1 trang → /kaggle/working/diag/B_fp32/01_hoa_don_tieng_anh/`
- Thời gian: real 1m7.395s (user 1m7.266s, sys 0m11.752s)
- `head -c 1500` file .md:
```markdown
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAkcAAAHYCAIAAADI+durAACUfUlEQVR4nO39f1ATabow/F/nO2qn1ElPR23AqgStNYBlAjNrFPfhh/WQgdkNYg0oOxvEOqLUHBTPg8I76yM8hUJ9dV92Dgr7iuZMOcJbIjkzjmHKkczqGp5SyHNE4xklsRyJWw5JlZKoFJ0Zpdtxy/eP/CC/AUXFnutTW7Vj6HTf/eu+uu/7uu/807NnzwAhhBDihf/f6y4AQgghNGUwqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/s
```

### C) C_nho
- Dòng ✔ của lệnh: `✔ /kaggle/working/testset/images/pub_tables_en/pubtabnet__598044.png: 1 trang → /kaggle/working/diag/C_nho/pubtabnet__598044/  (⚠ 1 trang JSON hỏng)`
- Thời gian: real 0m53.758s (user 0m56.053s, sys 0m5.774s)
- `head -c 1500` file .md:
```markdown
The 2024 National50000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000]
```

### D) D_nho_fitz
- Dòng ✔ của lệnh: `✔ /kaggle/working/testset/images/pub_tables_en/pubtabnet__598044.png: 1 trang → /kaggle/working/diag/D_nho_fitz/pubtabnet__598044/  (⚠ 1 trang JSON hỏng)`
- Thời gian: real 1m39.952s (user 1m42.044s, sys 0m5.955s)
- `head -c 1500` file .md:
```markdown
I am a student at the University of California, Berkeley.

I am a first-year student in the Computer Science program.

My name is John Smith.

I am from California, USA.

I am 19 years old.

My major is Computer Science.

I am interested in software engineering.

I have taken several computer science courses.

For example, I have taken

Introduction to Programming.

Introduction to Data Structures.

Algorithms.

Software Design.

Computer Architecture.

Operating Systems.

Database Systems.

C 编程语言基础.

C++ 语言基础.

计算机网络.

人工智能基础.

计算机图形学.

算法与数据结构.

软件工程基础.

软件开发实践.

软件质量保证.

软件测试.

软件设计模式.

软件开发工具.

软件开发环境.

软件开发标准.

软件开发流程.

软件开发管理.

软件开发文档.

软件开发工具.

软件开发环境.

软件开发标准.

软件开发流程.

软件开发管理.
```


## 2026-10-05 04:55 UTC — Chẩn đoán dots lần 2 (manual_embeds)
```text
transformers 5.0.0 | torch 2.10.0+cu128 | cuda Tesla T4
[1] token ảnh trong input: 416 · cần: 416 · OK · keys ['input_ids', 'attention_mask', 'pixel_values', 'image_grid_thw']
nạp model 4s
[2] bộ mã hoá ảnh: |gốc − vá| lớn nhất = 5.734e-04 · |gốc| TB = 1.232e+00 · OK · NaN/inf: False
[3] đường gốc: bước đầu có pixel_values = True (cache_position[0] = 0) · vision_tower gọi 1 lần [(416, 1536)]
    chữ: 
[4] inputs_embeds tự dựng (fp16): 
[5] inputs_embeds tự dựng (fp32):
```


## 2026-10-05 04:58 UTC — Kiểm tra web demo dots (thất bại)
- Kết quả kiểm tra: ✘ KIỂM TRA KHÔNG ĐẠT
- 80 dòng cuối demo.log:
```text
Loading weights:  95%|█████████▍| 609/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.mlp.fc2.weight]
Loading weights:  95%|█████████▍| 609/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.mlp.fc2.weight]
Loading weights:  95%|█████████▍| 610/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.mlp.fc3.weight]
Loading weights:  95%|█████████▍| 610/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.mlp.fc3.weight]
Loading weights:  95%|█████████▌| 611/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.norm1.weight]  
Loading weights:  95%|█████████▌| 611/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.norm1.weight]
Loading weights:  95%|█████████▌| 612/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.norm2.weight]
Loading weights:  95%|█████████▌| 612/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.norm2.weight]
Loading weights:  95%|█████████▌| 613/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.attn.proj.weight]
Loading weights:  95%|█████████▌| 613/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.attn.proj.weight]
Loading weights:  95%|█████████▌| 614/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.attn.qkv.weight] 
Loading weights:  95%|█████████▌| 614/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.attn.qkv.weight]
Loading weights:  96%|█████████▌| 615/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc1.weight] 
Loading weights:  96%|█████████▌| 615/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc1.weight]
Loading weights:  96%|█████████▌| 616/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc2.weight]
Loading weights:  96%|█████████▌| 616/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc2.weight]
Loading weights:  96%|█████████▌| 617/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc3.weight]
Loading weights:  96%|█████████▌| 617/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc3.weight]
Loading weights:  96%|█████████▌| 618/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.norm1.weight]  
Loading weights:  96%|█████████▌| 618/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.norm1.weight]
Loading weights:  96%|█████████▋| 619/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.norm2.weight]
Loading weights:  96%|█████████▋| 619/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.norm2.weight]
Loading weights:  96%|█████████▋| 620/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.attn.proj.weight]
Loading weights:  96%|█████████▋| 620/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.attn.proj.weight]
Loading weights:  97%|█████████▋| 621/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.attn.qkv.weight] 
Loading weights:  97%|█████████▋| 621/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.attn.qkv.weight]
Loading weights:  97%|█████████▋| 622/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc1.weight] 
Loading weights:  97%|█████████▋| 622/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc1.weight]
Loading weights:  97%|█████████▋| 623/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc2.weight]
Loading weights:  97%|█████████▋| 623/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc2.weight]
Loading weights:  97%|█████████▋| 624/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc3.weight]
Loading weights:  97%|█████████▋| 624/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc3.weight]
Loading weights:  97%|█████████▋| 625/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.norm1.weight]  
Loading weights:  97%|█████████▋| 625/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.norm1.weight]
Loading weights:  97%|█████████▋| 626/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.norm2.weight]
Loading weights:  97%|█████████▋| 626/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.norm2.weight]
Loading weights:  98%|█████████▊| 627/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.attn.proj.weight]
Loading weights:  98%|█████████▊| 627/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.attn.proj.weight]
Loading weights:  98%|█████████▊| 628/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.attn.qkv.weight] 
Loading weights:  98%|█████████▊| 628/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.attn.qkv.weight]
Loading weights:  98%|█████████▊| 629/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc1.weight] 
Loading weights:  98%|█████████▊| 629/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc1.weight]
Loading weights:  98%|█████████▊| 630/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc2.weight]
Loading weights:  98%|█████████▊| 630/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc2.weight]
Loading weights:  98%|█████████▊| 631/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc3.weight]
Loading weights:  98%|█████████▊| 631/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc3.weight]
Loading weights:  98%|█████████▊| 632/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.norm1.weight]  
Loading weights:  98%|█████████▊| 632/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.norm1.weight]
Loading weights:  98%|█████████▊| 633/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.norm2.weight]
Loading weights:  98%|█████████▊| 633/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.norm2.weight]
Loading weights:  99%|█████████▊| 634/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.ln_q.bias]      
Loading weights:  99%|█████████▊| 634/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.ln_q.bias]
Loading weights:  99%|█████████▉| 635/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.ln_q.weight]
Loading weights:  99%|█████████▉| 635/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.ln_q.weight]
Loading weights:  99%|█████████▉| 636/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.mlp.0.bias] 
Loading weights:  99%|█████████▉| 636/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.mlp.0.bias]
Loading weights:  99%|█████████▉| 637/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.mlp.0.weight]
Loading weights:  99%|█████████▉| 637/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.mlp.0.weight]
Loading weights:  99%|█████████▉| 638/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.0.weight]
Loading weights:  99%|█████████▉| 638/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.2.bias]  
Loading weights:  99%|█████████▉| 638/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.2.bias]
Loading weights:  99%|█████████▉| 639/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.2.weight]
Loading weights:  99%|█████████▉| 639/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.2.weight]
Loading weights: 100%|█████████▉| 640/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.norm.weight]
Loading weights: 100%|█████████▉| 640/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.norm.weight]
Loading weights: 100%|█████████▉| 641/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.proj.bias]  
Loading weights: 100%|█████████▉| 641/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.proj.bias]
Loading weights: 100%|█████████▉| 642/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.proj.weight]
Loading weights: 100%|█████████▉| 642/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.proj.weight]
Loading weights: 100%|██████████| 643/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.post_trunk_norm.weight]            
Loading weights: 100%|██████████| 643/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.post_trunk_norm.weight]
Loading weights: 100%|██████████| 643/643 [00:02<00:00, 234.42it/s, Materializing param=vision_tower.post_trunk_norm.weight]
nạp model: 20s trên 2 bản model
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
thời gian 1 trang: 21.1s · nguồn: OCR · lỗi: — · ghi chú: —
số khối bố cục: 1 · có bảng HTML: False
----- kết quả -----

-------------------
✘ KIỂM TRA KHÔNG ĐẠT — xem kết quả ở trên (gửi cho người sửa code)
```

## 2026-10-05 05:13 UTC — Web demo dots.mocr chạy thành công (venv transformers 4.56.1)
- Trạng thái: ✔ KIỂM TRA ĐẠT, web demo đang chạy tại http://127.0.0.1:7860 (HTTP 200)
- Trích xuất log kiểm tra tự động:
```text
   torch 2.10.0+cu128 | transformers 4.56.1 | GPU 2
== 2. Tự kiểm tra: dots đọc một trang mẫu (lần đầu tải model ~6 GB)
warning: The `fitz` API is deprecated and will be removed in future. Use `import pymupdf` instead.
Fetching 22 files: 100%|██████████| 22/22 [00:00<00:00, 2852.47it/s]
2026-10-05 05:11:05.529949: E external/local_xla/xla/stream_executor/cuda/cuda_fft.cc:467] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
E0000 00:00:1791177065.764530   61781 cuda_dnn.cc:8579] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
E0000 00:00:1791177065.825954   61781 cuda_blas.cc:1407] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
W0000 00:00:1791177066.353218   61781 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791177066.353247   61781 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791177066.353250   61781 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791177066.353253   61781 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-05 05:11:06.417471: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
Loading checkpoint shards: 100%|██████████| 2/2 [00:01<00:00,  1.08it/s]
Fetching 22 files: 100%|██████████| 22/22 [00:00<00:00, 2656.84it/s]
Loading checkpoint shards: 100%|██████████| 2/2 [00:01<00:00,  1.05it/s]
nạp model: 36s trên 2 bản model
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
thời gian 1 trang: 31.8s · nguồn: OCR · lỗi: — · ghi chú: —
số khối bố cục: 4 · có bảng HTML: True
----- kết quả -----
INVOICE No. 2041

Customer: Al Noor Trading LLC Date: 05/10/2026

<table><thead><tr><td>Item</td><td>Qty</td><td>Price</td></tr></thead><tbody><tr><td>Laptop</td><td>2</td><td>1,250.00</td></tr><tr><td>Printer</td><td>1</td><td>430.50</td></tr><tr><td>Total</td><td></td><td>2,930.50</td></tr></tbody></table>

Thank you for your business. Payment due within 30 days.
-------------------
✔ KIỂM TRA ĐẠT — mở web được
```

## 2026-10-05 06:17 UTC — Web demo mở qua ngrok
- Trạng thái: web demo mở qua ngrok, không đăng nhập

## 2026-10-05 09:55 UTC — Bắt đầu thí nghiệm TTA ký hiệu nhỏ (experiments/tta_markers)
- Web demo đã chuyển sang GPU 1 (ngrok link giữ nguyên, HTTP 200).
- Thí nghiệm đang chạy trên GPU 0 trong tmux session `exp`.
- Mẫu đầu tiên đang chạy: pubtabnet__552595.
- 10:05 UTC — Đã chạy xong mẫu 1 (pubtabnet__552595: CER 1.73 → 1.46, ghép v1 đúng 2/3 ký hiệu, sai 0) và mẫu 2 (pubtabnet__699374: CER 0.0). Đang chạy mẫu 3 (pubtabnet__684148).
- 10:16 UTC — Đã chạy xong 7 mẫu (552595, 699374, 684148, 707833, 644357, 590407, 550360). Đang chạy mẫu 8 (pubtabnet__729650). Còn 2 mẫu đối chứng (01, 08).


## Thí nghiệm TTA ký hiệu nhỏ (hướng 3)

# Thí nghiệm TTA + ghép ký hiệu nhỏ (dots.mocr)

Lượt phụ: `x4_ocr,x5_ocr,x5_layout` · min_votes 1 (v1) và 2 (v2)

| Ảnh | Kích thước | Ký hiệu đáp án | Gốc giữ | Ghép v1 (sai) | Ghép v2 (sai) | CER gốc | CER v1 | CER v2 | Giây gốc | Giây phụ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pubtabnet__552595 | 503×342 | 3 | 0 | 2 (0) | 0 (0) | 1.73 | 1.46 | 1.73 | 63.3 | 463.2 |
| pubtabnet__699374 | 245×96 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 15.9 | 51.7 |
| pubtabnet__684148 | 166×254 | 0 | 0 | 0 (0) | 0 (0) | 4.08 | 4.08 | 4.08 | 45.3 | 135.5 |
| pubtabnet__707833 | 245×65 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 10.7 | 32.5 |
| pubtabnet__644357 | 245×118 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 16.6 | 53.7 |
| pubtabnet__590407 | 341×75 | 0 | 0 | 0 (0) | 0 (0) | 3.58 | 3.58 | 3.58 | 22.9 | 74.4 |
| pubtabnet__550360 | 503×163 | 0 | 0 | 0 (0) | 0 (0) | 44.75 | 44.75 | 44.75 | 52.7 | 151.1 |
| pubtabnet__729650 | 486×130 | 0 | 0 | 0 (0) | 0 (0) | 6.97 | 6.97 | 6.97 | 16.3 | 74.2 |
| 01_hoa_don_tieng_anh | 1500×1793 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 93.4 | 0 |
| 08_anh_chup_xau_hoa_don_a_rap | 1150×1088 | 0 | 0 | 0 (0) | 0 (0) | 0.0 | 0.0 | 0.0 | 63.8 | 0 |

**Tổng ký hiệu trước số:** đáp án 3 · gốc giữ 0 · ghép v1 2 (thêm sai 0) · ghép v2 0 (thêm sai 0)

**Lượt phụ lỗi:**
- 01_hoa_don_tieng_anh · x4_ocr: OutOfMemoryError: CUDA out of memory. Tried to allocate 606.00 MiB. GPU 0 has a total capacity of 14.56 GiB of which 524.81 MiB is free. Including non-PyTorch memory, this process has 14.05 GiB memory in use. Of the allocated memory 13.29 GiB is allocated by PyTorch, and 641.10 MiB is reserved by Py
- 01_hoa_don_tieng_anh · x5_ocr: OutOfMemoryError: CUDA out of memory. Tried to allocate 606.00 MiB. GPU 0 has a total capacity of 14.56 GiB of which 390.81 MiB is free. Including non-PyTorch memory, this process has 14.18 GiB memory in use. Of the allocated memory 13.29 GiB is allocated by PyTorch, and 774.26 MiB is reserved by Py
- 01_hoa_don_tieng_anh · x5_layout: OutOfMemoryError: CUDA out of memory. Tried to allocate 640.00 MiB. GPU 0 has a total capacity of 14.56 GiB of which 114.81 MiB is free. Including non-PyTorch memory, this process has 14.45 GiB memory in use. Of the allocated memory 13.57 GiB is allocated by PyTorch, and 760.41 MiB is reserved by Py
- 08_anh_chup_xau_hoa_don_a_rap · x4_ocr: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.00 GiB. GPU 0 has a total capacity of 14.56 GiB of which 2.15 GiB is free. Including non-PyTorch memory, this process has 12.41 GiB memory in use. Of the allocated memory 11.66 GiB is allocated by PyTorch, and 627.63 MiB is reserved by PyTorc
- 08_anh_chup_xau_hoa_don_a_rap · x5_ocr: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.00 GiB. GPU 0 has a total capacity of 14.56 GiB of which 2.09 GiB is free. Including non-PyTorch memory, this process has 12.46 GiB memory in use. Of the allocated memory 11.66 GiB is allocated by PyTorch, and 685.63 MiB is reserved by PyTorc
- 08_anh_chup_xau_hoa_don_a_rap · x5_layout: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.15 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.98 GiB is free. Including non-PyTorch memory, this process has 12.58 GiB memory in use. Of the allocated memory 11.83 GiB is allocated by PyTorch, and 627.83 MiB is reserved by PyTorc

