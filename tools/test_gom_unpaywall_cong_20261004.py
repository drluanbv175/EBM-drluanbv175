# -*- coding: utf-8 -*-
"""Test cổng điều khoản + cổng nội dung của tầng 2 Unpaywall trong `gom_toan_van_dashboard.py` (04/10/2026).

Lỗi thật đo được 04/10: (1) tầng 2 lưu MỌI bản «is_oa», kể cả bản không giấy phép mở của NXB «cấm» — 32/42 tệp `_UPW` trong kho
không mang giấy phép mở; (2) cổng nội dung chỉ đòi ≥ 500 từ ⇒ 15/27 tệp `_UPW.html` là TRANG GIỚI THIỆU kho lưu trữ (tóm tắt +
metadata) mà vẫn được tính «có toàn văn», gồm 4 mục apply; (3) sổ phủ chỉ đếm `*.xml` nên báo thấp hơn thật. Ngoại tuyến hoàn toàn.
"""
from __future__ import annotations

import importlib.util
import io
import json
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap():
    sp = importlib.util.spec_from_file_location("_gom_tv_test", REPO / "tools" / "gom_toan_van_dashboard.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


g = _nap()

BANG = {
    "ADA (American Diabetes Association)": {"ket_luan": "cam", "doi": ("10.2337/",), "mien": ("diabetesjournals.org",)},
    "Wiley": {"ket_luan": "cam", "doi": ("10.1002/",), "mien": ("onlinelibrary.wiley.com",)},
}


def _dtv(uy_quyen: set[str]):
    def nxb_cua(doi="", url="", tieu_de=""):
        for ten, d in BANG.items():
            if any((doi or "").lower().startswith(t) for t in d["doi"]):
                return ten, d
        return None, None
    return types.SimpleNamespace(DIEU_KHOAN_NXB=BANG, nxb_cua=nxb_cua,
                                 uy_quyen_bac_si=lambda ten, hom_nay=None: {"ngay": "2026-10-03"} if ten in uy_quyen else None)


# ── Cổng điều khoản ──────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("lic", ["cc-by", "cc-by-nc-nd", "CC-BY-NC", "cc0", "pd", "public-domain"])
def test_giay_phep_mo_duoc_luu(lic):
    duoc, ly = g.quyet_dinh_unpaywall("10.2337/dc26-S012", "https://diabetesjournals.org/x", lic, dtv=_dtv(set()))
    assert duoc and "giấy phép mở" in ly


def test_nxb_cam_co_uy_quyen_doc_van_khong_luu_tu_dong():
    """Uỷ quyền 03/10 là uỷ quyền ĐỌC («KHÔNG lưu toàn văn») — lưu bản sao chỉ trong phiên có lời bác sĩ."""
    duoc, ly = g.quyet_dinh_unpaywall("10.1002/acr.22812", "https://repo.example/x", None, dtv=_dtv({"Wiley"}))
    assert not duoc and ly.startswith("cam_co_uq")


def test_nxb_cam_khong_uy_quyen_khong_luu():
    duoc, ly = g.quyet_dinh_unpaywall("10.2337/dc26-S002", "https://repo.example/x", "other-oa", dtv=_dtv(set()))
    assert not duoc and ly.startswith("cam_khong_uq")


def test_nxb_chua_kiem_khong_luu():
    duoc, ly = g.quyet_dinh_unpaywall("10.1378/chest.09-1584", "https://repo.example/x", "other-oa", dtv=_dtv(set()))
    assert not duoc and ly.startswith("chua_kiem")


def test_khong_nap_duoc_bang_thi_dong(monkeypatch):
    monkeypatch.setattr(g, "_nap_dtv", lambda: None)
    duoc, ly = g.quyet_dinh_unpaywall("10.9999/x", "https://repo.example/x", None)
    assert not duoc and ly.startswith("khong_nap_bang")


# ── Cổng nội dung ────────────────────────────────────────────────────────────────────────────────────────────────────────────
# Giống ca thật SUMMIT 27203508: tóm tắt có cấu trúc (đủ đề mục IMRaD) > 2500 từ + dấu trang kho — chỉ nhận diện trang giới thiệu loại được.
TRANG_GIOI_THIEU = ("Abstract Introduction Methods Results Discussion " + "word " * 2700
                    + " Fingerprint Dive into the research topics. Access to Document Link to publication")
IMRAD = "Introduction " + "a " * 900 + " Methods " + "b " * 900 + " Results " + "c " * 900 + " Discussion " + "d " * 200
GUIDELINE_DAI = "Recommendation " + "x " * 6500


def test_trang_gioi_thieu_kho_khong_phai_toan_van():
    ok, ly = g.la_toan_van_html(TRANG_GIOI_THIEU)
    assert not ok and "trang giới thiệu" in ly


def test_imrad_la_toan_van():
    assert g.la_toan_van_html(IMRAD)[0]


def test_guideline_dai_khong_de_muc_la_toan_van():
    assert g.la_toan_van_html(GUIDELINE_DAI)[0]


def test_ngan_khong_de_muc_khong_phai_toan_van():
    assert not g.la_toan_van_html("word " * 1000)[0]


# ── Sổ phủ đếm mọi loại toàn văn ────────────────────────────────────────────────────────────────────────────────────────────
def test_dem_toan_van_moi_loai(tmp_path):
    (tmp_path / "PMID-1_PMC11.xml").write_text("x")
    (tmp_path / "PMID-2_UPW.pdf").write_text("x")
    (tmp_path / "PMID-3_CHR.html").write_text("x")
    (tmp_path / "PMID-5_WTDM.pdf").write_text("x")
    (tmp_path / "trinh_duyet").mkdir()
    (tmp_path / "trinh_duyet" / "PMID-4.json").write_text("{}")
    (tmp_path / "doc_sau").mkdir()
    (tmp_path / "doc_sau" / "PMID-9.md").write_text("ghi chú đọc sâu — KHÔNG phải toàn văn")
    loai = g.dem_toan_van(tmp_path)
    tat_ca = set().union(*loai.values())
    assert tat_ca == {"1", "2", "3", "4", "5"}
    assert loai["XML"] == {"1"} and loai["UPW"] == {"2"} and loai["CHR"] == {"3"} and loai["TRINH_DUYET"] == {"4"}


# ── Tích hợp tang_unpaywall (mạng giả) ──────────────────────────────────────────────────────────────────────────────────────
class _PhanHoi(io.BytesIO):
    def __init__(self, du_lieu: bytes, url: str):
        super().__init__(du_lieu)
        self._url = url

    def geturl(self):
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _mang_gia(monkeypatch, doi: str, loc: dict, noi_dung: bytes, da_goi: list):
    def urlopen(req, timeout=None, context=None):
        url = req if isinstance(req, str) else req.full_url
        da_goi.append(url)
        if "esummary.fcgi" in url:
            pm = url.split("id=")[1].split("&")[0]
            return _PhanHoi(json.dumps({"result": {pm: {"articleids": [{"idtype": "doi", "value": doi}]}}}).encode(), url)
        if "api.unpaywall.org" in url:
            return _PhanHoi(json.dumps({"is_oa": True, "best_oa_location": loc}).encode(), url)
        return _PhanHoi(noi_dung, url)
    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    monkeypatch.setattr(g, "_email_lich_su", lambda: "test@example.org")
    monkeypatch.setattr(g.time, "sleep", lambda s: None)


def test_tang_unpaywall_khong_mo_noi_dung_khi_nxb_cam(monkeypatch, tmp_path):
    da_goi: list[str] = []
    monkeypatch.setattr(g, "KHO", tmp_path)
    monkeypatch.setattr(g, "_nap_dtv", lambda: _dtv(set()))
    _mang_gia(monkeypatch, "10.2337/dc26-S012", {"url": "https://repo.example/ada", "license": None}, IMRAD.encode(), da_goi)
    moi, thieu = g.tang_unpaywall(["41358886"])
    assert moi == 0 and thieu == ["41358886"]
    assert not list(tmp_path.glob("PMID-*")), "bản không giấy phép mở của NXB «cấm» bị lưu"
    assert not any("repo.example" in u for u in da_goi), "đã MỞ nội dung trước khi xét điều khoản"
    assert g.BO_QUA_UNPAYWALL and g.BO_QUA_UNPAYWALL[0][0] == "41358886"


def test_tang_unpaywall_luu_ban_cc_toan_van(monkeypatch, tmp_path):
    da_goi: list[str] = []
    monkeypatch.setattr(g, "KHO", tmp_path)
    monkeypatch.setattr(g, "_nap_dtv", lambda: _dtv(set()))
    _mang_gia(monkeypatch, "10.9999/cc", {"url": "https://repo.example/cc", "license": "cc-by"},
              ("<html><body>" + IMRAD + "</body></html>").encode(), da_goi)
    moi, _ = g.tang_unpaywall(["111"])
    assert moi == 1 and (tmp_path / "PMID-111_UPW.html").exists()


def test_tang_unpaywall_tu_choi_trang_gioi_thieu_du_co_cc(monkeypatch, tmp_path):
    da_goi: list[str] = []
    monkeypatch.setattr(g, "KHO", tmp_path)
    monkeypatch.setattr(g, "_nap_dtv", lambda: _dtv(set()))
    _mang_gia(monkeypatch, "10.9999/cc2", {"url": "https://repo.example/landing", "license": "cc-by"},
              ("<html><body>" + TRANG_GIOI_THIEU + "</body></html>").encode(), da_goi)
    moi, thieu = g.tang_unpaywall(["222"])
    assert moi == 0 and thieu == ["222"] and not list(tmp_path.glob("PMID-*"))
