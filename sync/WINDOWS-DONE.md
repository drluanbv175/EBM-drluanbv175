# ✅ Windows đã xong phần memory (2026-06-07)

Phản hồi cho `WINDOWS-PASTE-ME.md` từ phía Mac. Đã thực hiện trên Windows:

1. **Junction đã tạo:**
   `C:\Users\Admin\.claude\projects\C--Users-Admin-OneDrive-Claude-AI\memory`
   → trỏ tới `C:\Users\Admin\OneDrive\Claude AI\sync\memory` (reparse point, không cần admin).

2. **Kiểm chứng:**
   - Đọc xuyên junction OK (write-through test pass).
   - Đếm được **5 file .md** trong hub: `MEMORY.md`, `claude-code-harness-install.md`,
     `project-medical-ebm-automation.md`, `user-clinician-ebm.md`, `project-mac-windows-sync.md`.
   - `MEMORY.md` có đủ 4 mục index.
   - Bản memory cũ (chỉ có harness-install) đã được khôi phục đầy đủ; backup cũ giữ ở
     `...\projects\C--Users-Admin-OneDrive-Claude-AI\memory.bak-20260607-070356`.

3. **Đã ghim** thư mục `sync\memory` = "Always keep on this device" (Pinned, đọc được offline).

→ Memory giờ dùng chung 2 chiều Mac ↔ Windows qua hub OneDrive. Viết ở máy nào cũng tự sync.

_(Việc còn lại KHÁC memory: tab Code/Cowork trên Windows thiếu so với Mac — cần kiểm tra TÀI KHOẢN đăng nhập app Claude trên Windows, không liên quan OneDrive.)_
