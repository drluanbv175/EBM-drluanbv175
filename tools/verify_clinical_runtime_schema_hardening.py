#!/usr/bin/env python3
"""Kiểm clinical_runtime có các chốt hardening tối thiểu.

Verifier này không chứng nhận hệ lâm sàng đã production-ready. Nó chỉ xác nhận
các schema governance đã có đủ hợp đồng máy đọc được cho 3 rủi ro đã phát hiện:
nguồn bị rút, prompt injection trong nguồn truy xuất, chứng cứ/hướng dẫn xung
đột, và cổng áp dụng chứng cứ vào ngoại trú. Các cổng production thật vẫn cần
runtime integration, bác sĩ, pháp lý và bảo mật duyệt.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CLINICAL_RUNTIME = ROOT / "clinical_runtime"


def _configure_utf8_stdio() -> None:
    """Keep Vietnamese verifier output printable on Windows legacy consoles."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


_configure_utf8_stdio()


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

    required_fields = {"source_integrity", "prompt_injection_review", "conflict_review", "outpatient_apply_review"}
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
        "outpatient_apply_review",
        "strict_source_gate_passed",
        "safety_netting_present",
        "follow_up_plan_present",
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
        {"source_integrity", "prompt_injection_review", "conflict_review", "outpatient_apply_review"},
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
        "outpatient_apply_review",
        "doctor_final_approval_required",
    ]
    missing_markers = [marker for marker in markers if marker not in text]

    return {
        "name": "decision_contract",
        "status": "PASS" if ok_output and ok_input and not missing_markers else "FAIL",
        "details": [detail_output, detail_input],
        "missing_markers": missing_markers,
    }


def check_validation_cases() -> dict[str, Any]:
    """Kiểm CẤU TRÚC của TỪNG file trong VALIDATION_CASE_LIBRARY/, không chỉ 4/11.

    VÌ SAO CÓ (10/09/2026): README.md tự khai "10 DEMO_TEST cases... all must
    PASS" (nay là 11, xem TC-011), nhưng bản trước chỉ có markers cho
    TC-007/008/010/011 — 7 file (TC-001…006, TC-009) không được BẤT KỲ script
    nào soi tới. `check["status"]` vẫn báo PASS dù 7 fixture đó có thể bị xoá
    rỗng hoặc hỏng cấu trúc mà không ai biết — đúng họ lỗi "cổng nói đã kiểm
    nhưng chỉ kiểm được một phần" (cùng lớp với BH61/BH94/BH98 đã vá ở chỗ
    khác trong repo, lần đầu bắt được TẠI verifier này).
    """
    case_checks = {
        "TC-001_red_flag_emergency.json": [
            '"should_halt_immediately": true',
            "RF-CARDIO-001",
            "RED_FLAG_IMMEDIATE",
            '"expected_guardrail_result": "NOT_RUN"',
        ],
        "TC-002_missing_egfr.json": [
            "MISSING_RENAL_DATA",
            "ELDERLY_BEERS_GABAPENTIN",
            "CẦN eGFR",
            '"expected_guardrail_result": "FAIL"',
        ],
        "TC-003_ckd_polypharmacy.json": [
            "DOSE_ADJUSTMENT_RENAL_METFORMIN",
            "DRUG_INTERACTION_RAMIPRIL_SPIRONOLACTONE_HYPERKALEMIA",
            "DOSE_ADJUSTMENT_RENAL_COLCHICINE",
        ],
        "TC-004_liver_dysfunction.json": [
            "HEPATIC_CONTRAINDICATION_NSAID",
            "HEPATIC_DOSE_REDUCTION_ACETAMINOPHEN",
            "Child-Pugh B",
        ],
        "TC-005_elderly_frailty.json": [
            "BEERS_SULFONYLUREA_ELDERLY",
            "FRAILTY_ADJUSTED_TARGET_HBA1C",
            "STOPP_STATIN_LIMITED_PROGNOSIS",
        ],
        "TC-006_pregnancy_safety.json": [
            "PREGNANCY_CONTRAINDICATION_ACE_INHIBITOR",
            "PREGNANCY_SAFE_ALTERNATIVE_LABETALOL",
            "PREGNANCY_SAFE_ALTERNATIVE_METHYLDOPA",
        ],
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
        "TC-009_unavailable_drug.json": [
            "FORMULARY_UNAVAILABLE_DAPAGLIFLOZIN",
            "LOCAL_ALTERNATIVE_EMPAGLIFLOZIN",
            "PMID 31535729",
            "PMID 32865377",
        ],
        "TC-010_prompt_injection.json": [
            "PROMPT_INJECTION_DETECTED",
            "expected_prompt_injection_review",
            "retrieved_content_treated_as_data",
            "audit_logged",
        ],
        "TC-011_outpatient_apply_gate.json": [
            "OUTPATIENT_APPLY_GATE_INCOMPLETE",
            "expected_outpatient_apply_review",
            "strict_source_gate_passed",
            "safety_netting_present",
            "human_approval_id",
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


# Sổ khai ĐIỂM THI HÀNH cho từng cờ boolean trong CLINICAL_RUNTIME_FLAGS.json —
# khai báo tường minh, không suy đoán (cùng khuôn LY_DO_CHUA_CAI/SKILL_DUNG_SAN
# dùng ở nơi khác trong repo). None = ĐO ĐƯỢC là chưa có điểm thi hành nào
# (10/09/2026). Thêm cờ mới hoặc nối điểm thi hành mới thì sửa dòng tương ứng
# — nếu khai một file mà file đó không thật sự chứa tên cờ, check sẽ tự báo
# "khai có, không tìm thấy" thay vì im lặng tin lời khai.
_DIEM_THI_HANH: dict[str, Path | None] = {
    "require_human_approval": CLINICAL_RUNTIME.parents[0] / "tools" / "kiem_hop_dong_item.py",
    "require_strict_source": CLINICAL_RUNTIME.parents[0] / "tools" / "ensure_strict_source.py",
    "enforce_safety_net_templates": CLINICAL_RUNTIME.parents[0] / "tools" / "kiem_safety_net.py",
}


def check_runtime_flags() -> dict[str, Any]:
    """Cờ TRUE mà không có điểm thi hành nào đọc nó là cờ NÓI DỐI — đúng họ lỗi
    đã vá ở nơi khác trong repo (một lá cờ tuyên bố có thi hành mà không có gì
    thi hành). ADVISORY, KHÔNG chặn overall_status: job CI định kỳ
    (`giam-sat-dinh-ky.yml`) đòi verifier này thoát mã 0 trên bản sao trần, và
    quyết định BẬT/TẮT một cờ AN TOÀN LÂM SÀNG thuộc bác sĩ — không phải việc
    máy tự hạ để "cho xanh". Việc của check này CHỈ là làm sự thật hiện ra
    thay vì nằm im trong field `notes` (từng nói CẢ BA cờ "advisory" dù một
    cờ đã thật sự được thi hành từ 22/08/2026).
    """
    path = CLINICAL_RUNTIME / "CLINICAL_RUNTIME_FLAGS.json"
    data = _load_json(path)
    enforced: list[str] = []
    ornamental: list[str] = []
    for key, value in data.items():
        if key == "notes" or not isinstance(value, bool):
            continue
        site = _DIEM_THI_HANH.get(key, "CHUA_KHAI")
        if site == "CHUA_KHAI":
            ornamental.append(f"{key} (chưa khai điểm thi hành trong _DIEM_THI_HANH)")
        elif site is None:
            if value:
                ornamental.append(f"{key} (đo được: không nơi nào trong repo đọc cờ này)")
        elif not site.is_file() or key not in _text(site):
            ornamental.append(f"{key} (khai {site.name} nhưng không tìm thấy tên cờ trong file đó)")
        else:
            enforced.append(f"{key} -> {site.relative_to(CLINICAL_RUNTIME.parents[0])}")

    return {
        "name": "runtime_flags",
        "status": "ADVISORY" if ornamental else "PASS",
        "details": [f"enforced: {enforced}"],
        "missing_markers": ornamental,
    }


def check_outpatient_apply_gate() -> dict[str, Any]:
    import verify_clinical_practice_apply_gate as apply_gate

    report = apply_gate.run_verification()
    failed = [
        check["name"] for check in report.get("checks", [])
        if check.get("status") != "PASS"
    ]
    return {
        "name": "outpatient_apply_gate",
        "status": "PASS" if report.get("overall_status") == "PASS" else "FAIL",
        "details": [
            "clinical_runtime/CLINICAL_PRACTICE_APPLY_GATE.json present",
            "OUTPUT_SCHEMA requires outpatient_apply_review",
            "approved_for_use blocked without strict source, safety, local feasibility, safety-netting, follow-up, and human approval",
        ],
        "missing_markers": failed,
    }


# ADVISORY báo cáo sự thật nhưng không chặn overall_status (xem
# check_runtime_flags — quyết định bật/tắt một cờ an toàn lâm sàng là của bác
# sĩ, máy không được tự hạ cờ hay tự chặn CI để "cho xanh").
_KHONG_CHAN = {"PASS", "ADVISORY"}


def run_verification() -> dict[str, Any]:
    checks = [
        check_safety_rules(),
        check_output_schema(),
        check_decision_contract(),
        check_validation_cases(),
        check_runtime_flags(),
        check_outpatient_apply_gate(),
    ]
    overall = "PASS" if all(check["status"] in _KHONG_CHAN for check in checks) else "FAIL"
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
        status = check["status"]
        mark = status if status in _KHONG_CHAN else "FAIL"
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
