# 03/10/2026 — AN-09: 29 tệp trạng thái phiên của harness bị track trong repo công khai

**Đo (kiểm toàn diện 02/10, đo lại 03/10).** `git ls-files` có 29 tệp dưới `.claude/state/` và `.claude/sessions/` LỒNG trong
`tools/`, `tools/eval/`, `tools/critic/`, `tools/vietnamize/`, `tools/orchestrator/tests/`, `sync/skills/` và một số skill.
- Các tệp này do hook của claude-code-harness ghi vào thư mục làm việc của mỗi phiên: `changed-files.jsonl`,
  `breezing-timeline.jsonl`, `.last_inbox_read_<mã phiên>`, `broadcast.md`. Chúng lộ đường dẫn máy (`/Users/…`) và mã phiên ra
  repo công khai.
- `.gitignore` gốc chỉ chặn `/.claude/*` ở GỐC và `sync/skills/**/.claude/`, nhưng các tệp dưới `sync/skills/` đã bị track từ
  TRƯỚC khi có luật nên vẫn nằm trong git.

**Vá.**
- `.gitignore` thêm `**/.claude/state/` và `**/.claude/sessions/`.
- `git rm --cached` cả 29 tệp: tệp còn nguyên trên đĩa, không viết lại lịch sử.
- Test `tools/test_an09_khong_track_trang_thai_harness_20261003.py` chặn tệp đã track lọt lại (đột biến `git add -f` một tệp ⇒ đỏ).

**Lưu ý vận hành.** Máy kéo commit này sẽ thấy git XOÁ các tệp đó khỏi cây làm việc, vì đó là tệp từng track nay bị bỏ. Đây là bộ
đệm trạng thái phiên, harness tự tạo lại; không ảnh hưởng dữ liệu y khoa. Repo y khoa có 4 tệp cùng loại dưới
`exports/hai-long-benh-nhan-C1a-BVQY175/.claude/state/` (đã có luật ignore từ trước, chỉ thiếu `git rm --cached`) — vá ở PR y khoa riêng.

**Kiểm.** `pytest tools/` 2063 đạt; `chot_hoi_quy_bai_hoc` 🟢.
