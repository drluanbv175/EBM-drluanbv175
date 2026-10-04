#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHEST vào mục Elsevier + CMAJ vào bảng điều khoản NXB (04/10/2026, làn Chrome cho 13 bài nợ toàn văn).

Đo trên Chrome của bác sĩ: hai bài CHEST 2010 (CHA₂DS₂-VASc, HAS-BLED) mở được toàn văn trên journal.chestnet.org nhưng phiếu xếp
«điều khoản CHƯA KIỂM» vì tiền tố 10.1378 vắng bảng — trong khi Crossref ghi tiền tố này của Elsevier BV và chân trang trang tạp chí
trỏ đúng điều khoản website Elsevier ⇒ phải cùng khoá «Elsevier» (cùng điều khoản, cùng uỷ quyền 03/10). CMAJ (10.1503, CMA Impact)
im lặng về AI/TDM ⇒ «không rõ ⇒ xử như cấm» theo luật bảng. Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
_sp = importlib.util.spec_from_file_location("_dtv_chest_cmaj", TOOLS / "doc_toan_van_co_nguoi.py")
DTV = importlib.util.module_from_spec(_sp)
sys.modules["_dtv_chest_cmaj"] = DTV
_sp.loader.exec_module(DTV)
CMAJ = "CMAJ (Canadian Medical Association)"


def test_chest_theo_doi_va_theo_url_la_elsevier():
    assert DTV.nxb_cua(doi="10.1378/chest.09-1584")[0] == "Elsevier"
    assert DTV.nxb_cua(doi="10.1378/chest.10-0134")[0] == "Elsevier"
    assert DTV.nxb_cua(url="https://journal.chestnet.org/article/S0012-3692(10)60067-0/fulltext")[0] == "Elsevier"


def test_cmaj_theo_doi_va_theo_url():
    assert DTV.nxb_cua(doi="10.1503/cmaj.050051")[0] == CMAJ
    assert DTV.nxb_cua(url="https://www.cmaj.ca/content/173/5/489")[0] == CMAJ


def test_muc_cmaj_du_truong_va_trich_ngan():
    d = DTV.DIEU_KHOAN_NXB[CMAJ]
    assert d["ket_luan"] == "cam" and d["doi"] == ("10.1503/",)
    assert d["nguon"].startswith("https://www.cmaj.ca/") and d["doc_luc"] == "2026-10-04"
    assert 0 < len(d["trich"].split()) <= 15, "trích nguyên văn tối đa 15 từ"
    assert d.get("duong_hop_le"), "NXB «cấm» phải ghi đường hợp lệ"


def test_tien_to_khac_cua_elsevier_khong_doi():
    """Thêm 10.1378 không được làm rơi các nhánh cũ (bài Gastroenterology/AJKD từng rơi vào «chưa kiểm» khi thiếu nhánh)."""
    for doi in ("10.1016/s0140-6736(16)30069-1", "10.1053/j.gastro.2020.01.001", "10.1067/x"):
        assert DTV.nxb_cua(doi=doi)[0] == "Elsevier"


def test_doctrine_that_khop_bang():
    """Thêm NXB vào bảng mà quên doctrine ⇒ agent vẫn mở bài (CLAUDE.md §6.4). Doctrine thật phải nêu cả 10.1378 lẫn CMAJ."""
    van_ban = (REPO / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md").read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
