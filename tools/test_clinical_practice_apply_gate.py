from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_clinical_practice_apply_gate as V  # noqa: E402


def test_clinical_practice_apply_gate_overall_passes():
    report = V.run_verification()

    assert report["overall_status"] == "PASS"
    assert {check["name"] for check in report["checks"]} == {
        "contract_files",
        "approved_fixture",
        "blocks_missing_local_confirmation",
        "blocks_weak_apply",
        "blocks_red_flag",
    }


def test_approved_fixture_passes_all_apply_controls():
    result = V.evaluate_packet(V.approved_fixture())

    assert result["status"] == "PASS"
    assert result["errors"] == []


def test_low_quality_apply_is_blocked():
    packet = V.approved_fixture()
    packet["evidence_basis"][0]["grade_level"] = "low"

    result = V.evaluate_packet(packet)

    assert result["status"] == "FAIL"
    assert any("decision='apply'" in err for err in result["errors"])


def test_missing_local_confirmation_blocks_approved_for_use():
    packet = V.approved_fixture()
    packet["outpatient_apply_review"]["local_applicability_status"] = "needs_unit_confirmation"

    result = V.evaluate_packet(packet)

    assert result["status"] == "FAIL"
    assert any("local_applicability_status" in err for err in result["errors"])


def test_red_flag_blocks_approved_for_use():
    packet = V.approved_fixture()
    packet["red_flags_detected"] = [{"flag": "khó thở cấp", "urgency": "IMMEDIATE"}]

    result = V.evaluate_packet(packet)

    assert result["status"] == "FAIL"
    assert any("red_flags_detected" in err for err in result["errors"])


def test_doctor_review_required_is_not_actionable_but_can_be_safe_packet():
    packet = copy.deepcopy(V.approved_fixture())
    packet["release_state"] = "doctor_review_required"
    packet["audit_trail"].pop("human_approval_id")
    packet["outpatient_apply_review"]["local_applicability_status"] = "needs_unit_confirmation"

    result = V.evaluate_packet(packet)

    assert result["status"] == "PASS"
    assert any("không được coi là actionable" in warn for warn in result["warnings"])
