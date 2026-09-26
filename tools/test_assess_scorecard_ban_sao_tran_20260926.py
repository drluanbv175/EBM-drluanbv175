"""assess_agent_system.py không ghi đè scorecard TRACK trong git bằng số đo bản sao trần — 26/09/2026.

Đo thật: upgrade_verify chạy trên Cloud hạ scorecard 13 strong → 8 strong + 5 partial (thiếu dữ liệu
OneDrive) và bản đó suýt bị commit. Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "assess_agent_system.py"
_sp = importlib.util.spec_from_file_location("assess_agent_system_bst", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)


def test_ban_sao_tran_khong_ghi_de_mac_dinh():
    assert M.khong_ghi_scorecard_mac_dinh(None, ban_sao_tran=True) is True


def test_may_that_ghi_binh_thuong():
    assert M.khong_ghi_scorecard_mac_dinh(None, ban_sao_tran=False) is False


def test_out_tuong_minh_luon_duoc_ghi():
    assert M.khong_ghi_scorecard_mac_dinh("/tmp/rieng.json", ban_sao_tran=True) is False


def test_main_di_qua_cong_chan_truoc_khi_ghi():
    dong = [x.strip() for x in _TEP.read_text(encoding="utf-8").splitlines()
            if x.strip() and not x.strip().startswith("#")]
    i = dong.index("if khong_ghi_scorecard_mac_dinh(args.out):")
    j = next(k for k, x in enumerate(dong) if x.startswith("out.write_text("))
    assert i < j and "else:" in dong[i:j]
