"""tools/bat_git_hook.py — bật core.hooksPath=.githooks, không ghi đè lựa chọn khác của người dùng. 26/09/2026."""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "bat_git_hook.py"
_sp = importlib.util.spec_from_file_location("bat_git_hook_t", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)


def _repo(p: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(p)], check=True)
    (p / ".githooks").mkdir()
    (p / ".githooks" / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8", newline="\n")
    return p


def test_bat_khi_chua_co(tmp_path):
    r = _repo(tmp_path / "a")
    assert M.hooks_path(r) is None
    assert M.bat(r) is True and M.hooks_path(r) == ".githooks"


def test_khong_ghi_de_thu_muc_hook_khac(tmp_path):
    r = _repo(tmp_path / "b")
    subprocess.run(["git", "-C", str(r), "config", "core.hooksPath", "hooks-rieng"], check=True)
    assert M.bat(r) is False and M.hooks_path(r) == "hooks-rieng"


def test_main_im_khi_on_va_ap_dung(monkeypatch, tmp_path):
    r = _repo(tmp_path / "c")
    monkeypatch.setattr(M, "cac_repo", lambda: [r])
    assert M.main(["--im-khi-on"]) == 1
    assert M.main(["--ap-dung"]) == 0 and M.main(["--im-khi-on"]) == 0


def test_tu_sua_chua_chay_muc_nay_ca_tren_cloud():
    nguon = (_TEP.parent / "tu_sua_chua.py").read_text(encoding="utf-8")
    assert '[PY, "tools/bat_git_hook.py", "--ap-dung"], True),' in nguon


def test_khong_doi_mode_tep_hook_khac(tmp_path):
    """Chỉ pre-commit được bật bit thực thi — post-commit track trong git giữ nguyên mode."""
    r = _repo(tmp_path / "d")
    post = r / ".githooks" / "post-commit"
    post.write_text("#!/bin/sh\n", encoding="utf-8", newline="\n")
    post.chmod(0o644)
    (r / ".githooks" / "pre-commit").chmod(0o644)
    assert M.bat(r) is True
    assert post.stat().st_mode & 0o777 == 0o644
    assert (r / ".githooks" / "pre-commit").stat().st_mode & 0o100
