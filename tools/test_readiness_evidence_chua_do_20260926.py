"""build_research_readiness_evidence.py: mã 2 «chưa đo đủ» của công cụ con ⇒ NOT_MEASURED, không FAIL giả. 26/09/2026."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "build_research_readiness_evidence.py"
_sp = importlib.util.spec_from_file_location("brre_t", _TEP)
M = importlib.util.module_from_spec(_sp)
sys.modules["brre_t"] = M          # dataclass cần module đã đăng ký
_sp.loader.exec_module(M)

KHAI = M.EvidenceCheck(domain="x", command=["a.py"], proves="p", limitation="l", rc2_la_chua_do=True)
KHONG_KHAI = M.EvidenceCheck(domain="y", command=["b.py"], proves="p", limitation="l")


def test_ma_2_da_khai_tren_ban_sao_tran_la_chua_do():
    assert M.phan_loai(KHAI, 2, True) == M.NOT_MEASURED


def test_ma_2_tren_may_that_van_fail():
    assert M.phan_loai(KHAI, 2, False) == "FAIL"


def test_ma_2_cua_cong_cu_khong_khai_van_fail():
    assert M.phan_loai(KHONG_KHAI, 2, True) == "FAIL"


def test_ma_0_va_1():
    assert M.phan_loai(KHAI, 0, True) == "PASS"
    assert M.phan_loai(KHAI, 1, True) == "FAIL"


def _row(status, blocking=True):
    return {"status": status, "blocking": blocking}


def test_trang_thai_tong():
    assert M.trang_thai_tong([_row("PASS")]) == "PASS"
    assert M.trang_thai_tong([_row("PASS"), _row(M.NOT_MEASURED)]) == "MEASUREMENT_INCOMPLETE"
    assert M.trang_thai_tong([_row(M.NOT_MEASURED), _row("FAIL")]) == "FAIL"   # lỗi thật luôn thắng
    assert M.trang_thai_tong([_row("WARN", blocking=False)]) == "PASS"


def test_chi_pipeline_va_audit_duoc_khai_ma_2():
    """Không suy rộng: chỉ công cụ đã thật sự dùng mã 2 cho «chưa đo đủ» mới được khai."""
    khai = sorted(c.command[0] for c in M.CORE_CHECKS if c.rc2_la_chua_do)
    assert khai == ["tools/audit_ebm_system.py", "tools/verify_clinical_evidence_update_pipeline.py"]
