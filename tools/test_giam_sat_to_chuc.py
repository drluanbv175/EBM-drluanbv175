#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test NGOẠI TUYẾN cho chế độ dò/bật trạm của giam_sat_to_chuc (29/08/2026).

Vì sao có: trạm hội «dựng xong nằm chờ» từ 15/08 vì không ai xác minh sống được
URL; hai chế độ --kiem-tra/--bat-neu-ok là đường kích hoạt một-lệnh trên máy
thật. Test này khoá hợp đồng của chúng bằng fixture — không gọi mạng."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gstc_test_mod", ROOT / "tools" / "giam_sat_to_chuc.py")
assert SPEC and SPEC.loader
G = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = G
SPEC.loader.exec_module(G)

HTML_CO_TIEU_DE = "<html><h2>GOLD Report 2026 — Global Strategy</h2><a href=/x>Pocket Guide 2026</a></html>"
HTML_KHONG_TIEU_DE = "<html><p>chỉ văn xuôi giới thiệu hội, không mục lục</p></html>"


def _nguon(sid: str, status: str = "not-covered", url: str | None = "https://vi.du/x") -> dict:
    return {"id": sid, "org": "X", "domain": ["d"], "access": "html-watch",
            "endpoint_or_url": url, "status": status}


def test_kiem_tra_phan_biet_ba_ket_cuc(monkeypatch) -> None:
    """fetch hỏng ✗ · fetch OK nhưng 0 tiêu đề ✗ (kèm lý do) · có tiêu đề ✓."""
    noi_dung = {"https://vi.du/hong": None,
                "https://vi.du/rong": HTML_KHONG_TIEU_DE,
                "https://vi.du/tot": HTML_CO_TIEU_DE}
    monkeypatch.setattr(G, "_fetch", lambda url: noi_dung[url])
    kq = G.kiem_tra_tram([_nguon("A", url="https://vi.du/hong"),
                          _nguon("B", url="https://vi.du/rong"),
                          _nguon("C", url="https://vi.du/tot")])
    assert kq["A"]["ok"] is False and "fetch hỏng" in kq["A"]["ly_do"]
    assert kq["B"]["ok"] is False and "0 tiêu đề" in kq["B"]["ly_do"]
    assert kq["C"]["ok"] is True and kq["C"]["so_tieu_de"] >= 1


def test_kiem_tra_bo_qua_nguon_khong_phai_tram(monkeypatch) -> None:
    """Nguồn access=api/manual hoặc thiếu endpoint KHÔNG được dò — tránh gọi mạng thừa."""
    monkeypatch.setattr(G, "_fetch", lambda url: HTML_CO_TIEU_DE)
    kq = G.kiem_tra_tram([
        {"id": "API", "access": "api", "endpoint_or_url": "https://vi.du", "status": "active"},
        _nguon("THIEU-URL", url=None),
        _nguon("TRAM"),
    ])
    assert set(kq) == {"TRAM"}


def test_bat_neu_ok_chi_bat_tram_dat_va_dang_not_covered() -> None:
    """Chỉ trạm dò ĐẠT + đang not-covered mới bật; trạm active sẵn và trạm dò
    trượt giữ nguyên — bật trạm trượt là ghi «active» suông, đúng thứ sổ cấm."""
    du = {"sources": [_nguon("DAT"), _nguon("TRUOT"),
                       _nguon("DA-BAT", status="active")]}
    kq = {"DAT": {"ok": True, "so_tieu_de": 3, "ly_do": None},
          "TRUOT": {"ok": False, "so_tieu_de": 0, "ly_do": "fetch hỏng"},
          "DA-BAT": {"ok": True, "so_tieu_de": 2, "ly_do": None}}
    bat = G.bat_neu_ok(du, kq)
    assert bat == ["DAT"]
    trang_thai = {s["id"]: s["status"] for s in du["sources"]}
    assert trang_thai == {"DAT": "active", "TRUOT": "not-covered", "DA-BAT": "active"}
    dat = next(s for s in du["sources"] if s["id"] == "DAT")
    assert dat["kich_hoat"]["so_tieu_de_luc_do"] == 3
    assert "DA-BAT" not in [s["id"] for s in du["sources"] if "kich_hoat" in s]


def test_bat_neu_ok_khong_ghi_dia() -> None:
    """bat_neu_ok là hàm THUẦN sửa dict — caller sao lưu rồi mới ghi; hàm tự ghi
    đĩa sẽ vòng qua bước sao lưu."""
    import inspect
    nguon = inspect.getsource(G.bat_neu_ok)
    assert "write_text" not in nguon and "open(" not in nguon
