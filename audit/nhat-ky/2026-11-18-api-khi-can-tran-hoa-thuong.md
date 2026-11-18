# 18/11/2026 — Cơ chế API khi cần bỏ sót thông điệp vượt trần viết hoa

Bổ sung cho `2026-11-18-api-claude-tu-chay-khi-can.md` (gốc #423).

**Phát hiện:**
- Sau khi y khoa #306 gộp, tôi đọc nguyên văn các thông điệp `HetNganSach` của `tools/api_claude_nc.py`.
- Thông điệp vượt trần chính mở đầu bằng chữ hoa: «Trần chi phí Claude API tháng …: đã dùng …/… USD … ⇒ vượt trần».
- `api_khi_can.chay_de_cuong` so phân biệt hoa thường với «trần chi phí», nên bỏ sót thông điệp này.

**Hậu quả nếu xảy ra:**
- Không tốn tiền: cầu nối vẫn từ chối gửi.
- Nhưng cơ chế thử tiếp mọi việc đề cương còn lại thay vì dừng, và sổ không ghi lý do «chạm trần».

**Vá:**
- So CHỮ THƯỜNG với `DAU_HIEU_HET_TRAN`.
- Test dùng đúng ba thông điệp thật của cầu nối.
- Đột biến bỏ chữ thường hoá ⇒ 2 test đỏ (hai thông điệp «Trần» viết hoa), đúng chỗ.
- Kèm: đổi tên tham số lambda `l` → `lenh` trong test của #423 (ruff E741).

**Bài học:** nối với thông điệp của công cụ phiên khác thì đọc NGUYÊN VĂN thông điệp ở mã đã gộp, đừng đoán từ mô tả PR.
