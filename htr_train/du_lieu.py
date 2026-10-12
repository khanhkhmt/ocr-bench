"""Gom dữ liệu huấn luyện dòng chữ viết tay → <goc>/train.jsonl, val.jsonl, thong_ke.md.

    python -m htr_train.du_lieu <goc> [--nguon omar,muharaf,arams,khatt]

Mỗi dòng jsonl: {"anh": đường dẫn tuyệt đối, "nhan": chữ, "nguon": tên bộ}.
Nguồn:
  omar     Omar Al-Saleh train + test (CC BY 4.0, gated → HF_TOKEN). TẬP CHẤM blind_test KHÔNG BAO GIỜ được lấy.
  muharaf  Muharaf train → train, validation → val (ảnh MÀU giấy cũ). TẬP CHẤM test KHÔNG lấy.
  arams    AraMS-28k-HTR (bản thảo Naskh / Ruq'ah / Maghribi, ~28k dòng; zip 2,4 GB) — theo train/val manifest của bộ.
  khatt    KHATT (chữ tay hiện đại nhiều người viết; cặp .tif + .txt).
Chống rò rỉ: bỏ mọi dòng huấn luyện có nhãn (đã chuẩn hoá) TRÙNG một nhãn của tập chấm (Omar blind_test, Muharaf
test) — tập chấm được tải lại để so (Omar blind_test cần HF_TOKEN; thiếu thì cảnh báo, bỏ qua phần đó).
Chạy lại = dùng lại dữ liệu đã tải.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ocrbench.normalize import NormConfig, normalize  # noqa: E402

NORM = NormConfig(strip_markdown=False, strip_diacritics=True, unify_alef=True, unify_yeh=True, unify_digits=True)
IMG = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")


def _k(t: str) -> str:
    return " ".join(normalize(t, NORM).split())


def _tu_thu_muc(d: Path, taps: list[str], nguon: str) -> dict[str, list[dict]]:
    """Thư mục do htr_test.tai_omar / tai_muharaf tạo (danh_sach.csv) → {tập: [mục]}."""
    out: dict[str, list[dict]] = {t: [] for t in taps}
    for r in csv.DictReader(open(d / "danh_sach.csv", encoding="utf-8")):
        if r["tap"] in out:
            nhan = (d / r["nhan"]).read_text(encoding="utf-8").strip()
            if nhan:
                out[r["tap"]].append({"anh": str((d / r["anh"]).resolve()), "nhan": nhan, "nguon": nguon})
    return out


def _tai(lenh: list[str]) -> None:
    import subprocess

    if subprocess.run([sys.executable, "-m", *lenh], cwd=ROOT).returncode:
        sys.exit(f"✘ lỗi khi chạy: {' '.join(lenh)}")


def lay_omar(goc: Path) -> dict[str, list[dict]]:
    d = goc / "omar"
    if not (d / "danh_sach.csv").exists():
        _tai(["htr_test.tai_omar", str(d), "--splits", "train,test"])
    o = _tu_thu_muc(d, ["train", "test"], "omar")
    return {"train": o["train"] + o["test"], "val": []}


def lay_muharaf(goc: Path) -> dict[str, list[dict]]:
    d = goc / "muharaf"
    if not (d / "danh_sach.csv").exists():
        _tai(["htr_test.tai_muharaf", str(d), "--splits", "train,validation"])
    m = _tu_thu_muc(d, ["train", "validation"], "muharaf")
    return {"train": m["train"], "val": m["validation"]}


def _giai_nen(repo: str, ten: str, dich: Path) -> Path:
    from huggingface_hub import hf_hub_download

    if not (dich / ".xong").exists():
        z = hf_hub_download(repo, ten, repo_type="dataset")
        dich.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(z) as zf:
            zf.extractall(dich)
        (dich / ".xong").write_text("ok")
    return dich


def _cap_anh_nhan(d: Path, nguon: str, chi: set[Path] | None = None) -> list[dict]:
    """Ảnh + nhãn cùng tên (<ảnh>.gt.txt hoặc <tên>.txt)."""
    out = []
    for p in sorted(d.rglob("*")):
        if p.suffix.lower() not in IMG or (chi is not None and p.resolve() not in chi):
            continue
        for t in (p.with_suffix(".gt.txt"), p.with_name(p.name + ".gt.txt"), p.with_suffix(".txt")):
            if t.exists():
                nhan = t.read_text(encoding="utf-8", errors="replace").strip()
                if nhan:
                    out.append({"anh": str(p.resolve()), "nhan": nhan, "nguon": nguon})
                break
    return out


def lay_arams(goc: Path) -> dict[str, list[dict]]:
    d = _giai_nen("Archatext/AraMS-28k-HTR", "AraMS-28k-HTR.zip", goc / "arams")
    res = {}
    # tập test của AraMS KHÔNG phải tập chấm của mình → gộp vào train. Đường dẫn trong manifest tính từ GỐC zip.
    for tap, tens in (("train", ("train_manifest.txt", "test_manifest.txt")), ("val", ("val_manifest.txt",))):
        chi: set[Path] = set()
        for ten in tens:
            mf = next(d.rglob(ten), None)
            if mf is None:
                continue
            for ln in mf.read_text(encoding="utf-8").splitlines():
                if ln.strip():
                    q = (d / ln.strip()).resolve()
                    chi.add(q if q.exists() else (mf.parent / ln.strip()).resolve())
        res[tap] = _cap_anh_nhan(d, "arams", chi) if chi else []
    if not res["train"]:  # bố cục zip khác dự kiến → lấy hết làm train
        res["train"] = _cap_anh_nhan(d, "arams")
    return res


def lay_khatt(goc: Path) -> dict[str, list[dict]]:
    tr = _giai_nen("benhachem/KHATT", "data/train.zip", goc / "khatt" / "train")
    va = _giai_nen("benhachem/KHATT", "data/validation.zip", goc / "khatt" / "validation")
    return {"train": _cap_anh_nhan(tr, "khatt"), "val": _cap_anh_nhan(va, "khatt")}


def nhan_tap_cham(goc: Path) -> set[str]:
    """Nhãn (chuẩn hoá) của HAI tập chấm — dùng để loại dòng huấn luyện trùng."""
    cam: set[str] = set()
    m = goc / "cham_muharaf"
    if not (m / "danh_sach.csv").exists():
        _tai(["htr_test.tai_muharaf", str(m), "--splits", "test"])
    cam |= {_k(x["nhan"]) for x in _tu_thu_muc(m, ["test"], "x")["test"]}
    o = goc / "cham_omar"
    if not (o / "danh_sach.csv").exists():
        import subprocess

        if subprocess.run([sys.executable, "-m", "htr_test.tai_omar", str(o), "--splits", "blind_test"], cwd=ROOT).returncode:
            print("⚠ không tải được Omar blind_test (thiếu HF_TOKEN?) — không kiểm trùng nhãn với tập này", flush=True)
            return cam
    cam |= {_k(x["nhan"]) for x in _tu_thu_muc(o, ["blind_test"], "x")["blind_test"]}
    return cam


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("goc")
    ap.add_argument("--nguon", default="omar,muharaf,arams,khatt")
    ap.add_argument("--val-omar", type=int, default=300, help="giữ riêng N dòng Omar (train/test) làm val")
    a = ap.parse_args()
    goc = Path(a.goc).expanduser().resolve()
    goc.mkdir(parents=True, exist_ok=True)
    lay = {"omar": lay_omar, "muharaf": lay_muharaf, "arams": lay_arams, "khatt": lay_khatt}
    train, val, tk = [], [], []
    cam = nhan_tap_cham(goc)
    for n in [x.strip() for x in a.nguon.split(",") if x.strip()]:
        print(f"== {n}", flush=True)
        r = lay[n](goc)
        if n == "omar" and a.val_omar:
            random.Random(0).shuffle(r["train"])
            r["val"], r["train"] = r["train"][: a.val_omar], r["train"][a.val_omar:]
        bo = 0
        for tap, ds in (("train", train), ("val", val)):
            for x in r[tap]:
                if _k(x["nhan"]) in cam:
                    bo += 1
                    continue
                ds.append(x)
        tk.append(f"| {n} | {len(r['train'])} | {len(r['val'])} | {bo} |")
        print(f"   train {len(r['train'])} · val {len(r['val'])} · bỏ vì trùng nhãn tập chấm {bo}", flush=True)
    for ten, ds in (("train", train), ("val", val)):
        with open(goc / f"{ten}.jsonl", "w", encoding="utf-8") as fo:
            for x in ds:
                fo.write(json.dumps(x, ensure_ascii=False) + "\n")
    (goc / "thong_ke.md").write_text(
        "# Dữ liệu huấn luyện\n\n| Nguồn | train | val | bỏ (trùng nhãn tập chấm) |\n|---|---:|---:|---:|\n" + "\n".join(tk)
        + f"\n\nTổng: train {len(train)} · val {len(val)}. Tập chấm (Omar blind_test, Muharaf test) KHÔNG có trong dữ liệu này.\n",
        encoding="utf-8")
    print(f"✔ train {len(train)} · val {len(val)} → {goc}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
