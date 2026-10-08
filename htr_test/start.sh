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
# uv BỎ QUA gói hệ thống trong venv --system-site-packages → "uv pip install peft" từng kéo một torch MỚI vào venv,
# lệch với torchvision hệ thống ("operator torchvision::nms does not exist"). Sửa: (1) gỡ mọi torch/triton/nvidia-*
# đã lọt vào venv (venv dots vốn không có torch riêng); (2) cài peft + bitsandbytes bằng pip CỦA VENV (pip thấy torch
# hệ thống) và GHIM torch* = đúng bản hệ thống → gói nào đòi torch khác thì báo lỗi, không âm thầm cài.
echo "== Dọn torch lạc trong venv (nếu có)"
STRAY=$("$PY" - <<'PYEOF'
import re, sys, sysconfig
from importlib.metadata import distributions
site = sysconfig.get_paths()["purelib"]
names = {d.metadata["Name"] for d in distributions(path=[site])}
print(" ".join(sorted(n for n in names if re.fullmatch(r"(torch|torchvision|torchaudio|triton|nvidia-.*)", n.lower()))))
PYEOF
)
if [ -n "$STRAY" ]; then echo "   gỡ khỏi venv: $STRAY"; python -m uv pip uninstall -q -p "$PY" $STRAY; else echo "   không có"; fi
echo "== Cài thư viện (dots) bằng uv — các gói này không cần torch"
python -m uv pip install -q -p "$PY" "transformers==4.56.1" -e ".[app,dots]"
echo "== Cài peft + bitsandbytes bằng pip của venv, ghim torch hệ thống"
CONS="$VENV/torch_he_thong.txt"
"$PY" -c "
from importlib.metadata import version, PackageNotFoundError
for n in ('torch', 'torchvision', 'torchaudio', 'triton'):
    try: print(f'{n}=={version(n)}')
    except PackageNotFoundError: pass" > "$CONS"
echo "   ghim: $(tr '\n' ' ' < "$CONS")"
"$PY" -m pip install -q -c "$CONS" "transformers==4.56.1" peft bitsandbytes
"$PY" -c "import torch, torchvision, transformers, peft, bitsandbytes; torchvision.ops.nms(torch.zeros(1, 4), torch.zeros(1), 0.5); print('   torch', torch.__version__, '(' + torch.__file__.split('/site-packages')[0] + ') | torchvision', torchvision.__version__, '| transformers', transformers.__version__, '| peft', peft.__version__, '| bnb', bitsandbytes.__version__, '| GPU', torch.cuda.device_count())"
ARGS=(--port "$PORT" --gpu "$GPU")
[ -n "${NO_QUANT4:-}" ] && ARGS+=(--no-quant4)
echo "== Mở web: http://127.0.0.1:${PORT}  (VS Code: Ports → Forward ${PORT})"
exec "$PY" -m htr_test.app "${ARGS[@]}"
