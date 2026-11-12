# -*- coding: utf-8 -*-
"""md_sang_docx_times: không khai --co-chu thì tệp ra trong exports/ (hồ sơ đề tài) dùng 13pt — chuẩn trình bày của cổng
G0–G10 — còn nơi khác giữ 12pt như cũ (12/11/2026: 5 tài liệu đề tài BTM dựng bằng cỡ mặc định 12 bị bộ đo báo đỏ).
Khai --co-chu tường minh luôn thắng."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytest.importorskip("docx")
from docx import Document  # noqa: E402

TOOLS = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("md_sang_docx_times_cc", TOOLS / "md_sang_docx_times.py")
M = importlib.util.module_from_spec(_spec)
sys.modules["md_sang_docx_times_cc"] = M
_spec.loader.exec_module(M)


def _co_than(docx: Path) -> float:
    """Cỡ chữ của ĐÚNG đoạn thân bài (tiêu đề cũng là đoạn Normal nhưng chữ to hơn — không lấy)."""
    doc = Document(str(docx))
    for p in doc.paragraphs:
        if p.text.strip() == "Đoạn thân bài của tài liệu.":
            for r in p.runs:
                if r.font.size:
                    return r.font.size.pt
            if p.style.font.size:
                return p.style.font.size.pt
    return doc.styles["Normal"].font.size.pt


def _md(d: Path) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    p = d / "tai-lieu.md"
    p.write_text("# Tiêu đề\n\nĐoạn thân bài của tài liệu.\n", encoding="utf-8", newline="\n")
    return p


def test_co_chu_mac_dinh_theo_noi_ra(tmp_path):
    assert M.co_chu_mac_dinh(tmp_path / "exports" / "S" / "x.docx") == 13.0
    assert M.co_chu_mac_dinh(tmp_path / "bao-cao" / "x.docx") == 12.0


def test_main_trong_exports_ra_13pt_ngoai_exports_ra_12pt(tmp_path):
    p13 = _md(tmp_path / "exports" / "S")
    assert M.main([str(p13)]) == 0
    assert _co_than(p13.with_suffix(".docx")) == 13.0
    p12 = _md(tmp_path / "bao-cao")
    assert M.main([str(p12)]) == 0
    assert _co_than(p12.with_suffix(".docx")) == 12.0


def test_khai_tuong_minh_luon_thang(tmp_path):
    p = _md(tmp_path / "exports" / "S")
    assert M.main([str(p), "--co-chu", "12"]) == 0
    assert _co_than(p.with_suffix(".docx")) == 12.0
