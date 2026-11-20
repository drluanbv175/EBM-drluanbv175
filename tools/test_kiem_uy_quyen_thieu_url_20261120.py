#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`phien_uy_quyen_chrome.kiem` khi THIẾU URL (20/11/2026).

Sự cố: `--kiem <PMID> --doi 10.1207/…` (tiền tố cũ của T&F) và `--doi 10.1191/…` (SAGE) không kèm `--url` trả
«NXB của bài (chưa kiểm điều khoản) KHÔNG thuộc phạm vi phiên» — trong khi kèm URL thì cả hai đều «được». Thông báo
sai nguyên nhân làm agent suýt kết luận T&F/SAGE chưa có uỷ quyền. Nay: không xác định được NXB VÀ không có URL ⇒
«thiếu URL trang bài»; vẫn mã 3 (fail-closed). Có URL mà NXB lạ ⇒ giữ nguyên «KHÔNG thuộc phạm vi».
Ngoại tuyến (bộ điều khoản giả, tệp trong tmp_path).
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


P = _nap("_puq_thieu_url_test", "phien_uy_quyen_chrome.py")
T0 = datetime(2026, 11, 20, 9, 0, 0, tzinfo=timezone(timedelta(hours=7)))
LOI = "uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay"


def _dtv():
    """Bộ điều khoản giả: Elsevier (DOI 10.1016/) và T&F (DOI 10.1080/, miền tandfonline.com) đều có uỷ quyền."""
    bang = {"Elsevier": {"ket_luan": "cam", "doi": ("10.1016/",), "mien": ("sciencedirect.com",)},
            "Taylor & Francis": {"ket_luan": "cam", "doi": ("10.1080/",), "mien": ("tandfonline.com",)}}

    def nxb_cua(doi="", url="", tieu_de=""):
        h = P._mien(url)
        for ten, d in bang.items():
            if any((doi or "").lower().startswith(t) for t in d["doi"]) or any(h == m or h.endswith("." + m) for m in d["mien"]):
                return ten, d
        return None, None
    return types.SimpleNamespace(DIEU_KHOAN_NXB=bang, nxb_cua=nxb_cua,
                                 uy_quyen_bac_si=lambda ten, hom_nay=None: {"nxb": ten})


@pytest.fixture()
def so(tmp_path):
    p = tmp_path / "state" / "phien.json"
    ma, tb = P.mo(LOI, bay_gio=T0, tep=p, dtv=_dtv())
    assert ma == 0, tb
    return p


def test_khong_url_tien_to_doi_la_bao_thieu_url_khong_bao_ngoai_pham_vi(so):
    ma, tb = P.kiem("26776715", "", "10.1207/s15327906mbr2603_7", bay_gio=T0, tep=so, dtv=_dtv())
    assert ma == 3
    assert "thiếu URL" in tb and "KHÔNG thuộc phạm vi" not in tb


def test_co_url_cua_nxb_thi_duoc_du_tien_to_doi_la(so):
    ma, tb = P.kiem("26776715", "https://www.tandfonline.com/doi/pdf/10.1207/s15327906mbr2603_7",
                    "10.1207/s15327906mbr2603_7", bay_gio=T0, tep=so, dtv=_dtv())
    assert ma == 0, tb


def test_co_url_nhung_nxb_la_van_bao_ngoai_pham_vi(so):
    ma, tb = P.kiem("16279131", "https://journals.example.org/doi/pdf/10.9999/x", "10.9999/x",
                    bay_gio=T0, tep=so, dtv=_dtv())
    assert ma == 3 and "KHÔNG thuộc phạm vi" in tb


def test_doi_da_khai_ma_thieu_url_van_bao_thieu_url(so):
    ma, tb = P.kiem("34153348", "", "10.1016/j.jvs.2021.05.001", bay_gio=T0, tep=so, dtv=_dtv())
    assert ma == 3 and tb.startswith("thiếu URL trang bài")
