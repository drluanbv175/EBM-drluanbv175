# Gói đề xuất — nguồn chứng cứ & đọc toàn văn: 11 vấn đề chưa hoàn thiện (23/09/2026)

> Nối tiếp `audit/13-tong-hop-nguon-chung-cu-va-doc-toan-van_2026-09-23.md` (đã đính
> chính). Mỗi vấn đề dưới đây có: **Hiện trạng** (đo được, không suy diễn) · **Đề xuất**
> (việc cụ thể) · **Ai làm**. Đánh số theo mức ưu tiên thực dụng, không theo thứ tự xuất
> hiện trong sổ nguồn. Cần bác sĩ kiểm chứng.

## Tóm tắt chi tiết trạng thái hiện tại (trước khi vào từng vấn đề)

**36 nguồn đăng ký:** 28 `active` · 2 `degraded` · 6 `not-covered`.

**Ba tầng năng lực, đừng gộp:**
- **Khám phá theo tiêu đề** (Crossref, 20 hiệp hội) — biết "có bài mới", tóm tắt thường rỗng.
- **Dò thay đổi trang** (10 nguồn `html-watch`) — biết "trang đổi", phải người tự mở Browser.
- **Đọc toàn văn thật** — chỉ **GOLD, GINA** tự động + đã kiểm sống. Wiley TDM đọc được
  nhưng bị chặn IP. PMC/BTS/Thorax/NICE không đọc được (chặn mạng + rào pháp lý).
- **PubMed MCP tương tác** — đọc toàn văn THẬT cho bài nghiên cứu gốc (3/3 eLife) VÀ cho
  một phần thật guideline có PMCID (2/5 mẫu thử — xem vấn đề 3, ĐÃ LÀM).

**✅ ĐÃ LÀM trong phiên này (23/09/2026, theo yêu cầu "làm 1,2,3,4"):** vấn đề 1 (vá
taxonomy), 2 (tạo tác vụ lịch cho 9/10 trạm), 3 (mở rộng mẫu PubMed MCP lên 9 phép thử).
Vấn đề 4 (điều tra vá PMC) — xem kết luận ở cuối mục đó.

---

## Vấn đề 1 — Công cụ đo độ phủ chính thức của hệ đã lạc hậu

**✅ ĐÃ VÁ 23/09/2026.** Thêm tầng `guideline_fulltext` riêng (tách khỏi
`full_text_and_citation_context`) vào `EVIDENCE_SOURCE_UNIVERSE`, khớp đúng
`SourceClient.name` của cả 5 connector (xác nhận bằng grep, không suy đoán). Kiểm sống:
`healthy_sources=[gold_copd_fulltext, gina_asthma_fulltext]` → tầng PASS. +2 test hồi
quy, sửa 1 test cũ. Toàn bộ 5805 test PASS. Đã commit+push
(`feat(nguon): thêm tầng guideline_fulltext...`, medical-ebm-automation).

**Hiện trạng:** `app/sources/authority.py::assess_source_universe_coverage()` là hàm
DUY NHẤT cho ra kết luận PASS/PARTIAL chính thức của hệ, nhưng taxonomy của nó (tầng
`full_text_and_citation_context`) chỉ biết 4 tên cũ (`unpaywall`, `semantic_scholar`,
`publisher_full_text`, `pmc_full_text`) — KHÔNG khớp tên 5 connector toàn văn vừa xây hôm
nay (`gold_copd_fulltext`, `gina_asthma_fulltext`, `bts_guidelines_fulltext`,
`pmc_guideline_fulltext`, `wiley_tdm`). Nếu ai chạy hàm này bây giờ, nó sẽ báo tầng đó
PARTIAL/không thấy GOLD-GINA dù cả hai đang hoạt động thật — đúng họ lỗi "tên sai quy
ước" mà chính file này đã tự ghi chú cho vụ `high_impact_journals` ngày 05/09/2026.

**Đề xuất:** thêm 5 tên connector mới vào tầng `full_text_and_citation_context` (hoặc
tách tầng mới `guideline_fulltext` cho rõ nghĩa, vì 4 tên cũ là "tìm bản OA hợp pháp",
5 tên mới là "đọc toàn văn guideline theo tổ chức" — hai việc khác nhau). Việc máy móc,
rủi ro thấp, có thể làm ngay.

**Ai làm:** tôi (agent) — chỉ cần bác sĩ xác nhận ưu tiên làm ngay hay để dịp khác.

---

## Vấn đề 2 — 10 trạm "dò thay đổi trang" chưa tự động hóa

**✅ ĐÃ LÀM 23/09/2026 — nhưng khác kế hoạch ban đầu, vì đo lại lộ ra sự thật rẻ hơn.**
Trước khi tạo tác vụ lịch, chạy `giam_sat_to_chuc.py --kiem-tra` từ máy Mac thật (không
phải sandbox) để xác nhận: **9/10 trạm chạy TỐT bằng script thường, KHÔNG cần Browser**
(GOLD/GINA/KDIGO/ADA/ESC/IDSA/USPSTF/WHO/BYT) — chỉ ACC/AHA (SRC-015) thật sự bị
Cloudflare chặn (đã có tác vụ lịch riêng `giam-sat-acc-aha-quy` từ trước, quý/Browser).
Đọc code `giam_sat_to_chuc.py` xác nhận thêm: lệnh KHÔNG tham số đã là chế độ quét-và-ghi
thật (tự phát hiện tiêu đề mới, tự ghi hàng ứng viên, tự đánh dấu degraded khi hỏng) —
chỉ là **chưa từng được đưa vào lịch nào** (`grep` xác nhận 0 kết quả ngoài tác vụ
ACC/AHA). Đã tạo tác vụ lịch mới **`giam-sat-9-tram-web-hoi-tuan`** (thứ Hai 18:50, nối
tiếp nhịp `thu-thap-tuan-an-toan-thuoc`/`goi-duyet-tuan-ebm`), chỉ gọi
`python3 tools/giam_sat_to_chuc.py` — không cần Browser, đơn giản hơn nhiều so với đề
xuất ban đầu. Đã thử `run_now` để kiểm — phiên chạy thử bất thường lâu (55 tin nhắn cho
1 lệnh Bash đơn giản), chưa xác nhận được kết quả cuối cùng trong phiên này — bác sĩ nên
kiểm tra lại "Scheduled" → chạy tay lần nữa hoặc đợi lần chạy thật thứ Hai tới.

---

## Vấn đề 3 — PMC guideline full-text: mở rộng cỡ mẫu

**✅ ĐÃ LÀM 23/09/2026.** Mở rộng từ 1 lên 9 phép thử (3 nghiên cứu eLife + 5 guideline có
PMCID, tra qua `search_articles` — không đoán). Kết quả: **2/5 guideline có toàn văn
thật** (ONKOPEDIA hướng dẫn xơ tủy ~9.000 từ, Korean Thyroid Association 130.334 ký tự),
3/5 rỗng (ADA, ASFA, CFP deprescribing statins). Kết luận "guideline luôn rỗng" (đính
chính buổi sáng) đã SAI — sửa lại trong `audit/13` §7. Phát hiện thêm: chỉ 5/18 guideline
chuyên khoa được tra có PMCID — bản thân việc CÓ bản ghi PMC đã hiếm.

---

## Vấn đề 4 — `pmc_guideline_fulltext.py` (SRC-046) có vá được không?

**✅ ĐÃ VÁ THẬT 23/09/2026 — thành công, ngoài dự kiến ban đầu.** Đọc tài liệu chính thức
NCBI (`ftp.ncbi.nlm.nih.gov/pub/pmc/readme.txt`) tìm ra: FTP cũ đang bị khai tử, thay
bằng **bucket S3 công khai `pmc-oa-opendata`** (PMC Open Access Subset, AWS Open Data
Registry) — không cần tài khoản AWS, không cùng hạ tầng/WAF với `pmc.ncbi.nlm.nih.gov`.
Viết lại toàn bộ connector dùng đường này (liệt kê + tải `.txt` qua HTTPS thường). Kiểm
sống 4 PMCID: khớp 100% với kết quả PubMed MCP (vấn đề 3) — xác nhận đây CHÍNH LÀ nguồn
dữ liệu mà MCP dùng phía sau. `data/sources.json` SRC-046 → `active`. 10 test viết lại,
PASS. Đã commit + push cả 2 repo.

**Giới hạn thật, không phải lỗi:** chỉ bài ĐÃ nộp lưu toàn văn cho PMC OA Subset mới đọc
được — không phải "vá xong thì đọc được mọi guideline".

---

## Vấn đề 5 — Wiley TDM: chưa kiểm được từ mạng thật có quyền

**Hiện trạng:** token hợp lệ, cơ chế đúng, nhưng bị `ACCESS_DENIED` vì IP máy Mac hiện
tại ngoài dải IP tài khoản Wiley Online Library được cấp quyền.

**Đề xuất:** thử lại lệnh `python run.py wiley-tdm-test <DOI>` (đã có sẵn, không cần vá
gì) khi đang kết nối mạng bệnh viện/tổ chức có quyền Wiley. Nếu vẫn `ACCESS_DENIED` từ
mạng đó — cần liên hệ thư viện/IT bệnh viện xác nhận đúng dải IP đã đăng ký.

**Ai làm:** CHỈ bác sĩ (cần đổi mạng vật lý, ngoài tầm agent).

---

## Vấn đề 6 — BTS/Thorax/NICE: chấp nhận giới hạn hay xin giấy phép NICE?

**Hiện trạng:** đã điều tra kỹ (Cloudflare cho Thorax/BMJ — không vượt qua được; giấy
phép AI trả phí cho NICE). Hai bên đường cụt kỹ thuật, một bên là quyết định tiền bạc.

**Đề xuất:** hai lựa chọn, không cái nào tôi tự quyết được:
(a) chấp nhận — mở trình duyệt tay khi cần đọc guideline BTS cụ thể (miễn phí, chậm hơn);
(b) xin giấy phép AI của NICE (`nice.org.uk` → "permission to use nice content for AI
purposes") — có phí, có quy trình duyệt, không rõ chi phí/thời gian tới khi có kết quả.

**Ai làm:** bác sĩ quyết định hướng; nếu chọn (b), việc nộp đơn cũng là bác sĩ tự làm
(quan hệ hợp đồng với NICE, ngoài thẩm quyền agent).

---

## Vấn đề 7 — Cục Quản lý Dược VN (SRC-021): domain không tới được

**Hiện trạng:** `dav.gov.vn` không tới được từ môi trường phiên này qua CẢ 3 phương pháp
độc lập đã thử (22/09/2026) — chưa rõ do domain thật sự có vấn đề hay do mạng của phiên
này (một số cổng Việt Nam có yêu cầu route riêng).

**Đề xuất:** bác sĩ tự thử mở `dav.gov.vn/canh-bao-va-thu-hoi` bằng trình duyệt cá nhân
từ mạng Việt Nam trong nước — nếu mở được bình thường, cho biết để tôi thử lại (có thể
là vấn đề route/DNS riêng của môi trường phiên, không phải domain chết); nếu domain đó
tự nó cũng chập chờn thì giữ nguyên `not-covered`, theo dõi thủ công.

**Ai làm:** bác sĩ thử trước (1 phút), rồi báo lại — tôi thử tiếp nếu có tín hiệu domain sống.

---

## Vấn đề 8 — Epistemonikos: giữ nguyên quyết định cũ hay đổi ý?

**Hiện trạng:** connector viết sẵn, chỉ chờ token — bác sĩ đã đánh giá 22/09/2026 là
KHÔNG khả thi theo đuổi (cần gửi email xin duyệt thủ công, không tự cấp được).

**Đề xuất:** không có gì cần làm — chỉ xác nhận lại quyết định đó còn đúng, hay muốn thử
gửi email xin token (mất thời gian chờ phản hồi, không đảm bảo được duyệt).

**Ai làm:** bác sĩ (chỉ cần xác nhận, không cần hành động thêm nếu giữ nguyên).

---

## Vấn đề 9 — Wiley MCP (khác Wiley TDM API): ✅ HOẠT ĐỘNG THẬT 23/09/2026

**✅ ĐÃ XONG.** Bác sĩ Clear authentication → Re-authenticate qua claude.ai connector
settings (cấp lại từ đầu, không tái dùng phiên cũ thiếu scope). Kiểm sống ngay bằng câu
hỏi lâm sàng thật (momelotinib vs ruxolitinib trong xơ tủy): trả về **3 bài thật** — 2
bài tạp chí Wiley (HemaSphere, Am J Hematol) + 1 guideline **ONKOPEDIA 2025** (Int J
Cancer) — đủ DOI, ngày xuất bản, trích đoạn văn bản/bảng số liệu thật, không rỗng.

**Năng lực thật:** tìm kiếm NGỮ NGHĨA (theo ý câu hỏi, không chỉ từ khóa) trong tạp chí
Wiley — bổ sung cho Crossref/PubMed (chỉ khớp từ khóa/tiêu đề). Giới hạn: (1) chỉ nội
dung Wiley, nhà cung cấp tự khai sẽ mở rộng thêm nhà xuất bản khác sau; (2) tương tác —
cùng nhóm Cochrane/Scite, chỉ gọi được trong phiên Claude Code, KHÔNG vào vòng quét tuần
tự động; (3) mỗi kết quả kèm khối "disclosures" bắt buộc giữ khi trích dẫn (nguồn AI
sinh, cần xác minh, độ mới kho dữ liệu). `data/sources.json` SRC-041 → `active`.

**Ai làm:** bác sĩ (thao tác cấp quyền lại); tôi kiểm sống sau khi bác sĩ báo đã làm xong.

---

## Vấn đề 10 — 20 hiệp hội chỉ có "khám phá", 6 trong đó (KDIGO ngoại lệ đã có web-hội)
chưa có trạm "web hội" riêng như GOLD/GINA

**Hiện trạng:** EULAR · ATS/ERS/BTS · ACG/AGA/ASGE · AASLD/EASL · ASH/ISTH · AGS chỉ
được phủ qua Crossref theo tiêu đề (tóm tắt thường rỗng) — KHÔNG có trạm `html-watch`
riêng như GOLD/GINA/KDIGO/ADA/ESC/ACC-AHA đang có.

**Đề xuất:** nếu bác sĩ có chuyên khoa ưu tiên rõ (vd hay tra cứu thấp khớp → EULAR;
tiêu hóa → AASLD/ACG/AGA), có thể dựng thêm trạm `html-watch` cho hiệp hội đó — theo
đúng khuôn đã dùng cho GOLD/GINA (khảo sát robots.txt/ToU trước, không đoán URL). Việc
CÓ GIÁ TRỊ nhưng KHÔNG khẩn — 20 hiệp hội vẫn có khám phá cơ bản qua Crossref.

**Ai làm:** tôi, sau khi bác sĩ chọn ưu tiên chuyên khoa nào trước (đừng dàn trải 6 hội
cùng lúc — mỗi trạm cần khảo sát riêng, tốn thời gian).

---

## Vấn đề 11 — UpToDate/DynaMed/Embase: hoàn toàn ngoài tầm, thương mại

**Hiện trạng:** không có quyền hợp pháp — `not-covered`, bác sĩ tra tay khi cần.

**Đề xuất:** không có việc kỹ thuật nào để làm. Nếu bác sĩ/đơn vị cân nhắc mua license
(UpToDate/DynaMed thường có gói cá nhân hoặc theo đơn vị), đó là quyết định tài chính,
không phải kỹ thuật — không đề xuất gì thêm từ phía tôi.

**Ai làm:** bác sĩ (nếu có nhu cầu, đây là quyết định mua sắm, ngoài phạm vi công việc kỹ thuật).

---

## Vấn đề 12 (MỚI, ngoài 11 vấn đề gốc) — BTS/Thorax/NICE không đọc được toàn văn: vẫn
để trống tay hay có phương án dự phòng?

**Câu hỏi bác sĩ nêu sau khi đọc Vấn đề 6/hiện trạng BTS:** "BTS/Thorax/NICE không đọc
được toàn văn nhưng hãy thiết kế để hệ thống cung cấp trích dẫn và có một tóm tắt chi
tiết cho chứng cứ".

**Đã làm:** module mới `app/sources/guideline_citation_summary.py`
(`lay_trich_dan_tom_tat(doi=..., pmid=...)`) — dự phòng TRÍCH DẪN + TÓM TẮT cho BẤT KỲ
DOI/PMID nào mà mọi connector toàn văn (GOLD/GINA/BTS/PMC/Wiley) đã thử và thất bại,
không riêng BTS. Hai tầng, theo thứ tự:
1. **Europe PMC** — tra CHÍNH XÁC theo DOI hoặc PMID (`EXT_ID:<pmid> AND SRC:MED` hoặc
   `DOI:"<doi>"`, không phải tìm mờ theo từ khóa).
2. **Crossref** — tra TRỰC TIẾP `GET /works/{doi}` (khác `CrossrefClient.search()` hiện
   có, vốn là tìm mờ) — chỉ dùng khi Europe PMC không có bản ghi hoặc thiếu abstract.

**RANH GIỚI PHẢI HIỂU ĐÚNG — không được nhầm với toàn văn:** kết quả trả về là
**ABSTRACT** (tóm tắt do chính tác giả/nhà xuất bản viết và nộp lúc công bố), KHÔNG PHẢI
"đọc toàn văn rồi tóm tắt lại". Một abstract 150–350 từ đủ để biết bài nói về CÁI GÌ và
KẾT LUẬN CHUNG, nhưng KHÔNG đủ để trích số liệu/ngưỡng/liều cụ thể — những thứ đó chỉ có
trong toàn văn. Mọi kết quả trả về đều tự mang `ghi_chu` nói rõ ranh giới này. Ba kết
quả có thể xảy ra, không bịa ở bất kỳ trường hợp nào:
- **Có trích dẫn + có abstract** → dùng được để biết đại khái nội dung, `ghi_chu` nhắc
  "không phải toàn văn, cần bác sĩ kiểm chứng, muốn chi tiết đầy đủ phải tự đọc toàn văn".
- **Có trích dẫn thật nhưng KHÔNG có abstract công khai** (thường gặp — Crossref không
  phải mọi nhà xuất bản đều nộp abstract) → chỉ có tác giả/tạp chí/năm, `ghi_chu` nói rõ
  không tóm tắt được.
- **Không tra được ở cả hai nguồn** (DOI/PMID sai hoặc lỗi mạng) → thất bại trung thực,
  không bịa trích dẫn.

**Đã kiểm sống 23/09/2026, đúng ca BTS đã bị chặn hoàn toàn ở Vấn đề 6:** DOI hướng dẫn
tràn khí màng phổi BTS (`10.1136/thorax-2022-219784`, chính DOI đã xác nhận bị Cloudflare
chặn toàn văn) → Europe PMC/Crossref trả trích dẫn thật (tác giả, tạp chí *Thorax*, năm)
nhưng KHÔNG có abstract công khai — đúng nhánh "có trích dẫn, không có tóm tắt". Một
guideline khác đã thử (thần kinh, AAN) → có cả trích dẫn lẫn abstract thật.

**Đã dạy 2 agent gọi tới module này** (theo luật BH39 — thêm công cụ ở tầng lập trình
phải dạy agent cùng lúc, nếu không công cụ tồn tại mà không ai gọi):
`tra-cuu-chung-cu` (khi tra một câu hỏi điểm khám gặp nguồn bị chặn toàn văn) và
`huong-dan-lam-sang` (khi đối chiếu khuyến cáo với guideline không đọc được toàn văn).

**Việc CHƯA làm, có chủ ý:** module không tự tìm/đoán DOI/PMID — người gọi (agent/quy
trình khác) phải đã có định danh trước (từ Crossref title lane, PubMed, hoặc bác sĩ cung
cấp). Đây KHÔNG phải khoảng trống — module cố ý hẹp phạm vi để tránh trở thành nguồn tra
cứu mờ (fuzzy search) thứ hai.

**Ai làm:** đã xong về mặt kỹ thuật — không cần bác sĩ làm gì thêm. Vấn đề 6 (chọn chấp
nhận Cloudflare/xin giấy phép NICE) VẪN còn đó cho toàn văn đầy đủ; đây chỉ là lưới đỡ
để không "tay không hoàn toàn" khi toàn văn bị chặn.

---

## Bảng tổng hợp nhanh — ai làm gì trước

| # | Vấn đề | Việc tiếp theo | Ai |
|---|---|---|---|
| 1 | Công cụ đo độ phủ lạc hậu | ✅ ĐÃ VÁ — tầng `guideline_fulltext` mới | Xong |
| 3 | Cỡ mẫu PMC-MCP quá nhỏ | ✅ ĐÃ LÀM — 9 mẫu, 2/5 guideline có toàn văn | Xong |
| 2 | 10 trạm html-watch chưa tự động | ✅ ĐÃ TẠO tác vụ lịch (9/10, ACC/AHA có riêng) | Xong, cần bác sĩ xác nhận chạy tốt |
| 4 | Vá PMC full-text thật? | ✅ ĐÃ VÁ THẬT — dùng bucket S3 chính thức, SRC-046 active | Xong |
| 10 | 6 hiệp hội chưa có web-hội riêng | Chọn 1 chuyên khoa ưu tiên | Bác sĩ chọn, tôi làm |
| 5 | Wiley TDM chặn IP | Thử lại từ mạng bệnh viện | CHỈ bác sĩ |
| 6 | BTS/Thorax/NICE | Chọn: chấp nhận / xin giấy phép NICE | CHỈ bác sĩ |
| 7 | Cục QL Dược VN | Tự mở thử domain, báo lại | Bác sĩ trước, tôi sau |
| 8 | Epistemonikos | Xác nhận giữ nguyên hay đổi ý | Bác sĩ |
| 9 | Wiley MCP | ✅ Hoạt động thật — kiểm sống 3 bài, có cả guideline | Xong |
| 11 | UpToDate/DynaMed/Embase | Không có việc kỹ thuật | — |

**Cần bác sĩ kiểm chứng.**
