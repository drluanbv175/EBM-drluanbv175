# 15/11/2026 — Giả lập trọn vòng G5→G10 + nhập SPSS/R: lỗi hệ thống và khoảng trống «hỏi lại điều đã chốt»

## Bối cảnh
Bác sĩ giao: «Tất cả giả lập hãy nhập vào Spss và R giúp tôi, cho tôi một đề tài hoàn chỉnh để tôi kiểm tra và cùng xác
thực». Tiếp nối `2026-11-15-gia-lap-8-thiet-ke-dau-chuoi.md` (G0–G4).

Bộ giả lập `medical-ebm-automation/tools/gia_lap_tron_vong.py` nay đi trọn G0→G10. Đề tài thuần tập tổng hợp (PPI kéo
dài → gãy xương 3 năm, N = 4396), mọi cổng cứng ký bằng khoá GIẢ của pytest. Lượt sạch cuối đi một mạch trong 169 giây:

| Cổng | Trạng thái |
|---|---|
| G2 | PASS_G2_APPROVED |
| G3 | PASS_G3_CONFIRMED |
| G4 | PASS_G4_SAP_LOCKED |
| G5 | PASS_G5_DATA_LOCKED (nhập kép Excel ↔ SPSS bắt 4/4 lỗi cài) |
| G6 | PASS_G6_SCRIPTS_CONFIRMED (5 phân tích theo đặc tả SAP; kiểm chéo SPSS + R đều KHỚP; RR hiệu chỉnh 1,33, KTC 95% 1,11–1,60) |
| G7 | PASS_G7_CONFIRMED |
| G8 | PASS_G8_REVIEW_RECORDED |
| G9 | PASS_G9_PUBLICATION_INTEGRITY_LOCKED |
| G10 | PASS_G10_RELEASE_PACKAGE_LOCKED |

## Lỗi hệ thống đo được và đã vá (repo y khoa, PR drluanbv175/medical-ebm-automation#287)
1. **`run_g6_auto`:** dò từ khoá ghi «⚠️ Không tự phát hiện exposure/outcome → dùng tên dự phòng» TRƯỚC khi SAP §5/ma trận
   thay đúng biến. Dòng cũ nằm lại trong A7 ⇒ G6-AUTO-07 đỏ oan, thống kê viên phải sửa tay một dòng nhật ký.
   Sửa: biến đã giải thành tên có trong từ điển ⇒ thay bằng dòng ghi nguồn.
2. **`dien_giai_ket_qua`:** engine (`run_stats_analysis`, cũng là đường của `chay_sap_g6`) ghi kết quả ở GỐC thư mục đề
   tài; cổng G6 đọc gốc nhưng bản diễn giải chỉ nhận `06_ket_qua/`. Sửa: nhận đúng khuôn tên tệp kết quả của engine ở gốc;
   tệp tự gõ vẫn chặn.
3. **Lời hướng dẫn khuôn chứa «[CẦN...]» bị chính cổng đếm là ô chưa điền:**
   - dòng «Trạng thái» của DMP (G5-AUTO-03);
   - khối cảnh báo đầu gói A10 (G9-AUTO-05).

   Cùng họ với câu CRF của G5 đã vá đầu ngày. Sửa: đổi chữ, không còn ký hiệu ô trống.

Kiểm:
- Test ở `tests/test_gia_lap_tron_vong_sua_20261115.py`.
- Phép đột biến: 3 bản sửa đều làm test đỏ đúng ca rồi phục hồi xanh.
- Hồi quy nhóm G5/G6/G9/diễn giải/giả lập: 811 đạt, 8 bỏ qua.

## Khoảng trống đo được, CHƯA vá (cần bác sĩ quyết)
Số đo trên lượt sạch; ô được phân loại trước khi điền:

| Cổng | Ô hỏi lại điều đã chốt | Ô hỏi lặp |
|---|---|---|
| G2 | 2 | 11 |
| G4 | 1 | 2 |
| G5 | 0 | 7 |
| G7 | 14 | 3 |
| G9 | 0 | 53 |

- **G7:** bộ sinh bản thảo hỏi lại mục tiêu, cơ sở, tiêu chí nhận/loại, phơi nhiễm, kết cục, phần mềm (SAP §10). Không có
  lệnh gỡ ~40 dòng khung bản nháp (biểu ngữ DRAFT, khối «> …», bảng ước tính số từ) — tác giả phải gỡ tay.
- **G10:** StudySpec chỉ đọc `gate_params.G0/G1` ⇒ PI phải khai lại 21 khoá cấp cao của study_meta đã chốt ở nơi khác:
  - SAP đã khoá: §4 phân tích chính, §6 dữ liệu thiếu, §11 khung bảng;
  - G2: miễn ICF, phiên bản đề cương, không bắt buộc đăng ký;
  - G5: DMP, khử định danh, kiểm soát chất lượng;
  - G7: tác giả;
  - ma trận: phơi nhiễm, hiệp biến, nguồn đo, tên biến.

  Sửa StudySpec phải chạy test đầu–cuối G10 đủ 8 thiết kế.
- **G8:** phải gõ lại đúng tên kết cục chính đã chốt (G8-AUTO-05 so chuỗi con với SAP).
- **Engine G6:** bảng Poisson ghi «PR — tỷ lệ hiện mắc» cả với thuần tập (nên là RR). `chay_sap_g6` chưa có đường cho
  phân tích chính của chẩn đoán, dự báo, gộp, định tính.
- **Luật độ tươi:** G3 đọc G2 ⇒ hồ sơ G2 sinh lại sau G3 (để kèm phiếu thu thập) làm G3/G4 «cũ», G10 chặn. Bộ giả lập
  chạy lại G3 → G4 sau G2 như đề tài thật.

## Sự cố của chính bộ giả lập (đã sửa trong đợt)
Bản đầu bước A12 gọi `check_citations --study` NGOÀI biến pytest để có cấu hình nguồn thật (dưới pytest `app.config`
không nạp cấu hình ⇒ nguồn giả). Hệ quả: biên nhận A12 của **thư mục giả lập** (`~/.ebm-worktrees/gia-lap-tron-vong/`) bị
ký bằng khoá HMAC thật của máy, ở hai lượt chạy. Không ghi gì vào `exports/` thật; khoá không bị in ra.

Sửa: tách hai bước — tra mạng không `--study` (không ký), rồi ghi biên nhận bằng đúng hàm của `check_citations` trong môi
trường khoá giả. Lượt sạch cuối dùng hoàn toàn khoá giả; thư mục của hai lượt cũ đã đổi tên `_luot-truoc_*`.

## Bài học
- Chạy trọn vòng mới lộ lỗi ở chỗ nối giữa các cổng: kết quả G6 ↔ bản diễn giải, A12 ↔ manifest G9, G2 ↔ độ tươi G3.
  Chạy từng cổng riêng không thấy.
- Bước nào cần cấu hình thật VÀ ký thì phải tách tra cứu khỏi ghi có chữ ký. Chạy cả bước ngoài pytest là dùng khoá
  thật.
- Khiếm khuyết lớn nhất còn lại không phải cổng chặn sai mà là HỎI LẠI ĐIỀU ĐÃ CHỐT ở cổng sau (G7, G9, G10).

Cần bác sĩ kiểm chứng.
