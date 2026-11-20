# 20/11/2026 — `phien_uy_quyen_chrome --kiem` thiếu URL báo sai nguyên nhân «NXB không thuộc phạm vi»

**Bối cảnh.** Làm điểm quyết định DP-G10-1 của C1a (lấy toàn văn các nguồn nền về phương pháp), agent gọi
`--kiem <PMID> --doi <DOI>` không kèm `--url` cho TLTK 41 (DOI `10.1207/…`, tiền tố cũ của T&F) và TLTK 37
(`10.1191/…`, SAGE). Công cụ trả «NXB của bài (chưa kiểm điều khoản) KHÔNG thuộc phạm vi phiên». Kèm URL trang
bài thì cả hai đều «được» (T&F, SAGE có uỷ quyền đọc còn hiệu lực).

**Nguyên nhân.** `kiem()` xét phạm vi NXB TRƯỚC khi xét URL. Tiền tố DOI cũ không có trong bảng điều khoản,
nên khi thiếu URL, `nxb_cua_lan` không xác định được NXB và rơi vào nhánh «không thuộc phạm vi». Đây là báo sai
nguyên nhân, không phải mở hở: kết quả vẫn là từ chối (mã 3). Hậu quả: agent suýt kết luận T&F/SAGE chưa có
uỷ quyền, rồi bỏ làn hoặc đi đường đọc điều khoản và PR bảng không cần thiết.

**Vá.** Không xác định được NXB VÀ không có URL ⇒ «thiếu URL trang bài — chỉ PMID/DOI chưa xác định được NXB;
thêm --url rồi kiểm lại». Vẫn mã 3. Có URL mà NXB lạ thì giữ nguyên «KHÔNG thuộc phạm vi».

**Kiểm hồi quy.** `tools/test_kiem_uy_quyen_thieu_url_20261120.py` (4 ca). Đột biến tắt nhánh mới thì ca
«không URL, tiền tố DOI lạ» đỏ, phục hồi thì xanh. Cùng chạy với `test_phien_uy_quyen_chrome_20261004.py` và
`test_jrheum_va_pham_vi_phien_20261004.py`: 36 đạt.

**Kết quả lượt làm (ảnh chụp 20/11).** Wiley `pdfdirect` lấy được Whitehead 1993 và Heinze 2002. T&F
(`/doi/pdf` trả HTML) và SAGE (HTTP 403) không có quyền từ IP thoát hôm đó. Đây là hạn chế của thuê bao
theo IP, không phải của uỷ quyền.
