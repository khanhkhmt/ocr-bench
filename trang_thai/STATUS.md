# Trạng thái server — 2026-10-19 04:41 UTC

**Còn sống** · định kỳ

- máy: `e6a5044ee560` · up 51 minutes
- ngrok (SSH): tcp://0.tcp.ngrok.io:28751
- code: `72dcb7b hop_thu: RAM trong STATUS; prompt LLM: báo trạng thái mỗi 10 phút, server sập → làm lại từ BƯỚC 0` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  391M   20G   2% /kaggle/working
- RAM: Mem:              31           3           0           0          26          26 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 10545 MiB, 15360 MiB, 100 %
Tesla T4, 3 MiB, 15360 MiB, 0 %
15354, 10542 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
```

## Phiên tmux
```
adoc: 1 windows (created Mon Oct 19 04:02:40 2026)
hop_thu: 1 windows (created Mon Oct 19 04:01:52 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| adoc | đang chạy | 1 | 0 | 2026-10-19 04:02 UTC | `================ BƯỚC 6: đọc 4 trang mẫu, chế độ one_gpu_unload (04:30:22 UTC)` |

## adoc_run_all.log (sửa 12 phút trước)
```
| page | type | main | dots | ft3 | ft4 |
|---|---|---:|---:|---:|---:|
| page_1 | printed | 90.3 / 70.1 | 90.3 / 70.1 | 78.8 / 57.6 | 76.0 / 51.1 |
| page_2 | handwritten | 72.2 / 46.5 | 47.9 / 7.4 | 72.2 / 46.5 | 73.1 / 47.9 |
| page_3 | printed + stamps + Hebrew notary block | 79.0 / 44.0 | 79.0 / 44.0 | 79.7 / 51.5 | 80.3 / 53.5 |
| page_4 | typed + handwritten notes + watermark | 90.9 / 70.9 | 90.9 / 70.9 | 79.9 / 62.8 | 83.7 / 69.8 |
(correct characters % / correct words %)
================ BƯỚC 6: đọc 4 trang mẫu, chế độ one_gpu_unload (04:30:22 UTC)
```

