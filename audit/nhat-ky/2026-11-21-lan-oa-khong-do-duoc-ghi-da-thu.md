# 21/11/2026 — Làn truy cập mở KHÔNG ĐO ĐƯỢC mà biên nhận toàn văn TLTK vẫn ghi «đã thử»

**Bối cảnh.** Khi thêm TLTK Abma 2016 (PMID 27094345) cho đề cương C1a, lệnh
`nap_endnote_de_tai.py --study hai-long-benh-nhan-C1a-BVQY175 --gom-toan-van --ghi-bien-nhan-toan-van` được chạy
từ một worktree của repo gốc trong `~/.ebm-worktrees/`. Worktree không có `EBM-Dashboards/` (dữ liệu ngoài git), nên
bộ gom `gom_toan_van_dashboard.py` in «⚪ KHÔNG ĐO ĐƯỢC — không thấy kho …» và trả mã 2. Biên nhận
`exports/<mã>/TOAN_VAN_TLTK_<mã>.json` vẫn nhận một lượt `truy_cap_mo` ngày 21/11 với câu «không có bản truy cập mở
hợp lệ» cho 17 TLTK (đo 21/11/2026). Lượt giả đó đẩy TLTK về phía luật «đã thử hết OA mà không có toàn văn ⇒ loại
khỏi danh mục trích dẫn» (bác sĩ 25/10/2026) và cổng G10-AUTO-12. Biên nhận C1a đã được khôi phục tay trong PR
drluanbv175/medical-ebm-automation#400.

**Nguyên nhân.**
- `bien_nhan_toan_van` coi `bool(bc.get("gom_toan_van"))` là «làn đã chạy»: có báo cáo gom (kể cả báo cáo mang mã 2)
  là mọi TLTK thiếu PDF nhận lượt `truy_cap_mo`. Mã thoát của bộ gom và bộ in PDF không được đọc.
- Lượt ghi cả cho TLTK chưa từng được gửi đi gom: làn gom lấy TLTK từ đề cương nộp, còn biên nhận gồm cả bản thảo G7.
- Bộ gom trả mã 0 cả khi từng bài gặp lỗi mạng hoặc tầng Unpaywall bị bỏ vì thiếu email; làn Unpaywall theo DOI ghi
  «trang HTML» khi MỌI vị trí đều lỗi khi tải (thực chất là lỗi mạng).

**Cách vá** (`tools/nap_endnote_de_tai.py`). `gom_toan_van` trả `do_duoc` gồm các PMID/DOI mà làn đã ra kết luận ở
lượt này, và `khong_do_duoc` ghi lý do từng phần không đo được. Biên nhận chỉ ghi `truy_cap_mo` cho định danh nằm
trong `do_duoc` (gồm cả PMID suy từ DOI). Làn theo PMID chỉ tính là đo được khi đủ bốn điều kiện:
- kho làn ghi vào có thật;
- kho đó trùng kho lượt này đọc;
- bộ gom và bộ in PDF (nay được truyền `--kho`) đều trả mã 0;
- bộ gom không in dấu hiệu chưa trọn (`DAU_HIEU_GOM_CHUA_TRON`).

Kho vắng hoặc lệch thì làn không chạy. Báo cáo in «⚪ làn OA KHÔNG ĐO ĐƯỢC … ⇒ biên nhận KHÔNG ghi lượt
«truy_cap_mo»». Khi là worktree, báo cáo chỉ đường tới cây chính, và mã thoát là 1 (còn việc). Làn Unpaywall theo DOI
tách «đã kết luận» (`da_do_doi`) khỏi lỗi mạng.

**Không làm.** Không tự đọc hay ghi kho của cây chính từ worktree. Bộ gom, bộ in PDF và engine y khoa đều tự định vị
từ cây của chính chúng qua `ban_sao_tran.duong_goc`, và quy ước «worktree = bản sao trần, không tự tạo kho»
(TT-05/W9) là có chủ ý. Muốn chạy làn OA thật thì chạy từ cây chính.

**Kiểm hồi quy.** Test mới nằm trong `tools/test_bien_nhan_toan_van_tltk_20261118.py` (mục 21/11) và
`tools/test_nap_endnote_de_tai_20261025.py` (`test_main_gom_toan_van_khi_khong_thay_kho_…`). Bốn fixture cũ
`{"chay": True}` không phải khuôn thật nên đã được thay bằng khuôn `do_duoc` hợp lệ; assertion giữ nguyên.

Kiểm đột biến 12/12 bị bắt: mỗi đột biến làm đỏ đúng test, phục hồi thì xanh (`python -B`, xoá `__pycache__` trước
mỗi phép). Một chốt khớp chuỗi giữ dấu hiệu chưa trọn bám vào chuỗi THI HÀNH của bộ gom (AST, bỏ docstring). Nếu bộ
gom đổi câu chữ, chốt sẽ đỏ thay vì lặng lẽ thành «đã thử».

Thử với mô-đun cổng thật `toan_van_trich_dan` của cây chính: ở ca kho vắng, TLTK có sổ «không truy cập» nay là
`chua_thu_het` (CON_VIEC), không còn là `khong_lay_duoc` (VI_PHAM ⇒ loại).

**Bài học.** «Có báo cáo» ≠ «đã đo». Ghi một lượt thử vào sổ mà luật loại bỏ đọc thì phải xét mã thoát và phạm vi
của chính lượt đó, cho từng định danh.
