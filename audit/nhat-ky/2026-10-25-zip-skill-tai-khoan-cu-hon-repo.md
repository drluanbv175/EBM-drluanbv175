# 25/10/2026 — Bác sĩ tải ZIP skill lên nhiều lần mà hòm việc vẫn báo «skill tài khoản CŨ»: ZIP chưa được đóng lại sau khi repo đổi

**Triệu chứng (lời bác sĩ).** «2 skill trên tài khoản claude.ai đã cũ (cap-nhat-chung-cu-y-khoa, dark-analyst) … tôi đã tải lên nhiều
lần nhưng vẫn báo chưa tải».

**Đo (25/10, 06:48).** ZIP trong `CLAUDE_AI_SKILLS/` đóng gói 23/10 22:02; repo đổi hai skill ngày 24/10 (#242, #243). `danh_gia` xếp
«cap_nhat — đã đóng gói 2026-10-23 …, repo đổi sau đó ⇒ tải bản mới». Câu hòm việc chỉ nói «bác sĩ tải ZIP lên» ⇒ bác sĩ tải lại
ĐÚNG ZIP 23/10 (bản cũ) ⇒ cảnh báo đúng mà không hết. Gương bộ skill tài khoản `~/.claude/skills/synced/<uuid>` vẫn dừng ở 02/10
(BH168) nên máy không bao giờ thấy được lần tải lên nào.

**Vá.**
- `tools/dong_goi_skill_tai_khoan.py`: `can_dong_goi_lai()` + `--im-khi-on` (mã 1 + một dòng khi ZIP trong sổ lượt khác nội dung
  repo/chưa có; chỉ kiểm, không ghi; thiếu gương ⇒ 0 vì hòm việc đã báo ⚪ riêng).
- `tools/tu_sua_chua.py`: mục mới tự đóng lại ZIP khi repo đổi (sửa = chạy đóng gói; chỉ ghi `CLAUDE_AI_SKILLS/`, ngoài git;
  Cloud=False). Tải lên tài khoản vẫn là việc của bác sĩ.
- `tools/tu_de_xuat_viec.py`: dòng 🟡 nói rõ MÁY đóng lại ZIP trước, «tải lại ZIP cũ … không hết cảnh báo»; dòng ⚪ nêu tên + giờ
  ZIP đóng gói MỚI NHẤT để bác sĩ biết tải đúng tệp nào.
- ZIP mới của hai skill đã đóng 25/10 06:49.

**Kiểm.** `tools/test_dong_goi_skill_dong_lai_zip_20261025.py` (8 ca), 7 đột biến đều đỏ; 28 ca cũ của hai tệp test đóng gói xanh.

Cần bác sĩ kiểm chứng.
