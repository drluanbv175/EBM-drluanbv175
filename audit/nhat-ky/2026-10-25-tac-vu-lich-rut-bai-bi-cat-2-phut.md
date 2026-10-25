# 25/10/2026 — Tác vụ lịch «kiem-rut-bai-kho-thang» kỳ 04/10: lệnh bị cắt ở hạn 2 phút của Bash, app vẫn ghi «succeeded»

**Triệu chứng.** `kiem_lich_nen.py` 🔴: «kỳ 04/10/2026 18:30: có lượt chạy TRỄ 24/10 08:40 (ngoài hạn 30h)».

**Đo.** `list_task_runs`: lượt duy nhất 04/10 18:38 (giờ VN), trạng thái «succeeded», `last_activity_at` = `started_at`. Bản ghi phiên:
chạy `sync_safety_check.py` (🟡) → gọi Bash cho `chu_trinh_chung_cu.py --vong 3 --ghi-log state/kiem-rut-bai-kho.log` → hết. Không có
dòng «KẾT THÚC» nào của 04/10 trong log; dòng duy nhất là lượt chạy tay 24/10 08:40. Lượt chạy bù 25/10 chạy hơn 6 phút ⇒ hạn
mặc định 2 phút của Bash cắt lệnh trước khi công cụ kịp ghi dấu vết; app vẫn xếp lượt «succeeded».

**Vá.** `sync/scheduled-tasks/kiem-rut-bai-kho-thang/SKILL.md` bước 2: chạy nền (`run_in_background`) rồi đợi thông báo, hoặc
`timeout: 600000`; không kết thúc phiên khi log chưa có dòng «KẾT THÚC» mới — thiếu thì báo «⚪ lượt chưa hoàn tất». Bản chạy
(`~/.claude/scheduled-tasks/…`) chép từ nguồn git bằng `tools/dong_bo_tac_vu_lich.py` (tu_sua_chua). Kỳ 04/10 đã chạy bù 25/10.

**Bài học.** «succeeded» của app chỉ nói phiên kết thúc không lỗi, không nói lệnh đã chạy xong — dấu vết log của công cụ mới là bằng
chứng (đúng thiết kế cảm biến `kiem_lich_nen`). Mọi tác vụ lịch gọi lệnh > 2 phút phải nói rõ cách chạy nền.

Cần bác sĩ kiểm chứng.
