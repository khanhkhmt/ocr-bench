"""Các model đọc chữ viết tay theo dòng — gọi ĐÚNG như code mẫu của tác giả (BaseerNakba: xem lớp bên dưới).

KetabaOCR  — https://huggingface.co/HassanB4/Ketaba-OCR-LoRA
    LoRA (QLoRA 4-bit + DoRA + RSLoRA) trên sherif1313/Arabic-English-handwritten-OCR-v3 (Qwen2.5-VL-3B), huấn luyện
    trên dòng chữ tay bản thảo 1951–1965 (Ruq'ah, Naskh — bộ hồi ký Omar Al-Saleh, NakbaNLP 2026).
    Tác giả: CER 8,19% (theo dòng), WER 25,88%. Prompt: "اقرأ النص الموجود في الصورة:". Bắt buộc sửa ràng buộc
    trọng số lm_head = embed_tokens. Có thể TẮT LoRA để so với sherif gốc.
ArTrOCR    — https://huggingface.co/BushraAlmod03/ArTrOCR-HTR
    TrOCR (microsoft/trocr-base-handwritten) huấn luyện tiếp: chữ tổng hợp → 11.000 dòng KHATT. Ảnh dòng thu về cao 102,
    dán lên nền trắng 512×102; bật nội suy vị trí. Tác giả: CER 12,61% trên KHATT. Không học dấu nguyên âm.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

_LOCK = threading.Lock()


def _bf16_ok() -> bool:
    return torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8


def resolve_dtype(name: str = "auto") -> torch.dtype:
    """auto = bf16 nếu GPU hỗ trợ (Ampere+), không thì fp16 (T4). fp32 = chính xác số học nhất (chậm, tốn gấp đôi VRAM)."""
    if name == "auto":
        return torch.bfloat16 if _bf16_ok() else torch.float16
    return {"fp16": torch.float16, "bf16": torch.bfloat16, "fp32": torch.float32}[name]


class KetabaOCR:
    BASE = "sherif1313/Arabic-English-handwritten-OCR-v3"
    LORA = "HassanB4/Ketaba-OCR-LoRA"
    PROMPT = "اقرأ النص الموجود في الصورة:"

    def __init__(self, quant4: bool = True, device: str = "cuda:0", max_new_tokens: int = 512, dtype: str = "auto"):
        """quant4=True: như tác giả (nền 4-bit NF4 + DoRA) — trên T4 ~25 s/dòng (DoRA trên lớp 4-bit giải nén + tính lại
        chuẩn mỗi bước). quant4=False: nền fp16 + cùng adapter DoRA (KHÔNG gộp: thử gộp trên model thu nhỏ cho logits
        lệch tới ~0,08 → bỏ) — nhanh hơn, phải đo độ chính xác bằng htr_test.chan_doan trước khi dùng."""
        self.quant4, self.device, self.max_new_tokens, self.dtype = quant4, device, max_new_tokens, dtype
        self.model = self.processor = None

    @staticmethod
    def _peft_khong_torchao() -> None:
        """Colab có sẵn torchao 0.10 (cũ); peft gắn adapter lên lớp KHÔNG nén thì gọi is_torchao_available() và NÉM
        ImportError ("only versions above 0.16.0") thay vì bỏ qua. Ketaba không dùng torchao → báo peft là không có."""
        try:
            import peft.import_utils as iu
            iu.is_torchao_available = lambda: False
            import peft.tuners.lora.torchao as lt
            lt.is_torchao_available = lambda: False
        except Exception:  # noqa: BLE001 — bản peft khác bố cục: không cần vá
            pass

    def load(self):
        from peft import PeftModel

        self._peft_khong_torchao()
        from transformers import AutoProcessor, BitsAndBytesConfig, Qwen2_5_VLForConditionalGeneration

        t = time.time()
        kw = {"device_map": {"": self.device}, "trust_remote_code": True}
        if self.quant4:  # như tác giả: 4-bit NF4, double quant (T4 không có bf16 → tính toán fp16)
            kw["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=resolve_dtype(self.dtype))
            if self.dtype == "fp32":  # phần không lượng tử hoá (vision, norm...) cũng fp32
                kw["torch_dtype"] = torch.float32
        else:
            kw["torch_dtype"] = resolve_dtype(self.dtype)
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(self.BASE, **kw)
        model = PeftModel.from_pretrained(model, self.LORA)
        model.lm_head.weight = model.model.language_model.embed_tokens.weight  # sửa ràng buộc trọng số (tác giả)
        model.eval()
        self.model = model
        self.processor = AutoProcessor.from_pretrained(self.BASE, trust_remote_code=True)
        self.processor.tokenizer.padding_side = "left"
        self.load_s = round(time.time() - t, 1)
        return self

    def read(self, lines: list[Image.Image], use_lora: bool = True, batch: int = 1) -> list[str]:
        # batch = 1 MẶC ĐỊNH: ghép nhiều ảnh dòng vào một lô (đệm trái) làm Qwen2.5-VL trên transformers 4.56.1 dừng sớm /
        # lặp dòng — chẩn đoán 32 dòng Omar: Baseer lô 16 → 72,1% đúng ký tự, lô 1 → 91,2% (= công bố); fp16 = fp32.
        from qwen_vl_utils import process_vision_info

        if self.model is None:
            self.load()
        out = []
        for i in range(0, len(lines), batch):
            chunk = lines[i:i + batch]
            msgs = [[{"role": "user", "content": [{"type": "image", "image": im.convert("RGB")},
                                                  {"type": "text", "text": self.PROMPT}]}] for im in chunk]
            texts = [self.processor.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]
            imgs = [process_vision_info(m)[0][0] for m in msgs]
            inputs = self.processor(text=texts, images=imgs, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            with _LOCK, torch.no_grad():
                if use_lora:
                    ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, do_sample=False)
                else:
                    with self.model.disable_adapter():
                        ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, do_sample=False)
            n_in = inputs["input_ids"].shape[1]
            out += [self.processor.decode(r[n_in:], skip_special_tokens=True).strip() for r in ids]
        return out


class ArTrOCR:
    REPO = "BushraAlmod03/ArTrOCR-HTR"

    def __init__(self, device: str = "cuda:0", max_length: int = 140):
        self.device, self.max_length = device, max_length
        self.model = self.processor = None

    def load(self):
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel

        t = time.time()
        self.processor = self._processor(TrOCRProcessor)
        model = VisionEncoderDecoderModel.from_pretrained(self.REPO).to(self.device)
        # như tác giả: bật nội suy vị trí (ảnh 512×102 khác kích thước lúc tiền huấn luyện)
        model.config.encoder.interpolate_pos_encoding = True
        if not hasattr(model.encoder, "_original_forward"):
            model.encoder._original_forward = model.encoder.forward

            def patched_forward(pixel_values, *args, **kwargs):
                kwargs["interpolate_pos_encoding"] = True
                return model.encoder._original_forward(pixel_values, *args, **kwargs)

            model.encoder.forward = patched_forward
        model.eval()
        self.model = model
        self.load_s = round(time.time() - t, 1)
        return self

    def _processor(self, TrOCRProcessor):
        """Repo lưu bằng transformers 5 (tokenizer_class "TokenizersBackend" — bản 4.56.1 của venv dots không có).
        Bản 5 đọc được thẳng; bản 4 thì dựng lại từ đúng các file đó: tokenizer.json (BPE byte-level kiểu RoBERTa
        + chữ Ả Rập thêm vào) và ảnh theo processor_config.json (không resize, chuẩn hoá 0,5 / 0,5)."""
        try:
            return TrOCRProcessor.from_pretrained(self.REPO)
        except ValueError as e:
            if "TokenizersBackend" not in str(e):
                raise
        import json

        from huggingface_hub import hf_hub_download
        from transformers import PreTrainedTokenizerFast, ViTImageProcessor

        cfg = json.loads(Path(hf_hub_download(self.REPO, "tokenizer_config.json")).read_text())
        tok = PreTrainedTokenizerFast(
            tokenizer_file=hf_hub_download(self.REPO, "tokenizer.json"),
            **{k: cfg[k] for k in ("bos_token", "eos_token", "unk_token", "sep_token", "pad_token", "cls_token",
                                   "mask_token", "model_max_length", "padding_side") if k in cfg})
        ip = json.loads(Path(hf_hub_download(self.REPO, "processor_config.json")).read_text())["image_processor"]
        img = ViTImageProcessor(**{k: ip[k] for k in ("do_resize", "size", "resample", "do_rescale", "rescale_factor",
                                                      "do_normalize", "image_mean", "image_std") if k in ip})
        return TrOCRProcessor(image_processor=img, tokenizer=tok)

    @staticmethod
    def prep(img: Image.Image) -> np.ndarray:
        """Đúng code mẫu: thu về cao 102 (giữ tỉ lệ), dán sát TRÁI lên nền trắng 512×102; dài hơn thì ép rộng 512."""
        img = img.convert("RGB")
        th, tw = 102, 512
        w, h = img.size
        nw = int(w * th / h)
        img = img.resize((nw, th), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (tw, th), (255, 255, 255))
        if nw <= tw:
            canvas.paste(img, (0, 0))
        else:
            canvas.paste(img.resize((tw, th), Image.Resampling.LANCZOS), (0, 0))
        return np.array(canvas)

    def read(self, lines: list[Image.Image], batch: int = 16) -> list[str]:
        if self.model is None:
            self.load()
        out = []
        for i in range(0, len(lines), batch):
            arr = [self.prep(im) for im in lines[i:i + batch]]
            pv = self.processor(arr, return_tensors="pt").pixel_values.to(self.device)
            with _LOCK, torch.no_grad():
                ids = self.model.generate(pv, max_length=self.max_length)
            out += [t.strip() for t in self.processor.batch_decode(ids, skip_special_tokens=True)]
        return out


def clean_repeated_substrings(text: str) -> str:
    """Chép nguyên từ Baseer_Nakba.py của tác giả: cắt đuôi lặp (≥ 10 lần) khi model rơi vào vòng lặp."""
    n = len(text)
    if n < 200:
        return text
    for length in range(2, n // 10 + 1):
        candidate = text[-length:]
        count = 0
        i = n - length
        while i >= 0 and text[i:i + length] == candidate:
            count += 1
            i -= length
        if count >= 10:
            return text[:n - length * (count - 1)]
    return text


class BaseerNakba:
    """Misraj/Baseer__Nakba — hạng 1 NAKBA NLP 2026 (CER 7,9%, WER 24,4% trên dòng chữ tay Omar Al-Saleh 1951–65).

    Qwen2.5-VL-3B (Baseer) huấn luyện tiếp: Muharaf (chỉ decoder) → Nakba (cả encoder + decoder) → trộn SLERP 2 checkpoint.
    Giấy phép CC BY-NC-SA 4.0 (PHI THƯƠNG MẠI). Tham số y như Baseer_Nakba.py (github.com/misraj-ai/Nakba-pipeline):
    prompt "Extract the text from the above document." kèm system mặc định, min_pixels 28·28, max_pixels 1280·28·28,
    giải mã tham lam, repetition_penalty 1.1, tối đa 128 token, cắt đuôi lặp. Tác giả chạy vLLM; ở đây dùng
    transformers (không cài vLLM để khỏi đổi torch) — cùng trọng số, cùng tham số.
    """

    REPO = "Misraj/Baseer__Nakba"
    PROMPT = "Extract the text from the above document."
    TEMPLATE = ("<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
                "<|im_start|>user\n<|vision_start|><|image_pad|><|vision_end|>{p}<|im_end|>\n"
                "<|im_start|>assistant\n")

    def __init__(self, device: str = "cuda:0", quant4: bool = False, max_new_tokens: int = 128, dtype: str = "auto"):
        self.device, self.quant4, self.max_new_tokens, self.dtype = device, quant4, max_new_tokens, dtype
        self.model = self.processor = None

    def load(self):
        from transformers import AutoProcessor, BitsAndBytesConfig, Qwen2_5_VLForConditionalGeneration

        t = time.time()
        dtype = resolve_dtype(self.dtype)  # auto: T4 không có bf16 → fp16 (tác giả chạy bf16 trên H100)
        kw = {"device_map": {"": self.device}, "torch_dtype": dtype}
        if self.quant4:  # chỉ khi thiếu VRAM (không phải cách tác giả chạy)
            kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                           bnb_4bit_compute_dtype=dtype)
        from transformers import AutoConfig

        cfg = self._fix_config(AutoConfig.from_pretrained(self.REPO))
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(self.REPO, config=cfg, **kw).eval()
        self.processor = AutoProcessor.from_pretrained(self.REPO, min_pixels=28 * 28, max_pixels=1280 * 28 * 28)
        self.processor.tokenizer.padding_side = "left"
        self.load_s = round(time.time() - t, 1)
        return self

    TOKEN_KEYS = ("image_token_id", "video_token_id", "vision_start_token_id", "vision_end_token_id", "vision_token_id")

    @classmethod
    def _fix_config(cls, cfg):
        """Repo trộn bằng mergekit + lưu bằng transformers 4.57: các mã token ảnh CHỈ nằm trong text_config; bản 4.56.1
        (venv dots) đọc ở cấp ngoài → AttributeError 'vision_start_token_id'. Chép giá trị (không đổi) ra ngoài."""
        tc = getattr(cfg, "text_config", None)
        for k in cls.TOKEN_KEYS:
            v = getattr(tc, k, None) if tc is not None else None
            if v is not None and getattr(cfg, k, None) is None:
                setattr(cfg, k, v)
        return cfg

    def read(self, lines: list[Image.Image], batch: int = 1) -> list[str]:
        # batch = 1 MẶC ĐỊNH: ghép nhiều ảnh dòng vào một lô (đệm trái) làm Qwen2.5-VL trên transformers 4.56.1 dừng sớm /
        # lặp dòng — chẩn đoán 32 dòng Omar: Baseer lô 16 → 72,1% đúng ký tự, lô 1 → 91,2% (= công bố); fp16 = fp32.
        if self.model is None:
            self.load()
        out = []
        prompt = self.TEMPLATE.format(p=self.PROMPT)
        for i in range(0, len(lines), batch):
            chunk = [im.convert("RGB") for im in lines[i:i + batch]]
            inputs = self.processor(text=[prompt] * len(chunk), images=chunk, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            with _LOCK, torch.no_grad():
                ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, do_sample=False,
                                          repetition_penalty=1.1, eos_token_id=[151645, 151643],
                                          pad_token_id=151643)
            n_in = inputs["input_ids"].shape[1]
            out += [clean_repeated_substrings(self.processor.decode(r[n_in:], skip_special_tokens=True).strip())
                    for r in ids]
        return out


def free_cuda():
    import gc

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
