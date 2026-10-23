# Trạng thái server — 2026-10-23 06:47 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 4 hours, 43 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.9G   15G  25% /kaggle/working
- RAM: Mem:              31           5           0           0          25          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9077 MiB, 15360 MiB, 32 %
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[b1] [06:46:00]    ✔ tự kiểm: ft3 / gốc đọc giống hệt sản phẩm; tron34 bật đủ 2 adapter với hệ số ½` |

## dot1.log (sửa 2 phút trước)
```
[b1] 
[b1] 
[b0] [06:45:20]    nạp xong: 412 lớp LoRA × 3 adapter trên cuda:0
[b0] The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
[b1] [06:45:20]    nạp xong: 412 lớp LoRA × 3 adapter trên cuda:1
[b1] The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
[b0] [06:45:57]    ✔ tự kiểm: ft3 / gốc đọc giống hệt sản phẩm; tron34 bật đủ 2 adapter với hệ số ½
[b1] [06:46:00]    ✔ tự kiểm: ft3 / gốc đọc giống hệt sản phẩm; tron34 bật đủ 2 adapter với hệ số ½
```

## cai_adoc.log (sửa 240 phút trước)
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

