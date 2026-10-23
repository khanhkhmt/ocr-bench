# Trạng thái server — 2026-10-23 08:18 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 6 hours, 13 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.9G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10153 MiB, 15360 MiB, 34 %
Tesla T4, 9531 MiB, 15360 MiB, 0 %
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[b1] [08:18:05]    mtrang_kraken · ft1_s050 · phần 4: 50 dòng, 4.02 s/dòng · còn ~140 phần · RAM trống 25.1 GB` |

## dot1.log (sửa 0 phút trước)
```
[b1] [08:11:06]    giulai_B · ft1_s050 · phần 8: 50 dòng, 2.99 s/dòng · còn ~146 phần · RAM trống 25.1 GB
[b0] [08:12:51]    giulai_B · ft1_s050 · phần 9: 50 dòng, 2.65 s/dòng · còn ~145 phần · RAM trống 25.1 GB
[b1] [08:13:11]    mtrang_kraken · ft1_s050 · phần 0: 50 dòng, 2.48 s/dòng · còn ~144 phần · RAM trống 25.2 GB
[b0] [08:14:03]    mtrang_kraken · ft1_s050 · phần 1: 50 dòng, 1.44 s/dòng · còn ~143 phần · RAM trống 25.1 GB
[b1] [08:14:43]    mtrang_kraken · ft1_s050 · phần 2: 50 dòng, 1.83 s/dòng · còn ~142 phần · RAM trống 25.1 GB
[b0] [08:16:54]    mtrang_kraken · ft1_s050 · phần 3: 50 dòng, 3.39 s/dòng · còn ~141 phần · RAM trống 25.1 GB
[b0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 011b00a) — dot1 doc B: mtrang_kraken ft1_s050 phần 3
[b1] [08:18:05]    mtrang_kraken · ft1_s050 · phần 4: 50 dòng, 4.02 s/dòng · còn ~140 phần · RAM trống 25.1 GB
```

## cai_adoc.log (sửa 331 phút trước)
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

