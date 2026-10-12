# Dòng chữ viết tay Omar Al-Saleh — blind_test (500 dòng)

Cập nhật: 2026-10-12 10:32 UTC — XONG tất cả

| Model | đã chấm | **đúng ký tự** | **đúng từ** | CER gốc | WER gốc | CER chuẩn hoá | WER chuẩn hoá | CER TB theo dòng (chuẩn hoá) | độ dài TB | dòng dài ≥1,5× | dòng ngắn ≤0,5× |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ketaba | 240/500 | **93.5%** | **79.0%** | 8.9% | 29.7% | 6.5% | 21.0% | 5.9% | 1.00 | 0 | 0 |
| baseer_ft1_s050 | 500/500 | **93.4%** | **79.9%** | 8.8% | 28.4% | 6.6% | 20.1% | 6.7% | 1.00 | 1 | 0 |
| baseer | 500/500 | **93.3%** | **79.8%** | 8.8% | 28.4% | 6.7% | 20.2% | 7.0% | 1.00 | 1 | 1 |
| baseer_ft1_s075 | 500/500 | **92.8%** | **78.6%** | 9.3% | 29.5% | 7.2% | 21.4% | 7.3% | 1.00 | 1 | 0 |
| baseer_ft2 | 500/500 | **92.3%** | **77.6%** | 9.9% | 30.8% | 7.7% | 22.4% | 8.2% | 1.00 | 3 | 0 |
| baseer_ft1 | 500/500 | **92.0%** | **76.7%** | 10.2% | 31.3% | 8.0% | 23.3% | 8.3% | 1.00 | 2 | 0 |

đúng ký tự = 100% − CER chuẩn hoá (cả tập, tính theo tổng ký tự); đúng từ = 100% − WER chuẩn hoá. Từng dòng: chi_tiet.csv (mở bằng Excel) và xem_ket_qua.html (có ảnh).

Tham chiếu công bố (cả 2.671 dòng, CER/WER theo corpus): Baseer-Nakba 7,9% / 24,4% · Ketaba 9,4% / 30,0% · baseline Qwen3-VL-8B LoRA 36,8% / 69,1%.
