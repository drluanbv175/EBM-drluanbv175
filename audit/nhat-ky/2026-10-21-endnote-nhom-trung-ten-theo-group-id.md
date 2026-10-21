# 21/10/2026 — EndNote: nhóm trùng tên bị báo thành MỘT nhóm (AppleScript trả hợp) ⇒ đo theo group_id, chặn ghi (BH167)

## Sự cố
- Thư viện có 2 nhóm «EBM · Biến chứng thần kinh ở bệnh nhân đái tháo đường — …» (group_id 114: 5 bài, 162: 4 bài), nhưng
  công cụ MCP `endnote_nhom` báo 1 tên, 9 bài ⇒ tưởng việc gộp đã xong.
- Nguyên nhân: `endnote_nhom` đi qua AppleScript, mà EndNote chỉ gọi nhóm theo TÊN — `get records in "<tên>"` trả HỢP mọi nhóm
  cùng tên; danh sách tên lại khử trùng bằng `dict.fromkeys`. Công cụ ghi `endnote_dua_vao_nhom` cũng đếm lại bằng đúng lệnh đó.
- Liên quan: `post records … as "<tên>" of type "CUSTOM"` vào tên đã có nhóm từng TẠO NHÓM MỚI cùng tên (đo 18/10/2026);
  khi chưa có nhóm cùng tên thì tạo đúng MỘT nhóm (đo 21/10/2026, group 171).

## Đo (21/10/2026, bản sao tạm của `sdb.eni`, chỉ đọc)
- `sdb.eni` 19,6 MB, chế độ nhật ký rollback (không có -wal/-shm lúc đo). Bảng `groups`: 171 nhóm — 166 `TYPE;3` (tự tạo),
  5 `TYPE;6` (tìm trực tuyến). 9 tên đang có ≥2 nhóm, trong đó «Điều trị viêm gan B mạn…» có 4 nhóm (1 + 0 + 23 + 0 bài).
- `members` = 4 byte phiên bản + số lượng (uint32 LE) + từng recNum (uint32 LE) — khớp đo 19/10.

## Đã làm
- `tools/endnote_suc_khoe.py`: `ban_sao_csdl` chép sdb.eni (+ -wal/-shm/-journal nếu có) ra thư mục tạm rồi mới mở `mode=ro`;
  tệp gốc đổi trong lúc chép ⇒ chép lại, vẫn đổi ⇒ KHÔNG ĐO ĐƯỢC. `doc_nhom` / `nhom_theo_ten` / `nhom_trung_ten` trả từng nhóm
  theo group_id (không bao giờ cộng thành viên); thành viên không giải được ⇒ `loi`, không phải nhóm rỗng. `tinh_trang` có
  `nhom_trung_ten` (None khi không đo được).
- `tools/mcp/endnote_ebm_mcp.py` (1.1.0): `endnote_nhom` đọc sdb.eni (không cần EndNote mở), mỗi nhóm kèm số bài + cờ
  `trung_ten`; tên trùng ⇒ từng nhóm riêng + cảnh báo. `endnote_dua_vao_nhom` TỪ CHỐI (cả chạy khô) khi tên đích có ≥2 nhóm
  hoặc không đọc được sdb.eni; ghi xong đo lại theo group_id, báo `nhom_moi_tao` khi post sinh nhóm mới cùng tên.
  `endnote_trang_thai` có `nhom_trung_ten`.
- Không thêm công cụ xoá; không ghi sdb.eni.

## Kiểm hồi quy
- `tools/test_endnote_nhom_trung_ten_20261021.py` (15 test, sqlite giả, gồm ca dữ liệu chỉ nằm trong -wal).
- Đột biến: 11/11 phép bị bắt đúng test (ngưỡng trùng, bỏ chặn ghi, không chép -wal, khoá tên không NFC/casefold, không đo
  được ⇒ coi rỗng, nhom_moi_tao sai, bỏ so dấu tệp, mở tệp thật, trạng thái thiếu danh sách, chạy khô bỏ kiểm, thành viên hỏng
  ⇒ rỗng); chốt BH167 bắt 3/3 (bỏ chặn ghi, trạng thái thiếu, cộng thành viên cùng tên).

## Còn lại cho bác sĩ
Gộp 9 tên trùng hiện có vẫn là việc trên giao diện EndNote: xoá HẾT các nhóm cùng tên (bài không mất) → máy đăng lại toàn bộ
recNum (lấy từ `endnote_nhom` với `ten_nhom` TRƯỚC khi xoá) → đo lại theo group_id.
