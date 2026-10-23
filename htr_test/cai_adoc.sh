#!/usr/bin/env bash
# Cài môi trường chạy thí nghiệm của ocr-bench (bản chép pipeline adoc/, xem adoc/NGUON.md) — KHÔNG cần repo
# arabic-doc-ocr. Cùng cách cài với install.sh của arabic-doc-ocr@03e1e8e (cùng requirements → cùng số):
#
#   bash htr_test/cai_adoc.sh                # venv /kaggle/working/venvs/adoc + venv Kraken + model tách dòng + model (~15 GB)
#   SKIP_MODELS=1 bash htr_test/cai_adoc.sh  # chưa tải model lớn
#
# torch: dùng lại torch CUDA của Python hệ thống (Kaggle) và ghim lại (--system-site-packages) — không gì thay torch.
# Kraken ở venv riêng (torch CPU), vì Kraken ghim torch của nó. Thư mục riêng: ~/.cache/ocr_bench_adoc.
# Dòng cuối: "Done. adoc" nếu xong; trước đó là kết quả `python -m adoc check` (dòng OK / NOT READY).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
PY="${PYTHON:-python3}"
VENV="${OCRB_ADOC_VENV:-/kaggle/working/venvs/adoc}"  # như các venv khác của ocr-bench
HOME_DIR="${OCRB_ADOC_HOME:-$HOME/.cache/ocr_bench_adoc}"
KVENV="${OCRB_KRAKEN_VENV:-$HOME_DIR/kraken_venv}"
SEG="${OCRB_KRAKEN_SEG_MODEL:-$HOME_DIR/muharaf_seg_best.mlmodel}"
mkdir -p "$HOME_DIR"
fail() { echo "✘ $1"; exit 1; }

"$PY" -c 'import sys; assert sys.version_info >= (3, 10), "Python >= 3.10 needed"'
"$PY" -c 'import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)' 2>/dev/null \
  || fail "Python hệ thống ($PY) không có torch CUDA — script này chỉ dùng lại torch hệ thống, không tự cài torch"
if command -v uv >/dev/null 2>&1; then UV=(uv)
elif "$PY" -m pip install -q uv 2>/dev/null || "$PY" -m pip install -q --user uv 2>/dev/null; then UV=("$PY" -m uv)
else fail "không cài được uv"; fi

echo "== 1/4 venv chính: $VENV (torch hệ thống, ghim)"
mkdir -p "$(dirname "$VENV")"
[ -x "$VENV/bin/python" ] || "${UV[@]}" venv -q --seed "$VENV" -p "$PY" --system-site-packages
"$VENV/bin/python" -c "
from importlib.metadata import version, PackageNotFoundError
for n in ('torch', 'torchvision', 'torchaudio', 'triton'):
    try: print(f'{n}=={version(n)}')
    except PackageNotFoundError: pass" > "$VENV/torch_pin.txt"
# pip của venv thấy torch hệ thống; file ghim biến mọi lần định thay torch thành lỗi
"$VENV/bin/python" -m pip install -q -c "$VENV/torch_pin.txt" -r adoc/requirements.txt
# adoc / htr_test / ocrbench chạy thẳng từ thư mục gốc ocr-bench (python -m … trong $ROOT) — không cài gói nào
"$VENV/bin/python" - <<'EOF' || fail "venv không dùng torch hệ thống, hoặc thiếu gói"
import os, sys
import torch, peft, rapidfuzz, numpy, pyarrow  # noqa: F401
assert not os.path.realpath(torch.__file__).startswith(os.path.realpath(sys.prefix) + os.sep), \
    f"torch nằm TRONG venv ({torch.__file__}) — không phải torch hệ thống"
print(f"   torch {torch.__version__} (hệ thống) · peft {peft.__version__}")
EOF

echo "== 2/4 venv Kraken (torch CPU): $KVENV"
if [ ! -x "$KVENV/bin/kraken" ]; then
  "${UV[@]}" venv -q "$KVENV" -p 3.12 || "${UV[@]}" venv -q "$KVENV"
  "${UV[@]}" pip install -q -p "$KVENV/bin/python" --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cpu "kraken>=7.1,<8"
fi
"$KVENV/bin/kraken" --version | tail -1

echo "== 3/4 model tách dòng Muharaf (CC BY 4.0): $SEG"
[ -s "$SEG" ] || curl -fsSL -o "$SEG" "https://zenodo.org/records/14295555/files/muharaf_seg_best.mlmodel?download=1"
ls -la "$SEG"

echo "== 4/4 model"
if [ -z "${SKIP_MODELS:-}" ]; then "$VENV/bin/python" -m adoc download; else echo "   bỏ qua"; fi

"$VENV/bin/python" -m adoc check || true
echo
echo "Done. adoc — kiểm bản chép: $VENV/bin/python -m adoc kiem --out /kaggle/working/kiem_adoc"
