# 25/10/2026 — Đính chính: lượt tái kiểm rút bài kho chạy 23 phút, không phải «hơn 6 phút»

Bổ sung cho `2026-10-25-tac-vu-lich-rut-bai-bi-cat-2-phut.md` (PR #246, gộp trước khi lượt chạy bù xong). Lượt chạy bù 25/10:
`chu_trinh_chung_cu.py --vong 3 --ghi-log state/kiem-rut-bai-kho.log` hết **1377,7 giây (≈ 23 phút)**, mã 0, ghi dòng
«===== 2026-10-25 07:21:17 : KẾT THÚC chu_trinh_chung_cu (mã 0)». Tổng kết: 🟢 mọi chốt đạt; 2 nguồn mang cờ rút là BẢN ĐÍNH
CHÍNH bị rút — bác sĩ đã ký xem xét.

23 phút vượt cả hạn tối đa 10 phút của một lệnh Bash chạy thường ⇒ câu dự phòng «không có chạy nền thì đặt `timeout: 600000`»
trong SKILL.md là SAI — đã bỏ; nay BẮT BUỘC `run_in_background: true` rồi đợi thông báo. Bản chạy của tác vụ chép lại từ nguồn git.

Cần bác sĩ kiểm chứng.
