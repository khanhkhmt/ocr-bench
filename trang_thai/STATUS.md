# Trạng thái server — 2026-10-23 03:57 UTC

**Còn sống** · định kỳ

- máy: `82d3fda35fd3` · up 1 hour, 52 minutes
- ngrok (SSH): tcp://4.tcp.ngrok.io:10288
- code: `dc0462a adoc/: bản chép riêng pipeline arabic-doc-ocr main@03e1e8e — thí nghiệm ocr-bench không cần repo demo nữa` (nhánh `main`)
- ổ /kaggle/working: /dev/loop2       20G  3.2G   17G  17% /kaggle/working
- RAM: Mem:              31           2           3           0          25          28 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
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
| dot1 | đang chạy | 2 | 0 | 2026-10-23 03:47 UTC | `[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 6fa2945) — dot1 doc A xong (gpu 0)` |

## dot1.log (sửa 4 phút trước)
```
[bt] [03:47:51] bố cục 4 trang đã có (khôi phục) → chỉ cắt lại ảnh dòng theo khung đã lưu
[bt] [03:47:51] ✔ 4 trang: 113 dòng → bo__trang4.jsonl
[bt] [03:47:51] ✔ XONG bon_trang
[g1] [03:50:51] ✔ XONG doc A trên cuda:1: 0 dòng trong 0 phút
[g1] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 1f9e72a) — dot1 doc A xong (gpu 1)
[mt] [03:52:51] Muharaf test: 66 trang
[g0] [03:52:51] ✔ XONG doc A trên cuda:0: 0 dòng trong 0 phút
[g0] ✔ GITHUB: đã đẩy lên nhánh results-htr/dot1 (commit 6fa2945) — dot1 doc A xong (gpu 0)
```

## cai_adoc.log (sửa 70 phút trước)
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

