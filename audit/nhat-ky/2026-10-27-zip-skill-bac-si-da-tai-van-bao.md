# 27/10/2026 — Bác sĩ đã tải ZIP skill nhiều lần mà hệ vẫn nhắc; lịch sử thẻ hub ghi sai ngày sửa

**Phát hiện 1 — ZIP skill.** Bác sĩ hỏi: «đã tải ZIP skill nhiều lần sao vẫn báo chưa tải». Đo lại cho thấy:
- `dong_goi_skill_tai_khoan.py` xếp 44 skill vào nhóm «không đo được». Gương cục bộ của bộ skill tài khoản dừng ở lần đồng bộ 02/10, mà máy không đọc được tài khoản claude.ai.
- Hòm việc vì vậy luôn có một giác quan ⚪, và phiên Claude chép tiếp việc «tải ZIP skill» từ tệp bàn giao cũ.
- Không có chỗ nào ghi lời xác nhận của bác sĩ, nên nhắc nhở không bao giờ dứt.

**Cách vá 1.** Thêm lệnh `dong_goi_skill_tai_khoan.py --bac-si-da-tai "<nguyên văn lời bác sĩ>"`:
- Lệnh ghi mã băm mọi ZIP của lượt đóng gói hiện tại vào `CLAUDE_AI_SKILLS/.bac-si-da-tai.json`, nối thêm vào sổ, kèm lời bác sĩ và lúc ghi.
- Skill «không đo được» có ZIP cùng nội dung nằm trong sổ được xếp «bac_si_da_tai»: vẫn đóng gói để sổ lượt giữ dấu, không nhắc, và nằm riêng một nhóm trong `DANH-SACH-TAI-LEN.md`.
- Khi repo đổi nội dung skill, ZIP khác đi nên skill quay lại «cập nhật» và hòm việc nhắc như cũ.
- Thiếu lời, chưa có lượt đóng gói, hoặc sổ hỏng thì lệnh không ghi gì; sổ hỏng không bị ghi đè.
- Đã ghi lượt đầu theo lời bác sĩ «đã tải ZIP skill nhiều lần». Câu trả lời 27/10 «Có — ghi nhận cả 44» xác nhận lần tải gần nhất là sau lượt đóng gói 26/10 18:40.

**Phát hiện 2 — lịch sử thẻ hub.** Ngày 27/10 đổi quyết định hai thẻ EVID-2026-0942 và EVID-2026-1293 theo lời bác sĩ, nhưng lịch sử ghi «2026-10-26». Nguyên nhân: `manage_ledger.py set_field` lấy `meta.last_updated` (ngày nạp gần nhất của sổ) làm ngày sửa.

**Cách vá 2.** Lịch sử dùng ngày thật của lần sửa (`datetime.date.today()`). Hai dòng lịch sử ghi sai đã được chữa lại thành 2026-10-27 trong sổ thật, có sao lưu trước.

**Kiểm hồi quy.**
- Test `tools/test_dong_goi_skill_bac_si_da_tai_20261027.py` (4 ca) và `test_doi_quyet_dinh_ghi_lich_su_bang_ngay_sua`.
- 3 đột biến (bỏ phép xếp «bac_si_da_tai» · không đóng gói skill đã xác nhận · quay lại `meta.last_updated`) đều đỏ đúng chỗ rồi xanh lại.
- Trước khi thêm test mới đã chạy 40 test đóng gói skill và 11 test hub: đều đạt.
