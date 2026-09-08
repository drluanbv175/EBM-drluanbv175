---
name: paper-lookup
description: Tra cứu bài báo y khoa qua API MIỄN PHÍ (PubMed E-utilities, Crossref, Europe PMC) — tìm theo PICO/từ khóa/MeSH, phân giải và xác minh PMID/DOI, lấy metadata gốc. Dùng khi cần tìm bài cho một câu hỏi, kiểm một PMID/DOI có thật, hoặc lấy thông tin trích dẫn. LUÔN trả PMID/DOI; KHÔNG bịa bài; không tra ra → nói rõ, không "đoán".
---

<!-- EBM-VN-GUARD -->
> **⚕️ Bản điều chỉnh cho bác sĩ EBM ngoại trú (Việt Nam).** Skill gốc của K-Dense Inc. đã được chỉnh để phù hợp quy ước trong `CLAUDE.md` của người dùng.
>
> **QUY TẮC BẮT BUỘC — đọc trước, GHI ĐÈ mọi hướng dẫn tiếng Anh bên dưới:**
> 1. **Ngôn ngữ:** Mọi trao đổi và đầu ra cho người dùng viết bằng **tiếng Việt** (giữ thuật ngữ y khoa tiếng Anh khi cần; tên thuốc theo INN).
> 2. **Disclaimer:** Mọi đầu ra y khoa kết thúc bằng câu **"⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng."**
> 3. **Nguồn:** Mọi nhận định/khuyến cáo phải **ghi nguồn (PMID/DOI)**; không có nguồn thì không khẳng định. **Tuyệt đối không bịa dữ liệu hay nguồn.**
> 4. **Không PII:** **KHÔNG** lưu hay tạo thông tin định danh bệnh nhân (tên, ngày sinh, số hồ sơ, địa chỉ...). Dùng mã ẩn danh.
> 5. **Chỉ nguồn miễn phí:** Khi tra cứu y văn dùng **PubMed E-utilities** (miễn phí, không cần API key) và các CSDL mở. **KHÔNG** dùng dịch vụ trả phí (parallel.ai, Perplexity, OpenRouter...). Nếu một lệnh gốc gọi `parallel-cli`/Perplexity, thay bằng `python scripts/pubmed_lookup.py "..."` hoặc REST miễn phí.
> 6. **Bối cảnh:** Bỏ qua phần chỉ phục vụ ngữ cảnh dược phẩm/pháp lý Mỹ (HIPAA/FDA/ICH-CSR) khi không liên quan ngoại trú VN; ưu tiên guideline quốc tế mới nhất rồi hiệu chỉnh theo Bộ Y tế VN.
>
> Phần kỹ thuật chi tiết (template, script, references) giữ nguyên tiếng Anh nhưng phải tạo ra **đầu ra tiếng Việt** theo các quy tắc trên.


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
