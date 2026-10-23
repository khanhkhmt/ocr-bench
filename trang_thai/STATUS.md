# Trạng thái server — 2026-10-23 04:07 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 2 hours, 3 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  4.4G   16G  23% /kaggle/working
- RAM: Mem:              31           2           0           0          28          28 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `================ BƯỚC 8: #12: cắt lại dòng Kraken với khung nới 0/15/30/50 % (66 trang Muharaf + 4 trang mẫu, CPU) (03:58:24 UTC) · RAM còn 29 GB` |

## dot1.log (sửa 9 phút trước)
```
[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 6fa2945) — dot1 doc A xong (gpu 0)
[mt] [03:58:20] ✔ XONG mtrang: 66 trang · 1268 dòng chuẩn · 1359 dòng Kraken (Kraken lỗi 0 trang)
================ BƯỚC 6: vét bộ A (việc của 66 trang Muharaf có thể xuất hiện sau khi các tiến trình đọc đã thoát) (03:58:20 UTC) · RAM còn 29 GB
[v1] [03:58:21] ✔ XONG doc A trên cuda:1: 0 dòng trong 0 phút
[v0] [03:58:21] ✔ XONG doc A trên cuda:0: 0 dòng trong 0 phút
================ BƯỚC 7: chọn ứng viên theo luật (bộ A) (03:58:21 UTC) · RAM còn 29 GB
[03:58:24] ✔ ứng viên: bau5_dong (TB 3 bộ A 94.39 so với ft3 93.21) → bộ B đọc: ft3, ft4, ft1_s050, goc, tron34
================ BƯỚC 8: #12: cắt lại dòng Kraken với khung nới 0/15/30/50 % (66 trang Muharaf + 4 trang mẫu, CPU) (03:58:24 UTC) · RAM còn 29 GB
```

## cai_adoc.log (sửa 80 phút trước)
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

