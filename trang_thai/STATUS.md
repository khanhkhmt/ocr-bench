# Trạng thái server — 2026-10-14 06:48 UTC

**Còn sống** · định kỳ

- máy: `0b994473a1f2` · up 58 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `262fe62 cham_trang: 2 pha (dots mọi trang rồi trả VRAM → 2 nền Baseer song song: GPU0 gốc+ft1@0,5, GPU1 ft3+ft4), ghi + đẩy từng trang, chạy lại = đi tiếp; BaseerNakba._lock (mặc định khoá chung như cũ, mỗi nền một GPU đặt khoá riêng)` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.2G   18G  11% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 5491 MiB, 15360 MiB, 0 %
Tesla T4, 3 MiB, 15360 MiB, 0 %
5648, 5488 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
ct: 1 windows (created Wed Oct 14 06:10:56 2026)
hop_thu: 1 windows (created Wed Oct 14 06:06:05 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| ct | đang chạy | 1 | 0 | 2026-10-14 06:10 UTC | ``torch_dtype` is deprecated! Use `dtype` instead!` |

## ct.log (sửa 0 phút trước)
```
    📊 Found 1 dict objects
    ✅ No duplicate dict objects found
  ✅ Cleaning complete: 1 objects
    📊 Data length 1 <= 1, skipping deduplication check
   dots image_3: 0 khối · 0 dòng · tách  · 1589 s
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
   dots image_4: 11 khối · 19 dòng · tách chieu_ngang, kraken_muharaf · 39 s
`torch_dtype` is deprecated! Use `dtype` instead!
```

