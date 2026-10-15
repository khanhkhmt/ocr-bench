# Trạng thái server — 2026-10-15 03:48 UTC

**Còn sống** · định kỳ

- máy: `6f4169b1f2b2` · up 1 hour, 37 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19107
- code: `2d47a23 app_ft: loại chữ (viết tay → ft3/ft4; đánh máy → dots/ft3 kiểm chéo; hỗn hợp → tự chọn theo khối, thử nghiệm) + tải về đủ (ZIP, DOCX, TXT chính/ft3/ft4, HTML bảng soát, JSON, ảnh khung; tab một dòng → JSON); hf_repo/inference.py: tên kết quả không trùng khi nhiều trang cùng tên file` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.1G   18G  11% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 12927 MiB, 15360 MiB, 0 %
Tesla T4, 8019 MiB, 15360 MiB, 0 %
10701, 12924 MiB, /kaggle/working/venvs/dots/bin/python
10701, 8016 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
hop_thu: 1 windows (created Thu Oct 15 02:27:09 2026)
web: 1 windows (created Thu Oct 15 02:45:46 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| hf | XONG | 1 | 0 | 2026-10-15 02:30 UTC | `✔ XONG HF` |

## hf.log (sửa 63 phút trước)
```
W0000 00:00:1792031523.350307    5910 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1792031523.350313    5910 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
W0000 00:00:1792031523.350318    5910 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
2026-10-15 02:32:03.355415: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
loaded Misraj/Baseer__Nakba + ['ft3', 'ft4'] on cuda:0 (torch.float16) in 57s
The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
✔ XONG HF
```

