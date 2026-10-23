# Trạng thái server — 2026-10-23 06:37 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 4 hours, 33 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.8G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10181 MiB, 15360 MiB, 82 %
Tesla T4, 9493 MiB, 15360 MiB, 98 %
30480, 434 MiB, /kaggle/working/venvs/adoc/bin/python
30478, 9744 MiB, /kaggle/working/venvs/adoc/bin/python
30480, 9490 MiB, /kaggle/working/venvs/adoc/bin/python
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[n1] [06:36:06]    mtrang_kno50 · ft3 · phần 21: 50 dòng, 2.83 s/dòng · còn ~10 phần · RAM trống 25.1 GB` |

## dot1.log (sửa 2 phút trước)
```
[n0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit ea643bc) — dot1 doc N: mtrang_kno50 ft3 phần 15
[n0] [06:28:30]    mtrang_kno50 · ft3 · phần 17: 50 dòng, 2.07 s/dòng · còn ~14 phần · RAM trống 25.1 GB
[n1] [06:28:49]    mtrang_kno50 · ft3 · phần 16: 50 dòng, 4.91 s/dòng · còn ~15 phần · RAM trống 25.1 GB
[n1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit f0d03d4) — dot1 doc N: mtrang_kno50 ft3 phần 16
[n0] [06:30:25]    mtrang_kno50 · ft3 · phần 18: 50 dòng, 2.26 s/dòng · còn ~13 phần · RAM trống 25.2 GB
[n1] [06:33:43]    mtrang_kno50 · ft3 · phần 19: 50 dòng, 5.83 s/dòng · còn ~12 phần · RAM trống 25.0 GB
[n0] [06:35:53]    mtrang_kno50 · ft3 · phần 20: 50 dòng, 6.54 s/dòng · còn ~11 phần · RAM trống 25.1 GB
[n1] [06:36:06]    mtrang_kno50 · ft3 · phần 21: 50 dòng, 2.83 s/dòng · còn ~10 phần · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 230 phút trước)
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

