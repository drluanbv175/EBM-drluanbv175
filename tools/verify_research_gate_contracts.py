#!/usr/bin/env python3
"""verify_research_gate_contracts.py — smoke-test hợp đồng cổng nghiên cứu.

Tool này dựng fixture tạm, gọi trực tiếp `medical-ebm-automation/tools/audit_research_gates.py`
và kiểm 4 bất biến vận hành:
- study mới được resume tự động ở G0, có `GATE_ACTION_QUEUE.json`;
- G2 thiếu IRB thật phải dừng ở người thật;
- G5/G6 thiếu data-lock thật không được chạy phân tích downstream;
- G9 thiếu chữ ký liêm chính thật không được phát hành công bố.

Không ghi vào repo, không dùng dữ liệu thật, không chạm PII.

SỬA 02/11/2026 (CI `giam-sat-dinh-ky` đỏ từ 12/10): từ khi đài kiểm soát CHẤM SỐNG cổng (repo y khoa, 06/10/2026),
G0/G1 kiểu «checkpoint rỗng + artifact một dòng» bị chấm BLOCKED ⇒ người chặn đầu tiên thành G0 thay vì cổng đang kiểm.
G0+G1 nay dựng bằng helper DÙNG CHUNG của repo y khoa `tests/_chuoi_da_chot.py::dung_g0_g1_da_chot` (chốt thật, tự
kiểm chấm sống PASS — sống cùng bộ chấm nên không lạc hậu lần nữa); checkpoint mang khoá «study» và artifact đặt tên
theo mã đề tài như bộ sinh thật. Helper cần pytest + defusedxml + requests (bước CI cài đúng ba gói đó).
"""

from __future__ import annotations

import json
import sys
import tempfile
from contextlib import contextmanager
import pathlib
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
import importlib.util as _ilu_mea  # noqa: E402
_sp_mea = _ilu_mea.spec_from_file_location("_bst_vrgc_early", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst_mea = _ilu_mea.module_from_spec(_sp_mea)
_sp_mea.loader.exec_module(_bst_mea)
REPO = _bst_mea.duong_goc("medical-ebm-automation", ROOT) or (ROOT / "medical-ebm-automation")
REPO_TOOLS = REPO / "tools"
sys.path.insert(0, str(REPO_TOOLS))

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
        "_bst_vrgc", pathlib.Path(__file__).resolve().parent / "ban_sao_tran.py")
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

# Helper G0+G1 chốt thật nằm ở tests/ của repo y khoa; nó import module test (pytest) và engine (defusedxml, requests).
sys.path.insert(0, str(REPO / "tests"))
try:
    from _chuoi_da_chot import dung_g0_g1_da_chot  # noqa: E402
except ModuleNotFoundError as _exc:
    _LY_DO_HELPER = (f"FAIL: không nạp được medical-ebm-automation/tests/_chuoi_da_chot.py ({_exc}) — cần pytest, "
                     "defusedxml, requests (venv ~/.ebm-venv trên máy thật; bước CI cài ghim theo requirements.lock.txt).")
    if __name__ == "__main__":
        raise SystemExit(_LY_DO_HELPER)
    raise


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

def _fail(message: str) -> None:
    raise AssertionError(message)


def _assert(ok: bool, message: str) -> None:
    if not ok:
        _fail(message)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _checkpoint(out_dir: Path, gate: str, study: str, payload: dict[str, Any] | None = None) -> None:
    # Khoá «study» bắt buộc: thiếu nó skill_standards.real_world_signals suy mã đề tài từ tên thư mục tạm và chấm sống
    # các cổng bằng mã SAI (artifact không khớp tên) — xem tests/test_dai_kiem_soat_cham_song_20261102.py (repo y khoa).
    data: dict[str, Any] = {"study": study, "gate": gate, "guardrail": {"passed": True}}
    data.update(payload or {})
    _write_json(out_dir / f"{gate}_checkpoint.json", data)


def _write_required_artifacts(out_dir: Path, gates: list[str], study: str) -> None:
    for gate in gates:
        for ten in REQUIRED_ARTIFACTS.get(gate, []):
            # Bộ sinh thật đặt tên theo mã đề tài (G6_A7_ANALYSIS_SCRIPTS_<mã>.md); bộ chấm sống tìm đúng tên đó.
            name = ten.replace("_AUTO", f"_{study}")
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


def _dung_de_tai(out_dir: Path, study: str, gates_sau_g1: list[str], **meta: Any) -> None:
    """G0+G1 chốt THẬT (helper chung, tự kiểm chấm sống PASS) + checkpoint/artifact tổng hợp cho các cổng sau G1."""
    dung_g0_g1_da_chot(out_dir, study, them_meta={"title": "Đề tài fixture", **meta, "G3": {"effect_size": 0.5}})
    for gate in gates_sau_g1:
        _checkpoint(out_dir, gate, study)
    _write_required_artifacts(out_dir, gates_sau_g1, study)


# Trạng thái ĐẠT của bộ chấm từng cổng (gN_quality_gate) — dùng cho kịch bản «thượng nguồn đã xong».
_DAT_THEO_CONG = {
    "G2": "PASS_G2_APPROVED", "G3": "PASS_G3_CONFIRMED", "G4": "PASS_G4_SAP_LOCKED",
    "G5": "PASS_G5_DATA_LOCKED", "G6": "PASS_G6_SCRIPTS_CONFIRMED", "G7": "PASS_G7_CONFIRMED",
    "G8": "PASS_G8_REVIEW_RECORDED",
}


@contextmanager
def _gia_lap_thuong_nguon_dat(cac_cong: list[str]):
    """Giả lập chấm sống ĐẠT cho `cac_cong` (cùng cách đồ gá tests/_gia_lap_cham_song.py của repo y khoa), cổng khác
    chấm THẬT. Lý do: «G2/G4/G5/G8 đã ký» cần chữ ký sổ cái, mà khoá ký thử chỉ dùng được dưới pytest — script đứng
    riêng không dựng được chuỗi ký thật. Kịch bản G9 chỉ kiểm LOGIC phân loại của đài khi thượng nguồn xong; chính G9
    vẫn chấm thật. Khôi phục hàm thật khi ra khỏi khối."""
    import cong_song as CS  # noqa: PLC0415

    that = CS.trang_thai_song

    def _gia(gate: str, study: str, out_dir: Path, repo_root: Path | None = None) -> dict[str, Any]:
        g = str(gate).upper()
        if g in cac_cong:
            st = _DAT_THEO_CONG[g]
            return CS._ket(g, st, CS.NGUON_SONG, "giả lập: thượng nguồn đã đạt (verifier)", st)
        return that(gate, study, out_dir, repo_root)

    CS.xoa_dem()
    CS.trang_thai_song = _gia
    try:
        yield
    finally:
        CS.trang_thai_song = that
        CS.xoa_dem()


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
        _dung_de_tai(out_dir, "VERIFY-GATE-G2", ["G2"])

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
        _dung_de_tai(out_dir, "VERIFY-GATE-G6", ["G2", "G3", "G4", "G5", "G6"],
                     irb_approved=True, sap_lock_date="2026-07-13")

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
        _dung_de_tai(out_dir, "VERIFY-GATE-G9", ["G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"],
                     irb_approved=True, sap_lock_date="2026-07-13", data_lock_date="2026-07-13",
                     results_final=True)

        with _gia_lap_thuong_nguon_dat(["G2", "G3", "G4", "G5", "G6", "G7", "G8"]):
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
