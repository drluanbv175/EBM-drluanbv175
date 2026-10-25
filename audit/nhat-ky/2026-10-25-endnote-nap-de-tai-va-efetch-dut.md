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

**Kiểm.** `tools/test_nap_endnote_de_tai_20261025.py` (26 ca); 12 đột biến đều đỏ, phục hồi xanh; 271 ca EndNote xanh. Chạy khô
thật trên đề tài: 66/66 đã có trong thư viện, về đúng nhóm đã ghi nhớ, không nhập gì.

Cần bác sĩ kiểm chứng.
