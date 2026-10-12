"""Test bộ ghi độ tin cậy token (chỉ cần torch CPU)."""

import torch

from postcorrect.dots_logprob import TokenStatsRecorder


def test_chosen_token_comes_from_next_input_ids_not_argmax():
    r = TokenStatsRecorder()
    s0 = torch.tensor([[2.0, 1.9, 0.0, -1.0, -2.0]])      # hai token dẫn đầu gần hòa nhau
    s1 = torch.tensor([[0.0, 0.0, 3.0, 0.0, 0.0]])
    prompt = torch.tensor([[7, 7, 7]])
    assert r(prompt, s0) is s0                              # chỉ quan sát, không đổi scores
    # mô hình thực tế chọn token 1 (không phải argmax = 0) ở bước 0
    r(torch.cat([prompt, torch.tensor([[1]])], 1), s1)
    r.close()
    d = r.dump()
    p0 = torch.log_softmax(s0[0], -1)
    assert d["ids"] == [1, 2]                              # token thật, rồi argmax cho bước cuối
    assert abs(d["lp"][0] - float(p0[1])) < 1e-3          # log-prob của token ĐƯỢC CHỌN
    assert d["top_ids"][0] == [0, 1, 2]
    assert abs(d["margin"][0] - float(p0[0] - p0[1])) < 1e-3 and d["margin"][0] < 0.2
    assert len(d["ent"]) == len(d["lp"]) == len(d["top_lp"]) == 2


def test_disabled_recorder_records_nothing_and_reset_clears():
    r = TokenStatsRecorder()
    r.enabled = False
    r(torch.tensor([[1]]), torch.zeros(1, 4))
    r.close()
    assert r.ids == []
    r.enabled = True
    r(torch.tensor([[1]]), torch.zeros(1, 4))
    r.close()
    assert len(r.ids) == 1
    r.reset()
    assert r.ids == [] and r._prev is None


def test_dump_alt_pieces_only_for_uncertain_steps():
    class Tok:
        def convert_ids_to_tokens(self, ids):
            return [f"t{i}" for i in ids]

    r = TokenStatsRecorder()
    r(torch.tensor([[0]]), torch.tensor([[5.0, 0.0, 0.0, 0.0]]))   # chắc chắn (lề lớn)
    r(torch.tensor([[0, 0]]), torch.tensor([[1.0, 0.9, 0.5, 0.0]]))  # phân vân (không hòa ở top-3)
    r.close()
    d = r.dump(Tok())
    assert d["pieces"] == ["t0", "t0"]
    assert list(d["alt_pieces"]) == ["1"] and d["alt_pieces"]["1"] == ["t0", "t1", "t2"]
