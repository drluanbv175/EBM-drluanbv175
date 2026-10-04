#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bộ đọc sâu gắn nhãn đúng nguồn cho PDF phiên uỷ quyền Chrome (04/10/2026).

Chạy thật 04/10 trên kho: dòng từng bài in «(PDF PDF lưu trong phiên…)» (lặp chữ) và dòng tổng kết gọi MỌI PDF vừa sinh là
«PDF kênh TDM của NXB» dù 3/3 là PDF phiên Chrome — nói sai nguồn. Khoá: tổng kết đếm RIÊNG hai loại PDF; dòng từng bài không lặp
«PDF PDF». Ngoại tuyến (bộ đọc PDF giả).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location("_ds_nhan_chr", TOOLS / "doc_sau_toan_van.py")
DS = importlib.util.module_from_spec(sp)
sys.modules[sp.name] = DS
sp.loader.exec_module(DS)


def test_tong_ket_dem_rieng_pdf_tdm_va_pdf_phien_chrome(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(DS, "_doc_pdf", lambda pdf: (["Title\nAbstract\n" + "word " * 900], "Title"))
    dash = tmp_path / "EBM-Dashboards"
    kho = dash / "toan_van_oa"
    kho.mkdir(parents=True)
    (kho / "PMID-11111111_WTDM.pdf").write_bytes(b"%PDF-1.7 gia")
    (kho / "PMID-22222222_CHR.pdf").write_bytes(b"%PDF-1.7 gia")
    (kho / "PMID-33333333_CHR.pdf").write_bytes(b"%PDF-1.7 gia")
    assert DS.main(["--pmid", "11111111", "22222222", "33333333", "--dash", str(dash)]) == 0
    ra = capsys.readouterr().out
    assert "1 bài PDF kênh TDM của NXB · 2 bài PDF phiên uỷ quyền Chrome" in ra, ra
    assert "PDF PDF" not in ra
    md = (kho / "doc_sau" / "PMID-22222222.md").read_text(encoding="utf-8")
    assert DS.NHAN_NGUON_CHR in md and "token" not in md
