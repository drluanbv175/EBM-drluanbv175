# 18/11/2026 — Chạy thật hội đồng G3 BTM và kiểm máy trên đề cương hiện hành; trần chi phí bỏ qua kho bí mật

## Bối cảnh

Bác sĩ duyệt bốn việc:
- ghi biên bản G3-T1 và G3-T3;
- khởi tạo lại hội đồng G3 (một lượt tính phí mới) và «hoàn thiện»;
- chạy lại A12 và phản biện máy trên đề cương hiện hành;
- giữ trần chi phí, kèm câu «đối với trần tôi đã cài đặt».

## Đã làm và số đo

- **Biên bản G3-T1, G3-T3:** đã ghi (G3-DG-20261118T063222-77beba3f, -9683627c).
- **Hội đồng G3 khởi tạo lại** (chỉ còn G3-T2 và DP-G3-1/2; phần đã có biên bản tự được bỏ qua): ba batch nối tiếp
  chấm → phản biện → trọng tài. Ước 0,47 USD; thật 0,46 + 0,23 + 0,23 USD. Batch dùng được prompt caching: ghi 47.899
  token và đọc 13.671 token ở batch đầu. Đã ghi 3 biên bản.
  - G3-T2: cả hai người chấm kết luận «đạt có lưu ý».
  - DP-G3-1 (cỡ mẫu): «sửa kết luận». Giữ N = 385, nhưng sửa hai chỗ văn bản:
    - đề cương 4.4.2 nói có hiệu chỉnh quần thể hữu hạn, lệch với 4.4.1, 4.9 và Phụ lục A;
    - bộ biến ghi «khoảng 15 tham số», thiếu HbA1c 3 mức. Đúng là 16 tham số, EPV 6,0/12,0.
  - DP-G3-2 (bộ biến): «chuyển bác sĩ». Biến nguồn cho ĐN4; cơ chế khử định danh trường ngày.
- **A12 + phản biện máy chạy lại** (≈ 0,26 USD): báo cáo nay mang mã băm đề cương, được báo «còn hiệu lực». A12 có 8
  cặp cần xem trên 50; phản biện máy có 23 phát hiện (5 cao, 12 vừa, 6 thấp). Phiếu duyệt 31 mục đã gửi bác sĩ.
  Prompt caching của A12 chạy đúng: lô đầu ghi 711 token, ba lô sau mỗi lô đọc 711 token.
- **Sổ chi phí tháng 11:** ≈ 1,8 USD trên trần 20 USD.
- **PR dữ liệu y khoa:** sửa bộ biến G3 (16 tham số, ĐN4 chưa có biến nguồn, B10 chờ chủ nhiệm).

## Lỗi hệ lộ ra

1. **Trần chi phí bỏ qua kho bí mật.** Bản đầu của `tran_usd_thang` chỉ đọc biến môi trường. Theo §5, cấu hình nằm ở
   `~/.ebm-secrets/medical-ebm-automation.env`, nên trần đặt ở đó bị bỏ qua và lặng lẽ dùng mặc định. Đã vá cùng ngày:
   thứ tự biến môi trường → kho bí mật → mặc định, và thông điệp chặn nêu nơi đặt. Đo sau khi vá: không thấy trần ở biến
   môi trường, kho bí mật, settings Claude Code hay `.zshrc`/`.zprofile` ⇒ trần hiệu lực là 20 USD mặc định. Đã báo
   bác sĩ.
2. **Hội đồng chuyển bác sĩ một việc đã quyết từ trước.** Cơ chế khử định danh trường ngày đã được quyết ở B8 ngày
   28/10/2026 («Áp dụng B1–B9»: đổi thành «ngày thứ trong năm» trước khi chia sẻ tệp). Trọng tài vẫn xếp việc này vào
   «chuyển bác sĩ». Điều phối phải đối chiếu mục «Điểm cần chủ nhiệm quyết» trước khi trình, không trình lại quyết
   định đã có.

## Bài học

- **Cấu hình của bác sĩ phải được đọc ở mọi nơi §5 cho phép.** Đọc thiếu một nơi thì «đã cài đặt» thành vô hiệu mà
  không báo gì.
- **Phần «chuyển bác sĩ» của hội đồng máy phải đối chiếu sổ quyết định trước khi trình.**
