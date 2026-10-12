"""Thứ tự đọc các dòng trên trang (phải → trái cho Ả Rập / Hebrew) bằng XY-cut theo KHE RỘNG NHẤT.

Vì sao: kraken trả dòng theo thứ tự của nó; trên trang có vùng hai cột (thân văn bản ở trên, dưới là ô công chứng bên
phải + chữ ký bên trái) các dòng của hai cột bị xen kẽ nhau → văn bản ghép sai vị trí.

Cách làm (đệ quy trên khung các dòng, mỗi lần cắt MỘT nhát ở khe rộng nhất):
- Khe DỌC (khoảng x không dòng nào phủ) rộng ≥ `col_gap` × chiều cao dòng trung vị và ≥ ½ khe ngang rộng nhất →
  tách cột, cột PHẢI trước.
- Không thì cắt ở khe NGANG rộng nhất → phần trên trước, phần dưới sau.
- Không tách được nữa: gom HÀNG theo độ chồng dọc thật (≥ 50%), hàng trên → dưới, trong hàng phải → trái.
Thân văn bản một cột không có khe dọc (dòng phủ gần hết bề ngang) nên giữ nguyên thứ tự trên → dưới.
"""

from __future__ import annotations

import statistics


def _gaps(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Khe giữa các khoảng [a, b) đã hợp lại (chỉ khe bên trong)."""
    iv = sorted(intervals)
    out, end = [], None
    for a, b in iv:
        if end is not None and a > end:
            out.append((end, a))
        end = b if end is None else max(end, b)
    return out


def reading_order(boxes: list[list[int]], rtl: bool = True, col_gap: float = 1.2) -> list[int]:
    """boxes: [[x0, y0, x1, y1]] → thứ tự chỉ số theo thứ tự đọc."""
    if not boxes:
        return []
    hs = [max(1, b[3] - b[1]) for b in boxes]
    med_h = statistics.median(hs)

    def widest(gaps):
        return max(gaps, key=lambda g: g[1] - g[0]) if gaps else None

    def rec(idx: list[int]) -> list[int]:
        """Cắt ở KHE RỘNG NHẤT, mỗi lần một nhát: khe ngang lớn nhất tách thân văn bản khỏi khu chữ ký bên dưới; trong
        khu đó khe dọc (giữa cột phải / cột trái) thắng nếu đủ rộng → đọc hết cột phải rồi mới sang cột trái."""
        if len(idx) <= 1:
            return idx
        vg = widest(_gaps([(boxes[i][0], boxes[i][2]) for i in idx]))
        hg = widest(_gaps([(boxes[i][1], boxes[i][3]) for i in idx]))
        vw = vg[1] - vg[0] if vg else 0
        hw = hg[1] - hg[0] if hg else 0
        if vg and vw >= col_gap * med_h and vw >= 0.5 * hw:
            cut = (vg[0] + vg[1]) / 2
            left = [i for i in idx if (boxes[i][0] + boxes[i][2]) / 2 < cut]
            right = [i for i in idx if (boxes[i][0] + boxes[i][2]) / 2 >= cut]
            if left and right:
                first, second = (right, left) if rtl else (left, right)
                return rec(first) + rec(second)
        if hg:
            cut = (hg[0] + hg[1]) / 2
            top = [i for i in idx if (boxes[i][1] + boxes[i][3]) / 2 < cut]
            bottom = [i for i in idx if (boxes[i][1] + boxes[i][3]) / 2 >= cut]
            if top and bottom:
                return rec(top) + rec(bottom)
        return _rows(idx)

    def _rows(idx: list[int]) -> list[int]:
        """Các dòng chồng nhau theo chiều dọc (chữ đánh máy dòng sát: khung kraken chồng vài px) — cùng HÀNG chỉ khi
        chồng ≥ 50% chiều cao dòng thấp hơn; hàng xếp trên → dưới, trong hàng phải → trái."""
        rows: list[list[int]] = []
        for i in sorted(idx, key=lambda i: (boxes[i][1] + boxes[i][3]) / 2):
            b = boxes[i]
            for row in rows:
                r = boxes[row[0]]
                ov = min(b[3], r[3]) - max(b[1], r[1])
                if ov >= 0.5 * min(b[3] - b[1], r[3] - r[1]):
                    row.append(i)
                    break
            else:
                rows.append([i])
        out: list[int] = []
        for row in rows:
            out += sorted(row, key=lambda i: -boxes[i][2] if rtl else boxes[i][0])
        return out

    return rec(list(range(len(boxes))))
