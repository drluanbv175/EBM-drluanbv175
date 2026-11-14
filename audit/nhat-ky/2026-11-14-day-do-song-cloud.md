# 14/11/2026 — Dữ liệu đo sống nằm chờ trên Mac 9 ngày: thêm bước tự đẩy lên GitHub

**Đo:** khi đồng bộ Cloud ↔ Mac 14/11, cây gốc trên Mac có 7 tệp đo sống chưa commit (`cloud-mirror/trang-thai-chung-cu.json`,
`data/sources.json`, `quality/eval/negative/mau-thuan-quet-that.log`, `alerts/2026-11-05|09|12|13.md`) — cảnh báo cũ nhất từ
05/11. Hook SessionStart của Mac sinh lại gương mỗi phiên nhưng không gì commit/đẩy, nên phiên Cloud nhìn trạng thái cũ 9 ngày
(họ BH41). Bác sĩ commit tay (`e98da81`).

**Quyết định của bác sĩ (14/11/2026):** kho chứng cứ giữ đồng bộ MỘT CHIỀU — chọn «Một chiều + tự động». Căn cứ: hai repo GitHub
đều CÔNG KHAI (đo bằng danh sách repo), toàn văn/EndNote có bản quyền và chỉ dùng cá nhân ⇒ không đưa kho lên git; Cloud chỉ đọc
bản tóm tắt.

**Vá:** `tools/day_do_song_cloud.py` — chỉ commit danh sách trắng đo sống (tệp khác để nguyên), rào Cloud / vắng EBM-Dashboards /
sai nhánh / không tua nhanh được / `sync_safety_check` 🔴, commit qua hook pre-commit, chỉ đẩy khi mọi commit chưa lên origin đều
chỉ chạm danh sách trắng, đẩy lỗi thì giữ commit cho lượt sau. Nối vào `tools/tu_sua_chua.py` (`VIEC_MAY`, không chạy trên Cloud)
⇒ mỗi phiên Mac tự chạy qua hook SessionStart.

**Kiểm:** `tools/test_day_do_song_cloud_20261114.py` 7 ca trên repo git tạm (remote trần); đột biến bỏ lọc danh sách trắng / rào
Cloud / chặn commit lạ / rào an toàn / nối tu_sua_chua ⇒ mỗi phép đỏ đúng 1 ca, phục hồi xanh 7/7. Chưa chạy trên Mac thật.
