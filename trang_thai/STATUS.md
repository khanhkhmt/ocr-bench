# Trạng thái server — 2026-10-20 04:26 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 2 hours, 12 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.2G   17G  17% /kaggle/working
- RAM: Mem:              31           6           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 45 %
Tesla T4, 8351 MiB, 15360 MiB, 23 %
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[mt] [04:25:26]    [50/66] TAttallah2020-024: 21 dòng chuẩn · Kraken 18 dòng (90.2 s) · RAM trống 24.9 GB` |

## dot1.log (sửa 1 phút trước)
```
[g1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit d756815) — dot1 doc A: muharaf_A ft4 phần 5
[g0] [04:21:30]    muharaf_A · ft4 · phần 4: 50 dòng, 4.06 s/dòng · còn ~220 phần · RAM trống 24.3 GB
[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 173582e) — dot1 doc A: muharaf_A ft4 phần 4
[mt] [04:22:08]    [48/66] QBat3D_0010r: 17 dòng chuẩn · Kraken 17 dòng (96.4 s) · RAM trống 24.7 GB
[mt] [04:23:49]    [49/66] ST1A_197_09: 17 dòng chuẩn · Kraken 17 dòng (94.1 s) · RAM trống 24.8 GB
[g1] [04:24:13]    muharaf_A · ft4 · phần 6: 50 dòng, 3.45 s/dòng · còn ~218 phần · RAM trống 24.5 GB
[g0] [04:25:06]    muharaf_A · ft4 · phần 7: 50 dòng, 4.28 s/dòng · còn ~217 phần · RAM trống 24.4 GB
[mt] [04:25:26]    [50/66] TAttallah2020-024: 21 dòng chuẩn · Kraken 18 dòng (90.2 s) · RAM trống 24.9 GB
```

## cai_adoc.log (sửa 102 phút trước)
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

