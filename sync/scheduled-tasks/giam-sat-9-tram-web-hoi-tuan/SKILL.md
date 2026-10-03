---
name: giam-sat-9-tram-web-hoi-tuan
description: Quét tuần 9 trạm html-watch/rss không cần Browser (đo sống 23/09: chạy tốt bằng script thường) qua giam_sat_to_chuc.py — biết "trang đổi" sớm hơn PubMed hàng tuần-tháng; KHÁC giam-sat-acc-aha-quy (10/10 trạm, chỉ SRC-015 cần Browser vì Cloudflare)
---

NỀN TẢNG: macOS + Windows. THƯ MỤC LÀM VIỆC = gốc thư mục OneDrive «Claude AI» của MÁY ĐANG CHẠY (repo EBM-drluanbv175):
- macOS: "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI"
- Windows: "%USERPROFILE%\OneDrive\Claude AI" (máy hiện tại: C:\Users\Admin\OneDrive\Claude AI)
Không thấy thư mục đúng ⇒ DỪNG và báo nguyên văn; không đoán đường dẫn khác.
Trên Windows đổi lệnh: `python3` → `py -3`; `~/.ebm-venv/bin/python` → `%USERPROFILE%\.ebm-venv\Scripts\python.exe`.
Đường dẫn tương đối viết bằng `/` dùng được nguyên trên cả hai; tệp tạm ghi vào `state/` của thư mục làm việc, không dùng `/tmp`.

Bạn đang chạy một vòng quét giám sát TUẦN cho 9 trạm "web hội" (dò thay đổi trang, khác
Cloudflare-protected ACC/AHA) của hệ EBM Copilot, thư mục gốc: THƯ MỤC LÀM VIỆC ở trên.

BỐI CẢNH (để hiểu việc này làm gì, không cần đọc thêm): 9 trạm GOLD·GINA·KDIGO·ADA·ESC·
IDSA·USPSTF·WHO·BYT (SRC-010,011,012,013,014,017,019,020,022 trong data/sources.json) đã
`active`, đo sống 23/09/2026 xác nhận chạy tốt qua script thường (KHÔNG cần Browser, khác
SRC-015 ACC/AHA bị Cloudflare chặn — trạm đó có tác vụ lịch RIÊNG `giam-sat-acc-aha-quy`,
đừng đụng vào). Bản nguồn trong git thêm 02/10/2026 (F4 kiểm toàn diện: trước đó tác vụ chỉ có bản runtime,
app dọn runtime là mất trắng). Mỗi lượt để lại `EBM-Dashboards/surveillance/to-chuc-<YYYY-MM-DD>.md` —
`tools/kiem_lich_nen.py` canh theo đúng tệp đó (sổ khai `sync/lich-nen-ky-vong.json`).

CÁC BƯỚC:
1. Chạy: cd <THƯ MỤC LÀM VIỆC> && python3 tools/giam_sat_to_chuc.py
2. Đọc output. Công cụ TỰ ghi ứng viên phát hiện được vào hàng chờ (không cần bạn ghi gì
   thêm) và tự đánh dấu `degraded` cho trạm fetch hỏng lần quét này.
3. Nếu output có dòng "🟠 N tiêu đề mới", báo cáo NGẮN GỌN các tiêu đề đó bằng tiếng Việt
   theo tổ chức, kèm nhắc "Cần bác sĩ kiểm chứng — đối chiếu trang gốc trước khi coi là đã
   cập nhật thực hành". Nếu có dòng "✗ <id> ... fetch hỏng", liệt kê rõ trạm nào hỏng (có
   thể là mạng tạm thời hoặc trang đổi cấu trúc — KHÔNG tự suy diễn nguyên nhân, chỉ trích
   nguyên văn). Nếu không có gì mới và không trạm nào hỏng, chỉ cần một dòng xác nhận đã
   quét sạch.
4. KHÔNG chạy thêm lệnh nào khác, không tự sửa data/sources.json ngoài những gì chính lệnh
   ở bước 1 tự ghi.

RÀNG BUỘC BẤT BIẾN: đây CHỈ là bước GIÁM SÁT/PHÁT HIỆN — kết quả vào hàng ứng viên
(EBM-Dashboards/surveillance/), KHÔNG tự áp dụng lâm sàng, không đổi decision/gradeLevel
của bất kỳ dashboard nào. Không dùng PII. Trả lời bằng tiếng Việt.
