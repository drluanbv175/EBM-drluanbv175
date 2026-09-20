#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho run_eval.py — chốt bản sao trần (vòng 3, 10/09/2026).

Bối cảnh: trước bản vá, `run_eval.py` chạy MỘT PHẦN trên bản sao trần rồi chết
bằng traceback thô (`ModuleNotFoundError: No module named 'app'`) — và TRƯỚC
CẢ đó, Khối 1 đã đọc SAI: `thu_dau_cuoi_chung_cu.py` (canary) cũng crash vì
thiếu EBM-Dashboards/ (khác lý do — FileNotFoundError), khiến máy chấm báo
"CÓ LỖ HỔNG" (N09 ✗) trong khi sự thật là "chưa chạy được vì thiếu hạ tầng".
Đúng họ lỗi BH08/BH99/BH100: gộp "không biết" với "có vấn đề".

ĐÍNH CHÍNH 17/09/2026 (Gap 2, cascade duong_goc): early-bail cũ dùng
`ban_sao_git_tran(GOC)` — trên cloud (cloud-aware từ "Vòng 5") chỉ đòi
EBM-Dashboards/EBM_MASTER vắng, và HAI gốc đó LUÔN vắng trên MỌI phiên cloud,
nên máy chấm LUÔN bail dù medical-ebm-automation/ có mặt đầy đủ (sibling) —
0/11 nhóm chạy dù phần lớn không đụng EBM-Dashboards (BH08: "thiếu MỘT VÀI
nguyên liệu" bị đọc thành "không kiểm được GÌ CẢ"). Nay early-bail CHỈ còn
đòi đúng dependency CỨNG của file này — medical-ebm-automation/ resolvable
qua duong_goc() (Khối 2 import thẳng app.sources.retraction_chain, không có
đường giảm nhẹ) — nên điều kiện skip của bộ test này phải khớp ĐÚNG cùng một
câu hỏi, không phải câu hỏi bare-clone rộng hơn của ban_sao_git_tran() nữa;
nếu không, trên một phiên cloud có sibling medical-ebm-automation, test sẽ
tưởng nhánh early-bail còn chạy (dựa theo bare-clone cũ) trong khi thực ra
main() đã đi tiếp qua Khối 1-6 — cùng khoảng lệch mà bản vá này đóng lại.

Test này CHỈ có ý nghĩa khi CHÍNH dependency cứng đó (medical-ebm-automation/
+ app/sources/retraction_chain.py) không resolve được — trên máy có đủ cây đó
thì nhánh chặn sớm không chạy tới và test này không đo được gì, nên skip rõ
ràng thay vì khẳng định sai (cùng luật BH08 mà chính bản vá này bảo vệ).
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

_MEA_GOC = ban_sao_tran.duong_goc("medical-ebm-automation", GOC) or (GOC / "medical-ebm-automation")
_THIEU_MEA_CUNG = not (_MEA_GOC / "app" / "sources" / "retraction_chain.py").exists()

pytestmark = pytest.mark.skipif(
    not _THIEU_MEA_CUNG,
    reason="máy này CÓ medical-ebm-automation/app/sources/retraction_chain.py (lồng "
           "hoặc anh em) — nhánh chặn sớm không chạy tới, test không đo được gì",
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
    assert "THIẾU medical-ebm-automation" in r.stdout
    assert "HẠ TẦNG THIẾU" in r.stdout


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
