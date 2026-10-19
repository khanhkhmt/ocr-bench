#!/usr/bin/env bash
# Venv cho thử nghiệm LLM sửa lỗi OCR (htr_test/llm_sua.py). Dùng torch CÓ SẴN của hệ thống, không cài / gỡ torch.
#
#   bash htr_test/cai_llm.sh          # → /kaggle/working/venvs/llm  (đổi bằng LLM_VENV=…)
#
# torch hệ thống ≥ 2.6 → transformers 5.15.1 (chạy được cả 5 model, kể cả Qwen3.5 / Gemma 4).
# torch cũ hơn       → transformers 4.56.1 (chỉ Qwen2.5 / Qwen3 / ALLaM; llm_sua tự bỏ qua model không hỗ trợ, ghi lý do).
# Dòng cuối: "✔ VENV LLM SẴN SÀNG …" hoặc "✘ LỖI: …".
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PY="${PYTHON:-python3}"
VENV="${LLM_VENV:-/kaggle/working/venvs/llm}"
fail() { echo "✘ LỖI: $1"; exit 1; }

"$PY" -c 'import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)' 2>/dev/null \
  || fail "python hệ thống ($PY) không có torch CUDA"
TV=$("$PY" -c 'import torch; print(torch.__version__.split("+")[0])')
if "$PY" -c 'import sys, torch; v = tuple(int(x) for x in torch.__version__.split("+")[0].split(".")[:2]); sys.exit(0 if v >= (2, 6) else 1)'; then
  TF="5.15.1"
else
  TF="4.56.1"
fi
echo "== torch hệ thống $TV → transformers $TF"

if command -v uv >/dev/null 2>&1; then UV=(uv)
else "$PY" -m pip install -q uv || fail "không cài được uv"; UV=("$PY" -m uv); fi
[ -x "$VENV/bin/python" ] || "${UV[@]}" venv -q --seed "$VENV" -p "$PY" --system-site-packages
"$VENV/bin/python" -c "
from importlib.metadata import version, PackageNotFoundError
for n in ('torch', 'torchvision', 'torchaudio', 'triton'):
    try: print(f'{n}=={version(n)}')
    except PackageNotFoundError: pass" > "$VENV/torch_pin.txt"
echo "   ghim: $(tr '\n' ' ' < "$VENV/torch_pin.txt")"
# pip CỦA VENV thấy torch hệ thống; file ghim biến mọi lần định thay torch thành lỗi
"$VENV/bin/python" -m pip install -q -c "$VENV/torch_pin.txt" "transformers==$TF" "accelerate>=1.0" \
  "huggingface_hub" "rapidfuzz>=3" "pyyaml" "sentencepiece" "protobuf" || fail "pip install lỗi"
"$VENV/bin/python" - <<'EOF' || fail "kiểm tra venv lỗi"
import torch, transformers, accelerate, rapidfuzz, yaml
assert "/site-packages" in torch.__file__
n = torch.cuda.device_count()
print(f"   torch {torch.__version__} ({torch.__file__.split('/site-packages')[0]}) · transformers {transformers.__version__}"
      f" · accelerate {accelerate.__version__} · GPU {n}: " +
      ", ".join(torch.cuda.get_device_name(i) for i in range(n)))
from htr_test.sync import Sync  # noqa: F401  (đẩy kết quả lên GitHub cần import được)
EOF
echo "✔ VENV LLM SẴN SÀNG: $VENV (transformers $TF)"
