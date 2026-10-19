# Trạng thái server — 2026-10-19 03:30 UTC

**Còn sống** · định kỳ

- máy: `352243f8b4d9` · up 48 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `77048df llm_sua: thử LLM sửa lỗi OCR trên 4 trang mẫu (5 model × chon / sua / chon_sua, luật nhận thay đổi cố định, nhãn chỉ dùng để chấm) + cai_llm.sh (venv dùng torch hệ thống) + PROMPT_LLM_SUA.md cho agent Kaggle` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  387M   20G   2% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 12953 MiB, 15360 MiB, 0 %
Tesla T4, 8019 MiB, 15360 MiB, 0 %
8201, 12950 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
8201, 8016 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
```

## Phiên tmux
```
adoc: 1 windows (created Mon Oct 19 03:10:41 2026)
hop_thu: 1 windows (created Mon Oct 19 03:10:03 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| adoc | đang chạy | 1 | 0 | 2026-10-19 03:10 UTC | `================ BƯỚC 5: đọc 4 trang mẫu, chế độ two_gpus (03:14:02 UTC)` |

## adoc_run_all.log (sửa 16 phút trước)
```
13 passed in 3.20s
================ BƯỚC 4: dung lượng ổ đĩa (03:14:01 UTC)
venv_gb: 0.34
kraken_venv_gb: 1.29
model_gb dots-studio/dots.mocr: 5.67
model_gb Misraj/Baseer__Nakba: 7.01
model_gb khanh99/htr-baseer-nakba-ft: 0.61
================ BƯỚC 5: đọc 4 trang mẫu, chế độ two_gpus (03:14:02 UTC)
```

