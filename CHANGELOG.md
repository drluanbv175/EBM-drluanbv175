# Changelog — Hệ Agent + Skill EBM

Định dạng theo [Keep a Changelog](https://keepachangelog.com/), phiên bản theo
[Semantic Versioning](https://semver.org/). Phạm vi CHANGELOG này là **hệ agent lâm
sàng/nghiên cứu (`.claude/agents/`) + kho skill khoa học Việt hóa (`sync/skills/`) + công cụ
quản trị (`tools/`)** — không bao gồm `medical-ebm-automation/` (dự án con có git riêng) hay
các thư mục dashboard/nội dung khác ở gốc "Claude AI".

## [Unreleased]

## [1.2.1] - 2026-07-05

Rà nhất quán sau đợt 48→50 agent + đóng gói xong phần MÁY LÀM ĐƯỢC của gói đánh giá
người (κ/Likert) — nút thắt lớn nhất từng bị lặp lại nhiều lần trong các audit trước.

### Fixed — Số đếm agent còn sót (48→50)
- `_BAN-DO-KET-NOI.md` (tiêu đề), `dieu-phoi-nghien-cuu.md` (dòng tự-sinh-agent),
  `README.md` (nhật ký thêm agent thứ 50 `tham-dinh-do-chinh-xac-chan-doan` chưa được
  ghi) — cả 3 nay khớp "50 agent: 21 lâm sàng + 28 nghiên cứu + 1 guardrail".
- `tools/upgrade_verify.py` bước 8: nhãn "16 test" lỗi thời → "23 test" (khớp bộ test
  orchestrator thật).

### Added — Gói đánh giá người (`tools/eval/`) — phần chuẩn bị máy làm xong
- Phát hiện: 50 khuyến nghị agent (`agent_outputs/cases_all_C01-C50.md`) đã được sinh
  và xác minh trích dẫn từ 2026-06-15, nhưng 2 phiếu chấm (`expert_kappa_template.csv`,
  `likert_template.csv`) vẫn là skeleton rỗng — chưa ai điền case_id/tóm tắt/khuyến
  nghị cho cả 50 ca.
- Sinh `templates/expert_kappa_50cases.csv` (50 dòng, cột `case_id`/`summary`/
  `agent_rec` điền sẵn từ nội dung đã có, chỉ còn `expert1/2/3/ghi_chu` trống) và
  `templates/likert_50cases.csv` (150 dòng = 50 ca × 3 bác sĩ, cột `c1..c5` trống).
- Vá lỗi `human_eval_score.py`: cột `summary`/`agent_rec` chưa nằm trong danh sách bỏ
  qua của `load_kappa()` → nếu điền text vào 2 cột này, script hiểu nhầm thành nhãn
  chuyên gia và crash ("Nhãn lạ"). Đã thêm vào danh sách bỏ qua + smoke-test cả 2 file
  50-ca (dữ liệu giả) chạy đúng, không crash.
- Cập nhật `_GOI-DANH-GIA-NGUOI.md`, `templates/RUNBOOK.md`,
  `agent_outputs/_STATUS_50_CASES.md` để phản ánh đúng: phần MÁY LÀM đã xong 100%,
  việc DUY NHẤT còn lại là bác sĩ tổ chức 3 chuyên gia chấm MÙ và điền 2 CSV.

## [1.2.0] - 2026-07-05

Dựng **orchestrator control-plane chạy được** cho đội 50 agent — vá khoảng trống tự đánh
giá "nhánh lâm sàng chưa có orchestrator chạy được như run_pipeline của nghiên cứu"; khép
lại 2 caveat A2/S2 bằng probe khách quan thay vì chỉ ghi nhận giới hạn.

### Added — Orchestrator (`tools/orchestrator/`, `tools/run_orchestrator.py`)
- 6 module tương ứng 6 năng lực: `registry.py` (nạp 50 agent thật từ `.claude/agents/*.md`,
  không hardcode), `intent.py` (định tuyến clinical_case/research_topic/single_task),
  `knowledge.py` (thứ bậc nguồn Cấp 0/0.5/1 + thứ tự tra cứu §2bis), `tools_registry.py`
  (9 công cụ Python thật đã đăng ký), `context.py` (Session + checkpoint + resume ở
  `~/.ebm-orchestrator/`), `lifecycle.py` (máy trạng thái + 4 mã thoát), `flows.py` +
  `signals.py` (plan lâm sàng 8 bước / nghiên cứu G0–G9, mỗi agent trong bước mang **điều
  kiện áp dụng riêng** qua 14 tín hiệu ngữ cảnh khớp từ khóa minh bạch — không chạy mù cả
  nhánh khi request không đúng bối cảnh).
- CLI `tools/run_orchestrator.py` (dry-run mặc định, `--capabilities`/`--validate`/
  `--resume`/`--list`/`--json`); 23 test offline (`tools/orchestrator/tests/`).
- `agent_adapter.py`: seam `LLMExecutor` cho thực thi agent thật qua wrapper Codex/LLM
  (chưa bật — `[CẦN MÔI TRƯỜNG HỖ TRỢ]`); `DryRunExecutor` mặc định chạy/kiểm được ngay,
  không cần API.

### Changed — Tự đánh giá hệ (`tools/assess_agent_system.py`)
- A2/S2: thêm probe khách quan chạy `run_orchestrator.py --validate` + 23 test thật ở chế
  độ `--deep`; sửa lại caveat cho đúng — control-plane định tuyến/lập kế hoạch/cổng nay
  CHẠY ĐƯỢC và grounded vào registry thật (0 tham chiếu treo), nhưng CHƯA tự gọi LLM để
  thực thi agent (giới hạn còn lại, không thổi phồng).

### Changed — Một lệnh kiểm toàn hệ (`tools/upgrade_verify.py`)
- Thêm bước 7–8: `run_orchestrator.py --validate` + bộ 23 test orchestrator, sau chuỗi
  enforce→sync→check→routing→assess→audit sẵn có.

### Notes
- `_HE-THONG-SCORECARD.json` tự regenerate (13/13 tiêu chí strong) sau khi chạy assess.
- Đã đồng bộ bản mirror agent trong `medical-ebm-automation/.claude/agents` (repo con,
  ngoài phạm vi CHANGELOG này) khớp 50/50 với bản chính — commit riêng trong repo đó.

## [1.1.0] - 2026-07-04

Kiểm tra toàn diện hệ thống (workflow đối kháng, không lặp audit các phiên trước) — tìm và
sửa vi phạm nguyên tắc "chỉ nguồn miễn phí" còn sót từ trước phiên v1.0.0, cùng 1 lỗ hổng
audit đã biết nhưng chưa vá.

### Fixed — Security/Policy (P0, mức nghiêm trọng nhất tìm được)
- **8/10 skill Đợt 1** (`citation-management`, `clinical-decision-support`,
  `clinical-reports`, `literature-review`, `peer-review`, `research-lookup`,
  `scientific-writing`, `treatment-plans`) còn script THẬT gọi OpenRouter API
  (`scripts/generate_schematic.py`/`generate_schematic_ai.py`, `generate_image.py` cho
  scientific-writing) — mâu thuẫn trực tiếp với disclaimer "KHÔNG dùng dịch vụ trả phí"
  ngay trong chính SKILL.md của các skill này. Đã xóa toàn bộ script + sửa SKILL.md tương ứng.
- `ebm-master/SKILL.md` và `literature-review/SKILL.md`: gỡ lệnh cài đặt
  `curl -fsSL https://parallel.ai/install.sh | bash` (đánh dấu PRIMARY) — thay bằng ghi chú
  dùng skill `research-lookup`/`paper-lookup`/`database-lookup` (miễn phí).

### Added — Audit tooling
- `tools/audit_ebm_system.py`: thêm `routine_layer_failures()` — đối chiếu
  `Scheduled/*/SKILL.md` (thư mục thật) với bảng routine trong `_BAN-DO-KET-NOI.md` §8 và
  `_ROUTINE-AGENT-WIRING.md`, đóng lỗ hổng F2 nêu trong đánh giá độc lập 2026-07-03 (lớp
  ROUTINE trước đây không được kiểm "không tham chiếu treo" như lớp AGENT).

### Fixed — Documentation accuracy
- `_THU-VIEN-KY-NANG.md`: sửa `ehospital-mini` bị liệt kê nhầm như skill (thực ra là project
  riêng); làm rõ `ke-don-an-toan-benh-man` là skill, không phải agent.
- `sync/skills/README-EBM.md`: ghi rõ "21 skill" chỉ là phần K-Dense đã Việt hóa, không phải
  tổng số skill trong `sync/skills/` (~37 thư mục thật).

### Notes
- Đã sửa thêm một số file trong `Scheduled/` (routine ngoài phạm vi git repo này — xem
  `.gitignore`): vá đường dẫn treo `dark-analyst`, đồng bộ default Evidence Workbench, thêm
  bước guardrail `tham-dinh-dau-ra` còn thiếu ở 2 routine, đăng ký 2 task lịch còn thiếu. Các
  thay đổi này có hiệu lực trên đĩa nhưng KHÔNG version-control trong repo này.
- Phát hiện nhưng CHƯA tự quyết (cần bác sĩ): 2 thư mục routine trùng lặp
  (`antifacts-weekly-ebm` vs `antifacts-weekly-update`) — đã ghi nhận minh bạch trong cả 2 tài
  liệu wiring + trong chính 2 SKILL.md, chưa hợp nhất/xóa.
- `audit_ebm_system.py` PASS toàn bộ sau cùng (50/50 agent, routine layer PASS, dashboard 0
  lỗi). pytest (venv `~/.ebm-venv`, `medical-ebm-automation/`): 1346 passed, 9 skipped, 0
  failed — không hồi quy so với v1.0.0.

## [1.0.0] - 2026-07-04

Phiên bản đầu tiên được đưa vào version control. Ghi nhận trạng thái đã trưởng thành của hệ
thống tại thời điểm này — bao gồm cả công việc trước đó (đội agent, 10 skill Đợt 1) và công
việc mới trong phiên này (11 skill Đợt 2+3, nối dây agent↔skill).

### Added — Đội agent (`.claude/agents/`)
- 48 agent chuyên trách: 19 lâm sàng + 28 nghiên cứu + 1 guardrail dùng chung (`tham-dinh-dau-ra`).
- 2 nhạc trưởng tự động: `dieu-phoi-lam-sang` (5 bước EBM tại điểm khám), `dieu-phoi-nghien-cuu`
  (cổng G0–G9 trọn đời đề tài).
- Tài liệu quản trị hệ thống: `_HIEN-PHAP-LIEM-CHINH.md`, `_BAN-DO-KET-NOI.md`,
  `_THU-VIEN-KY-NANG.md`, `_ROUTINE-AGENT-WIRING.md`, `_KIEM-DUYET-DOC-LAP.md`,
  `_CHUAN-CHAT-LUONG-MEDPALM.md`, và các chuẩn/hiến pháp liêm chính khác.

### Added — Kho skill khoa học Việt hóa (`sync/skills/`)
Chọn lọc & điều chỉnh từ **scientific-agent-skills** của K-Dense Inc. (148 skill gốc, MIT
license) cho bác sĩ EBM ngoại trú Việt Nam. Mỗi skill: Việt hóa mô tả kích hoạt, chèn khối
`EBM-VN-GUARD` (tiếng Việt bắt buộc, disclaimer, PMID/DOI, không PII, chỉ nguồn miễn phí), và
gỡ mọi phụ thuộc API trả phí (OpenRouter/parallel.ai/Perplexity/Nano Banana) khi có.

- **Đợt 1** (trước phiên này): `research-lookup`, `paper-lookup`, `citation-management`,
  `literature-review`, `clinical-decision-support`, `clinical-reports`, `treatment-plans`,
  `scientific-writing`, `statistical-analysis`, `peer-review`.
- **Đợt 2** (2026-07-04): `statistical-power`, `experimental-design`, `statsmodels`,
  `scikit-survival`, `scientific-critical-thinking`, `venue-templates`,
  `exploratory-data-analysis`, `database-lookup`. Mỗi skill đã qua khảo sát chồng lấn (đọc code
  agent + tool tự động thật) xác nhận **BỔ SUNG**, không trùng lặp; 3/8 script đã CHẠY THẬT và
  đối chiếu tay khớp 100%.
- **Đợt 3 / Nhóm B** (2026-07-04): `scholar-evaluation`, `hypothesis-generation`, `pyhealth`.
  Cùng quy trình khảo sát chồng lấn nghiêm ngặt; `scholar-evaluation` đã CHẠY THẬT
  (`calculate_scores.py`, đối chiếu tay khớp 100%).

### Added — Nối dây agent ↔ skill (2026-07-04)
Sau khi nhập, mỗi skill Đợt 2/3 được **nối dây thật** vào đúng agent/cổng sẽ dùng nó (không chỉ
nằm độc lập trong kho): `co-mau-nghien-cuu`, `thiet-ke-nghien-cuu`, `phan-tich-thong-ke`,
`tham-dinh-phe-binh`, `tham-dinh-grade-nnt`, `viet-ban-thao`, `nop-bai-phan-hoi`,
`quan-ly-du-lieu`, `tra-cuu-chung-cu`, `thu-thu-tai-lieu`, `binh-duyet`, `cau-hoi-nghien-cuu`,
`mo-hinh-tien-luong`, `ke-don-an-toan` (+ skill VN `ke-don-an-toan-benh-man`). Mỗi điểm nối
đánh dấu `(2026-07-04)` để dễ tra cứu, kèm giải thích RÕ khoảng trống agent hiện có mà skill lấp
vào (không lấn sang phần agent đã tự động hóa sẵn).

### Added — Công cụ quản trị (`tools/`)
- `audit_ebm_system.py` — audit tổng thể (đồng bộ agent↔Codex, guardrail, dashboard, EBM_MASTER...).
- `enforce_agent_guardrails.py` — bắt buộc mọi agent có nguồn/disclaimer/guardrail chuẩn.
- `sync_agents_to_codex.py` — sinh bản mirror TOML cho Codex CLI từ `.claude/agents/*.md`.

### Changed
- `_THU-VIEN-KY-NANG.md` (bảng skill↔agent↔khi dùng): mở rộng mục 2 (nghiên cứu) với 10 dòng
  mới cho Đợt 2+3.
- `sync/skills/README-EBM.md`: thêm mục "Đợt 2" và "Đợt 3", cập nhật tổng 10→18→21 skill.
- `sync/skills/_vietnamize.py`: mở rộng `DESCRIPTIONS` từ 10→21 mục (idempotent, chạy lại an
  toàn trên toàn bộ `sync/skills/`).

### Fixed
- Sự cố thao tác (không phải lỗi hệ thống): 1 lần workflow tự động dùng nhầm field kết quả của
  agent khảo sát làm tên thư mục đích, tạo 2 thư mục tên sai trong `sync/skills/` — đã phát
  hiện, xóa, làm lại đúng ngay trong phiên (xem `project-3-skill-nhom-b-da-noi-day` trong bộ
  nhớ phiên làm việc).

### Notes / Phạm vi phiên bản
- Repo này CHỈ theo dõi `.claude/agents/`, `sync/skills/`, `tools/`, `CLAUDE.md` — xem `.gitignore`.
- `.Codex/agents/` (mirror TOML cho Codex CLI) và `.codex/agents/` **KHÔNG** version-control —
  đây là bản sinh tự động, tái tạo bằng `python tools/sync_agents_to_codex.py`. Sau khi clone
  repo này, chạy lệnh đó để có lại mirror Codex.
- `sync/memory/` (bộ nhớ dự án/cá nhân) và `medical-ebm-automation/` (đã có git riêng, ~226
  test) nằm NGOÀI phạm vi phiên bản này.
- Trạng thái tại thời điểm gắn tag: `python tools/audit_ebm_system.py` → **PASS** (49/49 agent,
  disclaimer 49/49, 0 lỗi dashboard).
