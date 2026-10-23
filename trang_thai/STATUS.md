# Trạng thái server — 2026-10-23 06:57 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 4 hours, 53 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.9G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9077 MiB, 15360 MiB, 34 %
Tesla T4, 8351 MiB, 15360 MiB, 31 %
63988, 434 MiB, /kaggle/working/venvs/adoc/bin/python
63985, 8640 MiB, /kaggle/working/venvs/adoc/bin/python
63988, 8348 MiB, /kaggle/working/venvs/adoc/bin/python
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[b0] [06:56:53]    giulai_B · ft4 · phần 6: 50 dòng, 2.72 s/dòng · còn ~206 phần · RAM trống 25.2 GB` |

## dot1.log (sửa 1 phút trước)
```
[b0] [06:50:20]    giulai_B · ft4 · phần 0: 50 dòng, 2.38 s/dòng · còn ~211 phần · RAM trống 25.2 GB
[b1] [06:50:43]    giulai_B · ft4 · phần 1: 50 dòng, 2.82 s/dòng · còn ~211 phần · RAM trống 25.2 GB
[b1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 4d1d3aa) — dot1 doc B: giulai_B ft4 phần 1
[b0] [06:52:23]    giulai_B · ft4 · phần 2: 50 dòng, 2.45 s/dòng · còn ~210 phần · RAM trống 25.2 GB
[b1] [06:53:14]    giulai_B · ft4 · phần 3: 50 dòng, 2.97 s/dòng · còn ~209 phần · RAM trống 25.2 GB
[b0] [06:54:36]    giulai_B · ft4 · phần 4: 50 dòng, 2.65 s/dòng · còn ~208 phần · RAM trống 25.2 GB
[b1] [06:55:39]    giulai_B · ft4 · phần 5: 50 dòng, 2.88 s/dòng · còn ~207 phần · RAM trống 25.2 GB
[b0] [06:56:53]    giulai_B · ft4 · phần 6: 50 dòng, 2.72 s/dòng · còn ~206 phần · RAM trống 25.2 GB
```

## cai_adoc.log (sửa 250 phút trước)
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

