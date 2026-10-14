# Trạng thái server — 2026-10-14 06:27 UTC

**Còn sống** · định kỳ

- máy: `0b994473a1f2` · up 37 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `262fe62 cham_trang: 2 pha (dots mọi trang rồi trả VRAM → 2 nền Baseer song song: GPU0 gốc+ft1@0,5, GPU1 ft3+ft4), ghi + đẩy từng trang, chạy lại = đi tiếp; BaseerNakba._lock (mặc định khoá chung như cũ, mỗi nền một GPU đặt khoá riêng)` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.2G   18G  11% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9995 MiB, 15360 MiB, 97 %
Tesla T4, 3 MiB, 15360 MiB, 0 %
5648, 9992 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
ct: 1 windows (created Wed Oct 14 06:10:56 2026)
hop_thu: 1 windows (created Wed Oct 14 06:06:05 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| ct | đang chạy | 1 | 0 | 2026-10-14 06:10 UTC | `Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.` |

## ct.log (sửa 8 phút trước)
```
W0000 00:00:1791958298.424997    5648 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-14 06:11:38.429051: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
   dots image_1: 12 khối · 24 dòng · tách chieu_ngang, kraken_muharaf · 85 s
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
   dots image_2: 40 khối · 36 dòng · tách chieu_ngang, kraken_muharaf · 165 s
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
```

