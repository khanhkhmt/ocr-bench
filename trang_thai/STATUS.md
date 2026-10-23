# Trạng thái server — 2026-10-23 07:27 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 5 hours, 23 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.9G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9941 MiB, 15360 MiB, 92 %
Tesla T4, 9531 MiB, 15360 MiB, 35 %
63988, 434 MiB, /kaggle/working/venvs/adoc/bin/python
63985, 9504 MiB, /kaggle/working/venvs/adoc/bin/python
63988, 9528 MiB, /kaggle/working/venvs/adoc/bin/python
```

## Phiên tmux
```
dot1: 1 windows (created Fri Oct 23 03:47:11 2026)
hop_thu: 1 windows (created Fri Oct 23 03:47:10 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| cai_adoc | XONG | 1 | 0 | 2026-10-23 02:43 UTC | `Done. adoc — kiểm bản chép: /kaggle/working/venvs/adoc/bin/python -m adoc kiem --out /kaggle/working/kiem_adoc` |
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[b1] [07:26:55]    mtrang_kraken · ft4 · phần 19: 50 dòng, 5.34 s/dòng · còn ~183 phần · RAM trống 25.1 GB` |

## dot1.log (sửa 1 phút trước)
```
[b1] [07:18:30]    mtrang_kraken · ft4 · phần 13: 50 dòng, 3.45 s/dòng · còn ~189 phần · RAM trống 25.2 GB
[b0] [07:20:10]    mtrang_kraken · ft4 · phần 15: 50 dòng, 2.30 s/dòng · còn ~187 phần · RAM trống 25.1 GB
[b0] [07:21:43]    mtrang_kraken · ft4 · phần 17: 50 dòng, 1.83 s/dòng · còn ~185 phần · RAM trống 25.2 GB
[b0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 8f4987a) — dot1 doc B: mtrang_kraken ft4 phần 17
[b1] [07:22:24]    mtrang_kraken · ft4 · phần 16: 50 dòng, 4.68 s/dòng · còn ~186 phần · RAM trống 25.2 GB
[b1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit ee45d6a) — dot1 doc B: mtrang_kraken ft4 phần 16
[b0] [07:23:28]    mtrang_kraken · ft4 · phần 18: 50 dòng, 2.03 s/dòng · còn ~184 phần · RAM trống 25.2 GB
[b1] [07:26:55]    mtrang_kraken · ft4 · phần 19: 50 dòng, 5.34 s/dòng · còn ~183 phần · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 280 phút trước)
```
  Kraken: /root/.cache/ocr_bench_adoc/kraken_venv/bin/kraken · model tách dòng: /root/.cache/ocr_bench_adoc/muharaf_seg_best.mlmodel
  RAM 31.3 GiB (còn 27.6)
  ổ (home) còn 1033.1 GiB
  model dots-studio/dots.mocr: có (5.7 GiB)
  model Misraj/Baseer__Nakba: có (7.0 GiB)
  model khanh99/htr-baseer-nakba-ft: có (0.6 GiB)
OK
Done. adoc — kiểm bản chép: /kaggle/working/venvs/adoc/bin/python -m adoc kiem --out /kaggle/working/kiem_adoc
```

