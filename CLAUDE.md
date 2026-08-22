# EBM Copilot — Trợ lý AI cho Bác sĩ Y học Bằng chứng

## Mục tiêu
Hệ thống tự động hóa cho bác sĩ ngoại trú thực hành EBM, gồm 3 module:
Research (nghiên cứu), Clinical (lâm sàng), Knowledge (quản lý kiến thức).

## Điều phối Agent — hành vi MẶC ĐỊNH (đội `.claude/agents`, 50 agent: 21 lâm sàng + 28 nghiên cứu + 1 guardrail dùng chung; +3 lâm sàng 2026-06-16 (dau-man-tinh·cham-soc-giam-nhe·tram-cam-lo-au); +2 lâm sàng 2026-07-04 (quan-ly-khang-dong — kháng đông trọn vòng; tham-dinh-do-chinh-xac-chan-doan — thẩm định độ chính xác chẩn đoán QUADAS-2/GRADE-cho-test, lấp khoảng trống audit))
Khi bác sĩ nêu việc lâm sàng hoặc nghiên cứu, MẶC ĐỊNH định tuyến tới "nhạc trưởng" phù hợp và để nó **tự chạy tuần tự theo Giao thức tự động** (không hỏi vặt từng bước):
- **Nêu một CA/tình huống lâm sàng** ("tôi có bệnh nhân…", "khám ca này", hỏi chẩn đoán/điều trị) → `dieu-phoi-lam-sang`: tự chạy 5 bước EBM (Hỏi→Tìm→Thẩm định→Áp dụng→Theo dõi); **cờ đỏ nêu NGAY**; dừng ở **Cổng A** (áp dụng cho BN) + **Cổng B** (ghi sổ cái).
- **Nêu một ĐỀ TÀI/câu hỏi nghiên cứu** (chỉ cần tên đề tài) → `dieu-phoi-nghien-cuu`: tự khôi phục trạng thái từ sổ cái → suy loại thiết kế → march G0→G10; dừng ở 6 cổng cứng (G2 đạo đức · G4 khóa SAP · G5 khóa dữ liệu thật · **G8 bình duyệt độc lập** · G9 liêm chính tác giả · G10 PI khóa gói phát hành) + nơi cần dữ liệu/phê duyệt thật. Mỗi cổng fail-closed theo ĐÚNG role (IRB/thống kê viên hoặc PI/quản lý dữ liệu hoặc PI/phản biện độc lập/PI/PI — xem `tools/gate_contract.py`), không chỉ "có ai đó ký".
- **Bảo đảm chuẩn nghiên cứu hiện hành:** G2 fail-closed khi WHO TRDS v1.3.1 mục 13/14/19/20 thiếu dữ kiện khoa học PI đã pin hoặc tham chiếu Hội đồng chỉ là fallback; G9 fail-closed khi thiếu quyền truy cập dữ liệu/độc lập nhà tài trợ theo ICMJE 1/2026. `python3 tools/verify_controlled_research_automation.py` kiểm hành vi này cùng danh sách 6 cổng canonical; không dùng PASS kỹ thuật thay IRB/PI/thống kê viên/phản biện.
- **Nêu VẤN ĐỀ CHỨNG CỨ (định tuyến bổ sung 15/08/2026 — «nêu vấn đề là tự giải quyết»):**
  (a) hỏi tại điểm khám («X xử trí thế nào?») → `python3 tools/tra_diem_kham.py "<câu hỏi>"`
  trả lời <1s CHỈ từ thẻ đã duyệt, ngoài phạm vi thì nói «chưa giám sát» + tự ghi tín hiệu
  watchlist; (b) «cập nhật chứng cứ chủ đề X» → `python3 ops/orchestrator.py --topic "X"
  --online` (A2 quét→A4 truy nguyên→B2 cổng→B5 hàng chờ; chủ đề chưa có dashboard thì
  orchestrator tự dừng ở bước PHIÊN NGƯỜI = gọi skill `cap-nhat-chung-cu-y-khoa`);
  (c) gói duyệt tuần TỰ nằm sẵn thứ Bảy 07:07 (tác vụ lịch `goi-duyet-tuan-ebm`).
  Mọi nhánh dừng ở CANDIDATE — Cổng A/B của bác sĩ nguyên vẹn.
- **Việc lẻ** (tra 1 câu hỏi, soát 1 danh mục TLTK, tính cỡ mẫu, đặc tả biến…) → gọi thẳng agent chuyên trách.
- **Điều phối plugin (MỘT OWNER):** quyền sở hữu canonical nằm ở
  `.claude/agents/_PLUGIN-ROUTING-CONTRACT.md` +
  `tools/orchestrator/plugin_ownership_registry.json`. `dieu-phoi-nghien-cuu` sở hữu vòng đời
  G0–G10; `dieu-phoi-lam-sang` sở hữu ca ngoại trú. ARS/Anthropic/BMAD/Bio chỉ là worker đúng
  allowlist/stage, không tự hợp nhất kết quả, không đổi trục cổng và không mở Cổng A/B/G. Yêu cầu
  đích danh plugin chỉ ưu tiên worker, không chuyển quyền owner. Kiểm fail-closed bằng
  `python3 tools/verify_plugin_orchestration.py`.

### Định tuyến khi NHIỀU công cụ cùng nhận một việc — LUẬT BẮT BUỘC (rà 2026-08-10)

**Vấn đề đã đo, không phải giả định.** Máy này đang bật 10 plugin = **846 skill**. Với mỗi việc
có cổng, số công cụ tự nhận làm được là: thiết kế nghiên cứu **53** · viết bản thảo **25** · chọn
tạp chí **21** · tổng quan-gộp **16** · bình duyệt **14** · thống kê **12** · khử định danh **11**
· kiểm trích dẫn **9** · cỡ mẫu **7**. Trong mỗi nhóm **chỉ 1 công cụ biết đến cổng G0–G10,
ledger và `study_meta.json`**; phần còn lại trả ra kết quả trông hợp lệ mà **không để lại dấu vết
cổng nào**. Registry `plugin_ownership_registry.json` có chặn, nhưng nó chỉ chạy trong
`tools/orchestrator/` — vốn tách rời luồng thật. Bảng dưới đây là luật cho **luồng thật**.

| Việc | CHỦ duy nhất (dùng cái này) | Tuyệt đối KHÔNG thay bằng |
|---|---|---|
| Cỡ mẫu / power | `co-mau-nghien-cuu` → `run_g3_auto.py` + `g3_quality_gate.py` | mọi `*sample-size*`, `*power-calculator*` của plugin |
| Thiết kế đề cương / SAP | `thiet-ke-nghien-cuu` → `run_g4_auto.py` + `g4_quality_gate.py` | 47 skill `*-planner`/`*-designer` của aipoch |
| Kiểm trích dẫn | `kiem-chung-trich-dan` + `check_citation_retraction.py` | `reference-integrity-checker`, `verify-refs`, `citation-*` |
| Bình duyệt (G8) | `binh-duyet` + `g8_quality_gate.py` | `sci-paper-reviewer`, `peer-review*` của plugin |
| Tổng quan / gộp | `tong-quan-y-van`, `meta-phan-tich` | `ma-end-to-end`, `systematic-review*`, `meta-*` của aipoch |
| Thống kê | `phan-tich-thong-ke` → `run_stats_analysis.py` | mọi `*statistical-analysis*` của plugin |
| Viết bản thảo | `viet-ban-thao` | 21 skill `*-section-writer`/`*-writer` của aipoch |
| Nộp bài / COI / khai AI | `nop-bai-phan-hoi` + `g9_quality_gate.py` | `cover-letter-*`, `journal-*`, `target-journal-matcher` |
| Khử định danh / PII | `quan-ly-du-lieu` + quy tắc KHÔNG PII | `deidentify*`, `openmed:*deident*` |
| Ca lâm sàng | `dieu-phoi-lam-sang` (dừng Cổng A/B) | mọi skill lâm sàng của plugin |

**Ba luật nền:**
1. **Plugin không bao giờ là chủ của việc có cổng.** Được gọi thì chỉ ở vai worker, đầu ra phải
   qua chủ chuẩn hoá rồi qua `tham-dinh-dau-ra`. Bác sĩ gọi đích danh plugin cũng KHÔNG đổi chủ.
2. **Không có chủ trong bảng → hỏi bác sĩ, không tự chọn plugin.** Đặc biệt với việc chạm vào
   `exports/*/approval_ledger*.json`, `study_meta.json`, `EBM_MASTER.json` — plugin bị cấm ghi.
3. **`humanizer` KHÔNG được chạy trên nội dung y khoa đã qua cổng** — nó sửa câu chữ, đủ để làm
   lệch một mệnh đề điều kiện ("ngoài thai kỳ", "nếu không chống chỉ định") mà không ai thấy.

**Nhóm 0 lượt dùng (quét 2712 phiên):** `aipoch-medical-research` (605 skill) · `openmed-skills`
(72) · `medsci-project` (59) · `mattpocock-skills` (41) · `pubmed-search` (10) = **787 skill chưa
từng gọi một lần**. Vẫn để bật theo quyết định của bác sĩ 2026-08-10, nên bảng trên là thứ DUY
NHẤT giữ chúng khỏi lọt vào việc có cổng. Tầng thật sự tạo giá trị là **MCP** (2528 lượt gọi,
riêng PubMed 1322) và **agent tự viết** (~125 lượt), không phải tầng skill của plugin.
- **Chốt kiểm đầu ra (MẶC ĐỊNH):** mỗi nhạc trưởng/routine lâm sàng, ở **bước cuối trước khi trả bác sĩ**, gọi guardrail `tham-dinh-dau-ra` soi gói theo **2 lớp** — **Lớp 1 LIÊM CHÍNH** R1–R7 (nguồn · PII · vượt cổng A/B/G · tự gán mức · tách 2 trục · nhãn [CẦN…] · disclaimer, mọi gói) + **Lớp 2 CHẤT LƯỢNG Med-PaLM 2** Q1–Q7 (dễ đọc · đúng đắn · đầy đủ · thiên kiến · nguy cơ hại · cập nhật · thẩm quyền nguồn — chỉ gói lâm sàng; `_CHUAN-CHAT-LUONG-MEDPALM.md`); gói lâm sàng chỉ phát hành khi ĐẠT cả 2 lớp, còn lỗi đỏ → TRẢ-VỀ-SỬA, Q2/Q5 đỏ → chuyển bác sĩ. Cơ chế & giới hạn: `.claude/agents/_KIEM-DUYET-DOC-LAP.md`.
- Bất biến: mỗi đầu ra kèm **PMID/DOI** + "Cần bác sĩ kiểm chứng"; **KHÔNG bịa, KHÔNG PII**; agent chỉ ĐỀ XUẤT, bác sĩ duyệt mới "áp dụng". Bản đồ đội: `.claude/agents/README.md`.
- **Đồng bộ Mac:** thư mục `.claude/agents/` nằm trong OneDrive → tự sync sang MacBook; trên Mac mở `claude` ngay trong thư mục `~/OneDrive/Claude AI` là dùng được cùng đội agent (đợi OneDrive xanh trước khi đổi máy).
- **Kiểm tra AN TOÀN đồng bộ — MẶC ĐỊNH trước khi làm việc/đổi máy:** chạy `python3 tools/sync_safety_check.py` (hoặc bấm đúp **`Kiểm tra An toàn Đồng bộ.command`**) để soi 4 nguy cơ đã gặp thật (conflict-copy OneDrive · git 2 repo lồng hỏng/treo · file lõi chưa tải thật · dấu hiệu máy/phiên khác vừa ghi). Verdict 🟢/🟡/🔴 (exit 0/1/2) — 🔴 nghĩa là DỪNG, không sửa gì cho tới khi xử lý xong mục đỏ. Thuần thư viện chuẩn Python, không cần venv/mạng, chạy được ngay cả khi môi trường EBM chưa cài. Nếu tool báo git repo hỏng (HEAD không giải được/`git fsck` báo "missing object" — dấu hiệu OneDrive đồng bộ dở `.git` sống, hay gặp khi 1 máy tạo git worktree bên trong cây OneDrive): trên máy CÒN đủ dữ liệu chạy `git bundle create <ten>.bundle --all` (ghi ra 1 file tĩnh, an toàn để OneDrive đồng bộ, khác với đồng bộ `.git` sống); đợi OneDrive xanh; máy thiếu chạy `git fetch <duong-dan-bundle> 'refs/*:refs/rescue/*'` rồi `git fsck --full` xác nhận sạch. Hoặc nhờ Claude Code soi từng mục.
- **Đồng bộ BỘ NHỚ (memory) giữa máy — KHÔNG tự sync, phải chạy tay:** bộ nhớ tự-động của Claude nằm ở `~/.claude/projects/<đường-dẫn-mã-hóa>/memory/` — **NGOÀI cây OneDrive** → đổi máy = "mất trí nhớ" dự án. Khắc phục: `python3 tools/sync_memory.py` (hoặc bấm đúp **`Đồng bộ Bộ nhớ.command`**) mirror 2 chiều sang `memory-sync/` (trong OneDrive, gitignored). **An toàn: file mới hơn thắng, KHÔNG xóa.** Chạy trên MỖI máy sau khi OneDrive xanh (máy A đẩy → máy B kéo về đúng đường-dẫn-mã-hóa của B). Các thứ NGOÀI OneDrive khác cũng phải làm lại mỗi máy: venv `~/.ebm-venv`, secrets `~/.ebm-secrets`, và cấp quyền lại MCP connectors.
- **Đồng bộ Claude Code ↔ Codex ChatGPT:** `.claude/agents/*.md` là nguồn biên tập chính; `.Codex/agents/*.toml` / `.codex/agents/*.toml` là bản sinh tự động. Sau khi sửa/thêm agent, chạy `python3 tools/enforce_agent_guardrails.py` → `python3 tools/sync_agents_to_codex.py` → `python3 tools/sync_agents_to_codex.py --check`; kiểm tra tổng thể bằng `python3 tools/audit_ebm_system.py`.
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
  `python3 tools/vietnamize/extract_catalog.py` → `python3 tools/vietnamize/build_danh_muc.py` →
  `python3 tools/vietnamize/build_trang_tra_cuu.py`. Chạy trên **CẢ HAI máy** — bản chụp
  `catalog_may/<Máy>.json` của máy nào chỉ máy đó cập nhật được, và trang tra gộp cả hai để
  gắn nhãn `[W]`/`[M]`. Bảng "Việc hay làm" sửa tay ở `tools/vietnamize/viec-hay-lam.json`
  (file DUY NHẤT trong bộ này sửa tay được; mọi thứ khác sinh tự động — **đừng sửa tay**).
- **🔴 NGUYÊN NHÂN GỐC của "gọi plugin mà không có" — NGÂN SÁCH DANH SÁCH SKILL (tìm ra 2026-08-10).**
  Claude Code chỉ dành `skillListingBudgetFraction` — **MẶC ĐỊNH 0.01 = 1% cửa sổ ngữ cảnh ≈ 8.000
  ký tự** — cho danh sách skill gửi cho model. Kho máy này cần **~45.000 ký tự CHỈ ĐỂ HIỆN ĐỦ TÊN**
  869 skill ⇒ **vượt 5,6 lần**. Vượt thì Claude Code **CẮT**: rụng mô tả trước, rồi rụng luôn skill.
  **Đây là lời giải cho cả hai than phiền lặp lại nhiều tháng của bác sĩ** — "gọi plugin đều không
  có" và "lúc đủ lúc không đủ": file vẫn ĐỦ trên đĩa, chỉ là model không được cho biết chúng tồn tại,
  và mỗi phiên lọt vào ngân sách một tập khác nhau. Nó cũng giải thích vì sao `mattpocock-skills`
  khai 25 skill mà chỉ 11 từng xuất hiện — phần còn lại bị cắt vì hết ngân sách, KHÔNG phải hỏng file
  (đã kiểm: cả 25 đều có file và YAML hợp lệ).
  **ĐÃ VÁ trong `~/.claude/settings.json`:** `skillListingBudgetFraction: 0.08` +
  `skillListingMaxDescChars: 80`. Sao lưu `.bak-20260810-195754` và `.bak-20260811-174341`.
  **Số đo thật (2 phép đo độc lập khớp nhau):** 933 mục cần **48.607 ký tự** để hiện đủ TÊN
  (869 skill plugin + 53 lệnh riêng + 10 skill riêng + ~8.000 ký tự cho skill dựng sẵn).
  Ngân sách 0,08 = 64.000 ký tự ⇒ **đủ toàn bộ, còn dư biên**.
  `maxDescChars: 80` là **trần chống vọt chi phí**: nếu cửa sổ ngữ cảnh lớn hơn 200k token thì
  0,08 mở ra nhiều ký tự hơn, và không có trần này Claude Code sẽ bơm mô tả đầy đủ (216.449 ký tự
  ≈ 54.000 token/lượt). Có trần thì chi phí ≤16.000 token (cửa sổ 200k) hoặc ≤31.000 (cửa sổ 1M).
  **Thang đánh đổi đã đo, để bác sĩ chọn lại khi cần:** chỉ tên 40.573 ký tự (~10k token) ·
  tên+mô tả ≤80 là 112.469 (~28k) · tên+mô tả đầy đủ 216.449 (~54k). Mô tả tiếng Việt đầy đủ đã
  có sẵn ở `TRA-CUU-CONG-CU.html` — **tra ở đó không tốn ngữ cảnh nào**, nên không cần mua mô tả
  đầy đủ bằng token.
  **Muốn rẻ hơn mà không mất năng lực:** dùng `skillOverrides` đặt các plugin ít dùng thành
  `"user-invocable-only"` — ẩn khỏi danh sách gửi cho model nhưng **vẫn gõ `/tên` gọi được**. Hợp
  với lối làm việc của bác sĩ: tra ở `TRA-CUU-CONG-CU.html` rồi gõ thẳng lệnh.
  ⚠️ Đây là khoá cấp NGƯỜI DÙNG (`~/.claude/settings.json`, NGOÀI OneDrive) ⇒ **máy Windows phải
  đặt lại bằng tay**, nếu không ở đó vẫn hỏng y như cũ.
  ✅ **ĐÃ ĐẶT TRÊN WINDOWS 12/08/2026** — cùng giá trị Mac (`0.08` + `maxDescChars: 80`); sao lưu
  `settings.json.bak-20260812-truoc-dat-skill-budget`. Chốt kho đi từ 🔴 (vượt ngân sách 5,1 lần)
  về 🟢. Đã ghi **mốc chuẩn riêng cho Windows**: 3 plugin · 668 skill (`tools/moc_chuan_plugin.json`)
  — đúng chủ ý của bác sĩ (3 bật + 8 medsci trùng đã tắt), KHÁC Mac (10 plugin · 870 skill) vì hai
  máy cài khác nhau, nên **mỗi máy tự `--ghi-moc` riêng, đừng chép mốc qua lại**.
- **✅ SKILL DÙNG NGUỒN CHUNG VÀ TỰ ĐỒNG BỘ (hoàn thiện 2026-08-20).**
  Lệnh `/anthropic-skills:<tên>` chạy bản nằm ở `~/Library/Application Support/Claude/
  local-agent-mode-sessions/skills-plugin/<uuid>/<uuid>/skills/<tên>/`. Trước 20/08 không có cơ chế
  tự đẩy từ `sync/skills/` sang đó. Đo ngày 13/08: **20/22 skill riêng đang chạy bản khác nguồn**,
  chỉ 2 khớp; `cap-nhat-chung-cu-y-khoa` chạy **v1.12.0** trong khi nguồn đã **v1.15.0** — toàn bộ
  bản vá cổng nguồn, bài học "73 mục bị che" và `13-source-universe.md` đều CHƯA tới nơi bác sĩ gọi.
  Đây là lời giải cho lớp bực bội "gọi skill mà nhận hành vi cũ".
  **Cơ chế hiện hành:** `sync/skills/` là nguồn duy nhất; `python3 tools/dong_bo_skill_claude_codex.py
  --ap-dung --dong-bo-plugin` nối trực tiếp sang `~/.claude/skills` + `~/.codex/skills`, đẩy Cowork
  bằng công cụ cũ, dựng lại catalog/ZIP router và giữ plugin Codex không cũ hơn Claude. Hook
  `SessionStart` tự chạy để bắt skill mới/registry mới; sửa nội dung skill có hiệu lực tức thời qua
  symlink. Không dùng LaunchAgent đọc OneDrive vì macOS TCC chặn tiến trình nền chưa được cấp quyền.
  ⚠️ **Quyết định chiều theo NỘI DUNG, KHÔNG theo `mtime`.** 6 skill từng có mtime runtime mới hơn
  (đều đúng mốc `21/06 18:12`) — đó là dấu thời gian **dựng lại hàng loạt**, không phải nội dung mới;
  kiểm nội dung thì runtime có **0 dòng riêng** còn nguồn nhiều hơn 1388 byte. Tin mtime sẽ chặn oan
  hoặc tệ hơn là ghi đè mất bản đầy đủ.
  **Hai luật của công cụ:** (a) runtime không có dòng riêng → nguồn bao trùm → đẩy; (b) runtime CÓ
  dòng riêng → chặn, TRỪ KHI nguồn có số phiên bản CAO HƠN (một lần tăng version là tuyên bố "bản
  này thay bản kia" — vẫn sao lưu trước khi ghi). Không có version ở một bên → không suy đoán, giữ
  nguyên chặn. **14 skill đang bị giữ lại chính là nhóm không tuyên bố version** — cần bác sĩ xem tay.
- **CHỐT KIỂM KHO CÔNG CỤ — tự chạy mỗi phiên (mới 2026-08-10).**
  `python3 tools/kiem_plugin_day_du.py` (0=🟢 · 1=🟡 · 2=🔴). Đã nối vào hook `SessionStart`
  ở `.claude/settings.json` với cờ `--im-khi-on` ⇒ **chỉ lên tiếng khi kho THIẾU**, im lặng khi đủ.
  **Vì sao có:** kho công cụ KHÔNG đứng yên trong một phiên. Đã đo 4 cơ chế: (a) cache plugin bị
  dọn rồi tự nạp lại giữa phiên — aipoch đi qua 605→360→438→475→605 trong MỘT phiên, bộ máy là
  marker `.in_use` + `.last-cleanup` + `.last_inuse_sweep`; (b) plugin kiểu thư mục đồng bộ lại từ
  repo nguồn; (c) phiên bản đổi giữa chừng (mattpocock 1.2.0→1.2.3 làm danh sách skill đổi theo);
  (d) **đường dẫn treo** trong `installed_plugins.json` → plugin biến mất im lặng.
  **(d) đã TÁI PHÁT ngay 10/08:** prune lúc 17:49 thì 17:52 file bị ghi lại, 8 mục medsci quay về
  và treo vì cache đã xoá.
  ⛔ **ĐÍNH CHÍNH 11/08 — lời khuyên trước đó ở dòng này là SAI và đã gây hại:** tôi từng ghi
  "gỡ hẳn 8 mục khỏi `enabledPlugins`, không chỉ đặt `false`". Làm vậy khiến Claude Code **CÀI LẠI
  cả 8 bộ** (278 MB tải về, 464 skill trùng tràn vào danh sách, suýt lại vượt ngân sách vừa vá).
  **Sự thật: vắng mặt trong `enabledPlugins` = BẬT, không phải tắt.** Cách bác sĩ đặt ban đầu —
  ghi rõ `false` — mới đúng và phải giữ nguyên. Đã khôi phục 10 BẬT · 8 TẮT.
  Hệ quả kèm theo: `extract_catalog.py` cũng đúng khi chỉ loại mục ghi RÕ `false` và GIỮ mục vắng mặt.
  **Mốc chuẩn** ở `tools/moc_chuan_plugin.json`, ghi bằng `--ghi-moc` khi kho đang đủ; **ghi RIÊNG
  trên mỗi máy** (Mac 10 plugin/870 skill; Windows khác). Sau khi cài/gỡ/cập nhật plugin có chủ ý
  thì phải `--ghi-moc` lại, nếu không chốt sẽ báo động nhầm.
  ⚠️ **Giới hạn cố ý:** công cụ đếm file `SKILL.md` TRÊN ĐĨA — con số đó KHÁC số skill Claude Code
  thật sự chào ra, vì mỗi plugin khai báo một kiểu trong `plugin.json` (`claude-code-harness` khai
  `["./skills/"]` cả thư mục; `medsci-project` khai 6 mà 58 skill vẫn gọi được; `mattpocock-skills`
  khai 25 mà chỉ 11 từng xuất hiện — **chưa giải thích được, đã kiểm: cả 25 đều có file và YAML hợp
  lệ**). Nên đây là chốt kiểm TOÀN VẸN CỦA KHO, KHÔNG phải bản kiểm kê thứ gọi được.
  ⚠️ **Thông báo skill giữa phiên là BẢN CHÊNH LỆCH, không phải kiểm kê**: đầu phiên liệt kê đầy đủ,
  giữa phiên chỉ liệt kê skill MỚI xuất hiện (đã thấy notice chỉ có 1–2 mục). Thấy "2 skill" mà
  tưởng hệ chỉ còn 2 là đọc nhầm — dùng lệnh trên để biết con số thật.
- **VIỆT HOÁ KHÔNG CÒN PHỤ THUỘC VÀO VIỆC SỬA FILE PLUGIN (đổi 2026-08-10).** Nguồn sự thật bền
  là **`tools/vietnamize/vi_descriptions.json`** (1664 mục, khoá theo `id`). Cả `build_danh_muc.py`
  lẫn `build_trang_tra_cuu.py` áp nó như **LỚP PHỦ lúc dựng** ⇒ danh mục và trang tra LUÔN tiếng
  Việt, kể cả khi bản cập nhật của plugin trả mô tả về tiếng Anh. Đã kiểm bằng thực nghiệm: ép
  toàn bộ 588 mô tả aipoch trong bản chụp về tiếng Anh rồi dựng lại → trang vẫn ra **604/604
  tiếng Việt**. `apply_vi.py` từ nay là **tuỳ chọn**, chỉ để menu gõ `/` trong Claude Code hiện
  tiếng Việt; bỏ qua nó không mất gì ở danh mục/trang tra.
- **RÀO AN TOÀN chống làm hỏng việc cập nhật plugin (2026-08-10).** `apply_vi.py` nay **TỪ CHỐI
  ghi vào bất kỳ file nào nằm trong một repo git** (trả `skip-git-repo`). Vì sao cần: plugin cài
  kiểu `"source": "directory"` (aipoch trỏ vào `~/Documents/GitHub/medical-research-skills`, là
  repo git thật của `github.com/aipoch/medical-research-skills`) — `extract_catalog.py` sẽ trỏ
  thẳng vào NGUỒN mỗi khi cache chưa dựng (máy mới · vừa gỡ-cài lại · vừa dọn cache). Ghi tiếng
  Việt vào đó = làm bẩn 605 file của repo ⇒ `git pull` lần sau XUNG ĐỘT và không cập nhật được
  plugin nữa. Bình thường công cụ chỉ chạm **cache** (`~/.claude/plugins/cache`) — cache là sản
  phẩm phái sinh nên sửa vào đó vô hại. **Trạng thái đã xác minh 10/08: repo nguồn aipoch SẠCH,
  0 file bị sửa, `git pull` an toàn.**
- **aipoch đã Việt hoá đủ 604/604** (532 bản dịch cũ + 72 bổ sung 10/08). Skill nào của aipoch
  TRÙNG việc có cổng (cỡ mẫu · thiết kế · phân tích gộp · đăng ký PROSPERO) đều mang sẵn cảnh
  báo ⚠️ trỏ về agent chủ, khớp với bảng định tuyến ở mục "Điều phối Agent". 8 thế mạnh RIÊNG
  của aipoch (MR · FAERS · độc chất mạng · đơn tế bào · đa omics · tái định vị thuốc · QTL) đã
  thêm vào bảng "Việc hay làm" — đây là các mảng hệ agent EBM không có.
- **Bộ `medsci-skills`: 9 plugin nhưng CÙNG MỘT bộ 58 skill byte-identical** (đã so md5). Đã
  **tắt 8, giữ `medsci-project`** trong `~/.claude/settings.json` → danh sách Windows 1405 → 941
  mục, **0 năng lực mất** (đã kiểm: cả 58 tên vẫn gọi được qua `/medsci-project:*`). **Tiền tố
  lệnh đổi**: `/medsci-review:check-reporting` → `/medsci-project:check-reporting`.
  **CẬP NHẬT 2026-08-10 — MAC ĐÃ DỌN, và câu "cache còn nguyên trên đĩa" KHÔNG CÒN ĐÚNG trên Mac:**
  cache của 8 plugin đã tắt đã bị xoá cùng đợt dọn 1306 MB, và mục của chúng đã được gỡ khỏi
  `installed_plugins.json` (gỡ cache mà để lại mục trong JSON chính là kiểu hỏng "plugin biến mất
  im lặng" ngày 05/08). Nên trên Mac, **bật lại = phải cài lại qua mạng**, không chỉ đổi `false`
  → `true`. Sao lưu trước khi dọn: `~/.claude/plugins/installed_plugins.json.bak-20260810-174911`
  và `~/.claude/settings.json.bak-20260810-174911`. Máy Windows chưa dọn cache — ở đó câu cũ vẫn đúng.
- **🔁 8 CỜ `false` NÀY BỊ APP XOÁ ĐỊNH KỲ — nay có công cụ, không sửa tay nữa (21/08/2026).**
  App ghi đè `settings.json` sau một số đợt cập nhật và xoá sạch các cờ `false`. Đã đo hai lần
  trên Mac: **17/08 (839→1311 skill)** và **21/08 (870→1319)**. Đây là hiện tượng ĐỊNH KỲ, không
  phải sự cố một lần. `python3 tools/kiem_co_tat_plugin_trung.py [--ap-dung]` khôi phục, đọc mốc
  chuẩn của CHÍNH máy để biết bộ nào bác sĩ giữ; đã nối vào `tu_sua_chua.py`, khoá bằng **BH69**.
  ⚠️ **Bẫy nguy hiểm hơn chính sự cố:** lúc đó chốt kho báo medsci-* là «MỚI so với mốc» và gợi ý
  `--ghi-moc`. **Làm theo là hỏng hẳn** — mốc sẽ nuốt luôn chỗ phồng và từ đó không chốt nào còn
  báo nữa, tức mất đúng cái giác quan sinh ra để canh. Khôi phục cờ TRƯỚC, ghi mốc SAU, và chỉ
  ghi khi việc cài/gỡ đúng là chủ ý của bác sĩ.
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
  `python3 tools/verify_clinical_runtime_schema_hardening.py`. Không gọi đây là production runtime
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
  (`build_library.py add`) → 3 sản phẩm phái sinh (`make_derivatives.py`) → **BỘ BỐN đồng thời**.
  **KHÔNG tự chạy `sync_all.py`/Antifacts nữa** (đổi 2026-08-05 — xem mục (3)). Không cần bác sĩ yêu cầu từng bước.
- **BỘ NĂM XUẤT ĐỒNG THỜI — MẶC ĐỊNH (bác sĩ chốt 2026-08-05; nâng BỘ BA→BỐN cùng ngày, →NĂM ngày 2026-08-10 khi thêm PDF giữ màu). MỘT lệnh duy nhất:**
  `python3 tools/xuat_goi_cap_nhat.py <dashboard>.html --online`
  Sinh cùng lúc và từ CÙNG một khối `DATA`: **① Dashboard** (đầu vào, đã qua cổng liêm chính) ·
  **② Bản đọc** `derivatives/<mã>_ban-doc.html` · **③ Bản Word** `derivatives/<mã>_TaiLieuChiTiet.docx` ·
  **④ Bản Word dạng HTML** `derivatives/<mã>_TaiLieuChiTiet.html` ·
  **⑤ Bản PDF GIỮ MÀU** `derivatives/<mã>_TaiLieuChiTiet.pdf`.
  Gộp một lệnh để các sản phẩm không bao giờ lệch phiên bản nhau — chạy rời rạc thì bản Word hoặc bản đọc
  dễ tụt lại một phiên bản so với dashboard mà không ai nhận ra.
  Cờ `--online` chạy `verify_dashboard.py --online` TRƯỚC; **chỉ khi cổng PASS thì bản Word mới được
  truyền `--verified`** (không PASS → tool docx tự hạ câu chữ thành "CẦN xác minh", không khẳng định sai).
  **CỔNG NGUỒN NGHIÊM NGẶT — bật 2026-08-11 (trước đó chưa bao giờ thi hành).** `DESIGN-SPEC.md` §6
  đòi `--online --strict-sources` từ đầu, nhưng dây chuyền chỉ chạy `--online`, nên nhóm luật mạnh
  nhất nằm im. Nay bước ①-bis chạy thêm `--strict-sources` và **tách hai loại lỗi**: thiếu
  `DATA.standards` ⇒ **chỉ CẢNH BÁO** (khối siêu dữ liệu ra đời SAU các bản cũ; "sửa" bằng cách bịa
  hợp đồng nguồn cho một lần tìm kiếm đã xảy ra chính là bịa provenance); `decision='apply'` trên
  `gradeLevel` na/low hoặc chỉ dựa Consensus ⇒ **CHẶN XUẤT, mã thoát 3**.
  **TUYỆT ĐỐI không nâng `gradeLevel`** (nâng mức cho nguồn không phân hạng là lỗi tự gán mức, R4 của
  `tham-dinh-dau-ra`).
  ⛔ **ĐÍNH CHÍNH 12/08 — câu "47/52 bản FAIL CHỈ VÌ thiếu `DATA.standards`, nội dung lâm sàng không
  sai" từng ghi ở đây là SAI, và nó CHE MẤT 73 mục nguy hiểm.** Vế "chỉ vì" là **ảo ảnh của một lệnh
  `return` sớm**: `verify_dashboard.py` (khoảng dòng 336) thoát NGAY khi thiếu `DATA.standards`, nên
  toàn bộ luật an toàn cấp item CHƯA TỪNG chạy trên 47 bản đó. Cổng báo đúng "1 lỗi cứng" — nhưng nó
  chưa hề đọc tới một item nào để có căn cứ nói nội dung không sai.
  **Đã bỏ `return` sớm.** Đo lại toàn bộ 61 dashboard sau khi vá: **73 mục `apply` trên chứng cứ
  yếu/không phân hạng, trên 16 dashboard** (trước khi vá chỉ thấy 4). Nặng nhất: VKDT_TongHop 17/07
  (13 mục) · SuyTim_TongHop 11/08 (12) · 05/08 (11) · 04/08 (8) · COPD_TimThanChuyenHoa (7) ·
  COPD_20260610 (5). Ví dụ TimMach_20260609 đi từ 1 lỗi → 10 lỗi.
  **Bài học chung, quan trọng hơn con số:** một cổng `return` sớm ở bước kiểm tra hình thức sẽ làm
  MỌI luật nội dung phía sau im lặng, mà đầu ra vẫn trông như đã soi đủ. Khi đọc kết quả cổng, phải
  hỏi "cổng đã chạy tới luật nào" chứ không chỉ đếm số lỗi.
  ⛔ **ĐÍNH CHÍNH 12/08 — câu "cách sửa ĐÚNG là HẠ `decision`" chỉ đúng MỘT NỬA.** Đem 32 mục bị chặn
  ra soi từng mục thì chúng thuộc HAI loại khác hẳn nhau, và hạ hết là làm giảm an toàn:
  **Nhóm B (17 mục) — chứng cứ yếu thật** (tổng quan tường thuật JAMA/Lancet/NEJM, thư gửi toà soạn,
  cohort n=66, Cochrane tự chấm GRADE thấp cho mọi kết cục): hạ `decision` xuống `consider` là ĐÚNG.
  **Nhóm A (15 mục) — nguồn QUY PHẠM** (guideline chính thức AGS Beers · NICE · ADA · AASLD · APASL ·
  IHS · EAN, và **nhãn thuốc FDA**): chúng để `gradeLevel:'na'` vì nguồn KHÔNG dùng thang GRADE, chứ
  không phải vì yếu. Hạ một **CHỐNG CHỈ ĐỊNH** (peginterferon ở xơ gan mất bù, AASLD+APASL xác nhận
  độc lập) hay **liều theo CrCl của nhãn FDA** xuống "cân nhắc" là làm GIẢM an toàn — đúng thứ cổng
  này sinh ra để ngăn.
  **Cách xử lý nhóm A: khai báo tường minh `normativeBasis`** — một trong `contraindication` ·
  `drug-label` · `official-classification` · `guideline-strong-rec` · `guideline-explicit-criteria`.
  Cổng chỉ miễn luật khi hội đủ BA điều kiện: `design` thật sự là Guideline/Nhãn thuốc (**Consensus
  KHÔNG BAO GIỜ đủ**) · `normativeBasis` hợp lệ · `gradeSource` có phân hạng nguyên bản. Miễn trừ chỉ
  áp cho `gradeLevel:'na'`; nguồn ĐÃ tự phân hạng `low`/`vlow` thì vẫn chặn. Khoá bằng
  `python EBM-Dashboards/tools/test_verify_dashboard_source_gate.py` (18 test, có test chống lách).
  🔴 **BUG PARSER đã vá cùng ngày — cổng từng nói SAI về dữ liệu ĐÚNG.** `field()` dùng lớp ký tự
  `[^'\"]*` nên DỪNG ở dấu nháy loại kia nằm BÊN TRONG chuỗi: giá trị
  `gradeSource:'"Usually Not Appropriate" — ACR'` bị đọc thành RỖNG, cổng báo "thiếu gradeSource" cho
  item có đủ dữ liệu. Trích nguyên văn phân hạng của nguồn gần như luôn có dấu nháy kép ⇒ lỗi nhắm
  thẳng vào trường quan trọng nhất. Vá xong còn **lộ ra 1 lỗi an toàn thật bị che từ trước**
  (COPD_DoiTuongDacBiet ITEM-17: `apply` trên Cochrane GRADE thấp) — đã hạ. Bài học: cổng nói sai về
  dữ liệu đúng nguy hiểm hơn cổng không chạy, vì nó tạo niềm tin sai.
  **`KNOWN_DESIGNS` cũng đã mở rộng có kỷ luật:** bộ cũ chỉ 5 giá trị trong khi thực tế 35 item/23
  loại nằm ngoài, gồm "Nhãn thuốc" và "Cảnh báo dược cảnh giác" — nay khớp theo HỌ (tiền tố), và
  design lạ chỉ CHẶN khi item đang `apply`, còn lại chỉ cảnh báo.
  **Trạng thái sau đợt rà 12/08: 60 dashboard → 13 PASS · 47 FAIL, và cả 47 chỉ vì thiếu
  `DATA.standards`** (nhóm chỉ-cảnh-báo). **0 lỗi an toàn còn lại.**
  🔴 **LỖI CỨNG MỚI 18/08/2026 — KHOÁ LẠ TRONG `DATA.summary` (chống VỨT ÂM THẦM nội dung an toàn).**
  `summary` chỉ được có ĐÚNG 4 khoá: `conclusion` · `doNow` · `dontDo` · `redFlags`. Template và **cả ba**
  bộ sinh phái sinh (`build_ban_doc_chung_cu.py` · `build_dashboard_docx.py` · `make_derivatives.py`) đều
  chỉ đọc đúng 4 tên đó. **Ca thật:** hai dashboard mới nhất (`BenhThanMan_ThieuMau` 16/08 và
  `DauManTinh` 18/08) ghi `notDo` ⇒ panel «Không nên / giới hạn» render **RỖNG trên MỌI sản phẩm** —
  đo được **0 mục** trong khối đó của cả hai bản đọc. Thứ bị giấu là nội dung an toàn thật: «KHÔNG ngừng
  opioid ĐỘT NGỘT ở người dùng dài hạn» và «không bình thường hoá Hb bằng ESA (đích 13-13,5 g/dL) — tăng
  biến cố tim mạch». **Không cổng nào bắt được** vì khối DATA vẫn đúng cú pháp và mọi luật khác vẫn chạy
  đúng — cùng HỌ với `return` sớm 12/08 (che 73 mục) và BH27 (fail-open A12): *công cụ vẫn chạy, vẫn in
  kết quả hợp lệ, nhưng thứ cần kiểm thì không bao giờ được kiểm.* Nay `verify_dashboard.py::kiem_khoa_summary`
  chặn **cứng** (chạy ở luồng LUÔN-CHẠY, không cần `--strict-sources`), khoá bằng **BH61**. Đã sửa cả 2 bản
  và **dựng lại trọn bộ năm** cho chúng — sửa nguồn mà không dựng lại phái sinh thì nội dung vẫn chưa tới tay
  bác sĩ. Muốn thêm trường mới vào `summary` thì phải nối dây ở CẢ 4 nơi rồi mới mở rộng `KHOA_SUMMARY_HOP_LE`.

  **ĐĂNG KÝ CHỦ ĐỀ — `python3 tools/dang_ky_chu_de.py` (thêm 12/08/2026).**
  Trả lời hai câu mà trước đây KHÔNG công cụ nào trả lời được: *bản nào còn hiệu lực?*
  và *có hai bản nào nói ngược nhau không?*
  **Phân biệt hai thứ rất dễ nhầm — nhầm là gây hại:**
  • **PHIÊN BẢN NỐI TIẾP** = cùng LÁT CẮT, khác ngày ⇒ bản mới THAY bản cũ. Thực tế chỉ có
    **2**: `SuyTim_TongHop` (3 bản) và `TienLuongSuyTim` (2 bản).
  • **LÁT CẮT KHÁC NHAU** của cùng chủ đề (COPD tổng quát · COPD ở đối tượng đặc biệt · COPD kèm
    tim mạch) là **BỔ SUNG, KHÔNG thay nhau** — phải đọc CẢ NHÓM.
  ⚠️ Bản đầu của công cụ này gộp hai thứ đó làm một và dán nhãn "đã có bản mới hơn" lên
  `COPD_20260610` chỉ vì có bản đối tượng đặc biệt ra sau ⇒ sẽ khiến bác sĩ **bỏ qua đúng bản
  mình cần**. Đã sửa: nhóm theo tên đầy đủ (lát cắt), không cắt hậu tố.
  **15 mục hai bản NÓI NGƯỢC NHAU về cùng một PMID** (COPD 4 · ĐauĐầu 5 · RA 5 · ViêmGanB 1),
  gồm những chỗ đáng lo: PMID 27783918 `consider`→`notyet` (oxy dài hạn), PMID 35081280
  `consider`→`apply` (cảnh báo JAK inhibitor). **5 mục ĐauĐầu là hệ quả TRỰC TIẾP của đợt sửa
  12/08**: thêm `normativeBasis` cho bản 18/07 mà không áp cùng cách cho bản 11/08 ⇒ ICHD-3 nay
  `apply` ở bản này và `consider` ở bản kia. **Bài học: sửa một dashboard KHÔNG tự lan sang bản
  khác cùng chủ đề — sửa xong phải chạy công cụ này.**
  Công cụ chỉ ĐO và BÁO; **KHÔNG tự nâng `decision`** (nâng làm khuyến cáo MẠNH hơn — nguy hiểm
  hơn hạ, thuộc thẩm quyền bác sĩ).

  ## 🧭 MẶC ĐỊNH MỚI 15–16/08/2026 — «nêu vấn đề là tự chạy» (đọc trước khi hỏi «còn gì để làm»)
  Toàn cảnh một trang: `EBM-Dashboards/derivatives/BAN-GIAO-KIEN-TRUC_2026-08-16.md`.
  - **«Hệ còn gì để hoàn thiện?» = `python3 tools/tu_de_xuat_viec.py`** — bảng 8 giác quan
    (sổ xác minh · gradeBy · mâu thuẫn · độ tươi · RAG · C1a · ⑦b CI HAI repo · ⑦c git 2 repo ·
    ⑦d lịch-nền đọc ĐẦU RA thật · ⑦e quyết-định-đã-duyệt · ⑧ bản đặt-cạnh). Mỗi dòng có số đo;
    👤 = thẩm quyền bác sĩ; «không còn gì» là kết quả hợp lệ. Tự chạy mở đầu gói tuần.
  - **Quyết định lâm sàng đã duyệt được CANH vĩnh viễn:** sổ máy-đọc
    `EBM-Dashboards/quyet-dinh-da-duyet.json` (CHỈ bác sĩ thêm/sửa) + `tools/kiem_quyet_dinh_da_duyet.py`
    — dashboard sinh lại lật ngược quyết định 13–14/08 sẽ bị BH58 (tự chạy mỗi phiên) bắt.
  - **Đặt-cạnh chứng cứ:** `tools/dat_canh_chung_cu_moi.py` (2 tuần/lần trong gói tuần) — mục
    `apply` có tổng quan/guideline MỚI HƠN được đặt cạnh kết luận nguyên văn abstract, ĐÃ tra rút
    bài, KHÔNG phán chiều (đã đo: cosine title không phân tách lạc/đúng — không lọc máy).
  - **Lịch nền = 2 tác vụ Claude** (`thu-thap-tuan-an-toan-thuoc` T7 06:30 · `cap-nhat-thang-ebm`
    mùng 1 18:30; launchd đã nghỉ hưu — chưa từng nổ thật). ⚠️ Kỳ đầu 16/08 ĐÃ LỠ (máy không thức);
    lưới đỡ: `tu_khoi_dong` khi mở phiên + giác quan ⑦d. Muốn nổ đúng hẹn: máy thức giờ đó hoặc
    bác sĩ đổi giờ/bấm «Run now».
  - **CI: HAI repo × 2 lane (ubuntu+windows), cả hai xanh.** Repo gốc lần đầu có CI
    (`.github/workflows/kiem-tinh-da-nen.yml`: compileall + chốt đa nền R1–R6 + smoke bảng);
    repo y khoa thêm bước `tools/kiem_newline_vung_ky.py` (miễn trừ `# da-nen: bo-qua` kèm lý do).
  - **Ed25519 «ed1»** đã sẵn trong lõi ký (`gate_contract.py`): khoá công trong repo ⇒ verify
    không cần bí mật; phát khoá từng vai bằng nút «Phat Khoa Ed25519» — CHỈ bác sĩ tự tay.
  - Bộ chốt bài học nay **BH01–BH58** (mutation-tested), tự chạy mỗi phiên. Sau khi thêm/sửa BH
    phải chạy TRỌN BỘ `chot_hoi_quy_bai_hoc.py` (17/08: BH10 từng bắt nhầm fixture BH58 — miễn
    trừ theo TỪNG match bằng marker `bh10-mien:` kèm lý do, không miễn cả file).

  ## 🔴 CƠ CHẾ ĐẢM BẢO CHỨNG CỨ MỚI & TIN CẬY (dựng 2026-08-12)
  **Một lệnh duy nhất trả lời "chứng cứ của tôi có mới và đáng tin không":**
  `python3 tools/chu_trinh_chung_cu.py` (thêm `--nhanh` để chỉ đọc sổ, không gọi mạng).
  Chạy 5 chốt theo đúng thứ tự phụ thuộc và **dừng ngay ở bước ① nếu nền tảng không đáng tin**:
  ① nguồn có THẬT không → ② độ tươi → ③ xác minh từng nguồn → ④ rút bài → ⑤ hai bản có nói ngược nhau không → ⑥ dây chuyền còn nguyên.
  Bước ① chặn cứng vì mọi bước sau VÔ NGHĨA khi nguồn là giả: xác minh dữ liệu giả vẫn "thành
  công" và cho ra độ phủ đẹp nhưng rỗng. Chu trình chỉ ĐO và BÁO — không tự quét chứng cứ mới,
  không tự nạp sổ cái, không tự áp dụng (Cổng A/B giữ nguyên).

  🔴 **PHÁT HIỆN NGHIÊM TRỌNG NHẤT 12/08 — máy Windows chạy DỮ LIỆU GIẢ suốt từ đầu.**
  `medical-ebm-automation/.env` trên Mac là **symlink** trỏ ra `~/.ebm-secrets/`. OneDrive đồng bộ
  symlink Unix sang Windows thành **file text 57 byte chứa đường dẫn macOS** ⇒ Windows không đọc
  được biến nào ⇒ `USE_MOCK_SOURCES` rơi về **mặc định True** ⇒ mọi lời gọi nguồn y văn trả **dữ
  liệu bịa**, và `NCBI_EMAIL` rỗng ⇒ **không tra cứu RÚT BÀI thật được**. Cảnh báo duy nhất là một
  dòng `logger.info`. Nghĩa là có thể chạy giám sát an toàn thuốc trên máy này và nhận một báo cáo
  trông bình thường nhưng toàn bộ là bịa.
  **Đã vá tận gốc:** `app/config.py` nay đọc thẳng `~/.ebm-secrets/medical-ebm-automation.env`
  TRƯỚC `.env` trong repo ⇒ **không cần symlink đi qua OneDrive nữa**, dùng chung một đường dẫn
  trên cả hai máy. Thứ tự ưu tiên: biến môi trường OS → kho secrets → `.env` repo.
  **Chốt canh:** `python3 tools/kiem_nguon_that.py` (`--nhanh` bỏ phần đo mạng, 0,2s — đã nối vào
  hook `SessionStart`, im khi ổn). Phân tầng rủi ro có chủ ý: **🔴 chỉ dành cho cấu hình** (mock
  bật / thiếu NCBI_EMAIL = dữ liệu SAI), **🟡 cho mạng** (chỉ là chưa lấy được, không làm dữ liệu
  sai) — gộp hai thứ này sẽ khiến bác sĩ quen bỏ qua màu đỏ vì mạng bệnh viện hay chập chờn.

  **SỔ XÁC MINH NGUỒN — `python3 tools/so_xac_minh_nguon.py --quet <dashboard> --vong 3`.**
  Vì sao cần: đo thật trên Windows, chạy `--online` bốn lần trên CÙNG một file cho **13 → 3 → 6 → 1
  lỗi cứng** (DNS chập chờn). Cổng không nhớ gì giữa các lần nên mạng kém thì **không lượt nào đủ**.
  Sổ tích luỹ bằng chứng theo TỪNG mục, nên chạy nhiều vòng sẽ dần đủ.
  ⚠️ **KHÁC HẲN "chạy lại lấy lần ít lỗi nhất"** (thứ mà `verify_dashboard.py` cảnh báo chống lại):
  ở đó người ta suy chất lượng CẢ GÓI từ một lượt may mắn; ở đây mỗi PMID/DOI có bằng chứng riêng
  kèm thời điểm. **Chỉ ghi THÀNH CÔNG — thất bại không bao giờ thành "đã xác minh".**
  **Hai mức hạn dùng, KHÔNG được gộp:** tồn tại+metadata **180 ngày** (gần như bất biến) · trạng
  thái **rút bài 30 ngày** (một bài đang tốt hôm nay có thể bị rút ngày mai).

  🔴 **BA BÁO ĐỘNG GIẢ đã vá cùng ngày — cùng một lớp lỗi: "không biết" bị báo thành "có vấn đề".**
  (a) Sổ ban đầu coi mọi status khác `ok` là ĐÃ BỊ RÚT ⇒ 18 PMID lành bị gắn cờ rút bài chỉ vì máy
  thiếu `NCBI_EMAIL` (status thật là `unknown_mock_or_no_email` = KHÔNG BIẾT).
  (b) `check_retraction_status()` trả `unresolved` khi **parse XML lỗi** — mà `unresolved` theo
  docstring nghĩa là "PubMed không có bản ghi" tức **nghi trích dẫn ma** ⇒ 18 PMID vừa được chính
  PubMed xác minh có thật bị báo là trích dẫn ma. Đã tách status mới `unknown_fetch_error`.
  (c) NCBI trả trang HTML **"WWW Error Blocked Diagnostic"** (chặn IP dùng chung, hay gặp ở mạng
  bệnh viện khi không có API key) rơi vào nhánh "parse XML lỗi" mơ hồ — nay nhận diện đích danh và
  chỉ ra cách sửa. Test: `pytest tests/test_check_citation_retraction.py` (27 test).
  **Bài học chung: báo động giả còn tệ hơn không kiểm, vì nó làm mất niềm tin vào cảnh báo thật.**
  Mỗi khi công cụ báo bất thường HÀNG LOẠT, kiểm chứng chéo trước khi tin.

  ✅ **HẾT PHỤ THUỘC NCBI API KEY (14/08/2026) — kiểm rút bài nay đi qua CHUỖI 3 TẦNG.**
  Ghi chú cũ ở đây nói "NCBI chặn ⇒ chưa tra cứu rút bài thật được, phải có API key" — **nay
  KHÔNG còn đúng**. Vấn đề thật chưa bao giờ là thiếu khoá mà là **ĐƠN NGUỒN**: chỉ có đúng một
  đường ra NCBI, nên một nhà cung cấp chặn là mất hẳn năng lực. `app/sources/retraction_chain.py`:
  **① Retraction Watch (Crossref, CC0) — NGOẠI TUYẾN**, tải một lần bằng
  `python3 medical-ebm-automation/tools/tai_retraction_watch.py` (63 MB, 71.778 dòng → **30.851
  PMID có phán quyết**), không khoá, không hạn mức, không IP nào chặn được; làm mới 30 ngày/lần
  (cache đã gitignore — là dữ liệu sinh lại được, không phải mã nguồn) ·
  **② NCBI E-utilities** giữ nguyên, dùng khi chạy được · **③ Europe PMC** không cần khoá, soi
  lại chính chỉ mục MEDLINE. `so_xac_minh_nguon.py` và `check_citation_retraction.py` đều đã
  chuyển sang chuỗi này. Đo thật bằng 2 PMID biết trước đáp án: NCBI chặn hoàn toàn → Europe PMC
  vẫn trả đúng cả hai; mất mạng hoàn toàn → nền ngoại tuyến vẫn bắt được bài đã rút. Muốn tự đo
  lại: `python3 tools/do_nguon_rut_bai.py`.
  **LUẬT GỘP bất đối xứng, đừng đảo:** tín hiệu **DƯƠNG** (đã rút/EoC) từ **bất kỳ** nguồn nào là
  nhận; tín hiệu **ÂM** ("ok") **chỉ** nguồn đã THỰC SỰ lấy được bản ghi mới được phát — Retraction
  Watch **vĩnh viễn không được nói "ok"** vì vắng mặt trong danh mục là *danh mục im lặng*, không
  phải *bài còn nguyên vẹn*. Không nguồn nào kết luận được ⇒ giữ KHÔNG BIẾT (fail-closed).

  🔴 **VÁ FAIL-OPEN TRONG CỔNG A12 cùng ngày — đã tái hiện được, không phải suy đoán.** Trạng thái
  `unknown_fetch_error` ra đời 12/08 để tách "KHÔNG BIẾT" khỏi "nghi trích dẫn ma", nhưng tập tiêu
  thụ `_PROBLEM_STATUSES` **không được cập nhật theo** ⇒ khi NCBI chặn (đúng tình trạng máy này),
  MỌI PMID nhận `unknown_fetch_error`, không cái nào bị tính là vấn đề, **`all_clean=true` được ghi
  VÀ KÝ vào `A12_RETRACTION_RECEIPT.json`**, CLI in "✅ Không phát hiện rút bài" và thoát 0 —
  `run_g10_assemble.py` (dòng ~1895) chỉ chặn khi `all_clean is not True`, nên **gói nộp đi qua cổng
  A12 trong khi KHÔNG một trích dẫn nào được kiểm**. Cùng lớp lỗi với `return` sớm ngày 12/08: cổng
  báo "đạt" vì chưa hề chạy tới luật cần chạy. Khoá bằng **BH27**, đã kiểm bằng 2 phép đột biến.

  🔴 **PHÁT HIỆN LÂM SÀNG NGAY LẦN CHẠY ĐẦU — và nó chứng minh vì sao phải đa nguồn.** Quét 57
  dashboard (562 PMID) với nền ngoại tuyến: `WebDashboard_EBM_VanDeCuThe_ViemGanB_DieuTri_20260716`
  **ITEM-05** ("TDF liên quan nguy cơ HCC thấp hơn Entecavir") trích **PMID 30267080** (Choi và cs.,
  JAMA Oncology) — Retraction Watch ghi **Retraction 25/04/2019, lý do "Error in Data; Retract and
  Replace"**, thông báo PMID 31021386 / doi:10.1001/jamaoncol.2019.0576. **CẢ PubMed LẪN Europe PMC
  đều trả `ok` cho PMID này** ⇒ thiết kế đơn nguồn cũ **sẽ không bao giờ bắt được, kể cả khi đã có
  NCBI API key**. ⚠️ Đọc đúng mức: đây là **"rút và thay"**, tức bài đã được SỬA rồi đăng lại —
  KHÁC bài bị rút bỏ hẳn, nên **không được xử lý như nhau**; việc cần làm là đối chiếu số liệu
  ITEM-05 với **bản đã thay**, không phải xoá mục. Chưa sửa — chờ bác sĩ (đổi `decision` là thẩm
  quyền bác sĩ).
  ✅ **CẬP NHẬT 14/08 — mục này KHÔNG còn chỉ nằm trong sổ.** Từ nay `verify_dashboard.py`
  **CHẶN CỨNG** gói có nguồn đã rút, và bản đọc in dải cảnh báo đỏ ngay dưới đầu trang. Hệ quả
  có chủ ý: `audit_ebm_system.py` nay **FAIL** chừng nào ITEM-05 chưa được xử lý — hệ không tự
  tuyên bố sạch khi còn một trích dẫn đã bị rút. Xem mục 🔎 ngay dưới.

  ## 🔎 BA LỖI "CON SỐ KHÔNG ĐO THỨ NÓ TỰ NHẬN" (vòng lặp kiểm tra–hoàn thiện, 14/08/2026)
  Cả ba đều lọt qua mọi chốt trước đó vì **công cụ vẫn chạy và vẫn in ra kết quả trông hợp lệ**.
  Đây là họ lỗi nguy hiểm nhất của hệ này, và nó đã tái diễn đủ nhiều lần để thành luật nền.

  | Mã | Lỗi | Vì sao vô hình | Hại theo hướng |
  |---|---|---|---|
  | **BH30** | `dang_ky_chu_de.tach_ten()` trả **tên chủ đề** ở đúng vị trí **NGÀY** (lệch một bậc sau bản vá "chủ đề là tuỳ chọn"). Bộ dò mâu thuẫn khoá cache theo giá trị đó ⇒ 3 bản `SuyTim_TongHop` sập vào MỘT khoá; cặp 04/08⟷05/08 hoá thành so bản 11/08 với **chính nó** ⇒ vĩnh viễn 0 mâu thuẫn | tổng số mâu thuẫn **không đổi** (11) vì kho tình cờ không có mâu thuẫn giữa các bản SuyTim ⇒ nhìn số là hoàn toàn không thấy | **bỏ sót** |
  | **BH31** | Cổng liêm chính **chưa bao giờ kiểm rút bài**; kết luận dương tính đã nằm sẵn trong sổ mà không nơi nào đọc | gói đúng ở mọi luật khác nên trông như đã soi đủ | **bỏ sót** |
  | **BH32** | `kiem_do_tuoi_chung_cu` lấy `max(ngày)` toàn kho rồi in *"🟢 CHỨNG CỨ còn hạn"* — nghĩa thật chỉ là *"có ít nhất MỘT gói mới"* | 🟢 là màu người ta không kiểm lại | **yên tâm giả** |

  **Số đo:** BH32 — gói mới nhất **1 ngày** tuổi ⇒ in 🟢, trong khi **37/59 chủ đề đã quá 35
  ngày**, trung vị **45**. Nay in kèm trung vị + 5 chủ đề lâu nhất; ngưỡng báo động để **riêng ở
  120 ngày**, cố ý cao hơn nhiều — ở nhịp làm việc thật phần lớn chủ đề luôn quá 35 ngày, lấy 35
  làm ngưỡng đỏ sẽ khiến mỗi phiên đều đỏ và bác sĩ học cách bỏ qua; lúc đó cảnh báo THẬT chìm theo.
  **Khoá gom nhóm** (BH30) từ nay phải là **đường dẫn**, không phải ngày: hai lát cắt khác nhau
  của cùng chủ đề có thể trùng ngày (`RA_Than` và `RA_TimMach` đều 30/06/2026).

  > **LUẬT NỀN, áp cho mọi lần đọc kết quả công cụ:** hỏi **"nó đã chạy tới luật nào"** và
  > **"con số này là của TẬP HỢP hay của MỘT phần tử"**, chứ không chỉ đếm số lỗi. Một chỉ số
  > gộp (`max` · `min` · "mới nhất") **không bao giờ** được trình bày như kết luận về toàn bộ.

  🔴 **BH33 — ĐIỂM MÙ THỨ TƯ, và nó bị chạm vào NGAY trong ngày.** Chuỗi 3 tầng chỉ nhận
  **PMID**, nên `con_hieu_luc()` xếp **540 DOI** (gần một nửa số định danh trong kho) vào nhóm
  "còn hiệu lực" dù chúng **CHƯA TỪNG được kiểm rút bài lần nào** — một lời bảo đảm rỗng.
  **Chuyện đã xảy ra:** mục `ViemGanB_DieuTri` ITEM-05 trích PMID 30267080 (đã rút) được sửa
  thành trích DOI `10.1001/jamaoncol.2018.4070`. Tra PubMed + Crossref: **hai định danh đó là
  CÙNG MỘT BÀI** (PMID 30267080 ⇄ DOI 10.1001/jamaoncol.2018.4070), và Crossref ghi rõ
  `updated-by: retraction → 10.1001/jamaoncol.2019.0576`. Nội dung không đổi; chỉ có **cảnh báo
  tắt đi**. Một đèn đỏ tắt mà nguy cơ còn nguyên nguy hiểm hơn hẳn chưa từng có đèn.
  **Đã vá:** tầng `medical-ebm-automation/app/sources/crossref_retraction.py` (Crossref
  `updated-by`, không cần khoá) + `so_xac_minh_nguon.kiem_rut_bai_theo_doi()`; `con_hieu_luc()`
  nay đòi dấu vết kiểm rút bài cho **DOI, kể cả DOI ghi dạng URL** (cùng lý lẽ BH24), nhưng
  **KHÔNG** đòi với URL thuần (nice.org.uk/…) — tránh báo động giả.
  `correction`/`corrigendum`/`erratum` **cố ý không** tính là rút bài: đính chính là chuyện bình
  thường của xuất bản, gộp vào sẽ tạo báo động giả hàng loạt.
  > **Luật:** *một định danh mang bảo đảm nào thì phải chịu đúng phép kiểm của bảo đảm đó, bất
  > kể nó được ghi bằng kiểu gì.* Đổi kiểu ghi không bao giờ được là đường thoát cổng.

  ⚠️ **Bài học vận hành đi kèm:** cách sửa ĐÚNG cho *retract-and-replace* là **đối chiếu số liệu
  với bản đã thay** rồi trích đúng bản đó — KHÔNG phải đổi sang một định danh khác của **chính
  bài đã rút**, và cũng không phải xoá mục. Bản thay thế của ca này là **PMID 31021386 /
  doi:10.1001/jamaoncol.2019.0576** (Notice of Retraction and Replacement).

  **Cảnh báo nay nằm ở NƠI BÁC SĨ ĐỌC, không chỉ trong terminal.** Bản đọc
  (`derivatives/<mã>_ban-doc.html`) mang 2 dải ngay dưới đầu trang: **đỏ "Nguồn đã bị rút"** và
  **cam "Bản khác cùng chủ đề đang kết luận ngược"**. Cả hai chỉ ĐẶT CẠNH NHAU hai kết luận —
  **không đổi `decision`** (BH10), **không đoán bên nào đúng** (BH28); không tính được thì in rõ
  *"chưa kiểm"*, tuyệt đối không im lặng.
  **Độ phủ xác minh nguồn: 51% → 99%** (1154/1155, 0 mục chưa kiểm) — NCBI đã trả lời được trở
  lại nên chạy thêm vòng `so_xac_minh_nguon.py` lấp gần hết; câu "cần NCBI_API_KEY" trong các ghi
  chú cũ chỉ đúng cho lúc NCBI đang chặn, **không phải điều kiện thường trực**.

  ## ✍️ QUYẾT ĐỊNH LÂM SÀNG BÁC SĨ DUYỆT 14/08/2026 — 4 câu, 11 mâu thuẫn → còn 5
  11 mục "hai bản nói ngược nhau" quy về **4 quyết định**; bác sĩ chọn, tôi ghi.
  **(a) COPD, theo bản mới 05/08** — `COPD_20260610`: PMID 27783918 (oxy dài hạn)
  `consider→notyet`; PMID 32162970 (bộ ba giảm tử vong) `consider→apply`.
  **(b) RA, thống nhất `apply` cho cảnh báo an toàn** — PMID 35081280 (ORAL Surveillance)
  ở `RA_EULAR2024` và `RA_TimMachChuyenHoaNoiTiet`; PMID 27697765 ở `RA_Than`.
  **(c) IMPACT (PMID 29668352) — KHÔNG phải mâu thuẫn:** hai lát cắt trích HAI KẾT CỤC
  khác nhau của cùng thử nghiệm (đợt cấp/nhập viện vs biến cố tim-phổi phối hợp). Khai ở
  `EBM-Dashboards/mau-thuan-da-duyet.json`; `dang_ky_chu_de.py` tách khỏi danh sách đỏ
  nhưng **vẫn liệt kê** kèm lý do + ngày duyệt — giấu hẳn thì không ai rà lại được, và
  nếu một bản đổi nội dung thì miễn trừ cũ có thể hết đúng.
  **(d) Sàng lọc lao tiềm ẩn/HBV trước b/tsDMARD** (`VKDT_TongHop` ITEM-13,
  `ViemKhopDangThap` ITEM-08): khai `normativeBasis:'drug-label'` dựa trên **Boxed
  Warning của FDA tra sống qua openFDA** — etanercept/infliximab: *"Perform test for
  latent TB; if positive, start treatment for TB prior to starting"*. EULAR 2025
  (PMID 41826212) **không** nêu tường minh việc này trong tóm tắt nên không dùng làm căn
  cứ. Giữ nguyên `decision:'apply'` và `gradeLevel:'na'` (FDA không dùng thang GRADE).

  🔴 **5 mục CÒN LẠI KHÔNG ghi được — vướng đúng luật chống tự gán mức, không được lách:**
  3 mục CKD (`BenhThanMan_BenhKem_DoiTuongDacBiet`: DAPA-CKD 32970396 · FIDELIO-DKD
  33264825 · EMPA-KIDNEY 36331190) và 2 mục RA (`RA_TimMachChuyenHoaNoiTiet` ITEM-01,
  PMID 27697765) đang có `gradeLevel:'na'`. Nâng lên `apply` cần một phân hạng THẬT.
  ⚠️ Đáng chú ý: bản `BenhThanMan_CKD` 07/06 đang để `apply` với `gradeLevel:'high'` mà lý
  do ghi là *"RCT đa trung tâm, mù đôi (chất lượng cao)"* — đó là **tự chấm của người
  soạn**, đúng thứ đã khiến `COPD_TimThanChuyenHoa ITEM-26` bị hạ ngày 13/08. Muốn cả hai
  bản cùng `apply` một cách trung thực thì phải **neo vào phân hạng của một tổ chức có
  chấm** (KDIGO cho CKD, EULAR LoE/SoR cho RA) và ghi mức nguyên bản của tổ chức đó —
  không phải chép mức tự chấm sang bản còn lại.

  ## 🎯 NĂM TRỤ "CHỨNG CỨ TỐT NHẤT · MỚI NHẤT · TIN CẬY NHẤT" (dựng 14/08/2026)
  Hệ vốn mạnh ở câu hỏi *"trích dẫn có THẬT không"*. Năm việc dưới đây nhắm câu hỏi khác:
  *"trích dẫn có ĐÚNG LÀ chứng cứ tốt nhất hiện có không"*.

  **① `gradeBy` — AI ĐÃ CHẤM MỨC NÀY?** `gradeLevel` là thứ bác sĩ **hành động theo**, nên
  một mức không truy được nguồn gây hại ở MỌI lần đọc (khác rút bài vốn hiếm). Đo: **530
  item có `gradeLevel` khác `na`, 249 (47%) không truy được**; 128 lấy MÔ TẢ THIẾT KẾ làm
  lý do ("RCT đa trung tâm, mù đôi" ⇒ `high`); **56 mục tự khai "nguồn không cung cấp phân
  hạng" mà VẪN mang mức** — vi phạm chính `DESIGN-SPEC §6`. **56 mục đó đã đưa về `na`**
  (chỉ hạ, không nâng; không đụng `decision`). Trường mới `gradeBy` + luật cổng ở mức
  **CẢNH BÁO**; công cụ xử lý dần: `python3 tools/kiem_phan_hang.py`. **BH36**.
  ⚠️ *Cố ý KHÔNG chặn cứng:* "chưa khai `gradeBy`" ≠ "mức sai" — nhiều mục đã nêu hệ chấm
  ngay trong `gradeSource` (vd "khuyến cáo COR I của AHA/ASA"), chỉ chưa tách trường. Chặn
  256 mục là biến CHƯA BIẾT thành CÓ VẤN ĐỀ (BH08), và bức tường đỏ sẽ bị vô hiệu hoá.
  Chuyển thành lỗi cứng khi `kiem_phan_hang.py` về 0.

  **② CHỨNG CỨ ĐÃ BỊ VƯỢT QUA** — `python3 tools/kiem_chung_cu_vuot_qua.py`. Mảnh thiếu lớn
  nhất của chữ *"mới nhất"*: `kiem_do_tuoi_chung_cu.py` chỉ đo tuổi GÓI, không đo tuổi
  CHỨNG CỨ bên trong. Với mỗi PMID đang `apply`, hỏi PubMed (`elink pubmed_pubmed_reviews`)
  các tổng quan/gộp/guideline MỚI HƠN. Lần chạy đầu: **125/172 mục có chứng cứ tổng hợp mới
  hơn**, bắt được **KDIGO 2026** (PMID 41485807) và **guideline đột quỵ 2026** (41582814).
  Báo cáo: `EBM-Dashboards/derivatives/CHUNG-CU-VUOT-QUA_*.txt`.
  ⚠️ Đây là *danh sách đáng đọc*, KHÔNG phải "chứng cứ của anh đã sai": bài mới có thể
  CỦNG CỐ kết luận đang dùng. Máy không đọc nội dung và không phán chiều (BH28).

  **③ TÌM KIẾM THEO TẦNG** — watchlist nay có `queries` 3 tầng: guideline/đồng thuận →
  tổng quan/gộp → RCT lớn; `surveillance_scan.py` chạy đúng thứ tự đó và gắn nhãn `tang`
  cho từng ứng viên, nên thứ mạnh nhất hiện trước thay vì thứ PubMed trả trước. Nhóm cảnh
  báo cơ quan quản lý **cố ý không** áp thứ bậc (lọc theo publication type sẽ giết sạch kết
  quả đúng). Tương thích ngược: thiếu `queries` thì lùi về `query` cũ.

  **④ KIỂM CON SỐ, KHÔNG CHỈ KIỂM PMID** — `python3 tools/kiem_so_lieu.py`. Trước nay hệ
  xác minh "PMID có thật + tiêu đề khớp", chưa bao giờ xác minh **hiệu số**. Đối chiếu
  `effect{hr,lo,hi}` với tóm tắt; đọc được cả `0.72` · `0·72` (Lancet) · `0,72`.
  **Ba mức, cố ý KHÔNG có mức "SAI"**: ✓ khớp · 🟠 một phần · ⚪ tóm tắt không nêu. Vắng mặt
  trong tóm tắt KHÔNG phải bằng chứng trích sai (nhiều bài chỉ để số ở toàn văn/bảng) — nói
  "sai" từ việc vắng mặt chính là biến *không biết* thành *có vấn đề*. Thử 25 mục `apply`:
  **24 khớp đủ**.

  **⑤ `provenanceUnknown` — TÁCH "CHƯA KHAI" KHỎI "CÓ VẤN ĐỀ"** — 44/62 gói chưa từng ghi
  nhận chiến lược tìm kiếm, rải đều 06→08/2026 (**không có mốc ngày nào để suy**, nên phải
  là khai báo tường minh). Trước đây chúng sinh 10 lỗi cứng GIỐNG HỆT gói lẽ ra phải có mà
  cố tình bỏ. Nay gói khai `provenanceUnknown: true` + `provenanceUnknownLyDo` → **một cảnh
  báo** nói rõ gói không tái lập/kiểm toán được. Khai mà không nêu lý do ⇒ lỗi cứng (miễn
  trừ phải có người chịu trách nhiệm). Miễn trừ **CHỈ** bỏ phần hợp đồng nguồn — **mọi luật
  an toàn cấp item vẫn chạy**, nếu không nó thành đường lách rộng hơn cả lỗi `return` sớm
  ngày 12/08 vốn đã che 73 mục nguy hiểm. **BH35** khoá đúng điều này.
  ⚠️ Khai `provenanceUnknown` là nói ra một sự thật kiểm chứng được (file không có khối
  standards) — **KHÁC HẲN** việc bịa chiến lược tìm kiếm, thứ vẫn tuyệt đối cấm.

  **KẾT QUẢ CỔNG: 15/62 → 51/62 gói PASS.** 11 gói còn lại đều vì **26 mục `apply` trên
  chứng cứ mà nguồn chưa từng phân hạng** — chờ bác sĩ quyết: hạ `decision`, hoặc neo vào
  một tổ chức có chấm (KDIGO/EULAR/Cochrane…) rồi ghi mức nguyên bản của tổ chức đó.

  ## 📥 CỔNG NHẬN CHỨNG CỨ — "mới nhất" và "tin cậy nhất" đi CÙNG NHAU (dựng 14/08/2026)
  Mọi thứ trước đây soi **kho đã có**. Mục này nâng đúng chỗ chứng cứ **đi vào hệ**.

  **Trạng thái cũ, đo được trong `surveillance_scan.py`: 0 lần kiểm rút bài · 0 lần đọc loại
  thiết kế · 0 lần đối chiếu kho.** Ứng viên tới tay bác sĩ chỉ mang tiêu đề · tạp chí · ngày ·
  một nhãn `authority` **suy từ TÊN TẠP CHÍ** — thứ trông như bảo đảm chất lượng nhưng không
  phải. Nghĩa là một bài **đã bị rút** vẫn có thể vào thẳng hàng ứng viên.

  **Nay mỗi ứng viên mang sẵn 4 dữ kiện trước khi tới mắt bác sĩ** (`gan_do_tin_cay()`):
  `rut_bai` (chuỗi 3 tầng) · `pubtype` (loại thiết kế THẬT từ PubMed, không đoán theo tạp chí)
  · `da_co_trong_kho` (đọc sổ xác minh, khỏi trình lại thứ đã đọc) · `chua_binh_duyet` (preprint).
  Nhãn **in ra trong báo cáo** — nằm trong JSON mà không hiện thì với người đọc nó không tồn tại.
  Bất đối xứng giữ nguyên: không kiểm được ⇒ `chua_kiem`, **tuyệt đối không mặc định `ok`**.

  **4 NGUỒN THẨM QUYỀN nay được gọi TÊN** — Cochrane · NICE · USPSTF · WHO. Trước đó watchlist
  **không nhắc tên nguồn nào trong nhóm này**, nên guideline/tổng quan mới nhất của họ có thể ra
  đời mà hệ không thấy. (Ghi chú: `CHANGELOG v1.15.0` khai đã thêm nhóm này ngày 13/08 nhưng bản
  sống KHÔNG có — thay đổi đó hoặc chưa từng áp, hoặc đã bị ghi đè.) Cả 4 tra qua chính PubMed,
  không cần API mới; **cố ý không áp bộ lọc 3 tầng** vì chúng đã là tầng cao nhất.

  **Đo sau khi nối (43 chủ đề · 45 ngày):** PASS · 87 ứng viên · 0 lỗi ·
  **87/87 đã kiểm rút bài** (trước: 0) · **87/87 có loại thiết kế thật** (trước: 0) ·
  41 tổng quan hệ thống · 24 practice guideline · 12 phân tích gộp · 26 RCT ·
  1 mục đã có trong kho (lọc khỏi danh sách). **BH37** khoá hành vi này.

  🔴 **LỖI "MỚI NHẤT" LỚN NHẤT — bộ lọc loại thiết kế đang vứt đi CHÍNH thứ mới nhất.**
  `search()` luôn AND thêm `[ptyp]`. Nhưng **publication type do MEDLINE gán TRONG LÚC lập chỉ
  mục**, việc xảy ra hàng tuần đến hàng tháng SAU khi bài vào PubMed. Lọc theo nó nghĩa là chỉ
  thấy thứ đã đánh chỉ mục xong — tức thứ **không còn mới**.
  **Số đo:** 40 bài mới vào PubMed 45 ngày (suy tim) → **30 bài chưa gán loại nào ngoài
  "Journal Article"**, trong đó có PMID 42552200 *"…heart failure: a systematic review"* — một
  tổng quan hệ thống bị vứt chỉ vì chưa kịp đánh chỉ mục. Đếm theo chủ đề (`edat`, 45 ngày):
  CÓ lọc **1 · 8 · 0** — KHÔNG lọc **46 · 49 · 22**. CKD trả **0** trong khi thực có 22 bản
  ghi mới, và "0 ứng viên" bị đọc thành "không có gì mới" — biến KHÔNG BIẾT thành SỰ THẬT.
  **Đã sửa:** tầng thứ tư `moi_vao_pubmed` đi bằng **`edat`** (ngày vào PubMed — đúng câu hỏi
  *"có gì mới so với lần quét trước"*, khác `pdat` là ngày bìa) và **không lọc** publication
  type. Ba tầng cũ giữ nguyên. Loại thiết kế nay dùng để **GẮN NHÃN và XẾP HẠNG, không dùng để
  loại bỏ**; bài chưa gán loại ghi rõ *"⚡ mới vào PubMed — chưa gán loại thiết kế"* (dấu hiệu
  MỚI, không phải khiếm khuyết). **BH38** khoá điều này.
  **Trước/sau (43 chủ đề · 45 ngày): 87 → 165 ứng viên · chủ đề "0 ứng viên" 22 → 7.**
  15 chủ đề từng báo "không có chứng cứ mới" thực ra CÓ — RA · viêm gan B · hen phế quản ·
  đột quỵ dự phòng thứ phát · lão khoa · GDMT nội trú…

  ⚠️ **Chưa làm, có chủ ý:** preprint (medRxiv/bioRxiv) và ClinicalTrials.gov **chưa** nối vào
  routine dù đã có MCP. Lý do: thêm một dòng tài liệu **chưa bình duyệt** khi nhãn độ tin cậy
  vừa mới có sẽ làm hỏng chính mục tiêu — phải để nhãn chạy ổn định trước.

  🔧 **Vá kèm — lỗi của chính bộ chốt:** `_nap()` trong `chot_hoi_quy_bai_hoc.py` không đăng ký
  module vào `sys.modules` trước khi `exec_module`, nên **mọi module có `@dataclass` đều nạp
  hỏng** (`@dataclass` tra `sys.modules.get(cls.__module__).__dict__` lúc dựng lớp → nhận None).
  Chốt hỏng thì hiện thành "BÀI HỌC TÁI PHÁT" — báo động giả đúng vào thứ sinh ra để chống báo
  động giả. Đã vá.

  ## 🧩 TẦNG AGENT — doctrine đã TRÔI TỤT sau cổng (rà 14/08/2026)
  Cả phiên 14/08 nâng **tầng công cụ**. Rà tầng agent lộ ra một khoảng trống chưa ai đo:

  | Thứ cổng ĐANG bắt buộc | Doctrine agent nhắc |
  |---|---|
  | `normativeBasis` (cổng bắt từ **12/08**) | **0/84 agent** |
  | `gradeBy` (cổng bắt từ 14/08) | **0/84 agent** |
  | 8 công cụ chứng cứ lâm sàng (sổ xác minh · chuỗi rút bài · dò vượt qua · phân hạng · con số · đăng ký chủ đề · chu trình · phủ giám sát) | **0/84 agent** gọi tên |

  Trong khi **tuyến NGHIÊN CỨU đã nối dây đầy đủ** — `gen_research_docx.py` được nhắc 73 lượt,
  `approve_gate.py` 8, `gate_contract.py` 6. Tức tuyến nghiên cứu có công cụ, **tuyến chứng cứ
  lâm sàng chỉ có doctrine**.

  🔴 **Chỗ nguy hiểm nhất:** `tra-cuu-chung-cu` có dặn tự chất vấn *"bài có bị rút không?"* —
  nhưng **không đưa công cụ nào**. Tức bảo mô hình trả lời bằng TRÍ NHỚ về một sự kiện có thể
  xảy ra sau ngày cắt kiến thức. Ca thật PMID 30267080: **cả PubMed lẫn Europe PMC đều trả
  `ok`**, chỉ nền Retraction Watch ngoại tuyến bắt được là đã rút-và-thay.

  **Đã sửa:** `tra-cuu-chung-cu` nay ra LỆNH CHẠY `check_citation_retraction.py` (không tra
  được ⇒ ghi *"chưa kiểm rút bài"*, không được ghi *"chưa bị rút"*), và được dạy rằng **bài quá
  mới thường CHƯA có publication type** nên đừng loại nó. `tham-dinh-grade-nnt` nay có hợp đồng
  hai trường `gradeBy` + `normativeBasis`. Guardrail `tham-dinh-dau-ra` thêm **R4b/R4c**.

  > **LUẬT NỀN MỚI (BH39):** thêm một luật ở CỔNG thì phải DẠY AGENT cùng lúc. Cổng bắt buộc
  > một trường mà agent chưa từng nghe tên nghĩa là agent dựng gói đúng theo doctrine rồi bị
  > chặn — và người đọc tưởng nội dung sai, trong khi lỗi thật là hai tầng nói hai thứ khác nhau.
  > Chốt BH39 đối chiếu trực tiếp: mọi trường cổng đang bắt buộc phải có mặt trong doctrine.

  🔧 **VÌ SAO DOCTRINE TRÔI TỤT ĐƯỢC — nguyên nhân gốc, đã vá (BH40).**
  `enforce_agent_guardrails.py` cấy một khối chung vào cả 50 agent, nhưng `_refresh()` chỉ
  biết **đúng MỘT cặp thay thế viết cứng**. Muốn thêm một luật cho toàn đội thì phải sửa chính
  cơ chế — nên trên thực tế **không ai thêm**, và mỗi luật mới chỉ nằm ở cổng. Đó là lý do cấu
  trúc khiến BH39 xảy ra được, chứ không phải ai đó quên.
  Nay `THAY_THE` là **danh sách cặp**: thêm luật = thêm một dòng rồi chạy `--refresh`.
  **Luật đầu tiên lan bằng cơ chế mới — "RÚT BÀI phải TRA, không được tự nhớ": 0/50 → 50/50
  agent.** Kèm câu chữ cụ thể: không tra được ⇒ ghi *"chưa kiểm rút bài"*, TUYỆT ĐỐI không ghi
  *"chưa bị rút"*; và bài quá mới thường chưa có publication type nên đừng loại nó.
  Đáng chú ý trong nhóm vừa nhận luật: **`tong-quan-y-van`** (agent tổng quan hệ thống) trước
  đó có **0 lần** nhắc rút bài — trong khi PRISMA/Cochrane bắt buộc kiểm trạng thái rút bài của
  nghiên cứu đưa vào.

  **7 CÔNG CỤ CÒN LẠI NỐI THEO VAI, không cấy đại trà** (cấy sai chỗ chỉ tạo nhiễu, mà nhiễu
  dạy người ta bỏ qua). Marker `<!-- EBM-CONGCU-CHUNGCU-LAMSANG -->`:

  | Agent | Công cụ phải gọi | Vì sao |
  |---|---|---|
  | `tra-cuu-chung-cu` | `kiem_chung_cu_vuot_qua` | 125/172 mục `apply` có tổng quan MỚI HƠN |
  | `huong-dan-lam-sang` | `kiem_chung_cu_vuot_qua` · `dang_ky_chu_de` | sửa 1 dashboard KHÔNG tự lan sang bản khác cùng chủ đề |
  | `dieu-phoi-lam-sang` | `chu_trinh_chung_cu` · `dang_ky_chu_de` | chốt trước khi trả gói; chu trình DỪNG ở bước ① nếu nguồn không đáng tin |
  | `cap-nhat-guideline` | `kiem_phu_giam_sat` · `uu_tien_cap_nhat` | **"0 ứng viên" ≠ "không có chứng cứ mới"** |
  | `trich-xuat-y-van` | `kiem_so_lieu` | hệ chưa bao giờ xác minh CON SỐ, chỉ xác minh PMID |
  | `kiem-chung-trich-dan` | `so_xac_minh_nguon` | cổng không nhớ gì giữa các lần chạy; mạng kém thì không lượt nào đủ |
  | `tham-dinh-dau-ra` | `kiem_so_lieu` (**R1c** mới) | R1 cũ chỉ kiểm PMID, không kiểm hiệu số |

  🔎 **Chốt BH41 tự bắt được một mục tôi bỏ sót** ngay lần chạy đầu: `so_xac_minh_nguon` chưa
  agent nào gọi. Đó đúng là việc chốt sinh ra để làm — một công cụ không agent nào gọi thì với
  dây chuyền hằng ngày nó **không tồn tại**, dù chạy đúng và có test.

  ## 🌍 CHUẨN QUỐC TẾ CÒN THIẾU Ở TẦNG AGENT (rà 14/08/2026)
  Đo trên 84 file `.claude/agents/`. Năm chuẩn ở mức **0 agent** (hoặc chỉ nằm ở rubric nội bộ):

  🔴 **AGREE II — nghiêm trọng nhất.** Xuất hiện ở **đúng 1 file**, và đó là
  `_RUBRIC-EVALUATE-CUNG-QA-GATE.md` (rubric QA nội bộ), **không phải agent thẩm định**. Trong
  khi `cap-nhat-guideline` nhắc "guideline" **16 lần**, `huong-dan-lam-sang` **19**,
  `tra-cuu-chung-cu` **13** — không agent nào cầm công cụ đo chất lượng guideline.
  ⇒ **Hệ đang tin guideline theo TÊN TỔ CHỨC.** Và điều đó vừa nguy hiểm hơn: watchlist mới mở
  4 kênh gọi thẳng tên Cochrane · NICE · USPSTF · WHO, nên hệ sẽ hút về nhiều guideline hơn,
  tất cả đều "có thương hiệu".
  **Điểm mấu chốt:** một khuyến cáo của hiệp hội lớn nhưng **Miền 3 — Rigour of Development**
  yếu thì bản chất là **đồng thuận chuyên gia có logo**. Cổng đã có sẵn cách gọi tên thứ đó:
  `design:'Consensus'` — và Consensus **KHÔNG BAO GIỜ** đủ để miễn trừ quy phạm (BH03).
  *(Thực dụng: không chấm đủ 23 mục cho mọi guideline. Tối thiểu — nêu Miền 3 có được mô tả
  không; guideline không mô tả cách tìm/chọn chứng cứ thì ghi rõ điều đó cạnh khuyến cáo.)*

  | Chuẩn | Vai trò | Bài phương pháp GỐC (đã tra PubMed 14/08, không lấy từ trí nhớ) |
  |---|---|---|
  | **AGREE II** | thẩm định chất lượng guideline | PMID **20656455** · J Clin Epidemiol 2010 · doi:10.1016/j.jclinepi.2010.07.001 |
  | **AGREE-REX** | độ tin cậy LÂM SÀNG của khuyến cáo (AGREE II không chạm tới) | — |
  | **RIGHT** | chuẩn BÁO CÁO khi CHÍNH MÌNH đưa ra khuyến cáo | PMID **27893062** · Ann Intern Med 2017 · doi:10.7326/M16-1565 |
  | **PRISMA-S** | báo cáo CHIẾN LƯỢC TÌM (16 mục) | PMID **34285662** · J Med Libr Assoc 2021 · doi:10.5195/jmla.2021.962 |
  | **ROBIS** | sai lệch của CHÍNH tổng quan (khác AMSTAR-2 = chất lượng phương pháp) | PMID **26092286** · J Clin Epidemiol 2016 · doi:10.1016/j.jclinepi.2015.06.005 |
  | **GRADE-CERQual** | độ tin cậy phát hiện ĐỊNH TÍNH (GRADE chuẩn không áp được) | PMID **26506244** · PLoS Med 2015 · doi:10.1371/journal.pmed.1001895 |

  **RIGHT gắn thẳng vào việc hệ đang làm:** hệ **sản xuất khuyến cáo** (`decision:'apply'`), nên
  phải chịu chuẩn báo cáo dành cho khuyến cáo — ai soạn · COI · cách tìm chứng cứ · cách NỐI
  chứng cứ với khuyến cáo · **độ mạnh TÁCH khỏi chất lượng chứng cứ** · kế hoạch cập nhật.
  *Bối cảnh:* RIGHT **đang được cập nhật** (PMID 42348121 · 41559761, J Evid Based Med 2026) —
  trích RIGHT 2017 là bản hiện hành, KHÔNG khẳng định là bản cuối.

  **PRISMA-S gắn vào lỗ hổng provenance:** 44/62 gói chưa từng ghi chiến lược tìm. Không hồi tố
  được, nhưng **mọi gói MỚI phải khai đủ**: CSDL + giao diện + ngày · truy vấn NGUYÊN VĂN chạy
  lại được · giới hạn · nguồn ngoài CSDL · số bản ghi mỗi nguồn · ai thiết kế truy vấn.

  **BH42** khoá: mỗi chuẩn phải có agent CẦM, kèm PMID bài phương pháp GỐC, và AGREE II phải nằm
  ở agent TIÊU THỤ guideline chứ không chỉ ở rubric nội bộ. *(Cả 5 PMID đã chạy qua chuỗi kiểm
  rút bài — `ok` toàn bộ, đúng luật vừa áp cho 50 agent.)*

  ## 🐤 CANARY ĐẦU–CUỐI — chứng minh dây chuyền CHẠY đúng, không chỉ CÓ CHỮ (14/08/2026)
  `python3 tools/thu_dau_cuoi_chung_cu.py` · **2 giây, ngoại tuyến, dữ liệu hoàn toàn giả**.

  **Vì sao cần:** cả BH01–BH42 đều kiểm **chữ trong file** — luật có mặt chưa, doctrine nhắc
  chưa, ba bản khớp chưa. **Không chốt nào chứng minh dây chuyền THẬT SỰ BẮT ĐƯỢC lỗi khi
  chạy.** Khoảng cách đó không lý thuyết: riêng 14/08 tìm được **ba ca luật CÓ MẶT mà KHÔNG BAO
  GIỜ chạy tới** — `return` sớm khi thiếu `DATA.standards` (che 73 mục nguy hiểm trên 47
  dashboard) · bộ lọc `[ptyp]` ở khâu tìm (22 chủ đề báo "0 ứng viên" trong khi có chứng cứ
  mới) · 8 công cụ chứng cứ mà 0 agent gọi.

  Canary gài **8 lỗi đã biết** vào một gói GIẢ rồi đòi dây chuyền bắt: `apply`+`na` trên nghiên
  cứu thường · `apply`+`na` trên guideline chưa khai basis · `apply` chỉ dựa Consensus · thiếu
  `gradeBy` · miễn trừ provenance **không được** tắt luật item · hai bản nói ngược nhau · PMID
  đã rút bắt ở khâu nhận · PMID không tra được **không** thành `ok`.

  ✅ **Đã kiểm bằng đột biến trên đúng lỗi lịch sử:** tái hiện `return` sớm ngày 12/08 ⇒ canary
  đỏ **5/8**. Tức nếu canary tồn tại từ 12/08, lỗi che 73 mục đã bị bắt ngay hôm đó.
  Bản đầu của canary còn **kỳ vọng NHẦM nhánh** luật `apply`+`na` (đòi thông điệp
  "normativeBasis" cho một `design:'RCT'`) — **cổng mới là bên đúng**. Đó chính là giá trị của
  phép thử có đáp án biết trước: nó sửa cả người viết test.

  ⚠️ **Giới hạn có chủ ý, đừng nói quá:** canary kiểm **dây chuyền CÔNG CỤ** — chứng minh
  *"cổng bắt được lỗi nếu gói đi qua cổng"*, KHÔNG chứng minh *"agent đã GỌI cổng"*. Vế sau chỉ
  quan sát được ở phiên thật; doctrine + BH39/40/41 làm cho vế sau khả dĩ, không thay thế được.

  📌 **ĐÍNH CHÍNH — 7 chốt TỰ CHẠY mỗi phiên, không phải 5.** Ghi chú trước đó của tôi nói
  `chot_hoi_quy_bai_hoc` "chỉ chạy khi có người gõ lệnh" là **SAI** (lệnh grep bị cắt ở dòng
  20). Danh sách đúng ở `SessionStart`: `chot_hoi_quy_bai_hoc` · `dong_bo_skill` ·
  `kiem_do_tuoi_chung_cu` · `kiem_nguon_that` · `kiem_plugin_day_du` · `tu_khoi_dong` ·
  `tu_sua_chua`. Vì **BH43 gọi canary từ bên trong** `chot_hoi_quy_bai_hoc`, canary đã tự chạy
  mỗi phiên — nên KHÔNG thêm hook riêng (thêm sẽ chạy hai lần và hai chỗ cùng báo một việc).
  *Số đo: canary 2 giây · trọn bộ 43 chốt 19 giây.*

  ## 🕸️ TẦNG ĐIỀU PHỐI AGENT — đo lần đầu 15/08/2026, chốt `kiem_dieu_phoi.py` (BH44)
  Tầng duy nhất chưa từng được đo. Kết quả: **đồ thị điều phối LÀNH** — `dieu-phoi-lam-sang`
  gọi 23 agent, `dieu-phoi-nghien-cuu` gọi 31, **0 agent mồ côi**, `dien-giai-ket-qua` thuộc
  nhạc trưởng nghiên cứu (G6.5) đúng thiết kế. Nhưng lần đo đầu lộ 2 lớp việc thật:

  🔴 **3 skill của bác sĩ chạy runtime mà KHÔNG có nguồn trong cây OneDrive** —
  `nghien-cuu-ebm-tong-hop` (44K) · `dao-tao-slide-tai-lieu-y-khoa` (28K) · `ehospital-mini`.
  App dọn runtime (đã xảy ra nhiều lần, đo 13/08: 20/22 skill lệch bản) là **mất trắng**, và
  `dong_bo_skill.py` không hề biết chúng tồn tại. **Đã cứu cả ba về `sync/skills/`** — nguồn
  skill nay 47, runtime 60/60 đều có nguồn.

  ⚠️ **Chính phép đo đầu tiên tạo BÁO ĐỘNG GIẢ hai lần** — ghi lại để lần rà sau không lặp:
  (a) 6 "tham chiếu agent hỏng" hoá ra là **SKILL** — tên agent và tên skill sống chung mặt
  chữ backtick nhưng thuộc **hai sổ đăng ký khác nhau**; phân giải phải tra agent ∪ skill
  nguồn ∪ skill runtime. (b) 22 skill "mất trắng" hoá ra **20 là skill dựng sẵn của
  Anthropic** (docx, pdf, pptx…) không cần nguồn cục bộ. (c) 3 tên còn lại
  (`antifacts-weekly-update`…) là **ghi chú lịch sử về routine đã RETIRE** mà doctrine tự ghi
  "không tồn tại" — xoá đi sẽ mất dấu vết vì sao retire.
  ⇒ Chốt dùng **KHAI BÁO tường minh** (`SKILL_DUNG_SAN` · `TEN_LICH_SU`) thay vì suy đoán —
  skill LẠ không nguồn vẫn đỏ, đúng như cần (BH28).

  **BH44** chạy chốt này trong bộ hồi quy (tự chạy mỗi phiên qua `chot_hoi_quy_bai_hoc`);
  đột biến kiểm: xoá nguồn một skill vừa cứu ⇒ đỏ đúng ③.

  ## 🤖 BA CHỐT TỰ ĐỘNG — hệ tự chạy, không chờ bác sĩ gọi (dựng 13/08/2026)
  Trả lời câu hỏi "hệ này đã là một hệ AGENT chưa". Trước 13/08 câu trả lời là **CHƯA**,
  và lý do đo được: `launchctl print` cho **`runs = 0 · (never exited)`** trên CẢ HAI job
  `com.medicalebm.weeklysafety` và `com.medicalebm.monthlyupdate` — **chưa từng nổ lần nào**
  kể từ khi cài 11/07. `StartCalendarInterval` đòi máy THỨC đúng 19:00 thứ Bảy; Windows
  không có launchd. Nghĩa là mọi lần cập nhật chứng cứ nhiều tháng qua đều do bác sĩ chủ
  động — hệ là CÔNG CỤ, không phải agent.
  **(a) `tools/tu_khoi_dong.py --phong` — TỰ KHỞI ĐỘNG.** Lấy lúc mở phiên làm nhịp thay
  đồng hồ: quá hạn thì phóng script giám sát ở **NỀN** (tách tiến trình, không chặn phiên).
  Chạy giống nhau trên macOS và Windows. **Ranh giới:** chỉ phóng được hai script chủ sở hữu
  trong allowlist `OWNER` (`weekly_safety.sh`, `monthly_update.sh`) — KHÔNG tự viết bộ thu
  thập mới, đúng doctrine "owner thu thập duy nhất"; kết quả vào hàng ỨNG VIÊN,
  `clinical_auto_apply: false`, Cổng A/B nguyên vẹn; khoá theo PID chống phóng chồng; công
  tắc tắt `--tat` (file `.tu-khoi-dong-tat`). **Đã kiểm THẬT 13/08:** phóng lần đầu →
  chạy trọn → `status: PASS`, 4/4 bước critical = 0. Đây là lần tự chạy đầu tiên của hệ.
  **(b) `tools/chot_hoi_quy_bai_hoc.py` — ĐÓNG VÒNG HỌC.** Mọi khiếm khuyết nghiêm trọng
  tháng vừa rồi đều do người tìm bằng tay, không chốt nào bắt được ⇒ vá xong thì bài học nằm
  trong tài liệu, không nằm trong máy, lần refactor sau lỗi quay lại y nguyên. 10 mục
  BH01–BH10, mỗi mục là **một lỗi CÓ THẬT, có ngày**, kiểm bằng cách **gọi vào mã đang sống**.
  Ba luật khi thêm mục: (1) chỉ lỗi ĐÃ xảy ra thật — chốt chưa từng bảo vệ điều gì chỉ làm
  loãng tín hiệu; (2) kiểm HÀNH VI, không đếm chuỗi trong file — đếm chuỗi đúng là bẫy
  TAUTOLOGY đã gặp ở guardrail G3/G8; (3) nhanh và ngoại tuyến.
  **Bắt được ngay lần chạy đầu:** `tools/run_retraction_and_med_safety.py` ghi cứng
  `C:/Users/Admin/OneDrive/Claude AI` ⇒ **chưa từng chạy được trên Mac** — cùng lớp lỗi với
  `ensure_strict_source.py`/`docx_sang_pdf_giu_mau.py`, và nằm đúng trong công cụ kiểm RÚT
  BÀI. Đã vá bằng `Path(__file__).resolve().parents[1]`.
  **(c) `tools/tu_sua_chua.py --ap-dung` — TỰ VÁ máy móc** (skill lệch bản · kho plugin thiếu
  · sai interpreter). KHÔNG đụng nội dung y khoa.
  🔴 **BẰNG CHỨNG vì sao ba việc lâm sàng phải cấm tự động — xảy ra 13/08 với chính công cụ
  vừa viết.** `tools/trinh_muc_can_duyet.py` bản đầu xét dấu hiệu "yếu" TRƯỚC dấu hiệu "quy
  phạm", mà trường `design` trong dữ liệu THẬT gắn nhãn `Consensus` cho **cả cảnh báo HỘP ĐEN
  FDA về JAK inhibitor** (PMID 35081280) **lẫn chống chỉ định leflunomide trên NHÃN THUỐC
  FDA**, cộng AGS Beers 2023, STOPP/START v3, tiêu chuẩn chẩn đoán GOLD, tiêu chuẩn phân loại
  ACR/EULAR 2010. Kết quả: **8 nguồn quy phạm bị xếp vào nhóm "nên HẠ decision"**. Nếu lớp ngữ
  nghĩa đó có quyền ghi, nó đã hạ hai cảnh báo an toàn.
  **Đã vá:** xét NGUỒN (`gradeSource`) trước THỂ LOẠI (`design`), và tách nhóm thứ tư
  `ĐỒNG THUẬN` thay vì gộp vào "yếu thật". Phân nhóm 56 mục đi từ *(QUY PHẠM 24 · YẾU THẬT 20
  · CHƯA RÕ 12)* về **QUY PHẠM 30 · ĐỒNG THUẬN 12 · YẾU THẬT 2 · CHƯA RÕ 12** — con số 2 khớp
  đúng phân tích tay từng mục (chỉ `VKDT ITEM-04` bài tổng quan tường thuật và
  `COPD_TimThanChuyenHoa ITEM-26` tác giả tự chấm vận hành).
  **Bài học chung: `design` là chuỗi TỰ DO — không bao giờ dùng nó làm căn cứ quyết định an
  toàn.** Đã khoá bằng BH03 (miễn trừ quy phạm phải từ chối `Consensus`) và BH10 (không công
  cụ nào được ghi `decision`/`gradeLevel`).

  ## ✍️ QUYẾT ĐỊNH LÂM SÀNG BÁC SĨ ĐÃ DUYỆT 13/08/2026 — 11 mục
  Đây là dấu vết của các thay đổi `decision`/`gradeLevel` **do bác sĩ chuẩn y**, không phải
  máy tự làm. Ghi ở đây vì `EBM-Dashboards/` nằm NGOÀI git (kiến trúc code→GitHub ·
  dữ liệu→OneDrive) nên lịch sử sửa không có trong commit. Mọi bản đều có `.bak-<dấu-thời-gian>`.

  **(a) HẠ `decision` — nguồn tự nói yếu (6 mục).** `apply → consider`:
  `VKDT ITEM-04` (chẩn đoán phân biệt VKDT/PsA — **bài tổng quan tường thuật**, PMID 30167326) ·
  `COPD_TimThanChuyenHoa ITEM-26` (checklist — gradeSource tự khai *"đánh giá vận hành, không
  phải phân hạng của nguồn"*) · `RA_Than ITEM-03` + `VKDT ITEM-22` (ACR 2021 — *"đa số có điều
  kiện"*) · `VKDT ITEM-35` (ACR 2021, trích nguyên văn *"khuyến cáo CÓ ĐIỀU KIỆN"*) ·
  `VKDT ITEM-37` (ACR/AAHKS 2022 — *"GRADE, mức CÓ ĐIỀU KIỆN cho toàn bộ bảng"*).

  **(b) GIỮ `apply`, sửa siêu dữ liệu cho đúng nguồn (1 mục).**
  `AnToanThuoc_Orlistat_AKI_FDA ITEM-01` — cảnh báo FDA về tổn thương thận cấp:
  `design` thêm tiền tố `"Nhãn thuốc — "` · `gradeLevel` **low → na** · khai
  `normativeBasis:"drug-label"`. Căn cứ: chính `gradeSource` đã tự ghi *"Nhãn gradeLevel là
  đánh giá vận hành, KHÔNG phải GRADE chính thức"* — FDA không dùng thang GRADE, nên `na` mới
  trung thực. **Hạ một cảnh báo an toàn của cơ quan quản lý xuống "cân nhắc" là làm GIẢM an toàn.**

  **(c) ĐỒNG NHẤT hai bản cùng chủ đề (5 mục).** `DauDau_TongHop 11/08` ITEM-04/07/20/21/24 được
  chép NGUYÊN `normativeBasis` + `decision:"apply"` từ bản `DauDau 18/07` đã duyệt (ICHD-3 →
  `official-classification`; EAN/SISC-IHS/MOH/TTH → `guideline-strong-rec`). Ánh xạ khớp tuyệt đối
  (cùng ITEM, cùng PMID, cùng design/gradeLevel), khác biệt DUY NHẤT là bản mới chưa được áp đợt
  sửa quy phạm 12/08. Mâu thuẫn giữa hai bản: **19 → 14**.

  🔴 **MỘT MỤC BỊ DỪNG LẠI — dashboard khai SAI về nguồn.** `SuyTim_NoiTiet ITEM-05` (nhận biết
  khủng hoảng thượng thận) có `gradeSource` ghi *"không phân hạng GRADE chính thức"*, nhưng tra
  PubMed thì hướng dẫn Endocrine Society (Bornstein 2016, PMID 26760044,
  doi:10.1210/jc.2015-1710) nói rõ **được xây dựng BẰNG hệ thống GRADE**. Vậy `gradeLevel` KHÔNG
  được chuyển sang `na` — nguồn CÓ chấm, chỉ là dashboard chưa ghi mức thật. Cần đọc toàn văn,
  ánh xạ mục này vào đúng khuyến cáo được đánh số rồi ghi mức GRADE nguyên bản.
  **Bài học: `gradeSource` là lời NGƯỜI SOẠN khai, không phải sự thật đã kiểm — phải tra nguồn
  trước khi dựa vào nó để đổi phân hạng.**

  **Tổng kết đợt:** mục `apply` bị cổng chặn **56 → 49**; nhóm "yếu thật" **20 → 0**; độ phủ xác
  minh tồn tại của nguồn **118 → 1146 định danh (phủ toàn bộ kho)**. *(Đính chính số cũ: mẫu số
  "297" từng ghi là do đếm bằng regex chỉ nhận nháy ĐƠN — tổng thật ~1103, nên điểm xuất phát là
  11% chứ không phải 39%.)* Kiểm rút bài **vẫn 0** — NCBI chặn máy này, cần `NCBI_API_KEY`.

  **NHẮC ĐỘ TƯƠI:** `tools/kiem_do_tuoi_chung_cu.py` đã nối vào hook `SessionStart` — vì hai job
  launchd (`weeklysafety` T7 19:00 · `monthlyupdate` mùng 1 18:00) kiểm ngày 11/08 đều cho
  `runs = 0` · `(never exited)`: **chưa từng tự nổ lần nào**, do `StartCalendarInterval` đòi máy phải
  thức đúng giờ đó. Máy móc KHÔNG hỏng — `weekly_safety.sh --canary` cho PASS toàn bộ (4/4 nguồn
  khoẻ, scanner ra ứng viên). Chốt chỉ NHẮC, không tự quét.
  🔴 **Chốt này CHẾT IM LẶNG trên Windows từ lúc ra đời tới 12/08.** Nó gọi `os.getuid()` — hàm KHÔNG
  tồn tại trên Windows — và chỉ bắt `(OSError, SubprocessError)`, nên `AttributeError` làm chết cả
  công cụ; hook lại kết thúc bằng `; true` nên **nuốt lỗi không một dòng báo**. Máy Windows vì thế
  chưa từng được nhắc lần nào. Vá 12/08: guard `sys.platform != "darwin"` + bắt `Exception` rộng
  (chốt nhắc không được phép làm chết phiên), và thông điệp đổi theo nền tảng — trên Windows nói
  thẳng **"máy này KHÔNG có lịch nền nào chạy giám sát, luôn phải chạy tay"** thay vì để bác sĩ tưởng
  launchd đang chạy hộ. Chạy ngay sau khi vá đã lòi ra việc thật: **giám sát an toàn thuốc lần cuối
  17/07, quá hạn 26 ngày** (ngưỡng 10).
  ⚠️ **Lớp lỗi này lặp lại nhiều lần — kiểm mọi công cụ dùng chung trên CẢ HAI máy, đừng tin
  "chạy được ở đây là chạy được ở kia".** Cùng đợt còn tìm thấy `tools/ensure_strict_source.py` ghi
  CỨNG `ROOT = Path("C:/Users/Admin/OneDrive/Claude AI")` (gãy trên Mac) và
  `tools/docx_sang_pdf_giu_mau.py` chỉ dò trình duyệt theo đường dẫn macOS nên **không bao giờ in
  được PDF trên Windows dù máy có sẵn cả Chrome lẫn Edge**. Cả ba đã vá.
  **Vì sao có ④ (thêm 05/08/2026):** `.docx` là tệp nén nhị phân nên **khung chat Claude KHÔNG mở thẳng được**,
  chỉ hiện thẻ tải về — bác sĩ phải rời khung chat mới đọc được tài liệu đầy đủ. Bước ④ dùng `pandoc` dựng
  HTML tự chứa **từ CHÍNH file `.docx` vừa sinh** (không dựng lại từ dữ liệu, để không có đường nào làm hai
  bản lệch nhau). **GIỮ** đủ chữ · bảng · đề mục · thứ tự; **MẤT** màu nền ô — huy hiệu mức chứng cứ/quyết
  định chỉ còn phần chữ, nên `.docx` vẫn là bản lưu trữ chuẩn và trang HTML tự in sẵn một dòng cảnh báo điều
  này ở đầu trang.
  ✅ **KHÔNG CÒN PHỤ THUỘC pandoc (đổi 12/08/2026 theo quyết định của bác sĩ).** Trước đó máy thiếu pandoc
  thì mất **CẢ ④ LẪN ⑤** (vì ⑤ dựng từ HTML của ④) ⇒ Windows chỉ ra 3/5 sản phẩm trong khi Mac ra đủ 5 từ
  cùng một dashboard — đúng thứ mà việc gộp "bộ năm" vào một lệnh sinh ra để tránh. Nay có nhánh dự phòng
  `tools/docx_sang_html_khong_pandoc.py` dựng HTML thẳng từ `.docx` bằng **python-docx** (đã có trong venv
  `~/.ebm-venv`). Đáng chú ý: nhánh này đọc màu từ chính `w:shd/@w:fill` nên **GIỮ ĐƯỢC màu nền ô** —
  thứ pandoc bỏ mất — nên trang sinh bằng nhánh dự phòng KHÔNG in cảnh báo "mất màu" (in cảnh báo đó khi
  màu vẫn còn là nói sai với người đọc). Mac có pandoc thì vẫn đi nhánh pandoc như cũ.
  **Đã kiểm THẬT trên Windows 12/08:** đủ **5/5 sản phẩm**, PDF 641 KB, **354/354 ô màu** bơm được,
  30/30 bảng, 112% số từ so với bản Word. Mac vẫn có pandoc 3.10 (`~/.local/bin/pandoc`). Không xuất được PDF trên Mac này: thiếu engine LaTeX, và Microsoft Word tuy có cài nhưng **từ chối
  mọi lệnh mở file qua AppleScript/MCP** (trả về 0 documents ở cả `/private/tmp`, `~/Documents` lẫn OneDrive)
  — cần PDF giữ màu thì bác sĩ tự mở `.docx` rồi `File → Save as → PDF`.
  **Sau khi chạy, MẶC ĐỊNH mở cả BỐN file cho bác sĩ ngay trong Claude** (SendUserFile, `display:"render"`
  cho 3 file HTML; `.docx` đính kèm để tải) — không bắt bác sĩ tự đi tìm trong thư mục.
  Chạy được trên cả macOS lẫn Windows: tool gọi trình thông dịch bằng `sys.executable` (Windows không có
  lệnh `python3`) và tự ép UTF-8 cho stdout (Windows mặc định cp1252 sẽ chết khi in tiếng Việt).
  Kiểm hồi quy kỹ thuật cho toàn dây chuyền này bằng `python3 tools/verify_clinical_evidence_update_pipeline.py`
  (fixture offline, không PII; dashboard thật vẫn cần `--online`, rà toàn văn và bác sĩ duyệt).
  **Vì sao có ⑤ (thêm 10/08/2026):** bước ④ dùng `pandoc`, mà pandoc **bỏ hết màu nền ô** khi chuyển `.docx`→HTML — mất đúng thứ giúp nhìn lướt bắt được mức khuyến cáo (xanh lá `#15803D` Cao/Áp dụng ngay · cam `#B45309` Trung bình/Cân nhắc · đỏ `#B91C1C` Rất thấp). `tools/docx_sang_pdf_giu_mau.py` đọc màu **từ chính `.docx`** (`w:shd/@w:fill`) rồi bơm lại vào HTML của bước ④, sau đó in bằng **Chrome headless** — giữ nguyên tắc mọi bản phái sinh sinh từ CÙNG một nguồn, không dựng lại tài liệu từ dữ liệu. Đã kiểm 9/9 tài liệu: 16-20 màu nền mỗi bản (bản HTML chỉ còn 4) và 102-111% chữ so với bản Word. **Câu 'máy này không xuất được PDF' trong các ghi chú cũ ĐÃ LỖI THỜI** — nó đúng cho đường LaTeX và Word-tự-động, nhưng đường Chrome thì chạy được và giữ màu. Máy thiếu Chrome/Edge/Chromium thì bước ⑤ bị bỏ qua kèm thông báo rõ, **không** làm hỏng bốn sản phẩm kia và **không** đổi mã thoát — PDF là tiện ích đọc, không phải cổng chất lượng.
- **Triển khai giám sát định kỳ fail-closed:** owner thu thập duy nhất là `medical-ebm-automation/scripts/weekly_safety.sh` + `monthly_update.sh`; routine khác chỉ dùng candidate queue. `source_health=PARTIAL/FAIL` giữ watermark, chặn bridge Hub/cảnh báo nội dung. Chỉ `READY_FOR_CONTROLLED_DEPLOYMENT` từ `python3 medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py --online` mới cho phép candidate-only; canary, runtime tuần/tháng, alert, rollback, 2 chu kỳ shadow và UAT/phê duyệt thật là bắt buộc. Claude Code không tự điền PASS hoặc ký UAT.
- Áp dụng cho skill `cap-nhat-chung-cu-y-khoa` và mọi tác vụ dashboard lâm sàng. Ngoại lệ: Dashboard Master
  quản trị (skill `dashboard-master-ebm-ngoai-tru`) giữ định dạng Excel/sổ riêng.
- Liêm chính: số liệu trích ĐÚNG nguồn; giữ nguyên grading (`gradeLevel:'na'` nếu không phân hạng); RoB 2
  chỉ cho RCT; kèm PMID/DOI; disclaimer "Cần bác sĩ kiểm chứng"; KHÔNG PII.
- **Lưu & tích lũy (thư mục chung):** mọi dashboard xuất vào `EBM-Dashboards/` (OneDrive-synced Mac↔Windows).
  Sau khi xuất, **chạy trong `EBM-Dashboards/`**: (1) `python3 tools/verify_dashboard.py <file>.html --online` → PASS;
  (2) `python3 tools/build_library.py add <file>.html` để cập nhật chỉ mục `evidence-library.html`. Hướng dẫn: `EBM-Dashboards/README.md`.
- **(3-bis) BẢN ĐỌC sau cập nhật — MẶC ĐỊNH TỰ CHẠY (bác sĩ chốt 2026-08-05):**
  `python3 tools/build_ban_doc_chung_cu.py <dashboard>.html` → `EBM-Dashboards/derivatives/<mã>_ban-doc.html`.
  Đây là trang bác sĩ ĐỌC NGAY sau khi chạy xong dây chuyền: cờ đỏ và việc cần làm đứng TRƯỚC, chứng cứ
  đặt sau trên MỘT trục thang log dùng chung (vạch 1,0 ở giữa — trái có lợi, phải bất lợi). Khác dashboard
  (công cụ tra cứu có bộ lọc) và khác bản Word (tài liệu lưu trữ đầy đủ). Tool tự chuẩn hoá VIẾT HOA THEO CÂU:
  khối `DATA` hay dùng VIẾT HOA TOÀN BỘ để nhấn mạnh ("KHÔNG dùng…", "phân suất tống máu BẢO TỒN"), trang đọc
  hạ về chữ thường và nhấn bằng màu + độ đậm, NHƯNG giữ nguyên tên viết tắt (HFrEF, PCI) và tên thử nghiệm
  (PARADIGM-HF, ATTR-CM). Chỉ mục có hiệu số định lượng mới lên biểu đồ; guideline/đồng thuận liệt kê riêng.
- **(3) KHÔNG còn tự đồng bộ lên Antifacts/hub (đổi mặc định 2026-08-05 theo yêu cầu bác sĩ).**
  Trước đây bước này chạy `EBM_MASTER/tools/sync_all.py` mặc định; nay **chỉ chạy khi bác sĩ yêu cầu riêng**.
  ⚠️ **Bỏ chạy `sync_all.py` là KHÔNG ĐỦ để giữ một gói ngoài Antifacts:** `tools/build_antifacts.py` quét
  `EBM-Dashboards/WebDashboard_*.html` bằng **glob**, và hai lịch launchd (`com.medicalebm.weeklysafety` /
  `com.medicalebm.monthlyupdate`) vẫn dựng lại Antifacts từ chính thư mục đó — nên gói mới sẽ tự lên hub.
  Muốn giữ ngoài hub thì **phải khai tên file** vào `EBM-Dashboards/antifacts-exclude.txt` (mỗi dòng một tên
  file; `#` là chú thích), rồi chạy lại `python3 tools/build_antifacts.py`.
  Nội dung mục (3) cũ giữ lại dưới đây để dùng khi bác sĩ yêu cầu đồng bộ:
- **(3-cũ) Đồng bộ vào hub EBM_MASTER — CHỈ KHI ĐƯỢC YÊU CẦU:** sau khi PASS, nạp dashboard
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
  truyền thì liệt kê tuần tự dưới 1 mục "Nội dung chứng cứ". ⛔ **ĐÍNH CHÍNH 18/08/2026 — câu cũ ở đây
  ("Mac hiện KHÔNG có Node.js/LibreOffice/pandoc/Homebrew") SAI ở 2/4 vế và tự mâu thuẫn với chính dòng
  1025 của file này.** Đo lại từng vế: **`node` v24.18.1 CÓ** (`~/.local/bin/node`, kèm `npm` 11.16.0) ·
  **`pandoc` 3.10 CÓ** (`~/.local/bin/pandoc` — dòng 1025 đã ghi đúng điều này từ trước, nên câu cũ mâu
  thuẫn nội bộ) · **LibreOffice/`soffice` THIẾU thật** · **Homebrew THIẾU thật**. Cả hai thứ CÓ đều nằm ở
  `~/.local/bin` chứ không phải `/usr/local/bin`, nên lệnh dò theo đường dẫn hệ thống sẽ báo thiếu nhầm —
  đây nhiều khả năng là nguồn gốc của khẳng định sai. Hệ quả: nhánh docx-js của skill `docx` **dùng được**
  trên máy này; vẫn KHUYẾN NGHỊ `python-docx` (đã có trong venv `~/.ebm-venv`) cho dây chuyền dashboard vì
  toàn bộ `build_dashboard_docx.py` đã viết theo nó — đổi sang docx-js là đổi cả dây chuyền, không phải đổi
  một lệnh. Xác thực output bằng `scripts/office/validate.py` của skill `docx` (kiểm XSD OOXML thuần
  Python) thay cho bước dựng ảnh xem trước (soffice+pdftoppm) mà máy này **thật sự** không chạy được (thiếu
  LibreOffice); chú ý bẫy thứ tự
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

## 🩺 TẦNG CUỘC GẶP — hai công cụ đầu tiên phục vụ PHÒNG KHÁM, không phải kho chứng cứ (22/08/2026)

**Vì sao có.** Báo cáo `audit/03-diem-nghen-thuc-hanh-ngoai-tru_2026-08-22.md` đo lại kho công cụ
và tìm ra một mất cân đối chưa ai nói ra: **117 tool, trong đó 32 tool chỉ để hệ tự kiểm chính nó,
và ĐÚNG 1 tool chạm vào khoảnh khắc trong phòng khám** (`tra_diem_kham.py`). Toàn bộ A1–A10 ·
B1–B5 · C1–C5 phục vụ **chuỗi cung ứng chứng cứ**. Trong khi số đo y văn nói tổn hại ngoại trú tập
trung ở chỗ khác: **78,9%** điểm gãy sai sót chẩn đoán nằm trong CUỘC GẶP (Singh 2013, PMID
23440149) và **6,8–62%** kết quả xét nghiệm không được theo dõi tiếp (Callen 2012, PMID 22183961).
*Cần bác sĩ kiểm chứng — số liệu Mỹ, cái chuyển được là VỊ TRÍ điểm gãy, không phải con số.*

**Luận điểm nối hai tầng:** độ chính xác chẩn đoán rơi 55,3% → 5,8% giữa ca dễ và ca khó trong khi
độ tự tin gần như không đổi 7,2 → 6,4/10 (Meyer 2013, PMID 23979070) ⇒ **niềm tin không đo được độ
đúng, nên phòng vệ phải nằm NGOÀI đầu bác sĩ.** Đó chính là kỹ thuật hệ này đã thành thạo ở tầng
chứng cứ (32 chốt tự kiểm) — hai công cụ dưới đây chỉ áp đúng kỹ thuật ấy cho tầng cuộc gặp.

**(a) `python3 tools/so_viec_chua_dong.py` — SỔ VIỆC CHƯA ĐÓNG.** Canh mọi thứ còn treo sau khi
bệnh nhân ra về (xét nghiệm chờ kết quả · hình ảnh · chuyển tuyến · tái khám · thử điều trị).
`--them` mở việc (BẮT BUỘC có hạn: `--han` hoặc `--han-sau N`) · `--dong` · `--huy --ly-do`
(huỷ không dấu vết là cách một việc biến mất mà không ai biết) · `--ds` · `--tuan` ·
mặc định in việc quá hạn. **Mã thoát 0/1/2**; có `--im-khi-on` để nối làm **chốt thứ 8** của hook
`SessionStart` (7 chốt hiện tại + cái này).
**Ranh giới cứng:** chỉ ĐO và NHẮC — không suy diễn lâm sàng, **không tự đóng việc**, không ghi
`decision`/`gradeLevel` (BH10, có test khoá). **Bộ chặn PII** ở `soi_pii()` cố ý chỉ bắt mẫu ĐỘ
CHÍNH XÁC CAO (điện thoại · dãy 9/12 số · email · ngày sinh · từ khoá định danh) — **không dò tên
riêng**, vì tiếng Việt viết hoa ở quá nhiều chỗ và chặn oan hàng loạt sẽ dạy người dùng bỏ qua cảnh
báo (BH08); thông điệp lỗi nói thẳng giới hạn đó.
**Sổ nằm NGOÀI git có chủ ý:** `state/viec-chua-dong.jsonl` rơi vào luật `/*` của `.gitignore` —
đây là dữ liệu vận hành phòng khám, chỉ CÔNG CỤ mới cần version-control.
Hồi quy: `python3 tools/test_so_viec_chua_dong.py` (30 test, đã kiểm bằng 2 phép đột biến —
bỏ regex điện thoại ⇒ đỏ 2; cho bản ghi thiếu hạn rơi vào nhóm "ổn" ⇒ đỏ 1).

**(b) `python3 tools/kiem_safety_net.py` — CHỐT SAFETY-NETTING.**
🔴 **Lỗi đã tồn tại trong repo, nay mới đo được:** `CLINICAL_RUNTIME_FLAGS.json` khai
`enforce_safety_net_templates: true`, nhưng `grep` toàn repo trả **0 file tham chiếu** tới
`clinical_runtime/safety_net_templates.json`, và nội dung file đó là **ba mẫu tiếng Anh chung
chung** ("Recommend follow-up within 4-6 weeks", "Severe shortness of breath") — không hội chứng,
không tiêu chí đo được, không nguồn. Tức **một lá cờ tuyên bố có thi hành mà không có gì thi hành**
— cùng HỌ với `return` sớm 12/08 (che 73 mục), BH27 (fail-open cổng A12) và BH61 (khoá lạ trong
`DATA.summary`), nhưng lần này rơi vào **tầng an toàn cho bệnh nhân**, không phải tầng governance.
**Đã dựng lại `safety_net_templates.json` v2.0.0** với schema 8 hội chứng và **hai trục TÁCH RIÊNG**:
`co_do_cho_bac_si` (dấu hiệu bác sĩ tìm lúc khám) ≠ `dan_benh_nhan_quay_lai` (câu dặn mang về nhà)
— gộp hai thứ này là biến thuật ngữ chuyên môn thành lời khuyên cho người bệnh.
**9 luật của chốt:** R1 khung · R2 trạng thái khớp nội dung · R3 đủ hai trục · R4 nguồn phải truy
được (PMID / DOI / guideline+năm — **văn xuôi bị từ chối**) · R5 ≥1 tiêu chí `do_duoc:true`
("nếu nặng hơn" không phải tiêu chí) · R6 khai `co-nguon` mà còn `[CẦN BÁC SĨ ĐIỀN]` ⇒ lỗi ·
R7 phải NÓI RA giới hạn nguyên văn của nguồn · R8 hạn rà soát 365 ngày ·
**R9 — luật mạnh nhất: cờ bật mà 0 hội chứng có nguồn ⇒ LỖI CỨNG.** Thiếu file cờ ⇒ fail-closed
(giả định cờ đang bật), không đọc thành "cờ đang tắt".
**Độ phủ hiện tại, nói thẳng: 1/8 hội chứng có nguồn · 0/8 có lời dặn bệnh nhân.** Mục duy nhất đã
điền là `dau-dau`, chép NGUYÊN 15 mục **SNNOOP10** (Do TP và cs., Neurology 2019;92(3):134-144 ·
PMID **30587518** · doi:10.1212/WNL.0000000000006697) kèm **giới hạn nguyên văn của chính bài gốc**
("một công cụ sàng lọc đã kiểm định VẪN CHƯA CÓ") — không được trình bày như thang đã kiểm định.
7 hội chứng còn lại để `chua-dien` + `[CẦN BÁC SĨ ĐIỀN]`: **trạng thái TRUNG THỰC, không phải lỗi**
— bịa ngưỡng cờ đỏ cho 7 hội chứng là đúng thứ doctrine cấm tuyệt đối.
Hồi quy: `python3 tools/test_kiem_safety_net.py` (21 test, mutation-tested).
🔎 **Chính test bắt được một fail-open trong bản đầu của chốt:** `hc.get("dan_benh_nhan_quay_lai", {})`
— `{}` LÀ dict nên `isinstance` luôn đúng ⇒ hội chứng **thiếu hẳn** khối lời dặn vẫn lọt R3. Mặc định
phải là `None`. Đúng bài học nền: luật CÓ MẶT nhưng không bao giờ chạy tới.

**Hai việc CHƯA làm, có chủ ý** (nêu ở §V báo cáo, chờ bác sĩ quyết): ② ô "Nghị trình bệnh nhân"
trong mẫu SOAP là đổi THÓI QUEN chứ không phải code; ④ "tờ quyết định một trang" (đầu ra thứ 6 của
`xuat_goi_cap_nhat.py`) đụng vào dây chuyền có 3 bản đồng bộ nên cần bác sĩ duyệt trước.

## Lệnh
> Chạy trong `medical-ebm-automation/` (dự án sống), với venv `~/.ebm-venv` đã kích hoạt.
- Cài: `pip install -r requirements.txt`
- Chạy app/dashboard: `python run.py` (hoặc "Mở Dashboard.command")
- Kiểm nhanh: `python -m compileall -q app scripts tests`
- Test: `pytest` (khi venv đã có dev dependencies)
- Lint: `ruff check` (khi venv đã có dev dependencies)
- Audit chung từ thư mục gốc: `python3 tools/audit_ebm_system.py`
- **Sổ việc chưa đóng (tầng cuộc gặp):** `python3 tools/so_viec_chua_dong.py` — mặc định in việc
  quá hạn; `--them`/`--dong`/`--huy`/`--ds`/`--tuan`. Chỉ ĐO và NHẮC, không PII, ngoại tuyến.
- **Chốt safety-netting:** `python3 tools/kiem_safety_net.py` — kiểm CẤU TRÚC ngân hàng cờ đỏ /
  lời dặn (9 luật, R9 chặn cứng khi lá cờ `enforce_safety_net_templates` nói hộ).
- **Kiểm + đồng bộ toàn hệ một lệnh:** `python3 tools/upgrade_verify.py` (hoặc bấm đúp "Nâng cấp & Kiểm tra EBM") — chạy trọn enforce→sync→check→routing→assess→audit→orchestrator(validate+test).
- **Kiểm riêng repo/Claude Code/Codex alignment:** `python3 tools/verify_claude_code_repo_alignment.py` — bắt lệch `AGENTS.md`/`CLAUDE.md`, file governance chưa track Git, hoặc sync health đỏ. Nếu cần soi riêng mirror agent, chạy `python3 tools/check_claude_codex_sync_health.py`.
- **Kiểm riêng rubric QA ↔ LESSONS taxonomy:** `python3 tools/verify_lessons_rubric_alignment.py` — bắt mọi mã lỗi rubric thiếu hàng taxonomy/bridge để vòng Evaluate→Learn không hở.
- **Kiểm riêng clinical runtime governance:** `python3 tools/verify_clinical_runtime_schema_hardening.py` — chốt source integrity, prompt injection, conflicting evidence trong schema.
- **Kiểm riêng pipeline cập nhật chứng cứ lâm sàng:** `python3 tools/verify_clinical_evidence_update_pipeline.py` — kiểm Evidence Workbench→verify_dashboard→library→derivatives→hợp đồng sync_all bằng fixture offline không PII.
- **Kiểm cổng triển khai giám sát ngoại trú:** `python3 medical-ebm-automation/tools/verify_evidence_surveillance_deployment.py --online` — PASS cuối chỉ khi đủ runtime + UAT thật; pre-commit/audit dùng `--contract-check` để kiểm fail-closed mà không giả lập phê duyệt.
- **Kiểm LIÊM CHÍNH NỘI DUNG tài liệu nghiên cứu (mới 2026-07-31):**
  `python3 tools/verify_exports_integrity.py` (trong `medical-ebm-automation/`; `--staged` cho hook,
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
- **Chạy chu trình tự động có kiểm soát:** `python3 tools/run_controlled_automation_cycle.py` — gom sync/routing/gate/dữ liệu/phản biện-thống kê/clinical governance thành một quyết định fail-closed hoặc human-gated.
- **Orchestrator chạy được (control plane 6 năng lực, dry-run):** `python3 tools/run_orchestrator.py "<ca/đề tài/câu hỏi>"` — định tuyến intent → dựng plan theo flow → dừng ở cổng bác sĩ → chốt guardrail. `--capabilities`/`--validate`/`--resume`. Tài liệu + 43 test (gồm cầu THẬT `guardrail_bridge.py`→`tools/eval/run_eval.py` vá dead-code `guardrail_fail` — xem `orchestrator.py::_guardrail_reroute_loop`; `appraisal_bridge.py` là seam mô phỏng riêng, CHƯA cắm vào orchestrator.py, 5/43 test): `tools/orchestrator/`.
- **"Đề tài này THỰC SỰ đang ở đâu, còn gì phải làm?" (mới 2026-07-27):**
  `python3 tools/study_readiness.py --study <mã>` (hoặc `--all`). Trả lời đúng câu hỏi mà
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
  `python3 tools/g0_quality_gate.py --study <mã>`. Chấm lại G0 từ artifact + `study_meta.json`
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
- **Danh sách + theo dõi TẤT CẢ đề tài (mới 2026-07-17):** `python3 tools/list_studies.py` — quét `exports/*/`, phân loại đề tài nhận diện được (topic + cổng xa nhất + mốc IRB/SAP/DB-khóa/kết quả/G9-ký) vs thư mục lạ vs thư mục RỖNG (nghi bị bỏ dở/gõ nhầm mã `--study`). `--study <mã>` xem chi tiết 1 đề tài; `--json` xuất máy đọc. Mỗi đề tài LUÔN có thư mục riêng `exports/<study>/` dùng xuyên suốt G0-G10 (mọi `run_g*_auto.py` ghi vào đó theo `--study`); `run_g0_auto.py` tự cảnh báo (không chặn) nếu `--study` trùng mã một đề tài khác hẳn về topic, tránh trộn lẫn dữ liệu 2 đề tài vào cùng thư mục.

- **Hợp đồng CHẤT LƯỢNG cổng G3 — cỡ mẫu (mới 2026-07-28):**
  `python3 tools/g3_quality_gate.py --study <mã>`. Tự chạy sẵn ở bước cuối của
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
  `python3 tools/g4_quality_gate.py --study <mã>`. Tự chạy ở bước cuối `approve_gate.py --gate G4`
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
  `python3 tools/g8_quality_gate.py --study <mã>`. Tự chạy ở bước cuối `run_g8_auto.py`.
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
  `python3 tools/g9_quality_gate.py --study <mã>`. Tự chạy ở bước cuối `run_g9_auto.py`; gọi tay để
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
