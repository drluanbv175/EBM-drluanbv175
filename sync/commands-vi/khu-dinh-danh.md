---
description: "Khử định danh bệnh án trước khi đưa vào nghiên cứu — xoá/thay PHI, chạy ngay trên máy"
---

Khử định danh văn bản bác sĩ cung cấp: **$ARGUMENTS**

1. Dùng kỹ năng `openmed-skills:deidentifying-clinical-text` (chạy hoàn toàn trên máy, dữ liệu KHÔNG rời máy).
   Nếu là cả tập dữ liệu thì dùng `deidentify-a-dataset`.
2. Với hồ sơ tiếng Việt, nhớ truyền `lang=`/`locale=` (xem `deidentifying-multilingual-text`).
3. Nếu nghiên cứu cần giữ khoảng cách thời gian giữa các mốc → dùng `shifting-clinical-dates` thay vì xoá ngày.
4. Sau khi khử, CHẠY KIỂM: `auditing-deid-leakage` để tìm định danh còn sót; chỉ báo "đã sạch" khi bước này không còn cảnh báo.
5. Nêu rõ đã xoá/thay những loại định danh nào. Nhắc: quy tắc HIPAA 18 nhóm là chuẩn Mỹ —
   quy định tại Việt Nam và yêu cầu của Hội đồng Đạo đức có thể khác. **Cần bác sĩ kiểm chứng**.
