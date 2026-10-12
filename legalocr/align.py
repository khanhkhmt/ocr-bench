"""Căn từ giữa nhiều cách đọc của CÙNG một dòng (mỗi model một cách) → các "ô" (slot) để bỏ phiếu, kiểu ROVER.

Khác diff của postcorrect (khớp từ chính xác): ở đây hai model hiếm khi đọc trùng từng chữ, nên chi phí thay thế là
khoảng cách ký tự chuẩn hoá (0 = giống, 1 = khác hẳn) trên `vote_key`. Thêm hai phép tách / gộp (một model đọc
"بعد الظهر", model kia "بعدالظهر") để khỏi lệch cả phần còn lại của dòng.

Dòng ngắn (≤ ~20 từ) nên quy hoạch động O(n·m) là đủ nhanh.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from rapidfuzz.distance import Levenshtein

from .script import vote_key

SPLIT_MERGE_PENALTY = 0.15
SPLIT_MERGE_MAX = 0.25


@lru_cache(maxsize=200_000)
def word_distance(a: str, b: str) -> float:
    ka, kb = vote_key(a), vote_key(b)
    if not ka and not kb:
        return 0.0 if a == b else 0.5
    return Levenshtein.normalized_distance(ka, kb)


def align_pair(ref: list[str], hyp: list[str], band: int | None = None) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Căn tối ưu ref ↔ hyp. Trả các cặp (chỉ số ref, chỉ số hyp) theo thứ tự: (i,)↔(j,) thay/khớp, (i,)↔() xoá,
    ()↔(j,) chèn, (i,)↔(j, j+1) model đọc tách đôi, (i, i+1)↔(j,) model đọc dính liền.
    `band`: chỉ xét ô cách đường chéo (đã co theo tỉ lệ độ dài) ≤ band — cho căn chỉnh cả trang (vài trăm từ)."""
    n, m = len(ref), len(hyp)
    INF = float("inf")
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back: list[list[tuple[int, int] | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    ratio = m / n if n else 1.0
    for i in range(n + 1):
        if band is None:
            js = range(m + 1)
        else:
            mid = int(i * ratio)
            js = range(max(0, mid - band), min(m, mid + band) + 1)
        for j in js:
            c = cost[i][j]
            if c == INF:
                continue
            steps = []
            if i < n and j < m:
                steps.append((1, 1, word_distance(ref[i], hyp[j])))
            if i < n:
                steps.append((1, 0, 1.0))
            if j < m:
                steps.append((0, 1, 1.0))
            # tách / gộp chỉ khi chữ cái gần như giữ nguyên (không thì "علي" ↔ "على من" thành tách đôi, nuốt từ "من")
            if i < n and j + 1 < m:
                d = word_distance(ref[i], hyp[j] + hyp[j + 1])
                if d <= SPLIT_MERGE_MAX:
                    steps.append((1, 2, d + SPLIT_MERGE_PENALTY))
            if i + 1 < n and j < m:
                d = word_distance(ref[i] + ref[i + 1], hyp[j])
                if d <= SPLIT_MERGE_MAX:
                    steps.append((2, 1, d + SPLIT_MERGE_PENALTY))
            for di, dj, w in steps:
                if c + w < cost[i + di][j + dj]:
                    cost[i + di][j + dj] = c + w
                    back[i + di][j + dj] = (di, dj)
    if band is not None and cost[n][m] == INF:  # dải quá hẹp (lệch quá nhiều) → căn đầy đủ
        return align_pair(ref, hyp, None)
    out = []
    i, j = n, m
    while i or j:
        di, dj = back[i][j]  # type: ignore[misc]
        out.append((tuple(range(i - di, i)), tuple(range(j - dj, j))))
        i, j = i - di, j - dj
    return out[::-1]


@dataclass
class Slot:
    """Một vị trí trên dòng. `pivot` = các chỉ số từ của model trụ (rỗng = từ mà model trụ KHÔNG đọc ra nhưng model
    khác có). `readings[engine]` = chuỗi model đó đọc ở vị trí này ("" = không đọc ra gì)."""
    pivot: tuple[int, ...]
    readings: dict[str, str] = field(default_factory=dict)
    probs: dict[str, float | None] = field(default_factory=dict)


def _join(words: list[str], idx: tuple[int, ...]) -> str:
    return " ".join(words[k] for k in idx)


def _prob(probs: list[float | None] | None, idx: tuple[int, ...]) -> float | None:
    if not probs or not idx:
        return None
    vals = [probs[k] for k in idx if k < len(probs) and probs[k] is not None]
    return min(vals) if vals else None


def align_many(pivot_engine: str, hyps: dict[str, list[str]],
               probs: dict[str, list[float | None] | None] | None = None) -> list[Slot]:
    """Căn mọi model vào model trụ → danh sách Slot theo thứ tự dòng.

    - Model nào đọc DÍNH hai từ của model trụ thành một → hai ô của model trụ gộp thành một ô (để mọi model so trên
      cùng một đoạn chữ).
    - Từ model khác đọc THÊM (model trụ không có) → ô chèn ở đúng khe đó; nhiều model chèn ở cùng khe thì chung một ô.
    """
    probs = probs or {}
    piv = hyps[pivot_engine]
    others = [e for e in hyps if e != pivot_engine]
    pairs = {e: align_pair(piv, hyps[e]) for e in others}

    # nhóm chỉ số model trụ cần gộp (có model đọc dính hai từ)
    group_of = list(range(len(piv)))
    for e in others:
        for pi, _ in pairs[e]:
            if len(pi) == 2:
                group_of[pi[1]] = group_of[pi[0]]
    groups: list[tuple[int, ...]] = []
    for k in range(len(piv)):
        if groups and group_of[k] == group_of[groups[-1][0]]:
            groups[-1] = groups[-1] + (k,)
        else:
            groups.append((k,))
    gi_of = {k: g for g, idx in enumerate(groups) for k in idx}

    # chữ mỗi model ở từng nhóm, và phần chèn ở từng khe (khe g = trước nhóm g; khe len(groups) = cuối dòng)
    cover: dict[str, dict[int, list[int]]] = {e: {} for e in others}
    inserts: dict[str, dict[int, list[int]]] = {e: {} for e in others}
    for e in others:
        last_group = -1
        for pi, hj in pairs[e]:
            if pi:
                g = gi_of[pi[0]]
                cover[e].setdefault(g, []).extend(hj)
                last_group = g
            else:
                inserts[e].setdefault(last_group + 1, []).extend(hj)

    slots: list[Slot] = []
    for g in range(len(groups) + 1):
        ins = {e: inserts[e][g] for e in others if inserts[e].get(g)}
        if ins:
            s = Slot(pivot=(), readings={pivot_engine: ""}, probs={pivot_engine: None})
            for e in others:
                idx = tuple(ins.get(e, ()))
                s.readings[e] = _join(hyps[e], idx)
                s.probs[e] = _prob(probs.get(e), idx)
            slots.append(s)
        if g == len(groups):
            break
        idx = groups[g]
        s = Slot(pivot=idx, readings={pivot_engine: _join(piv, idx)}, probs={pivot_engine: _prob(probs.get(pivot_engine), idx)})
        for e in others:
            hj = tuple(sorted(set(cover[e].get(g, []))))
            s.readings[e] = _join(hyps[e], hj)
            s.probs[e] = _prob(probs.get(e), hj)
        slots.append(s)
    return slots
