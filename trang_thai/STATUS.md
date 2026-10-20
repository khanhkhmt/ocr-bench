# Trạng thái server — 2026-10-20 03:26 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 1 hour, 12 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.8G   17G  15% /kaggle/working
- RAM: Mem:              31           5           1           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 15 %
Tesla T4, 8351 MiB, 15360 MiB, 18 %
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[mt] [03:26:26]    [15/66] FC2C_11_13: 11 dòng chuẩn · Kraken 11 dòng (96.3 s) · RAM trống 24.9 GB` |

## dot1.log (sửa 0 phút trước)
```
[mt] [03:21:17]    [12/66] EAK1A_192r: 17 dòng chuẩn · Kraken 17 dòng (93.2 s) · RAM trống 25.0 GB
[g1] [03:21:54]    omar_A · ft3 · phần 8: 50 dòng, 4.54 s/dòng · còn ~256 phần · RAM trống 24.2 GB
[mt] [03:23:01]    [13/66] ES1D_19_02: 20 dòng chuẩn · Kraken 19 dòng (93.7 s) · RAM trống 24.8 GB
[g0] [03:23:10]    omar_A · ft3 · phần 9: 50 dòng, 4.31 s/dòng · còn ~255 phần · RAM trống 24.9 GB
[mt] [03:24:42]    [14/66] FC2C_11_11: 11 dòng chuẩn · Kraken 11 dòng (93.7 s) · RAM trống 24.9 GB
[g1] [03:25:10]    muharaf_A · ft3 · phần 0: 50 dòng, 3.93 s/dòng · còn ~254 phần · RAM trống 24.5 GB
[g0] [03:26:06]    muharaf_A · ft3 · phần 1: 50 dòng, 3.51 s/dòng · còn ~253 phần · RAM trống 24.4 GB
[mt] [03:26:26]    [15/66] FC2C_11_13: 11 dòng chuẩn · Kraken 11 dòng (96.3 s) · RAM trống 24.9 GB
```

## cai_adoc.log (sửa 41 phút trước)
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

