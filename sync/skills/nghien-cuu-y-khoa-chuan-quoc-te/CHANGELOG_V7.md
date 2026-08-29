# Cập nhật v7 (nội dung 5.1) — 2026-05-30

Đợt chỉnh sửa qua skill-creator, tập trung ba mảng người dùng yêu cầu: cập nhật chuẩn/pháp lý, sửa module/workflow, và tối ưu description.

## 1. Tối ưu description (kích hoạt)

- Viết lại `description` trong `SKILL.md`: nêu rõ "Dùng skill này khi…" (khắc phục cảnh báo của `validate_skill.py`), liệt kê các tình huống kích hoạt cụ thể và nêu tên chuẩn báo cáo hiện hành.
- Thêm mệnh đề "pushy" để giảm undertrigger: kích hoạt cả khi yêu cầu không dùng chữ "nghiên cứu" nhưng thực chất là thiết kế/phân tích/báo cáo đề tài, QI hoặc nghiên cứu triển khai.
- Ghi rõ skill thay thế skill thống kê-chất lượng cũ để giảm cạnh tranh kích hoạt.
- Vẫn dưới giới hạn 1024 ký tự của Claude Custom Skills.

## 2. Tái kiểm chứng chuẩn/pháp lý (nguồn sơ cấp, 2026-05-30)

Đối chiếu trực tiếp nguồn gốc; xác nhận các mốc đang dùng vẫn là bản hiện hành:

- Declaration of Helsinki 2024 (WMA, 19/10/2024) — bản chính thức duy nhất.
- ICH E6(R3) GCP Step 4 Final Guideline (2025).
- CONSORT 2025 và SPIRIT 2025 (công bố 2025; CONSORT 30 mục + mục Open Science; SPIRIT 34 mục).
- ICMJE Recommendations bản 01/2026.

Bổ sung nhật ký tái kiểm chứng vào `references/00`.

## 3. Sửa nội dung module/reference

- `references/04`: chi tiết hóa ba thay đổi đã kiểm chứng của ICMJE 01/2026 (Section V về AI; quyền truy cập dữ liệu trong hợp tác có tài trợ; siết đăng ký thử nghiệm).
- `modules/02`: bổ sung mục Open Science (đăng ký, chia sẻ protocol/SAP/dữ liệu/mã) và sự tham gia người bệnh/cộng đồng (PPI, dùng GRIPP2 khi cần) theo CONSORT 2025; thêm hai hàng tương ứng trong bảng yêu cầu.

## 4. Không thay đổi

- Khung cổng chất lượng G0-G9, cấu trúc progressive disclosure, bộ template và bộ kiểm thử giữ nguyên.
- Không thêm số liệu, tài liệu tham khảo hay số văn bản không kiểm chứng được.

## Giới hạn

Đợt sửa này dựa trên kiểm chứng nguồn ngày 2026-05-30. Trước mỗi sản phẩm chính thức vẫn phải kiểm tra lại nguồn và yêu cầu của hội đồng/tạp chí đích. Kiểm tra cấu trúc không thay thế thẩm định chuyên gia.
