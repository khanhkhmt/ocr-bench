# Trạng thái server — 2026-10-14 03:01 UTC

**Còn sống** · dl XONG

- máy: `68056ead96f7` · up 18 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `bc0d024 README htr_train / htr_test: bảng các bản đã huấn luyện (ft1–ft4, độ mạnh, nơi để adapter), cách chạy dữ liệu → huấn luyện → chấm qua hộp thư, --hf-ckpt, tập người viết lạ, cham_ft.sh, hop_thu` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  794M   19G   4% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 8383 MiB, 15360 MiB, 0 %
Tesla T4, 7651 MiB, 15360 MiB, 0 %
5363, 7946 MiB, /kaggle/working/venvs/dots/bin/python
5432, 434 MiB, /kaggle/working/venvs/dots/bin/python
5432, 7648 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
c3: 1 windows (created Wed Oct 14 03:00:09 2026)
c4: 1 windows (created Wed Oct 14 03:00:16 2026)
hop_thu: 1 windows (created Wed Oct 14 02:55:28 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| dl | XONG | 1 | 0 | 2026-10-14 02:58 UTC | `✔ train 19997 · val 998 → /tmp/htr_data` |
| c3 | đang chạy | 1 | 0 | 2026-10-14 03:00 UTC | ``torch_dtype` is deprecated! Use `dtype` instead!` |
| c4 | đang chạy | 1 | 0 | 2026-10-14 03:00 UTC | ``torch_dtype` is deprecated! Use `dtype` instead!` |

## c4.log (sửa 0 phút trước)
```
E0000 00:00:1791946832.572541    5432 cuda_blas.cc:1407] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
W0000 00:00:1791946832.593014    5432 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791946832.593065    5432 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791946832.593071    5432 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791946832.593074    5432 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-14 03:00:32.598205: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
`torch_dtype` is deprecated! Use `dtype` instead!
```

## c3.log (sửa 0 phút trước)
```
E0000 00:00:1791946826.817240    5363 cuda_blas.cc:1407] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
W0000 00:00:1791946826.838670    5363 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791946826.838704    5363 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791946826.838707    5363 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791946826.838709    5363 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-14 03:00:26.843983: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
`torch_dtype` is deprecated! Use `dtype` instead!
```

## dl.log (sửa 2 phút trước)
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

