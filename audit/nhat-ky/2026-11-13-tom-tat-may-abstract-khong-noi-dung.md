# 13/11/2026 — Tóm tắt máy từ toàn văn PMC cho abstract guideline không nêu nội dung

**Bối cảnh.** Đợt 2 «Tóm tắt MÁY» (109 bài tham khảo, 13/11) ghi `han_che` «abstract là đoạn mô tả chung, không chứa
khuyến cáo — cần đọc toàn văn» cho ADA Standards of Care 2026 chương 5 (PMID 41358898), ASCO cachexia 2023 (PMID 37467399)
và 4 phần AUA 2026 sỏi thận (PMID 41263323, 41263322, 41263325, 42529979). Luật 20/10 chỉ cho soạn từ toàn văn PMC
(`"nguon": "toan_van_pmc"`) khi bản ghi KHÔNG có abstract ⇒ các bài này mang tóm tắt rút từ một abstract vô dụng.

**Quyết định của bác sĩ (13/11/2026, nguyên văn):** «Luật tóm tắt máy: có mở rộng cho abstract guideline».

**Cách vá (`tools/tom_tat_endnote_vi.py`).**
- Trường siêu dữ liệu mới `abstract_khong_noi_dung` (LÝ DO, không in). Bài CÓ abstract + `"nguon": "toan_van_pmc"` chỉ
  được nhận khi khai lý do này; không khai ⇒ vẫn ⛔ như cũ.
- Chốt số đối chiếu với toàn văn PMC truy cập mở (`PMID-<n>_PMC<id>.xml` trong kho), không phải abstract; kho thiếu tệp
  PMC ⇒ ⛔. Bản Chrome/Unpaywall vẫn không phải nguồn.
- Nhãn riêng «ℹ️ TÓM TẮT MÁY TỪ TOÀN VĂN PMC (abstract gốc không nêu nội dung khuyến cáo)» và dòng chân `CHAN_MAY_PMC_ABS`;
  abstract gốc giữ nguyên dưới dấu phân cách.
- `kiem_kho_tom_tat`: lý do rỗng ⇒ lỗi; lý do mà «nguon» không phải `toan_van_pmc` ⇒ lỗi.

**Phạm vi thực tế lúc vá.** Trong 6 bài nêu trên chỉ ADA chương 5 có toàn văn PMC (PMC12690188). ASCO (JCO — Cloudflare chặn
truy cập tự động) và AUA (J Urol — điều khoản cấm công cụ AI) không có bản máy được phép đọc ⇒ giữ tóm tắt từ abstract kèm
ghi chú «cần đọc toàn văn».

**Kiểm hồi quy.** `tools/test_tom_tat_may_abstract_khong_noi_dung_20261113.py` (7 ca, ngoại tuyến) + 12 ca cũ của
`test_tom_tat_may_toan_van_pmc_20261020.py` vẫn xanh. Đột biến 6/6 đỏ đúng chỗ: bỏ điều kiện lý do (hai chiều), nhãn không phân
biệt, bỏ kiểm lý do rỗng, bỏ kiểm sai nguồn, đối chiếu số theo abstract thay vì toàn văn.
