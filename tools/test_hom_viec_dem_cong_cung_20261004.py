# -*- coding: utf-8 -*-
"""Hòm việc nhận dòng «chữ ký thật: 0/<n>» của study_readiness (04/10/2026: từ «0/4» viết tay sang SÁU cổng cứng của
gate_contract repo y khoa). Nhận cả «0/4» bản cũ để thứ tự gộp hai repo không làm mất dòng nhắc C1a. Ngoại tuyến."""
from __future__ import annotations

import re
from pathlib import Path

NGUON = (Path(__file__).resolve().parent / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
MAU = re.compile(r"chữ ký thật: 0/(\d+)")


def test_dong_thi_hanh_do_dang_moi_va_dang_cu():
    dong = [x.strip() for x in NGUON.splitlines()]
    assert '_m_cc = re.search(r"chữ ký thật: 0/(\\d+)", out)' in dong
    assert 'if _m_cc or "0/4" in out:' in dong


def test_mau_nhan_ca_sau_cong_lan_bon_cong():
    assert MAU.search("   → Cổng CỨNG đã có chữ ký thật: 0/6 (G2 · G4 · G5 · G8 · G9 · G10)").group(1) == "6"
    assert MAU.search("   → Cổng CỨNG đã có chữ ký thật: 0/4 (G2 · G4 · G8 · G9)").group(1) == "4"
    assert not MAU.search("   → Cổng CỨNG đã có chữ ký thật: 2/6 (G2 · G4 · G5 · G8 · G9 · G10)")
