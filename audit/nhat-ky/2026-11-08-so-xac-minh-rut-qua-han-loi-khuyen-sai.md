# 08/11/2026 — Sổ xác minh nguồn: 94 bản ghi «ok» quá hạn kiểm rút bài kẹt vĩnh viễn, báo cáo khuyên nhầm NCBI_API_KEY

**Phát hiện:** `so_xac_minh_nguon.py --bao-cao` báo «94 mục: CHƯA kiểm được RÚT BÀI … thêm `NCBI_API_KEY` … [MA]
CAN_NCBI_API_KEY». Đã chạy `--quet --vong 3` (mọi dashboard), `--quet-ledger --vong 3` («cần kiểm 0»), `--phu-mo-coi --vong 3`
(«+94 xác minh») — báo cáo vẫn 94. Chạy `--kiem-rut-lai` cho đúng 94 định danh (`ghi_chu_rut == "ok"`, `kiem_rut_luc` > 30 ngày)
⇒ 94/94 «ok (chuỗi 3 tầng)»/«ok (Crossref)», báo cáo còn 0. Không cần khoá API.

**Gốc:**
1. `--phu-mo-coi` gom mọi bản ghi hết hiệu lực, gọi lại `xac_minh_mot` (xác minh TỒN TẠI) cho cả bản ghi chỉ quá hạn kiểm rút
   bài — việc thừa — rồi chỉ kiểm rút bài cho PMID CHƯA TỪNG kiểm. Bản ghi «ok» quá hạn và mọi DOI không bao giờ được kiểm lại ở
   nhánh này; `--quet` chỉ kiểm lại định danh đang được dashboard trích ⇒ nhóm mồ côi kẹt vĩnh viễn.
2. `--bao-cao` gộp «kiểm rút bài đã N ngày» (đã TỪNG kiểm được) với «chưa kiểm rút bài lần nào» dưới một lời khuyên khoá API —
   đúng lớp lỗi BH14 (lời khuyên lệch đòn bẩy làm bác sĩ đi sửa một cấu hình không sai).

**Vá:**
- `--phu-mo-coi`: chỉ xác minh lại tồn tại khi phần tồn tại quá hạn (`_can_xac_minh_ton_tai`); sau đó tái kiểm rút bài cho MỌI
  PMID/DOI chưa dương tính có kiểm rút bài vắng hoặc quá hạn (`_can_kiem_rut`) qua `kiem_rut_lai_dich_danh` — whitelist trạng thái
  đóng, luật bất đối xứng giữ nguyên (không bao giờ xoá dương tính cũ; «không tra được» không ghi `kiem_rut_luc`).
- Tách `kiem_rut_doi()` (Crossref) thành hàm riêng để dùng chung và để test chặn mạng.
- `--bao-cao`: nhóm mới «QUÁ HẠN kiểm rút bài» với mã `[MA] CAN_KIEM_RUT_LAI` và lời khuyên `--quet` / `--phu-mo-coi` /
  `--kiem-rut-lai`; nhóm «CHƯA kiểm được RÚT BÀI» giữ nguyên mã `CAN_NCBI_API_KEY` / `CAN_TAI_RETRACTION_WATCH` (chốt BH14 không
  đổi). `tools/chu_trinh_chung_cu.py` đọc mã mới.

**Kiểm:** `tools/test_so_xac_minh_rut_qua_han_20261108.py` (7 ca) + `tools/test_chu_trinh_chung_cu_kiem_rut_lai_20261108.py`;
5 đột biến (chỉ PMID chưa từng kiểm · xác minh lại tồn tại tất cả · gộp quá hạn vào chưa kiểm · bỏ điều kiện quá hạn · bỏ nhánh
mã mới ở chu trình) đều đỏ, phục hồi xanh. Fixture `test_so_xac_minh_phu_mo_coi_20260927.py` thêm chặn mạng `kiem_rut_doi`. Toàn
bộ test sổ xác minh + chu trình: 110 đạt. Chạy `bao_cao()` trên bản sao sổ thật với 3 mục giả lập quá hạn ⇒ đúng nhóm và mã mới.
