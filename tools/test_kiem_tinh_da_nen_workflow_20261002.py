#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy GỌN CI (02/10/2026): `kiem-tinh-da-nen.yml` chạy chồng lượt, ma trận thừa, không có trần thời gian.

Đo 70 lượt gần nhất: một nhánh có 50 lượt/10 ngày × 4 job, mỗi push chồng lên push cũ của cùng nhánh; Python 3.11 và 3.12 luôn cùng kết quả
(0/70 lệch) trong khi bản Python của máy Mac thật (3.14) không lane nào phủ; Windows là lane duy nhất từng đỏ riêng một mình.
Kiểm bằng văn bản (runner trần không có PyYAML)."""
from __future__ import annotations

import re
from pathlib import Path

TEP = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "kiem-tinh-da-nen.yml"


def _doc() -> str:
    return TEP.read_text(encoding="utf-8")


def _matrix() -> list[tuple[str, str]]:
    return re.findall(r'- os: ([\w.-]+)\n\s+python-version: "([\d.]+)"', _doc())


def test_ba_lane_dai_dien_ba_moi_truong_that():
    assert sorted(_matrix()) == sorted([("ubuntu-latest", "3.11"), ("windows-latest", "3.12"), ("ubuntu-latest", "3.14")])


def test_san_3_11_va_may_windows_va_may_mac_deu_duoc_phu():
    m = _matrix()
    assert ("ubuntu-latest", "3.11") in m, "mất lane SÀN 3.11 — cú pháp PEP 701 lại lọt (ca 22/08)"
    assert any(o == "windows-latest" for o, _ in m), "mất lane Windows — họ lỗi «gãy trên máy kia» không còn ai bắt"
    assert any(v == "3.14" for _, v in m), "không lane nào phủ Python 3.14 của máy Mac"


def test_khong_dung_ma_tran_nhan_hai_chieu_nua():
    assert "os: [ubuntu-latest, windows-latest]" not in _doc(), "quay lại ma trận 2×2 (4 job, cặp 3.11/3.12 luôn trùng kết quả)"


def test_huy_luot_cu_cua_cung_nhanh_nhung_khong_bao_gio_huy_master():
    d = _doc()
    assert re.search(r"(?m)^concurrency:\n  group: kiem-tinh-da-nen-\$\{\{ github\.ref \}\}", d)
    assert "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}" in d


def test_co_tran_thoi_gian_cho_job_va_job_tong_ket():
    d = _doc()
    khoi = d[d.index("\n  kiem-tinh:\n"):d.index("\n  ci-ok:\n")]   # CHỈ job kiem-tinh (ci-ok có trần riêng, không được che lỗi này)
    assert re.search(r"(?m)^    timeout-minutes: \d+", khoi), "job kiem-tinh không có trần thời gian"
    assert re.search(r"(?m)^  ci-ok:\n    name: ci-ok\n    if: always\(\)\n    needs: \[kiem-tinh\]", d)
    assert 'needs.kiem-tinh.result' in d and '"success"' in d, "ci-ok phải đòi kiem-tinh == success (huỷ/bỏ qua cũng là đỏ)"


def test_khong_them_su_kien_pull_request_gay_chay_trung():
    d = _doc()
    on = d[d.index("\non:"):d.index("\npermissions:")]
    assert "pull_request" not in on, "thêm pull_request trong khi push đã phủ ⇒ mỗi commit PR chạy hai lần (đo medical: 43/71 commit bị trùng)"
    assert 'branches: [ "**" ]' in on


def test_cac_buoc_kiem_van_con_du():
    d = _doc()
    for chuoi in ("python -m compileall -q tools ops", "tools/kiem_tuong_thich_da_nen.py", "tools/tu_de_xuat_viec.py --gon",
                  "python -m pytest tools/ -q -rs", "tools/sync_agents_to_codex.py"):
        assert chuoi in d, f"mất bước kiểm: {chuoi}"


def test_hanh_dong_van_ghim_sha():
    for u in re.findall(r"(?m)^\s+(?:- )?uses:\s*(\S+)", _doc()):
        assert re.search(r"@[0-9a-f]{40}$", u), f"hành động không ghim SHA: {u}"
