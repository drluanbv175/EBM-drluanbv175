# 01/10/2026 — Bộ nhớ Claude của repo y khoa không bao giờ lên OneDrive: `sync_memory.py` chỉ đồng bộ bộ nhớ repo gốc (BH143)

**Triệu chứng (đo 01/10/2026 trên Mac).** `tools/sync_memory.py` (CLAUDE.md §2: «Bộ nhớ … nằm NGOÀI OneDrive →
`python3 tools/sync_memory.py` trên mỗi máy») chỉ đồng bộ MỘT thư mục: `find_local_memory()` lấy
`~/.claude/projects/<mã của …/Claude AI>/memory` (186 tệp) và mirror phẳng sang `memory-sync/`. Phiên Claude Code mở
trong repo con `medical-ebm-automation/` và mọi worktree `.claude/worktrees/*` của nó ghi bộ nhớ ở thư mục KHÁC:
`~/.claude/projects/<mã của …/Claude AI/medical-ebm-automation>/memory` (5 tệp, có `MEMORY.md` riêng: cách chạy pytest
trên Mac, hook chặn chuỗi «.env», tệp giả của test trong `data/`, kiểm PR đang mở trước khi sửa). Thư mục đó không bao
giờ lên OneDrive ⇒ sang Windows, các phiên trong repo y khoa mất toàn bộ bộ nhớ ấy. Tái hiện bằng mã cũ trên cây tạm:
chạy xong, `memory-sync/` chỉ có `MEMORY.md` của gốc.

**Nguyên nhân gốc.** Claude Code đặt bộ nhớ theo thư mục MỞ PHIÊN và quy worktree về repo chính (đọc trong mã Claude
Code 2.1.284: `defaultPath` dùng `canonicalWcRoot`), nên mỗi repo có một bộ nhớ riêng. Công cụ được viết khi chỉ có một.

**Hai lỗi đi kèm, cùng chỗ.**
1. Lối dò dự phòng cũ («chỉ một ứng viên» rồi «tên chứa claude») giờ NGUY HIỂM: thư mục của repo y khoa cũng chứa
   «Claude-AI». Tái hiện trên cây tạm (máy mà thư mục gốc chưa mang tên tính được, chỉ có bộ nhớ repo y khoa): mã cũ
   chọn bộ nhớ repo y khoa làm bộ nhớ GỐC và ghi đè `memory-sync/MEMORY.md` bằng chỉ mục của repo y khoa — máy kia kéo về
   là hỏng chỉ mục bộ nhớ gốc. Máy thật hiện chưa dính (tên tính được của gốc có sẵn trên Mac; Windows là junction).
2. `_encode()` chỉ thay `[ /\:]`, trong khi Claude Code thay MỌI ký tự ngoài `[a-zA-Z0-9]` (kể cả `.`, `(`, `)`, chữ có
   dấu), chuẩn hoá NFC, và đường dẫn dài hơn 200 ký tự thì cắt + đuôi băm hệ 36 (băm kiểu `String.hashCode`). Lệch với
   mọi đường dẫn có `.` hay `(2)` (OneDrive từng gắn ở «OneDrive-Personal(2)»).

**Vá** (`tools/sync_memory.py`): sổ `MEMORY_PROJECTS`, mỗi dự án một mirror RIÊNG — gốc ↔ `memory-sync/` (giữ nguyên, máy
chưa cập nhật vẫn kéo từ đây), repo y khoa ↔ `memory-sync/medical-ebm-automation/` (trong repo GỐC đã gitignore, KHÔNG
trong repo y khoa vì repo đó công khai; mirror gốc chỉ đọc tầng đầu nên không bao giờ thấy thư mục con này, kể cả bản cũ).
Tên thư mục theo đúng quy tắc Claude Code (`claude_project_slug`, đối chiếu 9 ca với chính đoạn JS trích từ mã Claude
Code). Dò: (1) thư mục dự án mang tên tính được có sẵn ⇒ dùng; (2) chưa có ⇒ ứng viên có `memory/` mà tên KẾT THÚC bằng
đuôi «tên thư mục gốc + đường dẫn tương đối» (`-Claude-AI`, `-Claude-AI-medical-ebm-automation`), không mang chữ
«worktrees» — đúng một thì dùng, nhiều thì KHÔNG đoán (mã 1); (3) không có ⇒ tên tính được (máy mới). Chốt chống trộn
trên đường dẫn THẬT (theo symlink/junction): hai dự án chung/lồng thư mục cục bộ, hoặc cục bộ của dự án này trùng/chứa
mirror của dự án kia ⇒ TỪ CHỐI (mã 2). `--dry-run` in từng cặp (cục bộ ↔ mirror, cách dò) và từng tệp sẽ đẩy/kéo kèm lý
do. Giữ nguyên: hai chiều, mới hơn thắng (+1 giây), KHÔNG xoá; dry-run không ghi một byte. Lỗi chép một tệp không làm sập
cả lượt (đếm, mã 1). Dry-run trên dữ liệu THẬT (chặn mọi lệnh ghi bằng hàm ném lỗi): gốc đẩy 2 tệp, repo y khoa đẩy 5 tệp
(gồm `MEMORY.md` riêng) sang mirror riêng; mã 0.

**Kiểm.** 41 test mới (`tools/test_sync_memory_repo_con_20261001.py`, chỉ thư mục tạm, ca dòng lệnh trỏ HOME/USERPROFILE
sang tmp — không chạm `~/.claude` thật; 3 ca cần symlink tự bỏ qua có khai báo nếu máy không cho tạo). `pytest tools/`
1882 đạt, 33 bỏ qua có khai báo, 0 lỗi. Đột biến (`python -B`, xoá `__pycache__`, sao lưu ở `~/.ebm-worktrees/`, phục hồi
khớp SHA-256) 27/27 đỏ đúng chỗ; chốt BH143 tự đỏ với 6 đột biến cốt lõi (quy tắc mã hoá cũ · bỏ loại worktree · lối «tên
chứa claude» · bỏ chặn trùng thư mục · mirror phẳng · hạ mã từ chối). Ruff (đích py311) sạch phần thêm; chốt đa nền 🔴 0.

**Chưa làm / giới hạn.** Không đọc `CLAUDE_CONFIG_DIR` hay cài đặt `autoMemoryDirectory` của Claude Code (máy bác sĩ
không đặt). Vẫn chỉ đồng bộ tệp `.md`/`.json` ở tầng đầu như bản cũ. Làn «Bộ nhớ Claude» của `dong_bo_tat_ca.py` ở chế
độ KIỂM vẫn báo 🟢 dù còn tệp chưa đồng bộ (mã 0 khi dry-run — giữ nguyên hành vi cũ, hook mở phiên không bị làm ồn).
Chưa chạy trên Windows thật: sau khi gộp, chạy `python3 tools/sync_memory.py` trên Mac rồi (OneDrive xanh) trên Windows.

**Ghi vào đâu.** Mục này ở `audit/nhat-ky/` theo quy ước «mỗi sự cố một tệp» bác sĩ chọn 01/10 (nhánh
`claude/nhat-ky-moi-su-co-mot-tep-20261001`, chưa gộp lúc viết) để không thành PR thứ tư cùng nối cuối
`audit/NHAT-KY-SU-CO.md` (PR #75, #76 đang mở). Nếu quy ước đó không được gộp, chép nguyên khối này vào mục «SAU
24/09/2026» của tệp cũ (đổi `#` thành `###`).
