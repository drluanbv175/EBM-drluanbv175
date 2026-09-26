"""BH56: «công cụ MỒ CÔI» là lỗi trong-repo — không được ⚪ hoá trên bản sao trần (26/09/2026)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "chot_hoi_quy_bai_hoc.py"
_sp = importlib.util.spec_from_file_location("chot_bh56", _TEP)
C = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(C)


def test_mo_coi_tren_ban_tran_van_la_tai_phat():
    ct = "toan_van_guideline MỒ CÔI — không doctrine/nhịp nào gọi (họ BH41)"
    assert C.phan_loai("BH56", False, True, ct) == "tai_phat"


def test_loi_chi_muc_rag_tren_ban_tran_van_ngoai_pham_vi():
    ct = "kho có bài mà CHƯA từng dựng chỉ mục RAG"
    assert C.phan_loai("BH56", False, True, ct) == "ngoai_pham_vi"


def test_doctrine_that_dang_goi_cong_cu_toan_van():
    goc = _TEP.parents[1] / ".claude" / "agents"
    for ten in ("tra-cuu-chung-cu.md", "huong-dan-lam-sang.md"):
        assert "toan_van_guideline" in (goc / ten).read_text(encoding="utf-8"), ten
