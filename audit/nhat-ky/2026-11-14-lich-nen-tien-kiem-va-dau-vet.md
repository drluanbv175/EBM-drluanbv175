# 14/11/2026 — Lịch nền gãy âm thầm: lượt tháng sẽ bị cắt ngang, tác vụ kỹ thuật không canh được (mở rộng BH173)

**Đo 14/11/2026 (cây chính, Mac):**

1. `python3 tools/quyen_lich_nen.py` ⇒ 🔴 mã 1, «máy chưa áp: `Bash(python3 tools/xuat_goi_cap_nhat.py EBM-Dashboards/*.html
   --online --khong-endnote)`». Lượt tháng `cap-nhat-thang-ebm` kỳ 01/12 sẽ chạy bước 1–4 (watermark/con trỏ dịch) rồi bị
   cắt ngang ở bước gói duyệt mà bộ lập lịch vẫn ghi «succeeded» — đúng kiểu BH173 (W44).
2. `python3 tools/kiem_lich_nen.py` ⇒ «⚪ kiem-tra-hoan-thien-he-thong-thang: chưa khai dấu vết máy-đọc-được — không canh
   được» (sổ kỳ vọng khai `dau_vet: khong-co`): tác vụ bị xoá/tắt/cắt ngang đều vô hình.
3. Sổ xác minh nguồn: 97 mục chưa/hết hạn; tác vụ tháng không có bước làm mới định kỳ.

**Vá (PR nhánh `claude/lich-nen-tien-kiem-20261114`):**

- Tác vụ tháng có **bước 0 tiền kiểm**: `quyen_lich_nen.py --tac-vu cap-nhat-thang-ebm,goi-duyet-tuan-ebm` (cờ mới — chỉ xét
  lệnh lượt này thi hành; đo cả tập sẽ dừng oan bộ thu thập an toàn thuốc vì quy tắc của tác vụ khác) + `kiem_lich_nen.py`
  (chỉ báo). Mã 1/2 ⇒ DỪNG lượt trước bước 1, báo cáo + một dòng `alerts/<ngày>.md`.
- **Bước 4b** `so_xac_minh_nguon.py --vong 3` sau nhịp liêm chính (chỉ ghi THÀNH CÔNG; lỗi mạng không làm hỏng lượt).
- Công cụ mới `tools/ghi_dau_vet_lich.py`: lệnh đầu lượt ghi BẮT ĐẦU, lệnh cuối lượt ghi KẾT THÚC (giờ do máy lấy) vào log
  khai ở sổ kỳ vọng; chỉ ghi cho tác vụ tự khai `ghi_boi`, chỉ dưới `state/`. Cảm biến báo rõ «có BẮT ĐẦU nhưng KHÔNG có
  KẾT THÚC — lượt bị cắt ngang» thay vì «không có dấu vết».

**Bài học phụ (kiểm đột biến):** ở đột biến «bỏ rào `ghi_boi`», test gọi `main` trên repo thật đã GHI dòng KẾT THÚC giả vào
`state/kiem-rut-bai-kho.log` của worktree. Chạy trong cây chính khi rào hỏng, chính test sẽ giả dấu vết kỳ lỡ ⇒ test phải
chạy `main` trên bản sao tạm của sổ kỳ vọng thật; công cụ đọc `GOC` lúc gọi để test vá được.

**Kiểm hồi quy:** `tools/test_lich_nen_tien_kiem_20261114.py` (23 test) + test BH173 cũ; chốt BH173 mở rộng (5)–(7); 15 phép
đột biến đều đỏ đúng chỗ rồi xanh lại.

**Việc của bác sĩ sau khi gộp:** `python3 tools/quyen_lich_nen.py --ap-dung` (đo 14/11 với tệp khai mới: 6 dòng «máy chưa
áp» = 5 lệnh mới + lệnh `--khong-endnote` còn thiếu từ trước), rồi chép hai SKILL.md từ `sync/scheduled-tasks/` sang runtime trước kỳ 01/12.
