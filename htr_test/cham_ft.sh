#!/bin/bash
# Chấm một adapter tự huấn luyện (khanh99/htr-ckpt/<ft>/best) trên 3 tập, 500 dòng mỗi tập, rồi một model đối chứng
# trên tập Muharaf người viết lạ. Đăng ký qua hộp thư:
#   python3 -m htr_test.hop_thu viec c3 --log /kaggle/working/c3.log --xong "✔ XONG CHẤM ft3" -- bash htr_test/cham_ft.sh 0 ft3 baseer
#   python3 -m htr_test.hop_thu viec c4 --log /kaggle/working/c4.log --xong "✔ XONG CHẤM ft4" -- bash htr_test/cham_ft.sh 1 ft4 ft1s050
# Cần /tmp/htr_data (htr_train.du_lieu --giu-muharaf tu_dong), HF_TOKEN (repo riêng tư), GITHUB_TOKEN (--push).
set -euo pipefail
[ $# -eq 3 ] || { echo "✘ LỖI cách dùng: cham_ft.sh <gpu> <ft3|ft4|…> <baseer|ft1s050>"; exit 2; }
GPU=$1 FT=$2 DC=$3
W=/kaggle/working
D=/tmp/htr_data
for f in "$D/cham_muharaf/danh_sach.csv" "$D/giu_lai_muharaf/danh_sach.csv"; do
  [ -f "$f" ] || { echo "✘ LỖI thiếu $f — chạy htr_train.du_lieu $D --giu-muharaf tu_dong trước"; exit 2; }
done
cd "$(dirname "$0")/.."
E=("$W/venvs/dots/bin/python" -m htr_test.eval_lines --n 500 --gpu "$GPU" --push)
O=(--out "$W/htr_eval_n500" --split blind_test)
G=(--out "$W/htr_eval_giu_lai_n500" --data "$D/giu_lai_muharaf" --split giu_lai)
M=(--out "$W/htr_eval_muharaf_n500" --data "$D/cham_muharaf" --split test)
A=(--models "baseer_$FT" --lora "hf:khanh99/htr-ckpt/$FT/best")
"${E[@]}" "${O[@]}" "${A[@]}"
"${E[@]}" "${G[@]}" "${A[@]}"
"${E[@]}" "${M[@]}" "${A[@]}"
case "$DC" in
  baseer)  "${E[@]}" "${G[@]}" --models baseer ;;
  ft1s050) "${E[@]}" "${G[@]}" --models baseer_ft1_s050 --lora ft1 --lora-scale 0.5 ;;
  *) echo "✘ LỖI đối chứng lạ: $DC"; exit 2 ;;
esac
echo "✔ XONG CHẤM $FT"
