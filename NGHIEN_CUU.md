# Nghiên cứu song song — cải thiện luồng chính

Luồng chính (người dùng chốt): dots.mocr chia bố cục + đọc khối ĐÁNH MÁY → khối VIẾT TAY: cắt theo khung dots → tách
dòng → model chữ tay đọc từng dòng → ghép DOCX (A sửa được, B giữ bố cục). Tài liệu đích: giấy tờ pháp lý Ả Rập 1970s
(đánh máy + Ruq'ah viết tay, giấy ố, con dấu / chữ ký đè chữ, khối công chứng Hebrew). Ưu tiên: đọc ĐÚNG, không bịa.

## Hàng đợi chủ đề (mỗi lần kiểm tra ~25 phút làm 1 chủ đề)
1. Tách DÒNG chữ tay trong khối dots (hiện: chiếu ngang — thô) → model / thuật toán tốt hơn?
2. Phân biệt khối đánh máy vs viết tay (để biết khối nào gửi model chữ tay)
3. Phát hiện chữ bịa / đổi nghĩa: so khớp nhiều model, điểm tin cậy theo token
4. Giấy cũ màu: tiền xử lý (xám, phóng, lề, làm nét) — kiểm chứng trên Muharaf
5. Fine-tune model chữ tay dùng được thương mại (Ketaba Apache + Omar CC BY + làm cũ ảnh)
6. Con dấu / chữ ký đè chữ: tách lớp, hay để model tự xử lý
7. Khối công chứng Hebrew
8. Ghép kết quả chữ tay vào DOCX A/B

## Kết quả
