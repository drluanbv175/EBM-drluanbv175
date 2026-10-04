#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cảm biến sản lượng giám sát: tín hiệu «tầng thứ bậc trống» (04/10/2026).

VÌ SAO CÓ. Ngưỡng «mù» của `kiem_san_luong_giam_sat.py` tính TỔNG 4 tầng, nên tầng «mới vào PubMed» (không lọc thiết kế) che
mất chủ đề có ba tầng thứ bậc gần như trống. Đo 04/10: 10 chủ đề không mù có 0 tổng quan và guideline+SR+RCT ≤ 1 trong 90
ngày (statin, CKD, COPD…). Test khoá: phân loại, không đổi mã thoát, in được từ tệp cũ, và chu trình nêu thành việc 🟠.
Ngoại tuyến (fetch giả, subprocess giả).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


SL = _nap("_sl_tbt", "kiem_san_luong_giam_sat.py")


def _kq(loai="ON", g=0, s=0, r=0, m=40, do_duoc=True, bo_sr=False):
    tang = [{"tang": "guideline", "dem": g}, {"tang": "rct", "dem": r}, {"tang": "moi_vao_pubmed", "dem": m}]
    if not bo_sr:
        tang.insert(1, {"tang": "sr_ma", "dem": s})
    return {"topic": "X", "tang": tang, "do_duoc": do_duoc, "tong": sum((t["dem"] or 0) for t in tang), "loai": loai}


@pytest.mark.parametrize("kq,mong", [
    (_kq(), True),                                   # 0/0/0, tầng mới có bài
    (_kq(g=1), True),                                # tổng thứ bậc = 1 = ngưỡng
    (_kq(g=1, r=1), False),                          # tổng thứ bậc 2 > ngưỡng
    (_kq(s=1), False),                               # có tổng quan
    (_kq(loai="MU", m=2), False),                    # đã là «mù» — không báo trùng
    (_kq(loai="KHONG_DO", do_duoc=False), False),    # không đo được ⇒ không kết luận
    (_kq(bo_sr=True), False),                        # không có tầng sr_ma ⇒ không xét
])
def test_phan_loai_thu_bac_trong(kq, mong):
    assert SL.thu_bac_trong(kq) is mong


def test_sr_ma_khong_do_duoc_khong_phai_trong():
    kq = _kq()
    kq["tang"][1]["dem"] = None
    assert SL.thu_bac_trong(kq) is False


def _wl():
    def ch(ten, q):
        return {"topic": ten, "active": True, "queries": [
            {"tang": "guideline", "query": q + " G", "datetype": "pdat", "loc_thiet_ke": True},
            {"tang": "sr_ma", "query": q + " S", "datetype": "pdat", "loc_thiet_ke": True},
            {"tang": "rct", "query": q + " R", "datetype": "pdat", "loc_thiet_ke": True},
            {"tang": "moi_vao_pubmed", "query": q + " M", "datetype": "edat", "loc_thiet_ke": False}]}
    return {"topics": [ch("Mù", "mu"), ch("Hẹp", "hep"), ch("Khoẻ", "khoe")]}


DEM = {"mu": {"G": 0, "S": 0, "R": 0, "M": 2}, "hep": {"G": 1, "S": 0, "R": 0, "M": 46},
       "khoe": {"G": 3, "S": 17, "R": 1, "M": 108}}


def _fetch(term, datetype, days):
    goc = term.split("(", 1)[1].split(")", 1)[0].split()
    return DEM[goc[0]][goc[1]]


def test_kiem_tach_mu_va_thu_bac_trong_ma_thoat_khong_doi():
    b = SL.kiem(_wl(), _fetch, "DESIGN")
    assert b["mu"] == ["Mù"] and b["thu_bac_trong"] == ["Hẹp"]
    assert SL.ma_thoat(b) == 1
    chi_hep = SL.kiem({"topics": _wl()["topics"][1:]}, _fetch, "DESIGN")
    assert chi_hep["thu_bac_trong"] == ["Hẹp"] and chi_hep["mu"] == []
    assert SL.ma_thoat(chi_hep) == 0                 # 🟠 KHÔNG đổi nghĩa mã thoát


def test_in_bao_cao_danh_dau_cam_va_doc_duoc_tep_cu():
    b = SL.kiem(_wl(), _fetch, "DESIGN")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        SL.in_bao_cao(b)
    dong_hep = [x for x in out.getvalue().splitlines() if "Hẹp" in x]
    assert dong_hep and dong_hep[0].lstrip().startswith("🟠")
    assert "TẦNG THỨ BẬC TRỐNG" in out.getvalue()
    cu = {k: v for k, v in b.items() if k != "thu_bac_trong"}          # tệp --json viết trước bản vá
    out2 = io.StringIO()
    with contextlib.redirect_stdout(out2):
        SL.in_bao_cao(cu)
    assert "TẦNG THỨ BẬC TRỐNG" in out2.getvalue()


def test_khong_co_chu_de_hep_thi_khong_in_doan_cam():
    b = SL.kiem({"topics": [_wl()["topics"][2]]}, _fetch, "DESIGN")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        SL.in_bao_cao(b)
    assert "TẦNG THỨ BẬC TRỐNG" not in out.getvalue() and "🟠" not in out.getvalue()


# ── chu trình nêu thành việc 🟠 ─────────────────────────────────────────────────────────────────────────────────────────
CT = _nap("_ct_tbt", "chu_trinh_chung_cu.py")


class _P:
    def __init__(self, rc):
        self.returncode, self.stdout, self.stderr = rc, "", ""


def _chay_chu_trinh(rc_san_luong: int, state: dict | str | None):
    with tempfile.TemporaryDirectory() as td:
        goc = Path(td)
        (goc / "EBM-Dashboards").mkdir()
        (goc / "EBM-Dashboards" / "watchlist.json").write_text("{}", encoding="utf-8")
        if state is not None:
            (goc / "state").mkdir()
            (goc / "state" / "san-luong-giam-sat-gan-nhat.json").write_text(
                state if isinstance(state, str) else json.dumps(state), encoding="utf-8")

        def _goi(cmd, **_kw):
            c = [str(x) for x in cmd]
            return _P(rc_san_luong if len(c) > 1 and "kiem_san_luong_giam_sat.py" in c[1] else 0)
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py"]), mock.patch.object(CT.subprocess, "run", side_effect=_goi), \
                mock.patch.object(CT, "_co_dashboard_that", return_value=True), mock.patch.object(CT, "REPO", goc), \
                contextlib.redirect_stdout(out):
            CT.main()
        return out.getvalue()


def test_chu_trinh_neu_viec_cam_khi_co_chu_de_hep():
    out = _chay_chu_trinh(0, {"thu_bac_trong": ["Bệnh thận mạn (CKD)", "COPD"]})
    assert "2 chủ đề TẦNG THỨ BẬC TRỐNG" in out


def test_chu_trinh_im_lang_khi_khong_co_hoac_tep_hong():
    assert "TẦNG THỨ BẬC TRỐNG" not in _chay_chu_trinh(0, {"thu_bac_trong": []})
    assert "TẦNG THỨ BẬC TRỐNG" not in _chay_chu_trinh(0, "{hỏng")
    assert "TẦNG THỨ BẬC TRỐNG" not in _chay_chu_trinh(0, None)


def test_chu_trinh_khong_doc_ket_qua_khi_khong_do_duoc():
    """Mã 2 (không đo được) ⇒ tệp state có thể là của lượt CŨ — không được nêu việc từ nó."""
    out = _chay_chu_trinh(2, {"thu_bac_trong": ["COPD"]})
    assert "TẦNG THỨ BẬC TRỐNG" not in out and "Chưa đo được sản lượng" in out
