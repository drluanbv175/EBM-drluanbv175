#!/usr/bin/env python3
"""Vong lap kiem tra - hoan thien den nguong clinical production.

Cong cu nay dieu phoi cac verifier san co thanh mot loop co gioi han:
- loi ky thuat/sync/Unicode/test -> chay remediation an toan roi lap lai;
- thieu phe duyet lam sang, evidence package, UAT, signoff that -> dung fail-closed;
- chi bao CLINICAL_PRODUCTION_READY khi tat ca cong ky thuat PASS, knowledge packs
  clinical-release-ready va go-live gate that su PRODUCTION_READY.

No KHONG tao approval, KHONG sua evidence manifest thanh "approved", KHONG bat du lieu
benh nhan that. Do la phan cua bac si/PI/phap ly/bao mat/van hanh.
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

DISCLAIMER = (
    "Can bac si kiem chung. Vong lap nay chi tu sua cac loi ky thuat an toan; "
    "khong thay phe duyet lam sang, IRB/PI, bao mat, phap ly, UAT, signoff "
    "hoac quyet dinh dieu tri."
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
    raise SystemExit("Cannot find tsx CLI. Run pnpm install in chronic-care-clinic-os first.")


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

    kp = _run_command(runner, [PY, "tools/assess_knowledge_pack_release.py", "--json"], REPO)
    kp_payload = _json_from_output(kp)
    kp_ready = bool(kp_payload.get("clinical_release_allowed"))
    kp_summary = kp_payload.get("summary") or {}
    kp_action = (
        "Hoan tat 13_approval_record.json va 10_evidence_manifest.json cho moi pack; "
        f"hien tai clinical_release_ready={kp_summary.get('clinical_release_ready', '?')}/"
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
            stderr="BLOCKED: provide production evidence package and dual-control go-live attestation.",
        )
        steps.append(_step(
            "clinical_go_live_gate",
            HUMAN_GATE,
            missing,
            human_action=(
                "Cung cap production evidence package that, UAT/security/legal/clinical signoff, "
                "release-id, operator-ref, admin-approver, change ticket, rollback plan va "
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
            human_action="" if go_live_ready else "Sua tat ca blockedReasons trong go-live report; khong duoc dung placeholder hoac self-approval.",
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
        if status == TECHNICAL_FAIL and remediate and index < max_iterations:
            remediation = run_remediation(runner)
        iterations.append(LoopIteration(index, status, steps, remediation))
        if status != TECHNICAL_FAIL:
            break

    all_steps = [step for item in iterations for step in item.steps]
    human_actions = [
        {"step_id": step.step_id, "action": step.human_action}
        for step in all_steps
        if step.status == HUMAN_GATE and step.human_action
    ]
    technical_failures = [
        {"step_id": step.step_id, "tail": step.evidence_tail}
        for step in all_steps
        if step.status == FAIL
    ]
    return {
        "kind": "clinical_production_loop_report",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall_status": final_status,
        "clinical_production_allowed": final_status == CLINICAL_PRODUCTION_READY,
        "iteration_count": len(iterations),
        "max_iterations": max_iterations,
        "technical_failure_count": len(technical_failures),
        "human_gate_count": len(human_actions),
        "technical_failures": technical_failures,
        "required_human_actions": human_actions,
        "iterations": [asdict(item) for item in iterations],
        "disclaimer": DISCLAIMER,
    }


def markdown_report(report: dict) -> str:
    lines = [
        "# Clinical Production Loop",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Overall status: `{report['overall_status']}`",
        f"- Clinical production allowed: `{report['clinical_production_allowed']}`",
        f"- Iterations: `{report['iteration_count']}/{report['max_iterations']}`",
        f"- Technical failures: `{report['technical_failure_count']}`",
        f"- Human gates: `{report['human_gate_count']}`",
        "",
        "| Iteration | Step | Status | Evidence tail | Human action |",
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
        lines.extend(["", "## Required Human Actions"])
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
    parser = argparse.ArgumentParser(description="Run a fail-closed loop toward clinical production readiness.")
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument("--evidence", help="Production evidence package JSON for final go-live.")
    parser.add_argument("--release-id")
    parser.add_argument("--source-commit")
    parser.add_argument("--operator-ref")
    parser.add_argument("--admin-approver")
    parser.add_argument("--change-ticket")
    parser.add_argument("--rollback-plan")
    parser.add_argument("--post-deploy-checklist")
    parser.add_argument("--no-remediate", action="store_true")
    parser.add_argument("--out-json", default=str(REPORT_JSON))
    parser.add_argument("--out-md", default=str(REPORT_MD))
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--json", action="store_true")
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
        print(f"clinical_production_allowed={report['clinical_production_allowed']}")
        print(f"iteration_count={report['iteration_count']}/{report['max_iterations']}")
        print(f"technical_failure_count={report['technical_failure_count']}")
        print(f"human_gate_count={report['human_gate_count']}")
        for action in report["required_human_actions"]:
            print(f"human_gate:{action['step_id']}={action['action']}")
        print(DISCLAIMER)
    return 0 if report["overall_status"] == CLINICAL_PRODUCTION_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
