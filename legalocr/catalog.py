"""Danh mục model mã nguồn mở đã tra cứu cho pipeline (cập nhật 2026-10-12). `python -m legalocr models` in bảng này.

Quy ước cột:
- params / license / base: lấy từ API Hugging Face (cardData, safetensors) ngày 2026-10-12 — đã kiểm chứng.
- bench: số do TÁC GIẢ báo cáo, kèm nguồn; KHÔNG phải số đo trên tài liệu của anh/chị. "line" = chấm trên ẢNH DÒNG,
  không so được với CER cả trang.
- vram_t4: "đo" = đã đo trên máy này (2×T4); "ước" = ước tính từ số tham số (fp16 ≈ 2 byte/tham số, nf4 ≈ 0,6) + ảnh.
- role: vai trò đề xuất trong pipeline.
"""

from __future__ import annotations

MODELS = [
    # ---------------- nhận dạng chữ viết tay Ả Rập (HTR) / OCR
    {"id": "Misraj/Baseer__Nakba", "url": "https://huggingface.co/Misraj/Baseer__Nakba",
     "code": "https://github.com/misraj-ai/Nakba-pipeline", "arch": "Qwen2.5-VL-3B (Baseer), tinh chỉnh toàn bộ encoder+decoder, gộp SLERP ep1+ep5",
     "params": "3,75B", "license": "CC-BY-NC-SA-4.0 (phi thương mại)",
     "bench": "NakbaNLP 2026 (hồi ký Omar Al-Saleh, viết tay Palestine 1951–1965), test ẩn, line: CER 0,079 / WER 0,244 — hạng 1/7",
     "bench_src": "https://aclanthology.org/2026.nakbanlp-1.27.pdf",
     "vram_t4": "ước ~8 GiB fp16 (ảnh dòng 644×644)", "role": "engine dòng CHÍNH cho chữ viết tay Ả Rập",
     "note": "prompt gốc 'Extract the text from the above document.', max 128 token/dòng; trọng số bf16 → T4 chạy fp16, cần kiểm tra tràn số"},
    {"id": "sherif1313/Arabic-English-handwritten-OCR-v3", "url": "https://huggingface.co/sherif1313/Arabic-English-handwritten-OCR-v3",
     "arch": "Qwen2.5-VL-3B tinh chỉnh chữ viết tay Ả Rập–Anh", "params": "3,75B", "license": "Apache-2.0",
     "bench": "chưa có số công bố độc lập", "vram_t4": "ước ~8 GiB fp16", "role": "engine dòng thứ hai (đối chứng)",
     "note": "đã chạy trong ocrbench (sherif_handwriting)"},
    {"id": "NAMAA-Space/Qari-OCR-0.4.0-VL-4B-Instruct", "url": "https://huggingface.co/NAMAA-Space/Qari-OCR-0.4.0-VL-4B-Instruct",
     "arch": "LoRA trên Qwen3-VL-4B-Instruct, 45k cặp sách Hồi giáo in", "params": "~4,4B (gốc)", "license": "Apache-2.0",
     "bench": "CER 0,122 / WER 0,256 (tác giả, sách in); Muharaf dòng: CER 167% — bịa 62% lỗi (arXiv 2608.22366)",
     "bench_src": "https://arxiv.org/abs/2608.22366", "vram_t4": "ước ~9 GiB fp16",
     "role": "chỉ cho trang ĐÁNH MÁY / in (giấy uỷ quyền); KHÔNG dùng cho viết tay", "note": "prompt 'Free OCR.'"},
    {"id": "NAMAA-Space/Qari-OCR-v0.3-VL-2B-Instruct", "url": "https://huggingface.co/NAMAA-Space/Qari-OCR-v0.3-VL-2B-Instruct",
     "arch": "Qwen2-VL-2B", "params": "2,21B", "license": "Apache-2.0",
     "bench": "v0.2: CER 0,061 / WER 0,160 trên chữ in có tashkeel (arXiv 2506.02295)", "bench_src": "https://arxiv.org/abs/2506.02295",
     "vram_t4": "ước ~5 GiB fp16", "role": "đối chứng cho trang đánh máy", "note": "hay tự sinh tashkeel → chính sách harakat=consensus"},
    {"id": "dots-studio/dots.mocr", "url": "https://huggingface.co/dots-studio/dots.mocr",
     "arch": "dots.ocr 1.5 (VLM bố cục cả trang: khối + bbox + chữ)", "params": "3,04B", "license": "MIT trên HF; LICENSE AGREEMENT §5.2 hạn chế dữ liệu cá nhân nhạy cảm",
     "bench": "đo ở repo này: Muharaf dev ~51% CER cả trang (5–7 trang, sớm)", "vram_t4": "đo 14,26 GiB ở 5 MP (chiếm trọn 1 card)",
     "role": "engine CẢ TRANG (bố cục + phiếu bầu thứ ba + bắt dòng bị tách sót)", "note": "venv transformers==4.56.1"},
    {"id": "Archatext/hatformer-arams28k", "url": "https://huggingface.co/Archatext/hatformer-arams28k",
     "arch": "HATFormer (TrOCR-base + tokenizer BBPE tiếng Ả Rập)", "params": "0,33B", "license": "CC-BY-NC-SA-4.0",
     "bench": "bài gốc: CER 8,6% trên bộ viết tay lịch sử công khai lớn nhất (line); checkpoint này là bản cộng đồng, chưa rõ dữ liệu",
     "bench_src": "https://arxiv.org/abs/2410.02179", "vram_t4": "ước < 2 GiB", "role": "engine dòng nhẹ, kiến trúc KHÁC VLM (lỗi ít tương quan)",
     "note": "kiểm tra trên dev trước khi tin"},
    {"id": "Qwen/Qwen3-VL-8B-Instruct", "url": "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct",
     "arch": "VLM đa năng, OCR 32 ngôn ngữ (có Ả Rập, Hebrew)", "params": "8,77B", "license": "Apache-2.0",
     "bench": "chưa có số viết tay Ả Rập đáng tin; Qwen2.5-VL-7B Muharaf dòng CER 70,4% (arXiv 2608.22366)",
     "vram_t4": "ước ~6–7 GiB nf4", "role": "dòng HEBREW / Latin (con dấu, mẫu in của chính quyền), scorer ảnh", "note": ""},
    {"id": "QCRI/Fanar-2-Oryx-IVU", "url": "https://huggingface.co/QCRI/Fanar-2-Oryx-IVU",
     "arch": "Qwen2.5-VL-7B tinh chỉnh văn hoá / chữ Ả Rập", "params": "8,29B", "license": "Apache-2.0",
     "bench": "Muharaf dòng CER 70,8%; Madinah trang CER 39,6% (arXiv 2608.22366)", "vram_t4": "ước ~6 GiB nf4",
     "role": "scorer ảnh / phương án dự phòng", "note": ""},
    {"id": "tesseract (ara, heb, eng)", "url": "https://github.com/tesseract-ocr/tesseract",
     "arch": "LSTM, CPU", "params": "-", "license": "Apache-2.0",
     "bench": "Muharaf dòng CER 69,2% nhưng bỏ sót 47,7% (ít bịa) (arXiv 2608.22366)", "vram_t4": "CPU",
     "role": "phiếu đối chứng rẻ; engine chính cho dòng Hebrew in (cần tesseract-ocr-heb)", "note": ""},
    # ---------------- bố cục / vùng không phải chữ
    {"id": "kraken blla", "url": "https://github.com/mittagessen/kraken", "arch": "U-Net tách dòng (baseline + đa giác), RTL",
     "params": "-", "license": "Apache-2.0", "bench": "-", "vram_t4": "CPU ~23–28 s/trang (đo ở repo này)",
     "role": "tách DÒNG (đầu vào của engine dòng)", "note": "venv riêng: inference/setup_kraken.sh"},
    {"id": "mdefrance/yolos-base-signature-detection", "url": "https://huggingface.co/mdefrance/yolos-base-signature-detection",
     "arch": "YOLOS-base", "params": "0,13B", "license": "Apache-2.0", "bench": "-", "vram_t4": "CPU ~2,5 s/trang",
     "role": "chữ ký", "note": "đã dùng trong ocrbench/pictures.py"},
    {"id": "Ooredoo-Group/ooredoo-stamp-detection", "url": "https://huggingface.co/Ooredoo-Group/ooredoo-stamp-detection",
     "arch": "YOLOS-small, 1 lớp 'stamp'", "params": "0,03B", "license": "Apache-2.0",
     "bench": "mAP 0,99 tự báo, chỉ 350 ảnh huấn luyện", "vram_t4": "CPU", "role": "con dấu", "note": "kiểm tra trên con dấu thật trước khi tin"},
    # ---------------- LLM hiệu chỉnh theo ngữ cảnh (chỉ GỢI Ý)
    {"id": "Qwen/Qwen3-8B", "url": "https://huggingface.co/Qwen/Qwen3-8B", "arch": "LLM dày", "params": "8,19B",
     "license": "Apache-2.0", "bench": "-", "vram_t4": "đo 6,0 GiB nf4; 11 → 43 tok/s (batch 1 → 8)",
     "role": "LLM gợi ý mặc định", "note": "enable_thinking=False"},
    {"id": "ALLaM-AI/ALLaM-7B-Instruct-preview", "url": "https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview",
     "arch": "Llama, huấn luyện Ả Rập–Anh (SDAIA)", "params": "7,00B", "license": "Apache-2.0", "bench": "-",
     "vram_t4": "đo 4,4 GiB nf4; 16 → 66 tok/s", "role": "LLM gợi ý thứ hai (bỏ phiếu 2 LLM)", "note": ""},
    {"id": "QCRI/Fanar-1-9B-Instruct", "url": "https://huggingface.co/QCRI/Fanar-1-9B-Instruct", "arch": "Gemma-2-9B tiếp tục huấn luyện Ả Rập",
     "params": "8,78B", "license": "Apache-2.0", "bench": "-", "vram_t4": "ước ~6,5 GiB nf4", "role": "LLM thay thế", "note": ""},
    {"id": "QCRI/Fanar-2-27B-Instruct", "url": "https://huggingface.co/QCRI/Fanar-2-27B-Instruct", "arch": "Gemma-3-27B",
     "params": "27,0B", "license": "Apache-2.0", "bench": "-", "vram_t4": "ước ~17 GiB nf4 → KHÔNG vừa 1 T4",
     "role": "chỉ khi có GPU ≥ 24 GB", "note": ""},
    {"id": "inceptionai/Jais-2-8B-Chat", "url": "https://huggingface.co/inceptionai/Jais-2-8B-Chat", "arch": "Jais-2",
     "params": "8,09B", "license": "Apache-2.0 (gated: cần token HF)", "bench": "-", "vram_t4": "ước ~6 GiB nf4",
     "role": "LLM thay thế", "note": "cần transformers 5.x (kiến trúc jais2)"},
    {"id": "dicta-il/dictalm2.0-instruct", "url": "https://huggingface.co/dicta-il/dictalm2.0-instruct", "arch": "Mistral-7B tiếng Hebrew",
     "params": "7,25B", "license": "Apache-2.0", "bench": "-", "vram_t4": "ước ~5 GiB nf4", "role": "gợi ý cho dòng Hebrew", "note": ""},
    {"id": "CAMeL-Lab/bert-base-arabic-camelbert-msa-ner", "url": "https://huggingface.co/CAMeL-Lab/bert-base-arabic-camelbert-msa-ner",
     "arch": "BERT NER (PERS/LOC/ORG)", "params": "~0,11B", "license": "Apache-2.0", "bench": "-", "vram_t4": "CPU",
     "role": "tuỳ chọn: bổ sung nhận diện tên / địa danh cho entities.py", "note": "huấn luyện trên văn bản sạch — trên OCR nhiễu kém hơn"},
]

DATASETS = [
    {"id": "U4RASD/omar-al-saleh-manuscripts-segments", "url": "https://huggingface.co/datasets/U4RASD/omar-al-saleh-manuscripts-segments",
     "what": "ảnh dòng hồi ký viết tay Palestine 1951–1965 (NakbaNLP 2026), train/test/blind_test", "license": "CC-BY-4.0 (gated)",
     "use": "tập dev GẦN NHẤT với hồ sơ của anh/chị để chọn engine + hiệu chỉnh ngưỡng"},
    {"id": "TheRealOKAI/muharaf-public-pages", "url": "https://huggingface.co/datasets/TheRealOKAI/muharaf-public-pages",
     "what": "trang thư / hồ sơ viết tay Levant thế kỷ 20 (Muharaf, NeurIPS 2024)", "license": "gốc CC BY-NC-SA",
     "use": "đã có cache dots ở /kaggle/working/pc_eval"},
]

PAPERS = [
    ("Misraj AI at AR-MS NAKBA-NLP 2026", "https://aclanthology.org/2026.nakbanlp-1.27.pdf",
     "tinh chỉnh Muharaf → Nakba, mở khoá vision encoder: CER 0,19 → 0,08; Gemini 3.1 Pro zero-shot 0,22"),
    ("NakbaNLP 2026 shared task overview", "https://aclanthology.org/2026.nakbanlp-1.7/", "6.395 trang, 7 đội, baseline CER 0,368"),
    ("When Do VLMs Help Arabic Manuscript OCR? (2026)", "https://arxiv.org/abs/2608.22366",
     "VLM sửa có điều kiện OCR chỉ giúp khi OCR còn 'khôi phục được'; chỉ sharpen giúp; bịa 16–62% lỗi; tashkeel làm CER tăng"),
    ("Consensus Entropy (2025/2026)", "https://arxiv.org/abs/2504.11101",
     "đồng thuận nhiều VLM để tự kiểm OCR: F1 phát hiện lỗi +42,1% so với VLM-as-judge"),
    ("Beyond Recognition: Athar / Phoenix (2026)", "https://arxiv.org/abs/2608.19385",
     "giữ cách đọc theo ảnh, phương án có giới hạn, LM cục bộ dùng thận trọng, xuất TEI/PAGE-XML; rerank N-best gỡ < 4% khoảng trần"),
]


def table() -> str:
    rows = ["| model | vai trò | kiến trúc | tham số | giấy phép | VRAM T4 | benchmark (nguồn tác giả) |",
            "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        rows.append(f"| [{m['id']}]({m['url']}) | {m['role']} | {m['arch']} | {m['params']} | {m['license']} | "
                    f"{m['vram_t4']} | {m['bench']} |")
    return "\n".join(rows)
