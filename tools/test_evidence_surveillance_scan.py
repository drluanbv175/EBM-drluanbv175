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

# Giữ tham chiếu HÀM GỐC trước khi fixture autouse _chan_lan_goi_mang monkeypatch
# S.search_scopus_lane thành lambda: []. Test kiểm HÀNH VI THẬT của lane phải
# gọi tham chiếu này, không phải S.search_scopus_lane (đã bị chặn cho mọi test).
_SEARCH_SCOPUS_LANE_GOC = S.search_scopus_lane
# Cùng lý do — thêm 13/09/2026 cho search_dynamed_lane.
_SEARCH_DYNAMED_LANE_GOC = S.search_dynamed_lane

import pytest


@pytest.fixture(autouse=True)
def _chan_lan_goi_mang(monkeypatch):
    """28/08/2026 — run_scan có HAI làn phụ gọi MẠNG THẬT (medRxiv + ClinicalTrials.gov)
    mà test không stub: trên máy có mạng, truy vấn giả «A»/«B» kéo về ứng viên THẬT và
    candidate_count nhảy 1 → 10 (bắt được lần đầu trên CI ubuntu — nơi mạng đi thẳng,
    trong khi máy dev đi proxy nên làn lỗi êm và test «tình cờ» xanh). Unit test phải
    NGOẠI TUYẾN và tất định (đúng luật «nhanh và ngoại tuyến» của bộ chốt): chặn cả ba
    làn ở mọi test trong file; muốn test riêng làn thì viết test đích danh với stub HTTP.

    THÊM 13/09/2026 — search_scopus_lane: khác hai làn kia, làn này có thể THẬT SỰ gọi
    mạng (Elsevier) nếu máy đang chạy test đã có ENABLE_SCOPUS=true + SCOPUS_API_KEY
    thật trong .env (đúng tình trạng máy bác sĩ sau khi xác nhận key hoạt động) — phải
    chặn tuyệt đối, nếu không bộ test "ngoại tuyến" sẽ âm thầm gọi API trả phí thật.

    Cùng lý do, cùng ngày — search_dynamed_lane: máy đã bật ENABLE_DYNAMED=true +
    DYNAMED_CLIENT_ID/SECRET thật cũng sẽ khiến bộ test gọi OAuth2 EBSCO thật nếu
    không chặn."""
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_dynamed_lane", lambda *a, **k: [])


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


def test_ba_nhan_tap_chi_bac_si_duyet_30_08() -> None:
    """Ba nhóm nhãn bác sĩ duyệt 30/08/2026 (audit/07 §3). Vế ÂM quan trọng nhất:
    «stroke»/«neurology» trong TIÊU ĐỀ không được gán nhãn — chúng là từ thường
    gặp; chỉ trường tạp chí/tổ chức mới được khớp (AMBIGUOUS_SHORT_ALIASES)."""
    # Vế dương — khớp qua trường tạp chí
    assert S.detect_authority_source("Stroke", "HINTS to diagnose stroke") == "Stroke (AHA)"
    assert S.detect_authority_source("Neurology", "Red and orange flags") == "AAN/Neurology"
    assert S.detect_authority_source("American Family Physician", "Weight loss") == "AAFP"
    assert S.detect_authority_source("Am Fam Physician", "Weight loss") == "AAFP"
    # Vế ÂM — từ nhạy cảm chỉ nằm trong tiêu đề thì KHÔNG nhãn
    assert S.detect_authority_source("Tap chi X", "Acute stroke management update") == ""
    assert S.detect_authority_source("Tap chi X", "Neurology consult patterns 2026") == ""
    # JAMA Neurology vẫn thuộc nhóm JAMA (alias «jama» đứng trước) — hành vi chấp nhận
    assert S.detect_authority_source("JAMA Neurology", "BE-FAST validation") == "JAMA"


# ════════════════════════════════════════════════════════════════════════════
# LÀN SCOPUS (Elsevier) — thêm 13/09/2026, nối vào tầng giám sát lâm sàng
# ════════════════════════════════════════════════════════════════════════════

class _FakeScopusRecord:
    """Đứng thay cho app.sources.base.RawRecord — chỉ cần đúng thuộc tính mà
    search_scopus_lane() đọc, không phụ thuộc import chéo medical-ebm-automation."""

    def __init__(self, *, pmid="", title="", url="", doi="", publication_date="",
                journal_or_organization=""):
        self.pmid = pmid
        self.title = title
        self.url = url
        self.doi = doi
        self.publication_date = publication_date
        self.journal_or_organization = journal_or_organization


class _FakeScopusClient:
    """client_factory giả — không gọi mạng, không cần ENABLE_SCOPUS/API key thật."""

    def __init__(self, records=None, loi=None):
        self._records = records or []
        self._loi = loi
        self.use_mock = True  # search_scopus_lane() phải tự đặt False

    def search(self, query, *, max_results=20, since_date=None):
        if self._loi:
            raise self._loi
        self.dieu_kien_da_goi = {"query": query, "max_results": max_results,
                                 "since_date": since_date}
        return self._records


def test_search_scopus_lane_maps_record_fields_to_candidate():
    rec = _FakeScopusRecord(
        pmid="38000000", title="SGLT2 inhibitors in CKD",
        url="https://www.scopus.com/record/x", doi="10.1016/j.kint.2024.01.001",
        publication_date="2024-03-15", journal_or_organization="Kidney International",
    )
    client = _FakeScopusClient(records=[rec])
    out = _SEARCH_SCOPUS_LANE_GOC("ckd", 30, 10, client_factory=lambda: client)
    assert len(out) == 1
    c = out[0]
    assert c.pmid == "38000000"
    assert c.title == "SGLT2 inhibitors in CKD"
    assert c.url == "https://www.scopus.com/record/x"
    assert c.source == "Scopus (Elsevier)"
    assert c.journal_or_organization == "Kidney International"
    assert c.tang == "scopus_bo_sung"
    assert c.rut_bai == "chua_kiem"
    # search_scopus_lane() PHẢI tự ép use_mock=False — nếu không, một client
    # thật sẽ trả dữ liệu minh hoạ thay vì lỗi rõ ràng khi thiếu key.
    assert client.use_mock is False


def test_search_scopus_lane_url_falls_back_to_doi_when_no_url():
    rec = _FakeScopusRecord(pmid="1", title="X", url="", doi="10.1/abc")
    client = _FakeScopusClient(records=[rec])
    out = _SEARCH_SCOPUS_LANE_GOC("q", 30, 10, client_factory=lambda: client)
    assert out[0].url == "https://doi.org/10.1/abc"


def test_search_scopus_lane_empty_pmid_stays_empty_string_not_none():
    """Candidate.pmid không phải Optional — phải là chuỗi rỗng, khớp khuôn
    search_trials_lane() đã dùng cho ứng viên không có PMID."""
    rec = _FakeScopusRecord(pmid="", title="Không PMID", url="https://x")
    client = _FakeScopusClient(records=[rec])
    out = _SEARCH_SCOPUS_LANE_GOC("q", 30, 10, client_factory=lambda: client)
    assert out[0].pmid == ""


def test_search_scopus_lane_passes_since_date_and_capped_retmax():
    client = _FakeScopusClient(records=[])
    _SEARCH_SCOPUS_LANE_GOC("q", days=10, retmax=999, client_factory=lambda: client)
    assert client.dieu_kien_da_goi["max_results"] == 25  # trần an toàn, không phải 999
    assert client.dieu_kien_da_goi["since_date"] is not None


def test_search_scopus_lane_propagates_client_errors_not_swallowed():
    """Thiếu SCOPUS_API_KEY dù đã bật cờ -> ScopusClient.search() tự ném
    RuntimeError -- search_scopus_lane() KHÔNG được nuốt lỗi đó (khác lỗi mạng,
    vốn đã được ScopusClient tự bắt); run_scan() ở lớp ngoài mới là nơi ghi
    chú minh bạch, không phải hàm này im lặng trả []."""
    client = _FakeScopusClient(loi=RuntimeError("thiếu SCOPUS_API_KEY"))
    with pytest.raises(RuntimeError, match="SCOPUS_API_KEY"):
        _SEARCH_SCOPUS_LANE_GOC("q", 30, 10, client_factory=lambda: client)


def test_run_scan_merges_scopus_candidate_and_dedupes_by_pmid(monkeypatch):
    """Ứng viên Scopus trùng PMID với ứng viên PubMed chính phải bị loại — cùng
    luật dedup `all_pmids` áp cho preprint/trials."""
    rec_trung = _FakeScopusRecord(pmid="777", title="Bản trùng", url="https://scopus/1")
    rec_moi = _FakeScopusRecord(pmid="900", title="Bản mới từ Scopus", url="https://scopus/2")
    monkeypatch.setattr(S, "search_scopus_lane",
                        lambda *a, **k: [S.Candidate(r.pmid, "2026", r.title, r.url,
                                                     source="Scopus (Elsevier)",
                                                     tang="scopus_bo_sung")
                                        for r in (rec_trung, rec_moi)])

    def fake_search(_q, _d, _m):
        return ["777"]

    def fake_summary(_ids):
        return [S.Candidate("777", "2026", "Same paper", "https://pubmed.ncbi.nlm.nih.gov/777/")]

    report = S.run_scan([{"topic": "A", "query": "a"}], days=30, max_results=5,
                        search_fn=fake_search, summarize_fn=fake_summary)
    assert report["status"] == "PASS"
    titles = [c["title"] for c in report["topics"][0]["candidates"]]
    assert "Bản mới từ Scopus" in titles
    assert titles.count("Bản trùng") == 0  # PMID 777 giữ bản PubMed, loại bản Scopus trùng
    assert report["candidate_count"] == 2  # 777 (PubMed, giữ bản đầu) + 900 (Scopus)


def test_run_scan_scopus_lane_failure_does_not_fail_topic(monkeypatch):
    def loi(*a, **k):
        raise RuntimeError("thiếu SCOPUS_API_KEY")
    monkeypatch.setattr(S, "search_scopus_lane", loi)

    def fake_search(_q, _d, _m):
        return ["1"]

    def fake_summary(_ids):
        return [S.Candidate("1", "2026", "T", "https://pubmed.ncbi.nlm.nih.gov/1/")]

    report = S.run_scan([{"topic": "A", "query": "a"}], days=30, max_results=5,
                        search_fn=fake_search, summarize_fn=fake_summary)
    assert report["status"] == "PASS"
    assert "làn scopus lỗi" in report["topics"][0]["error"]
    assert len(report["topics"][0]["candidates"]) == 1


def test_markdown_report_scopus_candidate_not_mislabeled_as_new_in_pubmed():
    """scopus_bo_sung phải nằm trong danh sách «ngoài PubMed» của markdown_report,
    giống preprint/trials — nếu không, một bài Scopus không có pubtype sẽ bị gắn
    nhầm nhãn «⚡ mới vào PubMed» dù nó không hề đến từ PubMed."""
    report = {
        "days": 30, "status": "PASS", "successful_topics": 1, "failed_topics": 0,
        "candidate_count": 1, "disclaimer": S.DISCLAIMER,
        "topics": [{
            "topic": "A", "query": "a", "status": "PASS", "error": "",
            "candidates": [S.asdict(S.Candidate(
                pmid="", publication_date="2026", title="Từ Scopus",
                url="https://scopus/1", source="Scopus (Elsevier)",
                tang="scopus_bo_sung",
            ))],
        }],
    }
    md = S.markdown_report(report)
    assert "mới vào PubMed" not in md
    assert "không PMID — xem link" in md


# ════════════════════════════════════════════════════════════════════════════
# LÀN DYNAMED (EBSCO) — thêm 13/09/2026, nối vào tầng giám sát lâm sàng
# ════════════════════════════════════════════════════════════════════════════

class _FakeDynaMedRecord:
    """Đứng thay cho app.sources.base.RawRecord — chỉ cần đúng thuộc tính mà
    search_dynamed_lane() đọc, không phụ thuộc import chéo medical-ebm-automation."""

    def __init__(self, *, title="", url="", journal_or_organization=""):
        self.title = title
        self.url = url
        self.journal_or_organization = journal_or_organization


class _FakeDynaMedClient:
    """client_factory giả — không gọi mạng, không cần ENABLE_DYNAMED/credential thật."""

    def __init__(self, records=None, loi=None):
        self._records = records or []
        self._loi = loi
        self.use_mock = True  # search_dynamed_lane() phải tự đặt False

    def search(self, query, *, max_results=20):
        if self._loi:
            raise self._loi
        self.dieu_kien_da_goi = {"query": query, "max_results": max_results}
        return self._records


def test_search_dynamed_lane_maps_record_fields_to_candidate():
    rec = _FakeDynaMedRecord(
        title="Complications of Myocardial Infarction",
        url="https://www.dynamed.com/condition/myocardial-infarction-complications",
        journal_or_organization="DynaMed",
    )
    client = _FakeDynaMedClient(records=[rec])
    out = _SEARCH_DYNAMED_LANE_GOC("myocardial infarction", 30, 10, client_factory=lambda: client)
    assert len(out) == 1
    c = out[0]
    assert c.title == "Complications of Myocardial Infarction"
    assert c.url == "https://www.dynamed.com/condition/myocardial-infarction-complications"
    assert c.source == "DynaMed (EBSCO)"
    assert c.journal_or_organization == "DynaMed"
    assert c.tang == "dynamed_diem_kham"
    assert c.rut_bai == "chua_kiem"
    # search_dynamed_lane() PHẢI tự ép use_mock=False — nếu không, một client
    # thật sẽ trả dữ liệu minh hoạ thay vì lỗi rõ ràng khi thiếu credential.
    assert client.use_mock is False


def test_search_dynamed_lane_pmid_always_empty_string_not_none():
    """DynaMed KHÔNG BAO GIỜ có pmid (nội dung tổng hợp thứ cấp, không phải bài
    báo gốc) — Candidate.pmid không phải Optional nên phải là chuỗi rỗng, khớp
    khuôn search_trials_lane()/search_scopus_lane() đã dùng."""
    rec = _FakeDynaMedRecord(title="X", url="https://dynamed/x")
    client = _FakeDynaMedClient(records=[rec])
    out = _SEARCH_DYNAMED_LANE_GOC("q", 30, 10, client_factory=lambda: client)
    assert out[0].pmid == ""


def test_search_dynamed_lane_does_not_pass_since_date(monkeypatch):
    """DynaMedClient.search() cố ý bỏ qua since_date (nội dung cập nhật liên
    tục, không xuất bản rời rạc theo ngày) — lane không được tự chế tham số đó."""
    client = _FakeDynaMedClient(records=[])
    _SEARCH_DYNAMED_LANE_GOC("q", days=10, retmax=999, client_factory=lambda: client)
    assert "since_date" not in client.dieu_kien_da_goi
    assert client.dieu_kien_da_goi["max_results"] == 25  # trần an toàn, không phải 999


def test_search_dynamed_lane_propagates_client_errors_not_swallowed():
    """Thiếu DYNAMED_CLIENT_ID/SECRET dù đã bật cờ -> DynaMedClient.search() tự
    ném RuntimeError -- search_dynamed_lane() KHÔNG được nuốt lỗi đó (khác lỗi
    mạng, vốn đã được DynaMedClient tự bắt); run_scan() ở lớp ngoài mới là nơi
    ghi chú minh bạch, không phải hàm này im lặng trả []."""
    client = _FakeDynaMedClient(loi=RuntimeError("thiếu DYNAMED_CLIENT_ID"))
    with pytest.raises(RuntimeError, match="DYNAMED_CLIENT_ID"):
        _SEARCH_DYNAMED_LANE_GOC("q", 30, 10, client_factory=lambda: client)


def test_run_scan_merges_dynamed_candidate_and_dedupes_by_url(monkeypatch):
    """Ứng viên DynaMed không có pmid nên khoá dedup rơi về URL.

    LƯU Ý QUAN TRỌNG (bắt được khi viết chính test này): `all_pmids` trong
    `run_scan()` chỉ nhận PMID THÔ từ làn PubMed chính (`candidate.pmid`,
    KHÔNG phải `pmid or url`) — nên một ứng viên DynaMed vô tình mang URL
    dạng `pubmed.ncbi.nlm.nih.gov/<pmid>/` KHÔNG bị coi là trùng với chính
    PMID đó (chuỗi URL không khớp chuỗi PMID trần). Dedup theo URL chỉ có
    hiệu lực GIỮA các làn dùng chung khoá `pmid or url` (preprint/trials/
    scopus/dynamed — nhóm "BA LÀN" chạy sau `gan_do_tin_cay()`), đúng như
    kiểm ở đây: làn trials chạy TRƯỚC làn dynamed (thứ tự khai trong
    `run_scan()`), nên một URL đã được trials thêm vào `all_pmids` sẽ khiến
    dynamed lane bị loại nếu trùng — cùng luật `all_pmids` áp cho preprint/
    trials/scopus."""
    monkeypatch.setattr(
        S, "search_trials_lane",
        lambda *a, **k: [S.Candidate("", "", "Từ ClinicalTrials.gov",
                                     "https://vi-du/trung", tang="thu_nghiem_dang_ky")])
    monkeypatch.setattr(
        S, "search_dynamed_lane",
        lambda *a, **k: [
            S.Candidate("", "", "Bản trùng", "https://vi-du/trung",
                       source="DynaMed (EBSCO)", tang="dynamed_diem_kham"),
            S.Candidate("", "", "Bản mới từ DynaMed", "https://dynamed/moi",
                       source="DynaMed (EBSCO)", tang="dynamed_diem_kham"),
        ])

    def fake_search(_q, _d, _m):
        return []

    def fake_summary(_ids):
        return []

    report = S.run_scan([{"topic": "A", "query": "a"}], days=30, max_results=5,
                        search_fn=fake_search, summarize_fn=fake_summary)
    assert report["status"] == "PASS"
    titles = [c["title"] for c in report["topics"][0]["candidates"]]
    assert "Bản mới từ DynaMed" in titles
    assert titles.count("Bản trùng") == 0  # URL trùng với ứng viên trials, loại bản DynaMed
    assert report["candidate_count"] == 2  # trials (giữ bản đầu) + DynaMed (mới)


def test_run_scan_dynamed_lane_failure_does_not_fail_topic(monkeypatch):
    def loi(*a, **k):
        raise RuntimeError("thiếu DYNAMED_CLIENT_ID")
    monkeypatch.setattr(S, "search_dynamed_lane", loi)

    def fake_search(_q, _d, _m):
        return ["1"]

    def fake_summary(_ids):
        return [S.Candidate("1", "2026", "T", "https://pubmed.ncbi.nlm.nih.gov/1/")]

    report = S.run_scan([{"topic": "A", "query": "a"}], days=30, max_results=5,
                        search_fn=fake_search, summarize_fn=fake_summary)
    assert report["status"] == "PASS"
    assert "làn dynamed lỗi" in report["topics"][0]["error"]
    assert len(report["topics"][0]["candidates"]) == 1


def test_markdown_report_dynamed_candidate_not_mislabeled_as_new_in_pubmed():
    """dynamed_diem_kham phải nằm trong danh sách «ngoài PubMed» của
    markdown_report, giống preprint/trials/scopus — nếu không, một mục DynaMed
    (luôn không có pubtype) sẽ bị gắn nhầm nhãn «⚡ mới vào PubMed»."""
    report = {
        "days": 30, "status": "PASS", "successful_topics": 1, "failed_topics": 0,
        "candidate_count": 1, "disclaimer": S.DISCLAIMER,
        "topics": [{
            "topic": "A", "query": "a", "status": "PASS", "error": "",
            "candidates": [S.asdict(S.Candidate(
                pmid="", publication_date="", title="Từ DynaMed",
                url="https://dynamed/1", source="DynaMed (EBSCO)",
                tang="dynamed_diem_kham",
            ))],
        }],
    }
    md = S.markdown_report(report)
    assert "mới vào PubMed" not in md
    assert "không PMID — xem link" in md
