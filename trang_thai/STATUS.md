# Trạng thái server — 2026-10-20 03:06 UTC

**Còn sống** · định kỳ

- máy: `5649dab657e1` · up 52 minutes
- ngrok (SSH): tcp://2.tcp.ngrok.io:19216
- code: `028c4ee dot1: Đợt 1 thử không cần huấn luyện — bộ test A (chọn) / B (xác nhận), trộn ft3+ft4, độ mạnh ft3, bầu chọn, Bước 0 trên 66 trang Muharaf (dòng chuẩn vs Kraken), dots đọc từng khối; luật chọn / luật đạt viết sẵn; chay_dot1.sh + PROMPT_DOT1.md` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  2.6G   17G  13% /kaggle/working
- RAM: Mem:              31           6           0           0          24          24 (cột: tổng / đã dùng / trống / … / còn dùng được, GB)
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 13439 MiB, 15360 MiB, 44 %
Tesla T4, 8351 MiB, 15360 MiB, 22 %
8669, 12986 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
9277, 450 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
9277, 8348 MiB, /kaggle/working/arabic-doc-ocr/.venv/bin/python
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
| dot1 | đang chạy | 1 | 0 | 2026-10-20 02:47 UTC | `[bt] Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.` |

## dot1.log (sửa 0 phút trước)
```
[bt] [03:05:56]    #5 page_1 khối 5 ×1.5 (thực ×1.5): 0.7 s
[bt] Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
[bt] [03:05:57]    #5 page_1 khối 6 ×1.5 (thực ×1.5): 0.6 s
[bt] Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
[bt] [03:05:57]    #5 page_1 khối 7 ×1.5 (thực ×1.5): 0.6 s
[bt] Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
[bt] [03:05:59]    #5 page_3 khối 0 ×1.5 (thực ×1.5): 1.5 s
[bt] Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
```

## cai_adoc.log (sửa 21 phút trước)
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

