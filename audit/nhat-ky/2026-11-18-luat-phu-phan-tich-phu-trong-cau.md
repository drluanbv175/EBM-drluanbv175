# 18/11/2026 — Đã sửa giới hạn còn lại: phân tích phụ viết trong câu của SAP phải vào đặc tả G6

Bổ sung cho `2026-11-18-neo-phu-dinh-tltk-doi-va-mt1-fpc.md`. Tệp đó ghi giới hạn «chưa sửa»; bác sĩ giao «Sửa luôn giới
hạn còn lại giúp tôi». Mã ở PR y khoa drluanbv175/medical-ebm-automation#317 (mục 2b); dữ liệu ở #318.

## Giới hạn

- Luật phủ «SAP ↔ đặc tả G6» chỉ đòi phủ gạch đầu dòng §9 và mục nhãn đậm ở §1/§3/§5/§7.
- Phân tích phụ viết liền trong câu văn thì không bị đòi phủ. Ví dụ BTM §4: «nếu biết khung mẫu thì báo thêm KTC có hiệu
  chỉnh quần thể hữu hạn như một thông tin phụ».
- Vì vậy agent bỏ nhầm `MT1_fpc` mà không có gì đỏ.
- Phủ theo DÒNG cũng không bắt được, vì neo của phân tích chính nằm cùng gạch đầu dòng.

## Đã sửa

- `menh_de_phan_tich_phu` tách SAP (ngoài §9) thành mệnh đề theo «.»/«;».
- Mệnh đề nào mang dấu hiệu phân tích phụ thì phải có cụm neo nằm ngay trong chính mệnh đề đó. Dấu hiệu gồm: «báo thêm»,
  «trình bày thêm», «tính thêm», «ước lượng thêm», «kèm thêm», «chạy thêm», «làm thêm», «thông tin phụ», «phân tích phụ»,
  «phân tích bổ sung».
- Bỏ qua: dấu hiệu bị phủ định, dòng bảng, tiêu đề, khối mã.
- Thiếu cụm neo ⇒ LỖI, cùng mức luật phủ §9.

## Đo 18/11

- 2 SAP thật + 16 SAP giả lập ⇒ đúng 2 mệnh đề, cả hai là phân tích phụ thật (BTM §4 FPC, §5 mô hình biến chia nhóm).
- Đặc tả BTM thiếu `MT1_fpc` ⇒ 2 lỗi; sau #318 (thêm lại `MT1_fpc`, neo §5 cho `DN9_chia_nhom`) ⇒ 0 lỗi.
- C1a và giả lập: 0 lỗi.
- Đột biến 6/6 đỏ. Lượt đầu, phép «bỏ «báo thêm»» sống sót vì câu thử còn chứa «thông tin phụ»; đã thêm ca chỉ có
  «báo thêm».

## Còn lại

Dấu hiệu là danh sách từ cố định. Phân tích phụ diễn đạt khác («đồng thời ước lượng …», «so sánh thêm …») chưa bị bắt.
Khi gặp ca thật thì thêm cụm vào `_TU_PHAN_TICH_PHU`, kèm test.
