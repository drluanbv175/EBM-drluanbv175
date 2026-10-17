# 17/10/2026 — Làn Chrome chỉ sống trong script tạm; trạm nguồn ACC/AHA–WHO bị vòng quét urllib hạ degraded mỗi tuần

**Bối cảnh:** bác sĩ yêu cầu «các vấn đề nguồn hãy xây dựng làn Chrome để được phủ và toàn văn tốt nhất». Đo sống trước khi
xây:
- Sổ nguồn: 35 hoạt động · 4 suy giảm · 3 chưa phủ.
- Hàng chờ toàn văn của làn Chrome: 195 bài — 40 đã lưu, 23 không có quyền, CÒN 132.

**Phát hiện (đo 17/10/2026):**
1. **Làn toàn văn không có trong repo.**
   - Hàm JS dựng tệp, cách lấy thân bài/PDF theo NXB, dấu «không có quyền», hàng chờ theo ưu tiên và lệnh nhận tệp chỉ nằm ở
     `~/.ebm-worktrees/_lan_chrome_bo_chay/` cùng localStorage của từng miền ⇒ phiên/máy khác phải dò lại từ đầu.
   - Các cách lấy PDF: ScienceDirect `/pii/<PII>/pdfft`; OUP silverchair; trang xem PDF của Cochrane.
   - Các dấu không quyền: OUP `redirectedFrom=fulltext`; Nature «Access options»; LWW chuyển sang trang abstract Ovid.
2. **Trạm SRC-015 (ACC/AHA) và SRC-022 (WHO) mắc vòng «degraded» không thoát được.**
   - Nạp qua Chrome thành công (`--nap-van-ban`) mà nhãn vẫn `degraded`: đường này chỉ bật `not-covered → active`.
   - Vòng quét urllib hằng tuần vẫn tải hai trạm, luôn bị chặn bot, nên lại hạ `degraded`.
   - `--nap-van-ban` ghi «thành công» cả khi đọc ra 0 tiêu đề (trái BH138).
3. **Chạy làn nguồn bằng tay sinh ứng viên giả.**
   - Nạp cả trang WHO sinh **71 ứng viên giả** từ bảng guideline DỰ KIẾN 2026–2027; đã lọc tay tệp ứng viên, chỉ giữ 1 guideline
     mới thật.
   - Dòng chỉ có tháng-năm («Sep 2026») bị nối vào tiêu đề phía trên ⇒ tiêu đề rác.
   - Trang `/guidelines-and-statements` của ACC/AHA chỉ là trang giới thiệu (4 tiêu đề). Danh sách thật nằm ở
     `/guidelines-statements`.
4. **Ba nguồn KHÔNG phủ được bằng Chrome khi VPN bật** (IP thoát ở nước ngoài):
   - Cục Quản lý Dược: `ERR_CONNECTION_TIMED_OUT` ngay trên Chrome thật.
   - EMA: CloudFront chặn cả Chrome thật. Engine vẫn chạy dự phòng EC Union Register — kiểm thật 17/10.
   - Semantic Scholar: HTTP 429 khi không có khoá — cần khoá API, không phải việc của trình duyệt.

**Cách vá:**
- `tools/lan_chrome/bo_luu.js` — bộ lưu (bước 1 thân bài + PDF nhúng; bước 2 `__ebmPdfNut` kiểm `%PDF-` và URL chứa PII/hậu tố
  DOI). Phán quyết thuần `danhGia` tách riêng để test bằng node.
- `tools/lan_chrome/cau_hinh.json` — chỉ cấu hình ĐÃ KIỂM THẬT, kèm `kiem_lan_cuoi`:
  - 10 NXB: ScienceDirect · NEJM · AHA · OUP · Springer · Nature · SAGE · T&F · Cochrane · Wiley;
  - miền chuyển hướng `linkinghub.elsevier.com`;
  - dấu URL không quyền;
  - 4 trạm nguồn: hai trạm đang chạy có vùng cắt; Cục QLD/EMA khai `dieu_kien: tat_vpn`.
- `tools/lan_chrome.py`:
  - `toan-van` — kiểm phiên rồi in mã JS đã điền cấu hình;
  - `pdf`; `nhan` (HTML trước PDF, bỏ `.crdownload`);
  - `hang-cho` — theo miền · ưu tiên · có cấu hình · phạm vi phiên;
  - `nguon` — 🛎 trạm quá hạn; `--cat` cắt ĐÚNG vùng guideline đã phát hành rồi mới nạp.
- `tools/giam_sat_to_chuc.py`:
  - `--nap-van-ban`: 0 tiêu đề ⇒ không ghi gì; ≥1 tiêu đề ⇒ `degraded`/`broken` → `active`.
  - Vòng quét KHÔNG tải trạm kênh trình duyệt, chỉ xét độ cũ: quá chu kỳ ⇒ `degraded` + 🛎, không im lặng.
  - Trạm khai `dieu_kien` vẫn quét urllib như cũ.
- Dạy agent: thêm chỉ dẫn vào `doc_toan_van_co_nguoi.py --huong-dan` (bước 0b) và docstring quy trình
  `phien_uy_quyen_chrome.py`. Doctrine `_CONNECTOR-CHUNG-CU.md` chưa sửa: tệp có bản sao Codex và cặp với repo y khoa — việc
  sau.

**Kiểm hồi quy:**
- `tools/test_lan_chrome_dong_goi_20261017.py` — 34 test, trong đó có test chạy JS bằng node.
- 20 phép đột biến đều đỏ đúng test rồi phục hồi xanh. Một đột biến sống sót lần đầu («trạm điều kiện bị bỏ qua») — fixture
  thiếu vùng cắt nên phép kiểm `dieu_kien` không được thử; đã sửa fixture.
- Test liên quan (trạm nguồn · phiên uỷ quyền · đọc toàn văn · làn Chrome): 333 đạt / 2 bỏ qua. `giam_sat_to_chuc --self-test` đạt.

**Đã chạy làn nguồn 17/10 (trước bản vá, bằng `--nap-van-ban`):**
- WHO: 1 guideline mới — «WHO guidelines on the integrated management of obesity in adolescents», 07/10/2026.
- ACC/AHA: 1 guideline mới — «2026 Guideline for Adult Stroke Rehabilitation and Recovery».
- Cả hai nằm ở `EBM-Dashboards/surveillance/to-chuc-2026-10-17.md` ([CẦN KIỂM CHỨNG]).
- State của SRC-015 còn một tiêu đề rác từ lượt chạy tay; lần nạp đầu bằng `--cat` sẽ hiện lại các tiêu đề ACC/AHA đã sạch
  dòng ngày như «mới» một lần.
