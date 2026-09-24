# Tổng hợp TRUNG THỰC — nguồn chứng cứ đã kết nối & khả năng đọc toàn văn (23/09/2026)

> Trả lời câu hỏi của bác sĩ: «phủ các nguồn chứng cứ đến đâu, và đọc toàn văn được từ
> đâu — cho tôi cái nhìn tổng quát trung thực nhất». Mọi con số dưới đây đếm trực tiếp
> từ `data/sources.json` (36 mục, cập nhật hôm nay) và mã đang sống — không suy diễn,
> không lấy từ trí nhớ huấn luyện. Nối tiếp `audit/07-tong-kiem-do-phu-nguon-chung-cu_
> 2026-08-30.md` (24 ngày trước) — mục §6 nói rõ cái gì đã đổi từ đó tới nay.

## Kết luận ngắn — 3 dòng

1. **Tầng KHÁM PHÁ (biết bài/khuyến cáo nào tồn tại):** rộng, khỏe — 28/36 nguồn `active`,
   phủ 20 hiệp hội chuyên khoa qua Crossref theo tiêu đề, cộng PubMed/Europe PMC/Crossref/
   OpenAlex/Scopus/CORE làm 4 lớp đối chiếu độc lập.
2. **Tầng ĐỌC TOÀN VĂN TỰ ĐỘNG (không cần người can thiệp):** hẹp — **CHỈ 2 tổ chức thật
   sự đọc được toàn văn tự động và đã kiểm sống thành công: GOLD, GINA.** Ngoài ra có 1
   nguồn "đọc được về nguyên tắc nhưng bị chặn IP" (Wiley TDM) và 2 nguồn "code xong nhưng
   bị chặn vĩnh viễn ở tầng mạng/pháp lý, không sửa được" (PMC, BTS/Thorax/NICE).
3. **Tầng ĐỌC TOÀN VĂN TƯƠNG TÁC (cần một phiên Claude Code, người/agent gọi tay):**
   Cochrane, Scite, và **PubMed full-text MCP — đã kiểm thật với cỡ mẫu 9 bài (3 nghiên
   cứu + 5 guideline có PMCID), KHÔNG bị chặn WAF như đường scrape trực tiếp SRC-046.**
   Nghiên cứu gốc: 3/3 có toàn văn. Guideline: chỉ 5/18 mẫu thử có PMCID, và 2/5 trong số
   đó có toàn văn thật (ONKOPEDIA, Korean Thyroid Association — không phải 0% như đính
   chính buổi sáng kết luận vội trên 1 mẫu). Tức đây là công cụ ĐÁNG THỬ cho guideline cụ
   thể (tỷ lệ trúng thật, không phải giả), nhưng không đủ tin cậy để thay GOLD/GINA. Cả ba
   KHÔNG tham gia vòng quét tuần tự động, chỉ dùng khi tra cứu trực tiếp trong phiên.

Nói cách khác: **hệ biết RẤT RỘNG "có gì mới", nhưng chỉ ĐỌC ĐƯỢC toàn văn tự động một
phần rất nhỏ** (2/20 hiệp hội guideline). Đây không phải lỗ hổng thiết kế — là ranh giới
thật của internet công khai (bot-protection, giấy phép thương mại, chặn IP) mà không
công cụ nào vượt qua được mà vẫn giữ đúng nguyên tắc của dự án (không bịa, không lách
bot-detection, không vi phạm ToU).

---

## 1. Bức tranh tổng — BA TẦNG NĂNG LỰC KHÁC NHAU, đừng gộp làm một

Trước khi đọc bảng, cần hiểu rõ **KHÁC BIỆT SỐNG CÒN** giữa 3 loại khả năng — gộp chung
sẽ khiến "36 nguồn active" nghe như hệ đọc được toàn văn từ 36 nơi, điều đó SAI:

| Tầng | Trả về gì | Ví dụ | Tự động hóa |
|---|---|---|---|
| **① Khám phá theo tiêu đề** | tiêu đề + DOI/PMID + ngày + tóm tắt (thường RỖNG, phụ thuộc nhà xuất bản) | Crossref `crossref_title_lane` cho 20 hiệp hội | Có, chạy trong vòng quét tuần |
| **② Dò thay đổi trang** | biết "có bản mới" (tiêu đề trang đổi) | GOLD/GINA/ADA/ESC/ACC-AHA/IDSA (`html-watch`) | KHÔNG — phải người/agent tự mở phiên Browser mỗi lần |
| **③ Đọc toàn văn thật** | trích được câu chữ khuyến cáo cụ thể từ PDF/HTML | GOLD, GINA (đã kiểm sống 23/09) | Có (gọi hàm), nhưng KHÔNG nằm trong vòng quét tuần tự động — gọi theo yêu cầu |

**Chỉ tầng ③ mới trả lời được "đọc toàn văn chứng cứ" theo đúng nghĩa bác sĩ hỏi.**
Tầng ① và ② là chuẩn bị/khám phá — có giá trị thật (biết khi nào cần đọc) nhưng KHÔNG
phải đọc toàn văn.

---

## 2. Đếm theo trạng thái — 36 nguồn trong `data/sources.json`

| Trạng thái | Số lượng | Ý nghĩa |
|---|---|---|
| `active` | 28 | đang hoạt động đúng vai trò đã khai (không có nghĩa là "đọc toàn văn" — xem §1) |
| `degraded` | 2 | hoạt động đúng cơ chế nhưng có giới hạn thật (Semantic Scholar: nhịp thấp; Wiley TDM: chặn IP) |
| `not-covered` | 6 | không dùng được — có lý do cụ thể, không phải "chưa làm" |

| Kiểu truy cập (`access`) | Số lượng |
|---|---|
| `api` (gọi API thật) | 20 |
| `html-watch` (dò thay đổi trang, tầng ②) | 10 |
| `manual` (bác sĩ tự làm) | 3 |
| `rss` | 1 |
| `file` (kho ngoại tuyến) | 1 |
| `none` (không có kênh nào) | 1 |

---

## 3. TẦNG ③ — ĐỌC TOÀN VĂN THẬT: bảng đầy đủ, không giấu gì

| Tổ chức | Trạng thái | Đã kiểm sống? | Ghi chú trung thực |
|---|---|---|---|
| **GOLD** (COPD) | 🟢 `active` | ✅ 23/09/2026 — trích 200.000 ký tự (chạm giới hạn cắt) | Vá 1 lỗi thật (lấy nhầm Pocket Guide) trước khi đạt |
| **GINA** (Hen) | 🟢 `active` | ✅ 23/09/2026 — trích 200.000 ký tự | Vá 1 lỗi thật (trang đổi cấu trúc 2 bước) trước khi đạt |
| **Wiley** (mọi tạp chí Wiley, theo DOI đã biết) | 🟡 `degraded` | ✅ về mặt kỹ thuật — token hợp lệ, API phản hồi đúng — ❌ về mặt thực dụng — `ACCESS_DENIED` vì IP máy hiện tại ngoài dải IP tài khoản Wiley được cấp quyền | Chỉ hoạt động khi gọi từ mạng tổ chức đã đăng ký với Wiley (thường mạng bệnh viện) |
| **PMC** (guideline lưu trữ trên PubMed Central, dùng lại được cho nhiều hội) | 🔴 `not-covered` | ❌ Thử 23/09/2026 — chặn 403 tối giản, MỌI cách thử (UA khác nhau, API OA chính thức, OAI-PMH) đều thất bại. Đối chứng: `eutils.ncbi.nlm.nih.gov` vẫn chạy bình thường cùng lúc → đây là chặn RIÊNG của PMC, không phải chặn "misuse" đã biết trước | Ngoài tầm sửa code — chặn cấp biên mạng |
| **BTS** (British Thoracic Society) | 🔴 `not-covered` | ❌ Thử 23/09/2026 — site đã đổi cấu trúc, nội dung thật nằm ở thorax.bmj.com/bmjopenrespres.bmj.com, cả hai bị **Cloudflare Managed Challenge** (đòi JS+cookie) | Vượt qua = bypass bot-detection — hành vi tuyệt đối không được làm |
| **NICE** (đường thay thế cho một số guideline BTS đồng xuất bản) | 🔴 không xây | ❌ Kỹ thuật KHÔNG bị chặn (robots.txt cho phép, HTML sạch) nhưng điều khoản sử dụng đòi **giấy phép + phí cho mọi mục đích AI, không ngoại lệ** | Rào pháp lý — chỉ bác sĩ tự xin giấy phép mới gỡ được |

**⇒ Tổng kết tầng ③: 2 tổ chức đọc được toàn văn tự động, thật sự đã kiểm chứng (GOLD,
GINA). 1 tổ chức đọc được về nguyên tắc nhưng cần đổi mạng (Wiley). 2 tổ chức không đọc
được với công nghệ và giấy phép hiện có (PMC, BTS/Thorax/NICE).**

---

## 4. TẦNG ① — Khám phá theo tiêu đề: 20 hiệp hội, KHÔNG phải toàn văn

`app/sources/guideline_lanes.py::crossref_title_lane()` + cấu hình `_HIEP_HOI_TREN_TAP_CHI`
trong `feeds.py` — mỗi hiệp hội có ISSN tạp chí riêng + từ khóa lọc, chạy trong vòng quét
tuần (`ENABLE_GUIDELINE_FEEDS=true`, đang bật):

ACC/AHA · ESC · ADA · IDSA · EULAR · AASLD · KDIGO · ATS · ERS · BTS · AGS · ACP · ASCO ·
ESMO · ASH · AGA · ACG · AAN · AHA/ASA · ACR (20 hiệp hội).

**Giới hạn phải nhớ:** trả về **tiêu đề + DOI + ngày + `abstract` của Crossref** — trường
`abstract` này **thường RỖNG** vì phụ thuộc nhà xuất bản có nộp hay không (đã đo trực
tiếp trong phiên này). Đây là lớp "biết có bài mới ra", không phải "đọc được nội dung
khuyến cáo".

---

## 5. TẦNG ② — Dò thay đổi trang (html-watch), 10 nguồn

GOLD · GINA · KDIGO · ADA · ESC · ACC/AHA · IDSA(+AGS/USPSTF/WHO/NICE-web gộp) · USPSTF ·
WHO · Bộ Y tế VN — tất cả `active`, đã xác minh sống qua phiên Browser thật (không phải
Python tự động — nhiều domain trong nhóm này chặn Cloudflare khi gọi bằng script, ví dụ
ACC/AHA `professional.heart.org` đã ghi nhận 403 kèm cookie `__cf_bm`).

**Giới hạn kép:**
1. Chỉ biết "trang đã đổi" (tiêu đề mới xuất hiện) — không trích nội dung.
2. Phải người/agent **tự tay** mở phiên Browser mỗi lần kiểm — SRC-015 tự ghi rõ "việc
   còn lại: nối vào tác vụ lịch" (chưa tự động hóa xong).

---

## 6. Tầng liên minh bibliographic (đối chiếu độc lập) — mạnh, 8 nguồn active

PubMed E-utilities · Europe PMC · Crossref · OpenAlex · Scopus (Elsevier, nối 13/09) ·
CORE (nối 22/09) · Retraction Watch ngoại tuyến (30.851 PMID) · openFDA. Đây là tầng
XÁC MINH (PMID/DOI có thật không, có bị rút không) — không phải tầng toàn văn, nhưng là
nền tảng bắt buộc để mọi trích dẫn khác không bị bịa.

## 7. Tầng tương tác MCP (cần phiên Claude Code, không tự động)

⛔ **ĐÍNH CHÍNH cùng ngày (ngay sau khi báo cáo này công bố) — dòng "PubMed full-text"
dưới đây BAN ĐẦU xếp nhầm vào nhóm "giới hạn giống PMC/SRC-046". Đó là SUY LUẬN, chưa
từng gọi thử. Đã kiểm thật, kết quả khác hẳn — xem chi tiết ngay dưới bảng.**

| Nguồn | Vai trò | Giới hạn |
|---|---|---|
| Cochrane Library (CDSR) | tra tổng quan hệ thống Cochrane | Chỉ gọi được TỪ TRONG một phiên Claude Code — không tham gia vòng quét tuần |
| Scite | kiểm rút bài bổ sung + tally trích dẫn | Cùng giới hạn Cochrane, thêm cổng doctrine riêng |
| **PubMed (`get_full_text_article`)** | **đọc toàn văn PMC qua MCP — ĐÃ KIỂM THẬT, HOẠT ĐỘNG, và KHÔNG cùng giới hạn với SRC-046** | Xem đính chính ngay dưới — giới hạn thật khác hẳn giả định ban đầu |
| Wiley (MCP) | tìm kiếm ngữ nghĩa tạp chí Wiley | `not-covered` — server CẦN XÁC THỰC, bác sĩ chưa cấp quyền |

**Đo thật 23/09/2026 (cỡ mẫu mở rộng theo audit/14 vấn đề 3 — 9 phép thử, KHÔNG đoán
PMCID, mọi PMCID tra qua `search_articles`/`get_article_metadata` trước):**
- 3 bài nghiên cứu eLife (Gold Open Access): CẢ 3 đều trả **toàn văn thật, dài** —
  65.812 · 40.865 · 102.005 ký tự.
- 5 guideline lâm sàng thật có PMCID (tra `"Practice Guideline"[Publication Type]`,
  18 guideline được xem, chỉ 5 có PMCID — tự nó là một phát hiện: **phần lớn guideline
  chuyên khoa KHÔNG hề có bản ghi PMC**, không riêng gì chuyện toàn văn):
  - ✅ **CÓ toàn văn thật:** ONKOPEDIA (Đức) hướng dẫn xơ tủy 2025, PMC13432566, ~9.000
    từ, có bảng so sánh với NCCN · Korean Thyroid Association, quản lý ung thư giáp thể
    biệt hoá Phần II, PMC13555224, 130.334 ký tự.
  - ❌ **RỖNG:** ADA Standards of Care 2026 (PMC12690171) · American Society for
    Apheresis, Tenth Special Issue (PMC13580465) · Canadian Family Physician, cai statin
    người ≥65 tuổi (PMC13566657).

**Kết luận đúng, thay cho câu cũ (đã tự sửa 2 lần trong ngày — đây là bản CUỐI, dựa cỡ
mẫu đủ lớn để không còn là suy đoán từ 1 ca):** MCP này dùng một đường truy cập PMC
**KHÁC HẲN** đường HTML công khai (`pmc.ncbi.nlm.nih.gov`) mà `pmc_guideline_fulltext.py`
(SRC-046) dùng và bị chặn WAF — nên **KHÔNG bị chặn cùng lý do**, và nó **THẬT SỰ đọc
được toàn văn guideline lâm sàng cho một phần đáng kể trường hợp** — KHÔNG "luôn rỗng"
như đính chính buổi sáng từng kết luận vội trên 1 mẫu. Bức tranh đúng có 2 tầng lọc:
(1) guideline có PMCID hay không — chỉ ~1/4 mẫu đã thử có; (2) nếu có PMCID, có toàn văn
hay không — 2/5 mẫu đã thử có (40%). Không đủ dữ liệu để nói RÕ vì sao 2 bài thành công
mà 3 bài rỗng (có thể liên quan nhà xuất bản/tạp chí có nộp lưu XML song song với PDF
hay không) — không suy đoán thêm khi chưa đo được cơ chế thật.
**Vẫn đúng như đã ghi:** chỉ gọi được TỪ TRONG một phiên Claude Code tương tác, không
tham gia vòng quét tuần tự động — nên dù tỷ lệ thành công thật (không phải 0%), nó vẫn
KHÔNG thay được GOLD/GINA cho việc tự động hoá.

---

## 8. Không kết nối được — CÓ LÝ DO, không phải "chưa làm" (6 nguồn `not-covered`)

| Nguồn | Lý do thật |
|---|---|
| UpToDate · DynaMed · Embase | thương mại, ngoài phạm vi hợp pháp của máy — bác sĩ tra tay khi cần |
| Cục Quản lý Dược VN | `dav.gov.vn` không tới được từ môi trường phiên này qua CẢ 3 phương pháp độc lập đã thử |
| Epistemonikos | connector viết sẵn, chỉ chờ token — bác sĩ đánh giá 22/09 là KHÔNG khả thi theo đuổi (cần gửi email xin duyệt) |
| Wiley MCP | server cần xác thực OAuth, bác sĩ chưa cấp quyền (khác Wiley TDM API — đã cấp, xem §3) |
| PMC full-text | chặn mạng cấp biên, không sửa được bằng code |
| BTS/Thorax/NICE full-text | Cloudflare + giấy phép AI trả phí, không sửa được bằng code |

---

## 9. So với báo cáo gần nhất (`audit/07`, 30/08/2026) — 24 ngày đã đổi gì

Báo cáo trước đếm **8 nguồn active tầng thư viện**. Hôm nay là **28 nguồn active** trên
tổng 36. Thêm mới trong 24 ngày: Scopus · CORE · Consensus (bậc thang dự phòng) · SerpApi
Google Scholar (bậc thang dự phòng) · NICE qua Europe PMC · Cochrane MCP · Semantic
Scholar (bật lại) · Scite MCP · Wiley MCP (đăng ký, chưa cấp quyền) · **Wiley TDM API +
GOLD/GINA/BTS/PMC full-text connector (hoàn toàn mới, xây và kiểm sống trong phiên hôm
nay)**. Báo cáo trước nói "8 trạm web hội DỰNG XONG, CHỜ BẬT" — hôm nay CẢ 10 trạm đã
`active` và đã xác minh sống.

---

## 10. Giới hạn của CHÍNH báo cáo này — đừng đọc quá những gì nó chứng minh được

- Công cụ đo độ phủ chính thức của hệ (`assess_source_universe_coverage()` trong
  `app/sources/authority.py`) **CHƯA được cập nhật** để biết về 5 connector toàn văn mới
  hôm nay (GOLD/GINA/BTS/PMC/Wiley TDM full-text) — tầng `full_text_and_citation_context`
  trong taxonomy chính thức của nó chỉ liệt 4 nguồn cũ (`unpaywall`, `semantic_scholar`,
  `publisher_full_text`, `pmc_full_text`), không khớp tên connector thật vừa xây. Báo cáo
  này dùng trực tiếp `data/sources.json` thay vì chạy hàm đó, để không đưa ra một con số
  PASS/PARTIAL có thể sai vì taxonomy lạc hậu.
- Tầng `retraction_and_integrity` trong taxonomy chính thức đó tự khai "VĨNH VIỄN PARTIAL"
  theo thiết kế (cơ chế kiểm rút bài thật — `RetractionChain` 3 tầng — không tự báo cáo
  vào `healthy_sources`) — không phải dấu hiệu cơ chế rút bài yếu; cơ chế đó vẫn chạy tốt,
  đo riêng ở `tools/so_xac_minh_nguon.py`.
- "Đã kiểm sống thành công" cho GOLD/GINA nghĩa là: gọi được, trích được văn bản, ĐÚNG hôm
  nay. Cả hai trang web đều có lịch sử đổi cấu trúc (đã xảy ra ít nhất 1 lần mỗi trang
  trong vài tháng qua) — không có gì đảm bảo cấu trúc không đổi lần nữa; cần kiểm sống lại
  định kỳ, không coi "đã kiểm một lần" là vĩnh viễn đúng.

**Cần bác sĩ kiểm chứng.**
