"""Test các phần của adapter web demo (legalocr.adapter) — CPU, không kraken / Tesseract / model thật."""

import numpy as np
import pytest
from PIL import Image, ImageDraw

from legalocr.doc import READ, UNCERTAIN, Line, Word
from legalocr.engines import Reading, normalize_token
from legalocr.fuse import EngineSpec, FusionConfig, add_token_reading, decide_status
from legalocr.order import reading_order


# ---------------- thứ tự đọc
@pytest.mark.parametrize("boxes,expect", [
    # thân văn bản + dưới là 2 cột xen kẽ (ô công chứng phải, chữ ký trái)
    ([[50, 0, 950, 30], [50, 40, 950, 70], [60, 80, 940, 110], [550, 150, 950, 175], [50, 160, 400, 185],
      [550, 185, 950, 210], [50, 200, 400, 225], [550, 220, 950, 245]], [0, 1, 2, 3, 5, 7, 4, 6]),
    # hàng nhãn chữ ký cách xa nhau: đọc hết cột phải rồi cột trái
    ([[50, 0, 950, 30], [50, 40, 950, 70], [800, 150, 950, 180], [100, 150, 250, 180], [800, 230, 950, 260],
      [100, 230, 250, 260], [800, 310, 950, 340], [100, 310, 250, 340]], [0, 1, 2, 4, 6, 3, 5, 7]),
    # chữ đánh máy dòng sát nhau: khung kraken chồng vài px nhưng vẫn là các hàng khác nhau
    ([[144, 583, 796, 665], [155, 699, 936, 771], [144, 652, 870, 717], [223, 759, 868, 830]], [0, 2, 1, 3]),
])
def test_reading_order(boxes, expect):
    assert reading_order(boxes) == expect


def test_normalize_token():
    assert normalize_token("‎بالتــنبيه‏") == "بالتنبيه"     # LRM/RLM + tatweel
    assert normalize_token("بالتتههه") == "بالتته"                        # chữ cái lặp ≥ 3 lần → 1
    assert normalize_token("ممدوح") == "ممدوح"                            # lặp 2 lần là chữ thật


# ---------------- chữ số
def test_digit_decode_uses_one_system_per_number():
    import legalocr.digits as D

    P = np.zeros((3, len(D.CLASSES)))
    for row, (a, b) in enumerate([("١", "1"), ("٩", "9"), ("1", "١")]):  # nét giữa nghiêng về hệ Latin
        P[row, D.CLASSES.index(a)], P[row, D.CLASSES.index(b)] = 0.6, 0.4
    text, probs = D._decode(P, "ar")
    assert text == "١٩١" and all(0 < p <= 1 for p in probs)
    assert D._decode(P, "lat")[0] == "191"
    assert D.merge_affixes("18/04/2024.", ".18/04/2024") == "18/04/2024."   # dấu chấm cuối câu về đúng chỗ
    assert D.merge_affixes("(١٩٧٢)", "١٩٧٢") == "(١٩٧٢)"


def test_digit_components_left_to_right():
    import legalocr.digits as D

    im = Image.new("L", (200, 60), 255)
    d = ImageDraw.Draw(im)
    for x in (20, 70, 120):
        d.rectangle([x, 10, x + 20, 50], fill=0)
    d.rectangle([75, 5, 90, 12], fill=0)  # nét rời của cùng chữ số thứ 2 (chồng ngang) → gộp
    comps = D.components(D.ink_mask(im))
    assert [c[0] for c in comps] == [20, 70, 120]


def test_add_token_reading_revotes_digits():
    cfg = FusionConfig(engines={"a": EngineSpec("a", 0.9), "b": EngineSpec("b", 0.7), "digits": EngineSpec("digits", 1.2)})
    w = Word("l0:3", "1171", readings={"a": "1171", "b": "1411"}, probs={"a": 0.7, "b": 0.6},
             features={"insert_slot": 0, "crop": "x.png"}, critical=True)
    add_token_reading(w, "digits", "١٩٧٢", 0.9, cfg)
    decide_status(w, cfg)
    assert w.text == "١٩٧٢" and w.features["crop"] == "x.png"
    assert w.status == UNCERTAIN and "digits_disagree" in w.reasons
    w2 = Word("l0:4", "1972", readings={"a": "1972", "b": "1972"}, probs={"a": 0.9, "b": 0.9}, features={}, critical=True)
    add_token_reading(w2, "digits", "١٩٧٢", 0.95, cfg)
    decide_status(w2, cfg)
    assert w2.text == "١٩٧٢" and w2.status == READ   # cùng giá trị, khác hệ chữ số → khớp; hiển thị theo ảnh


# ---------------- màu mực, hướng đoạn
def test_red_watermark_line_detection():
    from legalocr.ink import ink_profile, is_red_mark

    def line(color):
        im = Image.new("RGB", (300, 40), (245, 240, 225))
        ImageDraw.Draw(im).rectangle([10, 10, 290, 30], fill=color)
        return im

    assert is_red_mark(ink_profile(line((220, 60, 80))))       # watermark / dấu đỏ
    assert not is_red_mark(ink_profile(line((20, 20, 20))))    # chữ đen
    assert not is_red_mark(ink_profile(line((40, 60, 160))))   # bút bi xanh = nội dung


def test_paragraph_direction_majority():
    from ocrbench.docx_export import para_rtl
    from ocrbench.viewer import ocr_html

    assert para_rtl("pel اثانة متحف الشعراء أحمد شوقي")       # rác Latin ở đầu dòng không lật cả dòng
    assert para_rtl("الهاتف: +971 56 512 3883 contact@firm.co.uk")
    assert not para_rtl("IBAN: SA39 7931 7540") and not para_rtl("12345")
    assert "‏" in ocr_html("Jacl ey بالتنبيه بندب من يلزم للاشراف")
    assert "‏" not in ocr_html("السيد الدكتور محمد")


# ---------------- logic adapter với engine giả
class FakeTess:
    def __init__(self, name, by_id, weight=0.9, scripts=frozenset({"ar", "digit", "mixed"})):
        self.name, self.by_id, self.weight, self.scripts = name, by_id, weight, scripts

    def read(self, ims):
        return [self.by_id.get(im.info["lid"], Reading("")) for im in ims]


def _adapter(arabic, hebrew=None):
    from legalocr.adapter import LegalOCRAdapter

    ad = LegalOCRAdapter()
    ad.arabic, ad.hebrew, ad.latin, ad.hand, ad.tessdata = arabic, hebrew, None, None, None
    return ad


def _crops(ids):
    out = {}
    for i in ids:
        im = Image.new("RGB", (200, 40), "white")
        im.info["lid"] = i
        out[i] = im
    return out


def R(text, conf):
    return Reading(text, [conf] * len(text.split()), [[0, 0, 10, 10]] * len(text.split()))


def test_script_arbitration_and_latin_failure():
    lines = [Line("l000", [0, 0, 200, 40]), Line("l001", [0, 50, 200, 90]), Line("l002", [0, 100, 200, 140])]
    ara = FakeTess("tess_ara_system", {"l000": R("بعت الارض", 0.9), "l001": R("نع ثصق", 0.2), "l002": R("(٢)", 0.5)})
    scr = FakeTess("tess_Arabic_best", {"l000": R("ERB ay NIS", 0.6), "l001": R("لا", 0.1), "l002": R("(٢)", 0.5)}, 0.5)
    heb = FakeTess("tess_heb", {"l000": R("אבג", 0.1), "l001": R("נוטריון ירושלים", 0.9), "l002": R("(א)", 0.95)},
                   0.8, frozenset({"he", "mixed"}))
    ad = _adapter([ara, scr], heb)
    out, scripts = ad._read(lines, _crops(["l000", "l001", "l002"]))
    assert scripts == {"l000": "ar", "l001": "he", "l002": "ar"}   # "(א)" một chữ: không đủ để chuyển sang Hebrew
    assert out["tess_heb"]["l001"].text == "נוטריון ירושלים"
    assert out["tess_Arabic_best"]["l000"].text == ""              # đầu ra Latin của model Ả Rập = hỏng, không bỏ phiếu


def test_prediction_labels_regions_and_skips_watermark():
    from legalocr.doc import Page

    ad = _adapter([])
    w = lambda t, c: Word("x", t, status=UNCERTAIN, confidence=c)  # noqa: E731
    lines = [Line("l000", [10, 10, 100, 30], words=[w("بعت", 0.9)]),
             Line("l001", [10, 40, 100, 60], region="Signature", words=[w("ري", 0.1)]),
             Line("l002", [10, 70, 100, 90], region="Stamp", words=[w("كاتب", 0.6), w("العدل", 0.6)]),
             Line("l003", [10, 100, 100, 120], region="Watermark", words=[w("اليوم", 0.9)])]
    page = Page("p", "", lines=lines)
    pred = ad._prediction(page, [{"category": "Signature", "bbox": [0, 35, 120, 65]}], k=2.0)
    assert pred.text.split("\n") == ["بعت[؟]", "[توقيع]", "[ختم: كاتب[؟] العدل[؟]]"]
    cats = [b["category"] for b in pred.extra["blocks"]]
    assert cats == ["Text", "Signature", "Text", "Text"]
    assert pred.extra["blocks"][0]["bbox"] == [5, 5, 50, 15]       # đổi về toạ độ ảnh gốc (ảnh đã phóng ×2)


def test_hebrew_needs_strong_neighbour():
    lines = [Line("l000", [500, 0, 900, 30]), Line("l001", [500, 40, 900, 70]), Line("l002", [0, 300, 400, 330])]
    ara = FakeTess("tess_ara_system", {i: R("نع ثصق", 0.2) for i in ("l000", "l001", "l002")})
    heb = FakeTess("tess_heb", {"l000": R("אימות חתימה", 0.75), "l001": R("שניתן מאת .₪07 7 רו", 0.45),
                                "l002": R("מ ונש = שש >", 0.5)}, 0.8, frozenset({"he", "mixed"}))
    ad = _adapter([ara], heb)
    _, scripts = ad._read(lines, _crops(["l000", "l001", "l002"]))
    assert scripts == {"l000": "he", "l001": "he", "l002": "ar"}  # dòng yếu đứng riêng (chữ tay Ả Rập) không thành Hebrew
