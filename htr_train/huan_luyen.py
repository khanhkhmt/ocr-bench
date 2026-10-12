"""Huấn luyện tiếp Baseer-Nakba (Qwen2.5-VL-3B) bằng LoRA trên dòng chữ tay giống giấy tờ cũ (htr_train/du_lieu.py).

    <python venv dots> -m htr_train.huan_luyen --data <goc> --out <thư mục> [--gpu 0] [--max-steps 3000]

- Prompt / tiền xử lý ảnh GIỐNG HỆT lúc đọc (htr_test.models.BaseerNakba): system mặc định + ảnh +
  "Extract the text from the above document.", min_pixels 28·28, max_pixels 1280·28·28 → model học đúng điều kiện dùng.
- LoRA cả phần NGÔN NGỮ và phần ẢNH (đội thắng NAKBA: mở encoder ảnh giúp WER giảm > 5 điểm), LR riêng cho phần ảnh.
- Làm cũ ảnh ngẫu nhiên (htr_train/lam_cu.py) — nhiều với ảnh sạch (Omar, KHATT), ít với ảnh đã cũ (Muharaf, AraMS).
- Lấy mẫu theo nguồn (--trong-so muharaf=2,…): ưu tiên giấy cũ màu.
- T4 không có bf16 → trọng số nền fp16, tham số LoRA fp32 + autocast fp16 + GradScaler. Gradient checkpointing.
- Lưu checkpoint mỗi --save-every bước vào <out>/ckpt-<bước> (adapter + trạng thái optimizer) → chạy lại = đi tiếp
  (Kaggle / Colab ngắt). Mỗi --eval-every bước: đọc --eval-n dòng val (đọc từng dòng, như lúc dùng thật) → CER;
  checkpoint tốt nhất chép sang <out>/best. Nhật ký: <out>/nhat_ky.jsonl.
- Tập CHẤM (Omar blind_test, Muharaf test) không có trong dữ liệu (du_lieu.py đã loại).
Đọc bằng model mới: htr_test eval_lines --models baseer_ft --lora <out>/best.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import shutil
import sys
import time
from pathlib import Path

import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from htr_test.models import BaseerNakba, clean_repeated_substrings, resolve_dtype  # noqa: E402
from htr_train.lam_cu import lam_cu  # noqa: E402

LM_RE = r"(?!.*visual).*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)"
VIS_RE = r".*visual\.blocks\.\d+\.(attn\.qkv|attn\.proj|mlp\.gate_proj|mlp\.up_proj|mlp\.down_proj)"
P_LAM_CU = {"omar": 1.0, "khatt": 1.0, "muharaf": 0.3, "arams": 0.5}  # nhân với --lam-cu


def doc_jsonl(f: Path) -> list[dict]:
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def danh_sach_mau(items: list[dict], trong_so: dict[str, float], max_mau: int, rng: random.Random) -> list[int]:
    """Chỉ số mẫu cho một epoch: mỗi mục lặp theo trọng số nguồn (phần lẻ → ngẫu nhiên), rồi xáo."""
    idx = []
    for i, x in enumerate(items):
        w = trong_so.get(x["nguon"], 1.0)
        idx += [i] * int(w) + ([i] if rng.random() < w - int(w) else [])
    rng.shuffle(idx)
    return idx[:max_mau] if max_mau else idx


def nap_model(a, dev: str):
    """→ (model PEFT, processor). Tách hàm để kiểm thử thay bằng model thu nhỏ."""
    from peft import LoraConfig, get_peft_model
    from transformers import AutoConfig, AutoProcessor, Qwen2_5_VLForConditionalGeneration

    dtype = resolve_dtype(a.dtype) if dev != "cpu" else torch.float32
    cfg = BaseerNakba._fix_config(AutoConfig.from_pretrained(a.base))
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(a.base, config=cfg, torch_dtype=dtype,
                                                               device_map={"": dev})
    proc = AutoProcessor.from_pretrained(a.base, min_pixels=28 * 28, max_pixels=1280 * 28 * 28)
    return them_lora(model, a), proc


def them_lora(model, a):
    from peft import LoraConfig, get_peft_model

    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    target = f"(?:{LM_RE})" + (f"|(?:{VIS_RE})" if a.vision else "")
    model = get_peft_model(model, LoraConfig(r=a.lora_r, lora_alpha=a.lora_alpha, lora_dropout=a.dropout,
                                             target_modules=target, use_rslora=True, task_type="CAUSAL_LM"))
    for p in model.parameters():  # tham số học ở fp32 (an toàn với GradScaler)
        if p.requires_grad:
            p.data = p.data.float()
    return model


class Gom:
    """Ghép một lô: prompt (giống lúc đọc) + nhãn + <|im_end|>; nhãn chỉ tính trên phần trả lời."""

    def __init__(self, proc, items, lam_cu_p: float, rng: random.Random):
        self.proc, self.items, self.p, self.rng = proc, items, lam_cu_p, rng
        self.prompt = BaseerNakba.TEMPLATE.format(p=BaseerNakba.PROMPT)
        self.proc.tokenizer.padding_side = "right"

    def anh(self, x: dict) -> Image.Image:
        img = Image.open(x["anh"]).convert("RGB")
        if self.rng.random() < self.p * P_LAM_CU.get(x["nguon"], 1.0):
            ban = Image.open(self.items[self.rng.randrange(len(self.items))]["anh"]) if self.rng.random() < 0.5 else None
            img = lam_cu(img, self.rng, ban=ban)
        return img

    def __call__(self, batch: list[dict]) -> dict:
        imgs = [self.anh(x) for x in batch]
        full = [self.prompt + x["nhan"] + "<|im_end|>" for x in batch]
        enc = self.proc(text=full, images=imgs, return_tensors="pt", padding=True)
        labels = enc["input_ids"].clone()
        labels[enc["attention_mask"] == 0] = -100
        for i, img in enumerate(imgs):  # che phần prompt (cùng ảnh → cùng số token ảnh)
            n = self.proc(text=[self.prompt], images=[img], return_tensors="pt")["input_ids"].shape[1]
            labels[i, :n] = -100
        enc["labels"] = labels
        return enc


@torch.no_grad()
def danh_gia(model, proc, val: list[dict], dev: str) -> dict:
    """Đọc từng dòng (lô 1, tham số như BaseerNakba.read) → CER / WER chuẩn hoá (htr_test.eval_lines.score)."""
    from htr_test.eval_lines import score

    model.eval()
    model.config.use_cache = True
    proc.tokenizer.padding_side = "left"
    prompt = BaseerNakba.TEMPLATE.format(p=BaseerNakba.PROMPT)
    pairs = []
    for x in val:
        enc = proc(text=[prompt], images=[Image.open(x["anh"]).convert("RGB")], return_tensors="pt").to(dev)
        with torch.autocast("cuda", dtype=torch.float16, enabled=dev != "cpu"):
            ids = model.generate(**enc, max_new_tokens=128, do_sample=False, repetition_penalty=1.1,
                                 eos_token_id=[151645, 151643], pad_token_id=151643)
        hyp = clean_repeated_substrings(proc.decode(ids[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).strip())
        pairs.append((x["nhan"], hyp))
    model.config.use_cache = False
    proc.tokenizer.padding_side = "right"
    model.train()
    s = score(pairs)
    return {"cer": s["chuan_hoa"]["cer"], "wer": s["chuan_hoa"]["wer"], "ngan": s["do_dai"]["ngan_x0_5"],
            "dai": s["do_dai"]["dai_x1_5"], "n": len(pairs)}


def _ckpts(out: Path) -> list[Path]:
    return sorted(out.glob("ckpt-*"), key=lambda p: int(p.name.split("-")[1]))


def luu(model, opt, sch, scaler, out: Path, buoc: int, vi_tri: int, giu: int = 2) -> Path:
    d = out / f"ckpt-{buoc}"
    model.save_pretrained(d)
    torch.save({"opt": opt.state_dict(), "sch": sch.state_dict(), "scaler": scaler.state_dict(), "buoc": buoc,
                "vi_tri": vi_tri}, d / "trang_thai.pt")
    for old in _ckpts(out)[:-giu]:
        shutil.rmtree(old, ignore_errors=True)
    return d


def viet_tom_tat(out: Path, buoc_toi_da: int, ghi_chu: str) -> None:
    """<out>/tom_tat.md từ nhat_ky.jsonl: bước, loss gần nhất, bảng các lần đánh giá (đọc được trên GitHub)."""
    rows = [json.loads(x) for x in (out / "nhat_ky.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    hl = [r for r in rows if "buoc" in r and "loss" in r]
    dg = [r["danh_gia"] for r in rows if "danh_gia" in r]
    L = [f"# Huấn luyện {out.name} — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}", "", f"Trạng thái: {ghi_chu}", ""]
    if hl:
        r = hl[-1]
        L += [f"Bước {r['buoc']}/{buoc_toi_da} · loss {r['loss']} · {r['s_buoc']} s/bước · lr {r['lr']:.2e}", ""]
    L += ["| bước | đúng ký tự (val) | đúng từ | dòng sót | dòng dài | số dòng |", "|---:|---:|---:|---:|---:|---:|"]
    L += [f"| {d['buoc']} | {max(0.0, 100 - 100 * d['cer']):.1f}% | {max(0.0, 100 - 100 * d['wer']):.1f}% | {d['ngan']} | "
          f"{d['dai']} | {d['n']} |" for d in dg]
    p = out / "tham_so.json"
    if p.exists():
        L += ["", "Tham số: `" + json.dumps({k: v for k, v in json.loads(p.read_text()).items()
                                             if k not in ("data", "out")}, ensure_ascii=False) + "`"]
    (out / "tom_tat.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None, nap=nap_model) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", default=BaseerNakba.REPO)
    ap.add_argument("--gpu", type=int, default=0, help="-1 = CPU (chỉ để thử)")
    ap.add_argument("--dtype", default="auto", choices=["auto", "fp16", "fp32"])
    ap.add_argument("--lora-r", type=int, default=32)
    ap.add_argument("--lora-alpha", type=int, default=64)
    ap.add_argument("--dropout", type=float, default=0.05)
    ap.add_argument("--vision", type=int, default=1, help="1 = LoRA cả phần ảnh")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lr-vision", type=float, default=2e-5)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--accum", type=int, default=4)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--max-steps", type=int, default=0, help="0 = hết 1 epoch (theo --max-mau)")
    ap.add_argument("--max-mau", type=int, default=0, help="giới hạn số mẫu / epoch (0 = hết)")
    ap.add_argument("--trong-so", default="muharaf=2,omar=1,arams=1,khatt=1")
    ap.add_argument("--lam-cu", type=float, default=0.5, help="xác suất làm cũ ảnh (nhân hệ số theo nguồn)")
    ap.add_argument("--save-every", type=int, default=200)
    ap.add_argument("--eval-every", type=int, default=400)
    ap.add_argument("--eval-n", type=int, default=150)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--push", action="store_true",
                    help="đẩy nhat_ky.jsonl + tom_tat.md (KHÔNG đẩy model) lên nhánh results-htr/<tên thư mục out> mỗi 10 phút")
    a = ap.parse_args(argv)
    dev = f"cuda:{a.gpu}" if a.gpu >= 0 else "cpu"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "tham_so.json").write_text(json.dumps(vars(a), ensure_ascii=False, indent=1), encoding="utf-8")
    train = doc_jsonl(Path(a.data) / "train.jsonl")
    val_all = doc_jsonl(Path(a.data) / "val.jsonl")
    rv = random.Random(1)
    by_src: dict[str, list] = {}
    for x in val_all:
        by_src.setdefault(x["nguon"], []).append(x)
    val = []  # val chia đều theo nguồn
    for src in sorted(by_src):
        val += rv.sample(by_src[src], min(len(by_src[src]), max(1, a.eval_n // len(by_src))))
    trong_so = {k: float(v) for k, v in (kv.split("=") for kv in a.trong_so.split(",") if kv)}
    rng = random.Random(a.seed)
    thu_tu = danh_sach_mau(train, trong_so, a.max_mau, rng)
    buoc_toi_da = a.max_steps or math.ceil(len(thu_tu) / (a.batch * a.accum))
    print(f"train {len(train)} mục → {len(thu_tu)} mẫu/epoch · val chấm {len(val)} · tối đa {buoc_toi_da} bước", flush=True)

    t0 = time.time()
    model, proc = nap(a, dev)
    print(f"nạp model {time.time() - t0:.0f}s", flush=True)
    model.print_trainable_parameters()
    vis = [p for n, p in model.named_parameters() if p.requires_grad and ".visual." in n]
    lm = [p for n, p in model.named_parameters() if p.requires_grad and ".visual." not in n]
    opt = torch.optim.AdamW([{"params": lm, "lr": a.lr}, {"params": vis, "lr": a.lr_vision}], weight_decay=0.01)
    from transformers import get_cosine_schedule_with_warmup

    sch = get_cosine_schedule_with_warmup(opt, a.warmup, buoc_toi_da)
    amp = dev != "cpu" and resolve_dtype(a.dtype) == torch.float16
    scaler = torch.amp.GradScaler("cuda", enabled=amp)
    buoc, vi_tri, best = 0, 0, None
    ck = _ckpts(out)
    if ck:  # chạy lại = đi tiếp
        from peft import set_peft_model_state_dict
        from safetensors.torch import load_file

        st = torch.load(ck[-1] / "trang_thai.pt", map_location="cpu", weights_only=False)
        set_peft_model_state_dict(model, load_file(str(ck[-1] / "adapter_model.safetensors")))
        for p in model.parameters():
            if p.requires_grad:
                p.data = p.data.float()
        opt.load_state_dict(st["opt"])
        sch.load_state_dict(st["sch"])
        scaler.load_state_dict(st["scaler"])
        buoc, vi_tri = st["buoc"], st["vi_tri"]
        print(f"✔ đi tiếp từ {ck[-1].name} (bước {buoc}, mẫu thứ {vi_tri})", flush=True)
    bf = out / "best" / "diem.json"
    if bf.exists():
        best = json.loads(bf.read_text())["cer"]
    gom = Gom(proc, train, a.lam_cu, random.Random(a.seed + buoc))
    nk = open(out / "nhat_ky.jsonl", "a", encoding="utf-8")
    sync = None
    if a.push:
        from htr_test.sync import Sync

        sync = Sync(out, every_min=10)

    def day(ghi_chu: str, ep: bool = False) -> None:
        if sync and (ep or sync.due()):
            viet_tom_tat(out, buoc_toi_da, ghi_chu)
            sync.push(ghi_chu)
    model.train()
    t_buoc, lo_mat = time.time(), []
    while buoc < buoc_toi_da:
        opt.zero_grad(set_to_none=True)
        for _ in range(a.accum):
            if vi_tri >= len(thu_tu):  # hết epoch → epoch mới, xáo lại
                thu_tu = danh_sach_mau(train, trong_so, a.max_mau, random.Random(a.seed + buoc + 1))
                vi_tri = 0
            batch = [train[i] for i in thu_tu[vi_tri:vi_tri + a.batch]]
            vi_tri += a.batch
            enc = {k: v.to(dev) for k, v in gom(batch).items()}
            with torch.autocast("cuda", dtype=torch.float16, enabled=amp):
                loss = model(**enc).loss / a.accum
            scaler.scale(loss).backward()
            lo_mat.append(loss.item() * a.accum)
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_([p for g in opt.param_groups for p in g["params"]], 1.0)
        scaler.step(opt)
        scaler.update()
        sch.step()
        buoc += 1
        if buoc % 10 == 0 or buoc == 1:
            rec = {"buoc": buoc, "loss": round(sum(lo_mat) / len(lo_mat), 4), "lr": sch.get_last_lr()[0],
                   "s_buoc": round((time.time() - t_buoc) / max(1, len(lo_mat) // a.accum), 2)}
            print(f"   bước {buoc}/{buoc_toi_da} · loss {rec['loss']} · {rec['s_buoc']} s/bước", flush=True)
            nk.write(json.dumps(rec) + "\n")
            nk.flush()
            t_buoc, lo_mat = time.time(), []
            day(f"bước {buoc}/{buoc_toi_da} · loss {rec['loss']}")
        if buoc % a.save_every == 0 or buoc == buoc_toi_da:
            d = luu(model, opt, sch, scaler, out, buoc, vi_tri)
            print(f"✔ lưu {d.name}", flush=True)
        if buoc % a.eval_every == 0 or buoc == buoc_toi_da:
            s = danh_gia(model, proc, val, dev)
            s["buoc"] = buoc
            nk.write(json.dumps({"danh_gia": s}) + "\n")
            nk.flush()
            print(f"== ĐÁNH GIÁ bước {buoc}: đúng ký tự {max(0.0, 100 - 100 * s['cer']):.1f}% · đúng từ {max(0.0, 100 - 100 * s['wer']):.1f}% "
                  f"· sót {s['ngan']} · dài {s['dai']} ({s['n']} dòng val)", flush=True)
            if best is None or s["cer"] < best:
                best = s["cer"]
                model.save_pretrained(out / "best")
                (out / "best" / "diem.json").write_text(json.dumps(s), encoding="utf-8")
                print(f"★ tốt nhất mới → {out / 'best'}", flush=True)
            day(f"đánh giá bước {buoc}: đúng ký tự {max(0.0, 100 - 100 * s['cer']):.1f}%", ep=True)
    print("✔ XONG HUẤN LUYỆN", flush=True)
    day("XONG HUẤN LUYỆN", ep=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
