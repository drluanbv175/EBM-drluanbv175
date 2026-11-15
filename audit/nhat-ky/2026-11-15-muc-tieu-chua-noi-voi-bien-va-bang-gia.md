# 15/11/2026 — Mục tiêu chưa nối với biến, phân tích SAP và bảng giả (giai đoạn 3)

**Bác sĩ (nguyên văn):** «Tiếp tục các giai đoạn còn lại … Hãy đảm bảo sự đồng bộ xuyên suốt và chính xác nhất».

## Phát hiện (kiểm tay C1a, BTM)

| Chỗ hở | Đề tài | Chi tiết |
|---|---|---|
| Chưa có ma trận mục tiêu → biến | C1a, BTM | `ma_tran_muc_tieu_bien kiem` báo MT-01 đỏ ở cả hai: mục tiêu G1 chưa được nối với biến, câu hỏi, phân tích SAP. |
| Kiểu biến | C1a | `ma_ban_kham` (đơn vị gom cụm) là trường REDCap `text`, chỉ nhận kiểu `van_ban`. |
| SAP gọi gộp tên biến | C1a | SAP ghi «`A_Mean`…`F_Mean`» nên máy không thấy `B_Mean`…`E_Mean`. |
| SAP chưa gọi tên biến | BTM | `nhom_g`, `nhom_a`, `thoi_gian_mac_dtd_5` chưa được SAP gọi đúng tên. |
| Bộ kiểm báo oan | BTM | MT-08 đọc biến nguồn dạng lặp `uacr_k_ngay` như một tên trường, báo «biến không có». |
| Nhãn mục tiêu ghi cứng | BTM | Khung SAP trong A2 của G1 ghi «Mục tiêu 1» và «Mục tiêu 2 — nếu có», trong khi BTM có MT1–MT2 mô tả và MT3 mới là phân tích yếu tố. |
| Không có luật bảng giả | mọi đề tài | Không luật nào đòi mỗi mục tiêu có đầu ra định trước. SAP do `run_g4_auto` sinh không gắn bảng nào với mục tiêu nào. |
| PII báo oan | BTM | Dựng lại G1 thì R2 bắt câu đếm «Số hồ sơ phải MỞ sẽ lớn hơn cỡ mẫu» (giải trình G3 chủ nhiệm đã xác nhận) là PII, khiến G1 BLOCKED. |

## Cách vá

**Repo y khoa:**
- **Ma trận cho hai đề tài**, dựng từ những gì đã chốt, không thêm biến:
  - C1a: 37 dòng, 2 mục tiêu;
  - BTM: 22 dòng, 3 mục tiêu;
  - cả hai ĐẠT; còn MT-08 vì công thức biến phái sinh chờ thống kê viên/PI duyệt.
- **SAP:** C1a 1.5 (chưa ký lại) và BTM (chưa ký) gọi đúng tên từng biến.
- **`ma_tran_muc_tieu_bien`:**
  - MT-08 nhận quy ước lặp «_k»;
  - **MT-11:** mục SAP mà ma trận trỏ tới phải có thật; mỗi mục tiêu phải có bảng/hình giả gắn nhãn «Mục tiêu k»/«MTk», trong SAP §11 hoặc phần Dự kiến kết quả của đề cương nộp.
- **`run_g4_auto`:** §11 tự thêm «Bảng MTk» cho mỗi mục tiêu; ô kết quả là `[CẦN KẾT QUẢ THẬT]`.
- **`run_g1_auto`:**
  - nhãn §4/§5 của khung SAP lấy theo đúng mục tiêu G1;
  - đã dựng lại G1 BTM: A2 nay trỏ sang SAP G4; G1 vẫn PASS_G1_CONFIRMED; G0–G4 không đổi.
- **`pii_van_ban.nhan_so_ho_so`:** «số hồ sơ» chỉ là PII khi kèm giá trị (`:`/`#` rồi giá trị, hoặc mã ≥ 4 chữ số, không tính năm). G0 và G1 dùng chung luật này.
- **`nhat_quan_xuyen_cong`:** thêm trục `ma_tran_muc_tieu` (G1 · G3 · G4 · G10), nên câu «Kết luận» phủ cả giai đoạn mục tiêu.

**Repo gốc:** dạy `bien-so-nghien-cuu`, `thiet-ke-nghien-cuu`, `dieu-phoi-g1`, `dieu-phoi-g4`.

## Kiểm hồi quy

- `tests/test_muc_tieu_20261115.py`: 8 ca.
- `tests/test_pii_so_ho_so_20261115.py`: 3 ca.
- 9/9 đột biến đỏ.
- Lượt đầu, MT-11 làm 59 test G4–G6 đỏ: SAP sinh từ khuôn không gắn nhãn mục tiêu, nên G3-AUTO-19 chuyển REVIEW và kéo đổ dây chuyền. Đã vá gốc ở khuôn `run_g4_auto`, không nới luật. Sau đó 146 tệp test liên quan (2446 ca) đạt.

## Còn mở (việc của người)

| Đề tài | Việc | Vai |
|---|---|---|
| C1a | Duyệt 10 công thức biến phái sinh | thống kê viên/PI |
| BTM | Duyệt 16 công thức biến phái sinh | thống kê viên/PI |
| C1a | Ký lại G4 cho SAP 1.5 | thống kê viên |
