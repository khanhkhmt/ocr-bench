"""Test phân tích tín hiệu / trần ứng viên (dữ liệu tổng hợp, không cần model)."""

import json

from postcorrect.analysis import alt_oracle, auroc, word_rows
from postcorrect.dots_conf import _DEC


def enc(s):
    inv = {b: c for c, b in _DEC.items()}
    return "".join(inv[b] for b in s.encode("utf-8"))


def test_auroc_basic():
    assert auroc([3, 4], [1, 2]) == 1.0
    assert auroc([1, 2], [3, 4]) == 0.0
    assert auroc([1, 1], [1, 1]) == 0.5
    assert auroc([], [1]) != auroc([], [1])  # nan


def make_rec(word="المحتزم", alts=("زم", "رم", "نم"), chosen_lp=-2.5):
    cells = [{"category": "Text", "text": f"كتب {word}", "bbox": [0, 0, 1, 1]}]
    response = json.dumps(cells, ensure_ascii=False)
    head, tail = response.split(word)[0], response.split(word)[1]
    pieces = [enc(head), enc(word[:-2]), enc(word[-2:]), enc(tail)]
    n = len(pieces)
    ts = {"pieces": pieces, "ids": [10, 11, 12, 13], "lp": [-0.1, -0.2, chosen_lp, -0.05], "margin": [3, 3, 0.4, 3],
          "ent": [0.1, 0.2, 2.0, 0.1], "top_ids": [[10, 1, 2], [11, 1, 2], [12, 21, 22], [13, 1, 2]],
          "top_lp": [[0, -3, -4]] * n, "alt_pieces": {"2": [enc(a) for a in alts]}}
    return {"id": "t", "cells": cells, "response": response, "token_stats": ts}


def test_word_rows_labels_and_dots_signals():
    rec = make_rec()
    page, rows = word_rows(rec, "كتب المحترم")
    assert [r.label for r in rows] == ["ok", "near"]
    assert rows[1].signals["dots_lp"] == 2.5 and rows[1].signals["dots_margin"] == -0.4
    assert rows[0].signals["dots_lp"] < rows[1].signals["dots_lp"]  # từ sai ngần ngừ hơn từ đúng


def test_alt_oracle_finds_gold_in_second_alternative():
    rec = make_rec(alts=("زم", "رم", "نم"))         # phương án 2 (index 1) = "رم" → "المحترم" đúng
    r = alt_oracle(rec, "كتب المحترم")
    assert r == {"near": 1, "covered": 1, "covered_top2": 1}
    rec = make_rec(alts=("زم", "بم", "نم"))         # không có phương án đúng
    assert alt_oracle(rec, "كتب المحترم")["covered"] == 0
    rec = make_rec(alts=("زم", "بم", "رم"))         # đúng nhưng chỉ ở phương án 3
    r = alt_oracle(rec, "كتب المحترم")
    assert r["covered"] == 1 and r["covered_top2"] == 0
