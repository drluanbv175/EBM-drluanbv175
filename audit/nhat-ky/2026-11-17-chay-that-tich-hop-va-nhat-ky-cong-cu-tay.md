# 17/11/2026 — Chạy thật hai tích hợp app lộ lỗi bộ tách đọc ảnh; hai công cụ chạy tay nay ghi sức khoẻ API

Bác sĩ duyệt «làm mục 1 và 3» (mục 2 — trần chi tiêu tháng — bác sĩ đã tự đặt ở console).

## Mục 1 — chạy thật hai tích hợp (repo y khoa, drluanbv175/medical-ebm-automation#299)

Dữ liệu tổng hợp (hội thoại bịa, dải ECG vẽ bằng máy), 3 lượt gọi, tổng 0,137 USD.
- SOAP (Sonnet 5.5) đúng, đủ S/O/A/P.
- **Đọc ảnh (Opus 5.5) — lỗi thật có từ 23/08:** API trả đủ (`end_turn`) nhưng mô hình viết nhãn in đậm «**MÔ TẢ:**»;
  bộ tách chỉ nhận nhãn trơn ⇒ mọi mục rỗng, và bản nháp hiện «Cờ đỏ: Không thấy trên ảnh» — bản đọc HỎNG trình như
  bản đọc bình thường. Test cũ dùng chuỗi giả viết nhãn trơn nên không thấy. Đoạn GIỚI HẠN của ảnh (1 chuyển đạo, số
  đo ước lượng) đứng trước nhãn đầu cũng bị bỏ âm thầm. Bảng Streamlit còn chỉ xem khoá ở biến môi trường.
- Vá trong #299 (commit thứ hai): bộ tách nhận nhãn có trang trí markdown; «Không thấy trên ảnh» CHỈ khi mô hình tự ghi
  (vắng ⇒ «CHƯA BIẾT», tách hỏng ⇒ cảnh báo + nguyên văn); giữ đoạn giới hạn; bảng xem cả kho bí mật. Đột biến 6/6.
- **Bài học:** chốt dùng khách API giả chỉ kiểm được khuôn mà người viết test TƯỞNG mô hình trả. Mỗi tích hợp đọc câu
  trả lời tự do của mô hình phải có ít nhất một lượt chạy thật trước khi coi là xong, và mẫu kiểm phải chép KHUÔN câu
  trả lời thật.

## Mục 3 — hai công cụ chạy tay ghi sức khoẻ API (repo gốc)

- `tools/nhat_ky_api_claude.py`: bộ ghi dùng chung cho công cụ gốc (cùng khuôn với skill và cầu nối y khoa, có rào
  pytest, `EBM_NHAT_KY_API` chỉ để kiểm thử).
- `quet_lac_chu_de_kho.py`: thiếu khoá ⇒ skipped; lỗi kênh API khi gửi/theo dõi batch ⇒ error và dừng gọn mã 2 (trước
  đây văng traceback); có yêu cầu thành công ⇒ ok; mọi yêu cầu lỗi ⇒ error.
- `eval/cafes_suite.py --api`: có lượt trả về ⇒ ok; thiếu khoá ⇒ skipped; lỗi xác thực/quyền SDK hoặc mọi lượt lỗi API
  ⇒ error; thiếu SDK/tệp agent (phía máy) ⇒ không ghi.
- Giác quan nhận hai nguồn mới. 18 test; đột biến 9/9 (đột biến «main không ghi ok» lọt ở lượt đầu ⇒ thêm chốt đầu–
  cuối nhánh thành công).
