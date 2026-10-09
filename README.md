# Nhánh điều khiển server (hộp thư qua GitHub)

| File | Ai ghi | Nội dung |
|---|---|---|
| `trang_thai/STATUS.md` | server (`htr_test/hop_thu.py chay`, tmux `hop_thu`) | mỗi 20 phút: còn sống, GPU, tmux, ngrok, log |
| `KE_HOACH.md` | Claude | kế hoạch + bước đang làm + luật cứng |
| `nhat_ky.md` | Claude | việc đã làm (qua SSH) |
| `lenh/PROMPT.md` | Claude | prompt cho agent (dự phòng khi SSH đứt) |
| `bao_cao/*.md` | agent | báo cáo (agent ghi vào /kaggle/working/hop_thu/bao_cao/<ID>.md) |

## Hướng dẫn cho agent trên server (chỉ khi được giao)
Mỗi 5–20 phút đọc /kaggle/working/hop_thu/PROMPT_MOI.md. Nếu ID chưa làm: làm đúng nội dung, theo LUẬT CỨNG trong
KE_HOACH.md; báo cáo (DÁN nguyên văn log/file, không gõ lại chữ Ả Rập) vào /kaggle/working/hop_thu/bao_cao/<ID>.md —
script hop_thu tự đẩy lên GitHub.
