# Trạng thái server — 2026-10-23 06:27 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 4 hours, 23 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.8G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10181 MiB, 15360 MiB, 36 %
Tesla T4, 9493 MiB, 15360 MiB, 32 %
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[n0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit ea643bc) — dot1 doc N: mtrang_kno50 ft3 phần 15` |

## dot1.log (sửa 1 phút trước)
```
[n1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 7b04240) — dot1 doc N: mtrang_kno50 ft3 phần 9
[n0] [06:18:42]    mtrang_kno50 · ft3 · phần 10: 50 dòng, 2.50 s/dòng · còn ~21 phần · RAM trống 25.1 GB
[n1] [06:21:46]    mtrang_kno50 · ft3 · phần 11: 50 dòng, 4.37 s/dòng · còn ~20 phần · RAM trống 25.1 GB
[n0] [06:22:01]    mtrang_kno50 · ft3 · phần 12: 50 dòng, 3.97 s/dòng · còn ~19 phần · RAM trống 25.1 GB
[n0] [06:24:35]    mtrang_kno50 · ft3 · phần 14: 50 dòng, 3.06 s/dòng · còn ~17 phần · RAM trống 25.1 GB
[n1] [06:24:43]    mtrang_kno50 · ft3 · phần 13: 50 dòng, 3.52 s/dòng · còn ~18 phần · RAM trống 25.1 GB
[n0] [06:26:44]    mtrang_kno50 · ft3 · phần 15: 50 dòng, 2.56 s/dòng · còn ~16 phần · RAM trống 25.2 GB
[n0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit ea643bc) — dot1 doc N: mtrang_kno50 ft3 phần 15
```

## cai_adoc.log (sửa 220 phút trước)
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

