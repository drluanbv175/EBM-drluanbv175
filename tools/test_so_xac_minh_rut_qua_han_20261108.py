"""Sổ xác minh: bản ghi «ok» QUÁ HẠN kiểm rút bài phải được tái kiểm, và báo cáo phải khuyên đúng đòn bẩy — 08/11/2026.

Vì sao có. Đo 08/11/2026: `--bao-cao` báo «94 mục: CHƯA kiểm được RÚT BÀI … thêm NCBI_API_KEY». Đã chạy `--quet --vong 3`,
`--quet-ledger`, `--phu-mo-coi --vong 3` («+94 xác minh») — báo cáo vẫn 94. `--kiem-rut-lai <94 định danh>` ⇒ 94/94 «ok»,
không cần khoá. Gốc: (1) `--phu-mo-coi` xác minh lại TỒN TẠI cho cả bản ghi chỉ quá hạn rút bài, rồi chỉ kiểm rút bài cho PMID
CHƯA TỪNG kiểm — bản ghi «ok» quá hạn và mọi DOI kẹt vĩnh viễn; (2) `--bao-cao` gộp «quá hạn» với «chưa kiểm được» dưới lời
khuyên NCBI_API_KEY (lớp lỗi BH14: lời khuyên lệch đòn bẩy). Ngoại tuyến: sổ tạm, mạng giả.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "so_xac_minh_nguon.py"


@pytest.fixture()
def M(tmp_path, monkeypatch):
    sp = importlib.util.spec_from_file_location("so_xac_minh_rut_qua_han_20261108", _TEP)
    mod = importlib.util.module_from_spec(sp)
    sys.modules["so_xac_minh_rut_qua_han_20261108"] = mod
    sp.loader.exec_module(mod)
    monkeypatch.setattr(mod, "SO", tmp_path / ".so-xac-minh-nguon.json")
    monkeypatch.setattr(mod, "_nap_verify_dashboard", lambda: None)
    mod._goi = {"ton_tai": [], "pmid": [], "doi": []}

    def _xm(khoa, vd):
        mod._goi["ton_tai"].append(khoa)
        loai, gt = khoa.split(":", 1)
        return {"loai": loai, "gia_tri": gt, "xac_minh_luc": _iso(0), "tieu_de": "t", "nguon_xac_minh": "gia"}

    def _pm(ds):
        mod._goi["pmid"].extend(ds)
        return {p: {"status": "ok"} for p in ds}

    def _doi(ds):
        mod._goi["doi"].extend(ds)
        return {d: {"status": "ok"} for d in ds}
    monkeypatch.setattr(mod, "xac_minh_mot", _xm)
    monkeypatch.setattr(mod, "kiem_rut_bai", _pm)
    monkeypatch.setattr(mod, "kiem_rut_doi", _doi)
    return mod


def _iso(ngay_truoc: int) -> str:
    return (dt.datetime.now() - dt.timedelta(days=ngay_truoc)).isoformat(timespec="seconds")


def _ghi(M, muc: dict) -> None:
    M.SO.write_text(json.dumps({"phien_ban": 1, "muc": muc}), encoding="utf-8")


def _phu(M) -> None:
    M._chay_lenh(argparse.Namespace(phu_mo_coi=True, vong=1, kiem_rut_lai=None, quet_ledger=False, bao_cao=False,
                                    quet=None, cuu_so_hong=False))


def _bg(loai, gt, xac_minh, kiem_rut=None, dashboards=()):
    bg = {"loai": loai, "gia_tri": gt, "xac_minh_luc": _iso(xac_minh), "cac_dashboard": list(dashboards)}
    if kiem_rut is not None:
        bg["kiem_rut_luc"] = _iso(kiem_rut)
        bg["ghi_chu_rut"] = "ok"
    return bg


def test_phu_mo_coi_tai_kiem_rut_bai_qua_han_ca_pmid_lan_doi(M):
    _ghi(M, {"pmid:111": _bg("pmid", "111", xac_minh=10, kiem_rut=42),
             "doi:10.1/a": _bg("doi", "10.1/a", xac_minh=10, kiem_rut=35)})
    _phu(M)
    muc = M.doc_so()["muc"]
    assert M._goi["pmid"] == ["111"] and M._goi["doi"] == ["10.1/a"], M._goi
    for k in ("pmid:111", "doi:10.1/a"):
        assert M.con_hieu_luc(muc[k]) == (True, ""), (k, muc[k])


def test_phu_mo_coi_khong_xac_minh_lai_ton_tai_khi_chi_qua_han_rut_bai(M):
    _ghi(M, {"pmid:111": _bg("pmid", "111", xac_minh=10, kiem_rut=42)})
    _phu(M)
    assert M._goi["ton_tai"] == [], "tồn tại còn hạn — gọi lại xac_minh_mot là việc thừa"


def test_phu_mo_coi_van_xac_minh_ton_tai_khi_ton_tai_qua_han(M):
    _ghi(M, {"pmid:222": _bg("pmid", "222", xac_minh=M.HAN_TON_TAI_NGAY + 5, kiem_rut=1)})
    _phu(M)
    assert M._goi["ton_tai"] == ["pmid:222"]


def test_phu_mo_coi_khong_xoa_duong_tinh_cu(M):
    bg = _bg("pmid", "333", xac_minh=10, kiem_rut=42)
    bg.update(da_rut=True, ghi_chu_rut="retracted")
    _ghi(M, {"pmid:333": bg})
    _phu(M)
    muc = M.doc_so()["muc"]
    assert muc["pmid:333"]["da_rut"] is True and M._goi["pmid"] == [], "dương tính không được đưa đi kiểm để «rửa»"


def test_phu_mo_coi_trang_thai_la_khong_ghi_kiem_rut(M, monkeypatch):
    monkeypatch.setattr(M, "kiem_rut_bai", lambda ds: {p: {"status": "unknown_fetch_error"} for p in ds})
    _ghi(M, {"pmid:444": _bg("pmid", "444", xac_minh=10, kiem_rut=42)})
    _phu(M)
    assert M.con_hieu_luc(M.doc_so()["muc"]["pmid:444"])[0] is False, "không tra được ≠ sạch"


def test_bao_cao_tach_qua_han_khoi_chua_kiem(M, capsys):
    _ghi(M, {"pmid:111": _bg("pmid", "111", xac_minh=10, kiem_rut=42),
             "doi:10.1/a": _bg("doi", "10.1/a", xac_minh=10, kiem_rut=35, dashboards=["X.html"])})
    M.bao_cao()
    out = capsys.readouterr().out
    assert "[MA] CAN_KIEM_RUT_LAI" in out and "QUÁ HẠN kiểm rút bài" in out
    assert "CAN_NCBI_API_KEY" not in out and "CAN_TAI_RETRACTION_WATCH" not in out, \
        "quá hạn (đã từng kiểm được) không được khuyên khoá API/tải nền"
    assert "CHƯA kiểm được RÚT BÀI" not in out
    assert "(1 mục không dashboard nào trích)" in out


def test_bao_cao_chua_kiem_lan_nao_van_giu_ma_cu(M, capsys):
    _ghi(M, {"pmid:555": _bg("pmid", "555", xac_minh=10)})
    M.bao_cao()
    out = capsys.readouterr().out
    assert "CHƯA kiểm được RÚT BÀI" in out
    assert ("[MA] CAN_NCBI_API_KEY" in out) or ("[MA] CAN_TAI_RETRACTION_WATCH" in out)
    assert "CAN_KIEM_RUT_LAI" not in out
