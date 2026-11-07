# 07/11/2026 — Báo động sai «vi phạm điều khoản ADA»: CLAUDE.md §6.4 lỗi thời so với sổ uỷ quyền

**Sự việc.** Một agent dựng bản nối tiếp dashboard Biến chứng thần kinh ĐTĐ đọc ADA Standards of Care 2026 mục 12 (PMID 41358886) từ tệp có sẵn trong kho `EBM-Dashboards/toan_van_oa/`. Phiên điều phối đối chiếu với CLAUDE.md §6.4 («Elsevier, ADA, EBSCO cấm … ⇒ Claude KHÔNG mở bài»), báo bác sĩ là «vi phạm điều khoản», trả mục về nội dung cũ và đề xuất vá `phien_uy_quyen_chrome.py --kiem`.

**Đo lại trước khi vá.** Sổ `EBM-Dashboards/dieu-khoan-bac-si-uy-quyen.json` ghi: TỐI 03/10/2026 bác sĩ chọn «Uỷ quyền máy đọc qua Chrome» cho ADA, Elsevier, OUP, NEJM, JAMA, ESC, SAGE, Springer Nature, AAP. `nxb_duoc_luu()` trả cả ADA lẫn Elsevier ⇒ `--kiem` báo «được» là ĐÚNG. Đối chiếu 1 667 PMID có tệp trong kho: 0 tệp thuộc NXB «cấm» chưa uỷ quyền. Không có lỗ hổng.

**Gốc.** Câu ở CLAUDE.md §6.4 là quyết định SÁNG 03/10; quyết định TỐI cùng ngày (sổ uỷ quyền) không được phản ánh lại vào CLAUDE.md và bộ nhớ.

**Xử lý.** Bác sĩ 07/11 chọn «Giữ uỷ quyền». Khôi phục bản ITEM-06 theo ADA SOC 2026 (cổng PASS, bộ năm chạy lại). Sửa câu CLAUDE.md §6.4: NXB «cấm AI» chỉ đọc khi còn uỷ quyền trong sổ, tra sổ trước khi báo vi phạm; EBSCO/DynaMed không bao giờ. Đính chính bộ nhớ và lời giao agent.

**Bài học.** Kết luận «vi phạm điều khoản» phải dựa trên sổ uỷ quyền (nguồn sự thật mà công cụ đọc), không dựa trên câu mô tả trong tài liệu tổng quan — tài liệu là ảnh chụp (CLAUDE.md §0.4).
