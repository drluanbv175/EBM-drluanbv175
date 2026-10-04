# 04/10/2026 — Uỷ quyền thêm giữa phiên không có hiệu lực; J Rheumatol vào bảng điều khoản; Wiley TDM theo IP (BH159)

**Bác sĩ nói giữa phiên Chrome 20261004-090236:** «J Rheumatol uỷ quyền;đã tắt VPN».

**Lỗi 1 — phạm vi phiên là ảnh chụp lúc mở.** `phien_uy_quyen_chrome.kiem` chỉ nhận các NXB ghi vào `d["nxb"]` lúc `--mo`.
Hệ quả:
- uỷ quyền bác sĩ thêm giữa phiên không có hiệu lực tới phiên sau;
- uỷ quyền bị RÚT giữa phiên (xoá mục/`het_han`) vẫn được lưu tiếp — chiều không an toàn.

Vá: phạm vi tính LÚC KIỂM = NXB có uỷ quyền đọc còn hiệu lực ngay lúc đó (`nxb_duoc_luu`, đã loại sẵn DynaMed/Scopus/WoS).
`d["nxb"]` chỉ còn là ảnh chụp để đối chiếu; `--trang-thai` in cả «NXB lúc mở» lẫn «NXB hiện hành».

**Lỗi 2 — J Rheumatol chưa có trong bảng.** `--ghi-uy-quyen` chỉ nhận khoá có trong `DIEU_KHOAN_NXB` với kết luận «cam».
Điều khoản jrheum.com (cập nhật 08/12/2016, đọc 04/10/2026) cấm sao chép, tải và dùng nội dung dưới mọi hình thức, không có điều
nào về AI ⇒ «không rõ ⇒ xử như cấm». Đã thêm mục (DOI `10.3899/`, miền jrheum.org/jrheum.com), dạy doctrine
`_CONNECTOR-CHUNG-CU.md` §2septies, và ghi đúng lời bác sĩ vào sổ uỷ quyền (ngoài git).

**Lỗi 3 — bộ so doctrine quá lỏng.** `lech_doctrine` chỉ xét CHỮ ĐẦU của tên NXB, nên «The Journal of Rheumatology» sẽ khớp
chỉ cần chữ «The» có ở chỗ khác trong mục. Doctrine tiếng Việt hiện không có chữ «The» nào khác nên lần này chưa lọt; bộ so nay
xét đủ phần tên trước « (».

**Đo thật cùng ngày:**
- Wiley TDM (token của bác sĩ) cấp quyền theo IP thoát:
  - IP VPN: cả 8 bài ACCESS_DENIED;
  - tắt VPN (IP Việt Nam): tải được 4/4 bài Cochrane, còn 4 bài tạp chí Wiley thuê bao vẫn bị từ chối.
- Wiley Scholar Gateway (gói miễn phí 30 lượt/tháng) không chứa CDSR/Cochrane. Phiên 04/10 lỡ tốn 4 lượt để tra lại điều đã ghi
  trong tệp trạng thái. Đọc tệp trạng thái TRƯỚC khi tiêu hạn mức.
- Bài J Rheumatol 31092721 lưu được trong phiên (HTML + PDF) sau khi bác sĩ tự bấm qua Cloudflare.
- Toàn văn mục `apply`: 139 → 144/163.

**Kiểm:**
- `tools/test_jrheum_va_pham_vi_phien_20261004.py`: 7 test, cùng 175 test liên quan xanh.
- Đột biến 3/3 đỏ đúng chỗ: phạm vi về ảnh chụp, bỏ mục J Rheumatol, bộ so về chữ đầu.
- BH159 kiểm hành vi ngoại tuyến.
