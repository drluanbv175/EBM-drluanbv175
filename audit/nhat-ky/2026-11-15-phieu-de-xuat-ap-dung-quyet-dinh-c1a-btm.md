# 15/11/2026 — Phiếu đề xuất: bác sĩ chọn 9 mục, máy áp dụng và đồng bộ; khuôn miễn ICF ghi sai «ẩn danh hoàn toàn»

**Bác sĩ (nguyên văn):** «Phiếu quyết định — việc chờ người của C1a và BTM (15/11/2026) hãy tạo đề xuất để tôi chọn và xác thực».

## Cách làm

- Soạn phiếu đề xuất `PHIEU-DE-XUAT-C1A-BTM_20261115.md`: mỗi mục có phương án, một phương án «Đề xuất» kèm lý do, căn cứ kiểm được.
  - Bốn trích dẫn phương pháp trung gian và RECORD đã tra PubMed (khớp tác giả, tạp chí, năm, DOI) và kiểm rút bài bằng chuỗi 3 tầng: chưa bài nào bị rút.
  - Tiền lệ lấy từ chính hồ sơ: thời hạn lưu trữ C1a, câu đề cương 4.10 / Phụ lục D.3.
- Bác sĩ chọn qua hộp hỏi đáp; **cả 9 mục đều chọn phương án đề xuất**.
- Mọi lựa chọn ghi nguyên văn vào `exports/<mã>/_quyet-dinh-bac-si-20261115.json`; `study_meta.json` được sao lưu trước mỗi lần ghi.

## Áp dụng

| Đề tài | Mục | Áp dụng |
|---|---|---|
| BTM | B1 | `gate_params.G10.xac_nhan_ket_cuc_chinh` dấu be7a10ba02e38f7d — thay xác nhận lúc máy chưa đọc được SAP §2 |
| BTM | B2 · B4 · B5 | `gate_params.G2`: `icf_waiver_requested`, `public_title`, `health_condition`, `protocol_version`, `icf_version`, `registration_required = false`, `recruitment_mode = RETROSPECTIVE_SECONDARY_DATA` |
| BTM | B3 | `_quy-trinh-du-lieu.csv`: lưu 2 năm; xoá an toàn có biên bản; neo G2 |
| BTM | B6 · B9 | Sổ tiến độ: 1.10 tạm dùng bố cục C1a; 3.2 xong; 3.7 viết sau khi G2 sẵn sàng |
| C1a | C1 | SAP 1.5 §5: trung gian nhân quả dựa trên hồi quy; §10 thêm gói `mediation`. Đề cương nộp 4.10 thêm phương pháp + 4 tài liệu tham khảo [53]–[56] (đánh số lại Vancouver). Đặc tả G6 cập nhật. |
| C1a | C3 | «Chưa nộp» ⇒ cập nhật đề cương nộp trực tiếp; không cần thủ tục sửa đổi |
| C1a | C5 | `gate_params.G1.reporting_extensions = [CROSS, RECORD]`. Sinh lại G1. SAP, gói G2, đề cương nộp ghi «STROBE + CROSS + RECORD» (+ tài liệu [33] Benchimol 2015). Biên nhận A12 làm mới với 40 PMID. Đề cương nộp ĐẠT K1–K7. |
| C1a | G1 | C5 làm dấu G1 đổi. Máy chứng minh thay đổi duy nhất là khoá `reporting_extensions` (bỏ khoá ⇒ dấu cũ e7446048…), rồi **hỏi**. Bác sĩ trả lời «Chốt G1» ⇒ ghi xác nhận dấu a1092035d7005539. |

## Phát hiện và vá

| # | Phát hiện | Vá |
|---|---|---|
| 1 | TÀI LIỆU 9 (đề nghị miễn ICF) đánh dấu sẵn «☑ … không truy ngược cá nhân» và «dữ liệu đã ẩn danh». BTM có bảng nối mã ↔ người bệnh tới khi khoá dữ liệu, tức dữ liệu là **giả danh hoá**. | `run_g2_auto.dieu_kien_mien_icf`: có bảng nối ⇒ điều kiện 1 và 3 lấy nguyên văn cam kết đã chốt. PI đã chọn xin miễn ⇒ dòng `[CẦN BÁC SĨ XÁC NHẬN…]` thay bằng ghi nhận quyết định. |
| 2 | Lỗi thao tác của máy: `check_citations.py --pmids` được truyền danh sách cách nhau bằng dấu cách, nên bị coi là MỘT PMID và **ghi đè biên nhận A12 đúng bằng biên nhận hỏng**. | Khôi phục bằng `git checkout --` ngay; chạy lại với chuỗi phân cách bằng dấu phẩy và HỢP PMID. Đã dạy agent. |

## Đo sau khi áp dụng

| Đề tài | Trục | Cổng |
|---|---|---|
| BTM | 21 khớp · **0 lệch mềm** · 2 cần xem · 2 chưa đủ để so | G1, G3 PASS · G2 bản nháp chỉ còn ô [CẦN] của chủ nhiệm + quyết định Hội đồng · G4 `READY_FOR_SIGNATURE` |
| C1a | 22 khớp · 2 lệch mềm · 4 cần xem — đều chờ C2/C4/C6 | G1, G3 PASS · G2 `READY_FOR_IRB_SUBMISSION` · **G4 lên `READY_FOR_SIGNATURE`** (trước là bản nháp chờ nội dung) |

**Repo gốc:** dạy `dao-duc-dang-ky`, `dieu-phoi-nghien-cuu`.

**Kiểm hồi quy:** `tests/test_g2_quy_trinh_du_lieu_20261115.py` thêm 2 ca; 3/3 đột biến đỏ đúng ca.

## Còn mở (việc ký của người)

| Việc | Vai |
|---|---|
| C2: ký SAP 1.5 | thống kê viên + PI |
| C4: ghi quyết định G10 mới ⇒ máy lắp lại gói ⇒ ký | PI |
| C6: duyệt đặc tả G6 (dấu 41c904db6807) | thống kê viên / PI |
| B7: ký SAP | thống kê viên + PI |
| B8: duyệt đặc tả G6 (dấu b23936640ab1) | thống kê viên / PI |
| Điền các ô [CẦN] của hồ sơ G2 BTM (họ tên, chức danh…) | chủ nhiệm |
