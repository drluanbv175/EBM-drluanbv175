# Báo cáo chỉnh sửa skill: phiên bản 5.0

## 1. Phạm vi chỉnh sửa

Chỉnh sửa skill `nghien-cuu-y-khoa-chuan-quoc-te` theo yêu cầu: tạo bản dùng cho nhiều thiết kế nghiên cứu y khoa, kiểm soát quy trình G0-G9, cập nhật pháp lý/chuẩn báo cáo/AI, có bộ kiểm thử và có thể đóng gói ZIP để upload lại vào Claude.

## 2. Nội dung giữ lại

- Tên skill kỹ thuật và định hướng toàn vòng đời nghiên cứu.
- Hệ thống cổng chất lượng G0-G9.
- Các mô-đun theo thiết kế nghiên cứu đã có.
- Nguyên tắc không tạo dữ liệu giả, không sửa dữ liệu gốc và không kết luận quá mức.

## 3. Nội dung đã sửa hoặc bổ sung

| Hạng mục | Thay đổi bản 5.0 |
|---|---|
| Frontmatter | Tối ưu `description` theo ngữ cảnh kích hoạt thực tế; giới hạn kiểm tra đổi đúng sang 1024 ký tự theo tài liệu Anthropic |
| `SKILL.md` | Tập trung vào điều phối, định tuyến tài liệu, cổng chất lượng và đầu ra mặc định; giảm trùng lặp |
| Nguồn chính thức | Ghi ngày kiểm chứng 2026-05-30; bổ sung nguồn Claude Skills, WMA, ICH, EQUATOR, ICMJE và văn bản Việt Nam |
| Đạo đức/pháp lý/dữ liệu | Làm rõ Luật 91/2025/QH15, Luật 15/2023/QH15, Thông tư 43/2024/TT-BYT; thêm AI/data governance |
| Bảo trì skill | Thêm workflow dùng khi chỉnh skill hoặc khi chuẩn thay đổi |
| Kiểm thử | Tách checklist cấu trúc và 8 ca kiểm thử đầu ra; thêm script đánh giá tĩnh |
| Báo cáo | Thêm mẫu báo cáo chỉnh sửa bằng skill-creator và báo cáo phát hành này |

## 4. Nguồn/chuẩn được xác minh khi biên soạn

- Anthropic Agent Skills overview và best practices.
- WMA Declaration of Helsinki 2024.
- ICH E6(R3) Step 4 Final Guideline 2025.
- EQUATOR/CONSORT-SPIRIT và ICMJE cập nhật tháng 01/2026.
- Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15, hiệu lực 01/01/2026.
- Luật Khám bệnh, chữa bệnh 15/2023/QH15, hiệu lực 01/01/2024.
- Thông tư 43/2024/TT-BYT, hiệu lực 01/02/2025.

## 5. Kiểm tra đã thực hiện ngoài Claude

- Kiểm tra cấu trúc tệp, frontmatter, đường dẫn tài liệu và không đóng gói dữ liệu nhạy cảm bằng `scripts/validate_skill.py`.
- Kiểm tra sự hiện diện của các neo an toàn/phương pháp/pháp lý/kiểm thử bằng `scripts/run_static_evaluations.py`.
- Kiểm tra ZIP mở được sau đóng gói.

## 6. Điều chưa thể xác nhận trong môi trường này

- Skill có kích hoạt đúng trong từng model Claude hay không.
- Chất lượng câu trả lời của Claude trên từng ca thử.
- Yêu cầu biểu mẫu cụ thể của Hội đồng đạo đức/bệnh viện/tạp chí tại thời điểm nộp.

Các điểm này phải được kiểm thử sau khi upload vào Claude và xác nhận tại đơn vị trước sử dụng chính thức.
