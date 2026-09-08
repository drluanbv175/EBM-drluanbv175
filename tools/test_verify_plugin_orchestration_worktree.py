"""Test _git_common_dir() trong verify_plugin_orchestration.py (worktree khác repo).

VÌ SAO CÓ (06/09/2026). `verify_plugin_orchestration.py` từng báo FAIL "router
runtime tro sai nguon" trên MỌI phiên chạy từ một `git worktree` phụ (vd phiên
cloud), vì symlink máy thật `~/.claude/skills/plugin-router-chatgpt` trỏ vào bản
checkout CHÍNH trong khi `ROOT` của phiên là một worktree khác — đúng cây git,
khác đường dẫn. So sánh path tuyệt đối coi đó là "trỏ sai nguồn", chặn commit vô
cớ trên mọi phiên worktree, không liên quan gì tới nội dung đang sửa.

Đã vá bằng `_git_common_dir()`: hai worktree của CÙNG repo luôn trỏ về CÙNG một
`.git` thật (git-common-dir) — test này khoá lại ĐÚNG hai chiều, để bản vá không
biến thành lỗ hổng: (1) worktree khác của CÙNG repo → được nhận diện đúng "cùng
repo"; (2) một thư mục git KHÁC HẲN (hoặc không phải git) → KHÔNG được coi là
cùng repo, symlink trỏ tới đó vẫn phải bị chặn như cũ (đây là trường hợp hijack/
trỏ nhầm thật).

Chạy: `pytest tools/test_verify_plugin_orchestration_worktree.py` hoặc
`python tools/test_verify_plugin_orchestration_worktree.py`.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify_plugin_orchestration as vpo  # noqa: E402


def _git(cay: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cay, check=True, capture_output=True, text=True)


def test_khong_phai_git_tra_none() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        khong_git = Path(tmp) / "khong-co-git"
        khong_git.mkdir()
        assert vpo._git_common_dir(khong_git) is None


def test_thu_muc_khong_ton_tai_tra_none() -> None:
    assert vpo._git_common_dir(Path("/duong-dan-khong-bao-gio-ton-tai-abc123")) is None


def test_repo_khac_han_khong_khop_root() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo_khac = Path(tmp) / "repo-khac"
        repo_khac.mkdir()
        _git(repo_khac, "init", "-q")
        khac = vpo._git_common_dir(repo_khac)
        root = vpo._git_common_dir(vpo.ROOT)
        assert khac is not None
        assert khac != root, "repo hoàn toàn khác KHÔNG được coi là cùng repo với ROOT"


def test_worktree_cua_chinh_root_khop_common_dir() -> None:
    """Tạo một `git worktree` THẬT của repo hiện tại — phải cùng git-common-dir với ROOT."""
    root_common = vpo._git_common_dir(vpo.ROOT)
    assert root_common is not None, "ROOT phải là một cây git hợp lệ để chạy test này"
    with tempfile.TemporaryDirectory() as tmp:
        worktree_path = Path(tmp) / "worktree-thu"
        r = subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree_path)],
            cwd=vpo.ROOT, capture_output=True, text=True,
        )
        try:
            assert r.returncode == 0, f"git worktree add thất bại: {r.stderr}"
            worktree_common = vpo._git_common_dir(worktree_path)
            assert worktree_common == root_common, (
                "worktree mới tạo của CHÍNH repo này phải cùng git-common-dir với ROOT"
            )
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree_path)],
                cwd=vpo.ROOT, capture_output=True, text=True,
            )


if __name__ == "__main__":
    ok = True
    for ten, ham in list(globals().items()):
        if ten.startswith("test_") and callable(ham):
            try:
                ham()
                print(f"✓ {ten}")
            except AssertionError as exc:
                ok = False
                print(f"✗ {ten}: {exc}")
    raise SystemExit(0 if ok else 1)
