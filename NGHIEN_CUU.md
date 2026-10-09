# Nghiên cứu song song — cải thiện luồng chính

Luồng chính (người dùng chốt): dots.mocr chia bố cục + đọc khối ĐÁNH MÁY → khối VIẾT TAY: cắt theo khung dots → tách
dòng → model chữ tay đọc từng dòng → ghép DOCX (A sửa được, B giữ bố cục). Tài liệu đích: giấy tờ pháp lý Ả Rập 1970s
(đánh máy + Ruq'ah viết tay, giấy ố, con dấu / chữ ký đè chữ, khối công chứng Hebrew). Ưu tiên: đọc ĐÚNG, không bịa.

## Hàng đợi chủ đề (mỗi lần kiểm tra ~25 phút làm 1 chủ đề)
1. ✅ Tách DÒNG chữ tay trong khối dots (hiện: chiếu ngang — thô) → model / thuật toán tốt hơn?
2. ✅ Phân biệt khối đánh máy vs viết tay (để biết khối nào gửi model chữ tay)
3. ✅ Phát hiện chữ bịa / đổi nghĩa: so khớp nhiều model, điểm tin cậy theo token
4. [cần GPU] Giấy cũ màu: tiền xử lý (xám, phóng, lề, làm nét) — kiểm chứng trên Muharaf
5. ✅ Fine-tune model chữ tay dùng được thương mại (Ketaba Apache + Omar CC BY + làm cũ ảnh)
6. ✅ Con dấu / chữ ký đè chữ: tách lớp, hay để model tự xử lý
7. ✅ Khối công chứng Hebrew
8. ✅ Ghép kết quả chữ tay vào DOCX A/B
9. Tách dòng bằng Kraken + model Muharaf trong htr_test/lines.py (cắt theo đa giác) — làm code, thử trên máy
10. Gắn danh_dau vào web / DOCX A: khối viết tay = model chữ tay + dots đọc song song → tô vàng chỗ lệch
11. [cần GPU] Ứng viên THƯƠNG MẠI chạy sẵn: Qari-OCR 0.4 (Qwen3-VL-4B, Apache) trên Omar + Muharaf
12. [cần GPU] dots trên 30 dòng Hebrew tự tạo (so với Kraken 99,6%); chồng dấu giả → đo lọc màu (chủ đề 6)

## Kết quả

### 2026-10-09 13:45 ICT — Chủ đề 1: tách dòng chữ tay
- **Kraken + model tách dòng Muharaf** (Zenodo 14295555, CC BY 4.0, 5 MB, `muharaf_seg_best.mlmodel`) — huấn luyện trên
  1.600 trang Muharaf (thư từ, giấy tờ pháp lý viết tay, giấy cũ). Thử trên MÁY NGƯỜI DÙNG (CPU, ~34 s/trang) với trang
  viết tay giấy kẻ của khách: 34 dòng, mỗi dòng thân văn bản đúng 1 vùng, đường bao ôm sát dòng cong/nghiêng; bỏ qua chữ ký.
- Kraken mặc định (blla): 41 dòng — thân văn bản tốt, thêm mẩu chữ ký / chữ rời.
- Chiếu ngang (web đang dùng): 33 dải — bám ĐƯỜNG KẺ GIẤY, nhiều dải cắt ngang chữ → kém nhất.
- Khác: YOLOv5 tách dòng cho bản thảo Ả Rập (ACM 2025, doi 10.1145/3744243); Athar Segmentation v4 (Kraken, RASAM,
  giấy phép "other"); tuỳ chọn `-r` (bỏ đường kẻ ngang) của Kraken giúp với chữ Ả Rập.
- **Đề xuất áp dụng**: tách dòng bằng Kraken + model Muharaf trên CẢ TRANG, gán dòng vào khối dots theo phần chồng lấn;
  cắt ảnh dòng theo ĐA GIÁC (nền ngoài đa giác tô trắng) thay vì hình chữ nhật → bớt chữ dòng trên/dưới lọt vào.
  Chưa có số đo (không có nhãn tách dòng cho trang của khách) — đo gián tiếp bằng % đúng của model đọc sau khi tách.
- Nguồn: https://zenodo.org/records/14295555 · https://kraken.re/main/advanced/segmentation.html ·
  https://huggingface.co/factlogic/athar-segmentation-v4 · https://dl.acm.org/doi/10.1145/3744243

### 2026-10-09 14:12 ICT — Chủ đề 2: phân biệt khối đánh máy / viết tay
- Không model bố cục sẵn nào có nhãn "viết tay": PP-DocLayout (23 loại, có "seal" nhưng không có handwriting),
  DocLayout-YOLO, Surya đều không; dots cũng không (11 loại).
- Tài liệu: phân biệt in/tay ở mức khối bằng bag-of-visual-words + SVM (Zagoris 2013); CNN nhận cả chữ viết (Ả Rập/Latin)
  lẫn kiểu (in/tay) — JATIT Vol.102 No.10 (KHATT, IAM); chưa thấy công trình 2024–2025 cho KHỐI tài liệu Ả Rập.
- Thử nhanh trên máy (numpy, 7 đặc trưng hình học: độ lệch chân dòng, đỉnh chiếu ngang, độ đều nét, dao động đỉnh chữ…;
  hồi quy logistic). Huấn luyện: 300 dòng tay Omar + 300 dòng IN tự tạo (phông nhóm A, nền ố, mờ, nhiễu, JPEG).
  Thử: chữ in phông CHƯA thấy → nhận đúng 98,3%; dòng tay Muharaf (giấy màu, người viết khác) → chỉ 65,0%.
  ⇒ đặc trưng hình học KHÔNG đủ tin cậy với nét / giấy lạ.
- **Đề xuất áp dụng** (xếp theo chi phí):
  (a) không cần phân loại: đọc MỌI khối chữ bằng dots, khối nào dots đọc kém tự tin (xác suất token thấp) hoặc dots và
      model chữ tay lệch nhau nhiều → gửi model chữ tay / đánh dấu cần người xem (gộp với chủ đề 3);
  (b) bộ phân loại học sâu nhỏ trên ẢNH DÒNG: tay = Omar + Muharaf + KHATT, in = chữ in tự tạo với phông kiểu máy chữ
      (Amiri Typewriter…) + bộ chữ in công khai (medyas 500k, CC BY-SA); kiểm định chéo theo NGUỒN (giữ hẳn 1 nguồn ra).
- Nguồn: http://www.jatit.org/volumes/Vol102No10/3Vol102No10.pdf ·
  https://www.primaresearch.org/www/assets/papers/PR2013_Zagoris_BagOfVisualWords.pdf · https://arxiv.org/pdf/2503.17213

### 2026-10-09 14:50 ICT — Chủ đề 3: phát hiện chữ bịa / đọc sai bằng SO KHỚP 2 model
- Thử trên 240 dòng Omar blind_test mà cả Baseer và Ketaba đã đọc (có nhãn thật):
  - Hai model GẦN NHƯ TRÙNG (lệch ≤ 3% ký tự, 87 dòng = 36%): Baseer đúng TB **98,7%**; khi lệch: 91,2%.
  - Đánh dấu dòng có lệch > 5%: bắt **100%** dòng Baseer sai > 10% (48/48), đánh dấu 50% số dòng (40% là sai thật).
    Lệch > 12%: bắt 67%, đánh dấu 17% số dòng (78% là sai thật).
  - Mức TỪ: đánh dấu từ Baseer đọc mà Ketaba không có → bắt **78% từ sai**, 65% từ bị đánh dấu là sai thật,
    chỉ đánh dấu 22% tổng số từ.
- Tài liệu cùng hướng: ROVER / bỏ phiếu nhiều hệ (2 đội NAKBA dùng bỏ phiếu ký tự/từ); đọc nhiều biến thể ảnh + căn
  chỉnh Needleman-Wunsch → độ tin cậy (arXiv 2509.09722); đầu dò trạng thái ẩn để từ chối (2511.19806); huấn luyện
  model biết từ chối khi ảnh mờ (Seeing is Believing, NeurIPS 2025, 2506.20168); bài Uruguay (2607.24077) đề xuất
  kết hợp nhiều hệ vì VLM thay tên/ngày mà CER không thấy.
- **Đề xuất áp dụng vào luồng chính** (rẻ, có số chứng minh): mỗi dòng chữ tay đọc bằng 2 model ĐỘC LẬP (vd. Ketaba +
  dots, hoặc Ketaba + Baseer khi được phép); dòng trùng → tin; từ lệch → TÔ VÀNG trong DOCX A (người kiểm chỉ cần xem
  ~1/5 số từ, bắt ~4/5 lỗi). Cần đo lại với cặp có dots khi benchmark dots xong (dots khác họ model → có thể bắt lỗi tốt hơn).
  Chưa thử: độ tự tin theo token (xác suất trong generate) — để chủ đề sau.

### 2026-10-09 15:25 ICT — Chủ đề 5: model chữ tay dùng được THƯƠNG MẠI (chủ đề 4 cần GPU — để khi server sống lại)
- ⚠ **Giấy phép model nền**: Qwen2.5-VL-**3B**-Instruct = **"qwen-research"** (không thương mại). sherif, Ketaba (tự ghi
  Apache-2.0) và Baseer-Nakba đều xây trên Qwen2.5-VL-3B → nhiều khả năng vẫn chịu giấy phép gốc (cần đọc kỹ
  https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/blob/main/LICENSE; không phải tư vấn pháp lý).
  Nền Apache-2.0: Qwen3-VL-2B / 4B, Qwen2.5-VL-7B, PaddleOCR-VL, Qari-OCR 0.4 (Qwen3-VL-4B + LoRA). dots.ocr: giấy phép riêng.
- Bằng chứng làm được: một đội NAKBA fine-tune **Qwen3-VL-4B** trên Omar: CER 8,59% (val) / 11,0% (blind) — gần Baseer
  (7,9%) / Ketaba (9,4%). Công thức đội thắng (Misraj): bước 1 chỉ decoder trên Muharaf (ảnh xám) → bước 2 mở cả encoder,
  LR riêng (encoder 9e-6, decoder 1e-4) → trộn SLERP 2 checkpoint; tăng cường ảnh: méo đàn hồi, ăn mòn, đổi tương phản, nhiễu.
- Dữ liệu dùng thương mại: Omar (CC BY 4.0, ~18k dòng) + dòng tự tạo (phông Ả Rập + làm cũ: nền ố, mờ, JPEG, con dấu giả)
  + làm cũ chính ảnh Omar (Augraphy). KHÔNG dùng được: Muharaf (NC-SA), Baseer (NC-SA); KHATT: điều khoản gốc chỉ nghiên cứu.
- T4: QLoRA 4-bit + gradient checkpointing chạy được với model 3–4B (tiền lệ: math-ocr / MJSynth trên Qwen2.5-VL-3B);
  T4 không có bf16 → fp16 + adapter fp32. Colab hay ngắt → lưu checkpoint thường xuyên (lên HF/GitHub, đẩy như benchmark).
- **Đề xuất áp dụng**: (1) báo khách / người dùng rủi ro giấy phép của Ketaba–Baseer; (2) ứng viên thương mại: fine-tune
  **Qwen3-VL-4B** (hoặc thử trước Qari-OCR 0.4 sẵn có, cùng nền) trên Omar + dữ liệu làm cũ; đánh giá bằng đúng benchmark
  hiện có (Omar blind_test + Muharaf test). Model CTC nhỏ (Kraken / PP-OCRv5 rec) huấn luyện trên Omar làm "người đọc
  thứ hai" độc lập cho so khớp (chủ đề 3) — không bịa câu trôi chảy, chạy CPU được.
- Nguồn: Qwen LICENSE (link trên) · https://aclanthology.org/2026.nakbanlp-1.7/ · https://huggingface.co/Misraj/Baseer__Nakba
  · https://huggingface.co/ericmrib/math-ocr · https://huggingface.co/NAMAA-Space/Qari-OCR-0.4.0-VL-4B-Instruct

### 2026-10-09 15:45 ICT — Chủ đề 6: con dấu / chữ ký / vân tay đè lên chữ
- Xoá dấu kiểu cổ điển (không cần huấn luyện): chiếu màu điểm ảnh lên thành phần chính trong HSV + ngưỡng Otsu tách dấu
  khỏi chữ, rồi đóng hình thái học nối lại nét bị đứt (Springer, "Colored Rubber Stamp Removal").
- Học sâu: U-Net hay để lại vệt dấu; GAN (SERGAN, UNet bất đối xứng + PatchGAN — ACM 2025); khuếch tán (diffusion) cho kết
  quả sạch nhất (PSNR 44,7 — ScienceDirect 2024; bản 2026 đề xuất thước đo EA-RMSE). Khó nhất: dấu MÀU NHẠT, gần màu mực.
  DocRevive (arXiv 2604.10077): khôi phục chữ bị che, có lớp thử nghiệm "Stamp" (dấu bán trong suốt).
- Chữ ký đè chữ in: SignaTR6K (ICCV 2023) — 200 mẫu giấy tờ PHÁP LÝ thật, gán nhãn từng điểm ảnh (chữ ký / chữ tay / chữ in,
  CHỒNG nhau được); tải qua Microsoft Forms (forms.office.com/r/2a5RDg7cAY) — cần người dùng điền.
- Lưu ý từ chủ đề trước: VLM bị HẠI khi sửa ảnh mạnh (nhị phân, khử nhiễu) → xoá dấu phải có kiểm chứng bằng CER.
- **Đề xuất áp dụng**:
  - Khối ĐÁNH MÁY (mực đen) bị dấu / vân tay MÀU (tím, xanh) đè: lọc theo độ bão hoà màu (giữ điểm ảnh tối, ít màu) TRƯỚC khi
    dots đọc — tách màu dễ vì khác hẳn màu mực.
  - Khối VIẾT TAY bút bi XANH: KHÔNG lọc màu (dấu xanh trùng màu mực → xoá luôn chữ); dựa vào so khớp 2 model (chủ đề 3) để
    đánh dấu chỗ đáng ngờ.
  - Kiểm chứng khi server sống lại: chồng dấu / vân tay giả (màu, bán trong suốt) lên dòng chữ in tự tạo và dòng Omar →
    đo CER của dots / model chữ tay khi có và không có bước lọc màu.
- Nguồn: https://link.springer.com/content/pdf/10.1007/978-3-642-45062-4_75.pdf ·
  https://www.sciencedirect.com/science/article/abs/pii/S0045790624006657 · https://dl.acm.org/doi/10.1145/3772128.3772162 ·
  https://arxiv.org/html/2604.10077v2 · https://arxiv.org/abs/2307.07887

### 2026-10-09 16:15 ICT — Chủ đề 7: khối công chứng tiếng Hebrew
- Chưa nguồn nào công bố điểm tiếng Hebrew của dots.ocr (bài dots có XDocParse 126 ngôn ngữ nhưng không thấy bảng theo
  ngôn ngữ) hay của các VLM OCR mới; GlotOCR Bench: model OCR vẫn yếu ngoài vài hệ chữ phổ biến.
- **Kraken + kraken-ppocrv6-medium** (Apache 2.0, 64 MB, 44 ngôn ngữ, Hebrew học từ HTR-School-Vienna/2025-hebrew):
  thử trên MÁY (CPU, ~3,6 s/dòng) với 30 dòng Hebrew IN tự tạo (câu kiểu công chứng TỰ VIẾT, 4 phông Noto/Liberation,
  nền ố, mờ, nhiễu, JPEG): **đúng 99,6% ký tự, 28/30 dòng đúng hoàn toàn** (lỗi: ו/מ, ר/ד).
  ⚠ Ở chế độ đọc dòng rời (`ocr -s`) Kraken trả chữ theo THỨ TỰ HIỂN THỊ (ngược) → phải đảo lại (dòng thuần Hebrew;
  dòng lẫn số cần thuật toán bidi).
- **Đề xuất áp dụng**: khối nào dots trả về có chữ Hebrew (dải Unicode U+0590–U+05FF) hoặc nằm trong vùng con dấu →
  đọc thêm bằng Kraken ppocrv6, so khớp với dots (chủ đề 3) → chỗ lệch tô vàng. Nội dung công chứng rất khuôn mẫu
  ("אימות חתימה", "נוטריון", "מאשר", số tiền, ngày) → có thể sửa theo từ điển cụm cố định.
  Kiểm chứng khi server sống lại: dots trên cùng 30 dòng Hebrew tự tạo (so với Kraken 99,6%).
- Nguồn: https://huggingface.co/small-models-for-glam/kraken-ppocrv6-medium · https://arxiv.org/pdf/2512.02498 ·
  https://arxiv.org/pdf/2604.12978

### 2026-10-09 16:40 ICT — Chủ đề 8: đưa kết quả chữ tay + chữ đáng ngờ vào DOCX
- Làm code: `htr_test/danh_dau.py` (commit 3b17057, có test): so khớp từ giữa bộ đọc chính và phụ (bỏ qua hamza/alef,
  ى/ي, ة/ه, dấu nguyên âm, dấu câu) → từ lệch TÔ VÀNG + mỗi cụm lệch một CHÚ THÍCH Word "<bộ phụ> đọc: …"
  (python-docx 1.2 add_comment; Word và Google Docs đều đọc được tô màu + chú thích).
- Đo trên 240 dòng Omar (Baseer chính, Ketaba phụ): tô vàng 22% số từ, bắt 80% từ sai, 64% từ tô vàng là sai thật.
  Ví dụ "لا" thêm vào làm đổi nghĩa → bị tô vàng, chú thích "Ketaba đọc: (không có)".
- DOCX mẫu (dữ liệu công khai Omar) đã gửi người dùng.
- **Đề xuất áp dụng**: DOCX A — khối viết tay = chữ model chữ tay, tô vàng chỗ lệch với bộ đọc thứ hai; DOCX B — giữ
  nguyên bố cục, cùng tô vàng (chú thích có thể bỏ để không lệch bố cục). Gắn vào web: chủ đề 10.
