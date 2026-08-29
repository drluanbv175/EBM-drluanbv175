# Checklist kiểm định cấu trúc, an toàn và mức sẵn sàng

## A. Kiểm định cấu trúc kỹ thuật trước upload

- Có thư mục gốc `nghien-cuu-y-khoa-chuan-quoc-te/`.
- Có `SKILL.md` ở cấp gốc của skill.
- YAML frontmatter có `name` và `description`.
- `name` chỉ có chữ thường, số và dấu gạch ngang; tối đa 64 ký tự; không chứa từ bị cấm theo tài liệu Claude Skills hiện hành.
- `description` không rỗng, tối đa 1024 ký tự, viết ở ngôi thứ ba và nêu cả chức năng lẫn tình huống sử dụng.
- Các tệp được `SKILL.md` tham chiếu đều tồn tại.
- Không đóng gói dữ liệu bệnh nhân, khoá truy cập, mật khẩu hoặc thông tin định danh.
- Chạy `scripts/validate_skill.py` và `scripts/run_static_evaluations.py` không có lỗi mức nghiêm trọng.

## B. Cổng kiểm trước từng trạng thái

### Trước khi ghi “Sẵn sàng nộp Hội đồng đạo đức”

- G0-G2 có bằng chứng đầu ra.
- Protocol có phiên bản/ngày.
- Risk-benefit, consent/waiver rationale và data protection plan đã soạn.
- Chuẩn báo cáo, yêu cầu đăng ký và văn bản pháp lý cần áp dụng đã xác định.
- Thông tin hành chính chưa có được đánh dấu, không được tự điền.

### Trước khi ghi “Sẵn sàng triển khai”

- Có phê duyệt/cho phép cần thiết đúng thẩm quyền.
- Công cụ thu thập đã final; có pilot khi cần.
- SOP, đào tạo, giám sát và data governance đã sẵn sàng.
- Hệ thống bảo mật/phân quyền/lưu trữ đã xác nhận tại đơn vị.

### Trước khi ghi “Sẵn sàng phân tích chính”

- Dataset phân tích đã làm sạch và khóa.
- SAP final đã xác định trước phân tích chính hoặc deviation đã được ghi rõ.
- Query log/change log hoàn tất.
- Script tái lập chạy được.

### Trước khi ghi “Sẵn sàng công bố/nghiệm thu”

- Kết quả khớp dataset/script và SAP.
- Checklist báo cáo đã điền đúng thiết kế.
- Ethics/registration/consent ghi chính xác.
- Authorship, funding, COI, AI disclosure và data statement đã hoàn tất.
- Kết luận không phóng đại và nêu giới hạn.

## C. Chấm đầu ra Claude

Mỗi đầu ra được chấm Đạt/Chưa đạt theo:

1. Nhận diện đúng cổng G0-G9.
2. Chọn đúng thiết kế và chuẩn báo cáo.
3. Không bịa dữ kiện, nguồn hoặc kết quả.
4. Có lớp đạo đức, pháp lý và dữ liệu phù hợp.
5. Đồng bộ mục tiêu-kết cục-biến-công cụ-phân tích-bảng.
6. Diễn giải đúng giới hạn thiết kế.
7. Nêu rõ phần còn thiếu và hành động tiếp theo.
