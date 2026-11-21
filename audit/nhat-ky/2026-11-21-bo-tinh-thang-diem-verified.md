# 21/11/2026 — Bộ tính tất định cho 11 thang điểm verified còn thiếu + phân giai đoạn KDIGO

**Bối cảnh.** Bác sĩ gửi một bài viết về dùng AI trong y khoa (Facebook, 3/11/2026), nhấn mạnh rằng thang điểm lâm sàng phải
do AI gọi công thức lập trình sẵn, không tự nhẩm. Đo cùng ngày trên `app/clinical_scores/verified.py`: 37 thang verified
nhưng `tools/risk_score_calc.py` chỉ có 15 bộ tính, và 14 trong số đó khớp một mục verified. 23 thang còn lại để agent tự
tính. Bác sĩ: «Thực hiện tác vụ này tại đây».

**Vá (PR y khoa + PR gốc này).**
- Bộ tính mới cho FIB-4, APRI, khoảng trống anion (kèm hiệu chỉnh albumin), HOMA-IR, Maddrey, PHQ-9 (mục 9 dương ⇒ cảnh báo
  dù tổng thấp), GAD-7, AUDIT-C, FRAIL, TIMI (UA/NSTEMI), GOLD ABE (không tự chọn khi mMRC và CAT lệch nhau) và `kdigo-stage`
  (phân giai đoạn G/A từ eGFR đã có — không tính eGFR).
- Công thức và ngưỡng chép từ chính mục verified (PMID/DOI của mục). Không có ngưỡng phổ quát thì không phán (HOMA-IR,
  khoảng trống anion).
- Không làm, và ghi lý do vào bảng `KHONG_CO_BO_TINH`:
  - chính sổ dặn dùng công cụ chính thức, không nhập hệ số tay: CKD-EPI, MELD-Na, SCORE2/ASCVD;
  - sổ chưa ghi bảng điểm: NEWS2, Glasgow-Blatchford, FINDRISC, ô màu KDIGO;
  - phân loại lâm sàng hoặc bộ tiêu chí: NYHA, Beers, STOPP/START.
- Bảng `BO_TINH_THEO_SCORE_ID` + `KHONG_CO_BO_TINH` phải phủ ĐÚNG mọi thang verified (test chốt). Thêm thang verified mới
  mà không khai ⇒ test đỏ — không để agent lặng lẽ tự nhẩm.
- Agent `thang-diem-nguy-co` (gốc + bản sao y khoa, manifest sinh lại) học luật: thang có bộ tính thì BẮT BUỘC gọi; thang
  chưa có thì ghi «tính tay — cần bác sĩ kiểm» hoặc `[CẦN CÔNG CỤ CHÍNH THỐNG]`.
- CLAUDE.md §4: «15 thang có công cụ tính» → 25 (số thang verified có bộ tính).

**Kiểm.**
- `tests/test_risk_score_calc_verified_20261121.py`: 52 test. Gồm ca biên mọi ngưỡng; ràng buộc sổ ↔ mã (hằng số của mã
  phải còn trong chữ của sổ); bao phủ; mọi lệnh CLI chạy được.
- 7 đột biến đều đỏ rồi xanh lại: HOMA 22,5→22 · Maddrey ≥32→>32 · PHQ-9 mục 9→8 · FIB-4 >65→≥65 · KDIGO A2 ≤300→<300 ·
  bỏ khai một thang khỏi bảng bao phủ · AUDIT-C nam 4→3.
- Bộ liên quan y khoa: 246 đạt. Bộ `tools` gốc: 5441 đạt.
