#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""7 miền tạp chí hội trên nền Elsevier (13/11/2026) — làn Chrome của phiếu tháng: bài J Pain, JACI, JACI In Practice, Mayo Clin
Proc, GIE, Am J Med, Heart Lung Circ (DOI 10.1016/, phân giải qua linkinghub về chính miền hội) bị `phien_uy_quyen_chrome.py
--kiem` chặn «trang ở www.jpain.org KHÔNG thuộc miền đã khai của Elsevier» dù cùng điều khoản Elsevier. Chân trang từng miền
(đọc trên Chrome 13/11/2026): «Copyright © 2026 Elsevier Inc.» + «Terms and Conditions» trỏ đúng trang điều khoản website Elsevier.

Khoá:
  • URL bài trên 7 miền nhận đúng khoá «Elsevier» (đi qua `nxb_cua`, chính hàm `--kiem` dùng);
  • miền giả mạo đuôi (vd «notjpain.org», «jpain.org.evil.com») KHÔNG nhận khoá Elsevier;
  • cấu hình làn Chrome `elsevier_hoi` có hai miền đã lưu bài thật 13/11 (endocrinepractice.org, cghjournal.org) và nhật ký
    `kiem_lan_cuoi` ghi đúng PMID.
Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


DTV = _nap("_dtv_mien_elsevier_hoi", "doc_toan_van_co_nguoi.py")

MIEN_MOI = [
    "https://www.jpain.org/article/S1526-5900(25)00837-5/fulltext",
    "https://www.jaci-inpractice.org/article/S2213-2198(25)01000-0/fulltext",
    "https://www.jacionline.org/article/S0091-6749(26)00100-0/fulltext",
    "https://www.mayoclinicproceedings.org/article/S0025-6196(26)00200-0/fulltext",
    "https://www.giejournal.org/article/S0016-5107(24)03600-0/fulltext",
    "https://www.amjmed.com/article/S0002-9343(23)00600-0/fulltext",
    "https://www.heartlungcirc.org/article/S1443-9506(23)04500-0/fulltext",
]


@pytest.mark.parametrize("url", MIEN_MOI)
def test_url_mien_hoi_nhan_khoa_elsevier(url) -> None:
    assert DTV.nxb_cua(url=url)[0] == "Elsevier", url


@pytest.mark.parametrize("url", ["https://notjpain.org/a", "https://www.jpain.org.evil.com/a", "https://amjmed.com.example.net/x"])
def test_mien_gia_mao_duoi_khong_nhan(url) -> None:
    assert DTV.nxb_cua(url=url)[0] != "Elsevier", url


def test_cau_hinh_elsevier_hoi_co_hai_mien_da_luu_that() -> None:
    ch = json.loads((TOOLS / "lan_chrome" / "cau_hinh.json").read_text(encoding="utf-8"))["nxb"]["elsevier_hoi"]
    for mien in ("www.endocrinepractice.org", "www.cghjournal.org"):
        assert mien in ch["mien"], mien
    assert "PMID 32427525" in ch["kiem_lan_cuoi"] and "PMID 38750866" in ch["kiem_lan_cuoi"]
