#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `_resolve_main_repo_root()` trong verify_plugin_orchestration.py.

Bối cảnh (10/09/2026): commit ở phiên worktree `focused-jang-fead23` bị chặn vĩnh
viễn bởi chính cổng này — router runtime (`~/.claude/skills/plugin-router-chatgpt`,
`~/.codex/skills/plugin-router-chatgpt`) trỏ ĐÚNG về repo CHÍNH (đúng theo bản vá
08/09/2026 của `dong_bo_skill_claude_codex._resolve_repo_root()`), nhưng cổng này
so sánh với `ROOT` — suy trực tiếp từ vị trí file (`parents[1]`) — nên khi chạy TỪ
một worktree phụ, ROOT luôn là gốc worktree, không phải repo chính. Kết quả: cổng
báo "router runtime trỏ sai nguồn" cho một runtime đang trỏ ĐÚNG, và báo "thiếu gói
ZIP" cho một gói thật sự tồn tại ở repo chính (`CHATGPT_SKILLS/dist/` bị gitignore
nên không bao giờ có mặt trong bất kỳ worktree phụ nào — reproducible ở MỌI
worktree, không riêng phiên cloud). Đây là CÙNG một lớp lỗi mà
`dong_bo_skill_claude_codex._resolve_repo_root()` /
`dong_bo_plugin_claude_codex._resolve_repo_root()` đã sửa — verifier này chưa từng
nhận bản vá tương ứng cho tới bản vá đi kèm bộ test này.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`):
  (1) chỉ kiểm HÀNH VI bằng cách gọi vào mã đang sống, không đếm chuỗi trong file;
  (2) mỗi ca gắn với một rủi ro THẬT đã nêu trong docstring của công cụ;
  (3) nhanh và ngoại tuyến (dựng repo git thật trong tmp_path, không đụng .git sống).

Chạy:  pytest tools/test_verify_plugin_orchestration.py
       python3 tools/test_verify_plugin_orchestration.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_plugin_orchestration as VPO  # noqa: E402


def _run_git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
    )


def _make_git_repo_with_worktree(tmp_path: Path) -> tuple[Path, Path]:
    """Dựng một repo git thật + một worktree phụ thật, độc lập với repo của
    chính dự án này (để test không đụng vào `.git` sống)."""
    main_repo = tmp_path / "repo-chinh"
    main_repo.mkdir()
    _run_git(["init", "-q", "-b", "main"], main_repo)
    (main_repo / "sync" / "skills" / "plugin-router-chatgpt").mkdir(parents=True)
    (main_repo / "README.md").write_text("goc\n", encoding="utf-8")
    _run_git(["add", "-A"], main_repo)
    _run_git(["commit", "-q", "-m", "khoi tao"], main_repo)

    worktree_dir = main_repo / ".claude" / "worktrees" / "worktree-phu"
    worktree_dir.parent.mkdir(parents=True)
    _run_git(["worktree", "add", "-q", "-b", "nhanh-phu", str(worktree_dir)], main_repo)

    (worktree_dir / "tools").mkdir(parents=True, exist_ok=True)
    return main_repo, worktree_dir


def test_resolve_main_repo_root_from_inside_worktree_returns_main_repo(tmp_path: Path) -> None:
    """Bug thật đã chặn commit: gọi TỪ BÊN TRONG worktree phụ phải trả về gốc
    repo CHÍNH — nơi ~/.claude/skills và ~/.codex/skills thực sự trỏ tới — không
    phải gốc worktree, kể cả khi worktree đó có sẵn `sync/skills` riêng (bản sao
    độc lập, dễ nhầm là "nguồn hợp lệ")."""
    main_repo, worktree_dir = _make_git_repo_with_worktree(tmp_path)
    (worktree_dir / "sync" / "skills" / "plugin-router-chatgpt").mkdir(parents=True)

    resolved = VPO._resolve_main_repo_root(start_dir=worktree_dir / "tools")

    assert resolved == main_repo, (
        f"Phải quy về repo CHÍNH ({main_repo}), không phải worktree phụ "
        f"({worktree_dir}) — nếu không, cổng sẽ báo 'router runtime trỏ sai "
        f"nguồn' cho một runtime đang trỏ ĐÚNG về repo chính."
    )


def test_resolve_main_repo_root_from_main_repo_returns_itself(tmp_path: Path) -> None:
    """Đối chứng: gọi từ CHÍNH repo (không phải worktree) không được đổi hành
    vi — vẫn phải trả về đúng gốc repo đó (no-op cho máy chạy đơn-checkout)."""
    main_repo, _worktree_dir = _make_git_repo_with_worktree(tmp_path)
    tools_dir = main_repo / "tools"
    tools_dir.mkdir()

    resolved = VPO._resolve_main_repo_root(start_dir=tools_dir)

    assert resolved == main_repo


def test_resolve_main_repo_root_falls_back_when_not_a_git_repo(tmp_path: Path) -> None:
    """Không phải git repo (hoặc git không gọi được) thì lùi về ROOT (hành vi
    cũ) thay vì ném lỗi làm chết cổng."""
    lone_dir = tmp_path / "khong-phai-git" / "tools"
    lone_dir.mkdir(parents=True)

    resolved = VPO._resolve_main_repo_root(start_dir=lone_dir)

    assert resolved == VPO.ROOT


def test_router_zip_and_source_are_scoped_to_main_repo_root() -> None:
    """Đối chứng cấu trúc: ROUTER_ZIP và CANONICAL_ROUTER_SOURCE phải nằm dưới
    MAIN_REPO_ROOT (tài nguyên dùng chung máy), còn ROUTER_SOURCE — dùng cho các
    kiểm tra NỘI DUNG file router (missing_router, catalog.json) — vẫn phải nằm
    dưới ROOT (worktree đang commit), để một lần sửa SKILL.md/catalog trong
    worktree luôn được cổng này soát tới ngay, không phải đợi đồng bộ sang repo
    chính trước."""
    assert VPO.ROUTER_ZIP.is_relative_to(VPO.MAIN_REPO_ROOT)
    assert VPO.CANONICAL_ROUTER_SOURCE.is_relative_to(VPO.MAIN_REPO_ROOT)
    assert VPO.ROUTER_SOURCE.is_relative_to(VPO.ROOT)


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
