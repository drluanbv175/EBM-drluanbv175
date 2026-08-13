# EBM Copilot — Trợ lý AI cho Bác sĩ Y học Bằng chứng

## Mục tiêu
Hệ thống tự động hóa cho bác sĩ ngoại trú thực hành EBM, gồm 3 module:
Research (nghiên cứu), Clinical (lâm sàng), Knowledge (quản lý kiến thức).

## Điều phối Agent — hành vi MẶC ĐỊNH (nguồn Claude Code `.claude/agents`, mirror Codex `.Codex/agents`/`.codex/agents`, 50 agent: 21 lâm sàng + 28 nghiên cứu + 1 guardrail dùng chung; +3 lâm sàng 2026-06-16 (dau-man-tinh·cham-soc-giam-nhe·tram-cam-lo-au); +2 lâm sàng 2026-07-04 (quan-ly-khang-dong · tham-dinh-do-chinh-xac-chan-doan))
Khi bác sĩ nêu việc lâm sàng hoặc nghiên cứu, MẶC ĐỊNH định tuyến tới "nhạc trưởng" phù hợp và để nó **tự chạy tuần tự theo Giao thức tự động** (không hỏi vặt từng bước):
- **Nêu một CA/tình huống lâm sàng** ("tôi có bệnh nhân…", "khám ca này", hỏi chẩn đoán/điều trị) → `dieu-phoi-lam-sang`: tự chạy 5 bước EBM (Hỏi→Tìm→Thẩm định→Áp dụng→Theo dõi); **cờ đỏ nêu NGAY**; dừng ở **Cổng A** (áp dụng cho BN) + **Cổng B** (ghi sổ cái).
- **Nêu một ĐỀ TÀI/câu hỏi nghiên cứu** (chỉ cần tên đề tài) → `dieu-phoi-nghien-cuu`: tự khôi phục trạng thái từ sổ cái → suy loại thiết kế → march G0→G10; dừng ở 6 cổng cứng (G2 đạo đức · G4 khóa SAP · G5 khóa dữ liệu thật · G8 bình duyệt độc lập · G9 liêm chính tác giả · G10 PI khóa gói phát hành) + nơi cần dữ liệu/phê duyệt thật. Mỗi cổng fail-closed theo đúng role (IRB/thống kê viên hoặc PI/quản lý dữ liệu hoặc PI/phản biện độc lập/PI/PI — xem `medical-ebm-automation/tools/gate_contract.py`), không chỉ "có ai đó ký".
- **Bảo đảm chuẩn nghiên cứu hiện hành:** G2 không được APPROVED nếu WHO TRDS v1.3.1 mục 13/14/19/20 thiếu dữ kiện khoa học PI đã pin hoặc tham chiếu Hội đồng chỉ là fallback; G9 không được READY nếu thiếu quyền truy cập dữ liệu/độc lập nhà tài trợ theo ICMJE 1/2026. Kiểm bằng `python tools/verify_controlled_research_automation.py`; đây là kiểm kỹ thuật, không thay IRB/PI/thống kê viên/phản biện.
- **Việc lẻ** (tra 1 câu hỏi, soát 1 danh mục TLTK, tính cỡ mẫu, đặc tả biến…) → gọi thẳng agent chuyên trách.
- **Điều phối plugin (MỘT OWNER):** quyền sở hữu canonical nằm ở
  `.claude/agents/_PLUGIN-ROUTING-CONTRACT.md` +
  `tools/orchestrator/plugin_ownership_registry.json`. `dieu-phoi-nghien-cuu` sở hữu vòng đời
  G0–G10; `dieu-phoi-lam-sang` sở hữu ca ngoại trú. ARS/Anthropic/BMAD/Bio chỉ là worker đúng
  allowlist/stage, không tự hợp nhất kết quả, không đổi trục cổng và không mở Cổng A/B/G. Yêu cầu
  đích danh plugin chỉ ưu tiên worker, không chuyển quyền owner. Kiểm fail-closed bằng
  `python tools/verify_plugin_orchestration.py`.
- **Chốt kiểm đầu ra (MẶC ĐỊNH):** mỗi nhạc trưởng/routine lâm sàng, ở **bước cuối trước khi trả bác sĩ**, gọi guardrail `tham-dinh-dau-ra` soi gói theo **2 lớp** — **Lớp 1 LIÊM CHÍNH** R1–R7 (nguồn · PII · vượt cổng A/B/G · tự gán mức · tách 2 trục · nhãn [CẦN…] · disclaimer, mọi gói) + **Lớp 2 CHẤT LƯỢNG Med-PaLM 2** Q1–Q7 (dễ đọc · đúng đắn · đầy đủ · thiên kiến · nguy cơ hại · cập nhật · thẩm quyền nguồn — chỉ gói lâm sàng; `_CHUAN-CHAT-LUONG-MEDPALM.md`); gói lâm sàng chỉ phát hành khi ĐẠT cả 2 lớp, còn lỗi đỏ → TRẢ-VỀ-SỬA, Q2/Q5 đỏ → chuyển bác sĩ. Cơ chế & giới hạn: `.claude/agents/_KIEM-DUYET-DOC-LAP.md`.
- Bất biến: mỗi đầu ra kèm **PMID/DOI** + "Cần bác sĩ kiểm chứng"; **KHÔNG bịa, KHÔNG PII**; agent chỉ ĐỀ XUẤT, bác sĩ duyệt mới "áp dụng". Bản đồ đội: `.claude/agents/README.md`; Codex dùng bản TOML mirror sinh tự động.
- **Source universe cho chứng cứ mới:** khi cập nhật chứng cứ, hệ thống phải tìm rộng theo các lớp nguồn: PubMed/MEDLINE · Europe PMC · Crossref · OpenAlex; guideline/HTA/hiệp hội/cơ quan chính thức; tạp chí uy tín cao (NEJM/Lancet/JAMA/BMJ/Annals/Nature Medicine...); trial registries; an toàn thuốc; retraction/integrity; full-text/citation context. Sau đó mới ưu tiên registry nguồn chính thức/tin cậy cao. Registry chỉ tăng ưu tiên thẩm định; không tự nâng editorial/preprint/tín hiệu yếu, trial registry chưa có kết quả, hoặc citation graph thành khuyến cáo áp dụng.
- **Đồng bộ Mac:** thư mục `.claude/agents/` nằm trong OneDrive → tự sync sang MacBook; trên Mac mở Claude Code/Codex trong cùng thư mục `~/OneDrive/Claude AI` là dùng cùng đội agent (đợi OneDrive xanh trước khi đổi máy).
- **Đồng bộ Claude Code ↔ Codex ChatGPT:** `.claude/agents/*.md` là nguồn biên tập chính cho Claude Code; `.Codex/agents/*.toml` / `.codex/agents/*.toml` là bản sinh tự động cho Codex ChatGPT. Sau khi sửa/thêm agent, chạy `python tools/enforce_agent_guardrails.py` → `python tools/sync_agents_to_codex.py` → `python tools/sync_agents_to_codex.py --check`; kiểm tra read-only bằng `python tools/check_claude_codex_sync_health.py`. Không sửa tay TOML sinh ra. Hai repo dùng `.githooks/pre-commit` fail-closed: mọi commit bị chặn khi source/mirror còn drift hoặc còn thay đổi agent chưa stage; không dùng `--no-verify` để tuyên bố hoàn thiện.
- **Audit tổng thể trước khi xem là sẵn sàng:** chạy `python tools/upgrade_verify.py` để enforce→sync→check→rubric/taxonomy→agent routing→plugin ownership→gate→clinical schema hardening→clinical evidence update pipeline→audit→orchestrator. PASS nghĩa là hệ nhất quán ở mức trợ lý EBM có bác sĩ duyệt; clinical runtime/chronic-care vẫn không production nếu còn blocker/phê duyệt thật chưa xong.

## Bản đồ dự án (đọc trước khi sửa code)
- **`medical-ebm-automation/` = DỰ ÁN SỐNG (chính).** Bản đầy đủ: pipeline EBM + research
  tracker + dashboard 9 tab + scheduler + scoring (32 thang `verified`) + evidence RAG.
  Có git, ~226 test, harness (`harness.toml`, `Plans.md`, `AGENTS.md`). **Mọi việc lập trình
  mặc định làm ở đây.** Đọc `medical-ebm-automation/AGENTS.md` + `AGENTS.md` khi vào việc code.
- **`ebm-copilot/` = NGUYÊN MẪU Phase 1 (lưu trữ, không phát triển tiếp).** Bản MVP sạch ban
  đầu (chỉ Research + Knowledge, `src/...`). Giữ làm tham chiếu giáo khoa; KHÔNG thêm tính
  năng mới vào đây — nếu cần, port sang `medical-ebm-automation/`.
- Hai thư mục trên là CODEBASE. Còn `EBM-Dashboards/`, `dashboard_mockups/`, `sync/` là hạ
  tầng dùng chung (xem mục Dashboard + INDEX.md ở thư mục gốc).
- **`clinical_runtime/` = hợp đồng governance Clinical V2 đã track Git.** Đây là schema/static
  hardening cho C3/C5/C6/C7, retraction, prompt-injection và conflicting evidence; kiểm bằng
  `python tools/verify_clinical_runtime_schema_hardening.py`. Không gọi đây là production runtime
  cho dữ liệu bệnh nhân thật nếu chưa có runtime integration, bảo mật, UAT và phê duyệt thật.
- **`Antifacts.html` (gốc) = MẶT TIỀN EBM theo CHUYÊN KHOA.** Gom mọi cập nhật chứng cứ + 45
  thang điểm + công cụ NC theo chuyên khoa; sinh bằng `tools/build_antifacts.py`. **TỰ TÍCH LŨY:**
  bước cuối `EBM_MASTER/tools/sync_all.py` chạy `build_library.py add` (làm giàu badge) →
  `build_antifacts.py`; 2 lịch (`weekly_safety`/`monthly_update`) cũng gọi. Nối 2 chiều với hub
  (nút "🛡️ Antifacts ↗" trên 3 trang hub ⇄ "↩ Hub EBM" trên Antifacts). Sửa bố cục = sửa generator,
  KHÔNG sửa tay HTML. Đã wired vào hệ agent: `.claude/agents/_BAN-DO-KET-NOI.md` §9; Codex dùng mirror TOML; có skill `antifacts`.

## Stack kỹ thuật
- Python 3.11+ (khuyến nghị 3.12), venv **ngoài OneDrive** (`~/.ebm-venv`), requirements.txt
- Secrets ở `.env` — đặt **ngoài OneDrive** tại `~/.ebm-secrets/`, symlink về repo (không để key
  trần trên cloud). Không hardcode, không commit, không in ra.
- Codex API cho mọi tác vụ AI (wrapper dùng chung)
- Nguồn miễn phí: PubMed E-utilities, Europe PMC, Crossref, OpenAlex, openFDA… (không key)
- Email: SMTP (Gmail App Password)

## Nguyên tắc bắt buộc
1. API keys CHỈ trong .env, không hardcode, .gitignore phải loại trừ .env
2. Docstring và comment bằng tiếng Việt, code rõ ràng cho người mới học
3. Mọi hàm gọi API: có error handling + retry
4. KHÔNG lưu thông tin định danh bệnh nhân (PII)
5. Mọi output y khoa kèm disclaimer "Cần bác sĩ kiểm chứng" và ghi nguồn (PMID/DOI)

## Thứ tự xây dựng
Phase 1: Module Research (làm trước, hoàn chỉnh)
Phase 2: Module Knowledge (xuất Obsidian/Anki)
Phase 3: Module Clinical (RAG guideline + drug check)

## Dashboard lâm sàng — mẫu MẶC ĐỊNH (bắt buộc)
- Mọi Web Dashboard lâm sàng EBM (tìm & thẩm định chứng cứ, cập nhật khuyến cáo theo một vấn đề cụ thể)
  MẶC ĐỊNH dùng mẫu **"Evidence Workbench"** (nền sáng, 3 cột: bộ lọc · Quick View + bảng item · panel
  thẩm định; có khối GRADE Evidence-to-Decision). *(Mặc định 2026-06-07 theo lựa chọn của bác sĩ;
  **"Dark Analyst"** nền tối chỉ dùng KHI bác sĩ yêu cầu.)*
- **Hai mẫu DÙNG CHUNG một schema `DATA`** (meta/summary/items[]; + `etd` cho EtD) → một khối dữ liệu chạy được cả hai:
  - Mặc định: `dashboard_mockups/templates/evidence-workbench-template.html`
  - Khi yêu cầu (nền tối, dày dữ liệu): `dashboard_mockups/templates/dark-analyst-template.html`
  - Đặc tả: `dashboard_mockups/templates/DESIGN-SPEC.md`. Tạo dashboard mới = copy template, chỉ thay khối
    `DATA`, KHÔNG sửa HTML/CSS.
- **BỐ CỤC/CSS = SỬA TEMPLATE, KHÔNG sửa từng file (chống "sửa xong lại như cũ"):** mỗi dashboard NHÚNG CỨNG
  vỏ (CSS+HTML+JS) lúc sinh ra → sửa 1 file không lan, chạy lại skill thì sinh đè bằng template cũ. Muốn đổi
  bố cục cho TẤT CẢ: (1) sửa `evidence-workbench-template.html` (và `dark-analyst-template.html` nếu cần);
  (2) ĐỒNG BỘ y hệt sang `EBM_MASTER/skill_assets/web-dashboard-*.html`; (3) áp lại cho mọi file đã xuất bằng
  `python3 EBM-Dashboards/tools/reskin_dashboards.py` (bóc khối `DATA`, bọc lại vỏ chuẩn — GIỮ NGUYÊN dữ liệu,
  tự backup vào `_reskin_backup/`; `--dry-run` xem trước). KHÔNG sửa tay `EBM_WEBAPP.html`/`DANH_MUC.html`
  (sinh lại từ JSON mỗi lần sync → mọi sửa tay sẽ mất). *(Mặc định 2026-06-16: template EW mặc định cột thẩm
  định bên phải TỰ THU khi chưa chọn item → bảng dùng trọn bề ngang; thẻ tóm tắt tự lọc abstract ngoại ngữ.)*
- **Tự động khi gọi skill:** mỗi lần `cap-nhat-chung-cu-y-khoa` được gọi → tự chạy TRỌN dây chuyền: dựng Dashboard
  (EW mặc định) → cổng liêm chính (`verify_dashboard.py --online`) → an toàn thuốc (nếu liên quan) → thư viện
  (`build_library.py add`) → 3 sản phẩm phái sinh (`make_derivatives.py`). Không cần bác sĩ yêu cầu từng bước.
  Kiểm hồi quy kỹ thuật cho toàn dây chuyền này bằng `python tools/verify_clinical_evidence_update_pipeline.py`
  (fixture offline, không PII; dashboard thật vẫn cần `--online`, rà toàn văn và bác sĩ duyệt).
- **Cổng direct-practice readiness (2026-08-13):** dashboard/thẻ đã PASS nguồn chưa đồng nghĩa tự được gọi là
  "áp dụng trực tiếp". Trước khi nâng thẻ `decision="apply"` hoặc trả một danh sách "sẵn sàng cho bác sĩ áp dụng",
  chạy trong `medical-ebm-automation/`: `python tools/verify_direct_clinical_practice_readiness.py --today YYYY-MM-DD --write`
  (hoặc `--strict-apply` khi cần fail-closed). Chỉ `READY_FOR_PHYSICIAN_DIRECT_USE` mới được gọi là direct-use;
  `REVIEW_REQUIRED` và `BLOCKED_FOR_DIRECT_USE` phải giữ hàng duyệt/chặn. Không tự sửa `consider/notyet` thành `apply`;
  bác sĩ/master gate là bắt buộc. Skill xem thêm `sync/skills/cap-nhat-chung-cu-y-khoa/references/12-direct-practice-readiness.md`.
- **Triển khai giám sát định kỳ fail-closed:** owner thu thập duy nhất là `medical-ebm-automation/scripts/weekly_safety.sh` + `monthly_update.sh`; routine khác chỉ dùng candidate queue. `source_health=PARTIAL/FAIL` phải giữ watermark, chặn bridge Hub và cảnh báo nội dung. Chỉ gọi là triển khai candidate-only khi `python medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py --online` trả `READY_FOR_CONTROLLED_DEPLOYMENT` sau canary, runtime tuần/tháng, alert, rollback, 2 chu kỳ shadow và UAT/phê duyệt thật. Agent không tự ký UAT.
- Áp dụng cho skill `cap-nhat-chung-cu-y-khoa` và mọi tác vụ dashboard lâm sàng. Ngoại lệ: Dashboard Master
  quản trị (skill `dashboard-master-ebm-ngoai-tru`) giữ định dạng Excel/sổ riêng.
- Liêm chính: số liệu trích ĐÚNG nguồn; giữ nguyên grading (`gradeLevel:'na'` nếu không phân hạng); RoB 2
  chỉ cho RCT; kèm PMID/DOI; disclaimer "Cần bác sĩ kiểm chứng"; KHÔNG PII.
- **Lưu & tích lũy (thư mục chung):** mọi dashboard xuất vào `EBM-Dashboards/` (OneDrive-synced Mac↔Windows).
  Sau khi xuất, **chạy trong `EBM-Dashboards/`**: (1) `python3 tools/verify_dashboard.py <file>.html --online` → PASS;
  (2) `python3 tools/build_library.py add <file>.html` để cập nhật chỉ mục `evidence-library.html`. Hướng dẫn: `EBM-Dashboards/README.md`.
- **(3) ĐỒNG BỘ VÀO HUB EBM_MASTER (bắt buộc — nếu không, nội dung KHÔNG vào "EBM" trung tâm):** sau khi PASS, nạp dashboard
  vào sổ cái trung tâm. **Hub đã gộp NGAY trong thư mục chung này: `Codex AI/EBM_MASTER/`** (từ 2026-06-11; trước ở
  `../Cập nhật hướng dẫn điều trị/EBM_MASTER`). **Cách nhanh nhất — một lệnh idempotent tự gom + dedup:**
  `python3 EBM_MASTER/tools/sync_all.py` (hoặc bấm đúp nút `Đồng bộ EBM.command` ở thư mục chung). Lệnh này tự: copy dashboard
  vào `EBM_MASTER/WEB_DASHBOARDS/` → `ingest_dashboard.py` (tự backup + chống trùng pmid|doi|title, tính cả `quarantined_cards`)
  → `integrity_guard.py --fix --quarantine-untraceable --strict` → sinh lại `DANH_MUC.html` + `EBM_WEBAPP.html`.
  Thẻ mới vào hàng "chờ bác sĩ duyệt", không tự "áp dụng ngay"; thẻ không truy nguyên được bị cách ly khỏi `evidence_cards`.
  Khi cập nhật template (EW/DA), đồng bộ luôn `EBM_MASTER/skill_assets/web-dashboard-*.html` để hub không sinh dashboard bằng bản cũ.

## Lệnh
> Chạy trong `medical-ebm-automation/` (dự án sống), với venv `~/.ebm-venv` đã kích hoạt.
- Cài: `pip install -r requirements.txt`
- Chạy app/dashboard: `python run.py` (hoặc "Mở Dashboard.command")
- Test: `pytest`
- Lint: `ruff check`
- Kiểm + đồng bộ toàn hệ từ thư mục gốc: `python tools/upgrade_verify.py`
- Kiểm riêng đồng bộ Claude Code ↔ Codex: `python tools/check_claude_codex_sync_health.py`
- Kiểm riêng rubric QA ↔ LESSONS taxonomy: `python tools/verify_lessons_rubric_alignment.py`
- Kiểm riêng clinical runtime governance: `python tools/verify_clinical_runtime_schema_hardening.py`
- Kiểm riêng pipeline cập nhật chứng cứ lâm sàng: `python tools/verify_clinical_evidence_update_pipeline.py`
- Kiểm cổng triển khai giám sát ngoại trú: `python medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py --online`
- Chạy chu trình tự động có kiểm soát: `python tools/run_controlled_automation_cycle.py`
- Vòng lặp kiểm tra-hoàn thiện tới clinical production: `python tools/clinical_production_loop.py --max-iterations 3`

_Nguyên mẫu cũ `ebm-copilot/`: `pip install -r requirements.txt` → `python -m src.research.digest` → `pytest tests/` (chỉ để tham chiếu)._
