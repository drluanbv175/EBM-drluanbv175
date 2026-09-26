"""Sổ công cụ orchestrator trên bản sao git trần: script chỉ-OneDrive vắng là ⚪, không phải registry hỏng. 26/09/2026."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from orchestrator import tools_registry as TR  # noqa: E402

_KHONG_TON_TAI = "tools/__khong_ton_tai_20260926.py"


def _so(monkeypatch, ban_sao_tran: bool, rel: str) -> TR.ToolRegistry:
    monkeypatch.setattr(TR, "_ban_sao_tran", lambda: ban_sao_tran)
    reg = TR.ToolRegistry()
    gia = TR.Tool("gia-onedrive", "EBM-Dashboards/tools/__khong_ton_tai.py", "", "giả", ("x",))
    gia2 = TR.Tool("gia-trong-repo", rel, "", "giả", ("x",))
    reg.tools = {"gia-onedrive": gia, "gia-trong-repo": gia2}
    return reg


def test_ban_sao_tran_script_onedrive_la_khong_do_duoc(monkeypatch):
    reg = _so(monkeypatch, True, "tools/upgrade_verify.py")
    assert reg.khong_do_duoc() == ["gia-onedrive"] and reg.validate() == []


def test_ban_sao_tran_van_do_script_trong_repo_bi_thieu(monkeypatch):
    """Script trỏ vào thư mục CÓ trong git mà vắng là registry trỏ sai thật — vẫn phải báo."""
    reg = _so(monkeypatch, True, _KHONG_TON_TAI)
    loi = reg.validate()
    assert len(loi) == 1 and "gia-trong-repo" in loi[0]


def test_may_that_script_onedrive_vang_van_la_loi(monkeypatch):
    reg = _so(monkeypatch, False, "tools/upgrade_verify.py")
    assert reg.khong_do_duoc() == [] and len(reg.validate()) == 1 and "gia-onedrive" in reg.validate()[0]


def test_validate_in_ra_dong_khong_do_duoc():
    nguon = (Path(__file__).resolve().parent / "run_orchestrator.py").read_text(encoding="utf-8")
    dong = [x for x in nguon.splitlines() if x.strip() and not x.strip().startswith("#")]
    assert any("khong_do = orch.tools.khong_do_duoc()" in x for x in dong)
    assert any("không đo được trên bản sao git trần" in x for x in dong)
