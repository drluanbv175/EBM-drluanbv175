#!/usr/bin/env python3
"""upgrade_verify.py — MỘT LỆNH kiểm tra + đồng bộ toàn hệ Agent/Hub EBM.

Chạy trọn dây chuyền liêm chính theo đúng thứ tự (24 bước tự động, thay cho gõ tay từng lệnh):
  1. enforce_agent_guardrails.py   — chèn/chuẩn hóa khối guardrail bắt buộc + disclaimer
  2. sync_agents_to_codex.py       — sinh lại bản Codex (.toml) từ nguồn .claude/agents
  3. sync_agents_to_codex.py --check — xác nhận nguồn Claude ↔ Codex khớp
  4. check_claude_codex_sync_health.py — cổng read-only guardrail/disclaimer/sync
  5. verify_claude_code_repo_alignment.py — hợp đồng repo/Claude Code/Codex không trôi lệch
  6. verify_lessons_rubric_alignment.py — rubric QA ↔ taxonomy LESSONS không lệch mã lỗi
  7. verify_agent_routing.py       — không agent mồ côi / không tham chiếu treo
  8. verify_research_gate_contracts.py — smoke-test action queue/resume/release contract
  9. verify_research_practical_readiness.py — synthetic real-data path đến G6 data-lock
 10. verify_controlled_research_automation.py — thẩm định/phản biện/PI-IRB-thống kê có kiểm soát
 11. run_controlled_automation_cycle.py — chu trình tự động có kiểm soát, fail-closed/human-gated
 12. EBM_MASTER/tools/sync_all.py  — gom dashboard, nạp sổ cái, sinh WebApp/Antifacts
 13. check_sync_all_idempotent.py  — chạy lại sync_all và xác nhận số thẻ hub không đổi
 14. assess_agent_system.py --deep — tự đánh giá 13 tiêu chí (A1–A7, S1–S6) bằng probe chạy thật
 15. clinical_runtime_readiness_report.py — báo cáo blocker production có phân loại
 16. verify_personal_production_hardening.py — kiểm 7 miền hardening cá nhân trước dữ liệu thật
 17. verify_clinical_runtime_schema_hardening.py — chốt retraction/prompt-injection/conflict trong schema
 18. verify_clinical_evidence_update_pipeline.py — dashboard→library→derivatives + hợp đồng sync hub
 19. verify_clinical_evidence_agent_standards.py — chuẩn agent cập nhật chứng cứ lâm sàng
 20. verify_clinical_production_control_plane.py — tự sửa/tự sinh agent/điều phối EBM lâm sàng
 21. audit_ebm_system.py           — audit tổng thể (guardrail/dashboard/repo/EBM_MASTER)
 22. build_research_readiness_evidence.py --include-full-pytest — xuất bảng chứng cứ kỹ thuật trung thực
 23. run_orchestrator.py --validate — tự kiểm điều phối ⇄ registry (control plane, không lỗi cấu hình)
 24. orchestrator/tests/test_orchestrator.py — bộ test đơn vị của orchestrator (routing/plan/gate/guardrail)

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


def _configure_utf8_stdio() -> None:
    """Keep the one-shot verifier printable on Windows legacy consoles."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


_configure_utf8_stdio()


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
        ("5. Repo/Claude Code alignment", ["tools/verify_claude_code_repo_alignment.py"], True),
        ("6. Rubric ↔ lessons taxonomy", ["tools/verify_lessons_rubric_alignment.py"], True),
        ("7. Định tuyến (routing)", ["tools/verify_agent_routing.py"], True),
        ("8. Hợp đồng gate nghiên cứu", ["tools/verify_research_gate_contracts.py"], True),
        ("9. Thực tiễn dữ liệu nghiên cứu", ["tools/verify_research_practical_readiness.py"], True),
        ("10. Tự động NC có kiểm soát", ["tools/verify_controlled_research_automation.py"], True),
        ("11. Controlled automation cycle", ["tools/run_controlled_automation_cycle.py"], True),
        ("12. Đồng bộ Hub EBM_MASTER", ["EBM_MASTER/tools/sync_all.py"], True),
        ("13. Idempotency sync_all", ["tools/check_sync_all_idempotent.py"], True),
        ("14. Tự đánh giá 13 tiêu chí", ["tools/assess_agent_system.py", "--deep"], True),
        ("15. Readiness clinical runtime", ["tools/clinical_runtime_readiness_report.py"], True),
        ("16. Hardening cá nhân 7 miền", ["medical-ebm-automation/tools/verify_personal_production_hardening.py"], True),
        ("17. Clinical schema hardening", ["tools/verify_clinical_runtime_schema_hardening.py"], True),
        ("18. Pipeline cập nhật chứng cứ LS", ["tools/verify_clinical_evidence_update_pipeline.py"], True),
        (
            "19. Clinical evidence agent standards",
            ["medical-ebm-automation/tools/verify_clinical_evidence_agent_standards.py"],
            True,
        ),
        (
            "20. Clinical production control-plane",
            ["medical-ebm-automation/tools/verify_clinical_production_control_plane.py"],
            True,
        ),
        ("21. Audit tổng thể", ["tools/audit_ebm_system.py"], True),
        ("22. Bảng chứng cứ thực tiễn", ["tools/build_research_readiness_evidence.py", "--include-full-pytest"], True),
        ("23. Orchestrator (validate)", ["tools/run_orchestrator.py", "--validate"], True),
        ("24. Orchestrator (23 test)", ["tools/orchestrator/tests/test_orchestrator.py"], True),
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
