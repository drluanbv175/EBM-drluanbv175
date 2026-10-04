# 04/10/2026 — Làn đối chiếu skill tài khoản ↔ repo báo «0 lệch bản» giả: bộ lọc «custom» loại sạch skill của bác sĩ (BH162)

**Bác sĩ hỏi:** «Tất cả đã được đồng bộ vào các skill».

**Đo:** `python3 tools/dong_bo_tat_ca.py`
- 8/9 làn xanh: skill → Claude + Codex (50 symlink), agent, plugin, hook, bộ nhớ, kho công cụ.
- Riêng làn «Cloud ↔ repo (bundle tài khoản)» 🟡, báo «giống hệt 0 · lệch bản 0 · khác hẳn 0 · chỉ cloud 0 · chỉ repo 25».

**Nguyên nhân:**
- `tools/doi_chieu_ba_ben.doi_chieu` (mặc định `chi_custom`) chỉ giữ skill có `source == "custom"`.
- `manifest.json` thật của bundle ghi:
  - skill của bác sĩ là «plugin» (25);
  - skill Anthropic là «anthropic» (4) và «anthropic-example» (15);
  - không có «custom» nào.
- Hệ quả: mọi skill của bác sĩ bị loại khỏi phép so.

**Sự thật (đo tay cùng ngày):**
- Trong 25 skill của bác sĩ trên tài khoản: 5 giống, 20 lệch bản.
- `cap-nhat-chung-cu-y-khoa` trên tài khoản là v1.15.0 (SKILL.md 49.932 byte; cổng `verify_dashboard.py` 16 KB).
- Bản trong repo là v1.53.0 (105.815 byte; cổng 143 KB). Nghĩa là Cowork / claude.ai / Routine đang chạy cổng của tháng 9, chưa có
  mọi vá sau đó, kể cả BẢO ĐẢM ĐỌC TOÀN VĂN.
- 25 skill trong repo không có trên tài khoản, gồm `dark-analyst` và `tong-thuat-chung-cu`.

**Vá:**
- Chỉ loại nguồn Anthropic (`NGUON_ANTHROPIC`); nguồn khác hoặc vắng ⇒ của bác sĩ ⇒ phải so.
- Làn nay báo «giống 5 · lệch bản 20 · chỉ repo 25».

**Kiểm:**
- `tools/test_doi_chieu_ba_ben_nguon_plugin_20261004.py`: 2 test.
- Đột biến về bộ lọc cũ ⇒ test đỏ và BH162 đỏ.

**Chưa làm (việc của bác sĩ):**
- Bundle tài khoản chỉ cập nhật được bằng thao tác tải skill lên tài khoản claude.ai. Agent không đổi cài đặt tài khoản.
- Đẩy vào thư mục chạy cục bộ của Claude Desktop (`dong_bo_skill.py`) KHÔNG lan lên tài khoản: thư mục đó đã khớp 50/50 từ trước, mà
  bundle tài khoản vẫn là bản tháng 9.
