"""Chạy dots.mocr trên một manifest và LƯU KẾT QUẢ THÔ (mỗi trang một file JSON) — "OCR một lần, thử LLM nhiều lần".

    # một tiến trình mỗi GPU (mỗi card T4 chứa trọn một bản dots ở 5 MP; không chung card với LLM):
    CUDA_VISIBLE_DEVICES=0 python -m postcorrect.ocr_cache --manifest M --out O --worker gpu0 &
    CUDA_VISIBLE_DEVICES=1 python -m postcorrect.ocr_cache --manifest M --out O --worker gpu1 &

Hai tiến trình chia việc động bằng file "claim" (O_EXCL) nên trang dài không làm một card ngồi chờ. Chạy lại lệnh
thì bỏ qua trang đã xong (resume sau khi sập); --retry-errors để chạy lại trang lỗi. Phải chạy bằng python của venv
dots (transformers==4.56.1), thêm PYTHONPATH=<repo> nếu postcorrect chưa được cài.

Tham số dots lấy từ inference/config.yaml (đúng cấu hình web demo đã chỉnh cho giấy tờ cũ), chỉ khác: min/max_pixels
(dải 4,6–5,0 MP — ảnh to hơn hết VRAM T4) và max_time. Mỗi file ghi: response (chuỗi JSON thô của dots), cells (khối đã
hậu xử lý: bbox, category, text), md, extra (cờ lặp / cắt…), token_stats (id, log-prob, lề, entropy, mảnh token).
"""

from __future__ import annotations

import argparse
import json
import os
import time
import traceback
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
# 4,6–5,0 MP: không vượt cấu hình 5 MP đã kiểm chứng (6 MP → hết VRAM T4, đã thấy khi chạy thử); min/max cách nhau
# ~8% vì max_pixels = min_pixels làm bbox lệch (ghi chú trong inference/config.yaml)
DEFAULT_OVERRIDES = {"min_pixels": 4_600_000, "max_pixels": 5_000_000, "max_time": 420}


def load_manifest(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    for r in rows:
        r["_image_path"] = str((path.parent / r["image"]).resolve())
    return rows


def claim(claims: Path, item_id: str) -> bool:
    try:
        fd = os.open(claims / item_id, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False


def make_adapter(config: Path, model: str, overrides: dict):
    from ocrbench.adapters import create_adapter
    from ocrbench.config import load_config
    from ocrbench.convert import merge_params

    spec = load_config(config).model(model)
    params = merge_params(spec.params, {**DEFAULT_OVERRIDES, **overrides, "blocks_with_text": True})
    adapter = create_adapter("postcorrect.dots_logprob:DotsLogprobAdapter", params)
    return adapter, params


def run(manifest: Path, out: Path, config: Path, model: str = "dots_mocr", worker: str = "w0", split: str | None = None,
        limit: int | None = None, retry_errors: bool = False, overrides: dict | None = None) -> None:
    import torch

    from ocrbench.preprocess import config_of, preprocess

    rows = load_manifest(manifest)
    if split:
        rows = [r for r in rows if r.get("split") == split]
    if limit:
        rows = rows[:limit]
    out.mkdir(parents=True, exist_ok=True)
    claims = out / ".claims"
    claims.mkdir(exist_ok=True)
    for c in claims.iterdir():  # claim còn sót của lần chạy bị ngắt (không có kết quả) → trả lại hàng đợi
        f = out / f"{c.name}.json"
        if not f.exists() or (retry_errors and json.loads(f.read_text(encoding="utf-8")).get("error")):
            if retry_errors and f.exists():
                f.unlink()
            c.unlink()
    todo = [r for r in rows if not (out / f"{r['id']}.json").exists()]
    print(f"[{worker}] {len(rows)} trang trong manifest, còn {len(todo)} chưa có kết quả", flush=True)
    if not todo:
        return
    adapter, params = make_adapter(config, model, overrides or {})
    t = time.perf_counter()
    adapter.load()
    print(f"[{worker}] nạp model {time.perf_counter() - t:.0f}s | max_pixels={params.get('max_pixels')} "
          f"min_pixels={params.get('min_pixels')} max_time={params.get('max_time')}", flush=True)
    pre_cfg, max_side = config_of(params.get("preprocess")), params.get("max_image_side")
    done = 0
    for r in todo:
        if not claim(claims, r["id"]):
            continue
        rec = {"id": r["id"], "split": r.get("split"), "doc_id": r.get("doc_id"), "model": model, "worker": worker,
               "image": r["image"]}
        t0 = time.perf_counter()
        try:
            img = ImageOps.exif_transpose(Image.open(r["_image_path"])).convert("RGB")
            if max_side and max(img.size) > max_side:
                img.thumbnail((max_side, max_side), Image.LANCZOS)
            if pre_cfg:
                img, _ = preprocess(img, pre_cfg)
            res = adapter.parse_image(img)
            rec.update(image_size=list(img.size), response=res["response"], filtered=res["filtered"],
                       cells=res["cells"], md=res["md"], extra={k: v for k, v in res["extra"].items() if k != "blocks"},
                       token_stats=res.get("token_stats"), error=None)
        except Exception as e:  # trang hỏng không được làm chết cả hàng đợi
            rec.update(error=f"{type(e).__name__}: {str(e)[:300]}", trace=traceback.format_exc()[-1500:])
            torch.cuda.empty_cache()
        rec["seconds"] = round(time.perf_counter() - t0, 1)
        tmp = out / f".{r['id']}.tmp"
        tmp.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        tmp.replace(out / f"{r['id']}.json")
        done += 1
        n_cells = len(rec.get("cells") or [])
        print(f"[{worker}] {r['id']} {rec['seconds']:6.1f}s | khối {n_cells:3d} | token {len((rec.get('token_stats') or {}).get('ids', [])):5d}"
              f" | {rec.get('error') or ''} {','.join(k for k in ('stopped_loop', 'hit_max_tokens', 'hit_max_time') if (rec.get('extra') or {}).get(k))}",
              flush=True)
        torch.cuda.empty_cache()
    print(f"[{worker}] xong {done} trang", flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default=str(ROOT / "inference/config.yaml"))
    ap.add_argument("--model", default="dots_mocr")
    ap.add_argument("--worker", default="w0")
    ap.add_argument("--split", choices=["dev", "holdout"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--retry-errors", action="store_true")
    ap.add_argument("--set", action="append", default=[], help="ghi đè tham số dots, vd. --set max_time=300")
    a = ap.parse_args(argv)
    ov = {}
    for kv in a.set:
        k, v = kv.split("=", 1)
        ov[k] = json.loads(v) if v[:1] in "0123456789[{\"" or v in ("true", "false", "null") else v
    run(Path(a.manifest), Path(a.out), Path(a.config), a.model, a.worker, a.split, a.limit, a.retry_errors, ov)


if __name__ == "__main__":
    main()
