"""Rào «origin/HEAD CŨ» của cảm biến CI (`tu_de_xuat_viec._nhanh_mac_dinh`) — rà phản biện 26/09/2026.

`refs/remotes/origin/HEAD` là bản chụp CỤC BỘ lúc clone; git không tự cập nhật khi GitHub đổi nhánh
mặc định. Một clone cũ của repo y khoa có thể còn trỏ `origin/main` — nhánh BỎ từ 28/06 — và nếu tin
nó ngay thì cảm biến đọc run cuối của `main` (có thể xanh) trong khi nhánh mặc định thật đang đỏ:
đúng họ xanh giả mà mục #9 sửa, chỉ đổi đường vào. Test khoá:
  • origin/HEAD KHỚP khai báo ⇒ dùng ngay, không gọi mạng;
  • origin/HEAD LỆCH khai báo ⇒ hỏi API `default_branch` (nguồn thẩm quyền) và theo API;
  • lệch khai báo mà API hỏng ⇒ «» (không đoán) ⇒ `doc_ci_mot_repo` không gửi truy vấn run nào,
    ghi đúng 1 giác quan chết, KHÔNG BAO GIỜ trả «success».

Ngoại tuyến: `urlopen` giả, repo git dựng trong thư mục tạm.
"""
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_origin_head_cu", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

NHANH_YK = "feat/r1-1-2-design-gap-remediation"
URL_YK = "https://github.com/chu/medical-ebm-automation.git"


def _g(cay: Path, *a: str) -> None:
    subprocess.run(["git", *a], cwd=cay, check=True, capture_output=True, text=True)


def _repo_origin_head(tmp_path: Path, url: str, nhanh_head: str) -> Path:
    """Repo tạm có `origin/HEAD` là symbolic ref trỏ `origin/<nhanh_head>`."""
    cay = tmp_path / "cay"
    cay.mkdir()
    _g(cay, "init", "-q", "-b", "master")
    _g(cay, "remote", "add", "origin", url)
    _g(cay, "config", "user.email", "t@t.t")
    _g(cay, "config", "user.name", "t")
    _g(cay, "config", "commit.gpgsign", "false")
    (cay / "a.txt").write_text("1", encoding="utf-8")
    _g(cay, "add", "-A")
    _g(cay, "commit", "-qm", "c1")
    _g(cay, "update-ref", f"refs/remotes/origin/{nhanh_head}", "HEAD")
    _g(cay, "symbolic-ref", "refs/remotes/origin/HEAD", f"refs/remotes/origin/{nhanh_head}")
    return cay


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _mo_gia(tuyen: dict, bat: list[str]):
    def mo(req, timeout=0):
        url = req.full_url
        bat.append(url)
        for khoa, payload in tuyen.items():
            if url.split("?")[0].endswith(khoa):
                if isinstance(payload, Exception):
                    raise payload
                return _Resp(json.dumps(payload).encode())
        raise OSError(f"không có tuyến giả cho {url}")
    return mo


@pytest.fixture(autouse=True)
def _sach():
    M._GIAC_QUAN_CHET.clear()
    M._SO_GIAC_QUAN["chay"] = 0


def test_origin_head_khop_khai_bao_dung_ngay_khong_goi_mang(tmp_path):
    bat: list[str] = []
    cay = _repo_origin_head(tmp_path, URL_YK, NHANH_YK)
    assert M._nhanh_mac_dinh(cay, urlopen=_mo_gia({}, bat), co_gh=False) == NHANH_YK
    assert bat == []


def test_origin_head_cu_lech_khai_bao_hoi_api_va_theo_api(tmp_path):
    bat: list[str] = []
    cay = _repo_origin_head(tmp_path, URL_YK, "main")
    nhanh = M._nhanh_mac_dinh(
        cay, urlopen=_mo_gia({"/repos/chu/medical-ebm-automation": {"default_branch": NHANH_YK}}, bat),
        co_gh=False)
    assert nhanh == NHANH_YK
    assert bat == ["https://api.github.com/repos/chu/medical-ebm-automation"]


def test_origin_head_cu_lech_khai_bao_api_hong_khong_doan(tmp_path):
    cay = _repo_origin_head(tmp_path, URL_YK, "main")
    nhanh = M._nhanh_mac_dinh(
        cay, urlopen=_mo_gia({"/repos/chu/medical-ebm-automation": OSError("x")}, []), co_gh=False)
    assert nhanh == ""


def test_doc_ci_mot_repo_origin_head_cu_khong_bao_gio_success(tmp_path):
    """Chuỗi đầy đủ: origin/HEAD→main cũ, API repo hỏng, /runs của main xanh ⇒ «», không hỏi /runs."""
    bat: list[str] = []
    cay = _repo_origin_head(tmp_path, URL_YK, "main")
    kq, nhanh = M.doc_ci_mot_repo(
        "y khoa", cay, "offline-ci.yml", co_gh=False,
        urlopen=_mo_gia({"/repos/chu/medical-ebm-automation": OSError("x"),
                         "/runs": {"workflow_runs": [{"conclusion": "success", "head_branch": "main"}]}},
                        bat))
    assert (kq, nhanh) == ("", "")
    assert not any("/runs" in u for u in bat)
    assert len(M._GIAC_QUAN_CHET) == 1
