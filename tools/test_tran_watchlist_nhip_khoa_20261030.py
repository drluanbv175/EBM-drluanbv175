"""Đưa chốt BH174 vào CI (30/10/2026): `chot_hoi_quy_bai_hoc.py` không chạy trên CI, chỉ pytest chạy — thiếu tệp này thì
trần watchlist, nhịp khoá và luật (c) của công cụ đồng bộ không có gì canh trên bản sao trần. Nội dung chốt: docstring của
`bh174_tran_watchlist_khong_giet_luot_quet`. Ngoại tuyến, kho tạm, không đụng khoá/alert thật.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent


def _nap(duong: Path, ten: str):
    spec = importlib.util.spec_from_file_location(ten, duong)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod                       # đăng ký TRƯỚC khi exec (dataclass cần)
    spec.loader.exec_module(mod)
    return mod


C = _nap(_TOOLS / "chot_hoi_quy_bai_hoc.py", "chot_bh174_ci")


def test_chot_bh174_xanh():
    ok, chi_tiet = C.bh174_tran_watchlist_khong_giet_luot_quet()
    assert ok, chi_tiet
