# Trạng thái server — 2026-10-19 05:27 UTC

**Còn sống** · adoc có lỗi trong log (vẫn chạy)

- máy: `e6a5044ee560` · up 1 hour, 36 minutes
- ngrok (SSH): tcp://0.tcp.ngrok.io:28751
- code: `72dcb7b hop_thu: RAM trong STATUS; prompt LLM: báo trạng thái mỗi 10 phút, server sập → làm lại từ BƯỚC 0` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  389M   20G   2% /kaggle/working
- RAM: Mem:              31           3           6           0          21          27 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 12797 MiB, 15360 MiB, 100 %
Tesla T4, 3 MiB, 15360 MiB, 0 %
38774, 12794 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
```

## Phiên tmux
```
adoc: 1 windows (created Mon Oct 19 04:02:40 2026)
hop_thu: 1 windows (created Mon Oct 19 04:01:52 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| adoc | LỖI | 1 | 0 | 2026-10-19 04:02 UTC | `================ BƯỚC 9: PDF nhiều trang (chế độ two_gpus) (05:23:16 UTC)` |

## adoc_run_all.log (sửa 4 phút trước)
```
           ^^^^^^^^^^^^^^^^^^^^^
  File "/kaggle/working/arabic-doc-ocr/.venv/lib/python3.12/site-packages/transformers/modeling_utils.py", line 813, in _load_state_dict_into_meta_model
    param = param[...]
            ~~~~~^^^^^
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 20.00 MiB. GPU 0 has a total capacity of 14.56 GiB of which 18.81 MiB is free. Including non-PyTorch memory, this process has 14.54 GiB memory in use. Of the allocated memory 14.09 GiB is allocated by PyTorch, and 325.77 MiB is reserved b
returncode 1 · 235.2 s · GPU peak (nvidia-smi) {0: 14.54, 1: 0.0} GB · RAM peak 6.19 GB → /kaggle/working/arabic-doc-ocr/results/one_gpu_both/measure.json
   (chế độ thử: hai model cùng một GPU — lỗi = GPU không đủ chỗ, ghi vào báo cáo, đi tiếp)
================ BƯỚC 9: PDF nhiều trang (chế độ two_gpus) (05:23:16 UTC)
```

