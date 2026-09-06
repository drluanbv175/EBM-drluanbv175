---
name: paper-lookup
description: Tra cứu bài báo y khoa qua API MIỄN PHÍ (PubMed E-utilities, Crossref, Europe PMC) — tìm theo PICO/từ khóa/MeSH, phân giải và xác minh PMID/DOI, lấy metadata gốc. Dùng khi cần tìm bài cho một câu hỏi, kiểm một PMID/DOI có thật, hoặc lấy thông tin trích dẫn. LUÔN trả PMID/DOI; KHÔNG bịa bài; không tra ra → nói rõ, không "đoán".
---

# Skill: Tra cứu bài báo qua API miễn phí (paper-lookup)

Dùng cho `tra-cuu-chung-cu`, `thu-thu-tai-lieu`, `tong-quan-y-van`, `kiem-chung-trich-dan`.

## Nguyên tắc liêm chính (4 trụ cột)
- **CHỈ nguồn/API miễn phí**, không backend trả phí.
- **KHÔNG bịa bài/PMID/DOI.** Một bài chỉ được nêu sau khi phân giải được định danh thật + metadata khớp. Không tra ra → ghi rõ, KHÔNG ghép tên/tiêu đề cho "nghe hợp lý".
- Connector lỗi → đánh dấu **PARTIAL**, không kết luận "không có bài".

## API MIỄN PHÍ dùng được (không cần khóa; nên thêm `tool=`, `email=` cho NCBI)
- **PubMed E-utilities** — `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
  - `esearch.fcgi?db=pubmed&term=...&retmax=...` → danh sách PMID
  - `esummary.fcgi?db=pubmed&id=PMID` → metadata tóm tắt
  - `efetch.fcgi?db=pubmed&id=PMID&rettype=abstract` → abstract
  - (Khuyến nghị ≤3 req/giây nếu không có API key; có key thì cao hơn.)
- **Crossref** — `https://api.crossref.org/works?query=...` hoặc `/works/{DOI}` → metadata theo DOI (thêm `mailto=` polite pool).
- **Europe PMC** — `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=...&format=json` → bao gồm PMC toàn văn mở; trường `pmid`,`doi`,`isOpenAccess`.

## Quy trình
**BƯỚC 0 — Tiền đề:** kiểm connector web/fetch — thiếu → PARTIAL. Xác định chế độ: TÌM (từ câu hỏi) hay PHÂN GIẢI (từ PMID/DOI sẵn).
1. **Dựng truy vấn:** từ khóa tự do + đồng nghĩa + MeSH (đánh dấu nếu MeSH chưa kiểm trong MeSH Browser); ghép AND/OR; nêu bộ lọc (năm/loại bài/ngôn ngữ).
2. **Gọi API:** PubMed esearch→esummary (chính); bổ sung Europe PMC (toàn văn mở) + Crossref (theo DOI). Ghi **ngày tra** + CSDL.
3. **Xác minh:** với mỗi bài lấy metadata gốc (tác giả, tiêu đề, tạp chí, năm, tập/số/trang, PMID, DOI); loại bài không phân giải được; cảnh báo **retracted** (PubMed publication type "Retracted Publication"/RetractionWatch nếu tra được).
4. **Xếp hạng:** theo thứ bậc chứng cứ (guideline→SR/MA→RCT→cohort→khác) + độ mới.

## Mẫu đầu ra
```
Truy vấn + CSDL + ngày tra: ____
| # | Tác giả (năm) | Tiêu đề | Loại NC | PMID | DOI | Toàn văn mở? |
[⚠ PARTIAL — connector lỗi / CSDL chưa tra: ____]
```
Mỗi bài kèm PMID/DOI đã xác minh. Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG thẩm định GRADE/chất lượng (→ thẩm định/critical appraisal); KHÔNG soát nội dung trích đúng/sai (→ `citation-management`). Chỉ TÌM + PHÂN GIẢI + XÁC MINH định danh.
