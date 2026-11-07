# 07/11/2026 — EndNote: khoá ghi theo tiến trình hở giữa các lượt kéo-thả gắn tag ⇒ thêm khoá «phiên giao diện»

Tiếp `2026-11-07-endnote-gan-tag-theo-luat.md` (PR #301). Bác sĩ: «Tiếp tục hoàn thiện vấn đề trên».

**Nguyên nhân gốc (đo):** `tools/khoa_ghi_endnote.py` giữ khoá theo TIẾN TRÌNH (nhả khi tiến trình thoát) và chỉ chờ khi bác
sĩ vừa thao tác < 20 giây. Phiên gắn tag là chuỗi nhiều lượt công cụ của Claude (mỗi lượt một tiến trình/hành động giao diện);
giữa hai lượt máy rảnh ≥ 20 giây và không ai giữ khoá ⇒ phiên khác ghi chen hợp lệ: 07:34 một lượt nhập bản ghi tóm tắt bệnh
ruột viêm (rec 9046) làm EndNote đổi vùng chọn ⇒ 9046 nhận nhầm «CAD»; 07:41 một lần show/highlight của phiên khác đổi danh sách
đang hiện (show/highlight không phải lệnh ghi nên không qua khoá). Phiên kia báo «đã dừng» lúc 08:36 nhưng agent con chỉ nhận
lệnh lúc 08:44 (gắn PDF 7 lần trong khoảng đó) — tin nhắn liên phiên không phải khoá.

**Vá:**
- `khoa_ghi_endnote.LY_DO_GIAO_DIEN` + `khoa_giao_dien_khac()`: nhận diện khoá phiên giao diện của tiến trình KHÁC còn hiệu lực.
- `gan_tag_endnote.py --giu-khoa [PHÚT]` (chạy nền, mặc định 30, tối đa 60): lấy khoá như mọi lệnh ghi (chờ tiến trình khác/
  bác sĩ, không lấy khi giao dịch treo), làm mới mỗi 30 giây, nhả khi hết hạn/SIGTERM/thoát (`pham_vi_ghi`). Mọi lệnh ghi qua
  `EndNoteMac` của mọi phiên (nhập, đăng nhóm, gắn tệp, ghi trường) chờ rồi bỏ lượt trong lúc đó.
- `--nha-khoa`: SIGTERM đúng tiến trình giữ khoá phiên giao diện; khoá khác (lượt nạp, MCP) KHÔNG đụng.
- `EndNoteMac.hien_ban_ghi`: khoá phiên giao diện của tiến trình khác còn hiệu lực ⇒ ném DangCoTienTrinhKhacGhi; chỉ `--hien` của
  chính phiên gắn tag truyền `trong_phien_gan_tag=True`. `--cho-vao-nhom` báo ⚪ thay vì traceback.
- Hướng dẫn `--huong-dan` bước 0/5 + skill ⑧: chạy nền `--giu-khoa 30` trước khi kéo, `--nha-khoa` khi xong; vẫn nhắn phiên khác
  (agent tự viết AppleScript riêng không đi qua khoá — giới hạn còn lại, nói thẳng).

**Chạy thật trên Mac (07/11 09:31):** `--giu-khoa 2` ghi khoá đúng pid + ly_do, phiên khác thấy `khoa_giao_dien_khac()` = True;
nhưng `--nha-khoa` chỉ nhả sau ~11 giây — Python thử lại `time.sleep` sau trình xử lý tín hiệu (PEP 475) nên tiến trình ngủ
nốt giấc 30 giây rồi mới thoát. Sửa: ngủ từng giây (`NHIP_NGU = 1.0`), làm mới khoá mỗi 30 giây. Chạy lại 09:32: nhả trong 0 giây.

**Kiểm:** `tools/test_khoa_giao_dien_gan_tag_20261107.py` 10 ca (thêm ca «mỗi giấc ≤ 1 giây, vẫn làm mới»); 12 đột biến — 11 đỏ,
1 sống là đột biến TƯƠNG ĐƯƠNG
(`except Exception` → `except RuntimeError`: DangCoTienTrinhKhacGhi là RuntimeError) — phục hồi xanh. Test không bao giờ gửi tín
hiệu thật (hàm `gui` giả) và không đọc/ghi khoá thật (tệp khoá tạm).
