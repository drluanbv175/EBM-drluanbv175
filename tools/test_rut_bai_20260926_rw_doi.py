#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #31 (đợt dò nâng cấp 26/09/2026): cổng hỏi nền Retraction Watch NGOẠI TUYẾN theo DOI.

Tái hiện gốc: tầng 3 của `kiem_nguon_da_rut` chỉ gửi PMID (`x.isdigit()`) tới nền; cùng một bài đã rút
(PMID 37362712 = DOI 10.1007/s11042-023-15640-2) trích bằng PMID thì CHẶN, trích bằng DOI thì chỉ CẢNH BÁO.

Hợp đồng giữ nguyên: chỉ tín hiệu DƯƠNG; DOI vắng khỏi nền vẫn CHƯA KIỂM; nền vắng ⇒ nói rõ DOI chưa được
đối chiếu; không bao giờ in ✓ «Rút bài». Ngoại tuyến 100% (stub/fixture), không mạng.
"""
from __future__ import annotations

import csv
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VD_NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


SO = _nap("so_rw_doi_20260926", ROOT / "tools" / "so_xac_minh_nguon.py")
DOI_RUT = "10.1007/s11042-023-15640-2"


# ── 1. Hàm mới của sổ ──────────────────────────────────────────────────────────────────────────────────
class _NenGia:
    def __init__(self, du_lieu):
        self._d = du_lieu

    def tra(self, pmid):
        return None

    def san_sang_doi(self):
        return True

    def tra_doi(self, doi):
        return self._d.get(str(doi).strip().lower())


def test_ham_doi_chi_tra_duong_tinh_giu_nguyen_chuoi_goc(monkeypatch):
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "da_thu", True)
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "chi_muc", _NenGia({DOI_RUT: {
        "status": "retracted", "reason": "+Paper Mill;", "title": "Bài RW", "notice_doi": "10.1007/x"}}))
    ra = SO.rut_bai_retraction_watch_ngoai_tuyen_doi(["10.1007/S11042-023-15640-2", "10.1000/sach"])
    assert [r["gia_tri"] for r in ra] == ["10.1007/S11042-023-15640-2"], "DOI vắng khỏi nền không được thành 'sạch'/'rút'"
    r = ra[0]
    assert r["loai"] == "doi" and r["khoa"] == "doi:10.1007/s11042-023-15640-2" and r["tinh_trang"] == "retracted"
    assert "Bài RW" in r["tieu_de"], "phải hiện tiêu đề RW để bác sĩ đối chiếu"
    assert "Retraction Watch" in r["nguon"] and "DOI" in r["nguon"]


def test_ham_doi_nen_vang_hoac_engine_cu_tra_none(monkeypatch):
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "da_thu", True)
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "chi_muc", None)
    assert SO.rut_bai_retraction_watch_ngoai_tuyen_doi([DOI_RUT]) is None
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "chi_muc", type("Cu", (), {"tra": lambda self, p: None})())
    assert SO.rut_bai_retraction_watch_ngoai_tuyen_doi([DOI_RUT]) is None, "engine cũ không có tra_doi ⇒ CHƯA KIỂM"
    assert SO.rut_bai_retraction_watch_ngoai_tuyen_doi([]) == []


def test_ham_pmid_giu_nguyen_chu_ky(monkeypatch):
    import inspect
    assert list(inspect.signature(SO.rut_bai_retraction_watch_ngoai_tuyen).parameters) == ["cac_pmid"]


def test_tich_hop_engine_that_voi_csv_fixture(monkeypatch, tmp_path):
    """Đi qua RetractionWatchIndex THẬT của repo y khoa (nếu có ở bố cục lồng/anh em) với CSV giả."""
    bst = _nap("bst_rw_doi_20260926", ROOT / "tools" / "ban_sao_tran.py")
    mea = bst.duong_goc("medical-ebm-automation", ROOT)
    if mea is None or not (mea / "app" / "sources" / "retraction_watch.py").exists():
        pytest.skip("không có repo y khoa cạnh repo gốc — không đo được tích hợp engine (⚪)")
    # Nạp qua sys.path đúng như sổ làm thật (`from app.sources.retraction_watch import …`).
    if str(mea) not in sys.path:
        monkeypatch.syspath_prepend(str(mea))
    from app.sources.retraction_watch import RetractionWatchIndex  # noqa: PLC0415
    if not hasattr(RetractionWatchIndex, "tra_doi"):
        pytest.skip("engine y khoa ở đây chưa có tra_doi() — cần commit #31 bên repo y khoa")
    p = tmp_path / "rw.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["Title", "OriginalPaperDOI", "OriginalPaperPubMedID", "RetractionNature",
                                           "Reason"])
        w.writeheader()
        w.writerow({"Title": "Bài có PMID", "OriginalPaperDOI": DOI_RUT, "OriginalPaperPubMedID": "37362712",
                    "RetractionNature": "Retraction", "Reason": "+Paper Mill;"})
        w.writerow({"Title": "Chỉ DOI", "OriginalPaperDOI": "10.1007/s11042-022-14078-2",
                    "OriginalPaperPubMedID": "0", "RetractionNature": "Retraction"})
    idx = RetractionWatchIndex(csv_path=p, meta_path=tmp_path / "m.json")
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "da_thu", True)
    monkeypatch.setitem(SO._RW_NGOAI_TUYEN, "chi_muc", idx)
    ra = SO.rut_bai_retraction_watch_ngoai_tuyen_doi(["https://doi.org/" + DOI_RUT, "10.1007/s11042-022-14078-2"])
    assert sorted(r["gia_tri"] for r in ra) == sorted(["https://doi.org/" + DOI_RUT, "10.1007/s11042-022-14078-2"])
    assert SO.rut_bai_retraction_watch_ngoai_tuyen(["37362712"])[0]["tinh_trang"] == "retracted"


# ── 2. Cổng verify_dashboard (cây thư mục giả, sổ stub) ───────────────────────────────────────────────
STUB_CHUNG = '''
def nguon_da_rut(ten): return []
def dinh_danh_da_rut(ids): return []
def pham_vi_kiem_rut_bai(ids):
    return {"co": [], "chua": list(ids)}
def _bg(loai, v):
    return {"khoa": loai + ":" + v.lower(), "loai": loai, "gia_tri": v, "tinh_trang": "retracted", "tieu_de": "RW",
            "kiem_luc": "2026-09-26", "nguon": "Retraction Watch (nền ngoại tuyến)", "rut_va_thay": False,
            "thong_bao": "", "sua_loi_bi_rut": False, "thong_bao_ids": []}
def rut_bai_retraction_watch_ngoai_tuyen(pmids):
    return [_bg("pmid", p) for p in pmids if p == "37362712"]
'''
STUB_DOI = '''
def rut_bai_retraction_watch_ngoai_tuyen_doi(dois):
    if _NEN_DOI_VANG: return None
    return [_bg("doi", d) for d in dois if d.lower() == "10.1007/s11042-023-15640-2"]
'''


def _dung_cay(tmp: Path, item_js: str, co_ham_doi: bool = True, nen_doi_vang: bool = False):
    (tmp / "tools").mkdir()
    shutil.copy(VD_NGUON, tmp / "tools" / "verify_dashboard.py")
    (tmp / "tools" / "so_xac_minh_nguon.py").write_text(
        f"_NEN_DOI_VANG = {nen_doi_vang!r}\n" + STUB_CHUNG + (STUB_DOI if co_ham_doi else ""), encoding="utf-8")
    page = tmp / "WebDashboard_EBM_VanDeCuThe_X_20260926.html"
    page.write_text("<script>const DATA={items:[%s]}</script>" % item_js, encoding="utf-8")
    vd = _nap("vd_rw_doi_" + tmp.name, tmp / "tools" / "verify_dashboard.py")
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    return errors, warns, oks


@pytest.mark.parametrize("item_js", ["{id:'ITEM-01', pmid:'37362712'}",
                                     "{id:'ITEM-01', doi:'10.1007/s11042-023-15640-2'}",
                                     "{id:'ITEM-01', doi:'10.1007/S11042-023-15640-2'}"])
def test_cung_bai_da_rut_bi_chan_du_trich_bang_pmid_hay_doi(tmp_path, item_js):
    errors, _w, oks = _dung_cay(tmp_path, item_js)
    assert any("ĐÃ BỊ RÚT" in e for e in errors), (item_js, errors)
    assert not any("Rút bài:" in o for o in oks)


def test_doi_da_hoi_nen_ma_im_lang_van_la_chua_kiem_khong_in_tick(tmp_path):
    errors, warns, oks = _dung_cay(tmp_path, "{id:'ITEM-01', doi:'10.1000/sach.hay.chua.biet'}")
    assert not errors
    pv = [w for w in warns if "Phạm vi kiểm rút bài" in w]
    assert pv and "10.1000/sach.hay.chua.biet" in pv[0] and "theo DOI" in pv[0] and "CHƯA KIỂM" in pv[0], warns
    assert "CHỈ được hỏi cho PMID" not in pv[0]
    assert not any("Rút bài:" in o for o in oks), "DOI im lặng trong nền không được thành ✓"


def test_nen_doi_vang_noi_ro_doi_chua_duoc_doi_chieu(tmp_path):
    _e, warns, oks = _dung_cay(tmp_path, "{id:'ITEM-01', doi:'10.1000/abc'}", nen_doi_vang=True)
    pv = [w for w in warns if "Phạm vi kiểm rút bài" in w]
    assert pv and "DOI CHƯA được đối chiếu" in pv[0] and "KHÔNG có trên máy này" in pv[0], warns
    assert not any("Rút bài:" in o for o in oks)


def test_so_cu_khong_co_ham_doi_giu_thong_diep_cu(tmp_path):
    _e, warns, _o = _dung_cay(tmp_path, "{id:'ITEM-01', doi:'10.1000/abc'}", co_ham_doi=False)
    pv = [w for w in warns if "Phạm vi kiểm rút bài" in w]
    assert pv and "CHỈ được hỏi cho PMID" in pv[0]


def test_thong_diep_thuan_ba_truong_hop_doi():
    vd = _nap("vd_rw_doi_thuan_20260926", VD_NGUON)
    da_hoi = vd._thong_diep_pham_vi_rw(["10.1/x"], None, [], [])
    vang = vd._thong_diep_pham_vi_rw(["10.1/x"], None, [], None)
    cu = vd._thong_diep_pham_vi_rw(["10.1/x"], None, [])
    tron = vd._thong_diep_pham_vi_rw(["123", "10.1/x"], [], ["123"], [])
    assert "theo DOI" in da_hoi and "CHƯA KIỂM" in da_hoi and "✓" not in da_hoi
    assert "DOI CHƯA được đối chiếu" in vang
    assert "CHỈ được hỏi cho PMID" in cu
    assert "cho các PMID chưa kiểm" in tron and "1 DOI đã đối chiếu" in tron
