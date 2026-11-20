# 20/11/2026 — Đo lại chi tiết cỡ mẫu, chọn mẫu, biến số của hai đề tài thật; bộ chấm G2–G5 có --no-write

**Yêu cầu bác sĩ:** «Hãy đo một cách chi tiết và hoàn thành một cách chi tiết giúp tôi. Vấn đề đề cương nghiên cứu đã được
hoàn chỉnh, hãy kiểm tra hoàn thiện vấn đề cỡ mẫu, mẫu, biến.»

**Đo:** cổng G3 (PASS_G3_CONFIRMED cả hai), nhất quán xuyên cổng (C1a 28/28, BTM 26/27 — trục còn lại là dấu duyệt đặc tả G6
chờ PI đóng lại), đối chiếu biến (0 LỆCH; 2 mục cần xem đã giải thích), biến phái sinh (BTM 42 đã duyệt; C1a 12 đã duyệt +
1 biến tầng do bộ máy G6), ma trận mục tiêu–biến ĐẠT, sai lệch ↔ SAP ĐẠT; tính lại độc lập 56 con số cỡ mẫu: 52 khớp.

**Lệch và quyết định của chủ nhiệm (20/11/2026):** C1a tự đánh giá sức khỏe vào mô hình dạng số; Khoa C1a chỉ khám thứ
Hai–Sáu (20 tầng, mô hình 19 tham số thay «khoảng 24»); OR nhỏ nhất CV 1,0 sửa 1,22 ở đề cương, chờ SAP sửa đổi ký; ICC
0,062 → 0,063. BTM thêm nhánh «EPV vẫn dưới 10 sau bước (3) ⇒ giữ mô hình 12 tham số» vào SAP (nháp 7) và đề cương.

**Sự cố của chính phiên:** chạy `g3_quality_gate.py` không `--no-write` trên checkout chính ⇒ ghi lại đường dẫn trong
G3_checkpoint C1a ⇒ G10-AUTO-03 chặn. Khôi phục đúng dòng bằng git (git rescue của pipeline_freshness gỡ cảnh báo), G10 về
READY. Vá hệ thống: `--no-write` cho g2–g5 (repo y khoa); dạy `co-mau-nghien-cuu`.
