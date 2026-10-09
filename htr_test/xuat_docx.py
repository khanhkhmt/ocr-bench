"""DOCX cho trang tài liệu trên web thử HTR: theo thứ tự khối dots —
  khối CHỮ: chữ của bộ đọc chính (model chữ tay, đọc từng dòng); từ mà bộ đọc thứ hai (model chữ tay khác, hoặc dots)
            đọc khác → tô vàng + chú thích (htr_test/danh_dau.py);
  khối BẢNG: chữ dots (bảng HTML → bảng Word, như DOCX A);
  khối ẢNH (logo, chữ ký, con dấu…): chèn ảnh cắt từ trang.
"""

from __future__ import annotations

import io
from pathlib import Path

from docx.shared import Cm, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from .danh_dau import them_doan_danh_dau

TEXT_CATS = {"Text", "Title", "Section-header", "List-item", "Caption", "Footnote", "Page-header", "Page-footer"}


def _chu_to(doc) -> None:
    """Cỡ chữ cho chữ Ả Rập (w:szCs) — mặc định Word nhỏ khó đọc trên điện thoại."""
    rpr = doc.styles["Normal"].element.get_or_add_rPr()
    if rpr.find(qn("w:szCs")) is None:
        el = OxmlElement("w:szCs")
        el.set(qn("w:val"), "28")  # 14pt
        rpr.append(el)


def xuat_docx(out: Path, blocks: list[dict], chinh: dict[int, str], phu: dict[int, str], ten_chinh: str,
              ten_phu: str | None, image=None) -> dict:
    """blocks: khối dots (category, bbox, text). chinh / phu: {chỉ số khối: chữ} của bộ đọc chính / thứ hai.
    → thống kê {khối, từ, từ_ngờ}."""
    from ocrbench.docx_export import _add_markdown, _set_bidi, new_document

    doc = new_document("Kết quả OCR — chữ tay")
    doc.styles["Normal"].font.size = Pt(12)
    _chu_to(doc)
    note = doc.add_paragraph()
    r = note.add_run(f"Chữ tay đọc bằng {ten_chinh}." + (
        f" TÔ VÀNG = {ten_phu} đọc khác chỗ đó (xem chú thích) — cần người kiểm." if ten_phu else ""))
    r.font.size = Pt(9)
    st = {"khối": 0, "từ": 0, "từ_ngờ": 0}
    for bi, b in enumerate(blocks):
        cat = b.get("category")
        if cat in TEXT_CATS and bi in chinh and chinh[bi].strip():
            for dong_chinh, dong_phu in _cap_dong(chinh[bi], phu.get(bi) if ten_phu else None):
                if dong_phu is None:
                    p = doc.add_paragraph(dong_chinh)
                    _set_bidi(p)
                    n = m = 0
                else:
                    _, n, m = them_doan_danh_dau(doc, dong_chinh, dong_phu, ten_phu=ten_phu or "")
                st["từ"] += n
                st["từ_ngờ"] += m
            st["khối"] += 1
        elif cat == "Table" and b.get("text"):
            _add_markdown(doc, b["text"])
            st["khối"] += 1
        elif cat not in TEXT_CATS and image is not None and len(b.get("bbox") or []) == 4:
            x0, y0, x1, y1 = [int(round(v)) for v in b["bbox"]]
            if x1 - x0 > 8 and y1 - y0 > 8:
                buf = io.BytesIO()
                image.crop((x0, y0, x1, y1)).convert("RGB").save(buf, format="PNG")
                buf.seek(0)
                doc.add_picture(buf, width=Cm(min(16.0, (x1 - x0) / image.width * 18)))
                st["khối"] += 1
    doc.save(out)
    return st


def _cap_dong(chinh: str, phu: str | None) -> list[tuple[str, str | None]]:
    """Ghép dòng chính – phụ. Cùng số dòng (vd. hai model chữ tay đọc cùng các ảnh dòng) → so từng dòng; khác (vd. dots
    trả cả khối) → so cả khối một lần (chữ chính vẫn giữ xuống dòng bằng cách nối lại sau)."""
    a = [x for x in chinh.split("\n") if x.strip()]
    if phu is None:
        return [(x, None) for x in a]
    b = [x for x in phu.split("\n") if x.strip()]
    if len(a) == len(b):
        return list(zip(a, b))
    return [(" ".join(a), " ".join(b))]
