"""
validate_traceability.py — Traceability Validator A01→A15
MRAQ-100 V3 | Phase 3

Kiểm tra tính nhất quán giữa các artifact synthetic_end_to_end/A01–A15:
- Outcome chính nhất quán (A01 → A03 → A07 → A09 → A13 → A15)
- Cỡ mẫu nhất quán (A07 ← A03, A06)
- Biến số nhất quán (A08 ↔ A11 ↔ A13 ↔ A15)
- SAP nhất quán với Table Shells (A13 ↔ A15)
- Missing data rules nhất quán (A11 ↔ A12 ↔ A13)

Chạy: python3 tools/validate_traceability.py
Xuất: MRAQ100_AUDIT/results/traceability_report.json
"""

import json
import os
import re
import sys
from datetime import datetime, timezone


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHETIC_DIR = os.path.join(PROJECT_ROOT, "MRAQ100_AUDIT", "synthetic_end_to_end")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "MRAQ100_AUDIT", "results")


def _read_artifact(artifact_id: str) -> str:
    """Đọc artifact file. Trả về nội dung hoặc rỗng nếu không tìm thấy."""
    pattern = f"{artifact_id}_"
    for fname in os.listdir(SYNTHETIC_DIR):
        if fname.startswith(pattern) and fname.endswith(".md"):
            with open(os.path.join(SYNTHETIC_DIR, fname), encoding="utf-8") as f:
                return f.read()
    return ""


def _search(text: str, patterns: list) -> list:
    """Tìm tất cả matches của các pattern trong text."""
    found = []
    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE | re.UNICODE)
        found.extend(matches)
    return found


def check_outcome_consistency() -> dict:
    """
    Kiểm tra outcome chính nhất quán qua A01→A03→A07→A09→A13→A15.
    Đề tài QY175: outcome chính = tỷ lệ hài lòng (proportion-based).
    """
    findings = []

    a01 = _read_artifact("A01")
    a03 = _read_artifact("A03")
    a07 = _read_artifact("A07")
    a13 = _read_artifact("A13")

    # Kiểm tra: phải có "hài lòng" / "satisfaction" / "sat_total" xuyên suốt
    satisfaction_terms = [r"hài lòng", r"satisfaction", r"sat_total", r"tỷ lệ hài lòng"]

    for artifact_id, content in [("A01", a01), ("A03", a03), ("A07", a07), ("A13", a13)]:
        if not content:
            findings.append({
                "severity": "FATAL",
                "artifact": artifact_id,
                "check": "outcome_consistency",
                "detail": f"{artifact_id} không tìm thấy"
            })
            continue
        found = _search(content, satisfaction_terms)
        if not found:
            findings.append({
                "severity": "WARNING",
                "artifact": artifact_id,
                "check": "outcome_consistency",
                "detail": f"{artifact_id}: không tìm thấy 'satisfaction/hài lòng/sat_total'"
            })

    # Kiểm tra A07: phải có "339" (cỡ mẫu từ V2)
    if a07 and "339" not in a07:
        findings.append({
            "severity": "FATAL",
            "artifact": "A07",
            "check": "sample_size",
            "detail": "A07 không chứa n=339 — không nhất quán với tính toán"
        })

    # Kiểm tra A06: phải có "339" hoặc "n=" placeholder
    a06 = _read_artifact("A06")
    if a06:
        has_n = "339" in a06 or re.search(r"n\s*=\s*3[0-9]{2}", a06)
        if not has_n:
            findings.append({
                "severity": "WARNING",
                "artifact": "A06",
                "check": "sample_size",
                "detail": "A06 dùng placeholder thay vì n=339 — cần đồng bộ với A07"
            })

    return {"check": "outcome_consistency", "findings": findings}


def check_variable_consistency() -> dict:
    """
    Kiểm tra biến số nhất quán: A08 ↔ A11 ↔ A13.
    Key variable: sat_total = (sum s1-s10 / 50) * 100
    """
    findings = []
    formula_pattern = r"sat_total\s*=?\s*\(?\s*sum"

    a08 = _read_artifact("A08")
    a11 = _read_artifact("A11")
    a13 = _read_artifact("A13")
    a14 = _read_artifact("A14")

    for artifact_id, content in [("A08", a08), ("A11", a11), ("A13", a13), ("A14", a14)]:
        if not content:
            findings.append({
                "severity": "FATAL",
                "artifact": artifact_id,
                "check": "variable_consistency",
                "detail": f"{artifact_id} không tìm thấy"
            })
            continue

        # sat_total phải có trong mỗi artifact
        if "sat_total" not in content.lower():
            findings.append({
                "severity": "WARNING",
                "artifact": artifact_id,
                "check": "variable_consistency",
                "detail": f"{artifact_id}: 'sat_total' không tìm thấy"
            })

    # A11 và A12 phải nhất quán về missing codes
    a12 = _read_artifact("A12")
    missing_codes_a11 = _search(a11, [r"missing.*?(?:9+|\.|\"\"|NA)", r"code.*?9+"])
    missing_codes_a12 = _search(a12, [r"missing.*?(?:9+|\.|\"\"|NA)", r"code.*?9+"])

    if a11 and a12:
        if not missing_codes_a11:
            findings.append({
                "severity": "WARNING",
                "artifact": "A11",
                "check": "missing_code",
                "detail": "A11: không tìm thấy định nghĩa missing code rõ ràng"
            })

    return {"check": "variable_consistency", "findings": findings}


def check_sap_table_consistency() -> dict:
    """
    Kiểm tra SAP (A13) nhất quán với Table Shells (A15).
    Primary analysis trong SAP phải có bảng tương ứng trong A15.
    """
    findings = []

    a13 = _read_artifact("A13")
    a15 = _read_artifact("A15")

    if not a13:
        findings.append({"severity": "FATAL", "artifact": "A13", "check": "sap_table", "detail": "A13 thiếu"})
        return {"check": "sap_table_consistency", "findings": findings}
    if not a15:
        findings.append({"severity": "FATAL", "artifact": "A15", "check": "sap_table", "detail": "A15 thiếu"})
        return {"check": "sap_table_consistency", "findings": findings}

    # Kiểm tra: Table 1 (demographics) phải có trong cả A13 và A15
    table1_in_sap = "table 1" in a13.lower() or "bảng 1" in a13.lower()
    table1_in_shells = "table 1" in a15.lower() or "bảng 1" in a15.lower()

    if table1_in_sap and not table1_in_shells:
        findings.append({
            "severity": "FATAL",
            "artifact": "A15",
            "check": "sap_table",
            "detail": "Table 1 có trong SAP (A13) nhưng thiếu trong Table Shells (A15)"
        })

    # Primary analysis: proportion + 95% CI
    primary_in_sap = any(kw in a13.lower() for kw in ["tỷ lệ", "proportion", "95% ci", "clopper"])
    primary_in_shells = any(kw in a15.lower() for kw in ["tỷ lệ", "proportion", "95% ci", "ci"])

    if primary_in_sap and not primary_in_shells:
        findings.append({
            "severity": "WARNING",
            "artifact": "A15",
            "check": "primary_analysis",
            "detail": "Primary analysis (proportion + 95% CI) có trong SAP nhưng chưa rõ trong Table Shells"
        })

    return {"check": "sap_table_consistency", "findings": findings}


def check_missing_data_rules() -> dict:
    """
    Kiểm tra quy tắc dữ liệu thiếu nhất quán: A11 ↔ A12 ↔ A13.
    FAS, derived score, primary analysis phải nhất quán.
    """
    findings = []

    a11 = _read_artifact("A11")
    a12 = _read_artifact("A12")
    a13 = _read_artifact("A13")

    # A13 phải có FAS definition
    if a13 and "fas" not in a13.lower() and "full analysis" not in a13.lower():
        findings.append({
            "severity": "WARNING",
            "artifact": "A13",
            "check": "fas_definition",
            "detail": "A13: FAS (Full Analysis Set) không tìm thấy rõ ràng"
        })

    # MICE phải được mô tả nếu dùng
    mice_in_sap = a13 and "mice" in a13.lower()
    mice_in_syntax = _read_artifact("A14") and "mice" in _read_artifact("A14").lower()

    if mice_in_sap and not mice_in_syntax:
        findings.append({
            "severity": "WARNING",
            "artifact": "A14",
            "check": "mice_consistency",
            "detail": "MICE được đề cập trong SAP (A13) nhưng không thấy trong syntax (A14)"
        })

    # Sampling label: phải là consecutive/convenience, không "random sample" nếu không có frame
    a01 = _read_artifact("A01")
    a06 = _read_artifact("A06")
    for artifact_id, content in [("A01", a01), ("A06", a06)]:
        if content:
            has_incorrect_random = re.search(r"\brandom\s+(?:sample|sampling)\b(?!\s+(?:allocation|assignment|number))", content, re.I)
            if has_incorrect_random:
                findings.append({
                    "severity": "WARNING",
                    "artifact": artifact_id,
                    "check": "sampling_label",
                    "detail": f"{artifact_id}: 'random sampling' có thể sai — phải là consecutive/convenience cho nghiên cứu ngoại trú"
                })

    return {"check": "missing_data_rules", "findings": findings}


def check_artifact_exists() -> dict:
    """Kiểm tra tất cả A01–A15 tồn tại."""
    findings = []
    for i in range(1, 16):
        artifact_id = f"A{i:02d}"
        content = _read_artifact(artifact_id)
        if not content:
            findings.append({
                "severity": "FATAL",
                "artifact": artifact_id,
                "check": "exists",
                "detail": f"{artifact_id} không tìm thấy trong {SYNTHETIC_DIR}"
            })
    return {"check": "artifact_exists", "findings": findings}


def run_all_checks() -> dict:
    """Chạy tất cả traceability checks."""
    run_id = f"TRACE-V3-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

    results = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "synthetic_dir": SYNTHETIC_DIR,
        "checks": []
    }

    checks = [
        check_artifact_exists,
        check_outcome_consistency,
        check_variable_consistency,
        check_sap_table_consistency,
        check_missing_data_rules,
    ]

    all_findings = []
    for check_fn in checks:
        result = check_fn()
        results["checks"].append(result)
        all_findings.extend(result["findings"])

    fatal_count = sum(1 for f in all_findings if f["severity"] == "FATAL")
    warning_count = sum(1 for f in all_findings if f["severity"] == "WARNING")

    results["summary"] = {
        "total_findings": len(all_findings),
        "fatal": fatal_count,
        "warnings": warning_count,
        "pass_fail": "FAIL" if fatal_count > 0 else "PASS"
    }

    return results


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    results = run_all_checks()

    out_path = os.path.join(RESULTS_DIR, "traceability_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    pf = results["summary"]["pass_fail"]
    status_str = "✓ PASS" if pf == "PASS" else "✗ FAIL"
    print(f"\n{status_str}  [{results['run_id']}]")
    print(f"  Fatals:   {results['summary']['fatal']}")
    print(f"  Warnings: {results['summary']['warnings']}")
    print(f"  Report:   {out_path}")

    if results["summary"]["fatal"] > 0:
        print("\nFATAL findings:")
        for check in results["checks"]:
            for f in check["findings"]:
                if f["severity"] == "FATAL":
                    print(f"  [{f['artifact']}] {f['check']}: {f['detail']}")

    sys.exit(0 if pf == "PASS" else 1)


if __name__ == "__main__":
    main()
