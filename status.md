# Trạng thái ocrbench

- Cập nhật: **2026-10-05 04:46 UTC** · chẩn đoán dots xong
- Máy: `2b44e3deaaa3` · GPU: Tesla T4, Tesla T4
- Code: `4b0cd19` · Dấu vân tay dữ liệu: `aa8fdd44e1715845`
- Đang chạy: (không có)

## Split `dev` (1051 mẫu)

| Model | Trạng thái | Đã chạy | Lỗi | CER norm (TB các mẫu đã chạy) | s/mẫu | VRAM đỉnh | Lần chạy cuối |
|---|---|---:|---:|---:|---:|---:|---|
| dots_mocr | ⚠ dừng giữa chừng (chưa kết thúc lần nào, có thể do sập) | 1/1051 | 0 | 96.8% | 22.46 | — | — |
| easyocr | ■ đã dừng | 1051/1051 | 0 | 35.9% | 3.36 | 13.3 GB | 2026-10-02T04:43:28+00:00 |
| sherif_handwriting | ■ đã dừng | 923/1051 | 1 | 19.8% | 23.52 | 13.0 GB | 2026-10-02T09:35:19+00:00 |
| sherif_handwriting__long | ⚠ dừng giữa chừng (chưa kết thúc lần nào, có thể do sập) | 6/1051 | 0 | 102.6% | 581.69 | — | — |
| sherif_handwriting__pp__long | ■ đã dừng | 24/1051 | 0 | 20.9% | 269.57 | 13.5 GB | 2026-10-05T03:31:36+00:00 |
| sherif_handwriting__sl__long | ■ đã dừng | 24/1051 | 5 | 59.3% | 366.44 | 0.0 GB | 2026-10-03T11:09:14+00:00 |
| tesseract | ■ đã dừng | 1051/1051 | 0 | 37.8% | 2.73 | — | 2026-10-02T03:36:45+00:00 |

CER norm theo nhóm (`số mẫu đã chạy: CER`):

| Nhóm | dots_mocr | easyocr | sherif_handwriting | sherif_handwriting__long | sherif_handwriting__pp__long | sherif_handwriting__sl__long | tesseract |
|---|---:|---:|---:|---:|---:|---:|---:|
| pub_handwriting_ar | — | 128: 49.3% | 128: 7.2% | — | — | — | 128: 74.4% |
| pub_handwriting_en | — | 63: 81.3% | 63: 10.9% | — | — | — | 63: 61.7% |
| pub_printed_ar | — | 63: 28.4% | 63: 41.1% | — | — | — | 63: 32.1% |
| pub_tables_ar | — | 58: 42.5% | 58: 49.5% | — | — | — | 58: 52.4% |
| pub_tables_en | 1: 96.8% | 61: 81.1% | 61: 46.3% | — | — | — | 61: 89.6% |
| syn_degraded | — | 61: 31.5% | 61: 40.4% | — | — | — | 61: 32.2% |
| syn_form_ar | — | 60: 20.4% | 60: 21.8% | — | — | — | 60: 35.2% |
| syn_form_en | — | 72: 45.7% | 72: 1.9% | — | — | — | 72: 11.7% |
| syn_invoice_ar | — | 57: 33.3% | 57: 27.5% | — | — | — | 57: 42.0% |
| syn_invoice_en | — | 62: 9.2% | 62: 2.0% | — | — | — | 62: 19.1% |
| syn_invoice_mixed | — | 57: 38.2% | 57: 29.0% | — | — | — | 57: 39.5% |
| syn_longtable | — | 61: 52.3% | — | 6: 102.6% | 12: 38.9% | 12: 82.6% | 61: 54.7% |
| syn_longtext | — | 67: 10.3% | — | — | 12: 2.9% | 12: 36.1% | 67: 3.0% |
| syn_text_ar | — | 60: 7.6% | 60: 5.2% | — | — | — | 60: 7.0% |
| syn_text_en | — | 57: 14.9% | 57: 1.0% | — | — | — | 57: 1.9% |
| syn_text_mixed | — | 64: 13.7% | 64: 11.5% | — | — | — | 64: 14.8% |

Số liệu ở đây là CER tính nhanh trên các mẫu đã chạy (chưa có TEDS / ô đúng vị trí). Số liệu chính thức: `runs/<split>/_report/report.md` và `decision_*.md`.

## Mục nhật ký gần nhất (EXPERIMENTS.md)

## 2026-10-05 04:42 UTC — Chẩn đoán dots

### A) A_fp16
- Dòng ✔ của lệnh: `✔ inference/samples/01_hoa_don_tieng_anh.png: 1 trang → /kaggle/working/diag/A_fp16/01_hoa_don_tieng_anh/`
- Thời gian: real 0m49.103s (user 0m51.079s, sys 0m6.137s)
- `head -c 1500` file .md:
```markdown
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKIAAACLCAIAAABtM9WyAAABWElEQVR4nO3RgQkAIRDAsPf33/ncQsEmExS6Zubjdf/tAE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOcHmBJsTbE6wOWED+hUEExfG8/AAAAAASUVORK5CYII=)
```

### B) B_fp32
- Dòng ✔ của lệnh: `✔ inference/samples/01_hoa_don_tieng_anh.png: 1 trang → /kaggle/working/diag/B_fp32/01_hoa_don_tieng_anh/`
- Thời gian: real 1m7.395s (user 1m7.266s, sys 0m11.752s)
- `head -c 1500` file .md:
```markdown
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAkcAAAHYCAIAAADI+durAACUfUlEQVR4nO39f1ATabow/F/nO2qn1ElPR23AqgStNYBlAjNrFPfhh/WQgdkNYg0oOxvEOqLUHBTPg8I76yM8hUJ9dV92Dgr7iuZMOcJbIjkzjmHKkczqGp5SyHNE4xklsRyJWw5JlZKoFJ0Zpdtxy/eP/CC/AUXFnutTW7Vj6HTf/eu+uu/7uu/807NnzwAhhBDihf/f6y4AQgghNGUwqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/sCohhBCiD8wqiGEEOIPjGoIIYT4A6MaQggh/s
```

### C) C_nho
- Dòng ✔ của lệnh: `✔ /kaggle/working/testset/images/pub_tables_en/pubtabnet__598044.png: 1 trang → /kaggle/working/diag/C_nho/pubtabnet__598044/  (⚠ 1 trang JSON hỏng)`
- Thời gian: real 0m53.758s (user 0m56.053s, sys 0m5.774s)
- `head -c 1500` file .md:
```markdown
The 2024 National50000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000]
```

### D) D_nho_fitz
- Dòng ✔ của lệnh: `✔ /kaggle/working/testset/images/pub_tables_en/pubtabnet__598044.png: 1 trang → /kaggle/working/diag/D_nho_fitz/pubtabnet__598044/  (⚠ 1 trang JSON hỏng)`
- Thời gian: real 1m39.952s (user 1m42.044s, sys 0m5.955s)
- `head -c 1500` file .md:
```markdown
I am a student at the University of California, Berkeley.

I am a first-year student in the Computer Science program.

My name is John Smith.

I am from California, USA.

I am 19 years old.

My major is Computer Science.

I am interested in software engineering.

I have taken several computer science courses.

For example, I have taken

Introduction to Programming.

Introduction to Data Structures.

Algorithms.

Software Design.

Computer Architecture.

Operating Systems.

Database Systems.

C 编程语言基础.

C++ 语言基础.

计算机网络.

人工智能基础.

计算机图形学.

算法与数据结构.

软件工程基础.

软件开发实践.

软件质量保证.

软件测试.

软件设计模式.

软件开发工具.

软件开发环境.

软件开发标准.

软件开发流程.

软件开发管理.

软件开发文档.

软件开发工具.

软件开发环境.

软件开发标准.

软件开发流程.

软件开发管理.
```
