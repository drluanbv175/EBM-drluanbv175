#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đọc điều khoản ASCO 30/10/2026: guideline ASCO 2020 (PMID 32663120) của gói Đau thần kinh bị
`phien_uy_quyen_chrome.py --kiem` từ chối «NXB của bài (chưa kiểm điều khoản) KHÔNG thuộc phạm vi phiên».

Khoá:
  • DOI tiền tố 10.1200 (Crossref /prefixes/10.1200 = American Society of Clinical Oncology, đọc 30/10/2026) và URL trên
    ascopubs.org, asco.org đều nhận khoá ASCO;
  • mục mới đủ trường theo khuôn (nguồn https, ngày đọc, trích ≤ 15 từ, đường hợp lệ) và «cam»;
  • doctrine §2septies nêu tên + tiền tố DOI (`lech_doctrine`), bắt được khi mất tiền tố hoặc tên;
  • đi trọn đường thật: tệp uỷ quyền có mục ASCO ⇒ `--kiem` của phiên nhận bài; chưa có ⇒ vẫn từ chối.
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


DTV = _nap("_dtv_asco_20261030", "doc_toan_van_co_nguoi.py")
P = _nap("_puq_asco_20261030", "phien_uy_quyen_chrome.py")

ASCO = "American Society of Clinical Oncology (ASCO)"
DOI = "10.1200/JCO.20.01399"
URL = "https://ascopubs.org/doi/10.1200/JCO.20.01399"


@pytest.mark.parametrize("doi", [DOI, "10.1200/jco.20.01399", "10.1200/OP.20.00001"])
def test_doi_tien_to_asco_nhan_dung_khoa(doi) -> None:
    assert DTV.nxb_cua(doi=doi)[0] == ASCO, doi


@pytest.mark.parametrize("url", [URL, "https://www.asco.org/about-asco/legal/terms-use"])
def test_url_asco_nhan_dung_khoa(url) -> None:
    assert DTV.nxb_cua(url=url)[0] == ASCO, url


def test_muc_moi_du_truong_va_trich_ngan() -> None:
    d = DTV.DIEU_KHOAN_NXB[ASCO]
    assert d["ket_luan"] == "cam"
    assert d["nguon"].startswith("https://") and d["doc_luc"] == "2026-10-30"
    assert d.get("duong_hop_le") and d.get("loai_nguon") and d["mien"]
    assert 0 < len(d["trich"].split()) <= 15, "trích nguyên văn tối đa 15 từ"


def test_doctrine_khop_bang_va_bat_duoc_khi_mat_tien_to_hoac_ten() -> None:
    van_ban = DOCTRINE.read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
    assert any(ASCO in x for x in DTV.lech_doctrine(van_ban.replace("`10.1200/`", "10.1200/")))
    assert any(ASCO in x for x in DTV.lech_doctrine(van_ban.replace("American Society of Clinical Oncology", "ASCO")))


T0 = datetime(2026, 10, 30, 19, 0, 0, tzinfo=timezone(timedelta(hours=7)))
CAN_CU = ("«uỷ quyền riêng cho Wiley như đã làm với J Rheumatol và cho tất cả các vấn đề tương tự khác không hỏi lại tôi nữa» "
          "(bác sĩ, 04/10/2026)")


def test_co_uy_quyen_thi_kiem_cua_phien_nhan_bai(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(DTV, "DASH", tmp_path)
    so = tmp_path / "state" / "phien.json"
    tep = tmp_path / DTV.TEN_TEP_UY_QUYEN
    tep.write_text(json.dumps({"muc": [{"nxb": "Elsevier", "ngay": "2026-10-03", "can_cu": "cho máy đọc toàn văn Elsevier"}]},
                              ensure_ascii=False), encoding="utf-8")
    assert P.mo("uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    ma, tb = P.kiem("32663120", URL, DOI, bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 3 and ASCO in tb and "KHÔNG thuộc phạm vi" in tb    # đã kiểm điều khoản nhưng CHƯA có uỷ quyền ⇒ vẫn dừng
    tep.write_text(json.dumps({"muc": [{"nxb": ASCO, "ngay": "2026-10-30", "can_cu": CAN_CU}]}, ensure_ascii=False),
                   encoding="utf-8")
    assert P.kiem("32663120", URL, DOI, bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    assert ASCO in P.nxb_duoc_luu(DTV, T0.date())
