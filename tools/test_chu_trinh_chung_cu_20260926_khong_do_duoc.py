#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #28 (đợt dò nâng cấp 26/09/2026): còi rút bài GIẢ trên bản sao trần.

Tái hiện gốc: trên bản sao trần (không EBM-Dashboards) `so_xac_minh_nguon.py --vong 2` in «✗ Không thấy
dashboard nào khớp.» rồi thoát 2 — trùng mã «có nguồn ĐÃ BỊ RÚT» — nên `chu_trinh_chung_cu` in
«🔴 CÓ NGUỒN RÚT BỎ HẲN đang được trích» dù không nguồn nào được đọc. `--bao-cao` thì in «Sổ trống» (mã 1).

Nay: hai ca «không đo được» trả mã 3 + dòng ⚪; chu_trinh xử lý mã 3 (và chuỗi của bản cũ) TRƯỚC mã 2,
BẮT BUỘC thêm một việc ⚪ (không bao giờ 🟢), mã tổng giữ 1. Mã 2 thật vẫn ra 🔴.
Ngoại tuyến: công cụ thật chạy trong cây thư mục tạm; chu_trinh dùng subprocess giả nạp đầu ra đó.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import chu_trinh_chung_cu as ctcc  # noqa: E402


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


# ── 1. so_xac_minh_nguon: mã 3 cho «không đo được» (chạy THẬT như chu_trinh gọi) ─────────────────────────
def _cay_tran(tmp: Path) -> Path:
    (tmp / "tools").mkdir()
    for ten in ("so_xac_minh_nguon.py", "ban_sao_tran.py"):
        shutil.copy(ROOT / "tools" / ten, tmp / "tools" / ten)
    return tmp


def _chay_that(tmp: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-B", "tools/so_xac_minh_nguon.py", *args], cwd=str(tmp),
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
                       env={**os.environ, "_EBM_DA_CHUYEN_VENV": "1", "PYTHONUTF8": "1"})
    return p.returncode, (p.stdout or "") + (p.stderr or "")


@pytest.fixture()
def dau_ra_that(tmp_path):
    goc = _cay_tran(tmp_path)
    return {"quet": _chay_that(goc, "--vong", "2"), "bao_cao": _chay_that(goc, "--bao-cao")}


def test_ban_sao_tran_quet_tra_3_khong_phai_2(dau_ra_that):
    rc, out = dau_ra_that["quet"]
    assert rc == 3, out
    assert "⚪ KHÔNG ĐO ĐƯỢC" in out and "KHONG_DO_DUOC" in out


def test_ban_sao_tran_bao_cao_tra_3(dau_ra_that):
    rc, out = dau_ra_that["bao_cao"]
    assert rc == 3, out
    assert "⚪ KHÔNG ĐO ĐƯỢC" in out


def test_so_co_nhung_rong_van_la_so_trong_ma_1(tmp_path, monkeypatch):
    so = _nap("so_kdd_20260926", ROOT / "tools" / "so_xac_minh_nguon.py")
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    (dash / ".so-xac-minh-nguon.json").write_text(json.dumps({"phien_ban": 1, "muc": {}}), encoding="utf-8")
    monkeypatch.setattr(so, "SO", dash / ".so-xac-minh-nguon.json")
    assert so.bao_cao() == 1


# ── 2. chu_trinh: ⚪ chứ không 🔴, không 🟢 ──────────────────────────────────────────────────────────────
class _P:
    def __init__(self, rc, out):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def _chay_chu_trinh(rc_so: int, out_so: str, nhanh: bool, capsys) -> tuple[int, str]:
    def _goi(cmd, **kw):
        if "so_xac_minh_nguon.py" in str(cmd[1]):
            return _P(rc_so, out_so)
        return _P(0, "")
    argv = ["chu_trinh_chung_cu.py"] + (["--nhanh"] if nhanh else [])
    with mock.patch.object(sys, "argv", argv), mock.patch.object(ctcc.subprocess, "run", side_effect=_goi):
        rc = ctcc.main()
    return rc, capsys.readouterr().out


def test_dau_ra_that_cua_ban_sao_tran_ra_trang_khong_ra_do(dau_ra_that, capsys):
    for khoa, nhanh in (("quet", False), ("bao_cao", True)):
        rc_so, out_so = dau_ra_that[khoa]
        rc, out = _chay_chu_trinh(rc_so, out_so, nhanh, capsys)
        assert "CÓ NGUỒN RÚT BỎ HẲN" not in out, khoa
        assert "⚪ Chưa đo được xác minh nguồn/rút bài" in out, khoa
        assert "🟢 Mọi chốt đạt" not in out, khoa
        assert rc == 1, khoa


@pytest.mark.parametrize("rc_so,out_so,nhanh", [
    (2, "✗ Không thấy dashboard nào khớp.", False),     # bản so_xac_minh_nguon CŨ
    (1, "Sổ trống — chạy --quet trước.", True),          # --nhanh, sổ rỗng/vắng kiểu cũ
    (3, "", False),                                       # chỉ có mã thoát
])
def test_cac_dang_khong_do_duoc_deu_ra_trang(rc_so, out_so, nhanh, capsys):
    rc, out = _chay_chu_trinh(rc_so, out_so, nhanh, capsys)
    assert "⚪ Chưa đo được xác minh nguồn/rút bài" in out
    assert "CÓ NGUỒN RÚT BỎ HẲN" not in out and "🟢 Mọi chốt đạt" not in out
    assert rc == 1


def test_ma_2_that_van_ra_do(capsys):
    out_that = "  🔴 NGUỒN ĐÃ BỊ RÚT — không dùng kết luận của các bài này:\n     • pmid:9500320 [retracted]"
    rc, out = _chay_chu_trinh(2, out_that, False, capsys)
    assert "🔴 CÓ NGUỒN RÚT BỎ HẲN" in out
    assert "⚪ Chưa đo được xác minh nguồn/rút bài" not in out
    assert rc == 1


def test_ma_la_khong_roi_im_lang_thanh_xanh(capsys):
    rc, out = _chay_chu_trinh(137, "", False, capsys)
    assert "thoát mã lạ (137)" in out and "🟢 Mọi chốt đạt" not in out and rc == 1
