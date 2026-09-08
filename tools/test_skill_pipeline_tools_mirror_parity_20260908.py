#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy: các tool dây chuyền dashboard dùng chung phải BYTE-IDENTICAL giữa
hai skill sync/skills/cap-nhat-chung-cu-y-khoa/tools/ và sync/skills/dark-analyst/tools/.

VÌ SAO CÓ (08/09/2026): CLAUDE.md mô tả hai skill này dùng chung MỘT schema
DATA và cùng bộ công cụ dây chuyền — nhưng trước bản vá này, 5/7 file dùng
chung đã LỆCH BẢN: build_library.py, check_topic_relevance.py,
dashboard_content_audit.py, drug_safety_scan.py, make_derivatives.py đều
thiếu bản vá UTF-8 stdout (`configure_utf8_stdio()`) mà cap-nhat-chung-cu-
y-khoa đã có từ 12/08/2026 (đúng bug: tool thoát mã 1 ở dòng print cuối vì
cp1252 trên Windows console, caller đọc mã thoát tưởng hỏng, bỏ luôn các
bước sau). Chỉ có `dong_bo_scanner_giam_sat.py` kiểm parity cho ĐÚNG MỘT
file (surveillance_scan.py) — 6 file còn lại không ai canh, nên trôi âm
thầm. Test này canh CẢ 7.

Nguyên tắc: so KHỚP BYTE, không so nội dung/AST — một dòng comment lệch
cũng là dấu hiệu hai bản đã tách nhánh sửa độc lập.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NGUON_CHUAN = REPO_ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools"
DARK_ANALYST = REPO_ROOT / "sync" / "skills" / "dark-analyst" / "tools"

# Các tool dây chuyền dashboard DÙNG CHUNG giữa hai skill (theo CLAUDE.md: cùng
# schema DATA, cùng bộ công cụ verify/build/derive). Không liệt kê file test
# (test_*.py) hay file chỉ một skill cần (vd build_trang_doc_artifact.py).
TOOL_DUNG_CHUNG = (
    "verify_dashboard.py",
    "surveillance_scan.py",
    "build_library.py",
    "check_topic_relevance.py",
    "dashboard_content_audit.py",
    "drug_safety_scan.py",
    "make_derivatives.py",
)


def test_ca_bay_tool_dung_chung_ton_tai_o_ca_hai_ban():
    for ten in TOOL_DUNG_CHUNG:
        assert (NGUON_CHUAN / ten).exists(), f"thiếu {ten} ở nguồn chuẩn cap-nhat-chung-cu-y-khoa"
        assert (DARK_ANALYST / ten).exists(), f"thiếu {ten} ở dark-analyst"


def test_ca_bay_tool_dung_chung_byte_identical():
    lech = []
    for ten in TOOL_DUNG_CHUNG:
        a = NGUON_CHUAN / ten
        b = DARK_ANALYST / ten
        if not (a.exists() and b.exists()):
            continue  # đã báo ở test trên
        if a.read_bytes() != b.read_bytes():
            lech.append(ten)
    assert not lech, (
        f"{len(lech)} tool lệch bản giữa cap-nhat-chung-cu-y-khoa và dark-analyst: "
        f"{', '.join(lech)} — chạy `cp sync/skills/cap-nhat-chung-cu-y-khoa/tools/<file> "
        "sync/skills/dark-analyst/tools/<file>` để đồng bộ lại (nguồn chuẩn là "
        "cap-nhat-chung-cu-y-khoa, theo quy ước dong_bo_scanner_giam_sat.py)."
    )
