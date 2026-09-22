#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #4, MEDIUM).

`kiem_nguon_da_rut()` từng khẳng định "đã đối chiếu nền Retraction Watch NGOẠI TUYẾN cho các
PMID chưa kiểm" ngay cả khi TOÀN BỘ danh sách "chưa kiểm" đang liệt kê là DOI — nền chỉ khoá
theo PMID nên không hề được hỏi cho DOI nào. `_thong_diep_pham_vi_rw()` là hàm thuần tách ra
để kiểm độc lập, không cần dựng cả cổng.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("vd_thong_diep_test", TOOLS / "verify_dashboard.py")
vd = importlib.util.module_from_spec(spec)
sys.modules["vd_thong_diep_test"] = vd
spec.loader.exec_module(vd)


def test_chua_toan_bo_la_doi_khong_duoc_noi_da_doi_chieu():
    msg = vd._thong_diep_pham_vi_rw(
        chua=["10.1016/S0140-6736(20)30748-0", "10.1097/CM9.0000000000002026"],
        rw=[{"loai": "pmid", "gia_tri": "999"}],  # có PMID KHÁC trong file được hỏi thành công
        pm_chua=[],
    )
    assert "CHỈ được hỏi cho PMID" in msg
    assert "2 DOI" in msg
    assert "đã đối chiếu nền Retraction Watch NGOẠI TUYẾN cho các PMID chưa kiểm" not in msg, (
        "không được ngụ ý DOI đã được đối chiếu khi nền chỉ khoá theo PMID"
    )


def test_chua_co_pmid_va_da_doi_chieu_thi_noi_dung_nhu_cu():
    msg = vd._thong_diep_pham_vi_rw(chua=["11111111"], rw=[{"loai": "pmid", "gia_tri": "22222222"}],
                                     pm_chua=["11111111"])
    assert "đã đối chiếu nền Retraction Watch NGOẠI TUYẾN cho các PMID chưa kiểm" in msg


def test_chua_co_pmid_nhung_khong_co_nen_ngoai_tuyen():
    msg = vd._thong_diep_pham_vi_rw(chua=["11111111"], rw=None, pm_chua=["11111111"])
    assert "KHÔNG có trên máy này" in msg


def test_chua_rong_tra_chuoi_rong():
    assert vd._thong_diep_pham_vi_rw(chua=[], rw=None, pm_chua=[]) == ""


def test_chua_hon_hop_pmid_va_doi_van_noi_da_doi_chieu_vi_co_pmid_that():
    """Danh sách «chưa kiểm» có CẢ PMID lẫn DOI — vì có PMID thật trong đó nên câu «đã đối
    chiếu» vẫn đúng cho PHẦN PMID (câu hiện tại không tách phần trăm theo loại — đây là giới
    hạn ĐÃ BIẾT, không phải bug; bản vá chỉ chặn trường hợp toàn bộ là DOI)."""
    msg = vd._thong_diep_pham_vi_rw(chua=["11111111", "10.1016/x"], rw=[{"loai": "pmid", "gia_tri": "3"}],
                                     pm_chua=["11111111"])
    assert "đã đối chiếu nền Retraction Watch NGOẠI TUYẾN cho các PMID chưa kiểm" in msg
    assert "CHỈ được hỏi cho PMID" not in msg
