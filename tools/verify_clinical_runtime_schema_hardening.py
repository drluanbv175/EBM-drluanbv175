#!/usr/bin/env python3
"""Kiểm clinical_runtime có các chốt hardening tối thiểu.

Verifier này không chứng nhận hệ lâm sàng đã production-ready. Nó chỉ xác nhận
các schema governance đã có đủ hợp đồng máy đọc được cho 3 rủi ro đã phát hiện:
nguồn bị rút, prompt injection trong nguồn truy xuất, và chứng cứ/hướng dẫn xung
đột. Các cổng production thật vẫn cần runtime integration, bác sĩ, pháp lý và bảo
mật duyệt.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CLINICAL_RUNTIME = ROOT / "clinical_runtime"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _check_required(container: dict[str, Any], keys: set[str], label: str) -> tuple[bool, str]:
    missing = sorted(keys - set(container))
    if missing:
        return False, f"{label}: thiếu {', '.join(missing)}"
    return True, f"{label}: đủ {len(keys)}/{len(keys)}"


def check_safety_rules() -> dict[str, Any]:
    path = CLINICAL_RUNTIME / "SAFETY_RULES_SCHEMA.json"
    data = _load_json(path)
    categories = data.get("rule_categories", {})
    examples = data.get("example_rules", [])
    text = _text(path)

    required_categories = {"RETRACTED_SOURCE", "PROMPT_INJECTION", "CONFLICTING_EVIDENCE"}
    ok_categories, detail_categories = _check_required(
        categories,
        required_categories,
        "SAFETY_RULES_SCHEMA.rule_categories",
    )

    found_example_categories = {rule.get("category") for rule in examples if isinstance(rule, dict)}
    ok_examples, detail_examples = _check_required(
        found_example_categories,
        required_categories,
        "SAFETY_RULES_SCHEMA.example_rules",
    )

    markers = [
        "retrieved text as untrusted data",
        "RETRACTED_SOURCE RED alerts",
        "CONFLICTING_EVIDENCE alerts",
        "audit_event",
        "block_release",
        "require_doctor_review",
    ]
    missing_markers = [marker for marker in markers if marker not in text]

    return {
        "name": "safety_rules",
        "status": "PASS" if ok_categories and ok_examples and not missing_markers else "FAIL",
        "details": [detail_categories, detail_examples],
        "missing_markers": missing_markers,
    }


def check_output_schema() -> dict[str, Any]:
    path = CLINICAL_RUNTIME / "OUTPUT_SCHEMA.json"
    data = _load_json(path)
    text = _text(path)

    required_fields = {"source_integrity", "prompt_injection_review", "conflict_review"}
    required = set(data.get("required", []))
    properties = data.get("properties", {})

    ok_required, detail_required = _check_required(
        required,
        required_fields,
        "OUTPUT_SCHEMA.required",
    )
    ok_properties, detail_properties = _check_required(
        properties,
        required_fields,
        "OUTPUT_SCHEMA.properties",
    )

    markers = [
        "retracted_sources_detected",
        "quarantined_source_ids",
        "retrieved_content_treated_as_data",
        "injection_detected",
        "conflicting_evidence_flag",
        "shared_decision_required",
        "approved_for_use",
        "allOf",
    ]
    missing_markers = [marker for marker in markers if marker not in text]

    return {
        "name": "output_schema",
        "status": "PASS" if ok_required and ok_properties and not missing_markers else "FAIL",
        "details": [detail_required, detail_properties],
        "missing_markers": missing_markers,
    }


def check_decision_contract() -> dict[str, Any]:
    path = CLINICAL_RUNTIME / "CLINICAL_DECISION_CONTRACT.json"
    data = _load_json(path)
    text = _text(path)

    output_fields = {
        field.get("name")
        for field in data.get("output_fields", {}).get("fields", [])
        if isinstance(field, dict)
    }
    input_fields = {
        field.get("name")
        for field in data.get("input_fields", {}).get("fields", [])
        if isinstance(field, dict)
    }
    ok_output, detail_output = _check_required(
        output_fields,
        {"source_integrity", "prompt_injection_review", "conflict_review"},
        "CLINICAL_DECISION_CONTRACT.output_fields",
    )
    ok_input, detail_input = _check_required(
        input_fields,
        {"retrieved_content_security_context"},
        "CLINICAL_DECISION_CONTRACT.input_fields",
    )

    markers = [
        "Retrieved content",
        "RETRACTED_SOURCE",
        "PROMPT_INJECTION",
        "CONFLICTING_EVIDENCE",
        "C3 Safety Gate",
        "C7 Human Approval Gate",
        "prevent release_state='approved_for_use'",
    ]
    missing_markers = [marker for marker in markers if marker not in text]

    return {
        "name": "decision_contract",
        "status": "PASS" if ok_output and ok_input and not missing_markers else "FAIL",
        "details": [detail_output, detail_input],
        "missing_markers": missing_markers,
    }


def check_validation_cases() -> dict[str, Any]:
    case_checks = {
        "TC-007_conflicting_guidelines.json": [
            "CONFLICTING_EVIDENCE_DETECTED",
            "expected_conflict_review",
            "conflicting_evidence_flag",
            "shared_decision_required",
        ],
        "TC-008_retracted_source.json": [
            "RETRACTED_SOURCE_DETECTED",
            "expected_source_integrity",
            "expected_rollback",
            "retraction_watch_logged",
        ],
        "TC-010_prompt_injection.json": [
            "PROMPT_INJECTION_DETECTED",
            "expected_prompt_injection_review",
            "retrieved_content_treated_as_data",
            "audit_logged",
        ],
    }
    missing: dict[str, list[str]] = {}
    for filename, markers in case_checks.items():
        path = CLINICAL_RUNTIME / "VALIDATION_CASE_LIBRARY" / filename
        text = _text(path)
        absent = [marker for marker in markers if marker not in text]
        if absent:
            missing[filename] = absent

    return {
        "name": "validation_cases",
        "status": "PASS" if not missing else "FAIL",
        "details": [f"{len(case_checks)} validation cases checked"],
        "missing_markers": missing,
    }


def run_verification() -> dict[str, Any]:
    checks = [
        check_safety_rules(),
        check_output_schema(),
        check_decision_contract(),
        check_validation_cases(),
    ]
    overall = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {
        "overall_status": overall,
        "checks": checks,
        "clinical_runtime_path": str(CLINICAL_RUNTIME),
        "scope": "static governance/schema hardening; not production clinical validation",
        "disclaimer": "Cần bác sĩ kiểm chứng.",
    }


def main() -> int:
    report = run_verification()
    print("Clinical runtime schema hardening")
    print(f"- path: {report['clinical_runtime_path']}")
    for check in report["checks"]:
        mark = "PASS" if check["status"] == "PASS" else "FAIL"
        print(f"- {mark}: {check['name']}")
        for detail in check.get("details", []):
            print(f"  - {detail}")
        missing = check.get("missing_markers")
        if missing:
            print(f"  - missing: {missing}")
    print(f"Overall: {report['overall_status']}")
    print(report["disclaimer"])
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
