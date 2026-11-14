---
name: cap-nhat-thang-ebm
description: Tác vụ THÁNG DUY NHẤT của hệ chứng cứ — ngày 1, 18:30: tiền kiểm quyền (thiếu ⇒ dừng ồn) → thu thập an toàn thuốc → cập nhật tháng + liêm chính + làm mới sổ xác minh nguồn → gói duyệt chứng cứ (≤7 thẻ CANDIDATE) → phiếu theo thư mục EndNote cho bác sĩ duyệt bản nối tiếp
---

NỀN TẢNG: CHỈ CHẠY TRÊN MAC — tác vụ gọi script bash (`*.sh`) ở bước 2–4. Windows: DỪNG ngay, báo «tác vụ này chỉ chạy trên Mac», không tự dịch sang lệnh khác.
THƯ MỤC LÀM VIỆC (macOS) = "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI" (repo EBM-drluanbv175). Không thấy ⇒ DỪNG và báo nguyên văn.
Tệp tạm ghi vào `state/` của thư mục làm việc, không dùng `/tmp`.

Bạn chạy nhịp THÁNG DUY NHẤT của hệ chứng cứ EBM. Trả lời tiếng Việt. Gộp theo lời bác sĩ 13/11/2026: «có 2 tác vụ cập nhật
tháng hãy kiểm tra lại và gộp lại chỉ 1 tác vụ», «các tác vụ giám sát Guideline cũng không cần nữa», «Gói thu thập an toàn thuốc
và duyệt chứng cứ hãy gộp vào một tác vụ tháng» ⇒ đã bỏ các tác vụ lịch riêng `thu-thap-tuan-an-toan-thuoc`, `goi-duyet-tuan-ebm`,
`cap-nhat-thang-thu-muc-endnote`, `giam-sat-9-tram-web-hoi-tuan`, `giam-sat-acc-aha-quy`; phần việc của ba tác vụ đầu nằm ở các
bước dưới. Bộ thu thập dùng mốc lần chạy trước (watermark) và bộ quét dùng con trỏ tăng dần ⇒ chạy tháng KHÔNG bỏ sót khoảng
giữa hai lượt, chỉ CHẬM hơn (tín hiệu an toàn thuốc tới tay bác sĩ chậm tới khoảng một tháng — quyết định của bác sĩ).

QUY TẮC CHẠY LỆNH — lượt lịch KHÔNG có ai bấm «cho phép»: mỗi lần gọi Bash chạy ĐÚNG MỘT lệnh viết Y NHƯ ở bước tương ứng (không
`cd … &&`, không `;`/`&&`, không chuyển hướng ra tệp). Mọi lệnh đã khai ở `sync/quyen-lich-nen.json` (khoá `cap-nhat-thang-ebm`
và khoá quy trình `goi-duyet-tuan-ebm`) và áp vào máy bằng `python3 tools/quyen_lich_nen.py --ap-dung` (bác sĩ chạy một lần).
Lệnh bị đòi duyệt quyền ⇒ ghi «⚪ bước <n> chưa chạy được — lệnh cần duyệt quyền: <lệnh>», KHÔNG bỏ qua âm thầm. (Thực tế
lượt lịch thường bị CẮT NGANG ngay tại lệnh đó mà bộ lập lịch vẫn ghi «succeeded» — vì vậy có BƯỚC 0 tiền kiểm bên dưới.)
LỆNH CHẠY LÂU (mỗi script thu thập tới cả giờ; quét chủ đề vài chục phút; gom toàn văn tới một giờ): BẮT BUỘC gọi Bash với
`run_in_background: true` rồi ĐỢI thông báo hoàn tất (không ngủ/thăm dò liên tục). Các bước chạy TUẦN TỰ, không song song.
Script thoát mã 75 kèm dòng «BỎ QUA — lượt khác đang chạy» (khoá một lượt, 29/09/2026) = một lượt khác trên máy này ĐANG chạy:
báo đúng như vậy, KHÔNG chạy lại, KHÔNG gọi là lỗi, làm tiếp bước sau.

CÁC BƯỚC:
0. TIỀN KIỂM (14/11/2026 — lượt phải GÃY ỒN, không gãy âm thầm). Chạy lần lượt hai lệnh:
   `python3 tools/quyen_lich_nen.py --tac-vu cap-nhat-thang-ebm,goi-duyet-tuan-ebm` (quyền của ĐÚNG các lệnh lượt này sẽ gõ:
   khoá tác vụ tháng + khoá quy trình gói duyệt) rồi `python3 tools/kiem_lich_nen.py` (cảm biến kỳ lỡ).
   - `quyen_lich_nen` mã 0 (🟢) ⇒ làm tiếp bước 1.
   - mã 1 (🔴 có lệnh của lượt này chưa được phép trên máy — lượt sẽ bị cắt ngang giữa chừng mà vẫn ghi «succeeded») HOẶC
     mã 2 (⚪ KHÔNG đo được quyền — không xác nhận được lượt sẽ chạy trọn; «không đo được» không phải «đủ») ⇒ DỪNG LƯỢT NGAY,
     KHÔNG chạy bước 1–6 (chạy dở tệ hơn không chạy: watermark/con trỏ dịch mà gói không ra). Báo cáo (tin nhắn cuối) mở đầu
     bằng «🔴 LƯỢT THÁNG DỪNG Ở BƯỚC 0 — tiền kiểm quyền mã <n>», dán NGUYÊN VĂN các dòng ✗/⚪ công cụ in, và lệnh bác sĩ tự
     chạy `python3 tools/quyen_lich_nen.py --ap-dung` rồi «Run now». Đồng thời thêm ĐÚNG MỘT dòng
     «- 🔴 Lượt tháng cap-nhat-thang-ebm DỪNG ở bước 0 (tiền kiểm quyền, mã <n>): <số lệnh chưa được phép / lý do ⚪> — bác sĩ
     chạy quyen_lich_nen.py --ap-dung rồi Run now» vào `alerts/<YYYY-MM-DD>.md` bằng Write/Edit (cùng khuôn
     «# CẢNH BÁO KHẨN — <ngày>» và cùng cách ghi alerts của quy trình gói duyệt; idempotent, không nhân đôi). Nếu chính danh sách
     ✗ có quy tắc `Edit(…/alerts/**)` thì KHÔNG ghi alerts (lệnh ghi sẽ bị cắt ngang) — chỉ báo trong tin nhắn cuối.
   - `kiem_lich_nen` chỉ để BÁO (kỳ cũ lỡ/trễ — lượt này chính là lượt bù): chép các dòng 🔴/🟠/⚪ vào báo cáo bước 7, KHÔNG
     dừng vì nó.
1. `python3 tools/sync_safety_check.py` — 🔴 ⇒ DỪNG, báo nguyên văn.
2. `bash medical-ebm-automation/scripts/weekly_safety.sh` — bộ thu thập AN TOÀN THUỐC + quét nguồn thật (live-update, safety,
   nối Hub, Antifacts, gom toàn văn, chỉ mục RAG); script tự `cd` vào thư mục engine. Log:
   `medical-ebm-automation/data/archive/launchd_weekly.log`.
3. `bash medical-ebm-automation/scripts/monthly_update.sh` — bộ cập nhật tháng. Log:
   `medical-ebm-automation/data/archive/launchd_monthly.log`.
4. `bash medical-ebm-automation/scripts/evidence_integrity_monthly.sh` — nhịp liêm chính tháng (tệp không tồn tại ⇒ bỏ qua và
   nói rõ). Log: `medical-ebm-automation/data/archive/evidence_integrity.log`.
4b. `python3 tools/so_xac_minh_nguon.py --vong 3` — làm mới SỔ XÁC MINH NGUỒN của mọi dashboard (tồn tại/metadata hạn 180
   ngày, trạng thái rút bài hạn 30 ngày; trước 14/11/2026 không có nhịp làm mới định kỳ nên mục hết hạn cứ dồn lại). Chạy nền
   (`run_in_background: true`). Sổ CHỈ ghi THÀNH CÔNG — lỗi mạng chỉ để mục ở «chưa xác minh», KHÔNG làm hỏng lượt: dù mã nào
   cũng làm tiếp bước 5. Đọc mã: 0 = mọi nguồn còn hiệu lực · 1 = còn mục thiếu/hết hạn (báo số công cụ in, không phải lỗi) ·
   2 KÈM dòng «[MA] SO_HONG» = sổ HỎNG, công cụ không ghi gì (báo nguyên văn; KHÔNG tự chạy `--cuu-so-hong`, đó là việc phiên
   có người) · 2 KHÔNG kèm dòng đó = CÓ NGUỒN ĐÃ BỊ RÚT ⇒ đưa lên ĐẦU báo cáo và thêm một dòng 🔴 vào `alerts/<YYYY-MM-DD>.md`
   như quy trình gói duyệt · 3 «[MA] KHONG_DO_DUOC» = ⚪ không đo được (không phải sạch, không phải rút bài).
5. GÓI DUYỆT CHỨNG CỨ: dùng công cụ Read đọc `sync/scheduled-tasks/goi-duyet-tuan-ebm/SKILL.md` (QUY TRÌNH gói duyệt — không
   còn là tác vụ lịch riêng) rồi làm TRỌN «QUY TRÌNH» 0–7, các mục «Bổ sung» và «BƯỚC CUỐI BẮT BUỘC» đúng như viết ở đó (đúng
   lệnh, đúng luật cứng: ≤7 thẻ CANDIDATE, kiểm rút bài, đọc toàn văn, mẫu thẻ, hòm thư bác sĩ, gửi tệp). Gói xuất
   `queue/tuan-<ISO-week>.md` theo tuần chạy. Bỏ qua phần NỀN TẢNG của tệp đó (đã nói ở trên).
6. `python3 tools/cap_nhat_thang_thu_muc_endnote.py --quet --toi-da 3 --hoan-thien --ghi` — phiếu theo thư mục EndNote. Công cụ
   tự làm ĐÚNG THỨ TỰ: đo mọi thư mục → `--quet` (orchestrator `--topic … --online` TUẦN TỰ cho ≤ 3 chủ đề nhóm (a) có
   watchlist, nghỉ giữa chủ đề, hạ tầng hỏng/NCBI chặn ⇒ dừng phần quét) → `--hoan-thien` phần KHÔNG ghi EndNote (gom toàn văn
   OA vào kho → in HTML trong kho sang PDF) → ĐO LẠI → ghi phiếu `EBM-Dashboards/derivatives/CAP-NHAT-THANG-THU-MUC_<YYYY-MM>.md`
   + `.json` và đề xuất watchlist (khoá `_de_xuat_thu_muc_endnote` của `EBM-Dashboards/watchlist.de-xuat.json`).
   Lượt lịch KHÔNG GHI EndNote (ranh giới quyền lượt lịch `sync/quyen-lich-nen.json` `_ranh_gioi`, chốt BH173): bước gắn PDF kho
   vào bản ghi và khối tiếng Việt «EBM · ĐỌC NHANH» được phiếu ghi thành việc 🛎 cho phiên Claude có người, chạy
   `python3 tools/cap_nhat_thang_thu_muc_endnote.py --hoan-thien --ghi-endnote --ghi` (rào: sức khoẻ EndNote 🟢, không giao dịch
   treo, không khoá ghi của tiến trình khác, không cờ tạm dừng — kiểm trước TỪNG bước ghi; EndNote chưa mở ⇒ bỏ qua, không tự
   bật). Lượt lịch KHÔNG tự chạy lệnh đó. KHÔNG kết thúc phiên trước khi phiếu tháng này có mặt — không thấy phiếu ⇒ báo
   «⚪ lượt chưa hoàn tất».
7. Báo NGẮN, TRUNG THỰC, theo thứ tự: (0) bước 0 — mã thoát tiền kiểm quyền và các dòng 🔴/🟠/⚪ của cảm biến kỳ lỡ (nếu có);
   (a) bước 2–4 — đọc dòng «KẾT THÚC» cuối của ba log trên (công cụ Read), mã thoát từng
   bước và verdict PASS/CÓ BƯỚC LỖI, KHÔNG tô hồng; bước lỗi nêu tên + mã thoát + hệ quả (watermark giữ, không nối Hub); có cảnh
   báo an toàn thuốc MỚI thì đưa lên đầu; (a') bước 4b — mã thoát sổ xác minh nguồn + số mục còn thiếu/hết hạn (nguồn ĐÃ RÚT thì
   đã đưa lên đầu); (b) bước 5 — tóm tắt gói duyệt ≤10 dòng như quy trình yêu cầu (tệp queue + hòm thư đã
   gửi); (c) bước 6 — đọc phiếu `.md` (công cụ Read), báo theo đúng thứ tự phiếu: bảng nhóm (a)–(d); 🔴 mục «Áp dụng» chưa đọc
   toàn văn; danh sách bản nối tiếp (ưu tiên trước, kèm ước tính token); ⑨ chờ duyệt; toàn văn còn thiếu; đề xuất watchlist; thư
   mục có nội dung thật chưa có dashboard; kết quả từng chủ đề quét và từng bước hoàn thiện. Mã thoát của bước 6: 0 không có việc
   · 1 có việc cho bác sĩ · 2 KHÔNG ĐO ĐƯỢC (báo nguyên văn) · 3 tham số sai. Dòng ⚪ giữ nguyên là ⚪ — KHÔNG đọc thành đạt hay lỗi.

RÀNG BUỘC BẤT BIẾN:
- CHỈ THU THẬP/BẢO TRÌ + CANDIDATE: kết quả vào hàng ứng viên; không dựng/sửa dashboard, không đổi decision/gradeLevel, không tự
  áp dụng lâm sàng, không tự duyệt thẻ thay bác sĩ, không sửa `EBM-Dashboards/watchlist.json` (đề xuất chỉ nằm ở
  watchlist.de-xuat.json, bác sĩ duyệt mới chép); Cổng A/B của bác sĩ nguyên vẹn.
- KHÔNG tự mở agent, Workflow hay làn Chrome. Bản nối tiếp dashboard (agent ≈ 0,5–0,8 triệu token/chủ đề), tóm tắt Word ⑨
  (≈ 0,3–0,6 triệu token/bài) và làn Chrome cho bài không OA CHỈ làm khi bác sĩ duyệt danh sách trong phiếu/gói.
- Mục «Áp dụng» MỚI chỉ xuất hiện sau khi bác sĩ duyệt bản nối tiếp; khi đó bộ năm của bản nối tiếp lo toàn văn/EndNote/⑨ như thường.
- Không nâng trần quét `--toi-da` (tối đa 8) — quyết định tốn hạn mức/NCBI của bác sĩ.
- Không PII. Kết thúc bằng «Cần bác sĩ kiểm chứng.»
