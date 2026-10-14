# Trạng thái server — 2026-10-14 04:40 UTC

**Còn sống** · ct CHẾT (lỗi không tự sửa được) → chờ lệnh

- máy: `68056ead96f7` · up 1 hour, 57 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `4f92fce htr_test/cham_trang.py: chấm cả TRANG tài liệu thật (đường đi như web: dots chia khối + đọc đánh máy; tách dòng; Baseer gốc / ft1@0,5 / ft3 / ft4 đọc từng dòng) so với 2 bộ nhãn — đúng ký tự / từ + thu hồi từ không tính thứ tự` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.2G   18G  12% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 0 MiB, 15360 MiB, 0 %
Tesla T4, 0 MiB, 15360 MiB, 0 %
(không có tiến trình)
```

## Phiên tmux
```
hop_thu: 1 windows (created Wed Oct 14 02:55:28 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| dl | XONG | 1 | 0 | 2026-10-14 02:58 UTC | `✔ train 19997 · val 998 → /tmp/htr_data` |
| c3 | XONG | 1 | 0 | 2026-10-14 03:00 UTC | `✔ XONG CHẤM ft3` |
| c4 | XONG | 1 | 0 | 2026-10-14 03:00 UTC | `✔ XONG CHẤM ft4` |
| ct | CHỜ LỆNH | 1 | 0 | 2026-10-14 04:32 UTC | `torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 136.00 MiB. GPU 1 has a total capacity of 14.56 GiB of which 62.81 MiB is free. Including non-PyTo` |

## ct.log (sửa 1 phút trước)
```
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/accelerate/hooks.py", line 175, in new_forward
    output = module._old_forward(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.cache/huggingface/modules/transformers_modules/DotsMOCR/modeling_dots_vision.py", line 229, in forward
    x = F.silu(self.fc1(x)) * self.fc3(x)
        ~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 136.00 MiB. GPU 1 has a total capacity of 14.56 GiB of which 62.81 MiB is free. Including non-PyTorch memory, this process has 14.50 GiB memory in use. Of the allocated memory 13.98 GiB is allocated by PyTorch, and 398.92 MiB is reserved 
```

## c4.log (sửa 32 phút trước)
```
| baseer_ft4 | 500/500 | **95.0%** | **86.0%** | 5.7% | 16.1% | 5.0% | 14.0% | 6.0% | 1.01 | 3 | 1 |
| baseer_ft3 | 500/500 | **94.7%** | **85.0%** | 6.0% | 17.6% | 5.3% | 15.0% | 5.6% | 1.00 | 1 | 1 |
| baseer_ft1_s050 | 500/500 | **93.3%** | **80.7%** | 8.6% | 27.0% | 6.7% | 19.3% | 7.1% | 0.99 | 1 | 3 |
| baseer | 500/500 | **88.3%** | **67.3%** | 14.3% | 42.6% | 11.7% | 32.7% | 12.7% | 1.00 | 2 | 3 |
đúng ký tự = 100% − CER chuẩn hoá (cả tập, tính theo tổng ký tự); đúng từ = 100% − WER chuẩn hoá. Từng dòng: chi_tiet.csv (mở bằng Excel) và xem_ket_qua.html (có ảnh).
Từng dòng: /kaggle/working/htr_eval_giu_lai_n500/chi_tiet.csv  ·  /kaggle/working/htr_eval_giu_lai_n500/xem_ket_qua.html
✔ GITHUB: đã đẩy lên nhánh results-htr/htr_eval_giu_lai_n500 (commit 33da40c) — XONG tất cả
✔ XONG CHẤM ft4
```

## c3.log (sửa 44 phút trước)
```
| baseer_ft4 | 500/500 | **95.0%** | **86.0%** | 5.7% | 16.1% | 5.0% | 14.0% | 6.0% | 1.01 | 3 | 1 |
| baseer_ft3 | 500/500 | **94.7%** | **85.0%** | 6.0% | 17.6% | 5.3% | 15.0% | 5.6% | 1.00 | 1 | 1 |
| baseer_ft1_s050 | 224/500 | **94.2%** | **83.1%** | 7.7% | 25.0% | 5.8% | 16.9% | 7.1% | 1.00 | 1 | 2 |
| baseer | 500/500 | **88.3%** | **67.3%** | 14.3% | 42.6% | 11.7% | 32.7% | 12.7% | 1.00 | 2 | 3 |
đúng ký tự = 100% − CER chuẩn hoá (cả tập, tính theo tổng ký tự); đúng từ = 100% − WER chuẩn hoá. Từng dòng: chi_tiet.csv (mở bằng Excel) và xem_ket_qua.html (có ảnh).
Từng dòng: /kaggle/working/htr_eval_giu_lai_n500/chi_tiet.csv  ·  /kaggle/working/htr_eval_giu_lai_n500/xem_ket_qua.html
✔ GITHUB: đã đẩy lên nhánh results-htr/htr_eval_giu_lai_n500 (commit a9c342b) — XONG tất cả
✔ XONG CHẤM ft3
```

## dl.log (sửa 102 phút trước)
```
  train: 22092 dòng
  validation: 1069 dòng
✔ 23161 dòng → /tmp/htr_data/muharaf  ·  xem: /tmp/htr_data/muharaf/xem_mau.html
== giữ riêng nhóm Muharaf: 2015, AnF, BEK, Baddour, ME, SB, YFS
== muharaf
   train 20568 · val 1030 · bỏ vì trùng nhãn tập chấm 603
   GIỮ RIÊNG 1562 dòng → /tmp/htr_data/giu_lai_muharaf
✔ train 19997 · val 998 → /tmp/htr_data
```

