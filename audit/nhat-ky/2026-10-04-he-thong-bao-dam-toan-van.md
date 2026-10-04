# 04/10/2026 — Hệ thống DẶN đọc toàn văn nhưng không KIỂM: cổng mù với mục apply chỉ có tóm tắt; chuỗi theo chủ đề không có bước toàn văn (BH161)

**Câu hỏi của bác sĩ:** «hệ thống hiện tại đã đảm bảo việc phủ chứng cứ và đọc toàn văn cho tôi chưa». Bác sĩ sẽ yêu cầu
cập nhật theo từng chủ đề sau, nên câu hỏi là về NĂNG LỰC của dây chuyền, không phải phần tồn của kho. Đo sống trên mã thật.

**Lỗ hổng 1 — cổng chỉ chặn khi mục tự khai.**
- Luật «TẦNG TOÀN VĂN» (15/08) ở `strict_source_checks` chặn `apply` khi mục TỰ KHAI `appraisalCompleteness:'partial'`;
  vắng trường thì không suy đoán (BH08).
- Đo 04/10 trên 342 mục apply:
  - chỉ 6 mục có khai trường đó;
  - 27 mục (20 PMID) không có toàn văn nào trong kho dùng chung mà vẫn qua cổng — kể cả 4 mục mà kho chỉ chứa trang giới thiệu
    kho lưu trữ (BH160);
  - 17 mục không có PMID (guideline chỉ có URL/DOI) — phép đo theo kho không với tới.

**Lỗ hổng 2 — chuỗi máy theo chủ đề không có bước toàn văn.**
- `ops/orchestrator.py` (A2 quét → A4 → B2 → B5) không gọi công cụ toàn văn nào.
- Chỉ gói tuần (bước 4b) và phiên skill có dặn.
- Ứng viên mới tới tay bác sĩ khi máy mới đọc tóm tắt.

**Vá (phạm vi hợp lệ — máy không lách tường phí):**
- `verify_dashboard.kiem_toan_van_apply`, gọi trong `main()` khi `--strict-sources`:
  - đo kho `toan_van_oa/` cạnh dashboard;
  - mục apply mà kho không có toàn văn của PMID chính và không tự khai ⇒ CẢNH BÁO;
  - không thấy kho ⇒ ⚪ «chưa đo» (không đỏ giả);
  - CHƯA chặn: chặn buộc đổi `decision` của các mục bác sĩ đã duyệt — nâng thành lỗi là quyết định của bác sĩ.
  - Đo trên 72 dashboard: đúng 27 cảnh báo, 0 dashboard đổi mã thoát.
- `tools/toan_van_theo_chu_de.py`, bước «TV» của orchestrator (giữa A2 và A4/B2, phụ trợ — không dừng chuỗi). Bước này nối ba
  công cụ có sẵn:
  - `gom_toan_van_dashboard.py --unpaywall` — PMC OA + giấy phép mở (BH160);
  - `doc_sau_toan_van.py`;
  - `doc_toan_van_co_nguoi.py` — phiếu làn trình duyệt có bác sĩ CHỈ cho bài còn thiếu.
  - PMID lấy từ ứng viên A2 (bỏ bài đã rút) cộng mục apply thiếu toàn văn; trần 60 PMID/lượt.

**Giới hạn còn lại (sự thật về quyền truy cập, không phải lỗi mã):**
- Đo 04/10: 50 bài OA có giấy phép CC còn thiếu — máy tải bị trang NXB chặn 50/50 (HTTP 403/trang thử thách).
- 101 bài đọc miễn phí của NXB đã uỷ quyền đọc phải qua làn trình duyệt có phiên.
- 181 bài không OA cần quyền truy cập.
- Bước TV chỉ LẬP PHIẾU cho các bài đó; người mở vẫn là bác sĩ.

**Kiểm:**
- `tools/test_toan_van_bao_dam_20261004.py`: 10 test, có một test chạy `main()` thật để kiểm DÒNG THI HÀNH.
- Đột biến 6/6 làm test đỏ.
- BH161 kiểm hành vi. Đột biến 4/4 làm BH161 đỏ, kể cả ca bước TV mang tiền tố «A2» (sẽ bị phân loại như bước quét).
- Test orchestrator cũ vẫn xanh.
