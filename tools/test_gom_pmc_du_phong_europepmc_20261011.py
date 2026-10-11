# -*- coding: utf-8 -*-
"""Tầng PMC của `gom_toan_van_dashboard.py` khi NCBI chặn IP (11/10/2026) — dự phòng Europe PMC.

Đo thật: NCBI trả trang HTML «Blocked Diagnostic» ⇒ elink nổ JSONDecodeError ⇒ bước gom `return 2` NGAY, bỏ cả tầng Unpaywall —
lượt toàn văn 63 chủ đề còn 49 bài «có bản truy cập mở mà chưa gom». Thêm: trang chặn có «<body» nên phép kiểm cũ
`b"<body" in xml` sẽ lưu NHẦM trang chặn làm toàn văn. Ngoại tuyến hoàn toàn.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("_gom_pmc_dp", REPO / "tools" / "gom_toan_van_dashboard.py")
g = importlib.util.module_from_spec(sp)
sp.loader.exec_module(g)

JATS = b'<?xml version="1.0"?><article><front/><body><sec><p>Methods</p></sec></body></article>'
STUB = b'<?xml version="1.0"?><article><front/></article>'
CHAN = (b'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"><html><head><title>NCBI - WWW Error Blocked Diagnostic</title>'
        b"</head><body>blocked</body></html>")


def _gom(tai=None, lien_ket=None):
    goi: list[str] = []

    def tai_toan_van(pmcid):
        goi.append(pmcid)
        return tai(pmcid) if tai else JATS

    def lien_ket_pmc(pmids):
        if isinstance(lien_ket, Exception):
            raise lien_ket
        return lien_ket or {}
    return types.SimpleNamespace(tai_toan_van=tai_toan_van, lien_ket_pmc=lien_ket_pmc), goi


def _lay_epmc(ket_qua: list[dict], toan_van: dict[str, bytes | Exception], goi: list[str] | None = None):
    def lay(url, timeout=60):
        if goi is not None:
            goi.append(url)
        if "/search?" in url:
            return json.dumps({"resultList": {"result": ket_qua}}).encode()
        pmc = url.split("/rest/")[1].split("/")[0]
        v = toan_van.get(pmc, OSError("500"))
        if isinstance(v, Exception):
            raise v
        return v
    return lay


def test_la_jats_toan_van_khong_nhan_trang_chan_hay_html():
    assert g.la_jats_toan_van(JATS)
    assert not g.la_jats_toan_van(CHAN), "trang chặn NCBI có «<body» — không được coi là toàn văn"
    assert not g.la_jats_toan_van(b"<html><body><article>x</article></body></html>")
    assert not g.la_jats_toan_van(STUB) and not g.la_jats_toan_van(None) and not g.la_jats_toan_van(b"")


def test_lien_ket_pmc_epmc_theo_lo_va_co_oa():
    pmids = [str(100000 + i) for i in range(85)]
    goi: list[str] = []
    kq = [{"pmid": "100000", "pmcid": "PMC9", "isOpenAccess": "Y"}, {"pmid": "100001", "pmcid": "PMC8", "isOpenAccess": "N"},
          {"pmid": "999999", "pmcid": "PMC7", "isOpenAccess": "Y"}, {"pmid": "100002"}]
    ra = g.lien_ket_pmc_epmc(pmids, lay=_lay_epmc(kq, {}, goi))
    assert ra == {"100000": ("9", True), "100001": ("8", False)}, "chỉ PMID của lô, bỏ bản ghi không PMCID"
    assert len(goi) == 2, "85 PMID ⇒ 2 lô 80"


def test_tai_jats_ncbi_tot_khong_goi_europepmc():
    gom, _ = _gom()
    goi: list[str] = []
    assert g.tai_jats(gom, "9", None, {}, lay=_lay_epmc([], {}, goi)) == (JATS, "ok") and goi == []
    gom2, _ = _gom(tai=lambda p: None)
    assert g.tai_jats(gom2, "9", None, {}, lay=_lay_epmc([], {}, goi)) == (None, "khong_oa") and goi == []


def test_tai_jats_trang_chan_chuyen_europepmc_va_ngung_goi_ncbi():
    gom, goi_ncbi = _gom(tai=lambda p: CHAN)
    trang: dict = {}
    lay = _lay_epmc([], {"PMC9": JATS, "PMC8": JATS})
    assert g.tai_jats(gom, "9", None, trang, lay=lay) == (JATS, "ok")
    assert trang["ncbi_chan"] is True
    assert g.tai_jats(gom, "8", None, trang, lay=lay) == (JATS, "ok")
    assert goi_ncbi == ["9"], "thấy trang chặn một lần thì không gọi NCBI nữa"


def test_tai_jats_ncbi_loi_mang_thi_thu_europepmc():
    def no(p):
        raise OSError("hết giờ")
    gom, _ = _gom(tai=no)
    assert g.tai_jats(gom, "9", None, {}, lay=_lay_epmc([], {"PMC9": JATS})) == (JATS, "ok")


def test_tai_jats_khong_oa_theo_europepmc_khong_goi_va_khong_ghi_so():
    gom, goi_ncbi = _gom()
    goi: list[str] = []
    assert g.tai_jats(gom, "9", False, {}, lay=_lay_epmc([], {}, goi)) == (None, "khong_oa_epmc")
    assert goi == [] and goi_ncbi == []


def test_tai_jats_europepmc_hong_la_loi_khong_phai_khong_oa():
    gom, _ = _gom(tai=lambda p: CHAN)
    assert g.tai_jats(gom, "9", None, {}, lay=_lay_epmc([], {"PMC9": OSError("500")})) == (None, "loi")
    assert g.tai_jats(gom, "9", None, {}, lay=_lay_epmc([], {"PMC9": CHAN})) == (None, "loi")


def _main(monkeypatch, tmp_path, argv, gom, lay):
    monkeypatch.setattr(g, "KHO", tmp_path)
    monkeypatch.setattr(g, "_nap_gom", lambda: gom)
    monkeypatch.setattr(g, "_lay", lay)
    monkeypatch.setattr(g.time, "sleep", lambda s: None)
    monkeypatch.setattr(sys, "argv", ["gom_toan_van_dashboard.py", *argv])
    return g.main()


def test_main_elink_chet_van_gom_qua_europepmc_va_khong_ghi_so_oan(monkeypatch, tmp_path):
    gom, goi_ncbi = _gom(lien_ket=json.JSONDecodeError("x", "<html>", 0))
    kq = [{"pmid": "111111", "pmcid": "PMC9", "isOpenAccess": "Y"}, {"pmid": "222222", "pmcid": "PMC8", "isOpenAccess": "N"}]
    ma = _main(monkeypatch, tmp_path, ["--pmid", "111111", "222222", "333333"], gom, _lay_epmc(kq, {"PMC9": JATS}))
    assert ma == 0
    assert (tmp_path / "PMID-111111_PMC9.xml").read_bytes() == JATS
    assert not list(tmp_path.glob("PMID-222222*")) and goi_ncbi == []
    so = (tmp_path / "khong-oa.txt").read_text(encoding="utf-8") if (tmp_path / "khong-oa.txt").exists() else ""
    assert "222222" not in so and "333333" not in so, "Europe PMC nói «không OA/không bản ghi» ≠ sổ 30 ngày của NCBI"


def test_main_ca_hai_nguon_chet_van_chay_unpaywall_va_tra_ma_2(monkeypatch, tmp_path):
    gom, _ = _gom(lien_ket=json.JSONDecodeError("x", "<html>", 0))

    def lay_chet(url, timeout=60):
        raise OSError("mất mạng")
    da_goi: list[list[str]] = []
    monkeypatch.setattr(g, "tang_unpaywall", lambda thu, gom=None: (da_goi.append(list(thu)), (0, list(thu)))[1])
    ma = _main(monkeypatch, tmp_path, ["--pmid", "111111", "--unpaywall"], gom, lay_chet)
    assert ma == 2, "tầng PMC chưa gom được ⇒ không được báo xong"
    assert da_goi == [["111111"]], "tầng Unpaywall vẫn phải chạy"
    so = (tmp_path / "khong-oa.txt").read_text(encoding="utf-8") if (tmp_path / "khong-oa.txt").exists() else ""
    assert "111111" not in so


@pytest.mark.parametrize("xml", [CHAN, b"<!DOCTYPE html><html><body><article><p>trang NXB</p></article></body></html>"],
                         ids=["trang-chan-ncbi", "html5-co-article"])
def test_main_ncbi_tra_html_khong_bao_gio_luu_lam_toan_van(monkeypatch, tmp_path, xml):
    gom, _ = _gom(tai=lambda p: xml, lien_ket={"111111": "9"})
    ma = _main(monkeypatch, tmp_path, ["--pmid", "111111"], gom, _lay_epmc([], {"PMC9": OSError("500")}))
    assert ma == 0 and not list(tmp_path.glob("PMID-111111_*"))
