# Trạng thái server — 2026-10-14 07:48 UTC

**Còn sống** · td có lỗi trong log (vẫn chạy)

- máy: `0b994473a1f2` · up 1 hour, 58 minutes
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `f13093d thu_dots: nạp dots lần lượt trên từng GPU (hai luồng cùng snapshot_download → tqdm AttributeError '_lock', GPU thứ hai không nạp được)` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.2G   18G  11% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 12029 MiB, 15360 MiB, 100 %
Tesla T4, 11929 MiB, 15360 MiB, 100 %
26575, 12026 MiB, /kaggle/working/venvs/dots/bin/python
26575, 11926 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
hop_thu: 1 windows (created Wed Oct 14 06:06:05 2026)
td: 1 windows (created Wed Oct 14 07:33:29 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| ct | XONG | 1 | 0 | 2026-10-14 06:10 UTC | `✔ XONG CHẤM TRANG` |
| td | LỖI | 2 | 0 | 2026-10-14 07:33 UTC | `✔ GITHUB: đã đẩy lên nhánh results-htr/thu_dots (commit 04e5d2b) — thử dots: image_3 khoi ×2 (14/36)` |

## td.log (sửa 2 phút trước)
```
    attn_output, attn_weights = attention_interface(
                                ^^^^^^^^^^^^^^^^^^^^
  File "/kaggle/working/venvs/dots/lib/python3.12/site-packages/transformers/integrations/sdpa_attention.py", line 83, in sdpa_attention_forward
    attn_output = torch.nn.functional.scaled_dot_product_attention(
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 3.26 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.73 GiB is free. Including non-PyTorch memory, this process has 12.83 GiB memory in use. Of the allocated memory 11.95 GiB is allocated by PyTorch, and 766.28 MiB is reserved by 
✔ image_3 khoi ×2 [cuda:0]: — · ? token · ? s · LỖI OutOfMemoryError: CUDA out of memory. Tried to allocate 3.26 GiB. GPU 0 has a total capacity of 14.56 GiB of which 1.73 GiB is free. Including non-PyTorch memory, this process has 12.83 GiB memory in use. Of the allocated memory 11.95 GiB is alloca
✔ GITHUB: đã đẩy lên nhánh results-htr/thu_dots (commit 04e5d2b) — thử dots: image_3 khoi ×2 (14/36)
```

## ct.log (sửa 51 phút trước)
```
## Chi tiết chạy
| trang | khối dots | dòng | tách dòng | dots (s) | đọc dòng 4 model (s) |
|---|---|---:|---|---:|---:|
| image_1 | 12 {'Page-header': 1, 'List-item': 3, 'Text': 5, 'Picture': 3} | 24 | chieu_ngang, kraken_muharaf | 85 | 142 |
| image_2 | 40 {'Section-header': 2, 'Text': 33, 'Picture': 5} | 36 | chieu_ngang, kraken_muharaf | 165 | 247 |
| image_3 | 0 {} | 0 |  | 1589 | 0 |
| image_4 | 11 {'Text': 7, 'Picture': 2, 'Caption': 1, 'Page-footer': 1} | 19 | chieu_ngang, kraken_muharaf | 39 | 91 |
✔ XONG CHẤM TRANG
```

