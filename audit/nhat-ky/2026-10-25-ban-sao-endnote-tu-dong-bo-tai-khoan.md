# 25/10/2026 — Bản sao thư viện EndNote để đo AppleScript TỰ ĐỒNG BỘ lên tài khoản EndNote online của bác sĩ

**Phát hiện.** Khi gộp hai cặp nhóm trùng tên (25/10, 06:55), EndNote đang mở HAI cửa sổ: thư viện thật và
`BanSaoDoNhom-Claude-20261024.enl` — bản sao dùng đo BH170 (24/10), nằm trong scratchpad của một phiên khác, không ai đóng. Cửa sổ
bản sao hiện «Syncing… / Retrieving references…», tài khoản bsluanbv175, «Last sync 24/10 19:51 — There are changes that need to be
sent and received»; nhóm: bản sao 159, online 155 — 4 nhóm chênh trùng với các nhóm thử sinh khi đo post vào tên đã có.
Thư viện thật cũng đồng bộ cùng tài khoản («Synced at 25/10/26, 06:44») ⇒ nếu bản sao đẩy xong, nhóm thử sẽ lan về thư viện thật.

**Xử lý.** File › Close Library trên cửa sổ bản sao → «Close Now» (không hoàn tất đồng bộ) → «No» (không đồng bộ thay đổi). Thư viện
thật đo lại sau đó: không nhóm lạ, `endnote_suc_khoe.py` 🟢. Không dùng AppleScript `close document` (làm EndNote sập).

**Bài học / luật.** Bản sao `.enl` + `.Data/sdb` MANG THEO cấu hình Sync của tài khoản ⇒ mở bản sao là tự đồng bộ lên online.
Đo hành vi AppleScript trên thư viện MỚI tạo (File › New, nhập vài bản ghi thử), không trên bản sao thư viện thật; lỡ mở bản sao
thì đóng ngay bằng «Close Now» + «No». Bộ nhớ `endnote-do-applescript-tren-ban-sao` đã đính chính.

Cần bác sĩ kiểm chứng.
