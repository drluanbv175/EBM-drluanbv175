# 03/10/2026 — Điều khoản NXB trong doctrine §2septies lệch văn bản gốc (đọc lại sau lượt kiểm độc lập)

**Phát hiện.** Ngay sau khi gộp #93 và y khoa #72, một agent độc lập mở lại từng trang điều khoản. Tôi tự đọc lại ba văn bản
Elsevier trước khi sửa: điều khoản website sửa 12/03/2026, điều khoản Scopus sửa 16/09/2026, và API Service Agreement §2.4.
- **Elsevier:** câu trích bỏ mất mệnh đề ngoại lệ «except as otherwise expressly permitted … or any relevant license or
  subscription agreement». Cũng điều khoản đó ghi rằng điều khoản riêng của dịch vụ hoặc hợp đồng thuê bao của cơ sở THẮNG.
- **Bài Elsevier OA:** bài mang giấy phép CC trong PMC đã đi đường OA trong mã (`duong_doc` xét OA trước NXB), nhưng doctrine
  viết «KHÔNG mở … dù tới qua đường nào». Lời và mã lệch nhau.
- **Scopus:** doctrine lấy căn cứ «là sản phẩm Elsevier». Thực ra điều khoản riêng của Scopus CHO dùng cùng công cụ AI kèm điều
  kiện: môi trường đóng cấp doanh nghiệp, chỉ cho cá nhân, không huấn luyện, không chia sẻ cho bên thứ ba. Kết luận «không mở trang
  Scopus» vẫn đứng được, nhưng phải nêu đúng căn cứ. `scopus.com` cũng chưa nằm trong miền của Elsevier.
- **Scopus API:** §2.4 đặt 5 điều kiện cho việc dùng cùng hệ AI. Agent độc lập bỏ sót 2 điều kiện: môi trường đóng chỉ cho
  nghiên cứu cá nhân, và không tạo dịch vụ thay thế. Engine lại đệm phản hồi 24 giờ. Đây là câu hỏi tuân thủ THẬT, để bác sĩ quyết.
- **EBSCO:** nguồn là tóm tắt giấy phép của thư viện UBC, không phải điều khoản của chính EBSCO. Kết luận «cấm» chỉ đứng theo
  luật «không rõ ⇒ dừng».
- **ADA:** trường «trích» là câu diễn giải, không phải câu nguyên văn. Trang trả 403 nên chưa xác minh lại được.
- **Web of Science:** tóm tắt UBC ghi AI = «Ask», TDM = «No», tức cùng loại bằng chứng đã khiến EBSCO «dừng». Nhưng lời dặn
  bác sĩ 03/10 cho chạy vài truy vấn khi bác sĩ có mặt.

**Sửa.** Chỉ sửa cho ĐÚNG văn bản gốc, không nới cổng nào.
- Thêm ngoại lệ, loại nguồn và đường hợp lệ đủ điều kiện vào bảng `DIEU_KHOAN_NXB` và doctrine. `scopus.com` vào miền Elsevier.
- Ghi rõ ngoại lệ PMC OA giấy phép CC. Làn trình duyệt vẫn chặn cả tiền tố DOI.
- Đánh dấu câu trích ADA là «CHƯA XÁC MINH NGUYÊN VĂN».
- Ghi bằng chứng mới về WoS và nêu rõ cần bác sĩ xác nhận lại. Tôi KHÔNG đổi lời dặn của bác sĩ.
- 1 test mới, 3 đột biến đều bị bắt. Bản y khoa của doctrine sửa y hệt từng byte bằng PR cặp.

**Việc của bác sĩ.**
1. Làn Scopus API có thoả §2.4 không (môi trường, lưu đệm 24 giờ)?
2. WoS giữ «vài truy vấn khi có mặt» hay chỉ Export?
3. Mở trang giấy phép ADA bằng Chrome để chép câu nguyên văn.
