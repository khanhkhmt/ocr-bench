"""Test CLI postcorrect đầu-cuối bằng backend giả và cache OCR tổng hợp (không GPU, không model)."""

import json

from postcorrect.cli import main
from tests.test_postcorrect_analysis import make_rec

GT = "كتب المحترم"


def build(tmp_path):
    man = tmp_path / "manifest.jsonl"
    ocr = tmp_path / "ocr"
    ocr.mkdir()
    rows = []
    for i, split in enumerate(["dev", "dev", "holdout"]):
        rec = make_rec()
        rec["id"] = f"p{i}"
        rec["split"] = split
        (ocr / f"p{i}.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        rows.append({"id": f"p{i}", "image": f"images/p{i}.jpg", "gt": GT, "split": split, "doc_id": f"d{i}",
                     "category": "x", "gt_type": "text"})
    man.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    return man, ocr


def test_correct_cache_dummy_resume_and_eval(tmp_path, capsys):
    man, ocr = build(tmp_path)
    run = tmp_path / "run"
    main(["correct-cache", "--ocr", str(ocr), "--manifest", str(man), "--out", str(run), "--split", "dev",
          "--model", "dummy", "--variants", "A,C"])
    for v in ("A", "C"):
        files = sorted(p.name for p in (tmp_path / f"run__{v}").glob("p*.json"))
        assert files == ["p0.json", "p1.json"]  # chỉ tập dev
    r = json.loads((tmp_path / "run__A" / "p0.json").read_text(encoding="utf-8"))
    assert r["original"] == "كتب المحتزم" and r["edits"] == [] and r["strategy"] == "A"
    capsys.readouterr()
    # chạy lại: bỏ qua trang đã có (resume)
    main(["correct-cache", "--ocr", str(ocr), "--manifest", str(man), "--out", str(run), "--split", "dev",
          "--model", "dummy", "--variants", "A"])
    assert "cần chạy 0" in capsys.readouterr().out
    main(["eval", "--manifest", str(man), "--runs", f"A={tmp_path / 'run__A'}", f"C={tmp_path / 'run__C'}",
          "--split", "dev", "--boot", "10"])
    out = capsys.readouterr().out
    assert "2 trang chung" in out and "ΔCER" in out and "| A |" in out and "| C |" in out


def test_analyze_without_model_runs_on_dots_signals(tmp_path, capsys):
    man, ocr = build(tmp_path)
    main(["analyze", "--ocr", str(ocr), "--manifest", str(man), "--split", "dev", "--no-model", "--boot", "10"])
    out = capsys.readouterr().out
    assert "dots_lp" in out and "AUROC" in out
    assert "Trần ứng viên" in out and "1/1" not in out
