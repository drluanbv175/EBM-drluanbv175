# 24/10/2026 — Điều khiển EndNote chạy nền: Select All bị khoá, menu kẹt ở chế độ Thùng rác (chỉ còn «Delete References…»)

**Bối cảnh.** Bác sĩ giao máy bấm «Move References to Trash» cho nhóm «_Cho thung rac 2026-10-24» và «Delete Group» 5 nhóm.
Bác sĩ không duyệt kịp quyền điều khiển toàn màn hình (hết giờ chờ), nên máy dùng công cụ chạy nền (`app_*`).

**Đo được.**
- Chạy nền: Edit › Select All bị TẮT; phím ⌘A không có tác dụng; chọn dòng bằng truy cập trợ năng thì THAY lựa chọn, không cộng
  dồn; shift+mũi tên đi vào ô đang có focus (lần đó là khung nhóm, đổi nhóm đang chọn — không đổi dữ liệu).
- Cách chắc đã dùng: chọn nhóm ở khung trái → chọn dòng đầu → References › Move References to Trash → lặp lại. Đã chuyển 8 bản ghi
  trùng; đo lại `sdb.eni`: bản trùng `trash_state=1`, bản giữ còn nguyên. Delete Group: gõ tên vào «Search for group», bung group set,
  chọn nhóm, Groups › Delete Group, hộp xác nhận ghi «references will not be deleted».
- Lượt sau cùng ngày (2 bản ghi bác sĩ loại): sau khi công cụ MCP đưa EndNote lên trước, menu References đọc qua chạy nền KẸT ở bộ
  mục của chế độ Thùng rác («Delete References…», «Restore to Library») dù màn hình đang ở nhóm và cả ở «All References».
  «Delete References…» trong Thùng rác = XOÁ VĨNH VIỄN ⇒ máy DỪNG, nhả quyền điều khiển, giao bác sĩ bấm.

**Luật rút ra.**
- Trước MỖI lệnh menu References khi chạy nền phải `list` menu và thấy đúng «Move References to Trash». Thấy «Delete References…»
  ⇒ dừng, không thử lại bằng cách khác.
- Nhóm EndNote đăng lại bằng `post` nằm ở gốc «My Groups», không vào group set cũ; xếp lại là việc kéo thả của bác sĩ.

**Bộ nhớ.** `endnote-dieu-khien-nen-tung-ban-ghi` (bộ nhớ dự án y khoa). Không có thay đổi mã; AppleScript `delete record` vẫn bị
cấm (`endnote-delete-record-xoa-han`).
