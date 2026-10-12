"""Prompt cho ba chiến lược (tiếng Anh cho phần chỉ dẫn, Ả Rập cho ví dụ):

  A — viết lại cả chunk với ràng buộc "sửa tối thiểu", rồi diff → danh sách sửa.
  B — chỉ khoanh từ nghi lỗi kèm đề xuất (JSON), không viết lại chunk.
  C — như A nhưng các từ nghi lỗi (do bước chấm NLL / độ tin cậy dots chọn) được đánh dấu [[...]]; chỉ được đổi từ đánh dấu.

Ví dụ few-shot do TÔI VIẾT TAY, không lấy từ dữ liệu đánh giá (tránh rò rỉ). Chúng cũng dạy điều quan trọng nhất của loại
tài liệu này: từ địa phương / chính tả cũ KHÔNG phải lỗi OCR → giữ nguyên.
"""

from __future__ import annotations

_RULES_KEEP = (
    "Keep everything else EXACTLY as written: dialect words, old-fashioned spellings, names of people and places, "
    "numbers, dates, abbreviations, punctuation and line breaks. Do NOT standardize or modernize the language, do NOT "
    "add hamza or diacritics, do NOT translate, paraphrase, add or delete words. If you are not sure that a word is an "
    "OCR mistake, leave it unchanged."
)
_MISTAKES = (
    "The text may contain OCR mistakes: a wrong letter caused by similar shapes or dots (ب ت ث ن ي, ج ح خ, د ذ, ر ز, "
    "س ش, ص ض, ط ظ, ع غ, ف ق, ة ه, ى ي, ا أ إ), a word wrongly split in two, or two words wrongly joined."
)
_INTRO = ("You are a conservative proofreader of OCR output from HANDWRITTEN Arabic documents (personal letters, "
          "contracts, records). The text may be dialectal or old-fashioned. ")

SYSTEM = {
    "A": _INTRO + _MISTAKES + " Correct ONLY such mistakes. " + _RULES_KEEP +
         " Output ONLY the corrected text inside <output></output> tags.",
    "B": _INTRO + _MISTAKES + " List ONLY the words that are very likely OCR mistakes, each with its corrected form. "
         "Never list a word you are unsure about, and never list numbers, dates, names or Latin text. Output ONLY a JSON "
         "array like [{\"word\": \"<exactly as it appears in the input>\", \"fix\": \"<corrected word>\"}], or [] if "
         "there is nothing to fix.",
    "C": _INTRO + "Words inside [[ ]] were flagged as possibly misread by the OCR engine. " + _MISTAKES +
         " For each flagged word decide whether it is a genuine OCR mistake; if so correct it, otherwise keep it "
         "unchanged. NEVER change a word that is not inside [[ ]]. " + _RULES_KEEP +
         " Remove the [[ ]] markers. Output ONLY the full text inside <output></output> tags.",
}

# Kiểu "quyết đoán" (assert): nói rõ MẬT ĐỘ LỖI CAO (dots đọc chữ viết tay sai tới ~40% ký tự) và yêu cầu sửa mọi từ rõ ràng là đọc
# sai, sửa ít chữ cái nhất có thể. Kiểu "bảo thủ" (cons, mặc định) tuyệt đối ưu tiên giữ nguyên: đo trên dev cho thấy nó gần như
# không sửa gì (sửa đúng ~1% số từ trong tầm với). Chốt chặn cứng (guard.py) áp như nhau cho cả hai kiểu.
_INTRO_ASSERT = ("You are an expert proofreader of OCR output from HANDWRITTEN Arabic documents (personal letters, official "
                 "decrees, contracts). The text may be dialectal or old-fashioned. The OCR engine is weak on handwriting: MANY "
                 "words (often a third or more) are misreadings — a wrong or missing letter, wrong dots, a word wrongly split "
                 "or two words wrongly joined. ")
_ASSERT_RULE = ("Read each sentence, understand its meaning from the context (place names, titles, common phrases, legal "
                "wording), and correct every word that is clearly a misreading, changing as few letters as possible (usually "
                "one or two). Keep words that are valid and fit the context unchanged — including dialect words, old "
                "spellings, names of people and places, numbers, dates and punctuation. Do NOT paraphrase, translate, add or "
                "delete words, or add diacritics. ")
SYSTEM_ASSERT = {
    "A": _INTRO_ASSERT + _ASSERT_RULE + "Output ONLY the corrected text inside <output></output> tags.",
    "B": _INTRO_ASSERT + "List every word that is clearly a misreading, each with its corrected form (change as few letters as "
         "possible). Never list valid words, numbers, dates, names or Latin text. Output ONLY a JSON array like "
         "[{\"word\": \"<exactly as it appears in the input>\", \"fix\": \"<corrected word>\"}], or [] if there is nothing to fix.",
    "C": _INTRO_ASSERT + "Words inside [[ ]] were flagged as likely misreadings. For each flagged word decide: if it is a "
         "misreading, correct it with as few letter changes as possible; if it is a valid word that fits the context, keep it. "
         "NEVER change a word that is not inside [[ ]]. Do NOT paraphrase, translate, add or delete words, or add diacritics. "
         "Remove the [[ ]] markers. Output ONLY the full text inside <output></output> tags.",
}
STYLES = {"cons": SYSTEM, "assert": SYSTEM_ASSERT}

# (đầu vào, đáp án mong muốn). Ví dụ 2: tiếng địa phương + số → KHÔNG đổi gì.
_EX = [
    ("الى الاخ العزيز جبيلي المحتزم\nاني بخير والحمد لله وارجو ان تكونوا بالف خبر",
     "الى الاخ العزيز جبيلي المحترم\nاني بخير والحمد لله وارجو ان تكونوا بالف خير",
     [("المحتزم", "المحترم"), ("خبر", "خير")]),
    ("بدي اروح عالبيت بكرا الصبح الساعه 9 ونحكي مع ابو علي",
     "بدي اروح عالبيت بكرا الصبح الساعه 9 ونحكي مع ابو علي", []),
    ("وصلنا الى البلدة بعدالظهر وكان الجو جميل جدا",
     "وصلنا الى البلدة بعد الظهر وكان الجو جميل جدا", [("بعدالظهر", "بعد الظهر")]),
]
# từ được đánh dấu [[ ]] trong ví dụ của chiến lược C (gồm cả từ ĐÚNG mà người dùng nên giữ nguyên)
_EX_MARKS = [["المحتزم", "خبر"], ["عالبيت", "الساعه"], ["بعدالظهر"]]


def mark_words(text_words_spans: list[tuple[str, int, int]], text: str, flagged: set[int]) -> str:
    """Bọc từ có chỉ số trong `flagged` bằng [[ ]] (chỉ số theo words_with_spans của `text`)."""
    out, pos = [], 0
    for i, (w, a, b) in enumerate(text_words_spans):
        out.append(text[pos:a])
        out.append(f"[[{w}]]" if i in flagged else w)
        pos = b
    out.append(text[pos:])
    return "".join(out)


def _mark_example(text: str, marks: list[str]) -> str:
    for m in marks:
        text = text.replace(m, f"[[{m}]]", 1)
    return text


def user_content(text: str) -> str:
    return f"<input>{text}</input>"


def messages(strategy: str, text: str, fewshot: bool = False, style: str = "cons") -> list[dict]:
    """Danh sách thông điệp chat cho một chunk. `text` của chiến lược C phải là văn bản đã đánh dấu [[ ]]."""
    msgs = [{"role": "system", "content": STYLES[style][strategy]}]
    if fewshot:
        for (src, dst, fixes), marks in zip(_EX, _EX_MARKS):
            if strategy == "A":
                u, a = src, f"<output>{dst}</output>"
            elif strategy == "C":
                u, a = _mark_example(src, marks), f"<output>{dst}</output>"
            else:
                import json

                u, a = src, json.dumps([{"word": w, "fix": f} for w, f in fixes], ensure_ascii=False)
            msgs += [{"role": "user", "content": user_content(u)}, {"role": "assistant", "content": a}]
    msgs.append({"role": "user", "content": user_content(text)})
    return msgs
