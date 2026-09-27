#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #2 (đợt dò nâng cấp 26/09/2026): sổ đã ghi EoC / «nghi ma» mà cổng vẫn in ✓.

Tái hiện gốc: đường quét chính chỉ ghi `quan_ngai`/`nghi_ma` (không `da_rut`), còn `nguon_da_rut` /
`dinh_danh_da_rut` chỉ lọc `da_rut` ⇒ nhánh «CÓ QUAN NGẠI (EoC)» của verify_dashboard không bao giờ chạy tới;
`pham_vi_kiem_rut_bai` còn tính EoC/nghi_ma là «đã kiểm, còn hạn» ⇒ cổng in ✓ «không thấy dương tính chưa
xử lý». Cờ còn bị MẤT sau lượt xác minh lại tồn tại.

Ngoại tuyến 100%: sổ THẬT trong cây thư mục tạm; mạng được thay bằng hàm giả.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
VD_NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"
TEN = "WebDashboard_EBM_VanDeCuThe_X_20260926.html"


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def _nay(ngay_truoc: int = 0) -> str:
    return (dt.datetime.now() - dt.timedelta(days=ngay_truoc)).isoformat(timespec="seconds")


def _bg(loai, gt, **kw):
    d = {"loai": loai, "gia_tri": gt, "xac_minh_luc": _nay(), "kiem_rut_luc": _nay(), "cac_dashboard": [TEN]}
    d.update(kw)
    return d


def _chay_cong(tmp: Path, muc: dict, item_js: str):
    (tmp / "tools").mkdir()
    shutil.copy(ROOT / "tools" / "so_xac_minh_nguon.py", tmp / "tools" / "so_xac_minh_nguon.py")
    shutil.copy(ROOT / "tools" / "ban_sao_tran.py", tmp / "tools" / "ban_sao_tran.py")
    dash = tmp / "EBM-Dashboards"
    (dash / "tools").mkdir(parents=True)
    shutil.copy(VD_NGUON, dash / "tools" / "verify_dashboard.py")
    (dash / ".so-xac-minh-nguon.json").write_text(json.dumps({"phien_ban": 1, "muc": muc}, ensure_ascii=False),
                                                  encoding="utf-8")
    page = dash / TEN
    page.write_text("<script>const DATA={items:[%s]}</script>" % item_js, encoding="utf-8")
    vd = _nap("vd_eoc_" + tmp.name, dash / "tools" / "verify_dashboard.py")
    # Cây tạm không có repo y khoa cạnh bên ⇒ nền Retraction Watch ngoại tuyến VẮNG: cô lập đúng đường SỔ.
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    return errors, warns, oks


@pytest.mark.parametrize("khoa,bg,item_js", [
    ("pmid:31111111", _bg("pmid", "31111111", ghi_chu_rut="expression_of_concern", quan_ngai=True),
     "{id:'ITEM-01', pmid:'31111111'}"),
    ("doi:10.1000/eoc.x", _bg("doi", "10.1000/eoc.x", ghi_chu_rut="expression_of_concern", quan_ngai=True),
     "{id:'ITEM-01', doi:'10.1000/eoc.x'}"),
    # cờ đã MẤT (mô phỏng sau lượt xác minh lại của bản cũ) — chỉ còn phán quyết ghi_chu_rut
    ("pmid:31111112", _bg("pmid", "31111112", ghi_chu_rut="expression_of_concern"),
     "{id:'ITEM-01', pmid:'31111112'}"),
])
def test_eoc_trong_so_la_loi_cung_khong_in_tick(tmp_path, khoa, bg, item_js):
    errors, _w, oks = _chay_cong(tmp_path, {khoa: bg}, item_js)
    assert any("CÓ QUAN NGẠI (EoC)" in e and bg["gia_tri"] in e for e in errors), errors
    assert not any("Rút bài:" in o for o in oks), "vừa có EoC vừa in ✓ «không thấy dương tính»"


def test_eoc_khong_gan_voi_dashboard_van_bi_bat_qua_tang_dinh_danh(tmp_path):
    bg = _bg("pmid", "31111111", ghi_chu_rut="expression_of_concern", quan_ngai=True, cac_dashboard=[])
    errors, _w, _o = _chay_cong(tmp_path, {"pmid:31111111": bg}, "{id:'ITEM-01', pmid:'31111111'}")
    assert any("CÓ QUAN NGẠI (EoC)" in e for e in errors), errors


def test_nghi_ma_chi_canh_bao_chua_kiem_khong_loi_cung_khong_tick(tmp_path):
    muc = {"pmid:32222222": _bg("pmid", "32222222", ghi_chu_rut="unresolved", nghi_ma=True),
           "pmid:33333333": _bg("pmid", "33333333", ghi_chu_rut="ok")}
    errors, warns, oks = _chay_cong(tmp_path, muc, "{id:'ITEM-01', pmid:'32222222'},{id:'ITEM-02', pmid:'33333333'}")
    assert not errors, "nghi ma có thể do lỗi tầng API — KHÔNG được chặn cứng"
    pv = [w for w in warns if "Phạm vi kiểm rút bài" in w]
    assert pv and "32222222" in pv[0] and "1/2" in pv[0], warns
    assert not any("Rút bài:" in o for o in oks)


def test_doi_chung_tat_ca_ok_con_han_moi_in_tick(tmp_path):
    muc = {"pmid:33333333": _bg("pmid", "33333333", ghi_chu_rut="ok")}
    errors, warns, oks = _chay_cong(tmp_path, muc, "{id:'ITEM-01', pmid:'33333333'}")
    assert not errors and not [w for w in warns if "Phạm vi kiểm rút bài" in w]
    assert any("Rút bài: 1/1" in o for o in oks), oks


# ── Hàm sổ ─────────────────────────────────────────────────────────────────────────────────────────────
SO = _nap("so_eoc_20260926", ROOT / "tools" / "so_xac_minh_nguon.py")


def test_ham_so_phat_eoc_dung_tinh_trang(monkeypatch):
    muc = {"pmid:1": _bg("pmid", "1", quan_ngai=True, ghi_chu_rut="expression_of_concern"),
           "pmid:2": _bg("pmid", "2", da_rut=True, ghi_chu_rut="retracted"),
           "pmid:3": _bg("pmid", "3", ghi_chu_rut="ok")}
    monkeypatch.setattr(SO, "doc_so", lambda: {"muc": muc})
    theo_dd = {r["gia_tri"]: r["tinh_trang"] for r in SO.dinh_danh_da_rut(["1", "2", "3"])}
    assert theo_dd == {"1": "expression_of_concern", "2": "retracted"}
    theo_ten = {r["gia_tri"]: r["tinh_trang"] for r in SO.nguon_da_rut(TEN)}
    assert theo_ten == {"1": "expression_of_concern", "2": "retracted"}


def test_pham_vi_nghi_ma_la_chua_phan_quyet_moi_nhat_quyet_dinh(monkeypatch):
    muc = {"pmid:1": _bg("pmid", "1", nghi_ma=True, ghi_chu_rut="unresolved"),
           "pmid:2": _bg("pmid", "2", nghi_ma=True, ghi_chu_rut="ok")}   # lượt sau trả ok thật
    monkeypatch.setattr(SO, "doc_so", lambda: {"muc": muc})
    assert SO.pham_vi_kiem_rut_bai(["1", "2"]) == {"co": ["2"], "chua": ["1"]}


def test_xac_minh_lai_ton_tai_khong_lam_mat_co_eoc(tmp_path, monkeypatch):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    so = dash / ".so-xac-minh-nguon.json"
    monkeypatch.setattr(SO, "DASH", dash)
    monkeypatch.setattr(SO, "SO", so)
    # xac_minh_luc quá 180 ngày ⇒ phải xác minh lại tồn tại; kiem_rut_luc còn hạn ⇒ không tra rút bài lại
    muc = {"pmid:31111111": _bg("pmid", "31111111", xac_minh_luc=_nay(400), quan_ngai=True,
                                ghi_chu_rut="expression_of_concern"),
           "pmid:32222222": _bg("pmid", "32222222", xac_minh_luc=_nay(400), nghi_ma=True, ghi_chu_rut="unresolved")}
    so.write_text(json.dumps({"phien_ban": 1, "muc": muc}), encoding="utf-8")
    page = dash / TEN
    page.write_text("<script>const DATA={items:[{id:'ITEM-01', pmid:'31111111'},{id:'ITEM-02', pmid:'32222222'}]}"
                    "</script>", encoding="utf-8")
    vd = _nap("vd_eoc_lenh_quet_20260926", VD_NGUON)

    def _xm(khoa, _vd):
        loai, _, gt = khoa.partition(":")
        return {"loai": loai, "gia_tri": gt, "xac_minh_luc": _nay(), "tieu_de": "T", "nguon_xac_minh": "pubmed"}
    with mock.patch.object(SO, "_nap_verify_dashboard", lambda: vd), mock.patch.object(SO, "xac_minh_mot", _xm), \
         mock.patch.object(SO, "kiem_rut_bai", lambda pmids: {}):
        SO.lenh_quet([page], 1)
    moi = json.loads(so.read_text(encoding="utf-8"))["muc"]
    assert moi["pmid:31111111"]["xac_minh_luc"][:10] == _nay()[:10], "fixture phải thực sự đi qua đường xác minh lại"
    assert moi["pmid:31111111"].get("quan_ngai") is True, "cờ EoC bị mất sau xác minh lại"
    assert moi["pmid:32222222"].get("nghi_ma") is True
