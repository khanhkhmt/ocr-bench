# Trạng thái server — 2026-10-14 08:18 UTC

**Còn sống** · td XONG

- máy: `0b994473a1f2` · up 2 hours, 28 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `f13093d thu_dots: nạp dots lần lượt trên từng GPU (hai luồng cùng snapshot_download → tqdm AttributeError '_lock', GPU thứ hai không nạp được)` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.2G   18G  11% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 0 MiB, 15360 MiB, 0 %
Tesla T4, 0 MiB, 15360 MiB, 0 %
(không có tiến trình)
```

## Phiên tmux
```
hop_thu: 1 windows (created Wed Oct 14 06:06:05 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| ct | XONG | 1 | 0 | 2026-10-14 06:10 UTC | `✔ XONG CHẤM TRANG` |
| td | XONG | 2 | 0 | 2026-10-14 07:33 UTC | `✔ XONG THỬ DOTS` |

## td.log (sửa 3 phút trước)
```
| image_4 | chi_chu | 2 |  |  |  |  | 0 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.54 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.44  |
| image_4 | day_du | 1 | 1165×1500 | 11 | 611 | 50 | 1 |  |
| image_4 | day_du | 1.5 | 1748×2250 | 11 | 625 | 95 | 0 |  |
| image_4 | day_du | 2 |  |  |  |  | 0 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.70 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.27  |
| image_4 | khoi | 1 | 1165×1500 | 12 | 597 | 46 | 1 |  |
| image_4 | khoi | 1.5 | 1748×2250 | 11 | 578 | 98 | 1 |  |
| image_4 | khoi | 2 |  |  |  |  | 1 |  LỖI: OutOfMemoryError: CUDA out of memory. Tried to allocate 3.61 GiB. GPU 1 has a total capacity of 14.56 GiB of which 1.27  |
✔ XONG THỬ DOTS
```

## ct.log (sửa 81 phút trước)
```
## Chi tiết chạy
| trang | khối dots | dòng | tách dòng | dots (s) | đọc dòng 4 model (s) |
|---|---|---:|---|---:|---:|
| image_1 | 12 {'Page-header': 1, 'List-item': 3, 'Text': 5, 'Picture': 3} | 24 | chieu_ngang, kraken_muharaf | 85 | 142 |
| image_2 | 40 {'Section-header': 2, 'Text': 33, 'Picture': 5} | 36 | chieu_ngang, kraken_muharaf | 165 | 247 |
| image_3 | 0 {} | 0 |  | 1589 | 0 |
| image_4 | 11 {'Text': 7, 'Picture': 2, 'Caption': 1, 'Page-footer': 1} | 19 | chieu_ngang, kraken_muharaf | 39 | 91 |
✔ XONG CHẤM TRANG
```

