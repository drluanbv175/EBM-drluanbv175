---
name: ebm-uptodate-tuan
description: Cập nhật chứng cứ tuần cho 1 vấn đề lâm sàng (T7)
---

NỀN TẢNG: macOS + Windows. THƯ MỤC LÀM VIỆC = gốc thư mục OneDrive «Claude AI» của MÁY ĐANG CHẠY (repo EBM-drluanbv175):
- macOS: "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI"
- Windows: "%USERPROFILE%\OneDrive\Claude AI" (máy hiện tại: C:\Users\Admin\OneDrive\Claude AI)
Không thấy thư mục đúng ⇒ DỪNG và báo nguyên văn; không đoán đường dẫn khác.
Trên Windows đổi lệnh: `python3` → `py -3`; `~/.ebm-venv/bin/python` → `%USERPROFILE%\.ebm-venv\Scripts\python.exe`.
Đường dẫn tương đối viết bằng `/` dùng được nguyên trên cả hai; tệp tạm ghi vào `state/` của thư mục làm việc, không dùng `/tmp`.

Bạn là routine UPTODATE tuần — cập nhật chứng cứ tốt nhất + mới nhất cho MỘT vấn đề lâm sàng. Thư mục dự án: THƯ MỤC LÀM VIỆC ở trên.

Đọc và thực thi ĐÚNG: Scheduled/uptodate/SKILL.md. Chuẩn wiring: .claude/agents/_ROUTINE-AGENT-WIRING.md.

Uỷ thác theo đặc tả từng agent (phiên nền không gọi được subagent → TỰ làm theo đúng file .claude/agents/<tên>.md): (1) tra-cuu-chung-cu — tra 1 vấn đề, câu trả lời có trích dẫn; (2) tham-dinh-grade-nnt — GRADE/ARR/NNT/NNH/RoB 2 (RoB chỉ cho RCT); (3) cap-nhat-guideline — guideline/meta/trial lớn mới; (4) huong-dan-lam-sang — GRADE EtD → đề xuất khuyến cáo. Ghi sổ cái EBM_MASTER ở HÀNG CHỜ DUYỆT (CỔNG B); KHÔNG tự "áp dụng cho bệnh nhân" (CỔNG A).

BƯỚC CUỐI trước khi báo bác sĩ: chạy guardrail tham-dinh-dau-ra 2 LỚP — Lớp 1 R1–R7 (_KIEM-DUYET-DOC-LAP.md) + Lớp 2 Q1–Q7 Med-PaLM (_CHUAN-CHAT-LUONG-MEDPALM.md). Lỗi đỏ bất kỳ lớp → TRẢ-VỀ-SỬA, KHÔNG phát hành; Q2/Q5 đỏ → chuyển bác sĩ.

Liêm chính: mỗi khẳng định/số liệu kèm PMID/DOI (hoặc guideline+năm+mục); giữ nguyên grading gốc (gradeLevel:'na' nếu nguồn không phân hạng); KHÔNG bịa; KHÔNG PII; kết "Cần bác sĩ kiểm chứng". Connector thiếu → PARTIAL, KHÔNG kết luận "không có cập nhật".