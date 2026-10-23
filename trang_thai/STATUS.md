# Trạng thái server — 2026-10-23 07:48 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 5 hours, 43 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.9G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10153 MiB, 15360 MiB, 31 %
Tesla T4, 9531 MiB, 15360 MiB, 32 %
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[b1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 62dac95) — dot1 doc B: omar_B ft1_s050 phần 7` |

## dot1.log (sửa 2 phút trước)
```
[b0] [07:40:19]    omar_B · ft1_s050 · phần 2: 50 dòng, 3.58 s/dòng · còn ~172 phần · RAM trống 25.1 GB
[b1] [07:40:29]    omar_B · ft1_s050 · phần 3: 50 dòng, 3.66 s/dòng · còn ~171 phần · RAM trống 25.1 GB
[b0] [07:42:56]    omar_B · ft1_s050 · phần 4: 50 dòng, 3.14 s/dòng · còn ~170 phần · RAM trống 25.1 GB
[b0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit ad89301) — dot1 doc B: omar_B ft1_s050 phần 4
[b1] [07:43:18]    omar_B · ft1_s050 · phần 5: 50 dòng, 3.35 s/dòng · còn ~169 phần · RAM trống 25.1 GB
[b0] [07:45:37]    omar_B · ft1_s050 · phần 6: 50 dòng, 3.14 s/dòng · còn ~168 phần · RAM trống 25.1 GB
[b1] [07:46:11]    omar_B · ft1_s050 · phần 7: 50 dòng, 3.46 s/dòng · còn ~167 phần · RAM trống 25.1 GB
[b1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 62dac95) — dot1 doc B: omar_B ft1_s050 phần 7
```

## cai_adoc.log (sửa 300 phút trước)
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

