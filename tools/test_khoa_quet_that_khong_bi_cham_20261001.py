"""Chốt BH47 và canary đầu–cuối KHÔNG được giành/xoá khoá quét THẬT (01/10/2026) — ngoại tuyến.

Khoá thật là `EBM-Dashboards/.quet.lock`, tệp OneDrive đồng bộ sang máy kia; `tra_khoa()` xoá nó KHÔNG hỏi chủ. Trước bản vá,
`bh47_quet_phai_co_khoa_cursor_va_alert()` và `thu_dau_cuoi_chung_cu.main()` đều gọi `gianh_khoa()` hai lần rồi `tra_khoa()`
trên khoá thật: (a) lượt quét thật đang giữ khoá ⇒ lần 1 không giành được ⇒ ✗ «khoá không chặn tiến trình thứ hai» GIẢ (đã đỏ
nhất thời trên cây thật 01/10), và (b) `tra_khoa()` nhả MẤT khoá của lượt quét thật ⇒ hai lượt cùng ghi sổ. Các ca dưới dựng một
cây giả có sẵn «khoá của lượt quét thật đang chạy» và khẳng định nó còn nguyên sau khi chốt/canary chạy.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import socket
import sys
import time
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parent
_REPO = _TOOLS.parent
_SS_CHUAN = _REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"


def _nap(duong: Path, ten: str):
    spec = importlib.util.spec_from_file_location(ten, duong)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod                       # đăng ký TRƯỚC khi exec (dataclass cần)
    spec.loader.exec_module(mod)
    return mod


C = _nap(_TOOLS / "chot_hoi_quy_bai_hoc.py", "chot_bh142_khoa")
T = _nap(_TOOLS / "thu_dau_cuoi_chung_cu.py", "canary_bh142_khoa")


def _cay_gia(tmp_path: Path, co_khoa: bool = True):
    """tmp/EBM-Dashboards/{tools/surveillance_scan.py, watchlist.json, .quet.lock tươi của «máy khác»}."""
    dash = tmp_path / "EBM-Dashboards"
    (dash / "tools").mkdir(parents=True)
    shutil.copy(_SS_CHUAN, dash / "tools" / "surveillance_scan.py")
    (dash / "watchlist.json").write_text('{"topics": []}', encoding="utf-8")
    khoa = dash / ".quet.lock"
    if co_khoa:
        khoa.write_text(json.dumps({"pid": 4242, "may": "may-khac", "luc": time.time()}), encoding="utf-8")
    return dash, khoa


def test_doi_chung_khoa_gia_dung_la_khoa_dang_song(tmp_path):
    """Nếu khoá giả không được coi là «đang giữ» thì mọi ca dưới đây vô nghĩa — gọi THẲNG phải bị từ chối và không đổi tệp."""
    dash, khoa = _cay_gia(tmp_path)
    ss = _nap(dash / "tools" / "surveillance_scan.py", "ss_bh142_doi_chung")
    truoc = khoa.read_bytes()
    ok, ly = ss.gianh_khoa()
    assert ok is False and "may-khac" in ly
    assert khoa.read_bytes() == truoc


def test_bh47_khong_cham_khoa_that_dang_duoc_giu(monkeypatch, tmp_path):
    dash, khoa = _cay_gia(tmp_path)
    truoc = khoa.read_bytes()
    monkeypatch.setattr(C, "REPO", tmp_path)
    ok, chi_tiet = C.bh47_quet_phai_co_khoa_cursor_va_alert()
    assert ok is True, f"chốt đỏ giả khi một lượt quét thật đang giữ khoá: {chi_tiet}"
    assert khoa.exists() and khoa.read_bytes() == truoc, "chốt đã xoá/ghi đè KHOÁ THẬT của lượt quét đang chạy"


def test_bh47_khong_tao_khoa_that_khi_chua_co(monkeypatch, tmp_path):
    dash, khoa = _cay_gia(tmp_path, co_khoa=False)
    monkeypatch.setattr(C, "REPO", tmp_path)
    ok, chi_tiet = C.bh47_quet_phai_co_khoa_cursor_va_alert()
    assert ok is True, chi_tiet
    assert not khoa.exists(), "chốt để lại/ tạo khoá THẬT — có thể chặn lượt quét thật bên máy kia qua OneDrive"


def test_bh47_khong_goi_mang_that(monkeypatch, tmp_path):
    """Gốc thứ hai của lần đỏ nhất thời 01/10: phản hồi NCBI giả thiếu `count` bị `search()` coi là LỖI và lùi sang Europe PMC
    bằng mạng thật — xanh khi mạng sống, đỏ («getaddrinfo failed») khi DNS trượt. Chặn mạng: BH47 phải vẫn xanh."""
    _cay_gia(tmp_path, co_khoa=False)
    monkeypatch.setattr(C, "REPO", tmp_path)

    def _no(*_a, **_k):
        raise AssertionError("chạm MẠNG THẬT")

    monkeypatch.setattr(socket, "getaddrinfo", _no)
    monkeypatch.setattr(socket, "create_connection", _no)
    ok, chi_tiet = C.bh47_quet_phai_co_khoa_cursor_va_alert()
    assert ok is True, chi_tiet


def test_canary_thu_khoa_co_lap_khong_cham_khoa_that(tmp_path):
    dash, khoa = _cay_gia(tmp_path)
    ss = _nap(dash / "tools" / "surveillance_scan.py", "ss_bh142_canary")
    truoc, wl_goc = khoa.read_bytes(), ss.DEFAULT_WATCHLIST
    canary = tmp_path / "canary"
    canary.mkdir()
    assert T.thu_khoa_quet_co_lap(ss, canary) == (True, False), "đúng thiết kế: lần 1 giành được, lần 2 bị chặn"
    assert khoa.exists() and khoa.read_bytes() == truoc, "canary đã xoá/ghi đè KHOÁ THẬT"
    assert ss.DEFAULT_WATCHLIST == wl_goc, "canary không trả DEFAULT_WATCHLIST về nguyên trạng"
    assert not (canary / ".quet.lock").exists(), "khoá tạm của canary phải được trả"


def test_canary_tra_default_watchlist_ke_ca_khi_gianh_khoa_no_loi(tmp_path):
    dash, khoa = _cay_gia(tmp_path)
    ss = _nap(dash / "tools" / "surveillance_scan.py", "ss_bh142_loi")
    wl_goc = ss.DEFAULT_WATCHLIST

    def _no(*_a, **_k):
        raise OSError("giả lập: ổ đĩa lỗi")

    ss.gianh_khoa = _no
    with pytest.raises(OSError):
        T.thu_khoa_quet_co_lap(ss, tmp_path)
    assert ss.DEFAULT_WATCHLIST == wl_goc, "lỗi giữa chừng làm mất việc trả DEFAULT_WATCHLIST — các bước sau chạy trên khoá tạm"


def test_chot_bh142_xanh_tren_ma_song():
    assert C.bh142_chot_va_canary_khong_cham_khoa_quet_that() == (True, "")
