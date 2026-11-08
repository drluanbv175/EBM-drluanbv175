"""Chu trình chứng cứ đọc mã CAN_KIEM_RUT_LAI của sổ xác minh — 08/11/2026.

Sổ xác minh nay tách «QUÁ HẠN kiểm rút bài» (đã từng kiểm được, chạy lại là sửa) khỏi «CHƯA kiểm được» (khoá API/nền ngoại
tuyến). Chu trình phải in đúng việc cần làm cho mã mới — không rơi về câu chung «xem phần ③④», càng không khuyên khoá API.
Ngoại tuyến: subprocess giả.
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


def _chay_voi(out_so: str, capsys) -> str:
    def _goi(cmd, **kw):
        cmd = [str(c) for c in cmd]
        if len(cmd) > 1 and "so_xac_minh_nguon.py" in cmd[1] and "--phu-mo-coi" not in cmd and "--quet-ledger" not in cmd:
            return _P(1, out_so)
        return _P(0, "")
    with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", "--nhanh"]), \
            mock.patch.object(ctcc.subprocess, "run", side_effect=_goi), \
            mock.patch.object(ctcc, "_co_dashboard_that", return_value=True):
        ctcc.main()
    return capsys.readouterr().out


def test_ma_kiem_rut_lai_cho_viec_dung_khong_khuyen_khoa(capsys):
    out = _chay_voi("  • 94 mục: QUÁ HẠN kiểm rút bài …\n       [MA] CAN_KIEM_RUT_LAI\n", capsys)
    assert "QUÁ HẠN kiểm rút bài" in out and "--phu-mo-coi" in out
    assert "NCBI_API_KEY" not in out
    assert "Còn nguồn chưa xác minh hoặc hết hạn — xem phần ③④" not in out
