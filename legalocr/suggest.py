"""LLM dùng NGỮ CẢNH để gợi ý cách đọc cho từ chưa chắc — có kiểm soát, và tách bạch "đọc từ ảnh" với "suy đoán".

Luật (theo thứ tự, gợi ý trượt luật nào thì bị loại và ghi lý do):
1. Chỉ hỏi về từ `uncertain` / `illegible`. Từ đã `read` không bao giờ được đưa ra để sửa.
2. Từ QUAN TRỌNG (tên, địa danh, số, ngày, số tiền, thửa đất, điều khoản, phủ định) bị KHOÁ: LLM chỉ được chọn một
   trong các cách đọc mà các model OCR đã đọc từ ảnh, hoặc trả null. Chữ mới → loại ("locked_invented").
3. Từ thường: được đề xuất chữ mới chỉ khi nó gần một cách đọc OCR về NÉT CHỮ: cùng khung chữ (chỉ khác dấu chấm / hamza)
   hoặc khác ≤ `max_char_edit` ký tự; không được thêm chữ số / chữ Latin ("not_visually_plausible").
4. Nếu có `scorer` (một VLM đọc dòng): chấm xác suất của CẢ DÒNG với cách đọc gốc và với gợi ý, có nhìn ảnh dòng.
   Điểm gợi ý thấp hơn gốc quá `image_margin` → `image_supported=False` (ảnh bác bỏ); cao hơn gốc quá margin →
   `image_prefers=True`. Scorer nên KHÁC model trụ
   (model trụ luôn chấm cao chính cách đọc tham lam của nó).
5. Gợi ý KHÔNG thay vào `word.text`. Nó nằm ở `word.suggestion`, hiện trong bản đọc chú giải và phiếu duyệt; chỉ người
   duyệt mới chấp nhận. Ngoại lệ duy nhất (tắt mặc định, `accept="ocr_option_image_verified"`): từ THƯỜNG, gợi ý trùng
   một cách đọc OCR khác, LLM chắc, ảnh ủng hộ gợi ý HƠN cách đọc trụ (image_prefers) → hiển thị cách đọc OCR đó thay cho cách đọc trụ; từ vẫn giữ [؟].
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from rapidfuzz.distance import Levenshtein

from .doc import ILLEGIBLE, UNCERTAIN, Line, Page, Word
from .script import core, has_digit, has_latin, rasm_key, vote_key

SYSTEM = (
    "You assist a human reviewer who is transcribing a HANDWRITTEN Arabic legal document (a land sale contract or a "
    "power of attorney, Palestine, 1950s-1980s). You see OCR text. Each uncertain word is replaced by a marker like "
    "⟦3⟧ and listed below with the readings proposed by several OCR engines. Using the context, pick the most plausible "
    "reading for each marker.\n"
    "Rules:\n"
    "- Items marked LOCKED (names, places, numbers, dates, amounts, legal terms): answer ONLY with one of the listed "
    "options, copied exactly, or null. Never invent a name, a place, a number, a date or an amount.\n"
    "- Other items: you may answer a different word only if it differs from one option by one or two letters that look "
    "alike in handwriting (dots: ب ت ث ن ي, ج ح خ, د ذ, ر ز, س ش, ص ض, ط ظ, ع غ, ف ق, ة ه, ى ي). Otherwise pick an option "
    "or null.\n"
    "- Keep dialect and old spellings. Do not add diacritics. If you are not sure, answer null with \"sure\": false.\n"
    "Output ONLY a JSON array: [{\"id\": <number>, \"choice\": \"<word>\" or null, \"sure\": true or false}]"
)


@dataclass
class SuggestConfig:
    context_lines: int = 1
    max_char_edit: int = 2
    max_char_ratio: float = 0.5
    image_margin: float = 0.05      # nat / token: gợi ý được coi là ảnh ủng hộ nếu ≥ điểm gốc − margin
    accept: str = "none"            # none | ocr_option_image_verified
    max_items_per_call: int = 12
    max_new_tokens: int = 400


def _options(w: Word) -> list[str]:
    out, seen = [], set()
    for t in [w.text, *w.alternatives, *w.readings.values()]:
        k = vote_key(t)
        if t and k and k not in seen:
            seen.add(k)
            out.append(t)
    return out


def build_request(page: Page, li: int, cfg: SuggestConfig) -> tuple[str, list[Word]] | None:
    """Prompt cho dòng `li` (kèm `context_lines` dòng trước / sau làm ngữ cảnh, chỉ dòng chính có marker)."""
    ln = page.lines[li]
    targets = [w for w in ln.words if w.status in (UNCERTAIN, ILLEGIBLE)][: cfg.max_items_per_call]
    if not targets:
        return None
    ids = {w.id: k + 1 for k, w in enumerate(targets)}
    ctx = []
    for j in range(max(0, li - cfg.context_lines), min(len(page.lines), li + cfg.context_lines + 1)):
        other = page.lines[j]
        if other.region != "Text":
            continue
        if j == li:
            ctx.append(" ".join(f"⟦{ids[w.id]}⟧" if w.id in ids else w.text for w in other.words))
        else:
            ctx.append(" ".join(w.text for w in other.words))
    items = []
    for w in targets:
        opts = _options(w)
        lock = " LOCKED" if w.critical else ""
        items.append(f"⟦{ids[w.id]}⟧{lock} options: " + " | ".join(opts if opts else ["(no reading)"]))
    user = "<text>\n" + "\n".join(ctx) + "\n</text>\n<items>\n" + "\n".join(items) + "\n</items>"
    return user, targets


def parse_reply(raw: str) -> list[dict]:
    s = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S)
    a, b = s.find("["), s.rfind("]")
    items = []
    if a != -1 and b > a:
        try:
            items = json.loads(s[a:b + 1])
        except json.JSONDecodeError:
            items = []
    if not items:
        for m in re.finditer(r"\{[^{}]*\}", s):
            try:
                items.append(json.loads(m.group()))
            except json.JSONDecodeError:
                pass
    out = []
    for it in items if isinstance(items, list) else []:
        if isinstance(it, dict) and isinstance(it.get("id"), int):
            ch = it.get("choice")
            out.append({"id": it["id"], "choice": ch.strip() if isinstance(ch, str) and ch.strip() else None,
                        "sure": bool(it.get("sure"))})
    return out


def validate(w: Word, choice: str, cfg: SuggestConfig) -> tuple[bool, str | None, bool]:
    """→ (hợp lệ, lý do loại, có phải một cách đọc OCR sẵn có)."""
    opts = _options(w)
    is_option = vote_key(choice) in {vote_key(o) for o in opts}
    if is_option:
        return True, None, True
    if w.critical:
        return False, "locked_invented", False
    if has_digit(choice) or has_latin(choice):
        return False, "introduces_digit_latin", False
    c = core(choice)
    for o in opts:
        d = Levenshtein.distance(core(o), c)
        # cùng khung nét (chỉ khác dấu chấm), hoặc khác ít ký tự VÀ ≤ 50% độ dài (từ ngắn: "علي" → "عمر" là đổi từ khác)
        if rasm_key(o) == rasm_key(choice) or (d <= cfg.max_char_edit and d / max(1, len(core(o))) <= cfg.max_char_ratio):
            return True, None, False
    return False, "not_visually_plausible", False


def _line_variant(ln: Line, w: Word, text: str) -> str:
    return " ".join(text if x.id == w.id else x.text for x in ln.words)


def suggest_page(page: Page, backend, cfg: SuggestConfig, scorer=None, crops: dict | None = None) -> dict:
    """Điền `word.suggestion` cho các từ chưa chắc. `backend`: build_prompt(msgs) + generate(prompts, max_new) (vd.
    postcorrect.backend.HFBackend). `scorer`: score(ảnh dòng, [chuỗi]) → [log-prob trung bình mỗi token]; `crops`:
    line.id → ảnh dòng (PIL) cho scorer. Trả thống kê."""
    reqs = []
    for li, ln in enumerate(page.lines):
        if ln.region != "Text":
            continue
        r = build_request(page, li, cfg)
        if r:
            reqs.append((li, *r))
    stats = {"lines": len(reqs), "asked": 0, "answered": 0, "valid": 0, "rejected": {}, "image_supported": 0,
             "accepted_display": 0}
    if not reqs:
        return stats
    prompts = [backend.build_prompt([{"role": "system", "content": SYSTEM}, {"role": "user", "content": u}])
               for _, u, _ in reqs]
    raws = backend.generate(prompts, [cfg.max_new_tokens] * len(prompts))
    for (li, _, targets), raw in zip(reqs, raws):
        ln = page.lines[li]
        stats["asked"] += len(targets)
        by_id = {it["id"]: it for it in parse_reply(raw)}
        for k, w in enumerate(targets, 1):
            it = by_id.get(k)
            if not it or it["choice"] is None or vote_key(it["choice"]) == vote_key(w.text):
                continue
            stats["answered"] += 1
            ok, why, is_option = validate(w, it["choice"], cfg)
            sug = {"text": it["choice"], "by": getattr(backend, "model_id", "llm"), "sure": it["sure"], "valid": ok,
                   "reason": why, "from_ocr_option": is_option, "image_score": None, "image_supported": None,
                   "displayed": False}
            if not ok:
                stats["rejected"][why] = stats["rejected"].get(why, 0) + 1
            elif scorer is not None and crops and ln.id in crops:
                s0, s1 = scorer.score(crops[ln.id], [_line_variant(ln, w, w.text), _line_variant(ln, w, it["choice"])])
                sug["image_score"] = {"original": round(s0, 4), "suggestion": round(s1, 4), "scorer": scorer.name}
                sug["image_supported"] = s1 >= s0 - cfg.image_margin   # ảnh không bác bỏ gợi ý
                sug["image_prefers"] = s1 > s0 + cfg.image_margin      # ảnh ủng hộ gợi ý HƠN cách đọc đang hiển thị
                stats["image_supported"] += int(sug["image_supported"])
            if ok:
                stats["valid"] += 1
            if (cfg.accept == "ocr_option_image_verified" and ok and is_option and it["sure"] and not w.critical
                    and sug.get("image_prefers")):
                sug["displayed"] = True
                sug["replaced"] = w.text
                w.text = next(o for o in _options(w) if vote_key(o) == vote_key(it["choice"]))
                w.origin = "ocr_alt_selected"   # vẫn là chữ một model OCR đọc từ ảnh; chỉ đổi cách đọc được hiển thị
                w.flag("alt_reading_selected")
                stats["accepted_display"] += 1
            w.suggestion = sug
    return stats


def image_rerank(page: Page, scorer, crops: dict) -> int:
    """Không cần LLM: với từ chưa chắc có ≥ 2 cách đọc OCR, chấm từng cách đọc theo ảnh dòng → ghi `image_ranking`
    vào features (người duyệt thấy cách đọc nào ảnh ủng hộ nhất). Không đổi chữ. Trả số từ đã chấm."""
    n = 0
    for ln in page.lines:
        if ln.id not in crops:
            continue
        for w in ln.words:
            opts = _options(w)
            if w.status == "read" or len(opts) < 2:
                continue
            scores = scorer.score(crops[ln.id], [_line_variant(ln, w, o) for o in opts])
            w.features["image_ranking"] = sorted(([o, round(s, 4)] for o, s in zip(opts, scores)), key=lambda x: -x[1])
            n += 1
    return n
