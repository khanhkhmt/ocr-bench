# Thử 2 model đọc chữ viết tay theo dòng — nhánh `thu-2-model-htr`

Bố cục: **dots.mocr** (như web demo). Đọc chữ: hai model chỉ nhận **ảnh một dòng** → web tách dòng trong từng khối
chữ của dots rồi cho model đọc từng dòng.

| Model | Gốc | Huấn luyện trên | Tác giả công bố |
|---|---|---|---|
| [Ketaba-OCR-LoRA](https://huggingface.co/HassanB4/Ketaba-OCR-LoRA) | LoRA trên sherif1313/Arabic-English-handwritten-OCR-v3 (Qwen2.5-VL-3B), 4-bit | dòng bản thảo viết tay 1951–1965, Ruq'ah / Naskh (hồi ký Omar Al-Saleh, NakbaNLP 2026) | CER 8,19% · WER 25,88% |
| [ArTrOCR-HTR](https://huggingface.co/BushraAlmod03/ArTrOCR-HTR) | microsoft/trocr-base-handwritten | chữ tổng hợp → 11.000 dòng KHATT | CER 12,61% (KHATT) |
| sherif gốc | Ketaba TẮT LoRA | — | để so LoRA giúp bao nhiêu |

Gọi model đúng như code mẫu của tác giả (`htr_test/models.py`).

## Chạy
```bash
tmux new -d -s htr "cd /kaggle/working/ocr-bench && bash htr_test/start.sh 2>&1 | tee /kaggle/working/htr.log"
# VS Code: Ports → Forward 7861 → http://localhost:7861
```
VRAM (T4 15 GB): dots ~7–8 GB + Ketaba 4-bit ~3 GB + ArTrOCR ~1,3 GB. Nút "Giải phóng model đọc dòng" trả VRAM.

## Tách dòng (`htr_test/lines.py`)
- Chiếu ngang (mặc định, nhanh): bỏ đường kẻ của giấy kẻ dòng, tách dòng dính, gộp dấu chấm lẻ.
- Kraken blla (chính xác hơn với chữ tay cổ) nếu có `/kaggle/working/venvs/kraken/bin/kraken`
  (tạo bằng `experiments/real_docs_probe/run_kraken.sh`), không có thì tự dùng chiếu ngang.
