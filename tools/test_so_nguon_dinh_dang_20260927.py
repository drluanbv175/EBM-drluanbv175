"""Sổ nguồn `data/sources.json` phải được GHI đúng định dạng của bản trong git: thụt lề 2, xuống dòng LF.

Vá 27/09/2026: `sources_health.py` và `giam_sat_to_chuc.py` từng ghi thụt lề 1, trong khi MỌI commit của sổ
thụt lề 2 ⇒ mỗi lượt chạy viết lại ~830/833 dòng dù chỉ đổi vài giá trị. Bản đo trạm ngày 25/09 vì thế thành
một diff 834 dòng chưa commit, chặn việc chuyển nhánh ngày 27/09 (phải cất vào stash). Test không gọi mạng;
sổ là bản sao trong tmp.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
MAU = {"updated": "2000-01-01", "sources": [
    {"id": "SRC-004", "name": "Crossref — thử «tiếng Việt»", "status": "active", "access": "api",
     "scan_frequency": "weekly", "endpoint_or_url": "https://api.crossref.org/"},
]}


def _nap(ten_tep: str, ten_mod: str):
    spec = importlib.util.spec_from_file_location(ten_mod, GOC / "tools" / ten_tep)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten_mod] = mod
    spec.loader.exec_module(mod)
    return mod


def _dung_dinh_dang(raw: bytes) -> bool:
    text = raw.decode("utf-8")
    return b"\r" not in raw and text == json.dumps(json.loads(text), ensure_ascii=False, indent=2) + "\n"


def test_sources_health_ghi_giu_thut_le_2(monkeypatch, tmp_path):
    mod = _nap("sources_health.py", "sh_dinh_dang_test")
    so = tmp_path / "sources.json"
    so.write_text(json.dumps(MAU, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    monkeypatch.setattr(mod, "SO", so)
    monkeypatch.setattr(mod, "lay_thanh_cong_that", lambda sid: None)
    monkeypatch.setattr(mod, "la_phien_cloud", lambda: False)
    monkeypatch.setattr(mod, "la_ban_sao_tran", lambda: False)  # máy thật — bản sao trần không ghi sổ (30/09/2026)
    monkeypatch.setattr(sys, "argv", ["sources_health", "--khong-mang"])
    mod.main()
    raw = so.read_bytes()
    assert json.loads(raw)["updated"] != "2000-01-01", "công cụ phải thật sự GHI sổ — không thì test vô nghĩa"
    assert _dung_dinh_dang(raw), "sources_health ghi lệch định dạng sổ ⇒ mỗi lượt viết lại cả tệp"


def test_giam_sat_to_chuc_ghi_giu_thut_le_2(monkeypatch, tmp_path):
    mod = _nap("giam_sat_to_chuc.py", "gstc_dinh_dang_test")
    so = tmp_path / "sources.json"
    monkeypatch.setattr(mod, "SO_NGUON", so)
    mod._ghi_so_nguon(json.loads(json.dumps(MAU)))
    assert _dung_dinh_dang(so.read_bytes())


@pytest.mark.parametrize("ten_tep, ten_so", [("sources_health.py", "SO"), ("giam_sat_to_chuc.py", "SO_NGUON")])
def test_moi_lenh_ghi_so_nguon_dung_dinh_dang(ten_tep, ten_so):
    """Soi DÒNG THI HÀNH (cây cú pháp), không khớp chuỗi cả tệp: một đường ghi mới thêm sau này cũng không lọt."""
    cay = ast.parse((GOC / "tools" / ten_tep).read_text(encoding="utf-8"))
    ghi = [n for n in ast.walk(cay) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
           and n.func.attr == "write_text" and isinstance(n.func.value, ast.Name) and n.func.value.id == ten_so]
    assert ghi, f"không thấy lệnh ghi {ten_so} nào trong {ten_tep} — test đang đo nhầm chỗ"
    for n in ghi:
        dumps = [c for c in ast.walk(n) if isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "dumps"]
        assert dumps, f"{ten_tep}:{n.lineno} ghi {ten_so} không qua json.dumps"
        indent = {k.arg: getattr(k.value, "value", None) for k in dumps[0].keywords}.get("indent")
        assert indent == 2, f"{ten_tep}:{n.lineno} ghi {ten_so} với indent={indent}"
        nl = {k.arg: getattr(k.value, "value", None) for k in n.keywords}.get("newline")
        assert nl == "\n", f"{ten_tep}:{n.lineno} thiếu newline='\\n' — máy Windows sẽ ghi CRLF"


def test_so_nguon_trong_repo_dung_dinh_dang():
    assert _dung_dinh_dang((GOC / "data" / "sources.json").read_bytes()), \
        "data/sources.json lệch định dạng (thụt lề 2 + LF) — có công cụ nào vừa ghi bằng định dạng khác?"
