#!/usr/bin/env bash
# Cài Kraken (venv RIÊNG, torch CPU — không đụng torch/CUDA của hệ thống / venv dots) + model tách dòng Muharaf (CC BY 4.0).
# Web (htr_test/app.py, "Kraken + model Muharaf") tự dùng: KRAKEN_BIN, KRAKEN_SEG_MODEL (mặc định đúng các đường dẫn dưới).
set -euo pipefail
VENV=/kaggle/working/venvs/kraken
M=/kaggle/working/kraken_models
if [ ! -x "$VENV/bin/kraken" ]; then
  python -m pip install -q uv
  python -m uv venv -q "$VENV" -p 3.12 || python -m uv venv -q "$VENV"
  python -m uv pip install -q -p "$VENV/bin/python" --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cpu "kraken>=5"
fi
mkdir -p "$M"
[ -s "$M/muharaf_seg_best.mlmodel" ] || curl -fsSL -o "$M/muharaf_seg_best.mlmodel" \
  "https://zenodo.org/records/14295555/files/muharaf_seg_best.mlmodel?download=1"
"$VENV/bin/kraken" --version | tail -1
ls -la "$M/muharaf_seg_best.mlmodel"
