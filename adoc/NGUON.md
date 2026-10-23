# adoc — bản chép pipeline của ocr-bench

Chép từ `khanhkhmt/arabic-doc-ocr`, nhánh `main`, commit `03e1e8e` (2026-10-19, lần đo 4 trang mẫu trên 2× T4),
để thí nghiệm của ocr-bench (htr_test/dot1.py, llm_sua.py…) chạy độc lập với repo demo: sửa arabic-doc-ocr không làm
đổi số đo ở đây, và ngược lại.

| ở đây | gốc trong arabic-doc-ocr | thay đổi |
|---|---|---|
| `config.py` | `arabic_doc_ocr/config.py` | thư mục riêng `~/.cache/ocr_bench_adoc` (biến `OCRB_ADOC_HOME`, `OCRB_KRAKEN_VENV`, `OCRB_KRAKEN_SEG_MODEL`); **#12:** `LINE_PAD_PCT = 50` |
| `lines.py` | `arabic_doc_ocr/lines.py` | biến môi trường `OCRB_KRAKEN_BIN`, `OCRB_KRAKEN_SEG_MODEL`; **#12:** `crop_poly(…, noi=0)` nới dòng theo chiều dọc |
| `dots_model.py` | `arabic_doc_ocr/dots_model.py` | tên thư mục symlink tạm `ocr_bench_adoc_models` |
| `pipeline.py` | cùng tên | **#12:** `Pipeline(…, line_pad_pct=config.LINE_PAD_PCT)` → cắt dòng Kraken bằng `crop_poly(noi=…)`; `info["line_pad_pct"]` |
| `htr_model.py`, `text.py`, `_vendor/` | cùng tên | không đổi (chỉ docstring) |
| `evaluate.py` | `scripts/evaluate.py` | không đổi |
| `requirements.txt` | `requirements.txt` | không đổi (giữ y nguyên phiên bản → cùng số) |
| `trang_mau/page_N/` | `examples/page_N/` | không đổi |
| `mau_ket_qua/` | `results/two_gpus/` (+ `results/hardware.txt`) | kết quả mốc của lần đo 2026-10-19 |
| `__main__.py` | `arabic_doc_ocr/cli.py` (lệnh check, download) | thêm `kiem` (dưới); bỏ page / line / web |

Model (dots.mocr, Baseer-Nakba, adapter ft3/ft4) nằm trong cache Hugging Face chung của máy — đó là trọng số, không
phải code; cùng tên repo như gốc.

## Kiểm bản chép

    /kaggle/working/venvs/adoc/bin/python -m adoc kiem --out /kaggle/working/kiem_adoc     # 2 GPU ~25 phút

Đọc lại 4 trang mẫu y như lần đo (dots trên cuda:0, ft3/ft4 trên cuda:1, không offload), chấm bằng `evaluate.py`,
so với `mau_ket_qua/eval.json`. ĐẠT (`✔ ADOC KHỚP MỐC`) khi CẢ 16 số (4 trang × chữ chính / dots / ft3 / ft4, % ký tự,
2 chữ số thập phân) bằng đúng mốc — lần đo 2026-10-19 cho cùng 16 số ở mọi chế độ GPU (two_gpus, one_gpu_unload,
one_gpu_cpu), nên lệch = bản chép hoặc môi trường khác, không phải ngẫu nhiên. Ghi `<out>/page_N_page.json` (cùng
dạng với arabic-doc-ocr, dùng được cho llm_sua.py) + `<out>/kiem.json` + `<out>/kiem.md`.

`kiem` luôn đọc với nới dòng 0 % (`--noi 0`, mặc định của lệnh) — đúng cách cắt của lần đo mốc — nên vẫn kiểm được
bản chép sau khi sản phẩm đã đổi mặc định sang 50 %.

## Đã đưa vào: #12 nới khung dòng Kraken 50 % (anh duyệt 2026-10-23)

Đợt 1, #12 (ft3, dòng Kraken, 66 trang Muharaf test, % ký tự): 0 % 63.6 · 15 % 65.6 · 30 % 66.7 · **50 % 67.2**;
trang 2 của khách 72.2 → 78.0. Cách cắt = `cat_no` của htr_test/dot1.py (tự kiểm so từng pixel). Đo cả pipeline:

    /kaggle/working/venvs/adoc/bin/python -m adoc kiem --noi 50 --out /kaggle/working/do_noi50   # in "✔ ĐO NỚI 50 % XONG"

(chay_dot1.sh tự chạy sau bộ B → `results-htr/dot1/do_noi50.md`, mục 5c của tom_tat.md). Chưa chuyển sang
arabic-doc-ocr: chờ số đo cả pipeline.

## Muốn đổi pipeline

Sửa ở đây, đo trong ocr-bench; thắng thì mới chuyển sang arabic-doc-ocr. Sửa file nào trong bảng trên thì ghi vào bảng.
