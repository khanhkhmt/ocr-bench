# Trạng thái server — 2026-10-20 10:37 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 8 hours, 24 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.4G   17G  18% /kaggle/working
- RAM: Mem:              31           5           0           0          24          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 31 %
Tesla T4, 8351 MiB, 15360 MiB, 31 %
100096, 8640 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
100100, 450 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
100100, 8348 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[b1] [10:37:40]    omar_B · ft4 · phần 3: 50 dòng, 3.43 s/dòng · còn ~229 phần · RAM trống 25.1 GB` |

## dot1.log (sửa 0 phút trước)
```
[b0] [10:31:29]    giulai_B · ft3 · phần 8: 50 dòng, 2.82 s/dòng · còn ~234 phần · RAM trống 25.1 GB
[b0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 5d57066) — dot1 doc B: giulai_B ft3 phần 8
[b1] [10:32:09]    giulai_B · ft3 · phần 9: 50 dòng, 2.73 s/dòng · còn ~233 phần · RAM trống 25.1 GB
[b1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 6c60eae) — dot1 doc B: giulai_B ft3 phần 9
[b0] [10:34:13]    omar_B · ft4 · phần 0: 50 dòng, 3.21 s/dòng · còn ~232 phần · RAM trống 25.1 GB
[b1] [10:34:48]    omar_B · ft4 · phần 1: 50 dòng, 3.13 s/dòng · còn ~231 phần · RAM trống 25.1 GB
[b0] [10:37:09]    omar_B · ft4 · phần 2: 50 dòng, 3.50 s/dòng · còn ~230 phần · RAM trống 25.1 GB
[b1] [10:37:40]    omar_B · ft4 · phần 3: 50 dòng, 3.43 s/dòng · còn ~229 phần · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 473 phút trước)
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

