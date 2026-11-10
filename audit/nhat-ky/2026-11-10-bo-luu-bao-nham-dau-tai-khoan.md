# 10/11/2026 — Bộ lưu làn Chrome báo nhầm «dấu tài khoản» vì mẫu dò thiếu ranh giới từ

**Sự việc.** Lượt 16 làn Chrome lấy bản PMC của PMID 39482474 (JGIM, PMC11861792). Bộ lưu `tools/lan_chrome/bo_luu.js` trả `ok:true` kèm «CÓ DẤU TÀI KHOẢN — đừng bấm, báo bác sĩ». Agent không bấm và báo phiên điều phối; phiên điều phối cũng không bấm, chuyển bác sĩ quyết. Bác sĩ chọn «Cho lưu»; cổng `phien_uy_quyen_chrome.py --nhan` nhận tệp (mã 0), bản in 9 trang, đã gắn EndNote.

**Đo.** Mẫu ở dòng thi hành của bộ lưu là `/sign out|log ?out|my account/i` (không ranh giới). Trên trang, mẫu khớp đúng MỘT chỗ: câu văn «…symptom or sign outside of the following…». Vùng thân bài không có phần tử tài khoản/đăng nhập nào (trang PMC công khai). Cổng nhận tệp dùng `\b(sign out|log ?out|my account|đăng xuất|tài khoản của tôi)\b` nên không khớp «sign outside».

**Gốc.** Hai nơi dò cùng một thứ nhưng viết hai mẫu khác nhau: bộ lưu (bước dựng tệp) lỏng hơn cổng (bước nhận tệp) ở ranh giới từ, và thiếu hai cụm tiếng Việt. Lệch theo chiều «báo thừa» nên không gây lưu sai, nhưng làm bài hợp lệ phải dừng chờ người.

**Vá.** Tách hàm thuần `coDauTaiKhoan` trong `bo_luu.js`, xuất cho node; mẫu `/(?<![\p{L}\p{N}_])(sign out|log ?out|my account|đăng xuất|tài khoản của tôi)(?![\p{L}\p{N}_])/iu` — cùng danh sách cụm với cổng; ranh giới viết bằng `\p{L}\p{N}` vì `\b` của JS chỉ hiểu chữ ASCII (cụm bắt đầu bằng «đ» sẽ không bao giờ khớp). Cảnh báo «đừng bấm, báo bác sĩ» giữ nguyên.

**Kiểm hồi quy.** `tools/test_lan_chrome_dau_tai_khoan_20261110.py`: bảng 15 mẫu (câu gốc của sự cố, «log output», «blogout», «design outcomes»… phải KHÔNG báo; «Sign out», «Logout», «My Account», «Đăng xuất», «Tài khoản của tôi» phải báo); bộ lưu và cổng phán giống nhau trên cùng bảng; cùng danh sách cụm; dòng THI HÀNH gọi hàm (chốt đọc dòng mã, bỏ chú thích). Đột biến 7/7 bị bắt (trả mẫu trần cũ, bỏ ranh giới trước/sau, bỏ cụm tiếng Việt, bỏ cờ `i`, hàm luôn `false`, không xuất hàm); phục hồi xanh. Test làn Chrome 72/72 (đo 10/11/2026).

**Bài học.** Một điều kiện an toàn được kiểm ở hai tầng thì hai tầng phải dùng CÙNG định nghĩa và có test đối chiếu; tầng trước lỏng hơn tầng sau sinh báo nhầm, tầng trước chặt hơn tầng sau sinh lọt.
