#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`kiem_dieu_phoi.phan_loai_runtime` — skill ĐÃ GỠ có chủ ý còn ở runtime Cowork (đến từ skill tài khoản claude.ai)
là việc 👤 của bác sĩ, không phải 🔴 «mất nguồn» (24/10/2026: BH44 đỏ sau khi gỡ aipoch). Ngoại tuyến."""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import kiem_dieu_phoi as KD  # noqa: E402


def test_skill_da_go_co_chu_y_la_viec_tai_khoan_khong_phai_mat_nguon():
    khong_nguon, cho_tk = KD.phan_loai_runtime({"dieu-phoi-aipoch", "skill-la"}, nguon=set())
    assert khong_nguon == ["skill-la"], "skill lạ không nguồn vẫn phải ĐỎ"
    assert cho_tk == ["dieu-phoi-aipoch"]


def test_skill_tro_lai_nguon_thi_khong_con_la_da_go():
    khong_nguon, cho_tk = KD.phan_loai_runtime({"dieu-phoi-aipoch"}, nguon={"dieu-phoi-aipoch"})
    assert khong_nguon == [] and cho_tk == []


def test_moi_dong_da_go_co_ly_do_va_khong_trung_skill_dung_san():
    assert all(str(v).strip() for v in KD.SKILL_DA_GO_CHO_TAI_KHOAN.values())
    assert not set(KD.SKILL_DA_GO_CHO_TAI_KHOAN) & KD.SKILL_DUNG_SAN
