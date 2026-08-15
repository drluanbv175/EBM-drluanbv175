#!/usr/bin/env python3
"""verify_research_gate_contracts.py — smoke-test hợp đồng cổng nghiên cứu.

Tool này dựng fixture tạm, gọi trực tiếp `medical-ebm-automation/tools/audit_research_gates.py`
và kiểm 4 bất biến vận hành:
- study mới được resume tự động ở G0, có `GATE_ACTION_QUEUE.json`;
- G2 thiếu IRB thật phải dừng ở người thật;
- G5/G6 thiếu data-lock thật không được chạy phân tích downstream;
- G9 thiếu chữ ký liêm chính thật không được phát hành công bố.

Không ghi vào repo, không dùng dữ liệu thật, không chạm PII.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "medical-ebm-automation"
REPO_TOOLS = REPO / "tools"
sys.path.insert(0, str(REPO_TOOLS))

import audit_research_gates as ARG  # noqa: E402


REQUIRED_ARTIFACTS = {
    "G0": ["G0_A1_PICO_FINER_AUTO.md"],
    "G1": [
        "G1_A1b_PROJECT_CHARTER_AUTO.md",
        "G1_A2_PROTOCOL_DESIGN_AUTO.md",
        "G1_A2b_EVIDENCE_LEDGER_AUTO.md",
        "G1_A13_IMPLEMENTATION_PLAN_AUTO.md",
        "G1_A13b_RISK_REGISTER_AUTO.md",
    ],
    "G2": [
        "G2_A3_ETHICS_PACKAGE_AUTO.md",
        "G2_REGISTRATION_DRAFT_AUTO.json",
        "G2_QUALITY_REPORT.json",
    ],
    "G3": ["G3_A4_SAMPLE_SIZE_AUTO.md"],
    "G4": ["G4_A5_SAP_FINAL_AUTO.md"],
    "G5": [
        "G5_A6_DATA_MGMT_AUTO.md",
        "G5_REDCap_dictionary_AUTO.csv",
        "G5_QUALITY_REPORT.json",
    ],
    "G6": ["G6_A7_ANALYSIS_SCRIPTS_AUTO.md"],
    "G7": ["G7_A8_MANUSCRIPT_AUTO.md"],
    "G8": ["G8_A9_PRESUBMISSION_AUTO.md"],
    "G9": ["G9_A10_AUTHOR_INTEGRITY_AUTO.md"],
}

CONFIRMED_G1_PARAMS = {
    "design": "rct",
    "design_confirmed": True,
    "objectives": ["Mục tiêu fixture đã chốt"],
    "primary_outcome": "Kết cục chính fixture tại 12 tuần",
    "population": "Quần thể fixture",
    "setting": "Bệnh viện fixture",
    "study_period": "2027-2028",
    "feasibility_confirmed": True,
    "evidence_review_confirmed": True,
    "reviewed_by_role": "methodologist",
    "reviewed_at": "2026-07-27T10:00:00+07:00",
}


def _fail(message: str) -> None:
    raise AssertionError(message)


def _assert(ok: bool, message: str) -> None:
    if not ok:
        _fail(message)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _checkpoint(out_dir: Path, gate: str, payload: dict[str, Any] | None = None) -> None:
    data: dict[str, Any] = {"gate": gate, "guardrail": {"passed": True}}
    if gate == "G1":
        data["quality_gate"] = {
            "status": "PASS_G1_CONFIRMED",
            "pending_actions": [],
        }
    data.update(payload or {})
    _write_json(out_dir / f"{gate}_checkpoint.json", data)


def _write_required_artifacts(out_dir: Path, gates: list[str]) -> None:
    for gate in gates:
        for name in REQUIRED_ARTIFACTS.get(gate, []):
            if name.endswith(".json"):
                _write_json(
                    out_dir / name,
                    {
                        "kind": "synthetic_fixture",
                        "gate": gate,
                        "disclaimer": "Cần bác sĩ kiểm chứng.",
                    },
                )
                continue
            suffix = "\n" if name.endswith(".md") else ""
            (out_dir / name).write_text(f"synthetic fixture for {gate}{suffix}", encoding="utf-8")


def _gate(report: dict[str, Any], gate: str) -> dict[str, Any]:
    return next(row for row in report["pipeline_gates"] if row["gate"] == gate)


def _verify_new_study_auto_resume() -> None:
    with tempfile.TemporaryDirectory(prefix="ebm_gate_contract_new_") as tmp:
        out_dir = Path(tmp)
        report = ARG.audit_gates(
            "VERIFY-GATE-NEW",
            out_dir=out_dir,
            topic="Tỷ lệ kiểm soát huyết áp",
            write=True,
        )

        queue_path = out_dir / ARG.ACTION_QUEUE_JSON
        _assert(queue_path.exists(), "Thiếu GATE_ACTION_QUEUE.json cho study mới")
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        _assert(queue["resume_contract"] == report["resume_contract"],
                "Action queue JSON không khớp resume_contract trong report")
        _assert(report["next_agent_action"]["gate"] == "G0",
                "Study mới phải gợi ý agent chạy G0 trước")
        _assert(report["resume_contract"]["mode"] == "AUTO_RUN_ALLOWED",
                "Study mới phải cho phép resume tự động ở G0")
        _assert(all("release_contract" in row for row in report["pipeline_gates"]),
                "Mỗi cổng phải có release_contract")


def _verify_g2_human_irb_stop() -> None:
    with tempfile.TemporaryDirectory(prefix="ebm_gate_contract_g2_") as tmp:
        out_dir = Path(tmp)
        _write_json(out_dir / "study_meta.json", {
            "title": "Đề tài fixture",
            "design_code": "rct",
            "gate_params": {
                "G1": CONFIRMED_G1_PARAMS,
                "G3": {"effect_size": 0.5},
            },
        })
        for gate in ["G0", "G1", "G2"]:
            _checkpoint(out_dir, gate)
        _write_required_artifacts(out_dir, ["G0", "G1", "G2"])

        report = ARG.audit_gates("VERIFY-GATE-G2", out_dir=out_dir, write=False)
        g2 = _gate(report, "G2")
        _assert(g2["status"] == ARG.STATUS_NEEDS_REAL, "G2 thiếu IRB thật phải ở trạng thái NEEDS_REAL")
        _assert(g2["release_contract"]["can_release_to_next_gate"] is False,
                "G2 thiếu IRB không được release downstream")
        _assert(report["resume_contract"]["mode"] == "HUMAN_GATE_REQUIRED",
                "G2 thiếu IRB phải chặn resume tự động")
        _assert(report["resume_contract"]["human_blocker"]["gate"] == "G2",
                "Human blocker đầu tiên phải là G2")


def _verify_g6_data_lock_stop() -> None:
    with tempfile.TemporaryDirectory(prefix="ebm_gate_contract_g6_") as tmp:
        out_dir = Path(tmp)
        _write_json(out_dir / "study_meta.json", {
            "title": "Đề tài fixture",
            "design_code": "rct",
            "irb_approved": True,
            "sap_lock_date": "2026-07-13",
            "gate_params": {
                "G1": CONFIRMED_G1_PARAMS,
                "G3": {"effect_size": 0.5},
            },
        })
        gates = ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]
        for gate in gates:
            _checkpoint(out_dir, gate)
        _write_required_artifacts(out_dir, gates)

        report = ARG.audit_gates("VERIFY-GATE-G6", out_dir=out_dir, write=False)
        g5 = _gate(report, "G5")
        g6 = _gate(report, "G6")
        _assert(g5["status"] == ARG.STATUS_NEEDS_REAL,
                "G5 thiếu data-lock thật phải NEEDS_REAL")
        _assert(g6["status"] == ARG.STATUS_NEEDS_REAL, "G6 thiếu data-lock thật phải NEEDS_REAL")
        _assert("dataset phân tích đã khóa" in g6["release_contract"]["blockers"],
                "G6 phải nêu blocker data-lock thật")
        _assert(g6["release_contract"]["responsible_actor"] == "human_pi_or_data_manager",
                "G6 thiếu data-lock phải giao cho PI/data manager")
        _assert(report["resume_contract"]["human_blocker"]["gate"] == "G5",
                "Data-lock nay thuộc hard gate G5 nên human blocker đầu tiên phải là G5")


def _verify_g9_integrity_stop() -> None:
    with tempfile.TemporaryDirectory(prefix="ebm_gate_contract_g9_") as tmp:
        out_dir = Path(tmp)
        _write_json(out_dir / "study_meta.json", {
            "title": "Đề tài fixture",
            "design_code": "rct",
            "irb_approved": True,
            "sap_lock_date": "2026-07-13",
            "data_lock_date": "2026-07-13",
            "results_final": True,
            "gate_params": {
                "G1": CONFIRMED_G1_PARAMS,
                "G3": {"effect_size": 0.5},
            },
        })
        gates = ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]
        for gate in gates:
            _checkpoint(out_dir, gate)
        _write_required_artifacts(out_dir, gates)

        report = ARG.audit_gates("VERIFY-GATE-G9", out_dir=out_dir, write=False)
        g9 = _gate(report, "G9")
        _assert(g9["status"] == ARG.STATUS_NEEDS_REAL, "G9 thiếu chữ ký liêm chính phải NEEDS_REAL")
        _assert("COI/tài trợ/đóng góp tác giả/khai báo AI đã ký" in g9["release_contract"]["blockers"],
                "G9 phải nêu blocker chữ ký liêm chính")
        _assert(g9["release_contract"]["can_release_to_next_gate"] is False,
                "G9 thiếu liêm chính không được release")
        _assert(report["resume_contract"]["human_blocker"]["gate"] == "G9",
                "Human blocker đầu tiên phải là G9")


def main() -> int:
    checks = [
        ("study mới resume G0", _verify_new_study_auto_resume),
        ("G2 dừng IRB thật", _verify_g2_human_irb_stop),
        ("G5/G6 dừng data-lock thật", _verify_g6_data_lock_stop),
        ("G9 dừng liêm chính thật", _verify_g9_integrity_stop),
    ]
    print("Research gate contract verifier")
    for label, fn in checks:
        fn()
        print(f"- PASS {label}")
    print("KẾT: PASS — action queue, resume contract và release contract hoạt động.")
    print("Cần bác sĩ kiểm chứng. Đây là kiểm cấu trúc bằng fixture synthetic, không thay phê duyệt thật.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"KẾT: FAIL — {exc}", file=sys.stderr)
        raise SystemExit(1)
