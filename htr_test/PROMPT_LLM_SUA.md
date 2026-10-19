# PROMPT CHO AGENT TRÊN SERVER KAGGLE — đo hệ thống + thử LLM sửa lỗi OCR

Bạn là agent chạy trên server Kaggle (2× T4). Làm ĐÚNG từng bước dưới đây, theo thứ tự, chép lệnh NGUYÊN VĂN.
Bạn KHÔNG thiết kế thí nghiệm, KHÔNG sửa code, KHÔNG đổi tham số: mọi thứ đã viết sẵn trong script.
Việc của bạn: chạy lệnh, chờ, kiểm tra đúng điều kiện ghi ở mỗi bước, báo cáo.

Server sập / khởi động lại giữa chừng → làm lại TỪ BƯỚC 0. Mọi bước chạy lại đều an toàn: code tự lấy lại, run_all.sh
đo lại từ đầu, llm_sua tự lấy phần đã xong từ GitHub và đi tiếp.

## LUẬT CỨNG (vi phạm = dừng ngay)

1. Token (`GITHUB_TOKEN`, `HF_TOKEN`) CHỈ nằm trong biến môi trường. CẤM in ra (`echo $GITHUB_TOKEN`, `env`,
   `printenv`, `set`), CẤM ghi vào file hay `.git/config`. Muốn biết có token chưa thì chỉ dùng `echo ${GITHUB_TOKEN:+CÓ}`.
2. CẤM `pkill`, `killall`, `kill -9` theo tên. Chỉ được `tmux kill-session -t <tên>` với các phiên do CHÍNH BẠN tạo
   trong prompt này: `hop_thu`, `adoc`, `cai_llm`, `llm_thu`, `llm`.
3. CẤM cài, gỡ hay nâng cấp torch / CUDA / transformers bằng tay (`pip install torch…`, `pip install -U transformers`…).
   Chỉ các script `install.sh`, `cai_llm.sh` được cài gói.
4. CẤM sửa bất kỳ file code nào trong `/kaggle/working/ocr-bench` và `/kaggle/working/arabic-doc-ocr`
   (không `sed -i`, không sửa tay, không `git commit` code). Code sai → báo cáo rồi DỪNG.
5. CẤM mở ngrok mới, link chia sẻ Gradio, Google Drive, hay đưa dữ liệu lên bất kỳ dịch vụ nào khác GitHub (chỉ qua
   các script có sẵn).
6. CẤM thêm, bớt hay đổi model, cách sửa, trang, ngưỡng. CẤM chạy lại thí nghiệm "cho đẹp số".
7. Lệnh nào chạy lâu hơn 2 phút PHẢI chạy bằng `hop_thu viec` (trong tmux), không chạy trực tiếp.
8. Gặp lỗi: dán NGUYÊN VĂN 30 dòng cuối log (`tail -n 30 <log>`) vào tin nhắn, dùng mẫu tin nhắn ở cuối, rồi DỪNG.
   KHÔNG tự sửa, KHÔNG thử cách khác, KHÔNG chạy lại (trừ khi bước đó cho phép).
9. Không gõ lại chữ Ả Rập bằng tay. Khi báo cáo thì chép nguyên văn file (`cat`).
10. Chờ bằng `sleep 600` (10 phút), rồi kiểm tra. Mỗi lần kiểm tra chỉ chạy các lệnh kiểm tra ghi trong bước.

## BƯỚC 0 — kiểm tra máy

```bash
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
df -h /kaggle/working /tmp | tail -2
for v in GITHUB_TOKEN HF_TOKEN; do
  if [ -z "${!v:-}" ] && tmux show-environment -g "$v" >/dev/null 2>&1; then export "$v=$(tmux show-environment -g "$v" | cut -d= -f2-)"; fi
done
echo "GITHUB_TOKEN: ${GITHUB_TOKEN:+CÓ}  HF_TOKEN: ${HF_TOKEN:+CÓ}"
```

ĐẠT khi: thấy 2 dòng GPU `Tesla T4` và `GITHUB_TOKEN: CÓ`. HF_TOKEN không bắt buộc, vì mọi model đều công khai.
- Thiếu `GITHUB_TOKEN` → gửi MẪU A rồi DỪNG.
- Chỉ có 1 GPU → vẫn làm tiếp, nhưng ghi nhớ: ở BƯỚC 5, `OCR_DIR` dùng `one_gpu_unload` thay cho `two_gpus`.

Mọi lệnh ở các bước sau phải chạy trong shell đã có `GITHUB_TOKEN`. Mở shell mới thì chạy lại vòng `for v in …` ở trên.

## BƯỚC 1 — lấy code + bật hộp thư (báo trạng thái server lên GitHub)

```bash
cd /kaggle/working
H="Authorization: Basic $(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 -w0)"
if [ -d ocr-bench/.git ]; then git -C ocr-bench -c http.extraHeader="$H" pull -q origin thu-2-model-htr
else git -c http.extraHeader="$H" clone -q -b thu-2-model-htr https://github.com/khanhkhmt/ocr-bench.git ocr-bench; fi
if [ -d arabic-doc-ocr/.git ]; then git -C arabic-doc-ocr pull -q origin main
else git clone -q https://github.com/khanhkhmt/arabic-doc-ocr.git arabic-doc-ocr; fi
git -C ocr-bench log --oneline -1; git -C arabic-doc-ocr log --oneline -1
tmux start-server
tmux set-environment -g GITHUB_TOKEN "$GITHUB_TOKEN"
[ -n "${HF_TOKEN:-}" ] && tmux set-environment -g HF_TOKEN "$HF_TOKEN"
tmux has-session -t hop_thu 2>/dev/null || tmux new -d -s hop_thu \
  "cd /kaggle/working/ocr-bench && python3 -m htr_test.hop_thu chay --phut 10 --kiem-lenh 5 2>&1 | tee -a /kaggle/working/hop_thu.log"
sleep 60; tail -n 5 /kaggle/working/hop_thu.log
```

ĐẠT khi: có 2 dòng commit và `hop_thu.log` không có `Traceback`. `hop_thu` lỗi → MẪU B (log = `/kaggle/working/hop_thu.log`).

Từ bước 2 trở đi, MỌI lệnh `hop_thu viec` chạy trong thư mục `/kaggle/working/ocr-bench`:
```bash
cd /kaggle/working/ocr-bench
```

## BƯỚC 2 — đo hệ thống arabic-doc-ocr (cài + đọc 4 trang mẫu ở mọi chế độ GPU), ~1,5–3 giờ

```bash
python3 -m htr_test.hop_thu viec adoc --log /kaggle/working/adoc_run_all.log --xong "✔ XONG TẤT CẢ" -- bash /kaggle/working/arabic-doc-ocr/scripts/run_all.sh
```

Kiểm tra mỗi 10 phút:
```bash
tail -n 3 /kaggle/working/adoc_run_all.log; tmux has-session -t adoc 2>/dev/null && echo "adoc ĐANG CHẠY" || echo "adoc ĐÃ THOÁT"
```

- Có dòng `✔ XONG TẤT CẢ` → sang BƯỚC 3.
- Có dòng `✘ LỖI ở bước` → MẪU B (log = `/kaggle/working/adoc_run_all.log`), DỪNG.
- `adoc ĐÃ THOÁT` mà không có hai dòng trên → chờ thêm 10 phút, vì hộp thư tự chạy lại khi lỗi mạng (tối đa 2 lần).
  Kiểm tra lại. Vẫn thoát, không chạy lại → MẪU B.
- Quá 4 giờ chưa xong → MẪU C, rồi CHỜ TIẾP (không dừng việc).
- Dòng `⚠`, cảnh báo, hay chế độ `one_gpu_both` báo lỗi hết bộ nhớ là BÌNH THƯỜNG. Không làm gì.

## BƯỚC 3 — đẩy kết quả đo hệ thống lên repo arabic-doc-ocr

```bash
cd /kaggle/working/arabic-doc-ocr && bash scripts/push_results.sh; cd /kaggle/working/ocr-bench
```

ĐẠT khi: có dòng `✔ ĐÃ ĐẨY`. Có `✘ LỖI` → dán nguyên văn toàn bộ output vào MẪU B, rồi VẪN LÀM TIẾP BƯỚC 4.
Kết quả đo đã nằm trên ổ, không mất.

## BƯỚC 4 — venv cho LLM, ~5–10 phút

```bash
python3 -m htr_test.hop_thu viec cai_llm --log /kaggle/working/cai_llm.log --xong "✔ VENV LLM SẴN SÀNG" -- bash htr_test/cai_llm.sh
```

Kiểm tra mỗi 2 phút: `tail -n 4 /kaggle/working/cai_llm.log`.
- Có `✔ VENV LLM SẴN SÀNG` → ghi lại nguyên văn dòng đó và dòng `torch … · transformers …` ngay trên nó, rồi sang BƯỚC 5.
- Có `✘ LỖI` → MẪU B, DỪNG.

## BƯỚC 5 — chạy thử nhanh với model nhỏ (1 trang), ~5–10 phút

Mục đích: kiểm tra code chạy được trên server trước khi chạy model lớn. Đây KHÔNG phải kết quả.

```bash
OCR_DIR=/kaggle/working/arabic-doc-ocr/results/two_gpus      # chỉ có 1 GPU → .../results/one_gpu_unload
ls $OCR_DIR/page_1_page.json $OCR_DIR/page_2_page.json $OCR_DIR/page_3_page.json $OCR_DIR/page_4_page.json
python3 -m htr_test.hop_thu viec llm_thu --log /kaggle/working/llm_thu.log --xong "✔ XONG TẤT CẢ" -- /kaggle/working/venvs/llm/bin/python -m htr_test.llm_sua --ocr $OCR_DIR --adoc /kaggle/working/arabic-doc-ocr --out /kaggle/working/llm_sua_thu --extra-model nho=Qwen/Qwen2.5-0.5B-Instruct --models nho --pages page_4 --push
```

- `ls` báo thiếu file → MẪU B (dán output `ls`), DỪNG.
- Kiểm tra mỗi 2 phút: `tail -n 5 /kaggle/working/llm_thu.log`.
- ĐẠT khi: có dòng `✔ XONG TẤT CẢ (1/1 model chạy được; lỗi: không)` và có dòng `✔ GITHUB: đã đẩy`.
  Sau đó chạy `cat /kaggle/working/llm_sua_thu/tom_tat.md`: phải có một dòng bảng bắt đầu bằng `| nho |`.
- Có `✘ LỖI`, hoặc `⚠ nho KHÔNG CHẠY ĐƯỢC`, hoặc `1/1` không xuất hiện → MẪU B, kèm thêm
  `cat /kaggle/working/llm_sua_thu/loi_nho.log` nếu file có. DỪNG.
- Điểm của model nhỏ tốt hay xấu đều KHÔNG quan trọng. Không bình luận, không chạy lại.

## BƯỚC 6 — thí nghiệm thật: 5 model × 3 cách sửa × 4 trang, ~2–4 giờ

```bash
python3 -m htr_test.hop_thu viec llm --log /kaggle/working/llm_sua.log --xong "✔ XONG TẤT CẢ" -- /kaggle/working/venvs/llm/bin/python -m htr_test.llm_sua --ocr $OCR_DIR --adoc /kaggle/working/arabic-doc-ocr --out /kaggle/working/llm_sua --push
```

(`OCR_DIR` giống hệt BƯỚC 5. Mở shell mới thì đặt lại.)

Kiểm tra mỗi 10 phút:
```bash
grep -E "^\[.*\] (==|   |⚠)" /kaggle/working/llm_sua.log | tail -n 6; tail -n 1 /kaggle/working/llm_sua.log
tmux has-session -t llm 2>/dev/null && echo "llm ĐANG CHẠY" || echo "llm ĐÃ THOÁT"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
```

- Dòng `⚠ <model> KHÔNG CHẠY ĐƯỢC` là BÌNH THƯỜNG: script tự ghi lý do và chạy model sau. KHÔNG làm gì, KHÔNG sửa.
  Model mới (Qwen3.5, Gemma 4) có thể không chạy được trên T4. Đó cũng là một kết quả.
- Có `✔ XONG TẤT CẢ` → sang BƯỚC 7.
- Có `✘ LỖI` → MẪU B, DỪNG.
- `llm ĐÃ THOÁT` mà không có hai dòng trên → chờ 10 phút, vì hộp thư tự chạy lại khi lỗi mạng; script tự đi tiếp từ
  chỗ dở. Vẫn thoát → MẪU B.
- Quá 6 giờ chưa xong → MẪU C, rồi CHỜ TIẾP.

## BƯỚC 7 — báo cáo

```bash
mkdir -p /kaggle/working/hop_thu/bao_cao
{ echo "# Báo cáo LLM sửa lỗi — $(date -u '+%Y-%m-%d %H:%M UTC')"; echo
  echo "## Venv"; grep -E "torch .* transformers|VENV LLM" /kaggle/working/cai_llm.log | tail -2; echo
  echo "## Kết quả"; cat /kaggle/working/llm_sua/tom_tat.md; echo
  echo "## Dòng cuối log"; tail -n 3 /kaggle/working/llm_sua.log
} > /kaggle/working/hop_thu/bao_cao/llm_sua.md
cat /kaggle/working/hop_thu/bao_cao/llm_sua.md
```

Gửi MẪU D. Xong thì DỪNG: không chạy gì thêm, không tắt `hop_thu`.

## MẪU TIN NHẮN (chép đúng khung, điền phần <…>)

**MẪU A — thiếu token**
```
DỪNG ở BƯỚC 0: không có GITHUB_TOKEN trong biến môi trường lẫn tmux global.
Cần: đặt GITHUB_TOKEN (quyền push repo khanhkhmt/ocr-bench và khanhkhmt/arabic-doc-ocr) rồi bảo tôi làm lại từ BƯỚC 0.
```

**MẪU B — lỗi**
```
DỪNG ở BƯỚC <số>: <một câu: lệnh nào, dấu hiệu gì (dòng ✘ / Traceback / thiếu file)>.
Log: <đường dẫn log>
30 dòng cuối (nguyên văn):
<dán output của tail -n 30 <log>>
Tôi chưa sửa gì, chưa chạy lại gì.
```

**MẪU C — quá lâu**
```
BƯỚC <số> chạy đã <số> giờ, chưa xong; tôi vẫn đang chờ.
Dòng log mới nhất (nguyên văn):
<dán output lệnh kiểm tra của bước đó>
```

**MẪU D — xong**
```
XONG BƯỚC 7. Kết quả đo hệ thống: <dòng ✔ ĐÃ ĐẨY của BƯỚC 3, hoặc "BƯỚC 3 lỗi — đã báo">.
Kết quả LLM: nhánh results-htr/llm_sua trên GitHub + /kaggle/working/hop_thu/bao_cao/llm_sua.md.
Nội dung báo cáo (nguyên văn):
<dán toàn bộ output cat ở BƯỚC 7>
```
