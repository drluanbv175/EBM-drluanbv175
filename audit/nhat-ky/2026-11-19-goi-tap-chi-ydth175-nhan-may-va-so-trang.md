# 19/11/2026 — Gói nộp Tạp chí Y Dược Thực hành 175: nhãn máy trong bản thảo, số trang chưa đo (Word: 15/10)

**Phát hiện khi:** bác sĩ giao «kiểm tra hồ sơ Hội đồng Đạo đức và chuẩn bị hồ sơ gửi Tạp chí Y Dược Thực hành 175».
Gói `exports/btm-dtd2-ngoai-tru-BVQY175/tap_chi/YDTH175/` do agent `viet-ban-thao` soạn cùng ngày. Gói nằm trong
`exports/`, ngoài git.

**Lỗi đo được:**
- Bản thảo, thư gửi Ban biên tập, thông tin tác giả, cam kết và bảng STROBE–RECORD đều mang nhãn «[BẢN NHÁP AI — …]»
  và dòng ghi chú «>»; luật K8 đếm được 9 dòng trong bản thảo. Điều này trái lời bác sĩ ngày 17/11: văn bản người đọc
  không mang dấu vết soạn thảo/máy. Nguyên nhân là doctrine `viet-ban-thao` vẫn dặn gắn nhãn vào chính bản thảo.
- Bảng kiểm đếm tay ghi số trang «chưa đo được bằng máy». Đo bằng Microsoft Word thật thì được 15 trang (5.173 từ),
  trong khi thể lệ cho tối đa 10 trang kể cả tài liệu tham khảo. Đã đối chiếu thể lệ trên trang gốc jpmp175.vn.
- Từ khoá phân cách bằng dấu chấm phẩy, thể lệ yêu cầu dấu phẩy.
- Nhãn tóm tắt viết «Đặt vấn đề / Đối tượng và phương pháp», thể lệ ghi «Giới thiệu chung / Phương pháp».
- Bảng Word chia cột đều nên cột đầu xuống dòng liên tục; riêng phần bảng tốn khoảng 1 trang.

**Vá:**
- Dữ liệu: chuyển nhãn và ghi chú sang `HUONG_DAN_DIEN_GOI_NOP_<mã>.md`; theo thứ tự cắt bảng kiểm đã đề xuất, bỏ dòng
  độ nhạy khỏi bảng và hai trích dẫn phương pháp. Kết quả: 12 trang, 4.418 từ, K8 = 0; bản cũ sao lưu ở `_sao_luu/`.
  Còn vượt khoảng 2 trang; phương án cắt nằm ở mục 0 của bảng kiểm, chờ tác giả chọn khi có kết quả.
- Mã (repo y khoa): `tools/kiem_ban_thao_tap_chi.py` đo bản thảo theo thể lệ, đếm trang bằng Word thật — không đo được
  thì «chưa đo», không bao giờ «đạt». Hồ sơ `tap_chi_y_duoc_thuc_hanh_175` của `md2docx_vn` dùng bảng gọn. Có 17 test,
  14/14 đột biến đều làm test đỏ.
- Doctrine: `viet-ban-thao` ghi nhãn nguồn gốc ở tệp hướng dẫn điền và chạy công cụ kiểm trước khi trả gói. Câu khai
  báo dùng trí tuệ nhân tạo theo ICMJE trong mục Tuyên bố vẫn giữ.
- Chốt: BH184.

**Bài học:** «chưa đo được» trong một bảng kiểm do agent tự viết không được để mặc. Cần đo bằng công cụ thật (ở đây là
Word), vì giới hạn trang mới là giới hạn chặn thật — 5.000 từ có bảng không vừa 10 trang ở cỡ chữ 13, giãn dòng 1,3.
