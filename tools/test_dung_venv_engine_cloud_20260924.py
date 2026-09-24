"""Kiểm `tools/dung_venv_engine_cloud.py` (24/09/2026) — OFFLINE, không tạo venv thật."""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

_P = Path(__file__).resolve().parent / "dung_venv_engine_cloud.py"
_sp = importlib.util.spec_from_file_location("dung_venv_engine_cloud", _P)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)


def _chay(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["dung_venv_engine_cloud.py", *args])
    return M.main()


def test_may_that_khong_lam_gi(monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    monkeypatch.setattr(M, "venv_san_sang", lambda *a: pytest.fail("không được kiểm venv trên máy thật"))
    assert _chay(monkeypatch, "--ap-dung") == 0


def test_cloud_venv_san_sang_thi_im(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    monkeypatch.setattr(M, "goc_engine", lambda: tmp_path)
    monkeypatch.setattr(M, "venv_san_sang", lambda *a: True)
    monkeypatch.setattr(M.subprocess, "Popen", lambda *a, **k: pytest.fail("không được dựng lại"))
    assert _chay(monkeypatch, "--ap-dung") == 0


def test_cloud_thieu_venv_im_khi_on_bao_1(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    monkeypatch.setattr(M, "goc_engine", lambda: tmp_path)
    monkeypatch.setattr(M, "venv_san_sang", lambda *a: False)
    monkeypatch.setattr(M, "dang_dung", lambda *a: False)
    assert _chay(monkeypatch, "--im-khi-on") == 1


def test_cloud_thieu_venv_ap_dung_phong_nen_khong_chan(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    monkeypatch.setattr(M, "goc_engine", lambda: tmp_path)
    monkeypatch.setattr(M, "venv_san_sang", lambda *a: False)
    monkeypatch.setattr(M, "dang_dung", lambda *a: False)
    monkeypatch.setattr(M, "tim_python312", lambda: "/usr/bin/python3.12")
    monkeypatch.setattr(M, "NHAT_KY", tmp_path / "log")
    monkeypatch.setattr(M, "KHOA", tmp_path / "lock")
    goi = {}

    class _P:
        pid = 4242

        def __init__(self, lenh, **kw):
            goi["lenh"], goi["kw"] = lenh, kw

    monkeypatch.setattr(M.subprocess, "Popen", _P)
    assert _chay(monkeypatch, "--ap-dung") == 0
    assert goi["kw"].get("start_new_session") is True          # tách tiến trình, không chặn phiên
    assert "requirements.lock.txt" in goi["lenh"][-1]           # cài ĐÚNG bản khoá
    assert "python3.12" in goi["lenh"][-1]
    assert "--clear" in goi["lenh"][-1]                         # venv 3.11 cũ phải bị thay
    assert (tmp_path / "lock").read_text() == "4242"


def test_dang_dung_thi_khong_phong_chong(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    monkeypatch.setattr(M, "goc_engine", lambda: tmp_path)
    monkeypatch.setattr(M, "venv_san_sang", lambda *a: False)
    monkeypatch.setattr(M, "dang_dung", lambda *a: True)
    monkeypatch.setattr(M.subprocess, "Popen", lambda *a, **k: pytest.fail("phóng chồng"))
    assert _chay(monkeypatch, "--ap-dung") == 0


def test_khong_co_python312_bao_2(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    monkeypatch.setattr(M, "goc_engine", lambda: tmp_path)
    monkeypatch.setattr(M, "venv_san_sang", lambda *a: False)
    monkeypatch.setattr(M, "dang_dung", lambda *a: False)
    monkeypatch.setattr(M, "tim_python312", lambda: None)
    assert _chay(monkeypatch, "--ap-dung") == 2


def test_venv_co_thu_muc_nhung_thieu_module_la_chua_san_sang(tmp_path):
    py = tmp_path / "bin" / "python"
    py.parent.mkdir(parents=True)
    py.write_text("#!/bin/sh\nexit 1\n")
    os.chmod(py, 0o755)
    assert M.venv_san_sang(tmp_path) is False


def test_khoa_pid_chet_khong_tinh_la_dang_dung(tmp_path):
    k = tmp_path / "lock"
    k.write_text("999999999")
    assert M.dang_dung(k) is False
    k.write_text(str(os.getpid()))
    assert M.dang_dung(k) is True


def test_noi_vao_tu_sua_chua_chay_tren_cloud():
    spec = importlib.util.spec_from_file_location("tsc", Path(__file__).resolve().parent / "tu_sua_chua.py")
    tsc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tsc)
    muc = [v for v in tsc.VIEC_MAY if any("dung_venv_engine_cloud.py" in str(x) for x in v[1])]
    assert muc, "chưa nối vào VIEC_MAY"
    assert muc[0][3] is True and "--ap-dung" in muc[0][2]
