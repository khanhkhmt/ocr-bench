# Trạng thái server — 2026-10-23 04:17 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 2 hours, 13 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.8G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10181 MiB, 15360 MiB, 35 %
Tesla T4, 9073 MiB, 15360 MiB, 33 %
30480, 434 MiB, /kaggle/working/venvs/adoc/bin/python
30478, 9744 MiB, /kaggle/working/venvs/adoc/bin/python
30480, 9070 MiB, /kaggle/working/venvs/adoc/bin/python
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[n1] [04:16:35]    mtrang_kno00 · ft3 · phần 3: 50 dòng, 3.84 s/dòng · còn ~121 phần · RAM trống 25.1 GB` |

## dot1.log (sửa 1 phút trước)
```
[n0] [04:11:16]    ✔ tự kiểm: ft3 / gốc đọc giống hệt sản phẩm; tron34 bật đủ 2 adapter với hệ số ½
[n1] [04:11:19]    ✔ tự kiểm: ft3 / gốc đọc giống hệt sản phẩm; tron34 bật đủ 2 adapter với hệ số ½
[n0] [04:12:33]    mtrang_kno00 · ft3 · phần 1: 50 dòng, 1.53 s/dòng · còn ~123 phần · RAM trống 25.2 GB
[n0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 5ef41f8) — dot1 doc N: mtrang_kno00 ft3 phần 1
[n1] [04:13:20]    mtrang_kno00 · ft3 · phần 0: 50 dòng, 2.42 s/dòng · còn ~123 phần · RAM trống 25.2 GB
[n1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 6248de9) — dot1 doc N: mtrang_kno00 ft3 phần 0
[n0] [04:14:19]    mtrang_kno00 · ft3 · phần 2: 50 dòng, 2.07 s/dòng · còn ~122 phần · RAM trống 25.2 GB
[n1] [04:16:35]    mtrang_kno00 · ft3 · phần 3: 50 dòng, 3.84 s/dòng · còn ~121 phần · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 90 phút trước)
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

