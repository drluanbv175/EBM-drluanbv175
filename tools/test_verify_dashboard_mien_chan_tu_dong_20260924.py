"""Khoá bản sửa 24/09/2026: cổng liêm chính báo «URL không tồn tại» với trang FDA CÓ THẬT.

www.fda.gov trả HTTP 404 cho trình khách tự động của cổng (urllib + SOURCE_GATE_USER_AGENT) trong khi
trình duyệt thật mở được đúng trang. Bản sửa KHÔNG giả dạng trình duyệt: với miền đã khai báo chặn kiểm
tự động, 403/404/410 không còn là «link chết» mà đòi bằng chứng mở bằng trình duyệt thật trong sổ
`url-xac-minh-trinh-duyet.json` cạnh dashboard. Các test dưới đây canh cả hai chiều: trang thật không bị
chặn oan, và URL bịa / link chết thật / bằng chứng giả KHÔNG lọt qua.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import urllib.error
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"

_spec = importlib.util.spec_from_file_location("vd_mien_chan_test", NGUON)
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

URL_FDA = ("https://www.fda.gov/safety/medical-product-safety-information/"
           "fda-approves-labeling-changes-over-counter-otc-weight-loss-drug-alli-orlistat-warn-risk-kidney")
URL_KHAC = "https://example.org/trang-da-go"


def _gia_mo(ma):
    def _mo(url, timeout=15):
        raise urllib.error.HTTPError(url, ma, "loi gia lap", hdrs=None, fp=None)
    return _mo


class _PhanHoi200:
    status = 200

    def read(self, n=-1):
        return b"<html>"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture
def dashboard(tmp_path):
    p = tmp_path / "WebDashboard_thu.html"
    p.write_text("<html></html>", encoding="utf-8")
    return p


def _ghi_so(thu_muc, muc):
    (thu_muc / V.SO_URL_TRINH_DUYET).write_text(json.dumps({"muc": muc}, ensure_ascii=False),
                                                 encoding="utf-8")


def _muc(url=URL_FDA, ngay=None, tieu_de="FDA Approves Labeling Changes for alli (Orlistat)",
         cach="trình duyệt trong app Claude"):
    return {"url": url, "tieu_de": tieu_de, "ngay": (ngay or date.today()).isoformat(), "cach": cach}


def test_mien_chua_khai_bao_404_van_la_link_chet(monkeypatch, dashboard):
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(404))
    ok, info = V.verify_url_online(URL_KHAC, retries=0, duong_dashboard=dashboard)
    assert ok is False and "không tồn tại" in info


def test_fda_mo_duoc_thi_dat_khong_can_so(monkeypatch, dashboard):
    monkeypatch.setattr(V, "source_urlopen", lambda url, timeout=15: _PhanHoi200())
    ok, _ = V.verify_url_online(URL_FDA, retries=0, duong_dashboard=dashboard)
    assert ok is True


def test_fda_bi_chan_khong_co_bang_chung_la_chua_xac_minh(monkeypatch, dashboard):
    """Không có bằng chứng ⇒ None (strict-sources vẫn chặn), KHÔNG phải False «link chết», KHÔNG phải True."""
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(404))
    ok, info = V.verify_url_online(URL_FDA, retries=0, duong_dashboard=dashboard)
    assert ok is None
    assert "KHÔNG phải bằng chứng link chết" in info and V.SO_URL_TRINH_DUYET in info


@pytest.mark.parametrize("ma", [403, 404, 410])
def test_fda_bi_chan_co_bang_chung_con_han_thi_dat(monkeypatch, dashboard, ma):
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(ma))
    _ghi_so(dashboard.parent, [_muc()])
    ok, info = V.verify_url_online(URL_FDA, retries=0, duong_dashboard=dashboard)
    assert ok is True and "đã mở bằng trình duyệt" in info


def test_bang_chung_qua_han_khong_duoc_tinh(monkeypatch, dashboard):
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(404))
    _ghi_so(dashboard.parent, [_muc(ngay=date.today() - timedelta(days=V.URL_TRINH_DUYET_HAN_NGAY + 1))])
    ok, info = V.verify_url_online(URL_FDA, retries=0, duong_dashboard=dashboard)
    assert ok is None and "quá" in info


def test_bang_chung_ngay_tuong_lai_hoac_tieu_de_gia_bi_tu_choi(monkeypatch, dashboard):
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(404))
    _ghi_so(dashboard.parent, [_muc(ngay=date.today() + timedelta(days=1)), _muc(tieu_de="ok")])
    ok, _ = V.verify_url_online(URL_FDA, retries=0, duong_dashboard=dashboard)
    assert ok is None


def test_nhieu_muc_cung_url_chi_can_mot_muc_con_han(monkeypatch, dashboard):
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(404))
    _ghi_so(dashboard.parent, [_muc(ngay=date.today() - timedelta(days=400)), _muc()])
    ok, _ = V.verify_url_online(URL_FDA, retries=0, duong_dashboard=dashboard)
    assert ok is True


def test_bang_chung_chi_ap_cho_dung_url(monkeypatch, dashboard):
    """Mục cho một URL KHÁC cùng miền không được tính — URL fda.gov bịa không lọt qua."""
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(404))
    _ghi_so(dashboard.parent, [_muc(url="https://www.fda.gov/trang-khac")])
    ok, _ = V.verify_url_online(URL_FDA, retries=0, duong_dashboard=dashboard)
    assert ok is None


def test_so_trinh_duyet_khong_ha_404_cua_mien_chua_khai_bao(monkeypatch, dashboard):
    """Miền chưa khai báo: có mục trong sổ cũng KHÔNG hạ 404 — muốn thế phải khai báo miền kèm bằng chứng."""
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(404))
    _ghi_so(dashboard.parent, [_muc(url=URL_KHAC)])
    ok, _ = V.verify_url_online(URL_KHAC, retries=0, duong_dashboard=dashboard)
    assert ok is False


def test_loi_goi_that_trong_main_truyen_duong_dashboard():
    """Chốt không ai gọi thì không tồn tại: mọi lời gọi verify_url_online trong main() phải truyền
    duong_dashboard (kiểm bằng cây cú pháp, không khớp chuỗi cả tệp)."""
    cay = ast.parse(NGUON.read_text(encoding="utf-8"))
    main = next(n for n in cay.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    goi = [n for n in ast.walk(main)
           if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "verify_url_online"]
    assert goi, "main() không còn gọi verify_url_online"
    assert all(any(k.arg == "duong_dashboard" for k in g.keywords) for g in goi)
