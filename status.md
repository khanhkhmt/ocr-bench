# Trạng thái ocrbench

- Cập nhật: **2026-10-05 04:58 UTC** · DỪNG: web demo dots vẫn lỗi
- Máy: `2b44e3deaaa3` · GPU: Tesla T4, Tesla T4
- Code: `6ff766e` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: (không có)

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| dots_mocr | ⚠ dừng giữa chừng (chưa kết thúc lần nào, có thể do sập) | 1/1051 | 0 | 96.8% | 22.46 | — | — |
| easyocr | ■ đã dừng | 1051/1051 | 0 | 35.9% | 3.36 | 13.3 GB | 2026-10-02T04:43:28+00:00 |
| sherif_handwriting | ■ đã dừng | 923/1051 | 1 | 19.8% | 23.52 | 13.0 GB | 2026-10-02T09:35:19+00:00 |
| sherif_handwriting__long | ⚠ dừng giữa chừng (chưa kết thúc lần nào, có thể do sập) | 6/1051 | 0 | 102.6% | 581.69 | — | — |
| sherif_handwriting__pp__long | ■ đã dừng | 24/1051 | 0 | 20.9% | 269.57 | 13.5 GB | 2026-10-05T03:31:36+00:00 |
| sherif_handwriting__sl__long | ■ đã dừng | 24/1051 | 5 | 59.3% | 366.44 | 0.0 GB | 2026-10-03T11:09:14+00:00 |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | dots_mocr | easyocr | sherif_handwriting | sherif_handwriting__long | sherif_handwriting__pp__long | sherif_handwriting__sl__long | tesseract |
|---|---:|---:|---:|---:|---:|---:|---:|
| pub_handwriting_ar | — | 128: 49.3% | 128: 7.2% | — | — | — | 128: 74.4% |
| pub_handwriting_en | — | 63: 81.3% | 63: 10.9% | — | — | — | 63: 61.7% |
| pub_printed_ar | — | 63: 28.4% | 63: 41.1% | — | — | — | 63: 32.1% |
| pub_tables_ar | — | 58: 42.5% | 58: 49.5% | — | — | — | 58: 52.4% |
| pub_tables_en | 1: 96.8% | 61: 81.1% | 61: 46.3% | — | — | — | 61: 89.6% |
| syn_degraded | — | 61: 31.5% | 61: 40.4% | — | — | — | 61: 32.2% |
| syn_form_ar | — | 60: 20.4% | 60: 21.8% | — | — | — | 60: 35.2% |
| syn_form_en | — | 72: 45.7% | 72: 1.9% | — | — | — | 72: 11.7% |
| syn_invoice_ar | — | 57: 33.3% | 57: 27.5% | — | — | — | 57: 42.0% |
| syn_invoice_en | — | 62: 9.2% | 62: 2.0% | — | — | — | 62: 19.1% |
| syn_invoice_mixed | — | 57: 38.2% | 57: 29.0% | — | — | — | 57: 39.5% |
| syn_longtable | — | 61: 52.3% | — | 6: 102.6% | 12: 38.9% | 12: 82.6% | 61: 54.7% |
| syn_longtext | — | 67: 10.3% | — | — | 12: 2.9% | 12: 36.1% | 67: 3.0% |
| syn_text_ar | — | 60: 7.6% | 60: 5.2% | — | — | — | 60: 7.0% |
| syn_text_en | — | 57: 14.9% | 57: 1.0% | — | — | — | 57: 1.9% |
| syn_text_mixed | — | 64: 13.7% | 64: 11.5% | — | — | — | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-05 04:58 UTC — Kiểm tra web demo dots (thất bại)
- Kết quả kiểm tra: ✘ KIỂM TRA KHÔNG ĐẠT
- 80 dòng cuối demo.log:
```text
Loading weights:  95%|█████████▍| 609/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.mlp.fc2.weight]
Loading weights:  95%|█████████▍| 609/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.mlp.fc2.weight]
Loading weights:  95%|█████████▍| 610/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.mlp.fc3.weight]
Loading weights:  95%|█████████▍| 610/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.mlp.fc3.weight]
Loading weights:  95%|█████████▌| 611/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.norm1.weight]  
Loading weights:  95%|█████████▌| 611/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.norm1.weight]
Loading weights:  95%|█████████▌| 612/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.norm2.weight]
Loading weights:  95%|█████████▌| 612/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.38.norm2.weight]
Loading weights:  95%|█████████▌| 613/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.attn.proj.weight]
Loading weights:  95%|█████████▌| 613/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.attn.proj.weight]
Loading weights:  95%|█████████▌| 614/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.attn.qkv.weight] 
Loading weights:  95%|█████████▌| 614/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.attn.qkv.weight]
Loading weights:  96%|█████████▌| 615/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc1.weight] 
Loading weights:  96%|█████████▌| 615/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc1.weight]
Loading weights:  96%|█████████▌| 616/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc2.weight]
Loading weights:  96%|█████████▌| 616/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc2.weight]
Loading weights:  96%|█████████▌| 617/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc3.weight]
Loading weights:  96%|█████████▌| 617/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.mlp.fc3.weight]
Loading weights:  96%|█████████▌| 618/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.norm1.weight]  
Loading weights:  96%|█████████▌| 618/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.norm1.weight]
Loading weights:  96%|█████████▋| 619/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.norm2.weight]
Loading weights:  96%|█████████▋| 619/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.39.norm2.weight]
Loading weights:  96%|█████████▋| 620/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.attn.proj.weight]
Loading weights:  96%|█████████▋| 620/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.attn.proj.weight]
Loading weights:  97%|█████████▋| 621/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.attn.qkv.weight] 
Loading weights:  97%|█████████▋| 621/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.attn.qkv.weight]
Loading weights:  97%|█████████▋| 622/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc1.weight] 
Loading weights:  97%|█████████▋| 622/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc1.weight]
Loading weights:  97%|█████████▋| 623/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc2.weight]
Loading weights:  97%|█████████▋| 623/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc2.weight]
Loading weights:  97%|█████████▋| 624/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc3.weight]
Loading weights:  97%|█████████▋| 624/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.mlp.fc3.weight]
Loading weights:  97%|█████████▋| 625/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.norm1.weight]  
Loading weights:  97%|█████████▋| 625/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.norm1.weight]
Loading weights:  97%|█████████▋| 626/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.norm2.weight]
Loading weights:  97%|█████████▋| 626/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.40.norm2.weight]
Loading weights:  98%|█████████▊| 627/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.attn.proj.weight]
Loading weights:  98%|█████████▊| 627/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.attn.proj.weight]
Loading weights:  98%|█████████▊| 628/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.attn.qkv.weight] 
Loading weights:  98%|█████████▊| 628/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.attn.qkv.weight]
Loading weights:  98%|█████████▊| 629/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc1.weight] 
Loading weights:  98%|█████████▊| 629/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc1.weight]
Loading weights:  98%|█████████▊| 630/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc2.weight]
Loading weights:  98%|█████████▊| 630/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc2.weight]
Loading weights:  98%|█████████▊| 631/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc3.weight]
Loading weights:  98%|█████████▊| 631/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.mlp.fc3.weight]
Loading weights:  98%|█████████▊| 632/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.norm1.weight]  
Loading weights:  98%|█████████▊| 632/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.norm1.weight]
Loading weights:  98%|█████████▊| 633/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.norm2.weight]
Loading weights:  98%|█████████▊| 633/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.blocks.41.norm2.weight]
Loading weights:  99%|█████████▊| 634/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.ln_q.bias]      
Loading weights:  99%|█████████▊| 634/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.ln_q.bias]
Loading weights:  99%|█████████▉| 635/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.ln_q.weight]
Loading weights:  99%|█████████▉| 635/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.ln_q.weight]
Loading weights:  99%|█████████▉| 636/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.mlp.0.bias] 
Loading weights:  99%|█████████▉| 636/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.mlp.0.bias]
Loading weights:  99%|█████████▉| 637/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.mlp.0.weight]
Loading weights:  99%|█████████▉| 637/643 [00:02<00:00, 296.95it/s, Materializing param=vision_tower.merger.mlp.0.weight]
Loading weights:  99%|█████████▉| 638/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.0.weight]
Loading weights:  99%|█████████▉| 638/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.2.bias]  
Loading weights:  99%|█████████▉| 638/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.2.bias]
Loading weights:  99%|█████████▉| 639/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.2.weight]
Loading weights:  99%|█████████▉| 639/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.merger.mlp.2.weight]
Loading weights: 100%|█████████▉| 640/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.norm.weight]
Loading weights: 100%|█████████▉| 640/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.norm.weight]
Loading weights: 100%|█████████▉| 641/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.proj.bias]  
Loading weights: 100%|█████████▉| 641/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.proj.bias]
Loading weights: 100%|█████████▉| 642/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.proj.weight]
Loading weights: 100%|█████████▉| 642/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.patch_embed.patchifier.proj.weight]
Loading weights: 100%|██████████| 643/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.post_trunk_norm.weight]            
Loading weights: 100%|██████████| 643/643 [00:02<00:00, 253.32it/s, Materializing param=vision_tower.post_trunk_norm.weight]
Loading weights: 100%|██████████| 643/643 [00:02<00:00, 234.42it/s, Materializing param=vision_tower.post_trunk_norm.weight]
nạp model: 20s trên 2 bản model
Setting `pad_token_id` to `eos_token_id`:151643 for open-end generation.
thời gian 1 trang: 21.1s · nguồn: OCR · lỗi: — · ghi chú: —
số khối bố cục: 1 · có bảng HTML: False
----- kết quả -----

-------------------
✘ KIỂM TRA KHÔNG ĐẠT — xem kết quả ở trên (gửi cho người sửa code)
```
