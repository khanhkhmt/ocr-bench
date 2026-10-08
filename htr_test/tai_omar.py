"""Tải bộ dòng chữ viết tay Omar Al-Saleh (NAKBA NLP 2026) và tách thành thư mục để xem / chấm.

    python -m htr_test.tai_omar ~/du_lieu_omar_al_saleh [--splits train,test,blind_test]

Bộ gated: tài khoản Hugging Face phải bấm "Agree and access repository" tại
https://huggingface.co/datasets/U4RASD/omar-al-saleh-manuscripts-segments ; token lấy từ biến HF_TOKEN hoặc
`hf auth login`. Giấy phép CC BY 4.0. Cấu trúc kết quả: xem htr_test/tai_du_lieu.py.
"""

from __future__ import annotations

import argparse
import sys

from htr_test.tai_du_lieu import tai

REPO = "U4RASD/omar-al-saleh-manuscripts-segments"

NGUON = """# Omar Al-Saleh Manuscripts — Segments (NAKBA NLP 2026)

- Nguồn: https://huggingface.co/datasets/U4RASD/omar-al-saleh-manuscripts-segments (gated: bấm đồng ý điều khoản)
- Nội dung: dòng chữ VIẾT TAY tiếng Ả Rập, hồi ký của Omar Al-Saleh (Palestine, 1951–1965), 16 tài liệu ~6.395 trang;
  cắt dòng + nhãn do chuyên gia kiểm tra. Kiểu chữ Ruq'ah / Naskh, giấy kẻ dòng, ảnh scan đen trắng.
- Giấy phép: **CC BY 4.0** (dùng thương mại được, phải ghi nguồn — trích dẫn trong README_goc.md).
- Nhãn đã chuẩn hoá chính tả (thêm hamza: ان → أن/إن; bỏ ngoặc quanh số) — khi chấm nên gộp alef/hamza.
- Ketaba-OCR-LoRA và Baseer-Nakba đã HỌC train (+ test) → đánh giá công bằng CHỈ trên `blind_test/`.
- KHÁC tài liệu của khách: ảnh scan đen trắng, nền sạch, không ố vàng / con dấu / biểu mẫu (xem bộ Muharaf).

{bang}

Cấu trúc: `<tập>/<mẫu>/input/<ảnh dòng>` · `<tập>/<mẫu>/output/nhan.txt`. Bảng đầy đủ: `danh_sach.csv`.
Xem nhanh: mở `xem_mau.html` bằng trình duyệt. Tạo bằng `python -m htr_test.tai_omar` (repo ocr-bench, nhánh thu-2-model-htr).
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dich")
    ap.add_argument("--splits", default="train,test,blind_test")
    a = ap.parse_args()
    files = {s.strip(): [f"data/{s.strip()}-00000-of-00001.parquet"] for s in a.splits.split(",") if s.strip()}
    return tai(a.dich, REPO, files, NGUON, "Omar Al-Saleh (NakbaNLP 2026)")


if __name__ == "__main__":
    sys.exit(main())
