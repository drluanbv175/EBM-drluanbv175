# Orchestrator EBM — control plane chạy được cho đội 50 agent

Vá đúng khoảng trống hệ tự đánh giá: *"nhánh LÂM SÀNG (dieu-phoi-lam-sang) là prose — chưa có
orchestrator chạy được"*. Đây là **control plane deterministic**: định tuyến → dựng plan → chạy
từng bước → dừng ở cổng bác sĩ → chốt guardrail — **chạy & kiểm được OFFLINE** (dry-run), có seam
cắm LLM để thực thi agent thật. Grounded vào registry `.claude/agents/*.md` THẬT (không hardcode).

## Sáu năng lực (mỗi năng lực = một module)

| # | Năng lực | Module | Điểm chính |
|---|---|---|---|
| 1 | **Điều phối agent** | `orchestrator.py` · `flows.py` · `agent_adapter.py` · `signals.py` | Flow lâm sàng 8 bước / nghiên cứu G0–G9; **mỗi agent trong bước mang điều kiện RIÊNG** (không chạy mù cả nhánh) |
| 2 | **Quản lý ngữ cảnh** | `context.py` | `Session` + checkpoint + **resume** (`~/.ebm-orchestrator/sessions/`) |
| 3 | **Định tuyến intent** | `intent.py` | `clinical_case` / `research_topic` / `single_task` / `unknown` (ma trận README) |
| 4 | **Tích hợp tri thức** | `knowledge.py` | Thứ bậc nguồn Cấp 0/0.5/1 + thuốc; thứ tự tra cứu §2bis; quy tắc PARTIAL |
| 5 | **Tích hợp công cụ** | `tools_registry.py` | 9 công cụ THẬT (clinical_calc grade/nnt, health_econ, run_g*, checkpoint, verify_dashboard…) |
| 6 | **Quản lý vòng đời** | `lifecycle.py` | `routed→planned→running→gate→guardrail→released/returned`; retry ≤3; **4 mã thoát** |

## Chạy (dry-run mặc định — không cần API)

```bash
python tools/run_orchestrator.py "Tôi có bệnh nhân nam 68 ĐTĐ2, eGFR 40, thêm thuốc gì?"
python tools/run_orchestrator.py "Đề tài hiệu quả metformin ở PCOS ngoại trú"
python tools/run_orchestrator.py "Đơn này an toàn không, thuốc có đánh nhau không?"
python tools/run_orchestrator.py --capabilities     # in 6 năng lực + số liệu
python tools/run_orchestrator.py --validate         # tự kiểm điều phối ⇄ registry (0 = sạch)
python tools/run_orchestrator.py --resume <id>      # khôi phục phiên
python tools/run_orchestrator.py --list             # liệt kê phiên
# thêm --json để in máy đọc
```

## Quan hệ với `medical-ebm-automation/tools/run_pipeline.py` (đọc kỹ — 2 hệ KHÁC NHAU)

Có **hai** thứ trông giống "orchestrator nghiên cứu" trong repo, KHÔNG liên thông với nhau
(xác nhận 2026-07-05 — không import/gọi lẫn nhau):

| | `tools/orchestrator/` (ở đây) | `medical-ebm-automation/tools/run_pipeline.py` |
|---|---|---|
| Vai trò | **Bản thiết kế/định tuyến** — xác định intent, dựng plan 28-agent theo G0–G9, dừng đúng cổng | **Orchestrator SẢN XUẤT thật** — chạy thật chuỗi G0–G10 |
| Thực thi | `DryRunExecutor` — chỉ in "sẽ gọi agent nào", KHÔNG chạy | Subprocess thật vào `run_g0_auto.py`…`run_g10_assemble.py`: PubMed thật (G0), công thức cỡ mẫu thật (G3), sinh checkpoint/DOCX thật |
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
python tools/orchestrator/tests/test_orchestrator.py    # 23 test, chạy offline
```

## Thực thi agent THẬT (seam LLM)

`agent_adapter.py` có 2 executor:
- **`DryRunExecutor`** (mặc định) — trả *kế hoạch* (agent sẽ làm gì + công cụ nào), không gọi LLM →
  plan/test/CI chạy được ngay, không cần API.
- **`LLMExecutor`** — seam cho thực thi thật qua wrapper **Codex/LLM** (cần API key + môi trường).
  CHƯA bật (trung thực về kỹ thuật `[CẦN MÔI TRƯỜNG HỖ TRỢ]`); cắm client vào là chạy agent thật,
  toàn bộ control plane (định tuyến/cổng/guardrail/ngữ cảnh) giữ nguyên.

## Bất biến (không nới an toàn/liêm chính)

Orchestrator chỉ **ĐỀ XUẤT** và **dừng** ở Cổng A/B (lâm sàng) + G2/G4/G9 (nghiên cứu); bước cuối
luôn qua guardrail `tham-dinh-dau-ra` (2 lớp R1–R14 + Q1–Q7). Mọi đầu ra kèm PMID/DOI, không PII,
kết **"Cần bác sĩ kiểm chứng."**
