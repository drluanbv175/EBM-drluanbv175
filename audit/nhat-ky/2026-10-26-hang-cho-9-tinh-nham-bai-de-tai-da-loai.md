# 26/10/2026 — Hàng chờ tóm tắt Word ⑨ tính nhầm 14 trích dẫn ĐỀ TÀI đã loại thành «chứng cứ MỚI»

**Phát hiện.** `tools/tu_de_xuat_viec.py` báo «🛎 16 trích dẫn MỚI có PDF chờ tóm tắt chứng cứ Word». Đo: 14/16 là trích dẫn của đề
tài `btm-dtd2-ngoai-tru-BVQY175` nằm trong khoá `loai_bo` của `exports/btm-dtd2-ngoai-tru-BVQY175/DANH_MUC_TRICH_DAN_*.json` (bác sĩ
25/10 cho loại 19/66 bài: không toàn văn hoặc ít phù hợp). Phiên đề tài đã gỡ chúng khỏi nhóm «NC · Chăm sóc thận ĐTĐ típ 2…» (đúng
luật: không thùng rác), nên 14 bản ghi có PDF không còn thuộc nhóm nào — kể cả bài tạp chí trong nước rec 7473 chỉ có DOI.

**Nguyên nhân.** Bản vá 25/10 (`chi_thuoc_de_tai`) chỉ loại bản ghi thuộc nhóm «NC · » mà không thuộc nhóm «EBM · ». Gỡ khỏi nhóm
đề tài làm bản ghi «rơi» về hàng chờ chứng cứ — hàng chờ tính MỌI bản ghi ngoài mốc có PDF. Nếu chạy theo hàng chờ, 14 bài × ~0,6–0,9
triệu token sẽ tiêu vào tóm tắt bài bác sĩ đã loại.

**Cách vá.** `hang_cho()` loại thêm bản ghi có PMID/DOI (DOI không phân biệt hoa thường) trong `trich_dan` HOẶC `loai_bo` của danh
mục trích dẫn của bất kỳ đề tài nào (`trich_dan_danh_muc_de_tai`, bỏ bản `.bak`), miễn bản ghi không thuộc nhóm «EBM · » nào (bài vừa
là trích dẫn đề tài vừa là chứng cứ vẫn theo luật chứng cứ). Thư mục đề tài định vị bằng `goc_du_lieu` (lồng rồi anh em); vắng ⇒
không loại thêm; danh mục không đọc được/sai khuôn ⇒ `NhomKhongDoDuoc` (⚪, mã 2) — không trả hàng chờ lẫn bài đề tài.

**Kiểm hồi quy.** 7 ca mới trong `tools/test_endnote_danh_muc_de_tai_hang_cho_20261025.py` (fixture cũ nay trỏ thư mục đề tài vào
tmp — không đọc danh mục thật của máy). 5 đột biến (bỏ `loai_bo`, bỏ hạ chữ DOI, bỏ ưu tiên nhóm EBM, bỏ bỏ-qua `.bak`, nuốt lỗi
danh mục) đều đỏ đúng chỗ rồi xanh lại. Đo thật trên thư viện: hàng chờ 16 → 2 (hai bài Cochrane 37142273, 37696529 chờ bác sĩ quyết).
