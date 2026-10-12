"""Test legalocr end-to-end trên ảnh tổng hợp (CPU, engine giả), tiền xử lý, duyệt, đánh giá, hiệu chỉnh, CLI."""

import json
import xml.etree.ElementTree as ET

import numpy as np
import pytest
from PIL import Image, ImageDraw

from legalocr.calibrate import calibrate, pick_threshold
from legalocr.doc import READ, UNCERTAIN, Page
from legalocr.engines import Reading, StaticEngine, trim_loops
from legalocr.evaluate import evaluate_page, summarize
from legalocr.fuse import EngineSpec, FusionConfig
from legalocr.pipeline import PipelineConfig, distribute_page_words, fuse_page, process_image
from legalocr.preprocess import mask_punch_holes, remove_ruled_lines
from legalocr.review import apply_decisions
from legalocr.segment import ProjectionSegmenter

GT = ["أنا الموقع أدناه البائع محمد بن علي الخطيب",
      "بعت قطعة الأرض رقم ٤٥ بثمن قدره ٥٠٠ دينار",
      "فقط خمسمائة دينار لا غير وقد قبضت الثمن",
      "الشاهد الأول سليم حسن"]


def synth_page(tmp_path, n=len(GT)):
    """Ảnh 'trang' có n dải mực ngang (mỗi dải = một dòng) — đủ cho ProjectionSegmenter; chữ đến từ engine giả."""
    im = Image.new("RGB", (1200, 120 * n + 80), (245, 240, 228))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(0)
    for i in range(n):
        y = 60 + 120 * i
        for x in range(200, 1100, 18):
            h = int(rng.integers(18, 34))
            d.rectangle([x, y + 34 - h, x + 10, y + 34], fill=(30, 30, 50))
    p = tmp_path / "page1.png"
    im.save(p)
    return p


def engines():
    bad = list(GT)
    bad[0] = bad[0].replace("الخطيب", "الحطيب")
    bad[1] = bad[1].replace("٥٠٠", "٥٥٠")
    return [StaticEngine("vlm_a", {f"l{i:03d}": {"text": t, "probs": [0.95] * len(t.split())} for i, t in enumerate(bad)}, 1.0),
            StaticEngine("vlm_b", {f"l{i:03d}": {"text": t, "probs": [0.9] * len(t.split())} for i, t in enumerate(GT)}, 0.9),
            StaticEngine("vlm_c", {f"l{i:03d}": {"text": t, "probs": [0.9] * len(t.split())} for i, t in enumerate(GT)}, 0.8)]


def test_end_to_end_outputs(tmp_path):
    img = synth_page(tmp_path)
    out = tmp_path / "out"
    page = process_image(img, out, ProjectionSegmenter(), engines(), cfg=PipelineConfig(nontext=False, doc_type="sale"))
    assert [ln.id for ln in page.lines] == ["l000", "l001", "l002", "l003"]
    w = next(w for w in page.words() if "طيب" in w.text)
    # 0,9 + 0,8 thắng 1,0 (đa số có trọng số) nhưng tên mà 1/3 model đọc khác → vẫn [؟], kèm cách đọc kia
    assert w.text == "الخطيب" and w.status == UNCERTAIN and w.alternatives == ["الحطيب"]
    w = next(w for w in page.words() if w.text in ("٥٠٠", "٥٥٠"))
    assert w.text == "٥٠٠" and w.status == UNCERTAIN and "digits_disagree" in w.reasons  # số: phải khớp mọi model
    assert any(i["type"] == "clause_missing" and i["details"]["clause"] == "buyer" for i in page.issues)
    for suffix in (".json", ".diplomatic.txt", ".annotated.txt", ".fields.json", ".page.xml", ".review.html"):
        assert (out / f"page1{suffix}").exists(), suffix
    ET.fromstring((out / "page1.page.xml").read_text(encoding="utf-8"))   # XML hợp lệ
    assert all((out / ln.crop).exists() for ln in page.lines)
    assert all((out / w.features["crop"]).exists() for w in page.words() if w.status != READ)
    html = (out / "page1.review.html").read_text(encoding="utf-8")
    assert 'data-wid="l001:' in html and "digits_disagree" in html
    again = Page.from_dict(json.loads((out / "page1.json").read_text(encoding="utf-8")))
    assert again.to_dict() == page.to_dict()
    assert len(page.image_sha256) == 64


def test_page_engine_distribution_and_page_only_text():
    pivot = [["بعت", "قطعة", "الأرض"], ["بثمن", "قدره", "٥٠٠"]]
    rd = Reading("بعت قطعه الأرض والشاهد سليم حسن عيسى بثمن قدره ٥٠٠", [0.9] * 10)
    per, extras = distribute_page_words(pivot, rd, min_run=3)
    assert per[0][0] == ["بعت", "قطعه", "الأرض"] and per[1][0] == ["بثمن", "قدره", "٥٠٠"]
    assert extras == [{"after_line": 0, "words": ["والشاهد", "سليم", "حسن", "عيسى"]}]


def test_fuse_page_with_page_engine_reports_unsupported_text():
    from legalocr.doc import Line

    lines = [Line("l000", [0, 0, 900, 40]), Line("l001", [0, 50, 900, 90])]
    page = Page("p", "p.png", lines=lines)
    lr = {"a": {"l000": Reading("بعت قطعة الأرض"), "l001": Reading("بثمن قدره ٥٠٠")},
          "b": {"l000": Reading("بعت قطعة الأرض"), "l001": Reading("بثمن قدره ٥٠٠")}}
    pr = {"dots": Reading("بعت قطعة الارض وقد قبضت الثمن كاملا بثمن قدره ٥٠٠")}
    cfg = PipelineConfig(fusion=FusionConfig(engines={"a": EngineSpec("a", 1.0), "b": EngineSpec("b", 0.9),
                                                      "dots": EngineSpec("dots", 0.8)}), doc_type=None)
    fuse_page(page, lr, pr, cfg)
    assert page.lines[0].hyps["dots"] == "بعت قطعة الارض"
    po = [i for i in page.issues if i["type"] == "page_only_text"]
    assert po and po[0]["details"]["words"] == ["وقد", "قبضت", "الثمن", "كاملا"]


def test_review_and_evaluate(tmp_path):
    img = synth_page(tmp_path)
    page = process_image(img, tmp_path / "out", ProjectionSegmenter(), engines(), cfg=PipelineConfig(nontext=False))
    gt = "\n".join(GT)
    before = evaluate_page(page, gt)
    assert before["char_edits"] == 0  # đa số đã đúng ở mọi chỗ
    assert before["all"]["clean_wrong"] == 0 and before["all"]["flagged"] > 0 and before["all"]["flagged_wrong"] == 0
    target = next(w for w in page.words() if w.status != READ)
    stats = apply_decisions(page, [{"word_id": target.id, "action": "replace", "text": "سهوا", "reviewer": "r1"}])
    assert stats["applied"] == 1 and target.origin == "human" and target.review["previous"]["text"] != "سهوا"
    after = evaluate_page(page, gt)
    assert after["char_edits"] > 0 and after["all"]["clean_wrong"] == 1  # người duyệt sửa sai cũng bị đo ra
    s = summarize([before, after])
    assert 0 <= s["all"]["residual_error"] <= 1 and "ece" in s


def test_calibration_learns_support():
    rng = np.random.default_rng(1)
    rows = []
    for _ in range(2000):
        sup = float(rng.choice([1.0, 0.67, 0.4]))
        y = int(rng.random() < {1.0: 0.97, 0.67: 0.7, 0.4: 0.3}[sup])
        rows.append({"support": sup, "rasm_support": sup, "p_mean": 0.9, "p_missing": 0, "multi_engine": 1,
                     "log_len": 1.5, "digit": 0, "insert_slot": 0, "critical": float(rng.random() < 0.2), "y": y})
    cal = calibrate(rows, target=0.05, target_critical=0.05)
    assert cal["weights"]["support"] > 0
    assert cal["residual"] <= 0.05 and 0.2 < cal["coverage"] < 0.6
    p = np.array([0.9, 0.8, 0.7, 0.6])
    tau, cov, res = pick_threshold(p, np.array([1, 1, 0, 1.0]), 0.0)
    assert tau == 0.8 and cov == 0.5 and res == 0.0


def test_remove_ruled_lines_keeps_crossing_strokes():
    im = Image.new("RGB", (800, 200), (240, 240, 240))
    d = ImageDraw.Draw(im)
    d.line([(20, 100), (780, 100)], fill=(100, 100, 120), width=2)   # dòng kẻ
    d.rectangle([400, 60, 404, 140], fill=(20, 20, 20))               # nét chữ cắt qua
    out, info = remove_ruled_lines(im)
    g = np.asarray(out.convert("L"))
    assert info["lines"] == 1
    assert g[100, 100] > 200 and g[100, 700] > 200      # đường kẻ đã xoá
    assert g[100, 402] < 60                              # chỗ nét chữ đè lên đường kẻ giữ nguyên
    assert g[70, 402] < 60 and g[130, 402] < 60


def test_mask_punch_holes_only_solid_margin_disks():
    im = Image.new("RGB", (1000, 800), (240, 236, 225))
    d = ImageDraw.Draw(im)
    d.ellipse([10, 380, 50, 420], fill=(20, 20, 20))                   # lỗ đục sát mép trái
    d.ellipse([480, 380, 520, 420], fill=(20, 20, 20))                 # mảng tròn giữa trang (không phải lỗ)
    d.ellipse([12, 600, 48, 636], outline=(20, 20, 20), width=4)       # vòng rỗng (như chữ o) sát mép
    out, info = mask_punch_holes(im)
    assert [h[:2] for h in info["holes"]] == [[30, 400]]
    g = np.asarray(out.convert("L"))
    assert g[400, 30] > 200 and g[400, 500] < 60 and g[600, 30] < 100


@pytest.mark.parametrize("words,expect,looped", [
    ("a b c c c c".split(), "a b c".split(), True),
    ("x y z y z y z".split(), "x y z".split(), True),
    ("a b c".split(), "a b c".split(), False)])
def test_trim_loops(words, expect, looped):
    assert trim_loops(words) == (expect, looped)


def test_cli_refuse_and_apply_review(tmp_path, capsys):
    from legalocr.cli import main

    img = synth_page(tmp_path)
    process_image(img, tmp_path / "out", ProjectionSegmenter(), engines(), cfg=PipelineConfig(nontext=False))
    main(["refuse", str(tmp_path / "out" / "page1.json"), "--out", str(tmp_path / "re"), "--tau-read", "0.99",
          "--doc-type", "none"])
    s = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert s["uncertain"] > 0 and (tmp_path / "re" / "page1.diplomatic.txt").exists()
    page = Page.from_dict(json.loads((tmp_path / "re" / "page1.json").read_text(encoding="utf-8")))
    wid = next(w.id for w in page.words() if w.status != READ)
    (tmp_path / "dec.json").write_text(json.dumps({"page": "page1", "decisions": [{"word_id": wid, "action": "accept"}]}))
    main(["apply-review", str(tmp_path / "re" / "page1.json"), str(tmp_path / "dec.json"), "--out", str(tmp_path / "final")])
    s = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert s["applied"] == 1 and (tmp_path / "final" / "page1.final.txt").exists()
    main(["models"])
    assert "Baseer__Nakba" in capsys.readouterr().out
