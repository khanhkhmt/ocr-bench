# Trạng thái server — 2026-10-23 08:28 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 6 hours, 23 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.9G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10153 MiB, 15360 MiB, 28 %
Tesla T4, 9531 MiB, 15360 MiB, 35 %
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[b0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit a603f79) — dot1 doc B: mtrang_kraken ft1_s050 phần 11` |

## dot1.log (sửa 1 phút trước)
```
[b1] [08:20:38]    mtrang_kraken · ft1_s050 · phần 6: 50 dòng, 3.04 s/dòng · còn ~138 phần · RAM trống 25.2 GB
[b1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 529c300) — dot1 doc B: mtrang_kraken ft1_s050 phần 6
[b0] [08:22:13]    mtrang_kraken · ft1_s050 · phần 7: 50 dòng, 2.52 s/dòng · còn ~137 phần · RAM trống 25.2 GB
[b1] [08:22:49]    mtrang_kraken · ft1_s050 · phần 8: 50 dòng, 2.56 s/dòng · còn ~136 phần · RAM trống 25.2 GB
[b0] [08:23:44]    mtrang_kraken · ft1_s050 · phần 9: 50 dòng, 1.81 s/dòng · còn ~135 phần · RAM trống 25.2 GB
[b1] [08:24:58]    mtrang_kraken · ft1_s050 · phần 10: 50 dòng, 2.56 s/dòng · còn ~134 phần · RAM trống 25.2 GB
[b0] [08:26:57]    mtrang_kraken · ft1_s050 · phần 11: 50 dòng, 3.86 s/dòng · còn ~133 phần · RAM trống 25.1 GB
[b0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit a603f79) — dot1 doc B: mtrang_kraken ft1_s050 phần 11
```

## cai_adoc.log (sửa 341 phút trước)
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

