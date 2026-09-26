"""Cảm biến CI của `tu_de_xuat_viec.py` lùi về GitHub REST API khi máy không có `gh` — 26/09/2026.

Ngoại tuyến: `urlopen` giả, remote git dựng trong thư mục tạm.
"""
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_ci", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)


def _repo(tmp_path: Path, url: str) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "remote", "add", "origin", url], check=True)
    return tmp_path


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _gia(payload, bat=None):
    def mo(req, timeout=0):
        bat is not None and bat.append(req.full_url)
        if isinstance(payload, Exception):
            raise payload
        return _Resp(json.dumps(payload).encode())
    return mo


@pytest.fixture(autouse=True)
def _sach():
    M._GIAC_QUAN_CHET.clear()
    M._SO_GIAC_QUAN["chay"] = 0


@pytest.mark.parametrize("url", [
    "https://github.com/chu/kho.git",
    "git@github.com:chu/kho.git",
    "http://local_proxy@127.0.0.1:41000/git/chu/kho",
])
def test_suy_owner_repo_moi_kieu_remote(tmp_path, url):
    assert M._owner_repo_tu_remote(_repo(tmp_path, url)) == "chu/kho"


def test_doc_phan_quyet_dung_workflow(tmp_path):
    bat: list[str] = []
    kq = M.doc_ci_qua_api(_repo(tmp_path, "https://github.com/chu/kho"), "ci.yml",
                          urlopen=_gia({"workflow_runs": [{"conclusion": "failure"}]}, bat))
    assert kq == "failure"
    assert bat == ["https://api.github.com/repos/chu/kho/actions/workflows/ci.yml/runs?per_page=1"]
    assert M._GIAC_QUAN_CHET == [] and M._SO_GIAC_QUAN["chay"] == 1


def test_dang_chay_tra_rong_nhung_khong_phai_giac_quan_chet(tmp_path):
    kq = M.doc_ci_qua_api(_repo(tmp_path, "https://github.com/chu/kho"), "ci.yml",
                          urlopen=_gia({"workflow_runs": [{"conclusion": None}]}))
    assert kq == "" and M._GIAC_QUAN_CHET == []


@pytest.mark.parametrize("payload", [OSError("mang"), {"workflow_runs": []}])
def test_khong_doc_duoc_la_khong_do_duoc_khong_bao_gio_success(tmp_path, payload):
    kq = M.doc_ci_qua_api(_repo(tmp_path, "https://github.com/chu/kho"), "ci.yml", urlopen=_gia(payload))
    assert kq == ""
    assert len(M._GIAC_QUAN_CHET) == 1                   # bảng không được in xanh
