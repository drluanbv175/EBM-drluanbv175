#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy EV-03 (03/10/2026): ba chủ đề thẩm quyền (NICE · USPSTF · cảnh báo an toàn thuốc) trả «PASS / 0 ứng viên» 7/7 tuần mà
làn PubMed không quan sát được văn bản chính thức (mẫu 0/18) — bộ quét phải nói rõ «0 ≠ không có cập nhật» và trỏ kênh khác."""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SS = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"


def _nap():
    sp = importlib.util.spec_from_file_location("_t_ev03_ss", SS)
    m = importlib.util.module_from_spec(sp)
    sys.modules["_t_ev03_ss"] = m
    sp.loader.exec_module(m)
    return m


M = _nap()


def _tr(topic, n=0, status="PASS", error=""):
    c = [object()] * n
    return M.TopicResult(topic=topic, query="q", status=status, candidates=c, error=error)


def test_gan_ghi_chu_dung_cho_lan_tham_quyen_0_ung_vien():
    ds_vao = [_tr("NICE — hướng dẫn mới"), _tr("USPSTF — khuyến cáo dự phòng", n=1), _tr("Tim mạch"),
              _tr("An toàn thuốc — cảnh báo mới (MHRA/FDA/EMA)", status="FAIL"),
              _tr("An toàn thuốc — cảnh báo mới (MHRA/FDA/EMA)", status="PASS_DEGRADED", error="SUY GIẢM: x")]
    ra, ds = M.gan_ghi_chu_quan_sat(ds_vao)
    assert "QUAN SÁT HẠN CHẾ" in ra[0].error and "SRC-017" in ra[0].error and ra[0].status == "PASS", "không đổi status"
    assert ra[1].error == "" and ra[2].error == "" and ra[3].error == "", "có ứng viên / chủ đề thường / FAIL thì không gắn"
    assert ra[4].error.startswith("SUY GIẢM: x; QUAN SÁT HẠN CHẾ"), "nối thêm, không xoá ghi chú cũ"
    assert [x["topic"] for x in ds] == ["NICE — hướng dẫn mới", "An toàn thuốc — cảnh báo mới (MHRA/FDA/EMA)"]


def test_bao_cao_markdown_co_dong_quan_sat_han_che():
    rep = {"days": 7, "status": "PASS", "degraded_topics": 0, "topic_count": 1, "successful_topics": 1, "failed_topics": 0,
           "candidate_count": 0, "topics": [], "disclaimer": "x",
           "quan_sat_han_che": [{"topic": "NICE — hướng dẫn mới", "kenh_khac": "SRC-017"}]}
    md = M.markdown_report(rep)
    assert "KHÔNG quan sát được văn bản chính thức" in md and "NICE — hướng dẫn mới → SRC-017" in md
    rep["quan_sat_han_che"] = []
    assert "KHÔNG quan sát được" not in M.markdown_report(rep)


def test_run_scan_goi_gan_ghi_chu_va_dua_vao_json():
    cay = ast.parse(SS.read_text(encoding="utf-8"))
    rs = next(n for n in cay.body if isinstance(n, ast.FunctionDef) and n.name == "run_scan")
    assert any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "gan_ghi_chu_quan_sat" for n in ast.walk(rs))
    assert any(isinstance(n, ast.Constant) and n.value == "quan_sat_han_che" for n in ast.walk(rs))


def test_kenh_khac_tro_toi_ma_nguon_co_that_trong_so():
    so = {s["id"] for s in json.loads((REPO / "data" / "sources.json").read_text(encoding="utf-8"))["sources"]}
    import re
    for ten, kenh in M.KENH_THAT_NGOAI_PUBMED.items():
        ma = re.findall(r"SRC-\d{3}", kenh)
        assert ma and set(ma) <= so, f"«{ten}» trỏ mã nguồn không có trong sổ: {set(ma) - so}"


def test_ten_chu_de_khop_watchlist_that():
    wl = REPO / "EBM-Dashboards" / "watchlist.json"
    if not wl.exists():
        pytest.skip("bản sao trần — không có watchlist thật (⚪ có khai báo)")
    d = json.loads(wl.read_text(encoding="utf-8"))
    ten = {t.get("topic") for t in (d["topics"] if isinstance(d, dict) and "topics" in d else d)}
    thieu = set(M.KENH_THAT_NGOAI_PUBMED) - ten
    assert not thieu, f"watchlist đổi tên chủ đề — ghi chú quan sát sẽ không gắn được: {thieu}"
