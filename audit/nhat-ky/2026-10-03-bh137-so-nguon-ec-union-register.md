# 03/10/2026 — BH137 ĐỎ trên cây chính: module nguồn `ec_union_register.py` của engine chưa có mục trong sổ nguồn

**Triệu chứng.** `python3 tools/chot_hoi_quy_bai_hoc.py` trên cây chính (master `6c844b7`, repo y khoa
`feat/r1-1-2-design-gap-remediation`) báo BH137 ✗ «engine có module nguồn CHƯA khai trong sổ: ec_union_register.py».

**Nguyên nhân.** PR y khoa #63 (commit `a85f35d`, 01/10/2026 — «VPN luôn bật») thêm `app/sources/ec_union_register.py`. Đây là Sổ đăng
ký Liên minh của Uỷ ban châu Âu, đường DỰ PHÒNG của danh mục EMA (SRC-048) khi CloudFront của EMA chặn IP thoát VPN. Repo gốc không có
mục sổ tương ứng, nên `sources_health.py` và tuyên bố độ phủ không thấy nguồn này. Đây đúng là loại lỗ BH137 sinh ra để bắt (30/09:
RxNorm/EMA/Scite/Unpaywall).

**Vá.**
- `data/sources.json` thêm SRC-052:
  - Đo SỐNG 03/10/2026 bằng client thật, không cache: 1.554 thuốc người đang lưu hành + 447 không còn lưu hành, 3,0 giây.
  - `terms_ok: null`, vì trang legal-notice của commission.europa.eu trả 403 cho truy cập tự động; không khẳng định điều khoản từ trí nhớ.
  - Không thêm điểm thăm `DIEM_THAM`: một lần thăm phải tải cả trang ~1,2 MB, và ping ≠ thu hoạch (BH50).
  - Ghi giới hạn của nguồn: chỉ có ĐANG / KHÔNG CÒN lưu hành, không có lý do hay ngày.
- `_BH137_MODULE_NGUON["ec_union_register.py"] = ("SRC-052",)`.

**Kiểm.**
- BH137 ✓ với engine thật (symlink tạm, đã gỡ); toàn bộ chốt 🟢 «Không bài học nào tái phát».
- `test_chot_bh137_bh138_20260930_so_nguon_noi_that.py` 22/22.
- `tuyen_bo_do_phu.py` tự liệt kê «EC Union Register» trong nhóm gọi theo yêu cầu.
- `pytest tools/` (bản sao trần) xanh.
