---
name: citation-management
description: Quản lý & kiểm chứng trích dẫn học thuật — phân giải PMID/DOI bắt buộc qua API miễn phí (PubMed/Crossref), đối chiếu metadata, bắt trích dẫn ma & citation washing, cảnh báo retracted/trùng, xuất danh mục Vancouver/ICMJE/AMA/BibTeX. Dùng khi soạn/soát tài liệu tham khảo, trước khi nộp bản thảo. KHÔNG bao giờ "tin" trích dẫn chưa phân giải; không bịa trích dẫn thay thế.
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


# Skill: Quản lý & kiểm chứng trích dẫn (citation-management)

Dùng cho `kiem-chung-trich-dan`, `binh-duyet`, `thu-thu-tai-lieu`, `tong-quan-y-van`. Cổng liêm chính chống trích dẫn ma.

## Nguyên tắc liêm chính (4 trụ cột)
- **KHÔNG tin trích dẫn chưa phân giải được.** PMID/DOI không tra ra → 🔴 NGHI NGỜ MA; KHÔNG "sửa cho hợp lý", KHÔNG bịa trích dẫn thay thế.
- Phân giải qua **API miễn phí**: PubMed E-utilities (PMID), Crossref (DOI). Connector lỗi → PARTIAL, không tuyên bố "đã xác minh".

## Quy trình (mỗi tài liệu)
**BƯỚC 0 — Tiền đề:** kiểm connector PubMed/Crossref; xác định phạm vi (chỉ định danh hay cả nội dung trích).
1. **Phân giải định danh:** PMID qua PubMed esummary; DOI qua Crossref `/works/{DOI}` → metadata gốc (tác giả, tiêu đề, tạp chí, năm, tập/số/trang).
2. **Đối chiếu metadata:** so tác giả·năm·tạp chí·tiêu đề trong bản thảo với gốc → khớp/lệch (nêu trường lệch).
3. **Kiểm nội dung (citation washing):** câu khẳng định trong bài có ĐÚNG điều bài báo nói không; bắt gán kết luận bài không có, trích sai chiều/quá tầm.
4. **Trùng & rút bài:** cảnh báo retracted/expression of concern/trùng.
5. **Xuất danh mục:** **Vancouver/ICMJE** (mặc định y khoa), hoặc AMA/APA/BibTeX; đánh số nhất quán với chỗ trích trong văn bản.

## Định dạng Vancouver/ICMJE (mẫu)
> Tác giả AA, Tác giả BB. Tiêu đề bài. Tên tạp chí viết tắt. Năm;Tập(Số):trang đầu-cuối. doi:....
- ≤6 tác giả: liệt kê hết; >6: 6 tác giả đầu + "et al."

## Mẫu đầu ra
```
| # | Trích dẫn trong bài | Trạng thái ✅/🟡/🔴 | Ghi chú | PMID/DOI đã xác minh |
DANH SÁCH 🔴 BẮT BUỘC xử lý (chặn "sẵn sàng nộp"): ____
Danh mục tham khảo sạch (Vancouver/ICMJE): ____
[⚠ PARTIAL — connector PubMed/Crossref không sẵn]
```
Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG viết lại nội dung khoa học; KHÔNG bịa trích dẫn thay thế khi thiếu — nêu "cần bổ sung nguồn". Tìm bài mới → `paper-lookup`.
