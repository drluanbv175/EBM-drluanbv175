#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt: các công cụ suy «cây chính» từ `git --git-common-dir` phải chịu được `.git` nằm NGOÀI cây (B1, 24/11/2026).

Bối cảnh: OneDrive hỏi «Remove files from OneDrive?» không dứt vì git liên tục xoá tệp trong `.git` (6.171 mục chỉ
trong buổi sáng 24/11). Phương án B1 (`audit/KE-HOACH-DUA-GIT-RA-KHOI-ONEDRIVE_20261122.md`) dời `.git` ra
`~/.ebm-git/<tên>.git`, trong OneDrive chỉ còn TỆP `.git` «gitdir: …». Khi đó common dir KHÔNG còn tên `.git`, cha của
nó là `~/.ebm-git` — lấy nhầm làm cây chính thì công cụ đồng bộ skill/plugin (chạy mỗi lần mở phiên) đọc `sync/...`
không tồn tại rồi áp lên trạng thái DÙNG CHUNG của máy. Git cũng in dòng đầu `git worktree list` là thư mục `.git`
bên ngoài. Cây chính thật khai ở config `ebm.cayChinh`.

Kiểm HÀNH VI trên repo thật dựng bằng `git init --separate-git-dir` (ngoại tuyến)."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="cần git (⚪ có khai báo)")


def _git(*args: str, cwd: Path | None = None) -> str:
    r = subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8", check=True)
    return r.stdout.strip()


def _nap(ten: str):
    sp = importlib.util.spec_from_file_location(f"_kiem_{ten}", TOOLS / f"{ten}.py")
    m = importlib.util.module_from_spec(sp)
    sys.modules[sp.name] = m          # @dataclass cần tìm thấy module của chính nó
    sp.loader.exec_module(m)
    return m


@pytest.fixture()
def cay_tach(tmp_path):
    """Cây chính `od/repo` có `.git` là TỆP trỏ ra `ext/repo.git`, kèm một worktree `wt/w1`. Trả (chinh, ext, w1)."""
    chinh, ext, w1 = tmp_path / "od" / "repo", tmp_path / "ext" / "repo.git", tmp_path / "wt" / "w1"
    chinh.parent.mkdir(parents=True)
    ext.parent.mkdir(parents=True)
    _git("init", "-q", "-b", "main", "--separate-git-dir", str(ext), str(chinh))
    (chinh / "tools").mkdir()
    (chinh / "tools" / "x.txt").write_text("x", encoding="utf-8")
    _git("add", "-A", cwd=chinh)
    _git("commit", "-qm", "c1", cwd=chinh)
    _git("worktree", "add", "-q", "-b", "n1", str(w1), cwd=chinh)
    assert (chinh / ".git").is_file() and Path(_git("rev-parse", "--path-format=absolute", "--git-common-dir",
                                                         cwd=w1)).name == "repo.git"
    return chinh, ext, w1


def _khai_cay_chinh(chinh: Path) -> None:
    _git("config", "ebm.cayChinh", str(chinh), cwd=chinh)


@pytest.mark.parametrize("ten,ham", [
    ("dong_bo_skill_claude_codex", "_resolve_repo_root"),
    ("dong_bo_skill", "goc_repo_chinh"),
    ("dong_bo_plugin_claude_codex", "_resolve_repo_root"),
])
def test_dong_bo_quy_ve_cay_chinh_khi_git_tach(cay_tach, ten, ham):
    """★ Có `ebm.cayChinh` ⇒ quy về đúng cây chính dù gọi từ worktree; không bao giờ trả thư mục chứa `.git` bên ngoài."""
    chinh, ext, w1 = cay_tach
    f = getattr(_nap(ten), ham)
    assert f(w1 / "tools") != ext.parent, "lấy cha của `.git` bên ngoài làm cây chính — sẽ đọc sync/... không tồn tại"
    _khai_cay_chinh(chinh)
    assert f(w1 / "tools").resolve() == chinh.resolve()
    assert f(chinh / "tools").resolve() == chinh.resolve()


def test_dong_bo_bo_cuc_thuong_khong_doi(tmp_path):
    """Bố cục thường (`.git` là thư mục) — hành vi y như trước: quy về cha của `.git`."""
    chinh, w1 = tmp_path / "repo", tmp_path / "w1"
    chinh.mkdir()
    _git("init", "-q", "-b", "main", cwd=chinh)
    (chinh / "tools").mkdir()
    (chinh / "tools" / "x.txt").write_text("x", encoding="utf-8")
    _git("add", "-A", cwd=chinh)
    _git("commit", "-qm", "c1", cwd=chinh)
    _git("worktree", "add", "-q", "-b", "n1", str(w1), cwd=chinh)
    m = _nap("dong_bo_skill_claude_codex")
    assert m._resolve_repo_root(w1 / "tools").resolve() == chinh.resolve()


def test_verify_plugin_dong_dau_worktree_list_la_cay_chinh(cay_tach):
    """★ `git worktree list` in dòng đầu là `ext/repo.git` — phải thay bằng cây chính khai báo."""
    chinh, ext, w1 = cay_tach
    vpo = _nap("verify_plugin_orchestration")
    _khai_cay_chinh(chinh)
    goc = [p.resolve() for p in vpo.cac_goc_worktree_git(chinh)]
    assert goc[0] == chinh.resolve() and w1.resolve() in goc and ext.resolve() not in goc


def test_don_worktree_tam_go_tu_cay_chinh(cay_tach):
    """★ Repo chính để chạy `git worktree remove` — không phải `ext/` (không phải cây làm việc)."""
    chinh, ext, w1 = cay_tach
    dwt = _nap("don_worktree_tam")

    def chay(args, cwd):
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
        return r.returncode, r.stdout

    assert dwt._repo_chinh(w1, chay).resolve() != ext.parent.resolve()
    _khai_cay_chinh(chinh)
    assert dwt._repo_chinh(w1, chay).resolve() == chinh.resolve()


def test_sync_safety_thay_khoa_trong_git_tach(cay_tach, monkeypatch):
    """★ `.git` là TỆP ⇒ chốt khoá phải soi trong thư mục git THẬT — không thì index.lock thành xanh giả."""
    chinh, ext, _ = cay_tach
    S = _nap("sync_safety_check")
    assert S._thu_muc_git_that(chinh).resolve() == ext.resolve()
    (ext / "index.lock").write_text("", encoding="utf-8")
    monkeypatch.setattr(S, "GIT_REPOS", [(".", chinh)])
    muc, ghi = S.check_git_health()
    assert muc == "RED" and any("index.lock" in g for g in ghi)
