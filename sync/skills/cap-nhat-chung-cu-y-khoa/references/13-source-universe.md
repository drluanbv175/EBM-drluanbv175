# 13. Source universe cho cập nhật chứng cứ lâm sàng

## Mục tiêu

Tìm rộng đủ lớp nguồn để bác sĩ có chứng cứ tốt nhất có thể truy nguyên, nhưng không tự xem mọi nguồn tìm được là khuyến cáo áp dụng.

## Ma trận nguồn bắt buộc

1. **Bibliographic core / định danh:** PubMed/MEDLINE, Europe PMC, Crossref, OpenAlex. Dùng để tìm bài, kiểm PMID/DOI, năm, tạp chí và metadata nhà xuất bản.
2. **Guideline, HTA, cơ quan/hiệp hội chính thức:** Cochrane, NICE, USPSTF, WHO, CDC, FDA, EMA, MHRA, ACC/AHA, ESC, ADA/EASD, KDIGO, GINA, GOLD, IDSA, EULAR/ACR, ACG/AGA/ASGE, AASLD/EASL, ASH/ISTH, AGS, ATS/ERS/BTS, Bộ Y tế/kcb.vn khi có tài liệu chính thức.
3. **Tạp chí uy tín cao:** NEJM, Lancet family, JAMA/JAMA Network, The BMJ, Annals of Internal Medicine, Nature Medicine, Circulation, JACC, Diabetes Care, Kidney International, Gut, CHEST, Blood và tạp chí chuyên khoa chính thức liên quan.
4. **Trial registry:** ClinicalTrials.gov, WHO ICTRP, EU Clinical Trials Register, ISRCTN. Dùng để phát hiện nghiên cứu đang/chưa công bố hoặc posted results; registry không có kết quả peer-reviewed không đủ để đổi thực hành.
5. **An toàn thuốc:** openFDA, FDA MedWatch/recalls, EMA/PRAC, MHRA Drug Safety Update, DailyMed, Drugs@FDA, LactMed, WHO VigiAccess khi phù hợp. Ưu tiên safety communication/label chính thức.
6. **Retraction/integrity:** PubMed publication type/comment, Crossmark/publisher page, Retraction Watch khi có quyền truy cập. Mọi paper quan trọng phải được kiểm trạng thái rút bài/withdrawal/expression of concern khi có công cụ.
7. **Full text/citation context:** Unpaywall, PubMed Central, publisher full text, Semantic Scholar/citation graph. Dùng để đọc/định vị toàn văn hợp pháp và bối cảnh trích dẫn; không thay thế nguồn gốc.

## Luật fail-closed

- Thiếu bibliographic core hoặc không truy được PMID/DOI/URL chính thức cho item thay đổi thực hành -> không được gọi là đã xác minh.
- Thiếu guideline/HTA/hiệp hội chính thức khi câu hỏi là khuyến cáo điều trị/chẩn đoán -> giữ `REVIEW_REQUIRED`.
- Thiếu lớp an toàn thuốc khi nội dung có thuốc, người cao tuổi, CKD, thai kỳ, đa thuốc hoặc cảnh báo ADR -> không được chốt hành động kê đơn.
- Trial registry, preprint, consensus, citation graph và full-text helper là **discovery-only** cho tới khi truy ngược được paper/guideline/label chính thức.
- Không thêm RSS/API chưa xác minh chính thức. Nếu endpoint không chắc, dùng PubMed/Europe PMC/Crossref/OpenAlex hoặc trang chính thức và ghi rõ đường truy nguyên.

## Cách ghi trong dashboard/câu trả lời

- Ghi ngày tìm kiếm và các lớp nguồn đã dùng.
- Với mỗi item chính: nêu PMID/DOI/official URL, tên nguồn, năm/phiên bản, population và grading gốc nếu có.
- Nếu source health `PARTIAL/FAIL`, nói rõ lớp nguồn nào thiếu; không diễn giải là "không có cập nhật".
- Luôn giữ nhãn: `Cần bác sĩ kiểm chứng.`
