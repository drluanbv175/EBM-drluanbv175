#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `_resolve_repo_root()` trong verify_plugin_orchestration.py.

Cùng họ lỗi đã vá 08/09/2026 ở `dong_bo_skill_claude_codex.py`/
`dong_bo_plugin_claude_codex.py` (xem `test_dong_bo_plugin_claude_codex.py`) —
nhưng lần này ở phía ĐỌC, không phải phía GHI. Trước bản vá này,
`ROUTER_SOURCE`/`ROUTER_ZIP` của chính cổng kiểm này được suy từ
`Path(__file__).resolve().parents[1]` — gốc của WORKTREE đang chạy cổng, không
phải repo CHÍNH. Trong khi đó `dong_bo_skill_claude_codex.py` (bên GHI symlink
`~/.claude/skills/plugin-router-chatgpt` và `~/.codex/skills/plugin-router-chatgpt`)
đã quy gốc qua `git rev-parse --git-common-dir` từ trước — nên symlink LUÔN trỏ
vào `sync/skills/plugin-router-chatgpt` của repo CHÍNH, bất kể ghi từ worktree
nào. Kết quả: chạy cổng này TỪ MỘT WORKTREE PHỤ báo FAIL giả ("router runtime
tro sai nguon") dù symlink hoàn toàn đúng — đo được thật 10/09/2026, cổng vẫn
FAIL sau khi chạy lại `dong_bo_skill_claude_codex.py --ap-dung --dong-bo-plugin`
để dựng lại đúng symlink, vì công cụ ĐỌC lệch gốc, không phải symlink sai.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`):
  (1) chỉ kiểm HÀNH VI bằng cách gọi vào mã đang sống, không đếm chuỗi trong file;
  (2) mỗi ca gắn với một rủi ro THẬT đã nêu trong docstring của công cụ;
  (3) nhanh và ngoại tuyến.

Chạy:  pytest tools/test_verify_plugin_orchestration_root.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_plugin_orchestration as VPO  # noqa: E402


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
    (main_repo / "sync" / "skills" / "plugin-router-chatgpt").mkdir(parents=True)
    (main_repo / "sync" / "skills" / "plugin-router-chatgpt" / "SKILL.md").write_text(
        "nguon CHINH\n", encoding="utf-8"
    )
    _run_git(["add", "-A"], main_repo)
    _run_git(["commit", "-q", "-m", "khoi tao"], main_repo)

    worktree_dir = main_repo / ".claude" / "worktrees" / "worktree-phu"
    worktree_dir.parent.mkdir(parents=True)
    _run_git(["worktree", "add", "-q", "-b", "nhanh-phu", str(worktree_dir)], main_repo)

    (worktree_dir / "tools").mkdir(parents=True, exist_ok=True)
    return main_repo, worktree_dir


def test_resolve_repo_root_from_inside_worktree_returns_main_repo(tmp_path):
    """Bug thật: gọi TỪ BÊN TRONG worktree phụ phải trả về gốc repo CHÍNH — nơi
    symlink `~/.claude/skills/plugin-router-chatgpt` thực sự trỏ tới — không phải
    gốc worktree, kể cả khi worktree đó có sẵn bản sao RIÊNG của
    sync/skills/plugin-router-chatgpt (checkout tự động khi tạo worktree)."""
    main_repo, worktree_dir = _make_git_repo_with_worktree(tmp_path)

    resolved = VPO._resolve_repo_root(start_dir=worktree_dir / "tools")

    assert resolved == main_repo, (
        f"Phải quy về repo CHÍNH ({main_repo}), không phải worktree phụ "
        f"({worktree_dir}) — nếu không, ROUTER_SOURCE sẽ trỏ vào bản sao của "
        f"worktree thay vì nơi symlink thật sự trỏ tới, và cổng báo FAIL giả."
    )


def test_resolve_repo_root_from_main_repo_returns_itself(tmp_path):
    main_repo, _worktree_dir = _make_git_repo_with_worktree(tmp_path)
    tools_dir = main_repo / "tools"
    tools_dir.mkdir()

    resolved = VPO._resolve_repo_root(start_dir=tools_dir)

    assert resolved == main_repo


def test_resolve_repo_root_falls_back_when_not_a_git_repo(tmp_path):
    lone_dir = tmp_path / "khong-phai-git" / "tools"
    lone_dir.mkdir(parents=True)

    resolved = VPO._resolve_repo_root(start_dir=lone_dir)

    assert resolved == lone_dir.parent


def test_router_source_paths_are_relative_to_repo_root_not_worktree():
    """Chốt hành vi cấp mô-đun: ROUTER_SOURCE/ROUTER_ZIP phải nằm dưới
    REPO_ROOT (đã quy gốc qua git), không phải ROOT (gốc của chính worktree
    đang chạy pytest) — nếu ai đó vô tình đổi lại ROUTER_SOURCE = ROOT / ...
    thì ca này bắt được ngay khi hai giá trị lệch nhau trên một worktree phụ."""
    assert VPO.ROUTER_SOURCE == VPO.REPO_ROOT / "sync/skills/plugin-router-chatgpt"
    assert VPO.ROUTER_ZIP == VPO.REPO_ROOT / "CHATGPT_SKILLS/dist/plugin-router-chatgpt.zip"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
