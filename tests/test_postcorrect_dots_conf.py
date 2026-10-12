"""Test ánh xạ thống kê token của dots → từng từ (không cần model)."""

import json

from postcorrect.dots_conf import _DEC, decode_with_spans, piece_bytes, word_confidences


def enc(s: str) -> str:
    """Mảnh BPE kiểu GPT-2 cho chuỗi s (mỗi byte một ký tự) — chỉ để dựng dữ liệu thử."""
    inv = {b: c for c, b in _DEC.items()}
    return "".join(inv[b] for b in s.encode("utf-8"))


def stats_for(pieces, lp=None):
    n = len(pieces)
    return {"pieces": pieces, "lp": lp or [-0.1] * n, "margin": [1.0] * n, "ent": [0.2] * n, "ids": list(range(n))}


def test_piece_bytes_roundtrip_and_special():
    assert piece_bytes(enc("مرحبا")).decode("utf-8") == "مرحبا"
    assert piece_bytes("<|im_end|>") == b""


def test_decode_with_spans_handles_token_splitting_a_character():
    raw = "ب".encode("utf-8")  # 2 byte; cắt đôi hai token
    inv = {b: c for c, b in _DEC.items()}
    pieces = [inv[raw[0]], inv[raw[1]] + enc("ا")]
    text, spans = decode_with_spans(pieces)
    assert text == "با" and spans[0] == (0, 1) and spans[1] == (1, 2)  # ký tự "ب" thuộc token chứa byte đầu


def test_word_confidences_maps_words_and_flags_low_prob_token():
    cells = [{"category": "Text", "text": "الى الاخ المحتزم", "bbox": [0, 0, 1, 1]},
             {"category": "Section-header", "text": "## عنوان", "bbox": [0, 0, 1, 1]}]
    response = json.dumps(cells, ensure_ascii=False)
    # mỗi từ một token, còn lại gộp thành mảnh lớn; đặt log-prob thấp cho token "المحتزم"
    parts = response.split("المحتزم")
    pieces = [enc(parts[0]), enc("المحتزم"), enc(parts[1])]
    st = stats_for(pieces, lp=[-0.05, -3.2, -0.05])
    out = word_confidences(response, st, cells)
    assert [w.word for w in out[0]] == ["الى", "الاخ", "المحتزم"]
    assert out[0][2].lp_min == -3.2 and out[0][0].lp_min == -0.05
    assert out[1][0].word == "عنوان"  # đã bỏ "## "


def test_word_confidences_returns_empty_when_response_differs():
    cells = [{"category": "Text", "text": "كلمة", "bbox": [0, 0, 1, 1]}]
    st = stats_for([enc("khác hoàn toàn")])
    assert word_confidences(json.dumps(cells, ensure_ascii=False), st, cells) == {}
