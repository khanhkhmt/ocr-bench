"""Áp quyết định của người duyệt (file JSON xuất từ phiếu duyệt HTML) vào kết quả trang.

Mỗi quyết định: {"word_id", "action": accept | replace | illegible, "text", "reviewer", "note"}.
- accept    : chữ OCR đang hiển thị đúng với ảnh → status "read", origin "human".
- replace   : người duyệt đọc khác → thay bằng "text", status "read", origin "human".
- illegible : người duyệt cũng không đọc được → status "illegible" (in [؟]).
Chữ cũ, người duyệt, thời điểm, ghi chú được giữ trong `word.review` (truy vết được ai đổi gì). Từ chưa có quyết định
giữ nguyên trạng thái — bản cuối vẫn in [؟] ở đó.
"""

from __future__ import annotations

import datetime as dt

from .doc import ILLEGIBLE, READ, Page
from .entities import extract_fields


def apply_decisions(page: Page, decisions: list[dict]) -> dict:
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    stats = {"applied": 0, "unknown": 0}
    for d in decisions:
        try:
            w = page.word(d["word_id"])
        except KeyError:
            stats["unknown"] += 1
            continue
        action = d.get("action")
        prev = {"text": w.text, "status": w.status, "origin": w.origin}
        if action == "accept":
            w.status = READ
        elif action == "replace" and (d.get("text") or "").strip():
            w.text = d["text"].strip()
            w.status = READ
        elif action == "illegible":
            w.status = ILLEGIBLE
        else:
            stats["unknown"] += 1
            continue
        w.origin = "human"
        w.review = {"action": action, "reviewer": d.get("reviewer") or "", "at": now, "note": d.get("note") or "",
                    "previous": prev}
        stats["applied"] += 1
    page.fields = extract_fields(page)
    page.provenance.setdefault("reviews", []).append({"at": now, **stats})
    return stats
