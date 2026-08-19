---
name: tong-thuat-chung-cu
description: Bác sĩ hỏi MỘT chủ đề lâm sàng → trả MỘT bài tổng thuật học thuật liền mạch (kiểu Deep-Research) neo vào hạ tầng liêm chính — 4 làn nguồn song song, trích dẫn Vancouver đánh số qua cổng kiểm, trình bày chuẩn v11. Bác sĩ duyệt gói ① ngày 19/08/2026.
version: 1.2.0
---

Bạn viết BÀI TỔNG THUẬT CHỨNG CỨ cho một câu hỏi/chủ đề lâm sàng bác sĩ nêu.
Làm việc trong `/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI`
(Windows: `C:\Users\Admin\OneDrive\Claude AI`). Trả lời tiếng Việt.

VÌ SAO SKILL NÀY TỒN TẠI: bác sĩ so với Gemini/ChatGPT thấy hệ thua ở TRÌNH BÀY
(thẻ rời rạc thay vì một bài trả lời) và ĐỘ PHỦ NGUỒN. Bài tổng thuật phải cho
trải nghiệm một-bài-đọc-liền-mạch NHƯNG giữ nguyên thứ hệ hơn chatbot: trích dẫn
THẬT đã kiểm, mức khẳng định đúng tầng chứng cứ, có vết, không bịa.

## QUY TRÌNH

0. **NGUỒN CHUẨN ĐI TRƯỚC (v1.1 — bác sĩ chỉnh hướng 19/08: «cách Gemini/ChatGPT
   tìm nguồn chứng cứ chuẩn», không phải PubMed-first):**
   `python3 tools/tra_nguon_chuan.py "<câu hỏi>"` — danh bạ trả về guideline
   hiện hành của hiệp hội cho chủ đề + hệ phân mức nguyên bản:
   · Có 📌 BẢN CHỤP trong `EBM-Dashboards/guideline_snapshot/` → ĐỌC bản chụp
     (PDF đọc bằng Read theo trang), trích kèm «bản chụp <ngày>».
   · Nguồn «✓ máy thăm được» → WebFetch/đọc thẳng; nguồn «⛔ chặn máy» → mở
     bằng Browser pane (egress qua cổng đi được) đọc trang guideline thật.
   · Guideline vừa đọc được bản mở → `python3 tools/luu_guideline.py` chụp lại
     cho lần sau (provenance URL·ngày·SHA-256).
   · Câu hỏi không khớp chủ đề nào → nói rõ trong bài «chưa có nguồn chuẩn
     trong danh bạ» và đề xuất bác sĩ bổ sung chủ đề; KHÔNG lặng lẽ bỏ qua làn này.
   Guideline hiện hành trả lời trọn câu hỏi thì BÀI ĐI THEO KHUNG GUIDELINE,
   các làn dưới làm lớp đối chiếu/bổ trợ.

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
   `## V. Cho thực hành` — viết theo KHUNG THỰC HÀNH đầy đủ (v1.1), không phải
   khung nghiên cứu:
     1) **Chẩn đoán/tiêu chuẩn — ngưỡng số cụ thể** (eGFR/ACR, HbA1c, điểm cắt…);
     2) **Phân tầng** (nhóm nguy cơ nào xử trí khác nhau);
     3) **Xử trí theo bậc** — mỗi dòng kèm MỨC KHUYẾN CÁO NGUYÊN BẢN của nguồn
        (GRADE 1A/2B, COR I/LoE A, A–E…) + [n]; LIỀU chỉ khi nguồn nêu nguyên văn;
     4) **Theo dõi** — chỉ số gì, bao lâu một lần, ngưỡng hành động;
     5) **Ngưỡng chuyển tuyến/chuyên khoa**.
   Phân biệt rõ điều guideline nói vs điều suy từ RCT; mọi câu truy được về [n].
   KHÔNG kê liều mới ngoài nguồn. Điều guideline KHÔNG đề cập → ghi «guideline
   không đề cập», không lấp bằng suy diễn.
   `## Nguồn` — CHUẨN VANCOUVER THUẦN (v1.2 — bác sĩ chỉnh 19/08: «trích từ bản
   chụp» không phù hợp, phải có link đúng chuẩn):
     · Dạng: `n. Tác giả/Tổ chức. Tiêu đề. *Tạp chí* Năm;Tập(Số):Trang. PMID … · doi:10.…`
       — PMID/DOI renderer tự thành link bấm được.
     · Tập/Số/Trang phải TRA MÁY (esummary/Crossref) — cấm điền từ trí nhớ
       (đo 19/08: trí nhớ sai 2/7 trường ngay lần đầu).
     · GUIDELINE trích theo ẤN PHẨM của nó (guideline lớn đều đăng tạp chí —
       tra PMID/DOI thật, vd KDIGO 2024 = Kidney Int 2024;105(4S):S117–S314,
       PMID 38490803); tài liệu dài ghi «(phần trích: tr. Sxxx–Syyy)» theo SỐ
       TRANG ẤN PHẨM, không phải trang file PDF. Guideline không đăng tạp chí
       → URL trang chính thức + «[truy cập ngày …]».
     · TUYỆT ĐỐI KHÔNG lộ ngôn ngữ vận hành vào thân bài hay mục Nguồn:
       «bản chụp», tên kho/đường dẫn nội bộ, SHA, nhãn [đã kiểm rút bài]…
       Provenance máy nằm ở sổ (so-guideline.json) — đó là chỗ của nó.
     · Minh bạch thẩm định gom thành MỘT đoạn «Ghi chú thẩm định: …» đặt SAU
       danh mục (renderer tự in nghiêng nhỏ): ngày kiểm rút bài + chuỗi kiểm,
       nguồn nào thẩm định trên toàn văn/tóm tắt.
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
