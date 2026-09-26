"""Giác quan lịch nền của `tu_de_xuat_viec.py` phân biệt Cloud / máy thật — 26/09/2026.

Trên Cloud, log thu thập tuần vắng mặt là «không đo được» (⚪), không phải 🔴 «chưa từng chạy».
Ngoại tuyến, chỉ dùng tệp tạm.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_lich", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)


@pytest.fixture(autouse=True)
def _sach():
    M._GIAC_QUAN_CHET.clear()


def test_cloud_vang_log_la_khong_do_duoc(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    assert M.giac_quan_lich_nen_theo_noi_chay(tmp_path / "vang.log") == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "Cloud" in M._GIAC_QUAN_CHET[0]


@pytest.mark.parametrize("gia_tri", [None, "", "false"])
def test_may_that_vang_log_van_do(monkeypatch, tmp_path, gia_tri):
    if gia_tri is None:
        monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    else:
        monkeypatch.setenv("CLAUDE_CODE_REMOTE", gia_tri)
    kq = M.giac_quan_lich_nen_theo_noi_chay(tmp_path / "vang.log")
    assert kq and kq[0][0] == 0 and "KHÔNG ĐỌC ĐƯỢC" in kq[0][1]
    assert M._GIAC_QUAN_CHET == []


def test_cloud_co_log_thi_van_cham_binh_thuong(monkeypatch, tmp_path):
    """Có tệp log (vd kéo về từ máy thật) thì Cloud vẫn chấm tuổi lượt PASS như máy thật."""
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    log = tmp_path / "tuan.log"
    cu = (dt.date.today() - dt.timedelta(days=30)).isoformat()
    log.write_text(f"{cu} 18:00 KẾT THÚC lượt tuần tổng thể=PASS\n", encoding="utf-8", newline="\n")
    kq = M.giac_quan_lich_nen_theo_noi_chay(log)
    assert kq and "quá hạn 30 ngày" in kq[0][1] and M._GIAC_QUAN_CHET == []
