#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""J Rheumatol vào bảng điều khoản + phạm vi phiên uỷ quyền Chrome tính LÚC KIỂM (04/10/2026).

Bác sĩ nói giữa phiên: «J Rheumatol uỷ quyền». Trước bản vá, phiên chỉ nhận các NXB chụp lúc mở (`d["nxb"]`), nên uỷ quyền mới
không có hiệu lực cho tới phiên sau, còn uỷ quyền bị rút vẫn được lưu tiếp. Khoá:
  • J Rheumatol có mục «cam» trong DIEU_KHOAN_NXB (DOI 10.3899/, miền jrheum.org/jrheum.com), nhận đúng khoá theo DOI và theo URL;
  • uỷ quyền THÊM giữa phiên có hiệu lực ngay; uỷ quyền bị RÚT giữa phiên thì dừng ngay;
  • cơ sở dữ liệu (DynaMed/Scopus/WoS) vẫn KHÔNG BAO GIỜ thuộc phiên, kể cả khi có mục uỷ quyền;
  • đi trọn đường thật: tệp uỷ quyền có mục J Rheumatol ⇒ `nxb_duoc_luu` của phiên có J Rheumatol.
Ngoại tuyến (bộ điều khoản giả + tệp trong tmp_path).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
JRHEUM = "The Journal of Rheumatology"
WK = "Wolters Kluwer Health (LWW · AHA journals · Neurology)"


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


P = _nap("_puq_jrheum_test", "phien_uy_quyen_chrome.py")
DTV = _nap("_dtv_jrheum_test", "doc_toan_van_co_nguoi.py")
T0 = datetime(2026, 10, 4, 9, 0, 0, tzinfo=timezone(timedelta(hours=7)))
LOI = "uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay"
URL_ELS = "https://www.sciencedirect.com/science/article/pii/S0741521421008934"
URL_AHA = "https://www.ahajournals.org/doi/10.1161/STR.0000000000000375"


def _dtv(uy_quyen):
    """Bộ điều khoản giả: Elsevier + EBSCO + WK đều «cam»; uỷ quyền chỉ cho những khoá trong `uy_quyen`."""
    bang = {"Elsevier": {"ket_luan": "cam", "doi": ("10.1016/",), "mien": ("sciencedirect.com",)},
            "EBSCO (DynaMed)": {"ket_luan": "cam", "doi": (), "mien": ("dynamed.com",)},
            WK: {"ket_luan": "cam", "doi": ("10.1161/",), "mien": ("ahajournals.org",)}}

    def nxb_cua(doi="", url="", tieu_de=""):
        h = P._mien(url)
        for ten, d in bang.items():
            if any((doi or "").lower().startswith(t) for t in d["doi"]) or any(h == m or h.endswith("." + m) for m in d["mien"]):
                return ten, d
        return None, None
    return types.SimpleNamespace(DIEU_KHOAN_NXB=bang, nxb_cua=nxb_cua,
                                 uy_quyen_bac_si=lambda ten, hom_nay=None: {"nxb": ten} if ten in uy_quyen else None)


@pytest.fixture()
def so(tmp_path):
    return tmp_path / "state" / "phien.json"


# ── bảng điều khoản ───────────────────────────────────────────────────────────────────────────────────────────────────────
def test_jrheum_co_muc_cam_dung_doi_va_mien() -> None:
    muc = DTV.DIEU_KHOAN_NXB[JRHEUM]
    assert muc["ket_luan"] == "cam"
    assert "10.3899/" in muc["doi"] and {"jrheum.org", "jrheum.com"} <= set(muc["mien"])
    assert len(muc["trich"].split()) <= 15 and muc["doc_luc"] == "2026-10-04"
    assert DTV.nxb_cua(doi="10.3899/jrheum.180726")[0] == JRHEUM
    assert DTV.nxb_cua(url="https://www.jrheum.org/content/47/2/171")[0] == JRHEUM


# ── phạm vi tính lúc kiểm ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_uy_quyen_them_giua_phien_co_hieu_luc_ngay(so) -> None:
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=_dtv(("Elsevier",)))[0] == 0
    assert WK not in P.doc_phien(so)["nxb"]                       # ảnh chụp lúc mở không có WK
    ma, tb = P.kiem("34024117", URL_AHA, bay_gio=T0, tep=so, dtv=_dtv(("Elsevier",)))
    assert ma == 3 and "KHÔNG thuộc phạm vi" in tb
    assert P.kiem("34024117", URL_AHA, bay_gio=T0, tep=so, dtv=_dtv(("Elsevier", WK)))[0] == 0


def test_rut_uy_quyen_giua_phien_dung_ngay(so) -> None:
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=_dtv(("Elsevier", WK)))[0] == 0
    assert P.kiem("34153348", URL_ELS, bay_gio=T0, tep=so, dtv=_dtv(("Elsevier", WK)))[0] == 0
    ma, tb = P.kiem("34153348", URL_ELS, bay_gio=T0, tep=so, dtv=_dtv((WK,)))   # bác sĩ rút uỷ quyền Elsevier
    assert ma == 3 and "KHÔNG thuộc phạm vi" in tb


def test_co_so_du_lieu_khong_bao_gio_thuoc_phien_du_co_uy_quyen(so) -> None:
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=_dtv(("Elsevier",)))[0] == 0
    ma, _tb = P.kiem("1", "https://www.dynamed.com/x", bay_gio=T0, tep=so, dtv=_dtv(("Elsevier", "EBSCO (DynaMed)")))
    assert ma == 3


def test_nhan_cung_theo_pham_vi_luc_kiem(tmp_path, so) -> None:
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=_dtv(("Elsevier",)))[0] == 0
    ma_phien = P.doc_phien(so)["ma"]
    tep = tmp_path / "PMID-34024117_CHR.html"
    tep.write_text(f"<!-- ebm-phien:{ma_phien} pmid:34024117 url:{URL_AHA} -->\n<html><body>" + "thân bài " * 900
                   + "</body></html>", encoding="utf-8")
    kho = tmp_path / "kho"
    ma, tb = P.nhan("34024117", tep, URL_AHA, bay_gio=T0, so=so, kho=kho, dtv=_dtv(("Elsevier",)))
    assert ma == 3 and "KHÔNG thuộc phạm vi" in tb and not kho.exists()
    ma, tb = P.nhan("34024117", tep, URL_AHA, bay_gio=T0, so=so, kho=kho, dtv=_dtv(("Elsevier", WK)))
    assert ma == 0 and (kho / "PMID-34024117_CHR.html").exists()


# ── đi trọn đường thật ────────────────────────────────────────────────────────────────────────────────────────────────────
def test_tep_uy_quyen_that_co_jrheum_thi_phien_nhan(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(DTV, "DASH", tmp_path)
    (tmp_path / DTV.TEN_TEP_UY_QUYEN).write_text(json.dumps({"muc": [
        {"nxb": JRHEUM, "ngay": "2026-10-04", "can_cu": "J Rheumatol uỷ quyền;đã tắt VPN"}]}, ensure_ascii=False),
        encoding="utf-8")
    assert DTV.uy_quyen_bac_si(JRHEUM, date(2026, 10, 4))
    assert JRHEUM in P.nxb_duoc_luu(DTV, date(2026, 10, 4))
    (tmp_path / DTV.TEN_TEP_UY_QUYEN).write_text(json.dumps({"muc": []}), encoding="utf-8")
    assert JRHEUM not in P.nxb_duoc_luu(DTV, date(2026, 10, 4))


def test_doctrine_phai_neu_du_ten_khong_chi_chu_dau() -> None:
    """Trước 04/10 bộ so chỉ xét CHỮ ĐẦU của tên NXB — «The Journal of Rheumatology» qua được chỉ cần chữ «The» có ở chỗ khác
    trong mục (doctrine tiếng Việt hiện không có chữ «The» nào khác, nên ca kiểm tự chèn một chữ để tái hiện)."""
    van_ban = (TOOLS.parent / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md").read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
    mat_ten = van_ban.replace("**The Journal of Rheumatology**", "**J Rheum**").replace("## 2septies. ", "## 2septies. The ", 1)
    assert any(JRHEUM in x for x in DTV.lech_doctrine(mat_ten))
    mat_doi = van_ban.replace("`10.3899/`", "10.3899")
    assert any(JRHEUM in x for x in DTV.lech_doctrine(mat_doi))


WILEY = "Wiley (Wiley Online Library · Cochrane Library)"


def test_wiley_co_muc_cam_nhan_dung_doi_mien_va_khong_chan_hindawi() -> None:
    muc = DTV.DIEU_KHOAN_NXB[WILEY]
    assert muc["ket_luan"] == "cam" and len(muc["trich"].split()) <= 15 and muc["doc_luc"] == "2026-10-04"
    assert DTV.nxb_cua(doi="10.1002/ajh.70118")[0] == WILEY
    assert DTV.nxb_cua(doi="10.1111/j.1365-2265.2008.03340.x")[0] == WILEY
    assert DTV.nxb_cua(doi="10.1002/14651858.CD008322.pub2")[0] == WILEY          # Cochrane
    assert DTV.nxb_cua(url="https://onlinelibrary.wiley.com/doi/10.1002/art.27584")[0] == WILEY
    assert DTV.nxb_cua(url="https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008616.pub2/full")[0] == WILEY
    assert DTV.nxb_cua(doi="10.1155/2013/586497")[0] != WILEY                     # Hindawi toàn OA CC BY
    # guideline ESC đăng trên EJHF (Wiley) vẫn mang khoá ESC — bảng xét tiêu đề ESC trước tiền tố DOI
    esc = DTV.nxb_cua(doi="10.1002/ejhf.2333", tieu_de="2021 ESC Guidelines for the diagnosis and treatment of heart failure")
    assert esc[0] == "ESC (European Society of Cardiology)"


def test_doctrine_ghi_uy_quyen_thuong_truc_nguyen_van_va_gioi_han() -> None:
    van_ban = (TOOLS.parent / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md").read_text(encoding="utf-8")
    i = van_ban.index("## 2septies. ")
    muc = van_ban[i:van_ban.index("\n## ", i + 5)]
    assert "**Uỷ quyền THƯỜNG TRỰC (04/10/2026)**" in muc
    assert "cho tất cả các vấn đề tương tự khác không hỏi lại tôi nữa" in muc
    assert "KHÔNG áp cho DynaMed/EBSCO, Scopus, Web of Science" in muc and "không gõ tài khoản/mật khẩu" in muc
    assert DTV.lech_doctrine(van_ban) == []
