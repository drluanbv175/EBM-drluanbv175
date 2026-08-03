# Dán nội dung dưới đây vào Claude Code trên máy WINDOWS

> Mở Claude Code trong thư mục `Claude AI` trên Windows, rồi dán nguyên khối chữ
> giữa hai vạch `---` bên dưới. Claude sẽ tự tạo junction memory và kiểm chứng.

---

Tôi đang đồng bộ "trí nhớ" (memory) của Claude giữa Mac và Windows qua OneDrive. Phía Mac đã xong: thư mục memory chung nằm ở `OneDrive\Claude AI\sync\memory\`. Trên máy Windows này, hãy:

1. Chạy script tạo junction (KHÔNG cần quyền admin) để trỏ memory cục bộ của Windows vào hub chung:
   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\OneDrive\Claude AI\sync\link-memory.ps1"
   ```
   (Nếu đường dẫn OneDrive khác, hãy tự tìm file `link-memory.ps1` trong thư mục `Claude AI\sync\` rồi chạy.)

2. Sau khi chạy, kiểm chứng giúp tôi:
   - Liệt kê `%USERPROFILE%\.claude\projects\*Claude-AI\memory` và xác nhận nó là một **junction/reparse point** trỏ tới `...\OneDrive\Claude AI\sync\memory`.
   - Xác nhận thấy đủ các file `.md` trong đó (ít nhất: `MEMORY.md`, `project-medical-ebm-automation.md`, `user-clinician-ebm.md`, `project-mac-windows-sync.md`).
   - Đọc thử `MEMORY.md` qua đường dẫn cục bộ đó để chắc đọc xuyên junction được.

3. Báo lại kết quả ngắn gọn (đã tạo junction chưa, đếm được mấy file).

Lưu ý: nếu trên Windows này trước đó đã có memory thật, script tự sao lưu thành `memory.bak-...` và gộp các file còn thiếu vào hub trước khi tạo junction, nên không mất dữ liệu.

---

## Sau khi xong (làm 1 lần, trong File Explorer)
Chuột phải thư mục `OneDrive\Claude AI\sync\memory` → **"Always keep on this device"** (Luôn giữ trên thiết bị này) để memory luôn đọc được kể cả khi offline.
