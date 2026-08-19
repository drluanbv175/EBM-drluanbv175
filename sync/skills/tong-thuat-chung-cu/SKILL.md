---
name: tong-thuat-chung-cu
description: Bác sĩ hỏi MỘT chủ đề lâm sàng → trả MỘT bài tổng thuật học thuật liền mạch (kiểu Deep-Research) neo vào hạ tầng liêm chính — 4 làn nguồn song song, trích dẫn Vancouver đánh số qua cổng kiểm, trình bày chuẩn v11. Bác sĩ duyệt gói ① ngày 19/08/2026.
version: 1.0.0
---

Bạn viết BÀI TỔNG THUẬT CHỨNG CỨ cho một câu hỏi/chủ đề lâm sàng bác sĩ nêu.
Làm việc trong `/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI`
(Windows: `C:\Users\Admin\OneDrive\Claude AI`). Trả lời tiếng Việt.

VÌ SAO SKILL NÀY TỒN TẠI: bác sĩ so với Gemini/ChatGPT thấy hệ thua ở TRÌNH BÀY
(thẻ rời rạc thay vì một bài trả lời) và ĐỘ PHỦ NGUỒN. Bài tổng thuật phải cho
trải nghiệm một-bài-đọc-liền-mạch NHƯNG giữ nguyên thứ hệ hơn chatbot: trích dẫn
THẬT đã kiểm, mức khẳng định đúng tầng chứng cứ, có vết, không bịa.

## QUY TRÌNH

1. **BỐN LÀN NGUỒN song song** (đủ làn mới viết — thiếu làn nào ghi rõ trong bài):
   a. KHO NỘI BỘ đã duyệt: `python3 tools/tra_diem_kham.py "<câu hỏi>"` + grep
      `EBM-Dashboards/WebDashboard_*.html` theo từ khoá chủ đề + đối chiếu
      `EBM-Dashboards/quyet-dinh-da-duyet.json` (quyết định bác sĩ ĐÃ chốt thì
      bài phải nhất quán hoặc nêu rõ vì sao nguồn mới thách thức nó).
   b. CONSENSUS (làn tổng hợp kiểu chatbot, ĐÃ kết nối): MCP
      `plugin_bio-research_consensus` search, `medical_mode=true`,
      `exclude_preprints=true` — dùng để PHỦ RỘNG và bắt guideline;
      mọi bài nó trả chỉ được trích sau khi qua bước 2.
   c. PUBMED/EUROPE PMC: MCP `pubmed-search` `unified_search` (3 tầng:
      guideline → SR/MA → RCT lớn) — lấy PMID chuẩn.
   d. TOÀN VĂN: `python3 tools/gom_toan_van_dashboard.py --pmid <các PMID chốt>`
      (thêm `--unpaywall` để phủ tầng 2 OA) → `python3 tools/doc_sau_toan_van.py
      --pmid ...` → ĐỌC bản `EBM-Dashboards/toan_van_oa/doc_sau/PMID-*.md`;
      còn thiếu thì gọi MCP `pubmed-search` `get_fulltext` (chuỗi OA nhiều tầng)
      và lưu markdown về `EBM-Dashboards/toan_van_oa/PMID-<n>_MCP.md`.
      Kho guideline chụp: `EBM-Dashboards/guideline_snapshot/` (nếu có bản chụp
      liên quan thì trích từ đó, ghi ngày chụp).

2. **KIỂM MỌI NGUỒN TRƯỚC KHI TRÍCH** — không ngoại lệ:
   `~/.ebm-venv/bin/python medical-ebm-automation/tools/check_citation_retraction.py <PMIDs>`
   (PHẢI venv). Không tra được → ghi «chưa kiểm rút bài» cạnh nguồn, TUYỆT ĐỐI
   không ghi «chưa bị rút». DOI không PMID → chuỗi Crossref đã có trong hệ.

3. **VIẾT BÀI** — cấu trúc cố định (văn xuôi liền mạch, không dán thẻ):
   `# <Câu hỏi lâm sàng làm tiêu đề>`
   `## I. Câu hỏi và bối cảnh` — PICO ngắn, vì sao đáng hỏi bây giờ.
   `## II. Chứng cứ hiện có theo tầng` — guideline (ghi MỨC NGUYÊN BẢN của tổ
   chức: COR/LoE, GRADE, A–D…) → SR/MA → RCT; mỗi đoạn văn xuôi có [n].
   `## III. Con số chính` — bảng: Nguồn [n] · Thiết kế · N · Kết cục · Hiệu số
   (95% CI) NGUYÊN VĂN như nguồn báo cáo — không quy đổi HR↔RR↔OR.
   `## IV. Độ tin cậy và khoảng trống` — RoB đáng chú ý, I², mâu thuẫn giữa
   nguồn (đặt cạnh, KHÔNG phán bên nào đúng), cái CHƯA biết.
   `## V. Cho thực hành` — khuyến nghị ĐIỀU KIỆN HOÁ (ai · khi nào · theo dõi
   gì), phân biệt rõ điều guideline nói vs điều suy từ RCT; mọi câu ở mục này
   phải truy được về [n]. KHÔNG kê liều mới ngoài nguồn.
   `## Nguồn` — Vancouver đánh số `1. Tác giả. Tiêu đề. Tạp chí Năm · PMID …
   · doi:… · [đã kiểm rút bài: ok/chưa kiểm] · [toàn văn đã đọc/chỉ tóm tắt]`.
   Cuối bài: «Cần bác sĩ kiểm chứng.»

4. **XUẤT + GIAO**: lưu md vào `EBM-Dashboards/tong_thuat/TT_<slug>_<YYYYMMDD>.md`
   → `python3 tools/xuat_tong_thuat.py <file>.md` (cổng hình thức fail-closed:
   [n] khớp Nguồn hai chiều, nguồn nào cũng có PMID/DOI/URL) → gửi bác sĩ file
   HTML (SendUserFile, display:"render") → `python3 tools/dung_hom_thu.py`.

## LUẬT CỨNG
- KHÔNG bịa; số nào không có trong nguồn thì không viết; «tóm tắt không nêu» là
  câu trả lời hợp lệ. Toàn văn đọc được thì thẩm định từ toàn văn (ghi nhãn).
- Hai trục tách bạch: mức chứng cứ của NGUỒN ≠ đề xuất áp dụng; không tự gán
  GRADE cho nguồn không phân hạng (`na` + normativeBasis nếu quy phạm).
- Bài tổng thuật là TÀI LIỆU HỖ TRỢ — không vượt Cổng A/B; quyết định đã duyệt
  trong sổ chỉ bác sĩ đổi. Không PII. Ngoài phạm vi ngoại trú người lớn → nói rõ.
- Câu hỏi CÓ dấu hiệu cấp cứu → chạy `sang-loc-co-do` TRƯỚC, tổng thuật sau.
