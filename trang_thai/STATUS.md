# Trạng thái server — 2026-10-14 03:58 UTC

**Còn sống** · c3 XONG

- máy: `68056ead96f7` · up 1 hour, 15 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `bc0d024 README htr_train / htr_test: bảng các bản đã huấn luyện (ft1–ft4, độ mạnh, nơi để adapter), cách chạy dữ liệu → huấn luyện → chấm qua hộp thư, --hf-ckpt, tập người viết lạ, cham_ft.sh, hop_thu` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  838M   19G   5% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 437 MiB, 15360 MiB, 0 %
Tesla T4, 7687 MiB, 15360 MiB, 34 %
15194, 434 MiB, /kaggle/working/venvs/dots/bin/python
15194, 7684 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
c4: 1 windows (created Wed Oct 14 03:00:16 2026)
hop_thu: 1 windows (created Wed Oct 14 02:55:28 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| dl | XONG | 1 | 0 | 2026-10-14 02:58 UTC | `✔ train 19997 · val 998 → /tmp/htr_data` |
| c3 | XONG | 1 | 0 | 2026-10-14 03:00 UTC | `✔ XONG CHẤM ft3` |
| c4 | đang chạy | 1 | 0 | 2026-10-14 03:00 UTC | `✔ GITHUB: đã đẩy lên nhánh results-htr/htr_eval_giu_lai_n500 (commit e199c39) — đang chấm baseer_ft1_s050 272/500` |

## c4.log (sửa 0 phút trước)
```
   baseer_ft1_s050: 176/500 · 2.52 s/dòng
   baseer_ft1_s050: 192/500 · 2.54 s/dòng
   baseer_ft1_s050: 208/500 · 2.51 s/dòng
   baseer_ft1_s050: 224/500 · 2.50 s/dòng
   baseer_ft1_s050: 240/500 · 2.53 s/dòng
   baseer_ft1_s050: 256/500 · 2.52 s/dòng
   baseer_ft1_s050: 272/500 · 2.50 s/dòng
✔ GITHUB: đã đẩy lên nhánh results-htr/htr_eval_giu_lai_n500 (commit e199c39) — đang chấm baseer_ft1_s050 272/500
```

## c3.log (sửa 2 phút trước)
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

## dl.log (sửa 60 phút trước)
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

