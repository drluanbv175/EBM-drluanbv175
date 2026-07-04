# Biến thể "-THAONGUYEN" — đã ARCHIVE 2026-07-03

5 file agent có hậu tố `-THAONGUYEN` (bản sao/biến thể cá nhân của agent gốc) được
chuyển vào đây vì **phá bất biến filename==name** (mỗi file dùng `name:` của agent gốc)
→ chặn `sync_agents_to_codex.py` và `audit_ebm_system.py`. Không được tham chiếu/ghi
nhận ở bất kỳ tài liệu nào (README/bản đồ). Chuyển-không-xóa, đảo ngược được.

Files: cap-nhat-guideline · dao-duc-dang-ky · dieu-phoi-lam-sang · dieu-phoi-nghien-cuu · hieu-dinh-song-ngu (đều +`-THAONGUYEN`).

**Nếu là biến thể có chủ đích:** cần đặt `name:` RIÊNG khớp filename + đăng ký vào README/bản đồ
+ cập nhật bộ đếm — KHÔNG để trùng name với agent gốc. Khôi phục: `git mv` / move lại ra `.claude/agents/`.
