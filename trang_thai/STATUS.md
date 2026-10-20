# Trạng thái server — 2026-10-20 03:36 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 1 hour, 22 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.9G   17G  15% /kaggle/working
- RAM: Mem:              31           6           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 24 %
Tesla T4, 8351 MiB, 15360 MiB, 59 %
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[mt] [03:35:46]    [20/66] HM1B_10_24v: 25 dòng chuẩn · Kraken 26 dòng (96.9 s) · RAM trống 25.0 GB` |

## dot1.log (sửa 1 phút trước)
```
[g1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 7305d28) — dot1 doc A: muharaf_A ft3 phần 4
[g0] [03:32:01]    muharaf_A · ft3 · phần 5: 50 dòng, 3.27 s/dòng · còn ~249 phần · RAM trống 24.5 GB
[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 6a19226) — dot1 doc A: muharaf_A ft3 phần 5
[mt] [03:32:10]    [18/66] HM1B_10_02v: 25 dòng chuẩn · Kraken 27 dòng (108.6 s) · RAM trống 25.0 GB
[mt] [03:33:59]    [19/66] HM1B_10_05v: 24 dòng chuẩn · Kraken 24 dòng (100.1 s) · RAM trống 25.1 GB
[g1] [03:34:22]    muharaf_A · ft3 · phần 6: 50 dòng, 3.48 s/dòng · còn ~248 phần · RAM trống 24.6 GB
[g0] [03:35:31]    muharaf_A · ft3 · phần 7: 50 dòng, 4.15 s/dòng · còn ~247 phần · RAM trống 24.5 GB
[mt] [03:35:46]    [20/66] HM1B_10_24v: 25 dòng chuẩn · Kraken 26 dòng (96.9 s) · RAM trống 25.0 GB
```

## cai_adoc.log (sửa 51 phút trước)
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

