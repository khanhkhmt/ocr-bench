# Trạng thái server — 2026-10-19 04:21 UTC

**Còn sống** · định kỳ

- máy: `e6a5044ee560` · up 31 minutes
- ngrok (SSH): tcp://0.tcp.ngrok.io:28751
- code: `72dcb7b hop_thu: RAM trong STATUS; prompt LLM: báo trạng thái mỗi 10 phút, server sập → làm lại từ BƯỚC 0` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  387M   20G   2% /kaggle/working
- RAM: Mem:              31           4           0           0          26          26 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 12953 MiB, 15360 MiB, 0 %
Tesla T4, 8019 MiB, 15360 MiB, 0 %
5224, 12950 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
5224, 8016 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
```

## Phiên tmux
```
adoc: 1 windows (created Mon Oct 19 04:02:40 2026)
hop_thu: 1 windows (created Mon Oct 19 04:01:52 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| adoc | đang chạy | 1 | 0 | 2026-10-19 04:02 UTC | `================ BƯỚC 5: đọc 4 trang mẫu, chế độ two_gpus (04:05:55 UTC)` |

## adoc_run_all.log (sửa 16 phút trước)
```
13 passed in 3.23s
================ BƯỚC 4: dung lượng ổ đĩa (04:05:54 UTC)
venv_gb: 0.34
kraken_venv_gb: 1.29
model_gb dots-studio/dots.mocr: 5.67
model_gb Misraj/Baseer__Nakba: 7.01
model_gb khanh99/htr-baseer-nakba-ft: 0.61
================ BƯỚC 5: đọc 4 trang mẫu, chế độ two_gpus (04:05:55 UTC)
```

