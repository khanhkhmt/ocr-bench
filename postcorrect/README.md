# postcorrect — LLM sửa lỗi + khoanh từ lỗi cho output OCR (dots.mocr)

Ghép sau dots.mocr để (1) sửa lỗi OCR chữ viết tay Ả Rập và (2) chỉ ra từ nghi lỗi, **kèm cách đo xem nó có giảm lỗi thật
không**. Module riêng: chỉ *gọi* `ocrbench` (adapter dots, metrics, normalize), không sửa gì trong đó.

**Quy tắc cứng:** mọi model chạy **cục bộ** (không API ngoài); dữ liệu thật không rời máy và không vào repo; chưa fine-tune
(chỉ zero/few-shot). Kết quả đo và khuyến nghị: [docs/POSTCORRECT_RESULTS.md](../docs/POSTCORRECT_RESULTS.md).

## Sơ đồ

```
ảnh ─► dots.mocr (1 card, ~14 GiB, ~2,4 phút/trang)  ──►  CACHE OCR (JSON mỗi trang: khối, chữ, độ tin cậy token)
                                                              │  "OCR một lần, thử LLM nhiều lần"
        ┌─────────────────────────────────────────────────────┘
        ▼
  văn bản trang (chỉ khối Text/Title/Section-header/List-item/Caption/Footnote; KHÔNG bảng, hình, đầu/chân trang)
        ▼  chunk ~700 ký tự, ngắt ở xuống dòng / dấu câu, giữ thứ tự (chunking.py)
  ┌── A: LLM viết lại chunk (<output>…</output>) ─┐
  ├── B: LLM trả JSON [{word, fix}] (chỉ khoanh)  ├─► diff mức từ ─► CHỐT CHẶN (guard.py) ─► {original, corrected, edits[]}
  └── C: như A nhưng chỉ được đổi từ NLL cao  ────┘                   (không qua = giữ nguyên bản OCR)
```

## Chạy

```bash
pip install -e ".[postcorrect]"                         # + tesseract không cần; dots cần venv riêng (xem inference/README.md)
# 1) dữ liệu đánh giá công khai (Muharaf, ngoài repo)
python -m postcorrect dataset muharaf --out /kaggle/working/pc_eval/muharaf --n 100
# 2) OCR một lần, MỖI GPU MỘT TIẾN TRÌNH (dots chiếm trọn 1 card T4), python của venv dots
for g in 0 1; do PYTHONPATH=. CUDA_VISIBLE_DEVICES=$g /kaggle/working/venvs/dots/bin/python -m postcorrect.ocr_cache \
    --manifest M --out OCR --worker gpu$g --split dev & done
# 3) sửa lỗi từ cache (một tiến trình mỗi GPU: --device i --shard i/2)
python -m postcorrect correct-cache --ocr OCR --manifest M --out RUN --model Qwen/Qwen3-8B --strategy A --split dev
# 4) đo
python -m postcorrect eval --manifest M --runs A=RUN_A B=RUN_B --split dev
python -m postcorrect analyze --ocr OCR --manifest M --split dev --model Qwen/Qwen3-8B     # tín hiệu khoanh từ lỗi
# 1 ảnh → JSON (dots ở GPU 0, LLM ở GPU 1)
python -m postcorrect correct-image trang.png --model Qwen/Qwen3-8B --strategy C
```

Mỗi trang ra một JSON: `{id, original, corrected, edits:[{index, span, from, to, chunk, block}], flags, rejected, chunks, settings}`;
`index` là chỉ số từ (tách theo khoảng trắng) trong `original`; `rejected` ghi lý do từng sửa bị chốt chặn loại.

## Chốt chặn (guard.py) — "nghi ngờ thì KHÔNG sửa"

| Luật | Lý do |
|---|---|
| Từ có chữ số / chữ Latin / `@` / lõi 1 chữ cái → không bao giờ sửa | số, ngày, mã, tên Latin; một chữ cái thì chỉ là đoán mò |
| Chỉ nhận thay 1→1 (≤ 2 ký tự khác, ≤ 50% độ dài), tách 1→2, gộp 2→1 (chữ cái gần như giữ nguyên) | lỗi OCR kiểu nét / dấu chấm / dính-tách từ; không nhận viết lại |
| Khác nhau chỉ ở tashkeel / dấu câu → bỏ; không để LLM thêm tashkeel | ngoài phạm vi |
| Chunk lệch > 10% số từ, hoặc > 35% số từ bị sửa → bỏ **cả chunk** | LLM đang viết lại / bịa (đã thấy: 10 từ → 67 từ) |
| Chiến lược C: chỉ nhận sửa ở từ được đánh dấu | LLM không được đụng chỗ khác |
| Không parse được / thiếu thẻ → giữ nguyên chunk | |

Mọi ngưỡng ở `GuardConfig`, chỉnh trên tập **dev**; tập **holdout** chỉ chấm một lần ở cuối.

## Đánh giá (evaluate.py)

CER/WER trước-sau (chuẩn hoá của `ocrbench`, **strict** không gộp أ/إ/ا và ى/ي), KTC 95% bootstrap theo trang;
mỗi sửa được chấm bằng độ giảm khoảng cách ký tự tới đáp án (`fixed / improved / harm / worse / neutral`);
**tỉ lệ sửa nhầm** = số từ đúng bị đổi / số từ đúng của OCR; "tầm với" = số từ OCR sai mà chốt chặn *có thể* sửa (≤ 2 ký tự).

## Tài nguyên (đo trên 2×T4, 15 GiB mỗi card)

dots.mocr chiếm ~14,3 GiB một card ở 4,6–5 MP → không chung card với LLM. LLM 4-bit nf4: Qwen3-8B 6,0 GiB
(11 → 43 tok/s khi batch 1 → 8), ALLaM-7B 4,4 GiB (16 → 66 tok/s). T4 không có bf16, không NVLink: dùng hai tiến trình
độc lập, mỗi tiến trình một card.

## Giới hạn

- Bộ đánh giá công khai (Muharaf: thư viết tay thế kỷ 20, tiếng địa phương Levant) **không phải** tài liệu đất đai cổ của người
  dùng; kết luận về mức nhiễu và tỉ lệ sửa nhầm cần được kiểm lại trên mẫu thật có phiên âm.
- Muharaf gốc CC BY-NC-SA 4.0 (bản HF ghi MIT): chỉ dùng nghiên cứu, không phân phối lại.
- Giấy phép trọng số dots.mocr §5.2: không xử lý tài liệu có dữ liệu cá nhân nhạy cảm nếu chưa có đồng ý + ẩn danh hoá.
