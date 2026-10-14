# Trạng thái server — 2026-10-14 10:47 UTC

**Còn sống** · định kỳ

- máy: `9c2cedb12555` · up 46 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `c54f487 cham_trang: --trang (chỉ chấm các trang chọn, vd. image_3)` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.2G   18G  11% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 8029 MiB, 15360 MiB, 26 %
Tesla T4, 8019 MiB, 15360 MiB, 23 %
9369, 8026 MiB, /kaggle/working/venvs/dots/bin/python
9369, 8016 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
ct3: 1 windows (created Wed Oct 14 10:39:07 2026)
hop_thu: 1 windows (created Wed Oct 14 10:26:55 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| ct3 | đang chạy | 1 | 0 | 2026-10-14 10:39 UTC | `The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.` |

## ct3.log (sửa 1 phút trước)
```
W0000 00:00:1791974445.614294    9369 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-14 10:40:45.618982: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
   dots image_3: 27 khối · 55 dòng · tách chieu_ngang, kraken_muharaf · dots ×1.5 · 215 s
`torch_dtype` is deprecated! Use `dtype` instead!
== đọc dòng: cuda:0: baseer_goc, ft1_s050 | cuda:1: ft3, ft4
The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
```

