#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #40 (26/09/2026): `xuat_tong_thuat.py --mo` gọi thẳng lệnh `open`
của macOS. Trên Windows/Linux (không có `open`) nó ném FileNotFoundError SAU KHI đã ghi
HTML ⇒ traceback, mã 1, và dòng disclaimer «Cần bác sĩ kiểm chứng» ở stdout bị mất.

Hợp đồng sau vá: disclaimer in TRƯỚC nhánh --mo; mở trình duyệt qua `webbrowser` trong
try; không mở được chỉ CẢNH BÁO, mã thoát giữ 0 (việc xuất đã xong); cổng hình thức trích
dẫn (mã 2) không bị đụng tới.

Test giả lập MỌI đường mở tệp đều hỏng như máy không có trình duyệt/`open` (webbrowser,
subprocess, os.startfile) để kết quả như nhau trên Mac/Windows/Linux, và trỏ RA_DIR vào
tmp_path — không ghi vào cây repo.
"""
from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import sys
import webbrowser
from contextlib import redirect_stdout
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent

BAI_DAT = """# Tổng thuật thử

Metformin là lựa chọn đầu tay [1]. Cần bác sĩ kiểm chứng.

## Nguồn

1. Tác giả A. Bài thử. Tạp chí. 2024. PMID 12345678
"""


def _nap():
    spec = importlib.util.spec_from_file_location("xuat_tong_thuat_t20260926",
                                                  HERE / "xuat_tong_thuat.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["xuat_tong_thuat_t20260926"] = mod
    spec.loader.exec_module(mod)
    return mod


X = _nap()


def _hong(*_a, **_k):
    raise FileNotFoundError(2, "No such file or directory: 'open'")


@pytest.fixture
def moi_truong(monkeypatch, tmp_path):
    ra = tmp_path / "ra"
    monkeypatch.setattr(X, "RA_DIR", ra)
    md = tmp_path / "bai.md"
    md.write_text(BAI_DAT, encoding="utf-8")
    return md, ra


def _chay(monkeypatch, *argv: str) -> tuple[int, str]:
    monkeypatch.setattr(sys, "argv", ["xuat_tong_thuat.py", *argv])
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = X.main()
    return rc, buf.getvalue()


def test_mo_hong_filenotfound_van_ma_0_co_html_co_disclaimer(monkeypatch, moi_truong):
    md, ra = moi_truong
    monkeypatch.setattr(webbrowser, "open", _hong)
    monkeypatch.setattr(subprocess, "run", _hong)
    if hasattr(os, "startfile"):
        monkeypatch.setattr(os, "startfile", _hong)
    rc, out = _chay(monkeypatch, str(md), "--mo")
    assert rc == 0, out
    assert (ra / "bai.html").is_file()
    assert "Cần bác sĩ kiểm chứng." in out
    assert "⚠ Không mở được trình duyệt" in out


def test_trinh_duyet_tra_false_chi_canh_bao(monkeypatch, moi_truong):
    md, ra = moi_truong
    monkeypatch.setattr(webbrowser, "open", lambda *_a, **_k: False)
    rc, out = _chay(monkeypatch, str(md), "--mo")
    assert rc == 0
    assert "⚠ Không mở được trình duyệt" in out


def test_disclaimer_in_truoc_khi_thu_mo(monkeypatch, moi_truong):
    """Dòng disclaimer phải có mặt TRƯỚC lúc thử mở — không phụ thuộc kết quả mở."""
    md, ra = moi_truong
    luc_mo = {}

    def mo_ghi_lai(uri, *_a, **_k):
        luc_mo["uri"] = uri
        luc_mo["da_in"] = "Cần bác sĩ kiểm chứng." in buf.getvalue()
        return True

    monkeypatch.setattr(webbrowser, "open", mo_ghi_lai)
    monkeypatch.setattr(sys, "argv", ["xuat_tong_thuat.py", str(md), "--mo"])
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = X.main()
    assert rc == 0
    assert luc_mo.get("da_in") is True, buf.getvalue()
    assert luc_mo["uri"].startswith("file:") and luc_mo["uri"].endswith("bai.html")
    assert "⚠" not in buf.getvalue()


def test_khong_mo_thi_khong_goi_trinh_duyet(monkeypatch, moi_truong):
    md, ra = moi_truong
    monkeypatch.setattr(webbrowser, "open", _hong)
    rc, out = _chay(monkeypatch, str(md))
    assert rc == 0 and "Cần bác sĩ kiểm chứng." in out and "⚠" not in out


def test_cong_hinh_thuc_van_chan_ma_2(monkeypatch, moi_truong, tmp_path):
    """Đối chứng: cổng trích dẫn không bị bản vá nới — thiếu disclaimer vẫn mã 2, không render."""
    md, ra = moi_truong
    md.write_text(BAI_DAT.replace("Cần bác sĩ kiểm chứng.", ""), encoding="utf-8")
    monkeypatch.setattr(webbrowser, "open", _hong)
    rc, out = _chay(monkeypatch, str(md), "--mo")
    assert rc == 2
    assert not (ra / "bai.html").exists()
