# 23/10/2026 — Gương cục bộ bộ skill tài khoản dừng ở 02/10 ⇒ «21 skill CŨ» đỏ giả sau khi bác sĩ đã tải lên (BH168)

**Bối cảnh.** Bác sĩ: «Kiểm tra lại vì tôi đã tải lên đủ hết các skill». `tools/dong_goi_skill_tai_khoan.py --chay-kho` và dòng
hòm việc vẫn báo «cập nhật 21 · mới 23». Danh sách skill SỐNG của tài khoản (công cụ ListSkills trong phiên Claude) có đủ 44
skill, mô tả trùng bản repo hiện tại (vd mô tả `cap-nhat-chung-cu-y-khoa` trên tài khoản khác bản chụp 02/10).

**Nguyên nhân (đo 23/10).** Phép so dùng GƯƠNG cục bộ `~/.claude/skills/synced/<uuid>/` do app chép về, không phải tài khoản.
`manifest.json` ghi `lastUpdated` = 02/10/2026 21:23 (+07), gương ghi `cap-nhat-chung-cu-y-khoa` 1.15.0 trong khi repo 1.54.0;
ZIP đóng gói 21/10/2026 20:02. App không làm mới gương từ 02/10 ⇒ mọi lần tải lên sau đó đều vô hình với công cụ.

**Vá.**
- `dong_goi_skill_tai_khoan.py`: đọc tuổi gương (`moc_guong`: `lastUpdated` của manifest, lùi về giờ sửa tệp) và sổ lượt
  `.dong-goi.json` (`doc_so_luot`). Skill gương báo khác mà nội dung hiện tại TRÙNG ZIP đã đóng gói SAU lần đồng bộ gương ⇒
  trạng thái `khong_do_duoc` (⚪), không bao giờ «đã mới»; vẫn đóng gói để sổ giữ dấu. Repo đổi sau lần đóng gói ⇒ «cập nhật»
  (kể cả skill gương chưa có — đã đóng gói thì không còn là «mới, tuỳ chọn»). Gương đồng bộ SAU lần đóng gói, gương không có
  manifest, hoặc không truyền sổ ⇒ giữ nguyên phán của gương. Sổ lượt thêm `dong_goi_dau` (lúc nội dung được đóng gói LẦN ĐẦU,
  giữ qua các lượt khi ZIP không đổi) và `luc_iso`; sổ cũ thiếu khoá thì lấy `luc`. ZIP dựng bằng một hàm `_zip_byte` dùng chung
  cho ghi đĩa và phép so. Danh sách tải lên có nhóm ⚪ riêng.
- `tu_de_xuat_viec.giac_quan_skill_tai_khoan`: đọc sổ lượt mặc định `CLAUDE_AI_SKILLS/`; skill không đo được ⇒ ⚪ «giác quan
  không đo được», không vào dòng 🟡.

**Số đo sau vá (23/10, sổ thật 21/10).** 42 skill ⚪ không đo được · 4 đã mới · 2 chỉ Claude Code · 2 cập nhật THẬT:
`cap-nhat-chung-cu-y-khoa` và `dark-analyst` khác ZIP 21/10 ở `tools/verify_dashboard.py` (+ CHANGELOG) — PR #229 (miền chặn
EMA, 21/10 20:58) gộp SAU lần đóng gói ⇒ bản trên tài khoản thiếu bản vá đó; cần đóng gói lại hai skill này và tải lên.

**Giới hạn.** Máy không đọc được tài khoản; ⚪ tồn tại tới khi app làm mới gương. Bác sĩ chỉ đóng gói mà chưa tải lên thì dòng
nhắc 🟡 chuyển thành ⚪ — có chủ ý («không đo được» ≠ «ổn», không còn là «có việc chắc chắn»).

**Kiểm hồi quy.** `tools/test_dong_goi_skill_guong_cu_20261023.py` (13 test); chốt **BH168**. Đột biến 12/12 bị bắt (đổi
«không đo được» thành «đã mới», bỏ so tuổi gương, bỏ so sha, `main()` không truyền sổ, hòm việc bỏ ⚪, không giữ lúc đóng gói lần
đầu, skill mới đổi nội dung vẫn «mới», sai đơn vị mili-giây, sổ cũ không lùi `luc`, nhóm ② gộp ⚪, hòm việc không đọc sổ mặc
định, ZIP có byte thừa).
