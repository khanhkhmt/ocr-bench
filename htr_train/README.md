# Huấn luyện tiếp Baseer-Nakba (LoRA) — chữ tay Ả Rập trên giấy cũ màu

Mục tiêu: **Muharaf test ≥ 85%** đúng ký tự (Baseer gốc 79,1%) mà **Omar blind_test vẫn ≥ 93%** (Baseer gốc 93,3%).
Chấm bằng `htr_test/eval_lines.py`, 500 dòng cố định (seed 0) mỗi tập. Hai tập chấm KHÔNG có trong dữ liệu huấn luyện.

| File | Việc |
|---|---|
| `du_lieu.py` | gom Omar train+test, Muharaf train(+val), AraMS-28k, KHATT → `train.jsonl` / `val.jsonl`; bỏ dòng trùng nhãn tập chấm; `--giu-muharaf tu_dong` giữ riêng tập "người viết lạ" |
| `lam_cu.py` | làm cũ ảnh: giấy ố, vết bẩn, giấy kẻ, mực thấm mặt sau, con dấu / vân tay màu, chụp điện thoại |
| `huan_luyen.py` | LoRA (ngôn ngữ ± ảnh), fp16 + GradScaler trên T4, lưu checkpoint / chạy lại đi tiếp, chấm val định kỳ |
| `guong_hf.py` | `--hf-ckpt`: gương checkpoint lên repo HF riêng tư — server sập thì phiên sau tự tải về chạy tiếp |

## Các bản đã huấn luyện

Chung: rsLoRA r=32, α=64, dropout 0,05; ngôn ngữ q/k/v/o/gate/up/down (LR 1e-4); ảnh qkv/proj/mlp (LR 2e-5);
16 dòng / bước (lô 2 × tích luỹ 8), warmup 100 + cosine; loss chỉ trên token trả lời; làm cũ 50% ảnh; seed 0.

| Bản | Phần ảnh | Bước | Trọng số lấy mẫu (muharaf / omar / arams / khatt) | Omar | Muharaf | Ở đâu |
|---|---|---|---|---|---|---|
| Baseer gốc | — | — | — | 93,3% | 79,1% | `Misraj/Baseer__Nakba` |
| ft1 | có | 600 | 2 / 1 / 1 / 1 | 92,0% | 89,1% | `khanh99/htr-baseer-nakba-ft/ft1` (công khai) |
| **ft1 độ mạnh 0,5** | có | 600 | 2 / 1 / 1 / 1 | **93,4%** | **87,0%** | như trên + `--lora-scale 0.5` — **bộ đọc chính** |
| ft2 | **không** | 600 | 2 / 1 / 1 / 1 | 92,3% | 87,3% | `khanh99/htr-baseer-nakba-ft/ft2` (công khai) — kiểm chéo tô vàng |
| **ft3** | có | 2000 | 2 / **2** / 1 / 1 | 93,4% | 91,4% | `khanh99/htr-baseer-nakba-ft/ft3` (công khai) — **bộ đọc chính** (web `app_ft.py`) |
| ft4 | có | 2000 | 2 / 1 / 1 / 1 | 92,8% | 92,0% | `khanh99/htr-baseer-nakba-ft/ft4` (công khai) — kiểm chéo tô vàng |

ft3 và ft4 chỉ khác trọng số Omar: ft4 = ft1 chạy lâu hơn; ft3 cho thấy Omar gấp đôi để thử bớt "quên" Omar.
Độ mạnh adapter (kiểu WiSE-FT): 1 = như huấn luyện, 0,5 = nửa đường về Baseer gốc — đổi được lúc đọc, không cần huấn luyện lại.

Lưu ý khi đọc số: 98% dòng Muharaf test thuộc các tài liệu (người viết) có trong train → mức tăng trên chữ của khách có thể
nhỏ hơn. Vì vậy có tập **người viết lạ** (`--giu-muharaf tu_dong`, dưới đây). Baseer gốc / ft1 / ft2 đã học các dòng của
tập này, nên trên tập đó phép so nghiêng về phía chúng.

## Chạy (Kaggle 2× T4, venv dots của htr_test/start.sh)

Lệnh dài nên chạy qua hộp thư (`htr_test/hop_thu.py`, xem htr_test/README.md): lỗi tự báo lên GitHub, lỗi mạng tự chạy lại.

```bash
cd /kaggle/working/ocr-bench; P=/kaggle/working/venvs/dots/bin/python
export HF_TOKEN=... GITHUB_TOKEN=...      # đặt bằng Kaggle Secrets / read -rs, KHÔNG dán vào prompt

# 1) dữ liệu (~8 GB, 30–40 phút; cần HF_TOKEN đã đồng ý điều khoản bộ Omar)
python3 -m htr_test.hop_thu viec dl --log /kaggle/working/dl.log --xong "✔ train" -- \
    $P -m htr_train.du_lieu /tmp/htr_data --giu-muharaf tu_dong
cat /tmp/htr_data/thong_ke.md; md5sum /tmp/htr_data/train.jsonl

# 2) huấn luyện (~11,7 s/bước trên T4 khi có phần ảnh → 2000 bước ≈ 6,5 giờ)
python3 -m htr_test.hop_thu viec ft3 --log /kaggle/working/ft3.log --xong "✔ XONG HUẤN LUYỆN" -- \
    $P -m htr_train.huan_luyen --data /tmp/htr_data --out /kaggle/working/ft3 --gpu 0 --vision 1 --max-steps 2000 \
    --trong-so muharaf=2,omar=2,arams=1,khatt=1 --hf-ckpt khanh99/htr-ckpt --push

# 3) chấm (Omar + Muharaf người viết lạ + Muharaf test, 500 dòng mỗi tập; + một model đối chứng trên tập người viết lạ)
python3 -m htr_test.hop_thu viec c3 --log /kaggle/working/c3.log --xong "✔ XONG CHẤM ft3" -- \
    bash htr_test/cham_ft.sh 0 ft3 baseer
```

| Tham số `huan_luyen` | Ý nghĩa |
|---|---|
| `--vision 1/0` | có / không LoRA phần ảnh |
| `--max-steps N` | số bước cập nhật (16 dòng / bước) |
| `--trong-so` | tỉ lệ lấy mẫu theo nguồn |
| `--hf-ckpt <repo>` | mỗi lần lưu (`--save-every 200`) đẩy ckpt + `best/` + nhật ký lên repo HF riêng tư (giữ 2 ckpt mới nhất); thư mục `--out` trống → tự tải ckpt mới nhất về chạy tiếp. Dữ liệu khác lúc lưu (md5 train.jsonl) → `✘ LỖI` |
| `--push` | nhật ký + bảng val lên nhánh GitHub `results-htr/<tên out>/tom_tat.md` |

Kết quả: `<out>/nhat_ky.jsonl`, `<out>/ckpt-*`, model tốt nhất theo val `<out>/best`.
Log có "lô tràn fp16 (đã tự bỏ qua — bình thường, KHÔNG phải lỗi)" là bình thường; loss nan suốt 10 bước → `✘ LỖI` và dừng.

**Server sập giữa chừng:** phiên mới làm lại bước 1 (md5 train.jsonl phải giống) rồi chạy lại đúng lệnh bước 2 — tự tải
checkpoint từ HF, mất tối đa 200 bước.

## Chấm một adapter bằng tay

```bash
$P -m htr_test.eval_lines --out /kaggle/working/htr_eval_n500 --split blind_test --n 500 \
    --models baseer_ft3 --lora hf:khanh99/htr-ckpt/ft3/best --gpu 0 --push                 # Omar
$P -m htr_test.eval_lines --out /kaggle/working/htr_eval_giu_lai_n500 --data /tmp/htr_data/giu_lai_muharaf \
    --split giu_lai --n 500 --models baseer_ft3 --lora hf:khanh99/htr-ckpt/ft3/best --gpu 0 --push   # người viết lạ
$P -m htr_test.eval_lines --out /kaggle/working/htr_eval_muharaf_n500 --data /tmp/htr_data/cham_muharaf \
    --split test --n 500 --models baseer_ft1_s050 --lora ft1 --lora-scale 0.5 --gpu 1 --push  # Muharaf, độ mạnh 0,5
```
`--lora`: thư mục có sẵn, `ft1` / `ft2` (repo công khai) hoặc `hf:<chủ>/<repo>/<thư mục con>`.
Độ mạnh khác 1 thì tên model phải có `_sNNN` (vd. `_s050`) để không trộn kết quả.
Kết quả: nhánh `results-htr/<tên out>/tom_tat.md`, `chi_tiet.csv`, `xem_ket_qua.html`.

## Chọn bản nào làm bộ đọc chính

Thay ft1@0,5 chỉ khi bản mới **hơn trên tập người viết lạ** mà **Omar vẫn ≥ 93%**. Omar tụt thì thử độ mạnh 0,5 / 0,75
(`--lora-scale`) trước khi bỏ. Bản được chọn → đưa adapter lên repo công khai `khanh99/htr-baseer-nakba-ft`, thêm vào
`HF_FT_ADAPTERS` (`htr_test/models.py`) và `FT_SCALE` (`htr_test/app.py`).
