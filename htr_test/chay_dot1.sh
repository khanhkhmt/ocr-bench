#!/usr/bin/env bash
# Đợt 1 (thử không cần huấn luyện) — chạy CẢ đợt trên server Kaggle, chạy lại = đi tiếp từ chỗ dở (kể cả server mới:
# lấy lại phần đã đẩy lên GitHub results-htr/dot1). Chạy qua hộp thư:
#
#   python3 -m htr_test.hop_thu viec dot1 --log /kaggle/working/dot1.log --xong "✔ XONG ĐỢT 1" -- bash htr_test/chay_dot1.sh
#
# Thứ tự: môi trường → kiểm bản chép adoc (4 trang mẫu = mốc) → khôi phục → dữ liệu → bộ A + 4 trang + 66 trang Muharaf → chọn → #12 nới khung dòng Kraken
# (báo cáo tạm lên GitHub) → bộ B → báo cáo.
# Cần: bash htr_test/cai_adoc.sh (venv /kaggle/working/venvs/adoc; pipeline = adoc/, bản chép riêng — KHÔNG cần repo
# arabic-doc-ocr), GITHUB_TOKEN, HF_TOKEN (bộ Omar là bộ gated).
# Dòng cuối: "✔ XONG ĐỢT 1 …" hoặc "✘ LỖI ở bước N: …". Log riêng từng tiến trình: /kaggle/working/dot1_logs/.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PY="${OCRB_ADOC_VENV:-/kaggle/working/venvs/adoc}/bin/python"
KIEM="${KIEM:-/kaggle/working/kiem_adoc}"
OUT="${OUT:-/kaggle/working/dot1}"
DATA="${DATA:-/kaggle/working/dot1_data}"
LOGD="${LOGD:-/kaggle/working/dot1_logs}"
BAO_CAO=/kaggle/working/hop_thu/bao_cao
mkdir -p "$OUT" "$DATA" "$LOGD"
STEP=0
D1=("$PY" -m htr_test.dot1)
# lỗi / thoát → dừng các tiến trình con do CHÍNH script này mở (tiến trình nền + lệnh bên trong chúng)
don_dep() { for p in $(jobs -p); do for c in $(ps -o pid= --ppid "$p" 2>/dev/null); do kill "$c" 2>/dev/null; done; kill "$p" 2>/dev/null; done; }
trap don_dep EXIT
fail() { echo; echo "✘ LỖI ở bước $STEP: $1"; exit 1; }
step() { STEP=$((STEP + 1)); echo; echo "================ BƯỚC $STEP: $1 ($(date -u +%H:%M:%S) UTC) · RAM còn $(free -g | awk '/Mem:/ {print $7}') GB"; }
# chạy nền, log ra file + ra màn hình (có nhãn); mã thoát của lệnh được giữ
nen() { local tag=$1 log=$2; shift 2; ( "$@" 2>&1 | tee -a "$log" | sed -u "s/^/[$tag] /"; exit "${PIPESTATUS[0]}" ) & }
cho() { local pid=$1 ten=$2 log=$3; wait "$pid" || { echo "--- 30 dòng cuối $log:"; tail -n 30 "$log"; fail "$ten lỗi (log $log)"; }; }

step "kiểm tra môi trường"
[ -x "$PY" ] || fail "chưa cài môi trường: không có $PY (bash htr_test/cai_adoc.sh)"
N_GPU=$(nvidia-smi -L 2>/dev/null | wc -l)
[ "$N_GPU" -ge 1 ] || fail "không thấy GPU"
echo "GPU: $N_GPU · ổ trống /kaggle/working: $(df -BG --output=avail /kaggle/working | tail -1 | tr -dc 0-9) GB"
[ -n "${GITHUB_TOKEN:-}" ] || fail "thiếu GITHUB_TOKEN"
[ -n "${HF_TOKEN:-}" ] || fail "thiếu HF_TOKEN (bộ Omar Al-Saleh là bộ gated)"
[ "$(df -BG --output=avail /kaggle/working | tail -1 | tr -dc 0-9)" -ge 6 ] || fail "ổ /kaggle/working còn < 6 GB"
"$PY" -c "import adoc, peft, rapidfuzz, numpy, pyarrow; from htr_test.sync import Sync; \
import os; assert os.path.realpath(adoc.__file__).startswith(os.path.realpath('$ROOT') + os.sep), adoc.__file__" \
  || fail "venv adoc thiếu gói, hoặc adoc không phải bản trong $ROOT (lỗi ở trên)"
"$PY" -m adoc check > "$LOGD/check.txt" 2>&1; tail -n 4 "$LOGD/check.txt"
grep -qx "OK" "$LOGD/check.txt" || fail "adoc check không in OK (xem $LOGD/check.txt)"
"${D1[@]}" tu_kiem --out "$OUT" || fail "tự kiểm hàm bầu chọn / chấm điểm không đạt"

step "kiểm bản chép adoc: đọc lại 4 trang mẫu, 16 số phải bằng mốc 2026-10-19 (2 GPU ~25 phút; một lần mỗi máy)"
if [ -f "$LOGD/kiem_adoc.ok" ]; then echo "đã khớp trên máy này ($(cat "$LOGD/kiem_adoc.ok")) → bỏ qua"
else
  if [ "$N_GPU" -ge 2 ]; then KD=(--dots-device cuda:0 --htr-device cuda:1); else KD=(--dots-device cuda:0 --htr-device cuda:0); fi
  "$PY" -m adoc kiem --out "$KIEM" "${KD[@]}" > "$LOGD/kiem_adoc.log" 2>&1
  RC=$?
  grep -E "^[✔✘] " "$LOGD/kiem_adoc.log"
  cp "$KIEM/kiem.md" "$OUT/kiem_adoc.md" 2>/dev/null; cp "$KIEM/kiem.json" "$OUT/kiem_adoc.json" 2>/dev/null
  [ $RC -eq 0 ] || { tail -n 30 "$LOGD/kiem_adoc.log"; fail "bản chép adoc KHÔNG khớp mốc (log $LOGD/kiem_adoc.log) — không chạy thí nghiệm trên pipeline lệch"; }
  date -u +%Y-%m-%dT%H:%MZ > "$LOGD/kiem_adoc.ok"
fi

step "lấy lại phần đã xong từ GitHub (results-htr/dot1)"
"${D1[@]}" khoi_phuc --out "$OUT" || fail "khôi phục lỗi"

step "tải dữ liệu dòng (Omar blind_test, Muharaf test, Muharaf người viết lạ) + tạo bộ A/B"
if [ ! -f "$DATA/cham_omar/danh_sach.csv" ] || [ ! -f "$DATA/cham_muharaf/danh_sach.csv" ] \
   || [ ! -f "$DATA/giu_lai_muharaf/danh_sach.csv" ]; then
  # cùng lệnh tạo dữ liệu như lúc train ft3 (chỉ nguồn muharaf) → tập "người viết lạ" giống hệt
  "$PY" -m htr_train.du_lieu "$DATA" --nguon muharaf --giu-muharaf tu_dong > "$LOGD/du_lieu.log" 2>&1 \
    || { tail -n 30 "$LOGD/du_lieu.log"; fail "tải dữ liệu lỗi (log $LOGD/du_lieu.log)"; }
  tail -n 4 "$LOGD/du_lieu.log"
fi
"${D1[@]}" bo --out "$OUT" --data "$DATA" || fail "tạo bộ A/B lỗi"

step "song song: dots 4 trang + #5 (GPU 0) · 66 trang Muharaf + Kraken (CPU) · đọc bộ A (GPU 1)"
rm -rf "$OUT/.nhan_viec"
# mở lệch nhau vài phút: nạp model ăn RAM nhiều nhất lúc đầu (server từng sập vì hết RAM) — không để 3 lần nạp trùng nhau
nen bt "$LOGD/bon_trang.log" "${D1[@]}" bon_trang --out "$OUT" --data "$DATA" --dots-device cuda:0; P_BT=$!
P_G1=""
if [ "$N_GPU" -ge 2 ]; then
  sleep 180
  nen g1 "$LOGD/docA_g1.log" "${D1[@]}" doc --phan A --gpu 1 --out "$OUT" --push; P_G1=$!
fi
sleep 120
nen mt "$LOGD/mtrang.log" "${D1[@]}" mtrang --out "$OUT" --data "$DATA"; P_MT=$!
cho "$P_BT" "bon_trang" "$LOGD/bon_trang.log"
nen g0 "$LOGD/docA_g0.log" "${D1[@]}" doc --phan A --gpu 0 --out "$OUT" --push; P_G0=$!
cho "$P_MT" "mtrang" "$LOGD/mtrang.log"
cho "$P_G0" "đọc A (GPU 0)" "$LOGD/docA_g0.log"
[ -n "$P_G1" ] && cho "$P_G1" "đọc A (GPU 1)" "$LOGD/docA_g1.log"

step "vét bộ A (việc của 66 trang Muharaf có thể xuất hiện sau khi các tiến trình đọc đã thoát)"
rm -rf "$OUT/.nhan_viec"
nen v0 "$LOGD/docA2_g0.log" "${D1[@]}" doc --phan A --gpu 0 --out "$OUT" --push; P0=$!
P1=""
if [ "$N_GPU" -ge 2 ]; then nen v1 "$LOGD/docA2_g1.log" "${D1[@]}" doc --phan A --gpu 1 --out "$OUT" --push; P1=$!; fi
cho "$P0" "vét A (GPU 0)" "$LOGD/docA2_g0.log"
[ -n "$P1" ] && cho "$P1" "vét A (GPU 1)" "$LOGD/docA2_g1.log"

step "chọn ứng viên theo luật (bộ A)"
"${D1[@]}" chon --out "$OUT" || fail "chọn ứng viên lỗi"

step "#12: cắt lại dòng Kraken với khung nới 0/15/30/50 % (66 trang Muharaf + 4 trang mẫu, CPU)"
"${D1[@]}" mtrang_no --out "$OUT" --data "$DATA" > "$LOGD/mtrang_no.log" 2>&1 \
  || { tail -n 30 "$LOGD/mtrang_no.log"; fail "cắt dòng nới khung lỗi"; }
tail -n 1 "$LOGD/mtrang_no.log"

step "#12: đọc dòng nới khung bằng ft3 (2 GPU) + báo cáo tạm lên GitHub"
rm -rf "$OUT/.nhan_viec"
nen n0 "$LOGD/docN_g0.log" "${D1[@]}" doc --phan N --gpu 0 --out "$OUT" --push; P0=$!
P1=""
if [ "$N_GPU" -ge 2 ]; then nen n1 "$LOGD/docN_g1.log" "${D1[@]}" doc --phan N --gpu 1 --out "$OUT" --push; P1=$!; fi
cho "$P0" "đọc #12 (GPU 0)" "$LOGD/docN_g0.log"
[ -n "$P1" ] && cho "$P1" "đọc #12 (GPU 1)" "$LOGD/docN_g1.log"
"${D1[@]}" bao_cao --out "$OUT" --push > "$LOGD/bao_cao_tam.log" 2>&1 \
  || { tail -n 30 "$LOGD/bao_cao_tam.log"; fail "báo cáo tạm lỗi"; }
mkdir -p "$BAO_CAO" && cp "$OUT/tom_tat.md" "$BAO_CAO/dot1.md"
grep "Nới khung dòng (#12)" "$OUT/tom_tat.md" | tail -n 1
echo "✔ #12 XONG — báo cáo tạm đã đẩy lên GitHub (results-htr/dot1/tom_tat.md)"

step "xác nhận trên bộ B + 66 trang Muharaf"
rm -rf "$OUT/.nhan_viec"
nen b0 "$LOGD/docB_g0.log" "${D1[@]}" doc --phan B --gpu 0 --out "$OUT" --push; P0=$!
P1=""
if [ "$N_GPU" -ge 2 ]; then nen b1 "$LOGD/docB_g1.log" "${D1[@]}" doc --phan B --gpu 1 --out "$OUT" --push; P1=$!; fi
cho "$P0" "đọc B (GPU 0)" "$LOGD/docB_g0.log"
[ -n "$P1" ] && cho "$P1" "đọc B (GPU 1)" "$LOGD/docB_g1.log"
rm -rf "$OUT/.nhan_viec"
"${D1[@]}" doc --phan B --gpu 0 --out "$OUT" --push > "$LOGD/docB2.log" 2>&1 \
  || { tail -n 30 "$LOGD/docB2.log"; fail "vét B lỗi"; }

step "báo cáo"
"${D1[@]}" bao_cao --out "$OUT" --push > "$LOGD/bao_cao.log" 2>&1 \
  || { tail -n 30 "$LOGD/bao_cao.log"; fail "báo cáo lỗi"; }
mkdir -p "$BAO_CAO" && cp "$OUT/tom_tat.md" "$BAO_CAO/dot1.md"
grep -E "^\*\*(ĐẠT|KHÔNG ĐẠT)|Kết luận theo luật" "$OUT/tom_tat.md" | head -n 6
echo
echo "✔ XONG ĐỢT 1 — kết quả: $OUT/tom_tat.md (GitHub results-htr/$(basename "$OUT")/tom_tat.md, bản sao $BAO_CAO/dot1.md)"
