# -*- coding: utf-8 -*-
"""BH107 đối chiếu bản doctrine engine ở bố cục LỒNG HOẶC ANH EM (synthesis #19, 26/09/2026).

Lỗi: BH107 ghép cứng `REPO / "medical-ebm-automation"` (vị trí lồng) nên trên phiên Cloud (engine là
ANH EM) chốt KHÔNG BAO GIỜ đọc bản `_CONNECTOR-CHUNG-CU.md` của engine ⇒ phép «hai bản không lệch»
luôn xanh. Tái lập: nới «tối đa **2 lời gọi MCP» thành 9 ở bản engine anh em mà chốt vẫn đạt.

Kiểm trên fixture tạm (bố cục anh em), không đụng hai repo thật.
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "chot_hoi_quy_bai_hoc.py"
_TEN = "chot_bh107_20260926"
_sp = importlib.util.spec_from_file_location(_TEN, _TEP)
C = importlib.util.module_from_spec(_sp)
sys.modules[_TEN] = C
_sp.loader.exec_module(C)

_DOC_GOC = C.REPO / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md"


def _dung(tmp_path: Path, van_ban_engine: str | None) -> Path:
    """Bố cục anh em: cha/EBM-drluanbv175 + cha/medical-ebm-automation (nếu van_ban_engine khác None)."""
    repo = tmp_path / "cha" / "EBM-drluanbv175"
    (repo / ".claude" / "agents").mkdir(parents=True)
    shutil.copy2(_DOC_GOC, repo / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md")
    if van_ban_engine is not None:
        eng = tmp_path / "cha" / "medical-ebm-automation" / ".claude" / "agents"
        eng.mkdir(parents=True)
        (eng / "_CONNECTOR-CHUNG-CU.md").write_text(van_ban_engine, encoding="utf-8", newline="\n")
    return repo


def _goc() -> str:
    return _DOC_GOC.read_text(encoding="utf-8")


def test_duong_engine_do_ca_anh_em(tmp_path):
    repo = _dung(tmp_path, _goc())
    duong = C._bh107_duong_dan(repo)
    assert duong["engine"] == tmp_path / "cha" / "medical-ebm-automation" / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md"
    assert duong["engine"].exists()


def test_anh_em_noi_tran_loi_goi_mcp_thi_do(tmp_path):
    """Đúng ca tái lập của phát hiện: nới trần MCP 2 → 9 ở bản engine anh em."""
    goc = _goc()
    assert "tối đa **2 lời gọi MCP" in goc
    repo = _dung(tmp_path, goc.replace("tối đa **2 lời gọi MCP", "tối đa **9 lời gọi MCP"))
    ok, ct = C._bh107_kiem_hai_ban(C._bh107_duong_dan(repo))
    assert ok is False
    assert "[engine]" in ct or "LỆCH bản gốc" in ct


def test_anh_em_lech_mot_dong_thi_do_lech_ban_goc(tmp_path):
    repo = _dung(tmp_path, _goc() + "\n<!-- lệch -->\n")
    ok, ct = C._bh107_kiem_hai_ban(C._bh107_duong_dan(repo))
    assert ok is False
    assert "LỆCH bản gốc" in ct


def test_anh_em_trung_byte_thi_dat_khong_nhan_kiem_yeu(tmp_path):
    repo = _dung(tmp_path, _goc())
    ok, ct = C._bh107_kiem_hai_ban(C._bh107_duong_dan(repo))
    assert ok is True
    assert not ct.startswith("⚪")


def test_engine_vang_van_dat_nhung_khai_kiem_yeu_hon(tmp_path):
    repo = _dung(tmp_path, None)
    ok, ct = C._bh107_kiem_hai_ban(C._bh107_duong_dan(repo))
    assert ok is True
    assert ct.startswith("⚪ KIỂM YẾU HƠN"), ct
    assert "CHƯA đối chiếu" in ct


def test_chot_day_du_do_khi_repo_la_fixture_anh_em_lech(tmp_path, monkeypatch):
    """Cả chuỗi bh107() (kể cả tự kiểm «răng còn») với REPO trỏ vào fixture anh em lệch ⇒ ĐỎ."""
    repo = _dung(tmp_path, _goc() + "\n<!-- lệch -->\n")
    # _goc_mea() nạp ban_sao_tran.py theo REPO/tools — chép sang fixture để nạp được.
    (repo / "tools").mkdir()
    shutil.copy2(C.REPO / "tools" / "ban_sao_tran.py", repo / "tools" / "ban_sao_tran.py")
    shutil.copy2(C.REPO / "tools" / "nhan_dien_may.py", repo / "tools" / "nhan_dien_may.py")
    monkeypatch.setattr(C, "REPO", repo)
    ok, ct = C.bh107_mcp_consensus_scite_phai_di_qua_cong()
    assert ok is False
    assert "LỆCH bản gốc" in ct


def test_tu_kiem_rang_con_tren_cay_that():
    ok, ct = C._bh107_tu_kiem_rang()
    assert ok is True, ct


def test_chot_that_su_goi_tu_kiem_rang(monkeypatch):
    """Tự kiểm «răng còn» phải được NỐI vào bh107(): răng mất ⇒ chốt ĐỎ, không chỉ là hàm mồ côi."""
    monkeypatch.setattr(C, "_bh107_tu_kiem_rang", lambda: (False, "răng BH107 mất: giả lập"))
    ok, ct = C.bh107_mcp_consensus_scite_phai_di_qua_cong()
    assert ok is False
    assert "răng BH107 mất" in ct
