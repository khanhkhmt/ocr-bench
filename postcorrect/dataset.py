"""Dựng bộ đánh giá công khai: các trang thư viết tay tiếng Ả Rập (Muharaf) kèm phiên âm của chuyên gia.

Lý do dùng: chưa có dữ liệu thật của người dùng trên máy. Muharaf là bản thảo viết tay thế kỷ 20 (thư, ghi chép; tiếng
địa phương + chính tả cũ) — bài thử khó cho nguy cơ "LLM sửa quá tay" (đổi từ địa phương / cổ thành chuẩn).

    python -m postcorrect.dataset muharaf --out /kaggle/working/pc_eval/muharaf --n 100

Ra: <out>/images/*.jpg (bytes gốc, không mã hoá lại), <out>/manifest.jsonl (cùng khuôn manifest của ocrbench:
id, image, category, gt, doc_id, split=dev|holdout), <out>/DATASET_CARD.md. Dữ liệu nằm NGOÀI repo, không commit.

Chia dev / holdout theo TÀI LIỆU (băm sha1 của doc_id), mỗi tài liệu tối đa 1 trang → trang cùng một lá thư không
rơi vào hai phía (không rò rỉ nét chữ / từ vựng). Holdout chỉ dùng một lần cho số liệu cuối.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import random
import re
from pathlib import Path

HF_ID = "TheRealOKAI/muharaf-public-pages"
_AR = re.compile(r"[؀-ۿ]")


def doc_id_of(page_id: str) -> str:
    """Bỏ hậu tố số trang (…_1, …_2_1) → mã tài liệu."""
    return re.sub(r"(_\d+)+$", "", page_id)


def split_of(doc_id: str) -> str:
    return "holdout" if int(hashlib.sha1(doc_id.encode("utf-8")).hexdigest()[:8], 16) % 2 else "dev"


def arabic_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    return sum(1 for c in letters if _AR.match(c)) / max(1, len(letters))


def eligible(text: str, min_chars=250, max_chars=1800, min_lines=5, max_lines=30, min_ar=0.85) -> bool:
    lines = text.count("\n") + 1
    return min_chars <= len(text) <= max_chars and min_lines <= lines <= max_lines and arabic_ratio(text) >= min_ar


def build_muharaf(out: Path, n: int = 100, seed: int = 13, min_mp: float = 2.0, max_mp: float = 9.0) -> dict:
    from datasets import Image as HFImage
    from datasets import load_dataset
    from PIL import Image

    ds = load_dataset(HF_ID, split="train").cast_column("image", HFImage(decode=False))
    meta = ds.select_columns(["id", "text"])
    by_doc: dict[str, list[int]] = {}
    for i, r in enumerate(meta):
        if eligible(r["text"]):
            by_doc.setdefault(doc_id_of(r["id"]), []).append(i)
    rng = random.Random(seed)
    docs = sorted(by_doc)
    rng.shuffle(docs)
    quota = {"dev": n // 2, "holdout": n - n // 2}
    chosen, count = [], {"dev": 0, "holdout": 0}
    (out / "images").mkdir(parents=True, exist_ok=True)
    for d in docs:
        sp = split_of(d)
        if count[sp] >= quota[sp]:
            continue
        i = rng.choice(by_doc[d])
        row = ds[i]
        data = row["image"]["bytes"]
        w, h = Image.open(io.BytesIO(data)).size
        if not (min_mp <= w * h / 1e6 <= max_mp):
            continue
        name = f"p{len(chosen):04d}_{hashlib.sha1(row['id'].encode('utf-8')).hexdigest()[:8]}.jpg"
        (out / "images" / name).write_bytes(data)
        chosen.append({"id": f"muharaf_{len(chosen):04d}", "image": f"images/{name}", "category": "handwriting_ar_hist",
                       "gt": row["text"], "gt_type": "text", "lang": "ar", "doc_id": d, "split": sp,
                       "meta": {"source_id": row["id"], "width": w, "height": h}})
        count[sp] += 1
        if all(count[s] >= quota[s] for s in quota):
            break
    with open(out / "manifest.jsonl", "w", encoding="utf-8") as f:
        for r in chosen:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    words = sum(len(r["gt"].split()) for r in chosen)
    card = (f"# Bộ đánh giá Muharaf (công khai)\n\n- Nguồn: `{HF_ID}` (bản chia sẻ lại của Muharaf, arXiv 2406.09630; "
            "thẻ HF ghi MIT, Muharaf gốc ghi CC BY-NC-SA 4.0 → chỉ dùng nghiên cứu, KHÔNG phân phối lại).\n"
            f"- Chọn {len(chosen)} trang (dev {count['dev']}, holdout {count['holdout']}), mỗi tài liệu tối đa 1 trang; "
            f"seed {seed}; {words} từ.\n- Tiêu chí: 250–1800 ký tự, 5–30 dòng, ≥85% chữ cái Ả Rập, ảnh {min_mp}–{max_mp} MP.\n"
            "- Chia dev/holdout theo băm sha1 của mã tài liệu. Holdout chỉ chấm một lần ở cuối.\n"
            "- Đáp án (`gt`) là phiên âm từng dòng, ngăn bằng xuống dòng; có chính tả cũ / tiếng địa phương và có thể sai sót.\n")
    (out / "DATASET_CARD.md").write_text(card, encoding="utf-8")
    return {"pages": len(chosen), **count, "words": words}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("muharaf")
    m.add_argument("--out", required=True)
    m.add_argument("--n", type=int, default=100)
    m.add_argument("--seed", type=int, default=13)
    a = ap.parse_args(argv)
    if a.cmd == "muharaf":
        print(build_muharaf(Path(a.out), a.n, a.seed))


if __name__ == "__main__":
    main()
