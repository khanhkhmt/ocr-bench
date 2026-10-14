# Trạng thái server — 2026-10-14 08:09 UTC

**Còn sống** · định kỳ

- máy: `0b994473a1f2` · up 2 hours, 19 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `f13093d thu_dots: nạp dots lần lượt trên từng GPU (hai luồng cùng snapshot_download → tqdm AttributeError '_lock', GPU thứ hai không nạp được)` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.2G   18G  11% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 12797 MiB, 15360 MiB, 100 %
Tesla T4, 11597 MiB, 15360 MiB, 99 %
26575, 12794 MiB, /kaggle/working/venvs/dots/bin/python
26575, 11594 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
hop_thu: 1 windows (created Wed Oct 14 06:06:05 2026)
td: 1 windows (created Wed Oct 14 07:33:29 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| ct | XONG | 1 | 0 | 2026-10-14 06:10 UTC | `✔ XONG CHẤM TRANG` |
| td | LỖI | 2 | 0 | 2026-10-14 07:33 UTC | `Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.` |

## td.log (sửa 0 phút trước)
```
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
✔ image_1 chi_chu ×1.5 [cuda:0]: 89.6% · 421 token · 79 s
✔ GITHUB: đã đẩy lên nhánh results-htr/thu_dots (commit 4bbfa2c) — thử dots: image_1 chi_chu ×1.5 (29/36)
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
```

## ct.log (sửa 72 phút trước)
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

