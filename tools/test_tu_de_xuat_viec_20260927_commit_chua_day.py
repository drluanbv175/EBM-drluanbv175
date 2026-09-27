"""Cảm biến «commit chưa đẩy» phải nhìn MỌI nhánh cục bộ, không chỉ nhánh đang đứng — vá 27/09/2026.

Cảm biến cũ đếm `@{u}..HEAD`: nhánh đang đứng đã đẩy (hoặc chưa có upstream ⇒ git lỗi ⇒ đếm thành 0) thì báo
«0 commit chưa đẩy» dù nhánh khác còn giữ commit không có trên remote nào. Đo 27/09: 8 nhánh cục bộ của repo gốc
giữ 20 commit như vậy. Ngoại tuyến: remote là repo trần trong thư mục tạm.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_commit_chua_day", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)


def _g(cay: Path, *a: str) -> str:
    return subprocess.run(["git", *a], cwd=cay, check=True, capture_output=True, text=True).stdout.strip()


def _repo_co_nhanh_chua_day(tmp_path: Path) -> Path:
    """`main` đã đẩy; nhánh `phu` có 2 commit KHÔNG có trên remote; đang đứng ở `main`."""
    tran = tmp_path / "remote.git"
    _g(tmp_path, "init", "--bare", "-q", str(tran))
    cay = tmp_path / "cay"
    cay.mkdir()
    _g(cay, "init", "-q", "-b", "main")
    _g(cay, "config", "user.email", "t@t")
    _g(cay, "config", "user.name", "t")
    (cay / "a.txt").write_text("a", encoding="utf-8")
    _g(cay, "add", "a.txt")
    _g(cay, "commit", "-q", "-m", "goc")
    _g(cay, "remote", "add", "origin", str(tran))
    _g(cay, "push", "-q", "-u", "origin", "main")
    _g(cay, "switch", "-q", "-c", "phu")
    for i in (1, 2):
        (cay / f"b{i}.txt").write_text(str(i), encoding="utf-8")
        _g(cay, "add", f"b{i}.txt")
        _g(cay, "commit", "-q", "-m", f"phu {i}")
    _g(cay, "switch", "-q", "main")
    return cay


def test_nhanh_khac_giu_commit_chua_day_duoc_dem(tmp_path):
    cay = _repo_co_nhanh_chua_day(tmp_path)
    assert _g(cay, "rev-list", "--count", "@{u}..HEAD") == "0", "kịch bản: nhánh đang đứng đã đẩy hết"
    assert M.dem_commit_chua_co_tren_remote(cay) == (2, ["phu"]), \
        "cảm biến phải thấy 2 commit ở nhánh `phu` dù nhánh đang đứng sạch — cảm biến cũ báo 0"


def test_day_ban_sao_rescue_len_remote_thi_het_bao(tmp_path):
    cay = _repo_co_nhanh_chua_day(tmp_path)
    _g(cay, "push", "-q", "origin", "phu:refs/heads/rescue/phu")
    _g(cay, "fetch", "-q", "origin")
    assert M.dem_commit_chua_co_tren_remote(cay) == (0, [])


def test_khong_phai_repo_git_la_khong_do_duoc_chu_khong_phai_0(tmp_path):
    assert M.dem_commit_chua_co_tren_remote(tmp_path) == (None, []), \
        "git lỗi phải là KHÔNG ĐO ĐƯỢC (None), không được đọc thành «0 commit chưa đẩy»"
