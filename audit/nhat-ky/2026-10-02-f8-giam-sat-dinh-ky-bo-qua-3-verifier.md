# 02/10/2026 — Workflow `giam-sat-dinh-ky` bỏ qua 3 verifier MỌI lượt mà vẫn xanh; issue đỏ cũ không bao giờ đóng; cron trúng đỉnh tải (F8)

**Triệu chứng (đo 02/10).** `.github/workflows/giam-sat-dinh-ky.yml` chỉ lấy repo anh em `medical-ebm-automation` khi có secret `SIBLING_REPO_TOKEN` — chưa ai đặt — nên 3 verifier cần repo đó
(`verify_research_gate_contracts`, `verify_controlled_research_automation`, `verify_lessons_rubric_alignment`) bị BỎ QUA mọi lượt, lượt vẫn xanh («chạy được ngay ngày đầu» — đúng, nhưng chỉ 11/14).
Repo anh em lại CÔNG KHAI (CLAUDE.md §2.1) nên không cần token. Issue «🔴 Giám sát định kỳ đỏ — 21/09» (#20) mở từ lượt đỏ 21/09 và không bao giờ được đóng dù lượt 28/09 và 01/10 đã xanh
(đèn đỏ cũ làm giảm giá trị đèn đỏ mới). Ba lượt `schedule` gần nhất chạy lúc 03:56 · 04:19 · 05:23 UTC so với 00:00 UTC khai báo: trễ 3,9–5,4 giờ (cron trúng đỉnh tải).

**Vá.**
- Lấy repo anh em bằng `github.token` (lối lùi) hoặc `SIBLING_REPO_TOKEN` (khi repo chuyển riêng tư); `continue-on-error: true` + bước cảnh báo `::warning::` khi không lấy được — «bỏ qua» không còn im lặng.
- 11 verifier chuyển lên TRƯỚC bước lấy repo anh em để vẫn đo trên bản sao trần (đúng nhãn của bước).
- Bước «Tự đóng issue giám sát cũ khi lượt này xanh» (`if: success()`; quyền `issues: write` đã có). Nội dung issue chỉ chứa đường dẫn nhật ký, không dữ liệu y khoa/PII (repo công khai).
- Cron lệch đỉnh tải: `43 0 * * 1` (tuần) và `17 1 1 * *` (tháng).

**Kiểm.** Phép thử mô phỏng runner trần: repo gốc + repo anh em lồng, `python3 -S` (không site-packages): cả 3 verifier thoát mã 0; bước gương `.codex` + cổng sức khoẻ vẫn PASS khi có repo anh em
(chạy bằng Python 3.14 của máy này; runner dùng 3.11 — repo cấm cú pháp PEP 701 nên không kỳ vọng khác). 8 ca pytest `tools/test_giam_sat_dinh_ky_workflow_20261002.py` kiểm bằng văn bản (không cần PyYAML).
**Kiểm đột biến:** 9 phép (lại chỉ chạy khi có secret · bỏ continue-on-error · bỏ `::warning` · đổi lời cảnh báo · cron về 00:00 · đóng issue khi ĐỎ · bỏ ghim SHA · bỏ lối dùng secret · workflow gốc trên master) — 9/9 bị bắt;
một phép (bỏ ghim SHA) ban đầu LỌT vì regex của chính bài test chỉ khớp `uses:` mà không khớp `- uses:` ⇒ sửa regex rồi đo lại mới bắt. Phục hồi `cmp` đúng.

**Chưa kiểm được ở máy này:** hành vi thật trên GitHub (hàng đợi `schedule`, quyền `issues: write` của token mặc định, `github.token` đọc được repo anh em công khai) — cần một lượt chạy thật sau khi merge.
Bác sĩ không phải làm gì thêm; chỉ merge PR rồi đọc kết quả lượt `workflow_dispatch`/lịch kế tiếp.
