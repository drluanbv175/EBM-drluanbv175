# Nhật ký sự cố — mỗi sự cố MỘT TỆP (từ 01/10/2026)

Thư mục này nhận mọi sự cố / bài học MỚI từ 01/10/2026. Lịch sử trước đó nằm nguyên văn ở
`audit/NHAT-KY-SU-CO.md` — tệp đó đã **ĐÓNG BĂNG** (chốt băm `nhat_ky_su_co` trong
`tools/verify_claude_code_repo_alignment.py`, chạy ở pre-commit).

**Vì sao:** từ 24/09 mọi PR nối mục vào cuối cùng một tệp, nên hai PR mở song song gần như chắc
xung đột ở đó và phải gộp tay (số đo và lý do chọn: `2026-10-01-xung-dot-gop-nhat-ky-chung.md`).
Hai PR ghi hai tệp khác tên thì không bao giờ xung đột, kể cả trên GitHub.

## Quy ước (chốt kiểm tự động)

1. **Tên tệp:** `YYYY-MM-DD-<slug>.md` — ngày có thật; slug chữ thường không dấu, số, nối bằng
   một gạch (vd `2026-10-01-xung-dot-gop-nhat-ky-chung.md`). Hai sự cố cùng ngày ⇒ hai slug khác nhau.
2. **Dòng đầu:** `# DD/MM/YYYY — <tiêu đề>`, ngày TRÙNG ngày trong tên tệp (để
   `grep -rn "01/10/2026"` ra mục mới giống hệt cách tra mục cũ).
3. Chỉ tệp `.md` nằm thẳng trong thư mục; không thư mục con. Tệp ẩn (`.DS_Store`) được bỏ qua;
   bản sao xung đột OneDrive kiểu «… 2.md» bị chốt báo — đúng ý.

## Nội dung một mục (giữ khung cũ)

Ngày · mã BH nếu có · nguyên nhân · cách vá · kiểm hồi quy (test, đột biến, chốt BH). Ghi số đo
kèm ngày đo — số đo là ẢNH CHỤP, không trích lại làm hiện trạng.

- **Bổ sung / đính chính** cho một sự cố đã merge: ưu tiên tệp MỚI (ngày mới) trỏ tới tệp gốc.
  Sửa thẳng tệp đã merge chỉ khi sửa lỗi chép; nếu hai PR cùng sửa một tệp, git BÁO xung đột
  (không gộp ngầm) — đó là điều mong muốn.
- **CLAUDE.md** chỉ nhận LUẬT THƯỜNG TRỰC mới sinh ra từ sự cố, viết gọn 1–3 dòng.

## Tra cứu

- `grep -rn "<từ khoá>" audit/NHAT-KY-SU-CO.md audit/nhat-ky/` — không đọc cả tệp cũ (~100k token).
- `python3 tools/muc_luc_nhat_ky.py [từ khoá]` — in mục lục (mới nhất trước) và kiểm quy ước.
  **Mục lục KHÔNG commit:** một tệp mục lục chung mà PR nào cũng sửa sẽ thành điểm nóng xung đột mới.

## Nhánh mở TRƯỚC khi đóng băng vẫn nối vào tệp cũ

Chốt `nhat_ky_su_co` báo FAIL. Cách xử lý:

1. `git diff origin/master -- audit/NHAT-KY-SU-CO.md` để thấy khối nhánh đã nối thêm.
2. Chép khối đó NGUYÊN VĂN sang tệp mới đúng quy ước (đổi `### DD/MM/YYYY — …` thành `# DD/MM/YYYY — …`).
3. `git checkout origin/master -- audit/NHAT-KY-SU-CO.md` để trả tệp cũ về bản đóng băng.

Không đổi hằng băm `NHAT_KY_CU_SHA256` để «cho qua» — đổi hằng chỉ trong PR có lý do ghi rõ.
