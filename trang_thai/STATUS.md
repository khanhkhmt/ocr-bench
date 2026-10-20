# Trạng thái server — 2026-10-20 03:46 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 1 hour, 32 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.9G   17G  15% /kaggle/working
- RAM: Mem:              31           6           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 22 %
Tesla T4, 8351 MiB, 15360 MiB, 32 %
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[mt] [03:45:36]    [26/66] JoM_Kobayat_0020: 24 dòng chuẩn · Kraken 23 dòng (107.4 s) · RAM trống 25.1 GB` |

## dot1.log (sửa 1 phút trước)
```
[g0] [03:41:30]    giulai_A · ft3 · phần 1: 50 dòng, 3.28 s/dòng · còn ~243 phần · RAM trống 24.6 GB
[mt] [03:42:10]    [24/66] JEH2F1_30_04v: 25 dòng chuẩn · Kraken 25 dòng (93.7 s) · RAM trống 25.1 GB
[mt] [03:43:41]    [25/66] JPK2B_096_04: 27 dòng chuẩn · Kraken 26 dòng (87.9 s) · RAM trống 25.1 GB
[g1] [03:44:16]    giulai_A · ft3 · phần 2: 50 dòng, 3.46 s/dòng · còn ~242 phần · RAM trống 24.6 GB
[g1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit ccdfe38) — dot1 doc A: giulai_A ft3 phần 2
[g0] [03:44:28]    giulai_A · ft3 · phần 3: 50 dòng, 3.55 s/dòng · còn ~241 phần · RAM trống 24.6 GB
[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 7086360) — dot1 doc A: giulai_A ft3 phần 3
[mt] [03:45:36]    [26/66] JoM_Kobayat_0020: 24 dòng chuẩn · Kraken 23 dòng (107.4 s) · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 61 phút trước)
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

