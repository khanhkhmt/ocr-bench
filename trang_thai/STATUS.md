# Trạng thái server — 2026-10-23 05:07 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 3 hours, 3 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.8G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10181 MiB, 15360 MiB, 35 %
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[n1] [05:07:20]    mtrang_kno15 · ft3 · phần 14: 50 dòng, 3.09 s/dòng · còn ~79 phần · RAM trống 25.1 GB` |

## dot1.log (sửa 0 phút trước)
```
[n1] [04:59:16]    mtrang_kno15 · ft3 · phần 8: 50 dòng, 2.65 s/dòng · còn ~85 phần · RAM trống 25.1 GB
[n1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit ba3b9bb) — dot1 doc N: mtrang_kno15 ft3 phần 8
[n0] [05:00:41]    mtrang_kno15 · ft3 · phần 9: 50 dòng, 1.82 s/dòng · còn ~84 phần · RAM trống 25.1 GB
[n1] [05:01:25]    mtrang_kno15 · ft3 · phần 10: 50 dòng, 2.53 s/dòng · còn ~83 phần · RAM trống 25.1 GB
[n0] [05:04:03]    mtrang_kno15 · ft3 · phần 11: 50 dòng, 4.02 s/dòng · còn ~82 phần · RAM trống 25.0 GB
[n1] [05:04:45]    mtrang_kno15 · ft3 · phần 12: 50 dòng, 3.97 s/dòng · còn ~81 phần · RAM trống 25.0 GB
[n0] [05:06:47]    mtrang_kno15 · ft3 · phần 13: 50 dòng, 3.27 s/dòng · còn ~80 phần · RAM trống 25.1 GB
[n1] [05:07:20]    mtrang_kno15 · ft3 · phần 14: 50 dòng, 3.09 s/dòng · còn ~79 phần · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 140 phút trước)
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

