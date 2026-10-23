# Trạng thái server — 2026-10-23 03:47 UTC

**Còn sống** · ĐÃ CHẠY lệnh 20261014-073148: ✔ keo_code → dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa; ✘ chay_lai td: không có việc 'td' (có: cai_adoc, dot1)

- máy: `82d3fda35fd3` · up 1 hour, 42 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  2.5G   18G  13% /kaggle/working
- RAM: Mem:              31           1           5           0          24          29 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 0 MiB, 15360 MiB, 0 %
Tesla T4, 0 MiB, 15360 MiB, 0 %
(không có tiến trình)
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `GPU: 2 · ổ trống /kaggle/working: 18 GB` |

## dot1.log (sửa 0 phút trước)
```
[g0] [03:46:03]    omar_A · ft3 · phần 6: 50 dòng, 5.46 s/dòng · còn ~258 phần · RAM trống 24.6 GB
[g0] ✘ ĐẨY GITHUB THẤT BẠI (chạy tiếp, lần sau thử lại): git fetch -q lỗi: remote: Invalid username or token. Password authentication is not supported for Git operations.
[g0] fatal: Authentication failed for 'https://github.com/khanhkhmt/ocr-bench.git/'
[g1] [03:46:55]    omar_A · ft3 · phần 7: 50 dòng, 5.37 s/dòng · còn ~257 phần · RAM trống 24.6 GB
[g1] ✘ ĐẨY GITHUB THẤT BẠI (chạy tiếp, lần sau thử lại): git fetch -q lỗi: remote: Invalid username or token. Password authentication is not supported for Git operations.
[g1] fatal: Authentication failed for 'https://github.com/khanhkhmt/ocr-bench.git/'
================ BƯỚC 1: kiểm tra môi trường (03:47:11 UTC) · RAM còn 28 GB
GPU: 2 · ổ trống /kaggle/working: 18 GB
```

## cai_adoc.log (sửa 60 phút trước)
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

