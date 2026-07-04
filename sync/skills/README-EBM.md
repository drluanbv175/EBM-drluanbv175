# Skill khoa học (bản điều chỉnh EBM-VN)

Bộ skill này được chọn lọc & điều chỉnh từ **scientific-agent-skills** của K-Dense Inc.
(148 skill gốc, bản v2.53.0) cho **bác sĩ EBM ngoại trú Việt Nam**, theo quy ước trong `CLAUDE.md`.

## Đã chọn 21 skill (bỏ ~127 skill tin sinh học/lý/hóa/omics không liên quan)

### Đợt 1 — truyền thông khoa học & lâm sàng

| Skill | Công dụng | Nguồn dữ liệu |
|---|---|---|
| `research-lookup` | Tra cứu nhanh y văn | **PubMed E-utilities (miễn phí)** — đã viết lại |
| `paper-lookup` | Tìm bài đa CSDL mở | PubMed/PMC/bioRxiv/OpenAlex... (REST miễn phí) |
| `citation-management` | Quản lý trích dẫn, BibTeX | PubMed + Google Scholar (miễn phí) |
| `literature-review` | Tổng quan có hệ thống (PICO/PRISMA) | PubMed (đã chuyển từ parallel-cli trả phí) |
| `clinical-decision-support` | Tài liệu hỗ trợ quyết định (GRADE) | LaTeX/PDF |
| `clinical-reports` | Case report (CARE), SOAP, báo cáo | template |
| `treatment-plans` | Kế hoạch điều trị ngắn gọn | LaTeX/PDF |
| `scientific-writing` | Viết bản thảo IMRAD | CONSORT/STROBE/PRISMA |
| `statistical-analysis` | Chọn test, cỡ mẫu, báo cáo APA | hướng dẫn |
| `peer-review` | Bình duyệt theo checklist | hướng dẫn |

### Đợt 2 (2026-07-04) — phương pháp nghiên cứu, bổ sung cho cụm agent G0–G9

Không trùng chức năng với 10 skill đợt 1 hay với 48 agent `.claude/agents` — đây là
**động cơ tính toán chạy được** (script Python) mà agent tương ứng mới chỉ mô tả cách làm,
chưa tự chạy.

| Skill | Công dụng | Bổ sung cho agent/cổng | Đã cắt gì so với gốc |
|---|---|---|---|
| `statistical-power` | Cỡ mẫu/power — công thức đóng + mô phỏng Monte Carlo (cluster-RCT, sống còn, mixed model...) | `co-mau-nghien-cuu` (G3) | không có gì để cắt (sạch) |
| `experimental-design` | Ngẫu nhiên hóa, phân khối, factorial/DOE, crossover, Latin square | `thiet-ke-nghien-cuu` (G1) | không có gì để cắt (sạch) |
| `statsmodels` | Chạy mô hình thật: OLS/GLM/mixed/ARIMA + chẩn đoán | `phan-tich-thong-ke` (G6) | không có gì để cắt (sạch) |
| `scikit-survival` | Sống còn/time-to-event: Cox, Random Survival Forest, nguy cơ cạnh tranh | `phan-tich-thong-ke` (G6) | không có gì để cắt (sạch) |
| `scientific-critical-thinking` | Khung thẩm định GRADE/Cochrane RoB, thiên kiến, ngụy biện | `tham-dinh-phe-binh`, `tham-dinh-grade-nnt` | gỡ nhánh vẽ sơ đồ bằng AI trả phí (OpenRouter) |
| `venue-templates` | Template LaTeX tạp chí/hội nghị/poster/grant + CONSORT/STROBE/PRISMA | `viet-ban-thao`, `nop-bai-phan-hoi` (G7) | xóa hẳn 2 script vẽ sơ đồ AI trả phí (Nano Banana/OpenRouter) |
| `exploratory-data-analysis` | Soi cấu trúc/chất lượng 1 file dữ liệu (200+ định dạng) → báo cáo markdown | `quan-ly-du-lieu` (G5) | không có gì để cắt (sạch) |
| `database-lookup` | Truy vấn 78+ CSDL công khai có provenance (PubChem, ClinicalTrials.gov, dbSNP...) | `tra-cuu-chung-cu` + agent nghiên cứu | không có gì để cắt (sạch) |

Cả 8 skill đợt 2 đã qua xác minh độc lập: quét từ khóa API trả phí
(`OPENROUTER`/`parallel.ai`/`Perplexity`/`Nano Banana`) trên toàn bộ file = 0 kết quả còn sót,
mọi script `.py` biên dịch sạch (`py_compile`), số file khớp nguồn (trừ 2 file đã chủ động xóa
ở `venue-templates`).

### Đợt 3 (2026-07-04) — Nhóm B: đánh giá định lượng, hình thức hóa giả thuyết, ML lâm sàng

Đã cân nhắc kỹ hơn đợt 2 (ban đầu xếp "Nhóm B — cân nhắc") vì có phụ thuộc API trả phí một
phần hoặc chồng lấn một phần với agent hiện có — cả 3 sau khi khảo sát chồng lấn (đọc code
thật của agent + tool tự động) đều xác nhận **BỔ SUNG**, không trùng lặp.

| Skill | Công dụng | Bổ sung cho agent/cổng | Đã cắt gì so với gốc |
|---|---|---|---|
| `scholar-evaluation` | Chấm điểm ĐỊNH LƯỢNG 8 chiều học thuật (0-5, có trọng số, bar chart) | `binh-duyet` (G8) — `run_g8_auto.py` chỉ đếm nhị phân "X/30 mục" | xóa hẳn 2 script vẽ sơ đồ AI trả phí (Nano Banana/OpenRouter) |
| `hypothesis-generation` | Sinh giả thuyết cạnh tranh + cơ chế + chấm 7 tiêu chí chất lượng (testability/falsifiability...) | `cau-hoi-nghien-cuu` (G0) → `thiet-ke-nghien-cuu` (G1) | xóa hẳn 2 script vẽ sơ đồ AI trả phí; sau khi xóa không còn `scripts/` — thuần references + template LaTeX |
| `pyhealth` | Pipeline ML lâm sàng (MIMIC/eICU/OMOP) + tra/đối chiếu mã ATC/NDC/RxNorm/CCS | `mo-hinh-tien-luong` (nhánh ML của M5) + `ke-don-an-toan`/`ke-don-an-toan-benh-man` (mã thuốc) | không có gì để cắt (sạch); nặng — cần cài PyTorch (`uv add pyhealth`) nếu muốn train model thật, KHÔNG cần cài gì để chỉ tra InnerMap/CrossMap |

`scholar-evaluation`: script `calculate_scores.py` đã CHẠY THẬT với dữ liệu mẫu (8 điểm 1-5),
đối chiếu tay khớp 100% (trung bình có trọng số 3.90/5.00 → "Good", đúng công thức
`DEFAULT_WEIGHTS`). `hypothesis-generation`/`pyhealth`: xác nhận sạch API trả phí + số file
khớp nguồn; `pyhealth` không chạy thật (cần cài PyTorch, quá nặng cho việc xác minh — chỉ
soát cú pháp `starter_pipeline.py` và tính nhất quán tài liệu).

## Đã sửa gì so với bản gốc

1. **Việt hóa kích hoạt:** trường `description` của mỗi `SKILL.md` viết lại bằng tiếng Việt
   để skill tự nhận diện đúng ngữ cảnh bác sĩ.
2. **Khối "QUY TẮC EBM BẮT BUỘC"** (đánh dấu `<!-- EBM-VN-GUARD -->`) chèn đầu mỗi
   `SKILL.md`, GHI ĐÈ hành vi: đầu ra tiếng Việt · disclaimer "⚠️ Cần bác sĩ kiểm chứng" ·
   ghi nguồn PMID/DOI · không bịa · không lưu PII · chỉ nguồn miễn phí.
3. **Thay API trả phí bằng PubMed miễn phí:**
   - `research-lookup`: viết lại hoàn toàn, dùng `scripts/pubmed_lookup.py` (E-utilities,
     có retry, comment tiếng Việt). Đã xóa code parallel.ai/Perplexity/OpenRouter.
   - `literature-review`: đoạn tìm kiếm chuyển sang `pubmed_lookup.py` + paper-lookup;
     sơ đồ ưu tiên **Mermaid** (miễn phí) thay vì hình AI trả phí.
4. **Giữ nguyên** phần kỹ thuật tiếng Anh (template LaTeX, references, công cụ kiểm tra) —
   chất lượng cao; khối EBM ở trên ép tạo **đầu ra tiếng Việt** đúng quy tắc.

> **Lưu ý:** Phần thân tiếng Anh của các skill lớn (clinical-*, treatment-plans...) chưa
> dịch từng dòng — khối EBM đầu file đã điều khiển hành vi/đầu ra sang tiếng Việt. Nếu
> muốn dịch trọn vẹn thân của một skill cụ thể, báo tên skill đó.

## Cài / đồng bộ (theo cơ chế hub OneDrive)

- **Mac/Linux:** `bash sync/link-skills.sh`
- **Windows:** bấm đúp `sync/link-skills.cmd` (tạo junction, không cần admin)

Script tạo symlink/junction từ `sync/skills/<tên>` → `~/.claude/skills/<tên>`. OneDrive
tự sync nội dung hub; mỗi máy chạy script 1 lần để tạo liên kết cục bộ. Idempotent.

Sau đó mở `claude` và mô tả nhu cầu bằng tiếng Việt (vd *"tổng quan y văn về SGLT2i
trong suy tim"*, *"viết case report theo CARE"*) — skill phù hợp sẽ tự kích hoạt.

## Tùy chọn: NCBI API key (không bắt buộc)

Tăng giới hạn PubMed 3→10 req/s. Đặt trong `.env` (KHÔNG hardcode):
`NCBI_API_KEY=...` và `NCBI_EMAIL=...` — lấy free tại NCBI account settings.

## Yêu cầu hệ thống

- Python 3 + `requests` (cho pubmed_lookup.py) — đã có sẵn trên Mac này.
- (Tùy chọn) LaTeX/`xelatex` nếu muốn xuất PDF từ clinical-*/treatment-plans/scientific-writing/venue-templates.
  Không có LaTeX vẫn xuất được nội dung Markdown/`.tex`.
- (Tùy chọn, đợt 2) Nếu muốn THỰC SỰ CHẠY script — không chỉ đọc hướng dẫn — của
  `statistical-power`/`experimental-design`/`exploratory-data-analysis`: cần thêm
  `scipy`, `statsmodels`, `pingouin`, `numpy`, `pandas` (xem `compatibility:` trong
  từng `SKILL.md` để biết chính xác). `statsmodels`/`scikit-survival`/`database-lookup`
  chỉ gồm tài liệu tham khảo (`references/`), không có script — dùng làm hướng dẫn
  agent tự viết code khi cần, không cài thêm gì.
- (Tùy chọn, đợt 3) `scholar-evaluation`: `scripts/calculate_scores.py` chỉ dùng thư viện
  chuẩn Python (json/argparse/pathlib) — không cần cài gì thêm. `pyhealth`: chỉ đọc
  `references/medcode.md` (InnerMap/CrossMap tra mã) không cần cài gì; nhưng nếu muốn
  THỰC SỰ TRAIN một mô hình theo `assets/starter_pipeline.py` thì cần Python ≥3.12,<3.14
  + `uv add pyhealth` (kéo theo PyTorch — nặng, cần mạng, chưa kiểm chứng chạy thật trong
  dự án này). `hypothesis-generation`: thuần tài liệu + template LaTeX, không cần cài gì.
