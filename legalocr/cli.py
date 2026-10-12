"""python -m legalocr <lệnh>

  run           ảnh → JSON + văn bản nguyên văn có [؟] + bản chú giải + trường quan trọng + PAGE-XML + phiếu duyệt HTML
  refuse        chạy lại bỏ phiếu / ngưỡng / kiểm tra chéo trên JSON đã có (không cần GPU), vd. sau khi hiệu chỉnh
  eval          chấm trên trang có đáp án: CER/WER + độ chính xác của cờ [؟] (residual error, precision, recall, ECE)
  calibrate     học độ tin cậy + ngưỡng từ các trang dev có đáp án → calibration.json
  apply-review  áp quyết định của người duyệt (JSON xuất từ phiếu duyệt) → bản cuối
  models        in danh mục model đã tra cứu (giấy phép, VRAM, benchmark có nguồn)

Engine (--engine, lặp lại được):  tesseract[:lang]  |  vlm:<model_id>  |  hatformer[:<model_id>]  |  static:<file.json>
  (thêm @trọng_số và #chữ_viết vào cuối, vd. vlm:Qwen/Qwen3-VL-8B-Instruct@0.8#he,lat  tesseract:heb#he)
  vd. --engine vlm:Misraj/Baseer__Nakba@1.0 --engine vlm:sherif1313/Arabic-English-handwritten-OCR-v3@0.8 --engine tesseract:ara@0.5
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .doc import Page


def _engine(spec: str, device: str):
    from .engines import HATFormerEngine, StaticEngine, TesseractEngine, VLMEngine

    weight = scripts = None
    if "#" in spec:  # chữ viết engine được bỏ phiếu: ar, he, lat, digit, mixed
        spec, sc = spec.rsplit("#", 1)
        scripts = frozenset(sc.split(","))
    if "@" in spec:
        spec, w = spec.rsplit("@", 1)
        weight = float(w)
    kind, _, arg = spec.partition(":")
    if kind == "tesseract":
        e = TesseractEngine(name=f"tesseract_{arg or 'ara'}", lang=arg or "ara")
    elif kind == "vlm":
        e = VLMEngine(arg, device=device)
    elif kind == "hatformer":
        e = HATFormerEngine(arg or "Archatext/hatformer-arams28k", device=device)
    elif kind == "static":
        data = json.loads(Path(arg).read_text(encoding="utf-8"))
        e = StaticEngine(data.get("name", Path(arg).stem), data["lines"])
    else:
        raise SystemExit(f"engine không hiểu: {spec}")
    if weight is not None:
        e.weight = weight
    if scripts is not None:
        e.scripts = scripts
    return e


def _cfg(a):
    from .fuse import FusionConfig
    from .pipeline import PipelineConfig
    from .suggest import SuggestConfig

    cal = json.loads(Path(a.calibration).read_text()) if getattr(a, "calibration", None) else None
    fc = FusionConfig(tau_read=a.tau_read, tau_read_critical=a.tau_read_critical, harakat=a.harakat, calibration=cal)
    if cal:
        fc.tau_read = cal.get("tau_read", fc.tau_read)
        fc.tau_read_critical = cal.get("tau_read_critical", fc.tau_read_critical)
    pre = {k: True for k in (a.pre or [])}
    return PipelineConfig(preprocess=pre, fusion=fc, suggest=SuggestConfig(accept=a.accept), doc_type=a.doc_type,
                          years=tuple(a.years), nontext=not a.no_nontext, image_rerank=a.image_rerank)


def _common(p):
    p.add_argument("--tau-read", type=float, default=0.75)
    p.add_argument("--tau-read-critical", type=float, default=0.90)
    p.add_argument("--harakat", choices=["drop", "consensus", "keep"], default="consensus")
    p.add_argument("--calibration", help="calibration.json từ lệnh calibrate")
    p.add_argument("--doc-type", default="auto", help="auto | sale | poa | none")
    p.add_argument("--years", type=int, nargs=2, default=[1940, 1995])
    p.add_argument("--accept", default="none", choices=["none", "ocr_option_image_verified"])
    p.add_argument("--pre", nargs="*", choices=["remove_rules", "mask_holes", "sharpen"], help="tiền xử lý bật thêm")
    p.add_argument("--no-nontext", action="store_true", help="không dò chữ ký / con dấu")
    p.add_argument("--image-rerank", action="store_true")


def cmd_run(a):
    from .pipeline import run_batch
    from .segment import KrakenSegmenter, ProjectionSegmenter

    cfg = _cfg(a)
    if a.doc_type == "none":
        cfg.doc_type = None
    seg = (KrakenSegmenter(device=a.kraken_device) if a.segmenter == "kraken"
           else ProjectionSegmenter(mode="valley" if a.segmenter == "valley" else "gap"))
    engines = [_engine(s, a.device) for s in a.engine]
    pages = []
    if a.dots_cache:
        from .engines import DotsCacheEngine

        pages = [DotsCacheEngine(a.dots_cache)]
    llm = scorer = None
    if a.llm:
        from postcorrect.backend import HFBackend

        llm = HFBackend(a.llm, device=a.llm_device)
    if a.scorer:
        scorer = next((e for e in engines if getattr(e, "model_id", None) == a.scorer), None) or _engine("vlm:" + a.scorer, a.device)
    from .export import summary

    for p in run_batch(a.images, a.out, seg, engines, pages, cfg, llm=llm, scorer=scorer, release=not a.keep_loaded):
        print(json.dumps({"page": p.id, **summary(p), "seconds": p.provenance.get("seconds")}, ensure_ascii=False))


def cmd_refuse(a):
    from .engines import Reading
    from .export import summary, write_all
    from .fuse import EngineSpec
    from .pipeline import fuse_page

    cfg = _cfg(a)
    if a.doc_type == "none":
        cfg.doc_type = None
    for f in a.pages:
        old = Page.from_dict(json.loads(Path(f).read_text(encoding="utf-8")))
        engines = {e for ln in old.lines for e in ln.hyps}
        for spec in old.provenance.get("engines", []):
            cfg.fusion.engines[spec["name"]] = EngineSpec(spec["name"], spec["weight"], frozenset(spec["scripts"]))
        readings = {e: {ln.id: Reading(ln.hyps.get(e, ""), ln.hyp_probs.get(e)) for ln in old.lines} for e in engines}
        for ln in old.lines:
            ln.words, ln.reasons, ln.dropped = [], [], []
        old.issues, old.fields = [], []
        page = fuse_page(old, readings, {}, cfg)
        write_all(page, Path(a.out))
        print(json.dumps({"page": page.id, **summary(page)}, ensure_ascii=False))


def cmd_eval(a):
    from .evaluate import evaluate_page, summarize

    rows = []
    for f in a.pages:
        page = Page.from_dict(json.loads(Path(f).read_text(encoding="utf-8")))
        gt = (Path(a.gt_dir) / f"{page.id}.txt").read_text(encoding="utf-8")
        rows.append(evaluate_page(page, gt))
    s = summarize(rows)
    print(json.dumps(s, ensure_ascii=False, indent=1))


def cmd_calibrate(a):
    from .calibrate import calibrate, save
    from .evaluate import training_rows

    rows = []
    for f in a.pages:
        page = Page.from_dict(json.loads(Path(f).read_text(encoding="utf-8")))
        rows += training_rows(page, (Path(a.gt_dir) / f"{page.id}.txt").read_text(encoding="utf-8"))
    cal = calibrate(rows, a.target, a.target_critical)
    save(cal, Path(a.out))
    print(json.dumps({k: v for k, v in cal.items() if k != "weights"}, indent=1))


def cmd_apply_review(a):
    from .export import page_text, summary, write_all
    from .review import apply_decisions

    page = Page.from_dict(json.loads(Path(a.page).read_text(encoding="utf-8")))
    dec = json.loads(Path(a.decisions).read_text(encoding="utf-8"))
    stats = apply_decisions(page, dec["decisions"] if isinstance(dec, dict) else dec)
    out = Path(a.out)
    write_all(page, out)
    (out / f"{page.id}.final.txt").write_text(page_text(page), encoding="utf-8")
    print(json.dumps({**stats, **summary(page)}, ensure_ascii=False))


def cmd_models(a):
    from .catalog import table

    print(table())


def main(argv=None):
    ap = argparse.ArgumentParser(prog="legalocr", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("images", nargs="+")
    p.add_argument("--out", required=True)
    p.add_argument("--engine", action="append", required=True)
    p.add_argument("--dots-cache", help="thư mục cache dots.mocr (postcorrect.ocr_cache) làm engine cả trang")
    p.add_argument("--segmenter", choices=["kraken", "projection", "valley"], default="kraken")
    p.add_argument("--keep-loaded", action="store_true", help="không nhả VRAM giữa các engine (đủ VRAM cho tất cả)")
    p.add_argument("--kraken-device", default="cpu")
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--llm", help="LLM gợi ý (cục bộ), vd. Qwen/Qwen3-8B")
    p.add_argument("--llm-device", type=int, default=1)
    p.add_argument("--scorer", help="VLM chấm gợi ý theo ảnh dòng (nên khác model trụ)")
    _common(p)
    p.set_defaults(fn=cmd_run)
    p = sub.add_parser("refuse")
    p.add_argument("pages", nargs="+")
    p.add_argument("--out", required=True)
    _common(p)
    p.set_defaults(fn=cmd_refuse)
    p = sub.add_parser("eval")
    p.add_argument("pages", nargs="+")
    p.add_argument("--gt-dir", required=True)
    p.set_defaults(fn=cmd_eval)
    p = sub.add_parser("calibrate")
    p.add_argument("pages", nargs="+")
    p.add_argument("--gt-dir", required=True)
    p.add_argument("--out", default="calibration.json")
    p.add_argument("--target", type=float, default=0.02)
    p.add_argument("--target-critical", type=float, default=0.005)
    p.set_defaults(fn=cmd_calibrate)
    p = sub.add_parser("apply-review")
    p.add_argument("page")
    p.add_argument("decisions")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_apply_review)
    p = sub.add_parser("models")
    p.set_defaults(fn=cmd_models)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
