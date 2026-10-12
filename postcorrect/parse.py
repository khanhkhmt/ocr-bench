"""Đọc đầu ra thô của LLM: chiến lược A/C (viết lại trong thẻ <output>) và B (mảng JSON các từ nghi lỗi)."""

from __future__ import annotations

import json
import re

_THINK = re.compile(r"<think>.*?</think>", re.S)
_OUT = re.compile(r"<output>(.*?)</output>", re.S)
_FENCE = re.compile(r"^```[a-zA-Z]*\s*|\s*```$")


def parse_rewrite(raw: str) -> tuple[str | None, str]:
    """(văn bản, trạng thái). Trạng thái: ok | no_close (thiếu </output>) | no_tags | empty."""
    s = _THINK.sub("", raw or "").strip()
    m = _OUT.search(s)
    if m:
        text, status = m.group(1), "ok"
    elif "<output>" in s:
        text, status = s.split("<output>", 1)[1], "no_close"
    else:
        text, status = s, "no_tags"
    text = _FENCE.sub("", text.strip()).strip()
    return (text, status) if text else (None, "empty")


def parse_flags(raw: str, limit: int = 200) -> tuple[list[dict], str]:
    """Mảng [{"word": ..., "fix": ...}]. Chịu được chữ thừa quanh JSON, hàng rào ```, JSON cụt."""
    s = _FENCE.sub("", _THINK.sub("", raw or "").strip()).strip()
    items, status = None, "ok"
    a, b = s.find("["), s.rfind("]")
    if a != -1 and b > a:
        try:
            items = json.loads(s[a:b + 1])
        except json.JSONDecodeError:
            items = None
    if items is None:  # nhặt từng object {...} hoàn chỉnh
        items, status = [], "partial"
        for m in re.finditer(r"\{[^{}]*\}", s):
            try:
                items.append(json.loads(m.group()))
            except json.JSONDecodeError:
                pass
        if not items and not s.strip().startswith("[]"):
            status = "bad_json"
    out = []
    for it in items if isinstance(items, list) else []:
        if isinstance(it, dict) and isinstance(it.get("word"), str) and isinstance(it.get("fix"), str):
            w, f = it["word"].strip(), it["fix"].strip()
            if w and f and w != f:
                out.append({"word": w, "fix": f})
    return out[:limit], status
