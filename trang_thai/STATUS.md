# Trạng thái server — 2026-10-14 02:46 UTC

**Còn sống** · dl XONG

- máy: `32b232540ae5` · up 38 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:25511
- code: `bc0d024 README htr_train / htr_test: bảng các bản đã huấn luyện (ft1–ft4, độ mạnh, nơi để adapter), cách chạy dữ liệu → huấn luyện → chấm qua hộp thư, --hf-ckpt, tập người viết lạ, cham_ft.sh, hop_thu` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  794M   19G   4% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 8399 MiB, 15360 MiB, 39 %
Tesla T4, 7687 MiB, 15360 MiB, 29 %
8764, 7962 MiB, /kaggle/working/venvs/dots/bin/python
8846, 434 MiB, /kaggle/working/venvs/dots/bin/python
8846, 7684 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
c3: 1 windows (created Wed Oct 14 02:44:41 2026)
c4: 1 windows (created Wed Oct 14 02:44:48 2026)
hop_thu: 1 windows (created Wed Oct 14 02:40:37 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| dl | XONG | 1 | 0 | 2026-10-14 02:43 UTC | `✔ train 19997 · val 998 → /tmp/htr_data` |
| c3 | đang chạy | 1 | 0 | 2026-10-14 02:44 UTC | `  split_sizes = (image_grid_thw.prod(-1) // self.visual.spatial_merge_size**2).tolist()` |
| c4 | đang chạy | 1 | 0 | 2026-10-14 02:44 UTC | `The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.` |

## c3.log (sửa 1 phút trước)
```
W0000 00:00:1791945898.162366    8764 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791945898.162369    8764 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-14 02:44:58.167586: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
`torch_dtype` is deprecated! Use `dtype` instead!
== baseer_ft3: nạp 67s, còn 484 dòng
The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
  split_sizes = (image_grid_thw.prod(-1) // self.visual.spatial_merge_size**2).tolist()
```

## c4.log (sửa 1 phút trước)
```
W0000 00:00:1791945904.581669    8846 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791945904.581675    8846 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791945904.581680    8846 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-14 02:45:04.586715: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
`torch_dtype` is deprecated! Use `dtype` instead!
== baseer_ft4: nạp 61s, còn 500 dòng
The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
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

