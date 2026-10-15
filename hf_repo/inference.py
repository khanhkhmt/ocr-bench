"""Arabic handwritten text recognition on old documents — Baseer-Nakba + LoRA adapters (ft3 / ft4).

The model reads ONE text-line image at a time. Two adapters read every line independently:
ft3 = main reader, ft4 = cross-check. Words where the two readings differ are flagged as suspicious
(on 500-line test sets this flags ~13–19% of words and catches 57–75% of the wrong words).

    # one or more LINE images
    python inference.py line line1.png line2.png
    # a whole PAGE: line segmentation (Kraken + Muharaf model if installed, else horizontal projection)
    python inference.py page page.jpg --out result/

    # Python
    from inference import HTRReader
    r = HTRReader()                              # ft3 + ft4 on Misraj/Baseer__Nakba
    r.read([Image.open("line.png")])             # ['…']  (ft3)
    r.read_check([Image.open("line.png")])       # [{'text': …, 'check': …, 'words': [(word, suspicious, alt)], …}]

Requirements: torch, transformers >= 4.49 (tested 4.56.1), peft, pillow, numpy, huggingface_hub.
GPU with >= 10 GB recommended (fp16 on T4, bf16 on Ampere+); CPU works (bf16) but is slow.
License: CC BY-NC-SA 4.0 (non-commercial), inherited from Baseer-Nakba and Muharaf.
"""

from __future__ import annotations

import argparse
import base64
import difflib
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO = "khanh99/htr-baseer-nakba-ft"
BASE = "Misraj/Baseer__Nakba"
# exactly as the authors' Baseer_Nakba.py (github.com/misraj-ai/Nakba-pipeline)
PROMPT = "Extract the text from the above document."
TEMPLATE = ("<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
            "<|im_start|>user\n<|vision_start|><|image_pad|><|vision_end|>{p}<|im_end|>\n"
            "<|im_start|>assistant\n")
MUHARAF_SEG_URL = "https://zenodo.org/records/14295555/files/muharaf_seg_best.mlmodel?download=1"  # CC BY 4.0


# ---------------------------------------------------------------------------------------------------------------- text

def clean_repeated_substrings(text: str) -> str:
    """From the authors' Baseer_Nakba.py: cut a tail repeated >= 10 times (generation loop)."""
    n = len(text)
    if n < 200:
        return text
    for length in range(2, n // 10 + 1):
        cand, count, i = text[-length:], 0, n - length
        while i >= 0 and text[i:i + length] == cand:
            count += 1
            i -= length
        if count >= 10:
            return text[:n - length * (count - 1)]
    return text


_PERSIAN = str.maketrans({"ی": "ي", "ک": "ك", "ۃ": "ة", "ہ": "ه", "ۀ": "ة",
                          **{chr(0x06F0 + i): chr(0x0660 + i) for i in range(10)}})
_LETTERS = "ء-يٮ-ۓ"
_LONE_WAW = re.compile(rf"(?<![{_LETTERS}ً-ْ])و([ً-ْ]*)\s+(?=[{_LETTERS}])")


def fix_arabic(s: str) -> str:
    """Persian code points → the Arabic letters with the same shape; a lone "و" is joined to the next word
    ("و" is never a word on its own). Nothing else is changed."""
    return _LONE_WAW.sub(r"و\1", (s or "").translate(_PERSIAN))


_HARAKAT = re.compile(r"[ً-ْٰـ]")
_ALEF = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه"})
_PUNCT = re.compile(r"[\s\.\,\:\;\!\?\(\)\[\]\"'«»،؛؟\-–—#\*_|]+")


def _key(w: str) -> str:
    """Ignore differences that do not change the reading: harakat, hamza/alef, ى/ي, ة/ه, attached punctuation."""
    return _PUNCT.sub("", _HARAKAT.sub("", w)).translate(_ALEF)


def compare_words(main: str, check: str) -> list[tuple[str, bool, str]]:
    """→ [(word of the main reading, suspicious?, what the check reader read there)]."""
    a, b = main.split(), check.split()
    sm = difflib.SequenceMatcher(None, [_key(w) for w in a], [_key(w) for w in b], autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        alt = " ".join(b[j1:j2])
        for w in a[i1:i2]:
            out.append((w, tag != "equal", "" if tag == "equal" else (alt or "(nothing)")))
    return out


# --------------------------------------------------------------------------------------------------------------- model

class HTRReader:
    """Baseer-Nakba (Qwen2.5-VL-3B) with one or more LoRA adapters from REPO sharing one base model."""

    def __init__(self, adapters=("ft3", "ft4"), device: str | None = None, dtype: str = "auto",
                 scale: dict[str, float] | None = None, repo: str = REPO, base: str = BASE,
                 max_new_tokens: int = 128):
        import torch

        self.torch = torch
        self.adapters = list(adapters)
        self.device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
        self.dtype, self.scale, self.repo, self.base = dtype, dict(scale or {}), repo, base
        self.max_new_tokens = max_new_tokens
        self.model = self.processor = None

    def _dtype(self):
        t = self.torch
        if self.dtype != "auto":
            return {"fp16": t.float16, "bf16": t.bfloat16, "fp32": t.float32}[self.dtype]
        if self.device.startswith("cuda"):
            return t.bfloat16 if t.cuda.get_device_capability(self.device)[0] >= 8 else t.float16
        return t.bfloat16  # CPU: half the RAM of fp32 (the authors run bf16)

    @staticmethod
    def _fix_config(cfg):
        """The base repo stores the image-token ids only in text_config; transformers 4.56 looks for them at the top
        level ('vision_start_token_id' AttributeError). Copy the values (unchanged)."""
        tc = getattr(cfg, "text_config", None)
        for k in ("image_token_id", "video_token_id", "vision_start_token_id", "vision_end_token_id",
                  "vision_token_id"):
            v = getattr(tc, k, None) if tc is not None else None
            if v is not None and getattr(cfg, k, None) is None:
                setattr(cfg, k, v)
        return cfg

    def load(self):
        import transformers
        from huggingface_hub import snapshot_download
        from peft import PeftModel
        from transformers import AutoConfig, AutoProcessor, Qwen2_5_VLForConditionalGeneration

        try:  # old torchao (e.g. Colab) makes peft raise ImportError on plain layers — we never use torchao
            import peft.import_utils as iu
            import peft.tuners.lora.torchao as lt
            iu.is_torchao_available = lt.is_torchao_available = lambda: False
        except Exception:  # noqa: BLE001
            pass
        t0 = time.time()
        major, minor = (int(x) for x in transformers.__version__.split(".")[:2])
        kw = {"dtype" if (major, minor) >= (4, 56) else "torch_dtype": self._dtype(),
              "device_map": {"": self.device}}
        cfg = self._fix_config(AutoConfig.from_pretrained(self.base))
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(self.base, config=cfg, **kw).eval()
        if self.adapters:
            root = Path(snapshot_download(self.repo, allow_patterns=[f"{a}/*" for a in self.adapters]))
            for i, a in enumerate(self.adapters):
                if not (root / a / "adapter_config.json").exists():
                    raise FileNotFoundError(f"adapter {a} not found in {self.repo}")
                if i == 0:
                    self.model = PeftModel.from_pretrained(self.model, str(root / a), adapter_name=a).eval()
                else:
                    self.model.load_adapter(str(root / a), adapter_name=a)
            self._apply_scale()
        try:
            self.processor = AutoProcessor.from_pretrained(self.base, min_pixels=28 * 28, max_pixels=1280 * 28 * 28)
        except TypeError:  # newer processors take a size dict
            self.processor = AutoProcessor.from_pretrained(
                self.base, size={"shortest_edge": 28 * 28, "longest_edge": 1280 * 28 * 28})
        self.processor.tokenizer.padding_side = "left"
        print(f"loaded {self.base} + {self.adapters} on {self.device} ({kw[next(iter(kw))]}) in "
              f"{time.time() - t0:.0f}s", file=sys.stderr)
        return self

    def _apply_scale(self):
        """Adapter strength: 1 = as trained, 0.5 = halfway back to the base model (ft1 is used at 0.5)."""
        sc = {a: v for a, v in self.scale.items() if v != 1.0}
        if set(sc) - set(self.adapters):
            raise ValueError(f"scale for adapters not loaded: {sorted(set(sc) - set(self.adapters))}")
        for mod in self.model.modules():
            s = getattr(mod, "scaling", None)
            if isinstance(s, dict):
                for a, v in sc.items():
                    if a in s:
                        s[a] *= v

    def _select(self, adapter: str | None):
        import contextlib

        if adapter == "base":
            return self.model.disable_adapter() if self.adapters else contextlib.nullcontext()
        if self.adapters:
            a = adapter or self.adapters[0]
            if a not in self.adapters:
                raise ValueError(f"adapter {a} not loaded ({self.adapters})")
            self.model.set_adapter(a)
        return contextlib.nullcontext()

    def read(self, lines: list[Image.Image], adapter: str | None = None) -> list[str]:
        """Read line images one by one (batch 1 — batching makes Qwen2.5-VL stop early on transformers 4.56).
        adapter: "ft3" / "ft4" / … (default: the first loaded), "base" = Baseer-Nakba without adapter."""
        if self.model is None:
            self.load()
        torch, out = self.torch, []
        prompt = TEMPLATE.format(p=PROMPT)
        for im in lines:
            inputs = self.processor(text=[prompt], images=[im.convert("RGB")], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            with torch.no_grad(), self._select(adapter):
                ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, do_sample=False,
                                          repetition_penalty=1.1, eos_token_id=[151645, 151643], pad_token_id=151643)
            n_in = inputs["input_ids"].shape[1]
            txt = self.processor.decode(ids[0][n_in:], skip_special_tokens=True).strip()
            out.append(fix_arabic(clean_repeated_substrings(txt)))
        return out

    def read_check(self, lines: list[Image.Image], main: str = "ft3", check: str = "ft4") -> list[dict]:
        """Read with two adapters → per line: text (main), check, words [(word, suspicious, alt)], agree (0–1)."""
        a, b = self.read(lines, main), self.read(lines, check)
        out = []
        for x, y in zip(a, b):
            w = compare_words(x, y)
            out.append({"text": x, "check": y, "words": w,
                        "agree": 1.0 if not w else sum(not s for _, s, _ in w) / len(w)})
        return out


# ---------------------------------------------------------------------------------------------- page → line images

def _ink(g: np.ndarray) -> np.ndarray:
    bg, dark = np.percentile(g, 75), np.percentile(g, 0.5)
    if bg - dark < 30:
        return np.zeros(g.shape, bool)
    m = g < (bg + dark) / 2
    m[m.mean(axis=1) > 0.5, :] = False  # long horizontal rules (ruled paper) are not text
    return m


def _projection_rows(m: np.ndarray, min_h: int = 6) -> list[tuple[int, int]]:
    H = m.shape[0]
    if not m.any():
        return []
    prof = m.sum(axis=1).astype(np.float32)
    on = prof > 0.05 * prof.max()
    bands, start = [], None
    for y in range(H + 1):
        if y < H and on[y] and start is None:
            start = y
        elif (y == H or not on[y]) and start is not None:
            bands.append((start, y))
            start = None
    med = float(np.median([b - a for a, b in bands])) if bands else 10.0
    k = max(3, int(med / 4))
    sm = np.convolve(prof, np.ones(k) / k, mode="same")
    thr = 0.12 * sm.max()
    bands, start = [], None
    for y in range(H + 1):
        if y < H and sm[y] > thr and start is None:
            start = y
        elif (y == H or sm[y] <= thr) and start is not None:
            bands.append((start, y))
            start = None
    if not bands:
        return []
    med = float(np.median([b - a for a, b in bands]))
    out = []
    for a, b in bands:  # unusually tall band = touching lines → cut at the lowest valley
        segs = [(a, b)]
        while True:
            a2, b2 = segs[-1]
            if b2 - a2 < 1.7 * med:
                break
            lo, hi = a2 + int(0.6 * med), b2 - int(0.6 * med)
            if hi <= lo:
                break
            cut = lo + int(np.argmin(sm[lo:hi]))
            segs[-1:] = [(a2, cut), (cut, b2)]
        out += segs
    merged: list[list[int]] = []
    for a, b in out:  # very thin band (dots / diacritics) → merge into the previous line
        if b - a < max(min_h, 0.35 * med) and merged and a - merged[-1][1] < 0.6 * med:
            merged[-1][1] = max(merged[-1][1], b)
            continue
        merged.append([a, b])
    pad = int(round(0.2 * med))
    return [(max(0, a - pad), min(H, b + pad)) for a, b in merged if b - a >= min_h]


def lines_projection(page: Image.Image) -> list[dict]:
    """Fallback segmentation without Kraken: horizontal projection on the whole page (single-column pages only)."""
    m = _ink(np.asarray(page.convert("L"), dtype=np.float32))
    W = m.shape[1]
    out = []
    for y0, y1 in _projection_rows(m):
        cols = np.nonzero(m[y0:y1].any(axis=0))[0]
        if len(cols):
            pad = max(4, int(0.02 * W))
            out.append({"box": (max(0, int(cols.min()) - pad), y0, min(W, int(cols.max()) + 1 + pad), y1),
                        "poly": [], "baseline": []})
    return out


def lines_kraken(page: Image.Image, kraken_bin: str, seg_model: str) -> list[dict] | None:
    """Kraken baseline segmentation (blla) with the Muharaf model — follows curved / slanted handwritten lines and
    ignores ruled-paper lines. None on failure."""
    with tempfile.TemporaryDirectory() as d:
        p, out = Path(d) / "page.png", Path(d) / "seg.json"
        page.convert("RGB").save(p)
        try:
            subprocess.run([kraken_bin, "-i", str(p), str(out), "segment", "-bl", "-i", seg_model], check=True,
                           capture_output=True, timeout=600)
            seg = json.loads(out.read_text())
        except Exception as e:  # noqa: BLE001
            print(f"kraken failed ({type(e).__name__}) → projection", file=sys.stderr)
            return None
    lines = []
    for ln in seg.get("lines", []):
        poly = [(float(x), float(y)) for x, y in (ln.get("boundary") or [])]
        base = [(float(x), float(y)) for x, y in (ln.get("baseline") or [])]
        pts = poly or base
        if len(pts) >= 2:
            xs, ys = [q[0] for q in pts], [q[1] for q in pts]
            lines.append({"box": (int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1), "poly": poly,
                          "baseline": base})
    lines.sort(key=lambda L: (L["box"][1] + L["box"][3]) / 2)
    return lines


def crop_line(page: Image.Image, line: dict, pad: int = 4) -> Image.Image:
    """Crop a line; outside the Kraken polygon is painted paper colour (less ink from the lines above / below)."""
    W, H = page.size
    x0, y0, x1, y1 = line["box"]
    x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    crop = page.convert("RGB").crop((x0, y0, x1, y1))
    if len(line.get("poly") or []) < 3:
        return crop
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in line["poly"]], fill=255)
    bg = int(np.percentile(np.asarray(crop.convert("L")), 90))
    return Image.composite(crop, Image.new("RGB", crop.size, (bg, bg, bg)), mask)


def segment(page: Image.Image, kraken_bin: str | None = None, seg_model: str | None = None,
            use_kraken: bool = True) -> tuple[list[dict], str]:
    kraken_bin = kraken_bin or shutil.which("kraken")
    if use_kraken and kraken_bin:
        if not seg_model:
            seg_model = str(Path.home() / ".cache" / "htr_ft" / "muharaf_seg_best.mlmodel")
            if not Path(seg_model).exists():
                Path(seg_model).parent.mkdir(parents=True, exist_ok=True)
                print("downloading Kraken Muharaf segmentation model (CC BY 4.0)…", file=sys.stderr)
                urllib.request.urlretrieve(MUHARAF_SEG_URL, seg_model)
        lines = lines_kraken(page, kraken_bin, seg_model)
        if lines:
            return lines, "kraken_muharaf"
    return lines_projection(page), "projection"


# --------------------------------------------------------------------------------------------------------------- output

def _b64(im: Image.Image, h: int = 56) -> str:
    im = im.copy()
    im.thumbnail((900, h))
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()


def _marked(words, main_name: str = "ft3", check_name: str = "ft4") -> str:
    return " ".join(f"<mark title='{check_name}: {html.escape(alt)}'>{html.escape(w)}</mark>" if s else html.escape(w)
                    for w, s, alt in words)


def write_page(out: Path, name: str, page: Image.Image, lines: list[dict], crops, res: list[dict], method: str,
               check: bool) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.txt").write_text("\n".join(r["text"] for r in res), encoding="utf-8")
    n_w = sum(len(r["words"]) for r in res) if check else 0
    n_s = sum(s for r in res for _, s, _ in r["words"]) if check else 0
    data = {"segmentation": method, "lines": len(res), "words": n_w, "suspicious_words": n_s,
            "result": [{"box": list(L["box"]), "text": r["text"], **({"check": r["check"], "agree": round(r["agree"], 3),
                        "suspicious": [w for w, s, _ in r["words"] if s]} if check else {})}
                       for L, r in zip(lines, res)]}
    (out / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    vis = page.convert("RGB").copy()
    dr = ImageDraw.Draw(vis)
    for L, r in zip(lines, res):
        col = (26, 127, 55) if (not check or r["agree"] >= 0.999) else (234, 88, 12)
        if len(L.get("poly") or []) >= 3:
            dr.polygon([tuple(p) for p in L["poly"]], outline=col, width=2)
        else:
            dr.rectangle(L["box"], outline=col, width=2)
    vis.save(out / f"{name}_lines.jpg", quality=85)
    rows = "".join(
        f"<tr><td><img src='data:image/jpeg;base64,{_b64(c)}'><br><small>{i + 1}</small></td>"
        f"<td class=ar>{_marked(r['words']) if check else html.escape(r['text'])}</td>"
        + (f"<td class=ar>{html.escape(r['check'])}</td>" if check else "") + "</tr>"
        for i, (c, r) in enumerate(zip(crops, res)))
    head = "<tr><th>line</th><th>ft3 (main)</th>" + ("<th>ft4 (check)</th>" if check else "") + "</tr>"
    css = ("body{font-family:sans-serif;margin:16px} table{border-collapse:collapse;width:100%} td,th{border:1px solid #ccc;"
           "padding:4px;vertical-align:top} .ar{direction:rtl;text-align:right;font-size:18px;line-height:1.7;"
           "font-family:'Noto Naskh Arabic','Amiri',serif} mark{background:#ffe14d} img{max-width:100%}")
    summary = (f"<p>{len(res)} lines · segmentation: {method}"
               + (f" · {n_s}/{n_w} words highlighted (ft4 read them differently — check against the image)" if check
                  else "") + "</p>")
    (out / f"{name}.html").write_text(f"<!doctype html><meta charset=utf-8><title>{html.escape(name)}</title>"
                                      f"<style>{css}</style>{summary}<table>{head}{rows}</table>", encoding="utf-8")
    return data


# ------------------------------------------------------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["line", "page"])
    ap.add_argument("images", nargs="+")
    ap.add_argument("--adapters", default="ft3,ft4", help="main[,check] — e.g. ft3,ft4 (default), ft3, ft1, base")
    ap.add_argument("--scale", default="", help="adapter strength, e.g. ft1=0.5 (ft1 is recommended at 0.5)")
    ap.add_argument("--device", default=None, help="cuda:0 / cpu (default: cuda if available)")
    ap.add_argument("--dtype", default="auto", choices=["auto", "fp16", "bf16", "fp32"])
    ap.add_argument("--out", default="htr_out", help="page mode: output folder")
    ap.add_argument("--kraken-bin", default=None, help="kraken executable (default: on PATH)")
    ap.add_argument("--seg-model", default=None, help="Kraken segmentation model (default: Muharaf, auto-download)")
    ap.add_argument("--no-kraken", action="store_true", help="page mode: horizontal projection only")
    ap.add_argument("--json", default=None, help="line mode: also write results to this JSON file")
    a = ap.parse_args(argv)
    names = [x for x in a.adapters.split(",") if x]
    load = [x for x in names if x != "base"]
    scale = {k: float(v) for k, v in (kv.split("=") for kv in a.scale.split(",") if kv)}
    reader = HTRReader(adapters=load, device=a.device, dtype=a.dtype, scale=scale)
    check = len(names) > 1
    if a.mode == "line":
        ims = [Image.open(p).convert("RGB") for p in a.images]
        res = (reader.read_check(ims, names[0], names[1]) if check else
               [{"text": t} for t in reader.read(ims, names[0])])
        for p, r in zip(a.images, res):
            if check:
                marked = " ".join(f"[?{w}]" if s else w for w, s, _ in r["words"])
                print(f"{p}\n  {names[0]}: {marked}\n  {names[1]}: {r['check']}")
            else:
                print(f"{p}\n  {names[0]}: {r['text']}")
        if a.json:
            Path(a.json).write_text(json.dumps([{"image": p, **{k: v for k, v in r.items() if k != "words"},
                                                 **({"suspicious": [w for w, s, _ in r["words"] if s]} if check else {})}
                                                for p, r in zip(a.images, res)], ensure_ascii=False, indent=1),
                                    encoding="utf-8")
        return 0
    for p in a.images:
        page = Image.open(p).convert("RGB")
        t0 = time.time()
        lines, method = segment(page, a.kraken_bin, a.seg_model, not a.no_kraken)
        crops = [crop_line(page, L) for L in lines]
        print(f"{p}: {len(lines)} lines ({method}) — reading…", file=sys.stderr)
        res = (reader.read_check(crops, names[0], names[1]) if check else
               [{"text": t, "words": []} for t in reader.read(crops, names[0])])
        d = write_page(Path(a.out), Path(p).stem, page, lines, crops, res, method, check)
        print(f"{p}: {d['lines']} lines" + (f", {d['suspicious_words']}/{d['words']} words highlighted" if check else "")
              + f" · {time.time() - t0:.0f}s → {a.out}/{Path(p).stem}.{{txt,json,html}}, _lines.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
