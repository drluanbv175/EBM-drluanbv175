# 02/10/2026 — Làn trình duyệt CÓ NGƯỜI: trang chặn bot do bác sĩ xác nhận, và tra Scopus / Web of Science / DynaMed bằng tài khoản của bác sĩ

**Bối cảnh (bác sĩ yêu cầu ba lần trong phiên).** (1) «Các trang chặn bot thì mở trang để tôi xác nhận». (2) «Tôi có tài khoản Scopus và Web of
Science — xây cơ chế để khi cần tôi mở tài khoản trên web». (3) «Tôi đã mở tài khoản DynaMed trên web, hãy hoàn thiện».

**Đo trước khi dựng.** FDA: trình duyệt trong app gặp trang «Sorry! This resembles an automated request» + nút «I am not a bot» (Claude KHÔNG
bấm — quy tắc an toàn cấm vượt kiểm tra chống bot); urllib nhận 401. DynaMed (bác sĩ đã đăng nhập): «Recent Alerts» có loại cảnh báo, ngày, câu
tóm tắt và trích dẫn tạp chí «(Ann Oncol 2026 May)»; trang chủ đề có 169 liên kết, 0 liên kết PubMed/DOI ⇒ phải tra ngược trích dẫn ra PMID.
Hai dạng văn bản trang đo được: loại và ngày trên hai dòng, hoặc dính một dòng («EvidenceUpdated 2 Oct 2026») — bộ tách nhận cả hai.

**Thiết kế (an toàn trước).** Mọi đăng nhập/vượt chặn bot do BÁC SĨ làm; máy không gõ mật khẩu, không giải CAPTCHA, không giả dạng trình duyệt.
Scopus/WoS: máy soạn câu tìm, bác sĩ dán + Export (chức năng chính thức) — máy KHÔNG cào trang kết quả (điều khoản Elsevier/Clarivate).
DynaMed: một lượt đọc «Recent Alerts» mỗi tuần theo yêu cầu, văn bản vào tệp TẠM ngoài repo; máy chỉ giữ trích dẫn + tên chủ đề + ngày + ≤ 4 từ
khoá, KHÔNG lưu câu tóm tắt (bản quyền EBSCO). Mọi kết quả chỉ là KHÁM PHÁ: chỉ bản ghi `xac_minh_duoc` qua bộ xác minh của làn dự phòng
(Crossref/PubMed + rút bài Crossref/Scite) mới thành CANDIDATE ở `surveillance/ung-vien-ngoai-quet.jsonl`; gói tuần kiểm lại rút bài chuỗi 3 tầng.

**Đo thật sau khi dựng.** Scopus CSV thử (1 bài RA thật + 1 DOI bịa): giữ 1, DOI bịa bị loại (Crossref không có bản ghi), 4,5 giây. DynaMed 10
cảnh báo hôm nay: tách 10/10; mặc định chỉ tra chủ đề watchlist ⇒ cảnh báo thuốc FDA obinutuzumab (thận hư trẻ em) gắn đúng chủ đề «Hội chứng
thận hư & Bệnh thận nhi» và nêu 👤 (nguồn ngoài PubMed); 9 cảnh báo thuộc chủ đề ngoài watchlist được liệt kê (dấu hiệu khoảng trống giám
sát). Với `--tat-ca`: 4 bài tra ngược ra đúng PMID và qua xác minh, 2 «mơ hồ» không đoán, 4 nguồn ngoài PubMed (FDA, NCCN).

**Ba lỗi bắt được khi chạy thật (trước khi giao).** (1) Luật gắn chủ đề «trùng 1 từ bất kỳ» gắn «HR-positive metastatic breast cancer» vào chủ
đề GLP-1 chỉ vì chữ «receptor» ⇒ nay đòi trùng ≥ 2 từ đặc hiệu (hoặc tên DynaMed chỉ có 1 từ đặc hiệu) và DUY NHẤT một chủ đề điểm cao nhất.
(2) Bản ghi Crossref không mang PMID làm mất PMID đã tra ⇒ trường rỗng của bản ghi đăng ký không ghi đè định danh đã biết. (3) Tham số mặc
định `thu_muc=DASH` chốt lúc nạp mô-đun (lần thứ hai trong ngày) ⇒ tra lúc gọi.

**Chốt BH150** + 30 test `tools/test_xac_nhan_trinh_duyet_20261002.py` + 47 test `tools/test_tra_cuu_co_tai_khoan_20261002.py`. Đột biến: công cụ
chặn bot + orchestrator 11/11; công cụ tra có tài khoản 12/12 (D5 lọt lần đầu vì ca test bị vô hiệu khi thêm «receptor» vào từ chung — thêm ca
«Obesity Hypoventilation Syndrome» rồi mới bắt); BH150 8/8. Một lỗi của chính tôi trong lúc đột biến: dùng `git checkout --` khôi phục tệp có sửa
chưa commit ⇒ mất phần sửa, phục hồi bằng chép từ bản nguồn chuẩn (trùng byte) — bài học: khôi phục từ bản sao lưu, không từ git, khi tệp có sửa dở.
