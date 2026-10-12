"""postcorrect — LLM sửa lỗi + khoanh từ lỗi cho output OCR (dots.mocr) của chữ viết tay Ả Rập.

Module tách biệt: chỉ GỌI ocrbench (DotsAdapter, metrics, normalize), KHÔNG sửa code của ocrbench.
Mọi model chạy CỤC BỘ — không gửi chữ hay ảnh ra API ngoài. Xem postcorrect/README.md.
"""

__version__ = "0.1.0"
