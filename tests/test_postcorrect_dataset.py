"""Test phần thuần (không tải dữ liệu) của bộ dựng dữ liệu đánh giá."""

from postcorrect.dataset import arabic_ratio, doc_id_of, eligible, split_of


def test_doc_id_strips_page_suffix():
    assert doc_id_of("2015 5-07b El-Khouri_Letter to Joseph Dec17 1959_2_1") == "2015 5-07b El-Khouri_Letter to Joseph Dec17 1959"
    assert doc_id_of("abc_1") == "abc" and doc_id_of("abc") == "abc"


def test_split_is_deterministic_and_by_document():
    assert split_of("doc A") == split_of("doc A") and {split_of(f"d{i}") for i in range(50)} == {"dev", "holdout"}


def test_eligibility_rules():
    ar = "\n".join(["كلمة " * 12] * 8)             # 8 dòng, ~480 ký tự, toàn chữ Ả Rập
    assert eligible(ar)
    assert not eligible("قصير")                     # quá ngắn
    assert not eligible("\n".join(["word " * 12] * 8))  # chữ Latin
    assert not eligible("كلمة " * 300)              # quá dài / một dòng
    assert arabic_ratio("abc") == 0 and arabic_ratio("كلمة") == 1
