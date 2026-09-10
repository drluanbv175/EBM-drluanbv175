#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho kiem_hop_dong_nguon.py (vòng 2, 10/09/2026).

Bối cảnh: `contracts/sources.schema.json` khai luật cho `data/sources.json`
(19 nguồn, đang duy trì thật) nhưng trước công cụ này KHÔNG có gì đối chiếu
hai file — bắt được ngay lần chạy đầu: SRC-031 scan_frequency ngoài enum.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`): (1) kiểm HÀNH VI,
không đếm chuỗi; (2) mỗi ca gắn rủi ro THẬT; (3) nhanh, ngoại tuyến.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_hop_dong_nguon as K  # noqa: E402

TOT = {
    "updated": "2026-09-10",
    "sources": [
        {"id": "SRC-001", "name": "x", "org": "y", "tier": 1, "domain": ["d"],
         "access": "api", "scan_frequency": "weekly", "detection_method": "api-query",
         "owner": "agent-A2", "status": "active"},
    ],
}


def test_self_test_dat():
    assert K._self_test() == 0


def test_du_lieu_that_cua_repo_hop_le():
    """Đối chứng tích hợp: data/sources.json thật của repo phải sạch — nếu ai
    lỡ thêm một nguồn sai enum, test này đỏ trước khi chốt phiên đỏ."""
    data = json.loads(K.SOURCES.read_text(encoding="utf-8"))
    assert K.kiem(data) == []


def test_bat_id_sai_mau():
    du = {**TOT, "sources": [{**TOT["sources"][0], "id": "SRC-1"}]}
    loi = K.kiem(du)
    assert any("không khớp mẫu" in l for l in loi)


def test_bat_scan_frequency_ngoai_enum():
    """Đúng ca thật đã bắt được ở SRC-031 trước khi vá."""
    du = {**TOT, "sources": [{**TOT["sources"][0], "scan_frequency": "theo lượt quét A2"}]}
    loi = K.kiem(du)
    assert any("scan_frequency" in l for l in loi)


def test_bat_id_trung_lap():
    du = {**TOT, "sources": [TOT["sources"][0], TOT["sources"][0]]}
    loi = K.kiem(du)
    assert any("trùng lặp" in l for l in loi)


def test_bat_thieu_truong_bat_buoc():
    du = {**TOT, "sources": [{"id": "SRC-002"}]}
    loi = K.kiem(du)
    assert any("`name`" in l for l in loi)


def test_khong_bao_dong_gia_khi_du_lieu_dung():
    assert K.kiem(TOT) == []


def test_thieu_file_thi_ma_thoat_2(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(K, "SOURCES", tmp_path / "khong-ton-tai.json")
    monkeypatch.setattr(sys, "argv", ["kiem_hop_dong_nguon.py"])
    rc = K.main()
    assert rc == 2
    out = capsys.readouterr().out
    assert "KHÔNG phải đã hợp lệ" in out


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
