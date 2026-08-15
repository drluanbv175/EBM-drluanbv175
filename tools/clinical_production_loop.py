#!/usr/bin/env python3
"""Vòng lặp kiểm tra–hoàn thiện toàn hệ EBM tới ngưỡng tốt nhất có thể.

Công cụ điều phối các verifier Research, Clinical, Knowledge và hạ tầng thành
một vòng lặp có giới hạn:
- lỗi kỹ thuật/sync/Unicode/test -> chạy remediation an toàn rồi kiểm lại;
- lỗi không đổi sau remediation hoặc remediation lỗi -> dừng sớm, không lặp mù;
- thiếu phê duyệt lâm sàng, evidence package, UAT, signoff thật -> dừng fail-closed
  và ghi nhận đây là mức tốt nhất có thể đạt tự động;
- chỉ báo CLINICAL_PRODUCTION_READY khi tất cả cổng kỹ thuật PASS, knowledge packs
  clinical-release-ready và go-live gate thật sự PRODUCTION_READY.

Nó KHÔNG tạo approval, KHÔNG sửa evidence manifest thành "approved", KHÔNG bật dữ
liệu bệnh nhân thật. Đó là phần của bác sĩ/PI/pháp lý/bảo mật/vận hành.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "medical-ebm-automation"
CCOS = REPO / "chronic-care-clinic-os"
REPORT_JSON = ROOT / "reports" / "CLINICAL_PRODUCTION_LOOP.json"
REPORT_MD = ROOT / "reports" / "CLINICAL_PRODUCTION_LOOP.md"
VENV_PY = (
    Path.home() / ".ebm-venv" / "Scripts" / "python.exe"
    if os.name == "nt"
    else Path.home() / ".ebm-venv" / "bin" / "python"
)
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable

PASS = "PASS"
FAIL = "FAIL"
HUMAN_GATE = "HUMAN_GATE"
TECHNICAL_FAIL = "TECHNICAL_FAIL"
BLOCKED_BY_HUMAN_GATES = "BLOCKED_BY_HUMAN_GATES"
CLINICAL_PRODUCTION_READY = "CLINICAL_PRODUCTION_READY"

ALL_GATES_PASSED = "ALL_GATES_PASSED"
HUMAN_GATES_ONLY = "HUMAN_GATES_ONLY"
NO_PROGRESS_AFTER_SAFE_REMEDIATION = "NO_PROGRESS_AFTER_SAFE_REMEDIATION"
SAFE_REMEDIATION_FAILED = "SAFE_REMEDIATION_FAILED"
REMEDIATION_DISABLED = "REMEDIATION_DISABLED"
MAX_ITERATIONS_REACHED = "MAX_ITERATIONS_REACHED"

FULLY_READY = "FULLY_READY"
BEST_ACHIEVABLE_WITHOUT_HUMAN_APPROVAL = "BEST_ACHIEVABLE_WITHOUT_HUMAN_APPROVAL"
INCOMPLETE_TECHNICAL = "INCOMPLETE_TECHNICAL"

DISCLAIMER = (
    "Cần bác sĩ kiểm chứng. Vòng lặp này chỉ tự sửa các lỗi kỹ thuật an toàn; "
    "không thay phê duyệt lâm sàng, IRB/PI, bảo mật, pháp lý, UAT, signoff "
    "hoặc quyết định điều trị."
)


def _configure_utf8_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


_configure_utf8_stdio()


@dataclass(frozen=True)
class CommandResult:
    command: str
    cwd: str
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class LoopStep:
    step_id: str
    status: str
    command: str
    returncode: int
    evidence_tail: str
    human_action: str = ""


@dataclass(frozen=True)
class LoopIteration:
    iteration: int
    status: str
    steps: list[LoopStep]
    remediation_steps: list[LoopStep]
    technical_failure_signature: str = ""


Runner = Callable[[Sequence[str], Path], CommandResult]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONPYCACHEPREFIX", str(Path(tempfile.gettempdir()) / "ebm_pycache"))
    return env


def _display(command: Sequence[str]) -> str:
    return " ".join(str(part) for part in command)


def _tail(stdout: str, stderr: str, max_lines: int = 4) -> str:
    lines = [line.strip() for line in (stdout or "").splitlines() if line.strip()]
    if not lines:
        lines = [line.strip() for line in (stderr or "").splitlines() if line.strip()]
    return " / ".join((lines or [""])[-max_lines:])[:800]


def _default_runner(command: Sequence[str], cwd: Path) -> CommandResult:
    proc = subprocess.run(
        [str(part) for part in command],
        cwd=str(cwd),
        env=_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return CommandResult(
        command=_display(command),
        cwd=str(cwd),
        returncode=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
    )


def _json_from_output(result: CommandResult) -> dict:
    text = (result.stdout or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return {}
    return {}


def _step(
    step_id: str,
    status: str,
    result: CommandResult,
    *,
    human_action: str = "",
) -> LoopStep:
    return LoopStep(
        step_id=step_id,
        status=status,
        command=result.command,
        returncode=result.returncode,
        evidence_tail=_tail(result.stdout, result.stderr),
        human_action=human_action,
    )


def _run_command(
    runner: Runner,
    command: Sequence[str],
    cwd: Path,
) -> CommandResult:
    return runner(command, cwd)


def _current_repo_commit(runner: Runner) -> str | None:
    result = _run_command(runner, ["git", "rev-parse", "HEAD"], REPO)
    if result.returncode != 0:
        return None
    value = (result.stdout or "").strip().splitlines()
    return value[-1].strip() if value else None


def _find_node() -> str:
    sys.path.insert(0, str(CCOS / "scripts"))
    import node_runtime  # type: ignore  # noqa: PLC0415

    return str(node_runtime.find_node())


def _find_tsx_cli() -> str:
    matches = sorted((CCOS / "node_modules" / ".pnpm").glob("tsx@*/node_modules/tsx/dist/cli.mjs"))
    if matches:
        return str(matches[-1])
    fallback = CCOS / "node_modules" / "tsx" / "dist" / "cli.mjs"
    if fallback.exists():
        return str(fallback)
    raise SystemExit("Không tìm thấy tsx CLI. Hãy chạy pnpm install trong chronic-care-clinic-os trước.")


def _go_live_command(
    *,
    evidence: str,
    release_id: str | None,
    source_commit: str | None,
    operator_ref: str | None,
    admin_approver: str | None,
    change_ticket: str | None,
    rollback_plan: str | None,
    post_deploy_checklist: str | None,
    runner: Runner,
) -> list[str]:
    commit = source_commit or _current_repo_commit(runner)
    command = [
        _find_node(),
        _find_tsx_cli(),
        "scripts/production-go-live.ts",
        "--evidence",
        evidence,
        "--json",
    ]
    optional_args = [
        ("--release-id", release_id),
        ("--source-commit", commit),
        ("--operator-ref", operator_ref),
        ("--admin-approver", admin_approver),
        ("--change-ticket", change_ticket),
        ("--rollback-plan", rollback_plan),
        ("--post-deploy-checklist", post_deploy_checklist),
    ]
    for flag, value in optional_args:
        if value:
            command.extend([flag, value])
    return command


def remediation_commands() -> list[tuple[str, list[str], Path]]:
    """Cac thao tac tu hoan thien an toan, idempotent, khong tu phe duyet clinical."""
    return [
        ("enforce_guardrails", [PY, "tools/enforce_agent_guardrails.py"], ROOT),
        ("sync_codex_agents", [PY, "tools/sync_agents_to_codex.py"], ROOT),
        ("check_codex_agent_sync", [PY, "tools/sync_agents_to_codex.py", "--check"], ROOT),
        ("sync_ebm_master", [PY, "EBM_MASTER/tools/sync_all.py"], ROOT),
        ("validate_knowledge_packs", [PY, "tools/validate_knowledge_packs.py"], REPO),
    ]


def run_remediation(runner: Runner) -> list[LoopStep]:
    steps: list[LoopStep] = []
    for step_id, command, cwd in remediation_commands():
        result = _run_command(runner, command, cwd)
        steps.append(_step(step_id, PASS if result.returncode == 0 else FAIL, result))
    return steps


def _technical_failure_signature(steps: Sequence[LoopStep]) -> str:
    """Tạo dấu vân tay ổn định để phát hiện remediation không tạo tiến triển."""
    failures = [
        f"{step.step_id}:{step.returncode}:{step.evidence_tail}"
        for step in steps
        if step.status == FAIL
    ]
    return " || ".join(failures)


def evaluate_once(
    *,
    runner: Runner = _default_runner,
    evidence: str | None = None,
    release_id: str | None = None,
    source_commit: str | None = None,
    operator_ref: str | None = None,
    admin_approver: str | None = None,
    change_ticket: str | None = None,
    rollback_plan: str | None = None,
    post_deploy_checklist: str | None = None,
) -> tuple[str, list[LoopStep]]:
    steps: list[LoopStep] = []

    upgrade = _run_command(runner, [PY, "tools/upgrade_verify.py"], ROOT)
    steps.append(_step("upgrade_verify", PASS if upgrade.returncode == 0 else FAIL, upgrade))

    cycle = _run_command(runner, [PY, "tools/run_controlled_automation_cycle.py", "--json"], ROOT)
    cycle_payload = _json_from_output(cycle)
    cycle_failed = cycle.returncode != 0 or cycle_payload.get("overall_status") == "FAIL_CLOSED"
    steps.append(_step("controlled_automation_cycle", PASS if not cycle_failed else FAIL, cycle))
    if not cycle_failed:
        for item in cycle_payload.get("next_required_human_actions") or []:
            step_id = str(item.get("step_id") or "").strip()
            action = str(item.get("action") or "").strip()
            if not step_id or not action:
                continue
            inherited_gate = CommandResult(
                command=cycle.command,
                cwd=cycle.cwd,
                returncode=0,
                stdout=f"CONTROLLED_HUMAN_GATE: {step_id}",
                stderr="",
            )
            steps.append(
                _step(
                    f"controlled_cycle:{step_id}",
                    HUMAN_GATE,
                    inherited_gate,
                    human_action=action,
                )
            )

    kp = _run_command(runner, [PY, "tools/assess_knowledge_pack_release.py", "--json"], REPO)
    kp_payload = _json_from_output(kp)
    kp_ready = bool(kp_payload.get("clinical_release_allowed"))
    kp_summary = kp_payload.get("summary") or {}
    kp_action = (
        "Hoàn tất 13_approval_record.json và 10_evidence_manifest.json cho từng pack; "
        f"hiện tại clinical_release_ready={kp_summary.get('clinical_release_ready', '?')}/"
        f"{kp_summary.get('total', '?')}."
    )
    steps.append(_step("knowledge_pack_release_gate", PASS if kp_ready else HUMAN_GATE, kp,
                       human_action="" if kp_ready else kp_action))

    if not evidence:
        missing = CommandResult(
            command="production-go-live --evidence <missing>",
            cwd=str(CCOS),
            returncode=2,
            stdout="",
            stderr="BLOCKED: cần gói chứng cứ production và xác nhận go-live kiểm soát kép.",
        )
        steps.append(_step(
            "clinical_go_live_gate",
            HUMAN_GATE,
            missing,
            human_action=(
                "Cung cấp production evidence package thật, UAT/security/legal/clinical signoff, "
                "release-id, operator-ref, admin-approver, change ticket, rollback plan và "
                "post-deploy checklist."
            ),
        ))
    else:
        go_live_command = _go_live_command(
            evidence=evidence,
            release_id=release_id,
            source_commit=source_commit,
            operator_ref=operator_ref,
            admin_approver=admin_approver,
            change_ticket=change_ticket,
            rollback_plan=rollback_plan,
            post_deploy_checklist=post_deploy_checklist,
            runner=runner,
        )
        go_live = _run_command(runner, go_live_command, CCOS)
        go_live_payload = _json_from_output(go_live)
        go_live_ready = (
            go_live.returncode == 0
            and (
                go_live_payload.get("productionReady") is True
                or "productionReady=true" in go_live.stdout
                or "status=PRODUCTION_READY" in go_live.stdout
            )
        )
        steps.append(_step(
            "clinical_go_live_gate",
            PASS if go_live_ready else HUMAN_GATE,
            go_live,
            human_action="" if go_live_ready else "Sửa tất cả blockedReasons trong go-live report; không được dùng placeholder hoặc self-approval.",
        ))

    if any(step.status == FAIL for step in steps):
        return TECHNICAL_FAIL, steps
    if any(step.status == HUMAN_GATE for step in steps):
        return BLOCKED_BY_HUMAN_GATES, steps
    return CLINICAL_PRODUCTION_READY, steps


def run_loop(
    *,
    max_iterations: int = 3,
    runner: Runner = _default_runner,
    evidence: str | None = None,
    release_id: str | None = None,
    source_commit: str | None = None,
    operator_ref: str | None = None,
    admin_approver: str | None = None,
    change_ticket: str | None = None,
    rollback_plan: str | None = None,
    post_deploy_checklist: str | None = None,
    remediate: bool = True,
) -> dict:
    iterations: list[LoopIteration] = []
    max_iterations = max(1, max_iterations)

    final_status = TECHNICAL_FAIL
    previous_failure_signature = ""
    convergence_reason = ""
    converged = False
    for index in range(1, max_iterations + 1):
        status, steps = evaluate_once(
            runner=runner,
            evidence=evidence,
            release_id=release_id,
            source_commit=source_commit,
            operator_ref=operator_ref,
            admin_approver=admin_approver,
            change_ticket=change_ticket,
            rollback_plan=rollback_plan,
            post_deploy_checklist=post_deploy_checklist,
        )
        remediation: list[LoopStep] = []
        final_status = status
        failure_signature = _technical_failure_signature(steps)

        if status == CLINICAL_PRODUCTION_READY:
            converged = True
            convergence_reason = ALL_GATES_PASSED
        elif status == BLOCKED_BY_HUMAN_GATES:
            converged = True
            convergence_reason = HUMAN_GATES_ONLY
        elif previous_failure_signature and failure_signature == previous_failure_signature:
            converged = True
            convergence_reason = NO_PROGRESS_AFTER_SAFE_REMEDIATION
        elif not remediate:
            convergence_reason = REMEDIATION_DISABLED
        elif index >= max_iterations:
            convergence_reason = MAX_ITERATIONS_REACHED
        else:
            remediation = run_remediation(runner)
            if any(step.status == FAIL for step in remediation):
                convergence_reason = SAFE_REMEDIATION_FAILED
            else:
                previous_failure_signature = failure_signature

        iterations.append(
            LoopIteration(index, status, steps, remediation, failure_signature)
        )
        if status != TECHNICAL_FAIL or convergence_reason in {
            NO_PROGRESS_AFTER_SAFE_REMEDIATION,
            SAFE_REMEDIATION_FAILED,
            REMEDIATION_DISABLED,
            MAX_ITERATIONS_REACHED,
        }:
            break

    all_steps = [step for item in iterations for step in item.steps]
    human_actions = []
    seen_human_actions: set[tuple[str, str]] = set()
    for step in all_steps:
        key = (step.step_id, step.human_action)
        if step.status == HUMAN_GATE and step.human_action and key not in seen_human_actions:
            seen_human_actions.add(key)
            human_actions.append({"step_id": step.step_id, "action": step.human_action})
    technical_failures = [
        {"step_id": step.step_id, "tail": step.evidence_tail}
        for step in all_steps
        if step.status == FAIL
    ]
    final_steps = iterations[-1].steps if iterations else []
    unresolved_technical_failures = [
        {"step_id": step.step_id, "tail": step.evidence_tail}
        for step in final_steps
        if step.status == FAIL
    ]
    technical_completion_achieved = final_status != TECHNICAL_FAIL
    best_achievable_automatically = final_status == BLOCKED_BY_HUMAN_GATES
    if final_status == CLINICAL_PRODUCTION_READY:
        completion_level = FULLY_READY
    elif best_achievable_automatically:
        completion_level = BEST_ACHIEVABLE_WITHOUT_HUMAN_APPROVAL
    else:
        completion_level = INCOMPLETE_TECHNICAL
    return {
        "kind": "clinical_production_loop_report",
        "scope": ["research", "clinical", "knowledge", "agents", "plugins", "hub", "tests", "lint"],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall_status": final_status,
        "completion_level": completion_level,
        "technical_completion_achieved": technical_completion_achieved,
        "best_achievable_automatically": best_achievable_automatically,
        "converged": converged,
        "convergence_reason": convergence_reason,
        "clinical_production_allowed": final_status == CLINICAL_PRODUCTION_READY,
        "iteration_count": len(iterations),
        "max_iterations": max_iterations,
        "technical_failure_count": len(technical_failures),
        "unresolved_technical_failure_count": len(unresolved_technical_failures),
        "human_gate_count": len(human_actions),
        "technical_failures": technical_failures,
        "unresolved_technical_failures": unresolved_technical_failures,
        "required_human_actions": human_actions,
        "iterations": [asdict(item) for item in iterations],
        "disclaimer": DISCLAIMER,
    }


def markdown_report(report: dict) -> str:
    lines = [
        "# Vòng lặp kiểm tra–hoàn thiện toàn hệ EBM",
        "",
        f"- Thời điểm: `{report['generated_at']}`",
        f"- Trạng thái tổng thể: `{report['overall_status']}`",
        f"- Mức hoàn thiện: `{report.get('completion_level', '-')}`",
        f"- Hoàn thiện kỹ thuật: `{report.get('technical_completion_achieved', False)}`",
        f"- Mức tốt nhất có thể tự động: `{report.get('best_achievable_automatically', False)}`",
        f"- Đã hội tụ: `{report.get('converged', False)}`",
        f"- Lý do hội tụ: `{report.get('convergence_reason', '-')}`",
        f"- Cho phép clinical production: `{report['clinical_production_allowed']}`",
        f"- Số vòng: `{report['iteration_count']}/{report['max_iterations']}`",
        f"- Tổng lỗi kỹ thuật đã gặp: `{report['technical_failure_count']}`",
        f"- Lỗi kỹ thuật chưa giải quyết: `{report.get('unresolved_technical_failure_count', 0)}`",
        f"- Cổng con người: `{report['human_gate_count']}`",
        "",
        "| Vòng | Bước | Trạng thái | Chứng cứ cuối | Hành động con người |",
        "|---|---|---|---|---|",
    ]
    for item in report["iterations"]:
        for row in item["steps"]:
            lines.append(
                "| {iteration} | {step_id} | {status} | {tail} | {action} |".format(
                    iteration=item["iteration"],
                    step_id=row["step_id"],
                    status=row["status"],
                    tail=str(row["evidence_tail"]).replace("|", "\\|"),
                    action=(row.get("human_action") or "-").replace("|", "\\|"),
                )
            )
        for row in item["remediation_steps"]:
            lines.append(
                "| {iteration} | remediation:{step_id} | {status} | {tail} | - |".format(
                    iteration=item["iteration"],
                    step_id=row["step_id"],
                    status=row["status"],
                    tail=str(row["evidence_tail"]).replace("|", "\\|"),
                )
            )
    if report["required_human_actions"]:
        lines.extend(["", "## Hành động bắt buộc của con người"])
        for action in report["required_human_actions"]:
            lines.append(f"- `{action['step_id']}`: {action['action']}")
    lines.extend(["", f"> {report['disclaimer']}", ""])
    return "\n".join(lines)


def write_report(report: dict, *, out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(markdown_report(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Chạy vòng lặp fail-closed hoàn thiện toàn hệ tới mức tốt nhất có thể."
    )
    parser.add_argument("--max-iterations", type=int, default=3, help="Số vòng kỹ thuật tối đa.")
    parser.add_argument("--evidence", help="Gói chứng cứ production JSON cho cổng go-live cuối.")
    parser.add_argument("--release-id")
    parser.add_argument("--source-commit")
    parser.add_argument("--operator-ref")
    parser.add_argument("--admin-approver")
    parser.add_argument("--change-ticket")
    parser.add_argument("--rollback-plan")
    parser.add_argument("--post-deploy-checklist")
    parser.add_argument("--no-remediate", action="store_true", help="Chỉ kiểm, không tự sửa kỹ thuật an toàn.")
    parser.add_argument("--out-json", default=str(REPORT_JSON))
    parser.add_argument("--out-md", default=str(REPORT_MD))
    parser.add_argument("--no-write", action="store_true", help="Không ghi báo cáo JSON/Markdown.")
    parser.add_argument("--json", action="store_true", help="In toàn bộ báo cáo JSON ra stdout.")
    args = parser.parse_args(argv)

    report = run_loop(
        max_iterations=args.max_iterations,
        evidence=args.evidence,
        release_id=args.release_id,
        source_commit=args.source_commit,
        operator_ref=args.operator_ref,
        admin_approver=args.admin_approver,
        change_ticket=args.change_ticket,
        rollback_plan=args.rollback_plan,
        post_deploy_checklist=args.post_deploy_checklist,
        remediate=not args.no_remediate,
    )
    if not args.no_write:
        write_report(report, out_json=Path(args.out_json), out_md=Path(args.out_md))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"overall_status={report['overall_status']}")
        print(f"completion_level={report['completion_level']}")
        print(f"technical_completion_achieved={report['technical_completion_achieved']}")
        print(f"best_achievable_automatically={report['best_achievable_automatically']}")
        print(f"converged={report['converged']}")
        print(f"convergence_reason={report['convergence_reason']}")
        print(f"clinical_production_allowed={report['clinical_production_allowed']}")
        print(f"iteration_count={report['iteration_count']}/{report['max_iterations']}")
        print(f"technical_failure_count={report['technical_failure_count']}")
        print(f"unresolved_technical_failure_count={report['unresolved_technical_failure_count']}")
        print(f"human_gate_count={report['human_gate_count']}")
        for action in report["required_human_actions"]:
            print(f"human_gate:{action['step_id']}={action['action']}")
        print(DISCLAIMER)
    return 0 if report["overall_status"] == CLINICAL_PRODUCTION_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
