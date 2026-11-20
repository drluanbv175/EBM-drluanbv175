# 20/11/2026 — Chuẩn trình bày văn bản nộp thành chốt máy cho mọi đề tài (K11, K9 «mỗi mức một dòng»)

**Yêu cầu bác sĩ:** «Đề cương nghiên cứu hãy đảm bảo từng câu, từng chữ, ngữ nghĩa phải chuẩn, từng bảng từng đồ thị phải
đúng chuẩn, đúng định dạng» rồi «hoàn thiện cho hệ thống chứ không riêng 2 đề tài C1a và BTM».

**Gặp khi soát tay hai đề cương nộp (BTM, C1a) — đều đã ĐẠT K1–K10:**
- Số kiểu máy (0.1; 100000; 2026-01-01), ngoặc kép thẳng/«», «vs», chữ IN HOA nhấn mạnh («ước lượng CAO»), loại biến
  «Định danh/thứ bậc», tên bảng hai ngoặc liền «(biến phụ thuộc của MT3) (Mục tiêu 3)».
- Bảng chữ viết tắt: SD và ĐLC cùng nghĩa; mục không dùng; chữ đang dùng chưa giải thích (BVQY175, KTV, CV…); không theo vần.
- C1a: bảng dồn nhiều mức vào một ô («Giới | Nam; Nữ | —»); Biểu đồ 5.2 lấy tham chiếu BHYT ngược Bảng 5.4 và thiếu 2 biến
  của mô hình (bộ sinh cắt im lặng ở 16 nhãn); tự đánh giá sức khỏe tách mức trong khi SAP đưa dạng số; Bảng 5.5 thiếu 3
  phân tích độ nhạy của SAP §9; cột gán đa trị đặt làm chính trong khi SAP lấy ca đủ dữ liệu làm chính.
- BTM: «Tuổi mỗi đơn vị» trong khi SAP «mỗi 10 năm»; cột trung vị toàn «—» ở bảng tỷ lệ; tổng quan nói tìm PubMed không có
  hướng dẫn nhưng Bảng 3.1 liệt kê hướng dẫn.
- Bộ sinh đề cương (dùng cho đề tài mới): «» và ngày ISO trong khuôn câu; bảng viết tắt lấy cả chữ trong danh mục tài liệu
  (tên tác giả «HA») — 8 đề cương giả lập đủ 8 thiết kế đều dính.

**Đã làm:** K11 (repo y khoa `kiem_de_cuong_nop_hoi_dong.py`, nối cả `kiem_ban_thao_tap_chi.py`); K9 thêm «mỗi mức một
dòng»; bộ sinh biểu bảng và bộ sinh đề cương tự ra văn bản đạt chuẩn (test cho 7 thiết kế); đối chiếu biến hiểu số kiểu
Việt Nam; dạy `viet-ban-thao`, `thiet-ke-nghien-cuu`, `dieu-phoi-g10`.

**Giới hạn còn lại (máy chưa đo, agent tự soát):** bảng đa biến/forest trùng biến và tham chiếu với SAP khi chương 5 soạn
tay; cột phân tích chính về dữ liệu thiếu (đặc tả G6 chưa có khoá nói phân tích nào là chính); bảng độ nhạy đủ mục SAP
(đặc tả G6 của C1a thiếu 3 mục so với SAP §9 — chờ thống kê viên duyệt bổ sung).
