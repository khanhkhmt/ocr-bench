"""Test legalocr: chữ viết, căn chỉnh, bỏ phiếu, thông tin quan trọng, kiểm tra chéo, LLM gợi ý. CPU, không model."""

import pytest

from legalocr.align import align_many, align_pair
from legalocr.crosscheck import run_all
from legalocr.doc import ILLEGIBLE, MARK, READ, UNCERTAIN, Line, Page, Word
from legalocr.entities import in_lex, LEGAL, tag_line, words_to_number
from legalocr.export import page_text
from legalocr.fuse import EngineSpec, FusionConfig, decide_status, fuse_line
from legalocr.script import digits_of, dominant_script, rasm_key, strip_harakat, vote_key
from legalocr.suggest import SuggestConfig, suggest_page, validate

AR = frozenset({"ar", "digit", "mixed"})


def cfg3(**kw):
    return FusionConfig(engines={"A": EngineSpec("A", 1.0, AR), "B": EngineSpec("B", 0.8), "C": EngineSpec("C", 0.6)}, **kw)


def fused(hyps, cfg=None, lid="l000"):
    cfg = cfg or cfg3()
    ln = fuse_line(Line(lid, [0, 0, 1000, 40]), {e: (t.split(), p) for e, (t, p) in hyps.items()}, cfg)
    tag_line(ln.words)
    for w in ln.words:
        decide_status(w, cfg)
    return ln


# ---------------- script
def test_scripts_and_keys():
    assert dominant_script("بعت قطعة الأرض رقم ١٢،") == "ar"
    assert dominant_script("שלום עולם") == "he"
    assert dominant_script("١٩٧٣/٥/١٢") == "digit"
    assert dominant_script("مدينة Jerusalem القدس") == "mixed"
    # cùng khung chữ, chỉ khác dấu chấm: đúng loại nhầm của chữ viết tay
    for a, b in [("ثابت", "تابت"), ("زيد", "ريد"), ("غانم", "عانم"), ("بيت", "يىت")]:
        assert rasm_key(a) == rasm_key(b), (a, b)
    assert rasm_key("محمد") != rasm_key("احمد")
    assert vote_key("«مُحَمَّد»،") == "محمد" and vote_key("١٢") == "12"
    assert digits_of("١٢/٥/١٩٧٣") == "1251973"
    assert strip_harakat("مُحَمَّدٌ") == "محمد"


# ---------------- align
def test_align_pair_split_merge_insert():
    assert align_pair("بعد الظهر جاء".split(), "بعدالظهر جاء".split()) == [((0, 1), (0,)), ((2,), (1,))]
    # "علي" ↔ "على من": thay + chèn, KHÔNG được coi là tách đôi (sẽ nuốt từ "من")
    assert align_pair("محمد بن علي".split(), "محمد بن على من".split())[-1] == ((), (3,))
    assert align_pair([], ["x"]) == [((), (0,))]


def test_align_many_merges_groups_and_inserts():
    slots = align_many("A", {"A": "بعت قطعة الارض".split(), "B": "بعت قطعه الارض رقم".split(),
                             "C": "بعت قطعةالارض".split()})
    assert [s.pivot for s in slots] == [(0,), (1, 2), ()]
    assert slots[1].readings == {"A": "قطعة الارض", "B": "قطعه الارض", "C": "قطعةالارض"}
    assert slots[2].readings == {"A": "", "B": "رقم", "C": ""}


# ---------------- fuse
def test_unanimous_is_read_disagreement_is_flagged():
    ln = fused({"A": ("بعت الارض للسيد محمد", [0.95] * 4), "B": ("بعت الارض للسيد محمد", [0.9] * 4),
                "C": ("بعت الارض للسيد مجمد", [0.9] * 4)})
    st = {w.text: w.status for w in ln.words}
    assert st["بعت"] == READ and st["الارض"] == READ
    w = ln.words[-1]
    assert w.text == "محمد" and w.critical and w.entity == "name"
    assert w.status == UNCERTAIN and "مجمد" in w.alternatives  # tên: 2/3 đồng ý chưa đủ ngưỡng từ quan trọng


def test_digits_must_agree_exactly():
    ln = fused({"A": ("قطعة رقم ١٢", [0.99] * 3), "B": ("قطعة رقم ١٢", [0.99] * 3), "C": ("قطعة رقم ١٣", [0.99] * 3)})
    w = ln.words[-1]
    assert w.critical and w.status == UNCERTAIN and "digits_disagree" in w.reasons
    ln = fused({"A": ("قطعة رقم ١٢", [0.99] * 3), "B": ("قطعة رقم 12", [0.99] * 3)})
    assert ln.words[-1].status == READ  # ١٢ = 12


def test_single_engine_never_verifies_critical():
    cfg = FusionConfig(engines={"A": EngineSpec("A", 1.0)})
    ln = fused({"A": ("المبلغ ٥٠٠ دينار", [0.99] * 3)}, cfg)
    assert all(w.status == UNCERTAIN for w in ln.words if w.critical)
    assert any("critical_unverified" in w.reasons for w in ln.words)


def test_minority_hallucination_dropped_and_latin_blocked():
    ln = fused({"A": ("من سكان قرية بيت صفافا Safafa", None), "B": ("من سكان قرية بيت صفافا", None),
                "C": ("من سكان قرية بيت صفافا", None)})
    assert "Safafa" not in " ".join(w.text for w in ln.words)
    assert ln.dropped and ln.dropped[0]["readings"] == {"A": "Safafa"}
    ln = fused({"A": ("قرية Beit صفافا", None), "B": ("قرية بيت صفافا", None)})
    w = ln.words[1]
    assert w.text == "Beit" and "latin_in_arabic_line" in w.reasons and w.status != READ


def test_harakat_consensus_policy():
    ln = fused({"A": ("مُحَمَّد علي", None), "B": ("محمد علي", None)})
    assert ln.words[0].text == "محمد" and "harakat_removed" in ln.words[0].reasons
    ln = fused({"A": ("مُحَمَّد علي", None), "B": ("مُحَمَّد علي", None)})
    assert ln.words[0].text == "مُحَمَّد"
    ln = fused({"A": ("مُحَمَّد علي", None), "B": ("محمد علي", None)}, cfg3(harakat="keep"))
    assert ln.words[0].text == "مُحَمَّد"


def test_engine_skipped_on_wrong_script():
    # A chỉ đọc chữ Ả Rập → trên dòng Hebrew (theo đa số model) bị bỏ
    ln = fused({"A": ("بيت لحم", None), "B": ("בית לחם", None), "C": ("בית לחם", None)})
    assert ln.script == "he" and ln.pivot == "B" and any(r.startswith("skip:A") for r in ln.reasons)
    assert [w.text for w in ln.words] == ["בית", "לחם"]


def test_empty_engine_does_not_vote():
    ln = fused({"A": ("بعت الارض", [0.95, 0.95]), "B": ("", None), "C": ("بعت الارض", [0.9, 0.9])})
    assert "empty:B" in ln.reasons and all(w.features["support"] == 1.0 for w in ln.words)


# ---------------- entities
@pytest.mark.parametrize("text,value", [
    ("خمسة آلاف وثلاثمائة دينار", 5300), ("ثلاث مائة", 300), ("احد عشر", 11), ("ثلاثة وعشرون", 23),
    ("فقط خمسمائة دينار اردني لا غير", 500), ("الفين و خمسمائة", 2500), ("مائة وخمسون الف", 150000),
    ("عشرة الاف", 10000), ("دينار", None)])
def test_words_to_number(text, value):
    assert words_to_number(text.split()) == value


def _tags(text):
    ws = [Word(f"w{i}", t, readings={"A": t}) for i, t in enumerate(text.split())]
    tag_line(ws)
    return {w.text: w.entity for w in ws}


def test_entity_tagging():
    t = _tags("أنا الموقع أدناه البائع محمد بن علي الخطيب من سكان قرية بيت صفافا")
    assert t["محمد"] == t["علي"] == t["الخطيب"] == "name" and t["بن"] == "name"
    assert t["الموقع"] is None and t["أدناه"] is None and t["من"] is None
    assert t["بيت"] == t["صفافا"] == "place"
    t = _tags("بثمن قدره ٥٠٠ دينار أردني بتاريخ ١٢/٥/١٩٧٣ وهي غير قابلة للعزل")
    assert t["٥٠٠"] == "amount" and t["دينار"] == "amount" and t["١٢/٥/١٩٧٣"] == "date"
    assert t["غير"] == "negation" and t["قابلة"] == "legal"
    t = _tags("الشاهد الأول سليم حسن والشاهد الثاني يوسف عيسى")
    assert t["سليم"] == t["حسن"] == t["يوسف"] == t["عيسى"] == "name" and t["الأول"] is None and t["والشاهد"] != "name"
    t = _tags("في الخامس من شهر آذار سنة ١٩٧٤")
    assert t["آذار"] == "date" and t["١٩٧٤"] == "date"
    # từ khoá đọc sai dấu chấm vẫn nhận ra (khớp theo khung chữ)
    assert in_lex("التاريح", frozenset({"التاريخ"}))
    assert in_lex("والتنازل", LEGAL)


# ---------------- crosscheck
def page_from(lines_text, status=READ):
    lines = []
    for i, t in enumerate(lines_text):
        ln = Line(f"l{i:03d}", [0, 40 * i, 1000, 40 * i + 30], hyps={"A": t})
        ln.words = [Word(f"l{i:03d}:{k}", w, status=status, confidence=0.95, readings={"A": w, "B": w},
                         features={"n_engines": 2, "digit": 0}) for k, w in enumerate(t.split())]
        tag_line(ln.words)
        lines.append(ln)
    return Page("p", "p.png", lines=lines)


def test_amount_words_vs_digits():
    p = page_from(["بثمن قدره ٥٥٠ دينار أردني", "فقط خمسمائة دينار لا غير"])
    run_all(p, doc_type=None)
    mm = [i for i in p.issues if i["type"] == "amount_mismatch"]
    assert mm and mm[0]["details"] == {"digits": "550", "words_value": 500}
    assert p.word("l000:2").status == UNCERTAIN  # hạ trạng thái cả hai bên
    p = page_from(["بثمن قدره ٥٠٠ دينار أردني فقط خمسمائة دينار لا غير"])
    run_all(p, doc_type=None)
    assert not [i for i in p.issues if i["type"] == "amount_mismatch"]


def test_dates_names_clauses_repetition():
    p = page_from(["بتاريخ ٣٥/١٤/١٩٧٣", "البائع محمد الخطيب", "المشتري احمد عودة", "وقبض البائع محمد الحطيب الثمن",
                   "الحوض الحوض الحوض"])
    run_all(p, doc_type="sale")
    kinds = {i["type"] for i in p.issues}
    assert {"date_invalid", "name_varies", "repetition", "clause_missing"} <= kinds
    missing = {i["details"]["clause"] for i in p.issues if i["type"] == "clause_missing"}
    assert "witnesses" in missing and "seller" not in missing


def test_unread_line_is_reported():
    p = page_from(["بعت الارض"])
    p.lines.append(Line("l001", [0, 50, 1000, 80], hyps={"A": "", "B": ""}))
    run_all(p, doc_type=None)
    assert any(i["type"] == "line_unread" for i in p.issues)
    assert page_text(p).split("\n")[-1] == MARK


# ---------------- export
def test_diplomatic_markers():
    p = page_from(["بعت الارض"])
    p.lines[0].words[1].status = UNCERTAIN
    p.lines[0].words[1].alternatives = ["الارص"]
    p.lines[0].words[0].status = ILLEGIBLE
    assert page_text(p) == f"{MARK} الارض{MARK}"
    assert page_text(p, annotated=True) == f"{MARK} الارض{MARK}⟨الارص⟩"
    sig = Line("l009", [0, 0, 10, 10], region="Signature")
    p.lines.append(sig)
    assert page_text(p).endswith("[توقيع]")


# ---------------- LLM gợi ý
class FakeLLM:
    model_id = "fake"

    def __init__(self, reply):
        self.reply, self.prompts = reply, []

    def build_prompt(self, msgs):
        return msgs[-1]["content"]

    def generate(self, prompts, max_new):
        self.prompts += prompts
        return [self.reply] * len(prompts)


class FakeScorer:
    name = "scorer"

    def __init__(self, good):
        self.good = good

    def score(self, image, texts):
        return [0.0 if self.good in t else -1.0 for t in texts]


def _uncertain_page():
    p = page_from(["وصلنا الى البلده بعد الظهر والسيد محمد"])
    w = p.lines[0].words[2]                 # thường: البلده
    w.status, w.alternatives, w.readings = UNCERTAIN, ["البلدة"], {"A": "البلده", "B": "البلدة"}
    n = p.lines[0].words[-1]                # quan trọng: tên
    n.status, n.alternatives, n.readings = UNCERTAIN, ["مجمد"], {"A": "محمد", "B": "مجمد"}
    return p, w, n


def test_llm_suggestion_never_overwrites_and_locks_names():
    p, w, n = _uncertain_page()
    llm = FakeLLM('[{"id": 1, "choice": "البلدة", "sure": true}, {"id": 2, "choice": "حامد", "sure": true}]')
    stats = suggest_page(p, llm, SuggestConfig())
    assert "⟦1⟧" in llm.prompts[0] and "⟦2⟧ LOCKED" in llm.prompts[0]
    assert w.text == "البلده" and w.suggestion["valid"] and w.suggestion["from_ocr_option"]
    assert n.text == "محمد" and not n.suggestion["valid"] and n.suggestion["reason"] == "locked_invented"
    assert stats["rejected"] == {"locked_invented": 1}
    assert "حامد" not in page_text(p) and "البلدة" not in page_text(p)  # bản nguyên văn không có chữ của LLM


def test_visual_plausibility_rule():
    w = Word("x", "الحطيب", status=UNCERTAIN, readings={"A": "الحطيب"})
    cfg = SuggestConfig()
    assert validate(w, "الخطيب", cfg)[0]          # chỉ khác dấu chấm
    assert not validate(w, "المحامي", cfg)[0]     # khác hẳn nét chữ
    assert validate(w, "الحطيب١", cfg)[1] == "introduces_digit_latin"


def test_image_verified_ocr_option_policy():
    p, w, n = _uncertain_page()
    llm = FakeLLM('[{"id": 1, "choice": "البلدة", "sure": true}]')
    suggest_page(p, llm, SuggestConfig(accept="ocr_option_image_verified"), FakeScorer("البلدة"), {"l000": object()})
    assert w.text == "البلدة" and w.origin == "ocr_alt_selected" and w.status == UNCERTAIN  # vẫn còn [؟]
    assert w.suggestion["image_supported"] and w.suggestion["displayed"]
    p, w, n = _uncertain_page()
    suggest_page(p, llm, SuggestConfig(accept="ocr_option_image_verified"), FakeScorer("لا شيء"), {"l000": object()})
    assert w.text == "البلده" and w.suggestion["image_supported"] and not w.suggestion["image_prefers"]  # ảnh không phân biệt
    p, w, n = _uncertain_page()
    suggest_page(p, llm, SuggestConfig(accept="ocr_option_image_verified"), FakeScorer("البلده"), {"l000": object()})
    assert w.text == "البلده" and w.suggestion["image_supported"] is False  # ảnh bác bỏ gợi ý
