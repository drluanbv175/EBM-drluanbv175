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


def _dong_tom_tat(out: str) -> str:
    return [ln for ln in out.splitlines() if "trung vị" in ln][0]


def test_so_qua_han_va_trung_vi_chi_tinh_chu_de_lam_moi_duoc(capsys):
    """20/11/2026: dòng tóm tắt từng in «11 chủ đề quá 35 ngày» trong khi cả 11 là bản tin gộp
    (`khong_can`) và «Lâu nhất» chỉ tới 31 ngày — số đếm và danh sách nói về hai tập khác nhau."""
    lau = [("Uptodate", 166), ("W24", 165), ("W25_NICE", 158), ("Orlistat_AKI_FDA", 31), ("COPD_X", 26), ("THA", 8)]
    kdt.in_bang_tuoi(lau, KC | {"W25": "bản tin gộp"})
    out = capsys.readouterr().out
    tom_tat = _dong_tom_tat(out)
    assert "3 chủ đề" in tom_tat, tom_tat
    assert "0 chủ đề quá" in tom_tat, "bản tin gộp bị đếm vào số chủ đề quá hạn"
    assert "trung vị 26 ngày" in tom_tat, "trung vị bị bản tin gộp kéo lệch"
    gop = [ln for ln in out.splitlines() if "bản tin gộp" in ln]
    assert gop and "3 bản tin gộp" in gop[0] and "3 bản quá" in gop[0], "bản tin gộp phải hiện ở dòng riêng, không bị giấu"
    assert "Lâu nhất" not in out, "không chủ đề làm mới được nào quá hạn thì không in «Lâu nhất»"


def test_chu_de_that_qua_han_van_bao_khi_co_ban_tin_gop(capsys):
    lau = [("Uptodate", 166), ("BenhThanMan_CKD", 50), ("THA", 8)]
    kdt.in_bang_tuoi(lau, KC)
    out = capsys.readouterr().out
    assert "1 chủ đề quá" in _dong_tom_tat(out)
    assert "BenhThanMan_CKD (50ng)" in [ln for ln in out.splitlines() if "Lâu nhất" in ln][0]


def test_chi_co_ban_tin_gop(capsys):
    kdt.in_bang_tuoi([("Uptodate", 166), ("W24", 165)], KC)
    out = capsys.readouterr().out
    assert "0 chủ đề làm mới được" in out and "2 bản tin gộp" in out and "Lâu nhất" not in out
