"""Chu trình chứng cứ phải PHỦ bản ghi mồ côi của sổ xác minh — vá 27/09/2026.

`so_xac_minh_nguon.py --vong N` chỉ tái kiểm định danh gom từ dashboard; bản ghi do cầu NC⇄LS/hub tạo trần không bao
giờ được chạm. Đo 27/09: chạy đúng lệnh cũ thêm 220 mục mới, còn 125 mục cũ của toàn sổ đứng yên; `--phu-mo-coi` (có từ
16/08) chưa quy trình nào gọi. Ngoại tuyến: subprocess giả ghi lại mọi lệnh.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import chu_trinh_chung_cu as ctcc  # noqa: E402


class _P:
    def __init__(self, rc, out):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def _chay(nhanh: bool, co_dash: bool, rc_quet: int = 0) -> list[list[str]]:
    """Chạy main() với subprocess giả; trả các lệnh gọi so_xac_minh_nguon theo đúng thứ tự."""
    lenh: list[list[str]] = []

    def _goi(cmd, **kw):
        cmd = [str(c) for c in cmd]
        lenh.append(cmd)
        if "so_xac_minh_nguon.py" in cmd[1] and "--phu-mo-coi" not in cmd and "--quet-ledger" not in cmd:
            return _P(rc_quet, "")
        return _P(0, "")
    argv = ["chu_trinh_chung_cu.py"] + (["--nhanh"] if nhanh else [])
    with mock.patch.object(sys, "argv", argv), mock.patch.object(ctcc.subprocess, "run", side_effect=_goi), \
            mock.patch.object(ctcc, "_co_dashboard_that", return_value=co_dash):
        ctcc.main()
    return [c for c in lenh if "so_xac_minh_nguon.py" in c[1]]


def test_che_do_day_du_phu_mo_coi_sau_luot_quet_dashboard():
    goi = _chay(nhanh=False, co_dash=True)
    assert len(goi) == 3, goi
    assert "--vong" in goi[0] and "--quet-ledger" not in goi[0] and "--phu-mo-coi" not in goi[0], goi
    assert "--quet-ledger" in goi[1] and "--phu-mo-coi" in goi[2], \
        "thứ tự hội tụ: quét dashboard → quét hub → phủ mồ côi (hub tạo bản ghi chưa có ngày xác minh)"


def test_che_do_nhanh_khong_goi_lan_mang_mo_coi():
    assert all("--phu-mo-coi" not in c and "--quet-ledger" not in c for c in _chay(nhanh=True, co_dash=True)), \
        "--nhanh chỉ đọc sổ, không được gọi mạng"


def test_ban_sao_tran_hoac_khong_do_duoc_thi_bo_qua():
    for goi in (_chay(nhanh=False, co_dash=False), _chay(nhanh=False, co_dash=True, rc_quet=3)):
        assert all("--phu-mo-coi" not in c and "--quet-ledger" not in c for c in goi), goi
