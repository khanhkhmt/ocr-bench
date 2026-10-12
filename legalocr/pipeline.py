"""Ghép các bước: ảnh → tiền xử lý → tách dòng + vùng không phải chữ → nhiều model đọc từng dòng (+ model đọc cả trang)
→ bỏ phiếu → khoanh thông tin quan trọng → ngưỡng tin cậy → kiểm tra chéo → (tuỳ chọn) LLM gợi ý + chấm bằng ảnh →
bằng chứng ảnh → xuất.

`fuse_page` tách riêng phần không cần ảnh / GPU (chỉ cần chữ các model đã đọc) để chạy lại nhanh khi đổi ngưỡng, đổi
trọng số model, hay sau khi hiệu chỉnh — và để test.
"""

from __future__ import annotations

import datetime as dt
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .align import align_pair
from .crosscheck import _issue, run_all
from .doc import Line, Page
from .engines import Reading
from .entities import tag_page
from .fuse import FusionConfig, decide_status, fuse_line
from .suggest import SuggestConfig, image_rerank, suggest_page

VERSION = "0.1.0"


@dataclass
class PipelineConfig:
    preprocess: dict = field(default_factory=dict)
    fusion: FusionConfig = field(default_factory=FusionConfig)
    suggest: SuggestConfig = field(default_factory=SuggestConfig)
    doc_type: str | None = "auto"            # auto | sale | poa | None
    years: tuple = (1940, 1995)
    hijri_years: tuple = (1360, 1415)
    nontext: bool = True
    image_rerank: bool = False
    page_only_min_words: int = 3
    extra_lexicon: dict | None = None


def distribute_page_words(pivot_words: list[list[str]], page: Reading, min_run: int = 3):
    """Chia chữ của model đọc CẢ TRANG về từng dòng, bằng cách căn với chữ model trụ của các dòng (theo thứ tự đọc).
    Chuỗi ≥ min_run từ mà không dòng nào có → KHÔNG gán (có thể là dòng bị tách sót, hoặc model trang bịa), trả về riêng
    để báo cáo. → ([(từ, xác suất)] mỗi dòng, [{"after_line": chỉ số, "words": [...]}])."""
    flat = [(li, w) for li, ws in enumerate(pivot_words) for w in ws]
    pw, pp = page.words, page.word_probs or [None] * len(page.words)
    per = [([], []) for _ in pivot_words]
    extras, run, run_line = [], [], 0
    last_line = 0

    def flush():
        nonlocal run
        if len(run) >= min_run:
            extras.append({"after_line": run_line, "words": [pw[j] for j in run]})
        elif run and per:
            for j in run:
                per[run_line][0].append(pw[j])
                per[run_line][1].append(pp[j])
        run = []

    band = max(40, int(0.15 * max(len(flat), len(pw))))  # thứ tự đọc gần giống nhau → căn trong dải chéo
    for pi, hj in align_pair([w for _, w in flat], pw, band):
        if pi:
            flush()
            last_line = flat[pi[0]][0]
            for j in hj:
                per[last_line][0].append(pw[j])
                per[last_line][1].append(pp[j])
        else:
            if not run:
                run_line = last_line
            run.extend(hj)
    flush()
    return per, extras


def fuse_page(page: Page, line_readings: dict[str, dict[str, Reading]], page_readings: dict[str, Reading],
              cfg: PipelineConfig) -> Page:
    fc = cfg.fusion
    lines = page.lines
    hyps = {ln.id: {e: (r[ln.id].words, r[ln.id].word_probs) for e, r in line_readings.items() if ln.id in r}
            for ln in lines}
    if page_readings:
        def pivot(ln):
            cand = [(fc.weight(e), e) for e, (ws, _) in hyps[ln.id].items() if ws]
            return hyps[ln.id][max(cand)[1]][0] if cand else []

        text_lines = [ln for ln in lines if ln.region == "Text"]
        pv = [pivot(ln) for ln in text_lines]
        for e, rd in page_readings.items():
            if rd is None or not rd.words:
                continue
            per, extras = distribute_page_words(pv, rd, cfg.page_only_min_words)
            for ln, (ws, ps) in zip(text_lines, per):
                hyps[ln.id][e] = (ws, ps)
            page.provenance.setdefault("page_only", {})[e] = extras
    for ln in lines:
        fuse_line(ln, hyps[ln.id], fc)
    tag_page(page, cfg.extra_lexicon)
    for w in page.words():
        decide_status(w, fc)
    run_all(page, cfg.doc_type, cfg.years, cfg.hijri_years)
    for e, extras in page.provenance.get("page_only", {}).items():
        for x in extras:
            ln = lines[min(x["after_line"], len(lines) - 1)] if lines else None
            _issue(page, "page_only_text", "warn",
                   f"{e} đọc ra {len(x['words'])} từ không dòng nào có (dòng bị tách sót, hoặc {e} bịa): "
                   + " ".join(x["words"][:20]), line=ln.id if ln else None, engine=e, words=x["words"])
    return page


@dataclass
class PageJob:
    """Một trang đã tiền xử lý + tách dòng, chờ các engine đọc."""
    id: str
    path: Path
    geom: object
    rec: object
    pre_info: dict
    lines: list
    boxes: dict
    crops: dict
    timing: dict = field(default_factory=dict)
    readings: dict = field(default_factory=dict)


def prepare_page(path: str | Path, segmenter, cfg: PipelineConfig, page_id: str | None = None) -> PageJob:
    from PIL import Image, ImageOps

    from .preprocess import prepare
    from .segment import detect_nontext, label_regions, line_crops

    path = Path(path)
    t0 = time.perf_counter()
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    geom, rec, pre_info = prepare(img, cfg.preprocess)
    lines: list[Line] = segmenter.segment(rec)
    boxes = detect_nontext(rec, lines) if cfg.nontext else {}
    label_regions(lines, boxes)
    job = PageJob(page_id or path.stem, path, geom, rec, pre_info, lines, boxes, line_crops(rec, lines))
    job.timing["prepare"] = time.perf_counter() - t0
    return job


def read_lines(jobs: list[PageJob], engine, release: bool = True) -> None:
    """MỘT engine đọc dòng của MỌI trang (theo lô), rồi giải phóng VRAM trước khi engine sau được nạp — hai VLM ~3,75B
    fp16 không vừa chung một T4."""
    from .engines import clean_text

    t = time.perf_counter()
    for job in jobs:
        ids = [ln.id for ln in job.lines]
        rs = engine.read_ids(ids) if hasattr(engine, "read_ids") else engine.read([job.crops[i] for i in ids])
        job.readings[engine.name] = {i: Reading(clean_text(r.text), r.word_probs, r.boxes, r.meta) for i, r in zip(ids, rs)}
    dt_ = time.perf_counter() - t
    for job in jobs:
        job.timing[engine.name] = dt_ / max(1, len(jobs))
    if release and hasattr(engine, "close"):
        engine.close()


def finish_page(job: PageJob, out_dir: str | Path, line_engines: list, page_engines: list = (),
                cfg: PipelineConfig | None = None, llm=None, scorer=None) -> Page:
    from .evidence import save_evidence, sha256_file
    from .export import write_all
    from .fuse import EngineSpec

    cfg = cfg or PipelineConfig()
    out_dir = Path(out_dir)
    t0 = time.perf_counter()
    page_readings = {pe.name: pe.read_page(job.id) for pe in page_engines}
    for e in list(line_engines) + list(page_engines):
        if e.name not in cfg.fusion.engines:
            cfg.fusion.engines[e.name] = EngineSpec(e.name, getattr(e, "weight", 1.0),
                                                    getattr(e, "scripts", EngineSpec("x").scripts))
    page = Page(id=job.id, image=str(job.path), image_sha256=sha256_file(job.path), size=list(job.geom.size),
                lines=job.lines)
    page.provenance = {
        "legalocr": VERSION, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "preprocess": job.pre_info,
        "engines": [{"name": e.name, "model": getattr(e, "model_id", getattr(e, "lang", None)),
                     "weight": cfg.fusion.weight(e.name), "scripts": sorted(cfg.fusion.engines[e.name].scripts)}
                    for e in list(line_engines) + list(page_engines)],
        "nontext": dict(job.boxes),
        "fusion": {k: v for k, v in asdict(cfg.fusion).items() if k != "engines"},
    }
    fuse_page(page, job.readings, page_readings, cfg)
    if scorer is not None and cfg.image_rerank:
        page.provenance["image_rerank"] = {"scorer": scorer.name, "words": image_rerank(page, scorer, job.crops)}
        if any(ln.pivot == scorer.name for ln in page.lines):
            page.provenance["image_rerank"]["warning"] = "scorer trùng model trụ: điểm ảnh thiên vị cách đọc của chính nó"
    if llm is not None:
        page.provenance["suggest"] = {"llm": getattr(llm, "model_id", "?"), "config": asdict(cfg.suggest),
                                      "stats": suggest_page(page, llm, cfg.suggest, scorer, job.crops)}
    save_evidence(page, job.geom, out_dir)
    job.timing["finish"] = time.perf_counter() - t0
    page.provenance["seconds"] = {k: round(v, 2) for k, v in job.timing.items()}
    write_all(page, out_dir)
    return page


def run_batch(paths: list, out_dir: str | Path, segmenter, line_engines: list, page_engines: list = (),
              cfg: PipelineConfig | None = None, llm=None, scorer=None, release: bool = True) -> list[Page]:
    """Nhiều trang: tách dòng hết → từng engine đọc hết rồi nhả GPU → bỏ phiếu / kiểm tra / gợi ý / xuất từng trang."""
    cfg = cfg or PipelineConfig()
    jobs = [prepare_page(p, segmenter, cfg) for p in paths]
    for e in line_engines:
        read_lines(jobs, e, release)
    return [finish_page(j, out_dir, line_engines, page_engines, cfg, llm, scorer) for j in jobs]


def process_image(path: str | Path, out_dir: str | Path, segmenter, line_engines: list, page_engines: list = (),
                  cfg: PipelineConfig | None = None, llm=None, scorer=None, page_id: str | None = None) -> Page:
    """Một trang (giữ engine đã nạp — gọi lại cho trang sau không phải nạp lại)."""
    cfg = cfg or PipelineConfig()
    job = prepare_page(path, segmenter, cfg, page_id)
    for e in line_engines:
        read_lines([job], e, release=False)
    return finish_page(job, out_dir, line_engines, page_engines, cfg, llm, scorer)
