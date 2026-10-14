# Dòng chữ viết tay Muharaf — nhóm tài liệu GIỮ RIÊNG (người viết lạ với ft3+) — giu_lai (500 dòng)

Cập nhật: 2026-10-14 03:56 UTC — đang chấm baseer 480/500

| Model | đã chấm | **đúng ký tự** | **đúng từ** | CER gốc | WER gốc | CER chuẩn hoá | WER chuẩn hoá | CER TB theo dòng (chuẩn hoá) | độ dài TB | dòng dài ≥1,5× | dòng ngắn ≤0,5× |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseer_ft4 | 500/500 | **95.0%** | **86.0%** | 5.7% | 16.1% | 5.0% | 14.0% | 6.0% | 1.01 | 3 | 1 |
| baseer_ft3 | 500/500 | **94.7%** | **85.0%** | 6.0% | 17.6% | 5.3% | 15.0% | 5.6% | 1.00 | 1 | 1 |
| baseer_ft1_s050 | 224/500 | **94.2%** | **83.1%** | 7.7% | 25.0% | 5.8% | 16.9% | 7.1% | 1.00 | 1 | 2 |
| baseer | 480/500 | **88.3%** | **67.2%** | 14.3% | 42.5% | 11.7% | 32.8% | 12.9% | 1.00 | 2 | 3 |

đúng ký tự = 100% − CER chuẩn hoá (cả tập, tính theo tổng ký tự); đúng từ = 100% − WER chuẩn hoá. Từng dòng: chi_tiet.csv (mở bằng Excel) và xem_ket_qua.html (có ảnh).
