---
name: quan-ly-cap-nhat-ebm
description: Sử dụng skill này khi bác sĩ muốn QUẢN LÝ kho cập nhật EBM đã lưu (sổ cái EBM_MASTER) — xem tổng quan, tìm/lọc, duyệt và phê chuẩn các cập nhật. Kích hoạt với "quản lý EBM", "xem các cập nhật", "hàng đợi duyệt", "duyệt thẻ…", "thống kê sổ cái", "tìm cập nhật về…", "loại thẻ nhiễu". Đây KHÔNG phải skill tạo cập nhật mới (dùng cap-nhat-chung-cu-y-khoa) — skill này quản lý cái ĐÃ lưu.
metadata:
  version: 1.0.0
---

# Skill: Quản lý kho cập nhật EBM (sổ cái EBM_MASTER)

## Mục đích
Cho bác sĩ quản lý ngay trong Claude các cập nhật đã tích lũy ở sổ cái trung tâm
`OneDrive/Claude AI/EBM_MASTER/EBM_MASTER.json`: XEM · TÌM · LỌC · DUYỆT.
Engine quét hằng tuần/tháng đổ thẻ "chưa xác minh" vào hàng đợi → bác sĩ duyệt ở đây.

## Công cụ (luôn `cd` vào thư mục hub trước)
Thư mục: `/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal(2)/Claude AI/EBM_MASTER`
Chạy: `python3 tools/manage_ledger.py <lệnh>`

| Bác sĩ nói | Lệnh chạy |
|---|---|
| "thống kê / tổng quan sổ cái" | `stats` |
| "lập danh mục / danh mục cây / xem theo chuyên khoa" | `tree` (sinh `DANH_MUC.md`: Chuyên khoa→Quyết định→thẻ) |
| "hàng đợi duyệt / có gì chờ duyệt" | `queue` |
| "xem các cập nhật mới nhất" | `list 20` |
| "tìm cập nhật về <X>" | `search <X>` |
| "xem chi tiết thẻ <ID>" | `show <ID>` |
| "duyệt / xác minh thẻ <ID>" | `approve <ID> [ID...]` |
| "cho áp dụng thẻ <ID>" | `apply <ID>` |
| "chuyển thẻ <ID> sang cân nhắc / chưa áp dụng" | `consider <ID>` / `notyet <ID>` |
| "loại thẻ nhiễu <ID>" | `drop <ID> <lý do>` |
| "cập nhật lại WebApp" | `regen` |

## Quy trình & an toàn (bắt buộc)
1. Khi bác sĩ muốn quản lý → mặc định chạy `stats` rồi `queue` để cho thấy bức tranh + việc cần duyệt.
2. **Thao tác SỬA** (`approve`/`apply`/`consider`/`notyet`/`drop`): mỗi lệnh tự BACKUP sổ cái + ghi history. Trước khi `approve`/`apply` một thẻ, nhắc bác sĩ rằng điều đó nghĩa là **bác sĩ đã đối chiếu nguồn** (mở PMID/DOI) — KHÔNG tự duyệt thay bác sĩ.
3. Sau khi sửa loạt thẻ → chạy `regen` để EBM_WEBAPP.html phản ánh trạng thái mới.
4. Trình bày kết quả gọn dạng bảng; với mỗi thẻ luôn cho thấy ID + quyết định + trạng thái xác minh + nguồn (PMID/DOI).
5. Liêm chính: KHÔNG bịa; "áp dụng" chỉ sau khi bác sĩ xác nhận; kèm nhắc "Cần bác sĩ kiểm chứng"; KHÔNG PII.

## Liên hệ
- Tạo cập nhật mới: skill `cap-nhat-chung-cu-y-khoa`.
- Engine tự đổ thẻ vào qua cầu nối `bridge_to_ebm_master.py`, kích hoạt bằng scheduled-task `thu-thap-tuan-an-toan-thuoc`/`cap-nhat-thang-ebm` (launchd `weeklysafety`/`monthlyupdate` cũ đã TẮT từ 15/08/2026).
- Bản đồ hệ thống: `Claude AI/HE-THONG-EBM.md`; cách dùng nhanh: `Claude AI/CACH-DUNG.md`.
