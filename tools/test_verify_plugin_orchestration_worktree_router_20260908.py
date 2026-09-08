#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy: cổng `verify_plugin_orchestration.py` phải NHẬN DIỆN được symlink
router runtime trỏ vào MỘT WORKTREE KHÁC của cùng repo, không chỉ worktree
đang chạy verifier.

VÌ SAO CÓ (08/09/2026): phiên Claude Code chạy trong một git WORKTREE riêng
(`.claude/worktrees/<tên>`), dùng chung `.git` với cây chính. Symlink runtime
của máy thật (`~/.claude/skills/plugin-router-chatgpt`,
`~/.codex/skills/plugin-router-chatgpt`) là tài nguyên TOÀN MÁY, luôn trỏ về
MỘT cây cố định (thường là cây chính bác sĩ dùng hằng ngày) — không lồng theo
worktree đang chạy. Bản cũ của `verify()` so `target.resolve()` với
`ROUTER_SOURCE` (luôn tính từ `ROOT`-của-worktree-đang-chạy) nên CHẶN CỨNG
mọi lần commit từ bất kỳ worktree nào khác worktree đang giữ symlink — kể cả
khi symlink hoàn toàn đúng và không có gì hỏng. Đã xác nhận bằng `git stash`:
lỗi giống hệt khi không có thay đổi nào đang chờ commit.

Test này canh HÀNH VI của hai hàm mới (`worktree_roots`, `router_source_candidates`)
bằng repo git THẬT dựng trong `tmp_path` — không đếm chuỗi trong file.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_plugin_orchestration as VPO  # noqa: E402


def _git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True,
                    capture_output=True, text=True)


def _init_repo_with_worktree(tmp_path):
    """Repo git THẬT có 2 worktree — mô phỏng đúng cấu trúc máy thật (cây
    chính + worktree ephemeral của phiên Claude Code)."""
    main = tmp_path / "main"
    main.mkdir()
    _git(["init", "-q"], cwd=main)
    _git(["config", "user.email", "t@t.test"], cwd=main)
    _git(["config", "user.name", "t"], cwd=main)
    (main / "README.md").write_text("x", encoding="utf-8")
    _git(["add", "."], cwd=main)
    _git(["commit", "-q", "-m", "init"], cwd=main)
    wt = tmp_path / "wt"
    _git(["worktree", "add", "-q", str(wt), "-b", "feature"], cwd=main)
    return main, wt


def test_worktree_roots_liet_ke_ca_hai_worktree(tmp_path):
    main, wt = _init_repo_with_worktree(tmp_path)
    roots = {p.resolve() for p in VPO.worktree_roots(main)}
    assert main.resolve() in roots
    assert wt.resolve() in roots


def test_worktree_roots_lui_ve_root_khi_khong_phai_repo_git(tmp_path):
    """Không gọi được `git worktree list` (không phải repo git) → lùi về [root]
    cũ, KHÔNG bao giờ trả rỗng hay ném lỗi ra ngoài."""
    khong_phai_git = tmp_path / "khong-phai-git"
    khong_phai_git.mkdir()
    assert VPO.worktree_roots(khong_phai_git) == [khong_phai_git]


def test_router_source_candidates_nhan_dien_worktree_khac(tmp_path):
    """Ca thật: verifier chạy từ `main`, nhưng nội dung router router chỉ có ở
    worktree KHÁC (`wt`) — đúng tình huống ngược của bug thật (máy thật trỏ về
    cây chính, phiên Claude Code chạy ở worktree). Phải NHẬN được cả hai phía."""
    main, wt = _init_repo_with_worktree(tmp_path)
    router_wt = wt / "sync" / "skills" / "plugin-router-chatgpt"
    router_wt.mkdir(parents=True)
    (router_wt / "SKILL.md").write_text("x", encoding="utf-8")

    candidates = VPO.router_source_candidates(main)
    assert router_wt.resolve() in candidates


def test_router_source_candidates_khong_nhan_thu_muc_la(tmp_path):
    """Chốt đối kháng — KHÔNG được nới lỏng thành 'chấp nhận bất kỳ đường dẫn
    nào'. Một thư mục lạ, không phải worktree của repo, không được lọt vào tập
    hợp lệ dù nó cũng tên `plugin-router-chatgpt`."""
    main, wt = _init_repo_with_worktree(tmp_path)
    router_wt = wt / "sync" / "skills" / "plugin-router-chatgpt"
    router_wt.mkdir(parents=True)

    thu_muc_la = tmp_path / "khong-lien-quan" / "plugin-router-chatgpt"
    thu_muc_la.mkdir(parents=True)

    candidates = VPO.router_source_candidates(main)
    assert thu_muc_la.resolve() not in candidates


def test_router_source_candidates_lui_ve_hanh_vi_cu_khi_khong_worktree_nao_co(tmp_path):
    """Không worktree nào có `sync/skills/plugin-router-chatgpt` thật → lùi về
    đúng `ROOT/sync/skills/plugin-router-chatgpt` của root truyền vào (hành vi
    CŨ, không nới lỏng thêm khi không có gì để mở rộng)."""
    main, _wt = _init_repo_with_worktree(tmp_path)
    candidates = VPO.router_source_candidates(main)
    assert candidates == {(main / "sync" / "skills" / "plugin-router-chatgpt").resolve()}


def test_check_that_would_have_caught_the_real_bug(tmp_path):
    """Tái hiện ĐÚNG bug thật đã chặn commit 08/09/2026: máy thật trỏ symlink
    runtime về worktree A, verifier lại chạy từ worktree B. Bản CŨ (so với
    ROUTER_SOURCE cố định của B) sẽ luôn FAIL ở đây; bản MỚI phải PASS."""
    main, wt = _init_repo_with_worktree(tmp_path)
    router_main = main / "sync" / "skills" / "plugin-router-chatgpt"
    router_main.mkdir(parents=True)
    (router_main / "SKILL.md").write_text("x", encoding="utf-8")

    # "Máy thật" trỏ về worktree `main`; verifier "đang chạy" từ `wt`.
    candidates_tu_wt = VPO.router_source_candidates(wt)
    assert router_main.resolve() in candidates_tu_wt

    # Đồng thời một target trỏ ra ngoài repo vẫn phải bị bắt — không phải mọi
    # thứ tự nhiên PASS sau khi mở rộng tập hợp lệ.
    target_hong = tmp_path / "mot-noi-khac"
    target_hong.mkdir()
    assert target_hong.resolve() not in candidates_tu_wt
