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
không ai biết (tác vụ quý `kiem-thang-diem-quy` từng phủ 32 thang điểm, đã bỏ 13/11/2026 theo bác sĩ). Tác vụ này là owner DUY NHẤT
của việc tái kiểm định kỳ đó; không nối trùng qua tools/tu_khoi_dong.py.

QUY TẮC CHẠY LỆNH — lượt lịch KHÔNG có ai bấm «cho phép» (14/11/2026): mỗi lần gọi Bash chạy ĐÚNG MỘT lệnh viết Y NHƯ ở bước
tương ứng (không `cd`, không nối `&&`/`;`/`|`, không chuyển hướng `>`). Mọi lệnh đã khai ở khoá `kiem-rut-bai-kho-thang` của
`sync/quyen-lich-nen.json`, áp vào máy bằng `python3 tools/quyen_lich_nen.py --ap-dung` (bác sĩ chạy). Lệnh chưa được phép làm
lượt bị CẮT NGANG ngay tại đó mà bộ lập lịch vẫn ghi «succeeded» — vì vậy có BƯỚC 0 tiền kiểm bên dưới. Đọc tệp ⇒ công cụ Read.

CÁC BƯỚC:
0. TIỀN KIỂM QUYỀN (14/11/2026; lượt phải GÃY ỒN, không gãy âm thầm — mẫu theo bước 0 của `cap-nhat-thang-ebm`). Lệnh Bash
   ĐẦU TIÊN của lượt: `python3 tools/quyen_lich_nen.py --tac-vu kiem-rut-bai-kho-thang` (quyền của ĐÚNG các lệnh lượt này sẽ
   gõ — khoá `kiem-rut-bai-kho-thang` của `sync/quyen-lich-nen.json`).
   - mã 0 (🟢) ⇒ làm tiếp bước 1.
   - mã 1 (🔴 có lệnh của lượt này chưa được phép trên máy, hoặc SKILL có lệnh chưa khai/lệnh ghép — lượt sẽ bị cắt ngang giữa
     chừng, vd ở lệnh chu trình bước 2 chạy 20+ phút, mà bộ lập lịch vẫn ghi «succeeded») HOẶC mã 2 (⚪ KHÔNG đo được quyền —
     «không đo được» không phải «đủ») ⇒ DỪNG LƯỢT NGAY, KHÔNG chạy bước 1–4. Kỳ này KHÔNG được tái kiểm: không có dòng
     «KẾT THÚC» mới trong state/kiem-rut-bai-kho.log nên cảm biến `tools/kiem_lich_nen.py` tự báo 🔴 kỳ lỡ — đúng sự thật;
     KHÔNG tự gõ dòng vào log (dấu vết tự khai là dấu vết giả). Tin nhắn cuối mở đầu bằng «🔴 LƯỢT RÚT BÀI THÁNG DỪNG Ở BƯỚC 0 —
     tiền kiểm quyền mã <n>», dán NGUYÊN VĂN các dòng ✗/⚪ công cụ in, và lệnh bác sĩ tự chạy
     `python3 tools/quyen_lich_nen.py --ap-dung` rồi «Run now». Đồng thời thêm ĐÚNG MỘT dòng «- 🔴 Lượt rút bài tháng
     kiem-rut-bai-kho-thang DỪNG ở bước 0 (tiền kiểm quyền, mã <n>): <số lệnh chưa được phép / lý do ⚪> — bác sĩ chạy
     quyen_lich_nen.py --ap-dung rồi Run now» vào `alerts/<YYYY-MM-DD>.md` bằng Write/Edit (khuôn «# CẢNH BÁO KHẨN — <ngày>»
     như các dòng alerts khác; idempotent, không nhân đôi). Nếu chính danh sách ✗ có quy tắc `Edit(…/alerts/**)` thì KHÔNG ghi
     alerts (lệnh ghi sẽ bị cắt ngang) — chỉ báo trong tin nhắn cuối.
   - Windows: BỎ QUA bước 0 — hợp đồng quyền `sync/quyen-lich-nen.json` chỉ khai cho macOS (`nen_tang: darwin`, cùng cách
     `tools/dong_bo_tac_vu_lich.py` coi là «không áp»); ghi «⚪ bước 0 không áp trên Windows» vào báo cáo rồi làm tiếp bước 1.
1. `python3 tools/sync_safety_check.py` (Windows: `py -3 tools\sync_safety_check.py`). 🔴 ⇒ DỪNG, báo nguyên văn.
1b. LÀM MỚI NỀN RETRACTION WATCH khi quá hạn (thêm 07/11/2026, bác sĩ chọn «Làm 1 và 2»: đo 07/11 nền 48 ngày tuổi — hạn 30 —
   vì chu trình chỉ tải khi nền VẮNG, không tải khi CŨ):
   `~/.ebm-venv/bin/python medical-ebm-automation/tools/tai_retraction_watch.py --kiem`; mã 1 (quá hạn) hoặc 2 (vắng) ⇒
   `~/.ebm-venv/bin/python medical-ebm-automation/tools/tai_retraction_watch.py` (CC0, ~67 MB; Crossref Labs → gương GitLab
   chính thức của Crossref). Tải hỏng ⇒ ghi «⚪ nền chưa làm mới» vào báo cáo và đi tiếp — KHÔNG coi kỳ này là sạch.
2. Chạy (Windows thay `python3` bằng `py -3`):
   `python3 tools/chu_trinh_chung_cu.py --vong 3 --ghi-log state/kiem-rut-bai-kho.log`
   Lệnh tự chạy ① nguồn thật → ② độ tươi → ③ xác minh (gồm bản ghi mồ côi) → ④ rút bài → ⑤ mâu thuẫn → ⑥ dây
   chuyền, và nối một dòng «KẾT THÚC (mã N)» vào state/kiem-rut-bai-kho.log để tools/kiem_lich_nen.py canh được kỳ này.
   LỆNH CHẠY LÂU (đo 25/10/2026: 23 phút — vượt cả hạn tối đa 10 phút của một lệnh Bash chạy thường). Lượt 04/10 gọi Bash với
   hạn mặc định 2 phút ⇒ lệnh bị cắt, KHÔNG ghi được dòng «KẾT THÚC», phiên vẫn hiện «succeeded» ⇒ lịch báo trễ. Vì vậy: BẮT
   BUỘC gọi Bash với `run_in_background: true` rồi ĐỢI thông báo hoàn tất (không ngủ/thăm dò liên tục; đặt `timeout` không đủ).
   KHÔNG kết thúc phiên trước khi
   state/kiem-rut-bai-kho.log có dòng «KẾT THÚC» MỚI của hôm nay — không thấy dòng đó thì báo «⚪ lượt chưa hoàn tất».
2b. QUÉT RÚT BÀI CHO TOÀN THƯ VIỆN ENDNOTE (thêm 07/11/2026 — chu trình ở bước 2 chỉ phủ trích dẫn CỦA DASHBOARD; bản ghi bác sĩ
   tự nhập, trích dẫn đề tài… thì không ai đối chiếu): `~/.ebm-venv/bin/python tools/kiem_rut_bai_endnote.py` (Windows dùng
   venv tương ứng; máy chưa khai thư viện EndNote ⇒ mã 2 «không đo được», ghi đúng như vậy). Ngoại tuyến, vài giây, chỉ đọc.
   Mã 1 ⇒ liệt kê từng recNum ĐÃ RÚT / Expression of concern kèm tiêu đề và câu «Cần bác sĩ xem; tag «⛔ Đã rút bài» và gỡ
   «★ Áp dụng» do phiên Claude làm qua giao diện (`python3 tools/gan_tag_endnote.py --huong-dan`)». Mã 2 ⇒ ⚪/🟡 giữ nguyên.
3. Đọc mã thoát (của bước 2; bước 2b báo riêng một dòng):
   - 0: báo MỘT dòng — kho sạch (không thấy nguồn bị rút), kèm câu phạm vi «chỉ là toàn vẹn kỹ thuật».
   - 1: liệt kê NGẮN từng việc chu trình in ra; mục 🔴 rút bài: nêu dashboard, định danh, trạng thái — kèm câu «Cần
     bác sĩ xem; với thông báo rút là bản đính chính bị rút, dựng mẫu bằng `python3 tools/mau_ky_rut_bai.py` — CHỈ bác
     sĩ ký». Mục ⚪ «không đo được» giữ nguyên là ⚪, KHÔNG đọc thành đạt hay thành lỗi.
   - 2: nền tảng không đáng tin (nguồn giả/thiếu NCBI_EMAIL) — báo nguyên văn hướng dẫn sửa; KHÔNG suy diễn.
4. KHÔNG sửa dashboard, KHÔNG đổi decision/gradeLevel, KHÔNG ký sổ rút bài, KHÔNG xoá mục — thẩm quyền bác sĩ.

RÀNG BUỘC BẤT BIẾN: chỉ GIÁM SÁT/PHÁT HIỆN; không PII; trả lời bằng tiếng Việt; kết «Cần bác sĩ kiểm chứng.»
