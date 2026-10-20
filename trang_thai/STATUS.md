# Trạng thái server — 2026-10-20 03:56 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 1 hour, 42 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.0G   17G  15% /kaggle/working
- RAM: Mem:              31           6           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 28 %
Tesla T4, 8351 MiB, 15360 MiB, 25 %
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[mt] [03:56:08]    [32/66] KEllis2020-140d: 16 dòng chuẩn · Kraken 16 dòng (86.8 s) · RAM trống 25.0 GB` |

## dot1.log (sửa 0 phút trước)
```
[g1] [03:50:06]    giulai_A · ft3 · phần 6: 50 dòng, 3.51 s/dòng · còn ~238 phần · RAM trống 24.5 GB
[g0] [03:50:24]    giulai_A · ft3 · phần 7: 50 dòng, 3.85 s/dòng · còn ~237 phần · RAM trống 24.5 GB
[mt] [03:51:17]    [29/66] JoM_Kobayat_0324: 30 dòng chuẩn · Kraken 28 dòng (110.3 s) · RAM trống 25.0 GB
[mt] [03:52:59]    [30/66] JoM_Kobayat_0690: 32 dòng chuẩn · Kraken 28 dòng (96.3 s) · RAM trống 25.0 GB
[g1] [03:53:22]    giulai_A · ft3 · phần 8: 50 dòng, 3.92 s/dòng · còn ~236 phần · RAM trống 24.6 GB
[g0] [03:53:28]    giulai_A · ft3 · phần 9: 50 dòng, 3.66 s/dòng · còn ~235 phần · RAM trống 24.5 GB
[mt] [03:54:35]    [31/66] KEllis2018-139a: 22 dòng chuẩn · Kraken 27 dòng (87.7 s) · RAM trống 25.0 GB
[mt] [03:56:08]    [32/66] KEllis2020-140d: 16 dòng chuẩn · Kraken 16 dòng (86.8 s) · RAM trống 25.0 GB
```

## cai_adoc.log (sửa 71 phút trước)
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

