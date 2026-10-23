# Trạng thái server — 2026-10-23 07:37 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 5 hours, 33 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.9G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10153 MiB, 15360 MiB, 31 %
Tesla T4, 9531 MiB, 15360 MiB, 31 %
63988, 434 MiB, /kaggle/working/venvs/adoc/bin/python
63985, 9716 MiB, /kaggle/working/venvs/adoc/bin/python
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[b1] [07:37:25]    omar_B · ft1_s050 · phần 0: 50 dòng, 3.37 s/dòng · còn ~174 phần · RAM trống 25.1 GB` |

## dot1.log (sửa 1 phút trước)
```
[b0] [07:32:44]    mtrang_kraken · ft4 · phần 24: 50 dòng, 1.50 s/dòng · còn ~178 phần · RAM trống 25.2 GB
[b0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 93c1619) — dot1 doc B: mtrang_kraken ft4 phần 24
[b0] [07:34:25]    mtrang_kraken · ft4 · phần 26: 50 dòng, 1.95 s/dòng · còn ~176 phần · RAM trống 25.1 GB
[b1] [07:34:34]    mtrang_kraken · ft4 · phần 25: 50 dòng, 3.25 s/dòng · còn ~177 phần · RAM trống 25.1 GB
[b1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit cf18040) — dot1 doc B: mtrang_kraken ft4 phần 25
[b0] [07:34:42]    mtrang_kraken · ft4 · phần 27: 9 dòng, 1.76 s/dòng · còn ~175 phần · RAM trống 25.1 GB
[b0] [07:37:18]    omar_B · ft1_s050 · phần 1: 50 dòng, 3.12 s/dòng · còn ~173 phần · RAM trống 25.1 GB
[b1] [07:37:25]    omar_B · ft1_s050 · phần 0: 50 dòng, 3.37 s/dòng · còn ~174 phần · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 290 phút trước)
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

