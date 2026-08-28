# Hướng dẫn sử dụng: `nghien-cuu-y-khoa-chuan-quoc-te`

## Mục tiêu

Gói skill này hỗ trợ nghiên cứu y khoa theo quy trình G0-G9, từ ý tưởng đến báo cáo/công bố. Skill giúp kiểm soát chất lượng và minh bạch; không thay thế Hội đồng đạo đức, thống kê viên, quy định đơn vị hoặc phản biện độc lập.

## Cách đưa vào Claude

1. Upload tệp ZIP chứa thư mục `nghien-cuu-y-khoa-chuan-quoc-te/` ở cấp gốc trong phần Custom Skills của Claude.
2. Kích hoạt skill khi làm đề tài nghiên cứu, rà soát hồ sơ, phân tích dữ liệu hoặc viết báo cáo.
3. Với dữ liệu người bệnh, chỉ cung cấp dữ liệu phù hợp quy định, ưu tiên khử định danh và loại bỏ thông tin không cần thiết.

## Cấu trúc gói

- `SKILL.md`: bộ điều phối ngắn gọn; Claude đọc khi skill được kích hoạt.
- `references/`: nguồn chính thức, pháp lý, chuẩn báo cáo, liêm chính công bố.
- `workflows/`: quy trình từng giai đoạn và bảo trì skill.
- `modules/`: chỉ dẫn theo thiết kế nghiên cứu.
- `templates/`: mẫu để soạn hồ sơ thực tế.
- `quality/`: checklist và tình huống kiểm thử.
- `scripts/`: kiểm tra cấu trúc và độ bao phủ nội dung của gói.

## Điều bắt buộc trước khi dùng hồ sơ chính thức

- Kiểm tra phiên bản hiện hành của quy định pháp lý, guideline báo cáo và yêu cầu của đơn vị/tạp chí.
- Không dùng tài liệu AI tạo ra thay cho phê duyệt đạo đức hoặc quyết định chuyên môn.
- Không đưa dữ liệu định danh người bệnh vào AI nếu không có căn cứ và biện pháp bảo vệ phù hợp.
- Không kết luận “sẵn sàng” nếu chưa có bằng chứng vượt cổng chất lượng tương ứng.

## Cách kiểm tra gói sau khi giải nén

Chạy:

```bash
python scripts/validate_skill.py
python scripts/run_static_evaluations.py
```

Hai script chỉ kiểm tra **cấu trúc và độ bao phủ chỉ dẫn**; hiệu năng thực tế phải kiểm thử bằng prompt trong Claude theo `quality/02_ca_kiem_thu_dau_ra.md`.

## Câu lệnh bắt đầu nhanh

Xem `templates/05_cau_lenh_su_dung_ngay.md`.
