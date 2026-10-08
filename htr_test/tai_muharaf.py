"""Tải bộ dòng chữ viết tay Muharaf (phần công khai, NeurIPS 2024) và tách thành thư mục để xem / chấm.

    python -m htr_test.tai_muharaf ~/du_lieu_muharaf [--splits train,validation,test]

Nguồn: https://huggingface.co/datasets/aamijar/muharaf-public (bản dòng của Zenodo 11492215, cùng 24.495 dòng, đã
chia train / validation / test). Không gated. Giấy phép **CC BY-NC-SA 4.0 — PHI THƯƠNG MẠI**.
Cấu trúc kết quả: xem htr_test/tai_du_lieu.py. Cột `trang` = tên file gốc bỏ số dòng (AF_295v-12.png → AF_295v).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from htr_test.tai_du_lieu import tai

REPO = "aamijar/muharaf-public"
FILES = {
    "train": [f"data/train-0000{i}-of-00003.parquet" for i in range(3)],
    "validation": ["data/validation-00000-of-00001.parquet"],
    "test": ["data/test-00000-of-00001.parquet"],
}

NGUON = """# Muharaf — Manuscripts of Handwritten Arabic (phần công khai, theo dòng)

- Bài báo: https://arxiv.org/abs/2406.09630 (NeurIPS 2024, Datasets & Benchmarks) · mã: https://github.com/MehreenMehreen/muharaf
- Nguồn tải: https://huggingface.co/datasets/aamijar/muharaf-public (= public_line_images của https://zenodo.org/records/11492215)
- Nội dung: dòng chữ VIẾT TAY tiếng Ả Rập cắt từ ảnh MÀU trang lưu trữ (Trung tâm Phoenix — Liban, Trung tâm Khayrallah),
  thế kỷ 19–21: thư từ, giấy tờ pháp lý / hành chính, sổ ghi chép, sổ nhà thờ. Giấy ố vàng, vết bẩn, giấy kẻ, đôi khi
  có con dấu / chữ ký. Ảnh dòng đã được đưa về cùng chiều cao 60 px.
- Giấy phép: **CC BY-NC-SA 4.0 — CHỈ PHI THƯƠNG MẠI** (đo / nghiên cứu được; KHÔNG dùng huấn luyện model bán cho khách).
- Nhãn có quy ước riêng của Muharaf (vd. dấu fatha đánh trên س: سَ) — khi chấm nên bỏ dấu nguyên âm.
- Baseer-Nakba đã học Muharaf (bước đầu) → điểm của nó trên bộ này có thể cao hơn thực tế.

{bang}

Cấu trúc: `<tập>/<mẫu>/input/<ảnh dòng>` · `<tập>/<mẫu>/output/nhan.txt`. Bảng đầy đủ: `danh_sach.csv`
(cột `trang`: các dòng cùng một trang). Xem nhanh: mở `xem_mau.html`. Tạo bằng `python -m htr_test.tai_muharaf`.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dich")
    ap.add_argument("--splits", default="train,validation,test")
    a = ap.parse_args()
    files = {s.strip(): FILES[s.strip()] for s in a.splits.split(",") if s.strip()}
    page = lambda fn: re.sub(r"-\d+$", "", Path(fn).stem)  # noqa: E731
    return tai(a.dich, REPO, files, NGUON, "Muharaf (NeurIPS 2024)", trang=page)


if __name__ == "__main__":
    sys.exit(main())
