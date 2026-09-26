"""verify_clinical_evidence_update_pipeline: FAIL → NOT_MEASURED chỉ khi thiếu tệp chỉ-OneDrive trên bản sao trần. 26/09/2026."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "verify_clinical_evidence_update_pipeline.py"
_sp = importlib.util.spec_from_file_location("vcep_chua_do", _TEP)
M = importlib.util.module_from_spec(_sp)
sys.modules[_sp.name] = M          # @dataclass cần module có trong sys.modules
_sp.loader.exec_module(M)


def _row(evidence: str, status: str = "FAIL") -> "M.CheckResult":
    return M.CheckResult("x", status, evidence, "p", "l")


def _thieu(rel: str) -> str:
    return f"THIẾU file {M.ROOT / rel}"


def test_thieu_chi_onedrive_tren_ban_sao_tran_la_chua_do():
    r = M.chuyen_khong_do_duoc(_row(_thieu("EBM_MASTER/tools/sync_all.py")), True)
    assert r.status == M.NOT_MEASURED


def test_may_that_van_fail():
    assert M.chuyen_khong_do_duoc(_row(_thieu("EBM_MASTER/tools/sync_all.py")), False).status == "FAIL"


def test_thieu_tep_trong_git_van_fail():
    assert M.chuyen_khong_do_duoc(_row(_thieu("tools/upgrade_verify.py")), True).status == "FAIL"


def test_lech_noi_dung_van_fail_du_co_thieu_onedrive():
    ev = _thieu("dashboard_mockups/templates/a.html") + "; b.html: thiếu marker: X"
    assert M.chuyen_khong_do_duoc(_row(ev), True).status == "FAIL"


def test_pass_giu_nguyen():
    assert M.chuyen_khong_do_duoc(_row("ok", "PASS"), True).status == "PASS"
