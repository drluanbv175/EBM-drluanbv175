"""Đặt-cạnh chỉ rà bản MỚI NHẤT của mỗi lát cắt — vá 24/10/2026.

Bản cũ gom mục `apply` từ mọi dashboard, kể cả bản đã bị phiên bản nối tiếp thay: mục bác sĩ đã hạ khỏi `apply` ở bản mới
vẫn bị đếm vào Đài E-MOI. Luật «cùng lát cắt, ngày mới hơn ⇒ thay bản cũ» lấy từ chính `dang_ky_chu_de.tach_ten`. Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_THU_MUC = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    spec = importlib.util.spec_from_file_location(ten, _THU_MUC / tep)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


DC = _nap("dat_canh_ban_moi_test", "dat_canh_chung_cu_moi.py")
DKC = _nap("dang_ky_chu_de_ban_moi_test", "dang_ky_chu_de.py")


def _p(*ten: str) -> list[Path]:
    return [Path("/kho") / t for t in ten]


def test_cung_lat_cat_chi_giu_ban_moi_nhat():
    ra = DC.chi_ban_moi_nhat(_p("WebDashboard_EBM_VanDeCuThe_BenhMachMauNao_HopNhat_20260614.html",
                                "WebDashboard_EBM_VanDeCuThe_BenhMachMauNao_HopNhat_20261018.html"), DKC.tach_ten)
    assert [f.name for f in ra] == ["WebDashboard_EBM_VanDeCuThe_BenhMachMauNao_HopNhat_20261018.html"]


def test_lat_cat_khac_cung_chu_de_goc_giu_ca_hai():
    """COPD tổng quát và COPD ở đối tượng đặc biệt BỔ SUNG nhau, không thay nhau (docstring tach_ten)."""
    ra = DC.chi_ban_moi_nhat(_p("WebDashboard_EBM_VanDeCuThe_COPD_20261020.html",
                                "WebDashboard_EBM_VanDeCuThe_COPD_DoiTuongDacBiet_DaBenh_20260805.html"), DKC.tach_ten)
    assert len(ra) == 2


def test_ban_tin_khong_co_chu_de_giu_du():
    """Bản tin Uptodate theo tuần không phải phiên bản nối tiếp của nhau."""
    ra = DC.chi_ban_moi_nhat(_p("WebDashboard_EBM_Uptodate_20260607.html",
                                "WebDashboard_EBM_Uptodate_20260713.html"), DKC.tach_ten)
    assert len(ra) == 2


def test_ten_khong_tach_duoc_thi_giu():
    ra = DC.chi_ban_moi_nhat(_p("WebDashboard_khac_le.html"), DKC.tach_ten)
    assert [f.name for f in ra] == ["WebDashboard_khac_le.html"]


def test_nhieu_phien_ban_lay_dung_ngay_lon_nhat():
    ra = DC.chi_ban_moi_nhat(_p(*(f"WebDashboard_EBM_VanDeCuThe_SuyTim_TongHop_2026{d}.html"
                                  for d in ("0804", "0914", "0805", "0811", "0909"))), DKC.tach_ten)
    assert [f.name for f in ra] == ["WebDashboard_EBM_VanDeCuThe_SuyTim_TongHop_20260914.html"]
