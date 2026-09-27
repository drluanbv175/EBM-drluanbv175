"""Sổ xác minh nhận bằng chứng TRÌNH DUYỆT THẬT cho miền chặn kiểm tự động, đúng như cổng — vá 27/09/2026.

Đo 27/09 (orchestrator `--cu-nhat 5`): bước A4 của gói Orlistat_AKI_FDA đỏ vì URL fda.gov «chưa xác minh lần nào», trong
khi cổng B2 cho qua nhờ bằng chứng mở bằng trình duyệt ngày 24/09. Sổ gọi `verify_url_online` không kèm đường dashboard
nên không bao giờ tra bằng chứng đó. Test dùng CHÍNH bản cổng trong git; mạng được thay bằng hàm giả trả «bị chặn».
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
URL_FDA = "https://www.fda.gov/safety/medical-product-safety-information/vi-du"


def _nap(ten: str, tep: Path):
    sp = importlib.util.spec_from_file_location(ten, tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


@pytest.fixture()
def moi_truong(tmp_path, monkeypatch):
    sx = _nap("sx_url_trinh_duyet_20260927", GOC / "tools" / "so_xac_minh_nguon.py")
    vd = _nap("vd_url_trinh_duyet_20260927",
              GOC / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py")
    monkeypatch.setattr(sx, "DASH", tmp_path)
    monkeypatch.setattr(vd, "verify_url_online", lambda url, *a, **k: (None, "HTTP 404 (bị chặn kiểm tự động)"))

    def ghi(url: str, ngay: dt.date) -> None:
        (tmp_path / vd.SO_URL_TRINH_DUYET).write_text(json.dumps({"muc": [{
            "url": url, "tieu_de": "FDA approves labeling changes — trang thật", "ngay": ngay.isoformat(),
            "cach": "mở bằng trình duyệt thật"}]}, ensure_ascii=False), encoding="utf-8")
    return sx, vd, ghi


def test_mien_chan_co_bang_chung_trinh_duyet_thi_xac_minh_theo_ngay_bang_chung(moi_truong):
    sx, vd, ghi = moi_truong
    ngay = dt.date.today() - dt.timedelta(days=3)
    ghi(URL_FDA, ngay)
    bg = sx.xac_minh_mot(f"url:{URL_FDA}", vd)
    assert bg is not None, "cổng nhận bằng chứng trình duyệt mà sổ vẫn «chưa xác minh»"
    assert bg["nguon_xac_minh"] == "trinh_duyet"
    assert bg["xac_minh_luc"].startswith(ngay.isoformat()), "ngày xác minh phải là ngày của bằng chứng, không phải hôm nay"
    assert sx.con_hieu_luc(bg) == (True, "")


def test_mien_chan_khong_co_bang_chung_van_chua_xac_minh(moi_truong):
    sx, vd, _ghi = moi_truong
    assert sx.xac_minh_mot(f"url:{URL_FDA}", vd) is None


def test_bang_chung_qua_han_180_ngay_khong_duoc_nhan(moi_truong):
    sx, vd, ghi = moi_truong
    ghi(URL_FDA, dt.date.today() - dt.timedelta(days=200))
    assert sx.xac_minh_mot(f"url:{URL_FDA}", vd) is None


def test_mien_khong_khai_bao_chan_thi_bang_chung_trinh_duyet_khong_thay_duoc_kiem_mang(moi_truong):
    sx, vd, ghi = moi_truong
    url = "https://example.org/bai-bao"
    ghi(url, dt.date.today())
    assert sx.xac_minh_mot(f"url:{url}", vd) is None, "chỉ miền ĐÃ KHAI BÁO chặn tự động mới được dùng bằng chứng trình duyệt"
