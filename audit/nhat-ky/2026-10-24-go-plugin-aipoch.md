# 24/10/2026 — Gỡ plugin aipoch-medical-research khỏi hệ (bác sĩ quyết)

**Bối cảnh.** Đài/hòm việc 🔴 «Kho plugin THIẾU — aipoch-medical-research BIẾN MẤT khỏi kho (mốc có, nay không)»: marketplace
còn khai nhưng plugin không còn cài (không có bản ghi trong `installed_plugins.json`, không có cache). Bác sĩ hỏi «plugin này có
còn ý nghĩa gì… lí do gì cài lại», rồi quyết «Gỡ aipoch».

**Đo trước khi quyết (24/10/2026).** 0 lượt gọi Skill aipoch trong mọi bản ghi phiên trên Mac. Vai duy nhất theo hợp đồng: 8
planner đặc thù ở G0–G1 (Mendelian randomization · FAERS · đơn tế bào · đa omics · tái định vị thuốc · QTL · độc chất mạng ·
biomarker tiên lượng), worker `specialty_planning_worker` dưới `thiet-ke-nghien-cuu` — không khớp đề tài thật C1a. 605 skill
chiếm ngân sách danh sách skill mỗi phiên.

**Gỡ.**
- `sync/plugin-manifest.json`: GIỮ mục, `can_o_may: []` + lý do «GỠ CÓ CHỦ Ý» — đúng mẫu 8 plugin medsci trùng (để công cụ
  tách «thiếu vì cố ý» khỏi «thiếu vì trôi dạt»).
- `tools/orchestrator/plugin_ownership_registry.json`: bỏ provider + 8 worker; `worker_inventory.py` bỏ đường dẫn.
- `tools/cap_nhat_plugin_tay.py`: bỏ khối aipoch (để nó KHÔNG tự clone lại kho 808 MB).
- `plugin-router-chatgpt`: bỏ khỏi `PLUGIN_IDS`/`PLUGIN_CUES`, dựng lại catalog — mất đúng 604 skill của aipoch, plugin khác
  không đổi (8 plugin · 224 skill).
- Skill `sync/skills/dieu-phoi-aipoch` gỡ; `dong_goi_skill_tai_khoan.py` bỏ mục; `viec-hay-lam.json` bỏ 8 việc gọi lệnh aipoch;
  danh mục tra cứu công cụ sinh lại.
- Doctrine: `dieu-phoi-nghien-cuu.md` + `_PLUGIN-ROUTING-CONTRACT.md` (PR cặp ở repo y khoa), CLAUDE.md §1.1.
- Test viết lại theo hành vi mới (yêu cầu MR không còn worker aipoch; catalog không còn plugin đó) — không xoá phép kiểm.

**Không làm.** Không sửa hồ sơ lịch sử (`audit/`, nhật ký đóng băng), không sửa hook được bảo vệ `.claude/hooks/`, không xoá
thư mục clone `~/Documents/GitHub/medical-research-skills` (bác sĩ tự quyết). Sau khi gộp: `--ghi-moc` lại ảnh chụp kho plugin
trên MỖI máy (thay đổi có chủ ý) và gỡ đăng ký marketplace aipoch.

**Kiểm.** `verify_agent_routing.py` không tham chiếu treo; `verify_plugin_orchestration.py` PASS; guardrail 64 agent; mirror
Codex 64 TOML; 299 test orchestrator/plugin/đóng gói/định tuyến xanh.
