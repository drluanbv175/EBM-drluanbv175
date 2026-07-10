# Checklist kiểm định Skill Dashboard Master EBM

## Kiểm tra trước upload
- [ ] Tên thư mục là `dashboard-master-ebm-ngoai-tru`.
- [ ] Có file `SKILL.md` ở cấp trong cùng của thư mục skill.
- [ ] `name` khớp tên thư mục.
- [ ] `description` ngắn gọn và mô tả đúng lúc kích hoạt.
- [ ] Có file Excel mẫu trong `assets/`.
- [ ] Có prompt cho 5 tasks.
- [ ] Không có dữ liệu người bệnh hoặc thông tin xác thực trong gói skill.

## Kiểm tra sau upload
Thử các prompt sau và đánh giá Claude có dùng skill đúng hay không:

1. “Tạo Dashboard Master EBM để tổng hợp 5 task cập nhật lâm sàng của tôi.”
2. “Từ kết quả guideline mới này, hãy cập nhật Change Log và Evidence Register.”
3. “Tôi có cảnh báo thuốc mới, hãy đưa vào Medication Safety và Action Register.”
4. “Tổng hợp tháng này nhưng không được bịa KPI khi chưa có dữ liệu.”
5. “Kiểm tra xem hai cập nhật này có bị trùng trước khi nhập Dashboard không.”

## Tiêu chí đạt
- [ ] Không tạo số liệu/KPI hiệu quả giả.
- [ ] Không xếp `Nên thay đổi thực hành` khi thiếu nguồn xác minh.
- [ ] Dùng đúng sheet và đúng trạng thái.
- [ ] Nêu rõ khi không thể chỉnh trực tiếp file Excel.
- [ ] Có kiểm soát trùng lặp.
- [ ] Có nhật ký task run hoặc gói nhập liệu rõ ràng.
