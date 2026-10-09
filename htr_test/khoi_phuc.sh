#!/usr/bin/env bash
# Dựng lại server Colab sau khi bị ngắt (máy mới, mất sạch ổ) — MỘT lệnh, chạy được qua SSH:
#   bash khoi_phuc.sh            # hoặc: curl … | bash  (script không chứa bí mật)
# Cần: GITHUB_TOKEN (+ HF_TOKEN nếu chấm Omar) trong biến môi trường HOẶC trong tmux global
# (tmux set-environment -g GITHUB_TOKEN …) — cell khởi động Colab của người dùng đặt sẵn.
# Làm: lấy code nhánh thu-2-model-htr → hộp thư (tmux hop_thu, báo trạng thái + địa chỉ ngrok lên GitHub) → web
# (tmux htr; start.sh tạo venv dots) → chờ venv sẵn sàng → benchmark (tmux htr_bench; tự kéo phần đã chấm từ GitHub).
# BENCH_ARGS mặc định = lần chạy đang dở; đặt BENCH_ARGS="" để không chạy benchmark.
set -euo pipefail
REPO=/root/ocr-bench
W=/kaggle/working
BENCH_ARGS="${BENCH_ARGS---tag n500 --n 500 --models dots,ketaba --datasets muharaf,omar --push}"
for v in GITHUB_TOKEN HF_TOKEN; do
  if [ -z "${!v:-}" ] && tmux show-environment -g "$v" >/dev/null 2>&1; then
    export "$v=$(tmux show-environment -g "$v" | cut -d= -f2-)"
  fi
done
[ -n "${GITHUB_TOKEN:-}" ] || { echo "✘ thiếu GITHUB_TOKEN (biến môi trường hoặc tmux global)"; exit 1; }
tmux start-server
tmux set-environment -g GITHUB_TOKEN "$GITHUB_TOKEN"
[ -n "${HF_TOKEN:-}" ] && tmux set-environment -g HF_TOKEN "$HF_TOKEN" || echo "⚠ thiếu HF_TOKEN — chấm Omar (bộ gated) sẽ lỗi"
H="Authorization: Basic $(printf 'x-access-token:%s' "$GITHUB_TOKEN" | base64 -w0)"
mkdir -p "$W"
if [ -d "$REPO/.git" ]; then
  git -C "$REPO" -c http.extraHeader="$H" pull -q origin thu-2-model-htr
else
  git -c http.extraHeader="$H" clone -q -b thu-2-model-htr https://github.com/khanhkhmt/ocr-bench.git "$REPO"
fi
echo "== code: $(git -C "$REPO" log --oneline -1)"
tmux has-session -t hop_thu 2>/dev/null || \
  tmux new -d -s hop_thu "cd $REPO && python3 -m htr_test.hop_thu chay --phut 20 --kiem-lenh 5 2>&1 | tee -a $W/hop_thu.log"
tmux has-session -t htr 2>/dev/null || \
  tmux new -d -s htr "cd $REPO && bash htr_test/start.sh 2>&1 | tee $W/htr.log"
echo "== chờ venv dots sẵn sàng (start.sh: cài gói ~5–10 phút)…"
for _ in $(seq 1 90); do
  grep -q "== Mở web" "$W/htr.log" 2>/dev/null && break
  sleep 10
done
grep -q "== Mở web" "$W/htr.log" || { echo "✘ start.sh chưa xong sau 15 phút — xem $W/htr.log"; exit 1; }
grep "torch .* | transformers" "$W/htr.log" | tail -1
echo "== Kraken + model tách dòng Muharaf (CPU, chạy nền)"
tmux has-session -t cai_kraken 2>/dev/null || tmux new -d -s cai_kraken "cd $REPO && bash htr_test/cai_kraken.sh 2>&1 | tee $W/cai_kraken.log"
if [ -n "$BENCH_ARGS" ] && ! tmux has-session -t htr_bench 2>/dev/null; then
  tmux new -d -s htr_bench "cd $REPO && $W/venvs/dots/bin/python -m htr_test.benchmark $BENCH_ARGS 2>&1 | tee -a $W/htr_bench_n500.log"
  echo "== benchmark: $BENCH_ARGS"
fi
tmux ls
