# 08/11/2026 — Tóm tắt Word ★: năm loại lỗi lặp lại làm mỗi bản tốn 2–3 lượt kiểm chéo

**Đo:** 5 bản ★ đầu của hàng chờ (PMID 41540779, 42593701, 42481270, 42642341, 42673560). Lượt kiểm chéo độc lập đầu tiên
đạt 145/145 · 140/140 · 120/125 · 155/159 (bản 1 làm trước đó); nhưng cả 5 bản đều phải sửa thêm theo ghi chú và chấm lại 1–2
lượt (~0,25 triệu token mỗi lượt). Lỗi cùng năm loại:
- MỨC LỜI: «phần lớn hoãn GC» cho «can be delayed»; GERD «không điều trị» cho «conditionally recommend against».
- THÊM «CHỈ KHI»: «Chỉ khi không đáp ứng … mới đề nghị thuốc độ tin cậy thấp» — AAN/AHS 2026 không có; câu này đặt ở mục
  điều kiện có thể khiến bác sĩ từ chối amitriptyline cho người đau xơ cơ, trái khuyến cáo 10.
- QUẦN THỂ: 4B («đang mang thai HOẶC dự định mang thai», Level A) bị gộp dưới nhãn «Thai kỳ».
- PHẠM VI «bài không nêu»: «không bàn tác hại, liều» khi bài có liều methylprednisolone và tác hại sinh thiết; «phần đợt cấp
  không phân hạng» khi KQ 3 có phân hạng.
- NƠI CHỨA DỮ LIỆU: «báo cáo phương pháp ở sổ AWMF» khi bài chỉ ghi «dữ liệu nền».

**Vá:** luật 12 trong `HUONG_DAN_DOC` (`tools/tom_tat_chung_cu_word.py`) — gói `chuan-bi` sau bản vá mang luật này; agent đọc
tránh ngay từ đầu. Không đổi cổng máy (các lỗi này là ngữ nghĩa, chỉ kiểm chéo độc lập bắt được).

**Kiểm:** `tools/test_tom_tat_huong_dan_luat_12_20261108.py`.
