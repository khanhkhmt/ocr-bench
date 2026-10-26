# Transcription guidelines — Arabic documents 1970–1990 (typed and handwritten)

Version 1 · 2026-10-26 · contact: the project owner (khanhkhmt)

You will receive scanned pages of Arabic documents from about 1970 to 1990: typewritten contracts, powers of attorney,
official letters, forms, some handwritten pages, often with stamps, signatures and short notes in other scripts.
For every page we need **an exact transcription of the Arabic text, as written**. It is used to measure and train
OCR software, so a wrong letter in the transcription counts as an OCR error. **Accuracy matters more than speed.**

## 1. What to deliver

For every image `<id>.jpg`, one UTF-8 JSON file `<id>.json`:

```json
{
  "page": "<id>",
  "type": "typed | handwritten | mixed",
  "text": "main Arabic text, one output line per line of the page, blank line between blocks",
  "stamps": "legible Arabic text inside stamps / seals, one stamp per line (empty string if none)",
  "handwritten_notes": "handwritten Arabic on a typed page (empty string if none or if type = handwritten)",
  "other_scripts": "which non-Arabic text is on the page (e.g. 'Hebrew notary block, right side') — do NOT transcribe it",
  "year": "year written on the document if visible, else empty",
  "quality": "good | faded | carbon copy | photocopy | damaged",
  "uncertain": ["short notes on words you are unsure of"],
  "annotator": "<your annotator code>",
  "minutes": <time spent on this page>
}
```

A filled example (a 1979 typed power of attorney with stamps and a Hebrew notary block) is in `example/page_3.json`
next to this file, with its image `example/page_3.jpeg`. It shows how the fields are used; its `text` is one
paragraph per block (an older format, stamps were not transcribed) — **your delivery must split the text line by
line (rule 3) and fill `stamps`**.

## 2. Transcription rules

1. **Write exactly what is on the page.** Do not correct spelling, grammar or names, even when they look wrong
   (example: a name typed `ماذن` stays `ماذن`). Do not complete abbreviations. Do not translate.
2. **Standard Arabic Unicode, normal (logical) order**, typed with a normal Arabic keyboard. No presentation forms,
   no tatweel `ـ`, no bidi control characters. Do not reverse the text.
3. **Lines:** one output line for each line of text on the page, in the same order. A line that continues across a
   column / table cell is still split as on the page.
4. **Blocks:** a blank line between blocks (title, paragraph, table, column, address, signature area). Reading order:
   top to bottom; when there are columns, the right column first.
5. **Letters as written:** keep `أ إ آ ا`, `ى ي`, `ة ه`, `ء ئ ؤ` exactly as the page shows them. Do not add vowel
   marks (harakat) that are not written; you may leave out the ones that are written.
6. **Digits as written:** Arabic-Indic `٠١٢٣٤٥٦٧٨٩` if the page uses them, `0–9` if the page uses them. Dates and
   numbers digit by digit as on the page (`١٩٧٢/٧/١٢`). Double-check every number: dates, amounts, ID numbers, plot
   numbers are the most important words of these documents.
7. **Punctuation** as written (`، ؛ ؟ . : ( ) -`). Do not add punctuation that is not there.
8. **Unsure of a word:** write your best reading inside `[? ]`, e.g. `[?الزغير]`, and add a note to `uncertain`.
   **Cannot read at all:** `[...]` (one for each unreadable word if you can count them, else one for the stretch).
   **Never guess silently.**
9. **Crossed-out text:** `[deleted: <text>]` if readable, else `[deleted]`. Text written above the line as a
   correction: put it where it is inserted, inside `[inserted: <text>]`.
10. **Not in `text`:**
    - stamps / seals → field `stamps`;
    - handwritten notes, signatures' names, marginal notes on a typed page → field `handwritten_notes`;
    - Hebrew, Latin or any non-Arabic text → only mention it in `other_scripts`, do not transcribe;
    - signatures, fingerprints, logos without text → nothing.
    On a page that is **all handwritten** (`type` = handwritten), the handwriting goes into `text`.
11. **Printed form + filled-in text** (forms with blanks filled by typewriter or hand): the printed form text and the
    filled-in typed text go into `text` in reading order; handwritten fill-ins go into `handwritten_notes`.
12. **Drafts we may send you:** some pages come with a machine draft (`<id>.draft.txt`). The draft is often wrong.
    Check every word against the image; do not trust it. Pages of the **test set come without a draft** — transcribe
    those from scratch (otherwise the draft's mistakes leak into the reference).

## 3. Quality control

- About **10 % of the pages are transcribed twice**, by two annotators who do not see each other's work. We compare
  them automatically. Target agreement: ≥ 98 % of characters on typed pages, ≥ 95 % on handwritten pages. Pages
  below target go back for a review by a third person.
- We check a random sample of every batch against the image ourselves. A batch with more than 2 % character errors on
  typed pages is returned.
- Report problems (missing page, unreadable scan) in `uncertain`; do not skip a page silently.

## 4. Confidentiality

Pages from the client are confidential: process them only on your own systems, do not upload them to any other
service (including online OCR / AI tools), do not keep them after delivery, do not use them to train your own
models. Public archive pages are marked as such in the batch list; the same working rules apply.

## 5. Pilot

Before a large batch: a **pilot of 10 pages** (typed, mixed, handwritten). We score it, send feedback, and only then
agree on the full batch. Please report the time spent per page in `minutes`.
