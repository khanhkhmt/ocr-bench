"""Thử LLM sửa lỗi OCR trên 4 trang mẫu của arabic-doc-ocr (chữ đánh máy + chữ viết tay).

    /kaggle/working/venvs/llm/bin/python -m htr_test.llm_sua \
        --ocr /kaggle/working/arabic-doc-ocr/results/two_gpus --adoc /kaggle/working/arabic-doc-ocr \
        --out /kaggle/working/llm_sua --push

ĐẦU VÀO: JSON kết quả của arabic-doc-ocr (`page_N*.json`, mỗi khối có văn bản chính, bản dots, ft3/ft4 từng dòng).
NHÃN (`examples/page_N/label.json`) CHỈ được đọc ở bước chấm, SAU khi sửa xong. Hàm sửa chỉ nhận chữ OCR, không bao
giờ thấy nhãn (`_sua_trang` không nhận đối số nhãn; nhãn nạp trong `_cham`).

Cách sửa — CỐ ĐỊNH TRƯỚC, không chỉnh theo kết quả 4 trang:
  chon      ở chỗ hai bản đọc khác nhau (đánh máy: dots ↔ ft3; viết tay: ft3 ↔ ft4; ≤ 3 từ mỗi bên, không có chữ số,
            không có chữ Latin / Hebrew) LLM tính xác suất của đoạn câu chứa bản A và đoạn câu chứa bản B → lấy bản có
            xác suất cao hơn. Không sinh chữ mới.
  sua       LLM viết lại văn bản chính đã sửa (bản đọc thứ hai đưa vào làm gợi ý). CHỈ nhận thay 1 từ ↔ 1 từ, đổi ≤ 2 ký
            tự và ≤ 40 % độ dài từ, từ gốc không có chữ số, từ mới toàn chữ cái Ả Rập (không dấu). Mọi thay đổi khác
            (thêm / bỏ / gộp / tách từ, đổi số, viết lại câu) bị bỏ, giữ nguyên chữ OCR.
  chon_sua  chon rồi sua.
  tran_chon KHÔNG phải cách sửa, không dùng LLM: ở mỗi chỗ khác nhau lấy bản khớp nhãn hơn → mức tối đa "chon" có thể
            đạt. Dùng nhãn, chỉ để tham khảo.

Kết quả trong --out: tom_tat.md + tom_tat.json (bảng điểm), chi_tiet.csv (mọi từ bị đổi: sửa đúng / làm hỏng /
không rõ), <model>.jsonl (văn bản sau sửa từng khối). Chạy lại = đi tiếp (bỏ model × cách × trang đã xong).
Model lỗi (không nạp được, hết VRAM, fp16 ra rác…) → ghi lý do, chạy tiếp model sau.
Dòng cuối của log: "✔ XONG TẤT CẢ" hoặc "✘ LỖI: …".
"""

from __future__ import annotations

import argparse
import csv
import difflib
import importlib.util
import json
import re
import shutil
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

# (tên ngắn, repo Hugging Face) — thứ tự chạy: model chắc chạy được trên T4 trước
MODELS = [
    ("qwen2.5-7b", "Qwen/Qwen2.5-7B-Instruct"),
    ("qwen3-8b", "Qwen/Qwen3-8B"),
    ("allam-7b", "humain-ai/ALLaM-7B-Instruct-preview"),
    ("qwen3.5-9b", "Qwen/Qwen3.5-9B"),
    ("gemma4-12b", "google/gemma-4-12B-it"),
]
METHODS = ("chon", "sua", "chon_sua")
TEXT_CATS = {"Text", "Title", "Section-header", "List-item", "Caption", "Footnote", "Page-header", "Page-footer"}

# --- quy tắc nhận thay đổi (cố định) ----------------------------------------------------------------------------------
MAX_SPAN_WORDS = 3          # chon: mỗi bên ≤ 3 từ
CTX_LEFT, CTX_RIGHT = 40, 12  # chon: số từ ngữ cảnh trái / phải
MAX_EDIT_CHARS = 2          # sua: đổi ≤ 2 ký tự …
MAX_EDIT_FRAC = 0.4         # … và ≤ 40 % độ dài từ gốc
CHUNK_WORDS = 60            # sua: mỗi lần gửi LLM ~60 từ (gom theo dòng)

SYSTEM = (
    "You are an expert proofreader of Arabic legal documents from the 1970s (sale contracts, powers of attorney, "
    "official letters from Palestine, Jordan and Egypt). The text you receive was produced by OCR and contains "
    "letter-level mistakes: letters with similar shapes are confused (for example ع/ح/غ/خ/ج, ة/ه, ب/ت/ث/ن/ي, ق/ف, "
    "د/ذ/ر/ز, س/ش/ص/ض) and some letters are dropped.\n"
    "Rules:\n"
    "1. Correct only words that are OCR mistakes. Change as few letters as possible.\n"
    "2. Never change numbers, digits or dates.\n"
    "3. Do not change personal names or place names unless the mistake is obvious.\n"
    "4. Do not add, remove, merge, split or reorder words. Keep the line breaks.\n"
    "5. Do not add diacritics (harakat).\n"
    "6. Output only the corrected text, with no explanation."
)

_AR_WORD = re.compile(r"[ء-ي]+")
_AR_WORD_HARAKAT = re.compile(r"[ء-يً-ْ]+")
_DIGIT = re.compile(r"[0-9٠-٩۰-۹]")
_FOREIGN = re.compile(r"[A-Za-z֐-׿]")
_EDGE = re.compile(r"^([^ء-ي]*)(.*?)([^ء-ي]*)$", re.S)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# --- đọc kết quả OCR + mã chấm của arabic-doc-ocr ---------------------------------------------------------------------

def _load_adoc(adoc: Path):
    """→ (evaluate module, compare_words key). Dùng ĐÚNG mã chấm của arabic-doc-ocr (scripts/evaluate.py)."""
    spec = importlib.util.spec_from_file_location("adoc_evaluate", adoc / "scripts" / "evaluate.py")
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    sys.path.insert(0, str(adoc))
    from arabic_doc_ocr.text import _key  # noqa: PLC0415  (cách so từ của bước tô vàng)
    return ev, _key


def _pages(ocr: Path, examples: Path, only: list[str] | None) -> list[tuple[str, Path]]:
    out = []
    for lab in sorted(examples.glob("*/label.json")):
        page = lab.parent.name
        if only and page not in only:
            continue
        cand = [c for c in sorted(ocr.glob(f"{page}*.json")) if not c.name.startswith("run_info")]
        if not cand:
            raise SystemExit(f"✘ LỖI: không có kết quả OCR của {page} trong {ocr}")
        out.append((page, cand[0]))
    if not out:
        raise SystemExit(f"✘ LỖI: không có trang nào (examples: {examples})")
    return out


def _units(js: dict) -> list[dict]:
    """Các khối cần sửa: khối chữ, không phải Hebrew. → [{key, main, check, reader}]."""
    units = []
    for pi, p in enumerate(js["pages"]):
        for bi, b in enumerate(p["blocks"]):
            if b.get("category") not in TEXT_CATS or b.get("reader") not in ("dots", "ft3"):
                continue
            main = b.get("text") or ""
            if not main.strip():
                continue
            other = "ft3" if b["reader"] == "dots" else "ft4"
            check = "\n".join(L[other] for L in b.get("lines", []))
            units.append({"key": f"{pi}:{bi}", "main": main, "check": check, "reader": b["reader"]})
    return units


def _with_texts(js: dict, texts: dict[str, str]) -> dict:
    js = json.loads(json.dumps(js))
    for k, t in texts.items():
        pi, bi = map(int, k.split(":"))
        js["pages"][pi]["blocks"][bi]["text"] = t
    return js


# --- ghép từ ---------------------------------------------------------------------------------------------------------

def _spans(main: str, check: str, key) -> tuple[list[str], list[tuple[int, int, list[str]]]]:
    """Chỗ khác nhau main ↔ check (thay thế ≤ 3 từ mỗi bên, không số, không chữ ngoại) → (từ main, [(i1, i2, từ check)])."""
    a, b = main.split(), check.split()
    sm = difflib.SequenceMatcher(None, [key(w) for w in a], [key(w) for w in b], autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "replace" or not (1 <= i2 - i1 <= MAX_SPAN_WORDS and 1 <= j2 - j1 <= MAX_SPAN_WORDS):
            continue
        both = " ".join(a[i1:i2] + b[j1:j2])
        if _DIGIT.search(both) or _FOREIGN.search(both):
            continue
        out.append((i1, i2, b[j1:j2]))
    return a, out


def _rebuild(text: str, repl: dict[int, str]) -> str:
    """Thay từ thứ i (theo split()) bằng repl[i], giữ nguyên khoảng trắng / xuống dòng của bản gốc."""
    parts, n = re.split(r"(\s+)", text), 0
    for k, p in enumerate(parts):
        if p and not p.isspace():
            if n in repl:
                parts[k] = repl[n]
            n += 1
    return "".join(parts)


def _accept(old: str, new: str) -> str | None:
    """Luật nhận một thay đổi 1 từ ↔ 1 từ của "sua" → từ mới (giữ dấu câu của từ gốc) hoặc None."""
    from rapidfuzz.distance import Levenshtein  # noqa: PLC0415

    if _DIGIT.search(old) or _DIGIT.search(new):
        return None
    po, co, so = _EDGE.match(old).groups()
    _, cn, _ = _EDGE.match(new).groups()
    if len(co) < 2 or not _AR_WORD_HARAKAT.fullmatch(co) or not _AR_WORD.fullmatch(cn or "-"):
        return None
    d = Levenshtein.distance(co, cn)
    if d == 0 or d > MAX_EDIT_CHARS or d > MAX_EDIT_FRAC * len(co):
        return None
    return po + cn + so


def _chunks(words: list[str], text: str) -> list[tuple[int, int]]:
    """Các đoạn [s, e) theo chỉ số từ, gom theo dòng tới ≥ CHUNK_WORDS từ."""
    out, s, n = [], 0, 0
    for line in text.split("\n"):
        n += len(line.split())
        if n - s >= CHUNK_WORDS:
            out.append((s, n))
            s = n
    if s < len(words):
        out.append((s, len(words)))
    return out


def _map_check(a: list[str], b: list[str], key) -> list[int]:
    """Chỉ số từ main → vị trí tương ứng trong check (để cắt gợi ý cho từng đoạn)."""
    m = [0] * (len(a) + 1)
    sm = difflib.SequenceMatcher(None, [key(w) for w in a], [key(w) for w in b], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        for k in range(i1, i2):
            m[k] = j1 + (k - i1 if tag == "equal" else min(k - i1, j2 - j1))
    m[len(a)] = len(b)
    return m


# --- LLM ---------------------------------------------------------------------------------------------------------------

class LLM:
    def __init__(self, repo: str, cache: Path, cpu: bool = False):
        import torch  # noqa: PLC0415
        import transformers  # noqa: PLC0415
        from huggingface_hub import HfApi, snapshot_download  # noqa: PLC0415
        from transformers import AutoConfig, AutoTokenizer  # noqa: PLC0415
        from transformers.models.auto.configuration_auto import CONFIG_MAPPING_NAMES  # noqa: PLC0415

        self.torch, self.repo = torch, repo
        self.revision = HfApi().model_info(repo).sha
        cfg_path = Path(snapshot_download(repo, revision=self.revision, cache_dir=cache, allow_patterns=["config.json"]))
        mtype = json.loads((cfg_path / "config.json").read_text())["model_type"]
        if mtype not in CONFIG_MAPPING_NAMES:
            raise RuntimeError(f"BỎ QUA: transformers {transformers.__version__} không có model_type '{mtype}' "
                               "(cần bản mới hơn — torch hệ thống quá cũ?)")
        path = snapshot_download(repo, revision=self.revision, cache_dir=cache,
                                 allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja", "*.tiktoken"])
        self.path = path
        cfg = AutoConfig.from_pretrained(path)
        if cpu or not torch.cuda.is_available():
            dtype, kw = torch.float32, {"device_map": "cpu"}
        else:
            dtype = torch.bfloat16 if torch.cuda.get_device_capability(0)[0] >= 8 else torch.float16
            mm = {i: f"{int(torch.cuda.get_device_properties(i).total_memory / 2**30 - 1.5)}GiB"
                  for i in range(torch.cuda.device_count())}
            kw = {"device_map": "auto", "max_memory": mm}
        self.dtype = str(dtype).replace("torch.", "")
        tv = tuple(int(x) for x in re.findall(r"\d+", transformers.__version__)[:2])
        kw["dtype" if tv >= (4, 56) else "torch_dtype"] = dtype
        if getattr(cfg, "vision_config", None) is not None:
            from transformers import AutoModelForImageTextToText as Cls  # noqa: PLC0415
        else:
            from transformers import AutoModelForCausalLM as Cls  # noqa: PLC0415
        self.model, info = Cls.from_pretrained(path, output_loading_info=True, **kw)
        missing = [k for k in info.get("missing_keys", []) if "lm_head" not in k]
        if missing:
            raise RuntimeError(f"trọng số thiếu khi nạp ({len(missing)}, vd. {missing[:3]}) — kết quả sẽ là rác")
        self.model.eval()
        self.tok = AutoTokenizer.from_pretrained(path)
        self.proc = None
        if not getattr(self.tok, "chat_template", None):
            from transformers import AutoProcessor  # noqa: PLC0415
            self.proc = AutoProcessor.from_pretrained(path)
        self.dev = self.model.get_input_embeddings().weight.device

    def logprob(self, text: str) -> float:
        torch = self.torch
        # tiền tố cố định: token đầu (không được chấm) luôn giống nhau giữa hai bản A / B
        ids = self.tok("نص: " + text, return_tensors="pt").input_ids.to(self.dev)
        with torch.no_grad():
            logits = self.model(input_ids=ids).logits[0, :-1].float()
        lp = torch.log_softmax(logits, -1).gather(1, ids[0, 1:, None]).sum().item()
        if lp != lp:  # NaN
            raise RuntimeError("logprob = NaN (fp16 tràn số?)")
        return lp

    def chat(self, user: str) -> str:
        torch = self.torch
        msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
        if self.proc is None:
            prompt = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        else:
            msgs = [{"role": m["role"], "content": [{"type": "text", "text": m["content"]}]} for m in msgs]
            prompt = self.proc.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                                   enable_thinking=False)
        ids = self.tok(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(self.dev)
        n_text = len(self.tok(user).input_ids)
        with torch.no_grad():
            out = self.model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), do_sample=False,
                                      max_new_tokens=min(1024, n_text + 64), pad_token_id=self.tok.eos_token_id)
        s = self.tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
        s = re.sub(r"<think>.*?</think>", "", s, flags=re.S)
        s = s.replace("<<<", "").replace(">>>", "").replace("```", "").strip()
        return s

    def close(self) -> None:
        del self.model
        import gc  # noqa: PLC0415
        gc.collect()
        if self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()


# --- các cách sửa (KHÔNG có nhãn ở đây) -------------------------------------------------------------------------------

def sua_chon(llm: LLM, u: dict, key) -> tuple[str, list[dict]]:
    a, spans = _spans(u["main"], u["check"], key)
    cur, repl, changes = list(a), {}, []
    for i1, i2, alt in spans:
        left = " ".join(cur[max(0, i1 - CTX_LEFT):i1])
        right = " ".join(cur[i2:i2 + CTX_RIGHT])
        ctx = lambda mid: " ".join(x for x in (left, mid, right) if x)  # noqa: E731
        lp_a, lp_b = llm.logprob(ctx(" ".join(a[i1:i2]))), llm.logprob(ctx(" ".join(alt)))
        if lp_b > lp_a:
            # thay cả cụm: từ đầu nhận cả cụm mới, các từ còn lại của cụm thành rỗng
            repl[i1] = " ".join(alt)
            for k in range(i1 + 1, i2):
                repl[k] = ""
            cur[i1:i2] = [" ".join(alt)] + [""] * (i2 - i1 - 1)
            changes.append({"old": " ".join(a[i1:i2]), "new": " ".join(alt), "lp_old": round(lp_a, 2),
                            "lp_new": round(lp_b, 2)})
    text = _rebuild(u["main"], repl)
    return re.sub(r"[ \t]{2,}", " ", text), changes


def sua_viet_lai(llm: LLM, main: str, check: str, key) -> tuple[str, list[dict]]:
    a, b = main.split(), check.split()
    m = _map_check(a, b, key) if b else None
    repl, changes, raw = {}, [], []
    for s, e in _chunks(a, main):
        piece = " ".join(a[s:e])
        hint = " ".join(b[m[s]:m[e]]) if m else ""
        user = f"OCR text:\n<<<\n{piece}\n>>>\n"
        if hint.strip():
            user += ("\nA second OCR system read the same passage as follows (it also makes mistakes; use it only "
                     f"as a hint):\n<<<\n{hint}\n>>>\n")
        user += "\nCorrected text:"
        out = llm.chat(user)
        raw.append(out)
        nw = out.split()
        sm = difflib.SequenceMatcher(None, a[s:e], nw, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "replace" or i2 - i1 != j2 - j1:
                continue
            for k in range(i2 - i1):
                old, new = a[s + i1 + k], nw[j1 + k]
                ok = _accept(old, new)
                if ok:
                    repl[s + i1 + k] = ok
                    changes.append({"old": old, "new": ok})
                else:
                    changes.append({"old": old, "new": new, "rejected": True})
    return _rebuild(main, repl), changes


def _sua_trang(llm: LLM, method: str, units: list[dict], key) -> tuple[dict[str, str], list[dict]]:
    texts, changes = {}, []
    for u in units:
        t, ch = u["main"], []
        if method in ("chon", "chon_sua"):
            t, c1 = sua_chon(llm, u, key)
            ch += [{**c, "step": "chon"} for c in c1]
        if method in ("sua", "chon_sua"):
            t, c2 = sua_viet_lai(llm, t, u["check"], key)
            ch += [{**c, "step": "sua"} for c in c2]
        texts[u["key"]] = t
        changes += [{**c, "block": u["key"], "reader": u["reader"]} for c in ch]
    return texts, changes


# --- chấm (CHỈ ở đây mới đọc nhãn) -------------------------------------------------------------------------------------

def _tran_chon(units: list[dict], ref_words: Counter, ev, key) -> dict[str, str]:
    texts = {}
    for u in units:
        a, spans = _spans(u["main"], u["check"], key)
        repl = {}
        for i1, i2, alt in spans:
            hit = lambda ws: sum(w in ref_words for w in ev.clean(" ".join(ws)).split())  # noqa: E731
            if hit(alt) > hit(a[i1:i2]):
                repl[i1] = " ".join(alt)
                for k in range(i1 + 1, i2):
                    repl[k] = ""
        texts[u["key"]] = re.sub(r"[ \t]{2,}", " ", _rebuild(u["main"], repl))
    return texts


def _classify(change: dict, ref_words: Counter, ev) -> str:
    if change.get("rejected"):
        return "bị luật chặn"
    o, n = ev.clean(change["old"]).split(), ev.clean(change["new"]).split()
    if o == n:
        return "không đổi khi chấm"
    ho, hn = sum(w in ref_words for w in o), sum(w in ref_words for w in n)
    return "sửa đúng" if hn > ho else "làm hỏng" if hn < ho else "không rõ"


# --- chạy -------------------------------------------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ocr", required=True, help="thư mục JSON kết quả arabic-doc-ocr (vd. results/two_gpus)")
    ap.add_argument("--adoc", required=True, help="thư mục repo arabic-doc-ocr (lấy scripts/evaluate.py + examples/)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--models", default="all", help="all hoặc tên ngắn cách nhau dấu phẩy: "
                    + ",".join(n for n, _ in MODELS))
    ap.add_argument("--methods", default=",".join(METHODS))
    ap.add_argument("--pages", default="", help="chỉ các trang này (vd. page_4) — để thử nhanh")
    ap.add_argument("--cache", default="/tmp/llm_sua_cache", help="nơi tải model; model xong là XOÁ khỏi đây")
    ap.add_argument("--keep", action="store_true", help="không xoá model khỏi --cache sau khi chạy")
    ap.add_argument("--cpu", action="store_true", help="chạy trên CPU (chỉ để thử với model nhỏ)")
    ap.add_argument("--extra-model", default="", help="thêm model ngoài danh sách: tên=repo (chỉ để thử)")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    out, adoc, cache = Path(a.out), Path(a.adoc), Path(a.cache)
    if "real_docs" in str(out) or "real_docs" in str(a.ocr):
        raise SystemExit("✘ LỖI: không chạy trên real_docs (dữ liệu khách)")
    out.mkdir(parents=True, exist_ok=True)
    ev, key = _load_adoc(adoc)
    pages = _pages(Path(a.ocr), adoc / "examples", [p for p in a.pages.split(",") if p] or None)
    models = list(MODELS) + ([tuple(a.extra_model.split("=", 1))] if a.extra_model else [])
    if a.models != "all":
        want = a.models.split(",")
        bad = [w for w in want if w not in dict(models)]
        if bad:
            raise SystemExit(f"✘ LỖI: model lạ {bad} (có: {', '.join(n for n, _ in models)})")
        models = [(n, r) for n, r in models if n in want]
    methods = [m for m in a.methods.split(",") if m]
    if any(m not in METHODS for m in methods):
        raise SystemExit(f"✘ LỖI: cách sửa lạ {methods} (có: {METHODS})")
    sync = None
    if a.push:
        from htr_test.sync import Sync  # noqa: PLC0415

        sync = Sync(out)
        sync.restore()
    ocr = {p: json.loads(f.read_text(encoding="utf-8")) for p, f in pages}
    units = {p: _units(js) for p, js in ocr.items()}
    log(f"{len(pages)} trang · {sum(len(u) for u in units.values())} khối · model: {[n for n, _ in models]} · "
        f"cách: {methods}")

    errors = json.loads((out / "loi.json").read_text()) if (out / "loi.json").exists() else {}
    for name, repo in models:
        f = out / f"{name}.jsonl"
        done = set()
        if f.exists():
            for ln in f.read_text(encoding="utf-8").splitlines():
                r = json.loads(ln)
                done.add((r["method"], r["page"]))
        todo = [(m, p) for m in methods for p, _ in pages if (m, p) not in done]
        if not todo:
            log(f"{name}: đã xong từ trước")
            continue
        t0, llm = time.time(), None
        try:
            log(f"== {name} ({repo}): tải + nạp …")
            free = shutil.disk_usage(cache.parent if cache.parent.exists() else "/").free / 2**30
            log(f"   ổ trống {free:.0f} GiB")
            llm = LLM(repo, cache, cpu=a.cpu)
            log(f"   nạp xong ({time.time() - t0:.0f} s, {llm.dtype}, revision {llm.revision[:10]})")
            for m, p in todo:
                t1 = time.time()
                texts, changes = _sua_trang(llm, m, units[p], key)
                rec = {"model": name, "repo": repo, "revision": llm.revision, "dtype": llm.dtype, "method": m,
                       "page": p, "seconds": round(time.time() - t1, 1), "texts": texts, "changes": changes}
                with f.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_ok = sum(1 for c in changes if not c.get("rejected"))
                log(f"   {name} · {m} · {p}: {n_ok} từ đổi ({len(changes) - n_ok} bị luật chặn), "
                    f"{rec['seconds']:.0f} s")
            errors.pop(name, None)
        except Exception as e:  # noqa: BLE001  — model lỗi: ghi lý do, chạy model sau
            msg = f"{type(e).__name__}: {e}"[:500]
            errors[name] = msg
            (out / f"loi_{name}.log").write_text(traceback.format_exc(), encoding="utf-8")
            log(f"⚠ {name} KHÔNG CHẠY ĐƯỢC — {msg}")
        finally:
            if llm is not None:
                llm.close()
            if not a.keep:
                shutil.rmtree(cache / ("models--" + repo.replace("/", "--")), ignore_errors=True)
        (out / "loi.json").write_text(json.dumps(errors, ensure_ascii=False, indent=1), encoding="utf-8")
        _report(out, ocr, units, models, methods, errors, adoc, ev, key)
        if sync:
            sync.push(f"llm_sua: xong {name}")

    _report(out, ocr, units, models, methods, errors, adoc, ev, key)
    if sync:
        sync.push("llm_sua — XONG")
    ran = [n for n, _ in models if (out / f"{n}.jsonl").exists()]
    if not ran:
        print("✘ LỖI: không model nào chạy được — xem loi.json", flush=True)
        return 1
    print(f"✔ XONG TẤT CẢ ({len(ran)}/{len(models)} model chạy được; lỗi: {list(errors) or 'không'})", flush=True)
    return 0


def _report(out: Path, ocr: dict, units: dict, models, methods, errors: dict, adoc: Path, ev, key) -> None:
    labels = {p: json.loads((adoc / "examples" / p / "label.json").read_text(encoding="utf-8")) for p in ocr}
    refw = {p: Counter(ev.clean(labels[p]["text"]).split()) for p in ocr}
    kind = {p: ("viết tay" if ocr[p]["pages"][0].get("info", {}).get("page_type") == "handwritten" else "đánh máy")
            for p in ocr}
    score = lambda p, texts: ev.score(labels[p]["text"], ev.readings(_with_texts(ocr[p], texts))["main"])  # noqa: E731
    rows = {("—", "khong"): {p: {**score(p, {}), "changes": {}} for p in ocr},
            ("—", "tran_chon"): {p: {**score(p, _tran_chon(units[p], refw[p], ev, key)), "changes": {}} for p in ocr}}
    detail = []
    for name, _ in models:
        f = out / f"{name}.jsonl"
        if not f.exists():
            continue
        for ln in f.read_text(encoding="utf-8").splitlines():
            r = json.loads(ln)
            if r["page"] not in ocr or r["method"] not in methods:
                continue
            cls = Counter()
            for c in r["changes"]:
                k = _classify(c, refw[r["page"]], ev)
                cls[k] += 1
                detail.append({"model": name, "method": r["method"], "page": r["page"], "block": c["block"],
                               "step": c.get("step"), "old": c["old"], "new": c["new"], "ket_qua": k})
            rows.setdefault((name, r["method"]), {})[r["page"]] = {**score(r["page"], r["texts"]),
                                                                   "changes": dict(cls), "seconds": r["seconds"]}
    base = rows[("—", "khong")]
    groups = {"đánh máy": [p for p in ocr if kind[p] == "đánh máy"], "viết tay": [p for p in ocr if kind[p] == "viết tay"]}

    def verdict(row: dict, ps: list[str]) -> str:
        """Luật ĐẠT cố định trước: từ đúng tăng ≥ 2 điểm (trung bình các trang), không trang nào giảm ký tự đúng quá
        0,3 điểm, số từ làm hỏng ≤ 1/4 số từ sửa đúng."""
        if not ps or any(p not in row for p in ps):
            return "chưa đủ trang"
        dw = sum(row[p]["words"] - base[p]["words"] for p in ps) / len(ps) * 100
        worst = min((row[p]["chars"] - base[p]["chars"]) * 100 for p in ps)
        good = sum(row[p]["changes"].get("sửa đúng", 0) for p in ps)
        bad = sum(row[p]["changes"].get("làm hỏng", 0) for p in ps)
        ok = dw >= 2.0 and worst >= -0.3 and bad <= good / 4
        return f"{'ĐẠT' if ok else 'không đạt'} (từ {dw:+.1f} · ký tự tệ nhất {worst:+.1f} · sửa đúng {good} / làm hỏng {bad})"

    P = list(ocr)
    L = ["# LLM sửa lỗi OCR — 4 trang mẫu", "",
         f"Cập nhật {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}. Điểm = % ký tự đúng / % từ đúng (mã chấm "
         "của arabic-doc-ocr `scripts/evaluate.py`, văn bản chính). Nhãn chỉ dùng để chấm, không đưa vào LLM.", "",
         "Loại trang: " + ", ".join(f"{p} = {kind[p]}" for p in P), "",
         "| model | cách | " + " | ".join(P) + " | sửa đúng | làm hỏng | không rõ | bị luật chặn | giây |",
         "|---|---|" + "---:|" * len(P) + "---:|---:|---:|---:|---:|"]
    for (name, m), row in rows.items():
        cells = []
        for p in P:
            if p not in row:
                cells.append("–")
                continue
            c, w = 100 * row[p]["chars"], 100 * row[p]["words"]
            if (name, m) == ("—", "khong"):
                cells.append(f"{c:.1f} / {w:.1f}")
            else:
                cells.append(f"{c:.1f} / {w:.1f} ({c - 100 * base[p]['chars']:+.1f} / {w - 100 * base[p]['words']:+.1f})")
        tot = Counter()
        for p in P:
            tot.update(row.get(p, {}).get("changes", {}))
        sec = sum(row.get(p, {}).get("seconds", 0) for p in P)
        L.append(f"| {name} | {m} | " + " | ".join(cells) +
                 f" | {tot['sửa đúng']} | {tot['làm hỏng']} | {tot['không rõ']} | {tot['bị luật chặn']} | {sec:.0f} |")
    L += ["", "`khong` = chưa sửa · `tran_chon` = mức tối đa của cách `chon` (dùng nhãn, không phải cách sửa).", "",
          "## Kết luận theo luật cố định", "",
          "ĐẠT = từ đúng tăng ≥ 2 điểm (trung bình), không trang nào giảm ký tự đúng quá 0,3 điểm, làm hỏng ≤ 1/4 sửa đúng.",
          "", "| model | cách | đánh máy | viết tay |", "|---|---|---|---|"]
    for (name, m), row in rows.items():
        if name == "—":
            continue
        L.append(f"| {name} | {m} | {verdict(row, groups['đánh máy'])} | {verdict(row, groups['viết tay'])} |")
    if errors:
        L += ["", "## Model không chạy được", ""] + [f"- **{n}**: {e}" for n, e in errors.items()]
    L += ["", "Chi tiết từng từ bị đổi: `chi_tiet.csv`."]
    (out / "tom_tat.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "tom_tat.json").write_text(json.dumps({f"{n}|{m}": r for (n, m), r in rows.items()} | {"errors": errors},
                                                 ensure_ascii=False, indent=1), encoding="utf-8")
    with (out / "chi_tiet.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, ["model", "method", "page", "block", "step", "old", "new", "ket_qua"])
        w.writeheader()
        w.writerows(detail)


if __name__ == "__main__":
    sys.exit(main())
