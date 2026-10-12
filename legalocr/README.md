# legalocr — OCR có kiểm chứng cho hồ sơ pháp lý tiếng Ả Rập (Palestine, thập niên 1950–1980)

Hợp đồng mua bán đất, giấy uỷ quyền: viết tay hoặc đánh máy, lẫn Hebrew / chữ số / Latin, giấy cũ, con dấu, vân tay.
Mục tiêu không phải văn bản *trôi chảy* mà văn bản *kiểm chứng được*: mỗi từ in ra biết **ai đọc** (model OCR nào, hay
người duyệt), **chắc tới đâu**, và **xem ở đâu trên ảnh gốc**.

## Nguyên tắc cứng (đã cài vào code, có test)

| # | Nguyên tắc | Ở đâu |
|---|---|---|
| 1 | Chữ in ra chỉ đến từ model OCR đọc ảnh (bỏ phiếu nhiều model) hoặc từ người duyệt. **LLM không ghi vào bản nguyên văn.** | `fuse.py`, `suggest.py`, `export.py` |
| 2 | Tên, địa danh, số, ngày, số tiền, thửa đất, điều khoản, từ phủ định = **từ quan trọng**: phải ≥ 2 model cùng đọc, chữ số khớp từng chữ số, ngưỡng tin cậy cao hơn. | `entities.py`, `fuse.decide_status` |
| 3 | LLM bị **khoá** với từ quan trọng: chỉ được chọn trong các cách đọc OCR đã có hoặc trả null. Từ thường: chỉ đề xuất chữ cùng khung nét (khác dấu chấm / ≤ 2 ký tự). | `suggest.validate` |
| 4 | Gợi ý của LLM được **chấm lại bằng ảnh dòng** (VLM teacher forcing): ảnh bác bỏ → đánh dấu. | `suggest.suggest_page`, `VLMEngine.score` |
| 5 | Chưa chắc → `từ[؟]`; không đọc được → `[؟]`; chữ chỉ thiểu số model thấy (nghi bịa) → bỏ khỏi văn bản, ghi vào báo cáo. | `export.py`, `crosscheck.py` |
| 6 | Mỗi từ cần duyệt có **ảnh cắt từ ảnh gốc** (chỉ xoay/phóng, không lọc màu) + SHA-256 file nguồn. | `evidence.py` |
| 7 | Không tự gộp chính tả (أ/ا, ة/ه, ى/ي): bỏ phiếu theo nguyên văn; harakat chỉ giữ khi mọi model đồng ý. | `script.vote_key`, `fuse._surface` |

## Sơ đồ

```
ảnh scan ─► preprocess.prepare ──► ảnh HÌNH HỌC (xoay/phóng; cắt bằng chứng)   ┐
            │                     ảnh ĐỌC (+ phẳng nền, tương phản; tuỳ chọn:   │ cùng toạ độ
            │                     xoá dòng kẻ, che lỗ đục, làm nét)             ┘
            ▼
   segment: kraken blla → DÒNG (đa giác, thứ tự đọc phải→trái)  + chữ ký (YOLOS) / con dấu (YOLOS) / vân tay, tem
            ▼                                                       (vùng này không đưa LLM, in [توقيع] / [ختم])
   engines: mỗi dòng → N model đọc (vd. Baseer__Nakba, sherif-handwriting-v3, Tesseract)  + dots.mocr đọc CẢ TRANG
            │   (log-prob từng token → xác suất từng từ; cắt vòng lặp)
            ▼
   align + fuse: căn từ kiểu ROVER (cho tách/gộp từ) → bỏ phiếu có trọng số → chữ được chọn + đặc trưng
            │   chữ viết của dòng (ar/he/lat) quyết định model nào được bỏ phiếu (model Ả Rập không đọc dòng Hebrew)
            ▼
   entities: khoanh tên / địa danh / số tiền (cả số viết bằng chữ) / ngày / thửa đất / số giấy tờ / điều khoản / phủ định
            ▼
   decide_status: read | uncertain | illegible   (ngưỡng chặt hơn cho từ quan trọng; hiệu chỉnh trên dev)
            ▼
   crosscheck: số ≠ chữ · ngày sai · tên viết khác nhau · thiếu điều khoản · dòng không đọc được · mật độ chữ lệch ·
            │  lặp · chữ chỉ model trang thấy (dòng bị sót?) — chỉ HẠ trạng thái, không sửa chữ
            ▼
   (tuỳ chọn) suggest: LLM cục bộ gợi ý cho từ chưa chắc (khoá với từ quan trọng) → VLM chấm gợi ý theo ảnh dòng
            ▼
   evidence + export: <id>.json · .diplomatic.txt · .annotated.txt · .fields.json · .page.xml · .review.html
            ▼
   người duyệt (phiếu HTML: ảnh cắt, các cách đọc, gợi ý) → decisions.json → apply-review → .final.txt
```

## Model đề xuất (tra cứu 2026-10-12; `python -m legalocr models` in bảng đầy đủ)

Giấy phép / số tham số lấy từ API Hugging Face; benchmark là số **tác giả công bố**, chưa đo trên hồ sơ của anh/chị.

| Vai trò | Model | Kiến trúc · tham số | Giấy phép | Benchmark (nguồn) | VRAM T4 |
|---|---|---|---|---|---|
| HTR dòng chính | [Misraj/Baseer__Nakba](https://huggingface.co/Misraj/Baseer__Nakba) | Qwen2.5-VL-3B, tinh chỉnh toàn bộ, 3,75B | **CC-BY-NC-SA-4.0** | NakbaNLP 2026 (viết tay Palestine 1951–65), **ảnh dòng**: CER 0,079 / WER 0,244, hạng 1/7 ([bài](https://aclanthology.org/2026.nakbanlp-1.27.pdf)) | ~8 GiB fp16 (ước) |
| HTR dòng đối chứng | [sherif1313/Arabic-English-handwritten-OCR-v3](https://huggingface.co/sherif1313/Arabic-English-handwritten-OCR-v3) | Qwen2.5-VL-3B, 3,75B | Apache-2.0 | chưa có số độc lập | ~8 GiB (ước) |
| HTR nhẹ, kiến trúc khác | [Archatext/hatformer-arams28k](https://huggingface.co/Archatext/hatformer-arams28k) | TrOCR-base (HATFormer), 0,33B | CC-BY-NC-SA-4.0 | bài gốc CER 8,6% dòng lịch sử ([arXiv 2410.02179](https://arxiv.org/abs/2410.02179)); checkpoint cộng đồng | < 2 GiB |
| Cả trang + bố cục | [dots-studio/dots.mocr](https://huggingface.co/dots-studio/dots.mocr) | 3,04B | MIT trên HF, nhưng LICENSE §5.2 hạn chế dữ liệu cá nhân | đo ở repo: Muharaf ~51% CER trang | 14,3 GiB (đo) |
| Trang đánh máy | [NAMAA-Space/Qari-OCR-0.4.0-VL-4B](https://huggingface.co/NAMAA-Space/Qari-OCR-0.4.0-VL-4B-Instruct) | LoRA Qwen3-VL-4B | Apache-2.0 | CER 0,122 sách in; **Muharaf viết tay CER 167%, bịa 62% lỗi** ([arXiv 2608.22366](https://arxiv.org/abs/2608.22366)) → không dùng cho viết tay | ~9 GiB |
| Hebrew / Latin, scorer | [Qwen/Qwen3-VL-8B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct) | 8,77B | Apache-2.0 | OCR 32 ngôn ngữ (có he); chưa có số viết tay | ~6–7 GiB nf4 |
| Phiếu cổ điển | Tesseract 5 (ara, heb, eng) | LSTM, CPU | Apache-2.0 | Muharaf dòng CER 69,2%, ít bịa, bỏ sót 47,7% (arXiv 2608.22366) | CPU |
| Tách dòng | [kraken](https://github.com/mittagessen/kraken) blla | U-Net | Apache-2.0 | — | CPU ~25 s/trang |
| Chữ ký / con dấu | [yolos-base-signature](https://huggingface.co/mdefrance/yolos-base-signature-detection), [ooredoo-stamp-detection](https://huggingface.co/Ooredoo-Group/ooredoo-stamp-detection) | YOLOS 0,13B / 0,03B | Apache-2.0 | con dấu: mAP 0,99 tự báo, 350 ảnh | CPU |
| LLM gợi ý | [Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B), [ALLaM-7B-Instruct-preview](https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview) | 8,19B / 7,00B | Apache-2.0 | — | 6,0 / 4,4 GiB nf4 (đo) |
| LLM thay thế | [QCRI/Fanar-1-9B-Instruct](https://huggingface.co/QCRI/Fanar-1-9B-Instruct), [Jais-2-8B-Chat](https://huggingface.co/inceptionai/Jais-2-8B-Chat) (gated), [dictalm2.0-instruct](https://huggingface.co/dicta-il/dictalm2.0-instruct) (Hebrew) | 8,8B / 8,1B / 7,3B | Apache-2.0 | — | ~5–6,5 GiB nf4 |

**Về con số Baseer__Nakba (CER 8% / WER 24%)** — đã xác minh trong bài báo: đó là CER *corpus* trên tập test ẩn của
NakbaNLP 2026, **chấm trên ảnh dòng đã cắt sẵn** (trung bình 614×52 px, ~57 ký tự/dòng) của **một** bộ hồi ký (Omar
Al-Saleh), sau khi tinh chỉnh trên chính bộ đó + Muharaf. CER 36–55% của anh/chị là **cả trang**, gồm lỗi tách
dòng / thứ tự đọc / bố cục. Không so trực tiếp được; muốn so phải tách dòng rồi chấm theo dòng (lệnh `eval` chấm cả trang
theo căn chỉnh từ). Cùng bài: Gemini 3.1 Pro zero-shot CER 0,22; Baseer chỉ tinh chỉnh trên Nakba 3 epoch CER 0,19;
thêm Muharaf + mở khoá vision encoder (lr 9e-6, decoder 1e-4) + gộp checkpoint → 0,08.

**Bằng chứng nghiên cứu cho các lựa chọn thiết kế**
- VLM sửa lỗi có điều kiện theo OCR chỉ giúp khi bản OCR còn "khôi phục được"; nhị phân hoá / khử nhiễu làm VLM kém đi,
  chỉ làm nét có ích; VLM bịa 16–62% số lỗi; prompt "cho phép null" giảm bịa trường thông tin ([arXiv 2608.22366](https://arxiv.org/abs/2608.22366)).
- Đồng thuận nhiều VLM là tín hiệu tự kiểm OCR tốt hơn VLM-làm-giám-khảo (+42,1% F1) ([Consensus Entropy](https://arxiv.org/abs/2504.11101)).
- Xếp hạng lại N-best bằng LM chỉ gỡ < 4% khoảng cách tới trần; nên giữ cách đọc theo ảnh, đưa phương án có giới hạn
  cho người duyệt, xuất PAGE-XML ([arXiv 2608.19385](https://arxiv.org/abs/2608.19385)).
- Ở repo này (postcorrect, Muharaf dev): chỉ ~16% từ sai là "sai gần" (≤ 2 ký tự) → bộ sửa hoàn hảo trong giới hạn đó
  chỉ giảm CER ~3,8 điểm. Cải thiện lớn phải đến từ **nhận dạng tốt hơn** (dòng + model HTR + tinh chỉnh), không từ LLM.

## Chạy

```bash
bash inference/setup_kraken.sh                      # một lần: venv kraken (CPU)
# 1 trang: 2 HTR dòng + Tesseract, dots.mocr từ cache làm phiếu cả trang, LLM gợi ý ở GPU 1, scorer = model khác trụ
python -m legalocr run trang.jpg --out out/ \
   --engine vlm:Misraj/Baseer__Nakba@1.0 --engine vlm:sherif1313/Arabic-English-handwritten-OCR-v3@0.8 \
   --engine tesseract:ara@0.5 --dots-cache /kaggle/working/pc_eval/ocr \
   --llm Qwen/Qwen3-8B --llm-device 1 --scorer sherif1313/Arabic-English-handwritten-OCR-v3 \
   --doc-type auto --years 1940 1995 --pre sharpen
# dòng Hebrew (con dấu, mẫu đơn in của chính quyền): thêm engine chỉ bỏ phiếu trên dòng he/lat (sau dấu #)
#   --engine tesseract:heb@0.6#he,lat --engine vlm:Qwen/Qwen3-VL-8B-Instruct@0.7#he,lat,mixed   (cần tesseract-ocr-heb)
# mở out/trang.review.html → duyệt → "Xuất quyết định" → trang.decisions.json
python -m legalocr apply-review out/trang.json trang.decisions.json --out final/
# có đáp án (dev): đo + hiệu chỉnh ngưỡng, rồi chạy lại phần bỏ phiếu không cần GPU
python -m legalocr eval out/*.json --gt-dir gt/
python -m legalocr calibrate out/*.json --gt-dir gt/ --target 0.02 --target-critical 0.005 --out cal.json
python -m legalocr refuse out/*.json --calibration cal.json --out out_cal/
```

Hai VLM ~3,75B cùng một card T4 fp16 không vừa (≈ 2 × 8 GiB): chạy lần lượt (mỗi engine nạp khi cần, `close()` sau khi
đọc xong) hoặc mỗi card một engine. dots.mocr chiếm trọn một card → chạy riêng bằng `postcorrect.ocr_cache`, dùng lại cache.

## Độ tin cậy và người duyệt

Đặc trưng mỗi từ (`fuse.FEATURES`): tỉ trọng model đồng ý (`support`), đồng ý về khung chữ (`rasm_support` — cùng nét,
khác dấu chấm), xác suất model tự báo (`p_mean`), số model, độ dài, có chữ số, model trụ có bỏ sót không, có quan trọng không.
Mặc định (chưa hiệu chỉnh): 1 model → `0,9·p`; ≥ 2 model → `support·(0,5 + 0,5·p)`; ngưỡng read 0,75 / quan trọng 0,90.
`calibrate` học hồi quy logistic trên dev rồi chọn ngưỡng nhỏ nhất để **tỉ lệ sai trong phần KHÔNG đánh dấu** ≤ mục tiêu
(mặc định 2% từ thường, 0,5% từ quan trọng). `eval` báo đúng các con số người duyệt cần:

| chỉ số | ý nghĩa |
|---|---|
| `residual_error` | tỉ lệ từ sai trong các từ in KHÔNG kèm [؟] — rủi ro còn lại nếu chỉ duyệt chỗ có [؟] |
| `flag_recall` | phần lỗi đã bị đánh dấu (lỗi không lọt qua) |
| `flag_precision` | phần đánh dấu là lỗi thật (công duyệt không phí) |
| `flag_rate` | tỉ lệ từ phải duyệt |
| `ece` | độ lệch giữa độ tin cậy và tỉ lệ đúng thật |

## Chạy thử thật (2026-10-12, CPU — GPU đang bận việc khác)

Một trang Muharaf **dev** viết tay (`muharaf_0010`, 42 từ, 11 dòng tách bằng `ProjectionSegmenter(mode="valley")`),
trọng số mặc định chưa hiệu chỉnh (Baseer 1,0 · HATFormer 0,7 · dots 0,7 · Tesseract 0,5). **Không phải benchmark:**
1 trang, và Baseer__Nakba lẫn HATFormer đều đã huấn luyện trên Muharaf → số lạc quan. Chỉ để chứng minh đường code chạy
thật và cho thấy dạng đánh đổi.

| | CER | WER |
|---|---|---|
| Tesseract 5 ara | 57,4% | 135,7% |
| HATFormer (Archatext/hatformer-arams28k) | 25,6% | 66,7% |
| Baseer__Nakba | 23,6% | 61,9% |
| dots.mocr (cả trang, cache) | 29,3% | 69,0% |
| bỏ phiếu — cách đọc tốt nhất ở MỌI từ | **20,7%** | **52,4%** |
| bỏ phiếu — bản nguyên văn (`[؟]` = để trống, 7 từ) | 30,2% | 50,0% |

Cờ `[؟]`: bắt **20/20** từ sai (sai còn lại ngoài phần đánh dấu: 0/6), nhưng phải đánh dấu 36/42 từ (86%) và ECE 0,28 —
đúng như dự kiến khi chưa hiệu chỉnh trên trang khó: ngưỡng mặc định bảo thủ, cần `calibrate` trên dev của bộ hồ sơ.
Tốc độ CPU (4 nhân, dùng chung): Baseer__Nakba fp32 ~1 phút/dòng khi chạy theo lô (631 s / 11 dòng), HATFormer 151 s,
Tesseract 3 s. `VLMEngine.score` phân biệt rõ cách đọc đúng (−0,26 nat/token) với chuỗi bị đảo (−4,72).

## Giới hạn — đọc trước khi dùng kết quả

- **Chưa đo trên hồ sơ thật của anh/chị** (không có trên máy). Số trong bảng là số tác giả; ngưỡng mặc định là ước lượng
  bảo thủ. Cần ~20–50 trang có phiên âm để chạy `eval` + `calibrate` trước khi tin tỉ lệ [؟].
- Trọng số Baseer__Nakba, HATFormer: **phi thương mại** (CC-BY-NC-SA-4.0). dots.mocr: điều khoản §5.2 về dữ liệu cá
  nhân nhạy cảm — hợp đồng đất có tên, số căn cước → hỏi pháp lý trước khi dùng trên hồ sơ thật. Mọi model chạy cục bộ.
- Bộ dữ liệu gần nhất với hồ sơ của anh/chị: [omar-al-saleh-manuscripts-segments](https://huggingface.co/datasets/U4RASD/omar-al-saleh-manuscripts-segments)
  (CC-BY-4.0, gated — cần token HF). Baseer__Nakba đã huấn luyện trên Muharaf → chấm Muharaf sẽ lạc quan.
- Bộ từ khoá (`entities.py`) viết tay theo kiến thức chung về hợp đồng Levant; bổ sung tên làng / dòng họ / thuật ngữ
  của bộ hồ sơ qua `lexicon_from_file` / `extra_lexicon` (chỉ dùng để KHOANH, không dùng để sửa).
- `ProjectionSegmenter` chỉ là dự phòng (trang một cột); trang thật dùng kraken.
- Hebrew viết tay: chưa có model mở đáng tin; dòng Hebrew in (con dấu, mẫu đơn) → Tesseract `heb` + Qwen3-VL.
