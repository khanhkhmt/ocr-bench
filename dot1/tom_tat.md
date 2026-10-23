# Đợt 1 — thử không cần huấn luyện

Cập nhật 2026-10-23 06:44 UTC. Luật chọn / luật đạt viết sẵn trong `htr_test/dot1.py` (LUAT) trước khi chạy.

## Bộ test

| bộ | số dòng / trang | dùng để |
|---|---:|---|
| Omar blind_test A | 500 dòng | chọn |
| Omar blind_test B | 500 dòng | xác nhận |
| Muharaf test A | 500 dòng | chọn |
| Muharaf test B | 500 dòng | xác nhận |
| Muharaf người viết lạ A | 500 dòng | chọn |
| Muharaf người viết lạ B | 500 dòng | xác nhận |
| Muharaf test, cả trang | 66 trang | Bước 0 + xác nhận trên cả trang |
| 4 trang mẫu | 113 dòng | cả trang (nhãn của anh) |

## 1. Bộ A — mọi cấu hình đọc dòng (% ký tự đúng / % từ đúng, đã chuẩn hoá)

| cách | Omar blind_test | Muharaf test | Muharaf người viết lạ | **TB ký tự** | hơn ft3 |
|---|---:|---:|---:|---:|---:|
| tran_bau5 | 95.4 / 84.9 | 94.5 / 86.2 | 97.2 / 91.1 | **95.73** | +2.51 |
| tran_bau4 | 95.3 / 84.6 | 94.0 / 84.9 | 97.0 / 90.5 | **95.44** | +2.22 |
| bau5_dong | 94.2 / 81.8 | 93.0 / 82.9 | 96.0 / 87.7 | **94.39** | +1.18 |
| tron34 | 93.6 / 80.6 | 92.9 / 83.1 | 95.8 / 87.8 | **94.12** | +0.90 |
| bau5_tu | 94.1 / 81.6 | 92.5 / 82.4 | 95.6 / 87.3 | **94.06** | +0.85 |
| bau4_dong | 94.2 / 81.8 | 91.8 / 80.3 | 95.4 / 86.2 | **93.79** | +0.58 |
| bau4_tu | 94.1 / 81.7 | 91.7 / 80.5 | 95.1 / 86.1 | **93.62** | +0.40 |
| ft3_s075 | 94.0 / 81.0 | 91.2 / 78.8 | 94.8 / 84.8 | **93.33** | +0.12 |
| ft4 | 92.8 / 78.4 | 92.0 / 80.9 | 95.0 / 86.1 | **93.26** | +0.05 |
| ft3 | 93.4 / 80.0 | 91.5 / 80.0 | 94.7 / 85.1 | **93.21** | +0.00 |
| ft3_s050 | 93.7 / 81.1 | 88.7 / 73.4 | 93.5 / 80.9 | **91.96** | -1.25 |
| ft3_s125 | 92.2 / 76.9 | 89.5 / 76.4 | 92.8 / 80.5 | **91.50** | -1.71 |
| ft1_s050 | 93.4 / 80.1 | 86.9 / 69.2 | 93.3 / 80.7 | **91.19** | -2.02 |
| goc | 93.3 / 79.9 | 79.2 / 55.2 | 88.4 / 67.4 | **86.96** | -6.26 |

`tronAB` = hai adapter cùng bật, mỗi cái ½. `ft3_sNNN` = ft3 ở độ mạnh NNN/100. `bauN_tu` = bầu theo từ (ft3 làm gốc), `bauN_dong` = chọn cả dòng gần các bản khác nhất; bau4 = ft3, ft4, ft1@0,5, gốc; bau5 = bau4 + tron34. `tran_bauN` = mức TRẦN (chọn bản đúng nhất theo nhãn) — chỉ để biết còn bao nhiêu chỗ, không phải cách đọc.

## 2. Bộ B — xác nhận ứng viên `bau5_dong` (chọn ở bộ A: +1.18 điểm so với ft3)

(bộ B chưa đọc xong)

## 3. Bước 0 — tách dòng làm mất bao nhiêu điểm (66 trang Muharaf test, đọc bằng ft3)

| dòng | % ký tự đúng (cả trang, có thứ tự) | % từ có mặt (túi từ, bỏ thứ tự) |
|---|---:|---:|
| cắt theo khung chuẩn của bộ dữ liệu | 82.7 | 65.5 |
| Kraken tự cắt (như sản phẩm) | 63.6 | 50.2 |
| **hụt** | **19.1** | **15.3** |

Kraken lỗi 0 / 66 trang (trang lỗi tính 0 điểm; bỏ các trang đó: chuẩn 82.7 / Kraken 63.6). Dòng chữ Latin / mã lưu trữ / gạch bỏ đã tô màu giấy ở cả hai cách. **Lưu ý:** model tách dòng Muharaf (Zenodo 14295555) học từ chính bộ Muharaf, có thể đã thấy các trang này → hụt thật trên giấy tờ của khách có thể LỚN hơn.

**Kết luận theo luật:** hụt 19.1 điểm → Đợt 2 LÀM #10 (dạy bằng dòng Kraken cắt).

## 4. Bốn trang mẫu — chữ chính theo luật sản phẩm (% ký tự / % từ)

Trang 1, 3, 4 = đánh máy (chữ chính = dots, đọc dòng chỉ kiểm chéo) → cấu hình đọc dòng chỉ đổi trang 2. Cột "chỉ đọc dòng" = mọi khối lấy chữ đọc dòng (để thấy cấu hình nào đọc chữ đánh máy tốt hơn).

| cách | page_1 | page_2 (viết tay) | page_3 | page_4 | chỉ đọc dòng: page_1 / page_3 / page_4 |
|---|---:|---:|---:|---:|---|
| ft3 | 90.3 / 70.1 | 72.2 / 46.5 | 79.0 / 44.0 | 90.9 / 70.9 | 78.8 / 73.6 / 79.9 |
| ft4 | 90.3 / 70.1 | 73.1 / 47.9 | 79.0 / 44.0 | 90.9 / 70.9 | 76.0 / 74.1 / 83.7 |
| ft1_s050 | 90.3 / 70.1 | 68.7 / 41.1 | 79.0 / 44.0 | 90.9 / 70.9 | 77.3 / 76.2 / 85.7 |
| goc | 90.3 / 70.1 | 62.9 / 30.1 | 79.0 / 44.0 | 90.9 / 70.9 | 77.4 / 73.4 / 83.5 |
| tron34 | 90.3 / 70.1 | 73.5 / 50.7 | 79.0 / 44.0 | 90.9 / 70.9 | 78.8 / 74.1 / 78.9 |
| ft3_s075 | 90.3 / 70.1 | 72.0 / 47.2 | 79.0 / 44.0 | 90.9 / 70.9 | 79.1 / 74.9 / 83.7 |
| ft3_s125 | 90.3 / 70.1 | 66.7 / 39.0 | 79.0 / 44.0 | 90.9 / 70.9 | 73.3 / 72.6 / 71.4 |
| ft3_s050 | 90.3 / 70.1 | 70.9 / 44.3 | 79.0 / 44.0 | 90.9 / 70.9 | 77.3 / 76.6 / 86.1 |
| bau4_tu | 90.3 / 70.1 | 72.5 / 45.7 | 79.0 / 44.0 | 90.9 / 70.9 | 78.9 / 74.8 / 83.7 |
| bau4_dong | 90.3 / 70.1 | 71.0 / 44.7 | 79.0 / 44.0 | 90.9 / 70.9 | 78.6 / 76.8 / 84.3 |
| bau5_tu | 90.3 / 70.1 | 73.3 / 48.9 | 79.0 / 44.0 | 90.9 / 70.9 | 79.2 / 74.8 / 82.7 |
| bau5_dong | 90.3 / 70.1 | 74.7 / 51.4 | 79.0 / 44.0 | 90.9 / 70.9 | 78.6 / 75.6 / 83.1 |

Mốc: docs/RESULTS.md của arabic-doc-ocr (lần đo 2026-10-19): 90.3 / 72.2 / 79.0 / 90.9 — dòng ft3 ở trên phải gần các số này (cùng code, cùng model).

## 5. dots đọc lại TỪNG khối chữ đánh máy (#5) — % ký tự / % từ (đã bỏ dấu Markdown ở mọi cột)

| cách | page_1 | page_3 | page_4 | TB ký tự | hơn sản phẩm |
|---|---:|---:|---:|---:|---:|
| sản phẩm (cả trang ×1,5) | 90.3 / 70.1 | 79.0 / 44.0 | 90.9 / 70.9 | 86.73 | — |
| từng khối ×1.5 | 88.3 / 65.8 | 81.6 / 49.5 | 87.1 / 68.6 | 85.68 | -1.05 | (1 khối dùng chữ sản phẩm)
| từng khối ×2.0 | 89.1 / 67.9 | 82.9 / 52.8 | 87.5 / 67.4 | 86.53 | -0.20 |
| từng khối ×3.0 | 88.3 / 62.5 | 81.3 / 49.8 | 89.5 / 66.3 | 86.38 | -0.35 | (1 khối dùng chữ sản phẩm)

**Kết luận theo luật:** tốt nhất ×2.0: -0.20 điểm, trang kém nhất -3.42 → **KHÔNG ĐẠT**. #5 ĐẠT nếu mức phóng tốt nhất (theo trung bình trang 1, 3, 4) hơn sản phẩm ≥ +0,5 điểm ký tự và không trang nào kém quá 0,3 điểm. Chỉ 3 trang và chọn 1 trong 3 mức → ĐẠT vẫn phải xác nhận trên bộ đánh máy khác trước khi đưa vào sản phẩm.

## 5b. Nới khung dòng Kraken (#12) — đọc bằng ft3, cùng dòng Kraken, chỉ đổi khung cắt

| nới thêm (% độ dày dòng) | 66 trang Muharaf: % ký tự | túi từ | hơn 0 % | trang 2 (viết tay): % ký tự / % từ | hơn 0 % |
|---|---:|---:|---:|---:|---:|
| 0 % | 63.6 | 50.2 | — | 72.2 / 46.5 | — |
| 15 % | 65.6 | 54.7 | +2.00 | 74.1 / 49.6 | +1.90 |
| 30 % | 66.7 | 56.7 | +3.13 | 74.9 / 50.7 | +2.69 |
| 50 % | 67.2 | 57.7 | +3.58 | 78.0 / 58.5 | +5.78 |

Mốc: mức 0 % đọc lại trong lần chạy này giống bản đọc Bước 0 ở 100.0 % số dòng (Bước 0: Kraken 63.6, dòng chuẩn 82.7).

**Kết luận theo luật:** tốt nhất nới 50 %: +3.58 điểm ký tự, túi từ +7.49, trang 2 +5.78 → **ĐẠT**. #12 ĐẠT nếu mức nới tốt nhất (theo % ký tự cả trang, 66 trang Muharaf, đọc bằng ft3) hơn mức 0 % (đọc lại cùng lần chạy) ≥ +1,0 điểm VÀ túi từ không kém VÀ trang 2 (viết tay của khách, chữ chính) không kém quá 1,0 điểm → đưa mức đó vào sản phẩm (crop_poly, chờ anh duyệt) và dùng khi cắt dòng Kraken cho #10. Chọn 1 trong 3 mức trên chính 66 trang → mức hơn hơi lạc quan; model tách dòng Muharaf có thể đã thấy các trang này.

## 7. Gợi ý cho Đợt 2 (tự rút theo luật)

- **Độ mạnh:** không mức nào hơn ft3 ≥ 0,2 → không rõ; nhật ký train (CER kiểm tra vẫn giảm ở bước 2000) nghiêng về train lâu hơn.
- **Bầu chọn:** tốt nhất bau5_dong +1.18 điểm so với ft3 → train VÀI bản ft5 khác nhau để bầu.
- **Trộn ft3+ft4:** +0.90 điểm so với ft3 → đưa bước trộn checkpoint vào cách train ft5.
- **Tách dòng (Bước 0):** hụt 19.1 điểm → Đợt 2 LÀM #10 (dạy bằng dòng Kraken cắt).
- **dots từng khối (#5):** ×2.0 -0.20 điểm → KHÔNG ĐẠT → #11 (dòng máy chữ tự sinh) ưu tiên trong Đợt 2.
- **Nới khung dòng (#12):** nới 50 % → +3.58 điểm trên 66 trang, trang 2 +5.78 → ĐẠT → đưa nới 50 % vào sản phẩm (chờ anh duyệt) và cắt dòng Kraken cho #10 bằng mức này.

## Lưu ý

- Số đọc dòng ở đây dùng đúng code đọc của adoc/ (bản chép arabic-doc-ocr) (có sửa mã chữ Ba Tư → Ả Rập), nên có thể lệch nhẹ so với bảng cũ của eval_lines.
- Chữ đánh máy chỉ có 3 trang → kết quả #5 là tín hiệu, chưa phải bằng chứng.
- Mọi luật: `LUAT` trong htr_test/dot1.py.
