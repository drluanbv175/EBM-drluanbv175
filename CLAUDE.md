# EBM Copilot — Trợ lý AI cho Bác sĩ Y học Bằng chứng

## Mục tiêu
Hệ thống tự động hóa cho bác sĩ ngoại trú thực hành EBM, gồm 3 module:
Research (nghiên cứu), Clinical (lâm sàng), Knowledge (quản lý kiến thức).

## Điều phối Agent — hành vi MẶC ĐỊNH (đội `.claude/agents`, 50 agent: 21 lâm sàng + 28 nghiên cứu + 1 guardrail dùng chung; +3 lâm sàng 2026-06-16 (dau-man-tinh·cham-soc-giam-nhe·tram-cam-lo-au); +2 lâm sàng 2026-07-04 (quan-ly-khang-dong — kháng đông trọn vòng; tham-dinh-do-chinh-xac-chan-doan — thẩm định độ chính xác chẩn đoán QUADAS-2/GRADE-cho-test, lấp khoảng trống audit))
Khi bác sĩ nêu việc lâm sàng hoặc nghiên cứu, MẶC ĐỊNH định tuyến tới "nhạc trưởng" phù hợp và để nó **tự chạy tuần tự theo Giao thức tự động** (không hỏi vặt từng bước):
- **Nêu một CA/tình huống lâm sàng** ("tôi có bệnh nhân…", "khám ca này", hỏi chẩn đoán/điều trị) → `dieu-phoi-lam-sang`: tự chạy 5 bước EBM (Hỏi→Tìm→Thẩm định→Áp dụng→Theo dõi); **cờ đỏ nêu NGAY**; dừng ở **Cổng A** (áp dụng cho BN) + **Cổng B** (ghi sổ cái).
- **Nêu một ĐỀ TÀI/câu hỏi nghiên cứu** (chỉ cần tên đề tài) → `dieu-phoi-nghien-cuu`: tự khôi phục trạng thái từ sổ cái → suy loại thiết kế → march G0→G10; dừng ở 6 cổng cứng (G2 đạo đức · G4 khóa SAP · G5 khóa dữ liệu thật · **G8 bình duyệt độc lập** · G9 liêm chính tác giả · G10 PI khóa gói phát hành) + nơi cần dữ liệu/phê duyệt thật. Mỗi cổng fail-closed theo ĐÚNG role (IRB/thống kê viên hoặc PI/quản lý dữ liệu hoặc PI/phản biện độc lập/PI/PI — xem `tools/gate_contract.py`), không chỉ "có ai đó ký".
- **Bảo đảm chuẩn nghiên cứu hiện hành:** G2 fail-closed khi WHO TRDS v1.3.1 mục 13/14/19/20 thiếu dữ kiện khoa học PI đã pin hoặc tham chiếu Hội đồng chỉ là fallback; G9 fail-closed khi thiếu quyền truy cập dữ liệu/độc lập nhà tài trợ theo ICMJE 1/2026. `python tools/verify_controlled_research_automation.py` kiểm hành vi này cùng danh sách 6 cổng canonical; không dùng PASS kỹ thuật thay IRB/PI/thống kê viên/phản biện.
- **Việc lẻ** (tra 1 câu hỏi, soát 1 danh mục TLTK, tính cỡ mẫu, đặc tả biến…) → gọi thẳng agent chuyên trách.
- **Điều phối plugin (MỘT OWNER):** quyền sở hữu canonical nằm ở
  `.claude/agents/_PLUGIN-ROUTING-CONTRACT.md` +
  `tools/orchestrator/plugin_ownership_registry.json`. `dieu-phoi-nghien-cuu` sở hữu vòng đời
  G0–G10; `dieu-phoi-lam-sang` sở hữu ca ngoại trú. ARS/Anthropic/BMAD/Bio chỉ là worker đúng
  allowlist/stage, không tự hợp nhất kết quả, không đổi trục cổng và không mở Cổng A/B/G. Yêu cầu
  đích danh plugin chỉ ưu tiên worker, không chuyển quyền owner. Kiểm fail-closed bằng
  `python tools/verify_plugin_orchestration.py`.
- **Chốt kiểm đầu ra (MẶC ĐỊNH):** mỗi nhạc trưởng/routine lâm sàng, ở **bước cuối trước khi trả bác sĩ**, gọi guardrail `tham-dinh-dau-ra` soi gói theo **2 lớp** — **Lớp 1 LIÊM CHÍNH** R1–R7 (nguồn · PII · vượt cổng A/B/G · tự gán mức · tách 2 trục · nhãn [CẦN…] · disclaimer, mọi gói) + **Lớp 2 CHẤT LƯỢNG Med-PaLM 2** Q1–Q7 (dễ đọc · đúng đắn · đầy đủ · thiên kiến · nguy cơ hại · cập nhật · thẩm quyền nguồn — chỉ gói lâm sàng; `_CHUAN-CHAT-LUONG-MEDPALM.md`); gói lâm sàng chỉ phát hành khi ĐẠT cả 2 lớp, còn lỗi đỏ → TRẢ-VỀ-SỬA, Q2/Q5 đỏ → chuyển bác sĩ. Cơ chế & giới hạn: `.claude/agents/_KIEM-DUYET-DOC-LAP.md`.
- Bất biến: mỗi đầu ra kèm **PMID/DOI** + "Cần bác sĩ kiểm chứng"; **KHÔNG bịa, KHÔNG PII**; agent chỉ ĐỀ XUẤT, bác sĩ duyệt mới "áp dụng". Bản đồ đội: `.claude/agents/README.md`.
- **Đồng bộ Mac:** thư mục `.claude/agents/` nằm trong OneDrive → tự sync sang MacBook; trên Mac mở `claude` ngay trong thư mục `~/OneDrive/Claude AI` là dùng được cùng đội agent (đợi OneDrive xanh trước khi đổi máy).
- **Kiểm tra AN TOÀN đồng bộ — MẶC ĐỊNH trước khi làm việc/đổi máy:** chạy `python3 tools/sync_safety_check.py` (hoặc bấm đúp **`Kiểm tra An toàn Đồng bộ.command`**) để soi 4 nguy cơ đã gặp thật (conflict-copy OneDrive · git 2 repo lồng hỏng/treo · file lõi chưa tải thật · dấu hiệu máy/phiên khác vừa ghi). Verdict 🟢/🟡/🔴 (exit 0/1/2) — 🔴 nghĩa là DỪNG, không sửa gì cho tới khi xử lý xong mục đỏ. Thuần thư viện chuẩn Python, không cần venv/mạng, chạy được ngay cả khi môi trường EBM chưa cài. Nếu tool báo git repo hỏng (HEAD không giải được/`git fsck` báo "missing object" — dấu hiệu OneDrive đồng bộ dở `.git` sống, hay gặp khi 1 máy tạo git worktree bên trong cây OneDrive): trên máy CÒN đủ dữ liệu chạy `git bundle create <ten>.bundle --all` (ghi ra 1 file tĩnh, an toàn để OneDrive đồng bộ, khác với đồng bộ `.git` sống); đợi OneDrive xanh; máy thiếu chạy `git fetch <duong-dan-bundle> 'refs/*:refs/rescue/*'` rồi `git fsck --full` xác nhận sạch. Hoặc nhờ Claude Code soi từng mục.
- **Đồng bộ BỘ NHỚ (memory) giữa máy — KHÔNG tự sync, phải chạy tay:** bộ nhớ tự-động của Claude nằm ở `~/.claude/projects/<đường-dẫn-mã-hóa>/memory/` — **NGOÀI cây OneDrive** → đổi máy = "mất trí nhớ" dự án. Khắc phục: `python3 tools/sync_memory.py` (hoặc bấm đúp **`Đồng bộ Bộ nhớ.command`**) mirror 2 chiều sang `memory-sync/` (trong OneDrive, gitignored). **An toàn: file mới hơn thắng, KHÔNG xóa.** Chạy trên MỖI máy sau khi OneDrive xanh (máy A đẩy → máy B kéo về đúng đường-dẫn-mã-hóa của B). Các thứ NGOÀI OneDrive khác cũng phải làm lại mỗi máy: venv `~/.ebm-venv`, secrets `~/.ebm-secrets`, và cấp quyền lại MCP connectors.
- **Đồng bộ Claude Code ↔ Codex ChatGPT:** `.claude/agents/*.md` là nguồn biên tập chính; `.Codex/agents/*.toml` / `.codex/agents/*.toml` là bản sinh tự động. Sau khi sửa/thêm agent, chạy `python tools/enforce_agent_guardrails.py` → `python tools/sync_agents_to_codex.py` → `python tools/sync_agents_to_codex.py --check`; kiểm tra tổng thể bằng `python tools/audit_ebm_system.py`.
  **Chặn tự động (2026-07-11; fail-closed toàn cục 2026-07-29):** hai repo dùng
  `.githooks/pre-commit`; mọi commit bị chặn khi source/mirror còn drift, guardrail/disclaimer
  chưa đạt, hợp đồng repo lệch, hoặc còn thay đổi agent chưa stage. Repo y khoa gọi lại chốt
  của repo gốc trước commit, nên không thể đánh dấu hoàn thiện runtime khi doctrine còn lệch.
  **Kích hoạt 1 lần/máy** (hook nằm ngoài `.git/hooks/` — tool không có quyền ghi `.git/` nội bộ nên
  không tự bật được, và cũng không tự đổi `git config` theo nguyên tắc an toàn): `git config
  core.hooksPath .githooks && chmod +x .githooks/pre-commit`; không dùng `--no-verify`
  để tuyên bố hoàn thiện.

## Tìm & dùng công cụ (plugin · skill · agent) — dọn 2026-08-05
- **Ba cách tra, theo thứ tự nên dùng:** (1) mở **`TRA-CUU-CONG-CU.html`** ở gốc thư mục này —
  gõ tiếng Việt CÓ DẤU hay KHÔNG DẤU đều ra, xếp theo độ sát (khớp ở TÊN thắng khớp trong mô tả),
  lọc theo loại/máy, bấm vào lệnh là chép; mở bằng chuột, không cần Claude chạy. (2) lệnh
  **`/cong-cu-gi <việc cần làm>`** — đọc `tools/vietnamize/INDEX-CONG-CU.md` (bản gọn 28 KB), chưa
  đủ thì **grep** trên `DANH-MUC-CONG-CU.md`, KHÔNG đọc cả file (~530 KB ≈ 150k token). (3) danh mục
  đầy đủ `tools/vietnamize/DANH-MUC-CONG-CU.md` khi cần đọc mô tả dài.
- **Sinh lại sau MỖI lần cập nhật/cài/gỡ plugin** (3 lệnh, chạy trong thư mục này):
  `python tools/vietnamize/extract_catalog.py` → `python tools/vietnamize/build_danh_muc.py` →
  `python tools/vietnamize/build_trang_tra_cuu.py`. Chạy trên **CẢ HAI máy** — bản chụp
  `catalog_may/<Máy>.json` của máy nào chỉ máy đó cập nhật được, và trang tra gộp cả hai để
  gắn nhãn `[W]`/`[M]`. Bảng "Việc hay làm" sửa tay ở `tools/vietnamize/viec-hay-lam.json`
  (file DUY NHẤT trong bộ này sửa tay được; mọi thứ khác sinh tự động — **đừng sửa tay**).
- **Bộ `medsci-skills`: 9 plugin nhưng CÙNG MỘT bộ 58 skill byte-identical** (đã so md5). Đã
  **tắt 8, giữ `medsci-project`** trong `~/.claude/settings.json` → danh sách Windows 1405 → 941
  mục, **0 năng lực mất** (đã kiểm: cả 58 tên vẫn gọi được qua `/medsci-project:*`). **Tiền tố
  lệnh đổi**: `/medsci-review:check-reporting` → `/medsci-project:check-reporting`. Bật lại =
  đổi `false` → `true` (cache còn nguyên trên đĩa, không phải tải lại). **MÁY MAC CHƯA DỌN** —
  làm y hệt rồi chạy lại 3 lệnh trên. Muốn lấy lại ~230 MB đĩa: `claude plugin uninstall
  medsci-analysis@medsci-skills` (lặp cho 8 plugin đã tắt) — không bắt buộc.
- **Ba bẫy đã vá cùng ngày, đừng để tái phát:** (a) `extract_catalog.py` từng liệt kê cả plugin
  ĐANG TẮT → danh mục mời gọi lệnh gõ vào là không chạy; nay bỏ qua mục `enabledPlugins: false`
  (chỉ khi ghi RÕ `false`, vắng mặt thì giữ). (b) Khi một skill có nhiều cách gọi, cách được
  khuyên phải là cách chạy được ở NHIỀU MÁY nhất — không thì bảng chữ cái sẽ chọn
  `/medsci-analysis:*` (đã tắt) thay vì `/medsci-project:*`. (c) 7 script trong `tools/vietnamize/`
  từng chết giữa chừng trên Windows vì `print()` tiếng Việt gặp stdout cp1252 — nay tự ép UTF-8.

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
  (`ClaimTraceabilityLedger`) — CLI thứ ba, không nằm trong doctrine; package tự khai "OFFLINE·SYNTHETIC
  ONLY... NO-GO — NOT QUALIFIED FOR RESEARCH WORKFLOW USE". **Sửa 2026-07-23 (vòng lặp kiểm tra-hoàn
  thiện vòng 11, đã xác minh bằng thực nghiệm — không phải suy đoán):** `--approval-ledger` của lệnh con
  `project-controlled-readiness` CHỈ ĐỌC (`ApprovalLedger.from_file()` → `json.loads()`, không có
  `to_file()`/ghi nào trong toàn bộ `research_project/`) — khẳng định cũ "có thể ghi đè ledger nếu ai đó
  gõ nhầm" là SAI, đã rà lại; rủi ro thật của cờ này là ĐỌC một ledger G0-G9 thật rồi PHA TRỘN với khung
  milestone/artifact 00-18 hoàn toàn hư cấu của `research_project/`, in ra báo cáo PASS/BLOCKED có thể
  gây hiểu nhầm là xác nhận cổng thật nếu đọc thoáng qua.
  (3) `app/core/approval_service.py` (class `ApprovalCenter`) + `app/models/governance_v7.py` +
  `app/chronic_care/` — hệ role thứ ba (physician/PI/system_owner) phục vụ "Chronic Care Phase 3A
  shadow pilot" nội bộ bằng Python, KHÁC HOÀN TOÀN thư mục `chronic-care-clinic-os/` (Next.js) ở trên dù
  trùng tên "chronic care". **Sửa 2026-07-23 (vòng lặp vòng 11, phát hiện CRITICAL):** khẳng định cũ
  "không có route/CLI thật nào ghi vào DB này ngoài script seed test" SAI ở phần "không có route thật
  gọi vào cụm code" — `app/dashboard/main.py` (mở bằng `python run.py dashboard`, KHÔNG phải script seed
  test) có tab 14 "🫀 Chronic Care Shadow Pilot" gọi thật `app/chronic_care/dashboard.py` mỗi lần
  Streamlit rerun (rerun toàn bộ script trên MỌI tương tác widget ở CẢ 14 tab, không chỉ khi mở đúng tab
  14) — route này CÓ THẬT và chạy thường xuyên trong phiên làm việc thật của bác sĩ, dù tự giới hạn
  read-only/dữ liệu tổng hợp theo thiết kế Phase 3A (đã vá thêm 1 lỗi hệ quả: audit log JSONL từng phình
  vô hạn mỗi lần rerun — nay seed 1 lần/tiến trình). Phần "không ghi DB thật qua ORM" của khẳng định cũ
  vẫn ĐÚNG (ChronicCareService dùng dataclass in-memory riêng, không đụng `governance_v7.py`/ORM).
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
- **Về 5 nhánh mồ côi trên — ĐÃ CÓ TEST CANH GÁC, KHÔNG cần (và KHÔNG nên) dời/xóa file.** Rà lại
  2026-07-26 bằng câu lệnh import THẬT (không grep lỏng): các nhánh này không bị cổng thật import,
  và repo đã có 2 test chặn đúng việc đó — `tests/test_no_orphaned_citation_verification_in_real_gates.py`
  và `TestNoResearchProjectImportInRealGates` trong `tests/test_stakeholder_review_audit.py` — nên nếu
  ai lỡ nối dây, test đỏ ngay. Đồng thời đính chính 2 điểm hay bị hiểu nhầm: `runtime/` KHÔNG chết cả
  gói (chỉ `policy_gate_engine.py`+`controlled_orchestrator.py` mồ côi; `runtime/approval_ledger.py`
  là bộ ledger THẬT mà `tools/approve_gate.py` dùng), và `app/models/governance_v7.py` CÓ đường sống
  tới dashboard qua `app/dashboard/v7_readonly.py` → `app/governance/migrations.py`. Dời các file này
  sẽ phá ~30 file test mà không tăng an toàn.
- **VÁ BẢO MẬT LỚP CHỮ KÝ CỔNG 2026-07-26 (audit ĐỘC LẬP, không phải vòng lặp doctrine):** 30 vòng
  "kiểm tra-hoàn thiện" trước đó soi NỘI DUNG y khoa nên không chạm tới thiết kế mật mã. Ba lỗ hổng
  thật đã vá trong `tools/gate_contract.py`: (1) payload ký cũ KHÔNG chứa `reviewer_role` → một chữ ký
  hợp lệ dùng lại được cho vai trò khác (đổi nhãn role trong JSON là qua cổng G2/G8) — nay role +
  reviewer_ref nằm trong payload (định dạng `v2:<phạm-vi>:<hex>`), và hỗ trợ **khóa RIÊNG theo vai
  trò** `~/.ebm-secrets/gate_approval_key_<NHÓM>` (`setup_gate_approval_key.py --role IRB`) để tách vai
  trò thành bằng chứng THẬT thay vì lời tự khai; (2) `EBM_GATE_KEY_PATH` ghi đè được ở vận hành thật →
  nay chỉ có tác dụng dưới pytest; (3) `ledger_approved()` FAIL-OPEN khi máy chưa cấu hình khóa (mọi đề
  tài ngoài `REAL_STUDY_DENYLIST` — danh sách phải nhớ cập nhật TAY — đều được coi là đã duyệt) → nay
  fail-closed mặc định, ngoại lệ duy nhất là đề tài đã tự tay đánh dấu `study_kind=synthetic_test`.
  Kèm theo: `run_g10_assemble.py` khi bị ép qua bằng `--i-know-*-not-*` nay trả **mã thoát 3**, không
  còn trả 0 (trước đây caller đọc mã thoát tưởng gói đủ điều kiện nộp). Hồi quy đối kháng:
  `tests/test_gate_signature_role_binding_20260726.py`. **Lưu ý vận hành:** khóa chung ký được MỌI vai
  trò, nên `approve_gate.py` nay NÓI RÕ mức bảo đảm ("shared" vs "role") thay vì im lặng — muốn G2/G8
  có bằng chứng độc lập thật thì phải tạo khóa riêng và để người duyệt đó giữ.

- **SỔ CÁI PHÊ DUYỆT NAY CÓ NIÊM PHONG (2026-07-27) — ĐỌC TRƯỚC KHI ĐỤNG VÀO `exports/`:**
  mỗi đề tài nay có THÊM file `exports/<study>/approval_ledger.seal.json` bên cạnh
  `approval_ledger.json`. **TUYỆT ĐỐI KHÔNG xóa, không sửa tay, không bỏ qua khi sao lưu/đồng
  bộ** — nó là con dấu (số bản ghi + vân tay đuôi, đã ký) và là thứ DUY NHẤT phát hiện được
  việc **cắt đuôi sổ cái** (gỡ bản ghi cuối, thường là một quyết định THU HỒI). Kèm theo, mỗi
  bản ghi nay ký cả `prev_hash` (chuỗi băm liên kết) nên **xóa/đảo/chèn bản ghi đều bị bắt**.
  **Hệ quả vận hành cần nhớ:** (1) từ nay **sửa tay `approval_ledger.json` sẽ làm mọi cổng của
  đề tài đó BỊ CHẶN** — muốn thay đổi phải chạy `tools/approve_gate.py` (nó tự niêm phong lại);
  (2) nếu bị chặn, thông điệp lỗi nói RÕ lý do (chưa ai duyệt / đã bị THU HỒI / sổ cái có dấu
  hiệu bị sửa / nội dung đã đổi sau khi duyệt) — đọc lý do trước khi làm gì; (3) đường phục hồi
  chuẩn khi sổ cái mang dấu vết từ máy hoặc khóa khác: **ký lại trên máy hiện tại**.
  `tools/stakeholder_review_audit.py` cũng đã kiểm chuỗi+dấu nên nó KHÔNG còn nói khác cổng thật.
  ⚠️ Còn MỘT giới hạn chưa đóng, cần bác sĩ quyết vì đổi QUY TRÌNH: HMAC là mật mã ĐỐI XỨNG nên
  máy xác minh buộc phải giữ khóa ⇒ **không chứng minh được người ký độc lập với chủ nhiệm đề
  tài**. Muốn có bảo đảm đó phải chuyển sang chữ ký BẤT ĐỐI XỨNG (Ed25519): người duyệt giữ khóa
  RIÊNG, máy chỉ giữ khóa CÔNG.

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
- **Triển khai giám sát định kỳ fail-closed:** owner thu thập duy nhất là `medical-ebm-automation/scripts/weekly_safety.sh` + `monthly_update.sh`; routine khác chỉ dùng candidate queue. `source_health=PARTIAL/FAIL` giữ watermark, chặn bridge Hub/cảnh báo nội dung. Chỉ `READY_FOR_CONTROLLED_DEPLOYMENT` từ `python medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py --online` mới cho phép candidate-only; canary, runtime tuần/tháng, alert, rollback, 2 chu kỳ shadow và UAT/phê duyệt thật là bắt buộc. Claude Code không tự điền PASS hoặc ký UAT.
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
- **(4) Xuất Word chi tiết — MẶC ĐỊNH TỰ CHẠY ở bước cuối mỗi dashboard lâm sàng (bác sĩ chốt 2026-07-18; trước đó chỉ chạy khi yêu cầu riêng):**
  `python3 EBM-Dashboards/tools/build_dashboard_docx.py <dashboard>.html --verified` (SỬA 2026-07-22, vòng lặp
  kiểm tra-hoàn thiện vòng 10, phát hiện HIGH: trước đây file .docx LUÔN khẳng định cứng "đã xác minh qua
  PubMed/Crossref" bất kể `verify_dashboard.py --online` đã PASS hay chưa cho dashboard đó — cờ `--verified`
  PHẢI truyền khi bước này chạy sau `verify_dashboard.py --online` đã PASS trong CÙNG lượt (đúng thứ tự pipeline
  mặc định dưới đây); không truyền → tool tự hạ câu chữ thành "CẦN xác minh", không khẳng định sai) — tự trích khối `DATA` từ dashboard
  (không gõ lại tay, tránh sai lệch), dựng `.docx` gồm trang bìa+cảnh báo, mục lục tự động, khối tóm tắt màu
  (nên làm/không nên/cờ đỏ), MỖI mục chứng cứ 1 bảng riêng có huy hiệu MÀU mức chứng cứ + quyết định (khớp
  đúng bảng màu Evidence Workbench: xanh lá=Cao/Áp dụng ngay, cam=Trung bình-Thấp/Cân nhắc, đỏ=Rất thấp/Chưa
  đủ), dòng "Khuyến cáo/Hành động" tô nền làm điểm nhấn, font Times New Roman toàn văn. TỰ CHẠY MẶC ĐỊNH ở
  BƯỚC CUỐI mỗi dashboard (nối tiếp verify_dashboard→build_library→sync_all), KHÔNG cần hỏi lại; file ra
  `EBM-Dashboards/derivatives/`. Parser JS→JSON của tool nhận CẢ khối `DATA` nháy đơn LẪN nháy kép (vá
  2026-07-18: trước chỉ nhận nháy kép nên vỡ với DATA nháy đơn theo quy ước template EW/DA). Tuỳ chọn `--parts <file.json>` để nhóm mục theo "phần" lớn
  khi dashboard gộp nhiều chủ đề con (như VKDT: chẩn đoán-điều trị / bệnh kèm / đối tượng đặc biệt); không
  truyền thì liệt kê tuần tự dưới 1 mục "Nội dung chứng cứ". **Mac hiện KHÔNG có Node.js/LibreOffice/pandoc/
  Homebrew** → KHÔNG dùng nhánh docx-js của skill `docx`; dùng thẳng `python-docx` (đã có sẵn trong venv
  `~/.ebm-venv`). Xác thực output bằng `scripts/office/validate.py` của skill `docx` (kiểm XSD OOXML thuần
  Python) thay cho bước dựng ảnh xem trước (soffice+pdftoppm) mà máy này không chạy được; chú ý bẫy thứ tự
  phần tử `tcPr`/`pPr` khi tự ghép XML bằng oxml (`tcBorders` phải trước `shd`; `pBdr` phải trước `spacing`).
- **(5) KÊNH TRÌNH BÀY THỨ 3 — "Bản tin chứng cứ trong khung chat" (chốt 2026-08-05):** khi bác sĩ hỏi ngay
  trong hội thoại (giữa hai bệnh nhân, trên điện thoại), mở dashboard/Word là quá chậm → trả lời bằng bản tin
  đọc thẳng trong khung chat claude.ai, theo bộ khung 8 khối cố định của
  `dashboard_mockups/templates/CHAT-BRIEF-SPEC.md`. **Cùng khối `DATA`** với 2 kênh kia, chỉ khác cách trình
  bày: rút gọn được, **thêm khẳng định mới thì KHÔNG** — mỗi câu phải truy được về một `items[]` của dashboard
  đã PASS `verify_dashboard.py --online`. Hai bẫy riêng của kênh này (đã ghi thành luật trong spec): (a) nén
  mạnh làm rụng mệnh đề điều kiện ("ngoài thai kỳ", "nếu không chống chỉ định") → biến câu đúng thành lời
  khuyên sai; (b) khung chat không có cột "kết cục" nên số liệu phải tự gắn đúng kết cục nó đo (vd RR 0,72 của
  sắt tĩnh mạch là kết cục GỘP nhập viện + tử vong tim mạch, KHÔNG phải "giảm nhập viện"). Chưa tự động hoá:
  bước tiếp là thêm đầu ra thứ 4 cho `make_derivatives.py` — chờ bác sĩ duyệt vì tool này có 3 bản đồng bộ.

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
- **Kiểm riêng rubric QA ↔ LESSONS taxonomy:** `python tools/verify_lessons_rubric_alignment.py` — bắt mọi mã lỗi rubric thiếu hàng taxonomy/bridge để vòng Evaluate→Learn không hở.
- **Kiểm riêng clinical runtime governance:** `python tools/verify_clinical_runtime_schema_hardening.py` — chốt source integrity, prompt injection, conflicting evidence trong schema.
- **Kiểm riêng pipeline cập nhật chứng cứ lâm sàng:** `python tools/verify_clinical_evidence_update_pipeline.py` — kiểm Evidence Workbench→verify_dashboard→library→derivatives→hợp đồng sync_all bằng fixture offline không PII.
- **Kiểm cổng triển khai giám sát ngoại trú:** `python medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py --online` — PASS cuối chỉ khi đủ runtime + UAT thật; pre-commit/audit dùng `--contract-check` để kiểm fail-closed mà không giả lập phê duyệt.
- **Kiểm LIÊM CHÍNH NỘI DUNG tài liệu nghiên cứu (mới 2026-07-31):**
  `python tools/verify_exports_integrity.py` (trong `medical-ebm-automation/`; `--staged` cho hook,
  `--path <file>` cho một tài liệu). Kiểm 5 luật trên file `.md` dưới `exports/`: toàn vẹn
  placeholder bảng dự kiến kết quả · định dạng PMID/DOI · disclaimer · dấu vết định danh · cân
  bằng markdown. **Đã nối vào `.githooks/pre-commit` của repo y khoa.**
  **Lý do tồn tại:** ngày 31/07/2026 commit `a21a01f` đi qua TOÀN BỘ chốt pre-commit **sạch hoàn
  toàn** trong khi file đề cương C1a đang hỏng 26 chỗ — placeholder giá trị (`n = —`, `cOR = —`,
  ô `— (—; —) [ref]`) bị một bước xử lý văn bản đổi nhầm thành dấu phẩy. Mọi chốt trước đó chỉ
  kiểm **đồng bộ agent/doctrine**, không chốt nào đọc **nội dung tài liệu nghiên cứu**; lỗi chỉ lộ
  ra nhờ có người đối chiếu tay với bản git trước đó. Đã kiểm bằng 3 phép thử: bản hỏng → 18 lỗi
  CHẶN; bản đã sửa → sạch; 42 tài liệu `exports/` → 0 lỗi chặn, 1 cảnh báo (không dương tính giả);
  thử commit thật file hỏng → hook chặn, HEAD không đổi. **Phạm vi cố ý hẹp:** chỉ bắt dấu hiệu
  hỏng máy đọc được, KHÔNG chấm chất lượng khoa học, KHÔNG thay quality gate G0-G10.
- **Chạy chu trình tự động có kiểm soát:** `python tools/run_controlled_automation_cycle.py` — gom sync/routing/gate/dữ liệu/phản biện-thống kê/clinical governance thành một quyết định fail-closed hoặc human-gated.
- **Orchestrator chạy được (control plane 6 năng lực, dry-run):** `python tools/run_orchestrator.py "<ca/đề tài/câu hỏi>"` — định tuyến intent → dựng plan theo flow → dừng ở cổng bác sĩ → chốt guardrail. `--capabilities`/`--validate`/`--resume`. Tài liệu + 43 test (gồm cầu THẬT `guardrail_bridge.py`→`tools/eval/run_eval.py` vá dead-code `guardrail_fail` — xem `orchestrator.py::_guardrail_reroute_loop`; `appraisal_bridge.py` là seam mô phỏng riêng, CHƯA cắm vào orchestrator.py, 5/43 test): `tools/orchestrator/`.
- **"Đề tài này THỰC SỰ đang ở đâu, còn gì phải làm?" (mới 2026-07-27):**
  `python tools/study_readiness.py --study <mã>` (hoặc `--all`). Trả lời đúng câu hỏi mà
  `list_studies.py` KHÔNG trả lời được: nó đếm **việc CHƯA làm** từ chính tài liệu của đề tài
  (ô `[ ]` trong mọi file `.md`), gắn cờ **QUYẾT ĐỊNH CÒN TREO** (loại có thể làm thay đổi đề
  cương), liệt kê **chỗ còn để trống** (tên chủ nhiệm, mã IRB, mã đăng ký…), và với cổng CỨNG
  chỉ ghi "ĐÃ KÝ" khi **ledger xác nhận thật** — không tin checkpoint.
  **Lý do tồn tại:** hệ thống ĐÃ BIẾT đề tài C1a còn 31 việc (nằm trong `_checklist-noi-bo.md`
  của chính nó) nhưng **không lệnh nào nói ra**, nên dễ hiểu nhầm là "sắp xong". `list_studies.py`
  thậm chí không nhận ra C1a là đề tài (nó sinh qua workflow agent, không qua `run_g*_auto.py`).
  Công cụ **cố ý bi quan**: chỉ đếm việc chưa làm, **không bao giờ in chữ "sẵn sàng"** — kết luận
  đó thuộc thẩm quyền bác sĩ và Hội đồng Đạo đức.
- **Chấm cổng G0 (câu hỏi nghiên cứu) — mới 2026-07-28:**
  `python tools/g0_quality_gate.py --study <mã>`. Chấm lại G0 từ artifact + `study_meta.json`
  đã có, **không gọi lại PubMed** (chạy được nhiều lần trong lúc bác sĩ điền dần).
  **Lý do tồn tại:** G0 từng là cổng DUY NHẤT trong chuỗi không có hợp đồng chất lượng
  riêng — `run_g0_auto.py` in "✅ G0 HOÀN THÀNH" và thoát mã 0 trên MỌI đề tài, kể cả khi
  toàn bộ ô P/I/C/O còn là placeholder; tức cổng khởi đầu tuyên bố hoàn thành khi **câu hỏi
  nghiên cứu chưa tồn tại**. Nay 3 trạng thái: `BLOCKED` (mã 3) · `DRAFT_READY_NEEDS_HUMAN_
  REVIEW` (mã 2 — kết quả ĐÚNG của lần chạy tự động đầu tiên, không phải lỗi) ·
  `PASS_G0_CONFIRMED` (mã 0, chỉ khi bác sĩ đã chốt). **Nơi chốt là `exports/<study>/
  study_meta.json → gate_params.G0`**, KHÔNG phải file `.md` (file .md bị ghi đè mỗi lần
  chạy lại G0 — nay có sao lưu `.bak-*` trước khi đè). G0 cũng đã tra **ClinicalTrials.gov**
  tự động (§3.6 của artifact) để trả lời "đã có ai ĐANG LÀM chưa" — PubMed chỉ biết cái ĐÃ
  CÔNG BỐ; PROSPERO/WHO ICTRP không có API mở nên chỉ sinh link, bác sĩ tự tra.
  **Ba phát hiện của đợt audit toàn diện G0-G10, 2026-07-30 (cùng đợt với G3/G4/G8/G9 ở trên):**
  (1) 3/9 luật của `guardrail_check_g0()` (R6 nhãn `[CẦN...]`, R7 disclaimer, R_LABEL "[BẢN
  NHÁP TỰ ĐỘNG]") là TAUTOLOGY_GUARDRAIL — `generate_a1_artifact()` in CỨNG cả ba chuỗi này
  VÔ ĐIỀU KIỆN nên không nhánh nào của pipeline thật khiến 3 luật đó BLOCK được; đã thêm
  comment trung thực tại chỗ (không phát minh điều kiện giả) nói rõ phạm vi thật: chỉ bắt
  được tampering/truncation SAU khi artifact đã sinh, không phải kiểm nội dung cho đề tài cụ
  thể — cùng tinh thần nhãn `PASS_G8_REVIEW_RECORDED`/`PASS_G4_SAP_LOCKED` không mang chữ
  "ĐỘC LẬP". (2) `refresh_checkpoint()` (cập nhật `G0_checkpoint.json["quality_gate"]` khi
  chấm ĐỘC LẬP, không qua `run_g0_auto.py`) hoá ra ĐÃ ĐƯỢC vá xong trong CÙNG đợt audit này
  trước khi tới lượt việc này — xác nhận lại bằng lời gọi hàm thật (`evaluate_study(write=True)`
  trên checkpoint cũ chưa có khối `quality_gate`) và bổ sung 4 test hồi quy (mutation-tested)
  vì trước đó module chưa có test nào phủ đúng hành vi này. (3) Doctrine `cau-hoi-nghien-cuu.md`
  từng liệt "scaffold đề tài đã tạo" là một THÀNH PHẦN của "Đạt G0" — mâu thuẫn thời gian với
  chính BƯỚC 0 của agent đó (`scaffold_research_project.py` chỉ chạy SAU KHI đã
  `PASS_G0_CONFIRMED`) và `g0_quality_gate.py` chưa từng chấm mục này; đã sửa doctrine thay vì
  thêm một tiêu chí máy giả tạo (sẽ luôn PASS vì exports/<study>/ + checkpoint LUÔN tồn tại
  tại thời điểm evaluate_study() chạy được — cùng lỗi tautology vừa vá ở (1)). Kiểm hồi quy:
  `pytest tests/test_g0_quality_gate_20260728.py` (47 test).
  **Giới hạn CÒN LẠI, CHẤP NHẬN CÓ CHỦ Ý (audit tích hợp plugin, 2026-07-31 — chưa từng ghi ở
  đây, dù đã có comment tại chỗ trong code từ lần sửa R5):** `guardrail_check_g0()` R5 (chặn câu
  hỏi nghiên cứu lồng chỉ thị lâm sàng sớm, vd "Nên dùng statin cho BN X không?" đọc nhầm thành
  y lệnh) đã hẹp phạm vi để không còn chặn oan câu hỏi PICO hợp lệ dạng "có nên dùng X cho bệnh
  nhân Y không?" — nhưng đổi lại, một chỉ thị lâm sàng THẬT lồng trong vỏ câu hỏi kiểu mệnh lệnh
  cụ thể hơn (vd "Có nên kê ngay 500mg X cho bệnh nhân tại phòng cấp cứu không?") **từ nay LỌT
  qua R5**, khác hành vi trước bản vá. Đây là đánh đổi precision/recall có chủ ý (không có bộ
  phân tích ngữ nghĩa tiếng Việt để phân biệt chính xác hơn bằng regex) — G0 chỉ là bước đầu
  (chưa qua Cổng A), nhưng vẫn là một guardrail an toàn có đường lách bằng cách diễn đạt lại
  câu; ghi nhận ở đây để không bị coi là "đã đóng hoàn toàn" khi tra cứu lại sau này. Xem
  `tools/run_g0_auto.py` quanh dòng có R5 để đọc nguyên văn giới hạn.
- **Danh sách + theo dõi TẤT CẢ đề tài (mới 2026-07-17):** `python tools/list_studies.py` — quét `exports/*/`, phân loại đề tài nhận diện được (topic + cổng xa nhất + mốc IRB/SAP/DB-khóa/kết quả/G9-ký) vs thư mục lạ vs thư mục RỖNG (nghi bị bỏ dở/gõ nhầm mã `--study`). `--study <mã>` xem chi tiết 1 đề tài; `--json` xuất máy đọc. Mỗi đề tài LUÔN có thư mục riêng `exports/<study>/` dùng xuyên suốt G0-G10 (mọi `run_g*_auto.py` ghi vào đó theo `--study`); `run_g0_auto.py` tự cảnh báo (không chặn) nếu `--study` trùng mã một đề tài khác hẳn về topic, tránh trộn lẫn dữ liệu 2 đề tài vào cùng thư mục.

- **Hợp đồng CHẤT LƯỢNG cổng G3 — cỡ mẫu (mới 2026-07-28):**
  `python tools/g3_quality_gate.py --study <mã>`. Tự chạy sẵn ở bước cuối của
  `run_g3_auto.py`, không cần gọi tay; gọi tay khi muốn CHẤM LẠI sau khi bác sĩ điền thêm nguồn.
  **Vì sao có:** guardrail cũ của G3 (`guardrail_check`, nhãn "R1–R7") chỉ soi VĂN BẢN do chính
  `generate_artifact()` vừa sinh ra, nên hầu hết luật là TỰ ĐÚNG — R3/R4/R5/R6/R7 kiểm sự có mặt
  của những câu in cứng trong template ("DRAFT", tiêu đề "PHÂN TÍCH ĐỘ NHẠY", 3 nhãn "[CẦN BÁC SĨ]",
  dòng disclaimer) nên không bao giờ fail được, còn R1 (PMID) là mã chết vì artifact không in PMID
  nào. Hệ quả: "G3 ✅ PASS" cũ chỉ có nghĩa **"hàm sinh artifact đã chạy"**. Lớp mới kiểm **CON SỐ
  và NGUỒN**: 18 tiêu chí tự động (G3-AUTO-00…17) + 7 tiêu chí người thật (G3-HUMAN-01…07), neo vào
  chuẩn đã xác minh sống (DELTA2 · ICH E9/E9(R1) · CONSORT 2025 **mục 16a/16b** — KHÔNG còn là 7a
  của bản 2010 · SPIRIT 2025 mục 19 · STROBE mục 10 · STARD 2015 mục 18 · TRIPOD+AI mục 10 ·
  Riley/pmsampsize · Buderer 1996 · TSA/RIS · FDA & EMA về biên non-inferiority · CONSORT cluster).
  **4 trạng thái rời nghĩa:** `BLOCKED` → `DRAFT_NEEDS_HUMAN_PARAMETERS` →
  `DRAFT_READY_NEEDS_STATISTICIAN_REVIEW` → `PASS_G3_CONFIRMED`. Kết quả ghi vào
  `exports/<study>/G3_QUALITY_REPORT.{json,md}` + khóa `quality_gate` trong `G3_checkpoint.json`.
  **Bác sĩ điền xác nhận ở đâu:** `study_meta.json` → `gate_params.G3` (`effect_source` kèm
  PMID/DOI/MCID, `effect_source_confirmed`, `p0_source`/`p_event_source`/`sd_source`/
  `dropout_source`/`prevalence_source`, `powered_for_outcome`, `hypothesis_confirmed`,
  `recruitment_feasibility_confirmed`, `reviewed_by_role` = STATISTICIAN hoặc PI, `reviewed_at`,
  `software`; thêm `ni_regulatory_framework`/`margin_justification`/`margin_source` cho
  non-inferiority, và `icc`/`icc_source`/`cluster_size`/`n_clusters` cho thiết kế theo chùm).
  **Ba giới hạn phải nhớ:** (1) G3 **KHÔNG phải cổng ký** — `_GATE_REQUIRED_STAKEHOLDERS` không khai
  stakeholder cho G3 và `approve_gate.py` không nhận `--gate G3`, nên `PASS_G3_CONFIRMED` là lời
  **tự khai có dấu vết**, KHÔNG phải bảo đảm mật mã như G2/G4/G5/G8/G9/G10; (2) lớp này **CỐ Ý KHÔNG đổi mã
  thoát** của `run_g3_auto.py` (19 file test + `run_pipeline`/`pipeline_freshness` dựa vào hợp đồng
  3 mã thoát cũ) — muốn quality BLOCKED chặn cứng cả pipeline là đổi QUY TRÌNH, cần bác sĩ quyết;
  (3) artifact `G3_QUALITY_REPORT.json` đăng ký ở `audit_research_gates.py` với `required=False`
  (khác G2 là `True`) vì `tools/verify_research_gate_contracts.py` ở thư mục gốc dựng fixture G3 chỉ
  với `G3_A4_SAMPLE_SIZE_AUTO.md` — nâng lên bắt buộc phải sửa ĐỒNG THỜI cả hai file.
  Kiểm hồi quy: `pytest tests/test_g3_quality_gate.py` (60 test, đã kiểm bằng 4 phép đột biến).

- **NĂM LỖ HỔNG LỘ RA KHI ĐỀ TÀI THẬT ĐẦU TIÊN ĐI QUA G0-G4 (2026-07-31, đề tài hài lòng
  người bệnh C1a):** trước ngày này, cả 19 đề tài mà `list_studies.py` nhận diện được đều là
  **fixture test**; đề cương C1a (953 dòng) sinh qua workflow agent nên chưa từng có checkpoint
  hay quality gate nào chấm. Cho đề tài thật chạy qua dây chuyền đã lộ ra 5 lỗi **cùng một lớp:
  toàn bộ G3/G4 ngầm giả định nghiên cứu là SO SÁNH HAI NHÓM**, trong khi mô tả cắt ngang là
  thiết kế phổ biến nhất ở tuyến cơ sở. (1) `run_g3_auto.py` BLOCK mọi đề tài mô tả không truyền
  `--effect-size`, dù thiết kế này tính cỡ mẫu theo ĐỘ CHÍNH XÁC (Lwanga & Lemeshow, WHO 1991) và
  không có effect size — muốn chạy phải nhét tỷ lệ p vào ô `--effect-size`, chính
  `tests/test_g3_confirmed_n.py` cũng phải làm vậy; nay có `--prevalence` và `--precision` riêng.
  (2) Sai số d bị cố định 0,05. (3) `g3_quality_gate.EFFECT_TYPES_BY_DESIGN['cross_sectional']`
  đã khai `{'PREVALENCE'}` từ trước nhưng `run_g3_auto.py` chưa bao giờ sinh ra tên đó — hai
  module viết cho nhau mà chưa từng nối. (4) Bảng độ nhạy dùng khung "Power × Effect size" cho
  mọi thiết kế (vô nghĩa với mô tả: ba dòng power bằng nhau) và tiêu đề tự khai "điều chỉnh N%
  dropout" trong khi ô là N TRƯỚC dropout; nay sinh bảng p × d và parser của quality gate đọc
  được. (5) **NGHIÊM TRỌNG NHẤT — `run_g4_auto.py` ghi N tối thiểu vào SAP thay vì cỡ mẫu KẾ
  HOẠCH**: `confirmed_n` trước đây chỉ dùng cho sr_ma/prediction/qualitative, nên SAP của C1a ghi
  "N = 453" trong khi Hội đồng đã chốt n = 1000. SAP là tài liệu ĐƯỢC KÝ VÀ KHÓA; ghi sai N ở đây
  khiến phân tích sau này lệch khỏi chính SAP đã khóa — đúng loại sai lệch mà G4 sinh ra để ngăn
  (chữ ký mật mã chỉ bảo vệ TOÀN VẸN nội dung, không bảo đảm nội dung ĐÚNG). Đã vá đồng thời
  `run_g4_auto.py` + `g4_quality_gate.py` (sửa một bên sẽ khiến bên kia báo lệch giả), N hiệu lực
  = `confirmed_n` cho MỌI thiết kế, in kèm dòng "N tối thiểu theo thống kê" để không giấu thông
  tin. Kiểm hồi quy: toàn bộ 3053 test pass. **Bài học vận hành:** fixture test không thay được
  một đề tài thật đi hết dây chuyền; 4 trong 5 lỗi này nằm im qua hàng chục vòng audit doctrine.
- **Hợp đồng CHẤT LƯỢNG cổng G4 — khóa SAP (mới 2026-07-29, từ kiểm toàn diện G0-G10):**
  `python tools/g4_quality_gate.py --study <mã>`. Tự chạy ở bước cuối `approve_gate.py --gate G4`
  sau khi ký thành công (khuôn dòng gọi giống G2/G5/G9/G10); gọi tay khi muốn CHẤM LẠI.
  **Vì sao có — G4 là cổng ký thật DUY NHẤT (cùng G2/G5/G8/G9/G10) chưa từng có lớp
  quality_gate riêng.** Guardrail nội bộ của `run_g4_auto.py` 3/4 luật (R4/R6/R7) là tautology
  (đếm đúng chuỗi mà `generate()` LUÔN in cứng); luật thật (R3) chỉ chạy MỘT LẦN ngay sau sinh
  artifact, không ai gọi lại trên nội dung bác sĩ vừa sửa. Chốt gác thật DUY NHẤT trước khi ký —
  `approve_gate._g4_sections_still_draft()` — chỉ đếm placeholder "[CẦN" ở §1/§2/§5/§10, không
  kiểm bất kỳ nội dung phương pháp luận nào (EPV/VIF, MCAR/MAR/MNAR, đa so sánh khớp alpha) mà
  doctrine `thiet-ke-nghien-cuu.md` đòi hỏi — thay mỗi "[CẦN...]" bằng "OK" vẫn ký sạch. **Lỗ hổng
  nghiêm trọng nhất:** không có bước nào đối chiếu lại số liệu ĐÃ KÝ (alpha/power/N/effect/margin ở
  §12 SAP) với `G3_checkpoint.json` HIỆN TẠI — một SAP bị sửa tay, hoặc sinh ra TRƯỚC khi G3 chạy
  lại với tham số khác, vẫn ký sạch mà không ai biết (chữ ký mật mã chỉ bảo vệ TOÀN VẸN nội dung
  đang có, không bảo đảm nội dung đó còn ĐÚNG với cỡ mẫu thật). Cuối cùng: tín hiệu "G4 đã khóa" mà
  `skill_standards.real_world_signals()`/`g7_quality_gate.py`/`list_studies.py` đọc
  (`g4_lock_date`/`g4_status`) trước đây KHÔNG được `approve_gate.py` cập nhật khi ký thật.
  **12 tiêu chí tự động (G4-AUTO-00…11) + 7 tiêu chí ký người thật (G4-HUMAN-01…07).** Đáng chú ý:
  G4-AUTO-03 đọc lại §12 bằng regex rồi so với G3_checkpoint.json SỐNG (không phải bản đã lưu lúc
  sinh SAP) — BLOCK nếu lệch bất kỳ giá trị nào; G4-AUTO-05/G4-AUTO-04 CỐ Ý không đếm sự có mặt của
  MCAR/MAR/MNAR (template mặc định ĐÃ in sẵn "MAR" nên đếm-có-mặt sẽ tautology y hệt lỗi vừa vá ở
  G3/G8) mà đếm placeholder "[CẦN" của biến imputation chưa điền; G4-AUTO-07 (subgroup tiền định,
  chống HARKing) kiểm §7 — mục KHÔNG nằm trong `_g4_sections_still_draft()` nên trước đây có thể ký
  dù còn nguyên placeholder; G4-AUTO-08 bắt kiểu "thay [CẦN] bằng OK" (đòi tên+phiên bản phần mềm
  VÀ seed số nguyên cụ thể, không chỉ vắng mặt placeholder); G4-AUTO-09 chặn CỨNG (BLOCK) khi
  hypothesis_type≠superiority mà margin(Δ) rỗng — an toàn tối quan trọng của NI/equivalence.
  **4 trạng thái:** `BLOCKED` → `DRAFT_NEEDS_HUMAN_CONTENT` → `READY_FOR_SIGNATURE` →
  `PASS_G4_SAP_LOCKED` (KHÔNG mang chữ "ĐỘC LẬP", cùng lý do HMAC-đối-xứng đã ghi ở G8). Bác sĩ điền
  xác nhận ở `study_meta.json → gate_params.G4` (`epv_vif_reviewed`, `missing_data_mechanism_confirmed`,
  `subgroup_multiplicity_predefined_confirmed`, `reviewed_by_role`, `reviewed_at` — khóa `G4` mới
  thêm vào `_GATE_PARAMS_SKELETON` của `gate_contract.py`); margin cần thêm `gate_params.G3.margin_source`
  + `margin_justification` (tái dùng khóa G3 đã có, không tạo bản sao). `refresh_checkpoint()` GHI
  `g4_lock_date` từ TIMESTAMP LEDGER THẬT khi LOCKED — đóng khoảng trống tín hiệu phân mảnh; đồng thời
  `skill_standards.real_world_signals()` nay chấm TRỰC TIẾP qua `g4_quality_gate.evaluate_study()`
  khi có `quality_contract_version` (mirror nhánh G5/G9), không còn tin field cũ.
  **Ba điều TUYỆT ĐỐI không đổi (cùng nguyên tắc G3/G8):** (1) tên artifact `G4_A5_SAP_FINAL_<study>.md`
  là hợp đồng downstream (guardrail/`approve_gate`/G5/G6/G9 đều dùng); (2) lớp này KHÔNG thêm điều
  kiện chặn ký mới vào `approve_gate.py` — `_g4_sections_still_draft()` vẫn là chốt trước-ký DUY
  NHẤT, module chỉ CHẤM LẠI và BÁO CÁO (nhất quán cách G3/G8 đã chọn, không đổi exit-code của
  `run_g4_auto.py`/`approve_gate.py` mà nhiều test đã khóa); (3) artifact `G4_QUALITY_REPORT.json`
  đăng ký ở `audit_research_gates.py` với `required=False` (giống G3/G8, khác G2) vì fixture của
  `tools/verify_research_gate_contracts.py` chỉ dựng artifact SAP — nâng bắt buộc phải sửa đồng thời.
  Kiểm hồi quy: `pytest tests/test_g4_quality_gate.py` (56 test, đã kiểm bằng 3 phép đột biến; gồm
  3 test tích hợp chạy CLI thật — sinh SAP → điền → ký bằng khóa vai trò → LOCKED + `g4_lock_date`
  khớp ledger, và mô phỏng G3 chạy lại sau khi ký để xác nhận G4-AUTO-03 bắt được).

- **Hợp đồng CHẤT LƯỢNG cổng G8 — bình duyệt độc lập (mới 2026-07-28):**
  `python tools/g8_quality_gate.py --study <mã>`. Tự chạy ở bước cuối `run_g8_auto.py`.
  **Vì sao có — KHÁC hẳn G3:** lớp mật mã của G8 rất dày và ĐÚNG (chữ ký HMAC payload v4 buộc
  nhóm vai trò · chuỗi băm `prev_hash` · con dấu niêm phong · `run_g10_assemble.py` fail-closed).
  Chỗ hỏng nằm ở **NỘI DUNG**: artifact mà chữ ký G8 ràng buộc vào —
  `G8_A9_PRESUBMISSION_<study>.md` — là **bản TỰ KIỂM do chính `run_g8_auto.py` sinh từ checkpoint
  G0–G7**, KHÔNG có mục nào chứa nhận xét của người bình duyệt. Nên chữ ký G8 hợp lệ chỉ chứng
  minh "một người truy cập được khóa đã xác nhận bản tự kiểm này", KHÔNG chứng minh "đã có bình
  duyệt độc lập". Cộng thêm: **HMAC là mật mã ĐỐI XỨNG** nên máy xác minh buộc phải giữ khóa đã
  ký ⇒ hệ KHÔNG chứng minh được người ký khác chủ nhiệm; `per_role_key_available()` chỉ chứng
  minh MỘT FILE tồn tại trên cùng máy. Vì vậy nhãn đạt **cố ý là `PASS_G8_REVIEW_RECORDED`, KHÔNG
  mang chữ "ĐỘC LẬP"**.
  **Lớp mới kiểm 3 nhóm chưa ai làm:** (1) NỘI DUNG bản thảo — vệt công cụ nội bộ còn sót (nhãn
  `[CẦN]`, tên file pipeline, "(A) hay (B)", TODO — doctrine xếp mức CHẶN) và **báo cáo kết quả
  chọn lọc** (kết cục chính trong bản thảo phải khớp SAP G4); (2) nghĩa vụ **ICMJE bản 1/2026** —
  Mục V.A (khai AI ở CẢ cover letter lẫn bản thảo, cấm AI làm tác giả, cấm trích dẫn nội dung AI
  làm nguồn gốc), **Mục V.B (người PHẢN BIỆN phải khai dùng AI + cam kết bảo mật — khoảng trống
  hoàn toàn trong repo)**, III.L.1 đăng ký tiền cứu, III.L.3 chia sẻ dữ liệu đủ 5 trường
  ("undecided" bị từ chối cứng), IV.B cover letter 5 nhóm nội dung; (3) **dấu hiệu độc lập** —
  đối chiếu `reviewer_ref` của G8 với G2/G4/G5/G9 (trùng = một người ký nhiều vai trò) và đọc
  `approving_signature_scope` để hạ mức khẳng định khi ký bằng khóa CHUNG.
  **5 trạng thái:** `BLOCKED` → `DRAFT_NEEDS_HUMAN_COMPLETION` → `READY_FOR_INDEPENDENT_REVIEW` →
  `PENDING_REAL_REVIEW_SIGNATURE` → `PASS_G8_REVIEW_RECORDED`. Ra
  `exports/<study>/G8_QUALITY_REPORT.{json,md}`. Bác sĩ điền ở `study_meta.json → gate_params.G8`.
  **Đòi thêm một artifact MỚI:** `G8_PEER_REVIEW_REPORT_<study>.md` — bản nhận xét THẬT của người
  phản biện theo mẫu `binh-duyet.md` (khuyến nghị 4 mức · lỗi nghiêm trọng kèm vị trí · góp ý nhỏ
  · câu hỏi cho tác giả · kết luận tổng thể). Máy KHÔNG sinh file này và không nên sinh.
  **Ba điều TUYỆT ĐỐI không đổi:** (1) tên `G8_A9_PRESUBMISSION_<study>.md` là hợp đồng ba bên
  (run_g8_auto ghi · run_g10_assemble tra ledger · doctrine dạy gõ tay vào `approve_gate --artifact`)
  và nội dung bị băm trong chữ ký — tên "A9" lệch crosswalk (A9 thật = DMP ở G5, bình duyệt = A15)
  là lệch ĐÃ BIẾT, sửa tên sẽ vô hiệu mọi chữ ký cũ; (2) mã thoát 3 bậc của `run_g8_auto.py`;
  (3) 6 điều kiện quyết định `g8_status` (lớp mới chỉ BÁO CÁO thêm, không thay — SỬA 2026-07-31:
  con số đúng là 6, không phải 5, xem ngay dưới).
  **"Một lệch nội bộ CÒN đúng... chưa sửa" ĐÃ LỖI THỜI (sửa 2026-07-31, phát hiện qua audit tích
  hợp plugin — rà lại các mục "chưa sửa" cũ):** dòng cũ ở đây nói `g8_status` chỉ tính 5/6 điều
  kiện (bỏ ngoài checklist ≥60%) — bug đó thật ra đã được vá **2026-07-29** (commit `bc2890a`,
  `decide_g8_status()` trong `run_g8_auto.py` nhận đủ 6 biến gồm `reporting_ok`), **trước cả khi
  dòng "chưa sửa" này được viết** — chỉ có 2 nơi mô tả bug (comment trong `g8_quality_gate.py` +
  chính dòng CLAUDE.md này) quên cập nhật theo. Đã sửa cả 2 nơi + 1 chuỗi `rep_evidence` từng lộ
  ra ngoài báo cáo cho bác sĩ ("run_g8_auto.py KHÔNG tính điều kiện này") — nay đọc đúng: G8-AUTO-10
  là lớp kiểm ĐỘC LẬP THỨ HAI (đọc lại checkpoint), không phải cửa duy nhất. Kiểm hồi quy:
  `pytest tests/test_g8_quality_gate.py -k checklist_duoi_nguong`.
  **Hai lệch khác đã VÁ (audit toàn diện G0-G10, 2026-07-30):** `_item_auto_check` trước đây đánh
  ☑ mục CONSORT/STROBE chỉ vì **file checkpoint cổng trước tồn tại**, không đọc bản thảo — nay đọc
  thật `G7_A8_MANUSCRIPT_<study>.md`, chỉ ☑ khi phần I/II tương ứng không còn nhãn `[CẦN`;
  `guardrail_g8` R6 (đếm nhãn `[CẦN...]`) từng thưởng việc dán nhãn và PHẠT chính việc bác sĩ điền
  thật (một gói THỰC SỰ gần xong có thể tụt dưới ngưỡng và bị chặn oan) — nay chỉ còn cảnh báo
  thông tin, không chặn; đồng thời `G8-AUTO-00` (guardrail nền) nay chạy LẠI guardrail thật trên
  artifact hiện tại thay vì tin `checkpoint["guardrail"]` đóng băng. Kiểm hồi quy:
  `pytest tests/test_g8_quality_gate.py` + `tests/test_g8_r6_and_item_auto_check_20260730.py`
  (mutation-tested). **Nhãn "ICMJE 2023" ĐÃ ĐƯỢC SỬA, không còn là việc tồn đọng (đính chính
  2026-07-31):** dòng cũ ở đây nói lỗi thời còn sót ở `run_g2_auto.py:1120` và
  `run_g7_auto.py:1382` — kiểm lại trực tiếp cả hai vị trí xác nhận nội dung hiện tại ĐÃ đúng chuẩn
  ("ICMJE Recommendations, Updated January 2026 — Mục V"); số dòng trong ghi chú cũ đã lệch do các
  lần sửa khác chèn/xóa dòng ở giữa, khiến việc "chưa vá" trông như còn tồn tại dù thực ra đã xong
  từ trước.

- **Hợp đồng CHẤT LƯỢNG cổng G9 — liêm chính tác giả & sẵn sàng công bố (mới 2026-07-28, tài
  liệu hóa 2026-07-30 — trước đó bị bỏ sót, khác hẳn G0/G3/G8 đều có mục riêng cùng ngày xây):**
  `python tools/g9_quality_gate.py --study <mã>`. Tự chạy ở bước cuối `run_g9_auto.py`; gọi tay để
  CHẤM LẠI sau khi bác sĩ bổ sung xác nhận.
  **Vì sao có:** doctrine cũ (`nop-bai-phan-hoi.md`) hứa "bác sĩ chỉ cần đọc, ký 3 xác nhận và
  nộp" (COI đầy đủ · tác giả đồng ý bản cuối · không đăng kép) — nhưng `approve_gate.py --gate G9`
  thật ra chỉ cho ký khi `g9_quality_gate.py` trả `READY_FOR_G9_PI_APPROVAL`, đòi **toàn bộ nhóm tiêu
  chí người thật** (ICMJE 4 tiêu chí + CRediT + COI + `evidence_ref` cho TỪNG tác giả · thứ tự
  tác giả/guarantor · khai AI đủ tools/purposes/confirmed_at · Data Availability đủ chi tiết
  ICMJE cho thử nghiệm lâm sàng · quyền truy cập dữ liệu/độc lập nhà tài trợ theo ICMJE 1/2026 · liêm chính công bố (similarity/image integrity/kết quả khớp
  phân tích khóa) · venue due diligence · ethics/privacy · **xác nhận thể chế** — trưởng đơn
  vị/hội đồng nội bộ/nhà tài trợ, thêm 2026-07-31, xem G9-HUMAN-11 dưới) — doctrine mô tả ít
  hơn hẳn code thật.
  **4 trạng thái:** `BLOCKED` → `DRAFT_READY_NEEDS_REAL_ATTESTATIONS` →
  `READY_FOR_G9_PI_APPROVAL` → `PASS_G9_PUBLICATION_INTEGRITY_LOCKED`. Ra
  `exports/<study>/G9_QUALITY_REPORT.{json,md}` từ `G9_PUBLICATION_READINESS.json` +
  `G9_A10_AUTHOR_INTEGRITY_<study>.md` + `G9_checkpoint.json`.
  **4 phát hiện đã vá cùng đợt tài liệu hóa này:** (1) STANDARDS_BASIS từng trích SAI DOI cho
  "COPE authorship and AI guidance" (`10.24318/LQU1h9US` trỏ nhầm sang một tài liệu 2017 về xuất
  bản luận văn — đã xác minh qua redirect thật) — sửa thành `10.24318/cCVRZBms`; (2) `G9-AUTO-02`
  (guardrail nền) từng đọc `checkpoint["guardrail"]` đóng băng — nay chạy LẠI
  `guardrail_check_g9()` trên file A10 thật; luật R5 (đếm `[CẦN`) từng xung đột trực tiếp với
  `_documents_clean()`/G9-AUTO-05 (đòi CHÍNH file đó sạch placeholder để coi là sẵn sàng nộp) —
  một gói THỰC SỰ hoàn chỉnh sẽ luôn bị R5 cũ chặn oan — nay chỉ còn cảnh báo thông tin; (3) thêm
  `G9-HUMAN-10` đối chiếu `reviewer_ref` của người ký G9 với G2/G4/G5/G8 (mirror `G8-HUMAN-04`,
  vốn đã nhắm cả tới G9 nhưng G9 chưa từng soi ngược lại) — CỐ Ý không gate trạng thái LOCKED (chỉ
  4 trạng thái, không có mức trung gian như G8, nên gate sẽ tạo bẫy con-gà-quả-trứng); (4) checkpoint
  tự mâu thuẫn nguồn chuẩn AI disclosure ("COPE + Nature Portfolio 2024" vs header thật "ICMJE Mục
  V, cập nhật 01/2026") — thống nhất về ICMJE Mục V. **Còn hở, chưa sửa:** checklist "Phần 8 —
  Hard Gate" mà bác sĩ đọc/ký trên giấy/Word vẫn tách rời khỏi cổng máy-chấm thật (đã thêm dòng
  LƯU Ý trỏ đúng lệnh `g9_quality_gate.py`/`approve_gate.py --gate G9`, nhưng không có cơ chế đọc
  ngược trạng thái tick ☐/☑). Kiểm hồi quy: `pytest tests/test_g9_quality_gate.py` +
  `tests/test_g9_reviewer_ref_cross_check_20260730.py` +
  `tests/test_g9_auto02_stale_cache_and_r5_20260730.py` (mutation-tested).

_Nguyên mẫu cũ `ebm-copilot/`: `pip install -r requirements.txt` → `python -m src.research.digest` → `pytest tests/` (chỉ để tham chiếu)._
