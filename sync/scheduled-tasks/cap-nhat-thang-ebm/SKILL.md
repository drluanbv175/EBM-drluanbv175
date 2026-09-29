---
name: cap-nhat-thang-ebm
description: Chạy bộ cập nhật tháng monthly_update.sh (thay launchd chưa từng tự nổ) + nhịp liêm chính tháng
---

NỀN TẢNG: CHỈ CHẠY TRÊN MAC — tác vụ gọi script bash (`*.sh`). Windows: DỪNG ngay, báo «tác vụ này chỉ chạy trên Mac», không tự dịch sang lệnh khác.
THƯ MỤC LÀM VIỆC (macOS) = "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI" (repo EBM-drluanbv175). Không thấy ⇒ DỪNG và báo nguyên văn.

Chạy bộ CẬP NHẬT THÁNG của hệ EBM (thay thế launchd com.medicalebm.monthlyupdate — runs=0 từ 11/07, và cùng bệnh TCC chặn launchd đọc ~/Library/CloudStorage như job tuần).

Các bước:
1. cd medical-ebm-automation (trong THƯ MỤC LÀM VIỆC) rồi chạy: bash scripts/monthly_update.sh
2. Chạy tiếp nhịp liêm chính tháng ở thư mục gốc: cd .. && bash ops/evidence_integrity_monthly.sh (nếu file tồn tại; không có thì bỏ qua và nói rõ).
3. Đọc log tương ứng trong medical-ebm-automation/data/archive/ — báo cáo TRUNG THỰC mã thoát từng bước, KHÔNG tô hồng; bước lỗi nêu tên + mã thoát + hệ quả (watermark giữ, không nối Hub). Mã 75 kèm dòng «BỎ QUA — lượt khác đang chạy» (khoá một lượt, 29/09/2026) = một lượt khác trên máy này ĐANG chạy: báo đúng như vậy, KHÔNG chạy lại, KHÔNG gọi là lỗi.

Ràng buộc bất biến: chỉ THU THẬP/BẢO TRÌ + báo cáo — kết quả vào hàng ứng viên, KHÔNG tự áp dụng lâm sàng, không đổi decision/gradeLevel, Cổng A/B của bác sĩ nguyên vẹn. Mọi đầu ra kèm "Cần bác sĩ kiểm chứng." Trả lời bằng tiếng Việt.