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

--giu-muharaf tu_dong: GIỮ RIÊNG các nhóm tài liệu Muharaf (nhóm = tiền tố chữ của tên trang, vd. BEK, YFS) KHÔNG có
trong Muharaf test → không đưa vào train/val; ghi <goc>/giu_lai_muharaf/danh_sach.csv (tập "giu_lai") để chấm "người
viết lạ" bằng eval_lines --data <goc>/giu_lai_muharaf --split giu_lai. Vì các nhóm này không có trong test nên điểm
Muharaf test vẫn so được với các lần trước. (Baseer gốc và ft1/ft2 ĐÃ học các dòng này → so với chúng là bất lợi cho
model mới: model mới vẫn thắng thì chắc chắn.)
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
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


def nhom_muharaf(trang: str) -> str:
    """Nhóm tài liệu (≈ bộ sưu tập / người viết) từ tên trang: tiền tố chữ (BEK1A_27_02r → BEK, kc0061_… → kc,
    KEllis2018-139d → KEllis); tên bắt đầu bằng số → phần đầu (2015 5-03 El-Khouri… → 2015). Gộp thô = an toàn hơn."""
    m = re.match(r"[A-Za-z]+", trang)
    return m.group(0) if m else re.split(r"[ _-]", trang)[0]


def lay_muharaf(goc: Path, giu: set[str] = frozenset()) -> dict[str, list[dict]]:
    d = goc / "muharaf"
    if not (d / "danh_sach.csv").exists():
        _tai(["htr_test.tai_muharaf", str(d), "--splits", "train,validation"])
    res: dict[str, list[dict]] = {"train": [], "val": [], "giu_lai": []}
    for r in csv.DictReader(open(d / "danh_sach.csv", encoding="utf-8")):
        if r["tap"] not in ("train", "validation"):
            continue
        nhan = (d / r["nhan"]).read_text(encoding="utf-8").strip()
        if not nhan:
            continue
        x = {"anh": str((d / r["anh"]).resolve()), "nhan": nhan, "nguon": "muharaf", "trang": r["trang"],
             "nhan_file": str((d / r["nhan"]).resolve()), "mau": r["mau"]}
        tap = "giu_lai" if nhom_muharaf(r["trang"]) in giu else ("train" if r["tap"] == "train" else "val")
        res[tap].append(x)
    return res


def nhom_muharaf_test(goc: Path) -> set[str]:
    m = goc / "cham_muharaf"
    return {nhom_muharaf(r["trang"]) for r in csv.DictReader(open(m / "danh_sach.csv", encoding="utf-8"))
            if r["tap"] == "test"}


def ghi_giu_lai(goc: Path, ds: list[dict], nhom: set[str]) -> Path:
    """Tập chấm "người viết lạ" theo bố cục eval_lines (danh_sach.csv; đường dẫn tuyệt đối)."""
    d = goc / "giu_lai_muharaf"
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "danh_sach.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tap", "mau", "trang", "anh", "nhan"])
        w.writeheader()
        for x in ds:
            w.writerow({"tap": "giu_lai", "mau": x["mau"], "trang": x["trang"], "anh": x["anh"], "nhan": x["nhan_file"]})
    (d / "NGUON.md").write_text(
        f"# Muharaf — nhóm tài liệu giữ riêng (không có trong huấn luyện từ ft3)\n\nNhóm: {', '.join(sorted(nhom))}\n"
        f"Số dòng: {len(ds)} (train + validation của các nhóm này). Không nhóm nào có trong Muharaf test.\n",
        encoding="utf-8")
    return d


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
    ap.add_argument("--giu-muharaf", default="", help='"tu_dong" = giữ riêng mọi nhóm Muharaf KHÔNG có trong test; '
                    'hoặc danh sách nhóm "BEK,YFS"; rỗng = không giữ (như ft1/ft2)')
    a = ap.parse_args()
    goc = Path(a.goc).expanduser().resolve()
    goc.mkdir(parents=True, exist_ok=True)
    train, val, tk = [], [], []
    cam = nhan_tap_cham(goc)
    giu: set[str] = set()
    if a.giu_muharaf == "tu_dong":
        mu = goc / "muharaf"
        if not (mu / "danh_sach.csv").exists():
            _tai(["htr_test.tai_muharaf", str(mu), "--splits", "train,validation"])
        co = {nhom_muharaf(r["trang"]) for r in csv.DictReader(open(mu / "danh_sach.csv", encoding="utf-8"))}
        giu = co - nhom_muharaf_test(goc)
    elif a.giu_muharaf:
        giu = {x.strip() for x in a.giu_muharaf.split(",") if x.strip()}
        if giu & nhom_muharaf_test(goc):
            sys.exit(f"✘ nhóm {sorted(giu & nhom_muharaf_test(goc))} có trong Muharaf test — không giữ riêng được")
    if giu:
        print(f"== giữ riêng nhóm Muharaf: {', '.join(sorted(giu))}", flush=True)
    lay = {"omar": lay_omar, "muharaf": lambda g: lay_muharaf(g, giu), "arams": lay_arams, "khatt": lay_khatt}
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
        if r.get("giu_lai"):
            d = ghi_giu_lai(goc, r["giu_lai"], giu)
            tk.append(f"| muharaf GIỮ RIÊNG ({', '.join(sorted(giu))}) | — | — | {len(r['giu_lai'])} dòng → {d.name}/ |")
            print(f"   GIỮ RIÊNG {len(r['giu_lai'])} dòng → {d}", flush=True)
    for ten, ds in (("train", train), ("val", val)):
        with open(goc / f"{ten}.jsonl", "w", encoding="utf-8") as fo:
            for x in ds:
                fo.write(json.dumps({k: x[k] for k in ("anh", "nhan", "nguon")}, ensure_ascii=False) + "\n")
    (goc / "thong_ke.md").write_text(
        "# Dữ liệu huấn luyện\n\n| Nguồn | train | val | bỏ (trùng nhãn tập chấm) |\n|---|---:|---:|---:|\n" + "\n".join(tk)
        + f"\n\nTổng: train {len(train)} · val {len(val)}. Tập chấm (Omar blind_test, Muharaf test) KHÔNG có trong dữ liệu này.\n",
        encoding="utf-8")
    print(f"✔ train {len(train)} · val {len(val)} → {goc}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
