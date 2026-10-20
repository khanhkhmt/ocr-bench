# Trạng thái server — 2026-10-20 09:07 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 6 hours, 53 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.4G   17G  18% /kaggle/working
- RAM: Mem:              31           5           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9947 MiB, 15360 MiB, 32 %
Tesla T4, 9145 MiB, 15360 MiB, 33 %
9277, 450 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
14233, 9494 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
9277, 9142 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
```

## Phiên tmux
```
dot1: 1 windows (created Tue Oct 20 02:47:26 2026)
hop_thu: 1 windows (created Tue Oct 20 02:41:19 2026)
init: 1 windows (created Tue Oct 20 02:40:12 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| cai_adoc | XONG | 1 | 0 | 2026-10-20 02:41 UTC | `Done. Web:  bash run_web.sh        CLI:  /kaggle/working/arabic-doc-ocr/.venv/bin/python -m arabic_doc_ocr page <file> --type printed` |
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[g1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit a705058) — dot1 doc A: mtrang_vang ft3 phần 15` |

## dot1.log (sửa 1 phút trước)
```
[g1] [08:57:37]    mtrang_vang · ft3 · phần 9: 50 dòng, 3.69 s/dòng · còn ~45 phần · RAM trống 24.8 GB
[g0] [08:59:19]    mtrang_vang · ft3 · phần 10: 50 dòng, 4.53 s/dòng · còn ~44 phần · RAM trống 24.8 GB
[g1] [09:00:26]    mtrang_vang · ft3 · phần 11: 50 dòng, 3.36 s/dòng · còn ~43 phần · RAM trống 24.8 GB
[g0] [09:02:07]    mtrang_vang · ft3 · phần 12: 50 dòng, 3.37 s/dòng · còn ~42 phần · RAM trống 24.8 GB
[g1] [09:03:23]    mtrang_vang · ft3 · phần 13: 50 dòng, 3.54 s/dòng · còn ~41 phần · RAM trống 24.8 GB
[g0] [09:05:10]    mtrang_vang · ft3 · phần 14: 50 dòng, 3.64 s/dòng · còn ~40 phần · RAM trống 24.9 GB
[g1] [09:06:40]    mtrang_vang · ft3 · phần 15: 50 dòng, 3.93 s/dòng · còn ~39 phần · RAM trống 24.9 GB
[g1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit a705058) — dot1 doc A: mtrang_vang ft3 phần 15
```

## cai_adoc.log (sửa 382 phút trước)
```
  Kraken: /root/.cache/arabic_doc_ocr/kraken_venv/bin/kraken · segmentation model: /root/.cache/arabic_doc_ocr/muharaf_seg_best.mlmodel
  RAM 31.3 GiB (free 28.2)
  disk (home) free 1051.2 GiB
  model dots-studio/dots.mocr: cached (5.7 GiB)
  model Misraj/Baseer__Nakba: cached (7.0 GiB)
  model khanh99/htr-baseer-nakba-ft: cached (0.6 GiB)
OK
Done. Web:  bash run_web.sh        CLI:  /kaggle/working/arabic-doc-ocr/.venv/bin/python -m arabic_doc_ocr page <file> --type printed
```

