# RUNBOOK — sự cố đã GẶP THẬT và cách khôi phục (đúc từ CLAUDE.md, 15/08/2026)

| Sự cố | Nhận biết | Khôi phục |
|---|---|---|
| 2 máy/2 phiên ghi chồng | `.quet.lock` chặn (exit 3); OneDrive conflict-copy | `python3 tools/sync_safety_check.py`; khoá mồ côi tự hết hạn 30' |
| Chạy dữ liệu GIẢ (mock) | `kiem_nguon_that.py` đỏ ở SessionStart | sửa `~/.ebm-secrets/medical-ebm-automation.env`; KHÔNG tin báo cáo sinh lúc mock bật |
| NCBI chặn IP | rút bài vẫn chạy (nền Retraction Watch + Europe PMC) | `python tools/do_nguon_rut_bai.py` đo lại; sổ không bao giờ ghi thất bại thành công |
| Sổ cái/ledger nghi bị sửa tay | cổng nghiên cứu chặn, thông điệp nêu lý do | ký lại bằng `approve_gate.py`; xem mục niêm phong CLAUDE.md |
| Skill runtime lệch nguồn | `dong_bo_skill` báo cần đẩy/phân kỳ | `--ap-dung` (an toàn: theo NỘI DUNG, sao lưu .bak) |
| Dashboard hỏng do sửa hàng loạt | canary/BH đỏ; cổng FAIL | mọi lần sửa hàng loạt đều có `.bak-<timestamp>` cạnh file — copy ngược lại |
| Rollback ledger EBM_MASTER | — | backup tự động trước ingest; hướng dẫn trong `EBM_MASTER/tools/` |
| Retraction trên item đã APPLIED | alerts/ + quét tháng | KHÔNG tự gỡ: retract-and-replace phải đối chiếu BẢN ĐÃ THAY (BH34) — trình bác sĩ |
