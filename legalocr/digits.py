"""Đọc CHỮ SỐ (Ả Rập-Ấn ٠–٩ lẫn Latin 0–9, và / . - ,) bằng một bộ phân loại nhỏ trên từng nét số — vì Tesseract (ara,
cả bản fast lẫn best, có hay không ép bộ ký tự) gần như không đọc được chữ số Ả Rập-Ấn của máy chữ: đo trên công văn 1972
"رقم ٥٤٩ لسنة ١٩٧٢" → "رقم 641 لسنة 1171", ép bộ ký tự ٠–٩ thì ra rỗng / "١".

Cách làm:
- Chữ số Ả Rập-Ấn đứng RỜI nhau (mỗi chữ số một vùng mực liền), viết trái → phải trong số. Cắt từ chứa số thành các
  vùng mực, phân loại từng vùng → ghép lại.
- Huấn luyện KHÔNG cần dữ liệu thật: dựng chuỗi số ngẫu nhiên bằng 21 phông Ả Rập mở (SIL OFL, thư viện phông của
  ocrbench), làm xấu kiểu máy chữ / scan (đậm–mảnh nét, mờ, nhiễu, xoay, nén), cắt vùng mực bằng CHÍNH hàm dùng lúc
  đọc → đặc trưng HOG + vị trí / cỡ tương đối trong từ (phân biệt ٠ giữa dòng với dấu chấm ở chân dòng) →
  MLP nhỏ (1 lớp ẩn). ~3–4 phút CPU lần đầu, lưu cache (~/.cache/legalocr/digits_v4.npz).
- Mỗi chữ số có xác suất; từ có chữ số nào < `min_prob`, hoặc vùng mực không giống chữ số nào → độ tin cậy thấp → [؟].
Giới hạn: chữ số VIẾT TAY dính nét, hoặc nét chữ cái bên cạnh lọt vào khung từ → đọc sai, nhưng xác suất thấp nên bị
đánh dấu; số Latin dính nhau ("24725" phông in) tách được vì phông in thường có khoảng hở.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"
LAT_DIGITS = "0123456789"
SYMBOLS = "/.-,"
CLASSES = list(AR_DIGITS + LAT_DIGITS + SYMBOLS)
CACHE = Path(os.environ.get("LEGALOCR_CACHE", Path.home() / ".cache" / "legalocr"))
MODEL_FILE = "digits_v4.npz"
SIZE = 32


# ------------------------------------------------------------------ tách vùng mực + đặc trưng (dùng chung train / đọc)
def ink_mask(img: Image.Image) -> np.ndarray:
    g = np.asarray(img.convert("L")).astype(np.float32)
    if g.size == 0:
        return np.zeros((0, 0), bool)
    bg = np.percentile(g, 90)
    fg = np.percentile(g, 5)
    if bg - fg < 25:  # gần như không có mực
        return np.zeros(g.shape, bool)
    return g < (bg + fg) / 2


def components(mask: np.ndarray, min_area: int = 4) -> list[tuple[int, int, int, int, np.ndarray]]:
    """Vùng mực liền (8 lân cận) → [(x0, y0, x1, y1, mặt nạ cắt)] trái → phải. Vùng chồng nhau theo chiều ngang
    > 60% bề rộng vùng hẹp hơn được gộp (nét rời của cùng một chữ số, vd. ٤ viết đứt)."""
    from scipy import ndimage as ndi

    lab, n = ndi.label(mask, structure=np.ones((3, 3)))
    boxes = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None:
            continue
        m = lab[sl] == i
        if m.sum() < min_area:
            continue
        boxes.append([sl[1].start, sl[0].start, sl[1].stop, sl[0].stop])
    boxes.sort()
    merged: list[list[int]] = []
    for b in boxes:
        if merged:
            p = merged[-1]
            ov = min(p[2], b[2]) - max(p[0], b[0])
            if ov > 0.6 * min(p[2] - p[0], b[2] - b[0]):
                merged[-1] = [min(p[0], b[0]), min(p[1], b[1]), max(p[2], b[2]), max(p[3], b[3])]
                continue
        merged.append(b)
    return [(x0, y0, x1, y1, mask[y0:y1, x0:x1]) for x0, y0, x1, y1 in merged]


def features(comp: tuple, token_h: int, token_top: int) -> np.ndarray:
    from skimage.feature import hog

    x0, y0, x1, y1, m = comp
    h, w = m.shape
    s = max(h, w)
    canvas = np.zeros((s, s), np.float32)
    canvas[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w] = m
    small = np.asarray(Image.fromarray((canvas * 255).astype(np.uint8)).resize((SIZE, SIZE), Image.BILINEAR),
                       np.float32) / 255
    hf = hog(small, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True)
    th = max(1, token_h)
    geo = np.array([h / th, w / th, w / max(1, h), ((y0 + y1) / 2 - token_top) / th, (y1 - token_top) / th,
                    m.mean()], np.float32)
    return np.concatenate([hf, small[::4, ::4].ravel(), geo * 3])


def token_features(img: Image.Image) -> tuple[list, list]:
    mask = ink_mask(img)
    comps = components(mask)
    if not comps:
        return [], []
    top = min(c[1] for c in comps)
    bot = max(c[3] for c in comps)
    return comps, [features(c, bot - top, top) for c in comps]


# ------------------------------------------------------------------ dữ liệu tổng hợp
def _fonts() -> list[Path]:
    from ocrbench.arabic_fonts import available

    out = []
    for reg, bold in available().values():  # cả bản Bold: chữ máy chữ / ruy băng đậm mực
        out += [Path(f) for f in (reg, bold) if f and Path(f).exists()]
    return out


def _random_string(rng) -> str:
    system = AR_DIGITS if rng.random() < 0.7 else LAT_DIGITS
    kind = rng.random()
    if kind < 0.3:   # ngày
        d, m, y = rng.integers(1, 32), rng.integers(1, 13), rng.integers(1900, 2030)
        parts = [str(d), str(m), str(y if rng.random() < 0.7 else y % 100)]
        if rng.random() < 0.5:
            parts = parts[::-1]
        s = rng.choice(["/", ".", "-"]).join(parts)
    elif kind < 0.4:
        s = f"{rng.integers(1, 99999)}.{rng.integers(0, 99)}"
    elif kind < 0.5:  # số tiền có phân cách hàng nghìn: 713,000.00
        s = f"{int(rng.integers(1000, 9_999_999)):,}" + (f".{int(rng.integers(0, 100)):02d}" if rng.random() < 0.5 else "")
    else:
        s = str(rng.integers(0, 10 ** int(rng.integers(1, 7))))
    return s.translate(str.maketrans(LAT_DIGITS, system))


def _render(text: str, font: ImageFont.FreeTypeFont, rng) -> tuple[Image.Image, list[tuple[int, int, str]]]:
    """Dựng chuỗi (trái → phải) + khoảng x của từng ký tự để gán nhãn vùng mực."""
    pad = 12
    spacing = int(rng.integers(0, max(1, font.size // 6)))
    xs, x = [], pad
    for ch in text:
        w = font.getlength(ch)
        xs.append((x, x + w, ch))
        x += w + spacing
    H = int(font.size * 1.8)
    im = Image.new("L", (int(x + pad), H), 255)
    d = ImageDraw.Draw(im)
    for x0, _, ch in xs:
        d.text((x0, font.size * 0.3), ch, font=font, fill=0)
    return im, [(int(a), int(b), ch) for a, b, ch in xs]


def _degrade(im: Image.Image, rng) -> Image.Image:
    r = rng.random()
    if r < 0.15:
        im = im.filter(ImageFilter.MinFilter(5))           # nét rất đậm: vòng của ٩ / ٥ bị lấp kín
    elif r < 0.4:
        im = im.filter(ImageFilter.MinFilter(3))           # nét đậm (ruy băng máy chữ đậm mực)
    elif r < 0.5:
        im = im.filter(ImageFilter.MaxFilter(3))           # nét mảnh / mực nhạt
    if rng.random() < 0.2:  # đóng hình thái học: lấp vòng nhỏ (٩ máy chữ đậm mực nhìn như ١ có đầu đặc) mà không làm đậm
        im = im.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    if rng.random() < 0.6:
        im = im.filter(ImageFilter.GaussianBlur(float(rng.uniform(0.3, 1.4))))
    if rng.random() < 0.5:
        im = im.rotate(float(rng.uniform(-4, 4)), resample=Image.BILINEAR, fillcolor=255, expand=False)
    k = float(rng.uniform(0.35, 1.0))                      # độ phân giải thấp (ảnh chụp màn hình) rồi phóng lại
    if k < 0.95:
        small = im.resize((max(8, int(im.width * k)), max(8, int(im.height * k))), Image.BILINEAR)
        im = small.resize(im.size, Image.BILINEAR)
    a = np.asarray(im).astype(np.float32)
    a = a * float(rng.uniform(0.75, 1.0)) + float(rng.uniform(0, 60))  # giấy ố, mực nhạt
    a += rng.normal(0, rng.uniform(0, 12), a.shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def synth_dataset(n_strings: int = 9000, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    fonts = _fonts()
    X, Y = [], []
    for _ in range(n_strings):
        f = fonts[int(rng.integers(len(fonts)))]
        font = ImageFont.truetype(str(f), int(rng.integers(18, 56)))
        text = _random_string(rng)
        im, spans = _render(text, font, rng)
        im = _degrade(im, rng)
        comps, feats = token_features(im)
        for c, ft in zip(comps, feats):
            cx = (c[0] + c[2]) / 2
            hit = [ch for a, b, ch in spans if a - 1 <= cx <= b + 1]
            inside = [ch for a, b, ch in spans if c[0] < b and c[2] > a]
            if len(hit) == 1 and len(inside) == 1:   # vùng mực trùm 2 ký tự (dính nhau) → bỏ khỏi dữ liệu huấn luyện
                X.append(ft)
                Y.append(CLASSES.index(hit[0]))
    return np.array(X, np.float32), np.array(Y, np.int64)


# ------------------------------------------------------------------ mô hình
@dataclass
class DigitModel:
    """MLP một lớp ẩn (ReLU) — trọng số numpy, suy luận không cần sklearn."""
    W1: np.ndarray
    b1: np.ndarray
    W2: np.ndarray
    b2: np.ndarray
    mu: np.ndarray
    sd: np.ndarray

    def proba(self, X: np.ndarray) -> np.ndarray:
        h = np.maximum(0, ((X - self.mu) / self.sd) @ self.W1 + self.b1)
        z = h @ self.W2 + self.b2
        z -= z.max(1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(1, keepdims=True)


def train(n_strings: int = 12000, seed: int = 0) -> tuple[DigitModel, dict]:
    from sklearn.neural_network import MLPClassifier

    X, Y = synth_dataset(n_strings, seed)
    mu, sd = X.mean(0), X.std(0) + 1e-4
    idx = np.random.default_rng(seed + 1).permutation(len(Y))
    cut = int(0.9 * len(Y))
    tr, va = idx[:cut], idx[cut:]
    clf = MLPClassifier(hidden_layer_sizes=(192,), alpha=1e-3, max_iter=60, early_stopping=True, random_state=seed)
    clf.fit((X[tr] - mu) / sd, Y[tr])
    W2 = np.zeros((clf.coefs_[1].shape[0], len(CLASSES)), np.float32)
    b2 = np.full(len(CLASSES), -30.0, np.float32)  # lớp không có trong dữ liệu → xác suất ~0
    W2[:, clf.classes_] = clf.coefs_[1]
    b2[clf.classes_] = clf.intercepts_[1]
    m = DigitModel(clf.coefs_[0].astype(np.float32), clf.intercepts_[0].astype(np.float32), W2, b2, mu, sd)
    acc = float((m.proba(X[va]).argmax(1) == Y[va]).mean())
    return m, {"n": int(len(Y)), "val_acc": acc}


def save(m: DigitModel, path: Path, info: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, W1=m.W1, b1=m.b1, W2=m.W2, b2=m.b2, mu=m.mu, sd=m.sd, val_acc=info["val_acc"], n=info["n"])


def load(path: Path | None = None) -> DigitModel:
    path = path or CACHE / MODEL_FILE
    if not path.exists():
        m, info = train()
        save(m, path, info)
    d = np.load(path)
    return DigitModel(d["W1"], d["b1"], d["W2"], d["b2"], d["mu"], d["sd"])


_MODEL: DigitModel | None = None


def model() -> DigitModel:
    global _MODEL
    if _MODEL is None:
        _MODEL = load()
    return _MODEL


@dataclass
class DigitReading:
    text: str
    probs: list[float]
    confidence: float     # xác suất thấp nhất trong các ký tự
    system: str           # ar | lat | mixed | none


def _decode(P: np.ndarray, system: str) -> tuple[str, list[float]]:
    ar_idx = [CLASSES.index(c) for c in AR_DIGITS]
    lat_idx = [CLASSES.index(c) for c in LAT_DIGITS]
    sym_idx = [CLASSES.index(c) for c in SYMBOLS]
    allowed = (ar_idx if system == "ar" else lat_idx) + sym_idx
    chars, probs = [], []
    for p in P:
        q = p[allowed] / max(1e-9, p[allowed].sum())
        k = int(q.argmax())
        chars.append(CLASSES[allowed[k]])
        probs.append(float(q[k]) * float(p[allowed].sum()))  # nhân phần xác suất dành cho hệ đã chọn
    return "".join(chars), probs


def _system_mass(P: np.ndarray) -> tuple[float, float]:
    ar = P[:, [CLASSES.index(c) for c in AR_DIGITS]].sum()
    lat = P[:, [CLASSES.index(c) for c in LAT_DIGITS]].sum()
    return float(ar), float(lat)


def read_tokens(imgs: list[Image.Image], strong: float = 3.0) -> list[DigitReading]:
    """Nhiều từ chứa số của CÙNG một trang. Một con số chỉ viết bằng MỘT hệ chữ số, và một trang thường chỉ dùng một
    hệ → chọn hệ theo tổng xác suất cả TRANG; từ nào tự nó nghiêng hẳn về hệ kia (≥ `strong` lần) mới giữ hệ riêng.
    Gỡ các cặp gần như giống hệt giữa hai hệ (١ / 1, ٠ / dấu chấm) ở số ngắn như "٦"."""
    Ps = []
    for im in imgs:
        comps, feats = token_features(im)
        Ps.append(model().proba(np.stack(feats)) if comps else None)
    tot_ar = sum(_system_mass(P)[0] for P in Ps if P is not None)
    tot_lat = sum(_system_mass(P)[1] for P in Ps if P is not None)
    page = "ar" if tot_ar >= tot_lat else "lat"
    out = []
    for P in Ps:
        if P is None:
            out.append(DigitReading("", [], 0.0, "none"))
            continue
        ar, lat = _system_mass(P)
        own = "ar" if ar >= lat else "lat"
        system = own if (own != page and max(ar, lat) >= strong * max(1e-9, min(ar, lat))) else page
        text, probs = _decode(P, system)
        out.append(DigitReading(text, probs, min(probs), system))
    return out


def read_token(img: Image.Image) -> DigitReading:
    """MỘT từ chứa số → chuỗi số đọc trái → phải (hệ chữ số theo chính từ đó)."""
    return read_tokens([img], strong=1.0)[0]


def merge_affixes(tess_token: str, digit_text: str) -> str:
    """Giữ dấu câu đầu / cuối từ của Tesseract (thứ tự logic), lấy phần số của bộ đọc chữ số. Bộ đọc đọc trái → phải
    nên dấu chấm cuối câu (nằm BÊN TRÁI số trong dòng phải → trái) bị đặt lên đầu: "18/04/2024." → ".18/04/2024"."""
    from postcorrect.text import split_affixes

    pre, _core, suf = split_affixes(tess_token)
    return pre + digit_text.strip(SYMBOLS) + suf


def plausible_number(text: str, max_len: int = 14, max_sym: float = 0.34) -> bool:
    """Chuỗi số có hình dạng hợp lý (số, ngày, số tiền). Trên dòng chữ tay / ô công chứng Hebrew bộ đọc từng nét số
    từng ra "٨.٥.٩٣.٦.٢--٠.٠١-.١٢..٣٤" — không bỏ phiếu chuỗi như vậy."""
    core = text.strip(SYMBOLS)
    if not core or len(core) > max_len:
        return False
    if sum(c in SYMBOLS for c in core) > max_sym * len(core):
        return False
    return not any(a in SYMBOLS and b in SYMBOLS for a, b in zip(core, core[1:]))
