# Nguồn cứu hộ SKILL của tác vụ lịch (scheduled-tasks)

Bản chạy thật nằm NGOÀI cây OneDrive: `~/.claude/scheduled-tasks/<tên>/SKILL.md`
— app dọn runtime là mất trắng (đã xảy ra với skill thường, đo 13/08: 20/22 lệch bản).
Thư mục này là BẢN SAO NGUỒN trong OneDrive để (a) không mất khi runtime bị dọn,
(b) máy Windows chép sang được. Sau khi SỬA một SKILL runtime, chép lại vào đây
(mỗi lần sửa — chưa có tool tự động; `dong_bo_skill.py` KHÔNG quản nhánh này).
Khôi phục: chép ngược `sync/scheduled-tasks/<tên>/SKILL.md` → `~/.claude/scheduled-tasks/<tên>/`.
Cần bác sĩ kiểm chứng.

## Chạy được trên Mac lẫn Windows (28/09/2026)
Mỗi SKILL mở đầu bằng ĐÚNG MỘT khối nền tảng:
- `NỀN TẢNG: macOS + Windows` — thư mục làm việc cho cả hai máy (`$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI`
  · `%USERPROFILE%\OneDrive\Claude AI`), quy tắc đổi `python3` → `py -3` và venv; tệp tạm vào `state/`, không `/tmp/`.
- `NỀN TẢNG: CHỈ CHẠY TRÊN MAC` — chỉ khi tác vụ gọi script bash (`*.sh`); Windows DỪNG và báo.
Không viết cứng `/Users/<tên>` hay `/tmp/`. Kiểm: `python3 tools/kiem_tac_vu_lich_da_nen.py` (Windows `py -3 …`); chốt BH130.
Sau khi sửa ở đây, chép lại bản runtime `~/.claude/scheduled-tasks/<tên>/SKILL.md` trên TỪNG máy.
