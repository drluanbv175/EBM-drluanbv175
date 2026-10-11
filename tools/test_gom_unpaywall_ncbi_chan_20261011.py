# -*- coding: utf-8 -*-
"""Tầng 2 Unpaywall khi NCBI chặn IP (11/10/2026) — `gom_toan_van_dashboard.doi_cua_pmid`.

Lỗi thật đo được 11/10: NCBI trả trang HTML «Blocked Diagnostic» (mã 200) cho mọi esummary ⇒ bước đổi PMID→DOI nổ
JSONDecodeError ⇒ cả 13 bài của chủ đề COPD báo «chưa lấy được» như thể Unpaywall hỏng; tầng 2 không chạy được bài nào.
Nay: NCBI chặn ⇒ lấy DOI qua Europe PMC và cả lượt không gọi NCBI nữa. Ngoại tuyến hoàn toàn (urlopen giả).
"""
from __future__ import annotations

import importlib.util
import io
import json
import types
import urllib.error
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap():
    sp = importlib.util.spec_from_file_location("_gom_tv_ncbi_chan_test", REPO / "tools" / "gom_toan_van_dashboard.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


g = _nap()

TRANG_CHAN = (b'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"> <html><head>'
              b"<title>NCBI - WWW Error Blocked Diagnostic</title></head><body>blocked</body></html>")
IMRAD = "Introduction " + "a " * 900 + " Methods " + "b " * 900 + " Results " + "c " * 900 + " Discussion " + "d " * 200


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


def _mang(monkeypatch, *, ncbi, epmc, da_goi):
    """ncbi(pm) → bytes | Exception; epmc(pm) → dict kết quả Europe PMC (rỗng = không có bản ghi) | Exception."""
    def urlopen(req, timeout=None, context=None):
        url = req if isinstance(req, str) else req.full_url
        da_goi.append(url)
        if "esummary.fcgi" in url:
            kq = ncbi(url.split("id=")[1].split("&")[0])
        elif "europepmc" in url:
            pm = url.split("EXT_ID%3A")[1].split("%20")[0]
            kq = epmc(pm)
            if isinstance(kq, dict):
                kq = json.dumps({"resultList": {"result": [kq] if kq else []}}).encode()
        elif "api.unpaywall.org" in url:
            kq = json.dumps({"is_oa": True, "best_oa_location": {"url": "https://repo.example/cc",
                                                                   "license": "cc-by"}}).encode()
        else:
            kq = ("<html><body>" + IMRAD + "</body></html>").encode()
        if isinstance(kq, Exception):
            raise kq
        return _PhanHoi(kq, url)
    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    monkeypatch.setattr(g, "_email_lich_su", lambda: "test@example.org")
    monkeypatch.setattr(g.time, "sleep", lambda s: None)
    monkeypatch.setattr(g, "_nap_dtv", lambda: types.SimpleNamespace(
        DIEU_KHOAN_NXB={}, nxb_cua=lambda doi="", url="", tieu_de="": (None, None),
        uy_quyen_bac_si=lambda ten, hom_nay=None: None))


def _json_ncbi(pm, doi):
    return json.dumps({"result": {pm: {"articleids": [{"idtype": "doi", "value": doi}] if doi else []}}}).encode()


def test_nhan_dien_trang_chan_ncbi():
    assert g.la_trang_chan_ncbi(TRANG_CHAN)
    assert not g.la_trang_chan_ncbi(_json_ncbi("1", "10.1/x"))


def test_ncbi_chan_thi_lay_doi_qua_europepmc_va_ngung_goi_ncbi(monkeypatch, tmp_path):
    da_goi: list[str] = []
    monkeypatch.setattr(g, "KHO", tmp_path)
    _mang(monkeypatch, ncbi=lambda pm: TRANG_CHAN, epmc=lambda pm: {"pmid": pm, "doi": f"10.9999/cc{pm}"}, da_goi=da_goi)
    moi, thieu = g.tang_unpaywall(["111", "222"])
    assert moi == 2 and thieu == []
    assert (tmp_path / "PMID-111_UPW.html").exists() and (tmp_path / "PMID-222_UPW.html").exists()
    assert sum("esummary.fcgi" in u for u in da_goi) == 1, "thấy trang chặn một lần thì cả lượt không gọi NCBI nữa"
    assert any("api.unpaywall.org/v2/10.9999/cc222" in u for u in da_goi)


def test_ncbi_tot_thi_khong_goi_europepmc(monkeypatch, tmp_path):
    da_goi: list[str] = []
    monkeypatch.setattr(g, "KHO", tmp_path)
    _mang(monkeypatch, ncbi=lambda pm: _json_ncbi(pm, "10.9999/ncbi"), epmc=lambda pm: {}, da_goi=da_goi)
    moi, _ = g.tang_unpaywall(["111"])
    assert moi == 1 and not any("europepmc" in u for u in da_goi)


def test_loi_mang_le_te_chi_chuyen_bai_do_khong_danh_dau_chan(monkeypatch, tmp_path):
    da_goi: list[str] = []
    monkeypatch.setattr(g, "KHO", tmp_path)
    lan = {"n": 0}

    def ncbi(pm):
        lan["n"] += 1
        return urllib.error.URLError("hết giờ") if lan["n"] == 1 else _json_ncbi(pm, "10.9999/ncbi")
    _mang(monkeypatch, ncbi=ncbi, epmc=lambda pm: {"pmid": pm, "doi": "10.9999/epmc"}, da_goi=da_goi)
    moi, thieu = g.tang_unpaywall(["111", "222"])
    assert moi == 2 and thieu == []
    assert sum("esummary.fcgi" in u for u in da_goi) == 2, "lỗi mạng một lần KHÔNG phải bị chặn — bài sau vẫn thử NCBI"
    assert sum("europepmc" in u for u in da_goi) == 1


def test_khong_nguon_nao_tra_loi_thi_bao_chua_lay_duoc_khong_coi_la_khong_doi(monkeypatch, tmp_path, capsys):
    da_goi: list[str] = []
    monkeypatch.setattr(g, "KHO", tmp_path)
    _mang(monkeypatch, ncbi=lambda pm: TRANG_CHAN, epmc=lambda pm: {}, da_goi=da_goi)
    moi, thieu = g.tang_unpaywall(["111"])
    assert moi == 0 and thieu == ["111"] and not list(tmp_path.glob("PMID-*"))
    assert "chưa lấy được" in capsys.readouterr().out
    assert not any("api.unpaywall.org" in u for u in da_goi)


def test_bai_that_su_khong_co_doi_thi_khong_hoi_europepmc(monkeypatch, tmp_path):
    da_goi: list[str] = []
    monkeypatch.setattr(g, "KHO", tmp_path)
    _mang(monkeypatch, ncbi=lambda pm: _json_ncbi(pm, ""), epmc=lambda pm: {"pmid": pm, "doi": "10.9999/x"}, da_goi=da_goi)
    moi, thieu = g.tang_unpaywall(["111"])
    assert moi == 0 and thieu == ["111"]
    assert not any("europepmc" in u for u in da_goi), "NCBI trả lời «không có DOI» là câu trả lời hợp lệ"


@pytest.mark.parametrize("loi", [ValueError("json hỏng"), urllib.error.URLError("x")])
def test_doi_cua_pmid_hai_nguon_cung_hong_thi_nem_loi(monkeypatch, loi):
    _mang(monkeypatch, ncbi=lambda pm: TRANG_CHAN, epmc=lambda pm: loi, da_goi=[])
    with pytest.raises((ValueError, OSError)):
        g.doi_cua_pmid("111", "test@example.org", {})
