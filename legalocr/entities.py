"""Khoanh THÔNG TIN QUAN TRỌNG trong văn bản đã bỏ phiếu: tên người, địa danh, số tiền, ngày tháng, số thửa / diện
tích, số giấy tờ, thuật ngữ pháp lý và từ phủ định. Từ được khoanh → `critical=True`: ngưỡng "read" chặt hơn, phải có
≥ 2 model cùng đọc, chữ số phải khớp từng chữ số, và LLM chỉ được XẾP HẠNG các cách đọc đã có (không đề xuất chữ mới).

Chạy trên văn bản OCR còn lỗi, nên từ khoá được so lỏng: bỏ tiền tố (و ف ب ل ك ال), gộp أ/إ/آ → ا, ى → ي, ة → ه, và
với từ ≥ 4 chữ cái thì khớp cả theo KHUNG CHỮ (rasm) — "التاريح" vẫn nhận ra là "التاريخ".

Bộ từ khoá viết cho hợp đồng mua bán đất / giấy uỷ quyền ở Palestine thập niên 1950–1980: tháng kiểu Levant
(كانون، شباط، آذار...) lẫn kiểu Ai Cập và Hijri; tiền دينار أردني، ليرة (إسرائيلية)، جنيه فلسطيني، فلس، قرش؛ đơn vị
đất دونم، قيراط (hệ 24 قيراط chia phần sở hữu)، حوض، قطعة. Bổ sung từ khoá theo bộ hồ sơ thật qua `extra_lexicon`.
"""

from __future__ import annotations

import re

from .doc import Line, Page, Word
from .script import digits_of, has_digit, rasm_key, vote_key

_LEX_MAP = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه"})


def lex_key(word: str) -> str:
    return vote_key(word).translate(_LEX_MAP)


def _set(words: str) -> frozenset:
    return frozenset(lex_key(w) for w in words.split())


DATE_CUE = _set("تاريخ التاريخ الموافق حرر تحريرا سنه عام لسنه لعام يوم اليوم شهر المؤرخ المؤرخه")
MONTH = _set("كانون شباط اذار نيسان ايار حزيران تموز اب ايلول تشرين يناير فبراير مارس ابريل مايو يونيو يونيه "
             "يوليو يوليه اغسطس سبتمبر اكتوبر نوفمبر ديسمبر محرم صفر ربيع جمادى جمادي رجب شعبان رمضان شوال القعده "
             "الحجه")
CURRENCY = _set("دينار دنانير دينارا الدينار الدنانير ليره ليرات الليره جنيه جنيها جنيهات فلس فلسا فلوس قرش قروش "
                "قرشا شيكل شاقل شواقل شيقل اردني فلسطيني اسرائيليه مصري")
AMOUNT_CUE = _set("فقط مبلغ المبلغ بمبلغ ثمن الثمن بثمن قيمه القيمه مقدار قدره وقدره")
LAND = _set("قطعه القطعه حوض الحوض قسيمه لوحه دونم دونما دونمات الدونم متر مترا امتار مساحه المساحه مساحتها حدود "
            "حدودها يحدها شمالا جنوبا شرقا غربا قيراط قيراطا قراريط سهم سهما اسهم حصه الحصه حصص مشاع شائع طابو "
            "الطابو سند تسجيل التسجيل الاراضي ارض الارض عقار العقار")
ID_CUE = _set("هويه الهويه هويته هويتها جواز بطاقه رقم الرقم")
NAME_CUE = _set("السيد السيده المدعو المدعوه البائع البائعه المشتري المشتريه الوكيل الموكل الموكله الفريق الطرف "
                "الشاهد الشهود المرحوم المرحومه الحاج الحاجه الشيخ انا الموقع الموقعه حضره المختار زوجه ارمله ورثه "
                "الورثه")
NAME_LINK = _set("بن ابن بنت ابو ام ال عبد")
PLACE_CUE = _set("قريه مدينه بلده قضاء لواء سكان اهالي الكائن الكائنه الواقع الواقعه المعروفه المسماه موقع مخيم حي "
                 "محله ناحيه اراضي المقيم الساكن القاطن")
STOP = _set("من في سكان قريه المولود رقم هويه وهو وهي الساكن المقيم المقيمه القاطن بموجب حامل حامله و الى عن "
            "قد الذي التي ادناه اعلاه المذكور المذكوره")
# "على" KHÔNG nằm trong STOP: gộp ى→ي làm nó trùng tên "علي".
# đứng giữa từ khoá và tên mà không thuộc tên: "الشاهد الأول سليم", "أنا الموقع أدناه البائع محمد"
FILLER = _set("الاول الثاني الثالث الرابع الاولى الثانيه ادناه اعلاه المذكور المذكوره")
LEGAL = _set("بعت باع بيع البيع بعته اشتريت اشترى الشراء شراء قبضت قبض استلمت استلم تسلمت تسليم التسليم تنازلت "
             "تنازل التنازل اسقطت اسقاط فراغ الفراغ افرغ وكاله الوكاله وكلت وكيلا عزل العزل قابله للعزل الرجوع رجوع "
             "نهائيا نهائي قطعيا الايجاب القبول ايجاب قبول رهن الرهن ارث تركه التركه هبه وهبت اقرار اقر اتعهد يتعهد "
             "تعهد يلتزم التزام ضمان ضامن كفيل كفاله المحكمه العدل مصدق تصديق شهود شاهد توقيع وقع بصمه ختم حق حقوق "
             "الحق ملك ملكيه الملكيه تملك مالك المالك كامل جميع كافه مطلقه دوريه الدوريه شامله")
NEGATION = _set("لا غير ليس ليست لم لن دون بدون عدم بلا")

# số viết bằng chữ (tafqit) → giá trị; "kind": u = đơn vị/chục (cộng), h = trăm, k = nghìn, m = triệu
_NUM = {}
for _w, _v in [("واحد", 1), ("واحده", 1), ("احد", 1), ("احدى", 1), ("اثنان", 2), ("اثنين", 2), ("اثنتان", 2),
               ("اثنتين", 2), ("ثلاث", 3), ("ثلاثه", 3), ("اربع", 4), ("اربعه", 4), ("خمس", 5), ("خمسه", 5),
               ("ست", 6), ("سته", 6), ("سبع", 7), ("سبعه", 7), ("ثمان", 8), ("ثماني", 8), ("ثمانيه", 8), ("تسع", 9),
               ("تسعه", 9), ("عشر", 10), ("عشره", 10), ("عشرون", 20), ("عشرين", 20), ("ثلاثون", 30), ("ثلاثين", 30),
               ("اربعون", 40), ("اربعين", 40), ("خمسون", 50), ("خمسين", 50), ("ستون", 60), ("ستين", 60),
               ("سبعون", 70), ("سبعين", 70), ("ثمانون", 80), ("ثمانين", 80), ("تسعون", 90), ("تسعين", 90)]:
    _NUM[lex_key(_w)] = (_v, "u")
for _w, _v in [("مائه", 100), ("مئه", 100), ("ميه", 100), ("مايه", 100), ("مائتان", 200), ("مائتين", 200),
               ("مئتان", 200), ("مئتين", 200), ("ميتين", 200)]:
    _NUM[lex_key(_w)] = (_v, "h")
for _p, _u in [("ثلاث", 3), ("اربع", 4), ("خمس", 5), ("ست", 6), ("سبع", 7), ("ثمان", 8), ("تسع", 9)]:
    for _h in ("مائه", "مئه"):
        _NUM[lex_key(_p + _h)] = (_u * 100, "h")
for _w, _v in [("الف", 1000), ("الفا", 1000), ("الاف", 1000), ("الفان", 2000), ("الفين", 2000)]:
    _NUM[lex_key(_w)] = (_v, "k")
for _w in ("مليون", "ملايين", "مليونا"):
    _NUM[lex_key(_w)] = (1_000_000, "m")
FRACTION = _set("نصف ربع ثلث ثلثي سدس")  # "ثمن" (1/8) bỏ: trùng "ثمن" = giá
_DATE_DIGITS = re.compile(r"^\D*\d{1,4}\s*[/.\-]\s*\d{1,2}(\s*[/.\-]\s*\d{1,4})?\D*$")

_RASM_LEX: dict[frozenset, frozenset] = {}
_SPAN_STOP = (NAME_CUE, PLACE_CUE, LAND, LEGAL, CURRENCY, DATE_CUE, AMOUNT_CUE, ID_CUE)


def _stems(word: str) -> list[str]:
    k = lex_key(word)
    out = [k]
    for p in ("و", "ف", "ب", "ل", "ك"):
        if k.startswith(p) and len(k) > 2:
            out.append(k[1:])
    for s in list(out):
        if s.startswith("ال") and len(s) > 3:
            out.append(s[2:])
        if s.startswith("لل") and len(s) > 3:
            out.append(s[2:])
    return out


def in_lex(word: str, lex: frozenset, fuzzy: bool = True) -> bool:
    stems = _stems(word)
    if any(s in lex or ("ال" + s) in lex for s in stems):
        return True
    if not fuzzy:
        return False
    if lex not in _RASM_LEX:
        _RASM_LEX[lex] = frozenset(rasm_key(w) for w in lex if len(w) >= 4)
    return any(len(s) >= 4 and rasm_key(s) in _RASM_LEX[lex] for s in stems)


def number_value(word: str) -> tuple[int, str] | None:
    for s in _stems(word):
        if s in _NUM:
            return _NUM[s]
    return None


def words_to_number(tokens: list[str]) -> int | None:
    """Số viết bằng chữ → số nguyên: "خمسة آلاف وثلاثمائة" → 5300, "ثلاث مائة" → 300, "احد عشر" → 11."""
    total, cur, last_unit, seen = 0, 0, 0, False
    for t in tokens:
        if lex_key(t) == "و":  # "خمسة و عشرون": chữ و đứng riêng
            continue
        nv = number_value(t)
        if nv is None:
            if seen:
                break
            continue
        v, kind = nv
        seen = True
        if kind == "u":
            cur += v
            last_unit = v if v < 10 else 0
        elif kind == "h":
            cur += last_unit * 99 if v == 100 and last_unit else v  # "ثلاث مائة" = 3 → 300
            last_unit = 0
        elif v == 2000:  # "الفين" (số đôi) đứng một mình
            total, cur, last_unit = total + cur + 2000, 0, 0
        else:  # nghìn / triệu: nhân phần đang có (mặc định 1)
            total, cur, last_unit = total + (cur or 1) * v, 0, 0
    return total + cur if seen else None


# khi một từ khớp nhiều loại: ngày (mẫu d/m/y) thắng số tiền ở gần, số tiền thắng "số" chung chung...
_PRIORITY = {"date": 7, "id": 6, "amount": 5, "land": 4, "name": 3, "place": 3, "number": 2, "legal": 1, "negation": 1}


def _tag(words: list[Word], i: int, entity: str) -> None:
    w = words[i]
    if w.entity is None or _PRIORITY.get(entity, 0) > _PRIORITY.get(w.entity, 0):
        w.entity = entity
    w.critical = True


def tag_line(words: list[Word], extra_lexicon: dict[str, frozenset] | None = None) -> None:
    """Gắn `entity` / `critical` cho từng từ của một dòng (theo chữ đã bỏ phiếu, lẫn các cách đọc khác: một model
    đọc ra chữ số ở vị trí này là đủ để coi vị trí đó là SỐ)."""
    n = len(words)
    texts = [w.text for w in words]
    for i, w in enumerate(words):
        variants = [w.text] + [r for r in w.readings.values() if r]
        if any(has_digit(v) for v in variants) or number_value(w.text) or in_lex(w.text, FRACTION, fuzzy=False):
            _tag(words, i, "number")
        if in_lex(w.text, LEGAL):
            _tag(words, i, "legal")
        if in_lex(w.text, NEGATION, fuzzy=False):
            _tag(words, i, "negation")
        for name, lex in (extra_lexicon or {}).items():
            if in_lex(w.text, lex):
                _tag(words, i, name)
    for i, t in enumerate(texts):
        near = range(max(0, i - 3), min(n, i + 4))
        if _DATE_DIGITS.match(digits_like(t)) and has_digit(t):
            _tag(words, i, "date")
        if in_lex(t, MONTH, fuzzy=False) and any(has_digit(texts[j]) or number_value(texts[j]) for j in near if j != i):
            for j in near:
                if has_digit(texts[j]) or j == i or in_lex(texts[j], MONTH, fuzzy=False):
                    _tag(words, j, "date")
        if in_lex(t, DATE_CUE):
            for j in range(i + 1, min(n, i + 5)):
                if has_digit(texts[j]) or in_lex(texts[j], MONTH, fuzzy=False) or number_value(texts[j]):
                    _tag(words, j, "date")
        if in_lex(t, CURRENCY):
            _tag(words, i, "amount")
            for j in near:
                if words[j].entity == "number" or has_digit(texts[j]) or number_value(texts[j]):
                    _tag(words, j, "amount")
        if lex_key(t) == "فقط":  # "فقط ... لا غير": cả cụm là số tiền viết bằng chữ
            for j in range(i, min(n, i + 14)):
                _tag(words, j, "amount")
                if lex_key(texts[j]).endswith("غير"):
                    break
        if in_lex(t, AMOUNT_CUE) and lex_key(t) != "فقط":
            for j in range(i + 1, min(n, i + 6)):
                if has_digit(texts[j]) or number_value(texts[j]):
                    _tag(words, j, "amount")
        if in_lex(t, LAND):
            _tag(words, i, "land")
            for j in range(i + 1, min(n, i + 3)):
                if has_digit(texts[j]) or number_value(texts[j]):
                    _tag(words, j, "land")
        if in_lex(t, ID_CUE, fuzzy=False):
            for j in range(i + 1, min(n, i + 4)):
                if has_digit(texts[j]):
                    _tag(words, j, "id")
        if in_lex(t, NAME_CUE):
            _span(words, texts, i + 1, "name", 5)
        if in_lex(t, PLACE_CUE):
            _span(words, texts, i + 1, "place", 3)


def _span(words: list[Word], texts: list[str], start: int, entity: str, max_len: int) -> None:
    """Gắn nhãn tối đa `max_len` từ (không tính bن / ابن / أبو...) sau từ khoá; bỏ qua từ đệm (الأول، أدناه) và từ khoá
    liền sau (chuỗi "أنا الموقع أدناه البائع"); dừng ở từ khoá loại khác, chữ số, dấu câu cuối từ."""
    j = start
    while j < len(texts) and (lex_key(texts[j]) in FILLER or in_lex(texts[j], NAME_CUE, fuzzy=False)
                              or in_lex(texts[j], PLACE_CUE, fuzzy=False)):
        j += 1
    k = 0
    while j < len(texts) and k < max_len:
        t = texts[j]
        if (not vote_key(t) or has_digit(t) or (lex_key(t) in STOP and lex_key(t) not in NAME_LINK)
                or any(in_lex(t, lex, fuzzy=False) for lex in _SPAN_STOP)):
            break
        _tag(words, j, entity)
        k += 0 if lex_key(t) in NAME_LINK else 1
        j += 1
        if t.rstrip()[-1:] in "،,.:؛":
            break


def digits_like(t: str) -> str:
    return t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "0123456789" * 2))


_ORDER = {"read": 0, "uncertain": 1, "illegible": 2}


def extract_fields(page: Page) -> list[dict]:
    """Gom các từ quan trọng liền nhau cùng loại thành một trường (vd. một tên 3 từ) — kèm trạng thái xấu nhất,
    độ tin cậy thấp nhất và id từ để truy về ảnh. "legal"/"negation" không gom (là từ đơn lẻ trong điều khoản)."""
    out: list[dict] = []
    for ln in page.lines:
        cur: list[Word] = []
        for w in ln.words + [None]:  # type: ignore[list-item]
            if cur and (w is None or w.entity != cur[0].entity):
                ent = cur[0].entity
                if ent not in ("legal", "negation"):
                    text = " ".join(x.text for x in cur)
                    f = {"type": ent, "text": text, "line": ln.id, "word_ids": [x.id for x in cur],
                         "status": max((x.status for x in cur), key=_ORDER.get),
                         "confidence": min(x.confidence for x in cur)}
                    if ent in ("amount", "number", "land"):
                        f["digits"] = " ".join(d for d in (digits_of(x.text) for x in cur) if d)
                        f["words_value"] = words_to_number([x.text for x in cur])
                    out.append(f)
                cur = []
            if w is not None and w.entity:
                cur.append(w)
    return out


def tag_page(page: Page, extra_lexicon: dict[str, frozenset] | None = None) -> None:
    for ln in page.lines:
        if ln.region == "Text":
            tag_line(ln.words, extra_lexicon)


def lexicon_from_file(path: str) -> frozenset:
    """Danh sách từ (mỗi dòng một tên làng / dòng họ / thuật ngữ) → bộ từ khoá dùng cho `extra_lexicon`."""
    with open(path, encoding="utf-8") as f:
        return frozenset(lex_key(w) for line in f for w in line.split() if w.strip())


def line_text(ln: Line) -> str:
    return " ".join(w.text for w in ln.words)
