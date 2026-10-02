#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy F5 (02/10/2026): khoá `.quet.lock` của bộ quét phải NGUYÊN TỬ — đúng MỘT tiến trình giành được.

Đo ở kiểm toàn diện: 10 tiến trình cùng giành một mốc, 10 vòng ⇒ 10/10 vòng có > 1 tiến trình «giành được» (kiểm-rồi-ghi). Chỉ
thêm `O_EXCL` vẫn hở khi đã có khoá MỒ CÔI (8 tiến trình: 2–5/vòng cùng thay). Test dưới chạy N tiến trình Python THẬT, cùng đợi
một mốc thời gian rồi cùng gọi `gianh_khoa()` trên tệp khoá trong thư mục tạm — cả ca thư mục trống lẫn ca có khoá mồ côi sẵn.
Ngoại tuyến."""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SS = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"

_CON = r'''
import importlib.util, sys, time
from pathlib import Path
spec = importlib.util.spec_from_file_location("ss_con", sys.argv[1])
m = importlib.util.module_from_spec(spec); sys.modules["ss_con"] = m; spec.loader.exec_module(m)
m._khoa_path = lambda: Path(sys.argv[2])
moc = float(sys.argv[3])
while time.time() < moc:
    pass
ok, _ = m.gianh_khoa()
print("OK" if ok else "NO")
'''


def _nap():
    spec = importlib.util.spec_from_file_location("ss_khoa_t", SS)
    m = importlib.util.module_from_spec(spec)
    sys.modules["ss_khoa_t"] = m
    spec.loader.exec_module(m)
    return m


def _mot_vong(tmp_path: Path, n: int, vong: int, mo_coi: bool = False) -> int:
    khoa = tmp_path / f"vong{vong}" / ".quet.lock"
    khoa.parent.mkdir()
    if mo_coi:
        khoa.write_text(json.dumps({"pid": 1, "may": "x", "luc": time.time() - 7200}), encoding="utf-8", newline="\n")
    moc = time.time() + 2.0
    ps = [subprocess.Popen([sys.executable, "-c", _CON, str(SS), str(khoa), str(moc)], stdout=subprocess.PIPE, text=True)
          for _ in range(n)]
    ra = [p.communicate(timeout=60)[0].strip() for p in ps]
    return ra.count("OK")


def test_nhieu_tien_trinh_cung_gianh_chi_mot_duoc(tmp_path):
    so_duoc = [_mot_vong(tmp_path, 6, v) for v in range(3)]
    assert so_duoc == [1, 1, 1], f"số tiến trình giành được khoá mỗi vòng: {so_duoc} (phải đúng 1)"


def test_nhieu_tien_trinh_cung_thay_khoa_mo_coi_chi_mot_duoc(tmp_path):
    so_duoc = [_mot_vong(tmp_path, 6, v, mo_coi=True) for v in range(3)]
    assert so_duoc == [1, 1, 1], f"số tiến trình cùng thay khoá mồ côi mỗi vòng: {so_duoc} (phải đúng 1)"


@pytest.fixture()
def ss(tmp_path, monkeypatch):
    m = _nap()
    monkeypatch.setattr(m, "_khoa_path", lambda: tmp_path / ".quet.lock")
    return m


def test_khoa_tuoi_thi_khong_gianh_duoc(ss, tmp_path):
    (tmp_path / ".quet.lock").write_text(json.dumps({"pid": 1, "may": "mac", "luc": time.time()}), encoding="utf-8",
                                         newline="\n")
    ok, ly = ss.gianh_khoa()
    assert ok is False and "đang quét" in ly


def test_khoa_mo_coi_thi_thay_va_ghi_chu_moi(ss, tmp_path):
    k = tmp_path / ".quet.lock"
    k.write_text(json.dumps({"pid": 1, "may": "mac", "luc": time.time() - 3600}), encoding="utf-8", newline="\n")
    ok, _ = ss.gianh_khoa()
    assert ok is True and json.loads(k.read_text(encoding="utf-8"))["pid"] == os.getpid()


def test_khoa_hong_dinh_dang_coi_nhu_mo_coi(ss, tmp_path):
    (tmp_path / ".quet.lock").write_text("{hỏng", encoding="utf-8", newline="\n")
    assert ss.gianh_khoa()[0] is True


def test_nha_roi_gianh_lai_duoc_va_lan_hai_bi_chan(ss, tmp_path):
    assert ss.gianh_khoa()[0] is True
    assert ss.gianh_khoa()[0] is False, "tiến trình thứ hai (cùng lúc) phải bị chặn"
    ss.tra_khoa()
    assert not (tmp_path / ".quet.lock").exists() and ss.gianh_khoa()[0] is True


def test_ma_nguon_dung_tao_nguyen_tu():
    """Khớp trên CÂY CÚ PHÁP (docstring có nhắc «O_EXCL» nên khớp chuỗi cả tệp sẽ xanh giả)."""
    cay = ast.parse(SS.read_text(encoding="utf-8"))
    ham = {n.name: n for n in cay.body if isinstance(n, ast.FunctionDef)}
    than = ham["_gianh_trong_mutex"]
    assert any(isinstance(n, ast.Attribute) and n.attr == "O_EXCL" for n in ast.walk(than)), "mất tạo nguyên tử O_EXCL"
    assert any(isinstance(n, ast.With) and any(isinstance(w.context_expr, ast.Call) and getattr(w.context_expr.func, "id", "")
                                               == "_mutex_khoa" for w in n.items) for n in ast.walk(than)), \
        "thủ tục đọc–gỡ–tạo khoá không còn nằm trong mutex hệ điều hành"
    assert not any(isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "write_text" for n in ast.walk(than)), \
        "quay lại kiểm-rồi-ghi bằng write_text"
    assert any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_gianh_trong_mutex" for n in ast.walk(ham["gianh_khoa"]))
