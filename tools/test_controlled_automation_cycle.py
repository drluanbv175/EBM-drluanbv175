from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_controlled_automation_cycle as C  # noqa: E402


def _completed(command: list[str], returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=command,
        returncode=returncode,
        stdout="synthetic PASS\nCần bác sĩ kiểm chứng.\n",
        stderr="",
    )


def test_control_steps_include_core_control_domains():
    steps = C.control_steps()
    step_ids = {step.step_id for step in steps}

    assert {
        "agent_sync",
        "repo_alignment",
        "agent_routing",
        "research_gate_contract",
        "real_data_path",
        "controlled_reviews_stats",
        "clinical_schema_hardening",
        "clinical_runtime_readiness",
    } <= step_ids
    assert any(step.human_gate for step in steps)
    assert all(step.command for step in steps)


def test_summarize_reports_controlled_ready_with_human_gates():
    report = C.run_cycle(python=sys.executable, runner=lambda command: _completed(command))

    assert report["overall_status"] == "CONTROLLED_READY_WITH_HUMAN_GATES"
    assert report["automation_allowed_for_offline_controlled_tasks"] is True
    assert report["clinical_production_allowed"] is False
    assert report["blocking_failure_count"] == 0
    assert report["human_gate_count"] >= 1
    assert report["next_required_human_actions"]


def test_summarize_fail_closed_on_blocking_failure():
    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        if "tools/verify_agent_routing.py" in command:
            return _completed(command, returncode=1)
        return _completed(command)

    report = C.run_cycle(python=sys.executable, runner=runner)

    assert report["overall_status"] == "FAIL_CLOSED"
    assert report["automation_allowed_for_offline_controlled_tasks"] is False
    assert report["blocking_failure_count"] == 1
    failed = [row for row in report["rows"] if row["status"] == "FAIL"]
    assert failed[0]["step_id"] == "agent_routing"


def test_nonblocking_human_gate_warning_does_not_fail_closed():
    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        if "tools/clinical_runtime_readiness_report.py" in command:
            return _completed(command, returncode=1)
        return _completed(command)

    report = C.run_cycle(python=sys.executable, runner=runner)

    assert report["overall_status"] == "CONTROLLED_READY_WITH_HUMAN_GATES"
    warning = [row for row in report["rows"] if row["step_id"] == "clinical_runtime_readiness"][0]
    assert warning["status"] == "WARN"
    assert warning["blocking"] is False


def test_markdown_report_lists_required_human_actions():
    report = C.run_cycle(python=sys.executable, runner=lambda command: _completed(command))
    md = C.markdown_report(report)

    assert "Controlled Automation Cycle" in md
    assert "CONTROLLED_READY_WITH_HUMAN_GATES" in md
    assert "Required Human Actions" in md
    assert "Cần bác sĩ kiểm chứng" in md
