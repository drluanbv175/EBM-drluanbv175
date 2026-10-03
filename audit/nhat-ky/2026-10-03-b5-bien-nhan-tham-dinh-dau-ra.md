# 03/10/2026 — B5: sổ QA sống `observability/APPRAISALS.jsonl` không có dòng nào sau 07/2026

**Số đo (kiểm toàn diện 02/10).** Sổ có 17 dòng: 11 dòng tháng 07/2026, 6 dòng có `ts` RỖNG, không dòng nào của tháng 8–10. Trong 89
phiên, `tham-dinh-dau-ra` được gọi 2 lần.

**Nguyên nhân (đọc mã, đo lại 03/10).**
1. Agent `tham-dinh-dau-ra` chỉ chạy `tools/eval/run_eval.py`, nơi ghi sổ, ở chế độ AUTO-DISPATCH (§8 — vòng tự sửa khi TRẢ-VỀ-SỬA
   trong CHAY-TOAN-BO). Một lần chấm bình thường không để lại dấu vết nào.
2. `tools/orchestrator/guardrail_bridge.emit_appraisal()` ghi `"ts": at or ""`; người gọi thật (orchestrator-live) không truyền `at`,
   nên 6 dòng không có thời điểm. `run_eval.emit_appraisal` thì luôn ghi giờ.

**Vá (không đổi luật chấm).**
- `tham-dinh-dau-ra.md` thêm §6bis «GHI BIÊN NHẬN — bắt buộc MỖI lần chấm»:
  1. Ghi gói vào tệp tạm ngoài repo.
  2. Chạy `run_eval.py --json --source tham-dinh-dau-ra`.
  3. Chép `appraisal.id` vào dòng **BIÊN NHẬN MÁY** của mẫu §4; phán định tự động khác phán định agent thì ghi cả hai.
  4. Không chạy được thì ghi lý do, KHÔNG bịa mã (`clinical_checkpoint` đối chiếu mã với sổ).
  §6 (tiêu chí hoàn thành) đòi có dòng này.
- `guardrail_bridge.emit_appraisal`: `at` mặc định là thời điểm ghi (UTC). Test vẫn truyền `at` cố định để tái lặp mã.

**Kiểm.**
- 3 test; đột biến bỏ mặc định thời gian ⇒ đỏ.
- Thử thật: `run_eval.py` trên một gói mẫu tổng hợp (không PII) ghi được dòng `APPRAISAL-20261003T080840-30e64f` có `ts`. Lượt thử
  chạy trong worktree nên ghi vào tệp ngoài git của worktree, đã dọn. Sổ sống nằm ở cây chính (OneDrive, ngoài git).
- `enforce_agent_guardrails` 0 tệp đổi; mirror Codex PASS; `orchestrator/tests` xanh.

**Còn lại.** Bản agent in-repo của repo y khoa (`medical-ebm-automation/.claude/agents/tham-dinh-dau-ra.md` + toml `.codex` + manifest)
đồng bộ SAU khi PR y khoa #62 gộp, vì #62 đang sinh lại đúng tệp toml đó. Trong lúc chờ, giác quan PM-15 (PR #97) báo lệch.
