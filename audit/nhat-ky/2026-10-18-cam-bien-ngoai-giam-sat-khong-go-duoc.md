# 18/10/2026 — Cảm biến «điểm-khám NGOÀI giám sát» không bao giờ gỡ được

**Triệu chứng.** Việc 🤖 «3 lượt điểm-khám NGOÀI giám sát — rà ứng viên mở watchlist» (`tools/tu_de_xuat_viec.py`, giác quan ⑦)
và chỉ số E-NGOAI = 3 trên Đài hoàn thiện không giảm, dù máy đã rà.

**Nguyên nhân.** `state/nhat-ky-tac-dong.jsonl` là sổ chỉ nối thêm (do `tra_diem_kham.py` ghi). Giác quan ⑦ đếm MỌI dòng `miss`
từ trước tới nay, không có chỗ ghi «đã rà» ⇒ chạm ngưỡng 3 rồi thì việc treo vĩnh viễn — đúng kiểu cảnh báo bác sĩ học cách bỏ qua.

**Đo khi rà (18/10/2026, `tra_chi_tiet` — không ghi nhật ký):** cả 3 lượt vẫn ra «không có».
- 20/08 — VKDT kém đáp ứng MTX, chọn bDMARD hay JAKi: hub CÓ thẻ đã xác minh (vd EVID-2026-0664, EVID-2026-0349 — leo thang
  bDMARD/JAKi khi MTX thất bại) nhưng bộ khớp ưu tiên độ chính xác không trúng ⇒ không phải khoảng trống giám sát; theo dõi ở
  `da_biet_chua_dat` của bộ vàng.
- 11/10 — đánh giá lão khoa toàn diện: dashboard `NguoiCaoTuoi_DaBenhLy_NgoaiTru_20261016` có ITEM-23 (CGA) nhưng CHƯA nạp hub.
- 13/10 — COPD nguy cơ tim phổi đa chuyên khoa: dashboard `COPD_NguyCoTimPhoi_DaChuyenKhoa_20261013` (27 mục) CHƯA nạp hub.
- Toàn kho: 7/74 dashboard chưa nạp hub (nạp hub là bước bác sĩ yêu cầu, không tự chạy `sync_all.py`).

**Cách vá.** Sổ rà `state/ngoai-giam-sat-da-ra.json` (ngoài git; khoá = `luc` của dòng miss; `cho_nguoi` = việc còn chờ bác sĩ).
`dem_ngoai_giam_sat()` trừ lượt đã rà khỏi việc 🤖; việc chờ bác sĩ hiện thành dòng 👤 riêng và Đài VẪN cộng nó vào E-NGOAI
(không đọc thành «đạt» khi câu hỏi vẫn chưa trả lời được). Sổ vắng/hỏng ⇒ coi như rỗng ⇒ mọi miss vẫn được đếm.

**Kiểm hồi quy.** `tools/test_ngoai_giam_sat_da_ra_20261018.py` (5 test); kiểm đột biến 2/2 (bỏ điều kiện trừ lượt đã rà; bỏ
phần Đài cộng dòng 👤) ⇒ đỏ đúng chỗ, phục hồi xanh. Biểu thức khoá `r.get("miss") and r.get("loai") != "khop_yeu"` giữ nguyên
ở dòng thi hành (test cũ của `tra_diem_kham` khớp chuỗi này).
