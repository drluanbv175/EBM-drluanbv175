---
name: ebm-giam-sat-chung-cu
description: Giám sát chứng cứ 8 nhóm nội khoa (uỷ thác đội Agent) — Thứ 4 19:20
---

NỀN TẢNG: macOS + Windows. THƯ MỤC LÀM VIỆC = gốc thư mục OneDrive «Claude AI» của MÁY ĐANG CHẠY (repo EBM-drluanbv175):
- macOS: "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI"
- Windows: "%USERPROFILE%\OneDrive\Claude AI" (máy hiện tại: C:\Users\Admin\OneDrive\Claude AI)
Không thấy thư mục đúng ⇒ DỪNG và báo nguyên văn; không đoán đường dẫn khác.
Trên Windows đổi lệnh: `python3` → `py -3`; `~/.ebm-venv/bin/python` → `%USERPROFILE%\.ebm-venv\Scripts\python.exe`.
Đường dẫn tương đối viết bằng `/` dùng được nguyên trên cả hai; tệp tạm ghi vào `state/` của thư mục làm việc, không dùng `/tmp`.

Bạn đang chạy ROUTINE GIÁM SÁT CHỨNG CỨ nội tổng quát ngoại trú cho BS Luân — tự động, KHÔNG hỏi lại, mặc định an toàn, append-only, KHÔNG bịa chứng cứ, KHÔNG PII.

BƯỚC 1 — Đọc và thực thi ĐÚNG file routine canonical (nguồn sự thật duy nhất):
`Scheduled/giam-sat-chung-cu/SKILL.md` (trong THƯ MỤC LÀM VIỆC)
Routine này dò CHỨNG CỨ LÂM SÀNG theo 8 nhóm bệnh nội khoa, ủy thác cho giao thức `.claude/agents/_GIAM-SAT-CHUNG-CU-NOI-CHUNG.md`; tra cứu/định vị qua các agent `cap-nhat-guideline`, `tra-cuu-chung-cu`, `tham-dinh-grade-nnt` (mục đổi thực hành), `huong-dan-lam-sang`.

BƯỚC 2 — Tuân chuẩn wiring dùng chung `.claude/agents/_ROUTINE-AGENT-WIRING.md` + hiến pháp liêm chính `.claude/agents/_HIEN-PHAP-LIEM-CHINH.md`:
- Mỗi phát hiện kèm PMID/DOI; disclaimer "Cần bác sĩ kiểm chứng"; KHÔNG PII.
- Connector (web/PubMed) thiếu → run = PARTIAL, ghi QC_LOG, KHÔNG kết luận "không có cập nhật".
- CHỈ ĐỀ XUẤT; "áp dụng ngay" = hàng chờ bác sĩ duyệt; KHÔNG tự đổi thực hành.

BƯỚC 3 — Ghi phát hiện vào sổ cái append-only `.claude/agents/_SO-EBM-MASTER.md` (backup .bak trước khi ghi; cập nhật last_sweep_date), rồi BÁO CÁO cho bác sĩ.

BƯỚC 4 — GUARDRAIL ĐẦU RA (bắt buộc, bước cuối): gọi agent `tham-dinh-dau-ra` soi gói theo 2 LỚP — Lớp 1 LIÊM CHÍNH R1–R7 + Lớp 2 CHẤT LƯỢNG Med-PaLM Q1–Q7 (dễ đọc · đúng đắn · đầy đủ · thiên kiến · nguy cơ hại · cập nhật · thẩm quyền nguồn; xem `.claude/agents/_CHUAN-CHAT-LUONG-MEDPALM.md`); còn lỗi đỏ → TRẢ-VỀ-SỬA, không phát hành; Q2/Q5 đỏ → chuyển bác sĩ.

Nếu một subagent không gọi được trong phiên nền, tự thực hiện bước đó theo đúng đặc tả file `.claude/agents/<tên>.md` (cùng chuẩn, cùng định dạng). Chạy trên MỘT máy (Mac) để tránh xung đột OneDrive.