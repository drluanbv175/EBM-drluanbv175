#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phiên uỷ quyền Chrome (04/10/2026): bác sĩ nói MỘT câu mỗi phiên, Claude đọc và lưu bản sao toàn văn trong phiên đó.

Khoá: phiên chỉ mở bằng lời bác sĩ (≥ 20 ký tự, ghi nguyên văn); chỉ NXB có uỷ quyền đọc còn hiệu lực, KHÔNG BAO GIỜ cơ sở dữ liệu
(DynaMed/Scopus/WoS); hết ngày tự đóng; trần 20 bài/miền và nhịp ≥ 60 giây; tệp HTML phải mang dấu phiên đúng và không có giao
diện tài khoản; không ghi đè; kho/bộ đọc sâu gắn nhãn «KHÔNG phải OA». Ngoại tuyến (bộ điều khoản giả, tệp trong tmp_path).
"""
from __future__ import annotations

import importlib.util
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


P = _nap("_puq_test", "phien_uy_quyen_chrome.py")
T0 = datetime(2026, 10, 4, 9, 0, 0, tzinfo=timezone(timedelta(hours=7)))
LOI = "uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay"
URL_ELS = "https://www.sciencedirect.com/science/article/pii/S0741521421008934"


def _dtv(uy_quyen=("Elsevier", "EBSCO (DynaMed)")):
    """Bộ điều khoản giả: Elsevier + EBSCO + WK đều «cam»; uỷ quyền chỉ cho những khoá trong `uy_quyen`."""
    bang = {"Elsevier": {"ket_luan": "cam", "doi": ("10.1016/",), "mien": ("sciencedirect.com",)},
            "EBSCO (DynaMed)": {"ket_luan": "cam", "doi": (), "mien": ("dynamed.com",)},
            "Wolters Kluwer Health (LWW · AHA journals · Neurology)": {"ket_luan": "cam", "doi": ("10.1161/",),
                                                                        "mien": ("ahajournals.org",)}}

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


def _mo(so, dtv=None, luc=T0):
    return P.mo(LOI, bay_gio=luc, tep=so, dtv=dtv or _dtv())


# ── mở / đóng ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_mo_can_loi_bac_si_du_dai(so):
    assert P.mo("đồng ý", bay_gio=T0, tep=so, dtv=_dtv())[0] == 3
    assert P.doc_phien(so) is None


def test_mo_chi_nxb_co_uy_quyen_va_khong_bao_gio_co_so_du_lieu(so):
    ma, tb = _mo(so)
    assert ma == 0, tb
    d = P.doc_phien(so)
    assert d["nxb"] == ["Elsevier"]                      # EBSCO bị loại dù có uỷ quyền; WK không có uỷ quyền
    assert d["can_cu"] == LOI and "LƯU" in d["pham_vi"]


def test_khong_nxb_nao_thi_khong_mo(so):
    assert _mo(so, _dtv(uy_quyen=("EBSCO (DynaMed)",)))[0] == 3


def test_khong_mo_chong_hai_phien_cung_ngay(so):
    assert _mo(so)[0] == 0
    assert _mo(so, luc=T0 + timedelta(hours=1))[0] == 3


def test_het_ngay_tu_dong_va_dung_dong_phien(so):
    _mo(so)
    assert P.phien_mo(T0 + timedelta(hours=3), so) is not None
    assert P.phien_mo(T0 + timedelta(days=1), so) is None          # hết ngày ⇒ phiên sau phải có lời mới
    assert P.dung(bay_gio=T0 + timedelta(hours=4), tep=so)[0] == 0
    assert P.phien_mo(T0 + timedelta(hours=5), so) is None


def test_so_hong_la_khong_co_phien(so):
    so.parent.mkdir(parents=True)
    so.write_text("{hỏng", encoding="utf-8")
    assert P.phien_mo(T0, so) is None
    assert P.kiem("1", URL_ELS, bay_gio=T0, tep=so, dtv=_dtv())[0] == 3


# ── kiểm trước mỗi bài ────────────────────────────────────────────────────────────────────────────────────────────────
def test_kiem_khong_co_phien_va_ngoai_pham_vi(so):
    assert P.kiem("34153348", URL_ELS, bay_gio=T0, tep=so, dtv=_dtv())[0] == 3
    _mo(so)
    assert P.kiem("34153348", URL_ELS, bay_gio=T0, tep=so, dtv=_dtv())[0] == 0
    ma, tb = P.kiem("34024117", "https://www.ahajournals.org/doi/10.1161/STR.0000000000000375", bay_gio=T0, tep=so, dtv=_dtv())
    assert ma == 3 and "KHÔNG thuộc phạm vi" in tb
    assert P.kiem("1", "https://www.dynamed.com/x", bay_gio=T0, tep=so, dtv=_dtv())[0] == 3


def _ghi_lich_su(so, n, luc):
    d = P.doc_phien(so)
    d["lich_su"] = [{"luc": (luc + timedelta(seconds=70 * i)).isoformat(), "pmid": str(10_000_000 + i),
                     "mien": "www.sciencedirect.com"} for i in range(n)]
    P._ghi(d, so)


def test_tran_moi_mien_va_bai_cu_van_duoc(so):
    _mo(so)
    _ghi_lich_su(so, P.TRAN_MOI_MIEN, T0)
    sau = T0 + timedelta(hours=2)
    ma, tb = P.kiem("99999999", URL_ELS, bay_gio=sau, tep=so, dtv=_dtv())
    assert ma == 3 and "đã đủ" in tb
    assert P.kiem("10000000", URL_ELS, bay_gio=sau, tep=so, dtv=_dtv())[0] == 0   # bài đã có trong phiên (vd thêm PDF)


def test_nhip_toi_thieu_giua_hai_bai_cung_mien(so):
    _mo(so)
    _ghi_lich_su(so, 1, T0)
    ma, tb = P.kiem("20000000", URL_ELS, bay_gio=T0 + timedelta(seconds=30), tep=so, dtv=_dtv())
    assert ma == 3 and "đợi thêm" in tb
    assert P.kiem("20000000", URL_ELS, bay_gio=T0 + timedelta(seconds=61), tep=so, dtv=_dtv())[0] == 0


# ── tệp ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _html(tmp_path, ma, pmid, them="", co=6000):
    t = tmp_path / f"bai-{pmid}.html"
    t.write_text(f"<!-- ebm-phien:{ma} pmid:{pmid} url:{URL_ELS} -->\n<article>{'x' * co}{them}</article>", encoding="utf-8")
    return t


def test_kiem_tep_html_va_pdf(tmp_path):
    assert P.kiem_tep(_html(tmp_path, "M1", "5"), "5", "M1")[0] == "html"
    assert P.kiem_tep(_html(tmp_path, "M2", "5"), "5", "M1")[0] is None             # dấu phiên khác
    assert P.kiem_tep(_html(tmp_path, "M1", "6"), "5", "M1")[0] is None             # dấu PMID khác
    assert P.kiem_tep(_html(tmp_path, "M1", "5", them="<a>Sign out</a>"), "5", "M1")[0] is None
    assert P.kiem_tep(_html(tmp_path, "M1", "5", co=100), "5", "M1")[0] is None     # quá ngắn (chỉ tóm tắt/trang chặn)
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF-1.7\n" + b"0" * 30_000)
    assert P.kiem_tep(pdf, "5", "M1")[0] == "pdf"
    pdf.write_bytes(b"%PDF-1.7\n" + b"0" * 100)
    assert P.kiem_tep(pdf, "5", "M1")[0] is None
    khong = tmp_path / "b.bin"
    khong.write_bytes(b"\xff\xfe\x00rac")
    assert P.kiem_tep(khong, "5", "M1")[0] is None


def test_nhan_luu_vao_kho_ghi_nhat_ky_khong_ghi_de(tmp_path, so):
    _mo(so)
    ma_phien = P.doc_phien(so)["ma"]
    kho = tmp_path / "kho"
    t = _html(tmp_path, ma_phien, "34153348")
    ma, tb = P.nhan("34153348", t, URL_ELS, "10.1016/j.jvs.2021.04.073", bay_gio=T0, so=so, kho=kho, dtv=_dtv())
    assert ma == 0, tb
    dich = kho / "PMID-34153348_CHR.html"
    assert dich.exists() and not t.exists()
    ls = P.doc_phien(so)["lich_su"]
    assert len(ls) == 1 and ls[0]["tep"] == dich.name and len(ls[0]["sha256"]) == 64 and ls[0]["loai"] == "html"
    # cùng bài, ngay sau đó, thêm PDF: không phải đợi nhịp
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.7\n" + b"0" * 30_000)
    assert P.nhan("34153348", pdf, URL_ELS, bay_gio=T0 + timedelta(seconds=5), so=so, kho=kho, dtv=_dtv())[0] == 0
    # bài KHÁC cùng miền trong 60 giây: phải đợi
    t2 = _html(tmp_path, ma_phien, "35598721")
    ma2, tb2 = P.nhan("35598721", t2, URL_ELS, bay_gio=T0 + timedelta(seconds=20), so=so, kho=kho, dtv=_dtv())
    assert ma2 == 3 and "đợi" in tb2 and t2.exists()
    # không ghi đè
    t3 = _html(tmp_path, ma_phien, "34153348")
    ma3, tb3 = P.nhan("34153348", t3, URL_ELS, bay_gio=T0 + timedelta(seconds=90), so=so, kho=kho, dtv=_dtv())
    assert ma3 == 3 and "không ghi đè" in tb3


def test_nhan_khong_co_phien_bi_tu_choi(tmp_path, so):
    t = _html(tmp_path, "M1", "1")
    assert P.nhan("1", t, URL_ELS, bay_gio=T0, so=so, kho=tmp_path / "kho", dtv=_dtv())[0] == 3
    assert t.exists()


def test_cli_trang_thai_khong_phien(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(P, "SO_PHIEN", tmp_path / "khong.json")
    assert P.main(["--trang-thai"]) == 0
    assert "Không có phiên" in capsys.readouterr().out


# ── kho và bộ đọc sâu gắn nhãn đúng ──────────────────────────────────────────────────────────────────────────────────
D = _nap("_dtv_puq_test", "doc_toan_van_co_nguoi.py")
DS = _nap("_ds_puq_test", "doc_sau_toan_van.py")


def test_kho_tinh_la_may_co_toan_van_khong_phai_oa(tmp_path):
    (tmp_path / "PMID-34153348_CHR.pdf").write_bytes(b"%PDF-1.7 gia")
    assert D.bao_phu_cuc_bo(["34153348"], tmp_path) == {"34153348": "phien_chrome"}
    assert "phien_chrome" in D.TRANG_THAI_MAY_CO_TOAN_VAN


def test_doc_sau_pdf_chr_gan_nhan_phien_khong_phai_token_tdm(tmp_path, monkeypatch):
    # ≥ TOI_THIEU_KY_TU_PDF (3000) ký tự chữ — dưới ngưỡng thì bộ đọc coi là ảnh quét và đúng là không sinh bản đọc
    monkeypatch.setattr(DS, "_doc_pdf", lambda pdf: (["Title\nAbstract\n" + "word " * 900], "Title"))
    (tmp_path / "PMID-34153348_CHR.pdf").write_bytes(b"%PDF-1.7 gia")
    nhom, ghi_chu = DS.xu_ly_pmid("34153348", tmp_path, lam_lai=False)
    assert nhom == "vua_sinh_tdm" and DS.NHAN_NGUON_CHR in ghi_chu
    md = (tmp_path / "doc_sau" / "PMID-34153348.md").read_text(encoding="utf-8")
    assert DS.NHAN_NGUON_CHR in md and "token" not in md and "KHÔNG phải OA" in md


def test_doc_sau_html_chr_doc_truc_tiep(tmp_path):
    (tmp_path / "PMID-34153348_CHR.html").write_text("<article>x</article>", encoding="utf-8")
    assert DS.xu_ly_pmid("34153348", tmp_path, lam_lai=False)[0] == "doc_truc_tiep"


# ── PDF nhúng trong HTML: mỗi bài MỘT lần tải (Chrome chặn lần tải tự động thứ hai trên cùng trang) ───────────────────
def _html_pdf(tmp_path, ma, pmid, pdf_bytes):
    import base64
    t = tmp_path / f"nhung-{pmid}.html"
    b64 = base64.b64encode(pdf_bytes).decode()
    t.write_text(f"<!-- ebm-phien:{ma} pmid:{pmid} url:{URL_ELS} -->\n<article>{'x' * 6000}</article>"
                 f'<script type="application/pdf;base64" id="ebm-pdf">{b64}</script>', encoding="utf-8")
    return t


def test_pdf_nhung_tach_thanh_hai_tep(tmp_path, so):
    _mo(so)
    ma = P.doc_phien(so)["ma"]
    kho = tmp_path / "kho"
    pdf = b"%PDF-1.7\n" + b"1" * 40_000
    t = _html_pdf(tmp_path, ma, "34024117", pdf)
    kq, tb = P.nhan("34024117", t, URL_ELS, bay_gio=T0, so=so, kho=kho, dtv=_dtv())
    assert kq == 0, tb
    assert (kho / "PMID-34024117_CHR.pdf").read_bytes() == pdf
    html = (kho / "PMID-34024117_CHR.html").read_text(encoding="utf-8")
    assert "ebm-pdf" not in html and "<article>" in html          # HTML lưu GỌN, không mang base64
    assert not t.exists()                                         # không để bản sao thứ hai trong Downloads
    assert sorted(x["loai"] for x in P.doc_phien(so)["lich_su"]) == ["html", "pdf"]


def test_pdf_nhung_hong_hoac_khong_phai_pdf_bi_tu_choi(tmp_path):
    t = _html_pdf(tmp_path, "M1", "5", b"KHONG-PHAI-PDF" * 3000)
    loai, ly = P.kiem_tep(t, "5", "M1")
    assert loai is None and "PDF" in ly
    hong = tmp_path / "hong.html"
    hong.write_text(f"<!-- ebm-phien:M1 pmid:5 url:{URL_ELS} -->\n<article>{'x' * 6000}</article>"
                    '<script type="application/pdf;base64" id="ebm-pdf">@@@không-phải-base64@@@</script>', encoding="utf-8")
    assert P.kiem_tep(hong, "5", "M1")[0] is None
