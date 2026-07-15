from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_claude_code_repo_alignment as V  # noqa: E402


def test_claude_code_repo_alignment_overall_passes():
    report = V.run_verification()

    assert report["overall_status"] == "PASS"
    assert {check["name"] for check in report["checks"]} == {
        "root_docs",
        "medical_repo_docs",
        "tracked_contract_files",
        "agent_sync_health",
        "upgrade_verify_wiring",
    }


def test_root_docs_share_required_claude_codex_markers():
    check = V.check_root_docs()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == {}


def test_medical_repo_docs_keep_claude_code_completion_contract():
    check = V.check_medical_docs()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == {}


def test_clinical_runtime_contract_files_are_tracked():
    check = V.check_tracked_contract_files()

    assert check["status"] == "PASS"
    assert check["missing_files"] == []


def test_agent_sync_health_is_green():
    check = V.check_agent_sync_health()

    assert check["status"] == "PASS"
    assert check["source_agents"] >= 40
    assert check["errors"] == []


def test_upgrade_verify_runs_alignment_gate():
    check = V.check_upgrade_verify_wires_alignment()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []
