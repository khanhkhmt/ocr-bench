# Nghiên cứu song song — cải thiện luồng chính

Luồng chính (người dùng chốt): dots.mocr chia bố cục + đọc khối ĐÁNH MÁY → khối VIẾT TAY: cắt theo khung dots → tách
dòng → model chữ tay đọc từng dòng → ghép DOCX (A sửa được, B giữ bố cục). Tài liệu đích: giấy tờ pháp lý Ả Rập 1970s
(đánh máy + Ruq'ah viết tay, giấy ố, con dấu / chữ ký đè chữ, khối công chứng Hebrew). Ưu tiên: đọc ĐÚNG, không bịa.

## Hàng đợi chủ đề (mỗi lần kiểm tra ~25 phút làm 1 chủ đề)
1. ✅ Tách DÒNG chữ tay trong khối dots (hiện: chiếu ngang — thô) → model / thuật toán tốt hơn?
2. ✅ Phân biệt khối đánh máy vs viết tay (để biết khối nào gửi model chữ tay)
3. ✅ Phát hiện chữ bịa / đổi nghĩa: so khớp nhiều model, điểm tin cậy theo token
4. Giấy cũ màu: tiền xử lý (xám, phóng, lề, làm nét) — kiểm chứng trên Muharaf
5. Fine-tune model chữ tay dùng được thương mại (Ketaba Apache + Omar CC BY + làm cũ ảnh)
6. Con dấu / chữ ký đè chữ: tách lớp, hay để model tự xử lý
7. Khối công chứng Hebrew
8. Ghép kết quả chữ tay vào DOCX A/B

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
