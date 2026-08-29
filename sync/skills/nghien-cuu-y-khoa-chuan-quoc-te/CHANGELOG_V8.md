# Cập nhật v8 (nội dung 5.2) — 2026-06-06

Đợt bảo trì theo `workflows/08`: tái kiểm chứng nguồn pháp lý Việt Nam với nguồn sơ cấp. Không thay đổi khung phương pháp, cổng chất lượng G0-G9 hay nội dung chuyên môn.

## Báo cáo phát hành tối thiểu (theo workflow 08)

- **Phiên bản:** nội dung 5.2 (CHANGELOG v8).
- **Ngày:** 2026-06-06.
- **Người chỉnh sửa:** bảo trì tự động qua Claude (có đối chiếu nguồn chính thức); tác giả con người kiểm chứng và chịu trách nhiệm.
- **File đã thay đổi:**
  - `references/00_nguon_chinh_thuc_va_quy_tac_cap_nhat.md` — thêm mục "Tái kiểm chứng bổ sung (2026-06-06)".
  - `MANIFEST.md` — bump phiên bản 5.1 → 5.2, ngày 2026-06-06.
  - `CHANGELOG_V8.md` — tệp này.

## Chuẩn/pháp lý được tái kiểm chứng và nguồn

Đối chiếu trực tiếp nguồn sơ cấp; **xác nhận các mốc đang dùng vẫn là bản hiện hành, không có thay đổi** so với rà soát 2026-05-30:

- **Thông tư 43/2024/TT-BYT** — ban hành 12/12/2024; hiệu lực **01/02/2025** theo Điều 22 (trích nguyên văn: "Thông tư này có hiệu lực thi hành kể từ ngày 01 tháng 02 năm 2025"); thay thế Thông tư 04/2020/TT-BYT (05/3/2020). Nguồn: thuvienphapluat.vn; Cổng thông tin Bộ Y tế (moh.gov.vn).
- **Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15** — thông qua 26/6/2025; hiệu lực **01/01/2026** (đã có hiệu lực tại thời điểm rà soát). Nguồn: chinhphu.vn; bocongan.gov.vn; vbpl.vn.

Lưu ý phân biệt thường gặp: **12/12/2024 là ngày KÝ ban hành** của Thông tư 43/2024/TT-BYT, **không phải** ngày hiệu lực (01/02/2025).

## Kết quả script kiểm tra

- `python scripts/validate_skill.py` → ĐẠT.
- `python scripts/run_static_evaluations.py` → ĐẠT.

## Rủi ro còn tồn tại

- Văn bản pháp luật và chuẩn báo cáo có thể được sửa đổi sau ngày kiểm chứng; phải đối chiếu lại nguồn chính thức trước mỗi sản phẩm chính thức (giữ nguyên quy tắc của `references/00`).
- Kiểm tra tĩnh không thay thế kiểm thử hành vi của Claude sau upload và rà soát chuyên gia.

## Không thay đổi

- Khung cổng chất lượng G0-G9, cấu trúc progressive disclosure, các module/workflow/template và bộ kiểm thử giữ nguyên.
