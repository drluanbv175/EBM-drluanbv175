# 07/11/2026 — EndNote: gắn nhầm tag khi Find Full Text đang chạy; nhóm hệ thống làm kế hoạch báo giả

Bổ sung cho `2026-11-07-endnote-ban-ghi-chua-phan-loai.md` (đã gộp ở PR #303).

- Lượt đưa 9151 (tóm tắt chủ đề Sỏi thận) vào nhóm 38: một lần thả rơi trúng «Update HPQ».
- Lúc đó bác sĩ đang chạy Find Full Text. EndNote sinh các nhóm hệ thống «Searching…» / «Not found» / «Found PDF» / «Found URL» (loại
  `TYPE;7`). Mỗi lần kết quả cập nhật, EndNote dựng lại thanh bên, cuộn về cuối và trả danh sách về đủ 3.545 bản ghi, nên toạ độ
  đo một nhịp trước đó đã lệch.
- Đã gỡ ngay ở chế độ nền: References › Edit Reference → bấm × trên chip tag. Hộp «Manage tags» thì bị từ chối ở chế độ nền vì
  vùng chip thuộc tiến trình khác. Đối chiếu với bản sao lưu trước lượt: chỉ 9151 đổi, đúng 2 tag dự kiến.
- Vá:
  - kế hoạch chỉ coi nhóm loại `custom` là chỗ phân loại; nhóm hệ thống thì bỏ qua (trước đó báo 4 nhóm 👤 giả);
  - `--huong-dan` thêm ba điều: zoom hai lần liền nhau ngay trước khi thả và hai ảnh phải trùng; Find Full Text đang chạy thì hoãn
    kéo-thả; thả cách mép thanh bên ≥ 60 px;
  - thêm cách gỡ tag ở chế độ nền.
