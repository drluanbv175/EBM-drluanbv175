from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clinical_production_loop as L  # noqa: E402


def _result(
    command: Sequence[str],
    cwd: Path,
    *,
    returncode: int = 0,
    payload: dict | None = None,
    stdout: str | None = None,
    stderr: str = "",
) -> L.CommandResult:
    if payload is not None:
        stdout = json.dumps(payload)
    return L.CommandResult(
        command=" ".join(str(part) for part in command),
        cwd=str(cwd),
        returncode=returncode,
        stdout=stdout or "PASS",
        stderr=stderr,
    )


def _controlled_payload(*, with_human_gates: bool = True) -> dict:
    payload = {
        "overall_status": (
            "CONTROLLED_READY_WITH_HUMAN_GATES" if with_human_gates else "CONTROLLED_READY"
        )
    }
    if with_human_gates:
        payload["human_gate_count"] = 1
        payload["next_required_human_actions"] = [
            {
                "step_id": "research_gate_contract",
                "action": "Cần IRB/PI xác nhận cổng nghiên cứu thật.",
            }
        ]
    return payload


def _knowledge_payload(*, allowed: bool) -> dict:
    ready = 10 if allowed else 0
    return {
        "clinical_release_allowed": allowed,
        "summary": {
            "total": 10,
            "clinical_release_ready": ready,
            "patient_facing_ready": ready,
        },
    }


def test_loop_blocks_on_human_gates_without_evidence_or_pack_release():
    def runner(command: Sequence[str], cwd: Path) -> L.CommandResult:
        command_text = " ".join(str(part) for part in command)
        if "upgrade_verify.py" in command_text:
            return _result(command, cwd, stdout="PASS 25/25")
        if "run_controlled_automation_cycle.py" in command_text:
            return _result(command, cwd, payload=_controlled_payload())
        if "assess_knowledge_pack_release.py" in command_text:
            return _result(command, cwd, payload=_knowledge_payload(allowed=False))
        raise AssertionError(f"unexpected command: {command_text}")

    report = L.run_loop(max_iterations=2, runner=runner, remediate=False)

    assert report["overall_status"] == L.BLOCKED_BY_HUMAN_GATES
    assert report["completion_level"] == L.BEST_ACHIEVABLE_WITHOUT_HUMAN_APPROVAL
    assert report["technical_completion_achieved"] is True
    assert report["best_achievable_automatically"] is True
    assert report["converged"] is True
    assert report["convergence_reason"] == L.HUMAN_GATES_ONLY
    assert report["clinical_production_allowed"] is False
    assert report["technical_failure_count"] == 0
    assert report["human_gate_count"] == 3
    assert {item["step_id"] for item in report["required_human_actions"]} == {
        "controlled_cycle:research_gate_contract",
        "knowledge_pack_release_gate",
        "clinical_go_live_gate",
    }


def test_loop_can_report_clinical_production_ready_when_all_gates_pass(monkeypatch):
    monkeypatch.setattr(L, "_find_node", lambda: "node")
    monkeypatch.setattr(L, "_find_tsx_cli", lambda: "tsx")

    def runner(command: Sequence[str], cwd: Path) -> L.CommandResult:
        command_text = " ".join(str(part) for part in command)
        if "upgrade_verify.py" in command_text:
            return _result(command, cwd, stdout="PASS 25/25")
        if "run_controlled_automation_cycle.py" in command_text:
            return _result(command, cwd, payload=_controlled_payload(with_human_gates=False))
        if "assess_knowledge_pack_release.py" in command_text:
            return _result(command, cwd, payload=_knowledge_payload(allowed=True))
        if "production-go-live.ts" in command_text:
            return _result(
                command,
                cwd,
                payload={"status": "PRODUCTION_READY", "productionReady": True},
            )
        raise AssertionError(f"unexpected command: {command_text}")

    report = L.run_loop(
        max_iterations=1,
        runner=runner,
        evidence="C:/secure/production-evidence.json",
        release_id="rel-2026-07-23",
        source_commit="abc1234",
        operator_ref="ops/on-call",
        admin_approver="cmio@example.test",
        change_ticket="CHG-123",
        rollback_plan="rollback.md",
        post_deploy_checklist="post-deploy.md",
    )

    assert report["overall_status"] == L.CLINICAL_PRODUCTION_READY
    assert report["completion_level"] == L.FULLY_READY
    assert report["technical_completion_achieved"] is True
    assert report["best_achievable_automatically"] is False
    assert report["converged"] is True
    assert report["convergence_reason"] == L.ALL_GATES_PASSED
    assert report["clinical_production_allowed"] is True
    assert report["human_gate_count"] == 0
    assert report["technical_failure_count"] == 0


def test_loop_remediates_technical_failure_then_rechecks():
    upgrade_calls = 0
    remediation_calls: list[str] = []

    def runner(command: Sequence[str], cwd: Path) -> L.CommandResult:
        nonlocal upgrade_calls
        command_text = " ".join(str(part) for part in command)
        if "upgrade_verify.py" in command_text:
            upgrade_calls += 1
            return _result(
                command,
                cwd,
                returncode=1 if upgrade_calls == 1 else 0,
                stdout="FAIL unicode gate" if upgrade_calls == 1 else "PASS 25/25",
            )
        if "run_controlled_automation_cycle.py" in command_text:
            return _result(command, cwd, payload=_controlled_payload())
        if "assess_knowledge_pack_release.py" in command_text:
            return _result(command, cwd, payload=_knowledge_payload(allowed=False))
        remediation_calls.append(command_text)
        return _result(command, cwd, stdout="remediated")

    report = L.run_loop(max_iterations=2, runner=runner, remediate=True)

    assert report["overall_status"] == L.BLOCKED_BY_HUMAN_GATES
    assert report["clinical_production_allowed"] is False
    assert report["iteration_count"] == 2
    assert report["iterations"][0]["status"] == L.TECHNICAL_FAIL
    assert report["iterations"][1]["status"] == L.BLOCKED_BY_HUMAN_GATES
    assert remediation_calls


def test_loop_stops_early_when_safe_remediation_makes_no_progress():
    remediation_calls: list[str] = []

    def runner(command: Sequence[str], cwd: Path) -> L.CommandResult:
        command_text = " ".join(str(part) for part in command)
        if "upgrade_verify.py" in command_text:
            return _result(command, cwd, returncode=1, stdout="FAIL stable gate")
        if "run_controlled_automation_cycle.py" in command_text:
            return _result(command, cwd, payload=_controlled_payload())
        if "assess_knowledge_pack_release.py" in command_text:
            return _result(command, cwd, payload=_knowledge_payload(allowed=False))
        remediation_calls.append(command_text)
        return _result(command, cwd, stdout="remediated")

    report = L.run_loop(max_iterations=5, runner=runner, remediate=True)

    assert report["overall_status"] == L.TECHNICAL_FAIL
    assert report["completion_level"] == L.INCOMPLETE_TECHNICAL
    assert report["iteration_count"] == 2
    assert report["converged"] is True
    assert report["convergence_reason"] == L.NO_PROGRESS_AFTER_SAFE_REMEDIATION
    assert report["unresolved_technical_failure_count"] == 1
    assert remediation_calls
    assert report["iterations"][1]["remediation_steps"] == []


def test_loop_stops_when_a_safe_remediation_step_fails():
    def runner(command: Sequence[str], cwd: Path) -> L.CommandResult:
        command_text = " ".join(str(part) for part in command)
        if "upgrade_verify.py" in command_text:
            return _result(command, cwd, returncode=1, stdout="FAIL technical gate")
        if "run_controlled_automation_cycle.py" in command_text:
            return _result(command, cwd, payload=_controlled_payload())
        if "assess_knowledge_pack_release.py" in command_text:
            return _result(command, cwd, payload=_knowledge_payload(allowed=False))
        if "sync_codex_agents" in command_text:
            return _result(command, cwd, returncode=1, stdout="FAIL remediation")
        # Nhận diện chính xác một lệnh remediation thật để mô phỏng thất bại.
        if "sync_agents_to_codex.py" in command_text and "--check" not in command_text:
            return _result(command, cwd, returncode=1, stdout="FAIL remediation")
        return _result(command, cwd, stdout="remediated")

    report = L.run_loop(max_iterations=5, runner=runner, remediate=True)

    assert report["overall_status"] == L.TECHNICAL_FAIL
    assert report["iteration_count"] == 1
    assert report["converged"] is False
    assert report["convergence_reason"] == L.SAFE_REMEDIATION_FAILED
    assert any(
        step["status"] == L.FAIL
        for step in report["iterations"][0]["remediation_steps"]
    )


def test_markdown_report_lists_required_human_actions():
    report = {
        "generated_at": "2026-07-23T00:00:00+00:00",
        "overall_status": L.BLOCKED_BY_HUMAN_GATES,
        "clinical_production_allowed": False,
        "iteration_count": 1,
        "max_iterations": 3,
        "technical_failure_count": 0,
        "human_gate_count": 1,
        "required_human_actions": [
            {"step_id": "clinical_go_live_gate", "action": "Provide real signoff."}
        ],
        "iterations": [
            {
                "iteration": 1,
                "steps": [
                    {
                        "step_id": "clinical_go_live_gate",
                        "status": L.HUMAN_GATE,
                        "evidence_tail": "missing evidence",
                        "human_action": "Provide real signoff.",
                    }
                ],
                "remediation_steps": [],
            }
        ],
        "disclaimer": L.DISCLAIMER,
    }

    md = L.markdown_report(report)

    assert "Vòng lặp kiểm tra–hoàn thiện toàn hệ EBM" in md
    assert L.BLOCKED_BY_HUMAN_GATES in md
    assert "Hành động bắt buộc của con người" in md
    assert "Provide real signoff." in md
