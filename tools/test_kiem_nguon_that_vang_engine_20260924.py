# -*- coding: utf-8 -*-
"""Test `kiem_nguon_that.kiem_env()` khi VẮNG repo engine (24/09/2026, đo lại nguồn trên Cloud).

Đo thật: phiên Cloud chỉ-một-repo không có `medical-ebm-automation` ⇒ công cụ báo «THIẾU THƯ VIỆN
(No module named 'app') — cài venv» và hook Cloud đọc mã 1 thành «DỮ LIỆU GIẢ», trong khi môi trường
đã đặt USE_MOCK_SOURCES=false + NCBI_EMAIL. Vắng engine phải là «KHÔNG ĐO ĐƯỢC» (🟡), nói đúng nguyên
nhân, và không in giá trị NCBI_EMAIL. Nhánh «thiếu thư viện» THẬT (engine có mặt nhưng import hỏng)
phải giữ nguyên. Không cần engine để chạy — dùng thư mục tạm, chạy được trên bản sao trần/CI.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_DUONG = Path(__file__).resolve().parent / "kiem_nguon_that.py"


@pytest.fixture()
def knt(monkeypatch):
    spec = importlib.util.spec_from_file_location("_knt_test_vang_engine", _DUONG)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # kiem_env() chèn MEA vào sys.path và import `app.config` — cô lập để không rò sang test khác.
    monkeypatch.setattr(sys, "path", list(sys.path))
    for ten in [t for t in sys.modules if t == "app" or t.startswith("app.")]:
        monkeypatch.delitem(sys.modules, ten)
    return mod


def test_vang_engine_la_khong_do_duoc_khong_phai_thieu_thu_vien(knt, monkeypatch, tmp_path):
    monkeypatch.setattr(knt, "MEA", tmp_path / "medical-ebm-automation")
    monkeypatch.setenv("USE_MOCK_SOURCES", "false")
    muc, tin = knt.kiem_env()
    assert muc == "vang"                       # 🟡 không đo được — không 🔴, không 🟢
    assert "KHÔNG có repo engine" in tin[0]
    assert "THIẾU THƯ VIỆN" not in tin[0]      # lời khuyên «cài venv» là sai khi không có engine
    assert "USE_MOCK_SOURCES=false" in tin[0]


def test_vang_engine_khong_in_gia_tri_ncbi_email(knt, monkeypatch, tmp_path):
    monkeypatch.setattr(knt, "MEA", tmp_path / "medical-ebm-automation")
    monkeypatch.setenv("NCBI_EMAIL", "bac-si-gia@example.org")
    monkeypatch.delenv("USE_MOCK_SOURCES", raising=False)
    _muc, tin = knt.kiem_env()
    assert "bac-si-gia@example.org" not in tin[0]
    assert "NCBI_EMAIL=có" in tin[0]
    assert "USE_MOCK_SOURCES=(không đặt)" in tin[0]


def test_engine_co_mat_nhung_import_hong_van_bao_thieu_thu_vien(knt, monkeypatch, tmp_path):
    mea = tmp_path / "medical-ebm-automation"
    (mea / "app").mkdir(parents=True)
    (mea / "app" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (mea / "app" / "config.py").write_text("import thu_vien_khong_ton_tai_24092026  # noqa\n",
                                           encoding="utf-8", newline="\n")
    monkeypatch.setattr(knt, "MEA", mea)
    muc, tin = knt.kiem_env()
    assert muc == "vang"
    assert "THIẾU THƯ VIỆN" in tin[0]
    assert "thu_vien_khong_ton_tai_24092026" in tin[0]
