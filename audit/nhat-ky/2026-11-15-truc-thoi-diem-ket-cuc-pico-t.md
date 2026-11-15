# 15/11/2026 — Trục thời điểm đo kết cục chính (PICO-T); SAP BTM lặng lẽ rơi khỏi trục kết cục chính

**Bác sĩ (nguyên văn):** «Tiếp tục vấn đê còn lại». Lần kiểm toàn hệ theo khung 12 bước để lại mục «máy chưa đo» số 1: thời điểm đo kết cục (chữ T của PICO(T)), lúc đó chỉ soi tay.

## Phát hiện

| # | Phát hiện | Loại |
|---|---|---|
| 1 | Không trục nào so thời điểm đo kết cục chính giữa G0, G1, TRDS mục 19 và SAP §2. | Thiếu phép đo |
| 2 | **SAP C1a §2 không nêu thời điểm đo kết cục chính.** Bộ sinh `run_g4_auto` có in «thời điểm: …», nhưng SAP C1a là bản sửa tay nên dòng này bị mất. Chuẩn SAP đòi nêu thời điểm đánh giá kết cục chính. | Lệch dữ liệu thật |
| 3 | `_ket_cuc_chinh_sap` chỉ khớp «**Kết cục chính:**». Từ giai đoạn 3, SAP BTM ghi «**Kết cục chính (MT1):**» (nhãn mục tiêu, MT-11), nên SAP BTM **lặng lẽ rơi khỏi** trục `ket_cuc_chinh`: chỉ còn G0/G1/G2 để so, mà không có thông báo nào. | Lỗi đo có từ trước |
| 4 | Sửa (3) thì SAP BTM được đọc lại, và trục kết cục chính BTM thành **lệch mềm**. Lý do: xác nhận của PI (dấu ea600fdb…) được ký khi máy chưa thấy SAP, nên chỉ phủ {G0, G1}. Dòng SAP là nguyên văn G1 cộng phần định nghĩa, không phải bản sao y nguyên. | Đúng luật — **không nới** luật chống đổi kết cục; PI xác nhận lại với dấu mới (be7a10ba02e38f7d) |

## Cách vá (repo y khoa)

- **Trục `thoi_diem_ket_cuc`** (`nhat_quan_xuyen_cong.truc_thoi_diem_ket_cuc`; cổng G0·G1·G2·G4·G10). Hàm `moc_thoi_gian` trích:
  - khoảng thời gian: «12 tháng», «30 ngày»;
  - mốc ngày: «01/01», «31/12», «2026».
- **Luật mức của trục:**
  - mốc mâu thuẫn ⇒ lệch mềm;
  - nơi có mốc, nơi không ⇒ cần xem;
  - không nơi nào có mốc ⇒ so độ trùng từ (dưới 0,5 ⇒ cần xem);
  - SAP §2 có kết cục chính mà thiếu thời điểm ⇒ cần xem.
- **SAP được đọc ở ba dạng:**
  - dòng «**Thời điểm đo:**» riêng;
  - «thời điểm:» nằm trong dòng kết cục chính (bản máy sinh);
  - dòng kết cục chính tự chứa mốc.
- `_ket_cuc_chinh_sap` nhận nhãn trong ngoặc: `**Kết cục chính (MT1):**`.
- **SAP C1a 1.5** (bản sửa đổi chưa ký):
  - §2 thêm dòng «**Thời điểm đo:**» chép nguyên văn G1 (nguồn: G1 `primary_outcome.timepoint`, đề cương nộp mục 4.3.1);
  - ghi thay đổi vào dòng lịch sử phiên bản 1.5;
  - xuất lại Word;
  - cập nhật `sha256_sap` trong đặc tả G6 (đặc tả chưa duyệt, neo không đổi; `chay_sap_g6 kiem`: 0 lỗi).
- **Bộ xuất Word:** thêm «ₕ» → chỉ số dưới «h» (ωₕ trong SAP C1a; Times New Roman thiếu glyph).
- **Sổ tiến độ BTM:** mục 3.1 chuyển `cho_bs` (máy đã chạy G2; chờ PI hoàn thiện), dựng lại bảng.

**Repo gốc:** dạy `thiet-ke-nghien-cuu`, `cau-hoi-nghien-cuu`, `dieu-phoi-g4`.

## Kiểm hồi quy

`tests/test_thoi_diem_ket_cuc_20261115.py`: 9 ca; **7/7 đột biến đỏ đúng ca**. Các đột biến:
- bỏ so mốc;
- bỏ ca «có/không mốc»;
- bỏ so trùng từ;
- bỏ cờ SAP thiếu thời điểm;
- SAP không đọc dòng «Thời điểm đo»;
- trả lại biểu thức cũ của kết cục chính;
- bỏ lời gọi trục trong `doi_chieu`.

## Đo sau khi vá

| Đề tài | Trục thời điểm | Trục còn lại |
|---|---|---|
| BTM | **khớp** — 4 nơi cùng mốc 12 tháng, 01/01–31/12/2026 | 20 khớp · 1 lệch mềm (kết cục chính, chờ PI xác nhận lại — B1) · 2 cần xem · 2 chưa đủ để so |
| C1a | **khớp** — sau khi thêm dòng vào SAP 1.5 | 22 khớp · 2 lệch mềm · 4 cần xem — đều chờ người |

Phiếu quyết định gom mọi việc chờ người của hai đề tài: `PHIEU-QUYET-DINH-C1A-BTM_20261115.md` (thư mục phiên).
