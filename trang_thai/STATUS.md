# Trạng thái server — 2026-10-23 07:07 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 5 hours, 3 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.9G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9733 MiB, 15360 MiB, 32 %
Tesla T4, 9531 MiB, 15360 MiB, 29 %
63988, 434 MiB, /kaggle/working/venvs/adoc/bin/python
63985, 9296 MiB, /kaggle/working/venvs/adoc/bin/python
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[b0] [07:06:08]    mtrang_kraken · ft4 · phần 4: 50 dòng, 4.05 s/dòng · còn ~198 phần · RAM trống 25.0 GB` |

## dot1.log (sửa 2 phút trước)
```
[b0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 5dc98f7) — dot1 doc B: giulai_B ft4 phần 8
[b1] [07:00:24]    giulai_B · ft4 · phần 9: 50 dòng, 2.90 s/dòng · còn ~203 phần · RAM trống 25.2 GB
[b0] [07:01:14]    mtrang_kraken · ft4 · phần 0: 50 dòng, 2.32 s/dòng · còn ~202 phần · RAM trống 25.1 GB
[b1] [07:01:42]    mtrang_kraken · ft4 · phần 1: 50 dòng, 1.55 s/dòng · còn ~201 phần · RAM trống 25.1 GB
[b1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit b928790) — dot1 doc B: mtrang_kraken ft4 phần 1
[b0] [07:02:45]    mtrang_kraken · ft4 · phần 2: 50 dòng, 1.80 s/dòng · còn ~200 phần · RAM trống 25.1 GB
[b1] [07:05:01]    mtrang_kraken · ft4 · phần 3: 50 dòng, 3.92 s/dòng · còn ~199 phần · RAM trống 25.1 GB
[b0] [07:06:08]    mtrang_kraken · ft4 · phần 4: 50 dòng, 4.05 s/dòng · còn ~198 phần · RAM trống 25.0 GB
```

## cai_adoc.log (sửa 260 phút trước)
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

