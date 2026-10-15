---
base_model: Misraj/Baseer__Nakba
library_name: peft
license: cc-by-nc-sa-4.0
language: [ar]
tags: [ocr, handwriting, arabic, htr, lora]
---
# LoRA for Arabic handwritten line recognition on old documents — continued training of Baseer-Nakba

LoRA adapters on top of [Misraj/Baseer__Nakba](https://huggingface.co/Misraj/Baseer__Nakba) (Qwen2.5-VL-3B) for
**handwritten Arabic text lines on old, yellowed documents** (letters, contracts, legal papers). The model reads **one
line image at a time**. `inference.py` reads line images or whole pages and flags doubtful words by reading every line
with two adapters.

**Recommended: `ft3` as the main reader, `ft4` as the cross-check.**

## Results

Character accuracy / word accuracy (= 100% − CER / WER), 500 random lines per set (seed 0), after normalisation
(NFKC, no harakat/tatweel, alef/yeh unified, Arabic-Indic digits → 0–9). None of these lines were used in training.

| model | Omar Al-Saleh blind_test (1951–65 Palestinian) | Muharaf, unseen writers | Muharaf test |
|---|---|---|---|
| **ft3/** | **93.4% · 79.9%** | 94.7% · 85.0% | 91.4% · 80.0% |
| **ft4/** | 92.8% · 78.2% | **95.0% · 86.0%** | **92.0% · 81.0%** |
| ft1/ at strength 0.5 | 93.4% · 79.9% | 93.3% · 80.7% | 87.0% · 69.1% |
| ft1/ (strength 1) | 92.0% | — | 89.1% · 74.6% |
| ft2/ | 92.3% | — | 87.3% · 71.6% |
| Baseer-Nakba base | 93.3% · 79.8% | 88.3% · 67.3% | 79.1% · 55.0% |

- *Unseen writers*: Muharaf documents held out by writer for ft3/ft4. Base, ft1 and ft2 were trained on some of these
  lines, so this column favours them.
- Paired bootstrap, ft3 vs ft1@0.5: unseen writers +1.5 points (95% CI +0.8…+2.2), Muharaf test +4.5 (+3.5…+5.4), Omar
  +0.1 (not significant). ft3 vs ft4: within noise except Omar (ft3 +0.6, CI +0.3…+1.0).
- Digits are the weak spot: digit accuracy ft3 75% (Omar), 76% (Muharaf test), 92% (unseen writers).
- One real 1970s contract page (blue ballpoint, ruled paper, phone photo), whole page through line segmentation:
  ft3 72.6%, ft4 72.9%, base 62.8% character accuracy. **Output is a draft for a human to check, not a final text.**

**Cross-check highlighting** (ft3 main + ft4 check, word level, same test sets): highlights 13–19% of words and
catches 57–75% of the wrong words; about 2/3 of highlighted words are really wrong. Words that are *not* highlighted
can still be wrong (both adapters share most of their training) — check digits, names and dates anyway.

## Usage

```bash
pip install torch "transformers>=4.49" peft pillow numpy huggingface_hub
# tested with transformers 4.56.1 + peft 0.18 on a T4 (fp16)

python inference.py line line1.png line2.png          # ft3 reading, doubtful words as [?word], + ft4 reading
python inference.py page page.jpg --out result/       # → result/page.txt, .json, .html (highlighted), _lines.jpg
python inference.py line l.png --adapters ft3         # one adapter only (faster, no cross-check)
python inference.py line l.png --adapters ft1 --scale ft1=0.5
```

```python
from PIL import Image
from inference import HTRReader

r = HTRReader()                               # base + ft3 + ft4 (one base model in memory, adapters switched)
r.read([Image.open("line.png")])              # ['…']  (ft3)
r.read_check([Image.open("line.png")])        # [{'text': ft3, 'check': ft4, 'words': [(w, suspicious, ft4 reading)], 'agree': …}]
```

Plain PEFT: `PeftModel.from_pretrained(Qwen2_5_VLForConditionalGeneration.from_pretrained("Misraj/Baseer__Nakba"),
"<snapshot>/ft3")`. Use the authors' settings: prompt "Extract the text from the above document." with the default
system prompt, `min_pixels=28*28`, `max_pixels=1280*28*28`, greedy, `repetition_penalty=1.1`, `max_new_tokens=128`,
**batch size 1** (batching makes Qwen2.5-VL stop early on transformers 4.56: 72% vs 91% on 32 test lines).

**Page mode** segments lines with [Kraken](https://kraken.re) (`pip install "kraken>=5"`, best in its own venv) and the
[Muharaf segmentation model](https://zenodo.org/records/14295555) (CC BY 4.0, downloaded on first use). Without
Kraken it falls back to horizontal projection, which only works for single-column pages. For mixed pages
(typed + handwritten, stamps, other scripts) use a layout model first and read only the handwritten regions — the
adapters invent Arabic text on stamps and non-Arabic blocks (e.g. Hebrew notary text).

Memory: ~9 GB VRAM in fp16 (base 3.75 B parameters + two adapters). CPU works (bf16, ~9 GB RAM) but is slow.

## Training

| | ft3 | ft4 | ft1 | ft2 |
|---|---|---|---|---|
| LoRA | language + vision | language + vision | language + vision | language only |
| steps × lines | 2000 × 16 | 2000 × 16 | 600 × 16 | 600 × 16 |
| sampling weights muharaf / omar / arams / khatt | 2 / **2** / 1 / 1 | 2 / 1 / 1 / 1 | 2 / 1 / 1 / 1 | 2 / 1 / 1 / 1 |
| validation CER (148 mixed lines) | 0.0860 | 0.0856 | 0.1106 | 0.1272 |

rsLoRA r=32, alpha=64, dropout 0.05; language q/k/v/o/gate/up/down (LR 1e-4), vision qkv/proj/mlp (LR 2e-5);
16 lines per step, warmup 100 + cosine, fp16 + GradScaler on a T4, loss on answer tokens only, 50% of training images
synthetically aged (yellowed paper, stains, ruled lines, show-through, stamps, fingerprints, phone-photo blur).

Data: Omar Al-Saleh train+test (CC BY 4.0), Muharaf train/validation (CC BY-NC-SA 4.0), AraMS-28k-HTR, KHATT. Lines
whose label equals a label of the evaluation sets were removed; for ft3/ft4 whole Muharaf documents were held out
as the unseen-writers set.

## License

CC BY-NC-SA 4.0 (non-commercial, share-alike, attribution) — inherited from Baseer-Nakba and Muharaf.
`inference.py` follows the authors' inference settings (github.com/misraj-ai/Nakba-pipeline).
