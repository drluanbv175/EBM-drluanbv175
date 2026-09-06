---
name: citation-management
description: Quản lý & kiểm chứng trích dẫn học thuật — phân giải PMID/DOI bắt buộc qua API miễn phí (PubMed/Crossref), đối chiếu metadata, bắt trích dẫn ma & citation washing, cảnh báo retracted/trùng, xuất danh mục Vancouver/ICMJE/AMA/BibTeX. Dùng khi soạn/soát tài liệu tham khảo, trước khi nộp bản thảo. KHÔNG bao giờ "tin" trích dẫn chưa phân giải; không bịa trích dẫn thay thế.
---

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
