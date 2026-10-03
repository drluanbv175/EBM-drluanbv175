# 02/10/2026 — Gọn CI hai repo: lượt chạy trùng, ma trận thừa, không trần thời gian (số đo từ 120–200 lượt gần nhất)

**Số đo (gh run list + gh run view, 02/10).**
- Repo gốc `kiem-tinh-da-nen`: 200 lượt/10 ngày, toàn `push`, 4 job mỗi lượt (ubuntu/windows × 3.11/3.12); trung vị 1,3 phút; một nhánh có 50 lượt. Trong 70 lượt: **3.11 và 3.12 luôn cùng kết quả (0 lệch)**;
  1 lượt đỏ CHỈ ở Windows (hai job Windows cùng đỏ), 0 lượt đỏ chỉ ở ubuntu. Hôm nay PR #87 cũng đỏ chỉ ở Windows (`os.getuid`, đường dẫn cứng). Không lane nào phủ Python 3.14 của máy Mac thật.
- Repo y khoa `offline-ci-hermetic`: 200 lượt/6 ngày, **43/71 commit chạy HAI lần** (`push` trên mọi nhánh + `pull_request`); một nhánh 81 lượt; job ubuntu TB 11 phút, windows TB 22 phút;
  tổng ≈ 2.319 phút job trong 70 lượt. Trong 70 lượt: Windows đỏ riêng một mình 4 lượt, ubuntu riêng một mình 1 lượt ⇒ Windows vẫn đáng giữ ĐỦ bộ test.
- Cả hai repo hiện CÔNG KHAI (phút Actions không tính phí). Nếu repo y khoa chuyển riêng tư: hạn mức 2.000 phút/tháng, Windows tính ×2 ⇒ cấu hình cũ vượt hạn mức trong vài ngày — gọn CI là điều kiện cần của quyết định đó.

**Đã làm (hai PR, không đổi nội dung kiểm).**
- Gốc: huỷ lượt cũ của cùng nhánh (không bao giờ huỷ master); ma trận 4 → 3 lane đại diện ba môi trường THẬT của bác sĩ — ubuntu 3.11 (sàn), windows 3.12 (máy Windows), ubuntu 3.14 (máy Mac, trước đây không ai phủ); `timeout-minutes: 15`; job `ci-ok`.
- Y khoa: `push` chỉ ở nhánh mặc định + `pull_request` (hết chạy trùng); concurrency huỷ lượt cũ của PR (không huỷ nhánh mặc định); hai job sao chép gộp thành MỘT ma trận (Windows chạy đủ bộ test như cũ); `timeout-minutes: 60`; cache pip; job `ci-ok`.
- `ci-ok` ở cả hai repo là MỘT tên kiểm tra ổn định cho «bảo vệ nhánh» (PM-02): bác sĩ bật required check một lần, đổi ma trận không phải sửa lại cài đặt.

**Kiểm.** Test bằng văn bản (không cần PyYAML) cho cả hai workflow; kiểm đột biến: gốc 10/10, y khoa 13/13 sau khi sửa hai lỗi của chính bài test (bộ test gốc không phân biệt trần thời gian của job chính với của `ci-ok`;
hai phép đầu hỏng vì cách gõ lệnh — chạy lại bằng python rồi bị bắt). Các bước CI không nằm trong pytest (`ruff check .`, `kiem_newline_vung_ky`) chạy cục bộ sạch — bài học từ PR #65 đỏ 4/4 vì quên bước này.

**Chưa làm — cần bác sĩ quyết.** (1) Bật «bảo vệ nhánh» với required check `ci-ok` ở cả hai repo (cài đặt tài khoản). (2) `giam-sat-dinh-ky` giữ nguyên (nhịp tim hằng tuần, 9 giây/lượt; nhịp THÁNG chạy đúng cùng nội dung — có thể bỏ nếu muốn gọn hơn).
(3) Chưa đụng các lớp kiểm khác ngoài GitHub (hook SessionStart 11 lệnh, pre-commit, tác vụ lịch) — chúng chồng chéo một phần với CI nhưng là lưới an toàn khác nhau; đề xuất ở báo cáo, không tự gỡ.
