# 28/10/2026 — Câu hỏi chủ đề chứng cứ không vào dây chuyền thiết kế ⇒ luật «một cửa vào» (BH172)

**Bác sĩ hỏi:** «Hãy kiểm tra lại tại sao tôi cập nhật chứng cứ y khoa không thực hiện theo đúng thiết kế và xây dựng».

**Đo (đọc nhật ký ba phiên chiều 28/10/2026):**

| Phiên | Câu bác sĩ gõ | Đường đã đi | Thiếu so với CLAUDE.md §6.2 |
|---|---|---|---|
| Suy tim | «Tiếp cận chẩn đoán điều trị, tiên lượng suy tim một cách toàn diện dựa trên chứng cứ mới nhất và độ tin cậy cao nhất» | skill `tong-thuat-chung-cu` → `TT_suy-tim-toan-dien_20261028` (64 nguồn) | không dashboard, không `verify_dashboard`, không bộ năm, không hub; EndNote nối sau khi bác sĩ hỏi (#270) |
| Đái tháo đường | «Tiếp cận chẩn đoán và điều trị bệnh tiểu đường, biến chứng … toàn diện nhất dựa trên chứng cứ mới nhất …» | skill `tong-thuat-chung-cu` (23 → 31 nguồn sau khi bác sĩ nhắc mới chạy orchestrator/làn Chrome) | như trên |
| Đa bệnh lý | «… cách tiếp cận như thế nào hợp lí nhất để không có những sai sót cá nhân …» | trả lời thẳng từ trí nhớ (tự bắt 3 trích dẫn sai: 2 PMID trỏ nhầm bài, 1 bài đã rút); thẻ A4 không qua cổng | sau khi bác sĩ nhắc mới gọi `cap-nhat-chung-cu-y-khoa` |

Đối chiếu bài suy tim với hai dashboard suy tim đang có: 44/64 và 48/64 nguồn KHÔNG có trong dashboard — tức không qua cổng
liêm chính, không vào hub (không vào `tra_diem_kham`, không được theo dõi độ tươi / đặt cạnh), không có ⑨.

**Nguyên nhân gốc (bốn lớp):**
1. Hai đường song song không có luật chọn: `tong-thuat-chung-cu` (19/08, bác sĩ duyệt «bài liền mạch» khi so với Gemini/ChatGPT)
   và dây chuyền `cap-nhat-chung-cu-y-khoa` (§6.2). CLAUDE.md §1 chỉ có nhánh «cập nhật chứng cứ chủ đề X», không nhắc tổng thuật;
   hai SKILL.md không nhắc nhau.
2. Danh sách skill cắt mô tả còn 80 ký tự (`skillListingMaxDescChars`): model thấy «…khi bác sĩ yêu cầu cập nhật chứng cứ hoặc
   khuyến cáo hiện hàn…» và «Bác sĩ hỏi MỘT chủ đề lâm sàng → trả MỘT bài tổng thuật…». Câu không có chữ «cập nhật» ⇒ khớp tổng thuật.
   `dark-analyst` trùng nguyên văn mô tả với `cap-nhat-chung-cu-y-khoa`.
3. `tools/orchestrator/intent.py` có nhưng không ai gọi lúc bác sĩ gõ (không có hook UserPromptSubmit); gọi thì cũng xếp hai câu
   đầu thành `tra-cuu-chung-cu` (một câu hỏi lẻ) và «Cập nhật chứng cứ suy tim» thành agent `cap-nhat-guideline` — lệch §1(b).
4. Lối tổng thuật thiếu các khâu: không lượt «mới vào PubMed»/«vượt qua», không cổng `verify_dashboard`, không hub, không bộ năm/⑨.

**Bác sĩ chọn (AskUserQuestion 28/10):** «Một cửa vào» · hai bài tổng thuật hôm nay «để sau khi sửa xong».

**Vá:**
- `intent.py`: câu có cue CHỦ ĐỀ (toàn diện · tiếp cận · cập nhật · tổng thuật · mới nhất · hiện hành · tin cậy cao nhất) VÀ từ chứng
  cứ/lâm sàng ⇒ `cong_cu` → `cap-nhat-chung-cu-y-khoa`. Đứng SAU đề tài và ca lâm sàng; thua cờ đỏ và việc lẻ MẠNH; câu hỏi VỀ hệ
  thống («hệ thống cập nhật…», «đúng thiết kế», skill/agent/hook…) không bị kéo vào; «hệ thống» trần không loại (lupus ban đỏ hệ thống).
- Hook UserPromptSubmit `tools/nhac_dinh_tuyen.py` (khai ở `.claude/settings.json` đi qua git): chạy router, nhắc đúng đường cho câu
  chủ đề / ca lâm sàng, im lặng với câu khác, lỗi ⇒ im lặng mã 0 (~0,05 giây).
- Mô tả skill: 80 ký tự đầu của `cap-nhat-chung-cu-y-khoa` = «CỬA VÀO DUY NHẤT…»; `tong-thuat-chung-cu` = «KHÔNG phải cửa vào…»;
  `dark-analyst` = «CHỈ khi bác sĩ yêu cầu RÕ giao diện Dark Analyst…». Thân `tong-thuat-chung-cu` thêm mục «ĐIỀU KIỆN VÀO»;
  thân `cap-nhat-chung-cu-y-khoa` §1 thêm «MỘT CỬA VÀO» (bước 0 orchestrator, lát cắt cho chủ đề «toàn diện», bài đọc sau bộ năm).
- `tools/xuat_tong_thuat.py --dashboard <dashboard>`: chặn mục «## Nguồn» không có PMID/DOI/URL trong dashboard (PMID khớp trọn số,
  DOI so chữ thường). Thiếu cờ ⇒ cảnh báo (không chặn, để không vỡ phiên đang chạy).
- CLAUDE.md §1(b) và §2 (hook) viết lại; để vừa ngân sách 60.000 ký tự đã rút ba đoạn số đo lịch sử, nguyên văn chép ở đây:
  «(BH149; OneDrive SyncEngine kẹt vòng lặp log tái diễn 21/08, 17/09, 01–02/10: log 24 GB/24.796 tệp/~54 tệp mỗi phút)» ·
  «(02/10/2026; đo 02/10: ADA, OUP-ESC, NEJM, Lancet, JAMA, AHA, Wiley, BMJ, Elsevier, SAGE, Springer… chặn truy cập tự động)» ·
  «Báo cáo đánh giá: thư mục `audit/` (12 = đánh giá hoàn thiện 21/09; 15 = nguồn chứng cứ trên Cloud 24/09)»; gộp mục 6 «Trả lời
  bác sĩ bằng TIẾNG VIỆT (§0.1)» vào mục 5 của §5.

**Kiểm hồi quy:** `tools/test_mot_cua_vao_chung_cu_20261028.py` (31 ca; chạy ĐÚNG lệnh hook đã khai bằng bash) — 10 phép đột
biến đều đỏ đúng chỗ, phục hồi xanh (ba phép sống sót lần đầu là lỗi phép thử: chuỗi `<agent-message>` tình cờ chứa «agent», dashboard
mẫu đã viết thường sẵn, đột biến trúng dòng chú thích thay vì lệnh — đã siết). Chốt **BH172** (6 đột biến đỏ). Bộ test router/
orchestrator cũ: 386 đạt.

**Chưa làm (bác sĩ chọn để sau):** đưa hai chủ đề suy tim, đái tháo đường vào dây chuyền thành bản nối tiếp dashboard có sẵn.
Hook chỉ có hiệu lực ở phiên MỚI mở sau khi gộp; bộ skill tài khoản (claude.ai/Cowork) cần bác sĩ tải lại ZIP để nhận mô tả mới.
