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
        "runtime_flags",
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


def test_validation_cases_covers_all_11_not_just_4():
    """10/09/2026: bản trước chỉ soi TC-007/008/010/011 (4/11) — 7 file còn lại
    không script nào kiểm dù README tự khai '10 (nay 11) DEMO_TEST... all must
    PASS'. Khoá số lượng để không tụt lại nếu ai rút bớt case_checks."""
    library = V.CLINICAL_RUNTIME / "VALIDATION_CASE_LIBRARY"
    so_file_that = len(list(library.glob("TC-*.json")))
    assert so_file_that == 11

    check = V.check_validation_cases()
    assert check["details"] == ["11 validation cases checked"]


def test_runtime_flags_reports_enforcement_site_for_every_true_flag():
    """10/09/2026: cờ TRUE mà không điểm thi hành nào đọc là cờ nói dối (họ lỗi
    BH94/BH98/BH61 vá ở nơi khác trong repo). Sau bản vá đi kèm
    (ensure_strict_source.py + kiem_hop_dong_item.py + kiem_safety_net.py đều
    đọc cờ thật), cả 3 cờ hiện có trong CLINICAL_RUNTIME_FLAGS.json phải có
    điểm thi hành — nếu ai gỡ một trong ba, test này đỏ trước khi CI đỏ."""
    check = V.check_runtime_flags()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []
    assert len(check["details"][0].split("->")) >= 2  # có ít nhất 1 cờ enforced


def test_outpatient_apply_gate_blocks_uncontrolled_practice_release():
    check = V.check_outpatient_apply_gate()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []
