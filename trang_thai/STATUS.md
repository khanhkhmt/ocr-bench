# Trạng thái server — 2026-10-23 05:37 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 3 hours, 33 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.8G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10181 MiB, 15360 MiB, 35 %
Tesla T4, 9491 MiB, 15360 MiB, 29 %
30480, 434 MiB, /kaggle/working/venvs/adoc/bin/python
30478, 9744 MiB, /kaggle/working/venvs/adoc/bin/python
30480, 9488 MiB, /kaggle/working/venvs/adoc/bin/python
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[n0] [05:36:58]    mtrang_kno30 · ft3 · phần 7: 50 dòng, 2.69 s/dòng · còn ~55 phần · RAM trống 25.1 GB` |

## dot1.log (sửa 1 phút trước)
```
[n1] [05:29:25]    mtrang_kno30 · ft3 · phần 2: 50 dòng, 1.98 s/dòng · còn ~60 phần · RAM trống 25.1 GB
[n0] [05:31:20]    mtrang_kno30 · ft3 · phần 3: 50 dòng, 3.99 s/dòng · còn ~59 phần · RAM trống 25.0 GB
[n0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 7495aad) — dot1 doc N: mtrang_kno30 ft3 phần 3
[n1] [05:33:15]    mtrang_kno30 · ft3 · phần 4: 50 dòng, 4.59 s/dòng · còn ~58 phần · RAM trống 25.0 GB
[n1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 17c68a0) — dot1 doc N: mtrang_kno30 ft3 phần 4
[n0] [05:34:43]    mtrang_kno30 · ft3 · phần 5: 50 dòng, 4.00 s/dòng · còn ~57 phần · RAM trống 25.0 GB
[n1] [05:35:56]    mtrang_kno30 · ft3 · phần 6: 50 dòng, 3.15 s/dòng · còn ~56 phần · RAM trống 25.1 GB
[n0] [05:36:58]    mtrang_kno30 · ft3 · phần 7: 50 dòng, 2.69 s/dòng · còn ~55 phần · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 170 phút trước)
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

