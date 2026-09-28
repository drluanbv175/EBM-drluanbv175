---
name: kiem-rut-bai-kho-thang
description: Tái kiểm rút bài HẰNG THÁNG cho mọi PMID/DOI/URL chứng cứ đã có trong kho (dashboard + bản ghi mồ côi) qua chu_trinh_chung_cu.py — chỉ đo và báo, không sửa nội dung
---

NỀN TẢNG: macOS + Windows. THƯ MỤC LÀM VIỆC = gốc thư mục OneDrive «Claude AI» của MÁY ĐANG CHẠY (repo EBM-drluanbv175):
- macOS: "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI"
- Windows: "%USERPROFILE%\OneDrive\Claude AI" (máy hiện tại: C:\Users\Admin\OneDrive\Claude AI)
Không thấy thư mục đúng ⇒ DỪNG và báo nguyên văn; không đoán đường dẫn khác.
Trên Windows đổi lệnh: `python3` → `py -3`; `~/.ebm-venv/bin/python` → `%USERPROFILE%\.ebm-venv\Scripts\python.exe`.
Đường dẫn tương đối viết bằng `/` dùng được nguyên trên cả hai; tệp tạm ghi vào `state/` của thư mục làm việc, không dùng `/tmp`.

Bạn đang chạy vòng TÁI KIỂM RÚT BÀI hằng tháng cho KHO CHỨNG CỨ của hệ EBM Copilot.

BỐI CẢNH (vì sao việc này phải chạy định kỳ): sổ xác minh nguồn chỉ coi trạng thái rút bài còn hiệu lực 30 ngày.
Trước 28/09/2026 không tác vụ lịch nào tái kiểm kho — một bài đã trích có thể bị rút sau khi dashboard phát hành mà
không ai biết (tác vụ `kiem-thang-diem-quy` chỉ phủ 32 thang điểm, không phủ dashboard). Tác vụ này là owner DUY NHẤT
của việc tái kiểm định kỳ đó; không nối trùng qua tools/tu_khoi_dong.py.

CÁC BƯỚC:
1. `python3 tools/sync_safety_check.py` (Windows: `py -3 tools\sync_safety_check.py`). 🔴 ⇒ DỪNG, báo nguyên văn.
2. Chạy (Windows thay `python3` bằng `py -3`):
   `python3 tools/chu_trinh_chung_cu.py --vong 3 --ghi-log state/kiem-rut-bai-kho.log`
   Lệnh tự chạy ① nguồn thật → ② độ tươi → ③ xác minh (gồm bản ghi mồ côi) → ④ rút bài → ⑤ mâu thuẫn → ⑥ dây
   chuyền, và nối một dòng «KẾT THÚC (mã N)» vào state/kiem-rut-bai-kho.log để tools/kiem_lich_nen.py canh được kỳ này.
3. Đọc mã thoát:
   - 0: báo MỘT dòng — kho sạch (không thấy nguồn bị rút), kèm câu phạm vi «chỉ là toàn vẹn kỹ thuật».
   - 1: liệt kê NGẮN từng việc chu trình in ra; mục 🔴 rút bài: nêu dashboard, định danh, trạng thái — kèm câu «Cần
     bác sĩ xem; với thông báo rút là bản đính chính bị rút, dựng mẫu bằng `python3 tools/mau_ky_rut_bai.py` — CHỈ bác
     sĩ ký». Mục ⚪ «không đo được» giữ nguyên là ⚪, KHÔNG đọc thành đạt hay thành lỗi.
   - 2: nền tảng không đáng tin (nguồn giả/thiếu NCBI_EMAIL) — báo nguyên văn hướng dẫn sửa; KHÔNG suy diễn.
4. KHÔNG sửa dashboard, KHÔNG đổi decision/gradeLevel, KHÔNG ký sổ rút bài, KHÔNG xoá mục — thẩm quyền bác sĩ.

RÀNG BUỘC BẤT BIẾN: chỉ GIÁM SÁT/PHÁT HIỆN; không PII; trả lời bằng tiếng Việt; kết «Cần bác sĩ kiểm chứng.»
