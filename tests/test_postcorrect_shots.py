"""Test ví dụ few-shot thật (không GPU)."""

import json

from postcorrect.cli import main
from postcorrect.prompts import messages
from postcorrect.shots import make_shots
from tests.test_postcorrect_analysis import enc  # noqa: F401  (dùng lại tiện ích mã hoá)

GT = "الى الاخ العزيز جبيلي المحترم اني بخير والحمد لله وارجو ان تكونوا بالف خير وسلامة"
OCR = "الى الاخ العزيز جبيلي المحتزم اني بخير والحمد لله وارجو ان تكونوا بالف خبر وسلامة"


def cache(tmp_path, ids):
    ocr = tmp_path / "ocr"
    ocr.mkdir(parents=True, exist_ok=True)
    for i in ids:
        cells = [{"category": "Text", "text": OCR, "bbox": [0, 0, 1, 1]}]
        (ocr / f"{i}.json").write_text(json.dumps({"id": i, "cells": cells, "error": None}), encoding="utf-8")
    return ocr


def test_make_shots_picks_fixed_chunks_and_a_clean_one(tmp_path):
    ocr = cache(tmp_path, ["a", "b"])
    shots = make_shots(ocr, {"a": GT, "b": GT}, ["a", "b"], n_fix=1, n_clean=0, min_fix=2)
    assert len(shots) == 1 and shots[0]["fixes"] == [["المحتزم", "المحترم"], ["خبر", "خير"]]
    assert shots[0]["tgt"] == GT and shots[0]["src"] == OCR
    # chunk không có chỗ nào sai → làm ví dụ "không đổi gì"
    ocr2 = cache(tmp_path / "x", ["c"])
    (ocr2 / "c.json").write_text(json.dumps({"id": "c", "cells": [{"category": "Text", "text": GT, "bbox": [0, 0, 1, 1]}], "error": None}))
    clean = make_shots(ocr2, {"c": GT}, ["c"], n_fix=0, n_clean=1)
    assert clean and clean[0]["fixes"] == [] and clean[0]["src"] == clean[0]["tgt"]


def test_messages_with_real_shots_for_each_strategy():
    shots = [{"id": "a", "src": OCR, "tgt": GT, "fixes": [["المحتزم", "المحترم"], ["خبر", "خير"]]}]
    a = messages("A", "نص", shots=shots)
    assert [m["role"] for m in a] == ["system", "user", "assistant", "user"] and a[2]["content"] == f"<output>{GT}</output>"
    b = messages("B", "نص", shots=shots)
    assert json.loads(b[2]["content"]) == [{"word": "المحتزم", "fix": "المحترم"}, {"word": "خبر", "fix": "خير"}]
    c = messages("C", "نص", shots=shots)
    assert "[[المحتزم]]" in c[1]["content"] and "[[خبر]]" in c[1]["content"] and "[[" in c[1]["content"]


def test_make_shots_cli_skips_evaluation_pages(tmp_path, capsys):
    ocr = cache(tmp_path, ["p0", "p1", "p2"])
    man = tmp_path / "manifest.jsonl"
    man.write_text("\n".join(json.dumps({"id": i, "image": "x.jpg", "gt": GT, "split": "dev"}) for i in ("p0", "p1", "p2")))
    out = tmp_path / "shots.json"
    main(["make-shots", "--ocr", str(ocr), "--manifest", str(man), "--skip", "2", "--out", str(out), "--n-fix", "1", "--n-clean", "0", "--min-fix", "2"])
    shots = json.loads(out.read_text(encoding="utf-8"))
    assert [s["id"] for s in shots] == ["p2"]          # p0, p1 là tập đang chấm → không được dùng làm ví dụ
