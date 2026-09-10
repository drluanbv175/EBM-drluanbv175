#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho run_eval.py — chốt bản sao trần (vòng 3, 10/09/2026).

Bối cảnh: trước bản vá, `run_eval.py` chạy MỘT PHẦN trên bản sao trần rồi chết
bằng traceback thô (`ModuleNotFoundError: No module named 'app'`) — và TRƯỚC
CẢ đó, Khối 1 đã đọc SAI: `thu_dau_cuoi_chung_cu.py` (canary) cũng crash vì
thiếu EBM-Dashboards/ (khác lý do — FileNotFoundError), khiến máy chấm báo
"CÓ LỖ HỔNG" (N09 ✗) trong khi sự thật là "chưa chạy được vì thiếu hạ tầng".
Đúng họ lỗi BH08/BH99/BH100: gộp "không biết" với "có vấn đề".

Test này CHỈ có ý nghĩa trên bản sao trần (đúng môi trường CI/worktree hiện
tại) — trên máy có đủ EBM-Dashboards/medical-ebm-automation thì nhánh chặn
sớm không chạy tới và test này không đo được gì, nên skip rõ ràng thay vì
khẳng định sai (cùng luật BH08 mà chính bản vá này bảo vệ).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import ban_sao_tran  # noqa: E402

GOC = Path(__file__).resolve().parents[2]
RUN_EVAL = GOC / "quality" / "eval" / "run_eval.py"

_BAN_SAO_TRAN = ban_sao_tran.ban_sao_git_tran(GOC)

pytestmark = pytest.mark.skipif(
    not _BAN_SAO_TRAN,
    reason="máy này CÓ đủ EBM-Dashboards/medical-ebm-automation — nhánh chặn sớm "
           "không chạy tới, test không đo được gì trên máy này",
)


def test_thoat_ma_2_khong_phai_traceback_tho():
    r = subprocess.run([sys.executable, str(RUN_EVAL)], capture_output=True, text=True,
                       cwd=GOC, timeout=60)
    assert r.returncode == 2, f"phải là mã 2 (hạ tầng thiếu), không phải {r.returncode}"
    assert "Traceback (most recent call last)" not in r.stderr, (
        "phải chặn TRƯỚC khi crash, không để lộ traceback thô ra ngoài")


def test_khong_bao_nham_la_co_lo_hong():
    r = subprocess.run([sys.executable, str(RUN_EVAL)], capture_output=True, text=True,
                       cwd=GOC, timeout=60)
    assert "CÓ LỖ HỔNG" not in r.stdout, (
        "hạ tầng thiếu KHÔNG được đọc thành 'canary phát hiện lỗ hổng thật'")
    assert "BẢN SAO GIT TRẦN" in r.stdout
    assert "HẠ TẦNG THIẾU" in r.stdout


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
