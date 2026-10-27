#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đợt đọc điều khoản NXB 27/10/2026 — RSNA: bài «Radiology: Cardiothoracic Imaging» (PMID 41410572) của gói Bệnh mạch vành
20261026 bị `phien_uy_quyen_chrome.py --kiem` từ chối «NXB của bài (chưa kiểm điều khoản) KHÔNG thuộc phạm vi phiên».

Khoá:
  • DOI tiền tố 10.1148 (Crossref /prefixes/10.1148 = Radiological Society of North America, đọc 27/10/2026) và URL trang bài trên
    pubs.rsna.org đều nhận khoá RSNA;
  • mục mới đủ trường theo khuôn (nguồn https, ngày đọc 27/10, trích ≤ 15 từ, đường hợp lệ) và «cam»;
  • doctrine §2septies nêu tên + tiền tố DOI (`lech_doctrine`), bắt được khi mất tiền tố hoặc tên;
  • đi trọn đường thật: tệp uỷ quyền có mục RSNA ⇒ `--kiem` của phiên nhận bài RSNA; chưa có ⇒ vẫn từ chối.
Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
DOCTRINE = TOOLS.parent / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md"


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


DTV = _nap("_dtv_dot_20261027", "doc_toan_van_co_nguoi.py")
P = _nap("_puq_dot_20261027", "phien_uy_quyen_chrome.py")

RSNA = "Radiological Society of North America (RSNA)"


@pytest.mark.parametrize("doi", ["10.1148/ryct.250313", "10.1148/RYCT.250313", "10.1148/radiol.2021204276"])
def test_doi_tien_to_rsna_nhan_dung_khoa(doi) -> None:
    assert DTV.nxb_cua(doi=doi)[0] == RSNA, doi


@pytest.mark.parametrize("url", ["https://pubs.rsna.org/doi/10.1148/ryct.250313",
                                 "https://pubs.rsna.org/doi/full/10.1148/ryct.250313"])
def test_url_trang_bai_nhan_dung_khoa(url) -> None:
    assert DTV.nxb_cua(url=url)[0] == RSNA, url


def test_muc_moi_du_truong_va_trich_ngan() -> None:
    d = DTV.DIEU_KHOAN_NXB[RSNA]
    assert d["ket_luan"] == "cam", "NXB «không rõ» vẫn ghi «cam» — bảng chỉ nhận «cấm»"
    assert d["nguon"].startswith("https://") and d["doc_luc"] == "2026-10-27"
    assert d.get("duong_hop_le") and d.get("loai_nguon") and d["mien"]
    assert 0 < len(d["trich"].split()) <= 15, "trích nguyên văn tối đa 15 từ"


def test_doctrine_khop_bang_va_bat_duoc_khi_mat_tien_to_hoac_ten() -> None:
    van_ban = DOCTRINE.read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
    assert any(RSNA in x for x in DTV.lech_doctrine(van_ban.replace("`10.1148/`", "10.1148/")))
    assert any(RSNA in x for x in DTV.lech_doctrine(van_ban.replace("Radiological Society of North America", "RSNA")))


T0 = datetime(2026, 10, 27, 19, 40, 0, tzinfo=timezone(timedelta(hours=7)))
CAN_CU = ("«uỷ quyền riêng cho Wiley như đã làm với J Rheumatol và cho tất cả các vấn đề tương tự khác không hỏi lại tôi nữa» "
          "(bác sĩ, 04/10/2026)")


def test_tep_uy_quyen_co_rsna_thi_kiem_cua_phien_nhan(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(DTV, "DASH", tmp_path)
    so = tmp_path / "state" / "phien.json"
    tep = tmp_path / DTV.TEN_TEP_UY_QUYEN
    tep.write_text(json.dumps({"muc": [{"nxb": "Elsevier", "ngay": "2026-10-03", "can_cu": "cho máy đọc toàn văn Elsevier"}]},
                              ensure_ascii=False), encoding="utf-8")
    assert P.mo("uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    url = "https://pubs.rsna.org/doi/10.1148/ryct.250313"
    ma, tb = P.kiem("41410572", url, "10.1148/ryct.250313", bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 3 and RSNA in tb and "KHÔNG thuộc phạm vi" in tb    # đã kiểm điều khoản nhưng CHƯA có uỷ quyền ⇒ vẫn dừng
    tep.write_text(json.dumps({"muc": [{"nxb": RSNA, "ngay": "2026-10-27", "can_cu": CAN_CU}]}, ensure_ascii=False),
                   encoding="utf-8")
    assert P.kiem("41410572", url, "10.1148/ryct.250313", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    assert RSNA in P.nxb_duoc_luu(DTV, T0.date())
