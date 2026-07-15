from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_clinical_runtime_schema_hardening as V  # noqa: E402


def test_clinical_runtime_hardening_overall_passes():
    report = V.run_verification()

    assert report["overall_status"] == "PASS"
    assert {check["name"] for check in report["checks"]} == {
        "safety_rules",
        "output_schema",
        "decision_contract",
        "validation_cases",
        "outpatient_apply_gate",
    }


def test_safety_rules_cover_retraction_injection_and_conflicts():
    check = V.check_safety_rules()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []


def test_output_schema_requires_machine_readable_hardening_fields():
    check = V.check_output_schema()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []


def test_decision_contract_blocks_actionable_release_for_hardening_alerts():
    check = V.check_decision_contract()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []


def test_validation_cases_pin_expected_hardening_outputs():
    check = V.check_validation_cases()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == {}


def test_outpatient_apply_gate_blocks_uncontrolled_practice_release():
    check = V.check_outpatient_apply_gate()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []
