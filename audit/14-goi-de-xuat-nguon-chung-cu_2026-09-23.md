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
- **PubMed MCP tương tác** (mới đo hôm nay) — đọc toàn văn THẬT cho bài nghiên cứu gốc
  (3/3 bài eLife, 40-102 nghìn ký tự), nhưng **rỗng** cho tài liệu dạng guideline (1/1
  chương ADA đã thử) — mạnh cho nghiên cứu, CHƯA chắc giúp được guideline lâm sàng.

---

## Vấn đề 1 — Công cụ đo độ phủ chính thức của hệ đã lạc hậu

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

**Hiện trạng:** GOLD·GINA·KDIGO·ADA·ESC·ACC/AHA·IDSA·USPSTF·WHO·BYT đều `active`, đã
xác minh sống — nhưng cơ chế `giam_sat_to_chuc.py --nap-van-ban` đòi **người/agent tự
tay** mở một phiên Browser mỗi lần kiểm. SRC-015 tự ghi rõ: "việc còn lại: nối vào một
tác vụ lịch (Claude scheduled task, có quyền Browser) để trạm này không cần bác sĩ/agent
làm tay mỗi lần".

**Đề xuất:** tạo một tác vụ lịch (`mcp__scheduled-tasks__create_scheduled_task`) chạy
định kỳ (đề xuất: hằng tuần, cùng nhịp `thu-thap-tuan-an-toan-thuoc`), tự mở phiên
Browser, quét cả 10 trạm, ghi kết quả vào sổ — khớp đúng mẫu 6 tác vụ lịch đã có.

**Ai làm:** cần một phiên Claude Code có quyền tạo tác vụ lịch — tôi có thể soạn script,
nhưng **tạo tác vụ lịch nền là hành động đứng (standing), nên hỏi bác sĩ xác nhận trước
khi tạo**, đúng nguyên tắc "hành động khó đảo ngược cần xác nhận".

---

## Vấn đề 3 — PMC guideline full-text: chỉ mới thử 1 mẫu cho câu "guideline luôn rỗng"

**Hiện trạng:** kết luận "PubMed MCP đọc rỗng cho guideline" hiện dựa trên **ĐÚNG 1 phép
thử** (chương ADA). Cỡ mẫu 1 chưa đủ để khẳng định chắc — có thể ADA riêng biệt (PMC chỉ
lưu PDF, không XML) trong khi guideline khác (vd của hội có tập tin XML đầy đủ) vẫn đọc
được.

**Đề xuất:** thử thêm 2-3 guideline khác đã có PMCID xác nhận (không đoán — tra qua
`search_articles`/`get_article_metadata` trước) để có cỡ mẫu đủ tin. Việc rẻ, nên làm.

**Ai làm:** tôi — làm được ngay trong phiên tiếp theo nếu bác sĩ muốn.

---

## Vấn đề 4 — `pmc_guideline_fulltext.py` (SRC-046) có thể vá được không, hay dừng hẳn?

**Hiện trạng:** connector tự viết của tôi bị chặn WAF khi gọi trực tiếp
`pmc.ncbi.nlm.nih.gov`. Nhưng PubMed MCP (bên thứ ba, không phải code của dự án) đọc
được toàn văn PMC cho bài nghiên cứu — chứng minh **CÓ tồn tại** một đường hợp pháp,
không bị WAF. Tôi chưa biết đường đó là gì (không có quyền xem code backend của MCP).

**Đề xuất:** dành một phiên điều tra riêng — thử các endpoint chính thức khác của NCBI
(FTP bulk OA, PMC Article Datasets trên AWS Open Data — dịch vụ có thật, KHÔNG phải đoán,
cần tra tài liệu NCBI chính thức trước khi thử) xem có đường nào không bị WAF chặn. Đây
là việc CÓ RỦI RO THẤT BẠI — không hứa trước sẽ vá được, chỉ là hướng đáng thử.

**Ai làm:** tôi, nếu bác sĩ muốn dành thời gian cho hướng này (không chắc thành công).

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

## Vấn đề 9 — Wiley MCP (khác Wiley TDM API): chưa cấp quyền

**Hiện trạng:** server `plugin:bio-research:wiley` cần xác thực OAuth — khác hẳn
Wiley TDM API (đã cấp token thành công §5). Đây là công cụ tìm kiếm ngữ nghĩa
(`semanticSearch`) trên tạp chí Wiley, không phải tải PDF.

**Đề xuất:** nếu muốn dùng, bác sĩ tự cấp quyền qua claude.ai connector settings. Giá trị
thêm so với Wiley TDM đã có: khám phá/tìm kiếm ngữ nghĩa, không phải tải toàn văn — mức
độ hữu ích thấp hơn so với việc đã có Crossref/PubMed/OpenAlex cho khám phá.

**Ai làm:** bác sĩ, và chỉ nên làm nếu thấy giá trị rõ ràng — không phải việc cấp thiết.

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

## Bảng tổng hợp nhanh — ai làm gì trước

| # | Vấn đề | Việc tiếp theo | Ai |
|---|---|---|---|
| 1 | Công cụ đo độ phủ lạc hậu | Vá taxonomy 5 tên connector mới | Tôi |
| 3 | Cỡ mẫu PMC-MCP quá nhỏ | Thử thêm 2-3 guideline khác | Tôi |
| 2 | 10 trạm html-watch chưa tự động | Tạo tác vụ lịch | Tôi, cần bác sĩ xác nhận trước |
| 4 | Vá PMC full-text thật? | Điều tra endpoint chính thức NCBI | Tôi, không chắc thành công |
| 10 | 6 hiệp hội chưa có web-hội riêng | Chọn 1 chuyên khoa ưu tiên | Bác sĩ chọn, tôi làm |
| 5 | Wiley TDM chặn IP | Thử lại từ mạng bệnh viện | CHỈ bác sĩ |
| 6 | BTS/Thorax/NICE | Chọn: chấp nhận / xin giấy phép NICE | CHỈ bác sĩ |
| 7 | Cục QL Dược VN | Tự mở thử domain, báo lại | Bác sĩ trước, tôi sau |
| 8 | Epistemonikos | Xác nhận giữ nguyên hay đổi ý | Bác sĩ |
| 9 | Wiley MCP | Cấp quyền nếu thấy giá trị | Bác sĩ |
| 11 | UpToDate/DynaMed/Embase | Không có việc kỹ thuật | — |

**Cần bác sĩ kiểm chứng.**
