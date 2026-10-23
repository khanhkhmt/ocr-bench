# Trạng thái server — 2026-10-23 04:47 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 2 hours, 43 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.8G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10181 MiB, 15360 MiB, 26 %
Tesla T4, 9489 MiB, 15360 MiB, 30 %
30480, 434 MiB, /kaggle/working/venvs/adoc/bin/python
30478, 9744 MiB, /kaggle/working/venvs/adoc/bin/python
30480, 9486 MiB, /kaggle/working/venvs/adoc/bin/python
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[n0] [04:45:50]    mtrang_kno00 · ft3 · phần 27: 9 dòng, 1.77 s/dòng · còn ~97 phần · RAM trống 25.0 GB` |

## dot1.log (sửa 2 phút trước)
```
[n0] [04:40:25]    mtrang_kno00 · ft3 · phần 20: 50 dòng, 6.10 s/dòng · còn ~104 phần · RAM trống 25.1 GB
[n1] [04:42:45]    mtrang_kno00 · ft3 · phần 22: 50 dòng, 3.30 s/dòng · còn ~102 phần · RAM trống 25.0 GB
[n0] [04:42:55]    mtrang_kno00 · ft3 · phần 23: 50 dòng, 2.99 s/dòng · còn ~101 phần · RAM trống 25.0 GB
[n1] [04:44:04]    mtrang_kno00 · ft3 · phần 24: 50 dòng, 1.55 s/dòng · còn ~100 phần · RAM trống 25.0 GB
[n0] [04:45:31]    mtrang_kno00 · ft3 · phần 25: 50 dòng, 3.10 s/dòng · còn ~99 phần · RAM trống 25.1 GB
[n0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 045a103) — dot1 doc N: mtrang_kno00 ft3 phần 25
[n1] [04:45:45]    mtrang_kno00 · ft3 · phần 26: 50 dòng, 2.00 s/dòng · còn ~98 phần · RAM trống 25.0 GB
[n0] [04:45:50]    mtrang_kno00 · ft3 · phần 27: 9 dòng, 1.77 s/dòng · còn ~97 phần · RAM trống 25.0 GB
```

## cai_adoc.log (sửa 120 phút trước)
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

