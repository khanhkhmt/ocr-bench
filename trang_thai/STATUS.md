# Trạng thái server — 2026-10-19 08:17 UTC

**Còn sống** · định kỳ

- máy: `e6a5044ee560` · up 4 hours, 27 minutes
- ngrok (SSH): tcp://0.tcp.ngrok.io:28751
- code: `72dcb7b hop_thu: RAM trong STATUS; prompt LLM: báo trạng thái mỗi 10 phút, server sập → làm lại từ BƯỚC 0` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  549M   19G   3% /kaggle/working
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
hop_thu: 1 windows (created Mon Oct 19 04:01:52 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| adoc | XONG | 1 | 0 | 2026-10-19 04:02 UTC | `✔ XONG TẤT CẢ — bước tiếp theo: bash scripts/push_results.sh` |
| cai_llm | CHỜ LỆNH | 1 | 0 | 2026-10-19 05:35 UTC | `✘ LỖI: kiểm tra venv lỗi` |

## cai_llm.log (sửa 162 phút trước)
```
== torch hệ thống 2.10.0 → transformers 5.15.1
   ghim: torch==2.10.0+cu128 torchvision==0.25.0+cu128 torchaudio==2.10.0+cu128 triton==3.6.0 
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
google-adk 1.25.1 requires google-cloud-bigquery-storage>=2.0.0, which is not installed.
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
AssertionError
✘ LỖI: kiểm tra venv lỗi
```

## adoc_run_all.log (sửa 164 phút trước)
```
| page_3 | printed | 213 s | 34 | 234 s |
| page_4 | printed | 114 s | 19 | 59 s |
## Disk
| item | size |
|---|---:|
| model dots-studio/dots.mocr | 5.7 GB |
| model Misraj/Baseer__Nakba | 7.0 GB |
✔ XONG TẤT CẢ — bước tiếp theo: bash scripts/push_results.sh
```

