#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy AN-09 (03/10/2026): trạng thái phiên do hook harness ghi (`.claude/state/`, `.claude/sessions/` ở MỌI thư mục làm việc)
không được nằm trong git — 29 tệp từng bị track ở tools/, tools/eval/, sync/skills/… làm lộ đường dẫn máy và mã phiên ra repo công
khai. `.gitignore` chặn tệp MỚI; test này chặn tệp đã track lọt lại (vd `git add -f`)."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MAU = re.compile(r"(^|/)\.claude/(state|sessions)/")


@pytest.mark.skipif(shutil.which("git") is None or not (REPO / ".git").exists(), reason="cần git và cây git (⚪ có khai báo)")
def test_khong_tep_trang_thai_harness_nao_bi_track():
    ra = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"], capture_output=True, timeout=60)
    assert ra.returncode == 0, ra.stderr
    lot = [f for f in ra.stdout.decode("utf-8", "replace").split("\0") if MAU.search(f)]
    assert lot == [], f"{len(lot)} tệp trạng thái harness đang bị track: {lot[:5]} — git rm --cached"


def test_gitignore_chan_tep_moi():
    s = (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "**/.claude/state/" in s and "**/.claude/sessions/" in s
