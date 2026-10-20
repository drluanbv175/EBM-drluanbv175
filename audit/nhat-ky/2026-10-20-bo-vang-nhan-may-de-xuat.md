# 20/10/2026 — Bộ vàng K1–K4: nhãn «?» và ghi rõ nhãn do máy soạn sẵn

**Bối cảnh.** Bác sĩ giao «Gắn nhãn 20 mục trong phiếu». Thiết kế `audit/16` (bác sĩ duyệt 25/09/2026) đặt bộ vàng là chuẩn
ĐỘC LẬP do bác sĩ gắn. Nếu Claude tự ghi nhãn thì số đo K1/K4 chỉ còn là máy so với máy, và quyết định chuyển K1/K4 sang
chặn sẽ đứng trên một chuẩn không độc lập.

**Cách làm.** Claude đọc từng mục đối chiếu tóm tắt PubMed (phần tóm tắt không có thì dựa hiểu biết về guideline, và ghi rõ
điều đó), soạn nhãn đề xuất có lý do, rồi trình bác sĩ xác nhận. Công cụ có thêm hai điểm:
- chữ `?` = chưa đủ căn cứ ⇒ để trống trục đó, không ép Đ/S (vd điều kiện chỉ kiểm được bằng toàn văn);
- `ghi --de-xuat-boi Claude` lưu nguồn gốc nhãn vào từng bản ghi. `do` cảnh báo «chuẩn CÓ máy tham gia, chưa phải bộ vàng
  bác sĩ gắn độc lập» mỗi khi có nhãn như vậy.

`main` truyền `tep=TEP_BO_VANG` lúc gọi (trước đây đối số mặc định chốt đường dẫn ngay lúc định nghĩa hàm, nên test qua dòng
lệnh có thể ghi vào tệp thật).

**Kiểm hồi quy.** Thêm 5 ca test (tổng 29). 5 phép đột biến đều đỏ: «?» thành Đ · bỏ ghi `de_xuat_boi` · đếm luôn 0 · bỏ cảnh
báo · dòng lệnh không truyền cờ. Lần đầu đột biến cuối sống sót, nên đã thêm ca test qua đúng đường dòng lệnh.
