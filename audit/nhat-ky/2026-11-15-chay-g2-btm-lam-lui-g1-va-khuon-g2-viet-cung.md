# 15/11/2026 — Chạy G2 cho BTM làm lùi G1/G3/G4; khuôn G2 viết cứng «không có PII» và «lưu 5 năm»

**Bác sĩ (nguyên văn):** «Chạy G32 cho BTM;C1a giải quyết đồng bộ tốt nhất giúp tôi», rồi «CHạy G2».

## Phát hiện

| # | Phát hiện | Gốc |
|---|---|---|
| 1 | Sau lượt `run_g2_auto` đầu tiên cho BTM, ba cổng lùi trạng thái: **G1** PASS → cần xem (G1-HUMAN-08), **G3** PASS → G3-AUTO-01, **G4** `READY_FOR_SIGNATURE` → G4-AUTO-12. | `run_g2_auto` gọi `ensure_study_meta(seed={"title", "design_code"})`. BTM chưa ghim `design_code` nên G2 chèn khoá này, mà `g1_quality_gate.dau_van_tay_g1` tính cả khoá đó ⇒ dấu quyết định G1 đổi (91fc5cda… → e5657f68…) ⇒ xác nhận của chủ nhiệm hết khớp, và G3, G4 lùi theo, dù thiết kế không đổi. C1a không dính vì đã có sẵn khoá này. |
| 2 | Khuôn đề nghị miễn ICF in cứng «Mã hóa: Không cần (không có PII)» và «Kế hoạch hủy: Lưu trữ 5 năm sau công bố theo quy định» cho mọi đề tài. | BTM có bảng nối mã nghiên cứu ↔ mã người bệnh (có dữ liệu cá nhân tới khi khử định danh), và PI chưa quyết thời hạn lưu trữ. Khuôn đã khẳng định thay người. |
| 3 | Bảng rủi ro cắt ngang luôn nói «Rò rỉ thông tin từ bộ câu hỏi», «Gánh nặng thời gian — bộ câu hỏi ngắn». | Sai với đề tài chỉ trích hồ sơ (BTM). |
| 4 | Trục `ket_cuc_chinh` rơi về lệch mềm dù TRDS mục 19 chép **nguyên văn** G1. | Chủ nhiệm đã xác nhận tập {G0, G1} (dấu ea600fdb…). Dấu băm «cổng · nơi · giá trị», nên mỗi bản sao trùng chữ đều làm xác nhận hết hiệu lực. |
| 5 | Trục `quan_the` báo «G2 thiếu: lọc máu, ghép, có thai…» (BTM) và «thiếu tên đơn vị» (C1a). | Trục chỉ đọc phần tiêu chí chọn của TRDS mục 14, trong khi WHO định nghĩa mục 14 gồm cả tiêu chí loại. Bản đăng ký thật có đủ. |
| 6 | C1a: `run_g10_assemble` từ chối lắp lại (mã 3): «G10 đã có chữ ký PI nhưng gói hiện tại không còn khớp manifest … ghi quyết định G10 mới có chủ ý trước khi lắp lại». | Đúng chốt bảo vệ — cần quyết định của PI. Agent không vượt. |
| 7 | C1a: bản G3/G5 vẫn in tên chủ đề G0. | Hai tệp sinh trước khi bộ sinh được sửa để in tên chính thức. |

## Cách vá (repo y khoa)

- **Gieo study_meta ở G2:** chỉ gieo `title`, không gieo `design_code`.
  - Chạy lại G2 cho BTM: `study_meta.json` không đổi; G1, G3 về PASS; G4 về `READY_FOR_SIGNATURE`; 🔴 = 0.
  - Phiên khác đã mở drluanbv175/medical-ebm-automation#281 sửa CÙNG gốc lỗi theo hướng bác sĩ chọn sau thẩm định #277 (gieo `{"title"}`, bản sao máy ghi vào `study_meta.design_code_tu_g1`; ghim thiết kế cần dấu người). Khối mã trong drluanbv175/medical-ebm-automation#283 được đưa về **giống hệt từng chữ** #281 để hai PR gộp sạch; bỏ hàm riêng `hat_giong_meta_g2` (thử gộp không ghi: chỉ còn xung đột ở hai tệp manifest sinh tự động).
- **Khuôn G2 lấy quy trình dữ liệu đã chốt** (`_quy-trinh-du-lieu.csv`):
  - `dam_bao_bao_mat_mien_icf` dựng «Mã hóa»/«Kế hoạch hủy»; chưa chốt thì để `[CẦN PI QUYẾT …]`;
  - `khoi_quy_trinh_g2` in khối đã chốt ở đầu TL6;
  - `ap_nguon_du_lieu` thay bảng rủi ro cho đề tài cắt ngang chỉ dùng dữ liệu thường quy.
- **`nhat_quan_xuyen_cong`:**
  - `ban_sao_nguyen_van_cua_tap_da_xac_nhan`: xác nhận còn hiệu lực khi có tập con nguồn mang đúng dấu đã ký và mọi nguồn khác trùng nguyên văn; diễn đạt mới vẫn làm hết hiệu lực; dấu của các xác nhận hiện có không đổi;
  - trục `quan_the` đọc cả tiêu chí chọn lẫn loại của TRDS mục 14 và `G1.exclusion_criteria`.
- **Bộ xuất Word:** `md2docx_vn._GLYPH_SUBSTITUTE` thêm «✓»/«✔» → «■» (Times New Roman không có glyph dấu tick).
- **Dữ liệu:**
  - BTM: gói G2 sinh mới; neo `neo_g2` cho `an_danh` và `huy_bang_noi`.
  - C1a: dòng «Đề tài» của G3/G5 thay bằng đúng chuỗi bộ sinh in (`ten_de_tai.ten_chinh_thuc`); xuất lại Word.

**Repo gốc:** dạy `dao-duc-dang-ky`, `dieu-phoi-g2`, `dieu-phoi-nghien-cuu`.

## Kiểm hồi quy

| Tệp test | Số ca | Đột biến |
|---|---|---|
| `tests/test_ket_cuc_ban_sao_nguyen_van_20261115.py` | 6 | 5/5 đỏ, sau khi bổ sung ca mức trục — hai đột biến sống sót ở lượt đầu |
| `tests/test_g2_quy_trinh_du_lieu_20261115.py` | 5 | 4/4 đỏ |
| `tests/test_g2_dau_cuoi_dong_bo_20261115.py` (chạy thật `run_g2_auto --skip-registry`) | 2 | 3/3 đỏ ở đường nối `main()`, gồm đột biến gieo lại `design_code` |

## Đo sau khi vá

| Đề tài | Kết quả |
|---|---|
| BTM | 0 lệch cứng · 0 lệch mềm · 19 khớp · 3 cần xem (PI đã xác nhận kết cục; lưu trữ/hủy chờ PI; đặc tả chờ duyệt) · 2 chưa đủ để so (chưa có đề cương nộp) |
| C1a | 0 lệch cứng · 2 lệch mềm · 21 khớp · 4 cần xem — đều chờ người: ký SAP 1.5; PI ghi quyết định G10 mới rồi agent lắp lại gói; duyệt đặc tả; RECORD |
