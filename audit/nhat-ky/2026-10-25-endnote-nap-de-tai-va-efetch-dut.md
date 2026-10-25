# 25/10/2026 — EndNote chưa nhận đề tài nghiên cứu; efetch PubMed đứt giữa chừng làm hỏng cả lượt nạp

**Bối cảnh.** Đề tài `btm-dtd2-ngoai-tru-BVQY175` (G0 xong phần agent) cần 66 trích dẫn trong EndNote. `nap_endnote_chu_de.py`
chỉ nhận dashboard `WebDashboard_*.html` ⇒ phiên trước nạp bằng kịch bản tạm trong scratchpad gọi `nap_nhieu` với `doc_data` dựng
từ `exports/<mã>/DANH_MUC_TRICH_DAN_<mã>.json`, nhóm «NC · Chăm sóc thận ĐTĐ típ 2 ngoại trú BVQY175 (btm-dtd2-ngoai-tru-BVQY175)»
(group_id 133), khoá ghi nhớ `DE-TAI_btm-dtd2-ngoai-tru-BVQY175` trong `~/.ebm-endnote.json`.

**Sự cố kèm theo (đo 25/10).** efetch PubMed cho 52 PMID đứt sau 1.160.011 byte ⇒ `http.client.IncompleteRead`. Lớp này thuộc
`http.client.HTTPException`, KHÔNG phải URLError/OSError ⇒ `_tai()` không thử lại, và `lay_metadata` (chỉ bắt
RuntimeError/ParseError/OSError) cũng không lùi sang Europe PMC ⇒ cả lượt nạp vỡ. Kịch bản tạm phải tự bọc thêm một vòng thử lại.

**Vá.**
- `tools/nap_endnote_chu_de.py::_tai`: thêm `http.client.HTTPException` vào nhánh thử lại; hết lượt ⇒ RuntimeError như lỗi mạng
  khác ⇒ `lay_metadata` lùi Europe PMC rồi Crossref.
- `--de-tai <mã>`: đọc danh mục trích dẫn của đề tài, dựng khối giống DATA của dashboard và đi ĐÚNG đường `nap_nhieu` (kiểm trùng,
  loại trừ, thùng rác, khoá ghi, nhóm theo group_id, gắn PDF từ kho chung). Nhóm mặc định «NC · <tên đề tài> (<mã>)» (tên lấy từ
  `study_meta.json`, ≤ 100 ký tự, mã không bị cắt); khoá chủ đề giữ đúng `DE-TAI_<mã>` của lượt tay ⇒ nhóm đã ghi nhớ thắng, không
  post nhóm thứ hai. KHÔNG chạy bước tóm tắt tiếng Việt (bác sĩ dặn 25/10: trích dẫn đề tài không cần tóm tắt chi tiết nhưng phải
  có toàn văn) — vì thế thiếu kho chỉ cảnh báo, không chặn. Kho mặc định là kho chung `EBM-Dashboards/toan_van_oa` (không đoán
  `toan_van_oa` cạnh thư mục đang đứng). Mã sai khuôn ⇒ 3; danh mục thiếu/hỏng/ghi đề tài khác ⇒ 2, không nạp gì. `--xuat-xml`
  dùng được cho máy không phải Mac.
- Câu cảnh báo chạy khô «--ap-dung ghi khối ĐỌC NHANH sẽ bị từ chối» chỉ in khi lượt `--ap-dung` thật sự bị chặn (trước đó in cả
  với `--khong-tom-tat`).

**Bổ sung cùng ngày — hàng chờ tóm tắt Word ⑨ tính cả bài đề tài** (phiên «Cài đặt cho Endnote» báo, ~18:30). `tom_tat_chung_cu_word
.hang_cho` lấy mọi bản ghi MỚI (ngoài mốc 19/10) có PDF ⇒ sau lượt nạp đề tài hàng chờ nhảy 2 → 43 (41 bài chỉ thuộc nhóm «NC · …»);
hòm việc báo «🛎 43 trích dẫn MỚI … chờ tóm tắt chứng cứ Word» — một phiên làm theo sẽ tốn ~150–400 nghìn token/bài cho việc bác sĩ
không muốn. Vá: `chi_thuoc_de_tai()` đo nhóm theo group_id trên bản sao sdb.eni (BH167): bản ghi nằm trong nhóm «NC · » mà không nằm
trong nhóm «EBM · » nào ⇒ loại khỏi hàng chờ (cả bản ghi mới lẫn bản ghi cũ ngoại lệ mốc); bài đề tài đồng thời là trích dẫn chứng
cứ vẫn vào. Không đọc được nhóm (sdb.eni đổi liên tục, lỗi sqlite, thành viên nhóm «NC · »/«EBM · » không giải được) ⇒
`NhomKhongDoDuoc` ⇒ `hang-cho`/`tien-do` in ⚪, mã 2 — không trả hàng chờ lẫn bài đề tài. Chỉ đọc nhóm khi có ứng viên. Đo lại bằng mã
mới trên thư viện thật: 43 → 2 (hai bài Cochrane của nhóm «EBM · COPD»); 63 bản ghi chỉ thuộc đề tài. Giới hạn: bài đề tài được dashboard
trích nhưng còn nằm trong hàng chờ «đưa vào nhóm ĐÃ có» (chưa vào nhóm «EBM · ») tạm thời chưa vào hàng chờ ⑨ — vào ngay khi được kéo
vào nhóm.

**Kiểm.** `tools/test_endnote_danh_muc_de_tai_hang_cho_20261025.py` (33 ca; đổi tên khi gộp #254 — tên cũ nay là test của `nap_endnote_de_tai.py`); 12 đột biến `--de-tai`/`_tai` + 9 đột biến hàng chờ đều đỏ, phục hồi
xanh (2 đột biến lúc đầu lọt do fixture thiếu tệp `.enl` — sửa fixture, không nới khẳng định); fixture hai tệp test hàng chờ cũ được
bổ sung `doc_nhom` (thư viện thật luôn có bảng nhóm); 431 ca EndNote + tóm tắt + hòm việc xanh. Chạy khô thật `--de-tai` trên đề tài:
66/66 đã có trong thư viện, về đúng nhóm đã ghi nhớ, không nhập gì.

**Bổ sung cùng ngày — hai công cụ nạp trích dẫn đề tài, hai tên nhóm.** #254 (gộp vào master trước #252) thêm
`tools/nap_endnote_de_tai.py` (TLTK của đề cương) với nhóm mặc định «NC · <mã>» và KHÔNG đọc bảng `nhom_theo_chu_de` ⇒ đề tài
`btm-dtd2-ngoai-tru-BVQY175` (đã có group 133 «NC · Chăm sóc thận ĐTĐ típ 2 ngoại trú BVQY175 (btm-…)», ghi nhớ bởi lượt
`--de-tai`) chạy `--ap-dung` không `--ten-nhom` sẽ dựng nhóm đề tài thứ hai. Bác sĩ chọn sửa ở #252. Vá: `chay()` lấy tên nhóm
theo thứ tự `--ten-nhom` → nhóm đã ghi nhớ (khoá `khoa_nhom_de_tai` = `DE-TAI_<mã>`, cùng khoá `doc_de_tai` của `--de-tai`) →
«NC · <mã>»; lượt `--ap-dung` thật (EndNote mở, nạp không lỗi) ghi nhớ tên đã dùng (`--ten-nhom` thắng và được ghi nhớ, như
`nap_nhieu`); báo cáo in nguồn tên nhóm. Dưới pytest ghi vào `~/.ebm-endnote.json` thật bị chặn cứng (`_ghi_nho_nhom`) — test
của #254 vốn không cô lập cấu hình (chạy thử trước khi thêm fixture: 3 ca nạp thật đỏ đúng ở rào, tệp thật không đổi); fixture tự
động nay trỏ `NE.CAU_HINH` sang tmp_path. Đo thật (chỉ đọc): btm-dtd2 → nhóm 133 (66 bản ghi); hai-long-benh-nhan-C1a chưa ghi
nhớ ⇒ «NC · hai-long-benh-nhan-C1a-BVQY175» = đúng group 135 đang có (52 bản ghi), lượt `--ap-dung` kế tiếp sẽ ghi nhớ.
Kiểm: 6 ca mới trong `tools/test_nap_endnote_de_tai_20261025.py` (29 ca); 8 đột biến đều đỏ, phục hồi nguyên byte.

Cần bác sĩ kiểm chứng.
