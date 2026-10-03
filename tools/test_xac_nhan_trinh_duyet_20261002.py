#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy 02/10/2026: trang chặn bot ⇒ máy mở trang, BÁC SĨ tự xác nhận, máy ghi bằng chứng (bác sĩ yêu cầu).

Sự cố gốc: www.fda.gov trả 401 + trang «Sorry! This resembles an automated request»; một URL thiếu bằng chứng trình duyệt làm
dừng CẢ lô `ops/orchestrator.py`. Kiểm: (1) hàng chờ đúng điều kiện `urls_only` của cổng; (2) `--ghi` từ chối tiêu đề trang
chặn/lỗi/tên cơ quan, miền chưa khai, thiếu cách kiểm; ghi có sao lưu, tự kiểm lại bằng hàm của cổng, hoàn nguyên khi cổng không
nhận; sổ hỏng thì không ghi đè; (3) orchestrator đổi «hạ tầng» của B2 thành việc 👤 và lô đi tiếp. Ngoại tuyến hoàn toàn."""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    spec = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


xn = _nap("tools/xac_nhan_trinh_duyet.py", "xn_t")
vd = _nap("sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py", "vd_xn_t")
op = _nap("ops/orchestrator.py", "op_xn_t")

URL_FDA = "https://www.fda.gov/safety/medical-product-safety-information/alli-orlistat-kidney"
URL_FDA2 = "https://www.fda.gov/news-events/press-announcements/oral-pcsk9"
HOM_NAY = date(2026, 10, 2)


def _dashboard(thu_muc: Path, ten: str, cac_muc: list[str]) -> Path:
    p = thu_muc / f"WebDashboard_{ten}.html"
    p.write_text("<html><script>const DATA = {meta:{}, items:[" + ",".join(cac_muc) + "]};\n// HẾT KHỐI DATA\n</script></html>",
                 encoding="utf-8")
    return p


def _so(thu_muc: Path, muc: list[dict]) -> Path:
    p = thu_muc / vd.SO_URL_TRINH_DUYET
    p.write_text(json.dumps({"_about": "x", "muc": muc}, ensure_ascii=False), encoding="utf-8")
    return p


def _bc(url=URL_FDA, ngay=HOM_NAY - timedelta(days=8), tieu_de="FDA Approves Labeling Changes for alli (Orlistat)"):
    return {"url": url, "tieu_de": tieu_de, "ngay": ngay.isoformat(), "cach": "Claude_Browser: đọc title + h1"}


@pytest.fixture()
def kho(tmp_path):
    d = tmp_path / "EBM-Dashboards"
    d.mkdir()
    _dashboard(d, "Orlistat", [f"{{id:'ITEM-01', url:'{URL_FDA}'}}"])
    _dashboard(d, "Lipid", [f"{{id:'ITEM-02', url:'{URL_FDA2}'}}",
                            f"{{id:'ITEM-03', pmid:'12345678', url:'{URL_FDA}'}}",      # có PMID ⇒ cổng không kiểm url
                            "{id:'ITEM-04', url:'https://example.org/x'}"])            # miền chưa khai ⇒ không vào hàng chờ
    return d


# ── hàng chờ ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_hang_cho_dung_dieu_kien_urls_only_cua_cong(kho):
    ds = xn.quet(vd, kho, hom_nay=HOM_NAY)
    assert {m["url"] for m in ds} == {URL_FDA, URL_FDA2}
    fda = next(m for m in ds if m["url"] == URL_FDA)
    assert fda["dung_o"] == ["WebDashboard_Orlistat.html#ITEM-01"], "mục có PMID không được tính (cổng không kiểm url của nó)"
    assert all(m["trang_thai"] == "THIEU" for m in ds)


def test_bang_chung_con_han_va_sap_het_han(kho):
    han = vd.URL_TRINH_DUYET_HAN_NGAY
    _so(kho, [_bc(ngay=HOM_NAY - timedelta(days=8)), _bc(url=URL_FDA2, ngay=HOM_NAY - timedelta(days=han - 10))])
    tt = {m["url"]: m for m in xn.quet(vd, kho, hom_nay=HOM_NAY)}
    assert tt[URL_FDA]["trang_thai"] == "CON_HAN" and tt[URL_FDA]["con_ngay"] == han - 8
    assert tt[URL_FDA2]["trang_thai"] == "SAP_HET_HAN" and tt[URL_FDA2]["con_ngay"] == 10
    assert [m["url"] for m in xn.can_xac_nhan(list(tt.values()))] == [URL_FDA2]


def test_bang_chung_qua_han_la_thieu(kho):
    _so(kho, [_bc(ngay=HOM_NAY - timedelta(days=vd.URL_TRINH_DUYET_HAN_NGAY + 1))])
    tt = {m["url"]: m for m in xn.quet(vd, kho, hom_nay=HOM_NAY)}
    assert tt[URL_FDA]["trang_thai"] == "THIEU" and "quá" in tt[URL_FDA]["ly_do"]


# ── kiểm tiêu đề ─────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("tieu_de", ["Sorry! This resembles an automated request", "I am not a bot", "Just a moment...",
                                     "Access Denied", "Page Not Found | FDA", "403 Forbidden", "U.S. Food and Drug Administration",
                                     "FDA", "", "  ngắn  ", "Attention Required! | Cloudflare", "401 Unauthorized"])
def test_tieu_de_trang_chan_loi_chung_chung_bi_tu_choi(tieu_de):
    assert xn.kiem_tieu_de(tieu_de) is not None, tieu_de


def test_tieu_de_tai_lieu_that_duoc_nhan():
    assert xn.kiem_tieu_de("FDA Approves Labeling Changes for Over-the-Counter (OTC) Weight Loss Drug alli (Orlistat)") is None


# ── ghi bằng chứng ───────────────────────────────────────────────────────────────────────────────────────────────────
def test_ghi_thanh_cong_co_sao_luu_va_cong_nhan(kho, tmp_path):
    goc = _so(kho, [_bc(url=URL_FDA2)])
    truoc = goc.read_bytes()
    sl = tmp_path / "sao-luu"
    ma, tb = xn.ghi(vd, URL_FDA, "FDA Approves Labeling Changes for alli (Orlistat)", "Claude_Browser: title + h1 khớp",
                    "Claude — bác sĩ tự vượt chặn bot", thu_muc=kho, hom_nay=HOM_NAY, sao_luu=sl)
    assert ma == 0 and "cổng nhận" in tb
    muc = json.loads(goc.read_text(encoding="utf-8"))["muc"]
    assert len(muc) == 2 and muc[-1]["url"] == URL_FDA and muc[-1]["ngay"] == HOM_NAY.isoformat()
    assert muc[-1]["dung_o"] == ["WebDashboard_Orlistat.html"]
    bak = list(sl.glob("*.bak"))
    assert len(bak) == 1 and bak[0].read_bytes() == truoc, "sao lưu phải khớp byte bản trước khi ghi"
    assert {m["url"]: m["trang_thai"] for m in xn.quet(vd, kho, hom_nay=HOM_NAY)}[URL_FDA] == "CON_HAN"


def test_ghi_khi_chua_co_so_thi_tao_moi(kho, tmp_path):
    ma, _ = xn.ghi(vd, URL_FDA, "FDA Approves Labeling Changes for alli (Orlistat)", "Claude_Browser: title + h1",
                   "x", thu_muc=kho, hom_nay=HOM_NAY, sao_luu=tmp_path / "sl")
    assert ma == 0 and (kho / vd.SO_URL_TRINH_DUYET).exists()


@pytest.mark.parametrize("url,tieu_de,cach,tu_khoa", [
    (URL_FDA, "Sorry! This resembles an automated request", "Claude_Browser: đã đọc", "CHẶN BOT"),
    (URL_FDA, "U.S. Food and Drug Administration", "Claude_Browser: đã đọc", "tên cơ quan"),
    ("https://example.org/x", "Một tiêu đề tài liệu đủ dài", "Claude_Browser: đã đọc", "CHƯA khai"),
    (URL_FDA, "FDA Approves Labeling Changes for alli (Orlistat)", "ngắn", "--cach"),
])
def test_ghi_tu_choi_va_khong_dong_vao_so(kho, tmp_path, url, tieu_de, cach, tu_khoa):
    goc = _so(kho, [_bc(url=URL_FDA2)])
    truoc = goc.read_bytes()
    ma, tb = xn.ghi(vd, url, tieu_de, cach, "x", thu_muc=kho, hom_nay=HOM_NAY, sao_luu=tmp_path / "sl")
    assert ma == 3 and tu_khoa in tb and goc.read_bytes() == truoc


def test_so_hong_khong_bi_ghi_de(kho, tmp_path):
    goc = kho / vd.SO_URL_TRINH_DUYET
    goc.write_text("{hỏng", encoding="utf-8")
    ma, tb = xn.ghi(vd, URL_FDA, "FDA Approves Labeling Changes for alli (Orlistat)", "Claude_Browser: title + h1",
                    "x", thu_muc=kho, hom_nay=HOM_NAY, sao_luu=tmp_path / "sl")
    assert ma == 2 and "KHÔNG ghi đè" in tb and goc.read_text(encoding="utf-8") == "{hỏng"


def test_cong_khong_nhan_thi_hoan_nguyen_dung_byte(kho, tmp_path, monkeypatch):
    goc = _so(kho, [_bc(url=URL_FDA2)])
    truoc = goc.read_bytes()
    monkeypatch.setattr(vd, "xac_minh_url_bang_trinh_duyet", lambda *a, **k: (None, "cổng giả từ chối"))
    ma, tb = xn.ghi(vd, URL_FDA, "FDA Approves Labeling Changes for alli (Orlistat)", "Claude_Browser: title + h1",
                    "x", thu_muc=kho, hom_nay=HOM_NAY, sao_luu=tmp_path / "sl")
    assert ma == 2 and "hoàn nguyên" in tb and goc.read_bytes() == truoc


def test_main_khong_co_ebm_dashboards_la_khong_do_duoc(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(xn, "DASH", tmp_path / "khong-co")
    assert xn.main([]) == 2 and "KHÔNG ĐO ĐƯỢC" in capsys.readouterr().out


def test_main_ma_thoat_theo_hang_cho(monkeypatch, kho, capsys):
    monkeypatch.setattr(xn, "DASH", kho)
    monkeypatch.setattr(xn, "nap_cong", lambda: vd)
    assert xn.main([]) == 1 and "chờ bác sĩ xác nhận" in capsys.readouterr().out
    _so(kho, [_bc(ngay=date.today()), _bc(url=URL_FDA2, ngay=date.today())])
    assert xn.main([]) == 0


def test_huong_dan_cam_claude_bam_vuot_chan_bot():
    hd = xn.HUONG_DAN
    assert "BÁC SĨ tự bấm" in hd and "Claude KHÔNG bấm" in hd and "KHÔNG giải CAPTCHA" in hd and "Page Not Found" in hd


# ── orchestrator ─────────────────────────────────────────────────────────────────────────────────────────────────────
def _plan():
    return [
        {"buoc": "B2-cong-liem-chinh[X]", "lat": "X", "lenh": ["py", "b2x", "/kho/WebDashboard_X.html"]},
        {"buoc": "B4-bo-nam[X]", "lat": "X", "lenh": ["py", "b4x"]},
        {"buoc": "B2-cong-liem-chinh[Y]", "lat": "Y", "lenh": ["py", "b2y", "/kho/WebDashboard_Y.html"]},
        {"buoc": "B5-hang-cho-bac-si", "lenh": ["py", "b5"]},
    ]


def test_b2_vi_url_chan_bot_thi_thanh_viec_bac_si_va_lo_di_tiep(monkeypatch):
    monkeypatch.setattr(op, "_url_cho_trinh_duyet", lambda lenh: [URL_FDA] if "b2x" in lenh else [])
    da_chay: list[str] = []
    res = op.thuc_thi(_plan(), chay=lambda lenh, _t: (da_chay.append(lenh[1]) or (2 if lenh[1] == "b2x" else 0)), in_=lambda *_: None)
    assert res["dung"] is None, "một URL chặn bot không được dừng cả lô"
    assert "b4x" not in da_chay and {"b2y", "b5"} <= set(da_chay)
    assert res["ket_qua"]["B2-cong-liem-chinh[X]"][0] == "cho_trinh_duyet" and res["cho_trinh_duyet"] == [URL_FDA]
    assert res["lat_hong"] == {"X"} and res["tong_rc"] == 1
    viec = op.phieu_can_phien("x", {"a2_arg": "x"}, [], res)
    assert any("XÁC NHẬN TRÊN TRÌNH DUYỆT" in v and "xac_nhan_trinh_duyet.py" in v for v in viec)


def test_b2_ha_tang_khong_co_url_chan_bot_van_dung_ca_lo(monkeypatch):
    monkeypatch.setattr(op, "_url_cho_trinh_duyet", lambda lenh: [])
    res = op.thuc_thi(_plan(), chay=lambda lenh, _t: 2 if lenh[1] == "b2x" else 0, in_=lambda *_: None)
    assert res["dung"] == "ha_tang", "lỗi mạng THẬT vẫn phải dừng lô như cũ"


def test_url_cho_trinh_duyet_doc_dung_dashboard_that(kho):
    db = kho / "WebDashboard_Orlistat.html"
    assert op._url_cho_trinh_duyet(["py", "verify_dashboard.py", str(db), "--online"]) == [URL_FDA]
    _so(kho, [_bc(ngay=date.today())])
    assert op._url_cho_trinh_duyet(["py", "verify_dashboard.py", str(db), "--online"]) == []
    assert op._url_cho_trinh_duyet(["py", "x", "/khong/co.html"]) == []
