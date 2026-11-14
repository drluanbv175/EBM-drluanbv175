# 14/11/2026 — Sổ xác minh nguồn sau thẩm định #355: ảnh gốc không có test, gộp hai dương tính không so mốc, dương tính mới mất im lặng khi khoá bận

Tệp gốc của sự cố: `2026-11-14-so-xac-minh-khoa-ghi.md` (PR #355, đã gộp `eb28473`). Người thẩm định #355 kết luận ĐẠT
nhưng để lại bốn việc mức thấp. Tệp này ghi phần vá cho cả bốn.

## 1. Đột biến M4 sống sót: bước làm mới ảnh gốc không có test nào giữ

Cuối `ghi_so` có dòng `so._anh_goc = du_lieu.encode("utf-8")`. Người thẩm định xoá dòng đó thì cả 83 test sổ vẫn xanh,
trong khi hành vi đã sai thật. Một tiến trình thêm bản ghi `pmid:2` và trường `tam`, ghi sổ, rồi xoá cả hai và ghi lần nữa.
Lần ghi thứ hai so với ảnh gốc CŨ (lúc chưa có hai thứ đó), nên coi chúng là «do tiến trình khác thêm» và giữ lại: hai thứ
đã xoá hiện lại trên đĩa. Nhật ký #355 ghi «17/17 đột biến bị bắt», nhưng danh sách 17 phép đó không có phép này.

Vá: chỉ thêm test, không đổi mã. Có hai ca:
- Một tiến trình: thêm, ghi, xoá, ghi, rồi kiểm cả đĩa lẫn bộ nhớ.
- Hai tiến trình thật trên sổ tạm: A ghi lần 1, B chen vào ghi `pmid:3`, rồi A xoá và ghi lần 2 (đi đường gộp).

Đột biến M4 làm cả hai ca ĐỎ, với đúng thông điệp «hồi sinh».

## 2. Hai bên cùng dương tính: docstring nói «của ta mới hơn» nhưng mã không so mốc

Luật 3 của `_gop_ban_ghi` ghi «Cả hai cùng dương tính ⇒ phán quyết của ta (mới hơn) thắng». Thực ra mã không so
`kiem_rut_luc`, nên phán quyết của ta thắng kể cả khi cũ hơn. Hệ quả: một bản «rút & thay» (`rut_va_thay=True`) CŨ của ta
đè được bản «rút bỏ hẳn» MỚI trên đĩa, tức hạ mã 2 xuống mã 1. Dương tính vẫn còn, chỉ sai mức nghiêm trọng.

Vá: thêm luật 4 và hàm `_ben_thang_khi_ca_hai_duong_tinh`. Khi nhóm phán quyết hai bên lệch nhau, một bên thắng CẢ nhóm,
không trộn trường của hai lần kiểm:
- Một bên «đã rút», bên kia chỉ có EoC ⇒ bên «đã rút» thắng, bất kể mốc thời gian (luật bất đối xứng).
- Còn lại thì `kiem_rut_luc` mới hơn thắng. Bên mới hơn có thể là bản tinh chỉnh hợp lệ, ví dụ lần kiểm sau mới thấy bài
  được đăng lại bản sửa.
- Không xác định được bên nào mới hơn (vắng mốc, mốc hỏng, bằng nhau, một bên có múi giờ còn bên kia không) ⇒ giữ bên
  NGHIÊM TRỌNG hơn, theo `_hang_nghiem_trong`: rút bỏ hẳn > thông báo rút là bản đính chính bị rút > rút & thay > EoC. Khi
  không biết thì không bao giờ hạ mức.

## 3. Dương tính mới gặp khoá bận thì mất im lặng

Giả sử một lượt vừa in «🔴 … ĐÃ BỊ RÚT», rồi `ghi_so` hết hạn chờ khoá. Trước bản vá, CLI trả mã 3, còn `chu_trinh_chung_cu`
ra ⚪ «khoá bận». Dương tính chỉ còn trong stdout, không vào sổ, và không có gì màu đỏ.

Vá:
- Khi không cầm được khoá, `ghi_so` gắn vào `SoDangKhoaLoi` danh sách `duong_tinh_chua_vao_so`. Đó là các dương tính có
  trong sổ bộ nhớ mà sổ trên đĩa chưa mang, kể cả trường hợp đĩa đang ở mức nhẹ hơn. Đĩa được đọc không cần khoá vì mọi lần
  ghi đều nguyên tử. Đĩa không đọc được thì so với ảnh gốc.
- Hàm dùng chung `in_loi_khoa` in danh sách đó (tối đa 50 dòng), dòng «[MA] DUONG_TINH_CHUA_VAO_SO» và trả mã 2. Không còn
  dương tính nào chưa vào sổ thì vẫn trả mã 3 như cũ. Dòng «[MA] SO_DANG_KHOA» luôn được in.
- `chu_trinh_chung_cu.py` đọc mã mới và nêu 🔴, cả ở bước ③④ lẫn ③a/③b. Khi bước ③④ đã vướng khoá, chu trình bỏ qua
  ③a/③b, vì mỗi lệnh sẽ lại chờ khoá 60 giây mà vẫn không ghi được gì.

## 4. Cầu NC⇄LS và orchestrator chưa nhận mã SO_DANG_KHOA

- `tools/cau_noi_nghien_cuu_lam_sang.py` trước đây thoát bằng traceback khi gặp `SoDangKhoaLoi`. Nay nó in đúng mã qua
  `in_loi_khoa`, kèm câu «Sổ đang khoá — chạy lại sau», và trả mã 3. Sổ hỏng (lúc đọc hoặc lúc ghi) in `[MA] SO_HONG` và trả
  mã 2. Không có lần nào in «Đã ghi sổ» khi thực tế không ghi.
- `ops/orchestrator.py`: mã 3 ở bước A4 nay thành mức `so_dang_khoa`, thông điệp «[MA] SO_DANG_KHOA — sổ đang khoá … chạy
  lại sau bằng --resume». Mức này không thuộc `DUNG_HET`, nên cả lô vẫn chạy tiếp, mã tổng ≥ 1 và phiếu có một dòng riêng
  (kể cả với bản tin gộp `khong_can`). Trước đây mã 3 rơi chung vào «sổ xác minh chưa đủ». Ở bước A4 không thể gặp
  `KHONG_DO_DUOC`, vì `_thieu_tep` đã chặn dashboard vắng từ trước. Mã 2, gồm cả dương tính chưa vào sổ, vẫn là «rut» 🔴.

## Kiểm

- Test mới `tools/test_so_xac_minh_tiep_20261114d.py`, 25 ca. Bộ test sổ, chu trình, cầu và orchestrator: 648 qua, 1 bỏ qua
  (nền trước bản vá: 623 qua, 1 bỏ qua). Chạy lặp 5 lần cùng tệp test khoá của #355: 43/43 qua cả 5 lần.
- Đột biến: bắt **27/27** phép, có lượt nền xanh trước và sau. Mỗi phép sao lưu bằng `cp -p`, kiểm `cmp`, rồi khôi phục và
  `cmp` khớp. Danh sách phép:
  - M4 (một tiến trình, hai tiến trình);
  - không so mốc (×2); dự phòng luôn chọn của ta; đảo thứ bậc nghiêm trọng; bỏ luật «đã rút thắng EoC»; bỏ rào TypeError
    múi giờ; bỏ luật 4 (tức mã cũ); chép một trường thay vì cả nhóm;
  - không gắn danh sách (×2); `in_loi_khoa` luôn trả 3; không in mã mới; so sánh bỏ qua đĩa (×2);
  - chu trình bỏ 🔴; chu trình vẫn chạy ③a/③b khi sổ khoá; bỏ 🔴 ở ③a/③b;
  - cầu: bỏ bắt khoá; khoá trả 0; bỏ bắt sổ hỏng;
  - orchestrator: bỏ nhánh mã 3 (×2); `thuc_thi` không ghi lại; phiếu không nói; sổ khoá dừng cả lô.

## Còn lại (ngoài phạm vi tệp của việc này)

- Bảng mã của skill `cap-nhat-chung-cu-y-khoa` (`sync/skills/…/SKILL.md`, dòng mã cấp lượt) chưa có
  `DUONG_TINH_CHUA_VAO_SO`. Mục đó thuộc việc khác; sau đó còn phải đóng gói lại ZIP skill tài khoản, và bác sĩ tự tải lên.
- Khoá vẫn chỉ có tác dụng trong một máy. Mac và Windows qua OneDrive vẫn theo luật «một máy tại một thời điểm».

Cần bác sĩ kiểm chứng.
