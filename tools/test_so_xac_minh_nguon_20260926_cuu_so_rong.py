#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy rà phản biện #3 (26/09/2026): `--cuu-so-hong` KHÔNG được dựng sổ rỗng hợp lệ từ một tệp rỗng.

Tái hiện: sổ là tệp giữ chỗ 0 byte của OneDrive (Files On-Demand) ⇒ `doc_so()` ném `SoHongLoi` (đúng), nhưng
`--cuu-so-hong` bản đầu vẫn chép bản «hỏng» 0 byte rồi GHI một sổ rỗng hợp lệ ⇒ cổng quay về «sổ im lặng» (đúng
lỗ fail-open mà #3 vừa bịt) và OneDrive đồng bộ sổ rỗng đè lên bản thật trên đám mây. Nay: tệp rỗng / không có nổi
một khoá sổ ⇒ mã 2, không ghi gì, không tạo bản `.hong-*`.

Ngoại tuyến 100%: sổ ở thư mục tạm.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


SO = _nap("so_cuu_rong_20260926", ROOT / "tools" / "so_xac_minh_nguon.py")


@pytest.fixture()
def so_tam(tmp_path, monkeypatch):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    so = dash / ".so-xac-minh-nguon.json"
    monkeypatch.setattr(SO, "DASH", dash)
    monkeypatch.setattr(SO, "SO", so)
    return so


@pytest.mark.parametrize("tho", [b"", b"   \n", b"\x00\x00\x00\x00", b'{"phien_ban": 1, "mu'],
                         ids=["0_byte", "khoang_trang", "byte_rac", "khong_co_khoa_so"])
def test_cuu_so_rong_tu_choi_khong_ghi_gi(so_tam, capsys, tho):
    so_tam.write_bytes(tho)
    with mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", "--cuu-so-hong"]):
        assert SO.main() == 2
    assert so_tam.read_bytes() == tho, "tệp gốc phải giữ NGUYÊN byte — không được thay bằng sổ rỗng hợp lệ"
    assert not list(so_tam.parent.glob(".so-xac-minh-nguon.hong-*.json"))
    with pytest.raises(SO.SoHongLoi):
        SO.doc_so()  # cổng vẫn thấy sổ HỎNG (lỗi cứng), không phải sổ rỗng im lặng
    assert "KHÔNG cứu" in capsys.readouterr().err


def test_doi_chung_so_cat_cut_co_khoa_van_cuu_duoc(so_tam):
    """Đối chứng: tệp cắt cụt nhưng còn khoá sổ + dương tính ⇒ vẫn cứu (không chặn nhầm đường cứu thật)."""
    so_tam.write_bytes(b'{"muc": {"pmid:9500320": {"da_rut": true, "loai": "pmid"}, "pmid:1": {"gh')
    with mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", "--cuu-so-hong"]):
        assert SO.main() == 0
    assert SO.doc_so()["muc"]["pmid:9500320"]["da_rut"] is True
