# Orchestrator EBM — control plane chạy được cho đội 50 agent + plugin worker

Vá đúng khoảng trống hệ tự đánh giá: *"nhánh LÂM SÀNG (dieu-phoi-lam-sang) là prose — chưa có
orchestrator chạy được"*. Đây là **control plane deterministic**: định tuyến → dựng plan → chạy
từng bước → dừng ở cổng bác sĩ → chốt guardrail — **chạy & kiểm được OFFLINE** (dry-run) hoặc
thực thi agent thật qua Codex CLI chỉ-đọc bằng `--execute`. Grounded vào registry `.claude/agents/*.md` THẬT và registry quyền
sở hữu plugin (một owner/capability; plugin chỉ là worker).

## Tám năng lực (mỗi năng lực = một module)

| # | Năng lực | Module | Điểm chính |
|---|---|---|---|
| 1 | **Điều phối agent** | `orchestrator.py` · `flows.py` · `agent_adapter.py` · `signals.py` | Flow lâm sàng 8 bước / nghiên cứu G0–G10; **mỗi agent trong bước mang điều kiện RIÊNG** (không chạy mù cả nhánh) |
| 2 | **Quản lý ngữ cảnh** | `context.py` | `Session` + checkpoint + **resume** + artifact revision (`~/.ebm-orchestrator/sessions/`) |
| 3 | **Định tuyến intent** | `intent.py` | `clinical_case` / `research_topic` / `single_task` / `unknown` (ma trận README) |
| 4 | **Tích hợp tri thức** | `knowledge.py` | Thứ bậc nguồn Cấp 0/0.5/1 + thuốc; thứ tự tra cứu §2bis; quy tắc PARTIAL |
| 5 | **Tích hợp công cụ** | `tools_registry.py` · `evidence_prefetch.py` | 13 công cụ THẬT; biên lai PubMed/Europe PMC/Crossref + chuỗi A12 kiểm rút bài; `validate()` fail-closed nếu script thiếu |
| 6 | **Quản lý vòng đời** | `lifecycle.py` | `routed→planned→running→gate→guardrail→released/returned`; retry ≤3; **4 mã thoát** |
| 7 | **Điều phối plugin** | `plugin_ownership.py` · `plugin_ownership_registry.json` | Một owner nội bộ/capability; allowlist worker theo stage; plugin không được mở cổng người |
| 8 | **Vòng khép kín** | `worker_inventory.py` · `guardrail_bridge.py` | Artifact sống có revision; re-route tối đa 3 vòng; rule-based R + critic Q1–Q7 ở phiên Codex tách biệt |

## Chạy (dry-run mặc định — không cần API)

```bash
python tools/run_orchestrator.py "Tôi có bệnh nhân nam 68 ĐTĐ2, eGFR 40, thêm thuốc gì?"
python tools/run_orchestrator.py "Đề tài hiệu quả metformin ở PCOS ngoại trú"
python tools/run_orchestrator.py "Đơn này an toàn không, thuốc có đánh nhau không?"
python tools/run_orchestrator.py --capabilities     # in 8 năng lực + số liệu
python tools/run_orchestrator.py --plugins          # tóm tắt registry plugin
python tools/run_orchestrator.py --resolve-capability research_lifecycle --json
python tools/run_orchestrator.py --validate         # tự kiểm điều phối ⇄ registry (0 = sạch)
python tools/run_orchestrator.py --resume <id>      # khôi phục phiên
python tools/run_orchestrator.py --list             # liệt kê phiên
python tools/run_orchestrator.py "<yêu cầu>" --execute --output /tmp/ebm-draft.md
# thêm --json để in máy đọc
```

## Quan hệ với `medical-ebm-automation/tools/run_pipeline.py` (đọc kỹ — 2 hệ KHÁC NHAU)

Có **hai** thứ trông giống "orchestrator nghiên cứu" trong repo, KHÔNG liên thông với nhau
(xác nhận 2026-07-05 — không import/gọi lẫn nhau):

| | `tools/orchestrator/` (ở đây) | `medical-ebm-automation/tools/run_pipeline.py` |
|---|---|---|
| Vai trò | Control-plane agent/plugin: dry-run hoặc sinh/tự sửa bản nháp qua Codex chỉ-đọc; không thay pipeline artifact | **Orchestrator SẢN XUẤT thật** — chạy chuỗi G0–G10 |
| Thực thi | `DryRunExecutor` mặc định; `LLMExecutor` khi `--execute`; không tự chạy tool có dữ liệu thật | Subprocess thật vào `run_g0_auto.py`…`run_g10_assemble.py`: PubMed thật (G0), công thức cỡ mẫu thật (G3), sinh checkpoint/DOCX thật |
| Tự sửa/chờ cổng | Đánh dấu gate_pending rồi dừng (tĩnh) | **Freshness guard** (phát hiện cổng cũ/lệch) + **retry có trần** + đọc `study_meta.json` (tham số bác sĩ PIN) + 4 mã thoát `gate_contract.py` (0 OK · 1 lỗi tạm-thời retry · 2 BLOCKED chờ input thật, KHÔNG retry · 3 vi phạm liêm chính) |
| Dùng khi nào | Xem trước NHANH agent nào sẽ chạy, nhánh nào áp dụng, cổng nào sẽ chặn — trước khi bắt tay làm thật | **Chạy đề tài thật**: `python tools/run_pipeline.py --study "<MÃ>" --topic "<chủ đề>"` |

`run_orchestrator.py` tự in dòng trỏ sang lệnh thật ở cuối mỗi lần intent là `research_topic`.
**Đừng tưởng lầm plan dry-run ở đây là đã "chạy nghiên cứu"** — nó chỉ là bản xem trước.

**Mã thoát** = hợp đồng DỪNG: `0` released · `1` returned-for-fix · `2` gate_pending (dừng chờ bác sĩ)
· `3` blocked · `4` unknown/cần làm rõ.

## Tín hiệu ngữ cảnh — plan phản ánh ĐÚNG ca (`signals.py`)

Lỗ hổng đã vá (2026-07-05): trước đây plan CHẠY MÙ mọi nhánh (đọc CLS, chẩn đoán, chuyên biệt,
PROM/mô hình/kinh tế/định tính…) bất kể request có đúng bối cảnh không. Nay mỗi `StepAgent` trong
`flows.py` mang một `condition` riêng, tra qua `Signals.detect(request)` — khớp từ khóa **minh
bạch** (không phải NLU/hộp đen), agent không khớp tín hiệu → `status: "skipped"` + lý do cụ thể
(không phải bị lặng lẽ xóa khỏi trace). Ví dụ: câu hỏi không nhắc xét nghiệm → `dien-giai-can-lam-sang`
skip; đề tài nhắc "thang đo/COSMIN" → `cong-cu-do-luong` chạy còn `kinh-te-y-te` skip. 14 tín hiệu
hiện có: `has_labs · is_diagnostic · needs_risk_score · anticoag · chronic · prevention ·
pain_chronic_branch · palliative_branch · mental_branch · qualitative · prom_tool ·
prognostic_model · economic · international_journal`.

## Kiểm thử

```bash
python tools/orchestrator/tests/test_orchestrator.py
python -m unittest discover -s tools/orchestrator/tests # toàn bộ kiểm thử offline + fake-client;
                                                        # canary Codex thật chạy riêng với --execute
```

## Quyền sở hữu plugin

Nguồn sự thật là `plugin_ownership_registry.json`; doctrine dùng chung cho Claude Code/Codex nằm tại
`.claude/agents/_PLUGIN-ROUTING-CONTRACT.md`. `/ars-full` bị hạ thành `stage_worker`, không thay
`dieu-phoi-nghien-cuu`; các skill lâm sàng cũng chỉ làm worker dưới `dieu-phoi-lam-sang`. Mỗi phiên
ghi checkpoint `plugin_routing` gồm capability, owner, worker được phép và cổng. Worker ngoài
allowlist/capability lạ bị báo chặn, không fallback sang pipeline plugin tự trị.

Từ 01/09/2026, mỗi agent trong flow còn được phân giải capability hẹp của chính nó. Ví dụ,
`dieu-phoi-nghien-cuu` vẫn sở hữu đề tài; tới G1, `thiet-ke-nghien-cuu` chọn ARS nền và chỉ gọi
đúng planner AIPOCH khi cue chuyên biệt khớp. `worker_inventory.py` kiểm `SKILL.md` trong đúng
provider; worker thiếu không làm đổi owner mà chuyển trạng thái `LOCAL_FALLBACK`.

Kiểm cứng:

```bash
python tools/verify_plugin_orchestration.py
```

## Thực thi agent thật

`agent_adapter.py` có 2 executor:
- **`DryRunExecutor`** (mặc định) — trả *kế hoạch* (agent sẽ làm gì + công cụ nào), không gọi LLM →
  plan/test/CI chạy được ngay, không cần API.
- **`LLMExecutor`** — đã nối `CodexCliClient`; mỗi agent chạy phiên `codex exec --ephemeral`
  trong thư mục tạm + sandbox `read-only`, không nhận environment bí mật, nhận artifact revision
  hiện tại và trả JSON theo schema.
- **Biên lai công cụ** — trước agent `kiem-chung-trich-dan`, parent chỉ lấy PMID/DOI rõ ràng
  rồi tra PubMed/Europe PMC/Crossref với retry và gọi đúng chuỗi A12 Retraction Watch→NCBI→Europe PMC;
  metadata/cờ rút bài và lỗi nguồn được gắn provenance vào
  prompt. Không gửi toàn bộ ca lâm sàng và không biến việc phân giải metadata thành phê duyệt.
- **Critic độc lập ngữ cảnh** — `IndependentClinicalGrader` chạy một phiên Codex khác, chỉ nhận
  bản nháp và rubric Q1–Q7. Q2/Q5 đỏ leo thang ngay; output sai schema/lỗi runtime đóng cổng.
- **Vòng tự sửa thật** — agent được re-route nhận mã lỗi + bản nháp hiện tại, sinh revision mới;
  cổng đọc lại revision mới ở mỗi vòng. Tối đa 3 vòng, sau đó chuyển bác sĩ.

Giới hạn: critic vẫn cùng họ mô hình và không phải hội đồng bác sĩ; `--execute` không tự ký cổng,
không chạy dữ liệu thật và không thay `medical-ebm-automation/tools/run_pipeline.py`.

## Bất biến (không nới an toàn/liêm chính)

Orchestrator chỉ **ĐỀ XUẤT** và **dừng** ở Cổng A/B (lâm sàng) + G2/G4/G5/G8/G9/G10 (nghiên cứu); bước cuối
luôn qua guardrail `tham-dinh-dau-ra` (2 lớp R1–R14 + Q1–Q7). Mọi đầu ra kèm PMID/DOI, không PII,
kết **"Cần bác sĩ kiểm chứng."**
