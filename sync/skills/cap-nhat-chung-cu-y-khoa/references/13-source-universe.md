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

## Thực thi THẬT trên máy này — đo ngày 13/08/2026

Doctrine ở trên là mục tiêu. Dưới đây là những gì hệ **thực sự** chạm tới, đã đo bằng lời gọi thật.

### Kênh đang chạy

| Lớp | Cơ chế | Trạng thái |
|---|---|---|
| Định danh | PubMed · Europe PMC · Crossref · OpenAlex | 9 connector nối trong `app/sources/__init__.py` |
| Tạp chí/hiệp hội qua RSS | 26 feed | NEJM · JAMA · The BMJ · JACC · Gut · Thorax · Ann Rheum Dis (EULAR) · Diabetologia (EASD) · CDC MMWR · ECDC · BJGP · Heart… |
| **Tạp chí qua PubMed `[ta]`** | nhóm **"Tạp chí hàng đầu"** | NEJM · Lancet · JAMA · BMJ · Annals of Internal Medicine |
| **Khuyến cáo qua PubMed** | nhóm **"Tổng quan hệ thống & khuyến cáo"** | Cochrane Database Syst Rev · NICE · USPSTF |
| An toàn thuốc | FDA MedWatch · FDA Recalls · MHRA DSU · openFDA (FAERS) | 4 kênh |
| Registry | ClinicalTrials.gov | nối |

### Vì sao một số nguồn phải đi vòng qua PubMed

Đã kiểm thật 10 feed ứng viên ngày 13/08/2026 — **tất cả đều bị chặn**:
Lancet 403 · Lancet Infect Dis 403 · Annals of Internal Medicine 403 · Cochrane 403 ·
NICE 403 · CHEST 403 · USPSTF 404 · Circulation 404 · Diabetes Care 404 · Blood 404.

Nhà xuất bản chặn truy cập tự động. Nên **không thêm RSS cho các nguồn này** — thay vào đó dùng
truy vấn PubMed theo trường `[ta]` (journal title abbreviation) và `[cn]` (corporate author), đã
kiểm chạy thật. Đừng "sửa" bằng cách thêm lại RSS: sẽ chỉ ghi thêm lỗi vào Source Log.

### Lọc nhiễu cảnh báo cơ quan quản lý

Feed `fda_recalls` trả **toàn bộ** thu hồi của FDA — thực phẩm, thiết bị y tế, mỹ phẩm, thức ăn
thú cưng, lẫn thuốc. Trước 13/08 tất cả bị gắn nhãn "An toàn thuốc": trong 40 mục của bản tin
13/08 chỉ ~30 liên quan thuốc, 4 là thiết bị, 6 là thực phẩm/mỹ phẩm/thú cưng.

`app/sources/rss_feed.py::phan_loai_canh_bao()` nay phân loại **từng mục** theo đường dẫn rồi tới
từ khoá, tách thành ba nhãn: `An toàn thuốc` · `An toàn thiết bị y tế` · `Thu hồi thực phẩm`.
Thiết bị/thực phẩm **không bị vứt bỏ**, chỉ tách khỏi báo cáo An toàn thuốc (bơm insulin rò rỉ vẫn
liên quan bệnh nhân đái tháo đường).

**Nguyên tắc an toàn của bộ lọc: KHÔNG CHẮC thì giữ là THUỐC.** Bỏ sót một cảnh báo thuốc nguy
hiểm hơn nhiều so với để lọt một mục nhiễu. Đã có phép thử chống bỏ sót cho domperidone,
morphine, valsartan/NDMA và montelukast — cả bốn giữ nguyên trong nhóm thuốc.
