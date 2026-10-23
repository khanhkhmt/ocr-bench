# PROMPT CHO AGENT TRÊN SERVER KAGGLE — Đợt 1: thử không cần huấn luyện

Bạn là agent chạy trên server Kaggle (2× T4). Làm ĐÚNG từng bước dưới đây, theo thứ tự, chép lệnh NGUYÊN VĂN.
Bạn KHÔNG thiết kế thí nghiệm, KHÔNG sửa code, KHÔNG đổi tham số: mọi thứ (bộ test, cấu hình, luật chọn, luật đạt) đã
viết sẵn trong `htr_test/dot1.py` và `htr_test/chay_dot1.sh`. Việc của bạn: chạy lệnh, chờ, kiểm tra đúng điều kiện ghi
ở mỗi bước, báo cáo.

Server sập / khởi động lại / phiên Kaggle hết giờ giữa chừng → làm lại TỪ BƯỚC 0 (kể cả server mới tinh). Mọi bước
chạy lại đều an toàn: `chay_dot1.sh` tự lấy lại phần đã đẩy lên GitHub (nhánh `results-htr/dot1`) và đi tiếp từ chỗ dở;
phần đã xong KHÔNG đọc lại. (Các lần trước đã xong bộ A, Bước 0, 4 trang, #5, #12 và khoảng nửa bộ B; lần này còn
nốt bộ B + đo pipeline adoc với nới dòng 50 % trên 4 trang mẫu.)

## LUẬT CỨNG (vi phạm = dừng ngay)

1. Token (`GITHUB_TOKEN`, `HF_TOKEN`) CHỈ nằm trong biến môi trường. CẤM in ra (`echo $GITHUB_TOKEN`, `env`,
   `printenv`, `set`), CẤM ghi vào file hay `.git/config`. Muốn biết có token chưa thì chỉ dùng `echo ${GITHUB_TOKEN:+CÓ}`.
2. CẤM `pkill`, `killall`, `kill -9` theo tên. Chỉ được `tmux kill-session -t <tên>` với các phiên do CHÍNH BẠN tạo
   trong prompt này: `hop_thu`, `cai_adoc`, `dot1`.
3. CẤM cài, gỡ hay nâng cấp torch / CUDA / transformers / peft bằng tay. Chỉ `htr_test/cai_adoc.sh` được cài gói.
4. CẤM sửa bất kỳ file code nào trong `/kaggle/working/ocr-bench` (kể cả `adoc/`)
   (không `sed -i`, không sửa tay, không `git commit` code). Code sai → báo cáo rồi DỪNG.
5. CẤM xoá `/kaggle/working/dot1`, `/kaggle/working/dot1_data`, `/kaggle/working/dot1_logs` (kết quả + dữ liệu đang dùng).
6. CẤM mở ngrok mới, link chia sẻ Gradio, Google Drive, hay đưa dữ liệu lên bất kỳ dịch vụ nào khác GitHub (chỉ qua
   các script có sẵn).
7. CẤM thêm, bớt hay đổi cấu hình, bộ test, ngưỡng. CẤM chạy lại thí nghiệm "cho đẹp số".
8. Lệnh nào chạy lâu hơn 2 phút PHẢI chạy bằng `hop_thu viec` (trong tmux), không chạy trực tiếp.
9. Gặp lỗi: dán NGUYÊN VĂN 30 dòng cuối log (`tail -n 30 <log>`) vào tin nhắn, dùng mẫu tin nhắn ở cuối, rồi DỪNG.
   KHÔNG tự sửa, KHÔNG thử cách khác, KHÔNG chạy lại (trừ khi bước đó cho phép).
10. Không gõ lại chữ Ả Rập bằng tay. Khi báo cáo thì chép nguyên văn file (`cat`).
11. Chờ bằng `sleep 600` (10 phút), rồi kiểm tra. Mỗi lần kiểm tra chỉ chạy các lệnh kiểm tra ghi trong bước.

## BƯỚC 0 — kiểm tra máy

```bash
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
df -h /kaggle/working /tmp | tail -2
free -g | head -2
for v in GITHUB_TOKEN HF_TOKEN; do
  if [ -z "${!v:-}" ] && tmux show-environment -g "$v" >/dev/null 2>&1; then export "$v=$(tmux show-environment -g "$v" | cut -d= -f2-)"; fi
done
echo "GITHUB_TOKEN: ${GITHUB_TOKEN:+CÓ}  HF_TOKEN: ${HF_TOKEN:+CÓ}"
```

ĐẠT khi: thấy dòng GPU `Tesla T4` và `GITHUB_TOKEN: CÓ  HF_TOKEN: CÓ`.
- Thiếu một trong hai token → gửi MẪU A rồi DỪNG. (Lần này HF_TOKEN BẮT BUỘC: bộ Omar Al-Saleh là bộ gated.)
- Chỉ có 1 GPU → vẫn làm tiếp (script tự chạy tuần tự, lâu gấp đôi).

Mọi lệnh ở các bước sau phải chạy trong shell đã có hai token. Mở shell mới thì chạy lại vòng `for v in …` ở trên.

## BƯỚC 1 — lấy code + bật hộp thư (báo trạng thái server lên GitHub)

```bash
cd /kaggle/working
H="Authorization: Basic $(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 -w0)"
if [ -d ocr-bench/.git ]; then git -C ocr-bench -c http.extraHeader="$H" pull -q origin thu-2-model-htr
else git -c http.extraHeader="$H" clone -q -b thu-2-model-htr https://github.com/khanhkhmt/ocr-bench.git ocr-bench; fi
git -C ocr-bench log --oneline -1
ls ocr-bench/htr_test/dot1.py ocr-bench/htr_test/chay_dot1.sh ocr-bench/htr_test/cai_adoc.sh ocr-bench/adoc/__main__.py
tmux start-server
tmux set-environment -g GITHUB_TOKEN "$GITHUB_TOKEN"
tmux set-environment -g HF_TOKEN "$HF_TOKEN"
tmux has-session -t hop_thu 2>/dev/null || tmux new -d -s hop_thu \
  "cd /kaggle/working/ocr-bench && python3 -m htr_test.hop_thu chay --phut 10 --kiem-lenh 5 2>&1 | tee -a /kaggle/working/hop_thu.log"
sleep 60; tail -n 5 /kaggle/working/hop_thu.log
```

ĐẠT khi: có 1 dòng commit, `ls` thấy đủ 4 file, `hop_thu.log` không có `Traceback`.
`ls` báo thiếu file hoặc `hop_thu` lỗi → MẪU B (log = `/kaggle/working/hop_thu.log`), DỪNG.

Từ bước 2 trở đi, MỌI lệnh `hop_thu viec` chạy trong thư mục `/kaggle/working/ocr-bench`:
```bash
cd /kaggle/working/ocr-bench
```

## BƯỚC 2 — cài môi trường (venv adoc + Kraken + tải model ~15 GB), ~20–40 phút

Không dùng repo arabic-doc-ocr: pipeline là bản chép `adoc/` trong ocr-bench (xem `adoc/NGUON.md`).

```bash
python3 -m htr_test.hop_thu viec cai_adoc --log /kaggle/working/cai_adoc.log --xong "Done. adoc" -- bash htr_test/cai_adoc.sh
```

Kiểm tra mỗi 5 phút (`sleep 300`):
```bash
tail -n 4 /kaggle/working/cai_adoc.log; tmux has-session -t cai_adoc 2>/dev/null && echo "cai_adoc ĐANG CHẠY" || echo "cai_adoc ĐÃ THOÁT"
```

- Có dòng `Done. adoc` → chạy `grep -x OK /kaggle/working/cai_adoc.log`:
  - in ra `OK` → sang BƯỚC 3;
  - không in gì → MẪU B (log = `/kaggle/working/cai_adoc.log`), DỪNG.
- `cai_adoc ĐÃ THOÁT` mà không có `Done. adoc` → MẪU B, DỪNG.
- Cảnh báo pip kiểu "dependency resolver … google-adk" là BÌNH THƯỜNG.

## BƯỚC 3 — chạy Đợt 1 (chạy tiếp: ~25 phút kiểm bản chép + ~1 giờ dựng lại + ~2,5 giờ nốt bộ B + ~25 phút đo nới 50 %, 2 GPU)

```bash
python3 -m htr_test.hop_thu viec dot1 --log /kaggle/working/dot1.log --xong "✔ XONG ĐỢT 1" -- bash htr_test/chay_dot1.sh
```

Script tự làm theo thứ tự (bạn KHÔNG làm tay bước nào):
1. kiểm tra môi trường + tự kiểm (`✔ TỰ KIỂM ĐẠT`),
2. kiểm bản chép adoc (nới dòng 0 %): đọc lại 4 trang mẫu, 16 số phải bằng mốc (`✔ ADOC KHỚP MỐC`; 2 GPU ~25 phút),
3. lấy lại phần đã xong từ GitHub, 4. tải dữ liệu dòng (~20–40 phút),
5. song song: dots đọc 4 trang mẫu (GPU 0) · tải 66 trang Muharaf + Kraken tách dòng (CPU) · đọc bộ A (GPU 1)
   (chạy tiếp: phần đã xong chỉ cắt lại ảnh dòng, vài phút),
6. vét bộ A, 7. chọn ứng viên, 8. #12: cắt lại dòng Kraken với khung nới (CPU, vài phút),
9. #12: đọc dòng nới khung (2 GPU, ~2,5 giờ) + đẩy báo cáo tạm lên GitHub (in `✔ #12 XONG`),
10. đọc bộ B, 11. đo adoc với nới dòng 50 % trên 4 trang mẫu (2 GPU ~25 phút, in `✔ ĐO NỚI 50 % XONG`; các dòng
    `· page_N` là BÌNH THƯỜNG — số khác mốc là đúng ý, không phải lỗi), 12. báo cáo.

Kiểm tra mỗi 10 phút:
```bash
grep -E "BƯỚC|✔|✘|⚠" /kaggle/working/dot1.log | tail -n 6; tail -n 2 /kaggle/working/dot1.log
tmux has-session -t dot1 2>/dev/null && echo "dot1 ĐANG CHẠY" || echo "dot1 ĐÃ THOÁT"
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader; free -g | grep Mem:
```

- Có `✔ XONG ĐỢT 1` → sang BƯỚC 4.
- Lần ĐẦU thấy `✔ #12 XONG` (chưa có `✔ XONG ĐỢT 1`; chạy tiếp thì dòng này hiện lại sau vài phút vì #12 đã đọc xong) → chạy
  `sed -n '/^## 5b/,/^## 6\|^## 7/p' /kaggle/working/dot1/tom_tat.md`, gửi MẪU E, rồi CHỜ TIẾP (việc vẫn chạy, không làm
  gì thêm). Chỉ gửi MẪU E một lần.
- Có `✘ LỖI ở bước` → MẪU B (log = `/kaggle/working/dot1.log`). Trong 30 dòng cuối đã có sẵn đoạn log của tiến
  trình bị lỗi (script tự in). DỪNG.
- `dot1 ĐÃ THOÁT` mà không có hai dòng trên → chờ thêm 10 phút, vì hộp thư tự chạy lại khi lỗi mạng (tối đa 2 lần),
  và script tự đi tiếp từ chỗ dở. Kiểm tra lại. Vẫn thoát, không chạy lại → MẪU B.
- Quá 12 giờ chưa xong → MẪU C, rồi CHỜ TIẾP (không dừng việc).
- BÌNH THƯỜNG, không làm gì: dòng `⚠ ĐỒNG BỘ`, `✘ ĐẨY GITHUB THẤT BẠI (chạy tiếp, lần sau thử lại)`,
  `⚠ <trang>: … bỏ trang`, `Kraken failed … → projection`,
  `dùng chữ của sản phẩm cho khối này`, `⚠ RAM TRỐNG < 2,5 GB` xuất hiện vài lần, GPU 0 rảnh ở đầu bước 5 trong khi GPU 1
  đang chạy, một GPU rảnh ở cuối các bước đọc (hết việc để chia).
- `free -g` cột `available` dưới 2 GB ở NHIỀU lần kiểm tra liên tiếp → gửi MẪU C (ghi rõ "RAM thấp"), KHÔNG dừng việc.

## BƯỚC 4 — báo cáo

```bash
cat /kaggle/working/dot1/tom_tat.md
ls /kaggle/working/hop_thu/bao_cao/dot1.md
```

Gửi MẪU D. Xong thì DỪNG: không chạy gì thêm, không tắt `hop_thu`.

## MẪU TIN NHẮN (chép đúng khung, điền phần <…>)

**MẪU A — thiếu token**
```
DỪNG ở BƯỚC 0: thiếu <GITHUB_TOKEN / HF_TOKEN> trong biến môi trường lẫn tmux global.
Cần: đặt token đó (GITHUB_TOKEN: quyền push repo khanhkhmt/ocr-bench; HF_TOKEN: tài khoản đã bấm đồng ý bộ
U4RASD/omar-al-saleh-manuscripts-segments) rồi bảo tôi làm lại từ BƯỚC 0.
```

**MẪU B — lỗi**
```
DỪNG ở BƯỚC <số>: <một câu: lệnh nào, dấu hiệu gì (dòng ✘ / Traceback / thiếu file)>.
Log: <đường dẫn log>
30 dòng cuối (nguyên văn):
<dán output của tail -n 30 <log>>
Tôi chưa sửa gì, chưa chạy lại gì.
```

**MẪU C — quá lâu / RAM thấp**
```
BƯỚC <số> chạy đã <số> giờ, chưa xong; tôi vẫn đang chờ. <"RAM thấp" nếu có>
Dòng log mới nhất (nguyên văn):
<dán output lệnh kiểm tra của bước đó>
```

**MẪU E — #12 xong (Đợt 1 vẫn đang chạy bộ B)**
```
#12 XONG (nới khung dòng Kraken); bộ B đang chạy, tôi vẫn chờ. Kết quả #12 (nguyên văn):
<dán output lệnh sed ở BƯỚC 3>
```

**MẪU D — xong**
```
XONG ĐỢT 1. Kết quả: nhánh results-htr/dot1 trên GitHub + /kaggle/working/hop_thu/bao_cao/dot1.md.
Nội dung báo cáo (nguyên văn):
<dán toàn bộ output cat ở BƯỚC 4>
```
