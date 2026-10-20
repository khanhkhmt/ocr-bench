# Trạng thái server — 2026-10-20 06:06 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 3 hours, 53 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.4G   17G  17% /kaggle/working
- RAM: Mem:              31           5           1           0          24          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 29 %
Tesla T4, 8351 MiB, 15360 MiB, 42 %
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 62c97aa) — dot1 doc A: muharaf_A tron34 phần 0` |

## dot1.log (sửa 2 phút trước)
```
[g0] [05:58:17]    omar_A · tron34 · phần 6: 50 dòng, 4.65 s/dòng · còn ~192 phần · RAM trống 25.1 GB
[g1] [05:58:35]    omar_A · tron34 · phần 7: 50 dòng, 4.36 s/dòng · còn ~191 phần · RAM trống 25.1 GB
[g0] [06:01:49]    omar_A · tron34 · phần 8: 50 dòng, 4.23 s/dòng · còn ~190 phần · RAM trống 25.1 GB
[g1] [06:02:00]    omar_A · tron34 · phần 9: 50 dòng, 4.08 s/dòng · còn ~189 phần · RAM trống 25.1 GB
[g1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit c51d4ad) — dot1 doc A: omar_A tron34 phần 9
[g1] [06:04:47]    muharaf_A · tron34 · phần 1: 50 dòng, 3.31 s/dòng · còn ~187 phần · RAM trống 25.1 GB
[g0] [06:04:51]    muharaf_A · tron34 · phần 0: 50 dòng, 3.62 s/dòng · còn ~188 phần · RAM trống 25.1 GB
[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 62c97aa) — dot1 doc A: muharaf_A tron34 phần 0
```

## cai_adoc.log (sửa 202 phút trước)
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

