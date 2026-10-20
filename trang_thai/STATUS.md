# Trạng thái server — 2026-10-20 04:16 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 2 hours, 2 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.1G   17G  16% /kaggle/working
- RAM: Mem:              31           6           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 30 %
Tesla T4, 8351 MiB, 15360 MiB, 30 %
9277, 450 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
14233, 8640 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
9277, 8348 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[g1] [04:15:24]    muharaf_A · ft4 · phần 0: 50 dòng, 3.94 s/dòng · còn ~224 phần · RAM trống 24.6 GB` |

## dot1.log (sửa 1 phút trước)
```
[mt] [04:10:36]    [41/66] Nasrallah-Al001-014h: 13 dòng chuẩn · Kraken 13 dòng (83.7 s) · RAM trống 24.9 GB
[mt] [04:11:58]    [42/66] Nasrallah-Al001-034j: 13 dòng chuẩn · Kraken 34 dòng (79.3 s) · RAM trống 25.0 GB
[g1] [04:12:07]    omar_A · ft4 · phần 9: 50 dòng, 4.20 s/dòng · còn ~225 phần · RAM trống 24.7 GB
[g0] [04:12:20]    omar_A · ft4 · phần 8: 50 dòng, 4.47 s/dòng · còn ~225 phần · RAM trống 24.5 GB
[mt] [04:13:23]    [43/66] Oussani2018-0292e_1: 26 dòng chuẩn · Kraken 22 dòng (82.9 s) · RAM trống 25.0 GB
[g0] [04:14:57]    muharaf_A · ft4 · phần 1: 50 dòng, 3.14 s/dòng · còn ~223 phần · RAM trống 24.5 GB
[mt] [04:15:01]    [44/66] QAJE5G_04_03r: 27 dòng chuẩn · Kraken 28 dòng (93.8 s) · RAM trống 25.0 GB
[g1] [04:15:24]    muharaf_A · ft4 · phần 0: 50 dòng, 3.94 s/dòng · còn ~224 phần · RAM trống 24.6 GB
```

## cai_adoc.log (sửa 91 phút trước)
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

