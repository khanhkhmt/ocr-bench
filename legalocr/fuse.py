"""Bỏ phiếu giữa nhiều model trên từng dòng → từ + độ tin cậy + trạng thái (read / uncertain / illegible).

Nguyên tắc: chữ in ra luôn là chữ MỘT model OCR đã đọc từ ảnh (không trộn, không do LLM sinh). Bỏ phiếu chỉ chọn
cách đọc được nhiều model (có trọng số) đồng ý nhất; độ tin cậy đo mức đồng ý đó, cộng độ chắc chắn của chính các
model (xác suất token) nếu có.

Độ tin cậy mặc định (chưa hiệu chỉnh) — dễ giải thích cho người duyệt:
    1 model:      p × 0,9          (không có gì để đối chiếu → không bao giờ "read": min_engines_read = 2)
    ≥ 2 model:    support × (0,5 + 0,5·p)
với support = tỉ trọng (theo trọng số model) đồng ý với cách đọc được chọn, p = xác suất trung bình các model đồng ý
tự báo (thiếu thì dùng `default_engine_prob`). Khi đã có dữ liệu dev có đáp án, `calibrate.py` học hàm logistic trên
cùng các đặc trưng (FEATURES) và thay công thức trên.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .align import Slot, align_many
from .doc import ILLEGIBLE, READ, Line, Word
from .script import digits_of, dominant_script, has_digit, has_harakat, has_latin, rasm_key, strip_harakat, vote_key

FEATURES = ["support", "rasm_support", "p_mean", "p_missing", "multi_engine", "log_len", "digit", "insert_slot",
            "critical"]


@dataclass
class EngineSpec:
    name: str
    weight: float = 1.0
    scripts: frozenset = frozenset({"ar", "he", "lat", "digit", "mixed"})


@dataclass
class FusionConfig:
    tau_read: float = 0.75
    tau_read_critical: float = 0.90
    tau_illegible: float = 0.25
    min_engines_critical: int = 2      # thông tin quan trọng phải có ≥ 2 model cùng đọc mới được "read"
    # MỌI từ: chỉ một model đọc dòng đó (không có gì đối chiếu) → không bao giờ "read". Đo trên hợp đồng viết tay 1972:
    # cho phép một model (HATFormer, tự tin cao cả khi bịa văn kiểu hadith "البخاري ثنا") → 256/307 từ thành "chắc"
    min_engines_read: int = 2
    harakat: str = "consensus"         # drop | consensus (giữ khi mọi model đồng ý giữ) | keep
    default_engine_prob: float = 0.75
    calibration: dict | None = None    # {"weights": {feature: w}, "bias": b} từ calibrate.py
    digits_never_illegible: bool = True  # từ có chữ số: in cách đọc tốt nhất kèm [؟] thay vì [؟] trơn (dễ soát hơn)
    engines: dict[str, EngineSpec] = field(default_factory=dict)

    def weight(self, e: str) -> float:
        return self.engines[e].weight if e in self.engines else 1.0


def line_script(hyps: dict[str, str], cfg: FusionConfig) -> str:
    votes: dict[str, float] = {}
    for e, t in hyps.items():
        s = dominant_script(t)
        if s != "none":
            votes[s] = votes.get(s, 0.0) + cfg.weight(e)
    return max(votes, key=votes.get) if votes else "none"


def confidence(feat: dict, cfg: FusionConfig) -> float:
    if cfg.calibration:
        w, b = cfg.calibration["weights"], cfg.calibration["bias"]
        z = b + sum(w.get(k, 0.0) * float(feat.get(k, 0.0)) for k in FEATURES)
        return 1 / (1 + math.exp(-z))
    p = feat["p_mean"] if not feat["p_missing"] else cfg.default_engine_prob
    if not feat["multi_engine"]:
        return round(p * 0.9, 4)
    return round(feat["support"] * (0.5 + 0.5 * p), 4)


def _surface(supporters: list[str], slot: Slot, cfg: FusionConfig, reasons: list[str]) -> str:
    best = max(supporters, key=cfg.weight)
    text = slot.readings[best]
    if not has_harakat(text) or cfg.harakat == "keep":
        return text
    forms = {slot.readings[e] for e in supporters}
    if cfg.harakat == "consensus" and len(supporters) >= 2 and len(forms) == 1:
        return text
    reasons.append("harakat_removed")
    return strip_harakat(text)


def vote_slot(slot: Slot, engines: list[str], cfg: FusionConfig) -> tuple[str | None, dict, list[str], list[str]]:
    """→ (chữ được chọn hoặc None nếu đa số nói "không có từ ở đây", đặc trưng, cách đọc khác, lý do)."""
    tally: dict[str, float] = {}
    for e in engines:
        k = vote_key(slot.readings.get(e, ""))
        tally[k] = tally.get(k, 0.0) + cfg.weight(e)
    total = sum(cfg.weight(e) for e in engines) or 1.0
    pivot_e = engines[0]
    top = max(tally, key=lambda k: (tally[k], k == vote_key(slot.readings.get(pivot_e, ""))))
    reasons: list[str] = []
    if top == "":
        return None, {"support": tally[top] / total}, [], reasons
    supporters = [e for e in engines if vote_key(slot.readings.get(e, "")) == top]
    text = _surface(supporters, slot, cfg, reasons)
    r_top = rasm_key(text)
    rasm_support = sum(cfg.weight(e) for e in engines if slot.readings.get(e) and rasm_key(slot.readings[e]) == r_top)
    ps = [slot.probs.get(e) for e in supporters if slot.probs.get(e) is not None]
    feat = {
        "support": round(tally[top] / total, 4),
        "rasm_support": round(rasm_support / total, 4),
        "p_mean": round(sum(ps) / len(ps), 4) if ps else 0.0,
        "p_missing": 0 if ps else 1,
        "multi_engine": int(len(engines) > 1),
        "n_engines": len(engines),
        "log_len": round(math.log1p(len(top)), 4),
        "digit": int(has_digit(text)),
        "insert_slot": int(not slot.pivot),
        "critical": 0,
    }
    if feat["insert_slot"]:
        reasons.append("pivot_missed")  # model trụ không đọc ra từ này → có thể là chữ bị sót, hoặc model khác bịa
    seen, alts = {top}, []
    for k in sorted(tally, key=tally.get, reverse=True):
        if k and k not in seen:
            seen.add(k)
            alts.append(next(slot.readings[e] for e in engines if vote_key(slot.readings.get(e, "")) == k))
    return text, feat, alts, reasons


def fuse_line(line: Line, hyps: dict[str, tuple[list[str], list[float | None] | None]], cfg: FusionConfig) -> Line:
    """hyps: engine → (từ, xác suất từng từ hoặc None). Điền line.words / script / pivot / dropped."""
    line.hyps = {e: " ".join(ws) for e, (ws, _) in hyps.items()}
    line.hyp_probs = {e: list(ps) for e, (ws, ps) in hyps.items() if ps is not None and len(ps) == len(ws)}
    line.script = line_script(line.hyps, cfg)
    usable = []
    for e, (ws, _) in hyps.items():
        if not ws:
            line.reasons.append(f"empty:{e}")
        elif e in cfg.engines and line.script not in cfg.engines[e].scripts:
            line.reasons.append(f"skip:{e}:script={line.script}")  # vd. model chữ viết tay Ả Rập trên dòng Hebrew
        else:
            usable.append(e)
    if not usable:
        line.words = []
        return line
    usable.sort(key=lambda e: -cfg.weight(e))  # model trụ = trọng số cao nhất có đọc ra chữ
    line.pivot = usable[0]
    slots = align_many(line.pivot, {e: hyps[e][0] for e in usable}, {e: hyps[e][1] for e in usable})
    words = []
    for slot in slots:
        text, feat, alts, reasons = vote_slot(slot, usable, cfg)
        readings = {e: slot.readings.get(e, "") for e in usable}
        if text is None:
            minority = {e: r for e, r in readings.items() if r}
            if minority:
                line.dropped.append({"readings": minority, "support": feat["support"]})
            continue
        # chữ Latin mà model khác đọc ra chữ không-Latin ở cùng chỗ: kiểu "trộn chữ Latin" / phiên âm do VLM tự thêm
        if has_latin(text) and any(r and not has_latin(r) for r in readings.values()):
            reasons.append("latin_in_arabic_line")
        w = Word(id=f"{line.id}:{len(words)}", text=text, readings=readings, features=feat, alternatives=alts,
                 reasons=reasons, probs={e: slot.probs.get(e) for e in usable})
        words.append(w)
    line.words = words
    return line


def decide_status(w: Word, cfg: FusionConfig) -> Word:
    """Gọi SAU khi gắn nhãn thông tin quan trọng (entities.py) vì ngưỡng của từ quan trọng chặt hơn."""
    f = w.features
    f["critical"] = int(w.critical)
    w.confidence = confidence(f, cfg)
    w.status = READ
    blocking = {"latin_in_arabic_line"}
    if (w.confidence < cfg.tau_illegible and f.get("rasm_support", 0) < 0.5
            and not (cfg.digits_never_illegible and f.get("digit"))):
        w.status = ILLEGIBLE
        return w
    if w.critical:
        if f.get("n_engines", 1) < cfg.min_engines_critical:
            w.flag("critical_unverified")
        if f["digit"]:
            ds = {digits_of(r) for r in w.readings.values() if r}
            if len(ds) > 1 or any(not r for r in w.readings.values()):
                w.flag("digits_disagree")
    if f.get("n_engines", 1) < cfg.min_engines_read:
        w.flag("single_engine")
    tau = cfg.tau_read_critical if w.critical else cfg.tau_read
    if w.confidence < tau:
        w.flag("low_confidence")
    if blocking & set(w.reasons):
        w.flag("blocked")
    return w


def add_token_reading(w: Word, engine: str, text: str, prob: float | None, cfg: FusionConfig) -> None:
    """Thêm phiếu của một engine chỉ đọc TỪNG TỪ (vd. bộ đọc chữ số trên khung từ) rồi bỏ phiếu lại ô này.
    Gọi trước decide_status. Không làm mất lý do / đặc trưng phụ (ảnh cắt...) đã có."""
    w.readings[engine] = text
    w.probs[engine] = prob
    engines = sorted(w.readings, key=lambda e: -cfg.weight(e))
    slot = Slot(pivot=() if w.features.get("insert_slot") else (0,), readings=dict(w.readings), probs=dict(w.probs))
    new_text, feat, alts, reasons = vote_slot(slot, engines, cfg)
    if new_text is None:  # đa số (có trọng số) nói không có từ ở đây: giữ chữ cũ nhưng đánh dấu
        w.flag("token_vote_empty")
        return
    extra = {k: v for k, v in w.features.items() if k not in feat}
    w.text, w.features, w.alternatives = new_text, {**feat, **extra}, alts
    for r in reasons:
        if r not in w.reasons:
            w.reasons.append(r)
