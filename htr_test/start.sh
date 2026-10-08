#!/usr/bin/env bash
# Web thử 2 model chữ viết tay (Ketaba-OCR-LoRA, ArTrOCR-HTR) + bố cục dots.mocr — nhánh thu-2-model-htr.
#   bash htr_test/start.sh                 # mở web 127.0.0.1:7861 (GPU 0)
#   PORT=7862 GPU=0 NO_QUANT4=1 bash htr_test/start.sh
# Dùng chung venv của dots (transformers 4.56.1) — Qwen2.5-VL (Ketaba) và TrOCR đều chạy được trên bản này.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PORT="${PORT:-7861}"; GPU="${GPU:-0}"
VENV="${DOTS_VENV:-/kaggle/working/venvs/dots}"
if [ ! -x "$VENV/bin/python" ]; then
  echo "== Tạo venv $VENV (transformers==4.56.1, dùng chung torch hệ thống)"
  python -m pip install -q uv
  python -m uv venv "$VENV" --system-site-packages
fi
PY="$VENV/bin/python"
echo "== Cài thư viện (dots + peft + bitsandbytes)"
python -m uv pip install -q -p "$PY" "transformers==4.56.1" -e ".[app,dots]" peft bitsandbytes
"$PY" -c "import torch, transformers, peft, bitsandbytes; print('   torch', torch.__version__, '| transformers', transformers.__version__, '| peft', peft.__version__, '| bnb', bitsandbytes.__version__, '| GPU', torch.cuda.device_count())"
ARGS=(--port "$PORT" --gpu "$GPU")
[ -n "${NO_QUANT4:-}" ] && ARGS+=(--no-quant4)
echo "== Mở web: http://127.0.0.1:${PORT}  (VS Code: Ports → Forward ${PORT})"
exec "$PY" -m htr_test.app "${ARGS[@]}"
