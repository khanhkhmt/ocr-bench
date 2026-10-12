# postcorrect — kết quả đo: LLM sửa lỗi sau dots.mocr có giảm lỗi thật không?

> **Trạng thái: phần dev đã xong; phần holdout (chấm một lần) và kiểm tra quy mô model (Qwen3-14B) đang chạy** — mục nào ghi «(chờ số)» sẽ
> được điền khi xong. Mọi con số đo trên máy của dự án (2× Tesla T4), bằng bộ dữ liệu công khai; **không có dữ liệu thật của người dùng
> và không có API ngoài**. Mã nguồn: [postcorrect/](../postcorrect/), hướng dẫn: [postcorrect/README.md](../postcorrect/README.md).

## 0. Tóm tắt

1. **Ở mức nhiễu này, LLM chạy cục bộ (≤ 14 tỉ tham số, 4-bit) sửa lỗi bằng văn bản đơn thuần gần như không giảm được CER.** Trên 24 trang dev
   (CER của dots 45,7%), cấu hình tốt nhất giảm **0,13 điểm CER** (ALLaM-7B, chỉ nhận sửa khi ≥ 2/3 lượt chạy đồng ý), trong khi một bộ sửa
   *hoàn hảo* bị giới hạn 2 ký tự sẽ giảm **3,10 điểm** — LLM đạt ~4% trần.
2. **Có chốt chặn thì không làm hại**: mọi cấu hình có chốt chặn đều cho 0–4 từ đúng bị đổi sai trên ~560 từ đúng của 24 trang (≤ 0,7%); **không có chốt chặn thì ước lượng
   dao động rất rộng** ([−1,4; +0,2] điểm) và chỉ trông "tốt hơn" nhờ cắt bớt một trang dots bịa văn bản lặp.
3. **Nút thắt không phải LLM kiểm chứng** (khi cho sẵn chữ đúng nó nhận đúng 41% với 1,3% nhận nhầm, precision 97%) **mà là thiếu bằng chứng để biết
   chữ đúng là gì**: 58% từ OCR sai xa (> 2 ký tự), 30% trang bị dots *bịa* văn bản kiểu Qur'an đầy tashkeel, và phần lỗi "sai ít" phần lớn cần
   nhìn ảnh để quyết định (`الرابعة` / `السابعة` / `التاسعة` chỉ khác nét).
4. **Khuyến nghị:** không triển khai LLM hậu xử lý như "tự sửa" trên đầu ra dots ở mức nhiễu này. Làm theo thứ tự: (a) **cải thiện bước đọc ảnh**
   (đây mới là đòn bẩy lớn: 15 trang dev có CER > 50%), (b) **kiểm chứng ứng viên bằng ảnh qua một model đọc ảnh KHÁC dots** (HTR theo dòng chấm xác suất của từng ứng viên
   trên ảnh cắt của dòng) thay vì chỉ bằng ngôn ngữ, (c) nếu vẫn dùng LLM thì chỉ ở chế độ **gợi ý có người duyệt** (JSON `edits` đã có chỉ số từ) và dùng
   **cờ chất lượng rẻ** (tashkeel > 10%, lặp vòng) để loại trang đọc hỏng ra trước khi nhờ LLM.

## 1. Câu hỏi và cách trả lời

Thêm một bước LLM sau dots.mocr để (a) sửa lỗi OCR chữ viết tay Ả Rập, (b) chỉ ra từ nghi lỗi. Với tài liệu cổ, **sửa sai nguy hiểm hơn bỏ sót**,
nên câu hỏi không phải "LLM sửa được bao nhiêu" mà là "**sau khi trừ đi số từ đúng bị sửa nhầm, lỗi có giảm không**, và giảm ở mức nhiễu OCR nào".

## 2. Thiết lập

| Mục | Giá trị |
|---|---|
| OCR | dots.mocr (3,04 tỉ tham số), cấu hình web demo của repo, ảnh 4,6–5,0 MP (6 MP hết VRAM T4); ~2,5–3 phút/trang/card |
| Dữ liệu | Muharaf công khai (thư viết tay Levant 1950–60: tiếng địa phương + chính tả cũ): 100 trang, mỗi tài liệu ≤ 1 trang, **50 dev** (chọn prompt / ngưỡng) + **50 holdout** (chấm một lần). So sánh LLM trên **24 trang dev đầu** (cùng một tập cho mọi cấu hình) |
| LLM (cục bộ, 4-bit nf4) | Qwen3-8B (8,19 tỉ tham số, 6,0 GiB), ALLaM-7B-Instruct-preview (7,00 tỉ, 4,4 GiB); kiểm tra quy mô: Qwen3-14B (14,77 tỉ) |
| Chiến lược | **A** viết lại chunk (≈700 ký tự) rồi diff · **B** chỉ khoanh từ lỗi (JSON `{word, fix}`) · **C** như A nhưng chỉ được đổi từ đã bị đánh dấu nghi lỗi (NLL của LM) · **D** ứng viên từ từ điển Wikipedia (200 nghìn từ, cách ≤ 2 ký tự) + LM chỉ chấm NLL, không sinh chữ |
| Prompt | *bảo thủ* ("không chắc thì giữ nguyên") và *quyết đoán* (nói rõ dots sai nhiều, sửa mọi từ rõ ràng là đọc sai); zero-shot, ví dụ tổng hợp, hoặc **ví dụ THẬT trong miền** (2 cặp OCR → bản chỉ sửa chỗ sai-gần-đúng, lấy từ dev trang 25–50, tức NGOÀI tập đang chấm) |
| Chốt chặn | chỉ nhận sửa nhỏ, cục bộ (≤ 2 ký tự khác, tách / gộp từ); không đụng số / Latin / chữ đơn; không đưa chữ ngoài bộ Ả Rập chuẩn vào; **chặn sửa chỉ khác quy ước** (hamza, `ى/ي`, `ة/ه`); bỏ cả chunk nếu lệch > 10% số từ, > 35% số từ bị sửa, hoặc **tashkeel > 5%** (dots đang bịa) |
| Chuẩn hoá khi chấm | **strict** (mặc định; không gộp أ/إ/ا, ى/ي vì đáp án là phiên âm TRUNG THÀNH: `ان` ≠ `أن`) và lenient (gộp). Số trong báo cáo là strict, trừ khi ghi khác |

### Cách đo
- **CER / WER** trước và sau (chuẩn hoá của `ocrbench`), khoảng tin cậy 95% bootstrap theo **trang**.
- **Mỗi sửa** chấm bằng độ giảm khoảng cách ký tự tới đoạn đáp án tương ứng: `fixed` (thành đúng hẳn), `improved`, `harm` (từ vốn ĐÚNG bị đổi sai), `worse`, `neutral`.
  **Tỉ lệ sửa nhầm** = số từ đúng bị đổi / số từ đúng của OCR. **Recall trong tầm với** = số từ sai-gần-đúng được sửa đúng / số từ sai-gần-đúng.
- **Trần** (`postcorrect oracle`): CER sau khi sửa HOÀN HẢO mọi từ sai trong tầm chốt chặn. Mọi con số của LLM phải đọc cạnh trần này.

## 3. OCR nền (dev, 50 trang, 7.266 từ đáp án)

- **CER micro 41,8%**; theo trang: trung vị 40,3%, p10 22,4%, p90 63,3%; **không trang nào dưới 15%** (16 trang 15–30%, 19 trang 30–50%, 15 trang ≥ 50%). 2/50 trang bị model lặp vòng.
- Trong 7.603 từ OCR: **20,0% đúng, 15,8% "sai-gần-đúng"** (≤ 2 ký tự so với đáp án — loại lỗi chốt chặn cho phép sửa), **58,2% sai xa**.
- **30% trang (15/50) bị dots bịa** văn bản kiểu Qur'an với tashkeel dày (> 10% ký tự; đáp án thật hiếm khi vượt 15%). Dots **tự tin hơn** ở nhóm này (log-prob trung bình −0,22
  so với −0,35 ở nhóm đọc thật) nên độ tin cậy của dots *không* phát hiện được; tashkeel dày thì có (CER trang trung vị 47,1% so với 34,7%).
- Kiểu lỗi của 1.202 từ sai-gần-đúng: 45,7% cần 2 ký tự; 22,8% thay một chữ bằng chữ khác nhóm (`حجب→يجب`, `المجلد→المجلس`); 17,6% OCR thiếu một chữ
  (`القرا→القرار`, `يروت→بيروت`); 6,4% nhầm nét/chấm cổ điển (`تكون→يكون`); 4,1% thừa chữ; 3,5% chỉ khác hamza/alef (`أن→ان`, khác biệt quy ước hơn là đọc sai).
- **Trần** (bộ sửa hoàn hảo dưới chốt chặn): 50 trang dev, giới hạn 1 / 2 / 3 / 4 ký tự → CER 41,8% → 40,2 / **37,8** / 35,6 / 33,3% (giảm 1,6 / **4,05** / 6,2 / 8,5 điểm);
  24 trang dev đầu (CER 45,7%) → giảm 1,3 / **3,1** / 4,7 / 6,6 điểm. Nhóm đọc thật (35 trang, tashkeel ≤ 10%): CER 38,5% → 33,9% với giới hạn 2 ký tự.
- **Tín hiệu khoanh từ sai-gần-đúng** (AUROC phân biệt với từ đúng; tỉ lệ nền 44,2%): độ ngần ngừ dots (log-prob) 0,745 · entropy dots 0,748 · NLL tổng của LM (Qwen3-8B) 0,740 ·
  NLL token-đắt-nhất 0,622 · **ngoài từ điển (OOV)**: chỉ 7,2% từ đúng là OOV so với 54,2% từ sai-gần-đúng. Phương án top-3 của chính dots chứa từ đúng ở chỉ 6,7% từ sai-gần-đúng.

## 4. Kết quả sửa lỗi trên dev (24 trang đầu; CER OCR 45,7%, WER 92,4%; từ OCR sai trong tầm với: 17,4%)

ΔCER tính bằng điểm phần trăm (âm = tốt), KTC 95% bootstrap theo trang. «Sửa nhầm» = số từ đúng bị đổi sai. Trần của bộ sửa hoàn hảo trên tập này: **−3,10**.

| Cấu hình | ΔCER [KTC 95%] | số sửa | precision | sửa nhầm | sửa đúng hẳn | recall trong tầm | giây GPU/trang |
|---|---|---|---|---|---|---|---|
| Qwen3-8B · A bảo thủ (zero-shot) | −0,01 [−0,02; +0,00] | 3 | 0,67 | 0 | 1 | 0,2% | 29,5 |
| Qwen3-8B · A quyết đoán | +0,02 [−0,01; +0,04] | 12 | 0,33 | 0 | 1 | 0,2% | 24,4 |
| Qwen3-8B · C (NLL) quyết đoán | −0,02 [−0,08; +0,02] | 22 | 0,32 | 1 | 3 | 0,7% | 24,7 |
| Qwen3-8B · B quyết đoán | +0,04 [+0,00; +0,08] | 16 | 0,06 | 1 | 0 | 0,0% | 13,3 |
| Qwen3-8B · A + ví dụ thật | −0,05 [−0,19; +0,05] | 44 | 0,34 | 0 | 5 | 1,2% | 27,3 |
| Qwen3-8B · C + ví dụ thật | +0,01 [−0,06; +0,09] | 31 | 0,26 | 3 | 4 | 1,0% | 25,4 |
| Qwen3-8B · B + ví dụ thật | **+0,10 [+0,05; +0,18]** (xấu đi) | 52 | 0,21 | 1 | 4 | 1,0% | 19,6 |
| **ALLaM-7B · A + ví dụ thật** | −0,07 [−0,21; +0,02] | 63 | 0,48 | 0 | 18 | 4,5% | 12,7 |
| ALLaM-7B · C + ví dụ thật | −0,01 [−0,09; +0,08] | 66 | 0,36 | 2 | 7 | 1,7% | 14,8 |
| ALLaM-7B · B + ví dụ thật | +0,02 [−0,11; +0,13] | 80 | 0,34 | 4 | 11 | 2,7% | 17,4 |
| **ALLaM-7B · đồng thuận ≥ 2/3 (A, B, C)** | **−0,13 [−0,29; −0,03]** | 20 | **0,80** | 0 | 9 | 2,2% | ≈ 45 (A+B+C) |
| ALLaM-7B · đồng thuận 3/3 | −0,01 [−0,04; +0,00] | 2 | 1,00 | 0 | 2 | 0,5% | ≈ 45 |
| Hai model · đồng thuận ≥ 2/6 | −0,13 [−0,30; −0,01] | 40 | 0,55 | 0 | 11 | 2,7% | ≈ 90 |
| Qwen3-8B · D (từ điển + LM chấm), τ = 3 nat, lề 0,5 | **+0,40 [+0,16; +0,70]** (xấu đi) | 217 | 0,18 | 2 | 11 | 2,7% | 7,7 |
| Qwen3-8B · D, τ = 3, lề 2 | +0,05 [−0,07; +0,18] | 80 | 0,20 | 0 | 2 | 0,5% | 7,7 |
| (không chốt chặn) A + ví dụ thật | −0,38 [−1,42; +0,16] | 84 | 0,24 | 3 | 6 | 1,5% | 27,3 |

Đọc bảng:
- **Không cấu hình nào đến gần trần.** Cấu hình tốt nhất (−0,13) là kết quả duy nhất có KTC không chứa 0, nhưng nó **được chọn sau khi thử nhiều biến thể trên dev** (nguy cơ chọn lọc) nên chỉ coi là giả thuyết, kiểm lại ở holdout (mục 5).
- **ALLaM-7B (chuyên tiếng Ả Rập) tốt hơn Qwen3-8B ở cùng cấu hình**: sửa đúng 18 từ so với 5, precision 0,48 so với 0,34, nhanh gấp đôi (12,7 so với 27,3 giây GPU/trang): tokenizer gọn hơn cho tiếng Ả Rập (2,64 so với 2,32 ký tự/token; ~325 so với ~490 token ra mỗi trang) và kiến trúc Llama đơn giản.
- **Ví dụ thật trong miền** làm model hoạt động nhiều hơn 3–4 lần (12 → 44 sửa) mà không tăng sửa nhầm; **prompt "quyết đoán"** thì ít khác biệt.
- **B (khoanh từ lỗi) kém A**: khi bị buộc liệt kê, model đề xuất nhiều sửa sai nghĩa (`المغوض→المغول`, đáp án `المفوض`).
- **Đồng thuận** là cách duy nhất tăng precision mà không mất hết recall (0,48 → 0,80), đúng kỳ vọng của self-consistency.

### Ví dụ thật
- Sửa **đúng** (Qwen3-8B / ALLaM, ví dụ thật): `والمعاهمات→والمعاهدات`, `بتوجيسها→بتوجيهها`, `المفتررة→المفترسة`, `اللبانية→اللبنانية`, `المجلد→المجلس`, `كتامبي→كتابي`, và dọn chữ lạ: `جهדكم→جهدكم` (Hebrew lọt vào), `الترکية→التركية` (kaf Ba Tư).
- Sửa **sai**: `المغوض→المغول` (đáp án `المفوض`), `الكتير→الكثير` (đáp án `السكرتير`), `القوائين→القوائم` (đáp án `القوانين`), và từ đúng bị đổi: `اقتصادي→الاقتصادي`, `الثلوج→الثلج`. Mô hình đoán một từ *hợp lý* chứ không phải từ *đúng*.
- Không có chốt chặn, LLM còn **chuẩn hoá quy ước** (`ان→أن`, `الى→إلى`, `العزنه→العزنة`) dù prompt cấm, và **bịa tashkeel / văn Qur'an** ở trang dots bịa; đó là lý do các luật tương ứng được thêm vào chốt chặn.

## 5. Kết quả cuối trên holdout (50 trang, chấm một lần; cấu hình đóng băng từ dev) — (chờ số)

## 6. Vì sao không hiệu quả: các phép chẩn đoán

| Phép đo | Kết quả | Kết luận |
|---|---|---|
| **Trần** sửa hoàn hảo ≤ 2 ký tự | −3,10 điểm (24 trang), −4,05 (50 trang) | Ngay cả hoàn hảo cũng chỉ cải thiện vài điểm: 58% từ sai xa |
| **LM có nhận ra chữ đúng khi được cho sẵn?** (`lm-prefer`, Qwen3-8B, 300 từ + 300 đối chứng) | thích bản có chữ đúng ở 55,7% từ sai-gần-đúng; ở τ = 3 nat: nhận đúng **40,7%**, nhận nhầm **1,3%**, precision **96,8%**; thích từ đúng gốc hơn bản bị làm nhiễu ở 96,7% | LM *kiểm chứng* tốt, nhưng *không đề xuất* được ứng viên đúng |
| **Ứng viên từ từ điển** (Wikipedia 200 nghìn từ) | chữ đáp án có trong từ điển 81,7%; trong 2 ký tự: 71,5%; ứng viên trung vị chạm trần 200/từ; xếp theo (khoảng cách, tần suất): top-1 14,6%, top-5 31,0% | Quá nhiều ứng viên gần nhau → cần bằng chứng ảnh để chọn |
| **D phân rã** (24 trang, 402 từ sai-gần-đúng) | chỉ 85 (21%) được chọn làm từ nghi lỗi; 51 (12,7% tổng) có chữ đúng trong 20 ứng viên; LM xếp đúng đầu 11/51 = 21,6%; 70% từ nghi lỗi là lỗi sai xa | Trần của D ≈ −0,5 điểm ngay cả khi chọn hoàn hảo; thực tế +0,4 |
| **Chốt chặn** (quét từng luật, A + ví dụ thật) | bỏ riêng từng luật: ΔCER −0,03…−0,07 (không đổi); bỏ hết: −0,38 [−1,42; +0,16] | "Cải thiện" khi bỏ hết đến từ **một** trang dots bịa lặp (`muharaf_0004`: 1.516 → 1.179 ký tự), không phải sửa lỗi |

## 7. Tài nguyên và độ trễ

| Thành phần | VRAM đo trên T4 | Thời gian |
|---|---|---|
| dots.mocr (OCR) | ~14,3 GiB đỉnh (hết một card 15 GiB) | ~150–180 giây/trang (trung vị 153; tối đa 290) |
| Qwen3-8B nf4 | 6,0 GiB sau nạp, đỉnh 6,2–7,0 GiB (batch 1–8) | 24–27 giây/trang (A) |
| ALLaM-7B nf4 | 4,4 GiB sau nạp, đỉnh 4,7–6,3 GiB | 12,7 (A) · 14,8 (C) · 17,4 (B) giây/trang; ~1.300–1.600 token vào + ~325 token ra mỗi lượt |
| Qwen3-14B nf4 | (chờ số) | (chờ số) |

- Một card (≥ 15 GiB): chạy **tuần tự** — OCR xong, giải phóng dots, rồi mới nạp LLM; đỉnh ~14,3 GiB. Giữ cả hai trong VRAM cùng lúc cần ~21 GiB (ước tính). Hai card: dots ở card này, LLM ở card kia, hoặc mỗi card một bản.
- Chi phí cục bộ: LLM thêm ~13–45 giây GPU/trang (khoảng 8–30% thời gian OCR); không có chi phí API. Để ước lượng nếu sau này dùng API: ~1.300–1.900 token vào và ~320–500 token ra mỗi trang cho mỗi lượt.
- Độ trễ LLM không phải nút cổ chai: **OCR chiếm ~80–95% thời gian** của cả pipeline.

## 8. Khuyến nghị và việc tiếp theo

**Kết luận:** với đầu ra dots ở mức nhiễu này (CER ~40%), LLM hậu xử lý **chưa đủ dùng** để tự sửa. Chốt chặn + đồng thuận biến nó thành *an toàn* (không làm hại) nhưng *gần như vô hiệu* (≈ 4% trần). Cần **bằng chứng thị giác** hoặc **fine-tune** chứ không phải LLM lớn hơn.

**Ba việc tiếp theo (theo thứ tự ưu tiên):**
1. **Nâng chất lượng đọc ảnh trước khi nhờ LLM.** Thử các OCR khác đã có trong benchmark của repo (Qari, sherif_handwriting, kraken cho chữ viết tay), đọc lại theo từng khối cắt ở độ phân giải cao, và/hoặc đồng thuận nhiều lượt đọc. Mỗi điểm CER giảm ở bước này lớn hơn toàn bộ những gì LLM hậu xử lý đạt được ở đây (−0,13).
2. **Kiểm chứng ứng viên bằng ảnh qua MỘT MODEL ĐỌC ẢNH KHÁC dots.** LLM (hoặc từ điển) đề xuất ứng viên, rồi một model HTR theo dòng (Baseer, Qari, HATFormer… có trong benchmark của repo) chấm xác suất của từng ứng viên trên ảnh cắt của dòng; chỉ nhận khi cả LM lẫn ảnh đồng ý, giữ chốt chặn hiện có. Chẩn đoán ở mục 6 cho thấy nút thắt là thiếu bằng chứng, và đây là cách thêm đúng bằng chứng đó. **Không dùng chính dots để chấm**: dots đã giải mã tham lam nên bản OCR chính là chữ nó ưa nhất (top-3 phương án của nó chứa chữ đúng ở chỉ 6,7% từ sai-gần-đúng), chấm lại chỉ lặp lại lựa chọn ấy. Chưa đo trong báo cáo này.
3. **Fine-tune nhỏ (QLoRA) trên cặp (đầu ra dots, phiên âm) của chính loại tài liệu**, nếu có vài trăm trang có phiên âm: dạy mô hình kiểu lỗi của dots và từ vựng pháp lý cổ. Ví dụ few-shot thật đã cho dấu hiệu theo hướng này (số sửa tăng 3–4 lần, không tăng sửa nhầm), dù mức giảm CER còn nhỏ. Khung đánh giá, chốt chặn và dữ liệu cặp đã sẵn sàng; **chưa làm** vì ngoài phạm vi giai đoạn này.

**Nếu vẫn muốn dùng LLM ngay:** dùng ở chế độ *gợi ý có người duyệt* (JSON `{index, from, to}` đã có), chỉ trên trang có tashkeel ≤ 10% và không lặp vòng, với ALLaM-7B đồng thuận ≥ 2/3 (precision 0,80 trên dev); loại hẳn chiến lược B và D.

## 9. Hạn chế
- Muharaf là thư cá nhân thế kỷ 20, tiếng địa phương, **không phải** văn bản đất đai cổ; nhiễu OCR cao hơn nhiều so với tài liệu in. Phải kiểm lại trên mẫu thật có phiên âm.
- So sánh LLM trên **24 trang dev** (≈ 2.950 từ) nên khoảng tin cậy rộng; cấu hình tốt nhất được chọn sau nhiều lần thử (chưa hiệu chỉnh đa so sánh) → cần holdout.
- Đáp án là phiên âm của tình nguyện viên, có thể sai sót; chuẩn hoá lenient được báo song song để bù khác biệt hamza / alef.
- Chỉ thử LLM text-only ≤ 14 tỉ tham số 4-bit, zero-shot / 2 ví dụ. Chưa thử API đóng (ngoài phạm vi: dữ liệu có thể nhạy cảm), VLM kiểm chứng ảnh, hay fine-tune.
- Muharaf gốc CC BY-NC-SA 4.0 (bản trên HF ghi MIT): chỉ dùng nghiên cứu, không phân phối lại. Giấy phép dots.mocr §5.2 hạn chế xử lý tài liệu có dữ liệu cá nhân nhạy cảm.
