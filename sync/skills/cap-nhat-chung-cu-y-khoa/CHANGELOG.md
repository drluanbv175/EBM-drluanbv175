# Changelog

## v1.15.0 — 2026-08-13

- **Quét theo TÊN TẠP CHÍ, không chỉ theo chủ đề.** Watchlist cũ có 11 nhóm/45 từ khoá, tất cả
  theo chủ đề — một bài NEJM/Lancet quan trọng về chủ đề ngoài 45 từ khoá đó sẽ không bao giờ
  được tìm thấy. Thêm 2 nhóm/8 truy vấn PubMed: **"Tạp chí hàng đầu"** (NEJM · Lancet · JAMA ·
  BMJ · Annals of Internal Medicine, lọc theo `[ta]` + publication type đổi thực hành) và
  **"Tổng quan hệ thống & khuyến cáo"** (Cochrane · NICE · USPSTF). Watchlist: 13 nhóm/53 truy vấn.
  Cả 8 truy vấn đã kiểm chạy thật.
- **Vì sao KHÔNG dùng RSS cho các nguồn này:** đã kiểm 10 feed ứng viên ngày 13/08 — tất cả bị
  chặn (Lancet/Annals/Cochrane/NICE/CHEST 403; USPSTF/Circulation/Diabetes Care/Blood 404). Nhà
  xuất bản chặn truy cập tự động. Ghi vào `references/13-source-universe.md` để không ai "sửa"
  bằng cách thêm lại RSS.
- **Lọc nhiễu cảnh báo cơ quan quản lý.** Feed `fda_recalls` trả toàn bộ thu hồi của FDA (thực
  phẩm, thiết bị, mỹ phẩm, thức ăn thú cưng, thuốc) nhưng gắn nhãn "An toàn thuốc" cho CẢ FEED.
  Đo bản tin 13/08: 40 mục "cảnh báo an toàn thuốc" gồm 6 thực phẩm + 4 thiết bị; cảnh báo thật
  đáng đọc (domperidone — chống chỉ định mới ở u tuỷ thượng thận, MHRA) bị chôn giữa thu hồi
  salsa. Nay `phan_loai_canh_bao()` phân loại TỪNG MỤC theo đường dẫn rồi từ khoá, tách 25% nhiễu.
  Nguyên tắc: **không chắc thì giữ là THUỐC** — có phép thử chống bỏ sót cho domperidone,
  morphine, valsartan/NDMA, montelukast.

## v1.14.0 — 2026-08-12

- **Cổng nguồn `--strict-sources` nay CHẠY THẬT trong dây chuyền một lệnh.** Trước đây
  `DESIGN-SPEC.md` §6 đòi `--online --strict-sources` từ đầu, nhưng `xuat_goi_cap_nhat.py` chỉ chạy
  `--online`, nên nhóm luật mạnh nhất nằm im. Nay bước ①-bis chạy thêm `--strict-sources` và tách
  hai loại lỗi: lỗi AN TOÀN (`decision='apply'` trên chứng cứ yếu/không phân hạng) ⇒ CHẶN XUẤT, mã
  thoát 3; thiếu `DATA.standards` ⇒ chỉ cảnh báo (bản cũ ra đời trước khi có khối này; bịa hợp đồng
  nguồn cho một lần tìm kiếm đã xảy ra chính là bịa provenance).
- **Vá lỗi che 73 mục nguy hiểm.** `verify_dashboard.py` `return` NGAY khi thiếu `DATA.standards`,
  nên toàn bộ luật an toàn cấp item CHƯA TỪNG chạy trên 47 dashboard. Cổng báo đúng "1 lỗi cứng" và
  người đọc kết luận "chỉ thiếu siêu dữ liệu, nội dung không sai" — một ảo ảnh của return sớm. Sau
  khi bỏ return, đo lại 61 dashboard: **73 mục `apply` trên chứng cứ yếu/không phân hạng, trên 16
  dashboard** (trước chỉ thấy 4). Bài học ghi vào SKILL.md: đọc kết quả cổng phải hỏi "cổng đã chạy
  tới luật nào", không chỉ đếm số lỗi.
- Đồng bộ `tools/verify_dashboard.py` cho khớp `EBM-Dashboards/tools/` và `EBM_MASTER/skill_assets/`
  (topology 3 bản — trước đó bản vá chỉ nằm ở một nơi, nên skill chạy bản chưa vá).

## v1.12.5 — 2026-07-15

- **Siết cổng nguồn chứng cứ để giảm nhu cầu bác sĩ tự dò từng nguồn.** Thêm `--strict-sources` cho
  `tools/verify_dashboard.py`: bắt `DATA.standards`, ngày tìm kiếm/cập nhật còn mới, ≥2 nguồn tìm
  kiếm, thứ bậc nguồn, chuẩn báo cáo, công cụ thẩm định, `references[]`, và chặn `decision='apply'`
  nếu chứng cứ yếu/không phân hạng/chỉ dựa đồng thuận. Khi chạy `--online --strict-sources`, cảnh báo
  PMID lạc đề/sai năm hoặc DOI chưa xác minh được được nâng thành lỗi cứng.
- Evidence Workbench hiển thị rõ trạng thái "Xác minh tự động nguồn" và yêu cầu
  `verify_dashboard.py --online --strict-sources` PASS trước phát hành. Lưu ý: cổng này giảm việc dò
  nguồn thủ công, nhưng không thay bác sĩ duyệt áp dụng cho bệnh nhân thật.

## v1.12.3 — 2026-07-11

- **Sửa `drug_safety_scan.py` gán nhầm cảnh báo đặc hiệu tramadol cho opioid khác (audit đối kháng
  2026-07-10).** Vòng lặp in chỉ hiển thị tên thuốc CANONICAL (`drug`), không hiển thị bí danh THỰC SỰ
  khớp (`found`) — dashboard nhắc đến fentanyl/morphine/oxycodone/codeine bị báo là "⚑ tramadol" kèm
  cảnh báo hạ ngưỡng co giật & hạ natri/serotonin CHỈ đặc hiệu cho tramadol (cơ chế serotonergic kép),
  không áp dụng cho các opioid thuần mu-agonist khác.
  - `drug_flags.json`: tách entry "tramadol" (giữ cảnh báo đặc hiệu) khỏi entry mới "opioid (khác
    tramadol)" (codeine/morphine/oxycodone/fentanyl — chỉ giữ cảnh báo CHUNG nhóm opioid: té ngã/sảng/táo bón).
  - `drug_safety_scan.py`: in kèm bí danh thực khớp khi khác tên canonical, vd "opioid (khác tramadol)
    (khớp: fentanyl)".
  - Đồng bộ 4 bản (`sync/skills/cap-nhat-chung-cu-y-khoa`, `sync/skills/dark-analyst`,
    `EBM-Dashboards/tools+data`, `EBM_MASTER/skill_assets`) — md5 khớp tuyệt đối.

## v1.12.2 — 2026-07-11

- **Vá doc-drift (audit đối kháng 2026-07-10):** README.md "## Phiên bản" đứng yên ở v1.3.0 trong khi
  SKILL.md đã v1.12.1 — bỏ danh sách phiên bản tay, trỏ về CHANGELOG.md (một nguồn duy nhất); mục
  "Web Dashboard kèm theo" còn mô tả mô hình cũ Clinical Quick View → cập nhật đúng mẫu mặc định
  hiện hành "Evidence Workbench" + chuỗi tự động 5D/5E. SKILL.md §9 bổ sung `EBM_MASTER/tools/sync_all.py`
  và `EBM-Dashboards/tools/reskin_dashboards.py` (2 phụ thuộc ngoài thư mục skill, đã được §5D/§4 dẫn
  chiếu là bắt buộc nhưng chưa từng liệt kê trong tài nguyên kèm theo).
- Đồng bộ luôn `sync/skills/dark-analyst/tools/verify_dashboard.py` (lệch sha256 từ 2026-06-21, thiếu
  toàn bộ `--check-topic`) + bổ sung `check_topic_relevance.py` còn thiếu ở đó.

## v1.12.1 — 2026-07-05

- **Đồng bộ verifier lệch giữa bản chạy thật và bản phân phối skill.** Kiểm tính đồng bộ phát hiện `tools/verify_dashboard.py` bản RUNTIME (`EBM-Dashboards/tools/`, 2026-07-02) đã được nâng cấp thêm cờ opt-in `--check-topic` + module phụ `check_topic_relevance.py`, nhưng bản trong skill (`sync/skills/.../tools/`) và hub (`EBM_MASTER/skill_assets/`) vẫn là snapshot cũ 2026-06-21 → cùng một dashboard có thể qua cổng liêm chính này nhưng khác kết quả ở cổng kia.
  - Back-port bản mới về **cả 3 nơi** (skill/tools · skill_assets · runtime) → md5 khớp tuyệt đối; bổ sung `check_topic_relevance.py` vào skill + skill_assets (trước chỉ có ở runtime).
  - `--check-topic`: LLM chấm item có lạc chủ đề/chuyên khoa dashboard không (lấp khoảng trống cổng kỹ thuật — vd bài sản/nhi lọt vào dashboard Tim mạch, sự cố thật `TimMach_20260609`). CHỈ cảnh báo, không chặn cứng; thiếu `ANTHROPIC_API_KEY` → bỏ qua êm.
  - Cập nhật SKILL.md §5D(a) + §9 khai báo cờ mới và tool mới. py_compile PASS; audit tổng PASS.
  - Ghi nhận điểm mù: `tools/audit_ebm_system.py` chỉ so template HTML, CHƯA so khớp các bản `.py` tool giữa 3 nơi — drift này lọt qua "Template sync: PASS".

## v1.12.0 — 2026-06-10

- **Sửa mất cân đối bố cục dọc** (bác sĩ báo: dashboard hiện tại vẫn chưa cân đối). Nguyên nhân thật: khối **GRADE Evidence-to-Decision là băng LUÔN hiển thị, rất cao ở đầu trang** → ép bảng chứng cứ (nội dung chính) thành dải mỏng ở đáy. (grep markers PASS nhưng mắt thấy lệch → đã kiểm chứng bằng ảnh chụp thực tế.)
  - *Evidence Workbench:* chuyển GRADE EtD từ băng đầu trang → **một TAB "⚖ GRADE EtD"** ở khu giữa (chỉ hiện khi có `etd`). Bảng giờ chiếm phần lớn màn hình. Thêm trần chiều cao thẻ tóm tắt (`max-height:188px;overflow:auto`) chống dữ liệu dài làm phình băng Quick View.
  - *Dark Analyst:* bọc GRADE EtD trong `<details>` **thu gọn mặc định** (bấm để mở) → còn 1 dòng thay vì băng to.
- Đồng bộ 2 template (EW+DA) qua 4 bản skill; **ghép lại 11 dashboard đã xuất** trong `EBM-Dashboards/` (giữ nguyên `DATA`); dựng lại 2 zip.
- Verify trực quan (1440×900): bảng chứng cứ là khu vực chính, EtD truy cập qua tab/details. Mặc định vẫn **Evidence Workbench**.

## v1.11.0 — 2026-06-09

- **Bố cục Dashboard responsive (cân đối mọi bề ngang)** — khắc phục "phần dưới hẹp, khó xem" trên màn ~1000px.
  - *Evidence Workbench:* lưới `clamp()`+`minmax(0,1fr)` (cột giữa `min-width:0`); ≤1199px panel thẩm định thành **ngăn kéo (drawer)** trượt từ phải (nền mờ + nút ✕) → bảng dùng trọn bề ngang; ≤820px bộ lọc thành dải ngang + ẩn cột Forest; ≤540px dồn 1–2 cột. Thêm `select`→`openDrawer`/`closeDetail`.
  - *Dark Analyst:* KPI/EtD/Quick-View tự giãn cột theo breakpoint; ≤860px chi tiết bung DỌC (`exp-in` 1 cột).
- Đồng bộ CẢ HAI template (EW + DA) qua 4 bản: `sync/skills/{cap-nhat,dark-analyst}` + bản live; dựng lại zip.
- Đã ghép layout mới cho các dashboard EW đã xuất trong `EBM-Dashboards/` (giữ nguyên khối `DATA`).
- Mặc định vẫn là **Evidence Workbench**. Verify trực quan ở 1000/1280/1440px PASS.

## v1.10.0 — 2026-06-07

- **Đổi mẫu MẶC ĐỊNH về "Evidence Workbench"** (nền sáng) theo lựa chọn của bác sĩ; **Dark Analyst** (nền tối) chỉ dùng KHI bác sĩ yêu cầu.
- **Thêm khối GRADE Evidence-to-Decision (EtD) vào template Evidence Workbench** (light theme) — nay CẢ HAI mẫu đều có EtD (field `etd`); tách rõ hàng chứng cứ-từ-nguồn vs đánh giá-vận-hành. JS cân bằng, gate PASS.
- **TỰ ĐỘNG khi gọi skill:** mỗi lần skill được gọi → tự chạy trọn dây chuyền (dựng Dashboard EW → cổng liêm chính `--online` → an toàn thuốc nếu liên quan → thư viện → 3 phái sinh), không cần yêu cầu từng bước. Ghi trong SKILL.md 5A + CLAUDE.md.
- Cập nhật checklist, danh mục tài nguyên, DESIGN-SPEC; đồng bộ template (mockup + skill).

## v1.9.0 — 2026-06-07

- **Sản phẩm phái sinh TỰ ĐỘNG mỗi lần chạy:** `tools/make_derivatives.py` sinh tờ dặn người bệnh + dàn ý slide (faithful, giữ PMID/GRADE) + kịch bản TikTok vào `EBM-Dashboards/derivatives/`. Video TikTok thật để bác sĩ gọi skill `tao-video-tiktok` khi cần. (Đã test trên ca thần kinh ĐTĐ.)
- **GRADE Evidence-to-Decision (EtD) trong Dashboard Dark Analyst:** thêm field tùy chọn `etd` (vấn đề · lợi ích · tác hại · độ chắc chắn · giá trị · cân bằng · nguồn lực · công bằng · chấp nhận · khả thi → khuyến cáo + độ mạnh). Tách rõ **hàng chứng cứ (từ nguồn) vs hàng đánh giá vận hành**; tương thích ngược (không có `etd` thì không hiển thị). Đã thêm CSS + render + ví dụ thật; JS cân bằng; gate vẫn PASS.
- Cập nhật SKILL.md (5D), checklist, tài nguyên; đồng bộ template (mockup + skill + standalone).

## v1.8.0 — 2026-06-07

- **Mục 5E + 3 nâng cấp** (theo yêu cầu bác sĩ):
  - **#5 Lớp phủ an toàn thuốc:** `tools/drug_safety_scan.py` + `data/drug_flags.json` (cờ Beers 2023/STOPP-START v3 cô đọng, có nguồn, KHÔNG đầy đủ) → quét thuốc trong dashboard, sinh prompt rà soát đầy đủ bằng skill `nguoi-cao-tuoi-da-benh-da-thuoc`. Ref 09. (Đã test: bắt amitriptyline/gabapentin/opioid.)
  - **#6 Giám sát định kỳ (Track B):** `tools/surveillance_scan.py` + `EBM-Dashboards/watchlist.json` → quét PubMed tìm guideline/SR/meta/RCT mới theo chủ đề lõi, báo cáo ứng viên để thẩm định. Ref 10. (Đã test: trả về chứng cứ 2026 thật.)
  - **#7 Bản địa hóa BYT:** `EBM-Dashboards/vn-guidelines/registry.json` + README → đối chiếu quốc tế ↔ hướng dẫn Bộ Y tế (do bác sĩ cung cấp, không bịa số QĐ), nối `clinical-evidence-rag`. Ref 11.
- Cập nhật checklist (lớp phủ an toàn thuốc) và danh mục tài nguyên.

## v1.7.1 — 2026-06-07

- **Thư mục chung tích lũy `EBM-Dashboards/`** (mục 5D-d + CLAUDE.md): mọi dashboard xuất vào một thư mục duy nhất trong OneDrive (tự đồng bộ Mac↔Windows), kèm `evidence-library.html` + `library.json` + bản sao `tools/` + `README.md`. Quy trình mỗi cập nhật: lưu vào thư mục → `verify_dashboard.py --online` PASS → `build_library.py add` để tích lũy vào chỉ mục.

## v1.7.0 — 2026-06-07

- **Thêm mục 5D + bộ công cụ `tools/`** (3 nâng cấp workflow theo yêu cầu bác sĩ):
  - **Cổng kiểm liêm chính** `tools/verify_dashboard.py`: kiểm mọi item có PMID/DOI, `gradeLevel`/`decision` hợp lệ, có disclaimer, quét PII; `--online` **tự xác minh mỗi PMID phân giải đúng trên PubMed** (chống trích dẫn ảo). Đã test: PASS/FAIL/âm tính + online xác minh thật.
  - **Thư viện cập nhật** `tools/build_library.py`: gom mọi dashboard vào `library.json` + sinh `evidence-library.html` (chỉ mục có tìm/lọc, mở thẳng từng bản).
  - **Sản phẩm phái sinh**: `references/08-xuat-san-pham-phai-sinh.md` + mẫu `templates/phai-sinh-to-dan-nguoi-benh.md`, `templates/phai-sinh-kich-ban-tiktok.md` (tờ dặn người bệnh / slide / TikTok — giữ liêm chính, không liều cho người bệnh/TikTok, có disclaimer, không PII).
- Cập nhật checklist (chạy cổng liêm chính trước khi giao) và danh mục tài nguyên.

## v1.6.0 — 2026-06-07

- **Đổi mẫu Web Dashboard MẶC ĐỊNH sang "Dark Analyst"** (nền tối, dày dữ liệu) theo lựa chọn của bác sĩ; Evidence Workbench (nền sáng) trở thành mẫu THAY THẾ.
- **Sản phẩm hóa Dark Analyst thành template tham số hóa** `templates/web-dashboard-dark-analyst.html`: chrome (tiêu đề, PICO chips, KPI, băng Clinical Quick View, verdict, bộ lọc, ô tìm) **tự sinh từ `DATA`**; bảng có cột Quyết định; click bung 3 cột thẩm định; hỗ trợ mọi loại thiết kế & mức GRADE.
- **Hai mẫu DÙNG CHUNG một schema `DATA`** (meta/summary/items[]) → một khối dữ liệu chạy được cả hai. Dark Analyst thêm field tùy chọn `effectText` (hiệu số phi-tỷ-số) và `rob` (RoB 2, chỉ RCT); giữ `frame`/`frameLabels`.
- Cập nhật SKILL.md (mục 5A, checklist, danh mục tài nguyên), `CLAUDE.md`, `DESIGN-SPEC.md` và đóng gói lại.

## v1.5.0 — 2026-06-07

- **Thêm mục 5C "Tự chọn khung câu hỏi"**: skill tự nhận diện loại câu hỏi lâm sàng và chọn khung phù hợp — ngoài **PICO(T)(S)** còn **PECO** (tác hại), **PIRT/QUADAS-2** (chẩn đoán), **PROGRESS/PICOTS** (tiên lượng), **CoCoPop** (tần suất), **SPIDER** (định tính), **ECLIPSE** (dịch vụ), PICO+chi phí (kinh tế).
- Bổ sung **mô hình tổng hợp bổ trợ**: phân tầng nguồn 6S, cân lợi ích–tác hại NNT/NNH, GRADE Evidence-to-Decision (EtD), bảng Tóm tắt phát hiện (SoF), tam giác liêm chính.
- Thêm tài liệu `references/07-mo-hinh-cau-hoi-va-khung-thay-the.md` (bảng chọn khung + cách ánh xạ vào Evidence Workbench + ví dụ).
- **Nâng template Evidence Workbench** (tương thích ngược): hỗ trợ field tùy chọn `frame` (nhãn khung) và `frameLabels` để đổi tên 4 ô P/I/C/O cho khung không phải PICO; không đặt thì hiển thị như cũ.
- Cập nhật checklist (nhận diện & nêu rõ khung đã dùng) và danh mục tài nguyên.

## v1.4.0 — 2026-06-07

- **Đổi mô hình Web Dashboard mặc định sang "Evidence Workbench"** (bố cục 3 cột: bộ lọc · Quick View + bảng điểm chứng cứ · panel thẩm định) theo lựa chọn của bác sĩ.
- Thêm template mặc định `templates/web-dashboard-evidence-workbench.html` (chỉ cần thay khối `DATA`); giữ template một-cột cũ làm fallback.
- Ba lớp nội dung bắt buộc giữ nguyên, ánh xạ vào bố cục: Clinical Quick View = băng tóm tắt + tab mặc định; Evidence Detail View = cột phải; Safety/Limits/VN = các tab riêng.
- Cập nhật bảng màu mặc định (nền sáng, dày dữ liệu) + màu ngữ nghĩa theo Quyết định/GRADE/Thiết kế; bổ sung forest plot mini và xuất CSV/JSON.
- Cập nhật mục 5A, frontmatter, checklist, danh mục tài nguyên, `references/05-…md` và `quality/web-dashboard-acceptance-checklist.md`.

## v1.3.0 — 2026-06-06

- Bổ sung **chế độ PICO**: chuẩn hóa trình bày chứng cứ theo P–I–C–O cho câu hỏi về hiệu quả/an toàn của can thiệp, kèm khối PICO 5 dòng (PICO + chứng cứ tốt nhất + grading từ nguồn + kết luận).
- Thêm mục 5B trong SKILL.md và tài liệu `references/06-pico-va-trich-dan.md` với mẫu, ví dụ và quy tắc liêm chính (trích hiệu số đúng nguồn, không tự gán GRADE, nêu cả hai chiều khi chứng cứ không đồng nhất).
- Thêm **quy tắc ghi nguồn sạch**: ghi nguồn dạng văn bản (tác giả/tổ chức + năm + tạp chí) và Vancouver/NLM; tuyệt đối không chèn thẻ markup trích dẫn thô/mã kỹ thuật vào câu trả lời; bắt buộc rà soát trước khi gửi.
- Bổ sung mục checklist tương ứng và cập nhật danh mục tài nguyên.

## v1.2.0 — 2026-06-02

- Bắt buộc tạo Web Dashboard HTML độc lập cho mỗi cập nhật EBM theo vấn đề cụ thể khi môi trường hỗ trợ tạo file.
- Áp dụng kiến trúc 3 lớp: Clinical Quick View mặc định, Evidence Detail View, Safety/Limits/Vietnam.
- Thêm schema record `ITEM-xx` cục bộ; không đồng nghĩa với ID Dashboard Master.
- Thêm template HTML tương tác có tìm kiếm, lọc, panel chi tiết, xuất CSV và tab kiểm chứng thao tác.
- Giữ nguyên nguyên tắc: chỉ tích hợp Dashboard Master/CỔNG A-B khi bác sĩ yêu cầu rõ.


## v1.1.0 — 2026-06-02

- Định nghĩa lại phạm vi: cập nhật chứng cứ cho **vấn đề lâm sàng cụ thể khi bác sĩ yêu cầu**.
- Không bắt buộc Dashboard, Web Dashboard, CỔNG A/B hoặc mã quản trị trong câu trả lời EBM thông thường.
- Bổ sung 4 tài liệu reference nội bộ còn thiếu.
- Bổ sung hai template đầu ra: nhanh và chuyên sâu.
- Bổ sung checklist nghiệm thu chất lượng.
- Tách chế độ an toàn thuốc, antibiotic stewardship, thang điểm/công cụ và thẩm định nguồn.
