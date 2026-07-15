#!/usr/bin/env python3
"""upgrade_verify.py — MỘT LỆNH kiểm tra + đồng bộ toàn hệ Agent/Hub EBM.

Chạy trọn dây chuyền liêm chính theo đúng thứ tự (17 bước tự động, thay cho gõ tay từng lệnh):
  1. enforce_agent_guardrails.py   — chèn/chuẩn hóa khối guardrail bắt buộc + disclaimer
  2. sync_agents_to_codex.py       — sinh lại bản Codex (.toml) từ nguồn .claude/agents
  3. sync_agents_to_codex.py --check — xác nhận nguồn Claude ↔ Codex khớp
  4. check_claude_codex_sync_health.py — cổng read-only guardrail/disclaimer/sync
  5. verify_agent_routing.py       — không agent mồ côi / không tham chiếu treo
  6. verify_research_gate_contracts.py — smoke-test action queue/resume/release contract
  7. verify_research_practical_readiness.py — synthetic real-data path đến G6 data-lock
  8. verify_controlled_research_automation.py — thẩm định/phản biện/PI-IRB-thống kê có kiểm soát
  9. EBM_MASTER/tools/sync_all.py  — gom dashboard, nạp sổ cái, sinh WebApp/Antifacts
 10. check_sync_all_idempotent.py  — chạy lại sync_all và xác nhận số thẻ hub không đổi
 11. assess_agent_system.py --deep — tự đánh giá 13 tiêu chí (A1–A7, S1–S6) bằng probe chạy thật
 12. clinical_runtime_readiness_report.py — báo cáo blocker production có phân loại
 13. verify_clinical_runtime_schema_hardening.py — chốt retraction/prompt-injection/conflict trong schema
 14. audit_ebm_system.py           — audit tổng thể (guardrail/dashboard/repo/EBM_MASTER)
 15. build_research_readiness_evidence.py --include-full-pytest — xuất bảng chứng cứ kỹ thuật trung thực
 16. run_orchestrator.py --validate — tự kiểm điều phối ⇄ registry (control plane, không lỗi cấu hình)
 17. orchestrator/tests/test_orchestrator.py — bộ test đơn vị của orchestrator (routing/plan/gate/guardrail)

Dùng:
  python tools/upgrade_verify.py           # chạy đủ, IN bảng tóm tắt + PASS/FAIL
  python tools/upgrade_verify.py --no-sync # không sinh lại Codex, vẫn kiểm/sync hub/audit

Mã thoát: 0 nếu MỌI bước PASS; 1 nếu có bước FAIL. Idempotent — chạy lại nhiều lần vô hại.
"Cần bác sĩ kiểm chứng." — công cụ chỉ kiểm cấu trúc/liêm chính, không thay thẩm định lâm sàng.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
VENV_PY = (
    Path.home() / ".ebm-venv" / "Scripts" / "python.exe"
    if os.name == "nt"
    else Path.home() / ".ebm-venv" / "bin" / "python"
)
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable


def run(label: str, args: list[str], pass_when_returncode_zero: bool = True) -> tuple[bool, str]:
    """Chạy một bước; trả (đạt?, dòng tóm tắt cuối). KHÔNG bịa kết quả — dựa returncode thật."""
    env = dict(
        os.environ,
        PYTHONUTF8="1",
        PYTHONIOENCODING="utf-8",
        PYTHONPYCACHEPREFIX=str(Path(tempfile.gettempdir()) / "ebm_pycache"),
    )
    try:
        proc = subprocess.run(
            [PY, *args], cwd=str(ROOT), env=env,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except Exception as exc:  # noqa: BLE001 — báo lỗi hạ tầng rõ, không nuốt
        return False, f"KHÔNG CHẠY ĐƯỢC ({exc})"
    ok = (proc.returncode == 0) if pass_when_returncode_zero else True
    # Lấy dòng cuối có nội dung làm tóm tắt
    lines = [ln.rstrip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
    tail = lines[-1] if lines else (proc.stderr.strip().splitlines() or [""])[-1]
    return ok, tail[:120]


def main() -> int:
    do_sync = "--no-sync" not in sys.argv
    print("=" * 70)
    print("  NÂNG CẤP & KIỂM TRA TOÀN HỆ AGENT EBM  (upgrade_verify)")
    print(f"  Python: {PY}")
    print("=" * 70)

    steps: list[tuple[str, list[str], bool]] = []
    if do_sync:
        steps += [
            ("1. Guardrail (enforce)", ["tools/enforce_agent_guardrails.py"], True),
            ("2. Đồng bộ Codex (sync)", ["tools/sync_agents_to_codex.py"], True),
        ]
    steps += [
        ("3. Kiểm đồng bộ (--check)", ["tools/sync_agents_to_codex.py", "--check"], True),
        ("4. Sync health read-only", ["tools/check_claude_codex_sync_health.py"], True),
        ("5. Định tuyến (routing)", ["tools/verify_agent_routing.py"], True),
        ("6. Hợp đồng gate nghiên cứu", ["tools/verify_research_gate_contracts.py"], True),
        ("7. Thực tiễn dữ liệu nghiên cứu", ["tools/verify_research_practical_readiness.py"], True),
        ("8. Tự động NC có kiểm soát", ["tools/verify_controlled_research_automation.py"], True),
        ("9. Đồng bộ Hub EBM_MASTER", ["EBM_MASTER/tools/sync_all.py"], True),
        ("10. Idempotency sync_all", ["tools/check_sync_all_idempotent.py"], True),
        ("11. Tự đánh giá 13 tiêu chí", ["tools/assess_agent_system.py", "--deep"], True),
        ("12. Readiness clinical runtime", ["tools/clinical_runtime_readiness_report.py"], True),
        ("13. Clinical schema hardening", ["tools/verify_clinical_runtime_schema_hardening.py"], True),
        ("14. Audit tổng thể", ["tools/audit_ebm_system.py"], True),
        ("15. Bảng chứng cứ thực tiễn", ["tools/build_research_readiness_evidence.py", "--include-full-pytest"], True),
        ("16. Orchestrator (validate)", ["tools/run_orchestrator.py", "--validate"], True),
        ("17. Orchestrator (23 test)", ["tools/orchestrator/tests/test_orchestrator.py"], True),
    ]

    results: list[tuple[str, bool, str]] = []
    for label, args, need_zero in steps:
        ok, tail = run(label, args, need_zero)
        results.append((label, ok, tail))
        mark = "✅" if ok else "❌"
        print(f"  {mark} {label:<28} {tail}")

    all_ok = all(ok for _, ok, _ in results)
    print("-" * 70)
    if all_ok:
        print("  KẾT: ✅ PASS — toàn hệ nhất quán, đã đồng bộ Claude ↔ Codex.")
    else:
        fails = [lbl for lbl, ok, _ in results if not ok]
        print(f"  KẾT: ❌ FAIL — bước lỗi: {', '.join(fails)}")
    print("  → Cần bác sĩ kiểm chứng (đây là kiểm cấu trúc, không thay thẩm định lâm sàng).")
    print("=" * 70)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
