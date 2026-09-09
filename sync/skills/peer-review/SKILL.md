---
name: peer-review
description: Bình duyệt bản thảo khoa học có CẤU TRÚC — đánh giá tính hợp lệ (validity), phương pháp, thống kê, đạo đức/đăng ký, trình bày & chuẩn báo cáo, trích dẫn; soạn nhận xét đối kháng đa lăng kính + thư phản biện cho tác giả. Dùng trước khi nộp (bình duyệt nội bộ) hoặc khi đóng vai phản biện. Phán định kèm bằng chứng từ bản thảo; KHÔNG bịa lỗi; tách "bắt buộc sửa" vs "đề xuất".
---

# Skill: Bình duyệt bản thảo (peer-review)

<!-- EBM-VN-GUARD -->
> **⚕️ Bản điều chỉnh cho bác sĩ EBM ngoại trú (Việt Nam).** Skill gốc của K-Dense Inc. đã được chỉnh để phù hợp quy ước trong `CLAUDE.md` của người dùng.

Dùng cho `binh-duyet`. Bình duyệt đối kháng, xây dựng, có bằng chứng.

## Nguyên tắc liêm chính (4 trụ cột)
- Mỗi phán định kèm **bằng chứng từ bản thảo** (vị trí/đoạn); KHÔNG bịa lỗi, KHÔNG khen sáo.
- Tách rõ **🔴 bắt buộc sửa (major)** vs **🟡 đề xuất (minor)**.
- Kiểm liêm chính: đăng ký nghiên cứu, kết cục đăng ký vs công bố, COI/tài trợ/khai báo AI, trích dẫn ma (phối hợp `citation-management`).

## Quy trình (6 lăng kính)
**BƯỚC 0 — Tiền đề:** xác định loại thiết kế → chuẩn báo cáo tương ứng; đọc trọn bản thảo trước khi chấm.
1. **Tính hợp lệ & tầm quan trọng:** câu hỏi rõ? khoảng trống thật? đóng góp gì?
2. **Phương pháp:** thiết kế phù hợp câu hỏi? chọn mẫu/cỡ mẫu/đối chứng/làm mù; nguy cơ sai lệch (RoB 2/ROBINS-I/QUADAS-2).
3. **Thống kê:** test/mô hình đúng giả định? báo CI không chỉ p? phân tích định trước vs thăm dò? dữ liệu thiếu xử lý ra sao? (đối chiếu skill `statistical-analysis`).
4. **Đạo đức & minh bạch:** phê duyệt IRB + ICF + mã đăng ký; COI/tài trợ; khai báo dùng AI; tuân chuẩn báo cáo.
5. **Trình bày & chuẩn báo cáo:** **tiêu đề** có nêu thiết kế + quần thể + kết cục? **tóm tắt** đủ 5 phần, độc lập, mọi số khớp Results? **từ khóa** có bổ sung từ ngoài tiêu đề? IMRAD mạch lạc; Results không lẫn diễn giải; Conclusion không vượt dữ liệu; bảng/hình rõ; checklist CONSORT/STROBE/PRISMA/STARD/TRIPOD đủ mục — kể cả mục Title-and-abstract của chuẩn đó.
6. **Trích dẫn:** PMID/DOI thật + trích đúng nội dung (phối hợp `citation-management`).

## Mẫu đầu ra
```
Tóm tắt bản thảo (2–3 câu) + khuyến nghị tổng thể: [chấp nhận / sửa nhỏ / sửa lớn / từ chối]
🔴 BẮT BUỘC SỬA (major): [#] vấn đề + vị trí + lý do + đề xuất
🟡 ĐỀ XUẤT (minor): ____
Đối chiếu chuẩn báo cáo — mục thiếu: ____
Liêm chính: đăng ký/đạo đức/COI/AI/trích dẫn: ____
THƯ PHẢN BIỆN (gửi tác giả): lịch sự, theo điểm, có thể trả lời được.
```
Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG tự viết lại bản thảo (→ `scientific-writing`); KHÔNG tự sửa số liệu. Bình duyệt nội bộ không thay bình duyệt chính thức của tạp chí.
