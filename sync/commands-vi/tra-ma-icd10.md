---
description: "Tra mã ICD-10 chẩn đoán/thủ thuật theo tên bệnh hoặc theo mã, kèm kiểm tính hợp lệ"
---

Tra mã ICD-10 cho: **$ARGUMENTS**

1. Nạp công cụ: ToolSearch với `select:mcp__plugin_healthcare_ICD10_Codes__search_codes,mcp__plugin_healthcare_ICD10_Codes__lookup_code,mcp__plugin_healthcare_ICD10_Codes__validate_code`
2. Nếu bác sĩ đưa TÊN BỆNH → `search_codes` (tìm theo mô tả). Nếu đưa MÃ → `lookup_code`.
3. Trả bảng: mã · mô tả tiếng Anh · nghĩa tiếng Việt · có dùng để thanh toán được không.
4. Với bệnh có nhiều giai đoạn (ung thư, đái tháo đường có biến chứng), liệt kê cả nhóm mã liên quan.
5. Nhắc: đây là bộ mã ICD-10-CM của Mỹ; mã dùng tại Việt Nam có thể khác — **cần bác sĩ kiểm chứng**.
