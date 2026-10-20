# Trạng thái server — 2026-10-20 04:46 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 2 hours, 32 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.3G   17G  17% /kaggle/working
- RAM: Mem:              31           6           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 40 %
Tesla T4, 8351 MiB, 15360 MiB, 0 %
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[g1] [04:46:41]    omar_A · ft1_s050 · phần 0: 50 dòng, 4.66 s/dòng · còn ~204 phần · RAM trống 24.6 GB` |

## dot1.log (sửa 0 phút trước)
```
[g0] [04:39:51]    giulai_A · ft4 · phần 7: 50 dòng, 3.76 s/dòng · còn ~207 phần · RAM trống 24.6 GB
[mt] [04:40:44]    [59/66] YS_4A_011j: 11 dòng chuẩn · Kraken 14 dòng (94.9 s) · RAM trống 25.0 GB
[mt] [04:42:29]    [60/66] kc0061_01_04_19210417_001: 17 dòng chuẩn · Kraken 18 dòng (99.8 s) · RAM trống 25.0 GB
[g1] [04:42:48]    giulai_A · ft4 · phần 8: 50 dòng, 3.98 s/dòng · còn ~206 phần · RAM trống 24.6 GB
[g0] [04:42:59]    giulai_A · ft4 · phần 9: 50 dòng, 3.76 s/dòng · còn ~205 phần · RAM trống 24.5 GB
[mt] [04:44:20]    [61/66] kc0061_01_04_19210504_001b: 20 dòng chuẩn · Kraken 20 dòng (103.4 s) · RAM trống 25.0 GB
[mt] [04:45:59]    [62/66] kc0066_01_01_1873diary_009: 14 dòng chuẩn · Kraken 15 dòng (92.5 s) · RAM trống 25.0 GB
[g1] [04:46:41]    omar_A · ft1_s050 · phần 0: 50 dòng, 4.66 s/dòng · còn ~204 phần · RAM trống 24.6 GB
```

## cai_adoc.log (sửa 122 phút trước)
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

