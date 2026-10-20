# Trạng thái server — 2026-10-20 04:06 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 1 hour, 52 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.1G   17G  16% /kaggle/working
- RAM: Mem:              31           6           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 26 %
Tesla T4, 8351 MiB, 15360 MiB, 28 %
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[mt] [04:05:55]    [38/66] MUKF4A_15_29r: 31 dòng chuẩn · Kraken 26 dòng (96.1 s) · RAM trống 24.9 GB` |

## dot1.log (sửa 1 phút trước)
```
[mt] [04:00:47]    [35/66] MG1_150_01: 22 dòng chuẩn · Kraken 22 dòng (104.8 s) · RAM trống 25.0 GB
[g0] [04:00:49]    omar_A · ft4 · phần 2: 50 dòng, 4.35 s/dòng · còn ~232 phần · RAM trống 25.0 GB
[g1] [04:01:03]    omar_A · ft4 · phần 3: 50 dòng, 4.52 s/dòng · còn ~231 phần · RAM trống 24.8 GB
[mt] [04:02:36]    [36/66] MK2A_08_04r: 12 dòng chuẩn · Kraken 18 dòng (102.3 s) · RAM trống 25.0 GB
[mt] [04:04:07]    [37/66] MUKF4A_02_082r: 35 dòng chuẩn · Kraken 37 dòng (82.5 s) · RAM trống 25.0 GB
[g0] [04:04:28]    omar_A · ft4 · phần 4: 50 dòng, 4.37 s/dòng · còn ~230 phần · RAM trống 24.8 GB
[g1] [04:04:53]    omar_A · ft4 · phần 5: 50 dòng, 4.59 s/dòng · còn ~229 phần · RAM trống 24.5 GB
[mt] [04:05:55]    [38/66] MUKF4A_15_29r: 31 dòng chuẩn · Kraken 26 dòng (96.1 s) · RAM trống 24.9 GB
```

## cai_adoc.log (sửa 81 phút trước)
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

