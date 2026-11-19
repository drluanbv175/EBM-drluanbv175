# 20/11/2026 — Bảo đảm đọc toàn văn chưa phủ mục «Áp dụng ngay» không có PMID

**Bối cảnh.** Bác sĩ yêu cầu ngày 20/11/2026 («Làm 2,3,6» — mục 2): mở rộng bảo đảm đọc toàn văn (BH161) sang các mục không có PMID.

**Nguyên nhân.** `verify_dashboard.kiem_toan_van_apply` và `tools/so_toan_van.py` chỉ đo theo PMID. Số đo ngày 20/11/2026 trên bản ĐÃ PASS mới nhất của mỗi chủ đề:
- 164 mục `apply` không có PMID;
- các mục này quy về 123 nguồn khác nhau, phần lớn là nhãn DailyMed/openFDA và trang FDA/MHRA, vài mục chỉ có DOI;
- 0/123 nguồn có bằng chứng đã đọc.

Tính trên mọi phiên bản dashboard: 375 mục, 127 nguồn. Nhóm này chưa từng có bằng chứng đã đọc nguồn gốc, nhưng sổ nợ và cổng đều không thấy.

**Cách vá** (PR gốc, nhánh `claude/toan-van-nguon-chinh-thuc-20261120`):
- **Cổng.** `verify_dashboard.py` (2 bản git trùng byte) thêm `khoa_nguon_chinh_thuc`, `bang_chung_nguon_chinh_thuc` và `kiem_doc_nguon_chinh_thuc_apply`.
  - Hàm cổng được gọi ngay sau `kiem_toan_van_apply` trong khối `--strict-sources`.
  - Hiện chỉ CẢNH BÁO, chưa chặn.
  - Khoá nguồn GIỮ query, chỉ bỏ `utm_*` và fragment. Bản đầu bỏ cả query nên gộp 224 mục openFDA và 90 mục DailyMed thành 22 «nguồn» — bắt được nhờ đo trước khi chốt.
- **Công cụ `tools/doc_nguon_chinh_thuc.py`.** Có các lệnh `liet-ke`, `tai`, `nap-trinh-duyet`, `bac-si-da-doc`, `huong-dan`; chạy khô mặc định.
  - **Cổng điều khoản NXB trước khi tải** (`lan_doc`, theo doctrine §2septies). Máy chỉ tải miền cơ quan nhà nước hoặc NXB khai giấy phép mở cấp NXB.
  - NXB trong `DIEU_KHOAN_NXB`: còn uỷ quyền đọc thì đi làn trình duyệt; không còn thì bác sĩ đọc trực tiếp.
  - NXB hoặc miền chưa kiểm điều khoản: đi làn trình duyệt, nạp phải kèm `--dieu-khoan`.
  - Miền chặn truy cập tự động được so ĐÚNG tên máy như cổng, nên `api.fda.gov` không bị coi là miền chặn.
  - Chuyển hướng ra khỏi miền được phép thì bỏ nội dung, không ghi.
  - Bản sao chữ chỉ lưu với miền giấy phép mở; miền khác chỉ lưu độ dài và sha256.
- **Báo cáo.** `so_toan_van.py` thêm phần «mục apply không PMID». `tu_de_xuat_viec.py` thêm việc 🛎 khi còn nguồn chưa đọc.
- **Dạy agent.** Cập nhật `cap-nhat-chung-cu-y-khoa/SKILL.md` và `.claude/agents/cap-nhat-guideline.md`.

**Kiểm hồi quy.**
- `tools/test_doc_nguon_chinh_thuc_20261120.py` (35 test, ngoại tuyến): xanh.
- Kiểm đột biến: 18/18 đột biến bị bắt, phục hồi xanh. Các đột biến gồm: bỏ query, bỏ ngưỡng ký tự, coi mọi nguồn là đã đọc, bỏ miễn trừ mục có PMID, không gọi cổng, bỏ bảng NXB cấm, bỏ uỷ quyền, làn bác sĩ vẫn tải, bỏ kiểm chuyển hướng, nạp không đòi điều khoản, so miền chặn theo hậu tố, lưu bản sao ở mọi miền, chạy khô vẫn ghi, nhận trang chặn, không đòi kết luận của bác sĩ…
- Test cũ liên quan (toàn văn, cổng, sổ việc, hòm việc): 544 test xanh.
- Chạy khô trên nguồn thật: 5/6 tải được, 1 chuyển sang làn trình duyệt.

**Còn treo.**
- Bật chặn thay cho cảnh báo là quyết định của bác sĩ, sau khi độ phủ đủ.
- Bản chạy ngoài git (`EBM-Dashboards/tools/`, `EBM_MASTER/skill_assets/`) phải đồng bộ sau khi gộp.
