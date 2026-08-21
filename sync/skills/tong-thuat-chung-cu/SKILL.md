---
name: tong-thuat-chung-cu
description: Bác sĩ hỏi MỘT chủ đề lâm sàng → trả MỘT bài tổng thuật học thuật liền mạch (kiểu Deep-Research) neo vào hạ tầng liêm chính — 4 làn nguồn song song, trích dẫn Vancouver đánh số qua cổng kiểm, trình bày chuẩn v11. Bác sĩ duyệt gói ① ngày 19/08/2026.
version: 1.7.0
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

3. **VIẾT BÀI** — hai chế độ (văn xuôi liền mạch, không dán thẻ):

   **3a. CÂU HỎI HẸP** (một quyết định lâm sàng cụ thể) — khung I–V như dưới.

   **3b. TỔNG QUAN CHỦ ĐỀ** (v1.3 — bác sĩ đưa mẫu Gemini 19/08: khi yêu cầu là
   «cập nhật chứng cứ cho <bệnh>» trọn chủ đề): khung 5 phần kiểu chương giáo khoa —
   `## I. Nguyên tắc quản lý hiện đại` (triết lý điều trị, cửa sổ cơ hội, T2T…)
   `## II. Chẩn đoán` (tiêu chuẩn phân loại + ngưỡng số nguyên văn)
   `## III. Điều trị theo bậc` (khởi đầu → bước hai → head-to-head then chốt)
   `## IV. Quản lý dài hạn` (giảm liều/ngừng thuốc · can thiệp không dùng thuốc)
   `## V. Kết luận và hướng chưa trả lời`
   — kèm ≥2 BẢNG so sánh (tiêu chuẩn · khuyến cáo hai tổ chức · head-to-head).
   LUẬT RIÊNG chế độ này (đúng lỗ hổng của bản Gemini bác sĩ đưa: chia sẻ ra ngoài
   là MẤT SẠCH trích dẫn, «một phân tích tổng hợp cho thấy…» không truy được):
   · CẤM khẳng định mồ côi — mọi «nghiên cứu/phân tích cho thấy» phải có [n];
   · chủ đề KHÔNG kịp xác minh nguồn gốc (dấu ấn mới, NMA xếp hạng…) → ghi rõ
     «chưa đưa vào vì chưa xác minh bài gốc», KHÔNG viết dựa trí nhớ;
   · nhất quán KHO: đối chiếu quyet-dinh-da-duyet.json + dashboard cùng chủ đề,
     mục nào hệ đã có quyết định thì bài phải ăn khớp hoặc nêu rõ vênh.

   Khung I–V cho chế độ 3a:
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
   → `python3 tools/xuat_tong_thuat.py <file>.md` (renderer TỰ sinh dải THẺ
   NGUỒN có link dưới mỗi mục — số [n] trong câu + thẻ bấm-mở-thẳng DOI/PubMed,
   theo mẫu bác sĩ duyệt 19/08; cổng hình thức fail-closed:
   [n] khớp Nguồn hai chiều, nguồn nào cũng có PMID/DOI/URL) → gửi bác sĩ file
   HTML (SendUserFile, display:"render") → `python3 tools/dung_hom_thu.py`.

## 5. TỰ SOI NỘI DUNG TRƯỚC KHI GIAO (v1.4 — bắt buộc)

Đo thật 20/08 trên 5 bài do máy viết: **trích dẫn hoàn hảo mà nội dung vẫn sai
nguy hiểm** — 7/7 dòng Vancouver khớp từng trường, mọi con số truy được về tóm
tắt, cổng hình thức PASS; nhưng thẩm định đối kháng vẫn bắt **13 lỗi NẶNG**,
trong đó có lỗi hại người bệnh. **Cổng trích dẫn là điều kiện CẦN, không đủ.**

Trước khi giao bài, soi đúng 5 lớp lỗi ĐÃ XẢY RA THẬT (mỗi lớp kiểm bằng cách
mở lại nguồn, không kiểm bằng trí nhớ):

| Lớp | Ca thật 20/08 | Cách tự bắt |
|---|---|---|
| ① Ngưỡng an toàn gán SAI nhóm thuốc | ngưỡng kali >5,0 của MRA bị gán cho ACE-I | mỗi ngưỡng phải chỉ đúng thuốc mà nguồn gắn nó |
| ② Bỏ sót luật NGỪNG thuốc / mức Harm | thiếu «ngừng MRA nếu K không giữ được <5,5» (COR 3: Harm) | tra mục khuyến cáo của chính thuốc đó, đọc CẢ khuyến cáo nghịch |
| ③ Khẳng định MỒ CÔI trái guideline | «yếu tố này quyết định trình tự chứ không quyết định có dùng hay không» — không [n], trái điều kiện khởi trị | mọi câu mang tính luật phải có [n] |
| ④ «Không nguồn nào nêu X» khi CHƯA đọc toàn văn | bài nói không nguồn nào cho mốc chỉnh liều, trong khi guideline có mục riêng | chỉ được viết «không nêu» cho phần ĐÃ ĐỌC; chưa đọc thì ghi «chưa đọc được» |
| ⑥ Trưng mức khuyến cáo KHÔNG áp cho quần thể của bài | bài viết cho ca CHƯA từng dùng thuốc, lại trưng mức của tình huống ĐỔI thuốc | đọc điều kiện áp dụng trong chính câu khuyến cáo; không khớp thì nói rõ «chưa đối chiếu được», KHÔNG chép mức từ trí nhớ |
| ⑦ Bỏ điều kiện an toàn của thuốc vừa khuyên kê | khuyên chuyển sang ARNI + đưa bảng liều mà thiếu rửa trôi 36 giờ và chống chỉ định phù mạch | mỗi thuốc có bảng liều PHẢI kèm điều kiện khởi trị/chống chỉ định; nguồn guideline không đọc được thì tra **nhãn thuốc** |
| ⑧ Mục hành động chỉ mang nửa NGUY CƠ, bỏ nửa LỢI ÍCH | ba gạch đều nghiêng khỏi JAKi, trong khi chính nguồn kết luận hồ sơ lợi ích–nguy cơ thuận lợi | mục V phải mang CẢ hai vế của nguồn lợi ích–nguy cơ, hoặc nói rõ vì sao chỉ lấy một vế |
| ⑤ Gán N GỘP cho từng ước lượng | N của cả tổng quan (30.994) dán cho mọi hàng trong bảng | mỗi hàng lấy đúng N của phân tích đó, không có thì để trống |
| ⑨ Điều kiện gắn NHẦM khuyến cáo | mốc «40 ngày sau nhồi máu» của khuyến cáo **cấy ICD** bị đặt làm ngoại lệ của tiêu chí **chuyển tuyến** ⇒ đọc thành «NYHA III–IV trong 40 ngày thì chưa chuyển», tức TRÌ HOÃN đúng nhóm nặng nhất | trích đúng nguyên văn vẫn có thể gắn sai đích. Với mỗi điều kiện, hỏi «điều kiện này là của KHUYẾN CÁO NÀO» và đọc lại đúng bảng/sơ đồ đó — cổng trích dẫn mù hoàn toàn với lớp này |
| ⑩ Hạ/nâng một mức theo MỘT nguồn khi bộ nguồn có nhiều mức | sửa mức ARNI ở ca de novo xuống **IIb B** cho đúng ESC, mà bỏ mất **COR 1 A** của AHA/ACC/HFSA cho cùng quần thể ⇒ bản «sửa cho đúng» làm thuốc trông YẾU hơn nền chứng cứ, có thể dẫn tới hoãn thuốc | trước khi đổi bất kỳ mức nào, quét **CẢ BỘ NGUỒN của bài** xem có tổ chức nào đặt mức khác cho cùng quần thể. Hai nguồn lệch nhau thì nêu CẢ HAI; không lấy mức thấp nhất làm kết luận chung |
| ⑪ Cấm một lối mà không nêu LỐI RA | mở rộng đúng lệnh cấm phù mạch cho cả ARNI lẫn ACE-I, nhưng bỏ mất **ARB ở COR 1 A** cho chính người không dung nạp vì phù mạch ⇒ mục hành động thành ngõ cụt | mỗi khi bài CẤM một lựa chọn, phải tra trong cùng nguồn xem có phương án thay được khuyến cáo không, và nêu kèm mức của nó |

Ba lớp ⑥⑦⑧ bổ sung 21/08 sau khi vòng SỬA lại sinh lỗi mới; ba lớp ⑨⑩⑪ bổ sung cùng ngày sau ba vòng thẩm định liên tiếp trên MỘT bài. **Mỗi lần sửa phải thẩm định lại** — bản vá tạo lỗi ở đúng chỗ nó vừa chạm vào, và điều này đo được ổn định: 3/5 bài sinh lỗi nặng MỚI trong vòng sửa đầu; vòng hai sinh thêm 4 phát hiện mới; vòng ba lại sinh 4 nữa, trong đó có một chỗ mà bản «sửa cho đúng mức» làm một thuốc trông yếu hơn nền chứng cứ. Số lỗi NẶNG về 0 từ vòng hai, nhưng lỗi CÂN BẰNG thì mỗi vòng vẫn ra thêm ⇒ **đừng dừng ở «0 lỗi nặng»**, dừng khi một vòng không còn phát hiện nào do chính vòng sửa trước gây ra.

**KHI LỖI TÁI SINH ĐÚNG CHỖ VỪA VÁ — DỪNG VÁ, VIẾT LẠI TRỌN KHỐI.** Đo trên bài suy tim
21/08: bốn vòng liền, mỗi vòng sửa xong thì vòng sau lại tìm ra lỗi mới **ngay tại khối vừa
chạm vào** (chuỗi phù mạch → lối ra). Đó không phải chuỗi lỗi rời rạc mà là dấu hiệu của một
**mạch lập luận có ràng buộc lẫn nhau**: thêm một vế cân bằng thì lộ ra vế kế tiếp, vì cả khối
phải đúng cùng lúc mới đúng. Vòng năm viết lại trọn khối thành một thang có đủ bậc — vòng sáu
**không còn phát hiện nào trong khối đó**, hai điểm mới rơi sang mục khác và nhẹ hơn hẳn.
Dấu hiệu nhận biết: hai vòng liên tiếp cùng báo lỗi ở cùng một khối, dù mỗi lần một câu khác.

Bài dùng cho quyết định thực hành (benchmark, gói tuần, tra điểm khám) nên chạy
thêm MỘT lượt thẩm định ĐỘC LẬP (agent khác/phiên khác) — người viết không nhìn
thấy lỗi của chính mình, đã đo được nhiều lần trong hệ này.

## LUẬT CỨNG
- KHÔNG bịa; số nào không có trong nguồn thì không viết; «tóm tắt không nêu» là
  câu trả lời hợp lệ. Toàn văn đọc được thì thẩm định từ toàn văn (ghi nhãn).
- Hai trục tách bạch: mức chứng cứ của NGUỒN ≠ đề xuất áp dụng; không tự gán
  GRADE cho nguồn không phân hạng (`na` + normativeBasis nếu quy phạm).
- Bài tổng thuật là TÀI LIỆU HỖ TRỢ — không vượt Cổng A/B; quyết định đã duyệt
  trong sổ chỉ bác sĩ đổi. Không PII. Ngoài phạm vi ngoại trú người lớn → nói rõ.
- Câu hỏi CÓ dấu hiệu cấp cứu → chạy `sang-loc-co-do` TRƯỚC, tổng thuật sau.
