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
         "owner": "agent-A2", "status": "active", "endpoint_or_url": "https://vi.du/api"},
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


def test_bat_active_khong_co_endpoint():
    """Vá 14/09/2026 (workflow kiểm tra toàn diện): status=active mà
    endpoint_or_url rỗng hoàn toàn — 'đang hoạt động' để quét cái gì? — trước
    bản vá lọt qua sạch (đo trên bản sao data/sources.json thật: cấy SRC-004
    active + xoá endpoint vẫn '🟢 Hợp lệ')."""
    du = {**TOT, "sources": [{**TOT["sources"][0], "endpoint_or_url": None}]}
    loi = K.kiem(du)
    assert any("status=active" in l and "endpoint_or_url rỗng" in l for l in loi)


def test_bat_not_covered_khong_endpoint_khong_known_gap():
    """Vá 14/09/2026: not-covered KHÔNG endpoint LẪN không known_gap (hoàn
    toàn không giải thích vì sao chưa phủ) — luật cũ chỉ bắt ca 'có endpoint
    mà thiếu known_gap', ca này lọt qua sạch (đo trên bản sao SRC-020 thật:
    known_gap=null + endpoint=null vẫn '🟢 Hợp lệ')."""
    du = {**TOT, "sources": [{**TOT["sources"][0], "status": "not-covered",
                              "endpoint_or_url": None, "known_gap": None}]}
    loi = K.kiem(du)
    assert any("status=not-covered mà không có known_gap" in l for l in loi)


def test_khong_bao_dong_gia_not_covered_co_known_gap_khong_endpoint():
    """Đối chứng: not-covered không endpoint NHƯNG có known_gap giải thích rõ
    thì hợp lệ — không được nới hẹp oan ca đã đúng từ trước (vd SRC-020/021
    thật: manual, không endpoint, có known_gap)."""
    du = {**TOT, "sources": [{**TOT["sources"][0], "status": "not-covered",
                              "endpoint_or_url": None,
                              "known_gap": "thu công, chưa có API"}]}
    assert K.kiem(du) == []


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
