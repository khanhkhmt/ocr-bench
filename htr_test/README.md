# Thử model đọc chữ viết tay theo dòng — nhánh `thu-2-model-htr`

Bố cục: **dots.mocr** (như web demo). Đọc chữ: hai model chỉ nhận **ảnh một dòng** → web tách dòng trong từng khối
chữ của dots rồi cho model đọc từng dòng.

| Model | Gốc | Huấn luyện trên | Tác giả công bố |
|---|---|---|---|
| [Baseer-Nakba](https://huggingface.co/Misraj/Baseer__Nakba) | Baseer (Qwen2.5-VL-3B), bf16 — **CC BY-NC-SA (phi thương mại)** | Muharaf → Omar Al-Saleh (cả encoder) → trộn SLERP | **hạng 1 NAKBA 2026**: CER 7,9% · WER 24,4% |
| [Ketaba-OCR-LoRA](https://huggingface.co/HassanB4/Ketaba-OCR-LoRA) | LoRA trên sherif1313/Arabic-English-handwritten-OCR-v3 (Qwen2.5-VL-3B), 4-bit | dòng bản thảo viết tay 1951–1965, Ruq'ah / Naskh (hồi ký Omar Al-Saleh, NakbaNLP 2026) | CER 8,19% · WER 25,88% |
| [ArTrOCR-HTR](https://huggingface.co/BushraAlmod03/ArTrOCR-HTR) | microsoft/trocr-base-handwritten | chữ tổng hợp → 11.000 dòng KHATT | CER 12,61% (KHATT) |
| sherif gốc | Ketaba TẮT LoRA | — | để so LoRA giúp bao nhiêu |
| **Baseer ft1 độ mạnh 0,5** (bộ đọc chính) | Baseer-Nakba + LoRA tự huấn luyện (`khanh99/htr-baseer-nakba-ft/ft1`, công khai) | Muharaf + Omar + AraMS + KHATT, làm cũ ảnh — xem htr_train/README.md | Omar 93,4% · Muharaf 87,0% đúng ký tự (500 dòng) |
| Baseer ft2 (kiểm chéo) | như trên, chỉ LoRA ngôn ngữ (`…/ft2`) | như trên | Omar 92,3% · Muharaf 87,3% |

Gọi model đúng như code mẫu của tác giả (`htr_test/models.py`).

Web: ft1@0,5 đọc chính; ft2 đọc lại cùng dòng — dòng hai bản đọc KHÁC nhau được tô vàng trong DOCX (89% lỗi trên Omar,
97% trên Muharaf nằm ở các dòng này). ft1 / ft2 / Baseer gốc dùng CHUNG một nền Baseer trên GPU (đổi adapter khi đọc).
Độ mạnh từng adapter: `FT_SCALE` trong `app.py`.

## Chạy
```bash
tmux new -d -s htr "cd /kaggle/working/ocr-bench && bash htr_test/start.sh 2>&1 | tee /kaggle/working/htr.log"
# VS Code: Ports → Forward 7861 → http://localhost:7861
```
VRAM (T4 15 GB): dots ~7–8 GB + Ketaba 4-bit ~3 GB + ArTrOCR ~1,3 GB. Nút "Giải phóng model đọc dòng" trả VRAM.

## Tách dòng (`htr_test/lines.py`)
- Chiếu ngang (mặc định, nhanh): bỏ đường kẻ của giấy kẻ dòng, tách dòng dính, gộp dấu chấm lẻ.
- Kraken blla (chính xác hơn với chữ tay cổ) nếu có `/kaggle/working/venvs/kraken/bin/kraken`
  (tạo bằng `experiments/real_docs_probe/run_kraken.sh`), không có thì tự dùng chiếu ngang.

## Tải bộ dữ liệu về xem
```bash
python -m htr_test.tai_omar ~/du_lieu_omar_al_saleh   # chữ tay Palestine 1951–65, scan đen trắng — CC BY 4.0, gated (HF_TOKEN)
python -m htr_test.tai_muharaf ~/du_lieu_muharaf      # chữ tay Liban TK 19–21, ảnh MÀU giấy cũ, có giấy tờ pháp lý — CC BY-NC-SA (phi thương mại)
```
Ra `<tập>/<mẫu>/input|output`, `danh_sach.csv`, `NGUON.md`, `xem_mau.html`.

## Benchmark gộp: các model × 2 bộ (một lệnh)
```bash
export HF_TOKEN=... GITHUB_TOKEN=...
/kaggle/working/venvs/dots/bin/python -m htr_test.benchmark --push   # mặc định: baseer,ketaba,dots × Omar blind_test + Muharaf test, cả tập
```
Ra `/kaggle/working/htr_benchmark/BENCHMARK_HTR.md` (bảng % đúng mỗi model × mỗi bộ, chênh lệch khi sang giấy cũ), cập nhật sau
mỗi bước và đẩy lên nhánh `results-htr`. Chạy lại = đi tiếp.

## Chấm bằng số trên blind_test của Omar Al-Saleh (`htr_test/eval_lines.py`)
Baseer-Nakba và Ketaba đã học train (+test) của bộ này → chỉ chấm trên `blind_test` (2.671 dòng).
```bash
export HF_TOKEN=...   # tài khoản đã bấm đồng ý điều khoản bộ U4RASD/omar-al-saleh-manuscripts-segments
/kaggle/working/venvs/dots/bin/python -m htr_test.eval_lines --out /kaggle/working/htr_eval --models baseer,ketaba,dots --n 500 --push
```
Chấm trên Muharaf (giấy cũ màu, gần hình thức tài liệu của khách hơn): tải `--splits test` rồi thêm `--data <thư mục> --split test --out /kaggle/working/htr_eval_muharaf`.
Chạy lại = đi tiếp (kể cả khi Colab mất ổ: `--push` tự kéo phần đã chấm từ nhánh `results-htr` về). `--push` đẩy jsonl + bảng tạm lên nhánh GitHub `results-htr` mỗi 10 phút và khi xong mỗi model (cần GITHUB_TOKEN). Kết quả: `tom_tat.md` (cả tập: **% đúng ký tự / từ**, CER/WER gốc và chuẩn hoá, tỉ lệ độ dài, số dòng dài/ngắn bất thường), `chi_tiet.csv` (**từng dòng**: nhãn, chữ mỗi model đọc, % đúng — mở bằng Excel), `xem_ket_qua.html` (như csv, kèm ảnh dòng).

## Chạy song song 2 GPU (Kaggle 2× T4) — vd. Ketaba trên Muharaf, cùng 500 dòng với benchmark n500
```bash
O=/kaggle/working/htr_eval_muharaf_n500; D=/kaggle/working/du_lieu_muharaf; PY=/kaggle/working/venvs/dots/bin/python
A="-m htr_test.eval_lines --out $O --data $D --split test --n 500 --models ketaba --push"
tmux new -d -s k0 "cd /kaggle/working/ocr-bench && $PY $A --shard 0/2 --gpu 0 2>&1 | tee -a /kaggle/working/k0.log"
tmux new -d -s k1 "cd /kaggle/working/ocr-bench && $PY $A --shard 1/2 --gpu 1 2>&1 | tee -a /kaggle/working/k1.log"
# xong cả hai → gộp bảng / chi tiết của thư mục này (không chấm gì thêm) và đẩy lên results-htr:
cd /kaggle/working/ocr-bench && $PY $A
# bảng benchmark gộp 2 bộ (cần đủ kết quả cả Omar + Muharaf ở máy chạy): python -m htr_test.benchmark --tag n500 --n 500 --chi-bang --push
```
Mỗi phần ghi `<model>.shard<i>of<k>.jsonl`; bảng / chi tiết tự gộp mọi phần; chạy lại = đi tiếp.

## Chấm adapter tự huấn luyện (`cham_ft.sh`) và lấy lại kết quả cũ (`lay_kq_cu.sh`)
```bash
bash htr_test/cham_ft.sh <gpu> <ft3|ft4|…> <baseer|ft1s050>
```
Chấm `hf:khanh99/htr-ckpt/<ft>/best` trên Omar blind_test → Muharaf người viết lạ (`/tmp/htr_data/giu_lai_muharaf`) →
Muharaf test (`/tmp/htr_data/cham_muharaf`), 500 dòng mỗi tập, rồi model đối chứng trên tập người viết lạ. Kết thúc in
`✔ XONG CHẤM <ft>`. Cần `/tmp/htr_data` từ `htr_train.du_lieu --giu-muharaf tu_dong`.
`bash htr_test/lay_kq_cu.sh htr_eval_n500 htr_eval_muharaf_n500`: chép các `<model>.jsonl` đã chấm từ `results-htr` về
`/kaggle/working/` (không ghi đè) — phiên Kaggle mới vẫn có đủ model cũ trong bảng tóm tắt.

## Hộp thư: giám sát server + nhận lệnh qua GitHub (`hop_thu.py`, nhánh `dieu-khien`)
Server Kaggle không có người ngồi canh → mọi việc dài đăng ký qua hộp thư.

**Trên server** (python hệ thống, chạy ngầm):
```bash
tmux new -d -s hop_thu -e GITHUB_TOKEN="$GITHUB_TOKEN" -e HF_TOKEN="$HF_TOKEN" \
  "cd /kaggle/working/ocr-bench && python3 -m htr_test.hop_thu chay --phut 20 --kiem-lenh 3 2>&1 | tee -a /kaggle/working/hop_thu.log"
python3 -m htr_test.hop_thu viec <tên> --log /kaggle/working/<tên>.log --xong "<dòng báo xong>" -- <lệnh…>
```
- mỗi `--phut` phút đẩy `trang_thai/STATUS.md` (GPU, phiên tmux, commit code, dòng cuối log — đã che token);
- mỗi `--kiem-lenh` phút xem các việc: xong → ghi XONG; chết vì **lỗi mạng** → tự chạy lại đúng lệnh (tối đa 2 lần,
  huấn luyện / chấm tự đi tiếp); lỗi khác (hết VRAM, `✘ LỖI`, lỗi code) → đẩy ngay `su_co/<giờ>-<việc>.md` (40 dòng cuối
  log) và chờ lệnh;
- chỉ nhận 5 lệnh cố định từ `lenh/LENH.md`: `keo_code`, `chay_lai <việc>`, `dung <việc>`, `log <việc> [n]`, `trang_thai`
  — không có lệnh shell tuỳ ý. Phiên mới không chạy lại lệnh cũ.

**Trên máy điều khiển** (thư mục repo, có quyền push):
```bash
python -m htr_test.hop_thu doc                          # trạng thái + sự cố + kết quả lệnh mới nhất
python -m htr_test.hop_thu theo_doi                     # chạy mãi, có sự cố / kết quả lệnh → thông báo desktop
python -m htr_test.hop_thu lenh keo_code "chay_lai c3"  # sửa code xong → server kéo code, chạy lại việc c3
```
