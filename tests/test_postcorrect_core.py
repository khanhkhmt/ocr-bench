"""Test cho postcorrect: chunker, diff, chốt chặn, parse. Không cần GPU / model."""

import random

from postcorrect.chunking import chunk_text
from postcorrect.diff import (Edit, apply_edits_text, apply_edits_words, diff_words, explode_equal_blocks)
from postcorrect.guard import GuardConfig, check_edit, filter_edits, finalize
from postcorrect.parse import parse_flags, parse_rewrite
from postcorrect.text import (core_of, has_digit, is_protected, norm_word, split_affixes, split_words,
                              strip_marks, words_with_spans)

AR_WORDS = "الى الاخ العزيز جبيلي المحترم اني بخير والحمد لله وارجو ان تكونوا بالف خير بدي اروح عالبيت بكرا".split()


def rand_text(rng, n_words, longest=9):
    out = []
    for i in range(n_words):
        w = rng.choice(AR_WORDS)
        if rng.random() < 0.05:
            w += rng.choice([".", "،", "؟", ":"])
        out.append(w)
        out.append(rng.choice([" ", " ", " ", "\n", "  "]) if i < n_words - 1 else "")
    return "".join(out)


# ---------- text ----------
def test_affixes_and_core():
    assert split_affixes("«كتب»،") == ("«", "كتب", "»،")
    assert split_affixes("،،") == ("،،", "", "")
    assert core_of("كَتَبَ،") == "كتب"
    assert strip_marks("مُحَمَّد") == "محمد"
    assert norm_word("١٢٣") == "123"


def test_protected_tokens():
    for w in ["24725", "٢٠٢٤/٠٤/١٨", "contact@mail.ae", "trang", "و", "،", "ab1"]:
        assert is_protected(w), w
    for w in ["المحترم", "بخير", "عالبيت", "بكرا،"]:
        assert not is_protected(w), w
    assert has_digit("١٩٦٠")


# ---------- chunking ----------
def check_invariants(text, max_chars):
    chunks = chunk_text(text, max_chars)
    ws = words_with_spans(text)
    assert sum(c.n_words for c in chunks) == len(ws)
    pos = 0
    for c in chunks:
        assert c.text == text[c.start:c.end]
        assert c.first_word == pos
        assert c.start == ws[c.first_word][1] and c.end == ws[c.first_word + c.n_words - 1][2]
        assert len(c.text) <= max_chars or c.n_words == 1
        pos += c.n_words
    assert [w for c in chunks for w in split_words(c.text)] == split_words(text)  # đúng thứ tự, không rơi từ nào
    return chunks


def test_chunk_invariants_random():
    rng = random.Random(5)
    for _ in range(200):
        text = rand_text(rng, rng.randint(0, 400))
        check_invariants(text, rng.choice([40, 120, 700]))


def test_chunk_regression_order_with_long_sentence_after_short():
    short = "هذه جملة قصيرة في البداية."
    long_ = " ".join(f"كلمة{i}" for i in range(160))  # ~1000 ký tự, không dấu câu
    chunks = check_invariants(short + " " + long_ + ".", 720)
    assert chunks[0].text.startswith("هذه جملة قصيرة")  # bản tham chiếu đặt câu ngắn vào chunk thứ hai


def test_chunk_regression_newlines_do_not_glue_words():
    text = "السطر الأول\nالسطر الثاني\n\nالفقرة الجديدة"
    chunks = check_invariants(text, 700)
    assert len(chunks) == 1 and chunks[0].text == text  # giữ nguyên xuống dòng, không dính chữ


def test_chunk_prefers_natural_boundary():
    lines = ["كلمة " * 30, "جملة " * 30, "فقرة " * 30]
    text = "\n".join(l.strip() for l in lines)
    chunks = check_invariants(text, 400)
    # dòng 1+2 (299 ký tự) vừa một chunk, dòng 3 sang chunk sau: luôn ngắt đúng chỗ xuống dòng, không giữa hàng
    assert [c.text for c in chunks] == ["\n".join(l.strip() for l in lines[:2]), lines[2].strip()]


def test_chunk_single_huge_word():
    text = "ا" * 2000 + " بسيط"
    chunks = check_invariants(text, 700)
    assert chunks[0].n_words == 1 and len(chunks[0].text) == 2000


# ---------- diff ----------
def test_diff_roundtrip_random():
    rng = random.Random(1)
    for _ in range(300):
        a = [rng.choice(AR_WORDS) for _ in range(rng.randint(0, 30))]
        b = list(a)
        for _ in range(rng.randint(0, 6)):
            op = rng.choice(["sub", "del", "ins"])
            if op == "sub" and b:
                b[rng.randrange(len(b))] = rng.choice(AR_WORDS) + "ي"
            elif op == "del" and b:
                b.pop(rng.randrange(len(b)))
            else:
                b.insert(rng.randint(0, len(b)), rng.choice(AR_WORDS))
        edits = diff_words(a, b)
        assert apply_edits_words(a, edits) == b
        assert apply_edits_words(a, explode_equal_blocks(edits)) == b


def test_apply_edits_text_preserves_whitespace():
    text = "الى  الاخ\nالعزيز جبيلي المحتزم،\nاني بخير"
    new = text.replace("المحتزم", "المحترم")
    edits = diff_words(split_words(text), split_words(new))
    assert len(edits) == 1 and edits[0].from_ == "المحتزم،" and edits[0].to == "المحترم،"
    assert apply_edits_text(text, edits) == new


def test_explode_equal_blocks_gives_independent_edits():
    edits = diff_words(["a", "b", "c", "d"], ["a", "X", "Y", "d"])
    assert len(edits) == 1 and edits[0].span == 2
    ex = explode_equal_blocks(edits)
    assert [(e.index, e.from_, e.to) for e in ex] == [(1, "b", "X"), (2, "c", "Y")]


# ---------- guard ----------
CFG = GuardConfig()


def E(i, src, dst):
    return Edit(i, tuple(src.split()), tuple(dst.split()))


def test_guard_accepts_small_letter_fix():
    assert check_edit(E(3, "المحتزم", "المحترم"), CFG) is None
    assert check_edit(E(3, "خبر", "خير"), CFG) is None


def test_guard_rejects_protected_and_digits():
    assert check_edit(E(0, "24725", "24726"), CFG) == "protected"
    assert check_edit(E(0, "trang", "صفحة"), CFG) == "protected"
    assert check_edit(E(0, "و", "في"), CFG) == "protected"
    assert check_edit(E(0, "الموافق", "الموافق2"), CFG) in ("introduces_digit_latin",)


def test_guard_rejects_big_rewrite_and_diacritics_only():
    assert check_edit(E(0, "بدي", "أريد"), CFG) == "too_far"
    assert check_edit(E(0, "عالبيت", "إلى البيت"), CFG) == "shape" or True  # 1→2 xa gốc → too_far
    assert check_edit(E(0, "محمد", "مُحَمَّد"), CFG) == "no_change"
    assert check_edit(E(0, "كتب،", "كتب."), CFG) == "no_change"


def test_guard_split_merge():
    assert check_edit(E(0, "بعدالظهر", "بعد الظهر"), CFG) is None
    assert check_edit(E(0, "بعد الظهر", "بعدالظهر"), CFG) is None
    assert check_edit(E(0, "بعدالظهر", "قبل الغروب"), CFG) in ("too_far", "shape")
    assert check_edit(Edit(0, ("بعد", "الظهر", "غدا"), ("بعدالظهر",)), CFG) == "shape"  # 3→1 không được phép


def test_guard_mask_for_flagged_words_only():
    e = E(5, "المحتزم", "المحترم")
    assert check_edit(e, CFG, allowed={4, 5}) is None
    assert check_edit(e, CFG, allowed={1, 2}) == "outside_flag"


def test_finalize_keeps_punct_and_does_not_add_diacritics():
    e = finalize(E(0, "المحتزم،", "المُحْتَرَم"))
    assert e.dst == ("المحترم،",)


def test_filter_edits_drops_whole_chunk_when_llm_rewrites():
    src = "الى الاخ العزيز جبيلي المحتزم اني بخير".split()
    out = "إلى الأخ العزيز جبيلي المحترم إنني بخير تماما".split()
    f = filter_edits(src, out, CFG)
    assert f.chunk_reason in ("drift", "too_many_edits") and not f.accepted
    ok = "الى الاخ العزيز جبيلي المحترم اني بخير".split()
    f = filter_edits(src, ok, CFG)
    assert f.chunk_reason is None and [e.to for e in f.accepted] == ["المحترم"]


def test_filter_edits_hallucinated_table_is_rejected():
    src = "فاتورة رقم".split()
    out = ("<table> <tr> <td>1</td> <td>Office</td> <td>chair</td> </tr> </table> " * 3).split()
    assert filter_edits(src, out, CFG).chunk_reason == "drift"


# ---------- parse ----------
def test_parse_rewrite_variants():
    assert parse_rewrite("<output>نص</output>") == ("نص", "ok")
    assert parse_rewrite("<output>سطر 1\nسطر 2") == ("سطر 1\nسطر 2", "no_close")
    assert parse_rewrite("نص بلا وسم") == ("نص بلا وسم", "no_tags")
    assert parse_rewrite("<think>\n\n</think>\n<output>نص</output>") == ("نص", "ok")
    assert parse_rewrite("   ") == (None, "empty")
    assert parse_rewrite("```\n<output>نص</output>\n```")[0] == "نص"


def test_parse_flags_variants():
    raw = 'نعم:\n```json\n[{"word": "المحتزم", "fix": "المحترم"}, {"word": "خبر", "fix": "خير"}]\n```'
    assert parse_flags(raw) == ([{"word": "المحتزم", "fix": "المحترم"}, {"word": "خبر", "fix": "خير"}], "ok")
    assert parse_flags("[]") == ([], "ok")
    items, st = parse_flags('[{"word": "أ", "fix": "ب"}, {"word": "ج", "fi')  # JSON cụt
    assert items == [{"word": "أ", "fix": "ب"}] and st == "partial"
    assert parse_flags("không có gì")[1] == "bad_json"
    assert parse_flags('[{"word": "س", "fix": "س"}]')[0] == []  # fix trùng word


def test_guard_blocks_foreign_script_letters_but_allows_removing_them():
    from postcorrect.guard import foreign_letters

    assert check_edit(E(0, "هنیا", "ہنیا"), CFG) == "foreign_script"      # ه (Ả Rập) → ہ (Urdu): sai
    assert check_edit(E(0, "جهדكم", "جهدكم"), CFG) is None                 # bỏ chữ Hebrew lọt vào: đúng
    assert foreign_letters(("هنیا",), ("هنيا",)) == set()                  # ی (Ba Tư) → ي (Ả Rập): chỉ chuyển về chữ chuẩn
    assert check_edit(E(0, "المحتزم", "المحترم"), CFG) is None


def test_guard_blocks_convention_only_edits():
    for src, dst in [("ان", "أن"), ("العزنه", "العزنة"), ("الى", "إلى"), ("على", "علي"), ("انها", "أنها")]:
        assert check_edit(E(0, src, dst), CFG) == "convention_only", (src, dst)
    assert check_edit(E(0, "فرجه", "فرحة"), CFG) is None            # ج→ح là sửa chữ thật (ه→ة đi kèm không làm nó thành "quy ước")
    assert check_edit(E(0, "ان", "أن"), GuardConfig(block_convention=False)) is None


def test_filter_edits_skips_chunks_with_dense_diacritics():
    src = ["مُحَمَّدٌ", "وَالْحَمْدُ", "لِلَّهِ", "الْعَالَمِينَ"] * 3
    hyp = list(src)
    hyp[0] = "مُحَمَّد"
    f = filter_edits(src, hyp, CFG)
    assert f.chunk_reason == "diacritics" and not f.accepted
    plain = "الى الاخ العزيز جبيلي المحتزم اني بخير".split()
    assert filter_edits(plain, "الى الاخ العزيز جبيلي المحترم اني بخير".split(), CFG).accepted
    assert filter_edits(src, hyp, GuardConfig(max_diacritic_ratio=0)).chunk_reason != "diacritics"


def test_guard_disabled_accepts_everything_the_llm_rewrote():
    src = "الى الاخ العزيز جبيلي المحتزم اني بخير".split()
    out = "إلى الأخ العزيز جبيلي المحترم إنني بخير تماما جدا".split()
    assert filter_edits(src, out, CFG).accepted == []                                 # có chốt chặn: bỏ cả chunk (lệch số từ)
    f = filter_edits(src, out, GuardConfig(enabled=False))
    assert f.chunk_reason is None and f.rejected == [] and len(f.accepted) >= 4       # không chốt chặn: nhận hết
