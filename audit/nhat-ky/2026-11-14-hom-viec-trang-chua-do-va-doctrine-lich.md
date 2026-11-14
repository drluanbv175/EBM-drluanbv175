# 14/11/2026 — Hòm việc bỏ rơi mục ⚪ của cảm biến lịch nền (xanh giả) + chốt doctrine tác vụ lịch còn âm tính giả

**Bối cảnh:** «Hướng hoàn thiện tiếp theo» tầng 5 (việc P); bác sĩ trả lời «Tiếp tục» (~17:00 ngày 14/11/2026). Bổ sung cho
`2026-11-14-lich-nen-don-muc-thap.md` (#356) và `2026-11-14-chot-doctrine-tac-vu-lich-da-bo.md` (#348). Ba vấn đề mức thấp do
thẩm định #356 nêu.

**Ba lỗ đo trên mã sống (origin/master c248fbb):**
1. `tools/tu_de_xuat_viec.py` chỉ đọc `phat_hien` của `kiem_lich_nen.kiem()`. Mọi mục `khong_do_duoc` biến mất khỏi bảng tự đề
   xuất và hòm việc, kể cả trạng thái ⚪ mới «KẾT THÚC không đọc được mã» của #356, tác vụ trước mốc dấu vết, máy không có bản
   chạy. Đo sống (chỉ đọc, cây chính 14/11): `kiem_lich_nen` có 1 mục ⚪ (`kiem-tra-hoan-thien-he-thong-thang` trước mốc
   03/12/2026), bảng và hòm không nhắc gì tới nó.
2. Hệ quả: bảng in «🟢 KHÔNG CÒN VIỆC NÀO», hòm in «🟢 không có việc nào chờ bác sĩ» dù còn mục chưa đo được. Đó là chỉ số
   gộp bị đọc thành kết luận về toàn bộ (BH08/BH27).
3. Chốt `doctrine_tac_vu_lich` (`tools/verify_claude_code_repo_alignment.py`) để lọt các câu: «tác vụ lịch tuần thứ 2 lúc 07:00
   `x`», «… vào thứ Hai `x`», «tác vụ lịch hằng tuần (thứ Hai) `x`», «tác vụ (lịch) `x`», «tác vụ mới — `x`».

**Vá:**
1. Hàm mới `giac_quan_nguoi_chet_lich_nen(kiem_fn=None)` (⑦f, tách khỏi `main()` để kiểm được phần nối dây) và
   `muc_chua_do_lich_nen()`. Mỗi mục `khong_do_duoc` thành một dòng ⚪ «chưa đo được: lịch nền — …» trong danh sách riêng
   `_CHUA_DO`. Mục ⚪ không phải việc 🛎 (không có lệnh nào xoá ⚪ ngay) và không bị tính là giác quan chết, nên số «Giác quan đo
   được X/Y» vẫn đúng. Kiểu sai ⇒ một dòng ⚪ nói rõ. Công cụ hỏng hoặc kết quả thiếu khoá ⇒ giác quan chết, không ghi dở dang.
   `phan_loai_lich_nen()` giữ nguyên chữ ký.
2. `dong_tom_tat()` chỉ in «🟢 KHÔNG CÒN VIỆC NÀO» khi không có việc, không có giác quan chết VÀ không có mục ⚪. Còn ⚪ thì in
   «⚪ Không có việc đỏ, còn N mục chưa đo được». `ghi_json` thêm khoá `chua_do`. `hom_viec_mot_cua.dong_hom` đọc khoá này:
   khi còn mục ⚪ thì in «⚪ không có việc đỏ chờ bác sĩ, còn N mục chưa đo được» kèm ví dụ mục đầu. Bảng cũ thiếu khoá ⇒ coi là
   rỗng, giữ tương thích. Khoá sai kiểu ⇒ ⚪.
3. Từ vựng lịch nhận thêm «lúc|vào», giờ «7h / 7 giờ 30 / 18g30», «mùng/mồng N». Một cặp ngoặc chứa 1–4 từ vựng lịch tính là
   một cụm. «—», «–», «-» được nhận như «:» trước tên. Trần tăng từ 6 lên 8 cụm. Vẫn KHÔNG nhận từ ngoài từ vựng, kể cả trong
   ngoặc hay sau gạch: «tác vụ tháng (quy trình `x`)», «tác vụ tháng — gọi agent `x`», «Tác vụ (agent) `x`» không bị bắt. Đo
   trên 909 tệp `.md` đang track: regex mới cho đúng tập khớp như regex cũ (không thêm, không bớt) ⇒ không thêm báo động nào trên
   kho hiện có. CLAUDE.md và AGENTS.md vẫn PASS.

**Kiểm hồi quy:** `tools/test_hom_viec_trang_va_doctrine_lich_20261114.py` (42 test; test `main()` có rào chặn mạng: vá
`doc_ci_mot_repo`, cấm `urlopen` và `socket.connect`). Đột biến 22 phép: 21 đỏ đúng test, 1 sống sót tương đương (bỏ ranh giới
từ `(?![^\W_])` sau từ vựng: ký tự kế tiếp bắt buộc đã là khoảng trắng, «:(», gạch, «)» hoặc dấu huyền — cùng kết luận với
thẩm định #356).

**Chưa làm (ngoài phân chia tệp):** tiêu đề «🟢 Mọi kỳ lịch nền … đúng hẹn» của chính `tools/kiem_lich_nen.py` vẫn in khi có
dòng ⚪ bên dưới. Đây là thiết kế có chủ ý từ 26/09 (#35), được khoá bởi `test_lich_nen_co_tac_vu_do_duoc_van_xanh` trong
`tools/test_do_tuoi_lich_nen_20260926_log_anh_em.py`. Muốn đổi phải giao rõ cả hai tệp.
