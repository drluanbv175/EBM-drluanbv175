#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test cho câu 'trạm web hội' trong tuyen_bo_do_phu.tra_khoi() (vá 13/09/2026).

Vì sao có: câu này trước đây hardcode "CHƯA CHẠY (chờ phê duyệt egress)" cho
MỌI lần sinh báo cáo — kể cả sau khi nhiều trạm html-watch (GOLD/GINA/KDIGO/
ADA/ESC/ACC-AHA) đã chạy thật qua kênh Browser (--nap-van-ban). Test này khoá
hành vi ĐÚNG: câu phải tính từ last_success_at thật, không phải chuỗi cố định."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("tbdp_test_mod", ROOT / "tools" / "tuyen_bo_do_phu.py")
assert SPEC and SPEC.loader
T = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = T
SPEC.loader.exec_module(T)


def _nguon(sid: str, access: str = "html-watch", status: str = "active",
           last_success_at: str | None = None, org: str = "X",
           name: str = "Nguồn X — web hội") -> dict:
    return {"id": sid, "org": org, "name": name, "access": access,
            "status": status, "last_success_at": last_success_at}


def _don_dep(monkeypatch, tmp_path: Path, sources: list[dict]) -> None:
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "sources.json").write_text(
        json.dumps({"updated": "2026-09-13", "sources": sources}), encoding="utf-8")
    monkeypatch.setattr(T, "GOC", tmp_path)


def test_tram_web_hoi_da_chay_het_khong_con_noi_cho_phe_duyet(monkeypatch, tmp_path: Path) -> None:
    """Mọi trạm html-watch đều có last_success_at ⇒ câu phải nói ĐÃ CHẠY, không
    còn được phép in cụm cố định cũ 'chờ phê duyệt egress'."""
    _don_dep(monkeypatch, tmp_path, [
        _nguon("SRC-A", last_success_at="2026-09-13"),
        _nguon("SRC-B", last_success_at="2026-09-13"),
    ])
    khoi = T.tra_khoi()
    dong_do_tre = next(d for d in khoi.splitlines() if d.startswith("Độ trễ đo được"))
    assert "2/2 đã chạy thật qua kênh Browser" in dong_do_tre
    assert "chờ phê duyệt egress" not in dong_do_tre
    assert "CHƯA CHẠY" not in dong_do_tre


def test_tram_web_hoi_con_mot_phan_chua_chay_neu_dung_ten(monkeypatch, tmp_path: Path) -> None:
    """Còn trạm chưa chạy thì phải liệt kê ĐÚNG tên trạm đó (không phải chuỗi
    'nhiều' lấy nhầm từ trường org khi org là nhãn gộp nhiều tổ chức)."""
    _don_dep(monkeypatch, tmp_path, [
        _nguon("SRC-A", last_success_at="2026-09-13"),
        _nguon("SRC-B", last_success_at=None, org="nhiều",
               name="IDSA · AGS Beers · USPSTF web · WHO web · NICE web"),
    ])
    khoi = T.tra_khoi()
    assert "1/2 đã chạy thật qua kênh Browser" in khoi
    assert "còn 1 trạm CHƯA CHẠY" in khoi
    assert "IDSA" in khoi
    assert "(nhiều)" not in khoi


def test_khong_co_tram_web_hoi_nao_khong_bien_thanh_chuoi_cam(monkeypatch, tmp_path: Path) -> None:
    """Sổ nguồn rỗng access=html-watch: không được crash, không được bịa số."""
    _don_dep(monkeypatch, tmp_path, [_nguon("SRC-A", access="api", last_success_at="2026-09-13")])
    khoi = T.tra_khoi()
    assert "CHƯA CÓ TRẠM NÀO KHAI TRONG SỔ NGUỒN" in khoi
