# 29/10/2026 — Hook «một cửa vào» không chạy ở phiên mở trong repo y khoa (BH172 mở rộng)

**Bác sĩ hỏi:** đã hoàn thiện hết chưa để hệ thống tự vận hành đúng sau lỗi 28/10 (câu hỏi chủ đề chứng cứ không vào dây
chuyền thiết kế). Bác sĩ chọn «giải quyết vấn đề 3 một cách tốt nhất».

**Đo:**
- Hook UserPromptSubmit `tools/nhac_dinh_tuyen.py` (BH172, PR #272) khai ở `.claude/settings.json` của repo GỐC. Claude Code
  chỉ đọc settings của THƯ MỤC DỰ ÁN đang mở, không đọc của thư mục cha.
- `medical-ebm-automation/.claude/settings.json` không tồn tại; `tools/nhac_dinh_tuyen.py` không có trong repo y khoa ⇒ phiên
  mở trong `medical-ebm-automation/` hoặc worktree của nó (`.claude/worktrees/<tên>`, `~/.ebm-worktrees/…`) không có hook,
  chỉ còn luật văn bản CLAUDE.md — đúng lớp gốc đã làm ba phiên 28/10 đi sai đường.
- Liệt kê phiên (29/10): mọi phiên nhóm «Cập nhật chứng cứ y khoa…» mở ở thư mục gốc (hook có hiệu lực); phiên nhóm
  «Nghiên cứu y khoa đăng tạp chí» mở ở `medical-ebm-automation/` (không có hook). Chưa thấy phiên chứng cứ nào đi sai vì lỗ
  này — rủi ro thấp nhưng có thật.

**Vá (cặp PR):**
- Repo y khoa: `tools/nhac_dinh_tuyen_cau_noi.py` tìm repo gốc — thư mục có ĐỦ `tools/nhac_dinh_tuyen.py` +
  `tools/orchestrator/intent.py` — theo thứ tự `EBM_WORKSPACE_ROOT` → đi ngược lên từ `CLAUDE_PROJECT_DIR`/vị trí tệp →
  worktree ngoài cây: `.git` (`gitdir:`) → `commondir` → checkout chính rồi đi lên; chạy ĐÚNG hook nhắc của repo gốc bằng tiến
  trình con (không chép bộ định tuyến — hai bản sẽ trôi lệch). Không thấy repo gốc/lỗi/quá hạn ⇒ im lặng, mã 0.
  `.claude/settings.json` (mới, đi qua git) khai hook cùng khuôn lệnh của repo gốc. Độ trễ đo thật 0,13 giây.
- Repo gốc: chốt **BH172** chạy thêm ĐÚNG lệnh hook khai trong settings của repo y khoa (khi repo y khoa lồng trong repo gốc —
  bố cục Mac/Windows nơi bác sĩ mở phiên); bản sao trần/Cloud ⇒ ⚪ «chưa đo phiên y khoa», không xanh giả.

**Kiểm:** `tests/test_nhac_dinh_tuyen_cau_noi_20261029.py` (repo y khoa, 18 ca: repo gốc giả ở ba bố cục — lồng, worktree lồng,
worktree ngoài cây dựng bằng `git worktree` thật —, biến môi trường khai đúng/sai, thiếu một dấu hiệu, hook gốc lỗi, hook gốc
quá hạn, dữ liệu rác, chạy đúng lệnh đã khai, và với repo gốc thật khi máy có). 7 đột biến đều đỏ đúng chỗ (lần đầu đột biến
«lỗi trong cầu nối không bị nuốt» sống sót vì chưa có ca gây lỗi ngay trong cầu nối — đã thêm ca quá hạn). Chốt BH172 đo trên
năm bố cục: không có repo y khoa ⇒ ⚪ đạt; có cầu nối ⇒ đạt; thiếu settings / khai sai tên tệp / thiếu cầu nối ⇒ đỏ.

**Thứ tự gộp:** PR repo y khoa trước → `git pull` checkout `medical-ebm-automation/` trên máy → PR repo gốc (chốt BH172 đo
checkout y khoa trên đĩa; checkout cũ ⇒ chốt đỏ với lời nhắc «git pull»).

**Giới hạn còn lại:** phiên Cloud mở RIÊNG repo y khoa không có repo gốc ⇒ cầu nối im lặng (không có gì để gọi). Phiên Cloud
nhiều repo không quét hook cấp dự án (giới hạn nền tảng, CLAUDE.md §2.1).
