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

Khi môi trường hỗ trợ tạo file, mỗi cập nhật EBM cho vấn đề cụ thể phải tạo thêm Web Dashboard HTML độc lập theo mô hình **Clinical Quick View → Evidence Detail → Safety/Limits/Vietnam**. Dashboard này dùng để tra cứu nhanh, không phải Dashboard Master.

## Trình bày theo PICO

Khi câu hỏi là về hiệu quả/an toàn của một can thiệp (hoặc khi bác sĩ yêu cầu "PICO"/"chứng cứ tốt nhất"), mỗi can thiệp được trình bày thành một khối **P–I–C–O + chứng cứ tốt nhất + grading từ nguồn + kết luận thực hành**. Hiệu số (effect size) trích đúng như nguồn; không tự gán GRADE. Chi tiết và ví dụ: `references/06-pico-va-trich-dan.md`.

Nguồn được ghi dạng văn bản thường (tác giả/tổ chức + năm + tạp chí) và Vancouver/NLM; không chèn thẻ markup trích dẫn hay mã kỹ thuật vào câu trả lời.

## Phiên bản

- `v1.3.0` — bổ sung chế độ PICO và quy tắc ghi nguồn sạch (văn bản + Vancouver, không thẻ markup); thêm `references/06-pico-va-trich-dan.md`.
- `v1.2.0` — bổ sung Web Dashboard Clinical Quick View độc lập bắt buộc cho mỗi vấn đề cụ thể khi tạo file được; vẫn không tự cập nhật Dashboard Master.
- `v1.1.0` — tách rõ cập nhật EBM theo yêu cầu khỏi hệ thống Dashboard định kỳ; bổ sung đầy đủ reference nội bộ và template đầu ra.
