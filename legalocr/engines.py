"""Các model đọc chữ ("engine"). Mỗi engine đọc ẢNH DÒNG (line engine) hoặc cả trang (page engine), trả về chữ kèm
xác suất từng từ nếu model có — để bỏ phiếu và tính độ tin cậy.

- TesseractEngine : LSTM cổ điển, CPU, lỗi KHÁC KIỂU với VLM (không bịa câu trôi chảy; đọc thiếu thay vì đọc thừa) → một
                    phiếu đối chứng rẻ. Cần gói ngôn ngữ: ara (Ả Rập), heb (Hebrew), eng.
- VLMEngine       : họ Qwen2/2.5/3-VL qua transformers (Baseer__Nakba, Arabic-English-handwritten-OCR-v3, Qari...).
                    Đọc theo lô, ghi log-prob từng token → xác suất từng từ; `score()` chấm một chuỗi cho trước có nhìn ảnh
                    (teacher forcing) — dùng để kiểm chứng gợi ý của LLM bằng ẢNH.
- DotsCacheEngine : đọc cả trang từ cache OCR của dots.mocr (postcorrect.ocr_cache), có độ tin cậy token.
- StaticEngine    : chữ đã có sẵn (JSON) — chạy lại bước bỏ phiếu / kiểm tra mà không cần GPU; dùng cho test.
"""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from postcorrect.text import words_with_spans

ALL_SCRIPTS = frozenset({"ar", "he", "lat", "digit", "mixed"})


@dataclass
class Reading:
    text: str
    word_probs: list[float | None] | None = None
    boxes: list[list[int]] | None = None    # khung từng từ trong ảnh dòng (nếu engine có, vd. Tesseract)
    meta: dict = field(default_factory=dict)

    @property
    def words(self) -> list[str]:
        return self.text.split()


def trim_loops(words: list[str], max_period: int = 6, min_repeats: int = 3) -> tuple[list[str], bool]:
    """Cắt vòng lặp cuối chuỗi (một cụm ≤ max_period từ lặp liên tiếp ≥ min_repeats lần) — kiểu lỗi VLM hay gặp."""
    n = len(words)
    for p in range(1, max_period + 1):
        reps, k = 1, n - p
        while k - p >= 0 and words[k - p:k] == words[k:k + p]:
            reps += 1
            k -= p
        if reps >= min_repeats:
            return words[:k + p], True
    return words, False


class TesseractEngine:
    """psm 7 (một dòng); dòng nào ra rỗng thì thử psm 13 (dòng thô, không phân tích bố cục) — đo trên ảnh hợp đồng
    tổng hợp: một dòng psm 7 rỗng, psm 13 đọc đủ."""

    def __init__(self, name: str = "tesseract", lang: str = "ara", psm: tuple = (7, 13), weight: float = 0.6,
                 scripts=ALL_SCRIPTS, timeout: float = 60):
        self.name, self.lang, self.weight, self.scripts, self.timeout = name, lang, weight, scripts, timeout
        self.psm = (psm,) if isinstance(psm, int) else tuple(psm)

    def _one(self, im, psm: int) -> Reading:
        import pytesseract

        try:
            d = pytesseract.image_to_data(im, lang=self.lang, config=f"--psm {psm}",
                                          output_type=pytesseract.Output.DICT, timeout=self.timeout)
        except RuntimeError:  # quá thời gian
            return Reading("", [], [], {"error": "timeout", "psm": psm})
        words, probs, boxes = [], [], []
        for i, t in enumerate(d["text"]):
            t = clean_text(t)
            if not t or float(d["conf"][i]) < 0:
                continue
            for piece in t.split():
                words.append(piece)
                probs.append(max(0.0, min(1.0, float(d["conf"][i]) / 100)))
                boxes.append([d["left"][i], d["top"][i], d["left"][i] + d["width"][i], d["top"][i] + d["height"][i]])
        return Reading(" ".join(words), probs, boxes, {"psm": psm})

    def read(self, crops) -> list[Reading]:
        os.environ.setdefault("OMP_THREAD_LIMIT", "1")  # nhiều luồng OpenMP tranh nhau trên máy ít nhân
        out = []
        for im in crops:
            r = Reading("")
            for psm in self.psm:
                r = self._one(im, psm)
                if r.text:
                    break
            out.append(r)
        return out


# Cấu hình suy luận theo mã gốc của tác giả (github.com/misraj-ai/Nakba-pipeline, Baseer_Nakba.py): prompt, system,
# dải điểm ảnh của processor, repetition_penalty, 128 token / dòng.
PRESETS = {
    "Misraj/Baseer__Nakba": {"prompt": "Extract the text from the above document.",
                             "system_prompt": "You are a helpful assistant.",
                             "processor_kwargs": {"min_pixels": 28 * 28, "max_pixels": 1280 * 28 * 28},
                             "generation_kwargs": {"repetition_penalty": 1.1}, "max_new_tokens": 128},
    "sherif1313/Arabic-English-handwritten-OCR-v3": {
        "prompt": "ارجو استخراج النص العربي كاملاً من هذه الصورة من البداية الى النهاية بدون اي اختصار ودون ذيادة او حذف. "
                  "اقرأ كل المحتوى النصي الموجود في الصورة:", "max_new_tokens": 256},
    "NAMAA-Space/Qari-OCR-0.4.0-VL-4B-Instruct": {"prompt": "Free OCR.", "max_new_tokens": 256},
}


class VLMEngine:
    """Họ Qwen-VL đọc ảnh dòng. Trên T4 (không bf16): dtype float16; model bf16 bị tràn số thì thử float32 hoặc nf4.
    Tham số không truyền thì lấy theo PRESETS[model_id] (nếu có), rồi mới tới mặc định."""

    def __init__(self, model_id: str, name: str | None = None, prompt: str | None = None,
                 system_prompt: str | None = None, device: str = "cuda:0", dtype: str = "float16",
                 quant: str | None = None, max_new_tokens: int | None = None, batch_size: int = 8, weight: float = 1.0,
                 scripts=frozenset({"ar", "digit", "mixed"}), processor_kwargs: dict | None = None,
                 generation_kwargs: dict | None = None):
        pre = PRESETS.get(model_id, {})
        self.model_id, self.name = model_id, name or model_id.split("/")[-1]
        self.prompt = prompt or pre.get("prompt", "Extract the text from the above document.")
        self.system_prompt = system_prompt or pre.get("system_prompt")
        self.device, self.dtype, self.quant = device, dtype, quant
        self.max_new_tokens = max_new_tokens or pre.get("max_new_tokens", 128)
        self.batch_size, self.weight, self.scripts = batch_size, weight, scripts
        self.processor_kwargs = processor_kwargs if processor_kwargs is not None else pre.get("processor_kwargs", {})
        self.generation_kwargs = generation_kwargs if generation_kwargs is not None else pre.get("generation_kwargs", {})
        self.model = None

    def load(self):
        import torch
        import transformers

        self.torch = torch
        kw = {"device_map": {"": self.device}, "dtype": getattr(torch, self.dtype)}
        if self.quant == "nf4":
            kw["quantization_config"] = transformers.BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=getattr(torch, self.dtype))
        cls = getattr(transformers, "AutoModelForImageTextToText", None) or transformers.AutoModelForVision2Seq
        self.processor = transformers.AutoProcessor.from_pretrained(self.model_id, **self.processor_kwargs)
        self.model = cls.from_pretrained(self.model_id, **kw).eval()
        self.tok = getattr(self.processor, "tokenizer", self.processor)
        return self

    def _chat(self, answer: str | None = None) -> str:
        msgs = []
        if self.system_prompt:
            msgs.append({"role": "system", "content": [{"type": "text", "text": self.system_prompt}]})
        msgs.append({"role": "user", "content": [{"type": "image"}, {"type": "text", "text": self.prompt}]})
        text = self.processor.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        return text if answer is None else text + answer

    def read(self, crops) -> list[Reading]:
        if self.model is None:
            self.load()
        out: list[Reading] = []
        for k in range(0, len(crops), self.batch_size):
            out += self._read_batch(list(crops[k:k + self.batch_size]))
        return out

    def _read_batch(self, ims) -> list[Reading]:
        torch, tok = self.torch, self.tok
        old, tok.padding_side = tok.padding_side, "left"
        try:
            enc = self.processor(text=[self._chat()] * len(ims), images=ims, return_tensors="pt", padding=True)
        finally:
            tok.padding_side = old
        enc = enc.to(self.model.device)
        try:
            with torch.inference_mode():
                g = self.model.generate(**enc, max_new_tokens=self.max_new_tokens, do_sample=False, temperature=None,
                                        top_p=None, top_k=None, output_scores=True, output_logits=True,
                                        return_dict_in_generate=True, **self.generation_kwargs)
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(ims) == 1:
                raise
            h = len(ims) // 2
            return self._read_batch(ims[:h]) + self._read_batch(ims[h:])
        new = g.sequences[:, enc["input_ids"].shape[1]:]
        # log-prob của token ĐÃ CHỌN (lấy từ sequences, không argmax lại: fp16 hay hoà điểm), trên logits THÔ (trước
        # repetition_penalty) để độ tin cậy không bị phạt lặp làm méo
        raw = getattr(g, "logits", None) or g.scores
        chosen = torch.stack([torch.log_softmax(s.float(), -1).gather(1, new[:, t:t + 1])[:, 0]  # từng bước: khỏi giữ B×T×V
                              for t, s in enumerate(raw)], 1).cpu().tolist()
        special = set(tok.all_special_ids)
        res = []
        for b in range(len(ims)):
            ids = [i for i in new[b].tolist()]
            keep = [t for t, i in enumerate(ids) if i not in special]
            res.append(self._to_reading([ids[t] for t in keep], [chosen[b][t] for t in keep]))
        return res

    def _to_reading(self, ids: list[int], lps: list[float]) -> Reading:
        return reading_from_tokens(self.tok, ids, lps)

    def score(self, image, texts: list[str]) -> list[float]:
        """log-prob TRUNG BÌNH mỗi token của từng chuỗi khi model nhìn ảnh (teacher forcing). Cao hơn = ảnh ủng hộ hơn."""
        if self.model is None:
            self.load()
        torch = self.torch
        base = self.processor(text=[self._chat()], images=[image], return_tensors="pt")
        n0 = base["input_ids"].shape[1]
        out = []
        for t in texts:
            enc = self.processor(text=[self._chat(t)], images=[image], return_tensors="pt").to(self.model.device)
            with torch.inference_mode():
                logits = self.model(**enc).logits[0, n0 - 1:-1].float()
            tgt = enc["input_ids"][0, n0:]
            lp = torch.log_softmax(logits, -1).gather(1, tgt[:, None])[:, 0]
            out.append(float(lp.mean()) if lp.numel() else float("-inf"))
        return out

    def close(self):
        if self.model is not None:
            del self.model
            self.model = None
            self.torch.cuda.empty_cache()


def reading_from_tokens(tok, ids: list[int], lps: list[float]) -> Reading:
    """Token đã sinh + log-prob từng token → Reading (xác suất từ = exp(log-prob token THẤP NHẤT phủ từ đó)), cắt vòng lặp."""
    ends = []
    for t in range(len(ids)):  # vị trí ký tự cuối của mỗi token trong chuỗi đã giải mã (dòng ngắn: O(n²) vẫn nhanh)
        ends.append(len(tok.decode(ids[:t + 1], skip_special_tokens=True)))
    text = tok.decode(ids, skip_special_tokens=True)
    starts = [0] + ends[:-1]
    words, probs = [], []
    for w, a, b in words_with_spans(text):
        tl = [lps[t] for t in range(len(ids)) if starts[t] < b and ends[t] > a]
        words.append(w)
        probs.append(math.exp(min(tl)) if tl else None)
    trimmed, looped = trim_loops(words)
    return Reading(" ".join(trimmed), probs[:len(trimmed)], None,
                   {"loop": looped, "mean_lp": sum(lps) / len(lps) if lps else None})


class HATFormerEngine:
    """HATFormer (TrOCR: ViT-384 + decoder, 0,33B) — kiến trúc KHÁC họ Qwen-VL nên lỗi ít tương quan: phiếu bầu có giá
    trị cho bỏ phiếu. Tiền xử lý đúng theo model card (Archatext/hatformer-arams28k): cao 64 px, LẬT NGANG (chữ
    phải→trái), xếp các đoạn 384 px thành hàng trên canvas 384×384 đen, chuẩn hoá (x−0,5)/0,5; beam 3. Dòng dài hơn
    6 × 384 px (ở cao 64) bị cắt — model card: lật ngang là bắt buộc. Giấy phép CC-BY-NC-SA-4.0."""

    def __init__(self, model_id: str = "Archatext/hatformer-arams28k", name: str = "hatformer", device: str = "cpu",
                 num_beams: int = 3, max_new_tokens: int = 64, batch_size: int = 8, weight: float = 0.6,
                 scripts=frozenset({"ar", "digit", "mixed"})):
        self.model_id, self.name, self.device = model_id, name, device
        self.num_beams, self.max_new_tokens, self.batch_size = num_beams, max_new_tokens, batch_size
        self.weight, self.scripts = weight, scripts
        self.model = None

    def load(self):
        import torch
        from huggingface_hub import snapshot_download
        from transformers import PreTrainedTokenizerFast, VisionEncoderDecoderModel

        self.torch = torch
        ckpt = snapshot_download(self.model_id)
        self.model = VisionEncoderDecoderModel.from_pretrained(ckpt).to(self.device).eval()
        tok = PreTrainedTokenizerFast.from_pretrained(ckpt)
        tok.add_special_tokens({"pad_token": "<pad>", "eos_token": "</s>", "cls_token": "<s>", "bos_token": "<s>"})
        self.model.config.decoder_start_token_id = tok.bos_token_id
        self.model.config.pad_token_id = tok.pad_token_id
        self.tok = tok
        return self

    @staticmethod
    def to_canvas(img, height: int = 64, size: int = 384):
        from PIL import Image

        img = img.convert("RGB")
        w, h = img.size
        line = img.resize((max(1, int(height * w / h)), height)).transpose(Image.FLIP_LEFT_RIGHT)
        canvas = Image.new("RGB", (size, size), (0, 0, 0))
        for i in range(min(size // height, (line.width + size - 1) // size)):
            canvas.paste(line.crop((i * size, 0, min((i + 1) * size, line.width), height)), (0, i * height))
        return canvas

    def read(self, crops) -> list[Reading]:
        import numpy as np

        if self.model is None:
            self.load()
        torch, out = self.torch, []
        for k in range(0, len(crops), self.batch_size):
            arr = np.stack([np.asarray(self.to_canvas(im), dtype=np.float32) / 255.0 for im in crops[k:k + self.batch_size]])
            pv = torch.from_numpy(np.transpose((arr - 0.5) / 0.5, (0, 3, 1, 2))).to(self.device)
            with torch.inference_mode():
                g = self.model.generate(pixel_values=pv, num_beams=self.num_beams, length_penalty=0,
                                        max_new_tokens=self.max_new_tokens, output_scores=True,
                                        return_dict_in_generate=True)
                trans = self.model.compute_transition_scores(g.sequences, g.scores, getattr(g, "beam_indices", None),
                                                             normalize_logits=False)
            special = set(self.tok.all_special_ids)
            for b in range(pv.shape[0]):
                ids = g.sequences[b, 1:].tolist()           # bỏ token khởi đầu của decoder
                lps = trans[b].float().cpu().tolist()
                keep = [t for t, i in enumerate(ids[:len(lps)]) if i not in special]
                out.append(reading_from_tokens(self.tok, [ids[t] for t in keep], [lps[t] for t in keep]))
        return out

    def close(self):
        if self.model is not None:
            del self.model
            self.model = None
            if self.torch.cuda.is_available():
                self.torch.cuda.empty_cache()


class DotsCacheEngine:
    """Cả trang từ cache dots.mocr (file JSON của postcorrect.ocr_cache). Xác suất từ = exp(log-prob token thấp nhất)."""

    def __init__(self, cache_dir: str, name: str = "dots_page", weight: float = 0.8, scripts=ALL_SCRIPTS):
        self.dir, self.name, self.weight, self.scripts = Path(cache_dir), name, weight, scripts

    def read_page(self, page_id: str) -> Reading | None:
        from postcorrect.dots_conf import page_word_conf
        from postcorrect.pipeline import page_text_from_cells

        f = self.dir / f"{page_id}.json"
        if not f.exists():
            return None
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("error"):
            return None
        page = page_text_from_cells(page_id, rec.get("cells"))
        conf = page_word_conf(rec)
        words = page.text.split()
        probs = [math.exp(c.lp_min) if c is not None else None for c in conf] if len(conf) == len(words) else None
        return Reading(" ".join(words), probs, None, {"flags": rec.get("extra", {})})


class StaticEngine:
    """Đọc chữ đã có: {line_id: "chữ"} hoặc {line_id: {"text": ..., "probs": [...]}} (line engine)."""

    def __init__(self, name: str, readings: dict, weight: float = 1.0, scripts=ALL_SCRIPTS):
        self.name, self.readings, self.weight, self.scripts = name, readings, weight, scripts

    def read_ids(self, ids: list[str]) -> list[Reading]:
        out = []
        for i in ids:
            r = self.readings.get(i, "")
            out.append(Reading(r["text"], r.get("probs")) if isinstance(r, dict) else Reading(r))
        return out


_SPACE = re.compile(r"\s+")
_BIDI = re.compile("[\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff\u061c]")  # ký tự điều khiển hướng chữ (Tesseract hay chèn)


def clean_text(s: str) -> str:
    return _SPACE.sub(" ", _BIDI.sub("", s or "")).strip()
