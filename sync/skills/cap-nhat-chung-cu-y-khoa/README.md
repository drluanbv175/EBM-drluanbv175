# Cập nhật chứng cứ y khoa — phiên bản theo yêu cầu

## Mục tiêu

Skill này dùng khi bác sĩ muốn hỏi **một vấn đề lâm sàng cụ thể** và nhận câu trả lời EBM hiện hành có thể áp dụng trong thực hành ngoại trú.

Ví dụ lệnh dùng:

- `Cập nhật EBM: điều trị COPD ở người cao tuổi có tim mạch và CKD.`
- `Cập nhật nhanh: an toàn duloxetine ở người cao tuổi đa thuốc.`
- `Phân tích chuyên sâu: suy tim EF bảo tồn, theo guideline mới nhất và RCT quan trọng.`
- `Thẩm định: guideline này có đủ tin cậy để áp dụng tại phòng khám không?`
- `Antibiotic stewardship: viêm bàng quang không biến chứng ngoại trú.`

## Không phải mục tiêu mặc định

Skill này không tự tạo báo cáo tuần/tháng, Dashboard, mã Master hoặc tác vụ theo dõi. Các chức năng đó chỉ được thêm khi bác sĩ yêu cầu riêng.

## Web Dashboard kèm theo

Khi môi trường hỗ trợ tạo file, mỗi cập nhật EBM cho vấn đề cụ thể phải tạo thêm Web Dashboard HTML độc lập theo mẫu **"Evidence Workbench"** (nền sáng, 3 cột: bộ lọc · Quick View + bảng item · panel thẩm định, có khối GRADE Evidence-to-Decision) — mặc định từ v1.10.0; mẫu "Dark Analyst" (nền tối) chỉ dùng khi bác sĩ yêu cầu. Dashboard này dùng để tra cứu nhanh, không phải Dashboard Master.

Chuỗi tự động khi gọi skill (không cần yêu cầu từng bước): dựng Dashboard → cổng liêm chính `verify_dashboard.py --online` → an toàn thuốc (nếu liên quan) → thư viện `build_library.py add` → 3 sản phẩm phái sinh `make_derivatives.py` → nạp vào sổ cái trung tâm `EBM_MASTER/tools/sync_all.py`. Chi tiết: `SKILL.md` §5A/§5D/§5E.

## Trình bày theo PICO

Khi câu hỏi là về hiệu quả/an toàn của một can thiệp (hoặc khi bác sĩ yêu cầu "PICO"/"chứng cứ tốt nhất"), mỗi can thiệp được trình bày thành một khối **P–I–C–O + chứng cứ tốt nhất + grading từ nguồn + kết luận thực hành**. Hiệu số (effect size) trích đúng như nguồn; không tự gán GRADE. Chi tiết và ví dụ: `references/06-pico-va-trich-dan.md`.

Nguồn được ghi dạng văn bản thường (tác giả/tổ chức + năm + tạp chí) và Vancouver/NLM; không chèn thẻ markup trích dẫn hay mã kỹ thuật vào câu trả lời.

## Phiên bản

Phiên bản hiện tại: xem `SKILL.md` (frontmatter `version:`). Lịch sử đầy đủ: `CHANGELOG.md` —
KHÔNG lặp lại danh sách phiên bản ở đây (README từng đứng yên ở v1.3.0 trong khi SKILL.md đã lên
v1.12.1, vá 2026-07-11: hai changelog tay dễ lệch nhau, chỉ giữ MỘT nguồn).
