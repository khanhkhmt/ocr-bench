# Trạng thái server — 2026-10-14 07:24 UTC

**Còn sống** · td có lỗi trong log (vẫn chạy)

- máy: `0b994473a1f2` · up 1 hour, 34 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `a527f19 htr_test/thu_dots.py: thử dots trên trang thật — phóng ảnh ×1/×2/×1,5 × 3 cách đọc (bố cục đầy đủ / bố cục rồi đọc từng khối / chỉ chữ), lưu output thô + cứu khối từ JSON bị cắt; 2 GPU chung hàng đợi, lỗi một lượt không dừng, chạy lại = đi tiếp (lượt lỗi chạy lại)` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.2G   18G  11% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 3 MiB, 15360 MiB, 0 %
Tesla T4, 9995 MiB, 15360 MiB, 96 %
23223, 9992 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
hop_thu: 1 windows (created Wed Oct 14 06:06:05 2026)
td: 1 windows (created Wed Oct 14 07:22:07 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| ct | XONG | 1 | 0 | 2026-10-14 06:10 UTC | `✔ XONG CHẤM TRANG` |
| td | LỖI | 1 | 0 | 2026-10-14 07:22 UTC | `Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.` |

## td.log (sửa 2 phút trước)
```
W0000 00:00:1791962534.641858   23257 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791962534.641885   23257 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791962534.641888   23257 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1791962534.641890   23257 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-14 07:22:14.648284: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
   dots nạp xong trên cuda:1
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
```

## ct.log (sửa 27 phút trước)
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

