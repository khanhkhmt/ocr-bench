"""python -m postcorrect <lệnh>

  dataset muharaf      dựng bộ đánh giá công khai (dataset.py)
  ocr                  chạy dots.mocr lưu cache OCR (ocr_cache.py; python của venv dots)
  correct-cache        sửa hàng loạt từ cache OCR  (một tiến trình mỗi GPU: --device i --shard i/n)
  correct-text         sửa một văn bản (file hoặc stdin) → JSON
  correct-image        ảnh → dots (GPU --ocr-device) → LLM (GPU --llm-device) → JSON  (venv dots)
  lexicon-coverage     độ phủ ứng viên của từ điển trên các từ sai-gần-đúng (hướng 'LLM chỉ kiểm chứng')
  lm-prefer            chẩn đoán: cho SẴN từ đúng, LM có nhận ra không (cận trên của 'ứng viên + chấm LM')
  oracle               trần: CER nếu sửa HOÀN HẢO mọi từ trong tầm chốt chặn
  vote                 đồng thuận: chỉ nhận sửa nhiều lượt chạy (khác prompt / khác model) cùng đề xuất
  make-shots           tạo ví dụ few-shot THẬT từ trang dev ngoài tập chấm (cho biến thể +rs)
  refilter             áp lại chốt chặn (ngưỡng khác) lên đầu ra thô đã lưu, không cần GPU
  analyze              tín hiệu nào khoanh đúng từ sai-gần-đúng (dots ngần ngừ / LM ngạc nhiên) + trần ứng viên
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

from .detect import canon_signal
from .guard import GuardConfig
from .pipeline import PageText, Settings, correct_pages, page_text_from_cells
from .text import split_words


def add_model_args(ap):
    ap.add_argument("--model", default="Qwen/Qwen3-8B", help="id Hugging Face của LLM (chạy cục bộ)")
    ap.add_argument("--quant", choices=["nf4", "fp16"], default="nf4")
    ap.add_argument("--strategy", choices=["A", "B", "C", "D"], default="A",
                    help="A viết lại chunk | B khoanh từ lỗi (JSON) | C viết lại, chỉ đổi từ NLL cao | D ứng viên từ điển + LM kiểm chứng")
    ap.add_argument("--lexicon", help="từ điển tần suất (JSON) cho chiến lược D — python -m postcorrect.lexicon")
    ap.add_argument("--d-tau", type=float, default=3.0)
    ap.add_argument("--d-margin", type=float, default=0.5)
    ap.add_argument("--fewshot", action="store_true")
    ap.add_argument("--chunk-chars", type=int, default=700)
    ap.add_argument("--flag-signal", default="nll_sum", help="nll_sum | nll_max | dots_lp | dots_lp+nll_sum | dots_lp+nll_max")
    ap.add_argument("--flag-frac", type=float, default=0.3)
    ap.add_argument("--flag-min", type=float, help="điểm tối thiểu để được đánh dấu (mặc định theo tín hiệu)")
    ap.add_argument("--nll-cache", help="thư mục cache NLL từng chunk (dùng lại giữa các lần chạy)")
    ap.add_argument("--max-char-edit", type=int, default=2)
    ap.add_argument("--max-edit-ratio", type=float, default=0.35)
    ap.add_argument("--max-diacritic-ratio", type=float, default=0.05)
    ap.add_argument("--no-block-convention", action="store_true")
    ap.add_argument("--tag", default="")
    ap.add_argument("--max-batch", type=int, default=8)


def settings_from(a) -> Settings:
    return Settings(strategy=a.strategy, chunk_chars=a.chunk_chars, fewshot=a.fewshot, flag_frac=a.flag_frac,
                    flag_min=a.flag_min, flag_signal=canon_signal(a.flag_signal), tag=a.tag,
                    d_tau=getattr(a, "d_tau", 3.0), d_margin=getattr(a, "d_margin", 0.5),
                    guard=GuardConfig(max_char_edit=a.max_char_edit, max_edit_ratio=a.max_edit_ratio,
                                      max_diacritic_ratio=a.max_diacritic_ratio, block_convention=not a.no_block_convention))


def load_backend(a, device: int):
    from .backend import DummyBackend, HFBackend

    if a.model == "dummy":  # chạy khô luồng dữ liệu, không model: không sửa gì, mọi từ NLL thấp
        b = DummyBackend()
        b.load_seconds = 0.0
        return b
    return HFBackend(a.model, device=device, quant=a.quant, max_batch=a.max_batch, nll_cache=getattr(a, "nll_cache", None))


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
            try:
                from .dots_conf import page_word_conf

                conf = page_word_conf(rec)
                p.dots = conf if len(conf) == len(split_words(p.text)) else None
            except Exception:  # thiếu / hỏng thống kê token → vẫn sửa được, chỉ không có tín hiệu dots
                p.dots = None
            pages.append(p)
    return pages


def parse_variant(v: str) -> tuple[str, str | None, str, str]:
    """Cú pháp biến thể: CHIẾN_LƯỢC[=TÍN_HIỆU][@KIỂU][+fs|+rs]. Vd. "A", "B+fs", "C=nll_sum", "C=dots_lp+nll_sum+fs", "A@assert+rs".
    +fs = ví dụ few-shot TỔNG HỢP; +rs = ví dụ THẬT trong miền (--shots-file); =TÍN_HIỆU chỉ dùng cho C (xem detect.SIGNALS);
    @KIỂU = cons (mặc định) | assert. Trả về (chiến lược, tín hiệu, "" | "fs" | "rs", kiểu)."""
    shots = ""
    for suffix in ("+fs", "+rs"):
        if v.endswith(suffix):
            shots, v = suffix[1:], v[:-3]
    core, _, style = v.partition("@")
    strategy, _, signal = core.partition("=")
    if strategy not in ("A", "B", "C", "D") or style not in ("", "cons", "assert"):
        raise ValueError(f"biến thể không hợp lệ: {v!r}")
    return strategy, (canon_signal(signal) if signal else None), shots, style or "cons"


def _run_variant(backend, a, ids: list[str], st: Settings, out: Path, shots: list[dict] | None = None, lexicon=None) -> None:
    out.mkdir(parents=True, exist_ok=True)
    pages = load_ocr_pages(Path(a.ocr), [i for i in ids if not (out / f"{i}.json").exists()])
    print(f"[{st.tag or st.strategy}] {len(ids)} trang thuộc phần này, cần chạy {len(pages)} "
          f"(còn lại đã có kết quả / OCR lỗi) → {out}", flush=True)
    if not pages:
        return
    meta = {"model": a.model, "quant": a.quant, "device": a.device, "shard": a.shard, "settings": st.as_dict(),
            "load_seconds": round(getattr(backend, "load_seconds", 0.0), 1), "groups": [], "pages_done": 0}
    t_all = time.perf_counter()
    for g in range(0, len(pages), a.group):
        grp = pages[g:g + a.group]
        s0 = (backend.stats.seconds, backend.stats.prompt_tokens, backend.stats.new_tokens)
        t = time.perf_counter()
        results = correct_pages(grp, backend, st, shots, lexicon)
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
        print(f"  [{st.tag or st.strategy}] {meta['pages_done']}/{len(pages)} trang | {dt:.0f}s | "
              f"{sum(len(r['edits']) for r in results)} sửa nhận / {sum(len(r['rejected']) for r in results)} từ chối",
              flush=True)


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
    variants = [v.strip() for v in a.variants.split(",")] if a.variants else [a.strategy + ("+fs" if a.fewshot else "")]
    for v in variants:
        parse_variant(v)  # báo lỗi cú pháp trước khi tốn thời gian nạp model
    lexicon = None
    if any(parse_variant(v)[0] == "D" for v in variants):
        if not a.lexicon:
            raise SystemExit("chiến lược D cần --lexicon")
        from .lexicon import Lexicon

        lexicon = Lexicon(a.lexicon)
    backend = load_backend(a, a.device)
    print(f"nạp {a.model} ({a.quant}) trên cuda:{a.device}: {getattr(backend, 'load_seconds', 0):.0f}s", flush=True)
    for v in variants:  # nhiều biến thể dùng chung MỘT lần nạp model
        st = settings_from(a)
        st.strategy, signal, shots_mode, st.style = parse_variant(v)
        st.fewshot, st.real_shots = shots_mode == "fs", shots_mode == "rs"
        if st.real_shots:
            if not a.shots_file:
                raise SystemExit("biến thể +rs cần --shots-file (tạo bằng: python -m postcorrect make-shots ...)")
            st.shots_tag = Path(a.shots_file).name
        if signal:
            st.flag_signal = signal
        st.tag = v
        tag_dir = v.replace("=", "_").replace("+", "_").replace("@", "_")
        _run_variant(backend, a, ids, st, Path(f"{a.out}__{tag_dir}") if a.variants else Path(a.out),
                     json.loads(Path(a.shots_file).read_text(encoding="utf-8")) if st.real_shots else None,
                     lexicon)
    backend.close()


# ---------------------------------------------------------------- correct-text / correct-image
def cmd_correct_text(a):
    text = sys.stdin.read() if a.input == "-" else Path(a.input).read_text(encoding="utf-8")
    backend = load_backend(a, a.device)
    res = correct_pages([PageText("text", text.strip(), [])], backend, settings_from(a))[0]
    print(json.dumps(res, ensure_ascii=False, indent=1))


def pick_devices(ocr_dev: int, llm_dev: int, n_gpu: int) -> tuple[int, int]:
    """Máy chỉ có 1 GPU: cả OCR lẫn LLM về cuda:0 (khi đó dots chạy trước rồi PHẢI được giải phóng: ~14 GiB + ~6 GiB không
    vừa một card 15 GiB)."""
    if n_gpu <= 0:
        raise RuntimeError("không thấy GPU CUDA")
    return min(ocr_dev, n_gpu - 1), min(llm_dev, n_gpu - 1)


def cmd_correct_image(a):
    import gc

    import torch
    from PIL import Image, ImageOps

    from .ocr_cache import ROOT, make_adapter

    od, ld = pick_devices(a.ocr_device, a.llm_device, torch.cuda.device_count())
    adapter, _ = make_adapter(Path(a.config or ROOT / "inference/config.yaml"), a.ocr_model,
                              {"device_map": {"": f"cuda:{od}"}})
    adapter.load()
    img = ImageOps.exif_transpose(Image.open(a.image)).convert("RGB")
    t = time.perf_counter()
    ocr = adapter.parse_image(img)
    ocr_s = time.perf_counter() - t
    page = page_text_from_cells(Path(a.image).stem, ocr["cells"])
    if od == ld:  # một card: trả VRAM của dots trước khi nạp LLM
        adapter.close()
        del adapter
        gc.collect()
        torch.cuda.empty_cache()
    backend = load_backend(a, ld)
    res = correct_pages([page], backend, settings_from(a))[0]
    res["ocr"] = {"seconds": round(ocr_s, 1), "flags": {k: v for k, v in ocr["extra"].items() if k != "blocks"},
                  "devices": {"ocr": od, "llm": ld}}
    print(json.dumps(res, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- analyze
def cmd_analyze(a):
    """Tín hiệu nào khoanh đúng từ sai-gần-đúng? (dots ngần ngừ / LM ngạc nhiên) + trần ứng viên từ phương án của dots."""
    from collections import Counter, defaultdict

    from .analysis import alt_oracle, auroc, bootstrap_auroc, word_rows
    from .chunking import chunk_text
    from .ocr_cache import load_manifest
    from .text import split_words

    man = {r["id"]: r for r in load_manifest(Path(a.manifest)) if not a.split or r.get("split") == a.split}
    recs = {}
    for i in man:
        f = Path(a.ocr) / f"{i}.json"
        if f.exists():
            r = json.loads(f.read_text(encoding="utf-8"))
            if not r.get("error") and r.get("cells"):
                recs[i] = r
    rows_by_page, oracle = {}, Counter()
    for i, rec in recs.items():
        page, rows = word_rows(rec, man[i]["gt"], a.max_char_edit)
        rows_by_page[i] = (page, rows)
        oracle.update(alt_oracle(rec, man[i]["gt"], a.max_char_edit))
    if a.model:
        backend = load_backend(a, a.device)
        for i, (page, rows) in rows_by_page.items():
            for ch in chunk_text(page.text, a.chunk_chars):
                for k, w in enumerate(backend.nll_words(ch.text)):
                    rows[ch.first_word + k].signals["nll_max"] = w.max
                    rows[ch.first_word + k].signals["nll_sum"] = w.total
        backend.close()
    for page, rows in rows_by_page.values():  # tổ hợp: trung bình hạng phân vị (trong trang) của hai tín hiệu
        for k in ("dots_lp", "nll_max", "nll_sum"):
            have = [r for r in rows if k in r.signals]
            for rank, r in enumerate(sorted(have, key=lambda r: r.signals[k])):
                r.signals[f"_r_{k}"] = rank / max(1, len(have) - 1)
        for r in rows:
            for other in ("nll_max", "nll_sum"):
                if "_r_dots_lp" in r.signals and f"_r_{other}" in r.signals:
                    r.signals[f"dots_lp+{other}"] = (r.signals["_r_dots_lp"] + r.signals[f"_r_{other}"]) / 2
    sigs = sorted({k for _, rows in rows_by_page.values() for r in rows for k in r.signals if not k.startswith("_")})
    cnt = Counter(r.label for _, rows in rows_by_page.values() for r in rows)
    n = sum(cnt.values())
    print(f"# Phân tích tín hiệu — {len(rows_by_page)} trang, {n} từ OCR: đúng {cnt['ok']} ({cnt['ok'] / n:.1%}), "
          f"sai-gần-đúng (≤{a.max_char_edit} ký tự) {cnt['near']} ({cnt['near'] / n:.1%}), sai-xa {cnt['far']}, thừa {cnt['extra']}\n")
    print("Phân biệt từ SAI-GẦN-ĐÚNG (dương) với từ ĐÚNG (âm); từ sai-xa / thừa bỏ khỏi bài toán này.\n")
    print("| tín hiệu | AUROC [KTC 95%] | recall khi đánh dấu 20% từ | precision@20% | recall @30% | precision @30% |")
    print("|---|---|---|---|---|---|")
    for k in sigs:
        by_page = defaultdict(list)
        for pid, (_, rows) in rows_by_page.items():
            for r in rows:
                if k in r.signals and r.label in ("ok", "near"):
                    by_page[pid].append((r.signals[k], int(r.label == "near")))
        flat = [x for v in by_page.values() for x in v]
        if not flat:
            continue
        pos = [s for s, y in flat if y]
        neg = [s for s, y in flat if not y]
        lo, hi = bootstrap_auroc(by_page, n=a.boot)
        cells = []
        for frac in (0.2, 0.3):
            top = sorted(flat, key=lambda x: -x[0])[: int(frac * len(flat))]
            tp = sum(y for _, y in top)
            cells += [f"{tp / max(1, len(pos)):.2f}", f"{tp / max(1, len(top)):.2f}"]
        print(f"| {k} | {auroc(pos, neg):.3f} [{lo:.3f}, {hi:.3f}] | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    base = cnt["near"] / max(1, cnt["near"] + cnt["ok"])
    print(f"\n(Tỉ lệ nền: {base:.1%} số từ xét là sai-gần-đúng → precision ngẫu nhiên = {base:.2f}, AUROC ngẫu nhiên = 0.5)")
    if oracle["near"]:
        print(f"\nTrần ứng viên từ phương án của dots: trong {oracle['near']} từ sai-gần-đúng, thay MỘT token bằng phương án top-3 "
              f"cho đúng từ đáp án ở {oracle['covered']} từ ({oracle['covered'] / oracle['near']:.1%}); chỉ riêng phương án thứ 2: "
              f"{oracle['covered_top2']} ({oracle['covered_top2'] / oracle['near']:.1%}).")

# ---------------------------------------------------------------- make-shots
def cmd_make_shots(a):
    """Tạo ví dụ few-shot THẬT từ các trang dev KHÔNG nằm trong tập đang chấm (--skip: bỏ N trang dev đầu tiên)."""
    from .ocr_cache import load_manifest
    from .shots import make_shots

    rows = [r for r in load_manifest(Path(a.manifest)) if r.get("split") == a.split]
    pool = rows[a.skip:]
    shots = make_shots(Path(a.ocr), {r["id"]: r["gt"] for r in pool}, [r["id"] for r in pool], a.n_fix, a.n_clean,
                       a.max_chars, a.min_fix)
    Path(a.out).write_text(json.dumps(shots, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(shots)} ví dụ từ {len(pool)} trang {a.split} (bỏ {a.skip} trang đầu để chống rò rỉ) → {a.out}")
    for s in shots:
        print(f"  {s['id']}: {len(s['src'])} ký tự, {len(s['fixes'])} sửa: {s['fixes'][:6]}")


# ---------------------------------------------------------------- refilter
def cmd_refilter(a):
    """Áp lại chốt chặn (ngưỡng khác) lên đầu ra thô đã lưu → thư mục kết quả mới. Không cần GPU."""
    from .pipeline import refilter_result

    src, dst = Path(a.run), Path(a.out)
    dst.mkdir(parents=True, exist_ok=True)
    guard = GuardConfig(max_char_edit=a.max_char_edit, max_char_ratio=a.max_char_ratio, max_edit_ratio=a.max_edit_ratio,
                        max_drift=a.max_drift, allow_split_merge=not a.no_split_merge,
                        block_convention=not a.no_block_convention, max_diacritic_ratio=a.max_diacritic_ratio)
    n = 0
    for f in sorted(src.glob("*.json")):
        if f.name.startswith("run_meta"):
            (dst / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
            continue
        res = refilter_result(json.loads(f.read_text(encoding="utf-8")), guard, a.d_tau, a.d_margin)
        (dst / f.name).write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
        n += 1
    print(f"đã áp lại chốt chặn cho {n} trang → {dst}")


# ---------------------------------------------------------------- vote
def cmd_vote(a):
    """Đồng thuận giữa các lượt chạy (khác prompt hoặc khác model): chỉ nhận sửa có ≥ --min-votes lượt cùng đề xuất."""
    from .pipeline import vote_results

    dirs = [Path(d) for d in a.runs]
    ids = sorted(set.intersection(*({f.stem for f in d.glob("*.json") if not f.name.startswith("run_meta")} for d in dirs)))
    dst = Path(a.out)
    dst.mkdir(parents=True, exist_ok=True)
    for i in ids:
        res = vote_results([json.loads((d / f"{i}.json").read_text(encoding="utf-8")) for d in dirs], a.min_votes)
        (dst / f"{i}.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    print(f"đồng thuận {a.min_votes}/{len(dirs)} cho {len(ids)} trang chung → {dst}")


# ---------------------------------------------------------------- lexicon-coverage
def cmd_lexicon_coverage(a):
    """Độ phủ ứng viên của từ điển trên các từ sai-gần-đúng: từ đáp án có trong từ điển không, có bao nhiêu ứng viên, xếp hạng ra sao."""
    from collections import Counter

    from .analysis import word_rows
    from .evaluate import align, norm_w
    from .lexicon import Lexicon
    from .ocr_cache import load_manifest
    from .text import norm_word, split_words

    lex = Lexicon(a.lexicon)
    man = [r for r in load_manifest(Path(a.manifest)) if not a.split or r.get("split") == a.split][: a.limit_pages or None]
    n_near = in_lex = in_cand = top1 = top5 = 0
    ncands, oov = [], Counter()
    for r in man:
        f = Path(a.ocr) / f"{r['id']}.json"
        if not f.exists():
            continue
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("error") or not rec.get("cells"):
            continue
        page, rows = word_rows(rec, r["gt"], a.max_char_edit)
        words, gw = split_words(page.text), split_words(r["gt"])
        al = align(words, gw)
        for row in rows:
            w = row.word
            if row.label in ("ok", "near", "far"):
                oov[(row.label, norm_word(w) in lex.set)] += 1
            if row.label != "near" or al.pair[row.index] is None:
                continue
            gold = norm_word(gw[al.pair[row.index]])
            cands = lex.candidates(w, a.max_char_edit, limit=200)
            n_near += 1
            in_lex += gold in lex.set
            names = [c[0] for c in cands]
            ncands.append(len(cands))
            if gold in names:
                in_cand += 1
                rank = names.index(gold)
                top1 += rank == 0
                top5 += rank < 5
    print(f"# Độ phủ từ điển ({len(lex.words)} từ) trên {n_near} từ sai-gần-đúng của {a.split or 'tất cả'}\n")
    print(f"- Từ đáp án CÓ trong từ điển: {in_lex / max(1, n_near):.1%} (= trần recall ứng viên; thiếu = từ địa phương / cổ / tên riêng)")
    print(f"- Từ đáp án nằm trong ứng viên cách ≤ {a.max_char_edit} ký tự: {in_cand / max(1, n_near):.1%}; xếp hạng top-1 / top-5 chỉ bằng (khoảng cách, tần suất): "
          f"{top1 / max(1, n_near):.1%} / {top5 / max(1, n_near):.1%}")
    srt = sorted(ncands)
    print(f"- Số ứng viên mỗi từ: trung vị {srt[len(srt) // 2] if srt else 0}, p90 {srt[int(.9 * (len(srt) - 1))] if srt else 0}, tối đa {srt[-1] if srt else 0}")
    for lab in ("ok", "near", "far"):
        tot = oov[(lab, True)] + oov[(lab, False)]
        print(f"- Từ OCR nhãn '{lab}': {oov[(lab, False)] / max(1, tot):.1%} NGOÀI từ điển (OOV) — tín hiệu 'từ nghi lỗi' miễn phí")


# ---------------------------------------------------------------- lm-prefer
def cmd_lm_prefer(a):
    """Chẩn đoán: cho SẴN từ đúng, LM có chấm văn bản chứa từ đúng tốt hơn văn bản chứa từ OCR không? (cận trên của 'ứng viên + chấm LM')"""
    from .lm_prefer import collect, roc_table
    from .ocr_cache import load_manifest

    man = [r for r in load_manifest(Path(a.manifest)) if not a.split or r.get("split") == a.split][: a.limit_pages or None]
    recs, gts = {}, {}
    for r in man:
        f = Path(a.ocr) / f"{r['id']}.json"
        if f.exists():
            rec = json.loads(f.read_text(encoding="utf-8"))
            if not rec.get("error") and rec.get("cells"):
                recs[r["id"]], gts[r["id"]] = rec, r["gt"]
    backend = load_backend(a, a.device)
    pos, neg = collect(backend, recs, gts, a.n, a.n, a.seed, a.max_char_edit)
    backend.close()
    pm = sum(pos) / max(1, len(pos))
    print(f"# LM có nhận ra từ đúng không? — {a.model}, {len(recs)} trang, {len(pos)} từ sai-gần-đúng + {len(neg)} đối chứng\n")
    print(f"- LM thích văn bản chứa TỪ ĐÚNG hơn văn bản chứa từ OCR ở {sum(1 for d in pos if d > 0) / max(1, len(pos)):.1%} số từ sai-gần-đúng "
          f"(Δ trung bình {pm:+.2f} nat).")
    print(f"- Đối chứng: LM thích từ đúng gốc hơn bản bị làm nhiễu ở {sum(1 for d in neg if d < 0) / max(1, len(neg)):.1%} số từ đúng.\n")
    print("| ngưỡng τ (nat) | nhận đúng (TPR) | nhận nhầm từ đúng (FPR) | precision |\n|---|---|---|---|")
    for t, tpr, fpr, prec in roc_table(pos, neg):
        print(f"| {t:.0f} | {tpr:.1%} | {fpr:.1%} | {prec:.1%} |")


# ---------------------------------------------------------------- oracle
def cmd_oracle(a):
    """Trần: CER sau khi sửa HOÀN HẢO mọi từ trong tầm chốt chặn (k ký tự). Cho biết nới chốt chặn có đáng không."""
    from .analysis import oracle_edits
    from .evaluate import page_metrics, summarize
    from .ocr_cache import load_manifest

    man = {r["id"]: r for r in load_manifest(Path(a.manifest)) if not a.split or r.get("split") == a.split}
    recs = []
    for i in man:
        f = Path(a.ocr) / f"{i}.json"
        if f.exists():
            r = json.loads(f.read_text(encoding="utf-8"))
            if not r.get("error") and r.get("cells"):
                recs.append(r)
    print(f"# Trần sửa hoàn hảo — {len(recs)} trang ({a.split or 'tất cả'})\n")
    for name in ("strict", "lenient"):
        print(f"## {name}\n\n| tầm với (ký tự) | CER trước | CER sau (trần) | ΔCER (điểm %) | WER sau (trần) | từ sửa được |\n|---|---|---|---|---|---|")
        for k in (1, 2, 3, 4):
            rows = []
            for r in recs:
                orig, corr, edits = oracle_edits(r, man[r["id"]]["gt"], k, name == "lenient")
                rows.append(page_metrics(man[r["id"]]["gt"], orig, corr, edits, None, k))
            s = summarize(rows, name)
            print(f"| {k} | {s['cer_before']:.4f} | {s['cer_after']:.4f} | {s['cer_delta'] * 100:+.2f} | {s['wer_after']:.4f} | {s['edits']} |")
        print()


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
    if a.subset != "all":  # tách nhóm trang dots "đọc thật" khỏi nhóm dots BỊA (tashkeel dày): hiệu quả sửa rất khác nhau
        from .guard import diacritic_ratio
        from .text import split_words

        want_suspect = a.subset == "suspect"
        for lab in runs:
            runs[lab] = {i: r for i, r in runs[lab].items()
                         if (diacritic_ratio(split_words(r["original"])) > 0.10) == want_suspect}
    common = sorted(set.intersection(*(set(v) for v in runs.values()))) if runs else []
    print(f"# Đánh giá — {len(common)} trang chung của {len(runs)} lượt chạy"
          f"{' (' + a.split + ')' if a.split else ''}{' · nhóm ' + a.subset if a.subset != 'all' else ''}\n")
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
        print("| lượt chạy | CER sau | ΔCER (điểm %) [KTC 95%] | WER sau | số sửa | precision | sửa nhầm (từ đúng bị đổi) | "
              "sửa đúng hẳn | recall (trong tầm với / tất cả lỗi) | giây GPU/trang |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for lab, rows in table.items():
            s = summarize(rows, name)
            meta = _meta_seconds(Path(dict(map(_label_path, a.runs))[lab]), len(runs[lab]))
            print(f"| {lab} | {s['cer_after']:.4f} | {s['cer_delta'] * 100:+.2f} {fmt_ci(rows, lambda x: x['cer_delta'], name)} | "
                  f"{s['wer_after']:.4f} | {s['edits']} | {s['precision']:.2f} | {s['harm_rate'] * 100:.2f}% ({s['harm']}) | "
                  f"{s['fixed']} | {s['fix_rate_of_reach']:.1%} / {s['recall_all']:.1%} | {meta} |")
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
        s = summarize(rows)
        if s.get("flags"):
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
    p.add_argument("--variants", help="vd. A,B,C=nll_sum@assert,A+rs — chạy lần lượt trong một tiến trình; kết quả ở <out>__<biến thể>")
    p.add_argument("--shots-file", help="JSON ví dụ THẬT trong miền (cho biến thể +rs), tạo bằng make-shots")
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
    p.add_argument("--subset", choices=["all", "clean", "suspect"], default="all",
                   help="clean = trang có tashkeel ≤ 10% (dots đọc thật); suspect = tashkeel > 10% (nghi dots bịa)")
    p.add_argument("--json")
    p.set_defaults(func=cmd_eval)

    p = sub.add_parser("make-shots")
    p.add_argument("--ocr", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--split", choices=["dev", "holdout"], default="dev")
    p.add_argument("--skip", type=int, default=24, help="bỏ N trang đầu của split (chính là tập đang chấm) khỏi nguồn ví dụ")
    p.add_argument("--n-fix", type=int, default=2)
    p.add_argument("--n-clean", type=int, default=1)
    p.add_argument("--max-chars", type=int, default=320)
    p.add_argument("--min-fix", type=int, default=3)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_make_shots)

    p = sub.add_parser("refilter")
    p.add_argument("--run", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--max-char-edit", type=int, default=2)
    p.add_argument("--max-char-ratio", type=float, default=0.5)
    p.add_argument("--max-edit-ratio", type=float, default=0.35)
    p.add_argument("--max-drift", type=float, default=0.10)
    p.add_argument("--no-split-merge", action="store_true")
    p.add_argument("--no-block-convention", action="store_true", help="cho phép sửa chỉ khác quy ước (hamza, ى/ي, ة/ه)")
    p.add_argument("--max-diacritic-ratio", type=float, default=0.05, help="bỏ chunk có tashkeel dày hơn mức này (0 = tắt)")
    p.add_argument("--d-tau", type=float, help="(chiến lược D) ngưỡng Δ NLL mới")
    p.add_argument("--d-margin", type=float, help="(chiến lược D) lề so với ứng viên thứ hai mới")
    p.set_defaults(func=cmd_refilter)

    p = sub.add_parser("lexicon-coverage")
    p.add_argument("--lexicon", required=True)
    p.add_argument("--ocr", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--split", choices=["dev", "holdout"])
    p.add_argument("--limit-pages", type=int)
    p.add_argument("--max-char-edit", type=int, default=2)
    p.set_defaults(func=cmd_lexicon_coverage)

    p = sub.add_parser("lm-prefer")
    p.add_argument("--ocr", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--split", choices=["dev", "holdout"])
    p.add_argument("--limit-pages", type=int)
    p.add_argument("--n", type=int, default=400, help="số từ dương và số đối chứng")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", type=int, default=0)
    add_model_args(p)
    p.set_defaults(func=cmd_lm_prefer)

    p = sub.add_parser("oracle")
    p.add_argument("--ocr", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--split", choices=["dev", "holdout"])
    p.set_defaults(func=cmd_oracle)

    p = sub.add_parser("vote")
    p.add_argument("--runs", nargs="+", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--min-votes", type=int, default=2)
    p.set_defaults(func=cmd_vote)

    p = sub.add_parser("analyze")
    p.add_argument("--ocr", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--split", choices=["dev", "holdout"])
    p.add_argument("--device", type=int, default=0)
    p.add_argument("--boot", type=int, default=300)
    p.add_argument("--no-model", dest="model_off", action="store_true", help="chỉ tín hiệu của dots, không nạp LLM")
    add_model_args(p)
    p.set_defaults(func=cmd_analyze)

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
    if getattr(a, "model_off", False):
        a.model = None
    a.func(a)


if __name__ == "__main__":
    main()
