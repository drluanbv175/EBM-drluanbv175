# 15/11/2026 — Đồng bộ cỡ mẫu & kỹ thuật chọn mẫu: kiểm tay thành chốt máy

**Bác sĩ (nguyên văn):**
- «Hãy kiểm tra và đánh giá sự đồng bộ Tính Cỡ Mẫu & Kỹ Thuật Chọn Mẫu một cách trung thực nhất và hoàn thiện cho tôi».
- «Với mỗi vấn đề xây dựng và hoàn thiện phải được cập nhật vào hệ thống của tôi để sau đó tất cả các vấn đề phải được thực hiện sự đồng bộ thống nhất».

## Kiểm tay (C1a, BTM)

**C1a** (đề cương nộp §4.4.1–4.4.3, SAP 1.4 đã ký, G3, G1 A2, G2, bản đăng ký, đề cương thống nhất):

- Tính lại khớp:
  - n₀ = 385;
  - DE = 1 + ((0,14² + 1)·20 − 1)·0,02 = 1,388;
  - N cần 535 → 630 (dự phòng 15%); độ nhạy CV 1,0 → 808;
  - nửa độ rộng ±3,7% / ±4,0%; ICC tối đa 0,083 / 0,062;
  - Bảng 4.1 và Bảng 4.2 (Whitehead) đúng từng ô.
- Chênh do làm tròn, đều theo chiều thận trọng: OR cận trên 1,23 (đúng ra 1,2248) và «CV tối đa ≈ 1,43» (đúng ra 1,439).
- Văn bản đã ký và hồ sơ đạo đức ghi N = 1000 thống nhất. Dòng «N tối thiểu 808, DE 1,78» trong SAP chỉ là lịch sử phiên bản 1.2; bản sửa đổi 1.4 đã chuyển sang CV 0,14.
- **Lệch thật:** `De-cuong_` (04/10) và `Bai-bao-giao-thuc_` (03/08):
  - vẫn giả định 8–20 bàn khám, dùng DE thiếu CV, báo độ chính xác «±4–6%»;
  - trong khi đề cương nộp dựa trên 50 bàn và tính ra ±3,7%;
  - hai tệp này vẫn được `kiem_chi_tiet_he_nghien_cuu` coi là tài liệu nộp.
- §4.4.3 thuật lại rằng thuyết minh đã nộp Bệnh viện ghi «chọn mẫu thuận tiện». Đề cương đã giải trình phần này.
- Bảng phân bổ nₕ/kₕ cho 20 tầng chưa tính, vì đang chờ số liệu HIS. kₕ ước khoảng 400.

**BTM:** n₀ = 385, không cộng dự phòng (có giải trình), N = 385 ở mọi văn bản. Ngẫu nhiên đơn khớp giữa G1, SAP §7 và phiếu.

## Lỗi của bộ đo cũ

- Trục chùm chấp nhận SAP chỉ cần MỘT giá trị DE khớp, nên DE cũ ghi ở chỗ khác vẫn lọt.
- K × m ≠ N chỉ được ghi chú, không thành lệch.
- Không trục nào tính lại cỡ mẫu.
- Kỹ thuật chọn mẫu chỉ được đo khi có chùm.
- Không kiểm tài liệu nộp.

## Cách vá

**Repo y khoa** (`nhat_quan_xuyen_cong.py`) — ba trục mới, gán cổng qua `TRUC_THEO_CONG`:

| Trục | Kiểm gì |
|---|---|
| `co_mau_tinh_lai` | Tính lại cỡ mẫu theo độ chính xác, so với checkpoint, «N tối thiểu» trong SAP/đề cương, và N chốt. |
| `ky_thuat_chon_mau` | Mã G1 ↔ tuyển chọn ↔ đề cương ↔ SAP. Phi xác suất ⇒ 🔴. Câu phủ định bỏ qua. Câu thuật lại ⇒ cần xem. |
| `tai_lieu_nop_co_mau` | N chốt và DE hiện hành trong mọi tài liệu nộp. Bản cũ cần dấu «BẢN CŨ — ĐÃ THAY BẰNG». |

Trục chùm sửa thêm hai điểm: mọi DE trong SAP phải thuộc tập hợp lệ; K × m ≠ N thành lệch mềm.

**Repo gốc:** dạy `co-mau-nghien-cuu`, `dieu-phoi-g3`, `thiet-ke-nghien-cuu`.

## Kiểm hồi quy

- `tests/test_co_mau_chon_mau_20261115.py`: 19 ca, 16 đột biến đều đỏ. Lần chạy đầu có một đột biến sống sót (mẫu số ≥ 1000), đã thêm ca âm.
- Đo thật trên C1a: trục kỹ thuật lúc đầu báo 🔴 vì câu thuật lại thuyết minh. Đã sửa thành «cần xem»; đây là chênh lệch thật giữa hai tài liệu nộp, đã được giải trình.

## Bài học

Một phép kiểm tay chỉ có giá trị một lần. Muốn mọi đề tài sau được đồng bộ, phải biến nó thành trục máy có test và đột biến, và dạy agent đọc trục đó trước khi báo «xong».
