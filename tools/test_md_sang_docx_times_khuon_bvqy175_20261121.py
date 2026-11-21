# -*- coding: utf-8 -*-
"""`md_sang_docx_times.py` với đề cương theo khuôn hướng dẫn chung BVQY175 (21/11/2026).

Đề cương có «# CHƯƠNG 1.» phải xuất bằng chế độ khuôn của repo y khoa (14pt, giãn 1,5, ba phần đánh số trang); chế độ
đề cương 13pt của công cụ này sẽ phá khuôn. Repo y khoa vắng/cũ ⇒ không ghi (không đè bản đúng khuôn). Ngoại tuyến,
module md2docx_vn giả — không phụ thuộc repo y khoa có mặt.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("docx")

REPO = Path(__file__).resolve().parents[1]
_sp = importlib.util.spec_from_file_location("_md_docx_khuon", REPO / "tools/md_sang_docx_times.py")
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

KHUON = "**BỆNH VIỆN MẪU**\n\n---\n\n# ĐẶT VẤN ĐỀ\n\nĐoạn.\n\n# CHƯƠNG 1. TỔNG QUAN TÀI LIỆU\n\nĐoạn.\n"
CU = "# ĐỀ CƯƠNG\n\n# 1. ĐẶT VẤN ĐỀ\n\nĐoạn.\n"


class _M2DCoKhuon:
    def __init__(self):
        self.goi = []

    def markdown_to_docx(self, md, out_path, title_page=None, khuon_bvqy175=False):
        self.goi.append(khuon_bvqy175)
        Path(out_path).write_bytes(b"PK-gia")
        return Path(out_path)


class _M2DCu:
    def markdown_to_docx(self, md, out_path, title_page=None):  # bản cũ: chưa có chế độ khuôn
        raise AssertionError("không được gọi")


def test_nhan_dien_de_cuong_khuon():
    assert M.la_de_cuong_khuon(KHUON) and not M.la_de_cuong_khuon(CU)


def test_de_cuong_khuon_giao_cho_che_do_khuon(tmp_path, monkeypatch):
    gia = _M2DCoKhuon()
    monkeypatch.setattr(M, "_nap_md2docx_vn", lambda: (gia, "md2docx_vn.py (giả)"))
    nguon = tmp_path / "de-cuong.md"
    nguon.write_text(KHUON, encoding="utf-8")
    assert M.main([str(nguon), "--co-chu", "13", "--trang-de-cuong"]) == 0
    assert gia.goi == [True]


def test_repo_y_khoa_cu_thi_khong_ghi(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(M, "_nap_md2docx_vn", lambda: (_M2DCu(), "md2docx_vn.py (cũ)"))
    nguon = tmp_path / "de-cuong.md"
    nguon.write_text(KHUON, encoding="utf-8")
    ra = tmp_path / "de-cuong.docx"
    ra.write_bytes(b"ban-dung-khuon")
    assert M.main([str(nguon)]) == 1
    assert ra.read_bytes() == b"ban-dung-khuon"  # bản đúng khuôn không bị đè
    assert "chưa có chế độ khuôn" in capsys.readouterr().err


def test_repo_y_khoa_vang_thi_khong_ghi(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "_nap_md2docx_vn", lambda: (None, "không thấy medical-ebm-automation/"))
    nguon = tmp_path / "de-cuong.md"
    nguon.write_text(KHUON, encoding="utf-8")
    assert M.main([str(nguon)]) == 1 and not (tmp_path / "de-cuong.docx").exists()


def test_de_cuong_cu_khong_doi_duong(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "_nap_md2docx_vn", lambda: (_ for _ in ()).throw(AssertionError("không được gọi")))
    nguon = tmp_path / "de-cuong.md"
    nguon.write_text(CU, encoding="utf-8")
    M.main([str(nguon), "--co-chu", "13"])
    assert (tmp_path / "de-cuong.docx").is_file()
