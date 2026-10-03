"""Kiểm kê quý gradeBy là KHOẢNG TRỐNG ĐÃ BIẾT (bác sĩ chọn «5b» ngày 03/10/2026) ⇒ dòng ⓘ, không phải việc 👤.

Hai tầng kiểm: hàm dựng dòng (số 0 / đầu ra hỏng ⇒ im) và HÀNH VI của main() thật — tháng đầu quý, công cụ báo
còn item thiếu ⇒ dòng nằm ở `_THONG_TIN`, KHÔNG nằm trong bảng việc ghi ra `--json` (hòm việc một cửa đọc bảng đó).
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_DUONG = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_spec = importlib.util.spec_from_file_location("tu_de_xuat_viec_gradeby_20261003", _DUONG)
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

# Đúng khuôn dòng tóm tắt mà tools/kiem_phan_hang.py in ra.
_RA_KIEM = "  506 item có gradeLevel khác 'na' · 341 CHƯA khai `gradeBy` (145 trong số đó là decision='apply')\n"


def test_dong_kiem_ke_co_so_la_dong_thong_tin_khoang_trong_da_biet() -> None:
    dong = T._dong_kiem_ke_gradeby(_RA_KIEM)
    assert dong is not None
    assert "341 item chưa khai (145 đang apply)" in dong
    assert "KHOẢNG TRỐNG ĐÃ BIẾT" in dong


@pytest.mark.parametrize("ra", ["", "traceback rỗng", _RA_KIEM.replace("341", "0")])
def test_dong_kiem_ke_im_khi_khong_co_so_hoac_bang_0(ra: str) -> None:
    assert T._dong_kiem_ke_gradeby(ra) is None


class _NgayThang10(dt.date):
    @classmethod
    def today(cls):  # noqa: D102 — tháng đầu quý để nhánh kiểm kê chạy
        return cls(2026, 10, 3)


def test_main_dua_gradeby_vao_thong_tin_khong_vao_bang_viec(monkeypatch, tmp_path) -> None:
    def fake_chay(lenh, giay=120, cwd=None):
        return _RA_KIEM if any("kiem_phan_hang.py" in str(x) for x in lenh) else ""

    monkeypatch.setattr(T, "_chay", fake_chay)
    monkeypatch.setattr(T, "DASH", tmp_path / "EBM-Dashboards-khong-ton-tai")
    monkeypatch.setattr(T.dt, "date", _NgayThang10)
    monkeypatch.setattr(T, "_THONG_TIN", [])
    tep = tmp_path / "hom-viec.json"
    monkeypatch.setattr(sys, "argv", ["tu_de_xuat_viec.py", "--gon", "--json", str(tep)])
    try:
        T.main()
    except SystemExit:
        pass
    assert any("Kiểm kê quý gradeBy" in x for x in T._THONG_TIN), "dòng ⓘ gradeBy không xuất hiện"
    assert tep.exists(), "main() không chạy tới bước ghi bảng việc — phép thử không đo được"
    viec = json.loads(tep.read_text(encoding="utf-8"))["viec"]
    assert not any("gradeBy" in v["viec"] for v in viec), "gradeBy vẫn nằm trong bảng việc của bác sĩ"
