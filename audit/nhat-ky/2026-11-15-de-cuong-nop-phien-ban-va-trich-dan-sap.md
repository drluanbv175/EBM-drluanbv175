# 15/11/2026 — Đề cương nộp: bìa thiếu phiên bản, trích phiên bản SAP cũ (giai đoạn 6)

**Bác sĩ (nguyên văn):** «Tiếp tục» — giai đoạn 6 (viết đề cương) trong chương trình «Hãy đảm bảo sự đồng bộ xuyên suốt và chính xác nhất».

## Phát hiện (kiểm tay C1a; BTM chưa có đề cương nộp)

`kiem_de_cuong_nop_hoi_dong.py` (K1–K7) cho C1a «ĐẠT», nhưng công cụ này chỉ kiểm HÌNH THỨC: đủ chương mục, Word khớp md, không ký hiệu nội bộ, N khớp G3, PMID đã kiểm rút bài, không PII. Đối chiếu NỘI DUNG với quyết định đã chốt:

| Điểm | Kết quả |
|---|---|
| Bìa đề cương ghi phiên bản/ngày | **Thiếu.** G1/G2 khai `protocol_version` 1.0; phiếu đồng ý ở phụ lục có «Phiên bản 1.0, ngày ……/……/2026». Hội đồng đòi phiên bản và ngày trên mọi tài liệu nộp. |
| Phiên bản kế hoạch phân tích được trích | **Lệch:** đề cương ghi «phiên bản 1.4 (đã khoá)»; SAP hiện 1.5 (sửa ở giai đoạn 1–4, chờ thống kê viên ký lại). |
| Phiên bản phiếu đồng ý | khớp (1.0 = `G2.icf_version`) |
| Thời gian thực hiện | khớp (12/2026–12/2028 = `G1.study_period`) |
| Bảng kinh phí | khớp (11 khoản = `G1.budget`) |
| Phân tích định trước ở đề cương 4.10 ↔ SAP | khớp: 7 phân tích độ nhạy, phân tích giới hạn cho người bỏ về, tỷ lệ chênh tương xứng một phần khi vi phạm giả định, Firth, trọng số, quy tắc gộp mức |

## Cách vá

**Repo y khoa:**
- **Trục mới `de_cuong_nop` của `nhat_quan_xuyen_cong`** (G2·G4·G10):
  - DC-01: bìa ghi phiên bản = protocol_version G1/G2. «Bìa» là phần trước đường kẻ «---» đầu tiên; bỏ qua dòng nói về SAP/phiếu.
  - DC-02: phiên bản SAP được đề cương trích = tiêu đề SAP.
  - DC-03: phiếu đồng ý ở phụ lục = `icf_version`.
  - DC-04: thời gian thực hiện = `study_period`.
  - DC-05: khoản chi = `G1.budget`. Chỉ đọc đúng bảng liền sau «Dự trù kinh phí», không tràn sang bảng rủi ro.
- **Dữ liệu C1a:**
  - thêm «**Phiên bản đề cương:** 1.0, ngày ……/……/2026» lên bìa;
  - sinh lại `.docx` bằng `tools/md_sang_docx_times.py --co-chu 13 --trang-de-cuong` (chạy ở thư mục OneDrive gốc, có `medical-ebm-automation/` lồng bên trong, để áp chuẩn trình bày);
  - K1–K7 vẫn ĐẠT; Word giữ đủ 30 bảng.
- **Không sửa câu trích SAP 1.4:** SAP 1.5 chưa ký, ghi trước «1.5 đã khoá» là ghi điều chưa xảy ra.

**Repo gốc:** dạy `viet-ban-thao`, `dieu-phoi-g10`, `dao-duc-dang-ky`.

## Kiểm hồi quy

- `tests/test_de_cuong_20261115.py`: 8 ca; 8/8 đột biến đỏ đúng ca.
- Lượt đầu, test bắt đúng một lỗi của chính trục: «bìa = 40 dòng đầu» lẫn câu «phiên bản 1.0» của SAP trong thân bài đề cương ngắn. Đã sửa: bìa dừng ở đường kẻ «---».

## Bài học vận hành

- Công cụ Word của repo gốc chạy từ worktree tách rời không thấy `medical-ebm-automation/`, nên bỏ qua chuẩn trình bày (báo «CHƯA đạt chuẩn nộp»). Phải chạy bản ở thư mục OneDrive gốc.

## Còn mở (việc của người)

| Đề tài | Việc | Vai |
|---|---|---|
| C1a | Thống kê viên ký SAP 1.5; sau đó agent sửa câu trích phiên bản SAP trong đề cương nộp (mục 4.4 và 4.10) và sinh lại Word; lắp lại G10; PI ký G10 | thống kê viên → agent → PI |
| C1a | Điền ngày trên bìa đề cương và phiếu đồng ý khi nộp Hội đồng | PI |
| BTM | Chưa có đề cương nộp (mới có mục lục dự kiến) — viết đề cương là việc riêng, cần PI đồng ý mở | PI |
