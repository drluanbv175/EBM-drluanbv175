"""`so_xac_minh_nguon.py --phu-mo-coi` phải GIỮ phán quyết rút bài đã có — vá 27/09/2026.

Lượt phủ mồ côi thay nguyên bản ghi bằng kết quả `xac_minh_mot()` (chỉ xác minh TỒN TẠI) nên mất `kiem_rut_luc`/
`ghi_chu_rut` mà `--quet-ledger` vừa ghi cho DOI chỉ-có-trong-hub: đo 27/09, 10 DOI quay về «chưa kiểm rút bài lần
nào» và sổ không bao giờ hội tụ. Ngoại tuyến: sổ tạm, `xac_minh_mot` giả.
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
    sp = importlib.util.spec_from_file_location("so_xac_minh_phu_mo_coi_20260927", _TEP)
    mod = importlib.util.module_from_spec(sp)
    sys.modules["so_xac_minh_phu_mo_coi_20260927"] = mod
    sp.loader.exec_module(mod)
    monkeypatch.setattr(mod, "SO", tmp_path / ".so-xac-minh-nguon.json")
    monkeypatch.setattr(mod, "_nap_verify_dashboard", lambda: None)
    monkeypatch.setattr(mod, "kiem_rut_bai", lambda ds: {})
    return mod


def _ghi_so(M, muc: dict) -> None:
    M.SO.write_text(json.dumps({"phien_ban": 1, "muc": muc}), encoding="utf-8")


def _phu(M) -> None:
    M._chay_lenh(argparse.Namespace(phu_mo_coi=True, vong=1, kiem_rut_lai=None, quet_ledger=False, bao_cao=False,
                                    quet=None, cuu_so_hong=False))


def test_doi_hub_giu_phan_quyet_rut_bai_va_con_hieu_luc(M, monkeypatch):
    bay_gio = dt.datetime.now().isoformat(timespec="seconds")
    _ghi_so(M, {"doi:10.1/x": {"loai": "doi", "gia_tri": "10.1/x", "cac_dashboard": ["(hub-only)"],
                               "kiem_rut_luc": bay_gio, "ghi_chu_rut": "ok"}})
    monkeypatch.setattr(M, "xac_minh_mot", lambda khoa, vd: {
        "loai": "doi", "gia_tri": "10.1/x", "xac_minh_luc": bay_gio, "tieu_de": "t", "nguon_xac_minh": "crossref"})
    _phu(M)
    bg = M.doc_so()["muc"]["doi:10.1/x"]
    assert bg["xac_minh_luc"] == bay_gio
    assert bg["kiem_rut_luc"] == bay_gio and bg["ghi_chu_rut"] == "ok", "mất phán quyết rút bài đã có"
    assert bg["cac_dashboard"] == ["(hub-only)"]
    assert M.con_hieu_luc(bg) == (True, "")


def test_ban_ghi_chua_tung_kiem_rut_bai_van_la_chua_kiem(M, monkeypatch):
    """Không được BỊA phán quyết: bản ghi chưa từng kiểm rút bài vẫn phải «chưa kiểm rút bài» sau lượt phủ (DOI)."""
    bay_gio = dt.datetime.now().isoformat(timespec="seconds")
    _ghi_so(M, {"doi:10.1/y": {"loai": "doi", "gia_tri": "10.1/y", "cac_dashboard": ["NC:x"]}})
    monkeypatch.setattr(M, "xac_minh_mot", lambda khoa, vd: {
        "loai": "doi", "gia_tri": "10.1/y", "xac_minh_luc": bay_gio, "tieu_de": "t", "nguon_xac_minh": "crossref"})
    _phu(M)
    bg = M.doc_so()["muc"]["doi:10.1/y"]
    assert "kiem_rut_luc" not in bg
    assert M.con_hieu_luc(bg) == (False, "chưa kiểm rút bài lần nào")
