# 15/11/2026 — Thiết kế: chuẩn báo cáo, nhãn thiết kế và kiểm soát sai lệch chưa đồng bộ với SAP (giai đoạn 4)

**Bác sĩ (nguyên văn):** «Tiếp tục giai đoạn 4» — trong chương trình «Hãy đảm bảo sự đồng bộ xuyên suốt và chính xác nhất».

## Phát hiện (kiểm tay C1a, BTM)

| Chỗ hở | Đề tài | Chi tiết |
|---|---|---|
| Chuẩn báo cáo lệch giữa tài liệu | C1a | Đề cương nộp ghi «STROBE và CROSS» (nghiên cứu khảo sát); G1, gói đạo đức G2 và SAP chỉ ghi «STROBE». |
| Chuẩn báo cáo lệch giữa tài liệu | BTM | SAP ghi «STROBE + RECORD» (dữ liệu thường quy); dòng chuẩn báo cáo của G1 chỉ ghi «STROBE». |
| Nhãn thiết kế không theo mục tiêu | C1a, BTM | G1, gói G2, SAP C1a và TRDS mục 15 ghi «Cắt ngang Mô tả (Cross-sectional / Prevalence)». Cả hai đề tài đều có mục tiêu PHÂN TÍCH yếu tố liên quan, và đề cương C1a ghi «mô tả cắt ngang có phân tích». |
| Tiêu đề SAP ghi sai phiên bản | C1a | Tiêu đề ghi 1.4 trong khi bảng lịch sử đã có 1.5. G10 in phiên bản lấy từ tiêu đề. |
| SAP thiếu phân tích mà G1/đề cương đã hứa | C1a | (1) Kế hoạch không đáp ứng (G1 `non_response_plan`, đề cương 4.4.2): tỷ lệ đồng ý/hoàn thành, so sánh người từ chối với người tham gia. (2) Đặc tính đo lường trong mẫu (đề cương 4.5.3): Cronbach's alpha/omega, EFA/CFA chia đôi mẫu và ngưỡng phù hợp. (3) Phân tích thăm dò định trước vai trò trung gian của kỳ vọng (đề cương 4.10, Phụ lục D.3). |
| SAP thiếu phân tích mà G1 đã hứa | BTM | So sánh tuổi, giới, nhóm đối tượng giữa người bị loại vì chỉ có 1 lượt khám và mẫu nghiên cứu. |
| Chưa có mối nối máy | mọi đề tài | Bảng kiểm soát sai lệch G1 không được đối chiếu với SAP. Trục `thiet_ke` chỉ so MÃ thiết kế. |

## Cách vá

**Repo y khoa:**
- `skill_standards`, một nguồn sự thật cho mọi bộ sinh và trục:
  - `chuan_bao_cao_de_tai`: thu mới bằng phiếu/khảo sát ⇒ CROSS; chỉ dùng dữ liệu thường quy ⇒ RECORD; vừa thu mới vừa ghép HIS ⇒ RECORD do PI quyết qua `gate_params.G1.reporting_extensions`. Câu «không thu mới» được đọc là phủ định.
  - `nhan_thiet_ke_theo_muc_tieu`.
- **Bộ sinh:**
  - G1 ghi nhãn và chuỗi chuẩn báo cáo của đề tài vào checkpoint; A2 có dòng nguồn và dòng «⚠ Cân nhắc RECORD».
  - G10 in «Chuẩn báo cáo áp dụng» lấy từ G1.
  - G2 và G4 vốn đã đọc từ G1.
- **Công cụ mới `tools/doi_chieu_sai_lech_sap.py`** (SL-01…SL-08) với bảng `_doi-chieu-sai-lech-sap.csv`. Chạy trên SAP cũ, công cụ bắt đúng 3 chỗ hở của C1a và 1 của BTM.
- **Ba trục mới của `nhat_quan_xuyen_cong`:**
  - `chuan_bao_cao` (G1·G2·G4·G10)
  - `mo_ta_thiet_ke` (G1·G2·G4·G10): nhãn theo mục tiêu; tuyển mẫu G2 ↔ cách thu thập G1; phiên bản tiêu đề SAP.
  - `kiem_soat_sai_lech` (G1·G4·G10)
- **Dữ liệu:**
  - SAP C1a 1.5 (chưa ký lại):
    - nhãn «có phân tích», STROBE + CROSS, tiêu đề 1.5;
    - §3 thêm kế hoạch không đáp ứng và đặc tính đo lường, chép nguyên đề cương 4.4.2 và 4.5.3;
    - §10 thêm gói `psych`/`lavaan` (đề xuất của bản nháp);
    - §5 thêm phân tích thăm dò kỳ vọng với ô «[CẦN THỐNG KÊ VIÊN CHỌN …]», vì đề cương chưa nêu phương pháp.
  - SAP BTM sửa nháp 3: §1 thêm so sánh nhóm 1 lượt khám.
  - Dựng lại G1 cho hai đề tài (vẫn PASS_G1_CONFIRMED; G0–G3 không đổi).
  - Gói G2 và TRDS mục 15 C1a: sửa đúng dòng, không chạy lại bộ sinh vì gói từng được sửa tay.
  - Bảng đối chiếu sai lệch: C1a 11 dòng, BTM 11 dòng, cả hai ĐẠT.

**Repo gốc:** dạy `thiet-ke-nghien-cuu`, `dieu-phoi-g1`, `dieu-phoi-g2`, `dieu-phoi-g4`, `dao-duc-dang-ky`.

## Kiểm hồi quy

- `tests/test_thiet_ke_20261115.py`: 22 ca; 15/15 đột biến đỏ đúng ca.
- Đo thật sau vá:
  - BTM: ba trục mới đều khớp.
  - C1a: `chuan_bao_cao` lệch mềm chỉ vì đề cương thống nhất G10 cũ (hết khi lắp lại G10), cộng thêm RECORD chờ PI quyết; `mo_ta_thiet_ke` cần xem chỉ vì G10 cũ; `kiem_soat_sai_lech` khớp.

## Bài học vận hành

- `g0_quality_gate.py` chạy dòng lệnh mặc định là GHI checkpoint/báo cáo. Chạy bằng python hệ thống (thiếu từ điển VI→EN) đã ghi đè G0 C1a thành DRAFT; đã khôi phục từ git. Chẩn đoán thì dùng `~/.ebm-venv/bin/python` và cờ `--no-write`.
- Dựng lại G1 C1a kéo theo khối COSMIN (bản vá nhóm B3 ngày 12/11, vì có thư mục `pha_cong_cu/`). Khối này còn ô [CẦN] chung chung, trong khi đề cương 4.5 đã có nội dung thật. Nối hai bên là việc của giai đoạn 5 (công cụ đo lường).

## Còn mở (việc của người)

| Đề tài | Việc | Vai |
|---|---|---|
| C1a | Chọn phương pháp phân tích thăm dò vai trò trung gian của kỳ vọng (SAP §5), rồi ký lại G4 (SAP 1.5) | thống kê viên |
| C1a | Quyết RECORD cho phần mốc HIS ghép với phiếu: ghi `gate_params.G1.reporting_extensions` (vd `["CROSS", "RECORD"]` hoặc `["CROSS"]`), hoặc ghi lý do không áp dụng ở đề cương | PI |
| C1a | Sau khi ký lại G4: agent lắp lại G10, rồi PI ký G10 | agent → PI |
| BTM | Ký G4 khi chốt SAP | thống kê viên/PI |
