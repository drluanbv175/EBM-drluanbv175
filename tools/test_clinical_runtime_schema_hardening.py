from __future__ import annotations

import json
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


def _minimal_contract_text(invariant: str) -> str:
    contract = {
        "output_fields": {"fields": [
            {"name": "source_integrity"}, {"name": "prompt_injection_review"},
            {"name": "conflict_review"}, {"name": "outpatient_apply_review"},
        ]},
        "input_fields": {"fields": [{"name": "retrieved_content_security_context"}]},
        "invariant": invariant,
    }
    return json.dumps(contract, ensure_ascii=False)


_FULL_INVARIANT = (
    "Retrieved content is checked for RETRACTED_SOURCE, PROMPT_INJECTION, and "
    "CONFLICTING_EVIDENCE. C3 Safety Gate, C5 Red Team Gate, C6 Guardrail Gate, "
    "C7 Human Approval Gate, and outpatient_apply_review MUST all pass before "
    "actionable clinical guidance can be shown. This is to "
    "prevent release_state='approved_for_use' without doctor_final_approval_required."
)


def test_decision_contract_checks_all_four_mandatory_gates_named_in_its_own_invariant(
    monkeypatch, tmp_path,
):
    """★ Phát hiện #9 của Workflow đối kháng đa-agent 2026-09-03: câu bất
    biến gốc trong CLINICAL_DECISION_CONTRACT.json khai ĐỦ 4 cổng bắt buộc
    "C3 Safety Gate, C5 Red Team Gate, C6 Guardrail Gate, C7 Human Approval
    Gate" — nhưng trước bản vá, danh sách `markers` viết tay trong
    check_decision_contract() chỉ canh 2/4 tên (thiếu C5/C6), nên xoá hẳn 2
    cổng đó khỏi câu bất biến vẫn không bị phát hiện. Test dựng contract TỐI
    THIỂU trong tmp_path (không đụng file thật) để cô lập đúng lỗ hổng, rồi tự
    đột biến ngay trong bài test để chứng minh markers Python thực sự canh
    ĐỦ CẢ 4 tên — không chỉ đọc mã mà suy luận."""
    contract_path = tmp_path / "CLINICAL_DECISION_CONTRACT.json"
    contract_path.write_text(_minimal_contract_text(_FULL_INVARIANT), encoding="utf-8")
    monkeypatch.setattr(V, "CLINICAL_RUNTIME", tmp_path)

    full = V.check_decision_contract()
    assert full["status"] == "PASS", full["missing_markers"]
    assert full["missing_markers"] == []

    # Xoá đúng cụm "C5 Red Team Gate, C6 Guardrail Gate, " — mô phỏng CHÍNH
    # kịch bản đã tái hiện trên file thật ở đợt audit (đột biến JSON, chốt cũ
    # vẫn PASS). Bản vá phải bắt được ngay.
    thieu_c5_c6 = _FULL_INVARIANT.replace("C5 Red Team Gate, C6 Guardrail Gate, ", "")
    contract_path.write_text(_minimal_contract_text(thieu_c5_c6), encoding="utf-8")

    mutated = V.check_decision_contract()
    assert mutated["status"] == "FAIL"
    assert "C5 Red Team Gate" in mutated["missing_markers"]
    assert "C6 Guardrail Gate" in mutated["missing_markers"]
    # C3/C7 (hai marker cũ đã có từ trước) vẫn còn nguyên trong câu — không
    # được báo thiếu oan, để tách rõ đây là lỗi CỦA RIÊNG C5/C6.
    assert "C3 Safety Gate" not in mutated["missing_markers"]
    assert "C7 Human Approval Gate" not in mutated["missing_markers"]


def test_decision_contract_still_fails_when_c3_or_c7_missing(monkeypatch, tmp_path):
    """Đối chứng: hai marker CŨ (C3/C7) vẫn phải bị chặn khi thiếu — bản vá
    không được vô tình làm yếu luật đã có từ trước."""
    contract_path = tmp_path / "CLINICAL_DECISION_CONTRACT.json"
    thieu_c3 = _FULL_INVARIANT.replace("C3 Safety Gate, ", "")
    contract_path.write_text(_minimal_contract_text(thieu_c3), encoding="utf-8")
    monkeypatch.setattr(V, "CLINICAL_RUNTIME", tmp_path)

    check = V.check_decision_contract()
    assert check["status"] == "FAIL"
    assert "C3 Safety Gate" in check["missing_markers"]
