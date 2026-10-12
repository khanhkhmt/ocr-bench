"""Xuất kết quả: văn bản nguyên văn có [؟], bản đọc có chú giải, trường thông tin quan trọng, PAGE-XML, phiếu duyệt HTML.

Quy ước trong văn bản (cả hai bản):
    từ          đọc chắc (các model khớp nhau, đủ ngưỡng)
    từ[؟]       có cách đọc nhưng chưa chắc — PHẢI soát với ảnh
    [؟]         không đọc được (không có cách đọc đáng tin)
    [توقيع] / [ختم] / [صورة]   chữ ký / con dấu / hình (vân tay, tem); chữ đọc được trong con dấu: [ختم: ...]
Bản NGUYÊN VĂN (diplomatic.txt) chỉ chứa chữ do model OCR đọc từ ảnh hoặc do người duyệt xác nhận — không một chữ nào
của LLM. Bản CHÚ GIẢI (annotated.txt) thêm sau từ chưa chắc: các cách đọc khác của OCR, và gợi ý LLM sau dấu "LLM:".
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from .doc import ILLEGIBLE, MARK, READ, Page, Word

REGION_LABEL = {"Signature": "توقيع", "Stamp": "ختم", "Picture": "صورة"}


def word_token(w: Word, annotated: bool = False) -> str:
    if w.status == ILLEGIBLE:
        base = MARK
    elif w.status == READ:
        return w.text
    else:
        base = f"{w.text}{MARK}"
    if not annotated:
        return base
    notes = []
    # từ không đọc được: bản chú giải vẫn cho người đọc thấy cách đọc tốt nhất (đứng đầu) cùng các cách đọc khác
    alts = ([w.text] if w.status == ILLEGIBLE and w.text else []) + [a for a in w.alternatives if a != w.text][:3]
    if alts:
        notes.append("/".join(alts))
    s = w.suggestion
    if s and s.get("valid"):
        tag = "LLM" + ("+ảnh" if s.get("image_supported") else "")
        notes.append(f"{tag}: {s['text']}")
    return base + (f"⟨{'; '.join(notes)}⟩" if notes else "")


def page_text(page: Page, annotated: bool = False) -> str:
    out = []
    for ln in page.lines:
        body = " ".join(word_token(w, annotated) for w in ln.words)
        if ln.region != "Text":
            label = REGION_LABEL.get(ln.region, ln.region)
            out.append(f"[{label}: {body}]" if body else f"[{label}]")
        elif ln.words:
            out.append(body)
        elif ln.hyps:
            out.append(MARK)  # dòng có mực mà không đọc được
    return "\n".join(out)


def summary(page: Page) -> dict:
    ws = list(page.words())
    st = {k: sum(1 for w in ws if w.status == k) for k in ("read", "uncertain", "illegible")}
    crit = [w for w in ws if w.critical]
    return {"words": len(ws), **st, "critical": len(crit),
            "critical_unresolved": sum(1 for w in crit if w.status != READ),
            "issues": {k: sum(1 for i in page.issues if i["severity"] == k) for k in ("error", "warn", "info")},
            "suggestions": sum(1 for w in ws if w.suggestion and w.suggestion.get("valid"))}


def write_all(page: Page, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / page.id
    paths = {
        "json": base.with_suffix(".json"),
        "diplomatic": out_dir / f"{page.id}.diplomatic.txt",
        "annotated": out_dir / f"{page.id}.annotated.txt",
        "fields": out_dir / f"{page.id}.fields.json",
        "pagexml": out_dir / f"{page.id}.page.xml",
        "review": out_dir / f"{page.id}.review.html",
    }
    paths["json"].write_text(json.dumps(page.to_dict(), ensure_ascii=False, indent=1), encoding="utf-8")
    paths["diplomatic"].write_text(page_text(page), encoding="utf-8")
    paths["annotated"].write_text(page_text(page, annotated=True), encoding="utf-8")
    paths["fields"].write_text(json.dumps({"fields": page.fields, "issues": page.issues, "summary": summary(page)},
                                          ensure_ascii=False, indent=1), encoding="utf-8")
    paths["pagexml"].write_text(page_xml(page), encoding="utf-8")
    paths["review"].write_text(review_html(page), encoding="utf-8")
    return paths


# ------------------------------------------------------------------ PAGE-XML
def _pts(poly) -> str:
    return " ".join(f"{int(x)},{int(y)}" for x, y in poly)


def page_xml(page: Page) -> str:
    """PAGE 2019 tối giản (eScriptorium / Transkribus mở được): TextLine + Word, TextEquiv@conf, trạng thái và loại
    thông tin trong thuộc tính custom."""
    e = html.escape
    W, H = (page.size + [0, 0])[:2]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15">',
           "<Metadata><Creator>legalocr</Creator></Metadata>",
           f'<Page imageFilename="{e(Path(page.image).name)}" imageWidth="{W}" imageHeight="{H}">',
           '<TextRegion id="r0"><Coords points="0,0 {0},0 {0},{1} 0,{1}"/>'.format(W, H)]
    for ln in page.lines:
        out.append(f'<TextLine id="{e(ln.id)}" custom="structure {{type:{e(ln.region)};}}">'
                   f'<Coords points="{_pts(ln.polygon)}"/>')
        for w in ln.words:
            b = w.box or ln.bbox
            custom = f"status {{value:{w.status};}}" + (f" entity {{value:{w.entity};}}" if w.entity else "")
            out.append(f'<Word id="{e(w.id.replace(":", "_"))}" custom="{e(custom)}">'
                       f'<Coords points="{b[0]},{b[1]} {b[2]},{b[1]} {b[2]},{b[3]} {b[0]},{b[3]}"/>'
                       f'<TextEquiv conf="{w.confidence:.3f}"><Unicode>{e(w.text)}</Unicode></TextEquiv></Word>')
        out.append(f'<TextEquiv><Unicode>{e(" ".join(word_token(w) for w in ln.words))}</Unicode></TextEquiv></TextLine>')
    out += ["</TextRegion>", "</Page>", "</PcGts>"]
    return "\n".join(out)


# ------------------------------------------------------------------ phiếu duyệt
_CSS = """
:root{--bg:#fff;--fg:#1d1d1f;--mut:#666;--line:#ddd;--warn:#fff4d6;--err:#ffe3e0;--ok:#e7f6ea;--acc:#2456c7}
@media (prefers-color-scheme:dark){:root{--bg:#18181a;--fg:#ececec;--mut:#a0a0a0;--line:#333;--warn:#3a3220;
--err:#3d2421;--ok:#1f3324;--acc:#7aa2ff}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:16px}
h1{font-size:20px}h2{font-size:16px;margin-top:28px}.mut{color:var(--mut)}
table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid var(--line);padding:6px;vertical-align:top}
.ar{direction:rtl;font-family:"Noto Naskh Arabic","Amiri",serif;font-size:19px}
img{max-width:100%;border:1px solid var(--line);background:#fff}
.error{background:var(--err)}.warn{background:var(--warn)}.crit{font-weight:600}
input[type=text]{width:100%;font-size:18px;direction:rtl}button{font-size:15px;padding:6px 14px}
.tag{display:inline-block;border:1px solid var(--line);border-radius:4px;padding:0 5px;font-size:12px;margin:1px}
"""

_JS = """
function collect(){const out=[];document.querySelectorAll('tr[data-wid]').forEach(tr=>{
 const a=tr.querySelector('input[type=radio]:checked');if(!a)return;
 out.push({word_id:tr.dataset.wid,action:a.value,text:tr.querySelector('input[type=text]').value,
 reviewer:document.getElementById('rev').value,note:tr.querySelector('.note').value});});
 const blob=new Blob([JSON.stringify({page:PAGE,decisions:out},null,1)],{type:'application/json'});
 const u=URL.createObjectURL(blob);const l=document.createElement('a');l.href=u;l.download=PAGE+'.decisions.json';l.click();}
"""


def review_html(page: Page) -> str:
    e = html.escape
    s = summary(page)
    rows = []
    for ln in page.lines:
        for w in ln.words:
            if w.status == READ and not (w.critical and w.reasons):
                continue
            crop = w.features.get("crop") or ln.crop
            readings = "".join(f'<div><span class="tag">{e(k)}</span> <span class="ar">{e(v) or "∅"}</span></div>'
                               for k, v in w.readings.items())
            sug = ""
            if w.suggestion:
                sg = w.suggestion
                verdict = "hợp lệ" if sg.get("valid") else f"bị loại: {sg.get('reason')}"
                img = "" if sg.get("image_supported") is None else (" · ảnh ủng hộ" if sg["image_supported"] else " · ảnh KHÔNG ủng hộ")
                sug = f'<div>LLM: <span class="ar">{e(sg["text"])}</span> <span class="mut">({verdict}{img})</span></div>'
            rank = w.features.get("image_ranking")
            if rank:
                sug += '<div class="mut">xếp hạng theo ảnh: ' + " > ".join(f'<span class="ar">{e(t)}</span>' for t, _ in rank) + "</div>"
            cls = "crit" if w.critical else ""
            rows.append(
                f'<tr data-wid="{e(w.id)}" class="{cls}"><td>{e(w.id)}<br><span class="tag">{e(w.status)}</span>'
                f'{"<span class=tag>" + e(w.entity) + "</span>" if w.entity else ""}<br>'
                f'<span class="mut">tin cậy {w.confidence:.2f}</span><br><span class="mut">{e(", ".join(w.reasons))}</span></td>'
                f'<td><img src="{e(crop or "")}" alt="{e(w.id)}"><br><img src="{e(ln.crop or "")}" alt="{e(ln.id)}"></td>'
                f'<td>{readings}{sug}</td>'
                f'<td><input type="text" value="{e(w.text)}"><br>'
                f'<label><input type="radio" name="a_{e(w.id)}" value="accept"> đúng như ảnh</label> '
                f'<label><input type="radio" name="a_{e(w.id)}" value="replace"> sửa thành ô trên</label> '
                f'<label><input type="radio" name="a_{e(w.id)}" value="illegible"> không đọc được</label>'
                f'<br><input class="note" type="text" placeholder="ghi chú" style="direction:ltr;font-size:13px"></td></tr>')
    issues = "".join(f'<tr class="{e(i["severity"])}"><td>{e(i["type"])}</td><td>{e(i["message"])}</td>'
                     f'<td>{e(i.get("line") or "")}</td></tr>' for i in page.issues)
    fields = "".join(f'<tr><td>{e(f["type"])}</td><td class="ar">{e(f["text"])}</td><td>{e(f["status"])}</td>'
                     f'<td>{f["confidence"]:.2f}</td></tr>' for f in page.fields)
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Duyệt {e(page.id)}</title><style>{_CSS}</style>
</head><body><h1>Phiếu duyệt — {e(page.id)}</h1>
<p class="mut">ảnh: {e(page.image)} · sha256 {e(page.image_sha256[:16])}… · {s['words']} từ: {s['read']} chắc,
{s['uncertain']} chưa chắc, {s['illegible']} không đọc được · {s['critical_unresolved']}/{s['critical']} từ quan trọng cần soát</p>
<h2>Kiểm tra chéo ({len(page.issues)})</h2><table>{issues or '<tr><td>không có</td></tr>'}</table>
<h2>Thông tin quan trọng</h2><table class="fields">{fields or '<tr><td>không có</td></tr>'}</table>
<h2>Từ cần duyệt</h2><p>Người duyệt: <input id="rev" type="text" style="width:220px;direction:ltr"> <button onclick="collect()">
Xuất quyết định (JSON)</button></p>
<table><tr><th>từ</th><th>ảnh (từ / dòng)</th><th>các model đọc</th><th>quyết định</th></tr>{''.join(rows)}</table>
<script>const PAGE={json.dumps(page.id)};{_JS}</script></body></html>"""
