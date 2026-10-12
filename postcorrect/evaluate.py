"""Đánh giá bước sửa lỗi: có GIẢM lỗi thật không, và sửa nhầm bao nhiêu.

Mọi số đều so với ĐÁP ÁN (phiên âm của người). Với mỗi trang có: gt (đáp án), original (văn bản OCR), corrected (sau sửa),
edits (danh sách sửa, chỉ số theo từ của `original`).

1. CER / WER trước và sau (ocrbench.normalize + ocrbench.metrics), có KTC 95% bootstrap theo TRANG.
   Hai bộ chuẩn hoá: strict (mặc định; KHÔNG gộp أ/إ/ا, ى/ي — vì đó là lỗi ta muốn sửa) và lenient (gộp).
2. Chỉ số mức SỬA. Căn chỉnh từ của `original` với `gt` (Levenshtein trên từ đã chuẩn hoá). Mỗi sửa được chấm bằng ĐỘ GIẢM
   khoảng cách ký tự tới đoạn đáp án tương ứng:
     fixed    = thành đúng hẳn            improved = gần đáp án hơn nhưng chưa đúng
     harm     = từ vốn ĐÚNG bị đổi sai    worse    = từ vốn sai bị đổi thành sai hơn
     neutral  = không đổi khoảng cách
   precision = (fixed + improved) / số sửa; tỉ lệ sửa nhầm = số từ ĐÚNG bị đổi (harm) / số từ đúng của OCR;
   net_char_gain = tổng độ giảm khoảng cách ký tự (dương = tốt).
3. "Tầm với": số từ OCR sai mà khoảng cách ký tự tới đáp án ≤ max_char_edit (chốt chặn cho phép sửa tối đa bấy nhiêu ký tự).
   Trần lý thuyết của bất kỳ bộ sửa nào bị chốt chặn đó. Ở nhiễu cao, phần lớn lỗi nằm NGOÀI tầm với.
4. Với danh sách cờ (strategy B/C): precision / recall của "từ được đánh dấu là lỗi" so với nhãn căn chỉnh.
"""

from __future__ import annotations

import dataclasses
import random
import unicodedata
from dataclasses import dataclass

from ocrbench.metrics import edit_stats
from ocrbench.normalize import NormConfig, normalize
from rapidfuzz.distance import Levenshtein

from .diff import Edit
from .text import split_words, strip_marks, split_affixes

STRICT = NormConfig(nfkc=True, strip_markdown=False, strip_tatweel=True, strip_diacritics=True, unify_alef=False,
                    unify_yeh=False, unify_digits=True, unify_punct=True)
LENIENT = dataclasses.replace(STRICT, unify_alef=True, unify_yeh=True)
_ALEF = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"})


def norm_w(word: str, lenient: bool = False) -> str:
    """Dạng so sánh của một từ: bỏ dấu câu hai đầu, tashkeel; chữ số → ASCII; lenient: gộp alef / yeh."""
    w = strip_marks(unicodedata.normalize("NFKC", split_affixes(word)[1]))
    w = w.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "0123456789" * 2))
    return w.translate(_ALEF) if lenient else w


def text_cer_wer(gt: str, hyp: str, cfg: NormConfig) -> dict:
    return edit_stats(normalize(gt, cfg), normalize(hyp, cfg))


@dataclass
class Alignment:
    label: list[str]                  # mỗi từ OCR: ok | sub | extra | empty
    pair: list[int | None]            # chỉ số từ đáp án tương ứng 1–1 (ok / sub), nếu có
    block: list[tuple[int, int]]      # đoạn đáp án [j1, j2) của khối căn chỉnh chứa từ này
    gt_norm: list[str]
    src_norm: list[str]


def align(src: list[str], gt: list[str], lenient: bool = False) -> Alignment:
    sn, gn = [norm_w(w, lenient) for w in src], [norm_w(w, lenient) for w in gt]
    si = [i for i, w in enumerate(sn) if w]
    gi = [j for j, w in enumerate(gn) if w]
    label, pair, block = ["empty"] * len(src), [None] * len(src), [(0, 0)] * len(src)

    def gt_range(j1, j2):
        if j2 > j1:
            return gi[j1], gi[j2 - 1] + 1
        pos = gi[j1] if j1 < len(gi) else len(gn)
        return pos, pos

    def flush(cur):
        if not cur:
            return
        i1, i2, j1, j2 = cur
        jr = gt_range(j1, j2)
        for k in range(i1, i2):
            i = si[k]
            block[i] = jr
            if j2 == j1:
                label[i] = "extra"  # từ thừa của OCR (đáp án không có từ tương ứng)
            else:
                label[i] = "sub"
                if (i2 - i1) == (j2 - j1):
                    pair[i] = gi[j1 + (k - i1)]

    cur = None  # khối khác nhau liền kề được gộp (như diff_words): thay + chèn / xoá = một khối
    for tag, i1, i2, j1, j2 in Levenshtein.opcodes([sn[i] for i in si], [gn[j] for j in gi]):
        if tag == "equal":
            flush(cur)
            cur = None
            jr = gt_range(j1, j2)
            for k in range(i1, i2):
                i = si[k]
                label[i], pair[i], block[i] = "ok", gi[j1 + (k - i1)], (gi[j1 + (k - i1)], gi[j1 + (k - i1)] + 1)
            continue
        cur = (i1, i2, j1, j2) if cur is None else (cur[0], i2, cur[2], j2)
    flush(cur)
    return Alignment(label, pair, block, gn, sn)


def _ref_for_span(al: Alignment, a: int, b: int) -> str:
    """Đoạn đáp án tương ứng với các từ OCR [a, b)."""
    ps = [al.pair[i] for i in range(a, b)]
    if ps and all(p is not None for p in ps) and ps == list(range(ps[0], ps[0] + len(ps))):
        return " ".join(al.gt_norm[ps[0]:ps[0] + len(ps)])
    j1 = min(al.block[i][0] for i in range(a, b))
    j2 = max(al.block[i][1] for i in range(a, b))
    return " ".join(al.gt_norm[j1:j2])


OUTCOMES = ("fixed", "improved", "harm", "worse", "neutral")


def score_edits(src: list[str], gt: list[str], edits: list[dict | Edit], lenient: bool = False,
                max_char_edit: int = 2) -> dict:
    al = align(src, gt, lenient)
    out = {k: 0 for k in OUTCOMES}
    out.update(edits=0, harm_words=0, net_char_gain=0, ok_words=sum(1 for l in al.label if l == "ok"),
               err_words=sum(1 for l in al.label if l in ("sub", "extra")),
               reach_words=0, fixed_words=0)
    for i, l in enumerate(al.label):  # từ sai nằm trong tầm với của chốt chặn (khoảng cách ≤ max_char_edit)
        if l == "sub" and al.pair[i] is not None and Levenshtein.distance(al.src_norm[i], al.gt_norm[al.pair[i]]) <= max_char_edit:
            out["reach_words"] += 1
    for e in edits:
        idx, frm, to = (e.index, e.src, e.dst) if isinstance(e, Edit) else (e["index"], e["from"].split(), e["to"].split())
        span = len(frm)
        if span == 0:
            continue
        ref = _ref_for_span(al, idx, idx + span)
        before = " ".join(al.src_norm[idx:idx + span])
        after = " ".join(norm_w(w, lenient) for w in to)
        d0, d1 = Levenshtein.distance(before, ref), Levenshtein.distance(after, ref)
        kind = ("harm" if d0 == 0 and d1 > 0 else "fixed" if d1 == 0 and d0 > 0 else "improved" if d1 < d0
                else "worse" if d1 > d0 else "neutral")
        out["edits"] += 1
        out[kind] += 1
        out["net_char_gain"] += d0 - d1
        if kind == "harm":
            out["harm_words"] += sum(1 for i in range(idx, idx + span) if al.label[i] == "ok")
        if kind == "fixed":
            out["fixed_words"] += span
    return out


def score_flags(src: list[str], gt: list[str], flagged: set[int], lenient: bool = False) -> dict:
    al = align(src, gt, lenient)
    err = {i for i, l in enumerate(al.label) if l in ("sub", "extra")}
    tp = len(flagged & err)
    return {"flags": len(flagged), "flag_tp": tp, "err_words": len(err)}


def page_metrics(gt: str, original: str, corrected: str, edits: list, flags: list | None = None,
                 max_char_edit: int = 2) -> dict:
    row = {}
    for name, cfg in (("strict", STRICT), ("lenient", LENIENT)):
        b, a = text_cer_wer(gt, original, cfg), text_cer_wer(gt, corrected, cfg)
        row[name] = {"ref_chars": b["ref_chars"], "ref_words": b["ref_words"], "cer_edits_before": b["char_edits"],
                     "cer_edits_after": a["char_edits"], "wer_edits_before": b["word_edits"],
                     "wer_edits_after": a["word_edits"]}
        row[name]["edits_scored"] = score_edits(split_words(original), split_words(gt), edits, name == "lenient", max_char_edit)
        if flags is not None:
            row[name]["flags_scored"] = score_flags(split_words(original), split_words(gt),
                                                    {f["index"] for f in flags}, name == "lenient")
    return row


def _sum(rows: list[dict], path: tuple) -> float:
    t = 0
    for r in rows:
        v = r
        for p in path:
            v = v[p]
        t += v
    return t


def summarize(rows: list[dict], name: str = "strict") -> dict:
    """Gộp (micro) các trang. rows = danh sách page_metrics()."""
    g = lambda *p: _sum(rows, (name,) + p)  # noqa: E731
    es = {k: g("edits_scored", k) for k in (*OUTCOMES, "edits", "harm_words", "net_char_gain", "ok_words", "err_words",
                                             "reach_words", "fixed_words")}
    s = {
        "pages": len(rows), "ref_chars": g("ref_chars"), "ref_words": g("ref_words"),
        "cer_before": g("cer_edits_before") / max(1, g("ref_chars")), "cer_after": g("cer_edits_after") / max(1, g("ref_chars")),
        "wer_before": g("wer_edits_before") / max(1, g("ref_words")), "wer_after": g("wer_edits_after") / max(1, g("ref_words")),
        **es,
        "precision": (es["fixed"] + es["improved"]) / es["edits"] if es["edits"] else float("nan"),
        "harm_rate": es["harm_words"] / es["ok_words"] if es["ok_words"] else float("nan"),
        "fix_rate_of_reach": es["fixed_words"] / es["reach_words"] if es["reach_words"] else float("nan"),
        "reach_frac_of_err": es["reach_words"] / es["err_words"] if es["err_words"] else float("nan"),
    }
    s["cer_delta"] = s["cer_after"] - s["cer_before"]
    s["wer_delta"] = s["wer_after"] - s["wer_before"]
    if "flags_scored" in rows[0][name]:
        f = {k: g("flags_scored", k) for k in ("flags", "flag_tp", "err_words")}
        s.update(flags=f["flags"], flag_precision=f["flag_tp"] / f["flags"] if f["flags"] else float("nan"),
                 flag_recall=f["flag_tp"] / f["err_words"] if f["err_words"] else float("nan"))
    return s


def bootstrap_ci(rows: list[dict], stat, n: int = 2000, seed: int = 0, name: str = "strict") -> tuple[float, float]:
    """KTC 95% percentile, resample TRANG (đơn vị độc lập vì mỗi trang thuộc một tài liệu khác nhau)."""
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        sample = [rows[rng.randrange(len(rows))] for _ in rows]
        vals.append(stat(summarize(sample, name)))
    vals.sort()
    return vals[int(0.025 * n)], vals[int(0.975 * n) - 1]


def by_noise_bins(rows: list[dict], edges=(0.0, 0.15, 0.30, 0.50, 10.0), name: str = "strict") -> list[tuple[str, dict]]:
    """Gộp theo mức nhiễu của OCR (CER trước sửa theo từng trang) — hiệu quả sửa phụ thuộc mạnh vào nhiễu."""
    out = []
    for lo, hi in zip(edges, edges[1:]):
        sel = [r for r in rows if lo <= r[name]["cer_edits_before"] / max(1, r[name]["ref_chars"]) < hi]
        if sel:
            out.append((f"CER OCR {lo:.2f}–{hi:.2f}" if hi < 10 else f"CER OCR ≥ {lo:.2f}", summarize(sel, name)))
    return out
