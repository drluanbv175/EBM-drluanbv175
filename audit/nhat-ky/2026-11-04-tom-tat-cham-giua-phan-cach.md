# 04/11/2026 — Cổng số ⑨ đọc « · » phân cách trong bản tóm tắt thành dấu thập phân

**Phát hiện khi chấm bù kiểm chéo:** `dung` của PMID 39490700 bị chặn «số 60.45 không có trong bài». Bản tóm tắt viết
«nhóm eGFR ≥60 · 45–<60 · <45». Bản vá 28/10 (#274) ghép «11 ·1», «2·⏎12» của văn bản PDF (pypdf tách số thập phân Lancet/NEJM)
thành số thập phân — nhưng `cac_so` dùng chung cho cả bài lẫn bản tóm tắt, nên « · » PHÂN CÁCH của bản tóm tắt (Word dùng
« · » làm dấu phân cách) cũng bị ghép.

**Đo trên toàn kho (282 gói, quét cổng tất định trước/sau):** 3 gói bị chặn oan chỉ vì lỗi này — 39490700 (60.45), 41033330
(dãy số đếm «34 · 3 · 9 · 3 · 1» ⇒ 34.3, 9.3; «66 · 11 · 11» ⇒ 66.11, 11.1), 17405970 (362.362, 364.382); và 2 gói khác mất
một phần lỗi số oan (19762550, 20872595 — còn lại lỗi thang mức thật). Trước đó các gói này bị xếp nhầm vào nhóm «lỗi số của
người soạn». Sau vá: 0 gói mới bị chặn; 16 gói còn bị chặn đều vì lỗi thật (thang mức, 2 gói số không có trong bài).

**Vá:** `cac_so_tom_tat()` — phía BẢN TÓM TẮT, chấm giữa có khoảng trắng HAI bên giữa hai chữ số là phân cách; «0·85», «1 ·01»
vẫn là thập phân. Ba chỗ cổng đọc số của bản tóm tắt (dòng kết quả theo trang, tập số bảng, số ở mọi trường chữ) dùng hàm mới.
Phía BÀI giữ nguyên cách ghép của #274 («11 · 1» trong PDF vẫn là 11.1).

**Kiểm:** `tools/test_tom_tat_cham_giua_20261104.py` 5 ca; 4 đột biến (cổng dùng lại `cac_so`, hàm mới không tách, nhận phân cách
khi chỉ một bên có khoảng trắng, áp phân cách cả phía bài) đều đỏ, phục hồi xanh. Bộ test tóm tắt ⑨ 211 xanh.

**Bài học:** chuẩn hoá số cho văn bản PDF (bên ngoài, lỗi trích xuất) và cho văn bản hệ tự viết (quy ước trình bày riêng) là hai
việc khác nhau — một hàm dùng chung cho cả hai phía thì mỗi lần nới phía này phải đo lại phía kia trên toàn kho.
