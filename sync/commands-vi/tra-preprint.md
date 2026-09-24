---
description: "Tra bản thảo tiền in y sinh trên medRxiv/bioRxiv — chứng cứ mới nhất nhưng CHƯA bình duyệt"
---

Tra preprint về: **$ARGUMENTS**

1. Nạp công cụ — tên KHÁC NHAU theo nơi chạy (đo 24/09/2026), thử lần lượt, dùng bộ nào nạp được:
   - Máy có plugin `bio-research` (Mac): ToolSearch `select:mcp__plugin_bio-research_biorxiv__search_preprints,mcp__plugin_bio-research_biorxiv__get_preprint,mcp__plugin_bio-research_biorxiv__search_published_preprints`
   - Connector claude.ai (phiên Cloud): ToolSearch `select:mcp__bioRxiv__search_preprints,mcp__bioRxiv__get_preprint,mcp__bioRxiv__search_published_preprints`
   Nếu công cụ nạp được nhưng lời gọi DỮ LIỆU lỗi (đo 24/09 trên Cloud: `get_categories` chạy, còn
   `search_preprints` trả «Internal error» ở 3/3 lần — máy chủ MCP không kéo được dữ liệu bioRxiv),
   thử lại MỘT lần; vẫn lỗi thì báo thẳng **«kênh preprint đang hỏng phía máy chủ connector — CHƯA tra
   được»**. TUYỆT ĐỐI không đổi sang trả lời «không có preprint nào», và không tự nhớ preprint từ trí nhớ.
   Đường thay thế có kiểm được (nêu rõ đây là kênh khác, độ phủ khác): Europe PMC `SRC:PPR` qua engine
   (chỉ khi mạng cho phép — Cloud «Trusted» chặn `www.ebi.ac.uk`), hoặc PubMed MCP (chỉ phủ phần
   preprint NIH đã đưa vào PubMed).
2. Lưu ý giới hạn thật của API: chỉ lọc được theo KHOẢNG NGÀY và CHUYÊN MỤC, không tìm theo từ khoá —
   nên nêu rõ cho bác sĩ nếu không tìm được đúng chủ đề, đừng giả vờ đã tìm theo từ khoá.
3. Với mỗi bài: DOI · ngày đăng · đã được đăng chính thức chưa (`search_published_preprints`).
4. **CẢNH BÁO BẮT BUỘC nêu ở đầu kết quả**: preprint CHƯA qua bình duyệt, không dùng để đổi thực hành lâm sàng.
