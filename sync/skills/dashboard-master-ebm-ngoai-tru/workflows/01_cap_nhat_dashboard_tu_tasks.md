# Workflow cập nhật Dashboard từ 5 Scheduled Tasks

## Quy trình chung sau mỗi task run

1. Ghi task nguồn và kỳ rà soát vào `Task_Run_Log`.
2. Liệt kê nguồn tìm thấy.
3. Xác minh nguồn tối thiểu theo file tham chiếu.
4. Loại trùng với các bản ghi có sẵn.
5. Phân loại: thay đổi thực hành / theo dõi thêm / không áp dụng.
6. Ghi vào đúng sheet.
7. Tạo hành động chỉ khi có việc cụ thể cần xem xét triển khai hoặc xác nhận.
8. Cập nhật phần tóm tắt hoặc xuất gói nhập liệu nếu không chỉnh được file.
9. Kết luận bằng một trong ba câu chuẩn:
   - `Có cập nhật đã xác minh cần xem xét thay đổi thực hành.`
   - `Có cập nhật cần theo dõi nhưng chưa đủ căn cứ thay đổi thực hành.`
   - `Không ghi nhận cập nhật đã xác minh có khả năng thay đổi thực hành trong kỳ này.`

## Module theo task

### Updateebm
- Tập trung cập nhật EBM tuần có giá trị ngoại trú.
- Sheet: `Change_Log`, `Evidence_Register`, `Not_For_Change`, `Task_Run_Log`.
- Không đưa nghiên cứu nhỏ hoặc tin nhiễu thành thay đổi thực hành.

### Guideline
- Chỉ theo dõi guideline, focused update hoặc pathway chính thức.
- Sheet: `Change_Log`, `Evidence_Register`, `Task_Run_Log`.
- Nếu trùng với Updateebm, liên kết bản ghi có sẵn thay vì tạo mới.

### Updatethuoc
- Theo dõi official safety alerts, contraindications, interactions, renal/hepatic dosing, WHO AWaRe và stewardship.
- Sheet: `Medication_Safety`, `Evidence_Register`, `Action_Register`, `Task_Run_Log`.
- Cảnh báo có nguy cơ gây hại nghiêm trọng được phân loại ưu tiên khẩn.

### Thangdiemls
- Theo dõi thang điểm/công cụ quyết định lâm sàng đã xác minh.
- Sheet: `Clinical_Tools`, `Evidence_Register`, `Action_Register`, `Task_Run_Log`.
- Không ghi công cụ khi chưa xác minh quần thể hoặc cách diễn giải.

### Tonghopcapnhat
- Tổng hợp tháng từ dữ liệu đã ghi nhận, loại trùng và ưu tiên hành động.
- Sheet: `Dashboard_Summary`, `Action_Register`, `Task_Run_Log`.
- Không tự tạo cập nhật mới nếu không có nguồn đầu vào xác minh.
