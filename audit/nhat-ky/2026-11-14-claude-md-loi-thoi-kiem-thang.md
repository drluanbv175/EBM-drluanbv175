# 14/11/2026 — Hai khẳng định lỗi thời trong CLAUDE.md (kiểm tra hoàn thiện hệ thống tháng)

**Phát hiện:** lượt lịch `kiem-tra-hoan-thien-he-thong-thang` 14/11/2026, mảng ⑦ (đối chiếu
khẳng định của CLAUDE.md với mã sống).

1. §2 ghi `tools/dong_bo_tat_ca.py` có «8 làn». Đo sống `python3 tools/dong_bo_tat_ca.py --liet-ke-lan`
   ⇒ **9 làn** (làn 9 «Cloud ↔ repo (bundle tài khoản)» thêm sau khi dòng doctrine được viết).
2. §10 ghi «Kiểm rút bài + độ tươi 37 thang điểm (QUÝ, tác vụ `kiem-thang-diem-quy`)». Tác vụ quý
   đã bỏ 13/11/2026 theo lời bác sĩ (#328, `2026-11-13-bo-tac-vu-kiem-thang-diem-quy.md`); công cụ
   giữ để chạy tay.

**Sửa:** chỉ văn bản mô tả trong CLAUDE.md (không đụng số liệu y khoa, cổng hay lịch).

**Lịch:** `list_scheduled_tasks` 14/11 xác nhận tác vụ KHÔNG còn đăng ký trong app; chỉ còn thư mục
runtime `~/.claude/scheduled-tasks/kiem-thang-diem-quy/` mồ côi (vô hại, không bắn).

**Bài học:** con số đếm thành phần (số làn, số tác vụ) trong doctrine trôi theo mã; ưu tiên chỉ
lệnh liệt kê (`--liet-ke-lan`) thay vì ghi cứng số.
