#!/usr/bin/env python3
"""Bật git hook pre-commit fail-closed (`core.hooksPath=.githooks`) cho repo gốc và repo y khoa — 26/09/2026.

CLAUDE.md §2 dặn «kích hoạt 1 lần/máy» bằng tay. Container Cloud dựng MỚI mỗi phiên nên bước tay đó
không bao giờ còn: đo 26/09, `verify_mcp_live_sync.py` báo cả hai repo `core.hooksPath=None` ⇒ mọi
commit trên Cloud đi qua mà KHÔNG chạy cổng pre-commit (mirror drift, guardrail, nhiễm artifact,
liêm chính exports/), trừ khi phiên đó tự nhớ `git -c core.hooksPath=.githooks commit`.

Chỉ đặt cấu hình git CỤC BỘ của repo (`git config core.hooksPath .githooks`) và bật bit thực thi cho
tệp hook đã có; KHÔNG sửa nội dung hook, KHÔNG đổi hook của repo đang trỏ nơi khác.
Nối vào `tu_sua_chua.py` (chạy mỗi phiên, kể cả `--pham-vi-cloud`).

Mã thoát: 0 = đã bật đủ (hoặc repo vắng) · 1 = còn repo chưa bật (--im-khi-on) · 2 = bật thất bại.
"""
from __future__ import annotations

import importlib.util
import os
import stat
import subprocess
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
_sp = importlib.util.spec_from_file_location("_bst_bgh", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_bst)
MONG_DOI = ".githooks"


def cac_repo() -> list[Path]:
    """Repo gốc + repo y khoa (lồng hoặc anh em) — chỉ những repo có .git và .githooks/pre-commit."""
    ung_vien = [GOC, _bst.duong_goc("medical-ebm-automation", GOC)]
    return [r for r in ung_vien if r and (r / ".git").exists() and (r / MONG_DOI / "pre-commit").is_file()]


def hooks_path(repo: Path) -> str | None:
    r = subprocess.run(["git", "-C", str(repo), "config", "--get", "core.hooksPath"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (r.stdout or "").strip() or None


def bat(repo: Path) -> bool:
    """Đặt hooksPath; KHÔNG ghi đè nếu repo đang trỏ tới một thư mục hook KHÁC (quyết định của người dùng)."""
    hien = hooks_path(repo)
    if hien not in (None, MONG_DOI):
        return False
    if hien is None:
        subprocess.run(["git", "-C", str(repo), "config", "core.hooksPath", MONG_DOI], check=False)
    # Chỉ pre-commit, và chỉ khi mất bit thực thi (OneDrive/Windows hay làm rơi): bật bit cho tệp track
    # khác (vd post-commit) sẽ tạo thay đổi mode trong git — đo thật 26/09 ở repo y khoa.
    pre = repo / MONG_DOI / "pre-commit"
    if os.name != "nt" and not os.access(pre, os.X_OK):
        pre.chmod(pre.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return hooks_path(repo) == MONG_DOI


def main(argv: list[str]) -> int:
    ap_dung, im = "--ap-dung" in argv, "--im-khi-on" in argv
    thieu = [r for r in cac_repo() if hooks_path(r) != MONG_DOI]
    if not thieu:
        if not im:
            print("🟢 core.hooksPath=.githooks đã bật ở mọi repo có hook.")
        return 0
    if not ap_dung:
        for r in thieu:
            print(f"🟡 {r.name}: core.hooksPath={hooks_path(r)!r} (cần '{MONG_DOI}') — chạy với --ap-dung để bật")
        return 1
    loi = [r for r in thieu if not bat(r)]
    for r in thieu:
        print(("✗ " if r in loi else "✓ ") + f"{r.name}: core.hooksPath={hooks_path(r)!r}")
    return 2 if loi else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
