#!/usr/bin/env python3
"""
verify_evidence_pack.py — MRAQ-100 Evidence Pack Verifier V3.2
===============================================================
V3.2 design: Source Scope = Curated (Model 2).
L1 kiểm tra SOURCE_MANIFEST bằng cách GIẢI NÉN source_snapshot.tar.gz
sang thư mục tạm, rồi hash-check từng file trong môi trường tái tạo đó.
Không chấp nhận manifest_count != snapshot_member_count.

CLI:
  python3 tools/verify_evidence_pack.py --root <pack-root>
  python3 tools/verify_evidence_pack.py --verify-zip <directory>

Output JSON:
  run_id, timestamp_utc, verifier_version, source_scope_model,
  source_manifest_count, snapshot_member_count,
  checked, missing, mismatch,
  audit_artifact_count, evidence_status, checksums_status, pass_fail

Bất biến bắt buộc (không thay đổi):
  - KHÔNG ghi PASS nếu còn missing source / hash mismatch / thiếu 18 audit docs
  - KHÔNG ghi PASS nếu manifest_count != snapshot_member_count
  - KHÔNG ghi PASS nếu run_id không đồng nhất
  - KHÔNG PII. Không tạo kết quả giả.
"""

import csv
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone

VERIFIER_VERSION = "3.2.2"
SOURCE_SCOPE_MODEL = "MODEL_2_CURATED_AUDIT_SCOPE"


# ─── Utilities ───────────────────────────────────────────────────────────────

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _new_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    import secrets
    suffix = secrets.token_hex(3).upper()
    return f"MRAQ100-V3.2-VERIFY-{ts}-{suffix}"


def _build_result(run_id, ts, pass_fail, layer_results, findings,
                  source_manifest_count, snapshot_member_count):
    fatal_count = sum(1 for f in findings if f["severity"] == "FATAL")
    warning_count = sum(1 for f in findings if f["severity"] == "WARNING")
    l1 = layer_results.get("L1_source_manifest", {})
    l2 = layer_results.get("L2_evidence_manifest", {})
    l3 = layer_results.get("L3_sha256sums", {})
    l5 = layer_results.get("L5_audit_artifacts", {})
    return {
        "run_id": run_id,
        "timestamp_utc": ts,
        "verifier_version": VERIFIER_VERSION,
        "source_scope_model": SOURCE_SCOPE_MODEL,
        "source_manifest_count": source_manifest_count,
        "snapshot_member_count": snapshot_member_count,
        "checked": l1.get("checked", 0),
        "missing": l1.get("missing", 0),
        "mismatch": l1.get("mismatch", 0),
        "audit_artifact_count": l5.get("present", 0),
        "evidence_status": l2.get("status", "FAIL"),
        "checksums_status": l3.get("status", "FAIL"),
        "pass_fail": pass_fail,
        "fatal_count": fatal_count,
        "warning_count": warning_count,
        "layer_results": layer_results,
        "findings": findings[:20],
        "findings_truncated": max(0, len(findings) - 20),
    }


# ─── Layer 1: SOURCE_MANIFEST (via snapshot extraction) ──────────────────────

def verify_source_manifest_via_snapshot(root: str, findings: list) -> dict:
    """
    L1 V3.2: giải nén source_snapshot.tar.gz → kiểm tra từng file trong
    SOURCE_MANIFEST.csv. Hash phải khớp file đã tái tạo.
    FATAL nếu manifest_count != snapshot_member_count.
    """
    result = {
        "name": "L1_source_manifest_via_snapshot",
        "status": "FAIL",
        "source_manifest_count": 0,
        "snapshot_member_count": 0,
        "total": 0,
        "checked": 0,
        "missing": 0,
        "mismatch": 0,
    }

    manifest_path = os.path.join(root, "MRAQ100_AUDIT", "evidence", "SOURCE_MANIFEST.csv")
    snapshot_path = os.path.join(root, "MRAQ100_AUDIT", "evidence", "source_snapshot.tar.gz")

    if not os.path.isfile(manifest_path):
        findings.append({"severity": "FATAL", "layer": "L1", "check": "manifest_exists",
                         "detail": "SOURCE_MANIFEST.csv không tồn tại"})
        return result

    try:
        with open(manifest_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        findings.append({"severity": "FATAL", "layer": "L1", "check": "manifest_readable",
                         "detail": f"Không đọc được SOURCE_MANIFEST: {e}"})
        return result

    result["source_manifest_count"] = len(rows)
    result["total"] = len(rows)

    if not os.path.isfile(snapshot_path):
        findings.append({"severity": "FATAL", "layer": "L1", "check": "snapshot_exists",
                         "detail": "source_snapshot.tar.gz không tồn tại — không thể tái tạo source"})
        return result

    try:
        with tarfile.open(snapshot_path, "r:gz") as t:
            snap_members = [m for m in t.getmembers() if m.isfile()]
            result["snapshot_member_count"] = len(snap_members)
    except Exception as e:
        findings.append({"severity": "FATAL", "layer": "L1", "check": "snapshot_readable",
                         "detail": f"Không mở được snapshot: {e}"})
        return result

    # FAIL HARD: manifest_count phải bằng snapshot_member_count
    if result["source_manifest_count"] != result["snapshot_member_count"]:
        findings.append({
            "severity": "FATAL", "layer": "L1", "check": "count_mismatch",
            "detail": (
                f"SOURCE_MANIFEST có {result['source_manifest_count']} files, "
                f"snapshot có {result['snapshot_member_count']} members — PHẢI bằng nhau "
                f"(Model 2: manifest = snapshot)"
            )
        })
        return result

    tmp_dir = tempfile.mkdtemp(prefix="mraq_l1_")
    try:
        with tarfile.open(snapshot_path, "r:gz") as t:
            for member in t.getmembers():
                if member.name.startswith("/") or ".." in member.name:
                    findings.append({"severity": "FATAL", "layer": "L1", "check": "path_traversal",
                                     "detail": f"Unsafe snapshot entry: {member.name}"})
                    return result
            t.extractall(tmp_dir)

        for row in rows:
            rel = (row.get("path") or row.get("relative_path") or "").strip()
            expected = row.get("sha256", "").strip()
            if not rel:
                continue

            extracted = os.path.join(tmp_dir, rel)
            if not os.path.isfile(extracted):
                findings.append({"severity": "FATAL", "layer": "L1", "check": "file_in_snapshot",
                                 "path": rel,
                                 "detail": f"File trong manifest nhưng không tái tạo được từ snapshot: {rel}"})
                result["missing"] += 1
                continue

            result["checked"] += 1
            actual = sha256_file(extracted)
            if actual != expected:
                findings.append({
                    "severity": "FATAL", "layer": "L1", "check": "hash_match",
                    "path": rel,
                    "expected": expected[:16] + "...",
                    "actual": actual[:16] + "...",
                    "detail": f"Hash mismatch sau khi tái tạo từ snapshot: {rel}"
                })
                result["mismatch"] += 1

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    if result["missing"] == 0 and result["mismatch"] == 0 and result["total"] > 0:
        result["status"] = "PASS"
    return result


# ─── Layer 2: EVIDENCE_MANIFEST ──────────────────────────────────────────────

def verify_evidence_manifest(root: str, findings: list) -> dict:
    """L2: EVIDENCE_MANIFEST.csv — tất cả files khai báo phải tồn tại và hash khớp."""
    manifest_path = os.path.join(root, "MRAQ100_AUDIT", "evidence", "EVIDENCE_MANIFEST.csv")
    result = {"name": "L2_evidence_manifest", "status": "FAIL",
               "total": 0, "checked": 0, "missing": 0, "mismatch": 0}

    if not os.path.isfile(manifest_path):
        findings.append({"severity": "FATAL", "layer": "L2", "check": "manifest_exists",
                         "detail": "EVIDENCE_MANIFEST.csv không tồn tại"})
        return result

    try:
        with open(manifest_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        findings.append({"severity": "FATAL", "layer": "L2", "check": "manifest_readable",
                         "detail": f"Không đọc được EVIDENCE_MANIFEST: {e}"})
        return result

    result["total"] = len(rows)
    if result["total"] == 0:
        findings.append({"severity": "FATAL", "layer": "L2", "check": "manifest_empty",
                         "detail": "EVIDENCE_MANIFEST.csv rỗng — FAIL"})
        return result

    for row in rows:
        # Hỗ trợ cả "path" (V3.2.1+) và "relative_path" (legacy)
        rel = (row.get("path") or row.get("relative_path") or "").strip()
        expected = row.get("sha256", "").strip()
        if not rel:
            findings.append({"severity": "FATAL", "layer": "L2", "check": "missing_path",
                             "detail": f"Row thiếu trường path: {dict(row)}"})
            continue
        abs_p = os.path.join(root, rel)
        if not os.path.isfile(abs_p):
            findings.append({"severity": "FATAL", "layer": "L2", "check": "file_exists",
                             "path": rel, "detail": f"File thiếu: {rel}"})
            result["missing"] += 1
            continue
        result["checked"] += 1
        actual = sha256_file(abs_p)
        if actual != expected:
            findings.append({"severity": "FATAL", "layer": "L2", "check": "hash_match",
                             "path": rel,
                             "expected": expected[:16] + "...",
                             "actual": actual[:16] + "...",
                             "detail": f"Hash mismatch: {rel}"})
            result["mismatch"] += 1

    # FAIL nếu checked < total (có row bị skip do path rỗng hoặc file thiếu)
    if result["checked"] < result["total"]:
        findings.append({"severity": "FATAL", "layer": "L2", "check": "incomplete_check",
                         "detail": f"checked={result['checked']} < total={result['total']} — không thể PASS"})
    if result["missing"] == 0 and result["mismatch"] == 0 and result["checked"] == result["total"] and result["total"] > 0:
        result["status"] = "PASS"
    return result


# ─── Layer 3: SHA256SUMS ─────────────────────────────────────────────────────

def verify_sha256sums(root: str, findings: list) -> dict:
    """L3: SHA256SUMS.txt — mọi checksum phải khớp. Bỏ qua dòng header/comment."""
    sums_path = os.path.join(root, "MRAQ100_AUDIT", "evidence", "SHA256SUMS.txt")
    result = {"name": "L3_sha256sums", "status": "FAIL",
               "total": 0, "checked": 0, "missing": 0, "mismatch": 0}

    if not os.path.isfile(sums_path):
        findings.append({"severity": "FATAL", "layer": "L3", "check": "sums_exists",
                         "detail": "SHA256SUMS.txt không tồn tại"})
        return result

    pattern = re.compile(r'^([0-9a-fA-F]{64})  (.+)$')
    entries = []
    with open(sums_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip('\n')
            m = pattern.match(line)
            if m:
                entries.append((m.group(1), m.group(2)))

    result["total"] = len(entries)
    for expected_hash, rel_path in entries:
        abs_p = os.path.join(root, rel_path)
        if not os.path.isfile(abs_p):
            findings.append({"severity": "FATAL", "layer": "L3", "check": "file_exists",
                             "path": rel_path, "detail": f"File thiếu: {rel_path}"})
            result["missing"] += 1
            continue
        result["checked"] += 1
        actual = sha256_file(abs_p)
        if actual != expected_hash:
            findings.append({"severity": "FATAL", "layer": "L3", "check": "hash_match",
                             "path": rel_path,
                             "expected": expected_hash[:16] + "...",
                             "actual": actual[:16] + "...",
                             "detail": f"SHA256SUMS mismatch: {rel_path}"})
            result["mismatch"] += 1

    if result["missing"] == 0 and result["mismatch"] == 0 and result["total"] > 0:
        result["status"] = "PASS"
    elif result["total"] == 0:
        findings.append({"severity": "WARNING", "layer": "L3", "check": "sums_empty",
                         "detail": "SHA256SUMS.txt không có dòng checksum nào"})
    return result


# ─── Layer 4: Source Snapshot ─────────────────────────────────────────────────

def verify_source_snapshot(root: str, findings: list) -> dict:
    """L4: source_snapshot.tar.gz — tồn tại, extractable, không rỗng."""
    snapshot_path = os.path.join(root, "MRAQ100_AUDIT", "evidence", "source_snapshot.tar.gz")
    result = {"name": "L4_source_snapshot", "status": "FAIL", "exists": False,
               "extractable": False, "member_count": 0}

    if not os.path.isfile(snapshot_path):
        findings.append({"severity": "FATAL", "layer": "L4", "check": "snapshot_exists",
                         "detail": "source_snapshot.tar.gz không tồn tại"})
        return result

    result["exists"] = True
    try:
        with tarfile.open(snapshot_path, "r:gz") as t:
            members = [m for m in t.getmembers() if m.isfile()]
            result["member_count"] = len(members)
            result["extractable"] = True
    except Exception as e:
        findings.append({"severity": "FATAL", "layer": "L4", "check": "snapshot_extractable",
                         "detail": f"Không mở được snapshot: {e}"})
        return result

    if result["member_count"] == 0:
        findings.append({"severity": "FATAL", "layer": "L4", "check": "snapshot_not_empty",
                         "detail": "source_snapshot.tar.gz rỗng (0 file members)"})
        return result

    result["status"] = "PASS"
    return result


# ─── Layer 5: 18 Audit Artifacts ─────────────────────────────────────────────

AUDIT_FILES_18 = [
    "01_SYSTEM_INVENTORY.md",
    "02_AGENT_REGISTRY_AND_RACI.md",
    "03_MRAQ100_SCORECARD.md",
    "04_ZERO_TOLERANCE_FAIL_REGISTER.md",
    "05_END_TO_END_TEST_REPORT.md",
    "06_ADVERSARIAL_TEST_MATRIX_AND_RESULTS.md",
    "07_EVIDENCE_INTEGRITY_AUDIT.md",
    "08_ETHICS_PRIVACY_DATA_AUDIT.md",
    "09_METHODS_SAP_REPRODUCIBILITY_AUDIT.md",
    "10_TRACEABILITY_MATRIX.md",
    "11_GAP_REGISTER.md",
    "12_RISK_REGISTER.md",
    "13_REMEDIATION_BACKLOG.md",
    "14_ADR_AND_HIGH_RISK_PROPOSALS.md",
    "15_RETEST_REPORT.md",
    "16_SYSTEM_QUALIFICATION_DECISION.md",
    "17_PROJECT_READINESS_TEMPLATE.md",
    "18_EXECUTIVE_SUMMARY.md",
]


def verify_18_audit_artifacts(root: str, findings: list) -> dict:
    """L5: 18 audit docs phải tồn tại trong MRAQ100_AUDIT/."""
    audit_dir = os.path.join(root, "MRAQ100_AUDIT")
    result = {"name": "L5_audit_artifacts", "status": "FAIL",
               "present": 0, "missing": []}

    for fname in AUDIT_FILES_18:
        fpath = os.path.join(audit_dir, fname)
        if os.path.isfile(fpath):
            result["present"] += 1
        else:
            findings.append({"severity": "FATAL", "layer": "L5", "check": "audit_file_exists",
                             "path": fname, "detail": f"Bắt buộc thiếu: {fname}"})
            result["missing"].append(fname)

    if result["present"] == 18 and not result["missing"]:
        result["status"] = "PASS"
    return result


# ─── Master Verifier ─────────────────────────────────────────────────────────

def run_full_verification(root: str, out_path: str) -> dict:
    """
    Chạy đủ 5 layer theo thứ tự.
    L1 tái tạo source từ snapshot — không còn WARNING do file không có trong pack root.
    FAIL toàn bộ nếu bất kỳ layer nào FAIL.
    """
    run_id = _new_run_id()
    ts = datetime.now(timezone.utc).isoformat()
    findings = []
    layer_results = {}

    l1 = verify_source_manifest_via_snapshot(root, findings)
    layer_results["L1_source_manifest"] = {
        "status": l1["status"],
        "source_manifest_count": l1["source_manifest_count"],
        "snapshot_member_count": l1["snapshot_member_count"],
        "total": l1["total"],
        "checked": l1["checked"],
        "missing": l1["missing"],
        "mismatch": l1["mismatch"],
    }

    l2 = verify_evidence_manifest(root, findings)
    layer_results["L2_evidence_manifest"] = {
        "status": l2["status"],
        "total": l2["total"],
        "checked": l2["checked"],
        "missing": l2["missing"],
        "mismatch": l2["mismatch"],
    }

    l3 = verify_sha256sums(root, findings)
    layer_results["L3_sha256sums"] = {
        "status": l3["status"],
        "total": l3["total"],
        "checked": l3["checked"],
        "missing": l3["missing"],
        "mismatch": l3["mismatch"],
    }

    l4 = verify_source_snapshot(root, findings)
    layer_results["L4_source_snapshot"] = {
        "status": l4["status"],
        "exists": l4["exists"],
        "extractable": l4["extractable"],
        "member_count": l4["member_count"],
    }

    l5 = verify_18_audit_artifacts(root, findings)
    layer_results["L5_audit_artifacts"] = {
        "status": l5["status"],
        "present": l5["present"],
        "missing_count": len(l5["missing"]),
    }

    fatal_count = sum(1 for f in findings if f["severity"] == "FATAL")
    all_pass = all(v.get("status") == "PASS" for v in layer_results.values())
    pass_fail = "PASS" if (fatal_count == 0 and all_pass) else "FAIL"

    src_count = l1["source_manifest_count"]
    snap_count = l1["snapshot_member_count"]

    result = _build_result(run_id, ts, pass_fail, layer_results, findings,
                           src_count, snap_count)
    result["root_verified"] = os.path.abspath(root)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


# ─── ZIP Mode ─────────────────────────────────────────────────────────────────

def verify_zip_mode(zip_dir: str, out_path: str) -> dict:
    """
    --verify-zip <dir>: tìm ZIP mới nhất (ưu tiên V3.2 > V3.1 > V3),
    giải nén sang thư mục tạm, chạy run_full_verification().
    """
    zips = glob.glob(os.path.join(zip_dir, "MRAQ100_EVIDENCE_PACK*.zip"))
    if not zips:
        zips = glob.glob(os.path.join(zip_dir, "*.zip"))
    if not zips:
        print(f"FATAL: Không tìm thấy file ZIP nào trong: {zip_dir}", file=sys.stderr)
        sys.exit(2)

    def _zip_key(p):
        n = os.path.basename(p)
        # Order: V3_2_5_ > V3_2_4_ > V3_2_3_ > V3_2_2_ > V3_2_1_ > V3_2_ > V3_1_ > V3_ (longest match first)
        n = n.replace("V3_2_5_", "V3.250_").replace("V3_2_4_", "V3.240_").replace("V3_2_3_", "V3.230_").replace("V3_2_2_", "V3.220_").replace("V3_2_1_", "V3.210_").replace("V3_2_", "V3.200_").replace("V3_1_", "V3.100_").replace("V3_", "V3.000_")
        return n

    zip_path = sorted(zips, key=_zip_key)[-1]
    print(f"  ZIP: {os.path.basename(zip_path)} ({os.path.getsize(zip_path)//1024}KB)")

    tmp_root = tempfile.mkdtemp(prefix="mraq_verify_")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                if name.startswith("/") or ".." in name:
                    print(f"FATAL: Unsafe ZIP entry: {name}", file=sys.stderr)
                    sys.exit(2)
            zf.extractall(tmp_root)

        result = run_full_verification(tmp_root, out_path)
        result["verified_zip"] = os.path.basename(zip_path)
        result["zip_sha256"] = sha256_file(zip_path)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _print_summary(result: dict, out_path: str):
    status_str = "✓ PASS" if result["pass_fail"] == "PASS" else "✗ FAIL"
    print(f"\n{status_str}  [{result['run_id']}]")
    root_info = result.get("root_verified") or result.get("verified_zip", "-")
    print(f"  Root/ZIP: {root_info}")
    print(f"  Scope:    {result['source_scope_model']}")
    print(f"  Manifest: {result['source_manifest_count']} files")
    print(f"  Snapshot: {result['snapshot_member_count']} members")
    for layer_name, lr in result.get("layer_results", {}).items():
        ls = lr.get("status", "?")
        icon = "✓" if ls == "PASS" else "✗"
        extra = ""
        if "source_manifest_count" in lr:
            extra = (f" (manifest={lr['source_manifest_count']}, "
                     f"snapshot={lr['snapshot_member_count']}, "
                     f"{lr.get('checked',0)} checked, "
                     f"{lr.get('missing',0)} missing, "
                     f"{lr.get('mismatch',0)} mismatch)")
        elif "total" in lr and "checked" in lr:
            extra = (f" ({lr.get('checked',0)}/{lr.get('total',0)} checked, "
                     f"{lr.get('missing',0)} missing, {lr.get('mismatch',0)} mismatch)")
        elif "present" in lr:
            extra = f" ({lr.get('present',0)}/18 present)"
        elif "member_count" in lr:
            extra = f" ({lr.get('member_count',0)} members)"
        print(f"  {icon} {layer_name}{extra}")
    print(f"  FATAL:    {result['fatal_count']}")
    print(f"  Warnings: {result['warning_count']}")
    print(f"  Result:   {out_path}")

    all_findings = result.get("findings", [])
    fatal_findings = [f for f in all_findings if f["severity"] == "FATAL"]
    trunc = result.get("findings_truncated", 0)
    if fatal_findings:
        print(f"\nFindings:")
        for f in fatal_findings[:15]:
            print(f"  [{f['severity']}][{f['layer']}] {f['check']}: {f['detail']}")
        if trunc > 0:
            print(f"  ... và {trunc} findings khác (xem JSON)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="MRAQ-100 Evidence Pack Verifier V3.2")
    parser.add_argument("--root", help="Pack root directory")
    parser.add_argument("--verify-zip", dest="zip_dir", help="Directory containing ZIP to verify")
    parser.add_argument("--out", default=None, help="Output JSON path")
    args = parser.parse_args()

    if not args.root and not args.zip_dir:
        parser.error("Cần --root hoặc --verify-zip")

    if args.zip_dir:
        out = args.out or os.path.join(
            os.path.dirname(os.path.abspath(args.zip_dir)), "verifier_result_zip.json"
        )
        result = verify_zip_mode(args.zip_dir, out)
    else:
        out = args.out or os.path.join(
            os.path.abspath(args.root), "MRAQ100_AUDIT", "results", "verifier_result.json"
        )
        result = run_full_verification(args.root, out)

    _print_summary(result, out)
    sys.exit(0 if result["pass_fail"] == "PASS" else 1)


if __name__ == "__main__":
    main()
