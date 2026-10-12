"""Adapter ocrbench `legalocr.adapter:LegalOCRAdapter` — dùng được ngay trong web demo / `ocrbench convert`:
kraken tách dòng → mỗi dòng đọc bằng NHIỀU engine theo chữ viết → bỏ phiếu → đọc lại chữ số → khoanh thông tin quan
trọng → kiểm tra chéo → khối chữ có [؟] + khối hình (chữ ký / con dấu) theo thứ tự đọc.

Sửa đúng các lỗi đo được ở cấu hình cũ (kraken + Tesseract `ara+eng`):
- `ara+eng` → mỗi engine MỘT ngôn ngữ, model tessdata_best: hết rác Latin, hết LRM/RLM Tesseract chèn quanh mẩu Latin.
- chữ số Ả Rập-Ấn Tesseract không đọc được ("١٩٧٢" → "1171", "٥٤٩" → "1") → bộ đọc chữ số riêng (legalocr.digits)
  bỏ phiếu ở từng từ có số; số chỉ "chắc" khi mọi engine khớp TỪNG chữ số, không thì [؟].
- dòng bị xếp sai chỗ (hai cột xen kẽ) → thứ tự đọc XY-cut (legalocr.order), cột phải trước.
- dòng Hebrew (ô công chứng) đọc bằng `ara` thành rác → mỗi dòng đọc cả `heb`, chọn theo độ tin cậy.
- dòng nằm trong khung chữ ký / con dấu bị BỎ (số công văn, ngày viết tay cạnh chữ ký) → giữ, đọc, in [توقيع: …].
- nét kéo dài máy chữ / chữ lặp, ký tự điều khiển → chuẩn hoá (engines.normalize_token).
- không có độ tin cậy → mỗi từ có trạng thái; văn bản in từ[؟] / [؟]; `extra` có issues + fields để soát.
Dòng chữ viết tay (độ tin cậy Tesseract thấp) có thể gửi thêm engine chữ tay: `handwriting: hatformer` (CPU, chậm,
CC-BY-NC-SA) hoặc `handwriting: vlm:<model_id>` (GPU).
"""

from __future__ import annotations

import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ocrbench.adapters.base import Adapter, Prediction

from .doc import Line, Page
from .engines import TesseractEngine, default_tessdata, fetch_tessdata, upscale_line
from .export import REGION_LABEL, summary, word_token
from .fuse import EngineSpec, FusionConfig, add_token_reading
from .pipeline import PipelineConfig, fuse_page
from .script import has_digit, script_profile

RTL_SCRIPTS = frozenset({"ar", "digit", "mixed"})


def _mean_conf(r) -> float:
    """Độ tin cậy trung bình của một dòng, theo độ dài từ."""
    if not r or not r.words or not r.word_probs:
        return 0.0
    w = [max(1, len(t)) for t in r.words]
    return sum(p * k for p, k in zip(r.word_probs, w)) / sum(w)


def _share(text: str, script: str) -> float:
    p = script_profile(text)
    letters = p["ar"] + p["he"] + p["lat"]
    return p[script] / letters if letters else 0.0


class LegalOCRAdapter(Adapter):
    defaults = {
        "python": None,                 # python của venv kraken (inference/setup_kraken.sh); None = tự tìm
        "seg_model": None,
        "seg_height": 1400,
        "device": "cpu",
        "text_direction": "horizontal-rl",
        "min_line_ink": 0.72,
        "tessdata": "auto",             # thư mục tessdata_best | auto | null (tessdata hệ thống, bản fast)
        "fetch_tessdata": False,        # thiếu tessdata_best thì tải (cần mạng) vào ~/.cache/legalocr/tessdata_best
        # model Tesseract cho dòng Ả Rập — mỗi model một phiếu. Đo trên 2 trang có đáp án (công văn 1972, hợp đồng
        # số): ara FAST + phóng dòng tốt nhất (CER 18,2% / 1,3%), ara best + phóng 19,4% / 2,2%, script/Arabic 23,7% /
        # 1,8% → fast làm phiếu chính. tessdata: system = tessdata của hệ thống, best = thư mục tessdata_best.
        "arabic": [{"lang": "ara", "tessdata": "system", "weight": 0.9},
                   {"lang": "ara", "tessdata": "best", "weight": 0.7},
                   {"lang": "Arabic", "tessdata": "best", "weight": 0.5}],
        "hebrew": "heb",                # null = không đọc Hebrew
        "latin": "eng",                 # chỉ thử trên dòng trong vùng con dấu / tem khi ara, heb đều kém
        "digits": True,
        "digit_weight": 1.2,
        "handwriting": None,            # null | hatformer | vlm:<model_id>
        "handwriting_device": "cpu",
        "hard_conf": 0.55,              # dòng chữ Ả Rập có độ tin cậy Tesseract < ngưỡng → gửi engine chữ tay
        "max_hard_lines": 60,
        # dòng có engine chữ tay mà Tesseract < ngưỡng → bỏ phiếu Tesseract: trên 6 dòng chữ tay (hợp đồng 1972) HATFormer
        # một mình CER 35,9%, bỏ phiếu chung với Tesseract 45,9%
        "drop_tesseract_below": 0.55,
        "pictures": True,
        "signatures": True,
        "stamps": True,
        "signature_threshold": 0.45,
        "upscale_to": 80,               # chiều cao dòng tối thiểu khi đưa Tesseract
        # legalocr.preprocess.prepare — mặc định TẮT hết: trên công văn 1972 (550×708) làm phẳng nền làm CER Tesseract
        # 19,4% → 21,3%, phóng cả trang 19,4% → 22,1% (phóng TỪNG DÒNG lúc đọc đã đủ). deskew luôn tắt (giữ toạ độ).
        "preprocess": {"flatten": False, "contrast": False, "upscale": False},
        "stamp_aspect": [0.5, 2.0],     # khung "con dấu" dài / dẹt hơn khoảng này (vd. tiêu đề in màu) → bỏ
        "junk_conf": 0.3,               # dòng trong vùng chữ ký / con dấu có độ tin cậy trung bình < ngưỡng → in [توقيع]
        "doc_type": "auto",
        "years": [1940, 1995],
        "tau_read": 0.75,
        "tau_read_critical": 0.90,
        "keep_page": True,              # extra["legalocr"] = toàn bộ trang (mọi cách đọc, lý do, độ tin cậy)
        "workers": None,
        "timeout": 600,
    }

    def load(self):
        from ocrbench.adapters.kraken_layout import KrakenWorker, default_python

        p = self.params
        py = p["python"] or default_python()
        if not py:
            raise RuntimeError("Chưa có venv kraken: chạy `bash inference/setup_kraken.sh`")
        if not shutil.which("tesseract"):
            raise RuntimeError("Chưa cài tesseract (apt-get install -y tesseract-ocr tesseract-ocr-ara)")
        tdir = default_tessdata() if p["tessdata"] == "auto" else p["tessdata"]
        if tdir is None and p["fetch_tessdata"]:
            tdir = str(fetch_tessdata(Path.home() / ".cache" / "legalocr" / "tessdata_best"))
        self.tessdata = tdir
        avail = {"system": set(_langs(None)), "best": set(_langs(tdir)) if tdir else set()}
        n = p["workers"] or max(1, len(os.sched_getaffinity(0)))
        self.arabic = []
        for spec in p["arabic"]:
            src = spec.get("tessdata", "best")
            if spec["lang"] in avail.get(src, set()):
                self.arabic.append(TesseractEngine(f"tess_{spec['lang']}_{src}", spec["lang"], weight=spec["weight"],
                                                   scripts=RTL_SCRIPTS, tessdata_dir=None if src == "system" else tdir,
                                                   upscale_to=p["upscale_to"], workers=n))
        if not self.arabic:
            raise RuntimeError(f"không có model Tesseract Ả Rập nào: {p['arabic']} (tessdata_best: {tdir})")
        def single(lang, name, scripts):
            src = "best" if lang in avail["best"] else "system" if lang in avail["system"] else None
            return (TesseractEngine(name, lang, weight=0.8, scripts=scripts, tessdata_dir=tdir if src == "best" else None,
                                    upscale_to=p["upscale_to"], workers=n) if lang and src else None)

        self.hebrew = single(p["hebrew"], "tess_heb", frozenset({"he", "mixed"}))
        self.latin = single(p["latin"], "tess_eng", frozenset({"lat", "mixed", "digit"}))
        self.hand = None
        if p["handwriting"] == "hatformer":
            from .engines import HATFormerEngine

            # beam 1: nhanh gấp 3,5 lần beam 3 trên CPU (29 s so với 104 s / 6 dòng), CER 35,9% so với 38,6%
            self.hand = HATFormerEngine(device=p["handwriting_device"], weight=1.1, num_beams=1)
        elif p["handwriting"] and str(p["handwriting"]).startswith("vlm:"):
            from .engines import VLMEngine

            self.hand = VLMEngine(p["handwriting"][4:], device=p["handwriting_device"], weight=1.1)
        if p["digits"]:
            from .digits import model

            model()  # lần đầu: huấn luyện từ phông (~3 phút CPU) rồi lưu cache
        self.worker = KrakenWorker(py, p["seg_model"], p["device"], p["seg_height"], p["timeout"])
        self.worker.start()
        self.pool = ThreadPoolExecutor(2)

    def close(self):
        self.worker.close()
        self.pool.shutdown(wait=False)
        if self.hand is not None and hasattr(self.hand, "close"):
            self.hand.close()

    # ------------------------------------------------------------------ các bước
    def _segment(self, rec) -> list[Line]:
        from ocrbench.adapters.kraken_layout import drop_faint_lines, parse_lines

        from .segment import _line, extend_to_ink, fragmented, merge_fragments

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "page.png"
            rec.save(path)
            seg = self.worker.segment(str(path), self.params["text_direction"])
        raw = parse_lines(seg)
        if self.params["min_line_ink"]:
            raw = drop_faint_lines(rec, raw, self.params["min_line_ink"])
        lines = [_line(i, ln["bbox"], ln["polygon"]) for i, ln in enumerate(raw)]
        return extend_to_ink(merge_fragments(lines), rec) if fragmented(lines) else lines

    def _regions(self, rec, lines: list[Line]) -> tuple[list[dict], list[list[int]]]:
        """→ (khối hình cho DOCX: Picture / Signature, khung con dấu từ model con dấu — để gắn nhãn [ختم])."""
        from ocrbench.adapters.kraken_layout import text_mask
        from ocrbench.pictures import combine, find_pictures, find_signatures

        from .segment import STAMP_MODEL, SIGNATURE_MODEL

        p = self.params
        if not p["pictures"]:
            return [], []
        sigs = stamps = None
        if p["signatures"]:
            try:
                sigs = find_signatures(rec, SIGNATURE_MODEL if p["signatures"] is True else p["signatures"],
                                       p["signature_threshold"])
            except Exception:  # chưa tải được model: chỉ dùng luật ảnh
                sigs = None
        if p["stamps"]:
            try:
                stamps = find_signatures(rec, STAMP_MODEL if p["stamps"] is True else p["stamps"], p["signature_threshold"])
            except Exception:
                stamps = None
        mask, lh = text_mask(rec.size, [{"polygon": ln.polygon, "bbox": ln.bbox} for ln in lines])
        pics = find_pictures(rec, text_mask=mask, line_height=lh)
        lo, hi = p["stamp_aspect"]
        # con dấu tròn / vuông; khung dài (tiêu đề in màu bị nhận nhầm là con dấu — đo trên hợp đồng mẫu) → bỏ
        stamps = [b for b in (stamps or []) if lo <= (b[2] - b[0]) / max(1, b[3] - b[1]) <= hi]
        pics += [{"bbox": b, "kind": "stamp", "fill": 1.0} for b in stamps]
        return combine(pics, sigs), list(stamps or [])

    def predict(self, image, item):
        from .ink import ink_profile, is_red_mark
        from .order import reading_order
        from .preprocess import prepare
        from .segment import label_regions, line_crops

        p = self.params
        image = image.convert("RGB")
        geom, rec, pre_info = prepare(image, {**p["preprocess"], "deskew": False})
        k = rec.width / image.width  # hệ số phóng (ảnh nhỏ / ảnh chụp màn hình được phóng trước khi tách dòng)
        lines = self._segment(rec)
        regions, stamps = self._regions(rec, lines)
        label_regions(lines, {"Signature": [r["bbox"] for r in regions if r["category"] == "Signature"],
                              "Stamp": stamps, "Picture": [r["bbox"] for r in regions if r["category"] == "Picture"]})
        order = reading_order([ln.bbox for ln in lines])
        lines = [lines[i] for i in order]
        for i, ln in enumerate(lines):
            ln.id = f"l{i:03d}"
        crops = line_crops(rec, lines)
        for ln in lines:
            if is_red_mark(ink_profile(crops[ln.id])):
                ln.region = "Watermark"
        todo = [ln for ln in lines if ln.region != "Watermark"]
        readings, scripts = self._read(todo, crops)
        fc = FusionConfig(tau_read=p["tau_read"], tau_read_critical=p["tau_read_critical"])
        for e in self.arabic + [x for x in (self.hebrew, self.latin, self.hand) if x is not None]:
            fc.engines[e.name] = EngineSpec(e.name, e.weight, e.scripts)
        fc.engines["digits"] = EngineSpec("digits", p["digit_weight"])
        cfg = PipelineConfig(fusion=fc, doc_type=None if p["doc_type"] in (None, "none") else p["doc_type"],
                             years=tuple(p["years"]), nontext=False)
        page = Page(id=str(getattr(item, "id", None) or "page"), image="", size=list(rec.size), lines=lines)
        hook = self._digit_hook(crops, readings, fc) if p["digits"] else None
        fuse_page(page, readings, {}, cfg, token_hook=hook)
        for ln in lines:
            if ln.region == "Watermark":
                page.issues.append({"type": "watermark_line", "severity": "info", "line": ln.id, "word_ids": [],
                                    "message": "dòng mực đỏ (watermark / dấu đỏ) — không đọc, không in", "details": {}})
        page.provenance = {"preprocess": pre_info, "scale": round(k, 4), "tessdata": self.tessdata, "scripts": scripts,
                           "regions": regions, "engines": sorted(readings)}
        return self._prediction(page, regions, k)

    def _read(self, lines: list[Line], crops: dict) -> tuple[dict, dict]:
        """Mọi dòng: các model Ả Rập + Hebrew; chọn chữ viết từng dòng theo độ tin cậy; dòng vùng hình kém cả hai thì
        thử Latin; dòng Ả Rập kém (chữ tay) → engine chữ tay. → (readings[engine][line_id], script mỗi dòng)."""
        p = self.params
        ims = [crops[ln.id] for ln in lines]
        ids = [ln.id for ln in lines]
        raw = {e.name: dict(zip(ids, e.read(ims))) for e in self.arabic}
        from .engines import Reading

        for e in self.arabic:  # model Ả Rập trả chữ Latin (script/Arabic hay ra "ERB ay NIS…") = đọc hỏng → không bỏ phiếu
            for i, r in raw[e.name].items():
                if r.text and _share(r.text, "lat") > 0.3:
                    raw[e.name][i] = Reading("", [], [], {"failed": "latin_output"})
        heb = dict(zip(ids, self.hebrew.read(ims))) if self.hebrew else {}
        scripts, out = {}, {e.name: {} for e in self.arabic}
        hard = []
        hebrew_lines = self._hebrew_lines(lines, raw, heb)
        for ln in lines:
            a = max(_mean_conf(raw[e.name][ln.id]) for e in self.arabic)
            h = _mean_conf(heb.get(ln.id))
            if ln.id in hebrew_lines:
                scripts[ln.id] = "he"
                out.setdefault(self.hebrew.name, {})[ln.id] = heb[ln.id]
                continue
            if self.latin and ln.region != "Text" and max(a, h) < 0.5:
                r = self.latin.read([crops[ln.id]])[0]
                if _mean_conf(r) >= max(a, h) + 0.1 and _share(r.text, "lat") >= 0.6:
                    scripts[ln.id] = "lat"
                    out.setdefault(self.latin.name, {})[ln.id] = r
                    continue
            scripts[ln.id] = "ar"
            for e in self.arabic:
                out[e.name][ln.id] = raw[e.name][ln.id]
            if a < p["hard_conf"]:
                hard.append((a, ln.id))
        if self.hand is not None and hard:
            hard = sorted(hard)[: p["max_hard_lines"]]
            hr = self.hand.read([crops[i] for _, i in hard])
            for (a, i), r in zip(hard, hr):
                out.setdefault(self.hand.name, {})[i] = r
                if a < p["drop_tesseract_below"]:
                    for e in self.arabic:
                        out[e.name].pop(i, None)
                    scripts[i] = "ar_hand"
        return out, scripts

    def _hebrew_lines(self, lines: list[Line], raw: dict, heb: dict) -> set[str]:
        """Dòng nào là Hebrew. Độ tin cậy `heb` của dòng Hebrew thật (ô công chứng: 0,45–0,79) và của dòng chữ tay Ả Rập
        bị nhận nhầm (0,27–0,50) chồng lên nhau → thêm bằng chứng VỊ TRÍ: dòng "chắc" (tin cậy ≥ 0,6, ≥ 75% ký tự là chữ
        Hebrew, ≥ 3 chữ) nhận ngay; dòng yếu hơn chỉ nhận khi cùng cột và cách một dòng chắc ≤ 3 lần chiều cao dòng."""
        if not heb:
            return set()

        def stats(ln):
            a = max(_mean_conf(raw[e.name][ln.id]) for e in self.arabic)
            r = heb.get(ln.id)
            t = r.text if r else ""
            chars = [c for c in t if not c.isspace()]
            prof = script_profile(t)
            return a, _mean_conf(r), prof["he"], prof["he"] / max(1, len(chars))

        cand = {}
        for ln in lines:
            a, h, n_he, he_frac = stats(ln)
            if h >= a + 0.08 and n_he >= 3 and _share(heb[ln.id].text, "he") >= 0.6:
                cand[ln.id] = (ln, h >= 0.6 and he_frac >= 0.75)
        strong = [ln for ln, ok in cand.values() if ok]
        keep = {ln.id for ln in strong}
        for lid, (ln, ok) in cand.items():
            if ok:
                continue
            h_ = ln.bbox[3] - ln.bbox[1]
            for s_ in strong:
                dy = max(0, max(s_.bbox[1], ln.bbox[1]) - min(s_.bbox[3], ln.bbox[3]))
                same_col = min(s_.bbox[2], ln.bbox[2]) - max(s_.bbox[0], ln.bbox[0]) > 0.3 * (ln.bbox[2] - ln.bbox[0])
                if same_col and dy <= 3 * h_:
                    keep.add(lid)
                    break
        return keep

    def _digit_hook(self, crops: dict, readings: dict, fc: FusionConfig):
        """Bộ đọc chữ số bỏ phiếu ở mọi từ mà ÍT NHẤT MỘT engine Ả Rập thấy có chữ số (fast hay đọc chữ số máy chữ
        thành chữ cái: "٥٤٩" → "44ه" ở bản best nhưng không có số ở bản fast) — khung từ lấy từ chính engine đó."""
        names = [e.name for e in self.arabic]

        def hook(page: Page) -> None:
            from .digits import merge_affixes, read_tokens

            jobs, keys = [], []  # ảnh từ; (line_id, engine, chỉ số token trong dòng của engine, chữ token)
            for ln in page.lines:
                up = None
                for e in names:
                    r = readings.get(e, {}).get(ln.id)
                    if not r or not r.boxes:
                        continue
                    for t, (w, b) in enumerate(zip(r.words, r.boxes)):
                        if has_digit(w):
                            up = up or upscale_line(crops[ln.id], self.params["upscale_to"])
                            jobs.append(up.crop((max(0, b[0] - 4), max(0, b[1] - 6), b[2] + 4, b[3] + 6)))
                            keys.append((ln.id, e, t, w))
            if not jobs:
                return
            reads = read_tokens(jobs)
            by_line: dict[str, dict[str, list]] = {}
            for (lid, e, t, w), d in zip(keys, reads):
                by_line.setdefault(lid, {}).setdefault(e, []).append((w, d))
            for ln in page.lines:
                engines = by_line.get(ln.id)
                if not engines:
                    continue
                pos = {e: 0 for e in engines}
                for w in ln.words:
                    for e in names:  # engine trọng số cao trước
                        queue = engines.get(e)
                        rd = w.readings.get(e, "")
                        if not queue or len(rd.split()) != 1 or not has_digit(rd):
                            continue
                        k = next((k for k in range(pos[e], len(queue)) if queue[k][0] == rd), None)
                        if k is None:
                            continue
                        pos[e] = k + 1
                        tok, d = queue[k]
                        if d.text:
                            add_token_reading(w, "digits", merge_affixes(tok, d.text), d.confidence, fc)
                            w.features["digits_conf"] = round(d.confidence, 3)
                            w.features["digits_from"] = e
                        break
        return hook

    def _prediction(self, page: Page, regions: list[dict], k: float) -> Prediction:
        def back(b):
            return [int(round(v / k)) for v in b]

        blocks, texts = [], []
        regs = sorted(regions, key=lambda r: r["bbox"][1])
        placed = set()
        for ln in page.lines:
            for ri, r in enumerate(regs):  # khối hình đặt trước dòng đầu tiên nằm thấp hơn nó (như ocrbench.pictures)
                if ri not in placed and r["bbox"][1] <= ln.bbox[1]:
                    blocks.append({"category": r["category"], "bbox": back(r["bbox"]), "text": ""})
                    placed.add(ri)
            if ln.region == "Watermark" or not ln.words:
                continue
            body = " ".join(word_token(w) for w in ln.words)
            if ln.region != "Text":
                label = REGION_LABEL.get(ln.region, ln.region)
                mean = sum(w.confidence for w in ln.words) / len(ln.words)
                # nét chữ ký / hoa văn con dấu đọc ra rác: chỉ in nhãn (cách đọc vẫn nằm trong extra["legalocr"])
                body = f"[{label}]" if mean < self.params["junk_conf"] else f"[{label}: {body}]"
            texts.append(body)
            blocks.append({"category": "Text", "bbox": back(ln.bbox), "polygon": [back(pt) for pt in ln.polygon],
                           "text": body})
        for ri, r in enumerate(regs):
            if ri not in placed:
                blocks.append({"category": r["category"], "bbox": back(r["bbox"]), "text": ""})
        confs = [w.confidence for w in page.words()]
        extra = {"blocks": blocks, "lines": len(page.lines), "issues": page.issues, "fields": page.fields,
                 "summary": summary(page)}
        if self.params["keep_page"]:
            extra["legalocr"] = page.to_dict()
        return Prediction("\n".join(texts), confidence=(sum(confs) / len(confs)) if confs else None, extra=extra)


def _langs(tessdata_dir: str | None) -> list[str]:
    import subprocess

    cmd = ["tesseract", "--list-langs"] + (["--tessdata-dir", tessdata_dir] if tessdata_dir else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    lines = (r.stdout + "\n" + r.stderr).splitlines()  # tuỳ bản, danh sách in ra stdout hoặc stderr
    return [x.strip() for x in lines if x.strip() and " " not in x.strip() and ":" not in x]
