# 19/11/2026 — Tra điểm khám: luật «từ ghép bắt buộc kề nhau» mong manh khi kho lớn; bộ vàng 80/80 → 73/80

**Phát hiện:** kiểm toàn diện hệ chứng cứ, `pytest tools/` trên máy thật.
- `BoVangTrenSoThat` ĐỎ, 73/80 trên sổ cái 3.248 thẻ. CI bỏ qua vì thiếu `EBM_MASTER`, nên hồi quy không tự lộ.

**Phân loại 7 câu hỏng** (chi tiết: `quality/eval/tra-diem-kham/DE-XUAT-SUA-BO-VANG_20261119.md`):
- **1 hồi quy thuật toán:** «chống đông rung nhĩ DOAC».
  - Luật cũ coi cặp là «từ ghép» nếu từng kề nhau ở ≥1 tiêu đề.
  - Một tiêu đề mới «CHỈ ĐỊNH KHÁNG ĐÔNG: rung nhĩ…» biến cặp vắt ranh giới cụm «đông | rung» (2/42 tiêu đề có cả hai vế) thành từ ghép giả ⇒ thẻ «Kháng đông đường uống cho rung nhĩ (DOAC ưu tiên)» bị loại.
  - Chính ghi chú bộ vàng 22/09 đã viết «cặp ngang ranh giới cụm không bị đòi kề» — giả định này hỏng khi kho lớn.
- 1 do nội dung kho đổi (JAK).
- 3 nhãn bộ vàng lỗi thời: kho nay đã phủ dengue, thoát vị đĩa đệm, kháng sinh dự phòng.
- 1 luật cấm quá thô («tăng cân»).
- 1 lỗi chính xác thật («viêm da» → «viêm đa dây»).

**Cách vá** (`tra_diem_kham._la_tu_ghep`):
- Cặp là từ ghép khi kề nhau ≥50% số tiêu đề có cả hai vế, HOẶC ≥3 tiêu đề với tỉ lệ ≥10%.
- Từ ghép thật có thành phần phổ biến vẫn giữ: «chống đông» 23/87, «tăng huyết» 24/74, «tăng cân» 11/69, «lợi tiểu» 8/18.
- Cặp a = b («đau đầu») giữ luật cũ.

**Kiểm:**
- Bộ vàng trên sổ thật: hết lỗi DOAC, KHÔNG thêm lỗi nào (8 → 7; còn lại chờ bác sĩ duyệt nhãn).
- 67 test tra điểm khám đạt.
- Đột biến 3/3 đỏ: luật cũ; bỏ nhánh ≥3 tiêu đề; bỏ sàn tỉ lệ.

**Bài học:** heuristic dựa trên «từng xuất hiện ≥1 lần» trong kho tăng trưởng sẽ trôi theo kích thước kho. Đo bằng tỉ lệ có ngưỡng; và chạy bộ vàng trên sổ thật định kỳ, vì CI không thấy.
