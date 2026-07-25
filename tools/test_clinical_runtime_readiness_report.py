from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clinical_runtime_readiness_report as R  # noqa: E402


def test_readiness_report_unlocks_21_of_37_repo_controls_without_production():
    report = R.build_report()
    summary = report["summary"]

    assert summary["total_blockers"] == 37
    assert summary["repo_control_ready_unlocked"] == 21
    assert summary["expected_repo_control_unlocks"] == 21
    assert summary["repo_actionable_without_control"] == 0
    assert summary["requires_human_approval"] == 37
    assert summary["clinical_production_allowed"] is False
    assert summary["ai_clinical_runtime_enabled"] is False
    assert summary["status"] == "BLOCKED_FOR_PRODUCTION"
    assert report["missing_expected_repository_controls"] == []


def test_unlocked_rows_are_still_human_gated_and_control_linked():
    report = R.build_report()
    rows = report["repo_control_ready_blockers"]

    assert {row["blocker_id"] for row in rows} == {
        "SEC-001",
        "SEC-003",
        "SEC-004",
        "SEC-005",
        "SEC-006",
        "SEC-007",
        "SEC-008",
        "DATA-001",
        "DATA-002",
        "DATA-003",
        "DATA-004",
        "CLIN-002",
        "CLIN-003",
        "CLIN-004",
        "OPS-001",
        "OPS-002",
        "OPS-003",
        "OPS-004",
        "PHASE3A-PATIENT-COMMUNICATION-POLICY",
        "PHASE3A-LIVE-GOVERNANCE-PERSISTENCE",
        "AI-001",
    }
    assert all(row["status"] == R.STATUS_REPO_CONTROL_READY for row in rows)
    assert all(row["requires_human_approval"] is True for row in rows)
    assert all(row["control_files"] for row in rows)
    assert all(row["residual_gate"] for row in rows)


def test_markdown_names_21_of_37_and_keeps_safety_boundary():
    markdown = R.markdown_report(R.build_report())

    assert "Repository-control unlocked: `21/37`" in markdown
    assert "Repository-Control Unlocked Blockers (21/37)" in markdown
    assert "Clinical production allowed: `False`" in markdown
    assert "Clinical runtime/chronic-care is still blocked for production" in markdown
