# 19/10/2026 — Nút «Chuyen Nhom Vao Thung Rac.command» bấm đúp không chạy: git không ghi bit thực thi (BH166)

**Mã chốt:** BH166 (mới) · liên quan PR #214 (kết nối EndNote ↔ Claude).

## Bác sĩ báo
«Chuyen Nhom Vao Thung Rac.command ấn vào không được» — ngay sau khi gộp PR #214.

## Đo
- `git ls-files -s` cho thấy tệp mang chế độ `100644`, còn trên đĩa là `-rw-r--r--`. Các nút cũ, ví dụ `Phat Khoa Ed25519.command`, mang `100755`.
- Repo gốc đặt `core.fileMode=false`. Khi soạn PR #214, `chmod +x` trong worktree không được git ghi lại. Commit lưu `100644`, nên máy kéo master về nhận tệp không có quyền chạy.
- Quét toàn repo còn thêm một nút cùng lỗi: `sync/Vá Route Scopus Qua VPN.command`.

## Đã làm
- Gắn lại bit thực thi cho hai tệp: `git update-index --chmod=+x`. Trên máy Mac của bác sĩ, tôi cũng đã `chmod +x` ngay để nút dùng được trước khi PR được gộp.
- Thêm vào `.githooks/pre-commit` một khối CHẶN commit khi có tệp `.command` trong index không mang `100755`. Lệnh in tên tệp kèm cách sửa và hiển thị đúng tên có dấu (`core.quotePath=false`).
- Thêm chốt BH166 vào `tools/chot_hoi_quy_bai_hoc.py`, kiểm hai điều:
  - mọi tệp `.command` đã track mang `100755` trong index;
  - pre-commit còn dòng THI HÀNH chặn lỗi này (dòng chú thích không tính).

## Kiểm
- BH166 xanh: 9 tệp `.command` đều mang `100755`.
- Đột biến «bỏ bit một tệp» ⇒ đỏ, đúng tên tệp.
- Đột biến «biến dòng chặn thành chú thích» ⇒ đỏ.
- Khối pre-commit với một tệp `100644` ⇒ «CHAN COMMIT», mã 1.
- Phục hồi ⇒ xanh.

## Bài học
Repo đặt `core.fileMode=false` thì quyền chạy phải ghi bằng `git update-index --chmod=+x` (hoặc `git add --chmod=+x`), không bằng `chmod`. Mọi nút bấm đúp mới phải kiểm `git ls-files -s` trước khi mở PR.
