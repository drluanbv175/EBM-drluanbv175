# Quản trị dữ liệu, làm sạch, khóa số và tái lập

## 1. Quy tắc bất di bất dịch

- Bản dữ liệu gốc là chỉ đọc; không sửa đè.
- Tất cả thao tác làm sạch phải thực hiện qua syntax/script hoặc query log có thể kiểm toán.
- Không làm sạch để làm đẹp kết quả.
- Không mở khóa phân tích chính sau khi xem kết quả mà không có biên bản và lý do.

## 2. Data management plan

| Miền | Nội dung phải xác định |
|---|---|
| Nguồn dữ liệu | Phiếu giấy, REDCap, SPSS, HIS/EMR, registry, xét nghiệm |
| Mã định danh | Cách tạo ID, tách khóa nhận diện |
| Quyền truy cập | Ai xem bản định danh, ai phân tích bản khử định danh |
| Lưu trữ/sao lưu | Vị trí, mã hóa, bản sao, thời gian lưu |
| Nhập liệu | Nhập đơn/đôi, validation, audit trail |
| Missing | Mã hóa và xử lý |
| Query | Quy trình truy vấn/sửa/đóng query |
| Dữ liệu xuất | Định dạng, phiên bản, kiểm tra |
| Khóa dữ liệu | Tiêu chí, người xác nhận, biên bản |
| Chia sẻ/hủy | Quyền, điều kiện, thời hạn |

## 3. Kiểm tra làm sạch

- Duplicate ID.
- Giá trị ngoài phạm vi.
- Logic mâu thuẫn.
- Ngày không hợp lệ.
- Missing critical variables.
- Outlier cần xác minh, không tự xóa.
- Biến tính toán tái lập.
- Đối chiếu mẫu nguồn nếu cần.

## 4. Cấu trúc thư mục dữ liệu đề nghị

```
project/
  00_protocol_ethics/
  01_source_data_restricted/
  02_raw_readonly/
  03_cleaning_scripts/
  04_query_logs/
  05_clean_locked/
  06_analysis_scripts/
  07_outputs/
  08_manuscript_reports/
  09_archive/
```

## 5. Biên bản khóa dữ liệu

| Nội dung | Giá trị |
|---|---|
| Dataset khóa | [Tên file, phiên bản, checksum nếu có] |
| Ngày khóa | [CẦN BỔ SUNG] |
| Số quan sát | [CẦN BỔ SUNG] |
| Query còn mở | Không/có và lý do |
| Protocol/SAP áp dụng | Phiên bản |
| Người xác nhận | [CẦN BỔ SUNG] |
| Quy tắc mở khóa | Chỉ bằng biên bản và phê duyệt phù hợp |
