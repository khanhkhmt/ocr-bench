"""Test chẩn đoán LM-prefer bằng LM giả có từ vựng cố định."""

import json
from dataclasses import dataclass

from postcorrect.backend import WordNLL
from postcorrect.lm_prefer import collect, perturb, roc_table
from postcorrect.text import words_with_spans

GT = "الى الاخ العزيز جبيلي المحترم اني بخير والحمد لله وارجو ان تكونوا بالف خير وسلامة"
OCR = "الى الاخ العزيز جبيلي المحتزم اني بخير والحمد لله وارجو ان تكونوا بالف خبر وسلامة"
VOCAB = set(GT.split())


@dataclass
class VocabLM:
    """LM giả: từ trong từ vựng NLL thấp, ngoài từ vựng NLL cao."""
    model_id: str = "vocab"

    def nll_words(self, text):
        return [WordNLL(1.0, 1.0, 1) if w in VOCAB else WordNLL(9.0, 9.0, 1) for w, _, _ in words_with_spans(text)]


def test_collect_prefers_gold_words_and_rejects_perturbations():
    import random

    recs = {"p": {"id": "p", "cells": [{"category": "Text", "text": OCR, "bbox": [0, 0, 1, 1]}], "response": "", "token_stats": None}}
    pos, neg = collect(VocabLM(), recs, {"p": GT}, n_pos=10, n_neg=10, seed=1)
    assert len(pos) == 2 and all(d > 0 for d in pos)         # thay bằng từ đúng: NLL giảm
    assert neg and all(d <= 0 for d in neg)                  # làm nhiễu từ đúng: LM không thích hơn
    rows = roc_table(pos, neg, taus=(0.0, 5.0))
    assert rows[0][1] == 1.0 and rows[0][2] == 0.0 and rows[0][3] == 1.0
    assert perturb("ab", random.Random(0)) is None and perturb("الكتاب", random.Random(0)) != "الكتاب"
