---
name: thu-thap-tuan-an-toan-thuoc
description: Chạy bộ thu thập giám sát tuần weekly_safety.sh — 18:00 thứ Hai (bác sĩ đổi 17/08, giờ máy thường thức; trước là 06:30 T7 đã lỡ kỳ đầu)
---

NỀN TẢNG: CHỈ CHẠY TRÊN MAC — tác vụ gọi script bash (`*.sh`). Windows: DỪNG ngay, báo «tác vụ này chỉ chạy trên Mac», không tự dịch sang lệnh khác.
THƯ MỤC LÀM VIỆC (macOS) = "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI" (repo EBM-drluanbv175). Không thấy ⇒ DỪNG và báo nguyên văn.

Chạy bộ THU THẬP giám sát chứng cứ tuần của hệ EBM (thay thế launchd com.medicalebm.weeklysafety — job đó chết EX_CONFIG vì TCC chặn launchd đọc ~/Library/CloudStorage; tác vụ này chạy trong ngữ cảnh Claude có quyền đọc OneDrive).

Các bước:
1. cd medical-ebm-automation (trong THƯ MỤC LÀM VIỆC) rồi chạy: bash scripts/weekly_safety.sh
2. Đọc đuôi data/archive/launchd_weekly.log — báo cáo TRUNG THỰC mã thoát từng bước (1)-(6) và verdict PASS/CÓ BƯỚC LỖI. KHÔNG tô hồng: bước lỗi phải nêu tên + mã thoát. Script thoát mã 75 kèm dòng «BỎ QUA — lượt khác đang chạy» (khoá một lượt, 29/09/2026) nghĩa là một lượt khác trên máy này ĐANG chạy: báo đúng như vậy, KHÔNG chạy lại, KHÔNG gọi là lỗi; kết quả là của lượt đang chạy.
3. Nếu status PASS: nói ngắn gọn số ứng viên mới (nếu log có). Nếu PARTIAL/FAIL: liệt kê bước hỏng và nhắc rằng watermark giữ nguyên, không có gì được nối vào Hub (fail-closed đúng thiết kế).

Ràng buộc bất biến: đây chỉ là THU THẬP + báo cáo — kết quả vào hàng ứng viên, KHÔNG tự áp dụng lâm sàng, không đổi decision/gradeLevel, Cổng A/B của bác sĩ nguyên vẹn. Mọi đầu ra kèm "Cần bác sĩ kiểm chứng." Trả lời bằng tiếng Việt.