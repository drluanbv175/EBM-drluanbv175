---
description: "Tra nhanh PubMed/PMC theo chủ đề, lấy PMID/DOI và tóm tắt — dùng khi cần tra gọn, không cần thẩm định GRADE"
---

Tra y văn về: **$ARGUMENTS**

1. Nạp công cụ: ToolSearch với `select:mcp__plugin_healthcare_PubMed__search_articles,mcp__plugin_healthcare_PubMed__get_article_metadata,mcp__plugin_healthcare_PubMed__find_related_articles`
2. Ưu tiên bằng chứng mạnh: guideline → tổng quan hệ thống/phân tích gộp → RCT → quan sát. Nêu rõ loại thiết kế của từng bài.
3. Mỗi bài BẮT BUỘC kèm PMID (và DOI nếu có). KHÔNG liệt kê bài không xác minh được.
4. Nếu câu hỏi là để RA QUYẾT ĐỊNH cho một bệnh nhân → chuyển sang agent `tra-cuu-chung-cu` rồi `tham-dinh-grade-nnt`,
   vì lệnh này chỉ tra, không thẩm định chất lượng chứng cứ.
5. Kết thúc bằng "Cần bác sĩ kiểm chứng".
