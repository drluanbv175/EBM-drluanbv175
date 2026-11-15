# 15/11/2026 — Kiểm lại toàn hệ theo khung 12 bước: bản Word lọt bản cũ, gói đã ký hết khớp, đo sai chỗ sổ cái

**Bác sĩ (nguyên văn):** «Sau đó kiểm tra lại Hệ thống xây dựng mặc dù đã kết luận về tính hoàn thiện nhưng kiểm lại thì không đạt được sự thống nhất, đồng bộ ....Kết luận, một nghiên cứu y khoa tin cậy là sản phẩm của một quy trình khoa học nghiêm ngặt, được lên kế hoạch kỹ lưỡng ngay từ đầu và được thực hiện với sự trung thực tuyệt đối.» Bác sĩ gửi kèm khung 12 bước (3 giai đoạn) và 5 yếu tố then chốt (Validity, Precision & Reliability, Objectivity, Ethics, Transparency).

**Cách đo:** sau khi xong giai đoạn 8–9, chạy `nhat_quan_xuyen_cong` (27 trục C1a, 24 trục BTM) và `kiem_chi_tiet_he_nghien_cuu` (11 cổng × 5 trục) cho C1a và BTM, trên worktree có đủ thay đổi giai đoạn 1–9. Cây OneDrive lạc hậu 19 commit nên không dùng để đo.

## Phát hiện

| # | Phát hiện | Loại |
|---|---|---|
| 1 | Ba bản Word (gói G2 C1a, SAP C1a, SAP BTM) cũ hơn bản `.md`: `.md` sửa ở giai đoạn 4 (commit c546fcd1) mà Word không xuất lại. Trục ④ của `kiem_chi_tiet_he_nghien_cuu` có bắt (theo mtime), nhưng không chốt nào chặn lúc commit, và chuỗi kiểm từng giai đoạn chỉ chạy `nhat_quan_xuyen_cong`. | Lệch thật — máy sửa được |
| 2 | Worktree không chứa `approval_ledger.json` (tệp ngoài git) ⇒ `kiem_chi_tiet` báo «Sổ cái: chưa ký» cho mọi cổng của C1a, kể cả G10 đã ký. Đó là đo sai chỗ, không phải trạng thái thật. Đo đúng: chép tạm sổ cái + niêm phong (chỉ đọc) vào worktree, đo, rồi gỡ bản chép. Bản gốc trên OneDrive không đổi. | Bẫy đo |
| 3 | Đo đúng chỗ: G10 C1a «đã ký thật, niêm phong hợp lệ» (PI ký 28/10), nhưng chấm sống BLOCKED ở G10-AUTO-02/03/10. G10-AUTO-10 = manifest gói đã ký không còn khớp tệp hiện hành. G4 ⑤ 🔴 «nội dung đã đổi sau khi duyệt»: chữ ký gắn SAP 1.4, SAP hiện là bản sửa đổi 1.5 chưa ký. Các sửa ở giai đoạn 1–9 (SAP, gói G2, đề cương) là SỬA ĐỔI của gói đã ký. | Đúng quy trình sửa đổi — cần người ký lại |
| 4 | BTM: G2 đủ tiền đề mà chưa chạy (`run_g2_auto.py`). | Máy làm được — chờ bác sĩ đồng ý |
| 5 | Máy chưa có trục cho thời điểm đo kết cục (chữ T của PICO-T). Soi tay G0 ↔ G1 ↔ SAP ↔ đề cương: khớp ở cả hai đề tài. | Chưa đo bằng máy |

## Cách vá

**Repo y khoa:**
- `tools/verify_exports_integrity.py` thêm luật **EXP-DOCX-STALE**, chỉ chạy ở chế độ `--staged` (pre-commit). Nếu `exports/…/X.md` đổi mà `X.docx` cùng tên đang được git theo dõi lại không đổi trong cùng commit ⇒ CHẶN, kèm lệnh xuất lại (đề cương nộp dùng `md_sang_docx_times.py`).
  - Hàm thuần `docx_chua_xuat_lai` có 4 test; 3/3 đột biến đỏ đúng ca.
  - Thử trên chỉ mục git tạm: stage riêng `.md` đề cương C1a ⇒ chặn; stage cả `.docx` ⇒ qua.
- Xuất lại ba bản Word lệch bằng `xuat_docx_chuan.py`.

**Repo gốc:** dạy `thiet-ke-nghien-cuu`, `dao-duc-dang-ky`, `dieu-phoi-nghien-cuu` hai điều:
- sửa `.md` thì xuất lại Word ngay trong cùng lượt;
- sửa tài liệu thuộc gói đã ký là sửa đổi: báo người phải ký lại, không gọi là «đã đồng bộ».

## Còn mở

| Việc | Vai |
|---|---|
| C1a: thống kê viên chọn phương pháp SAP §5 và ký SAP 1.5 ⇒ agent đồng bộ đặc tả G6 + phiên bản SAP trong đề cương ⇒ lắp lại G10 ⇒ PI ký lại gói | thống kê viên → agent → PI |
| C1a: nếu gói 28/10 ĐÃ nộp Hội đồng thì các sửa ở giai đoạn 1–9 phải trình Hội đồng như sửa đổi đề cương | PI |
| BTM: đồng ý cho chạy `run_g2_auto.py`; viết đề cương nộp; chốt thời hạn lưu trữ/huỷ; ký SAP | PI |
| Thêm trục máy cho thời điểm đo kết cục (PICO-T) | agent — khi bác sĩ đồng ý |
