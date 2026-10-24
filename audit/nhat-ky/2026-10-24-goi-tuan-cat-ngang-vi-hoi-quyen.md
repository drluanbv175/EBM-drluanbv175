# 24/10/2026 — Gói duyệt tuần W43 không ra: lượt lịch bị cắt ngang vì lệnh đòi duyệt quyền

**Hiện tượng.** Hòm việc/Đài 🔴 «goi-duyet-tuan-ebm kỳ 19/10/2026 18:30: thiếu queue/tuan-2026-W43.md». `list_task_runs`
báo 4 lượt (19/10, 21/10, 23/10 ×2) đều «succeeded» nhưng mỗi lượt chỉ sống ~1 phút; lượt W42 (12/10) chạy 2 giờ.

**Nguyên nhân (đọc bản ghi phiên).** Mỗi lượt dừng đúng ở lần gọi Bash bước 1, kết quả công cụ:
«Tool permission request failed: AbortError: Tool permission stream closed before response received» — lệnh cần duyệt quyền,
lượt lịch không có người bấm ⇒ lượt bị cắt (`lastTurnCutShort: true`). Siêu dữ liệu phiên: các lượt chạy tốt (21/09–12/10)
mang `permissionMode: auto`; lượt 19/10, 21/10, 23/10 21:37 mang `default` (app chưa đặt `permissions.defaultMode`). Lượt
23/10 20:21 mang `auto` mà vẫn chết — bộ phân loại đòi duyệt lệnh `ps -axo … | grep …; ls -la …` do agent tự thêm. Lệnh bị
chặn đều là lệnh agent tự ghép (`cd … && time … > log 2>&1; tail`), không phải chính công cụ của quy trình.

**Vá.** (1) Bác sĩ đặt chế độ quyền Auto (Settings → Claude Code) — việc của bác sĩ. (2) Lời nhắc tác vụ
`sync/scheduled-tasks/goi-duyet-tuan-ebm/SKILL.md` thêm «QUY TẮC CHẠY LỆNH»: mỗi lần Bash đúng MỘT lệnh của quy trình,
không `cd`/`time`/`ps`/`ls`/chuỗi lệnh/chuyển hướng; đầu ra dài dùng cờ báo cáo của chính công cụ rồi Read; kiểm khoá
bằng Read; lệnh bị từ chối ⇒ ghi «⚪ bước <n> chưa chạy được» vào gói, không bỏ qua âm thầm. Sau khi gộp:
`python3 tools/dong_bo_tac_vu_lich.py --ap-dung` chép nguồn → bản chạy của app.

**Kiểm.** `tools/kiem_tac_vu_lich_da_nen.py` 15/15 tác vụ đúng nền tảng; test lịch (24 ca) xanh. Lượt tuần kế tiếp là
phép thử thật — `python3 tools/kiem_lich_nen.py` báo kỳ có tệp gói hay không.
