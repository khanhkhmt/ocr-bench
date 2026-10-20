# Trạng thái server — 2026-10-20 08:07 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 5 hours, 53 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.4G   17G  18% /kaggle/working
- RAM: Mem:              31           5           0           0          24          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 31 %
Tesla T4, 8351 MiB, 15360 MiB, 34 %
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[g1] [08:06:47]    muharaf_A · ft3_s050 · phần 5: 50 dòng, 2.50 s/dòng · còn ~93 phần · RAM trống 25.1 GB` |

## dot1.log (sửa 1 phút trước)
```
[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 5450cac) — dot1 doc A: omar_A ft3_s050 phần 8
[g1] [08:00:16]    omar_A · ft3_s050 · phần 9: 50 dòng, 3.19 s/dòng · còn ~99 phần · RAM trống 25.1 GB
[g0] [08:01:38]    muharaf_A · ft3_s050 · phần 0: 50 dòng, 2.66 s/dòng · còn ~98 phần · RAM trống 25.1 GB
[g1] [08:02:24]    muharaf_A · ft3_s050 · phần 1: 50 dòng, 2.55 s/dòng · còn ~97 phần · RAM trống 25.1 GB
[g0] [08:03:49]    muharaf_A · ft3_s050 · phần 2: 50 dòng, 2.62 s/dòng · còn ~96 phần · RAM trống 25.1 GB
[g1] [08:04:41]    muharaf_A · ft3_s050 · phần 3: 50 dòng, 2.74 s/dòng · còn ~95 phần · RAM trống 25.1 GB
[g0] [08:06:14]    muharaf_A · ft3_s050 · phần 4: 50 dòng, 2.89 s/dòng · còn ~94 phần · RAM trống 25.1 GB
[g1] [08:06:47]    muharaf_A · ft3_s050 · phần 5: 50 dòng, 2.50 s/dòng · còn ~93 phần · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 322 phút trước)
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

