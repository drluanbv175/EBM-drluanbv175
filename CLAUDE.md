# EBM Copilot — Trợ lý AI cho Bác sĩ Y học Bằng chứng

## Mục tiêu
Hệ thống tự động hóa cho bác sĩ ngoại trú thực hành EBM, gồm 3 module:
Research (nghiên cứu), Clinical (lâm sàng), Knowledge (quản lý kiến thức).

## Điều phối Agent — hành vi MẶC ĐỊNH (đội `.claude/agents`, 50 agent: 21 lâm sàng + 28 nghiên cứu + 1 guardrail dùng chung; +3 lâm sàng 2026-06-16 (dau-man-tinh·cham-soc-giam-nhe·tram-cam-lo-au); +2 lâm sàng 2026-07-04 (quan-ly-khang-dong — kháng đông trọn vòng; tham-dinh-do-chinh-xac-chan-doan — thẩm định độ chính xác chẩn đoán QUADAS-2/GRADE-cho-test, lấp khoảng trống audit))
Khi bác sĩ nêu việc lâm sàng hoặc nghiên cứu, MẶC ĐỊNH định tuyến tới "nhạc trưởng" phù hợp và để nó **tự chạy tuần tự theo Giao thức tự động** (không hỏi vặt từng bước):
- **Nêu một CA/tình huống lâm sàng** ("tôi có bệnh nhân…", "khám ca này", hỏi chẩn đoán/điều trị) → `dieu-phoi-lam-sang`: tự chạy 5 bước EBM (Hỏi→Tìm→Thẩm định→Áp dụng→Theo dõi); **cờ đỏ nêu NGAY**; dừng ở **Cổng A** (áp dụng cho BN) + **Cổng B** (ghi sổ cái).
- **Nêu một ĐỀ TÀI/câu hỏi nghiên cứu** (chỉ cần tên đề tài) → `dieu-phoi-nghien-cuu`: tự khôi phục trạng thái từ sổ cái → suy loại thiết kế → march G0→G9; dừng ở 5 cổng cứng (G2 đạo đức · G4 khóa SAP · dữ liệu thật trước phân tích · **G8 bình duyệt độc lập** (mới 2026-07-14) · liêm chính tác giả G9) + nơi cần dữ liệu/phê duyệt thật. Mỗi cổng fail-closed theo ĐÚNG role (IRB/thống kê viên hoặc PI/phản biện độc lập/PI — xem `tools/gate_contract.py`), không chỉ "có ai đó ký".
- **Việc lẻ** (tra 1 câu hỏi, soát 1 danh mục TLTK, tính cỡ mẫu, đặc tả biến…) → gọi thẳng agent chuyên trách.
- **Chốt kiểm đầu ra (MẶC ĐỊNH):** mỗi nhạc trưởng/routine lâm sàng, ở **bước cuối trước khi trả bác sĩ**, gọi guardrail `tham-dinh-dau-ra` soi gói theo **2 lớp** — **Lớp 1 LIÊM CHÍNH** R1–R7 (nguồn · PII · vượt cổng A/B/G · tự gán mức · tách 2 trục · nhãn [CẦN…] · disclaimer, mọi gói) + **Lớp 2 CHẤT LƯỢNG Med-PaLM 2** Q1–Q7 (dễ đọc · đúng đắn · đầy đủ · thiên kiến · nguy cơ hại · cập nhật · thẩm quyền nguồn — chỉ gói lâm sàng; `_CHUAN-CHAT-LUONG-MEDPALM.md`); gói lâm sàng chỉ phát hành khi ĐẠT cả 2 lớp, còn lỗi đỏ → TRẢ-VỀ-SỬA, Q2/Q5 đỏ → chuyển bác sĩ. Cơ chế & giới hạn: `.claude/agents/_KIEM-DUYET-DOC-LAP.md`.
- Bất biến: mỗi đầu ra kèm **PMID/DOI** + "Cần bác sĩ kiểm chứng"; **KHÔNG bịa, KHÔNG PII**; agent chỉ ĐỀ XUẤT, bác sĩ duyệt mới "áp dụng". Bản đồ đội: `.claude/agents/README.md`.
- **Đồng bộ Mac:** thư mục `.claude/agents/` nằm trong OneDrive → tự sync sang MacBook; trên Mac mở `claude` ngay trong thư mục `~/OneDrive/Claude AI` là dùng được cùng đội agent (đợi OneDrive xanh trước khi đổi máy).
- **Kiểm tra AN TOÀN đồng bộ — MẶC ĐỊNH trước khi làm việc/đổi máy:** chạy `python3 tools/sync_safety_check.py` (hoặc bấm đúp **`Kiểm tra An toàn Đồng bộ.command`**) để soi 4 nguy cơ đã gặp thật (conflict-copy OneDrive · git 2 repo lồng hỏng/treo · file lõi chưa tải thật · dấu hiệu máy/phiên khác vừa ghi). Verdict 🟢/🟡/🔴 (exit 0/1/2) — 🔴 nghĩa là DỪNG, không sửa gì cho tới khi xử lý xong mục đỏ. Thuần thư viện chuẩn Python, không cần venv/mạng, chạy được ngay cả khi môi trường EBM chưa cài. Nếu tool báo git repo hỏng (HEAD không giải được/`git fsck` báo "missing object" — dấu hiệu OneDrive đồng bộ dở `.git` sống, hay gặp khi 1 máy tạo git worktree bên trong cây OneDrive): trên máy CÒN đủ dữ liệu chạy `git bundle create <ten>.bundle --all` (ghi ra 1 file tĩnh, an toàn để OneDrive đồng bộ, khác với đồng bộ `.git` sống); đợi OneDrive xanh; máy thiếu chạy `git fetch <duong-dan-bundle> 'refs/*:refs/rescue/*'` rồi `git fsck --full` xác nhận sạch. Hoặc nhờ Claude Code soi từng mục.
- **Đồng bộ BỘ NHỚ (memory) giữa máy — KHÔNG tự sync, phải chạy tay:** bộ nhớ tự-động của Claude nằm ở `~/.claude/projects/<đường-dẫn-mã-hóa>/memory/` — **NGOÀI cây OneDrive** → đổi máy = "mất trí nhớ" dự án. Khắc phục: `python3 tools/sync_memory.py` (hoặc bấm đúp **`Đồng bộ Bộ nhớ.command`**) mirror 2 chiều sang `memory-sync/` (trong OneDrive, gitignored). **An toàn: file mới hơn thắng, KHÔNG xóa.** Chạy trên MỖI máy sau khi OneDrive xanh (máy A đẩy → máy B kéo về đúng đường-dẫn-mã-hóa của B). Các thứ NGOÀI OneDrive khác cũng phải làm lại mỗi máy: venv `~/.ebm-venv`, secrets `~/.ebm-secrets`, và cấp quyền lại MCP connectors.
- **Đồng bộ Claude Code ↔ Codex ChatGPT:** `.claude/agents/*.md` là nguồn biên tập chính; `.Codex/agents/*.toml` / `.codex/agents/*.toml` là bản sinh tự động. Sau khi sửa/thêm agent, chạy `python tools/enforce_agent_guardrails.py` → `python tools/sync_agents_to_codex.py` → `python tools/sync_agents_to_codex.py --check`; kiểm tra tổng thể bằng `python tools/audit_ebm_system.py`.
  **Chặn tự động (2026-07-11):** đã có git hook `.githooks/pre-commit` — chặn commit nếu `.claude/agents/*.md`
  thay đổi mà `.Codex/agents` chưa đồng bộ (đã kiểm chứng: PASS khi sạch, FAIL/chặn khi lệch thật).
  **Kích hoạt 1 lần/máy** (hook nằm ngoài `.git/hooks/` — tool không có quyền ghi `.git/` nội bộ nên
  không tự bật được, và cũng không tự đổi `git config` theo nguyên tắc an toàn): `git config
  core.hooksPath .githooks && chmod +x .githooks/pre-commit`.

## Bản đồ dự án (đọc trước khi sửa code)
- **`medical-ebm-automation/` = DỰ ÁN SỐNG (chính).** Bản đầy đủ: pipeline EBM + research
  tracker + dashboard 12 tab + Evidence Workbench + scheduler + scoring (32 thang có nguồn trích dẫn
  đã rà soát `verified` — CHỈ 8 thang trong đó có công cụ tính điểm xác định/unit-test thật, xem
  `tools/risk_score_calc.py`; 24 thang còn lại chỉ mô tả văn xuôi, agent `thang-diem-nguy-co` biết
  ranh giới này) + "RAG" chứng cứ (tra cứu chuỗi con trên file tổng hợp tĩnh, chưa phải
  embedding/vector search thật — vá 2026-07-11, vòng 9 audit).
  Có git, ~226 test, harness (`harness.toml`, `Plans.md`, `AGENTS.md`). **Mọi việc lập trình
  mặc định làm ở đây.** Đọc `medical-ebm-automation/CLAUDE.md` + `AGENTS.md` khi vào việc code.
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
  `build_antifacts.py`; 2 lịch launchd (`com.medicalebm.weeklysafety`/`com.medicalebm.monthlyupdate`
  — nhãn KHÔNG có gạch dưới, khác tên file script `weekly_safety.sh`/`monthly_update.sh` bên trong,
  dễ nhầm khi grep/tra log) cũng gọi. Nối 2 chiều với hub
  (nút "🛡️ Antifacts ↗" trên 3 trang hub ⇄ "↩ Hub EBM" trên Antifacts). Sửa bố cục = sửa generator,
  KHÔNG sửa tay HTML. Đã wired vào hệ agent: `.claude/agents/_BAN-DO-KET-NOI.md` §9; có skill `antifacts`.
- **Thư mục "phụ" ở gốc — chưa từng liệt kê ở đây trước 2026-07-12, phát hiện qua audit toàn diện:**
  `observability/` là sổ QA sống (APPRAISALS.jsonl…) — `tools/eval/*.py` + `tools/orchestrator/
  guardrail_bridge.py` đọc/ghi thật, ĐANG chạy. `governance/`, `assurance/`, `convergence/` là hồ sơ
  chính sách/bằng chứng TĨNH — `governance/CLINICAL_GATES.md` tự khai "chưa enforce runtime";
  KHÔNG có code nào gọi vào 3 thư mục này (đọc như tài liệu tham khảo, không phải hệ thống chạy).
  `medical-ebm-automation/chronic-care-clinic-os/` là app Next.js+Prisma THẬT (không phải mock) cho
  một sáng kiến "phòng khám bệnh mạn" riêng — **CHƯA nối vào hệ agent `.claude/agents/` hay
  `tools/orchestrator/`** (dieu-phoi-lam-sang/dieu-phoi-nghien-cuu không gọi tới); tự khóa
  `BLOCKED_FOR_PRODUCTION` (37 blocker mở, xem `chronic-care-clinic-os/PRODUCTION_BLOCKERS.md`) —
  hiện KHÔNG ghi DB thật, KHÔNG có code AI/LLM nào (`AI_DRAFTS_ENABLED=false` mới chỉ là biến khai
  trong `.env.example`, chưa có chỗ nào trong code đọc nó). `tools/orchestrator/` (control plane 6
  năng lực, xem mục Lệnh) cũng **tách rời khỏi luồng agent thật** — chỉ là bộ dry-run/self-audit song
  song, bác sĩ không cần đụng tới khi làm việc qua Claude/Codex agent bình thường.
- **5 nhánh mồ côi khác trong `medical-ebm-automation/`, phát hiện qua audit cổng 2026-07-14 —
  cùng kiểu "tách rời" như `tools/orchestrator/`, KHÔNG do doctrine/agent nào gọi tới, ĐỪNG nhầm là
  cổng thật đang bảo vệ pipeline:** (1) `runtime/policy_gate_engine.py` + `runtime/controlled_orchestrator.py`
  + `research_studio/` + `research_automation/` — tự khai "NO-GO — NOT QUALIFIED FOR RESEARCH WORKFLOW USE"
  ngay trong docstring, ledger của nó chỉ sống trong bộ nhớ (không bao giờ ghi ra
  `exports/<study>/approval_ledger.json` — file THẬT mà `tools/approve_gate.py`/`run_g*_auto.py` dùng).
  (2) `research_project/project_cli.py` + `research_project/project_claim_traceability.py`
  (`ClaimTraceabilityLedger`) — CLI thứ ba, không nằm trong doctrine, có thể vô tình trỏ
  `--approval-ledger` vào ĐÚNG path thật và ghi đè ledger nếu ai đó gõ nhầm (rủi ro tiềm ẩn, chưa xảy ra);
  package tự khai "OFFLINE·SYNTHETIC ONLY... NO-GO — NOT QUALIFIED FOR RESEARCH WORKFLOW USE".
  (3) `app/core/approval_service.py` (class `ApprovalCenter`) + `app/models/governance_v7.py` +
  `app/chronic_care/` — hệ role thứ ba (physician/PI/system_owner) phục vụ "Chronic Care Phase 3A
  shadow pilot" nội bộ bằng Python, KHÁC HOÀN TOÀN thư mục `chronic-care-clinic-os/` (Next.js) ở trên dù
  trùng tên "chronic care" — không có route/CLI thật nào ghi vào DB này ngoài script seed test.
  (4) `app/evidence/citation_verification.py` + `phase_2d_claim_mapping_validator.py` +
  `retraction_monitor.py` (gọi bởi `scripts/phase_2b_live_source_smoke_test.py`,
  `scripts/phase_2c_live_source_validation.py`, `app/evidence/phase_2d_pack_readiness.py`, và cross-ref
  bởi `app/models/governance_v7.py` ở mục (3) — 2 nhánh mồ côi này GIAO NHAU) — một hệ claim/citation/
  retraction-tracking THỨ HAI song song với (2), CŨNG không được `tools/run_g7_auto.py`/`run_g9_auto.py`
  gọi tới. `retraction_monitor.detect_retraction()` của nhánh này chỉ đọc chữ "retracted"/"withdrawn"
  ĐÃ CÓ SẴN trong metadata truyền vào — KHÔNG tự tra cứu gì, khác hẳn cơ chế THẬT đang dùng (mục dưới).
  Cổng G0-G9 THẬT duy nhất đang chạy là `tools/gate_contract.py` + `tools/approve_gate.py` +
  `tools/run_g*_auto.py`. Từ 2026-07-14: cổng A12 (kiểm chứng trích dẫn, agent `kiem-chung-trich-dan`)
  cũng THẬT — `tools/run_g10_assemble.py` xác minh artifact `A12_CITATION_VERIFICATION_<study>.md` trước
  khi cho lắp gói nộp, và rút bài được tra CHỦ ĐỘNG bằng `tools/check_citation_retraction.py`
  (`app/sources/pubmed.py::PubMedClient.check_retraction_status()` — gọi PubMed E-utilities thật, xác
  nhận bằng PMID 9500320/Wakefield 1998; KHÁC nhánh mồ côi (4) ở trên).

## Stack kỹ thuật
- Python 3.11+ (khuyến nghị 3.12), venv **ngoài OneDrive** (`~/.ebm-venv`), requirements.txt.
  **Trạng thái thật 2026-07-15 (ĐÃ ĐÓNG — cả 2 máy đều ≥3.11):** Windows chạy 3.12.10; Mac đã
  nâng từ 3.9.6 lên **3.14.6** (bác sĩ tự cài, không có bản 3.12 khả dụng lúc đó) — cùng
  `requirements.lock.txt` cài sạch và cho đúng 1812 test pass/0 fail/17 skip trên CẢ HAI (xác
  nhận bằng `pip freeze` giống hệt nhau). venv 3.9.6 cũ giữ lại không xóa tại
  `~/.ebm-venv-py39-backup-20260715` làm dự phòng. Lưới an toàn vẫn giữ nguyên dù rào cản gốc đã
  đóng: `ruff.toml` bật rule `FA102` (target-version=py39) chặn cú pháp PEP604 `X | None` thiếu
  `from __future__ import annotations` — đúng lỗi từng làm crash `pytest` trên máy 3.9
  (2026-07-15, đã vá 2 file) — CI chạy `ruff check` mỗi lần push
  (`.github/workflows/offline-ci.yml`).
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
- Áp dụng cho skill `cap-nhat-chung-cu-y-khoa` và mọi tác vụ dashboard lâm sàng. Ngoại lệ: Dashboard Master
  quản trị (skill `dashboard-master-ebm-ngoai-tru`) giữ định dạng Excel/sổ riêng.
- Liêm chính: số liệu trích ĐÚNG nguồn; giữ nguyên grading (`gradeLevel:'na'` nếu không phân hạng); RoB 2
  chỉ cho RCT; kèm PMID/DOI; disclaimer "Cần bác sĩ kiểm chứng"; KHÔNG PII.
- **Lưu & tích lũy (thư mục chung):** mọi dashboard xuất vào `EBM-Dashboards/` (OneDrive-synced Mac↔Windows).
  Sau khi xuất, **chạy trong `EBM-Dashboards/`**: (1) `python3 tools/verify_dashboard.py <file>.html --online` → PASS;
  (2) `python3 tools/build_library.py add <file>.html` để cập nhật chỉ mục `evidence-library.html`. Hướng dẫn: `EBM-Dashboards/README.md`.
- **(3) ĐỒNG BỘ VÀO HUB EBM_MASTER (bắt buộc — nếu không, nội dung KHÔNG vào "EBM" trung tâm):** sau khi PASS, nạp dashboard
  vào sổ cái trung tâm. **Hub đã gộp NGAY trong thư mục chung này: `Claude AI/EBM_MASTER/`** (từ 2026-06-11; trước ở
  `../Cập nhật hướng dẫn điều trị/EBM_MASTER`). **Cách nhanh nhất — một lệnh idempotent tự gom + dedup:**
  `python3 EBM_MASTER/tools/sync_all.py` (hoặc bấm đúp nút `Đồng bộ EBM.command` ở thư mục chung). Lệnh này tự: copy dashboard
  vào `EBM_MASTER/WEB_DASHBOARDS/` → `ingest_dashboard.py` (tự backup + chống trùng pmid|doi|title) →
  `integrity_guard.py --fix --quarantine-untraceable --strict` → sinh lại `DANH_MUC.html` + `EBM_WEBAPP.html`.
  Thẻ mới vào hàng "chờ bác sĩ duyệt", không tự "áp dụng ngay"; thẻ không truy nguyên được bị cách ly khỏi `evidence_cards`.
  Khi cập nhật template (EW/DA), đồng bộ luôn `EBM_MASTER/skill_assets/web-dashboard-*.html` để hub không sinh dashboard bằng bản cũ.

## Lệnh
> Chạy trong `medical-ebm-automation/` (dự án sống), với venv `~/.ebm-venv` đã kích hoạt.
- Cài: `pip install -r requirements.txt`
- Chạy app/dashboard: `python run.py` (hoặc "Mở Dashboard.command")
- Kiểm nhanh: `python -m compileall -q app scripts tests`
- Test: `pytest` (khi venv đã có dev dependencies)
- Lint: `ruff check` (khi venv đã có dev dependencies)
- Audit chung từ thư mục gốc: `python tools/audit_ebm_system.py`
- **Kiểm + đồng bộ toàn hệ một lệnh:** `python tools/upgrade_verify.py` (hoặc bấm đúp "Nâng cấp & Kiểm tra EBM") — chạy trọn enforce→sync→check→routing→assess→audit→orchestrator(validate+test).
- **Kiểm riêng repo/Claude Code/Codex alignment:** `python tools/verify_claude_code_repo_alignment.py` — bắt lệch `AGENTS.md`/`CLAUDE.md`, file governance chưa track Git, hoặc sync health đỏ. Nếu cần soi riêng mirror agent, chạy `python tools/check_claude_codex_sync_health.py`.
- **Kiểm riêng clinical runtime governance:** `python tools/verify_clinical_runtime_schema_hardening.py` — chốt source integrity, prompt injection, conflicting evidence trong schema.
- **Kiểm riêng pipeline cập nhật chứng cứ lâm sàng:** `python tools/verify_clinical_evidence_update_pipeline.py` — kiểm Evidence Workbench→verify_dashboard→library→derivatives→hợp đồng sync_all bằng fixture offline không PII.
- **Chạy chu trình tự động có kiểm soát:** `python tools/run_controlled_automation_cycle.py` — gom sync/routing/gate/dữ liệu/phản biện-thống kê/clinical governance thành một quyết định fail-closed hoặc human-gated.
- **Orchestrator chạy được (control plane 6 năng lực, dry-run):** `python tools/run_orchestrator.py "<ca/đề tài/câu hỏi>"` — định tuyến intent → dựng plan theo flow → dừng ở cổng bác sĩ → chốt guardrail. `--capabilities`/`--validate`/`--resume`. Tài liệu + 43 test (gồm cầu THẬT `guardrail_bridge.py`→`tools/eval/run_eval.py` vá dead-code `guardrail_fail` — xem `orchestrator.py::_guardrail_reroute_loop`; `appraisal_bridge.py` là seam mô phỏng riêng, CHƯA cắm vào orchestrator.py, 5/43 test): `tools/orchestrator/`.

_Nguyên mẫu cũ `ebm-copilot/`: `pip install -r requirements.txt` → `python -m src.research.digest` → `pytest tests/` (chỉ để tham chiếu)._
