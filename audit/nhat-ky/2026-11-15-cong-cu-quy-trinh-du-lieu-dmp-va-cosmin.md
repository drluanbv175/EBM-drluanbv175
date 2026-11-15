# 15/11/2026 — Công cụ & phương pháp thu thập: DMP không mang quy trình đã hứa, khối COSMIN còn ô trống (giai đoạn 5)

**Bác sĩ (nguyên văn):** «Tiếp tục giai đoạn tiếp theo» — trong chương trình «Hãy đảm bảo sự đồng bộ xuyên suốt và chính xác nhất».

## Phát hiện (kiểm tay C1a, BTM)

Các trục cũ đều khớp: phiếu ↔ từ điển nhập liệu (C1a 22 câu chọn đáp án; BTM 73 trường), từ điển REDCap G5 ↔ bộ biến G3 (C1a 71/71, không lệch thuộc tính), luật kiểm dữ liệu và mã thiếu đều trỏ đúng biến có thật. Chỗ hở nằm ở những phần chưa trục nào đo:

| Chỗ hở | Đề tài | Chi tiết |
|---|---|---|
| DMP G5 không mang quy trình đã chốt | C1a | Đề cương nộp và phiếu thông tin G2 khớp nhau ở: lưu 2 năm rồi hủy; bảng đối chiếu HIS hủy trong 30 ngày. Đề cương còn có: nhập kép toàn bộ phiếu; mở hòm phiếu bằng tổ hai người; hai người ngoài khoa mã hoá câu hỏi mở độc lập; hủy phiếu bằng máy hủy tài liệu, có biên bản. DMP G5 (tài liệu VẬN HÀNH lúc thu thập và khoá dữ liệu) không có điều nào, chỉ có câu khuôn «không dùng một thời hạn cứng cho mọi đề tài». |
| Quy trình chưa có dạng máy đọc | BTM | SOP trích hồ sơ đã có trích lại 10%, ngưỡng đồng thuận `xn_du` ≥ 95%, kappa cho biến chính; bảng nối mã mã hoá, hủy sau khi khoá dữ liệu. Thời hạn lưu trữ và cách hủy CHƯA được chốt. |
| Khối COSMIN của A2 toàn ô trống chung | C1a | Ghi «[CẦN hội đồng chuyên gia + hệ số CVI]», «☐ EFA ☐ CFA [CẦN]»… trong khi đề cương 4.5.1/4.5.3 đã có CVI, phỏng vấn nhận thức, EFA/CFA, Cronbach, sàn–trần, và ghi rõ test–retest/SEM/MCID ngoài phạm vi. |

## Cách vá

**Repo y khoa:**
- **Công cụ mới `tools/quy_trinh_du_lieu.py`** (QT-01…QT-07) với bảng `_quy-trinh-du-lieu.csv`:
  - mỗi quyết định ghi kèm nguồn và cụm neo nguyên văn ở đề cương/G2;
  - DMP phải mang nguyên quyết định;
  - số năm lưu trữ hoặc số ngày hủy bảng nối khác nhau giữa các tài liệu ⇒ MÂU THUẪN.
- **`run_g5_auto`:** in «PHẦN 1B — quy trình thu thập, nhập liệu và lưu trữ (đã chốt)» và dòng «Lưu trữ/hủy» từ bảng; câu khuôn chỉ còn khi đề tài chưa chốt.
- **`run_g1_auto._bang_cosmin`:** khối COSMIN là bảng truy nguyên. Mỗi đặc tính ghi một trong bốn: đã có ở mục nào của đề cương (+ SAP §k); ngoài phạm vi (đề cương ghi rõ); không áp dụng (công cụ tự xây dựng); hoặc [CẦN] khi đề cương chưa nói tới. Ưu tiên mục công cụ của đề cương; mục tổng quan tài liệu như «3.2 Công cụ đo lường…» không được trích.
- **Hai trục mới của `nhat_quan_xuyen_cong`:**
  - `quy_trinh_du_lieu` (G1·G2·G5·G10)
  - `cong_cu_do_luong` (G1·G3·G10)
- **Dữ liệu:**
  - bảng quy trình C1a (9 quyết định) và BTM (7 quyết định, 2 chờ PI);
  - DMP C1a chèn khối do chính hàm của bộ sinh tạo (không chạy lại G5, vì chưa có dữ liệu), sinh lại docx; trạng thái G5 không đổi;
  - dựng lại G1 C1a: A2 mang bảng COSMIN mới; vẫn PASS_G1_CONFIRMED.

**Repo gốc:** dạy `quan-ly-du-lieu`, `cong-cu-do-luong`, `dieu-phoi-g5`, `dieu-phoi-g1`, `dao-duc-dang-ky`.

## Kiểm hồi quy

- `tests/test_cong_cu_20261115.py`: 11 ca; 12/12 đột biến đỏ đúng ca.
- Chạy trên dữ liệu thật:
  - C1a trước khi vá DMP: 9 lỗi QT-06 (đề cương và G2 khớp, chỉ DMP thiếu). Sau vá: 0 lỗi, 0 mâu thuẫn; `cong_cu_do_luong` khớp (11/11 đặc tính truy nguyên được).
  - BTM: chỉ còn 2 mục chờ PI.

## Còn mở (việc của người)

| Đề tài | Việc | Vai |
|---|---|---|
| BTM | Chốt thời hạn lưu trữ dữ liệu sau khi kết thúc nghiên cứu và cách hủy tệp (bảng `_quy-trinh-du-lieu.csv` đang ghi «[CẦN PI QUYẾT]») | PI |
| C1a | Hội đồng chuyên gia quyết đề xuất tách câu C6/C9 (`pha_cong_cu/DE_XUAT_TACH_C6_C9.md`) ở pha phát triển công cụ, sau phê duyệt đạo đức | hội đồng chuyên gia, PI |
