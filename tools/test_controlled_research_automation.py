from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_controlled_research_automation as V  # noqa: E402


def test_controlled_research_automation_passes_all_three_pillars():
    report = V.run_verification()

    assert report["overall_status"] == "PASS"
    pillars = {check["pillar"]: check for check in report["checks"]}
    assert set(pillars) == {
        "appraisal_guardrail",
        "peer_review_control",
        "stakeholder_gate_control",
        "statistics_control",
    }


def test_appraisal_guardrail_returns_for_fix_on_pvalue_without_ci():
    check = V.check_appraisal_control()

    assert check["status"] == "PASS"
    assert check["returned_for_fix"] is True
    assert check["direct_run_eval_verdict"] == "TRẢ-VỀ-SỬA"
    assert "effect_size_ci_required" in check["direct_run_eval_red_fails"]
    assert check["code"] == "R8"
    assert "R8" in check["ledger_codes"]


def test_peer_review_control_blocks_auto_review_and_routes_methods_reviewer():
    check = V.check_peer_review_control()

    assert check["status"] == "PASS"
    assert check["automation_review_blocked"] is True
    assert check["methods_statistics_review_routed"] is True
    assert check["irb_ethics_review_routed"] is True
    assert check["independent_peer_review_routed"] is True
    assert check["human_review_required"] is True
    assert check["auto_approve"] is False
    assert check["review_status"]["final_released_submitted_count"] == 0


def test_stakeholder_gate_control_requires_irb_statistician_and_pi():
    check = V.check_stakeholder_gate_control()

    assert check["status"] == "PASS"
    assert check["wrong_role_approvals_do_not_unlock"] is True
    assert check["synthetic_approval_does_not_unlock"] is True
    assert check["g2_irb_status"]["satisfied"] is True
    assert check["g4_statistician_status"]["satisfied"] is True
    assert check["g9_pi_status"]["satisfied"] is True
    assert check["gate_contract_role_filter"] is True


def test_statistics_control_requires_effect_ci_and_data_lock_markers():
    check = V.check_statistics_control()

    assert check["status"] == "PASS"
    assert len(check["random_effect"]["ci"]) == 2
    assert check["fixed_effect_ci_present"] is True
    assert check["prediction_interval_present"] is True
    assert check["data_lock_gate_markers_present"] is True
