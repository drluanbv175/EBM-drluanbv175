#!/usr/bin/env python3
"""verify_research_practical_readiness.py — kiểm thực dụng luồng nghiên cứu có dữ liệu.

Verifier này chạy hoàn toàn trên dữ liệu synthetic trong thư mục tạm, nhưng dùng
đúng code sản xuất của `medical-ebm-automation/tools`:
- raw CSV có PII phải bị intake chặn;
- de-identification tạo bản sạch và không lưu giá trị PII trong report công khai;
- pseudonymization tạo dataset phân tích + bảng ánh xạ bảo vệ ngoài exports/repo;
- cleaning chạy trên bản sao, sinh query log;
- data lock chặn khi thiếu xác nhận, và chỉ khóa khi đủ xác nhận thật;
- audit G6 nhìn thấy data-lock + IRB/SAP thật và cho release G6.

Mục tiêu: chứng minh hệ không chỉ "có tool", mà vận hành được một đường đi tối
thiểu có thể áp dụng cho đề tài thật sau khi bác sĩ/PI cung cấp phê duyệt thật.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import pathlib
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "medical-ebm-automation"
REPO_TOOLS = REPO / "tools"
sys.path.insert(0, str(REPO_TOOLS))
sys.path.insert(0, str(REPO))

# 28/08/2026 — repo y khoa nằm ngoài bản sao git gốc; thiếu thì khai báo rõ
# thay vì ModuleNotFoundError trần (trông như lỗi mã, thật ra thiếu nguyên liệu).
if not (REPO_TOOLS / "audit_research_gates.py").exists():
    # Vòng 4 (bình duyệt đối kháng): thông điệp cũ «FAIL (bỏ qua CÓ KHAI BÁO)» tự mâu
    # thuẫn, và không phân biệt bản trần với máy thật đang hỏng. Nay tách hai nhánh
    # bằng định nghĩa DUY NHẤT ở tools/ban_sao_tran.py; CẢ HAI đều thoát ≠0 vì toàn bộ
    # đối tượng của verifier này nằm trong repo y khoa — không có gì kiểm được thì
    # không được đọc thành «đã kiểm» (khác nhóm hook vốn còn phần trong-repo kiểm đủ).
    import importlib.util as _ilu
    _sp = _ilu.spec_from_file_location(
        "_bst_vrpr", pathlib.Path(__file__).resolve().parent / "ban_sao_tran.py")
    _bst = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_bst)
    if _bst.ban_sao_git_tran(ROOT):
        _LY_DO = ("⚪ NGOÀI PHẠM VI BẢN SAO TRẦN: thiếu medical-ebm-automation/tools/audit_research_gates.py — "
                  "toàn bộ đối tượng của verifier này nằm trong repo y khoa nên không có phần "
                  "trong-repo nào kiểm được; thoát 1 để không ai đọc thành «đã kiểm». "
                  "Chạy trên máy có đủ hai repo.")
    else:
        _LY_DO = ("FAIL: máy này CÓ cây dữ liệu OneDrive nhưng thiếu medical-ebm-automation/tools/audit_research_gates.py — "
                  "repo y khoa hỏng hoặc đồng bộ dở; chạy tools/sync_safety_check.py trước.")
    if __name__ == "__main__":
        raise SystemExit(_LY_DO)
    raise ModuleNotFoundError(_LY_DO)

import audit_research_gates as ARG  # noqa: E402
import clean_research_dataset as CLEAN  # noqa: E402
import deidentify_research_dataset as DEID  # noqa: E402
import import_real_dataset as INTAKE  # noqa: E402
import lock_analysis_dataset as LOCK  # noqa: E402
import pseudonymize_research_dataset as PSEUDO  # noqa: E402

from tests.g5_test_helpers import prepare_locked_g5_study  # noqa: E402


def _configure_utf8_stdio() -> None:
    """Keep Vietnamese practical-readiness output printable on Windows legacy consoles."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


_configure_utf8_stdio()


RAW_ROWS = [
    {
        "ho_ten": "Nguyen Van A",
        "phone": "0912345678",
        "email": "a@example.com",
        "age": "61",
        "sbp": "142",
        "outcome": "1",
        "visit_date": "2026-07-01",
        "note": "call 0912345678 before visit",
    },
    {
        "ho_ten": "Tran Thi B",
        "phone": "0987654321",
        "email": "b@example.com",
        "age": "58",
        "sbp": "136",
        "outcome": "0",
        "visit_date": "2026-07-02",
        "note": "stable",
    },
    {
        "ho_ten": "Le Van C",
        "phone": "0900000000",
        "email": "c@example.com",
        "age": "66",
        "sbp": "151",
        "outcome": "1",
        "visit_date": "2026-07-03",
        "note": "email c@example.com",
    },
]

REQUIRED_GATE_ARTIFACTS = {
    "G0": ["G0_A1_PICO_FINER_AUTO.md"],
    "G1": ["G1_A2_PROTOCOL_DESIGN_AUTO.md"],
    "G2": ["G2_A3_ETHICS_PACKAGE_AUTO.md"],
    "G3": ["G3_A4_SAMPLE_SIZE_AUTO.md"],
    "G4": ["G4_A5_SAP_FINAL_AUTO.md"],
    "G5": ["G5_A6_DATA_MGMT_AUTO.md", "G5_REDCap_dictionary_AUTO.csv"],
    "G6": ["G6_A7_ANALYSIS_SCRIPTS_AUTO.md"],
}


def _assert(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def _write_csv(path: Path, rows: list[dict[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def _write_dictionary(path: Path) -> Path:
    payload = {
        "id_column": "study_subject_id",
        "variables": [
            {"name": "study_subject_id", "type": "text", "required": True},
            {"name": "age", "type": "integer", "required": True, "min": 18, "max": 110},
            {"name": "sbp", "type": "number", "required": True, "min": 60, "max": 260},
            {"name": "outcome", "type": "category", "required": True, "allowed": ["0", "1"]},
            {"name": "visit_date", "type": "date", "required": True, "date_format": "%Y-%m-%d"},
            {"name": "note", "type": "text", "required": False},
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _load_meta(out_dir: Path) -> Dict[str, Any]:
    return json.loads((out_dir / "study_meta.json").read_text(encoding="utf-8"))


def _save_meta(out_dir: Path, meta: Dict[str, Any]) -> None:
    (out_dir / "study_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_checkpoint(out_dir: Path, gate: str) -> None:
    (out_dir / f"{gate}_checkpoint.json").write_text(
        json.dumps({"gate": gate, "guardrail": {"passed": True}}, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_gate_scaffold(out_dir: Path, gates: list[str]) -> None:
    """Dựng checkpoint/artifact tối thiểu để audit không coi G6 là mồ côi."""
    for gate in gates:
        checkpoint = out_dir / f"{gate}_checkpoint.json"
        if not checkpoint.exists():
            _write_checkpoint(out_dir, gate)
        for artifact in REQUIRED_GATE_ARTIFACTS.get(gate, []):
            target = out_dir / artifact
            if target.exists():
                continue
            suffix = "\n" if artifact.endswith(".md") else ""
            target.write_text(
                f"Synthetic {gate} artifact for practical readiness verification.{suffix}",
                encoding="utf-8",
            )


def _restore_temp_cleanup_access(path: Path) -> None:
    """Noi long quyen tren temp synthetic de Windows co the xoa sau khi verifier xong."""
    if not path.exists():
        return
    if os.name == "nt":
        result = subprocess.run(["whoami"], capture_output=True, text=True, check=False, encoding="utf-8", errors="replace")
        principal = (result.stdout or "").strip()
        if result.returncode != 0 or "\\" not in principal:
            user = os.environ.get("USERNAME", "")
            domain = os.environ.get("USERDOMAIN", "")
            principal = f"{domain}\\{user}" if domain and user else user
        if not principal:
            return
        commands = [
            ["icacls", str(path), "/grant:r", f"{principal}:(OI)(CI)F", "/T", "/C"],
            ["icacls", str(path), "/inheritance:e", "/T", "/C"],
        ]
        for command in commands:
            subprocess.run(command, capture_output=True, text=True, check=False, encoding="utf-8", errors="replace")
        return

    for item in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        try:
            item.chmod(0o700 if item.is_dir() else 0o600)
        except OSError:
            pass


def _verify_deidentification_path(exports_root: Path, raw_path: Path) -> Dict[str, Any]:
    study = "VERIFY-PRACTICAL-DEID"
    raw_sha_before = INTAKE._sha256_file(raw_path)

    blocked = INTAKE.import_dataset(study, raw_path, exports_root=exports_root)
    _assert(blocked["status"] == INTAKE.BLOCKED_STATUS, "Raw CSV còn PII phải bị intake chặn")
    _assert(blocked["raw_readonly_path"] is None, "Không được copy raw có PII vào 02_raw_readonly")

    report = DEID.deidentify_dataset(
        study,
        raw_path,
        exports_root=exports_root,
        then_import=True,
    )
    out_dir = exports_root / study
    report_text = _read(out_dir / DEID.REPORT_NAME)

    _assert(INTAKE._sha256_file(raw_path) == raw_sha_before, "Không được sửa file nguồn khi de-identify")
    _assert(report["status"] == DEID.DEIDENTIFIED_STATUS, "De-identification phải tạo dataset sạch")
    _assert(report["then_import"]["status"] == INTAKE.READY_STATUS,
            "Bản đã de-identify phải qua intake an toàn")
    for token in ("Nguyen Van A", "0912345678", "a@example.com"):
        _assert(token not in report_text, "Report de-identification công khai không được chứa PII")

    return {
        "study": study,
        "raw_intake_status": blocked["status"],
        "deidentification_status": report["status"],
        "then_import_status": report["then_import"]["status"],
        "redacted_cells": report["redacted_cell_count"],
    }


def _verify_pseudonymized_lock_path(exports_root: Path, mapping_root: Path,
                                    raw_path: Path) -> Dict[str, Any]:
    study = "VERIFY-PRACTICAL-PSEUDO"
    raw_sha_before = INTAKE._sha256_file(raw_path)

    # Viết dictionary TRƯỚC pseudonymize (đảo thứ tự 08/09/2026) — trước đây
    # dictionary chỉ được viết SAU, ngay trước clean_dataset(), nên pseudonymize
    # (chạy TRƯỚC) không hề biết `visit_date` đã khai "type": "date" và xoá luôn
    # giá trị bằng mẫu PII "date" (thêm 04/09, đúng để bắt ngày rò rỉ trong ghi
    # chú tự do — nhưng áp nhầm cả lên biến ngày NGHIÊN CỨU đã khai tường minh).
    out_dir = exports_root / study
    out_dir.mkdir(parents=True, exist_ok=True)
    dictionary = _write_dictionary(out_dir / "data_dictionary.json")

    report = PSEUDO.pseudonymize_dataset(
        study,
        raw_path,
        exports_root=exports_root,
        mapping_root=mapping_root,
        then_import=True,
        id_prefix="PRAC",
        dictionary_path=dictionary,
    )
    report_text = _read(out_dir / PSEUDO.REPORT_NAME)

    _assert(INTAKE._sha256_file(raw_path) == raw_sha_before, "Không được sửa file nguồn khi pseudonymize")
    _assert(report["status"] == PSEUDO.PSEUDONYMIZED_STATUS, "Pseudonymization phải tạo dataset sạch")
    _assert(report["protected_mapping_created"] is True, "Phải tạo bảng ánh xạ bảo vệ")
    _assert(report["mapping_location"] == "[PROTECTED_EXTERNAL_ROOT]",
            "Report công khai không được lộ đường dẫn mapping")
    _assert(report["then_import"]["status"] == INTAKE.READY_STATUS,
            "Dataset pseudonymized phải qua intake an toàn")
    _assert(not (out_dir / PSEUDO.LINKAGE_MAP_NAME).exists(),
            "Không được lưu linkage map trong exports/study")
    for token in ("Tran Thi B", "0987654321", "b@example.com"):
        _assert(token not in report_text, "Report pseudonymization công khai không được chứa PII")

    mapping_dirs = list((mapping_root / study).glob("*"))
    _assert(mapping_dirs, "Thiếu thư mục mapping bên ngoài")
    mapping_dir = mapping_dirs[0]
    _assert(not str(mapping_dir.resolve()).startswith(str(exports_root.resolve())),
            "Mapping root không được nằm trong exports")
    _assert((mapping_dir / PSEUDO.LINKAGE_MAP_NAME).exists(),
            "Mapping bảo vệ phải có linkage_map.csv")

    # Hành vi TRỌNG TÂM của bản vá 08/09/2026: cột đã khai "type": "date" trong
    # dictionary phải được BÁO RA (không âm thầm) và giá trị THẬT SỰ còn nguyên
    # trong file đã pseudonymize — khác hẳn PII thật (tên/SĐT/email ở trên) vẫn
    # phải bị xoá. Kiểm cả hai chiều để không lặp lại lỗi cũ theo hướng ngược lại
    # (nới lỏng quá tay, để lọt PII thật qua đường "cột đã khai là ngày").
    _assert("visit_date" in report.get("date_columns_exempted_from_date_pattern", []),
            "Report phải khai RÕ cột 'visit_date' được miễn mẫu date — không được im lặng")
    raw_readonly = out_dir / report["then_import"]["raw_readonly_path"]
    pseudonymized_text = _read(raw_readonly)
    for visit_date in ("2026-07-01", "2026-07-02", "2026-07-03"):
        _assert(visit_date in pseudonymized_text,
                f"Cột visit_date đã khai kiểu date phải GIỮ NGUYÊN giá trị ({visit_date}), "
                "không bị xoá như PII thật")
    for token in ("0912345678", "0987654321", "0900000000", "c@example.com"):
        _assert(token not in pseudonymized_text,
                f"PII thật lẫn trong ghi chú tự do vẫn phải bị xoá dù có dictionary ({token})")

    clean = CLEAN.clean_dataset(
        study,
        raw_readonly,
        dictionary_path=dictionary,
        exports_root=exports_root,
    )
    _assert(clean["status"] == CLEAN.CLEAN_READY_STATUS, "Dataset hợp lệ phải clean ready")
    _assert(clean["open_query_count"] == 0, "Dataset hợp lệ không được còn query mở")

    clean_path = out_dir / clean["clean_dataset_path"]
    query_log = out_dir / clean["query_log"]
    blocked_lock = LOCK.lock_dataset(
        study,
        clean_path,
        lock_date="2026-07-13",
        reviewer_role="DATA_GOVERNANCE_QA_REVIEWER",
        reviewer_ref="VERIFY-G5-BLOCKED",
        sap_version="1.0",
        query_log=query_log,
        exports_root=exports_root,
    )
    _assert(blocked_lock["status"] == LOCK.BLOCKED_STATUS,
            "Data lock phải chặn nếu thiếu xác nhận thật")
    _assert(any(item.startswith("missing_confirmation:") for item in blocked_lock["blockers"]),
            "Data lock phải nêu rõ thiếu xác nhận")

    dictionary_dates = frozenset(
        INTAKE._normalize_header(str(rule["name"]))
        for rule in (CLEAN._load_dictionary(dictionary).get("variables") or [])
        if isinstance(rule, dict) and rule.get("type") == "date" and rule.get("name")
    )
    locked_path, quality = prepare_locked_g5_study(
        study,
        raw_readonly,
        exports_root=exports_root,
        repo_root=exports_root.parent,
        extra_date_columns=dictionary_dates,
    )
    locked = json.loads(
        (out_dir / "DATA_LOCK_manifest.json").read_text(encoding="utf-8")
    )
    _assert(locked["status"] == LOCK.LOCKED_STATUS, "Data lock phải khóa khi đủ xác nhận")
    _assert(locked["analysis_allowed"] is True, "Manifest locked phải cho phép phân tích")
    _assert(quality["status"] == "PASS_G5_DATA_LOCKED", "G5 quality phải PASS sau approval")
    _assert(locked_path.exists(), "Dataset khóa phải tồn tại")

    meta = _load_meta(out_dir)
    meta["irb_approved"] = True
    meta["sap_lock_date"] = "2026-07-13"
    meta.setdefault("gate_params", {}).setdefault("G3", {})["effect_size"] = 0.5
    _save_meta(out_dir, meta)
    _write_gate_scaffold(out_dir, ["G0", "G1", "G2", "G3", "G4", "G5", "G6"])

    gate_report = ARG.audit_gates(study, out_dir=out_dir, write=False)
    g6 = next(row for row in gate_report["pipeline_gates"] if row["gate"] == "G6")
    _assert(g6["status"] == ARG.STATUS_LOCKED, "Audit G6 phải nhận data-lock thật")
    _assert(g6["release_contract"]["can_release_to_next_gate"] is True,
            "G6 đã đủ IRB/SAP/data-lock/artifact phải release được")

    return {
        "study": study,
        "pseudonymization_status": report["status"],
        "then_import_status": report["then_import"]["status"],
        "cleaning_status": clean["status"],
        "blocked_lock_status": blocked_lock["status"],
        "locked_status": locked["status"],
        "g6_status": g6["status"],
        "g6_can_release": g6["release_contract"]["can_release_to_next_gate"],
    }


def run_verification() -> Dict[str, Any]:
    """Chạy toàn bộ verifier và trả summary máy-đọc-được."""
    with tempfile.TemporaryDirectory(prefix="ebm_practical_readiness_") as tmp:
        tmp_root = Path(tmp)
        try:
            exports_root = tmp_root / "exports"
            mapping_root = tmp_root / "protected_mapping"
            key_path = tmp_root / "gate_approval_key"
            key_path.write_text("synthetic-practical-readiness-key", encoding="utf-8")
            old_key = os.environ.get("EBM_GATE_KEY_PATH")
            old_pytest = os.environ.get("PYTEST_CURRENT_TEST")
            os.environ["EBM_GATE_KEY_PATH"] = str(key_path)
            os.environ["PYTEST_CURRENT_TEST"] = "synthetic practical readiness verifier"
            raw_path = _write_csv(tmp_root / "raw_with_pii.csv", RAW_ROWS)

            deid = _verify_deidentification_path(exports_root, raw_path)
            pseudo = _verify_pseudonymized_lock_path(exports_root, mapping_root, raw_path)
            return {
                "status": "PASS",
                "kind": "research_practical_readiness_verification",
                "uses_synthetic_data": True,
                "pii_policy": "raw PII blocked; public reports do not store PII values",
                "deidentification": deid,
                "pseudonymization_to_g6": pseudo,
            }
        finally:
            if "old_key" in locals():
                if old_key is None:
                    os.environ.pop("EBM_GATE_KEY_PATH", None)
                else:
                    os.environ["EBM_GATE_KEY_PATH"] = old_key
                if old_pytest is None:
                    os.environ.pop("PYTEST_CURRENT_TEST", None)
                else:
                    os.environ["PYTEST_CURRENT_TEST"] = old_pytest
            _restore_temp_cleanup_access(tmp_root)


def main() -> int:
    summary = run_verification()
    print("Research practical readiness verifier")
    print(f"- PASS de-identification path: {summary['deidentification']['deidentification_status']}")
    print(f"- PASS pseudonymization path: {summary['pseudonymization_to_g6']['pseudonymization_status']}")
    print(f"- PASS cleaning: {summary['pseudonymization_to_g6']['cleaning_status']}")
    print(f"- PASS data lock: {summary['pseudonymization_to_g6']['locked_status']}")
    print(f"- PASS audit G6 release: {summary['pseudonymization_to_g6']['g6_status']}")
    print("KẾT: PASS — luồng dữ liệu nghiên cứu synthetic chạy được tới G6 có data-lock.")
    print("Cần bác sĩ kiểm chứng. Dữ liệu thật vẫn cần IRB/SAP/data-lock và PI xác nhận.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"KẾT: FAIL — {exc}", file=sys.stderr)
        raise SystemExit(1)
