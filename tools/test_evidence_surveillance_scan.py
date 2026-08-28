from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
SPEC = importlib.util.spec_from_file_location("evidence_surveillance_scan", MODULE_PATH)
assert SPEC and SPEC.loader
S = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = S
SPEC.loader.exec_module(S)


import pytest


@pytest.fixture(autouse=True)
def _chan_lan_goi_mang(monkeypatch):
    """28/08/2026 — run_scan có HAI làn phụ gọi MẠNG THẬT (medRxiv + ClinicalTrials.gov)
    mà test không stub: trên máy có mạng, truy vấn giả «A»/«B» kéo về ứng viên THẬT và
    candidate_count nhảy 1 → 10 (bắt được lần đầu trên CI ubuntu — nơi mạng đi thẳng,
    trong khi máy dev đi proxy nên làn lỗi êm và test «tình cờ» xanh). Unit test phải
    NGOẠI TUYẾN và tất định (đúng luật «nhanh và ngoại tuyến» của bộ chốt): chặn cả hai
    làn ở mọi test trong file; muốn test riêng làn thì viết test đích danh với stub HTTP."""
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])


def test_watchlist_schema_rejects_duplicate_queries() -> None:
    payload = {
        "topics": [
            {"topic": "A", "query": "hypertension", "active": True},
            {"topic": "B", "query": "Hypertension", "active": True},
        ]
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "watchlist.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        try:
            S.load_watchlist(path)
        except ValueError as exc:
            assert "Trùng query" in str(exc)
        else:  # pragma: no cover - nhánh bảo vệ fail-closed
            raise AssertionError("Watchlist trùng query phải bị chặn")


def test_scan_marks_partial_and_does_not_claim_no_update_on_failed_topic() -> None:
    topics = [
        {"topic": "Tim mạch", "query": "heart failure"},
        {"topic": "An toàn thuốc", "query": "drug safety"},
    ]

    def fake_search(query: str, _days: int, _max_results: int) -> list[str]:
        if query == "drug safety":
            raise RuntimeError("source timeout")
        return ["12345"]

    def fake_summary(_ids: list[str]) -> list[object]:
        return [S.Candidate("12345", "2026", "Synthetic title", "https://pubmed.ncbi.nlm.nih.gov/12345/")]

    report = S.run_scan(
        topics,
        days=30,
        max_results=5,
        search_fn=fake_search,
        summarize_fn=fake_summary,
    )
    markdown = S.markdown_report(report)

    assert report["status"] == "PARTIAL"
    assert report["candidate_count"] == 1
    assert report["failed_topics"] == 1
    assert "KHÔNG QUÉT ĐƯỢC" in markdown
    assert "Không được diễn giải là 'không có cập nhật'" in markdown
    assert report["auto_apply"] is False


def test_scan_deduplicates_pmid_across_topics() -> None:
    topics = [
        {"topic": "A", "query": "a"},
        {"topic": "B", "query": "b"},
    ]

    def fake_search(_query: str, _days: int, _max_results: int) -> list[str]:
        return ["777"]

    def fake_summary(_ids: list[str]) -> list[object]:
        return [S.Candidate("777", "2026", "Same paper", "https://pubmed.ncbi.nlm.nih.gov/777/")]

    report = S.run_scan(
        topics,
        days=30,
        max_results=5,
        search_fn=fake_search,
        summarize_fn=fake_summary,
    )

    assert report["status"] == "PASS"
    assert report["candidate_count"] == 1
    assert len(report["topics"][0]["candidates"]) == 1
    assert len(report["topics"][1]["candidates"]) == 0
