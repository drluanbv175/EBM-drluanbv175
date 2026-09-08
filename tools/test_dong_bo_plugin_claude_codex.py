#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `_resolve_repo_root()` trong dong_bo_plugin_claude_codex.py.

Cùng họ lỗi đã vá 08/09/2026 ở `tools/dong_bo_skill_claude_codex.py` (xem
docstring test tương ứng, `test_dong_bo_skill_claude_codex.py`): công cụ này
CŨNG đọc một sổ khai dùng chung (`sync/plugin-manifest.json`) rồi ghi vào các
đường dẫn plugin DÙNG CHUNG cho cả máy (`~/.claude/plugins/...`,
`~/.codex/skills`). Trước bản vá, `REPO = Path(__file__).resolve().parents[1]`
suy gốc repo từ vị trí file — một phiên chạy TRONG một git worktree phụ sẽ đọc
`plugin-manifest.json` RIÊNG của worktree đó (có thể cũ hơn nhánh chính) rồi áp
lên trạng thái plugin DÙNG CHUNG cho mọi phiên trên máy.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`):
  (1) chỉ kiểm HÀNH VI bằng cách gọi vào mã đang sống, không đếm chuỗi trong file;
  (2) mỗi ca gắn với một rủi ro THẬT đã nêu trong docstring của công cụ;
  (3) nhanh và ngoại tuyến.

Chạy:  pytest tools/test_dong_bo_plugin_claude_codex.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dong_bo_plugin_claude_codex as DB  # noqa: E402


def _run_git(args, cwd):
    subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
    )


def _make_git_repo_with_worktree(tmp_path):
    main_repo = tmp_path / "repo-chinh"
    main_repo.mkdir()
    _run_git(["init", "-q", "-b", "main"], main_repo)
    (main_repo / "sync").mkdir()
    (main_repo / "sync" / "plugin-manifest.json").write_text("{}\n", encoding="utf-8")
    _run_git(["add", "-A"], main_repo)
    _run_git(["commit", "-q", "-m", "khoi tao"], main_repo)

    worktree_dir = main_repo / ".claude" / "worktrees" / "worktree-phu"
    worktree_dir.parent.mkdir(parents=True)
    _run_git(["worktree", "add", "-q", "-b", "nhanh-phu", str(worktree_dir)], main_repo)

    (worktree_dir / "tools").mkdir(parents=True, exist_ok=True)
    return main_repo, worktree_dir


def test_resolve_repo_root_from_inside_worktree_returns_main_repo(tmp_path):
    """Bug thật: gọi TỪ BÊN TRONG worktree phụ phải trả về gốc repo CHÍNH,
    không phải gốc worktree — kể cả khi worktree đó có sẵn sync/plugin-manifest.json
    riêng (bản khai cũ, dễ gây nhầm là "nguồn hợp lệ")."""
    main_repo, worktree_dir = _make_git_repo_with_worktree(tmp_path)
    # `git worktree add` đã checkout sẵn sync/plugin-manifest.json (tracked ở
    # commit khởi tạo) — ghi đè để mô phỏng "bản khai RIÊNG, có thể cũ, của
    # chính worktree đó", không cần tự tạo thư mục (đã có sẵn từ checkout).
    (worktree_dir / "sync" / "plugin-manifest.json").write_text(
        '{"khai": "cua worktree"}\n', encoding="utf-8"
    )

    resolved = DB._resolve_repo_root(start_dir=worktree_dir / "tools")

    assert resolved == main_repo, (
        f"Phải quy về repo CHÍNH ({main_repo}), không phải worktree phụ "
        f"({worktree_dir}) — nếu không, plugin-manifest.json sẽ đọc nhầm bản "
        f"cũ và áp lên trạng thái plugin dùng chung cho mọi phiên."
    )


def test_resolve_repo_root_from_main_repo_returns_itself(tmp_path):
    main_repo, _worktree_dir = _make_git_repo_with_worktree(tmp_path)
    tools_dir = main_repo / "tools"
    tools_dir.mkdir()

    resolved = DB._resolve_repo_root(start_dir=tools_dir)

    assert resolved == main_repo


def test_resolve_repo_root_falls_back_when_not_a_git_repo(tmp_path):
    lone_dir = tmp_path / "khong-phai-git" / "tools"
    lone_dir.mkdir(parents=True)

    resolved = DB._resolve_repo_root(start_dir=lone_dir)

    assert resolved == lone_dir.parent


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
