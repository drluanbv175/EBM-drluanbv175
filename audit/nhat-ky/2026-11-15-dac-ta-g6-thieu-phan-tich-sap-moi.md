# 15/11/2026 — Đặc tả phân tích G6 cũ và thiếu các phân tích SAP mới bổ sung (giai đoạn 7, độ sẵn sàng)

**Bác sĩ (nguyên văn):** «Tiếp tục giai đoạn tiếp theo» — giai đoạn 7 (phân tích số liệu) trong chương trình «Hãy đảm bảo sự đồng bộ xuyên suốt và chính xác nhất». Hai đề tài CHƯA có dữ liệu ⇒ giai đoạn này chỉ kiểm được ĐỘ SẴN SÀNG: SAP → đặc tả máy đọc G6 → lệnh chạy.

## Phát hiện (kiểm tay C1a, BTM)

| Chỗ hở | Đề tài | Chi tiết |
|---|---|---|
| Đặc tả soạn trên SAP cũ | C1a, BTM | `sha256_sap` ≠ SAP hiện tại (SAP đã sửa ở giai đoạn 1–5) ⇒ `chay_sap_g6 chay` sẽ từ chối. Chỉ lộ khi có người chạy `kiem`; không trục nào đo. |
| Đặc tả THIẾU phân tích SAP mới bổ sung | C1a | Thiếu cả ba mục mà SAP 1.5 vừa thêm: báo cáo đáp ứng và so sánh người từ chối (§3), đặc tính đo lường (Cronbach/ω, EFA/CFA; §3), phân tích thăm dò định trước vai trò trung gian của kỳ vọng (§5). |
| Đặc tả THIẾU phân tích SAP mới bổ sung | BTM | Thiếu phần so sánh nhóm bị loại vì chỉ có 1 lượt khám với mẫu nghiên cứu (§1, sửa nháp 3). |
| Không có mối nối mục ↔ SAP | mọi đề tài | Đặc tả chỉ ghi `sap_muc` («§9») và mô tả. Thông báo «SHA khác» không nói đặc tả thiếu phân tích nào hay trỏ vào phân tích SAP đã bỏ. |

## Cách vá

**Repo y khoa:**
- **`chay_sap_g6.kiem_phu_sap`** (gọi trong `kiem_dac_ta`): kiểm đặc tả ↔ SAP HAI CHIỀU.
  - Mỗi mục khai `sap_neo` là cụm chữ nguyên văn trong SAP; cụm không còn trong SAP ⇒ lỗi.
  - Mọi gạch đầu dòng cấp 1 của §9, và mọi mục nhãn đậm là phân tích ở §1/§3/§5/§7 (trừ mục «KHÔNG CÓ»), phải có ít nhất một neo; thiếu ⇒ lỗi.
  - Mục chưa neo ⇒ cảnh báo.
- **Trục mới `dac_ta_phan_tich` của `nhat_quan_xuyen_cong`** (G4·G6·G10).
- **Dữ liệu:** đồng bộ lại đặc tả của hai đề tài theo SAP hiện tại (chưa duyệt; agent không ghi `nguoi_duyet`).
  - C1a: 14 → 17 mục; thêm đáp ứng, đo lường, thăm dò kỳ vọng, đều ghi «chưa tự động» kèm lý do (sổ từ chối ngoài bộ dữ liệu; R psych/lavaan; SAP §5 còn chờ thống kê viên chọn phương pháp).
  - BTM: 26 → 27 mục; thêm so sánh nhóm 1 lượt khám.
  - Neo mọi mục; cập nhật `sha256_sap`; giữ thụt lề tệp gốc nên diff chỉ có thay đổi thật.
  - `chay_sap_g6 kiem`: 0 lỗi; còn 1 cảnh báo «chưa duyệt».

**Repo gốc:** dạy `phan-tich-thong-ke`, `thiet-ke-nghien-cuu`, `dieu-phoi-g6`, `dieu-phoi-g4`.

## Kiểm hồi quy

- `tests/test_phan_tich_20261115.py`: 8 ca; 8/8 đột biến đỏ đúng ca.
- Đặc tả cũ chạy qua phép kiểm mới: C1a 16 lỗi độ phủ, BTM 10.

## Còn mở (việc của người)

| Đề tài | Việc | Vai |
|---|---|---|
| C1a | Chọn phương pháp phân tích thăm dò kỳ vọng (SAP §5) ⇒ ký SAP 1.5 ⇒ agent đồng bộ lại đặc tả (SHA mới, mục TD_ky_vong có tham số nếu công cụ hỗ trợ) ⇒ duyệt đặc tả (`nguoi_duyet`) | thống kê viên → agent → thống kê viên/PI |
| BTM | Ký SAP ⇒ agent đồng bộ đặc tả ⇒ duyệt đặc tả | thống kê viên/PI |
| C1a, BTM | Phân tích «chưa tự động» (EFA/CFA, partial PO, RCS, mô hình hỗn hợp, trọng số, bảng mô tả từ sổ/khung mẫu…) làm tay bằng R/SPSS theo SAP sau khi khoá dữ liệu | thống kê viên |
