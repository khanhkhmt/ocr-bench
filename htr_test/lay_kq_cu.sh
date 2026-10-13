#!/bin/bash
# Lấy các <model>.jsonl đã chấm từ nhánh results-htr về /kaggle/working/<thư mục> (phiên Kaggle mới) → eval_lines bỏ qua
# dòng đã có và tom_tat.md so được với model cũ. Không ghi đè file đã có. Cần GITHUB_TOKEN (không in ra).
#   bash htr_test/lay_kq_cu.sh htr_eval_n500 htr_eval_muharaf_n500
set -euo pipefail
cd "$(dirname "$0")/.."
H="Authorization: Basic $(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 -w0)"
git -c http.extraHeader="$H" fetch -q origin results-htr
for d in "$@"; do
  mkdir -p "/kaggle/working/$d"
  for f in $(git ls-tree --name-only origin/results-htr "$d/" | grep '\.jsonl$'); do
    [ -e "/kaggle/working/$f" ] || git show "origin/results-htr:$f" > "/kaggle/working/$f"
  done
  echo "== $d: $(ls "/kaggle/working/$d" | grep '\.jsonl$' | tr '\n' ' ')"
done
