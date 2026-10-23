# Trạng thái server — 2026-10-23 04:57 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 2 hours, 53 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.8G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10181 MiB, 15360 MiB, 29 %
Tesla T4, 9489 MiB, 15360 MiB, 35 %
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[n1] [04:57:03]    mtrang_kno15 · ft3 · phần 5: 50 dòng, 4.05 s/dòng · còn ~88 phần · RAM trống 25.0 GB` |

## dot1.log (sửa 0 phút trước)
```
[n0] [04:49:35]    mtrang_kno15 · ft3 · phần 1: 50 dòng, 1.56 s/dòng · còn ~92 phần · RAM trống 25.0 GB
[n1] [04:50:17]    mtrang_kno15 · ft3 · phần 0: 50 dòng, 2.44 s/dòng · còn ~93 phần · RAM trống 25.1 GB
[n0] [04:51:05]    mtrang_kno15 · ft3 · phần 2: 50 dòng, 1.79 s/dòng · còn ~91 phần · RAM trống 25.1 GB
[n1] [04:53:40]    mtrang_kno15 · ft3 · phần 3: 50 dòng, 4.03 s/dòng · còn ~90 phần · RAM trống 25.0 GB
[n0] [04:54:28]    mtrang_kno15 · ft3 · phần 4: 50 dòng, 4.05 s/dòng · còn ~89 phần · RAM trống 25.0 GB
[n0] [04:56:55]    mtrang_kno15 · ft3 · phần 6: 50 dòng, 2.92 s/dòng · còn ~87 phần · RAM trống 24.9 GB
[n0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit c344f0a) — dot1 doc N: mtrang_kno15 ft3 phần 6
[n1] [04:57:03]    mtrang_kno15 · ft3 · phần 5: 50 dòng, 4.05 s/dòng · còn ~88 phần · RAM trống 25.0 GB
```

## cai_adoc.log (sửa 130 phút trước)
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

