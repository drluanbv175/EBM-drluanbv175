# 20/11/2026 — Tổng quan tài liệu: mỗi tài liệu đỡ một câu, danh mục Vancouver theo metadata A12, con số ↔ toàn văn

**Yêu cầu của bác sĩ:** «Hãy kiểm tra và hoàn thiện vấn đề tổng quan tài liệu giúp tôi», rồi «đồng ý» mã hoá các lỗi tìm
tay thành chốt máy và dạy agent.

## Lỗi đã gặp (đề cương BTM, bản phản biện 19/11 mục O11–O14, O17 — K1–K11 đều ĐẠT nên không thấy)

- Khối trích dẫn gộp «Các tổng quan, nghiên cứu… được tham khảo khi xây dựng đề cương [15–36]»: 22 tài liệu, hơn một
  nửa danh mục, không đỡ câu nào. Gốc ở **bộ sinh** `sinh_de_cuong_nop_hoi_dong.py`: mọi tài liệu ứng viên chưa được nhắc
  tự nhiên bị gom vào MỘT câu cuối phần bằng chứng (và một câu gộp tài liệu phương pháp ở mục cỡ mẫu).
- Danh mục cắt ở 5 tác giả không «et al.», thiếu «năm;tập(số):trang», tên tạp chí đầy đủ viết thường. Gốc ở **biên
  nhận A12**: `PubMedClient.fetch_metadata` chỉ giữ 5 tác giả đầu (tên tập thể bị rỗng) và không lấy tập/số/trang hay
  tên viết tắt NLM; `run_g10_assemble._vancouver` dựng từ đó.
- Con số gán lệch quần thể (46,9% là của mọi người bệnh thận mạn, ở người ĐTĐ típ 2 là 52,7%), ước lượng chọn lọc (nêu
  22% hiệu ứng cố định, bỏ 49% hiệu ứng ngẫu nhiên), thuật ngữ lệch nguồn («bệnh thận đái tháo đường», «biến chứng thận»
  được viết thành «bệnh thận mạn»).
- Tệp đính kèm đầu tiên của KDIGO 2022/2024 trong EndNote là «_TomTatChungCu.pdf» do hệ thống dựng — đọc nhầm sẽ đối
  chiếu số liệu với chính bản tóm tắt của mình.
- Lắp lại G10 trong worktree (không có sổ phê duyệt — tệp cố ý ngoài git) ghi SAP C1a thành «chưa khoá», G2 «dự thảo»
  vào đề cương thống nhất. Đã hoàn tác, lắp lại trên checkout chính.

## Đã làm

- Dữ liệu: drluanbv175/medical-ebm-automation#355 — viết lại chương 3 đề cương BTM (6 mục, 62 TLTK Vancouver, 11 bài
  trong nước), soát chương 3 C1a với nguồn (sửa câu Bull 2019), lắp lại G10 C1a.
- Chốt máy (repo y khoa, PR riêng): K12 (ngoặc gộp từ 6 tài liệu; mục TLTK không được trích), K13 (mục có PMID ↔
  metadata A12: et al./tác giả thứ 6, năm;tập, tên tạp chí NLM); biên nhận A12 thêm `n_authors`, `authors_6` (gồm tên tập
  thể), `journal_abbr`, `volume`, `issue`, `pages`; `_vancouver` dùng các khoá đó (biên nhận cũ giữ cách dựng cũ); bộ
  sinh xếp tài liệu còn lại vào bảng «Các tài liệu liên quan khác đã được rà soát» kèm tên bài nguyên văn, câu tài liệu
  phương pháp gắn từng tài liệu với tên bài; K11 miễn cột bảng khai «(nguyên văn)»; công cụ tư vấn
  `tools/kiem_so_lieu_toan_van.py` (con số ↔ toàn văn theo từng vế, bỏ tệp TomTatChungCu). 13/13 đột biến đỏ đúng chỗ.
- Dạy agent: `viet-ban-thao`, `dieu-phoi-g10` (K1–K13 + công cụ số ↔ toàn văn trước lượt lắp G10),
  `kiem-chung-trich-dan`, `thu-thu-tai-lieu`. CLAUDE.md §8 gộp vào dòng «Số liệu có nguồn thật; trình bày đúng chuẩn».

## Giới hạn còn lại

- K13 chỉ chạy khi biên nhận A12 có khoá mới ⇒ biên nhận BTM/C1a phải dựng lại bằng `check_citations.py --study <mã>`.
- Công cụ số ↔ toàn văn chỉ kiểm SỰ CÓ MẶT: số viết bằng chữ («Eighty-eight») máy không thấy; số ngắn («1,1») trùng
  ngẫu nhiên — đột biến chuyển «1,1%» sang sai tài liệu từng lọt; quần thể, chiều liên quan vẫn phải đọc.
- Máy Mac không chạy được giả lập trọn vòng cục bộ (nhánh gốc cũng dừng ở «phan_a: khong_do_duoc») — CI gia-lap-16 là
  phép đo cho bộ sinh.
