#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test NGOẠI TUYẾN cho luật bất đối xứng khi gộp trạng thái rút bài (14/09/2026).

Vì sao có: khảo sát qua workflow kiểm tra toàn diện phát hiện CẢ HAI đường tra
rút bài trong so_xac_minh_nguon.py (PMID trong lenh_quet() và DOI trong
kiem_rut_bai_theo_doi()) dùng BLACKLIST MỞ — chỉ loại trừ đúng vài chuỗi trạng
thái đã biết là "chưa kiểm" — nên một trạng thái LẠ (module RetractionChain/
CrossrefRetraction thêm loại lỗi mới, hoặc info thiếu hẳn khoá "status") lọt
xuống và bị ghi kiem_rut_luc coi như ĐÃ KIỂM XONG, dù không khớp nhánh if/elif
nào xử lý nội dung thật. Đây là đúng luật bất đối xứng ("không biết" bị báo
thành "có vấn đề" — ở đây ngược lại: "không biết" bị báo thành "sạch") mà
chính module này (và BH27/BH33 của dự án) sinh ra để chống. File này KHÔNG
tồn tại trước khi phát hiện — chưa có test nào che phủ hai đường này."""
from __future__ import annotations

import datetime as dt
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sxmn_test_mod", ROOT / "tools" / "so_xac_minh_nguon.py")
assert SPEC and SPEC.loader
S = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = S
SPEC.loader.exec_module(S)


def test_lenh_quet_khong_coi_trang_thai_pmid_la_da_kiem(monkeypatch) -> None:
    """Vá 14/09/2026: một trạng thái PMID LẠ (chưa từng liệt kê) từ kiem_rut_bai()
    không được ghi kiem_rut_luc/ghi_chu_rut — whitelist đóng thay blacklist mở.
    Cô lập ĐÚNG đoạn "kiểm rút bài cho PMID" trong lenh_quet() bằng cách monkeypatch
    mọi bước trước đó thành no-op (khớp cách đã verify phát hiện này bằng chạy thật)."""
    khoa = "pmid:99999"
    muc = {khoa: {"loai": "pmid", "gia_tri": "99999", "cac_dashboard": ["x.html"]}}
    so = {"muc": muc}

    monkeypatch.setattr(S, "doc_so", lambda: so)
    monkeypatch.setattr(S, "ghi_so", lambda s: None)
    monkeypatch.setattr(S, "_nap_verify_dashboard", lambda: None)
    monkeypatch.setattr(S, "gom_nguon", lambda files, vd: {khoa: {"x.html"}})
    monkeypatch.setattr(S, "dong_bo_lien_ket_dashboard", lambda muc, nguon, ten: 0)
    monkeypatch.setattr(S, "con_hieu_luc", lambda bg: (True, ""))
    monkeypatch.setattr(S, "kiem_rut_bai_theo_doi", lambda muc, nguon, so: None)
    monkeypatch.setattr(S, "kiem_rut_bai", lambda pmids: {"99999": {"status": "unknown_dns_timeout"}})

    S.lenh_quet([], vong=1)

    assert "kiem_rut_luc" not in muc[khoa]
    assert "ghi_chu_rut" not in muc[khoa]
    assert muc[khoa].get("da_rut") is not True


def test_lenh_quet_pmid_thieu_khoa_status_khong_coi_la_da_kiem(monkeypatch) -> None:
    """Cùng lỗi, dạng khác: info thiếu hẳn khoá "status" (→ chuỗi rỗng qua .get)
    cũng không được coi là đã kiểm — không cần một enum lạ mới bắt được lỗi này."""
    khoa = "pmid:77777"
    muc = {khoa: {"loai": "pmid", "gia_tri": "77777", "cac_dashboard": ["x.html"]}}
    so = {"muc": muc}

    monkeypatch.setattr(S, "doc_so", lambda: so)
    monkeypatch.setattr(S, "ghi_so", lambda s: None)
    monkeypatch.setattr(S, "_nap_verify_dashboard", lambda: None)
    monkeypatch.setattr(S, "gom_nguon", lambda files, vd: {khoa: {"x.html"}})
    monkeypatch.setattr(S, "dong_bo_lien_ket_dashboard", lambda muc, nguon, ten: 0)
    monkeypatch.setattr(S, "con_hieu_luc", lambda bg: (True, ""))
    monkeypatch.setattr(S, "kiem_rut_bai_theo_doi", lambda muc, nguon, so: None)
    monkeypatch.setattr(S, "kiem_rut_bai", lambda pmids: {"77777": {}})

    S.lenh_quet([], vong=1)

    assert "kiem_rut_luc" not in muc[khoa]


def test_lenh_quet_pmid_trang_thai_da_biet_van_ghi_dung(monkeypatch) -> None:
    """Đối chứng: 4 trạng thái ĐÃ BIẾT (ok/retracted/expression_of_concern/
    unresolved) vẫn phải được ghi kiem_rut_luc như cũ — vá whitelist không được
    làm rớt các ca hợp lệ."""
    muc = {
        "pmid:1": {"loai": "pmid", "gia_tri": "1", "cac_dashboard": ["x.html"]},
        "pmid:2": {"loai": "pmid", "gia_tri": "2", "cac_dashboard": ["x.html"]},
        "pmid:3": {"loai": "pmid", "gia_tri": "3", "cac_dashboard": ["x.html"]},
        "pmid:4": {"loai": "pmid", "gia_tri": "4", "cac_dashboard": ["x.html"]},
    }
    so = {"muc": muc}
    ket_qua = {
        "1": {"status": "ok"},
        "2": {"status": "retracted"},
        "3": {"status": "expression_of_concern"},
        "4": {"status": "unresolved"},
    }

    monkeypatch.setattr(S, "doc_so", lambda: so)
    monkeypatch.setattr(S, "ghi_so", lambda s: None)
    monkeypatch.setattr(S, "_nap_verify_dashboard", lambda: None)
    monkeypatch.setattr(S, "gom_nguon", lambda files, vd: {k: {"x.html"} for k in muc})
    monkeypatch.setattr(S, "dong_bo_lien_ket_dashboard", lambda muc, nguon, ten: 0)
    monkeypatch.setattr(S, "con_hieu_luc", lambda bg: (True, ""))
    monkeypatch.setattr(S, "kiem_rut_bai_theo_doi", lambda muc, nguon, so: None)
    monkeypatch.setattr(S, "kiem_rut_bai", lambda pmids: ket_qua)

    S.lenh_quet([], vong=1)

    assert all("kiem_rut_luc" in muc[k] for k in muc)
    assert muc["pmid:2"]["da_rut"] is True
    assert muc["pmid:3"]["quan_ngai"] is True
    assert muc["pmid:4"]["nghi_ma"] is True


def test_kiem_rut_bai_theo_doi_khong_coi_trang_thai_la_da_kiem(monkeypatch) -> None:
    """Vá 14/09/2026: cùng lỗi ở đường DOI — trạng thái Crossref LẠ không được
    ghi kiem_rut_luc. Mock thẳng module app.sources.crossref_retraction trong
    sys.modules để không cần cây medical-ebm-automation/ tồn tại."""
    import types

    fake_pkg = types.ModuleType("app")
    fake_sources = types.ModuleType("app.sources")
    fake_mod = types.ModuleType("app.sources.crossref_retraction")

    class _FakeCrossrefRetraction:
        def __init__(self, mailto=""):
            pass

        def check(self, dois):
            return {d: {"status": "unknown_rate_limited"} for d in dois}

    fake_mod.CrossrefRetraction = _FakeCrossrefRetraction
    monkeypatch.setitem(sys.modules, "app", fake_pkg)
    monkeypatch.setitem(sys.modules, "app.sources", fake_sources)
    monkeypatch.setitem(sys.modules, "app.sources.crossref_retraction", fake_mod)

    mea = S.REPO / "medical-ebm-automation"
    monkeypatch.setattr(
        type(mea), "exists",
        lambda self: True if str(self).endswith("crossref_retraction.py") else Path.exists(self),
        raising=False,
    )

    monkeypatch.setattr(S, "ghi_so", lambda s: None)

    khoa = "doi:10.1/x"
    muc = {khoa: {"loai": "doi", "gia_tri": "10.1/x"}}
    nguon = {khoa: {"x.html"}}
    so = {"muc": muc}

    S.kiem_rut_bai_theo_doi(muc, nguon, so)

    assert "kiem_rut_luc" not in muc[khoa]
    assert "ghi_chu_rut" not in muc[khoa]


def test_kiem_rut_bai_theo_doi_trang_thai_da_biet_van_ghi_dung(monkeypatch) -> None:
    """Đối chứng: DOI với status="retracted" vẫn phải được ghi nhận đúng."""
    import types

    fake_pkg = types.ModuleType("app")
    fake_sources = types.ModuleType("app.sources")
    fake_mod = types.ModuleType("app.sources.crossref_retraction")

    class _FakeCrossrefRetraction:
        def __init__(self, mailto=""):
            pass

        def check(self, dois):
            return {d: {"status": "retracted", "retract_and_replace": False} for d in dois}

    fake_mod.CrossrefRetraction = _FakeCrossrefRetraction
    monkeypatch.setitem(sys.modules, "app", fake_pkg)
    monkeypatch.setitem(sys.modules, "app.sources", fake_sources)
    monkeypatch.setitem(sys.modules, "app.sources.crossref_retraction", fake_mod)

    mea = S.REPO / "medical-ebm-automation"
    monkeypatch.setattr(
        type(mea), "exists",
        lambda self: True if str(self).endswith("crossref_retraction.py") else Path.exists(self),
        raising=False,
    )

    monkeypatch.setattr(S, "ghi_so", lambda s: None)

    khoa = "doi:10.1/y"
    muc = {khoa: {"loai": "doi", "gia_tri": "10.1/y"}}
    nguon = {khoa: {"x.html"}}
    so = {"muc": muc}

    S.kiem_rut_bai_theo_doi(muc, nguon, so)

    assert muc[khoa]["da_rut"] is True
    assert "kiem_rut_luc" in muc[khoa]
