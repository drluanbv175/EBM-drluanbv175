# 04/10/2026 — Cặp PMID–DOI của cùng một mục trỏ HAI bài khác nhau; cổng không thấy (BH156)

**Phát hiện:** khi đọc toàn văn mục «apply», bản ghi Europe PMC của PMID 41485807 (KDIGO 2026 thiếu máu/CKD) mang DOI
khác với DOI ghi trong mục. Quét toàn kho bằng chính bộ tách mục của cổng (chỉ đọc).

**Số đo (04/10/2026, NCBI esummary và Europe PMC cho cùng kết quả):** 72 dashboard, 1164 mục ghi cả PMID lẫn DOI,
637 PMID duy nhất, xác minh được cả 637. Kết quả: 1153 khớp, **10 lệch** (3 mục `apply`), 1 «chưa so được» (PMID
10023943, CIBIS-II 1999: PubMed không ghi DOI).

**Vì sao cổng không thấy:** `verify_dashboard.py --online` xác minh TỪNG định danh có tồn tại (PMID qua PubMed, DOI qua
Crossref) nên cả hai đều «✓». Không bước nào hỏi hai định danh có cùng một bài không. Người đọc bấm PMID và bấm DOI
sẽ tới hai bài khác nhau, và không ai biết số liệu của mục được lấy từ bài nào.

**Nguyên nhân (đối chiếu tiêu đề, nội dung và references của từng mục):**
- **5 mục** mang PMID đúng (tiêu đề, nội dung và references khớp PMID) nhưng DOI thuộc một bài nằm trong DANH MỤC THAM
  KHẢO của chính bài đó: TimMach ITEM-06 (bài ESC 2026 về VĐV nhi ↔ BMJ 1999), ITEM-11 (COMPASS 2026 ↔ JACC 2019),
  ITEM-12 (ESH 2026 ↔ IPCC 2023), CapCuuBanau ITEM-01 và NhiKhoa_SocPhanVe ITEM-05 (IAP 2026 ↔ WAO 2020). Đây đúng là
  lớp lỗi engine đã vá ngày 14/08 (`app/sources/pubmed.py::_own_article_doi`, PMID 30267080). Các dashboard này đều mang
  ngày 09/06–06/07, tức là dữ liệu sót lại từ trước bản vá. Tuy vậy lỗi VẪN SỐNG ở 4 script trong `sync/skills` duyệt
  `.//ArticleId`:
  - `nghien-cuu-ebm-tong-hop/scripts/pubmed_search.py` ghi đè DOI ở mỗi vòng lặp ⇒ trả DOI của tài liệu tham khảo CUỐI
    cho MỌI bài có ReferenceList;
  - 3 script K-Dense lấy DOI đầu tiên rồi dừng ⇒ chỉ sai khi bản ghi không có DOI ở ArticleIdList.
- **3 mục** có DOI của một bài khác cùng tạp chí hoặc cùng chủ đề: ThieuMau ITEM-01 (DOI một bài nhi khoa CKD có PMID
  liền kề), DauManTinh ITEM-04 (một bài Pain khác), BenhDMCanh ITEM-01 (DOI báo cáo bằng chứng USPSTF đi cùng PMID bản
  khuyến cáo).
- **1 mục** là bản đồng xuất bản: HopNhat ITEM-30, guideline ESO về huyết khối tĩnh mạch não, có bản ở Eur J Neurol và
  bản ở Eur Stroke J.
- **1 mục** có PMID trỏ một THƯ bạn đọc (Letter/Comment) cùng tên thử nghiệm: COPD ITEM-09, PMID 22150046 ↔ thử nghiệm
  azithromycin NEJM 2011 (PMID đúng là 21864166).

**Vá (PR này):**
1. Cổng lấy DOI mà CHÍNH PubMed ghi cho PMID (esummary `articleids`/`elocationid`; Europe PMC khi NCBI chặn), so với DOI
   của mục (không phân biệt hoa/thường), ở bước 3b′:
   - lệch ⇒ cảnh báo; `--strict-sources` ⇒ lỗi cứng (cùng khuôn luật tráo trích dẫn và luật lệch năm);
   - thông điệp nêu rõ khi PMID trỏ thư/bình luận/đính chính, và khi hai DOI là hai phiên bản của cùng một tổng quan
     Cochrane;
   - PubMed không ghi DOI ⇒ «chưa so được» (cảnh báo, không bao giờ in thành khớp).
   - API `verify_pmid_online` giữ nguyên bộ ba trả về, `so_xac_minh_nguon.py` không đổi.
2. Bốn bộ rút XML trong `sync/skills` chỉ đọc `PubmedData/ArticleIdList` rồi `ELocationID` hợp lệ của chính bài.
3. Dạy agent: `SKILL.md` của `cap-nhat-chung-cu-y-khoa` (mục (a) và khối 🔴), `CLAUDE.md` §6.3.

**Kiểm:**
- `tools/test_verify_dashboard_cap_pmid_doi_20261004.py` (25 test, gồm chạy `main()` thật với mạng giả);
  `tools/test_doi_chinh_bai_pubmed_20261004.py` (7 test, bản cũ đỏ 6/7).
- Đột biến cổng 13/13 và BH156 5/5 đỏ đúng chỗ, phục hồi xanh.
- Đo lại trên dữ liệu thật bằng hàm mới: 1153/10/1 như trên, không báo nhầm.

**Việc của bác sĩ (máy KHÔNG sửa dashboard):** bảng đề xuất sửa 10 mục ở PR. Ở mỗi mục, định danh nào khớp
nội dung/references thì giữ, định danh kia sửa theo. Khi PR này được gộp, 8 dashboard chứa cặp lệch sẽ bị
`--strict-sources` chặn cho tới khi sửa xong (HopNhat là bản đồng xuất bản: chọn một bản, ghi đủ cặp của bản đó).
