# 14/11/2026 — Cảm biến bình duyệt độc lập: neo mốc manifest G10, chốt 1.500 ký tự, lớp denylist, khai đủ giới hạn

**Bổ sung cho** `2026-11-14-cam-bien-binh-duyet-doc-lap.md` (PR #337, đã gộp 03:07Z cùng ngày). Một người duyệt độc lập nêu
bốn vấn đề. Đã kiểm lại cả bốn trên mã sống và dữ liệu thật, cả bốn đều đúng.

**1. Xanh giả khi manifest G10 được làm mới (mức cao).** Bản đầu ngầm coi «tệp gói khớp `release_manifest`» nghĩa là «nội
dung có từ lúc `generated_at`». Điều này sai. Khi G10 chưa được PI ký, mỗi lượt `g10_quality_gate.py` có ghi (write=True)
sẽ ghi đè `release_manifest` bằng băm hiện hành nhưng giữ nguyên `generated_at` (`PF.ghi_checkpoint_giu_moc_sinh`, nhánh nền y
khoa, khoảng dòng 1294–1308). Tiêu chí G10-AUTO-10 còn dặn «Trước ký: chạy lại g10_quality_gate.py để cập nhật manifest».
Kịch bản lỗi: lắp G10 ngày 28/10, bình duyệt 29/10, sửa gói 31/10 rồi chấm lại ⇒ bản đầu trả «ổn».
**Vá:** `_ngay_cham_g10` đọc `G10_QUALITY_REPORT.json` và chỉ nhận khi `package_sha256` trùng
`release_manifest.package_sha256`, giờ có múi được quy về giờ VN (UTC+7) trước khi lấy ngày. Lượt chấm có ghi luôn viết báo
cáo trước manifest, và chỉ bộ chấm G10 ghi manifest, nên mốc báo cáo là cận TRÊN của lúc manifest được viết. Hai mốc dùng
như sau. G_lắp (ngày `generated_at`) là cận DƯỚI. G = max(G_lắp, mốc báo cáo). Khi tệp khớp manifest: R > G ⇒ phủ; R < G_lắp ⇒
🛎; G_lắp ≤ R < G, cùng ngày G, hoặc không ràng buộc được báo cáo ⇒ ⚪. Khi tệp lệch manifest: lúc sửa nằm sau G (hoặc sau
G_lắp khi G vắng), nên R nhỏ hơn mốc đó ⇒ 🛎. Nhờ vậy ca «chấm lại 31/10 rồi sửa» nay ra 🛎 thay vì ⚪.

**2. Luật «chỉ đọc 1.500 ký tự đầu» chưa có test ghim (mức vừa).** Đột biến `dau = noi_dung` từng để 28/28 ca xanh.
**Vá:** thêm ca có ngày «phản biện … ngày 30/10/2026» và dòng «Ngày: 30/10/2026» nằm sau ký tự thứ 1.500 ⇒ ca phải ra ⚪
«không định được ngày».

**3. Cách xác định «đề tài thật» lệch với repo y khoa (mức vừa).** Bản đầu thấy `study_kind=synthetic_test` là bỏ qua ngay.
Repo y khoa coi cờ đó chỉ là lớp thứ nhất; `gate_contract.REAL_STUDY_DENYLIST` là lớp thứ hai và cố ý vẫn coi đề tài là
THẬT khi cờ bị đặt nhầm. **Vá:** `doc_danh_sach_de_tai_that` đọc frozenset đó bằng `ast` (không import engine) và chuẩn
hoá NFC + casefold như `is_real_study_denylisted`. Đề tài synthetic chỉ bị bỏ qua khi tên KHÔNG có trong danh sách. Tên có
trong danh sách ⇒ vẫn đo như đề tài thật, dòng 🛎 hoặc ⚪ kèm cảnh báo «cờ đặt nhầm». Không đọc được danh sách (vắng tệp, cú
pháp lạ, danh sách rỗng) ⇒ ⚪. Đề tài không mang cờ synthetic thì không cần danh sách. Đo 14/11: C1a và BTM đều có
`study_kind` vắng, nên lỗi này chưa xảy ra trên dữ liệu thật.

**4. Giới hạn chưa khai (mức vừa).** Cảm biến CHỈ đo một điều: tệp gói `.md` trong `exports/` có đổi sau bản bình duyệt hay
không. Nó KHÔNG đo các phát hiện 🔴/🟠 của bản bình duyệt đã được xử lý chưa. Nó cũng KHÔNG canh bản sao nộp nằm ngoài
`exports/` hay bản `.docx`, mà tệp thực sự nộp nhiều khả năng là `.docx`. Với C1a: dòng 1 của
`PHAN_BIEN_DE_CUONG_NOP_20261029_…md` ghi rõ «bản nộp trong `exports/` không đổi», và việc sửa 🔴 làm trên BẢN SAO NỘP ngoài
`exports/`. Kết luận của bản đó là «chưa nên nộp nguyên trạng», còn 4 việc 🔴. Trong `exports/` không có hồ sơ nào cho thấy 4
việc này đã xử lý (đo 14/11). **Vì vậy «C1a không có việc» của cảm biến KHÔNG có nghĩa C1a đã qua bình duyệt.** C1a hiện còn
4 🔴 chờ sửa trên bản sao nộp.

**Đo trên dữ liệu thật (14/11/2026):** C1a: `generated_at` 28/10 19:19 (giờ VN, không múi), báo cáo 2026-10-28T13:51Z (20:51
giờ VN) có `package_sha256` trùng manifest ⇒ G = 28/10, bình duyệt 29/10 ⇒ không có việc. BTM chưa có G10_checkpoint ⇒ không
báo. Bộ đọc denylist trên `gate_contract.py` thật (cây chính và nhánh nền) ra đúng hai tên.

**Kiểm:** `tools/test_cam_bien_binh_duyet_20261114.py`: 44 ca qua, 1 ca bỏ trong worktree (ca đọc `gate_contract.py` thật,
cần cây có repo y khoa). 42 tệp test có dùng `tu_de_xuat_viec`: 623 qua. Fixture nay mô phỏng đúng bộ chấm G10 (manifest có
`package_sha256` và kèm `G10_QUALITY_REPORT.json`). Đột biến 15 phép, mỗi phép có sao lưu, xoá `__pycache__`, chạy `python -B`
rồi khôi phục và `cmp`: neo theo `generated_at`, bỏ ràng buộc băm gói, bỏ quy đổi giờ VN, nhận giờ không múi, nhánh lệch chỉ
dùng `generated_at`, lùi về `generated_at` khi không ràng buộc, bỏ nhánh «chấm lại sau bình duyệt», đọc cả thân bài, bỏ lớp
denylist, không đọc được denylist thì bỏ qua, bỏ NFC, bỏ casefold, denylist đã bình duyệt thì im lặng, sai đường dẫn
`gate_contract` mặc định, bỏ cảnh báo cờ trên dòng 🛎. Phép nào cũng đỏ đúng ca dự kiến, khôi phục xong `cmp` khớp và bộ test
xanh lại.

**Giới hạn còn lại:**
- Chấm lại G10 SAU khi ký (approve_gate hoặc g10_quality_gate có ghi) làm mốc báo cáo tiến lên dù gói không đổi. Khi đó cảm
  biến có thể ra ⚪ «chấm lại sau bình duyệt». Đây là chiều an toàn, không phải xanh giả. Muốn gỡ thì ghi sha256 gói vào bản
  bình duyệt (`--van-tay-goi`).
- Agent `binh-duyet` vẫn chưa được dạy ghi sha256 (sửa agent cần PR cặp hai repo).
- Các giới hạn ở mục 4 vẫn còn nguyên.

**Hướng tiếp theo (bác sĩ quyết):** (a) khai đường dẫn bản sao nộp (md hoặc docx) để cảm biến băm cả bản đó; (b) đọc dòng
kết luận hoặc bảng 🔴 của bản bình duyệt rồi đối chiếu với một sổ xử lý, để «còn 🔴 chưa đóng» thành một dòng 👤; (c) dạy
agent `binh-duyet` ghi các dòng sha256 của `--van-tay-goi` vào bản bình duyệt.
