---
name: giam-sat-acc-aha-quy
description: Quét quý trang ACC/AHA guidelines qua Browser (urllib bị Cloudflare chặn), nạp qua giam_sat_to_chuc.py --nap-van-ban SRC-015
---

Bạn đang chạy một vòng quét giám sát guideline theo QUÝ cho trạm SRC-015 (ACC/AHA) của hệ EBM Copilot,
thư mục gốc: "/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI".

BỐI CẢNH (đọc để hiểu tại sao việc này cần Browser, không phải script thường): trang
https://professional.heart.org/en/guidelines-and-statements bị Cloudflare bot-challenge chặn MỌI
request urllib/script thường (403, cookie __cf_bm) — kể cả đổi User-Agent giả trình duyệt. Chỉ một
phiên Browser THẬT (thực thi JS) mới tải được nội dung. Đây là lý do trạm này KHÔNG nằm trong vòng quét
tự động thường (`python3 tools/giam_sat_to_chuc.py` không tham số) mà cần một phiên agent có Browser.

CÁC BƯỚC:
1. Dùng Browser tool điều hướng tới: https://professional.heart.org/en/guidelines-and-statements
2. Lấy nội dung trang bằng get_page_text (văn bản thuần, không cần HTML thô).
3. Ghi nội dung đó vào MỘT file tạm (vd /tmp/acc-aha-<ngày>.txt).
4. Chạy: cd "/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI" && python3 tools/giam_sat_to_chuc.py --nap-van-ban SRC-015 <đường-dẫn-file-tạm>
5. Đọc output của lệnh trên — nếu có "🟠 N tiêu đề mới", báo cáo NGẮN GỌN các tiêu đề mới đó bằng
   tiếng Việt (kèm nhắc "Cần bác sĩ kiểm chứng — đối chiếu trang gốc trước khi coi là đã cập nhật
   thực hành"). Nếu "◌ ... 0 tiêu đề MỚI", chỉ cần báo một dòng ngắn xác nhận đã quét, không có gì mới.
   Nếu lệnh báo lỗi (mã thoát 2, "quá ngắn"/"sổ nguồn hỏng"), báo rõ lỗi đó — KHÔNG tự suy diễn nguyên
   nhân, chỉ trích nguyên văn thông báo lỗi.
6. Xoá file tạm đã tạo ở bước 3 sau khi dùng xong.

RÀNG BUỘC BẤT BIẾN: đây CHỈ là bước GIÁM SÁT/PHÁT HIỆN — kết quả vào hàng ứng viên
(EBM-Dashboards/surveillance/), KHÔNG tự áp dụng lâm sàng, không đổi decision/gradeLevel của bất kỳ
dashboard nào, không tự sửa data/sources.json ngoài những gì lệnh --nap-van-ban tự ghi. Không dùng
PII. Trả lời bằng tiếng Việt.