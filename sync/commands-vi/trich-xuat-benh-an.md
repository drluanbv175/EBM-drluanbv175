---
description: "Bóc thông tin có cấu trúc từ bệnh án chữ tự do: chẩn đoán, thuốc, xét nghiệm, thủ thuật"
---

Bóc thông tin có cấu trúc từ bệnh án bác sĩ cung cấp: **$ARGUMENTS**

1. **TRƯỚC TIÊN kiểm tra PII**: nếu văn bản còn họ tên, ngày sinh, số hồ sơ, địa chỉ, số điện thoại →
   DỪNG LẠI, báo bác sĩ và đề nghị khử định danh trước (`/khu-dinh-danh`). KHÔNG xử lý bệnh án còn định danh.
2. Dùng kỹ năng `healthcare:clinical-note-extract` (hoặc `extracting-clinical-entities` của OpenMed nếu muốn chạy ngay trên máy).
3. Xử lý PHỦ ĐỊNH và THỜI ĐIỂM: "không đau ngực" không được đếm thành có đau ngực; tiền sử không lẫn với bệnh hiện tại.
4. Trả bảng theo nhóm: chẩn đoán · thuốc · xét nghiệm · thủ thuật · yếu tố nguy cơ.
5. Ghi rõ mục nào là suy luận chứ không có nguyên văn trong bệnh án. **Cần bác sĩ kiểm chứng**.
