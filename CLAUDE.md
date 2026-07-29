# EBM Copilot — Trợ lý AI cho Bác sĩ Y học Bằng chứng

## Mục tiêu
Hệ thống tự động hóa cho bác sĩ ngoại trú thực hành EBM, gồm 3 module:
Research (nghiên cứu), Clinical (lâm sàng), Knowledge (quản lý kiến thức).

## Điều phối Agent — hành vi MẶC ĐỊNH (đội `.claude/agents`, 50 agent: 21 lâm sàng + 28 nghiên cứu + 1 guardrail dùng chung; +3 lâm sàng 2026-06-16 (dau-man-tinh·cham-soc-giam-nhe·tram-cam-lo-au); +2 lâm sàng 2026-07-04 (quan-ly-khang-dong — kháng đông trọn vòng; tham-dinh-do-chinh-xac-chan-doan — thẩm định độ chính xác chẩn đoán QUADAS-2/GRADE-cho-test, lấp khoảng trống audit))
Khi bác sĩ nêu việc lâm sàng hoặc nghiên cứu, MẶC ĐỊNH định tuyến tới "nhạc trưởng" phù hợp và để nó **tự chạy tuần tự theo Giao thức tự động** (không hỏi vặt từng bước):
- **Nêu một CA/tình huống lâm sàng** ("tôi có bệnh nhân…", "khám ca này", hỏi chẩn đoán/điều trị) → `dieu-phoi-lam-sang`: tự chạy 5 bước EBM (Hỏi→Tìm→Thẩm định→Áp dụng→Theo dõi); **cờ đỏ nêu NGAY**; dừng ở **Cổng A** (áp dụng cho BN) + **Cổng B** (ghi sổ cái).
- **Nêu một ĐỀ TÀI/câu hỏi nghiên cứu** (chỉ cần tên đề tài) → `dieu-phoi-nghien-cuu`: tự khôi phục trạng thái từ sổ cái → suy loại thiết kế → march G0→G10; dừng ở 6 cổng cứng (G2 đạo đức · G4 khóa SAP · G5 khóa dữ liệu thật · **G8 bình duyệt độc lập** · G9 liêm chính tác giả · G10 PI khóa gói phát hành) + nơi cần dữ liệu/phê duyệt thật. Mỗi cổng fail-closed theo ĐÚNG role (IRB/thống kê viên hoặc PI/quản lý dữ liệu hoặc PI/phản biện độc lập/PI/PI — xem `tools/gate_contract.py`), không chỉ "có ai đó ký".
- **Việc lẻ** (tra 1 câu hỏi, soát 1 danh mục TLTK, tính cỡ mẫu, đặc tả biến…) → gọi thẳng agent chuyên trách.
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
  (3) 5 điều kiện quyết định `g8_status` (lớp mới chỉ BÁO CÁO thêm, không thay).
  **Ba lệch nội bộ đã ghi nhận, CHƯA sửa:** artifact in "6 điều kiện BẮT BUỘC" nhưng `g8_status`
  chỉ tính 5 (checklist ≥60% bị bỏ ngoài); `_item_auto_check` đánh ☑ mục CONSORT/STROBE chỉ vì
  **file checkpoint cổng trước tồn tại**, không đọc bản thảo; `guardrail_g8` R6 vẫn thưởng việc
  dán ≥8 nhãn `[CAN`. Kiểm hồi quy: `pytest tests/test_g8_quality_gate.py` (42 test, đã kiểm bằng
  4 phép đột biến). **Nhãn "ICMJE 2023" lỗi thời còn sót ở `run_g2_auto.py:1120` và
  `run_g7_auto.py:1382`** (chưa vá vì thuộc file phiên khác đang sửa).

_Nguyên mẫu cũ `ebm-copilot/`: `pip install -r requirements.txt` → `python -m src.research.digest` → `pytest tests/` (chỉ để tham chiếu)._
