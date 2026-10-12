"""python -m postcorrect <lệnh>

  dataset muharaf      dựng bộ đánh giá công khai (dataset.py)
  ocr                  chạy dots.mocr lưu cache OCR (ocr_cache.py; python của venv dots)
  correct-cache        sửa hàng loạt từ cache OCR  (một tiến trình mỗi GPU: --device i --shard i/n)
  correct-text         sửa một văn bản (file hoặc stdin) → JSON
  correct-image        ảnh → dots (GPU --ocr-device) → LLM (GPU --llm-device) → JSON  (venv dots)
  eval                 so các lượt chạy với đáp án: CER/WER trước-sau, sửa đúng / sửa nhầm, KTC bootstrap

JSON kết quả mỗi trang: {id, original, corrected, edits:[{index, span, from, to, chunk, block}], flags, rejected, chunks,
settings}. `index` = chỉ số từ (theo khoảng trắng) trong `original`.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .guard import GuardConfig
from .pipeline import PageText, Settings, correct_pages, page_text_from_cells


def add_model_args(ap):
    ap.add_argument("--model", default="Qwen/Qwen3-8B", help="id Hugging Face của LLM (chạy cục bộ)")
    ap.add_argument("--quant", choices=["nf4", "fp16"], default="nf4")
    ap.add_argument("--strategy", choices=["A", "B", "C"], default="A",
                    help="A viết lại chunk | B khoanh từ lỗi (JSON) | C viết lại, chỉ đổi từ NLL cao")
    ap.add_argument("--fewshot", action="store_true")
    ap.add_argument("--chunk-chars", type=int, default=700)
    ap.add_argument("--flag-frac", type=float, default=0.3)
    ap.add_argument("--flag-min-nll", type=float, default=3.0)
    ap.add_argument("--max-char-edit", type=int, default=2)
    ap.add_argument("--max-edit-ratio", type=float, default=0.35)
    ap.add_argument("--tag", default="")
    ap.add_argument("--max-batch", type=int, default=8)


def settings_from(a) -> Settings:
    return Settings(strategy=a.strategy, chunk_chars=a.chunk_chars, fewshot=a.fewshot, flag_frac=a.flag_frac,
                    flag_min_nll=a.flag_min_nll, tag=a.tag,
                    guard=GuardConfig(max_char_edit=a.max_char_edit, max_edit_ratio=a.max_edit_ratio))


def load_backend(a, device: int):
    from .backend import HFBackend

    return HFBackend(a.model, device=device, quant=a.quant, max_batch=a.max_batch)


# ---------------------------------------------------------------- correct-cache
def load_ocr_pages(ocr_dir: Path, ids: list[str]) -> list[PageText]:
    pages = []
    for i in ids:
        f = ocr_dir / f"{i}.json"
        if not f.exists():
            continue
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("error") or not rec.get("cells"):
            continue
        p = page_text_from_cells(rec["id"], rec["cells"])
        if p.text.strip():
            pages.append(p)
    return pages


def cmd_correct_cache(a):
    from .ocr_cache import load_manifest

    rows = load_manifest(Path(a.manifest))
    if a.split:
        rows = [r for r in rows if r.get("split") == a.split]
    ids = [r["id"] for r in rows]
    if a.limit:
        ids = ids[:a.limit]
    si, sn = (int(x) for x in a.shard.split("/"))
    ids = [i for k, i in enumerate(ids) if k % sn == si]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pages = [p for p in load_ocr_pages(Path(a.ocr), [i for i in ids if not (out / f"{i}.json").exists()])]
    print(f"[shard {a.shard}] {len(ids)} trang thuộc phần này, cần chạy {len(pages)} (còn lại đã có kết quả / OCR lỗi)", flush=True)
    if not pages:
        return
    st = settings_from(a)
    backend = load_backend(a, a.device)
    print(f"nạp {a.model} ({a.quant}) trên cuda:{a.device}: {backend.load_seconds:.0f}s", flush=True)
    meta = {"model": a.model, "quant": a.quant, "device": a.device, "shard": a.shard, "settings": st.as_dict(),
            "load_seconds": round(backend.load_seconds, 1), "groups": [], "pages_done": 0}
    t_all = time.perf_counter()
    for g in range(0, len(pages), a.group):
        grp = pages[g:g + a.group]
        s0 = (backend.stats.seconds, backend.stats.prompt_tokens, backend.stats.new_tokens)
        t = time.perf_counter()
        results = correct_pages(grp, backend, st)
        dt = time.perf_counter() - t
        for r in results:
            (out / f"{r['id']}.json").write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        meta["pages_done"] += len(grp)
        meta["groups"].append({"pages": len(grp), "seconds": round(dt, 1),
                               "gen_seconds": round(backend.stats.seconds - s0[0], 1),
                               "prompt_tokens": backend.stats.prompt_tokens - s0[1],
                               "new_tokens": backend.stats.new_tokens - s0[2]})
        meta["wall_seconds"] = round(time.perf_counter() - t_all, 1)
        meta["oom_retries"] = backend.stats.oom_retries
        (out / f"run_meta_{a.shard.replace('/', 'of')}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        n_e = sum(len(r["edits"]) for r in results)
        print(f"  {meta['pages_done']}/{len(pages)} trang | {dt:.0f}s | {n_e} sửa nhận / "
              f"{sum(len(r['rejected']) for r in results)} từ chối", flush=True)
    backend.close()


# ---------------------------------------------------------------- correct-text / correct-image
def cmd_correct_text(a):
    text = sys.stdin.read() if a.input == "-" else Path(a.input).read_text(encoding="utf-8")
    backend = load_backend(a, a.device)
    res = correct_pages([PageText("text", text.strip(), [])], backend, settings_from(a))[0]
    print(json.dumps(res, ensure_ascii=False, indent=1))


def cmd_correct_image(a):
    from PIL import Image, ImageOps

    from .ocr_cache import ROOT, make_adapter

    adapter, _ = make_adapter(Path(a.config or ROOT / "inference/config.yaml"), a.ocr_model,
                              {"device_map": {"": f"cuda:{a.ocr_device}"}})
    adapter.load()
    img = ImageOps.exif_transpose(Image.open(a.image)).convert("RGB")
    t = time.perf_counter()
    ocr = adapter.parse_image(img)
    ocr_s = time.perf_counter() - t
    page = page_text_from_cells(Path(a.image).stem, ocr["cells"])
    backend = load_backend(a, a.llm_device)
    res = correct_pages([page], backend, settings_from(a))[0]
    res["ocr"] = {"seconds": round(ocr_s, 1), "flags": {k: v for k, v in ocr["extra"].items() if k != "blocks"}}
    print(json.dumps(res, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- eval
def _label_path(s: str) -> tuple[str, Path]:
    return tuple(s.split("=", 1)) if "=" in s else (Path(s).name, Path(s))  # type: ignore[return-value]


def cmd_eval(a):
    from collections import Counter

    from .evaluate import STRICT, bootstrap_ci, by_noise_bins, page_metrics, summarize
    from .ocr_cache import load_manifest

    man = {r["id"]: r for r in load_manifest(Path(a.manifest))}
    runs = {}
    for lab, path in map(_label_path, a.runs):
        runs[lab] = {}
        for f in sorted(Path(path).glob("*.json")):
            if f.name.startswith("run_meta"):
                continue
            r = json.loads(f.read_text(encoding="utf-8"))
            if r["id"] in man and (not a.split or man[r["id"]].get("split") == a.split):
                runs[lab][r["id"]] = r
    common = sorted(set.intersection(*(set(v) for v in runs.values()))) if runs else []
    print(f"# Đánh giá — {len(common)} trang chung của {len(runs)} lượt chạy"
          f"{' (' + a.split + ')' if a.split else ''}\n")
    if not common:
        return
    table = {}
    for lab, rs in runs.items():
        rows = [page_metrics(man[i]["gt"], rs[i]["original"], rs[i]["corrected"], rs[i]["edits"], rs[i].get("flags"))
                for i in common]
        table[lab] = rows
    base_rows = [page_metrics(man[i]["gt"], next(iter(runs.values()))[i]["original"],
                              next(iter(runs.values()))[i]["original"], []) for i in common]
    out = {}

    def fmt_ci(rows, stat, name):
        lo, hi = bootstrap_ci(rows, stat, n=a.boot, name=name)
        return f"[{lo * 100:+.2f}, {hi * 100:+.2f}]"

    for name in ("strict", "lenient"):
        sb = summarize(base_rows, name)
        print(f"## Chuẩn hoá {name}  (CER/WER OCR gốc: {sb['cer_before']:.3f} / {sb['wer_before']:.3f}; "
              f"{sb['ref_words']} từ đáp án; từ OCR sai trong tầm với của chốt chặn: {sb['reach_frac_of_err']:.1%})\n")
        print("| lượt chạy | CER sau | ΔCER (điểm %) [KTC 95%] | WER sau | số sửa | chính xác | sửa nhầm (từ đúng bị đổi) | "
              "sửa đúng hẳn | giây/trang |")
        print("|---|---|---|---|---|---|---|---|---|")
        for lab, rows in table.items():
            s = summarize(rows, name)
            meta = _meta_seconds(Path(dict(map(_label_path, a.runs))[lab]), len(runs[lab]))
            print(f"| {lab} | {s['cer_after']:.4f} | {s['cer_delta'] * 100:+.2f} {fmt_ci(rows, lambda x: x['cer_delta'], name)} | "
                  f"{s['wer_after']:.4f} | {s['edits']} | {s['precision']:.2f} | {s['harm_rate'] * 100:.2f}% ({s['harm']}) | "
                  f"{s['fixed']} | {meta} |")
            out.setdefault(lab, {})[name] = s
        print()
    print("## Theo mức nhiễu của OCR (strict): ΔCER điểm % / số sửa đúng hẳn / số từ đúng bị đổi\n")
    bins = {lab: dict(by_noise_bins(rows)) for lab, rows in table.items()}
    names = list(next(iter(bins.values())).keys())
    print("| lượt chạy | " + " | ".join(f"{n} ({bins[next(iter(bins))][n]['pages']} trang)" for n in names) + " |")
    print("|---|" + "---|" * len(names))
    for lab in table:
        cells = []
        for n in names:
            s = bins[lab].get(n)
            cells.append(f"{s['cer_delta'] * 100:+.2f} / {s['fixed']} / {s['harm']}" if s else "—")
        print(f"| {lab} | " + " | ".join(cells) + " |")
    print()
    for lab, rows in table.items():
        if "flag_precision" in summarize(rows):
            s = summarize(rows)
            print(f"- Cờ nghi lỗi của {lab}: {s['flags']} từ, precision {s['flag_precision']:.2f}, recall {s['flag_recall']:.2f}")
        why = Counter(x["reason"] for r in runs[lab].values() for x in r["rejected"])
        cr = Counter(c["chunk_reason"] for r in runs[lab].values() for c in r["chunks"] if c["chunk_reason"])
        st = Counter(c["status"] for r in runs[lab].values() for c in r["chunks"])
        print(f"- {lab}: từ chối theo lý do {dict(why)}; bỏ cả chunk {dict(cr)}; trạng thái chunk {dict(st)}")
    if a.json:
        Path(a.json).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


def _meta_seconds(path: Path, pages: int) -> str:
    """Giây sinh chữ trung bình mỗi trang trên MỘT GPU (cộng các shard)."""
    tot, n = 0.0, 0
    for f in path.glob("run_meta*.json"):
        m = json.loads(f.read_text(encoding="utf-8"))
        tot += sum(g["seconds"] for g in m["groups"])
        n += m["pages_done"]
    return f"{tot / n:.1f}" if n else "—"


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(prog="postcorrect", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("correct-cache")
    p.add_argument("--ocr", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--split", choices=["dev", "holdout"])
    p.add_argument("--limit", type=int)
    p.add_argument("--device", type=int, default=0)
    p.add_argument("--shard", default="0/1")
    p.add_argument("--group", type=int, default=8)
    add_model_args(p)
    p.set_defaults(func=cmd_correct_cache)

    p = sub.add_parser("correct-text")
    p.add_argument("input", help="file văn bản hoặc - (stdin)")
    p.add_argument("--device", type=int, default=0)
    add_model_args(p)
    p.set_defaults(func=cmd_correct_text)

    p = sub.add_parser("correct-image")
    p.add_argument("image")
    p.add_argument("--config")
    p.add_argument("--ocr-model", default="dots_mocr")
    p.add_argument("--ocr-device", type=int, default=0)
    p.add_argument("--llm-device", type=int, default=1)
    add_model_args(p)
    p.set_defaults(func=cmd_correct_image)

    p = sub.add_parser("eval")
    p.add_argument("--manifest", required=True)
    p.add_argument("--runs", nargs="+", required=True, help="thư mục kết quả, dạng nhãn=đường_dẫn")
    p.add_argument("--split", choices=["dev", "holdout"])
    p.add_argument("--boot", type=int, default=2000)
    p.add_argument("--json")
    p.set_defaults(func=cmd_eval)

    p = sub.add_parser("ocr")
    p.set_defaults(func=None)
    p = sub.add_parser("dataset")
    p.set_defaults(func=None)

    a, rest = ap.parse_known_args(argv)
    if a.cmd == "ocr":
        from .ocr_cache import main as m

        return m(rest)
    if a.cmd == "dataset":
        from .dataset import main as m

        return m(rest)
    if rest:
        ap.error(f"tham số lạ: {rest}")
    a.func(a)


if __name__ == "__main__":
    main()
