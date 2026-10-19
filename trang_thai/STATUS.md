# Trạng thái server — 2026-10-19 08:47 UTC

**Còn sống** · cai_llm XONG

- máy: `e6a5044ee560` · up 4 hours, 57 minutes
- ngrok (SSH): tcp://0.tcp.ngrok.io:28751
- code: `ce65530 cai_llm.sh: kiểm tra torch hệ thống theo vị trí ngoài venv (Kaggle để torch ở dist-packages, không phải site-packages)` (nhánh `thu-2-model-htr`)
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
| cai_llm | XONG | 2 | 0 | 2026-10-19 08:46 UTC | `✔ VENV LLM SẴN SÀNG: /kaggle/working/venvs/llm (transformers 5.15.1)` |

## cai_llm.log (sửa 1 phút trước)
```
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
AssertionError
✘ LỖI: kiểm tra venv lỗi
== torch hệ thống 2.10.0 → transformers 5.15.1
   ghim: torch==2.10.0+cu128 torchvision==0.25.0+cu128 torchaudio==2.10.0+cu128 triton==3.6.0 
   torch 2.10.0+cu128 (/usr/local/lib/python3.12/dist-packages) · transformers 5.15.1 · accelerate 1.12.0 · GPU 2: Tesla T4, Tesla T4
✔ VENV LLM SẴN SÀNG: /kaggle/working/venvs/llm (transformers 5.15.1)
```

## adoc_run_all.log (sửa 194 phút trước)
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

