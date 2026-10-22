"""Đợt 1 — thử KHÔNG cần huấn luyện, trên server GPU (Kaggle 2× T4). Chạy cả đợt: bash htr_test/chay_dot1.sh.

Bộ test (cố định, ghi ra bo__*.jsonl):
  omar_A / muharaf_A / giulai_A   500 dòng mỗi bộ = ĐÚNG 500 dòng (seed 0) của các lần chấm trước → so được số cũ.
                                  Dùng để CHỌN cách tốt nhất.
  omar_B / muharaf_B / giulai_B   500 dòng KHÁC (seed 1, không trùng A) → XÁC NHẬN cách đã chọn (tránh chọn trúng may).
  trang4                          dòng của 4 trang mẫu (Kraken cắt, như sản phẩm) → chấm cả trang bằng nhãn trang.
  mtrang_vang / mtrang_kraken     66 trang Muharaf test (ảnh cả trang, Zenodo 11492215): dòng cắt theo khung CHUẨN của
                                  bộ dữ liệu / dòng do KRAKEN tự cắt → Bước 0: tách dòng làm mất bao nhiêu điểm.

Thử nghiệm (cùng một nền Baseer-Nakba + 3 adapter ft3 / ft4 / ft1 của khanh99/htr-baseer-nakba-ft):
  #1 trộn ft3 + ft4 (0,5 / 0,5: y = Wx + ½·ΔW₃x + ½·ΔW₄x — chính xác, không gộp trọng số gần đúng)
  #2 độ mạnh ft3: 0,5 / 0,75 / 1,25 (1 = như huấn luyện)
  #3 bầu chọn nhiều bản đọc (theo từ và theo cả dòng), tính từ các bản đọc đã có — không tốn GPU
  #4 Bước 0 (trên)
  #5 dots đọc lại TỪNG khối chữ đánh máy, phóng ×1,5 / ×2 / ×3 (trang 1, 3, 4)
Luật chọn / luật đạt viết SẴN trong file này (LUAT) — báo cáo tự áp, không chỉnh tay sau khi thấy số.

Lệnh con (python = venv của arabic-doc-ocr, ADOC=<thư mục arabic-doc-ocr>):
  bo          tạo các bộ dòng A/B từ dữ liệu đã tải (htr_train.du_lieu)
  bon_trang   dots: bố cục 4 trang (như sản phẩm) + #5 đọc lại từng khối  [GPU]
  mtrang      tải 66 trang Muharaf test (chỉ phần cần, đọc theo khoảng byte) + cắt dòng chuẩn + Kraken  [CPU]
  doc         đọc dòng theo hàng việc (nhiều tiến trình / GPU cùng chạy, tự chia việc, chạy lại = đi tiếp)  [GPU]
  chon        chọn ứng viên từ bộ A theo LUAT → ung_vien.jsonl
  bao_cao     tom_tat.md + tom_tat.json (kết luận theo LUAT)
  tu_kiem     kiểm tra hàm bầu chọn / chấm điểm (CPU, không cần model)
Kết quả: <out>/ (đẩy lên nhánh results-htr/<tên out> bằng --push). Dữ liệu ảnh: <data>/ (không đẩy).
"""

from __future__ import annotations

import argparse
import collections
import contextlib
import csv
import difflib
import importlib.util
import io
import json
import math
import os
import random
import re
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ADOC = Path(os.environ.get("ADOC", "/kaggle/working/arabic-doc-ocr")).resolve()

from ocrbench.metrics import edit_stats  # noqa: E402
from ocrbench.normalize import NormConfig, normalize  # noqa: E402

NORM = NormConfig(strip_markdown=False, strip_diacritics=True, unify_alef=True, unify_yeh=True, unify_digits=True)

# --- cấu hình đọc dòng: {adapter: hệ số}. {} = Baseer-Nakba gốc (tắt adapter) ------------------------------------------
ADAPTERS = ("ft3", "ft4", "ft1")
CAU_HINH = {
    "ft3": {"ft3": 1.0},
    "ft4": {"ft4": 1.0},
    "ft1_s050": {"ft1": 0.5},
    "goc": {},
    "tron34": {"ft3": 0.5, "ft4": 0.5},
    "ft3_s075": {"ft3": 0.75},
    "ft3_s125": {"ft3": 1.25},
    "ft3_s050": {"ft3": 0.5},
}
CH_A = list(CAU_HINH)  # bộ A: mọi cấu hình (ft3 trước — mốc so sánh)
BAU = {"bau4": ["ft3", "ft4", "ft1_s050", "goc"], "bau5": ["ft3", "ft4", "ft1_s050", "goc", "tron34"]}
BO_DONG = ("omar", "muharaf", "giulai")
TEN_BO = {"omar": "Omar blind_test", "muharaf": "Muharaf test", "giulai": "Muharaf người viết lạ"}
N_MAU = 500
CHUNK = 50
PRINTED = ("page_1", "page_3", "page_4")  # loại trang như docs/RESULTS.md của arabic-doc-ocr (page_2 = viết tay)
KHOI_F = (1.5, 2.0, 3.0)  # #5: phóng khối so với trang đã chuẩn bị (sản phẩm đọc cả trang ở ~×1,5)
KHOI_MAX_PX = 4_500_000  # trang 2400 px (~4,1 MP) vừa T4; 3200 px (~7 MP) hết VRAM → giới hạn mỗi khối
MUHARAF_ZIP = "https://zenodo.org/api/records/11492215/files/public_data_files.zip/content"
# #12: nới khung dòng Kraken theo chiều dọc thêm N % độ dày dòng (nửa trên, nửa dưới). Bước 0 thấy dòng Kraken chỉ cao
# ~76% dòng chuẩn (trung vị) → nét trên / dưới và dấu chấm bị tô mất. 0 = cắt y như sản phẩm, đọc lại làm mốc cùng lần chạy.
NO_MUC = (0, 15, 30, 50)

LUAT = {
    "chon": "Ứng viên = cách có điểm ký tự TRUNG BÌNH 3 bộ A cao nhất (mọi cấu hình + mọi kiểu bầu, trừ ft3 và mức trần), "
            "với điều kiện Omar_A không kém ft3 quá 0,3 điểm.",
    "dat_B": "ĐẠT nếu trên bộ B (dòng chưa dùng để chọn): trung bình 3 bộ hơn ft3 ≥ +0,3 điểm VÀ khoảng tin cậy 95% "
             "(bootstrap 2000 lần theo dòng) của mức hơn > 0 VÀ không bộ nào kém ft3 quá 0,3 điểm VÀ 66 trang Muharaf "
             "(Kraken cắt) không kém ft3 quá 0,3 điểm VÀ trang 2 (viết tay) không kém ft3 quá 1,0 điểm.",
    "buoc0": "Hụt = điểm (dòng chuẩn) − điểm (dòng Kraken cắt), cả 66 trang. Hụt ≥ 5 điểm → Đợt 2 LÀM #10 (dạy bằng dòng "
             "Kraken cắt); 2–5 → cân nhắc (xem hụt theo túi từ); < 2 → BỎ #10.",
    "khoi": "#5 ĐẠT nếu mức phóng tốt nhất (theo trung bình trang 1, 3, 4) hơn sản phẩm ≥ +0,5 điểm ký tự và không trang "
            "nào kém quá 0,3 điểm. Chỉ 3 trang và chọn 1 trong 3 mức → ĐẠT vẫn phải xác nhận trên bộ đánh máy khác trước "
            "khi đưa vào sản phẩm.",
    "do_manh": "Độ mạnh ft3: 1,25 tốt nhất (hơn ft3 ≥ 0,2) → ft3 HỌC CHƯA ĐỦ → Đợt 2 train lâu hơn; 0,5 hoặc 0,75 tốt "
               "nhất (hơn ≥ 0,2) → học QUÁ / quên kiến thức gốc → Đợt 2 trộn checkpoint, giữ một phần gốc; còn lại → "
               "không rõ (nhật ký train: CER kiểm tra vẫn giảm ở bước 2000 → nghiêng về train lâu hơn).",
    "bau": "Bầu chọn tốt nhất hơn ft3 ≥ 1,0 điểm (bộ A) → Đợt 2 train vài bản ft5 khác nhau để bầu; ít hơn → một bản.",
    "no": "#12 ĐẠT nếu mức nới tốt nhất (theo % ký tự cả trang, 66 trang Muharaf, đọc bằng ft3) hơn mức 0 % (đọc lại cùng "
          "lần chạy) ≥ +1,0 điểm VÀ túi từ không kém VÀ trang 2 (viết tay của khách, chữ chính) không kém quá 1,0 điểm → "
          "đưa mức đó vào sản phẩm (crop_poly, chờ anh duyệt) và dùng khi cắt dòng Kraken cho #10. Chọn 1 trong 3 mức trên "
          "chính 66 trang → mức hơn hơi lạc quan; model tách dòng Muharaf có thể đã thấy các trang này.",
}


def log(*a) -> None:
    print(time.strftime("[%H:%M:%S]"), *a, flush=True)


def ram_gb() -> float:
    try:
        for ln in open("/proc/meminfo"):
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1]) / 1048576
    except OSError:
        pass
    return -1.0


# --- tiện ích file ----------------------------------------------------------------------------------------------------

def doc_jsonl(f: Path) -> list[dict]:
    if not f.exists():
        return []
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def ghi_jsonl(f: Path, rows: list[dict]) -> None:
    tmp = f.with_name(f.name + ".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    os.replace(tmp, f)  # ghi trọn rồi mới đổi tên → sập giữa chừng không để lại file dở


def bo_file(out: Path, ten: str) -> Path:
    return out / f"bo__{ten}.jsonl"


def doc_bo(out: Path, ten: str) -> list[dict]:
    return doc_jsonl(bo_file(out, ten))


def adoc_eval():
    """scripts/evaluate.py của arabic-doc-ocr (chấm cả trang đúng như docs/RESULTS.md) — nạp theo đường dẫn để không
    đụng gói `evaluate` của Hugging Face có sẵn trên Kaggle."""
    spec = importlib.util.spec_from_file_location("adoc_evaluate", ADOC / "scripts" / "evaluate.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _norm(s: str) -> str:
    return " ".join(normalize(s or "", NORM).split())


# === 1. bộ dòng ========================================================================================================

def _hang(d: Path, tap: str) -> list[dict]:
    """MỌI dòng của tập theo thứ tự danh_sach.csv (kể cả nhãn rỗng) — giống eval_lines.load_lines, để lấy mẫu seed 0
    ra cùng các dòng như các lần chấm trước; dòng nhãn rỗng bỏ SAU khi lấy mẫu."""
    rows = []
    for r in csv.DictReader(open(d / "danh_sach.csv", encoding="utf-8")):
        if r["tap"] == tap:
            rows.append({"id": r["mau"], "anh": str((d / r["anh"]).resolve()),
                         "nhan": (d / r["nhan"]).read_text(encoding="utf-8").strip()})
    return rows


def cmd_bo(a) -> int:
    data, out = Path(a.data), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    nguon = {"omar": (data / "cham_omar", "blind_test"), "muharaf": (data / "cham_muharaf", "test"),
             "giulai": (data / "giu_lai_muharaf", "giu_lai")}
    for ten, (d, tap) in nguon.items():
        if not (d / "danh_sach.csv").exists():
            sys.exit(f"✘ LỖI: thiếu {d}/danh_sach.csv — chạy htr_train.du_lieu trước (xem chay_dot1.sh)")
        rows = _hang(d, tap)
        if len(rows) < 2 * N_MAU + 50:
            sys.exit(f"✘ LỖI: {ten} chỉ có {len(rows)} dòng (< {2 * N_MAU + 50})")
        A0 = random.Random(0).sample(rows, N_MAU)  # = eval_lines --n 500 (seed 0) → cùng mẫu với các lần chấm trước
        da = {r["id"] for r in A0}
        A = [r for r in A0 if r["nhan"]]
        B = random.Random(1).sample([r for r in rows if r["id"] not in da and r["nhan"]], N_MAU)
        for phan, ds in (("A", A), ("B", B)):
            f = bo_file(out, f"{ten}_{phan}")
            cu = doc_jsonl(f)
            if cu and [r["id"] for r in cu] != [r["id"] for r in ds]:
                sys.exit(f"✘ LỖI: {f.name} đã có (khôi phục từ GitHub) nhưng KHÁC bộ vừa tạo — dữ liệu tải về đã đổi")
            ghi_jsonl(f, ds)
        log(f"✔ {ten}: {len(rows)} dòng → A {len(A)} (bỏ {N_MAU - len(A)} nhãn rỗng) · B {len(B)} (không trùng A)")
    return 0


def cmd_khoi_phuc(a) -> int:
    """Kéo kết quả đã đẩy lên GitHub (results-htr/<tên out>) về <out> — server mới sau khi sập đi tiếp từ đó."""
    from htr_test.sync import Sync

    got = Sync(Path(a.out), repo_suffix="-kp").restore()
    log(f"✔ khôi phục: {len(got)} file" if got else "khôi phục: không có gì mới trên GitHub")
    return 0


# === 2. bốn trang mẫu: bố cục dots + #5 =============================================================================

def _trang_mau() -> list[tuple[str, Path, dict]]:
    out = []
    for d in sorted((ADOC / "examples").glob("page_*")):
        img = next((p for p in d.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")), None)
        if img and (d / "label.json").exists():
            out.append((d.name, img, json.loads((d / "label.json").read_text(encoding="utf-8"))))
    if len(out) != 4:
        sys.exit(f"✘ LỖI: cần 4 trang mẫu trong {ADOC}/examples, thấy {len(out)}")
    return out


def _cat_dong(img, rec: dict):
    from arabic_doc_ocr.lines import crop_poly

    box = tuple(rec["box"])
    if rec.get("poly"):
        return crop_poly(img, {"box": box, "poly": [tuple(p) for p in rec["poly"]]})
    return img.crop(box)


def cmd_bon_trang(a) -> int:
    from arabic_doc_ocr.pipeline import Pipeline, free_gpu, load_pages, prepare

    out, data = Path(a.out), Path(a.data)
    crops = data / "crops" / "trang4"
    crops.mkdir(parents=True, exist_ok=True)
    lay_f, bo_f = out / "trang4_bo_cuc.jsonl", bo_file(out, "trang4")
    pages = _trang_mau()
    imgs = {name: prepare(load_pages(p)[0]) for name, p, _ in pages}
    pipe = None
    if lay_f.exists() and bo_f.exists():
        log("bố cục 4 trang đã có (khôi phục) → chỉ cắt lại ảnh dòng theo khung đã lưu")
        bo_cuc = {r["page"]: r for r in doc_jsonl(lay_f)}
        rows = doc_bo(out, "trang4")
    else:
        pipe = Pipeline(a.dots_device, a.dots_device, offload="none")
        bo_cuc, rows = {}, []
        for name, p, _ in pages:
            t = time.time()
            res = pipe.layout(load_pages(p)[0])
            if res.image.size != imgs[name].size:
                sys.exit("✘ LỖI: ảnh trang chuẩn bị khác nhau giữa hai lần — không cắt lại được dòng")
            bo_cuc[name] = {"page": name, "blocks": [{k: v for k, v in b.items() if k in
                                                      ("category", "bbox", "text", "hebrew", "fallback")}
                                                     for b in res.blocks], "info": res.info}
            for n, L in enumerate(res.lines):
                rows.append({"id": f"{name}:L{n:03d}", "nhom": name, "thu_tu": n, "khoi": L.block,
                             "box": list(L.box), "poly": [list(q) for q in L.poly] if L.poly else None,
                             "anh": str(crops / f"{name}_L{n:03d}.png"), "nhan": None})
            log(f"   {name}: {len(res.blocks)} khối, {len(res.lines)} dòng, {time.time() - t:.0f} s "
                f"(dots ×{res.info.get('dots_scale')}, {res.info.get('dots_tokens')} token)")
    for r in rows:  # ảnh dòng TRƯỚC, file bộ SAU → tiến trình đọc không bao giờ thấy bộ mà thiếu ảnh
        if not Path(r["anh"]).exists():
            _cat_dong(imgs[r["nhom"]], r).save(r["anh"])
    if pipe is not None:
        ghi_jsonl(lay_f, [bo_cuc[n] for n, _, _ in pages])
        ghi_jsonl(bo_f, rows)
    log(f"✔ 4 trang: {len(rows)} dòng → {bo_f.name}")

    # --- #5: dots đọc lại từng khối chữ (trang đánh máy) ---
    from arabic_doc_ocr import config as AC
    from arabic_doc_ocr.dots_model import _dots_utils
    from arabic_doc_ocr.text import fix_arabic

    kf = out / "khoi_dots.jsonl"
    xong = {(r["page"], r["khoi"], r["f"]) for r in doc_jsonl(kf)}
    viec = [(name, bi, f) for f in KHOI_F for name in PRINTED for bi, b in enumerate(bo_cuc[name]["blocks"])
            if b.get("category") in AC.TEXT_CATS and not b.get("hebrew") and not b.get("fallback")
            and len(b.get("bbox") or []) == 4 and (b.get("text") or "").strip()]
    viec = [v for v in viec if v not in xong]
    if viec:
        prompts, image_utils, _ = _dots_utils()
        if pipe is None:
            pipe = Pipeline(a.dots_device, a.dots_device, offload="none")
        dots = pipe.models.dots()
        log(f"#5: {len(viec)} khối × mức phóng còn phải đọc")
    for name, bi, f in viec:
        img = imgs[name]
        x0, y0, x1, y1 = [int(round(v)) for v in bo_cuc[name]["blocks"][bi]["bbox"]]
        x0, y0, x1, y1 = max(0, x0 - 6), max(0, y0 - 6), min(img.width, x1 + 6), min(img.height, y1 + 6)
        crop = img.crop((x0, y0, x1, y1))
        f_thuc = min(f, math.sqrt(KHOI_MAX_PX / max(1, crop.width * crop.height)))
        rec = {"page": name, "khoi": bi, "f": f, "f_thuc": round(f_thuc, 3), "text": None, "loi": None}
        t = time.time()
        for lan in range(2):
            try:
                im = crop.resize((max(28, round(crop.width * f_thuc)), max(28, round(crop.height * f_thuc))))
                resp, info = dots._generate(image_utils.fetch_image(im, min_pixels=None, max_pixels=None),
                                            prompts.dict_promptmode_to_prompt["prompt_ocr"])
                rec.update(text=fix_arabic(resp.strip()), tokens=info.get("new_tokens"),
                           het_token=info.get("hit_max_tokens"), lap=info.get("stopped_loop"))
                if info.get("hit_max_tokens") or info.get("stopped_loop"):
                    rec["loi"] = "hết token / lặp → dùng chữ của sản phẩm cho khối này"
                break
            except Exception as e:  # noqa: BLE001
                if "out of memory" not in str(e).lower() or lan:
                    rec["loi"] = f"{type(e).__name__}: {str(e)[:200]}"
                    break
                free_gpu()
                f_thuc *= 0.75
                rec["f_thuc"] = round(f_thuc, 3)
        rec["giay"] = round(time.time() - t, 1)
        with open(kf, "a", encoding="utf-8") as fo:
            fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
        log(f"   #5 {name} khối {bi} ×{f} (thực ×{rec['f_thuc']}): {rec['giay']} s" + (f" — {rec['loi']}" if rec["loi"] else ""))
    log("✔ XONG bon_trang")
    return 0


# === 3. trang Muharaf test (Bước 0) ===================================================================================

class _HttpFile(io.RawIOBase):
    """File trên mạng đọc theo khoảng byte (Range) → zipfile lấy đúng vài file trong zip 3 GB mà không tải cả zip."""

    def __init__(self, url: str):
        import urllib.request

        self._u = urllib.request
        r = self._open(urllib.request.Request(url, method="HEAD"))
        self.url, self.size, self.pos = r.url, int(r.headers["Content-Length"]), 0

    def _open(self, req):
        for lan in range(6):
            try:
                return self._u.urlopen(req, timeout=120)
            except Exception:  # noqa: BLE001
                if lan == 5:
                    raise
                time.sleep(5 * (lan + 1))

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, o, w=0):
        self.pos = o if w == 0 else self.pos + o if w == 1 else self.size + o
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        if n == 0 or self.pos >= self.size:
            return b""
        end = min(self.size, self.pos + n) - 1
        b = self._open(self._u.Request(self.url, headers={"Range": f"bytes={self.pos}-{end}"})).read()
        self.pos += len(b)
        return b

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)


def _dong_muharaf(js: dict) -> tuple[list[dict], list[list]]:
    """Dòng chữ Ả Rập có nhãn của một trang (theo thứ tự đọc của bộ dữ liệu) + đa giác các dòng bị loại."""
    j = js.get("json") or {}
    giu, bo = [], []
    for k, L in j.items():
        if not k.startswith("line_") or not isinstance(L, dict):
            continue
        c = L.get("coord") or []
        poly = [(float(c[i]), float(c[i + 1])) for i in range(0, len(c) - 1, 2)]
        text = (L.get("text") or "").strip()
        tags = L.get("tags") or {}
        ok = (text and len(poly) >= 3 and (L.get("language") or "Arabic") == "Arabic" and not L.get("Archivist_Tag")
              and not tags.get("Archivist_Tag") and not tags.get("Crossed_out"))
        if not ok:
            if len(poly) >= 3:
                bo.append(poly)
            continue
        so = int(re.sub(r"\D", "", k) or 0)

        def _so(v, mac_dinh):
            try:
                return int(v)
            except (TypeError, ValueError):
                return mac_dinh

        # thứ tự đọc của bộ dữ liệu: nhóm (có thể None) → index → số thứ tự line_N
        giu.append({"poly": poly, "nhan": text,
                    "thu_tu": (_so(L.get("sorted_group_index"), 10**6), _so(L.get("index"), so), so)})
    giu.sort(key=lambda x: x["thu_tu"])
    return giu, bo


def _anh_mtrang(raw: Path, p: str):
    """Ảnh một trang Muharaf test đúng như Bước 0 dùng: xoay / co theo page_dict, dòng bị loại tô màu giấy, prepare() như
    sản phẩm; kèm dòng chuẩn (đa giác theo ảnh đó). → (ảnh, dòng chuẩn, cách khớp toạ độ), hoặc None nếu thiếu file /
    trang không có dòng Ả Rập có nhãn."""
    from PIL import Image, ImageDraw, ImageOps

    from arabic_doc_ocr.pipeline import prepare

    js_f = raw / f"{p}.json"
    imf = next(iter(raw.glob(f"{p}.img.*")), None)
    if not js_f.exists() or imf is None:
        return None
    js = json.loads(js_f.read_text(encoding="utf-8"))
    giu, bo = _dong_muharaf(js)
    if not giu:
        log(f"   ⚠ {p}: không có dòng Ả Rập có nhãn → bỏ")
        return None
    img = Image.open(imf)
    pdct = js.get("page_dict") or {}
    wj, hj = int(float(pdct.get("imageWidth") or 0)), int(float(pdct.get("imageHeight") or 0))
    cach = "goc"
    if wj and hj and img.size != (wj, hj):
        t = ImageOps.exif_transpose(img)
        if t.size == (wj, hj):
            img, cach = t, "exif"
        else:
            sx, sy = img.width / wj, img.height / hj
            for g in giu:
                g["poly"] = [(x * sx, y * sy) for x, y in g["poly"]]
            bo = [[(x * sx, y * sy) for x, y in q] for q in bo]
            cach = f"co_{sx:.3f}x{sy:.3f}"
    img = img.convert("RGB")
    w0 = img.width
    # dòng bị loại (chữ Latin, mã lưu trữ, gạch bỏ…) → tô màu giấy; dòng giữ lại dán lại nguyên vẹn
    if bo:
        import numpy as np

        bg = tuple(int(v) for v in np.median(np.asarray(img).reshape(-1, 3), axis=0))
        to = img.copy()
        dr = ImageDraw.Draw(to)
        for q in bo:
            dr.polygon(q, fill=bg)
        m = Image.new("L", img.size, 0)
        dm = ImageDraw.Draw(m)
        for g in giu:
            dm.polygon(g["poly"], fill=255)
        img = Image.composite(img, to, m)
    img = prepare(img)  # như sản phẩm (chỉ phóng ảnh nhỏ < 1000 px) → khung chuẩn phóng theo
    if img.width != w0:
        s = img.width / w0
        for g in giu:
            g["poly"] = [(x * s, y * s) for x, y in g["poly"]]
    return img, giu, cach


def cmd_mtrang(a) -> int:
    from arabic_doc_ocr.lines import kraken_page

    out, data = Path(a.out), Path(a.data)
    raw, cd = data / "mtrang_raw", data / "crops" / "mtrang"
    raw.mkdir(parents=True, exist_ok=True)
    cd.mkdir(parents=True, exist_ok=True)
    pids = sorted({r["trang"] for r in csv.DictReader(open(data / "cham_muharaf" / "danh_sach.csv", encoding="utf-8"))
                   if r["tap"] == "test"})
    log(f"Muharaf test: {len(pids)} trang")
    thieu = [p for p in pids if not (raw / f"{p}.json").exists() or not list(raw.glob(f"{p}.img.*"))]
    if thieu:
        z = zipfile.ZipFile(io.BufferedReader(_HttpFile(MUHARAF_ZIP), 1 << 20))
        ten = {Path(n).name: n for n in z.namelist()}
        for p in thieu:
            jn = ten.get(f"{p}.json")
            im = next((ten[f"{p}{e}"] for e in (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG") if f"{p}{e}" in ten), None)
            if not jn or not im:
                log(f"   ⚠ {p}: không thấy ảnh / json trong zip → bỏ trang")
                continue
            (raw / f"{p}.img{Path(im).suffix.lower()}").write_bytes(z.read(im))
            (raw / f"{p}.json").write_bytes(z.read(jn))
        log(f"✔ tải {len(thieu)} trang (theo khoảng byte)")

    trang_f, vang_f, kr_f = bo_file(out, "mtrang_trang"), bo_file(out, "mtrang_vang"), bo_file(out, "mtrang_kraken")
    cu = {r["id"]: r for r in doc_jsonl(trang_f)}
    vang = {r["id"]: r for r in doc_jsonl(vang_f)}
    kr = {r["id"]: r for r in doc_jsonl(kr_f)}
    trang_rows, vang_rows, kr_rows = [], [], []
    for i, p in enumerate(pids):
        dung = _anh_mtrang(raw, p)
        if dung is None:
            continue
        img, giu, cach = dung
        nhan = "\n".join(g["nhan"] for g in giu)
        for n, g in enumerate(giu):
            lid = f"{p}:V{n:03d}"
            xs, ys = [q[0] for q in g["poly"]], [q[1] for q in g["poly"]]
            rec = vang.get(lid) or {"id": lid, "nhom": p, "thu_tu": n, "nhan": g["nhan"],
                                    "box": [int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1],
                                    "poly": [list(q) for q in g["poly"]], "anh": str(cd / f"{p}_V{n:03d}.png")}
            if not Path(rec["anh"]).exists():
                _cat_dong(img, rec).save(rec["anh"])
            vang_rows.append(rec)
        tr = cu.get(p)
        if tr is None:
            t = time.time()
            lines = kraken_page(img)
            tr = {"id": p, "nhan": nhan, "so_dong_chuan": len(giu), "cach_toa_do": cach, "kraken_ok": lines is not None,
                  "so_dong_kraken": len(lines or []), "kraken_giay": round(time.time() - t, 1), "co_anh": list(img.size)}
            for n, L in enumerate(lines or []):
                lid = f"{p}:K{n:03d}"
                kr[lid] = {"id": lid, "nhom": p, "thu_tu": n, "nhan": None, "box": list(L["box"]),
                           "poly": [list(q) for q in L["poly"]] if L.get("poly") else None,
                           "anh": str(cd / f"{p}_K{n:03d}.png")}
            log(f"   [{i + 1}/{len(pids)}] {p}: {len(giu)} dòng chuẩn · Kraken {tr['so_dong_kraken']} dòng "
                f"({tr['kraken_giay']} s{'' if tr['kraken_ok'] else ', LỖI'}) · RAM trống {ram_gb():.1f} GB")
        for lid in sorted(k for k in kr if k.startswith(p + ":K")):
            rec = kr[lid]
            if not Path(rec["anh"]).exists():
                _cat_dong(img, rec).save(rec["anh"])
            kr_rows.append(rec)
        trang_rows.append(tr)
        cu[p] = tr
        # ghi sau MỖI trang → sập giữa chừng thì chạy lại đi tiếp (Kraken không phải chạy lại trang đã xong)
        ghi_jsonl(trang_f, trang_rows + [cu[q] for q in pids[i + 1:] if q in cu])
        ghi_jsonl(vang_f, vang_rows)
        ghi_jsonl(kr_f, kr_rows + [kr[k] for k in sorted(kr) if k.split(":")[0] in pids[i + 1:]])
    ok = sum(r["kraken_ok"] for r in trang_rows)
    if len(trang_rows) < 50:
        sys.exit(f"✘ LỖI: chỉ dựng được {len(trang_rows)} / {len(pids)} trang Muharaf")
    # dấu "đã xong": tiến trình đọc chỉ dùng hai bộ này khi có dấu (tránh chia việc theo bộ đang ghi dở)
    ghi_jsonl(bo_file(out, "mtrang_xong"), [{"trang": len(trang_rows), "vang": len(vang_rows), "kraken": len(kr_rows),
                                             "kraken_loi": len(trang_rows) - ok}])
    log(f"✔ XONG mtrang: {len(trang_rows)} trang · {len(vang_rows)} dòng chuẩn · {len(kr_rows)} dòng Kraken "
        f"(Kraken lỗi {len(trang_rows) - ok} trang)")
    return 0


# === 3b. #12: nới khung dòng Kraken ===================================================================================

def cat_no(img, rec: dict, muc: int):
    """Ảnh dòng cắt như sản phẩm (crop_poly), nhưng khung NỚI theo chiều dọc thêm `muc` % độ dày dòng (nửa trên, nửa
    dưới). Mặt nạ = đa giác vẽ chồng ở mọi độ dời dọc trong [−d, d] → giãn đúng theo chiều dọc, giữ dáng dòng cong /
    nghiêng. Độ dày dòng = diện tích đa giác / bề ngang. muc = 0 → đúng crop_poly của sản phẩm."""
    if not muc:
        return _cat_dong(img, rec)
    import numpy as np
    from PIL import Image, ImageDraw

    W, H = img.size
    x0, y0, x1, y1 = rec["box"]
    poly = rec.get("poly") or []
    if len(poly) >= 3:
        xs = [q[0] for q in poly]
        dt = abs(sum(poly[k][0] * poly[k - 1][1] - poly[k - 1][0] * poly[k][1] for k in range(len(poly)))) / 2
        day = dt / max(1.0, max(xs) - min(xs))
    else:
        day = y1 - y0
    d = int(round(muc / 100 * day / 2))
    pad = 4  # như crop_poly
    cx0, cy0, cx1, cy1 = max(0, x0 - pad), max(0, y0 - d - pad), min(W, x1 + pad), min(H, y1 + d + pad)
    crop = img.convert("RGB").crop((cx0, cy0, cx1, cy1))
    if len(poly) < 3:
        return crop
    mask = Image.new("L", crop.size, 0)
    dr = ImageDraw.Draw(mask)
    for dy in range(-d, d + 1):
        dr.polygon([(x - cx0, y - cy0 + dy) for x, y in poly], fill=255)
    bg = int(np.percentile(np.asarray(crop.convert("L")), 90))  # màu giấy, như crop_poly
    return Image.composite(crop, Image.new("RGB", crop.size, (bg, bg, bg)), mask)


def _giong_anh(a, f: Path) -> bool:
    import numpy as np
    from PIL import Image

    return np.array_equal(np.asarray(a.convert("RGB")), np.asarray(Image.open(f).convert("RGB")))


def cmd_mtrang_no(a) -> int:
    """#12: cắt lại dòng Kraken (khung đã lưu, KHÔNG chạy lại Kraken) của 66 trang Muharaf và 4 trang mẫu ở mọi mức
    NO_MUC → bộ mtrang_knoNN / trang4_noNN, CÙNG id với mtrang_kraken / trang4 (chấm bằng cùng hàm). Ảnh dòng trước,
    file bộ sau."""
    from arabic_doc_ocr.pipeline import load_pages, prepare

    out, data = Path(a.out), Path(a.data)
    if not bo_file(out, "mtrang_xong").exists():
        sys.exit("✘ LỖI: chưa dựng xong 66 trang Muharaf (bo__mtrang_xong.jsonl) — chạy mtrang trước")
    raw, cd = data / "mtrang_raw", data / "crops" / "mtrang_no"
    cd.mkdir(parents=True, exist_ok=True)

    def ten_anh(r, m):
        return str(cd / f"{r['id'].replace(':', '_')}_n{m:02d}.png")

    kr = doc_bo(out, "mtrang_kraken")
    theo = collections.defaultdict(list)
    for r in kr:
        theo[r["nhom"]].append(r)
    rows = {m: [] for m in NO_MUC}
    for i, p in enumerate(sorted(theo)):
        dung = _anh_mtrang(raw, p)
        if dung is None:
            sys.exit(f"✘ LỖI: không dựng lại được ảnh trang {p} ({raw}/{p}.*) — chạy mtrang trước")
        img = dung[0]
        # ảnh trang dựng lại phải Y HỆT ảnh mà mtrang vừa cắt dòng Kraken (so dòng đầu của trang)
        r0 = theo[p][0]
        if not Path(r0["anh"]).exists():
            sys.exit(f"✘ LỖI: thiếu ảnh dòng Kraken {r0['anh']} — chạy mtrang trước")
        if not _giong_anh(cat_no(img, r0, 0), Path(r0["anh"])):
            sys.exit(f"✘ LỖI: trang {p}: cắt lại mức 0 % KHÁC ảnh dòng Kraken của mtrang — không so được")
        for r in theo[p]:
            for m in NO_MUC:
                rec = dict(r, anh=ten_anh(r, m), no=m)
                if not Path(rec["anh"]).exists():
                    cat_no(img, r, m).save(rec["anh"])
                rows[m].append(rec)
        if (i + 1) % 10 == 0:
            log(f"   #12: {i + 1}/{len(theo)} trang Muharaf")

    rows4 = doc_bo(out, "trang4")
    if not rows4:
        sys.exit("✘ LỖI: chưa có bo__trang4.jsonl — chạy bon_trang trước")
    imgs = {name: prepare(load_pages(pth)[0]) for name, pth, _ in _trang_mau()}
    r4, da_kiem = {m: [] for m in NO_MUC}, set()
    for r in rows4:
        if r["nhom"] not in da_kiem:
            if not Path(r["anh"]).exists():
                sys.exit(f"✘ LỖI: thiếu ảnh dòng {r['anh']} — chạy bon_trang trước")
            if not _giong_anh(cat_no(imgs[r["nhom"]], r, 0), Path(r["anh"])):
                sys.exit(f"✘ LỖI: {r['nhom']}: cắt lại mức 0 % KHÁC ảnh dòng của bon_trang — không so được")
            da_kiem.add(r["nhom"])
        for m in NO_MUC:
            rec = dict(r, anh=ten_anh(r, m), no=m)
            if not Path(rec["anh"]).exists():
                cat_no(imgs[r["nhom"]], r, m).save(rec["anh"])
            r4[m].append(rec)
    for m in NO_MUC:
        ghi_jsonl(bo_file(out, f"mtrang_kno{m:02d}"), rows[m])
        ghi_jsonl(bo_file(out, f"trang4_no{m:02d}"), r4[m])
    log(f"✔ XONG mtrang_no: {len(theo)} trang Muharaf × {len(kr)} dòng Kraken + 4 trang mẫu × {len(rows4)} dòng, "
        f"mức nới {', '.join(f'{m} %' for m in NO_MUC)} (mức 0 % khớp ảnh cũ từng pixel)")
    return 0


# === 4. đọc dòng (hàng việc chung cho nhiều tiến trình) ===============================================================

class DocDong:
    """Một nền Baseer-Nakba + 3 adapter; đổi cấu hình bằng hệ số LoRA của từng lớp (không nạp lại model)."""

    def __init__(self, device: str):
        from peft.tuners.lora import LoraLayer

        from arabic_doc_ocr.htr_model import HTRReader

        self.r = HTRReader(device, adapters=ADAPTERS).load()
        self.layers = [m for m in self.r.model.modules() if isinstance(m, LoraLayer)]
        self.goc = [{a: m.scaling[a] for a in ADAPTERS if a in m.scaling} for m in self.layers]
        for a in ADAPTERS:
            n = sum(a in g for g in self.goc)
            if not n:
                raise RuntimeError(f"adapter {a} không có lớp LoRA nào")
        log(f"   nạp xong: {len(self.layers)} lớp LoRA × {len(ADAPTERS)} adapter trên {device}")
        self.ten, self.tat = None, False

    def dat(self, ten: str) -> None:
        w = CAU_HINH[ten]
        for m, g in zip(self.layers, self.goc):
            for a, s in g.items():
                m.scaling[a] = s * w.get(a, 0.0)
            act = [a for a in w if a in g and w[a] != 0]
            if act:
                m.set_adapter(act)
        self.ten, self.tat = ten, not w

    def doc(self, ims) -> list[str]:
        from arabic_doc_ocr import config as AC
        from arabic_doc_ocr.htr_model import _EOS, _PAD, PROMPT, TEMPLATE
        from arabic_doc_ocr.text import clean_repeated_substrings, fix_arabic

        torch, model, proc = self.r.torch, self.r.model, self.r.processor
        prompt, out = TEMPLATE.format(p=PROMPT), []
        ctx = model.disable_adapter() if self.tat else contextlib.nullcontext()
        with torch.no_grad(), ctx:
            for im in ims:
                inp = proc(text=[prompt], images=[im.convert("RGB")], return_tensors="pt", padding=True)
                inp = {k: v.to(model.device) for k, v in inp.items()}
                ids = model.generate(**inp, max_new_tokens=AC.HTR_MAX_NEW_TOKENS, do_sample=False,
                                     repetition_penalty=1.1, eos_token_id=_EOS, pad_token_id=_PAD)
                text = proc.decode(ids[0][inp["input_ids"].shape[1]:], skip_special_tokens=True).strip()
                out.append(fix_arabic(clean_repeated_substrings(text)))
        return out

    def kiem(self, ims) -> None:
        """Đọc kiểu mới (đổi hệ số) phải RA ĐÚNG như cách đọc của sản phẩm (HTRReader.read) cho ft3 và gốc."""
        for ten, ad in (("ft3", "ft3"), ("goc", "base")):
            self.dat(ten)
            moi = self.doc(ims)
            cu = self.r.read(ims, ad)
            if moi != cu:
                raise RuntimeError(f"tự kiểm {ten}: đọc qua hệ số KHÁC đọc của sản phẩm\n  mới: {moi}\n  cũ:  {cu}")
        self.dat("tron34")
        m, g = next((m, g) for m, g in zip(self.layers, self.goc) if "ft3" in g and "ft4" in g)
        if sorted(m.active_adapters) != ["ft3", "ft4"] or abs(m.scaling["ft3"] - 0.5 * g["ft3"]) > 1e-9:
            raise RuntimeError(f"tự kiểm tron34: adapter bật {m.active_adapters}, hệ số {m.scaling}")
        log("   ✔ tự kiểm: ft3 / gốc đọc giống hệt sản phẩm; tron34 bật đủ 2 adapter với hệ số ½")


def _viec(out: Path, phan: str) -> list[tuple[str, str, int, list[dict]]]:
    def co(ten):
        return bo_file(out, ten).exists()

    cap = []
    if phan == "A":
        for c in CH_A:
            cap += [(f"{b}_A", c) for b in BO_DONG]
        if co("trang4"):
            cap += [("trang4", c) for c in CH_A]
        if co("mtrang_xong"):
            cap += [("mtrang_vang", "ft3"), ("mtrang_kraken", "ft3")]
    elif phan == "B":
        uv = doc_jsonl(out / "ung_vien.jsonl")
        if not uv:
            sys.exit("✘ LỖI: chưa có ung_vien.jsonl — chạy `chon` trước")
        if not co("mtrang_xong"):
            sys.exit("✘ LỖI: chưa dựng xong 66 trang Muharaf (bo__mtrang_xong.jsonl)")
        for c in uv[0]["can_doc_B"]:
            cap += [(f"{b}_B", c) for b in BO_DONG] + [("mtrang_kraken", c)]
    elif phan == "N":  # #12: dòng Kraken nới khung, đọc bằng ft3
        cap = [(b, "ft3") for m in NO_MUC for b in (f"mtrang_kno{m:02d}", f"trang4_no{m:02d}") if co(b)]
        if len(cap) != 2 * len(NO_MUC):
            sys.exit("✘ LỖI: chưa cắt đủ dòng nới khung (bo__mtrang_knoNN / bo__trang4_noNN) — chạy mtrang_no trước")
    else:
        sys.exit(f"✘ LỖI: phần {phan} lạ (A, B hoặc N)")
    viec, co_anh = [], {}
    for b, c in cap:
        rows = doc_bo(out, b)
        for j in range(0, len(rows), CHUNK):
            phan = rows[j:j + CHUNK]
            k = (b, j)
            if k not in co_anh:  # ảnh dòng chưa cắt xong (đang dựng lại sau khi khôi phục) → để lượt sau
                co_anh[k] = all(Path(r["anh"]).exists() for r in phan)
            if co_anh[k]:
                viec.append((b, c, j // CHUNK, phan))
    return viec


def kq_file(out: Path, b: str, c: str, j: int) -> Path:
    return out / f"doc__{b}__{c}__c{j:03d}.jsonl"


def doc_ket_qua(out: Path, b: str, c: str) -> dict[str, str]:
    d = {}
    for f in sorted(out.glob(f"doc__{b}__{c}__c*.jsonl")):
        for r in doc_jsonl(f):
            d[r["id"]] = r["doan"]
    return d


def cmd_doc(a) -> int:
    from PIL import Image

    out = Path(a.out)
    claim = out / ".nhan_viec"
    claim.mkdir(parents=True, exist_ok=True)
    sync = None
    if a.push:
        from htr_test.sync import Sync

        sync = Sync(out, every_min=10, repo_suffix=f"-g{a.gpu}")
    rd, t0, n_doc = None, time.time(), 0
    while True:
        viec = [v for v in _viec(out, a.phan) if not kq_file(out, v[0], v[1], v[2]).exists()]
        lay = None
        for v in viec:
            try:
                fd = os.open(claim / f"{v[0]}__{v[1]}__c{v[2]:03d}", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"gpu{a.gpu} {time.time():.0f}".encode())
                os.close(fd)
                lay = v
                break
            except FileExistsError:
                continue
        if lay is None:
            break
        b, c, j, rows = lay
        if rd is None:
            log(f"== nạp model trên cuda:{a.gpu} · RAM trống {ram_gb():.1f} GB")
            rd = DocDong(f"cuda:{a.gpu}")
            mau = [Image.open(r["anh"]) for r in doc_bo(out, "omar_A")[:3]]
            rd.kiem(mau)
        if rd.ten != c:
            rd.dat(c)
        t = time.time()
        texts = rd.doc([Image.open(r["anh"]) for r in rows])
        ghi_jsonl(kq_file(out, b, c, j), [{"id": r["id"], "doan": x} for r, x in zip(rows, texts)])
        n_doc += len(rows)
        con = len(viec) - 1
        log(f"   {b} · {c} · phần {j}: {len(rows)} dòng, {(time.time() - t) / max(1, len(rows)):.2f} s/dòng · "
            f"còn ~{con} phần · RAM trống {ram_gb():.1f} GB")
        if ram_gb() >= 0 and ram_gb() < 2.5:
            log("   ⚠ RAM TRỐNG < 2,5 GB")
        if sync and sync.due():
            sync.push(f"dot1 doc {a.phan}: {b} {c} phần {j}")
    log(f"✔ XONG doc {a.phan} trên cuda:{a.gpu}: {n_doc} dòng trong {(time.time() - t0) / 60:.0f} phút")
    if sync:
        sync.push(f"dot1 doc {a.phan} xong (gpu {a.gpu})")
    return 0


# === 5. bầu chọn ======================================================================================================

def _key(w: str) -> str:
    from arabic_doc_ocr.text import _key as k

    return k(w)


def bau_tu(cands: list[str]) -> str:
    """Bầu theo TỪ, lấy bản đầu (ft3) làm gốc: một đoạn của gốc chỉ bị thay khi ≥ 2 bản khác cùng đọc một kiểu khác
    VÀ số bản đọc kiểu đó nhiều hơn số bản (kể cả gốc) đọc giống gốc ở đúng đoạn đó. Hoà → giữ gốc."""
    piv = (cands[0] or "").split()
    pk = [_key(w) for w in piv]
    props: dict[tuple, dict] = {}
    eq_masks, inserts = [], []
    for c in cands[1:]:
        w = (c or "").split()
        ops = difflib.SequenceMatcher(None, pk, [_key(x) for x in w], autojunk=False).get_opcodes()
        eq = [False] * len(piv)
        ins = set()
        for tag, i1, i2, j1, j2 in ops:
            if tag == "equal":
                for i in range(i1, i2):
                    eq[i] = True
                continue
            if i1 == i2:
                ins.add(i1)
            alt = w[j1:j2]
            k = (i1, i2, " ".join(_key(x) for x in alt))
            p = props.setdefault(k, {"raw": alt, "n": 0})
            p["n"] += 1
        eq_masks.append(eq)
        inserts.append(ins)

    def ung_ho_goc(i1, i2):
        n = 1
        for eq, ins in zip(eq_masks, inserts):
            if i1 < i2:
                n += all(eq[i1:i2])
            else:
                n += i1 not in ins
        return n

    nhan = []
    for (i1, i2, _), p in props.items():
        s = ung_ho_goc(i1, i2)
        if p["n"] >= 2 and p["n"] > s:
            nhan.append((p["n"] - s, p["n"], i1, i2, p["raw"]))
    nhan.sort(key=lambda x: (-x[0], -x[1], x[2]))
    chon, dung = [], set()
    for _, _, i1, i2, raw in nhan:
        vung = set(range(i1, i2)) if i1 < i2 else {i1 - 0.5}
        if vung & dung:
            continue
        dung |= vung
        chon.append((i1, i2, raw))
    words = list(piv)
    for i1, i2, raw in sorted(chon, key=lambda x: (-x[0], -x[1])):
        words[i1:i2] = raw
    return " ".join(words)


def bau_dong(cands: list[str]) -> str:
    """Bầu theo cả DÒNG: chọn bản đọc gần các bản còn lại nhất (tổng khoảng cách ký tự nhỏ nhất); hoà → bản đầu."""
    from rapidfuzz.distance import Levenshtein

    nn = [_norm(c) for c in cands]
    tong = [sum(Levenshtein.distance(x, y) for y in nn) for x in nn]
    return cands[min(range(len(cands)), key=lambda i: (tong[i], i))]


PHUONG_AN_BAU = {f"{k}_{kieu}": (v, fn) for k, v in BAU.items() for kieu, fn in (("tu", bau_tu), ("dong", bau_dong))}


def doc_ca(out: Path, b: str, ten: str, rows: list[dict] | None = None) -> dict[str, str] | None:
    """Bản đọc của một cách (cấu hình hoặc bầu chọn) trên bộ b; None nếu chưa đủ bản đọc."""
    rows = rows if rows is not None else doc_bo(out, b)
    if ten in CAU_HINH:
        d = doc_ket_qua(out, b, ten)
        return d if all(r["id"] in d for r in rows) else None
    if ten in PHUONG_AN_BAU:
        thanh, fn = PHUONG_AN_BAU[ten]
        ds = [doc_ket_qua(out, b, c) for c in thanh]
        if not all(all(r["id"] in d for r in rows) for d in ds):
            return None
        return {r["id"]: fn([d[r["id"]] for d in ds]) for r in rows}
    if ten.startswith("tran_"):  # mức trần: chọn bản đúng nhất theo NHÃN — chỉ để biết giới hạn, không phải cách đọc
        thanh = BAU[ten[5:]]
        ds = [doc_ket_qua(out, b, c) for c in thanh]
        if not all(all(r["id"] in d for r in rows) for d in ds):
            return None
        res = {}
        for r in rows:
            cs = [d[r["id"]] for d in ds]
            res[r["id"]] = min(cs, key=lambda x: edit_stats(_norm(r["nhan"]), _norm(x))["char_edits"])
        return res
    raise KeyError(ten)


# === 6. chấm điểm =====================================================================================================

def diem_dong(rows: list[dict], doan: dict[str, str]) -> dict:
    ce = cr = we = wr = 0
    per = []
    for r in rows:
        s = edit_stats(_norm(r["nhan"]), _norm(doan[r["id"]]))
        ce, cr, we, wr = ce + s["char_edits"], cr + s["ref_chars"], we + s["word_edits"], wr + s["ref_words"]
        per.append((s["char_edits"], s["ref_chars"]))
    return {"ky_tu": 100 * (1 - ce / max(1, cr)), "tu": 100 * (1 - we / max(1, wr)), "n": len(rows), "per": per}


def bootstrap(per_a: dict[str, list], per_b: dict[str, list], n: int = 2000, seed: int = 0) -> tuple[float, float]:
    """Khoảng tin cậy 95% của (điểm TB các bộ của b) − (của a), điểm = % ký tự đúng; lấy mẫu lại dòng trong từng bộ,
    ghép cặp theo dòng (per = [(số lỗi ký tự, số ký tự nhãn)] cùng thứ tự dòng ở a và b)."""
    import numpy as np

    rng = np.random.default_rng(seed)
    arr = {k: (np.array([x[0] for x in per_a[k]], float), np.array([x[0] for x in per_b[k]], float),
               np.array([x[1] for x in per_a[k]], float)) for k in per_a}
    diffs = []
    for _ in range(n):
        d = []
        for ea, eb, rl in arr.values():
            idx = rng.integers(0, len(rl), len(rl))
            s = max(1.0, rl[idx].sum())
            d.append(100 * (ea[idx].sum() - eb[idx].sum()) / s)  # b ít lỗi hơn a → dương
        diffs.append(sum(d) / len(d))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(lo), float(hi)


def _ghep_trang(bo_cuc: dict, rows: list[dict], doan: dict[str, str], loai: str, khoi_moi: dict | None = None,
                chi_dong: bool = False) -> str:
    """Chữ chính của một trang, theo đúng luật của sản phẩm (Pipeline.assemble). khoi_moi: {khối: chữ} thay chữ dots
    (#5). chi_dong: mọi khối lấy chữ đọc dòng (để so các cấu hình đọc dòng trên cả trang đánh máy)."""
    from arabic_doc_ocr import config as AC

    theo_khoi = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: r["thu_tu"]):
        theo_khoi[r["khoi"]].append(doan.get(r["id"], ""))
    parts = []
    for bi, b in enumerate(bo_cuc["blocks"]):
        if b.get("category") not in AC.TEXT_CATS:
            continue
        dots_t, lines_t = b.get("text") or "", "\n".join(theo_khoi.get(bi, []))
        if b.get("hebrew"):
            parts.append(dots_t)
        elif chi_dong:
            parts.append(lines_t)
        elif not dots_t.strip() or (loai != "printed" and lines_t.strip()):
            parts.append(lines_t)
        else:
            parts.append((khoi_moi or {}).get(bi, dots_t))
    return "\n".join(parts)


_MD = re.compile(r"^\s*#+\s*|\*\*|\|", re.M)


def _bo_md(s: str) -> str:
    return _MD.sub(" ", s or "")


def diem_trang(ev, ref: str, hyp: str) -> dict:
    """Chấm cả trang bằng scripts/evaluate.py của arabic-doc-ocr (như docs/RESULTS.md); ce / cr = số lỗi / số ký tự
    nhãn sau chuẩn hoá (để cộng dồn nhiều trang)."""
    from rapidfuzz.distance import Levenshtein

    s = ev.score(ref, hyp)
    r, h = ev.clean(ref), ev.clean(hyp)
    return {"ky_tu": 100 * s["chars"], "tu": 100 * s["words"], "tui_tu": 100 * s["word_recall"],
            "ce": Levenshtein.distance(r, h), "cr": max(1, len(r))}


# === 7. chọn ứng viên ================================================================================================

def bang_A(out: Path) -> dict:
    res = {}
    rows = {b: doc_bo(out, f"{b}_A") for b in BO_DONG}
    for ten in [*CAU_HINH, *PHUONG_AN_BAU, *[f"tran_{k}" for k in BAU]]:
        r = {}
        for b in BO_DONG:
            d = doc_ca(out, f"{b}_A", ten, rows[b])
            if d is not None:
                r[b] = diem_dong(rows[b], d)
        if len(r) == len(BO_DONG):
            r["tb"] = sum(r[b]["ky_tu"] for b in BO_DONG) / len(BO_DONG)
            r["tb_tu"] = sum(r[b]["tu"] for b in BO_DONG) / len(BO_DONG)
            res[ten] = r
    return res


def cmd_chon(a) -> int:
    out = Path(a.out)
    A = bang_A(out)
    if "ft3" not in A:
        sys.exit("✘ LỖI: bộ A chưa đọc xong bằng ft3")
    thieu = [c for c in CAU_HINH if c not in A]
    if thieu:
        sys.exit(f"✘ LỖI: bộ A chưa đọc xong: {thieu}")
    f3 = A["ft3"]
    hop_le = {k: v for k, v in A.items() if k != "ft3" and not k.startswith("tran_")
              and v["omar"]["ky_tu"] >= f3["omar"]["ky_tu"] - 0.3}
    best = max(hop_le, key=lambda k: hop_le[k]["tb"]) if hop_le else None
    if best is None:
        sys.exit("✘ LỖI: không có cách nào hợp lệ (mọi cách đều làm Omar kém ft3 > 0,3 điểm)")
    can = sorted(set(["ft3"] + (PHUONG_AN_BAU[best][0] if best in PHUONG_AN_BAU else [best])),
                 key=lambda c: CH_A.index(c))
    rec = {"ung_vien": best, "tb_A": round(A[best]["tb"], 2), "tb_A_ft3": round(f3["tb"], 2),
           "hon_ft3_A": round(A[best]["tb"] - f3["tb"], 2), "can_doc_B": can, "luat": LUAT["chon"],
           "luc": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}
    cu = doc_jsonl(out / "ung_vien.jsonl")
    if cu and cu[0]["ung_vien"] != best:
        sys.exit(f"✘ LỖI: ung_vien.jsonl đã chọn {cu[0]['ung_vien']} nhưng lần này ra {best} — bộ A đã thay đổi?")
    ghi_jsonl(out / "ung_vien.jsonl", [rec])
    log(f"✔ ứng viên: {best} (TB 3 bộ A {A[best]['tb']:.2f} so với ft3 {f3['tb']:.2f}) → bộ B đọc: {', '.join(can)}")
    return 0


# === 8. báo cáo =======================================================================================================

def _f(x, nd=1):
    return "—" if x is None else f"{x:.{nd}f}"


def _d(x, nd=1):
    return "—" if x is None else f"{x:+.{nd}f}"


def cmd_bao_cao(a) -> int:
    out = Path(a.out)
    ev = adoc_eval()
    J, L = {"luat": LUAT}, ["# Đợt 1 — thử không cần huấn luyện", "",
                           f"Cập nhật {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}. "
                           "Luật chọn / luật đạt viết sẵn trong `htr_test/dot1.py` (LUAT) trước khi chạy.", ""]
    goi_y = []

    # --- bộ test
    L += ["## Bộ test", "", "| bộ | số dòng / trang | dùng để |", "|---|---:|---|"]
    for b in BO_DONG:
        for phan, de in (("A", "chọn"), ("B", "xác nhận")):
            L.append(f"| {TEN_BO[b]} {phan} | {len(doc_bo(out, f'{b}_{phan}'))} dòng | {de} |")
    mt = doc_bo(out, "mtrang_trang")
    L += [f"| Muharaf test, cả trang | {len(mt)} trang | Bước 0 + xác nhận trên cả trang |",
          f"| 4 trang mẫu | {len(doc_bo(out, 'trang4'))} dòng | cả trang (nhãn của anh) |", ""]

    # --- bảng A
    A = bang_A(out)
    J["A"] = {k: {b: {kk: vv for kk, vv in v[b].items() if kk != "per"} for b in BO_DONG} | {"tb": v["tb"]}
              for k, v in A.items()}
    f3 = A.get("ft3")
    L += ["## 1. Bộ A — mọi cấu hình đọc dòng (% ký tự đúng / % từ đúng, đã chuẩn hoá)", "",
          "| cách | " + " | ".join(TEN_BO[b] for b in BO_DONG) + " | **TB ký tự** | hơn ft3 |",
          "|---|" + "---:|" * (len(BO_DONG) + 2)]
    for k, v in sorted(A.items(), key=lambda kv: -kv[1]["tb"]):
        L.append(f"| {k} | " + " | ".join(f"{v[b]['ky_tu']:.1f} / {v[b]['tu']:.1f}" for b in BO_DONG)
                 + f" | **{v['tb']:.2f}** | {_d(v['tb'] - f3['tb'], 2) if f3 else '—'} |")
    L += ["", "`tronAB` = hai adapter cùng bật, mỗi cái ½. `ft3_sNNN` = ft3 ở độ mạnh NNN/100. `bauN_tu` = bầu theo từ "
          "(ft3 làm gốc), `bauN_dong` = chọn cả dòng gần các bản khác nhất; bau4 = ft3, ft4, ft1@0,5, gốc; bau5 = bau4 + "
          "tron34. `tran_bauN` = mức TRẦN (chọn bản đúng nhất theo nhãn) — chỉ để biết còn bao nhiêu chỗ, không phải cách đọc.", ""]
    if f3:
        s = {k: A[k]["tb"] - f3["tb"] for k in ("ft3_s050", "ft3_s075", "ft3_s125") if k in A}
        if s:
            tot = max(s, key=s.get)
            if tot == "ft3_s125" and s[tot] >= 0.2:
                goi_y.append(f"**Độ mạnh:** 1,25 tốt nhất ({_d(s[tot], 2)}) → ft3 học chưa đủ → Đợt 2 train LÂU HƠN.")
            elif tot in ("ft3_s050", "ft3_s075") and s[tot] >= 0.2:
                goi_y.append(f"**Độ mạnh:** {tot} tốt nhất ({_d(s[tot], 2)}) → ft3 học quá / quên gốc → Đợt 2 trộn "
                             "checkpoint, giữ một phần gốc.")
            else:
                goi_y.append("**Độ mạnh:** không mức nào hơn ft3 ≥ 0,2 → không rõ; nhật ký train (CER kiểm tra vẫn giảm ở "
                             "bước 2000) nghiêng về train lâu hơn.")
        bb = [k for k in A if k in PHUONG_AN_BAU]
        if bb:
            tb = max(bb, key=lambda k: A[k]["tb"])
            g = A[tb]["tb"] - f3["tb"]
            goi_y.append(f"**Bầu chọn:** tốt nhất {tb} {_d(g, 2)} điểm so với ft3 → "
                         + ("train VÀI bản ft5 khác nhau để bầu." if g >= 1.0 else "một bản ft5 là đủ."))
        if "tron34" in A:
            goi_y.append(f"**Trộn ft3+ft4:** {_d(A['tron34']['tb'] - f3['tb'], 2)} điểm so với ft3 → "
                         + ("đưa bước trộn checkpoint vào cách train ft5." if A["tron34"]["tb"] - f3["tb"] >= 0.2
                            else "trộn hai adapter không giúp rõ."))

    # --- bộ B
    uv = doc_jsonl(out / "ung_vien.jsonl")
    if uv and f3:
        u = uv[0]["ung_vien"]
        rowsB = {b: doc_bo(out, f"{b}_B") for b in BO_DONG}
        sc = {}
        for ten in ("ft3", u):
            r = {}
            for b in BO_DONG:
                d = doc_ca(out, f"{b}_B", ten, rowsB[b])
                if d is not None:
                    r[b] = diem_dong(rowsB[b], d)
            sc[ten] = r
        L += [f"## 2. Bộ B — xác nhận ứng viên `{u}` (chọn ở bộ A: {_d(uv[0]['hon_ft3_A'], 2)} điểm so với ft3)", ""]
        if all(len(sc[t]) == len(BO_DONG) for t in sc):
            hon = {b: sc[u][b]["ky_tu"] - sc["ft3"][b]["ky_tu"] for b in BO_DONG}
            tb = sum(hon.values()) / len(hon)
            lo, hi = bootstrap({b: sc["ft3"][b]["per"] for b in BO_DONG}, {b: sc[u][b]["per"] for b in BO_DONG})
            L += ["| bộ | ft3 | " + u + " | hơn |", "|---|---:|---:|---:|"]
            for b in BO_DONG:
                L.append(f"| {TEN_BO[b]} B | {sc['ft3'][b]['ky_tu']:.2f} | {sc[u][b]['ky_tu']:.2f} | {_d(hon[b], 2)} |")
            L += [f"| **TB** | | | **{_d(tb, 2)}** (95%: {lo:+.2f} … {hi:+.2f}) |", ""]
            J["B"] = {"ung_vien": u, "hon": hon, "tb": tb, "ci": [lo, hi]}
        else:
            L += ["(bộ B chưa đọc xong)", ""]
            tb = lo = None
            hon = {}
    else:
        u, tb, lo, hon = None, None, None, {}

    # --- cả trang: Muharaf (Bước 0 + xác nhận) và 4 trang
    tr_m = {r["id"]: r for r in mt}
    vang, kr = doc_bo(out, "mtrang_vang"), doc_bo(out, "mtrang_kraken")

    def diem_mtrang(ds_rows, doan):
        theo = collections.defaultdict(list)
        for r in sorted(ds_rows, key=lambda r: (r["nhom"], r["thu_tu"])):
            theo[r["nhom"]].append(doan.get(r["id"], ""))
        res = {}
        for p, t in tr_m.items():
            res[p] = diem_trang(ev, t["nhan"], "\n".join(theo.get(p, [])))
        return res

    def tong(res, chi=None):
        ks = [p for p in res if chi is None or p in chi]
        ce, cr = sum(res[p]["ce"] for p in ks), sum(res[p]["cr"] for p in ks)
        tt = sum(res[p]["tui_tu"] for p in ks) / max(1, len(ks))
        return {"ky_tu": 100 * (1 - ce / max(1, cr)), "tui_tu": tt, "so_trang": len(ks)}

    J["buoc0"] = None
    if mt and vang and kr:
        dv, dk = doc_ca(out, "mtrang_vang", "ft3", vang), doc_ca(out, "mtrang_kraken", "ft3", kr)
        if dv is not None and dk is not None:
            rv, rk = diem_mtrang(vang, dv), diem_mtrang(kr, dk)
            ok = {p for p, t in tr_m.items() if t.get("kraken_ok")}
            sv, sk, sv2, sk2 = tong(rv), tong(rk), tong(rv, ok), tong(rk, ok)
            hut, hut_tui = sv["ky_tu"] - sk["ky_tu"], sv["tui_tu"] - sk["tui_tu"]
            ket = ("Đợt 2 LÀM #10 (dạy bằng dòng Kraken cắt)" if hut >= 5 else
                   "cân nhắc #10 — xem hụt theo túi từ" if hut >= 2 else "BỎ #10")
            L += ["## 3. Bước 0 — tách dòng làm mất bao nhiêu điểm (66 trang Muharaf test, đọc bằng ft3)", "",
                  "| dòng | % ký tự đúng (cả trang, có thứ tự) | % từ có mặt (túi từ, bỏ thứ tự) |", "|---|---:|---:|",
                  f"| cắt theo khung chuẩn của bộ dữ liệu | {sv['ky_tu']:.1f} | {sv['tui_tu']:.1f} |",
                  f"| Kraken tự cắt (như sản phẩm) | {sk['ky_tu']:.1f} | {sk['tui_tu']:.1f} |",
                  f"| **hụt** | **{hut:.1f}** | **{hut_tui:.1f}** |", "",
                  f"Kraken lỗi {len(tr_m) - len(ok)} / {len(tr_m)} trang (trang lỗi tính 0 điểm; bỏ các trang đó: chuẩn "
                  f"{sv2['ky_tu']:.1f} / Kraken {sk2['ky_tu']:.1f}). Dòng chữ Latin / mã lưu trữ / gạch bỏ đã tô màu giấy ở "
                  "cả hai cách. **Lưu ý:** model tách dòng Muharaf (Zenodo 14295555) học từ chính bộ Muharaf, có thể đã "
                  "thấy các trang này → hụt thật trên giấy tờ của khách có thể LỚN hơn.", "",
                  f"**Kết luận theo luật:** hụt {hut:.1f} điểm → {ket}.", ""]
            goi_y.append(f"**Tách dòng (Bước 0):** hụt {hut:.1f} điểm → {ket}.")
            J["buoc0"] = {"vang": sv, "kraken": sk, "hut": hut, "hut_tui_tu": hut_tui, "ket_luan": ket,
                          "kraken_loi": len(tr_m) - len(ok)}
            if u and u != "ft3":
                du = doc_ca(out, "mtrang_kraken", u, kr)
                if du is not None:
                    su = tong(diem_mtrang(kr, du))
                    J["mtrang_ung_vien"] = su
                    hon["mtrang"] = su["ky_tu"] - sk["ky_tu"]
                    L += [f"Ứng viên `{u}` trên 66 trang (Kraken cắt): {su['ky_tu']:.1f} so với ft3 {sk['ky_tu']:.1f} "
                          f"({_d(hon['mtrang'], 2)}).", ""]

    # 4 trang mẫu
    bo4 = {r["page"]: r for r in doc_jsonl(out / "trang4_bo_cuc.jsonl")}
    rows4 = doc_bo(out, "trang4")
    nhan4 = {name: (lab, lab.get("type", "")) for name, _, lab in _trang_mau()}
    if bo4 and rows4:
        theo_trang = collections.defaultdict(list)
        for r in rows4:
            theo_trang[r["nhom"]].append(r)
        L += ["## 4. Bốn trang mẫu — chữ chính theo luật sản phẩm (% ký tự / % từ)", "",
              "Trang 1, 3, 4 = đánh máy (chữ chính = dots, đọc dòng chỉ kiểm chéo) → cấu hình đọc dòng chỉ đổi trang 2. "
              "Cột \"chỉ đọc dòng\" = mọi khối lấy chữ đọc dòng (để thấy cấu hình nào đọc chữ đánh máy tốt hơn).", "",
              "| cách | page_1 | page_2 (viết tay) | page_3 | page_4 | chỉ đọc dòng: page_1 / page_3 / page_4 |",
              "|---|---:|---:|---:|---:|---|"]
        J["trang4"] = {}
        for ten in [*CAU_HINH, *PHUONG_AN_BAU]:
            d = doc_ca(out, "trang4", ten, rows4)
            if d is None:
                continue
            o, cd = {}, {}
            for name in sorted(bo4):
                loai = "printed" if name in PRINTED else "handwritten"
                o[name] = diem_trang(ev, nhan4[name][0]["text"], _ghep_trang(bo4[name], theo_trang[name], d, loai))
                if name in PRINTED:
                    cd[name] = diem_trang(ev, nhan4[name][0]["text"],
                                          _ghep_trang(bo4[name], theo_trang[name], d, loai, chi_dong=True))
            J["trang4"][ten] = {"chinh": o, "chi_dong": cd}
            L.append(f"| {ten} | " + " | ".join(f"{o[n]['ky_tu']:.1f} / {o[n]['tu']:.1f}" for n in sorted(o))
                     + " | " + " / ".join(f"{cd[n]['ky_tu']:.1f}" for n in sorted(cd)) + " |")
        L += ["", "Mốc: docs/RESULTS.md của arabic-doc-ocr (lần đo 2026-10-19): 90.3 / 72.2 / 79.0 / 90.9 — dòng ft3 ở "
              "trên phải gần các số này (cùng code, cùng model).", ""]
        if u and u in J["trang4"] and "ft3" in J["trang4"]:
            hon["page_2"] = J["trang4"][u]["chinh"]["page_2"]["ky_tu"] - J["trang4"]["ft3"]["chinh"]["page_2"]["ky_tu"]

        # #5
        kd = doc_jsonl(out / "khoi_dots.jsonl")
        if kd:
            L += ["## 5. dots đọc lại TỪNG khối chữ đánh máy (#5) — % ký tự / % từ (đã bỏ dấu Markdown ở mọi cột)", "",
                  "| cách | page_1 | page_3 | page_4 | TB ký tự | hơn sản phẩm |", "|---|---:|---:|---:|---:|---:|"]
            d3 = doc_ca(out, "trang4", "ft3", rows4) or {}
            goc5 = {}
            for name in PRINTED:
                goc5[name] = diem_trang(ev, nhan4[name][0]["text"],
                                        _bo_md(_ghep_trang(bo4[name], theo_trang[name], d3, "printed")))
            tb0 = sum(goc5[n]["ky_tu"] for n in PRINTED) / len(PRINTED)
            L.append("| sản phẩm (cả trang ×1,5) | " + " | ".join(f"{goc5[n]['ky_tu']:.1f} / {goc5[n]['tu']:.1f}"
                                                               for n in PRINTED) + f" | {tb0:.2f} | — |")
            J["khoi"] = {"san_pham": goc5}
            tot5 = None
            for f in KHOI_F:
                moi = collections.defaultdict(dict)
                loi = 0
                for r in kd:
                    if r["f"] == f and r.get("text") and not r.get("loi"):
                        moi[r["page"]][r["khoi"]] = r["text"]
                    elif r["f"] == f:
                        loi += 1
                sc5 = {name: diem_trang(ev, nhan4[name][0]["text"], _bo_md(
                    _ghep_trang(bo4[name], theo_trang[name], d3, "printed", khoi_moi=moi.get(name, {}))))
                    for name in PRINTED}
                tbf = sum(sc5[n]["ky_tu"] for n in PRINTED) / len(PRINTED)
                J["khoi"][f"x{f}"] = {"diem": sc5, "tb": tbf, "khoi_dung_du_phong": loi}
                L.append(f"| từng khối ×{f} | " + " | ".join(f"{sc5[n]['ky_tu']:.1f} / {sc5[n]['tu']:.1f}" for n in PRINTED)
                         + f" | {tbf:.2f} | {_d(tbf - tb0, 2)} |" + (f" ({loi} khối dùng chữ sản phẩm)" if loi else ""))
                if tot5 is None or tbf > J["khoi"][f"x{tot5}"]["tb"]:
                    tot5 = f
            if tot5 is not None:
                g = J["khoi"][f"x{tot5}"]
                kem = min(g["diem"][n]["ky_tu"] - goc5[n]["ky_tu"] for n in PRINTED)
                dat5 = g["tb"] - tb0 >= 0.5 and kem >= -0.3
                L += ["", f"**Kết luận theo luật:** tốt nhất ×{tot5}: {_d(g['tb'] - tb0, 2)} điểm, trang kém nhất "
                      f"{_d(kem, 2)} → **{'ĐẠT' if dat5 else 'KHÔNG ĐẠT'}**. {LUAT['khoi']}", ""]
                goi_y.append(f"**dots từng khối (#5):** ×{tot5} {_d(g['tb'] - tb0, 2)} điểm → "
                             + ("ĐẠT → #11 (dòng máy chữ tự sinh) bớt gấp; xác nhận trên bộ đánh máy khác."
                                if dat5 else "KHÔNG ĐẠT → #11 (dòng máy chữ tự sinh) ưu tiên trong Đợt 2."))
                J["khoi"]["ket_luan"] = {"tot_nhat": tot5, "dat": dat5}

    # --- #12: nới khung dòng Kraken (66 trang Muharaf + trang 2 viết tay của khách), đọc bằng ft3
    no = {}
    for m in NO_MUC:
        rk_m = doc_bo(out, f"mtrang_kno{m:02d}")
        d = doc_ca(out, f"mtrang_kno{m:02d}", "ft3", rk_m) if rk_m and mt else None
        r4m = doc_bo(out, f"trang4_no{m:02d}")
        d4 = doc_ca(out, f"trang4_no{m:02d}", "ft3", r4m) if r4m and "page_2" in bo4 else None
        if d is None or d4 is None:
            continue
        no[m] = {"mtrang": tong(diem_mtrang(rk_m, d)),
                 "page_2": diem_trang(ev, nhan4["page_2"][0]["text"],
                                      _ghep_trang(bo4["page_2"], [r for r in r4m if r["nhom"] == "page_2"], d4,
                                                  "handwritten"))}
        if m == 0:
            cu = doc_ket_qua(out, "mtrang_kraken", "ft3")
            no[0]["giong_cu"] = 100 * sum(cu.get(k) == v for k, v in d.items()) / max(1, len(d))
    if len(no) == len(NO_MUC):
        g0 = no[0]
        L += ["## 5b. Nới khung dòng Kraken (#12) — đọc bằng ft3, cùng dòng Kraken, chỉ đổi khung cắt", "",
              "| nới thêm (% độ dày dòng) | 66 trang Muharaf: % ký tự | túi từ | hơn 0 % | trang 2 (viết tay): % ký tự "
              "/ % từ | hơn 0 % |", "|---|---:|---:|---:|---:|---:|"]
        for m in NO_MUC:
            v = no[m]
            L.append(f"| {m} % | {v['mtrang']['ky_tu']:.1f} | {v['mtrang']['tui_tu']:.1f} | "
                     f"{_d(v['mtrang']['ky_tu'] - g0['mtrang']['ky_tu'], 2) if m else '—'} | "
                     f"{v['page_2']['ky_tu']:.1f} / {v['page_2']['tu']:.1f} | "
                     f"{_d(v['page_2']['ky_tu'] - g0['page_2']['ky_tu'], 2) if m else '—'} |")
        b0 = J.get("buoc0") or {}
        L += ["", f"Mốc: mức 0 % đọc lại trong lần chạy này giống bản đọc Bước 0 ở {g0['giong_cu']:.1f} % số dòng "
              f"(Bước 0: Kraken {_f((b0.get('kraken') or {}).get('ky_tu'))}, dòng chuẩn "
              f"{_f((b0.get('vang') or {}).get('ky_tu'))})."]
        tot = max((m for m in NO_MUC if m), key=lambda m: no[m]["mtrang"]["ky_tu"])
        hon_k = no[tot]["mtrang"]["ky_tu"] - g0["mtrang"]["ky_tu"]
        hon_t = no[tot]["mtrang"]["tui_tu"] - g0["mtrang"]["tui_tu"]
        hon_p2 = no[tot]["page_2"]["ky_tu"] - g0["page_2"]["ky_tu"]
        dat12 = hon_k >= 1.0 and hon_t >= 0 and hon_p2 >= -1.0
        L += ["", f"**Kết luận theo luật:** tốt nhất nới {tot} %: {_d(hon_k, 2)} điểm ký tự, túi từ {_d(hon_t, 2)}, "
              f"trang 2 {_d(hon_p2, 2)} → **{'ĐẠT' if dat12 else 'KHÔNG ĐẠT'}**. {LUAT['no']}", ""]
        goi_y.append(f"**Nới khung dòng (#12):** nới {tot} % → {_d(hon_k, 2)} điểm trên 66 trang, trang 2 {_d(hon_p2, 2)} → "
                     + (f"ĐẠT → đưa nới {tot} % vào sản phẩm (chờ anh duyệt) và cắt dòng Kraken cho #10 bằng mức này."
                        if dat12 else "KHÔNG ĐẠT → giữ khung cũ; #10 cắt dòng như sản phẩm."))
        J["no"] = {"diem": no, "tot_nhat": tot, "hon": hon_k, "hon_tui_tu": hon_t, "hon_page_2": hon_p2, "dat": dat12}
    elif any(bo_file(out, f"mtrang_kno{m:02d}").exists() for m in NO_MUC):
        L += ["## 5b. Nới khung dòng Kraken (#12)", "", "(chưa đọc xong)", ""]

    # --- kết luận ứng viên (cần B + trang)
    if u and tb is not None and lo is not None:
        dk = [("TB 3 bộ B ≥ +0,3", tb >= 0.3), ("khoảng tin cậy 95% > 0", lo > 0),
              ("không bộ B nào kém > 0,3", all(hon[b] >= -0.3 for b in BO_DONG))]
        if u != "ft3":
            dk.append(("66 trang Muharaf không kém > 0,3", hon.get("mtrang", -99) >= -0.3))
            dk.append(("trang 2 không kém > 1,0", hon.get("page_2", -99) >= -1.0))
        dat = all(x for _, x in dk)
        L += [f"## 6. Kết luận ứng viên `{u}`", "", "| điều kiện | |", "|---|---|"]
        L += [f"| {t} | {'✔' if x else '✘'} |" for t, x in dk]
        L += ["", f"**{'ĐẠT' if dat else 'KHÔNG ĐẠT'}** — {LUAT['dat_B']}", ""]
        goi_y.insert(0, f"**Ứng viên `{u}`:** {'ĐẠT → có thể thay ft3 trong sản phẩm (chờ anh duyệt)' if dat else 'KHÔNG ĐẠT → giữ ft3'}.")
        J["ket_luan_ung_vien"] = {"ung_vien": u, "dat": dat, "dieu_kien": dk}

    L += ["## 7. Gợi ý cho Đợt 2 (tự rút theo luật)", ""] + [f"- {x}" for x in goi_y] + [""]
    L += ["## Lưu ý", "",
          "- Số đọc dòng ở đây dùng đúng code đọc của arabic-doc-ocr (có sửa mã chữ Ba Tư → Ả Rập), nên có thể lệch "
          "nhẹ so với bảng cũ của eval_lines.",
          "- Chữ đánh máy chỉ có 3 trang → kết quả #5 là tín hiệu, chưa phải bằng chứng.",
          "- Mọi luật: `LUAT` trong htr_test/dot1.py.", ""]
    J["goi_y"] = goi_y
    (out / "tom_tat.md").write_text("\n".join(L), encoding="utf-8")
    (out / "tom_tat.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("\n".join(L))
    if a.push:
        from htr_test.sync import Sync

        Sync(out, repo_suffix="-bc").push("dot1 bao_cao")
    return 0


# === 9. tự kiểm (CPU) =================================================================================================

def cmd_tu_kiem(a) -> int:
    ok = True

    def kt(ten, dk):
        nonlocal ok
        print(("✔ " if dk else "✘ ") + ten, flush=True)
        ok &= bool(dk)

    kt("bầu từ: 3/4 bản cùng sửa một từ → thay", bau_tu(["قال الرجل", "قال الرحل", "قال الرحل", "قال الرحل"]) == "قال الرحل")
    kt("bầu từ: 2 sửa / 2 giữ (hoà) → giữ gốc", bau_tu(["قال الرجل", "قال الرحل", "قال الرحل", "قال الرجل"]) == "قال الرجل")
    kt("bầu từ: 3 bản khác nhau → giữ gốc", bau_tu(["قال الرجل", "قال الرحل", "قال الرخل", "قال الرجل"]) == "قال الرجل")
    kt("bầu từ: 3/4 bản cùng thêm từ → thêm", bau_tu(["قال الرجل", "قال لي الرجل", "قال لي الرجل", "قال لي الرجل"])
       == "قال لي الرجل")
    kt("bầu từ: chỉ 1 bản thêm → không thêm", bau_tu(["قال الرجل", "قال لي الرجل", "قال الرجل", "قال الرجل"]) == "قال الرجل")
    kt("bầu từ: hamza / ة khác không tính là khác", bau_tu(["أحمد مدرسة", "احمد مدرسه", "احمد مدرسه", "احمد مدرسه"])
       == "أحمد مدرسة")
    kt("bầu dòng: chọn bản ở giữa", bau_dong(["ابجد", "ابجد هوز", "ابجد هوز", "ابجد هوز حطي"]) == "ابجد هوز")
    kt("bầu dòng: hoà → bản đầu", bau_dong(["اب", "اج"]) == "اب")
    rows = [{"id": "1", "nhan": "قال الرجل"}, {"id": "2", "nhan": "سلام"}]
    s = diem_dong(rows, {"1": "قال الرجل", "2": "سلام"})
    kt("chấm dòng: đúng hết = 100", abs(s["ky_tu"] - 100) < 1e-9 and abs(s["tu"] - 100) < 1e-9)
    s = diem_dong(rows, {"1": "قال الرحل", "2": "سلام"})
    kt("chấm dòng: sai 1 ký tự", 80 < s["ky_tu"] < 100)
    lo, hi = bootstrap({"x": [(5, 100)] * 50}, {"x": [(3, 100)] * 50}, n=200)
    kt("bootstrap: hơn đều 2 điểm → khoảng quanh +2", abs(lo - 2) < 1e-6 and abs(hi - 2) < 1e-6)
    ev = adoc_eval()
    d = diem_trang(ev, "قال الرجل\nسلام", "قال الرجل\nسلام")
    kt("chấm trang (evaluate.py của arabic-doc-ocr): đúng hết = 100", abs(d["ky_tu"] - 100) < 1e-9)
    bc = {"blocks": [{"category": "Text", "text": "dots 1"}, {"category": "Picture"},
                     {"category": "Text", "text": "", "hebrew": False}, {"category": "Text", "text": "שלום", "hebrew": True}]}
    rr = [{"id": "a", "khoi": 0, "thu_tu": 0}, {"id": "b", "khoi": 2, "thu_tu": 1}]
    dd = {"a": "dong a", "b": "dong b"}
    kt("ghép trang đánh máy: dots / khối rỗng → dòng / Hebrew giữ dots",
       _ghep_trang(bc, rr, dd, "printed") == "dots 1\ndong b\nשלום")
    kt("ghép trang viết tay: dòng", _ghep_trang(bc, rr, dd, "handwritten") == "dong a\ndong b\nשלום")
    kt("ghép trang: #5 thay chữ dots của khối", _ghep_trang(bc, rr, dd, "printed", khoi_moi={0: "moi"}) == "moi\ndong b\nשלום")
    kt("bỏ Markdown", _bo_md("## عنوان\n**قوي** | x").split() == ["عنوان", "قوي", "x"])
    js = {"json": {"line_1": {"coord": [0, 0, 10, 0, 10, 5, 0, 5], "text": "سطر", "language": "Arabic", "index": 1},
                   "line_2": {"coord": [0, 10, 10, 10, 10, 15, 0, 15], "text": "AB-1", "language": "Latin"},
                   "line_3": {"coord": [0, 20, 10, 20, 10, 25, 0, 25], "text": "اول", "language": "Arabic", "index": 0}}}
    g, b = _dong_muharaf(js)
    kt("Muharaf: giữ dòng Ả Rập theo thứ tự đọc, loại dòng Latin", [x["nhan"] for x in g] == ["اول", "سطر"] and len(b) == 1)
    import numpy as np
    from PIL import Image, ImageDraw

    from arabic_doc_ocr.lines import crop_poly

    im = Image.new("RGB", (60, 40), (250, 250, 250))
    ImageDraw.Draw(im).line([(0, 13), (59, 13)], fill=(0, 0, 0))  # nét mực ở y=13, ngay trên dòng (y 15–25)
    rec = {"box": [10, 15, 50, 25], "poly": [[10, 15], [50, 15], [50, 25], [10, 25]]}
    c0, c60 = cat_no(im, rec, 0), cat_no(im, rec, 60)  # độ dày 10 → nới 60 % = 3 px mỗi phía
    kt("nới khung 0 % = crop_poly của sản phẩm (từng pixel)", np.array_equal(
        np.asarray(c0), np.asarray(crop_poly(im, {"box": (10, 15, 50, 25), "poly": [(10, 15), (50, 15), (50, 25), (10, 25)]}))))
    kt("nới khung 0 %: nét mực ngoài đa giác bị tô màu giấy", int(np.asarray(c0.convert("L"))[13 - 11, 20]) > 200)
    kt("nới khung 60 %: ảnh cao thêm 2×3 px, nét mực ngay trên dòng được giữ",
       c60.size == (c0.size[0], c0.size[1] + 6) and int(np.asarray(c60.convert("L"))[13 - 8, 20]) < 50)
    print("✔ TỰ KIỂM ĐẠT" if ok else "✘ LỖI: TỰ KIỂM KHÔNG ĐẠT", flush=True)
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)
    for ten in ("khoi_phuc", "bo", "bon_trang", "mtrang", "mtrang_no", "doc", "chon", "bao_cao", "tu_kiem"):
        p = sub.add_parser(ten)
        p.add_argument("--out", default="/kaggle/working/dot1")
        p.add_argument("--data", default="/kaggle/working/dot1_data")
        if ten == "bon_trang":
            p.add_argument("--dots-device", default="cuda:0")
        if ten == "doc":
            p.add_argument("--phan", required=True, choices=["A", "B", "N"])
            p.add_argument("--gpu", type=int, default=0)
        if ten in ("doc", "bao_cao"):
            p.add_argument("--push", action="store_true")
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    return {"khoi_phuc": cmd_khoi_phuc, "bo": cmd_bo, "bon_trang": cmd_bon_trang, "mtrang": cmd_mtrang,
            "mtrang_no": cmd_mtrang_no, "doc": cmd_doc, "chon": cmd_chon,
            "bao_cao": cmd_bao_cao, "tu_kiem": cmd_tu_kiem}[a.lenh](a)


if __name__ == "__main__":
    sys.exit(main())
