---
name: cap-nhat-thang-thu-muc-endnote
description: Phiếu cập nhật chứng cứ THÁNG theo thư mục EndNote — ngày 5, 18:00: quét candidate có trần → hoàn thiện phần máy (toàn văn/PDF/tóm tắt tiếng Việt) → phiếu cho bác sĩ duyệt bản nối tiếp
---

NỀN TẢNG: macOS + Windows. THƯ MỤC LÀM VIỆC = gốc thư mục OneDrive «Claude AI» của MÁY ĐANG CHẠY (repo EBM-drluanbv175):
- macOS: "$HOME/Library/CloudStorage/OneDrive-Personal/Claude AI"
- Windows: "%USERPROFILE%\OneDrive\Claude AI" (máy hiện tại: C:\Users\Admin\OneDrive\Claude AI)
Không thấy thư mục đúng ⇒ DỪNG và báo nguyên văn; không đoán đường dẫn khác.
Trên Windows đổi lệnh: `python3` → `py -3`; `~/.ebm-venv/bin/python` → `%USERPROFILE%\.ebm-venv\Scripts\python.exe`.
Đường dẫn tương đối viết bằng `/` dùng được nguyên trên cả hai; tệp tạm ghi vào `state/` của thư mục làm việc, không dùng `/tmp`.
Trên Windows công cụ tự bỏ bước GHI EndNote (chỉ Mac điều khiển được EndNote) và ghi lý do vào phiếu — không phải lỗi.

Bạn chạy nhịp THÁNG «cập nhật chứng cứ theo thư mục EndNote» (bác sĩ giao 12/11/2026: «Xây dựng tự động cập nhật chứng cứ
hàng tháng với các thư mục trong Endnote»; bổ sung cùng ngày: «Với việc cập nhật những chứng cứ áp dụng cho thực hành lâm sàng
đảm bảo toàn văn và tóm tắt như đã xây dựng cho hệ thống cập nhật chứng cứ»). Trả lời tiếng Việt.

VÌ SAO NGÀY 5: sau bộ thu thập tháng `cap-nhat-thang-ebm` (ngày 1), tác vụ tháng `kiem-tra-hoan-thien-he-thong-thang` (ngày 3)
và tái kiểm rút bài `kiem-rut-bai-kho-thang` (ngày 4) — phiếu đọc kết quả mới nhất của chúng và của gói tuần, không chạy trùng
việc thu thập của owner (weekly_safety.sh + monthly_update.sh), không dồn tải NCBI vào cùng tối ngày 1.

QUY TẮC CHẠY LỆNH — lượt lịch KHÔNG có ai bấm «cho phép»: mỗi lần gọi Bash chạy ĐÚNG MỘT lệnh viết Y NHƯ ở bước tương ứng (không
`cd … &&`, không `;`/`&&`, không chuyển hướng ra tệp). Mọi lệnh đã khai ở `sync/quyen-lich-nen.json` và áp vào máy bằng
`python3 tools/quyen_lich_nen.py --ap-dung` (bác sĩ chạy một lần). Lệnh bị đòi duyệt quyền ⇒ ghi «⚪ bước <n> chưa chạy được —
lệnh cần duyệt quyền: <lệnh>», KHÔNG bỏ qua âm thầm.

CÁC BƯỚC:
1. `python3 tools/sync_safety_check.py` — 🔴 ⇒ DỪNG, báo nguyên văn.
2. `python3 tools/cap_nhat_thang_thu_muc_endnote.py --quet --toi-da 3 --hoan-thien --ghi`
   Công cụ tự làm ĐÚNG THỨ TỰ: đo mọi thư mục → `--quet` (orchestrator `--topic … --online` TUẦN TỰ cho ≤ 3 chủ đề nhóm (a) có
   watchlist, nghỉ giữa chủ đề, hạ tầng hỏng/NCBI chặn ⇒ dừng phần quét) → `--hoan-thien` phần KHÔNG ghi EndNote (gom toàn văn OA
   vào kho → in HTML trong kho sang PDF) → ĐO LẠI → ghi phiếu `EBM-Dashboards/derivatives/CAP-NHAT-THANG-THU-MUC_<YYYY-MM>.md`
   + `.json` và đề xuất watchlist (khoá `_de_xuat_thu_muc_endnote` của `EBM-Dashboards/watchlist.de-xuat.json`).
   Lượt lịch KHÔNG GHI EndNote (ranh giới quyền lượt lịch `sync/quyen-lich-nen.json` `_ranh_gioi`, chốt BH173): bước gắn PDF kho
   vào bản ghi và khối tiếng Việt «EBM · ĐỌC NHANH» được phiếu ghi thành việc 🛎 cho phiên Claude có người, chạy
   `python3 tools/cap_nhat_thang_thu_muc_endnote.py --hoan-thien --ghi-endnote --ghi` (rào: sức khoẻ EndNote 🟢, không giao dịch
   treo, không khoá ghi của tiến trình khác, không cờ tạm dừng — kiểm trước TỪNG bước ghi; EndNote chưa mở ⇒ bỏ qua, không tự
   bật). Lượt lịch KHÔNG tự chạy lệnh đó.
   LỆNH CHẠY LÂU (mỗi chủ đề quét tới vài chục phút; gom toàn văn tới một giờ): BẮT BUỘC gọi Bash với `run_in_background: true`
   rồi ĐỢI thông báo hoàn tất (không ngủ/thăm dò liên tục). KHÔNG kết thúc phiên trước khi phiếu tháng này có mặt — không thấy
   phiếu ⇒ báo «⚪ lượt chưa hoàn tất» (cảm biến `tools/kiem_lich_nen.py` canh kỳ này qua chính tệp phiếu).
3. Đọc phiếu `.md` vừa ghi (công cụ Read) và báo NGẮN theo đúng thứ tự phiếu: bảng nhóm (a)–(d); 🔴 mục «Áp dụng» chưa đọc toàn
   văn; danh sách bản nối tiếp (ưu tiên trước, kèm ước tính token); ⑨ chờ duyệt; toàn văn còn thiếu; đề xuất watchlist; thư mục
   có nội dung thật chưa có dashboard; kết quả từng chủ đề quét (mã, run) và từng bước hoàn thiện (mã hoặc lý do bỏ). Dòng ⚪ giữ
   nguyên là ⚪ — KHÔNG đọc thành đạt hay thành lỗi. Mã thoát của bước 2: 0 không có việc · 1 có việc cho bác sĩ · 2 KHÔNG ĐO
   ĐƯỢC (báo nguyên văn) · 3 tham số sai.

RÀNG BUỘC BẤT BIẾN:
- CHỈ CANDIDATE: không dựng/sửa dashboard, không đổi decision/gradeLevel, không tự áp dụng, không sửa `EBM-Dashboards/watchlist.json`
  (đề xuất chỉ nằm ở watchlist.de-xuat.json, bác sĩ duyệt mới chép).
- KHÔNG tự mở agent, Workflow hay làn Chrome. Bản nối tiếp dashboard (agent ≈ 0,5–0,8 triệu token/chủ đề), tóm tắt Word ⑨
  (≈ 0,3–0,6 triệu token/bài) và làn Chrome cho bài không OA CHỈ làm khi bác sĩ duyệt danh sách trong phiếu.
- Mục «Áp dụng» MỚI chỉ xuất hiện sau khi bác sĩ duyệt bản nối tiếp; khi đó bộ năm của bản nối tiếp lo toàn văn/EndNote/⑨ như thường.
- Không nâng trần quét `--toi-da` (tối đa 8) — quyết định tốn hạn mức/NCBI của bác sĩ.
- Không PII. Kết thúc bằng «Cần bác sĩ kiểm chứng.»
