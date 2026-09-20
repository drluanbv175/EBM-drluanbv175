"""Bản tin gộp (`khong_can`) không được tính vào «lâu chưa xem lại» — T1-12, 20/09/2026."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("kdt_t", GOC / "tools" / "kiem_do_tuoi_chung_cu.py")
kdt = importlib.util.module_from_spec(sp)
sys.modules["kdt_t"] = kdt
sp.loader.exec_module(kdt)

KC = {"Uptodate": "bản tin gộp", "W24": "bản tin gộp", "PhatAmPhuAm_T_C": "bản tin gộp"}


def test_nhan_ra_ban_tin_gop_theo_lat_cat_hoac_goc():
    assert kdt.la_khong_can("Uptodate", KC) and kdt.la_khong_can("W24", KC)
    assert kdt.la_khong_can("PhatAmPhuAm_T_C", KC)
    assert kdt.la_khong_can("Uptodate_W25", KC), "lát cắt bắt đầu bằng gốc khai khong_can"


def test_chu_de_lam_sang_that_khong_bi_loai():
    assert not kdt.la_khong_can("BenhThanMan_CKD", KC)
    assert not kdt.la_khong_can("SuyTim_TongHop", {})


def test_bang_tuoi_khong_liet_ke_ban_tin_gop_vao_lau_nhat(capsys):
    lau = [("Uptodate", 105), ("W24", 104), ("BenhThanMan_CKD", 100)]
    kdt.in_bang_tuoi(lau, KC)
    out = capsys.readouterr().out
    lau_nhat = [ln for ln in out.splitlines() if "Lâu nhất" in ln][0]
    assert "BenhThanMan_CKD" in lau_nhat and "Uptodate" not in lau_nhat and "W24" not in lau_nhat
    assert "2 bản tin gộp không tính" in out
