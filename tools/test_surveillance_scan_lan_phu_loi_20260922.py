"""Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #10, LOW).

Khi CẢ BA làn phụ (preprint/clinicaltrials/scopus) hỏng, `status` chủ đề vẫn "PASS" (làn phụ
không dùng con trỏ nên không kéo chủ đề FAIL/DEGRADED) — trước đây thông tin lỗi chỉ nằm trong
chuỗi tự do `error`, không có trường máy đọc để bên tiêu thụ (uu_tien_cap_nhat, orchestrator)
phân biệt "0 ứng viên vì không có gì mới" với "0 ứng viên vì làn phụ hỏng".
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_lan_phu_loi_test", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_lan_phu_loi_test"] = S
_sp.loader.exec_module(S)


def _search_ok(query, days, retmax, **kw):
    return []


def _summarize_ok(ids):
    return []


def test_ca_ba_lan_phu_hong_van_ghi_ten_lan_du_status_pass(monkeypatch):
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    rep = S.run_scan([{"topic": "A", "query": "q"}], days=30, max_results=5,
                     search_fn=_search_ok, summarize_fn=_summarize_ok)
    t = rep["topics"][0]
    assert t["status"] == "PASS", "làn phụ hỏng không được kéo status xuống FAIL/DEGRADED"
    assert set(t["lan_phu_loi"]) == {"preprint", "clinicaltrials", "scopus"}
    assert "làn scopus lỗi" in t["error"] and "làn preprint lỗi" in t["error"]


def test_lan_phu_chay_duoc_thi_lan_phu_loi_rong(monkeypatch):
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    rep = S.run_scan([{"topic": "A", "query": "q"}], days=30, max_results=5,
                     search_fn=_search_ok, summarize_fn=_summarize_ok)
    t = rep["topics"][0]
    assert t["lan_phu_loi"] == [], "0 kết quả THẬT (không lỗi) không được coi là làn hỏng"


def test_chi_mot_lan_hong_chi_ghi_dung_ten_lan_do(monkeypatch):
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    rep = S.run_scan([{"topic": "A", "query": "q"}], days=30, max_results=5,
                     search_fn=_search_ok, summarize_fn=_summarize_ok)
    t = rep["topics"][0]
    assert t["lan_phu_loi"] == ["preprint"]
