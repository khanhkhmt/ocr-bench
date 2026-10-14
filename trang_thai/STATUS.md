# Trạng thái server — 2026-10-14 07:21 UTC

**Còn sống** · định kỳ

- máy: `0b994473a1f2` · up 1 hour, 31 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `a527f19 htr_test/thu_dots.py: thử dots trên trang thật — phóng ảnh ×1/×2/×1,5 × 3 cách đọc (bố cục đầy đủ / bố cục rồi đọc từng khối / chỉ chữ), lưu output thô + cứu khối từ JSON bị cắt; 2 GPU chung hàng đợi, lỗi một lượt không dừng, chạy lại = đi tiếp (lượt lỗi chạy lại)` (nhánh `thu-2-model-htr`)
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

## ct.log (sửa 24 phút trước)
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

