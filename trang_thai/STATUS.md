# Trạng thái server — 2026-10-20 09:57 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 7 hours, 43 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  3.4G   17G  18% /kaggle/working
- RAM: Mem:              31           5           0           0          24          25 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 9093 MiB, 15360 MiB, 30 %
Tesla T4, 8351 MiB, 15360 MiB, 28 %
100096, 8640 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
100100, 450 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
100100, 8348 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
```

## Phiên tmux
```
dot1: 1 windows (created Tue Oct 20 02:47:26 2026)
hop_thu: 1 windows (created Tue Oct 20 02:41:19 2026)
init: 1 windows (created Tue Oct 20 02:40:12 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| cai_adoc | XONG | 1 | 0 | 2026-10-20 02:41 UTC | `Done. Web:  bash run_web.sh        CLI:  /kaggle/working/arabic-doc-ocr/.venv/bin/python -m arabic_doc_ocr page <file> --type printed` |
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[b1] [09:55:06]    ✔ tự kiểm: ft3 / gốc đọc giống hệt sản phẩm; tron34 bật đủ 2 adapter với hệ số ½` |

## dot1.log (sửa 3 phút trước)
```
[b1] 
[b1] 
[b0] [09:54:26]    nạp xong: 412 lớp LoRA × 3 adapter trên cuda:0
[b0] The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
[b1] [09:54:27]    nạp xong: 412 lớp LoRA × 3 adapter trên cuda:1
[b1] The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
[b0] [09:55:04]    ✔ tự kiểm: ft3 / gốc đọc giống hệt sản phẩm; tron34 bật đủ 2 adapter với hệ số ½
[b1] [09:55:06]    ✔ tự kiểm: ft3 / gốc đọc giống hệt sản phẩm; tron34 bật đủ 2 adapter với hệ số ½
```

## cai_adoc.log (sửa 433 phút trước)
```
  Kraken: /root/.cache/arabic_doc_ocr/kraken_venv/bin/kraken · segmentation model: /root/.cache/arabic_doc_ocr/muharaf_seg_best.mlmodel
  RAM 31.3 GiB (free 28.2)
  disk (home) free 1051.2 GiB
  model dots-studio/dots.mocr: cached (5.7 GiB)
  model Misraj/Baseer__Nakba: cached (7.0 GiB)
  model khanh99/htr-baseer-nakba-ft: cached (0.6 GiB)
OK
Done. Web:  bash run_web.sh        CLI:  /kaggle/working/arabic-doc-ocr/.venv/bin/python -m arabic_doc_ocr page <file> --type printed
```

