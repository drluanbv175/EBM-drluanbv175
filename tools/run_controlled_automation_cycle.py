#!/usr/bin/env python3
"""Chạy một chu trình tự động có kiểm soát cho hệ EBM.

Tool này gom các verifier quan trọng thành một vòng vận hành fail-closed:
- lỗi kỹ thuật/đồng bộ/guardrail -> FAIL_CLOSED;
- kiểm kỹ thuật PASS nhưng còn phê duyệt thật -> CONTROLLED_READY_WITH_HUMAN_GATES;
- không có blocker kỹ thuật và không có human gate -> CONTROLLED_READY.

Không dùng dữ liệu thật, không tự duyệt IRB/PI/thống kê/phản biện, không bật
clinical production. Đây là control-plane để chứng minh hệ biết tự chạy và tự
dừng đúng chỗ.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "reports" / "CONTROLLED_AUTOMATION_CYCLE.json"
DEFAULT_MD = ROOT / "reports" / "CONTROLLED_AUTOMATION_CYCLE.md"
DISCLAIMER = (
    "Cần bác sĩ kiểm chứng. Đây là control-plane kỹ thuật/offline; không thay "
    "IRB, PI, thống kê viên, phản biện độc lập, bảo mật triển khai hoặc thẩm định lâm sàng."
)


@dataclass(frozen=True)
class ControlStep:
    step_id: str
    phase: str
    command: list[str]
    proves: str
    limitation: str
    blocking: bool = True
    human_gate: bool = False
    human_action: str = ""


@dataclass(frozen=True)
class StepResult:
    step_id: str
    phase: str
    command: str
    status: str
    returncode: int
    evidence_tail: str
    proves: str
    limitation: str
    blocking: bool
    human_gate: bool
    human_action: str


def control_steps() -> list[ControlStep]:
    return [
        ControlStep(
            step_id="agent_sync",
            phase="sync",
            command=["tools/check_claude_codex_sync_health.py"],
            proves="Agent nguồn Claude Code và Codex mirror đồng bộ, đủ guardrail/disclaimer.",
            limitation="Không đánh giá chất lượng từng câu trả lời.",
        ),
        ControlStep(
            step_id="repo_alignment",
            phase="sync",
            command=["tools/verify_claude_code_repo_alignment.py"],
            proves="AGENTS.md/CLAUDE.md/clinical_runtime và mirror agent không trôi lệch doctrine.",
            limitation="Không thay review bảo mật hoặc thiết kế thực địa.",
        ),
        ControlStep(
            step_id="agent_routing",
            phase="orchestration",
            command=["tools/verify_agent_routing.py"],
            proves="Nhạc trưởng không có tham chiếu treo và tiêu đề agent còn khớp thực tế.",
            limitation="Định tuyến deterministic chưa phải LLM-agent thực thi thật.",
        ),
        ControlStep(
            step_id="research_gate_contract",
            phase="research",
            command=["tools/verify_research_gate_contracts.py"],
            proves="Action queue/resume/release contract chặn G2/G6/G9 khi thiếu bằng chứng thật.",
            limitation="Fixture synthetic; phê duyệt thật vẫn do IRB/PI/người có thẩm quyền.",
            human_gate=True,
            human_action="Cung cấp IRB/SAP/data-lock/liêm chính thật trước khi vượt cổng nghiên cứu tương ứng.",
        ),
        ControlStep(
            step_id="real_data_path",
            phase="research",
            command=["tools/verify_research_practical_readiness.py"],
            proves="Luồng de-id/pseudonymization/cleaning/data-lock synthetic chạy được và không sửa raw.",
            limitation="Dữ liệu thật cần DMP, IRB, phân quyền và kiểm định tại đơn vị.",
            human_gate=True,
            human_action="PI/data manager xác nhận DMP, nguồn dữ liệu thật, data-lock và quyền xử lý dữ liệu.",
        ),
        ControlStep(
            step_id="controlled_reviews_stats",
            phase="research",
            command=["tools/verify_controlled_research_automation.py"],
            proves="Automation không tự duyệt; phản biện/PI/IRB/thống kê và CI/effect size được kiểm soát.",
            limitation="Không thay phản biện độc lập, thống kê viên hoặc IRB thật.",
            human_gate=True,
            human_action="Bố trí PI, IRB, thống kê viên và phản biện độc lập ký/nhận xét trên hồ sơ thật.",
        ),
        ControlStep(
            step_id="clinical_schema_hardening",
            phase="clinical",
            command=["tools/verify_clinical_runtime_schema_hardening.py"],
            proves="Clinical V2 schema chặn retraction, prompt injection và conflicting evidence ở tầng governance.",
            limitation="Schema tĩnh; chưa chứng minh runtime production với bệnh nhân thật.",
            human_gate=True,
            human_action="Chỉ bật clinical runtime thật sau runtime integration, UAT, security/legal/clinical sign-off.",
        ),
        ControlStep(
            step_id="clinical_runtime_readiness",
            phase="clinical",
            command=["tools/clinical_runtime_readiness_report.py"],
            proves="Clinical runtime/chronic-care blocker được phân loại thành repo-actionable và cần duyệt thật.",
            limitation="Tool báo cáo blocker và vẫn giữ production blocked khi còn phê duyệt/thử nghiệm thật.",
            blocking=False,
            human_gate=True,
            human_action="Đóng các blocker cần bác sĩ/pháp lý/bảo mật/UAT trước khi gọi production-ready.",
        ),
        ControlStep(
            step_id="personal_production_hardening",
            phase="production_hardening",
            command=["medical-ebm-automation/tools/verify_personal_production_hardening.py"],
            proves="7 miền hardening cá nhân được kiểm: blocker production, actor thật, dữ liệu thật, SOP, UAT, backup/rollback và tách mode.",
            limitation="Không thay evidence package, signoff, UAT, bảo mật hoặc go-live thật.",
            human_gate=True,
            human_action="Hoàn tất evidence package, UAT, backup/restore drill, actor key và signoff trước khi dùng dữ liệu bệnh nhân thật.",
        ),
    ]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONPYCACHEPREFIX", str(Path(tempfile.gettempdir()) / "ebm_pycache"))
    return env


def _tail(stdout: str, stderr: str, max_lines: int = 3) -> str:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    return " / ".join((lines or [""])[-max_lines:])[:600]


def _display(command: Sequence[str]) -> str:
    return " ".join(command)


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _default_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(ROOT),
        env=_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_step(step: ControlStep, *, python: str, runner: Runner = _default_runner) -> StepResult:
    command = [python, *step.command] if step.command[0].endswith(".py") else list(step.command)
    proc = runner(command)
    ok = proc.returncode == 0
    if ok and step.human_gate:
        status = "CONTROLLED_HUMAN_GATE"
    elif ok:
        status = "PASS"
    elif step.blocking:
        status = "FAIL"
    else:
        status = "WARN"
    return StepResult(
        step_id=step.step_id,
        phase=step.phase,
        command=_display(command),
        status=status,
        returncode=proc.returncode,
        evidence_tail=_tail(proc.stdout or "", proc.stderr or ""),
        proves=step.proves,
        limitation=step.limitation,
        blocking=step.blocking,
        human_gate=step.human_gate,
        human_action=step.human_action,
    )


def summarize(results: list[StepResult]) -> dict:
    blocking_failures = [row for row in results if row.blocking and row.status == "FAIL"]
    human_gates = [row for row in results if row.human_gate and row.status != "FAIL"]
    if blocking_failures:
        overall = "FAIL_CLOSED"
        automation_allowed = False
    elif human_gates:
        overall = "CONTROLLED_READY_WITH_HUMAN_GATES"
        automation_allowed = True
    else:
        overall = "CONTROLLED_READY"
        automation_allowed = True
    return {
        "overall_status": overall,
        "automation_allowed_for_offline_controlled_tasks": automation_allowed,
        "clinical_production_allowed": False,
        "blocking_failure_count": len(blocking_failures),
        "human_gate_count": len(human_gates),
        "next_required_human_actions": [
            {"step_id": row.step_id, "action": row.human_action}
            for row in human_gates
            if row.human_action
        ],
    }


def run_cycle(*, python: str | None = None, runner: Runner = _default_runner) -> dict:
    py = python or sys.executable
    results = [run_step(step, python=py, runner=runner) for step in control_steps()]
    summary = summarize(results)
    return {
        "kind": "controlled_automation_cycle",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        **summary,
        "rows": [asdict(row) for row in results],
        "disclaimer": DISCLAIMER,
    }


def markdown_report(report: dict) -> str:
    lines = [
        "# Controlled Automation Cycle",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Overall status: `{report['overall_status']}`",
        f"- Blocking failures: `{report['blocking_failure_count']}`",
        f"- Human gates: `{report['human_gate_count']}`",
        f"- Clinical production allowed: `{report['clinical_production_allowed']}`",
        "",
        "| Step | Phase | Status | Evidence tail | Proves | Limitation |",
        "|---|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {step} | {phase} | {status} | {tail} | {proves} | {limit} |".format(
                step=str(row["step_id"]).replace("|", "\\|"),
                phase=str(row["phase"]).replace("|", "\\|"),
                status=str(row["status"]).replace("|", "\\|"),
                tail=str(row["evidence_tail"]).replace("|", "\\|"),
                proves=str(row["proves"]).replace("|", "\\|"),
                limit=str(row["limitation"]).replace("|", "\\|"),
            )
        )
    if report["next_required_human_actions"]:
        lines.extend(["", "## Required Human Actions"])
        for action in report["next_required_human_actions"]:
            lines.append(f"- `{action['step_id']}`: {action['action']}")
    lines.extend(["", f"> {report['disclaimer']}", ""])
    return "\n".join(lines)


def write_report(report: dict, *, out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(markdown_report(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", default=str(DEFAULT_JSON))
    parser.add_argument("--out-md", default=str(DEFAULT_MD))
    parser.add_argument("--json", action="store_true", help="In JSON ra stdout.")
    args = parser.parse_args()

    report = run_cycle()
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    write_report(report, out_json=out_json, out_md=out_md)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Controlled automation cycle:", report["overall_status"])
        for row in report["rows"]:
            print(f"- {row['status']} {row['step_id']}: {row['evidence_tail']}")
        print(f"JSON: {out_json}")
        print(f"Markdown: {out_md}")
        print(report["disclaimer"])
    return 1 if report["overall_status"] == "FAIL_CLOSED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
