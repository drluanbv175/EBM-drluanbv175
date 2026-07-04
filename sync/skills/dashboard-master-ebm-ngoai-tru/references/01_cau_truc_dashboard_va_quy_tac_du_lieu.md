# Cấu trúc Dashboard Master EBM và quy tắc dữ liệu

## 1. Các sheet bắt buộc

| Sheet | Chức năng | Nguồn cập nhật chính |
|---|---|---|
| `Dashboard_Summary` | Trang điều hành tổng hợp, công thức và biểu đồ | Tự tổng hợp từ các sheet dữ liệu |
| `Change_Log` | Các thay đổi đã xác minh có khả năng ảnh hưởng thực hành | Updateebm, Guideline |
| `Action_Register` | Hành động triển khai hoặc cần xác nhận | Tất cả task khi có hành động |
| `Evidence_Register` | Danh mục nguồn đã xác minh, truy nguyên được | Tất cả task |
| `Medication_Safety` | Cảnh báo thuốc, kháng sinh, stewardship | Updatethuoc |
| `Clinical_Tools` | Thang điểm/công cụ lâm sàng | Thangdiemls |
| `Not_For_Change` | Nội dung chưa đủ căn cứ thay đổi thực hành | Tất cả task |
| `Task_Run_Log` | Nhật ký mỗi lần task chạy | Tất cả task |
| `Lists_Validation` | Danh mục chuẩn dùng cho dropdown/kiểm soát dữ liệu | Quản trị workbook |

## 2. Quy tắc ID

| Loại bản ghi | Định dạng |
|---|---|
| Change ID | `CHG-[TASK]-YYYYMMDD-NN` |
| Action ID | `ACT-YYYYMMDD-NN` |
| Evidence ID | `EVD-[TASK]-YYYYMMDD-NN` |
| Med ID | `MED-YYYYMMDD-NN` |
| Tool ID | `TOOL-YYYYMMDD-NN` |
| Run ID | `RUN-[TASK]-YYYYMMDD-NN` |

Tên task chuẩn: `UPDATEEBM`, `GUIDELINE`, `UPDATETHUOC`, `THANGDIEMLS`, `TONGHOPCAPNHAT`.

## 3. Change_Log

Các cột:
- Change ID
- Ngày ghi nhận
- Task nguồn
- Chuyên khoa/chủ đề
- Vấn đề lâm sàng
- Cập nhật đã xác minh
- Hành động thực hành đề nghị
- Đối tượng áp dụng
- Không áp dụng/thận trọng
- Độ chắc chắn chứng cứ
- Độ mạnh khuyến cáo
- Nguồn chính/năm/phiên bản
- Evidence ID liên kết
- Trạng thái
- Ghi chú xác nhận tại đơn vị

Chỉ dùng sheet này cho cập nhật đã được xác minh hoặc đang chờ đánh giá áp dụng; không dùng cho tín hiệu chưa kiểm chứng.

## 4. Action_Register

Các cột:
- Action ID
- Change ID liên kết
- Hành động cần thực hiện
- Mức ưu tiên
- Người/đơn vị cần xác nhận
- Sản phẩm/quy trình cần cập nhật
- Trạng thái thực hiện
- Hạn đề nghị
- Ghi chú

Không tự tạo tên người phụ trách hoặc hạn bắt buộc khi chưa được cung cấp.

## 5. Evidence_Register

Các cột:
- Evidence ID
- Change ID liên kết
- Ngày xác minh
- Loại nguồn
- Tổ chức/tác giả
- Tên tài liệu
- Năm/phiên bản
- Quần thể áp dụng
- Kết luận liên quan
- Grading nguyên bản
- URL/nguồn truy nguyên
- Đã kiểm chứng nguồn gốc?
- Ghi chú

## 6. Medication_Safety

Chỉ ghi nội dung liên quan thuốc/kháng sinh:
- cảnh báo an toàn chính thức;
- chống chỉ định/thận trọng;
- tương tác thuốc;
- chỉnh liều ở nhóm đặc biệt;
- hạn chế/ngừng dùng;
- stewardship hoặc WHO AWaRe;
- medication reconciliation;
- theo dõi độc tính.

## 7. Clinical_Tools

Chỉ đề xuất công cụ khi đã xác minh:
- quần thể áp dụng;
- mục đích;
- cut-off/cách diễn giải;
- hành động lâm sàng;
- giới hạn áp dụng.

Không tự tạo cut-off hoặc mở rộng đối tượng sử dụng.

## 8. Dashboard_Summary

Chỉ hiển thị số lượng bản ghi đã có trong hệ thống, ví dụ:
- số cập nhật đã xác minh;
- số cập nhật nên thay đổi thực hành;
- số nội dung theo dõi thêm;
- số cảnh báo an toàn thuốc;
- số công cụ cần xem xét;
- số hành động cần thực hiện.

Không hiển thị KPI kết quả điều trị, lợi ích người bệnh, chi phí hoặc tuân thủ nếu chưa có dữ liệu triển khai thật.
