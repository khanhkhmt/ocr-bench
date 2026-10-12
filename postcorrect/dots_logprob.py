"""DotsAdapter ghi thêm độ tin cậy TỪNG TOKEN lúc sinh — tín hiệu "nhìn thấy ảnh" miễn phí cho bước khoanh từ lỗi.

Vì sao: LLM sửa lỗi chỉ thấy chữ, không thấy nét; còn chính dots đã nhìn pixel. Token dots sinh ra với xác suất thấp /
lề top1−top2 nhỏ / entropy cao là chỗ nó "đoán". Ghi lại lúc OCR (không tốn thêm GPU) để sau này đo xem có khoanh đúng từ
lỗi không, mà không phải OCR lại (OCR là phần đắt nhất: ~2,4 phút/trang trên T4). Ghi cả top-3 phương án ở mỗi bước: chữ
dots phân vân (vd. ب/ن) là ứng viên sửa "có cơ sở trên ảnh".

Không sửa ocrbench: kế thừa DotsAdapter, gắn một LogitsProcessor qua generation_kwargs.

Token ĐƯỢC CHỌN lấy từ input_ids ở lần gọi kế tiếp (token cuối của chuỗi), không suy ra bằng argmax: ở fp16 hai token hay
hòa nhau và topk / argmax có thể chọn khác thật (đã thấy "841" so với "840") → lệch ánh xạ ký tự về sau.

Dùng trong config: `adapter: "postcorrect.dots_logprob:DotsLogprobAdapter"`.
"""

from __future__ import annotations

from ocrbench.adapters.dots import DotsAdapter

TOPK = 3


class TokenStatsRecorder:
    """LogitsProcessor chỉ quan sát (trả nguyên scores). Mỗi bước ghi: token thật, log-prob của nó, top-3 (id, log-prob), entropy."""

    def __init__(self):
        self.enabled = True
        self.reset()

    def reset(self):
        self.ids, self.lp, self.ent, self.top_ids, self.top_lp = [], [], [], [], []
        self._prev = None

    def _finalize(self, chosen: int | None):
        if self._prev is None:
            return
        logp, tid, tlp, ent = self._prev
        if chosen is None:  # bước cuối (không còn lần gọi sau): coi như token argmax
            chosen, lp = tid[0], tlp[0]
        else:
            lp = float(logp[chosen])
        self.ids.append(chosen)
        self.lp.append(lp)
        self.ent.append(ent)
        self.top_ids.append(tid)
        self.top_lp.append(tlp)
        self._prev = None

    def __call__(self, input_ids, scores):
        if not self.enabled:
            return scores
        import torch

        if self._prev is not None:
            self._finalize(int(input_ids[0, -1]))
        logp = torch.log_softmax(scores[0].float(), -1)
        top = torch.topk(logp, TOPK)
        ent = float(-(logp.exp() * logp).sum())
        self._prev = (logp, top.indices.tolist(), top.values.tolist(), ent)
        return scores

    def close(self):
        self._finalize(None)

    def dump(self, tokenizer=None) -> dict:
        r = lambda xs: [round(x, 3) for x in xs]  # noqa: E731
        out = {"ids": self.ids, "lp": r(self.lp), "ent": r(self.ent),
               "margin": r([t[0] - t[1] for t in self.top_lp]),
               "top_ids": self.top_ids, "top_lp": [r(t) for t in self.top_lp]}
        if tokenizer is not None:
            out["pieces"] = tokenizer.convert_ids_to_tokens(self.ids)
            # mảnh của các phương án chỉ lưu ở chỗ dots phân vân (lề < 2 nat) để file gọn
            out["alt_pieces"] = {str(i): tokenizer.convert_ids_to_tokens(self.top_ids[i])
                                 for i, t in enumerate(self.top_lp) if t[0] - t[1] < 2.0}
        return out


class DotsLogprobAdapter(DotsAdapter):
    def load(self):
        super().load()
        from transformers import LogitsProcessorList

        self._rec = TokenStatsRecorder()
        self._depth = 0
        kw = dict(self.params.get("generation_kwargs") or {})
        kw["logits_processor"] = LogitsProcessorList([self._rec])
        self.params["generation_kwargs"] = kw

    def parse_image(self, origin_image, prompt_mode=None, bbox=None, min_pixels=None, max_pixels=None, zoom=True):
        top = self._depth == 0
        if top:  # lượt sinh chính của trang; các lượt zoom lồng nhau (nếu có) diễn ra SAU và không được ghi
            self._rec.reset()
            self._rec.enabled = True
        else:
            self._rec.enabled = False
        self._depth += 1
        try:
            out = super().parse_image(origin_image, prompt_mode, bbox, min_pixels, max_pixels, zoom)
        finally:
            self._depth -= 1
        if top:
            self._rec.enabled = False
            self._rec.close()
            out["token_stats"] = self._rec.dump(getattr(self._processor, "tokenizer", self._processor))
        return out
