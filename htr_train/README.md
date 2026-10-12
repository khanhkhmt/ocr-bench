# Huấn luyện tiếp Baseer-Nakba (LoRA) — mục tiêu: chữ tay Ả Rập trên giấy cũ màu

Mục tiêu đo: Muharaf test (giấy cũ màu) > 79,1% đúng ký tự (Baseer gốc) mà Omar blind_test vẫn ≥ 93%
(benchmark htr_test, 500 dòng cố định). Hai tập chấm KHÔNG có trong dữ liệu huấn luyện.

| File | Việc |
|---|---|
| `du_lieu.py` | gom Omar train+test, Muharaf train(+val), AraMS-28k, KHATT → train.jsonl / val.jsonl; bỏ dòng trùng nhãn tập chấm |
| `lam_cu.py` | làm cũ ảnh: giấy ố, vết bẩn, giấy kẻ, mực thấm mặt sau, con dấu / vân tay màu, chụp điện thoại |
| `huan_luyen.py` | LoRA (ngôn ngữ + ảnh), fp16 + GradScaler trên T4, lưu checkpoint / chạy lại đi tiếp, chấm val định kỳ |

## Chạy (Kaggle, venv dots của htr_test/start.sh)
```bash
cd /kaggle/working/ocr-bench; PY=/kaggle/working/venvs/dots/bin/python
$PY -m htr_train.du_lieu /tmp/htr_data                      # cần HF_TOKEN (Omar); ~8 GB, 20–40 phút
$PY -m htr_train.huan_luyen --data /tmp/htr_data --out /kaggle/working/ft1 --gpu 0 --max-steps 600 --push   # --push: nhật ký lên results-htr/ft1
# chấm model mới bằng đúng benchmark (500 dòng cố định):
$PY -m htr_test.eval_lines --out /kaggle/working/htr_eval_muharaf_n500 --data /kaggle/working/du_lieu_muharaf \
    --split test --n 500 --models baseer_ft1 --lora /kaggle/working/ft1/best --push
```
Mặc định: r=32, α=64, LR 1e-4 (ngôn ngữ) / 2e-5 (ảnh), lô 4 × tích luỹ 4, lấy mẫu muharaf=2 / còn lại 1, làm cũ 50%.
Nhật ký: `<out>/nhat_ky.jsonl`; model tốt nhất (theo CER val): `<out>/best`.
Đã thử CPU với model thu nhỏ (transformers 4.56.1): học → lưu → chấm → chạy lại đi tiếp; LoRA gắn đủ 7 lớp ngôn ngữ + 5 lớp ảnh.
