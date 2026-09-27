# -*- coding: utf-8 -*-
"""Hồi quy 26/09/2026 (synthesis #37) — tập check của run_verification() và độ phủ test.

Lỗi: commit e682cc5 (24/09) thêm `check_claude_md_budget()` vào run_verification()
nhưng test_claude_code_repo_alignment_overall_passes vẫn so với tập 6 check cũ ⇒ đỏ
trên Mac/Windows, còn trên Cloud/CI bị conftest skip che nên không ai thấy.

Hai phép kiểm:
  1. Tập tên check khớp CHÍNH XÁC (không so tập con — tập con làm yếu chốt).
  2. conftest KHÔNG còn skip test tổng — để lần trôi sau bị bắt ngay trên Cloud/CI.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLS))
import verify_claude_code_repo_alignment as V  # noqa: E402

_TAP_CHECK = {
    "root_docs",
    "claude_md_budget",
    "medical_repo_docs",
    "tracked_contract_files",
    "agent_sync_health",
    "agent_files_git_tracked",
    "upgrade_verify_wiring",
}


def test_tap_check_run_verification_khop_chinh_xac_va_khong_trung():
    ten = [check["name"] for check in V.run_verification()["checks"]]
    assert len(ten) == len(set(ten)), f"tên check bị trùng: {ten}"
    assert set(ten) == _TAP_CHECK


def test_chot_ngan_sach_claude_md_nam_trong_tap_check():
    ten = {check["name"] for check in V.run_verification()["checks"]}
    assert "claude_md_budget" in ten


def _nap_conftest():
    spec = importlib.util.spec_from_file_location(
        "_conftest_hoi_quy_tap_check_20260926", _TOOLS / "conftest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_conftest_khong_con_skip_test_tong_alignment():
    cf = _nap_conftest()
    ten_test = "test_claude_code_repo_alignment_overall_passes"
    for bang in ("_TEST_CAN_ONEDRIVE", "_TEST_CAN_REPO_Y_KHOA"):
        for tep, tap in getattr(cf, bang).items():
            assert ten_test not in tap, f"{ten_test} vẫn bị skip qua {bang}[{tep}]"
