# 04/10/2026 — Tầng thứ bậc trống bị tầng «mới vào PubMed» che: cảm biến «mù» không thấy (BH157)

**Phát hiện:** khi đo sống 04/10 để bác sĩ duyệt đề xuất watchlist (10 chủ đề «mù»), bảng sản lượng cho thấy thêm 10 chủ đề
KHÔNG bị gắn «mù» nhưng có 0 tổng quan hệ thống/gộp, và guideline + SR + RCT ≤ 1 trong 90 ngày. Đó là: statin, CKD, COPD,
CKM, GDMT, lão khoa, phản vệ, Dengue, HS, AI/CDS. Tầng «mới vào PubMed» của các chủ đề này vẫn có 6–49 bản ghi.

**Vì sao cảm biến không bắt:** `kiem_san_luong_giam_sat.py` gắn «mù» khi TỔNG 4 tầng ≤ 3. Tầng «mới vào PubMed» không lọc theo
thiết kế nghiên cứu nên đẩy tổng lên trên ngưỡng. Trong khi đó, với lĩnh vực như statin, CKD hay COPD, việc 0 tổng quan trong
cả một quý gần như chắc là do truy vấn ở tầng thứ bậc quá hẹp, không phải do thiếu chứng cứ.

**Vá:**
- Thêm tín hiệu 🟠 `thu_bac_trong`: chủ đề đo trọn, không mù, tầng `sr_ma` = 0 và guideline + sr_ma + rct ≤ `NGUONG_THU_BAC` (1).
- Tín hiệu được tính từ chính các tầng, nên tệp `--json` cũ vẫn in đúng.
- KHÔNG đổi mã thoát, vì `chu_trinh_chung_cu` đọc mã 1 là «có chủ đề mù».
- `chu_trinh_chung_cu` đọc khoá JSON và nêu thành việc 🟠. Khi cảm biến không đo được (mã 2) thì chu trình không đọc tệp state cũ.
- Dạy luật ở `CLAUDE.md` §6.4.

**Kiểm:**
- `tools/test_thu_bac_trong_20261004.py`: 14 test.
- Đột biến 9/9; BH157 đột biến 4/4 đỏ đúng chỗ.
- Đo thật 04/10 bằng bản mới trên watchlist đã áp dụng: 0 🔴, 10 🟠 (đúng 10 chủ đề nêu trên), mã thoát 0.

**Việc tiếp:** máy soạn đề xuất đợt 2 cho 10 chủ đề 🟠 vào `EBM-Dashboards/watchlist.de-xuat.json`, bác sĩ duyệt bằng
`python3 tools/ap_dung_de_xuat_watchlist.py`. Tín hiệu chỉ là NGHI để soạn lại truy vấn, không kết luận lĩnh vực thiếu chứng cứ.
