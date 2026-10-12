# postcorrect — kết quả đo: LLM sửa lỗi sau dots.mocr có giảm lỗi thật không?

> **Trạng thái: ĐANG LÀM.** Các mục đánh dấu «(chờ số)» sẽ được điền khi các lượt chạy xong. Mọi con số trong tài liệu này
> đo trên máy của dự án (2× Tesla T4), bằng bộ dữ liệu công khai; không có dữ liệu thật của người dùng và không có API ngoài.

## 1. Câu hỏi và cách trả lời

Thêm một bước LLM sau dots.mocr để (a) sửa lỗi OCR chữ viết tay Ả Rập, (b) chỉ ra từ nghi lỗi. Với tài liệu cổ, **sửa sai nguy hiểm
hơn bỏ sót**, nên câu hỏi không phải "LLM sửa được bao nhiêu" mà là "**sau khi trừ đi số từ đúng bị sửa nhầm, lỗi có giảm không**,
và giảm ở mức nhiễu OCR nào".

## 2. Thiết lập

| Mục | Giá trị |
|---|---|
| OCR | dots.mocr (3,04 tỉ tham số), cấu hình web demo của repo, ảnh 4,6–5,0 MP (6 MP hết VRAM T4); ~2,5 phút/trang/card |
| Dữ liệu | Muharaf công khai (thư viết tay Levant 1950–60, tiếng địa phương + chính tả cũ): 100 trang, mỗi tài liệu ≤ 1 trang, **50 dev** (chọn prompt / ngưỡng) + **50 holdout** (chấm một lần). KHATT-paragraph (24 đoạn) làm điểm nhiễu thấp hơn (chờ số) |
| LLM (cục bộ, 4-bit nf4) | Qwen3-8B (8,19 tỉ tham số, 6,0 GiB), ALLaM-7B-Instruct-preview (7,00 tỉ, 4,4 GiB); (tuỳ chọn) Qwen3-14B (14,77 tỉ) |
| Chiến lược | **A** viết lại chunk (≈700 ký tự) với ràng buộc "sửa tối thiểu" rồi diff · **B** chỉ khoanh từ lỗi (JSON `{word, fix}`) · **C** như A nhưng chỉ được đổi các từ đã bị đánh dấu nghi lỗi (bằng NLL của LM / độ ngần ngừ của dots) |
| Chốt chặn | chỉ nhận sửa nhỏ, cục bộ (≤ 2 ký tự khác, tách / gộp từ), không đụng số / Latin / chữ đơn, không đưa chữ ngoài bộ Ả Rập chuẩn vào, bỏ cả chunk nếu lệch > 10% số từ hoặc > 35% số từ bị sửa |
| Chuẩn hoá khi chấm | **strict** (mặc định; không gộp أ/إ/ا, ى/ي vì đó là lỗi cần sửa; đáp án là phiên âm TRUNG THÀNH nên `ان` ≠ `أن`) và lenient (gộp) |

### Cách đo
- **CER / WER** trước và sau (chuẩn hoá của `ocrbench`), khoảng tin cậy 95% bootstrap theo **trang**.
- **Mỗi sửa** được chấm bằng độ giảm khoảng cách ký tự tới đoạn đáp án tương ứng: `fixed` (thành đúng hẳn), `improved`, `harm` (từ vốn
  ĐÚNG bị đổi sai), `worse`, `neutral`. **Tỉ lệ sửa nhầm** = số từ đúng bị đổi / số từ đúng của OCR.
- **Tầm với**: số từ OCR sai mà chốt chặn *có thể* sửa (≤ 2 ký tự khác đáp án). Một bộ sửa **hoàn hảo** dưới chốt chặn đó cho **trần** giảm CER
  (lệnh `postcorrect oracle`); mọi lượt chạy phải được đặt cạnh trần này.

## 3. OCR nền (dev, 50 trang, 7.266 từ đáp án)

- **CER micro 41,8%**; theo trang: trung vị 40,3%, p10 22,4%, p90 63,3%; **không trang nào dưới 15%** (16 trang 15–30%, 19 trang 30–50%, 15 trang ≥ 50%). 2/50 trang bị model lặp vòng (tự dừng, tự sửa phần cắt).
- Trong 7.603 từ OCR: **20,0% đúng, 15,8% "sai-gần-đúng"** (≤ 2 ký tự so với đáp án — loại lỗi chốt chặn cho phép sửa), **58,2% sai xa**.
- Kiểu lỗi của 1.202 từ sai-gần-đúng: 45,7% cần 2 ký tự; 22,8% thay một chữ bằng chữ khác nhóm (`حجب→يجب`, `المجلد→المجلس`); 17,6% OCR thiếu một chữ
  (`القرا→القرار`, `يروت→بيروت`); 6,4% nhầm nét/chấm cổ điển (`تكون→يكون`); 4,1% thừa chữ; 3,5% chỉ khác hamza/alef (`أن→ان`, khác biệt quy ước hơn là đọc sai).
- **Trần** (bộ sửa hoàn hảo dưới chốt chặn, dev): giới hạn 1 / 2 / 3 / 4 ký tự → CER 41,8% → 40,2 / **37,8** / 35,6 / 33,3% (giảm 1,6 / **4,05** / 6,2 / 8,5 điểm).
- **Tín hiệu khoanh từ sai-gần-đúng** (AUROC phân biệt với từ đúng; tỉ lệ nền 44,2%): độ ngần ngừ dots (log-prob) 0,745 · entropy dots 0,748 · NLL tổng của LM (Qwen3-8B) 0,740 ·
  NLL token-đắt-nhất 0,622. Phương án top-3 của chính dots chứa từ đúng ở chỉ 6,7% từ sai-gần-đúng → bỏ hướng "chọn lại trong phương án của dots".

## 4. Kết quả sửa lỗi trên dev (chờ số)

## 5. Kết quả cuối trên holdout (chờ số)

## 6. Tài nguyên và độ trễ

| Thành phần | VRAM đo trên T4 |
|---|---|
| dots.mocr | ~14,3 GiB đỉnh (hết một card 15 GiB) |
| Qwen3-8B nf4 | 6,0 GiB sau nạp, đỉnh 6,2–7,0 GiB (batch 1–8) |
| ALLaM-7B nf4 | 4,4 GiB sau nạp, đỉnh 4,7–6,3 GiB |

Một card (≥ 15 GiB): chạy **tuần tự** — OCR xong, giải phóng dots, rồi mới nạp LLM; đỉnh ~14,3 GiB. Giữ cả hai trong VRAM cùng lúc cần ~21 GiB (ước tính). Độ trễ LLM (chờ số).

## 7. Khuyến nghị và việc tiếp theo (chờ số)

## 8. Hạn chế
- Muharaf là thư cá nhân thế kỷ 20, tiếng địa phương, **không phải** văn bản đất đai cổ; nhiễu OCR cao hơn nhiều so với tài liệu in. Phải kiểm lại trên mẫu thật có phiên âm.
- Đáp án là phiên âm của tình nguyện viên, có thể sai sót; chuẩn hoá lenient được báo song song để bù khác biệt hamza / alef.
- Mẫu nhỏ (50 + 50 trang): khoảng tin cậy rộng; chọn cấu hình trên dev, holdout chỉ chấm một lần cho vài cấu hình.
- Muharaf gốc CC BY-NC-SA 4.0 (bản trên HF ghi MIT): chỉ dùng nghiên cứu, không phân phối lại. Giấy phép dots.mocr §5.2 hạn chế xử lý tài liệu có dữ liệu cá nhân nhạy cảm.
