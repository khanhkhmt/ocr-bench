# Trạng thái server — 2026-10-19 09:33 UTC

**Còn sống** · định kỳ

- máy: `e6a5044ee560` · up 5 hours, 43 minutes
- ngrok (SSH): tcp://0.tcp.ngrok.io:28751
- code: `ce65530 cai_llm.sh: kiểm tra torch hệ thống theo vị trí ngoài venv (Kaggle để torch ở dist-packages, không phải site-packages)` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  591M   19G   3% /kaggle/working
- RAM: Mem:              31           7           0           0          22          22 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 163 MiB, 15360 MiB, 0 %
Tesla T4, 161 MiB, 15360 MiB, 0 %
84096, 160 MiB, /kaggle/working/venvs/llm/bin/python
84096, 158 MiB, /kaggle/working/venvs/llm/bin/python
```

## Phiên tmux
```
hop_thu: 1 windows (created Mon Oct 19 04:01:52 2026)
llm: 1 windows (created Mon Oct 19 08:51:27 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| adoc | XONG | 1 | 0 | 2026-10-19 04:02 UTC | `✔ XONG TẤT CẢ — bước tiếp theo: bash scripts/push_results.sh` |
| cai_llm | XONG | 2 | 0 | 2026-10-19 08:46 UTC | `✔ VENV LLM SẴN SÀNG: /kaggle/working/venvs/llm (transformers 5.15.1)` |
| llm_thu | XONG | 1 | 0 | 2026-10-19 08:48 UTC | `✔ XONG TẤT CẢ (1/1 model chạy được; lỗi: không)` |
| llm | đang chạy | 1 | 0 | 2026-10-19 08:51 UTC | `[09:32:40]    ổ trống 993 GiB` |

## llm_sua.log (sửa 0 phút trước)
```
[09:27:49]    qwen3.5-9b · sua · page_4: 14 từ đổi (3 bị luật chặn), 25 s
[09:28:40]    qwen3.5-9b · chon_sua · page_1: 36 từ đổi (13 bị luật chặn), 51 s
[09:30:10]    qwen3.5-9b · chon_sua · page_2: 39 từ đổi (11 bị luật chặn), 91 s
[09:32:07]    qwen3.5-9b · chon_sua · page_3: 86 từ đổi (10 bị luật chặn), 117 s
[09:32:38]    qwen3.5-9b · chon_sua · page_4: 16 từ đổi (3 bị luật chặn), 31 s
✔ GITHUB: đã đẩy lên nhánh results-htr/llm_sua (commit dbd6dc0) — llm_sua: xong qwen3.5-9b
[09:32:40] == gemma4-12b (google/gemma-4-12B-it): tải + nạp …
[09:32:40]    ổ trống 993 GiB
```

## llm_thu.log (sửa 44 phút trước)
```
[08:48:51] == nho (Qwen/Qwen2.5-0.5B-Instruct): tải + nạp …
[08:48:51]    ổ trống 1054 GiB
[08:49:09]    nạp xong (17 s, float16, revision 7ae557604a)
[08:49:10]    nho · chon · page_4: 6 từ đổi (0 bị luật chặn), 2 s
[08:49:21]    nho · sua · page_4: 7 từ đổi (7 bị luật chặn), 11 s
[08:49:33]    nho · chon_sua · page_4: 14 từ đổi (7 bị luật chặn), 12 s
✔ GITHUB: đã đẩy lên nhánh results-htr/llm_sua_thu (commit 7e04fab) — llm_sua: xong nho
✔ XONG TẤT CẢ (1/1 model chạy được; lỗi: không)
```

## cai_llm.log (sửa 47 phút trước)
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

## adoc_run_all.log (sửa 240 phút trước)
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

