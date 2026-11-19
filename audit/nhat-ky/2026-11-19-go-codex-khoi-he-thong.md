# 19/11/2026 — Gỡ Codex khỏi hệ thống (bác sĩ không còn dùng)

## Yêu cầu
Bác sĩ: «Codex nếu không cần thiết hãy loại bỏ ra cho tôi vì tôi cũng không còn dùng nữa». Khi được hỏi phạm vi gỡ trên
máy, bác sĩ chọn «Repo + tắt plugin (Khuyến nghị)», tức là GIỮ `~/.codex` (3,9 GB, có `auth.json` và phiên cũ) để bác sĩ
tự xoá khi chắc.

## Vì sao không cần nữa
Codex móc vào hệ ở năm chỗ. Không chỗ nào còn phục vụ việc lâm sàng hay nghiên cứu khi không ai dùng Codex:

1. **Bản sao agent `.Codex/agents/*.toml`** sinh từ `.claude/agents`. Chốt pre-commit chặn mọi commit khi bản sao lệch.
   Chính chốt này chặn commit ngày 19/11 ở worktree vì bản sao vắng, và báo «drift» ở cây chính khi một phiên khác sinh
   lại bản sao.
2. **Runtime skill `~/.codex/skills`**: nối symlink song song với `~/.claude/skills`.
3. **Kho plugin `~/.codex/plugins/cache`**: WorkerInventory và catalog router đọc ở đây. Catalog cũ đọc qua Codex nên còn
   số skill cũ, chưa có bản đã cắt tỉa (pubmed-search 31 thay vì 10, academic-research-skills 17 thay vì 4).
4. **Nhánh `run_orchestrator.py --execute`** gọi `codex exec`. CLI `codex` không cài trên máy này nên nhánh này vốn đã
   hỏng.
5. **Trọng tài Codex của hội đồng cổng** (`args.trong_tai: "codex"`) gửi trích đoạn hồ sơ đề tài ra dịch vụ OpenAI.

## Đã làm (repo gốc)
- Xoá `tools/sync_agents_to_codex.py`, `tools/check_claude_codex_sync_health.py` và hai bộ test của chúng. Thêm
  `tools/kiem_suc_khoe_agent.py`, giữ ĐÚNG phần kiểm NGUỒN: frontmatter, khối guardrail, disclaimer, agent cốt lõi, sổ hạ
  tầng.
- Chuyển sang công cụ mới, bỏ phần bản sao: pre-commit, `verify_claude_code_repo_alignment` (`agent_sync_health` →
  `agent_health`), `upgrade_verify`, `audit_ebm_system`, `dong_bo_tat_ca` (làn ④ «Agent»), `tu_sua_chua`,
  `clinical_production_loop`, `generate_agent`, `verify_mcp_live_sync`, `verify_plugin_orchestration`, `assess_agent_system`,
  `build_research_readiness_evidence`, `run_controlled_automation_cycle`, cùng hai workflow CI.
- Gỡ runtime `~/.codex/skills` khỏi `dong_bo_skill_claude_codex.py`, `link-skills.sh`/`.ps1` và `doi_chieu_ba_ben`. Gỡ phần
  chiếu skill sang Codex khỏi `dong_bo_plugin_claude_codex.py`. Hai tên tệp này GIỮ NGUYÊN vì hook SessionStart, lịch nền
  và nhiều công cụ gọi đúng tên đó; đổi tên là việc riêng nếu bác sĩ muốn.
- Orchestrator: xoá `CodexCliClient`. `LLMExecutor` và `IndependentClinicalGrader` nay đòi client được tiêm. Cờ `--execute`
  báo «đã gỡ» và thoát mã 4. Bỏ provider `codex` khỏi registry plugin và WorkerInventory.
- Catalog router `plugin-router-chatgpt` chỉ đọc cache Claude Code và bỏ plugin `codex@openai-codex`; đã dựng lại catalog.
- Workflow `hoi-dong-cong.js`: `trong_tai: "codex"` ném lỗi «đã gỡ». Tài liệu agent (`_HOI-DONG-CONG.md`,
  `trong-tai-tranh-bien.md`, `dieu-phoi-nghien-cuu.md`, README, `_PLUGIN-ROUTING-CONTRACT.md`, `_TU-SINH-AGENT.md`,
  `_KIEM-DUYET-DOC-LAP.md`, `_CROSSWALK-NGHIEN-CUU.md`) bỏ hai chế độ Codex.
- Bộ chốt hồi quy:
  - RÚT BH144 (bản sao `.codex/agents` của repo y khoa) và bỏ `_dung_lai_mirror_codex`.
  - BH70 và BH83 chỉ đòi runtime Claude.
  - BH91 chạy `kiem_suc_khoe_agent`.
  - BH140 bỏ mock `co_codex_tren_may`.
  - Chốt inventory không đòi kho Codex.
- Tài liệu: `CLAUDE.md` (§1, §1.1, §2, §2.1, §10) · `AGENTS.md` · `sync/SYNC-README.md` · `.gitignore` · câu thông báo
  trong `sync/hooks-sessionstart.json`.
- Sổ khai plugin: `codex@openai-codex` → `can_o_may: []`; bỏ trường `chieu_sang_codex` ở mọi mục.

## Trên máy Mac (phiên này)
- `"codex@openai-codex": false` trong cả `~/.claude/settings.json` lẫn `~/.claude/settings.local.json`, sao lưu
  `*.bak-go-codex-20261119`. Có hiệu lực từ phiên sau.
- Ghi lại mốc `tools/moc_chuan_plugin.json` (8 plugin, 239 skill). Dựng lại danh mục tra cứu công cụ.
- `~/.codex` để NGUYÊN theo lựa chọn của bác sĩ. Bản sao `.Codex/agents` cũ trong cây chính nằm ngoài git, bị bỏ qua, xoá
  tay khi chắc.

## Không làm được (cần bác sĩ)
- `.claude/hooks/session-start.sh` là hook được bảo vệ, agent không sửa. Bước ④ «sinh lại mirror Codex» tự bỏ qua vì công
  cụ không còn, nhưng các dòng chú thích và echo vẫn nhắc Codex.
- Máy Windows: tắt plugin, chạy `kiem_plugin_day_du.py --ghi-moc` và dựng lại danh mục trên máy đó. Việc chỉ-Windows không
  xếp ưu tiên.

## Kiểm
`pytest tools/` của repo gốc chạy trên worktree; chi tiết ở PR. `kiem_suc_khoe_agent`: 64/64 guardrail · 64/64
disclaimer. `verify_plugin_orchestration` PASS. Sổ khai mới đối chiếu kho thật: 0 đỏ, 0 vàng.
