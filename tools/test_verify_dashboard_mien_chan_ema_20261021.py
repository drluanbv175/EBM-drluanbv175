"""Khoá bản sửa 21/10/2026 (bác sĩ duyệt): khai www.ema.europa.eu vào MIEN_CHAN_TRUY_CAP_TU_DONG.

EMA trả HTTP 403 CloudFront «Request blocked» cho MỌI trình khách khi đi qua IP của VPN (cả trình duyệt trong app); VPN tắt thì
mở bình thường, nhưng khi đó NCBI lại chặn IP Việt Nam. Trước bản sửa, mỗi gói EMA phải tắt VPN riêng cho bước cổng rồi bật lại
(lô 20261018T143247-lo dừng ba lần). Sau bản sửa: 403 của EMA đi đường sổ trình duyệt như FDA — CHỈ đạt khi có bằng chứng còn
hạn đúng URL. Các test canh cả hai chiều: trang EMA thật không bị chặn oan, còn miền giả dạng / tiêu đề trang lỗi / bằng chứng
sai URL / mã lỗi khác KHÔNG lọt qua. Ngoại tuyến hoàn toàn.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import urllib.error
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"


def _nap(duong: Path, ten: str):
    spec = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


V = _nap(NGUON, "vd_mien_chan_ema_test")
XN = _nap(REPO / "tools" / "xac_nhan_trinh_duyet.py", "xn_mien_chan_ema_test")

URL_EMA = ("https://www.ema.europa.eu/en/news/"
           "meeting-highlights-pharmacovigilance-risk-assessment-committee-prac-8-11-june-2026")
TIEU_DE_THAT = ("Meeting highlights from the Pharmacovigilance Risk Assessment Committee (PRAC) 8-11 June 2026 | "
                "European Medicines Agency (EMA)")
# Đúng tiêu đề trang CloudFront mà trình duyệt trong app thấy khi VPN bật (đo 21/10/2026).
TIEU_DE_CLOUDFRONT = "ERROR: The request could not be satisfied"


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
    p = tmp_path / "WebDashboard_thu_ema.html"
    p.write_text("<html></html>", encoding="utf-8")
    return p


def _ghi_so(thu_muc, url=URL_EMA, tieu_de=TIEU_DE_THAT):
    muc = {"url": url, "tieu_de": tieu_de, "ngay": date.today().isoformat(),
           "cach": "trình duyệt trong app Claude, VPN tắt"}
    (thu_muc / V.SO_URL_TRINH_DUYET).write_text(json.dumps({"muc": [muc]}, ensure_ascii=False), encoding="utf-8")


@pytest.mark.parametrize("url", [URL_EMA, "https://ema.europa.eu/en/x"])
def test_mien_ema_da_khai_bao(url):
    assert V.mien_chan_tu_dong(url) in {"www.ema.europa.eu", "ema.europa.eu"}


@pytest.mark.parametrize("url", ["https://www.ema.europa.eu.evil.com/en/x", "https://fake-ema.europa.eu/en/x",
                                 "https://ema.europa.eu.example.org/x"])
def test_mien_gia_dang_ema_khong_duoc_nhan(url):
    """Khớp ĐÚNG tên máy chủ — miền mượn chữ «ema.europa.eu» không được đi đường sổ trình duyệt."""
    assert V.mien_chan_tu_dong(url) is None


def test_ema_mo_duoc_thi_dat_khong_can_so(monkeypatch, dashboard):
    """VPN tắt: urllib nhận 200 ⇒ đạt như mọi trang khác, không cần sổ."""
    monkeypatch.setattr(V, "source_urlopen", lambda url, timeout=15: _PhanHoi200())
    ok, _ = V.verify_url_online(URL_EMA, retries=0, duong_dashboard=dashboard)
    assert ok is True


def test_ema_403_khong_co_bang_chung_van_chua_xac_minh(monkeypatch, dashboard):
    """403 KHÔNG tự thành đạt: thiếu bằng chứng ⇒ None (strict-sources vẫn chặn), không phải False «link chết»."""
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(403))
    ok, info = V.verify_url_online(URL_EMA, retries=0, duong_dashboard=dashboard)
    assert ok is None
    assert V.SO_URL_TRINH_DUYET in info


def test_ema_403_co_bang_chung_con_han_thi_dat(monkeypatch, dashboard):
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(403))
    _ghi_so(dashboard.parent)
    ok, info = V.verify_url_online(URL_EMA, retries=0, duong_dashboard=dashboard)
    assert ok is True and "đã mở bằng trình duyệt" in info


def test_bang_chung_ema_chi_ap_cho_dung_url(monkeypatch, dashboard):
    """Bằng chứng của trang PRAC tháng 6 không cho trang PRAC khác (hay URL bịa cùng miền) đi qua."""
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(403))
    _ghi_so(dashboard.parent)
    ok, _ = V.verify_url_online(URL_EMA.replace("8-11-june", "6-9-july"), retries=0, duong_dashboard=dashboard)
    assert ok is None


def test_ema_500_van_la_loi_mang_du_co_bang_chung(monkeypatch, dashboard):
    monkeypatch.setattr(V, "source_urlopen", _gia_mo(500))
    _ghi_so(dashboard.parent)
    ok, info = V.verify_url_online(URL_EMA, retries=0, duong_dashboard=dashboard)
    assert ok is None and "lỗi mạng" in info


def test_tieu_de_trang_cloudfront_va_ten_co_quan_bi_tu_choi():
    assert XN.kiem_tieu_de(TIEU_DE_CLOUDFRONT) is not None
    assert XN.kiem_tieu_de("European Medicines Agency") is not None
    assert XN.kiem_tieu_de("European Medicines Agency (EMA)") is not None
    assert XN.kiem_tieu_de(TIEU_DE_THAT) is None


def test_ghi_bang_chung_ema_duoc_cong_nhan(tmp_path):
    """`--ghi` nhận URL EMA (miền đã khai) và tự kiểm lại bằng chính hàm của cổng."""
    ma, info = XN.ghi(V, URL_EMA, TIEU_DE_THAT, "Claude_Browser, VPN tắt: đọc title + h1 trang PRAC 8-11/6/2026", "bác sĩ",
                      thu_muc=tmp_path, sao_luu=tmp_path / "sao-luu")
    assert ma == 0, info
    so = json.loads((tmp_path / V.SO_URL_TRINH_DUYET).read_text(encoding="utf-8"))
    assert [m["url"] for m in so["muc"]] == [URL_EMA]


def test_ghi_tu_choi_tieu_de_cloudfront(tmp_path):
    ma, _ = XN.ghi(V, URL_EMA, TIEU_DE_CLOUDFRONT, "Claude_Browser khi VPN bật", "bác sĩ",
                   thu_muc=tmp_path, sao_luu=tmp_path / "sao-luu")
    assert ma == 3
    assert not (tmp_path / V.SO_URL_TRINH_DUYET).exists()
