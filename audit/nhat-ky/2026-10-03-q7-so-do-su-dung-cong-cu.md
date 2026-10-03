# 03/10/2026 — Q7: không có sổ đo sử dụng công cụ dài hạn (transcript chỉ giữ ~26 ngày)

**Số đo (kiểm toàn diện 02/10).** `~/.claude/projects`: 586 tệp, 1,4 GB, cũ nhất 06/09/2026; settings không đặt `cleanupPeriodDays`.
Mọi kết luận «công cụ X không ai dùng» chỉ bảo đảm cho ~26 ngày. Công cụ dùng theo QUÝ (ACC/AHA, thang điểm) có thể bị coi nhầm là bỏ
không.

**Vá.**
- `tools/do_su_dung_cong_cu.py` đếm theo TÊN: tool · skill (input.skill) · agent con (input.subagent_type) · máy chủ MCP · mô hình ·
  lệnh `/…` trong thẻ `<command-name>` của tin nhắn người dùng.
- Ghi `state/su-dung-cong-cu-<YYYY-MM>.json` (ngoài git), khoá theo mã phiên nên chạy lại không đếm trùng. Có `--tong-hop` gộp các tháng.
- KHÔNG giữ lời nhắc, đầu ra công cụ hay tham số nào khác; test cài chuỗi «bí mật» vào transcript giả và kiểm nó không lọt vào sổ.
- Tác vụ tháng `kiem-tra-hoan-thien-he-thong-thang` thêm bước ⑨: ghi tháng trước, tổng hợp, và cấm đề xuất tắt công cụ khi sổ có
  dưới 3 tháng.

**Đo thật tháng 09/2026** (3,9 giây cho 1,4 GB; tệp có mtime trước tháng bị bỏ nhanh): 64 phiên có lượt gọi.
- Lệnh gạch chéo 10 tên (cap-nhat-chung-cu-y-khoa 5, cochrane 2…); Skill 6 tên; agent con 5 tên (general-purpose 28, Explore 15,
  tham-dinh-dau-ra 2…).
- 29 máy chủ MCP (Claude_Browser 389, PubMed 171, scheduled-tasks 109…).
- Bash 19.877 lượt.

**Kiểm.** 6 test (transcript giả trong thư mục tạm, kể cả agent con và dòng hỏng). 4 đột biến đều bị bắt: rò nội dung input · cộng
dồn khi chạy lại · bỏ đếm lệnh · nhận dòng sai tháng.
