# Changelog — Hệ Agent + Skill EBM

Định dạng theo [Keep a Changelog](https://keepachangelog.com/), phiên bản theo
[Semantic Versioning](https://semver.org/). Phạm vi CHANGELOG này là **hệ agent lâm
sàng/nghiên cứu (`.claude/agents/`) + kho skill khoa học Việt hóa (`sync/skills/`) + công cụ
quản trị (`tools/`)** — không bao gồm `medical-ebm-automation/` (dự án con có git riêng) hay
các thư mục dashboard/nội dung khác ở gốc "Claude AI".

## [Unreleased]

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
