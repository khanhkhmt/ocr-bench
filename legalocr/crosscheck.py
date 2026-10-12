"""Kiểm tra chéo mức trang — bắt lỗi mà bỏ phiếu từng từ không thấy. KHÔNG sửa chữ nào: chỉ ghi `page.issues` và hạ
trạng thái các từ liên quan xuống "uncertain" để người duyệt xem.

| Kiểm tra          | Bắt được                                                                                  |
|-------------------|-------------------------------------------------------------------------------------------|
| amount_mismatch   | số tiền viết bằng số ≠ viết bằng chữ ("500 دينار ... فقط خمسون دينارا") — một trong hai đọc sai |
| date_invalid      | ngày > 31, tháng > 12, năm ngoài khoảng của bộ hồ sơ (vd. 1940–1995, hoặc Hijri 1360–1415)     |
| name_varies       | cùng một người / nơi viết khác nhau ở các lần nhắc (ت/ث, ب/ي...) — hoặc OCR đọc sai một lần    |
| clause_missing    | hợp đồng mua bán / uỷ quyền thiếu phần thường có (bên bán, giá, ngày, nhân chứng...) → có thể sót |
| line_unread       | dòng có mực nhưng không model nào đọc ra chữ → sót                                          |
| density_low/high  | số ký tự / bề rộng dòng lệch xa trung vị trang → đọc thiếu (sót) hoặc thừa (bịa, lặp)        |
| repetition        | một từ / cụm lặp liên tiếp (kiểu lặp vòng của VLM)                                          |
| minority_dropped  | chữ chỉ thiểu số model đọc ra (đã bỏ khỏi văn bản) — người duyệt quyết định sót hay bịa       |
"""

from __future__ import annotations

import re
import statistics

from rapidfuzz.distance import Levenshtein

from .doc import Page
from .entities import extract_fields, in_lex, lex_key
from .script import digits_of, vote_key

_DMY = re.compile(r"(\d{1,4})\s*[/.\-]\s*(\d{1,2})\s*[/.\-]\s*(\d{1,4})")

CLAUSES = {
    "sale": {
        "seller": "البائع بعت باع الفريق",
        "buyer": "المشتري اشتريت اشترى",
        "object": "قطعه حوض ارض الارض دونم عقار",
        "price": "ثمن الثمن مبلغ بمبلغ دينار ليره جنيه",
        "receipt": "قبضت قبض استلمت استلم تسلمت",
        "witnesses": "شاهد الشاهد شهود الشهود",
    },
    "poa": {
        "principal": "الموكل الموكله انا الموقع",
        "agent": "الوكيل وكلت وكيلا",
        "scope": "بيع فراغ تسجيل التسجيل المحكمه التصرف الاراضي",
        "witness_or_notary": "شاهد شهود العدل مصدق تصديق",
    },
}
_CLAUSE_LEX = {t: {k: frozenset(lex_key(w) for w in v.split()) for k, v in d.items()} for t, d in CLAUSES.items()}


def _issue(page: Page, kind: str, severity: str, message: str, word_ids=(), line=None, **details) -> dict:
    it = {"type": kind, "severity": severity, "message": message, "word_ids": list(word_ids), "line": line,
          "details": details}
    page.issues.append(it)
    for wid in word_ids:
        page.word(wid).flag(kind)
    return it


def check_amounts(page: Page, fields: list[dict]) -> None:
    amounts = [f for f in fields if f["type"] == "amount"]
    line_no = {ln.id: k for k, ln in enumerate(page.lines)}
    for k, f in enumerate(amounts):
        digits = f.get("digits", "").replace(" ", "")
        if not digits or not digits.isdigit():
            continue
        # chữ đi kèm: trong cùng trường, hoặc trường chữ gần nhất trong 2 dòng sau
        partner = f if f.get("words_value") else None
        if partner is None:
            for g in amounts[k + 1:]:
                if line_no[g["line"]] - line_no[f["line"]] > 2:
                    break
                if g.get("words_value") and not g.get("digits"):
                    partner = g
                    break
        if partner is None:
            continue
        if int(digits) != partner["words_value"]:
            _issue(page, "amount_mismatch", "error",
                   f"số tiền bằng số {digits} ≠ bằng chữ {partner['words_value']} — một trong hai bị đọc sai",
                   f["word_ids"] + ([] if partner is f else partner["word_ids"]), f["line"],
                   digits=digits, words_value=partner["words_value"])


def check_dates(page: Page, fields: list[dict], years=(1940, 1995), hijri_years=(1360, 1415)) -> None:
    for f in fields:
        if f["type"] != "date":
            continue
        m = _DMY.search(vote_key(f["text"].replace(" ", "")))
        if not m:
            continue
        a, b, c = (int(x) for x in m.groups())
        d, mo, y = (c, b, a) if a > 31 else (a, b, c)  # y/m/d hoặc d/m/y
        if y < 100:
            y += 1900
        ok_y = years[0] <= y <= years[1] or hijri_years[0] <= y <= hijri_years[1]
        if not (1 <= d <= 31 and 1 <= mo <= 12 and ok_y):
            _issue(page, "date_invalid", "error", f"ngày không hợp lệ hoặc ngoài khoảng năm của hồ sơ: {d}/{mo}/{y}",
                   f["word_ids"], f["line"], day=d, month=mo, year=y)


def check_names(page: Page, fields: list[dict], max_dist: float = 0.25) -> None:
    for kind in ("name", "place"):
        ms = [f for f in fields if f["type"] == kind and len(lex_key(f["text"])) >= 3]
        used: set[int] = set()
        for i, f in enumerate(ms):
            if i in used:
                continue
            group = [f]
            for j in range(i + 1, len(ms)):
                if j in used:
                    continue
                d = Levenshtein.normalized_distance(lex_key(f["text"]), lex_key(ms[j]["text"]))
                if 0 < d <= max_dist:
                    group.append(ms[j])
                    used.add(j)
            spellings = sorted({g["text"] for g in group})
            if len(spellings) > 1:
                _issue(page, "name_varies", "warn",
                       f"{'tên' if kind == 'name' else 'địa danh'} viết khác nhau giữa các lần nhắc: {' / '.join(spellings)}",
                       [w for g in group for w in g["word_ids"]], None, spellings=spellings)


def detect_doc_type(page: Page) -> str | None:
    words = [w.text for w in page.words()]
    score = {t: sum(any(in_lex(w, lex) for w in words) for lex in d.values()) for t, d in _CLAUSE_LEX.items()}
    best = max(score, key=score.get)
    return best if score[best] >= 2 else None


def check_clauses(page: Page, doc_type: str | None = "auto") -> None:
    if doc_type == "auto":
        doc_type = detect_doc_type(page)
    if not doc_type or doc_type not in _CLAUSE_LEX:
        return
    words = [w.text for w in page.words()]
    for name, lex in _CLAUSE_LEX[doc_type].items():
        if not any(in_lex(w, lex) for w in words):
            _issue(page, "clause_missing", "warn",
                   f"không thấy phần '{name}' của {doc_type} trong văn bản OCR — có thể bị sót, hoặc nằm ở trang khác",
                   clause=name, doc_type=doc_type)


def check_coverage(page: Page, low=0.45, high=2.2) -> None:
    text_lines = [ln for ln in page.lines if ln.region == "Text"]
    dens = {}
    for ln in text_lines:
        width = max(1, ln.bbox[2] - ln.bbox[0])
        n = sum(len(vote_key(w.text)) for w in ln.words)
        if not ln.words:
            if ln.hyps and not any(ln.hyps.values()):
                _issue(page, "line_unread", "error", "dòng có mực nhưng không model nào đọc ra chữ", line=ln.id)
            continue
        dens[ln.id] = n / width
    if len(dens) >= 4:
        med = statistics.median(dens.values())
        for ln in text_lines:
            if ln.id not in dens or med <= 0:
                continue
            r = dens[ln.id] / med
            if r < low:
                _issue(page, "density_low", "warn", f"dòng ít chữ bất thường so với bề rộng ({r:.2f}× trung vị) — có thể sót",
                       [w.id for w in ln.words], ln.id, ratio=round(r, 2))
            elif r > high:
                _issue(page, "density_high", "warn", f"dòng nhiều chữ bất thường ({r:.2f}× trung vị) — có thể bịa / lặp",
                       [w.id for w in ln.words], ln.id, ratio=round(r, 2))
    for ln in text_lines:
        keys = [vote_key(w.text) for w in ln.words]
        for k in range(len(keys) - 2):
            if keys[k] and keys[k] == keys[k + 1] == keys[k + 2]:
                _issue(page, "repetition", "warn", f"từ lặp liên tiếp: {ln.words[k].text}",
                       [w.id for w in ln.words[k:k + 3]], ln.id)
                break
        for d in ln.dropped:
            _issue(page, "minority_dropped", "info",
                   "chữ chỉ thiểu số model đọc ra, đã bỏ khỏi văn bản: " + " | ".join(f"{e}: {r}" for e, r in d["readings"].items()),
                   (), ln.id, readings=d["readings"])


def run_all(page: Page, doc_type: str | None = "auto", years=(1940, 1995), hijri_years=(1360, 1415)) -> list[dict]:
    fields = extract_fields(page)
    check_amounts(page, fields)
    check_dates(page, fields, years, hijri_years)
    check_names(page, fields)
    check_clauses(page, doc_type)
    check_coverage(page)
    page.fields = extract_fields(page)  # sau khi hạ trạng thái
    return page.issues


def digits_agree(readings: dict[str, str]) -> bool:
    ds = {digits_of(r) for r in readings.values() if r}
    return len(ds) <= 1
