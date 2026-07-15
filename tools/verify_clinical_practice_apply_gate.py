#!/usr/bin/env python3
"""Verifier cho cổng áp dụng chứng cứ vào khám ngoại trú.

Mục tiêu: biến nguyên tắc "chỉ áp dụng chứng cứ tốt nhất khi đã qua kiểm soát"
thành kiểm tra máy đọc được. Verifier này KHÔNG chứng nhận hệ lâm sàng đã
production-ready; nó chỉ chặn trạng thái `approved_for_use` khi thiếu nguồn đã
xác minh, kiểm an toàn, bối cảnh Việt Nam, safety-netting, theo dõi hoặc phê
duyệt bác sĩ.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CLINICAL_RUNTIME = ROOT / "clinical_runtime"
DISCLAIMER_RE = re.compile(r"cần bác sĩ kiểm chứng", re.IGNORECASE)
PII_PATTERNS = [
    re.compile(r"\b0\d{9,10}\b"),
    re.compile(r"\b\d{12}\b"),
    re.compile(r"\b\d{2}/\d{2}/\d{4}\b"),
    re.compile(r"\b(MRN|CCCD|CMND|BHYT|số hồ sơ)\b", re.IGNORECASE),
]

REQUIRED_PACKET_FIELDS = {
    "release_state",
    "recommendation_summary",
    "evidence_basis",
    "grade_summary",
    "safety_alerts",
    "red_flags_detected",
    "source_integrity",
    "prompt_injection_review",
    "conflict_review",
    "outpatient_apply_review",
    "audit_trail",
}
REQUIRED_TRUE_FOR_APPROVED = {
    "strict_source_gate_passed",
    "evidence_currency_checked",
    "red_flag_screen_done",
    "safety_review_done",
    "organ_function_checked",
    "special_population_checked",
    "local_feasibility_checked",
    "shared_decision_ready",
    "safety_netting_present",
    "follow_up_plan_present",
    "doctor_final_approval_required",
}
BAD_SOURCE_STATUSES = {"retracted", "quarantined", "unknown"}
WEAK_APPLY_GRADES = {"low", "vlow", "na"}
OK_LOCAL_STATUS_FOR_APPROVED = {"confirmed", "not_applicable"}
OK_ABSOLUTE_EFFECTS_STATUS = {"reported", "not_applicable", "source_not_reported_labeled"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        for v in value.values():
            out.extend(_walk_strings(v))
        return out
    if isinstance(value, list):
        out: list[str] = []
        for v in value:
            out.extend(_walk_strings(v))
        return out
    return []


def _has_pii(packet: dict[str, Any]) -> list[str]:
    hits: list[str] = []
    for s in _walk_strings(packet):
        for pat in PII_PATTERNS:
            if pat.search(s):
                hits.append(s[:120])
                break
    return hits


def approved_fixture() -> dict[str, Any]:
    """Một gói synthetic đủ điều kiện máy đọc được để minh họa đường PASS."""
    return {
        "output_id": "OUT-2026-000011",
        "session_id": "SYNTH-OUTPATIENT-APPLY",
        "timestamp_utc": "2026-07-15T00:00:00Z",
        "release_state": "approved_for_use",
        "recommendation_summary": (
            "Khuyến cáo ngoại trú synthetic đã qua kiểm nguồn, an toàn, bối cảnh Việt Nam, "
            "safety-netting, theo dõi và phê duyệt bác sĩ. Cần bác sĩ kiểm chứng trước khi áp dụng."
        ),
        "evidence_basis": [
            {
                "source_id": "10.1056/NEJMoa000000",
                "source_type": "doi",
                "title": "[SYNTHETIC] guideline-supported outpatient intervention",
                "study_type": "Guideline",
                "grade_level": "mod",
                "decision": "apply",
                "effect_size": "absolute effect reported in source",
                "retraction_checked": True,
                "source_status": "active",
                "source_integrity_note": "strict source gate PASS",
            }
        ],
        "grade_summary": {
            "certainty": "moderate",
            "direction": "benefit",
            "balance_benefits_harms": "benefits likely outweigh harms for selected patients",
            "values_preferences_variability": "shared decision discussion prepared",
            "resource_use": "reviewed for outpatient Vietnam setting",
            "equity": "no flagged inequity",
            "acceptability": "doctor-patient discussion required",
            "feasibility": "confirmed",
        },
        "safety_alerts": [],
        "red_flags_detected": [],
        "source_integrity": {
            "all_sources_checked": True,
            "retracted_sources_detected": [],
            "quarantined_source_ids": [],
            "retraction_watch_logged": True,
        },
        "prompt_injection_review": {
            "retrieved_content_treated_as_data": True,
            "injection_detected": False,
            "sanitized_source_ids": [],
            "audit_logged": True,
        },
        "conflict_review": {
            "conflicting_evidence_flag": False,
            "shared_decision_required": False,
            "conflict_sets": [],
        },
        "outpatient_apply_review": {
            "question_frame": "PICO",
            "strict_source_gate_passed": True,
            "evidence_currency_checked": True,
            "absolute_effects_status": "reported",
            "red_flag_screen_done": True,
            "safety_review_done": True,
            "medication_recommendation_present": True,
            "medication_safety_checked": True,
            "organ_function_checked": True,
            "special_population_checked": True,
            "local_feasibility_checked": True,
            "local_applicability_status": "confirmed",
            "shared_decision_ready": True,
            "safety_netting_present": True,
            "follow_up_plan_present": True,
            "doctor_final_approval_required": True,
        },
        "audit_trail": {
            "requesting_agent": "dieu-phoi-lam-sang",
            "guardrail_result": "PASS",
            "human_approval_id": "HA-2026-000011",
        },
    }


def evaluate_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Trả PASS/FAIL cho một gói clinical output đã có release_state."""
    errors: list[str] = []
    warnings: list[str] = []

    missing = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing:
        errors.append("Thiếu field bắt buộc: " + ", ".join(missing))
        return {"status": "FAIL", "errors": errors, "warnings": warnings}

    release_state = packet.get("release_state")
    approved = release_state == "approved_for_use"
    if not DISCLAIMER_RE.search(str(packet.get("recommendation_summary", ""))):
        errors.append("recommendation_summary thiếu disclaimer 'Cần bác sĩ kiểm chứng'.")

    pii_hits = _has_pii(packet)
    if pii_hits:
        errors.append("Nghi PII trong output: " + "; ".join(pii_hits[:3]))

    evidence = packet.get("evidence_basis")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence_basis rỗng hoặc không phải list.")
        evidence = []

    for idx, item in enumerate(evidence, start=1):
        if not isinstance(item, dict):
            errors.append(f"evidence_basis[{idx}] không phải object.")
            continue
        source_id = str(item.get("source_id", "")).strip()
        source_type = str(item.get("source_type", "")).strip()
        status = str(item.get("source_status", "unknown"))
        decision = str(item.get("decision", ""))
        grade = str(item.get("grade_level", ""))
        if not source_id or not source_type:
            errors.append(f"evidence_basis[{idx}] thiếu source_id/source_type.")
        if approved and status in BAD_SOURCE_STATUSES:
            errors.append(f"evidence_basis[{idx}] source_status={status!r} chặn approved_for_use.")
        if approved and decision == "apply" and grade in WEAK_APPLY_GRADES:
            errors.append(f"evidence_basis[{idx}] decision='apply' với grade_level={grade!r}.")

    source_integrity = packet.get("source_integrity", {})
    if approved:
        if not source_integrity.get("all_sources_checked"):
            errors.append("approved_for_use nhưng source_integrity.all_sources_checked != true.")
        if source_integrity.get("retracted_sources_detected"):
            errors.append("approved_for_use nhưng có retracted_sources_detected.")
        if source_integrity.get("quarantined_source_ids"):
            errors.append("approved_for_use nhưng có quarantined_source_ids.")

    injection = packet.get("prompt_injection_review", {})
    if approved:
        if not injection.get("retrieved_content_treated_as_data"):
            errors.append("approved_for_use nhưng retrieved_content_treated_as_data != true.")
        if injection.get("injection_detected"):
            errors.append("approved_for_use nhưng injection_detected=true.")
        if not injection.get("audit_logged"):
            errors.append("approved_for_use nhưng prompt_injection_review.audit_logged != true.")

    conflict = packet.get("conflict_review", {})
    if approved and conflict.get("conflicting_evidence_flag"):
        errors.append("approved_for_use nhưng conflict_review.conflicting_evidence_flag=true.")
    if approved and conflict.get("shared_decision_required"):
        errors.append("approved_for_use nhưng conflict_review.shared_decision_required=true.")

    red_flags = packet.get("red_flags_detected", [])
    if approved and red_flags:
        errors.append("approved_for_use nhưng red_flags_detected không rỗng.")

    for alert in packet.get("safety_alerts", []):
        if isinstance(alert, dict) and approved and alert.get("severity") == "RED":
            errors.append("approved_for_use nhưng còn RED safety alert: " + str(alert.get("alert_type", "?")))

    review = packet.get("outpatient_apply_review")
    if not isinstance(review, dict):
        errors.append("outpatient_apply_review không phải object.")
        review = {}
    if approved:
        for field in sorted(REQUIRED_TRUE_FOR_APPROVED):
            if review.get(field) is not True:
                errors.append(f"approved_for_use nhưng outpatient_apply_review.{field} != true.")
        if review.get("medication_recommendation_present") and review.get("medication_safety_checked") is not True:
            errors.append("Có khuyến cáo thuốc nhưng medication_safety_checked != true.")
        if review.get("local_applicability_status") not in OK_LOCAL_STATUS_FOR_APPROVED:
            errors.append(
                "approved_for_use nhưng local_applicability_status="
                + repr(review.get("local_applicability_status"))
            )
        if review.get("absolute_effects_status") not in OK_ABSOLUTE_EFFECTS_STATUS:
            errors.append(
                "absolute_effects_status không hợp lệ: "
                + repr(review.get("absolute_effects_status"))
            )

        audit = packet.get("audit_trail", {})
        if audit.get("guardrail_result") != "PASS":
            errors.append("approved_for_use nhưng audit_trail.guardrail_result != PASS.")
        if not str(audit.get("human_approval_id", "")).strip():
            errors.append("approved_for_use nhưng thiếu audit_trail.human_approval_id.")
    else:
        warnings.append(f"release_state={release_state!r}; output không được coi là actionable.")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
    }


def check_contract_files() -> dict[str, Any]:
    errors: list[str] = []
    output_schema = _load_json(CLINICAL_RUNTIME / "OUTPUT_SCHEMA.json")
    contract = _load_json(CLINICAL_RUNTIME / "CLINICAL_DECISION_CONTRACT.json")
    apply_gate = _load_json(CLINICAL_RUNTIME / "CLINICAL_PRACTICE_APPLY_GATE.json")
    tc_011 = _load_json(CLINICAL_RUNTIME / "VALIDATION_CASE_LIBRARY" / "TC-011_outpatient_apply_gate.json")

    required = set(output_schema.get("required", []))
    properties = set(output_schema.get("properties", {}))
    if "outpatient_apply_review" not in required:
        errors.append("OUTPUT_SCHEMA.required thiếu outpatient_apply_review.")
    if "outpatient_apply_review" not in properties:
        errors.append("OUTPUT_SCHEMA.properties thiếu outpatient_apply_review.")

    output_fields = {
        field.get("name")
        for field in contract.get("output_fields", {}).get("fields", [])
        if isinstance(field, dict)
    }
    if "outpatient_apply_review" not in output_fields:
        errors.append("CLINICAL_DECISION_CONTRACT.output_fields thiếu outpatient_apply_review.")

    text_markers = [
        "strict_source_gate_passed",
        "medication_safety_checked",
        "local_feasibility_checked",
        "safety_netting_present",
        "follow_up_plan_present",
        "human_approval_id",
    ]
    combined_text = "\n".join(
        [
            _text(CLINICAL_RUNTIME / "OUTPUT_SCHEMA.json"),
            _text(CLINICAL_RUNTIME / "CLINICAL_DECISION_CONTRACT.json"),
            _text(CLINICAL_RUNTIME / "CLINICAL_PRACTICE_APPLY_GATE.json"),
        ]
    )
    missing_markers = [marker for marker in text_markers if marker not in combined_text]
    if missing_markers:
        errors.append("Thiếu marker hợp đồng: " + ", ".join(missing_markers))

    controls = set(apply_gate.get("required_controls_for_approved_use", []))
    missing_controls = REQUIRED_TRUE_FOR_APPROVED - controls
    if missing_controls:
        errors.append("CLINICAL_PRACTICE_APPLY_GATE thiếu controls: " + ", ".join(sorted(missing_controls)))

    expected = tc_011.get("expected_outpatient_apply_review", {})
    for field in REQUIRED_TRUE_FOR_APPROVED | {"medication_safety_checked"}:
        if field not in expected:
            errors.append(f"TC-011 thiếu expected_outpatient_apply_review.{field}.")

    return {"status": "PASS" if not errors else "FAIL", "errors": errors}


def run_verification() -> dict[str, Any]:
    contract_check = check_contract_files()
    good = evaluate_packet(approved_fixture())

    missing_local = approved_fixture()
    missing_local["outpatient_apply_review"]["local_applicability_status"] = "needs_unit_confirmation"
    missing_local_result = evaluate_packet(missing_local)

    weak_apply = approved_fixture()
    weak_apply["evidence_basis"][0]["grade_level"] = "low"
    weak_apply_result = evaluate_packet(weak_apply)

    red_flag = approved_fixture()
    red_flag["red_flags_detected"] = [{"flag": "đau ngực kiểu ACS", "urgency": "IMMEDIATE"}]
    red_flag_result = evaluate_packet(red_flag)

    checks = [
        {"name": "contract_files", **contract_check},
        {"name": "approved_fixture", **good},
        {
            "name": "blocks_missing_local_confirmation",
            "status": "PASS" if missing_local_result["status"] == "FAIL" else "FAIL",
            "errors": [] if missing_local_result["status"] == "FAIL" else ["missing local confirmation did not block"],
            "blocked_by": missing_local_result["errors"],
        },
        {
            "name": "blocks_weak_apply",
            "status": "PASS" if weak_apply_result["status"] == "FAIL" else "FAIL",
            "errors": [] if weak_apply_result["status"] == "FAIL" else ["weak apply did not block"],
            "blocked_by": weak_apply_result["errors"],
        },
        {
            "name": "blocks_red_flag",
            "status": "PASS" if red_flag_result["status"] == "FAIL" else "FAIL",
            "errors": [] if red_flag_result["status"] == "FAIL" else ["red flag did not block"],
            "blocked_by": red_flag_result["errors"],
        },
    ]
    overall = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {
        "overall_status": overall,
        "checks": checks,
        "scope": "static outpatient apply-gate verifier; not production clinical validation",
        "disclaimer": "Cần bác sĩ kiểm chứng.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", nargs="?", help="Optional clinical output packet JSON to validate")
    args = parser.parse_args()

    if args.packet:
        result = evaluate_packet(_load_json(Path(args.packet)))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1

    report = run_verification()
    print("Clinical practice apply gate")
    for check in report["checks"]:
        print(f"- {check['status']}: {check['name']}")
        if check.get("errors"):
            for err in check["errors"]:
                print(f"  - {err}")
        if check.get("blocked_by"):
            print("  - blocked_by: " + "; ".join(check["blocked_by"][:3]))
    print(f"Overall: {report['overall_status']}")
    print(report["disclaimer"])
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
