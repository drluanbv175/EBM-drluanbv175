# 20/11/2026 — Số liệu «trôi nổi» trong tổng quan đề cương BTM; luật «không có chứng cứ thực thì loại» (K10)

**Phát hiện.** Phản biện máy đề cương BTM (Claude API, bác sĩ tự chạy `api_khi_can.py`) và kiểm nội dung trích dẫn A12
bắt câu ở mục 3.2: «Trong nước: các nghiên cứu tìm được đo tỷ lệ bệnh thận mạn … (15,32% đến 31,1%) hoặc mô tả kê
đơn …; chỉ một nghiên cứu đo tỷ lệ làm UACR … [11].» Hai con số đến từ hai bài tạp chí trong nước CÓ THẬT (nằm trong
tổng hợp G0 và trong bản thảo tạp chí kèm nguồn), nhưng KHÔNG có trong danh mục tài liệu tham khảo của đề cương (loại
vì không lấy được toàn văn); câu chỉ mang [11] ở mệnh đề sau dấu «;» nên người đọc tưởng có nguồn. Cùng đoạn còn câu
«chưa đọc toàn văn và không chấm GRADE cho tập này» — đã sai (BTM có toàn văn 42/42) và là ghi chú nội bộ.

**Bác sĩ giao.** «Không có số liệu thực, chứng cứ thực hãy loại bỏ trong hệ thống nghiên cứu y khoa.»

**Đã làm.** (1) Đề cương BTM: bỏ khoảng số và vế «mô tả kê đơn» không nguồn, bỏ câu ghi chú nội bộ; K1–K9 ĐẠT, nhất quán
27/27. C1a: ba câu «kết quả có số; kết quả tiếp [n].» cùng một nguồn ⇒ đổi «;» thành dấu phẩy nối (số đã khớp abstract
nguồn theo A12); lắp lại G10. (2) Chốt máy K10 ở `kiem_de_cuong_nop_hoi_dong.py` (và `kiem_ban_thao_tap_chi.py`): trong
đặt vấn đề/tổng quan/bàn luận, mỗi mệnh đề mang số liệu kiểu kết quả phải tự mang [n]; tách mệnh đề ở «;» NGOÀI ngoặc.
K10 bắt bản BTM trước khi sửa; hai đề cương hiện hành và bản thảo tạp chí BTM đạt. (3) Dạy `viet-ban-thao`,
`kiem-chung-trich-dan`; một dòng luật ở CLAUDE.md §8.

**Giới hạn đã biết.** K10 là kiểm hình thức: nó bắt số KHÔNG có trích dẫn trong mệnh đề, không chứng minh trích dẫn
có chứa con số — phần đó là kiểm nội dung A12 (Claude API, «số không thấy trong nguồn») và người đọc.

**Kiểm hồi quy.** `tests/test_k10_so_lieu_phai_co_nguon_20261120.py` (7 ca, repo y khoa); 4 đột biến (tách «;» bỏ qua
ngoặc · bỏ kế thừa mục cha · bỏ nối K10 vào `kiem()` · bỏ mẫu TB ± ĐLC) đều đỏ đúng ca.
