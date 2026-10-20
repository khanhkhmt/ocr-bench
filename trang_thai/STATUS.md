# Trạng thái server — 2026-10-20 09:47 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 7 hours, 33 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.4G   17G  18% /kaggle/working
- RAM: Mem:              31           5           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10159 MiB, 15360 MiB, 36 %
Tesla T4, 9149 MiB, 15360 MiB, 32 %
9277, 450 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
14233, 9706 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
9277, 9146 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[g0] [09:46:28]    mtrang_kraken · ft3 · phần 19: 50 dòng, 4.92 s/dòng · còn ~9 phần · RAM trống 25.0 GB` |

## dot1.log (sửa 1 phút trước)
```
[g0] [09:38:54]    mtrang_kraken · ft3 · phần 14: 50 dòng, 2.89 s/dòng · còn ~14 phần · RAM trống 25.0 GB
[g1] [09:39:32]    mtrang_kraken · ft3 · phần 15: 50 dòng, 2.41 s/dòng · còn ~13 phần · RAM trống 25.0 GB
[g1] [09:41:07]    mtrang_kraken · ft3 · phần 17: 50 dòng, 1.89 s/dòng · còn ~11 phần · RAM trống 25.1 GB
[g1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 433f5cc) — dot1 doc A: mtrang_kraken ft3 phần 17
[g0] [09:42:20]    mtrang_kraken · ft3 · phần 16: 50 dòng, 4.11 s/dòng · còn ~12 phần · RAM trống 25.0 GB
[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit f80aa07) — dot1 doc A: mtrang_kraken ft3 phần 16
[g1] [09:42:53]    mtrang_kraken · ft3 · phần 18: 50 dòng, 2.08 s/dòng · còn ~10 phần · RAM trống 25.0 GB
[g0] [09:46:28]    mtrang_kraken · ft3 · phần 19: 50 dòng, 4.92 s/dòng · còn ~9 phần · RAM trống 25.0 GB
```

## cai_adoc.log (sửa 422 phút trước)
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

