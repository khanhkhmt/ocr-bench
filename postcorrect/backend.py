"""Backend LLM CỤC BỘ (không gọi API ngoài). Hai việc: sinh chữ theo batch, và chấm NLL từng từ (chỉ một lượt forward).

HFBackend chạy bằng transformers + bitsandbytes (nf4) hoặc fp16 trên MỘT card (device_map={"": device}); T4 không có bf16
nên tính toán ở fp16. Đã đo trên T4: Qwen3-8B nf4 = 6,0 GiB, 11 tok/s (batch 1) → 43 tok/s (batch 8). Muốn dùng cả hai
card thì chạy hai tiến trình, mỗi tiến trình một card (--shard i/n), vì T4 không có NVLink.

DummyBackend: "LLM" giả xác định để test logic pipeline trên CPU.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from .text import words_with_spans


@dataclass
class GenStats:
    seconds: float = 0.0
    prompt_tokens: int = 0
    new_tokens: int = 0
    batches: int = 0
    oom_retries: int = 0


@dataclass
class WordNLL:
    total: float   # tổng NLL các token thuộc từ (nat)
    max: float     # NLL lớn nhất của một token trong từ
    n_tok: int


class HFBackend:
    def __init__(self, model_id: str, device: int = 0, quant: str = "nf4", max_batch: int = 8,
                 max_batch_tokens: int = 6000, nll_cache: str | None = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        self.torch, self.model_id, self.device, self.quant = torch, model_id, device, quant
        self.max_batch, self.max_batch_tokens = max_batch, max_batch_tokens
        self.nll_cache = Path(nll_cache) / re.sub(r"[^A-Za-z0-9_.-]+", "_", model_id) if nll_cache else None
        if self.nll_cache:
            self.nll_cache.mkdir(parents=True, exist_ok=True)
        self.tok = AutoTokenizer.from_pretrained(model_id)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        kw = {"torch_dtype": torch.float16, "device_map": {"": device}}
        if quant == "nf4":
            kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                            bnb_4bit_compute_dtype=torch.float16)
        elif quant != "fp16":
            raise ValueError("quant phải là nf4 hoặc fp16")
        t = time.perf_counter()
        self.model = AutoModelForCausalLM.from_pretrained(model_id, **kw).eval()
        self.load_seconds = time.perf_counter() - t
        self.stats = GenStats()

    # --- prompt ---
    def build_prompt(self, msgs: list[dict]) -> str:
        try:
            return self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        except Exception:  # model không nhận vai system → gộp vào lượt user đầu
            sys_, rest = msgs[0]["content"], msgs[1:]
            rest = [dict(rest[0], content=sys_ + "\n\n" + rest[0]["content"])] + rest[1:]
            return self.tok.apply_chat_template(rest, tokenize=False, add_generation_prompt=True)

    def n_tokens(self, text: str) -> int:
        return len(self.tok(text, add_special_tokens=False)["input_ids"])

    # --- sinh chữ ---
    def generate(self, prompts: list[str], max_new: list[int]) -> list[str]:
        """Sinh tham lam (không repetition_penalty — tác vụ chép lại phần lớn đầu vào). Gom theo độ dài để ít đệm."""
        order = sorted(range(len(prompts)), key=lambda i: self.n_tokens(prompts[i]))
        out: list[str | None] = [None] * len(prompts)
        i = 0
        while i < len(order):
            batch = [order[i]]
            while (i + len(batch) < len(order) and len(batch) < self.max_batch
                   and self.n_tokens(prompts[order[i + len(batch)]]) * (len(batch) + 1) <= self.max_batch_tokens):
                batch.append(order[i + len(batch)])
            for idx, text in zip(batch, self._run(batch, prompts, max_new)):
                out[idx] = text
            i += len(batch)
        return out  # type: ignore[return-value]

    def _run(self, batch: list[int], prompts: list[str], max_new: list[int]) -> list[str]:
        torch, tok = self.torch, self.tok
        try:
            tok.padding_side = "left"
            enc = tok([prompts[i] for i in batch], return_tensors="pt", padding=True, add_special_tokens=False)
            enc = enc.to(self.model.device)
            torch.cuda.synchronize(self.device)
            t = time.perf_counter()
            with torch.inference_mode():
                gen = self.model.generate(**enc, max_new_tokens=max(max_new[i] for i in batch), do_sample=False,
                                          temperature=None, top_p=None, top_k=None, pad_token_id=tok.pad_token_id)
            torch.cuda.synchronize(self.device)
            new = gen[:, enc["input_ids"].shape[1]:]
            self.stats.seconds += time.perf_counter() - t
            self.stats.batches += 1
            self.stats.prompt_tokens += int(enc["attention_mask"].sum())
            self.stats.new_tokens += int((new != tok.pad_token_id).sum())
            return tok.batch_decode(new, skip_special_tokens=True)
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(batch) == 1:
                raise
            self.stats.oom_retries += 1
            half = len(batch) // 2
            return self._run(batch[:half], prompts, max_new) + self._run(batch[half:], prompts, max_new)

    # --- chấm NLL từng từ ---
    def nll_words(self, text: str) -> list[WordNLL]:
        """NLL của mỗi từ (theo words_with_spans) khi LM đọc cả `text`. Một lượt forward, không sinh gì. Có thể cache ra đĩa
        (khoá = băm của văn bản; mỗi model một thư mục) vì thí nghiệm lặp lại trên cùng văn bản OCR."""
        torch, tok = self.torch, self.tok
        spans = [(a, b) for _, a, b in words_with_spans(text)]
        if not spans:
            return []
        cache_file = self.nll_cache / (hashlib.sha1(text.encode("utf-8")).hexdigest() + ".json") if self.nll_cache else None
        if cache_file is not None and cache_file.exists():
            return [WordNLL(*x) for x in json.loads(cache_file.read_text(encoding="utf-8"))]
        enc = tok(text, return_offsets_mapping=True, return_tensors="pt")
        ids = enc["input_ids"].to(self.model.device)
        with torch.inference_mode():
            logp = torch.log_softmax(self.model(ids).logits[0, :-1].float(), -1)
        nll = (-logp.gather(1, ids[0, 1:, None])[:, 0]).cpu().tolist()
        cw = [-1] * len(text)
        for wi, (a, b) in enumerate(spans):
            for k in range(a, b):
                cw[k] = wi
        tot, mx, cnt = [0.0] * len(spans), [0.0] * len(spans), [0] * len(spans)
        for t, (s, e) in enumerate(enc["offset_mapping"][0].tolist()):
            if t == 0:  # token đầu không có ngữ cảnh → không có NLL
                continue
            seg = text[s:e]
            pos = s + (len(seg) - len(seg.lstrip()))
            if pos >= e or cw[pos] < 0:
                continue
            wi = cw[pos]
            tot[wi] += nll[t - 1]
            mx[wi] = max(mx[wi], nll[t - 1])
            cnt[wi] += 1
        out = [WordNLL(a, b, c) for a, b, c in zip(tot, mx, cnt)]
        if cache_file is not None:
            cache_file.write_text(json.dumps([[w.total, w.max, w.n_tok] for w in out]), encoding="utf-8")
        return out

    def close(self):
        del self.model
        self.torch.cuda.empty_cache()


@dataclass
class DummyBackend:
    """LLM giả: thay từ theo bảng `fixes` (chiến lược A/C: viết lại; B: trả JSON). NLL: `suspicious` cao, còn lại thấp."""
    fixes: dict = field(default_factory=dict)
    suspicious: set = field(default_factory=set)
    model_id: str = "dummy"
    stats: GenStats = field(default_factory=GenStats)
    calls: list = field(default_factory=list)

    def build_prompt(self, msgs):
        return msgs[-1]["content"] if msgs[0]["role"] != "system" else "\x00".join(m["content"] for m in msgs)

    def n_tokens(self, text):
        return max(1, len(text) // 3)

    def generate(self, prompts, max_new):
        import json

        outs = []
        for p in prompts:
            self.calls.append(p)
            m = re.search(r"<input>(.*?)</input>\s*$", p, re.S)
            text = m.group(1) if m else p
            if "JSON" in p.split("\x00")[0] or "List ONLY" in p:
                words = [w for w in text.split() if w in self.fixes]
                outs.append(json.dumps([{"word": w, "fix": self.fixes[w]} for w in words], ensure_ascii=False))
            else:
                text = text.replace("[[", "").replace("]]", "")
                outs.append("<output>" + " ".join(self.fixes.get(w, w) for w in text.split(" ")) + "</output>")
        return outs

    def nll_words(self, text):
        return [WordNLL(8.0, 8.0, 2) if w in self.suspicious else WordNLL(1.0, 0.5, 1)
                for w, _, _ in words_with_spans(text)]

    def close(self):
        pass
