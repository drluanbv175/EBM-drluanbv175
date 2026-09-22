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
_SEARCH_CORE_LANE_GOC = S.search_core_lane
_BO_SUNG_DU_PHONG_LANE_GOC = S.bo_sung_du_phong_lane

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

    THÊM 22/09/2026 — search_core_lane (miễn phí nhưng vẫn tốn nhịp/hạn mức của
    core.ac.uk) và bo_sung_du_phong_lane (Consensus + SerpApi Scholar — CẢ HAI ĐỀU
    TÍNH PHÍ/HẠN MỨC THÁNG RẤT NHỎ: Consensus 10/tháng, SerpApi 200/tháng) — máy bác
    sĩ đã bật ENABLE_CORE + ENABLE_CONSENSUS + ENABLE_SERPAPI_SCHOLAR thật, nên KHÔNG
    chặn ở đây sẽ khiến MỖI LẦN chạy `pytest` đốt hạn mức tháng thật một cách âm thầm."""
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_core_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lambda *a, **k: ([], ""))


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


# ════════════════════════════════════════════════════════════════════════════
# LÀN CORE (core.ac.uk) — thêm 22/09/2026, khuôn hệt LÀN SCOPUS ở trên
# ════════════════════════════════════════════════════════════════════════════

class _FakeCoreRecord:
    """Đứng thay app.sources.base.RawRecord — chỉ cần đúng thuộc tính mà
    search_core_lane() đọc."""

    def __init__(self, *, pmid="", title="", url="", doi="", publication_date="",
                journal_or_organization=""):
        self.pmid = pmid
        self.title = title
        self.url = url
        self.doi = doi
        self.publication_date = publication_date
        self.journal_or_organization = journal_or_organization


class _FakeCoreClient:
    """client_factory giả — không gọi mạng, không cần ENABLE_CORE/API key thật."""

    def __init__(self, records=None, loi=None):
        self._records = records or []
        self._loi = loi
        self.use_mock = True  # search_core_lane() phải tự đặt False

    def search(self, query, *, max_results=20, since_date=None):
        if self._loi:
            raise self._loi
        self.dieu_kien_da_goi = {"query": query, "max_results": max_results,
                                 "since_date": since_date}
        return self._records


def test_search_core_lane_maps_record_fields_to_candidate():
    rec = _FakeCoreRecord(
        pmid="", title="Systematic guideline review method", url="",
        doi="10.1186/1472-6963-9-74", publication_date="2009-01-01",
        journal_or_organization="BMC Health Services Research",
    )
    client = _FakeCoreClient(records=[rec])
    out = _SEARCH_CORE_LANE_GOC("heart failure", 30, 10, client_factory=lambda: client)
    assert len(out) == 1
    c = out[0]
    assert c.pmid == ""
    assert c.title == "Systematic guideline review method"
    assert c.url == "https://doi.org/10.1186/1472-6963-9-74"  # rơi về DOI khi thiếu url
    assert c.source == "CORE (core.ac.uk)"
    assert c.journal_or_organization == "BMC Health Services Research"
    assert c.tang == "core_bo_sung"
    assert c.rut_bai == "chua_kiem"
    assert client.use_mock is False


def test_search_core_lane_pmid_that_duoc_giu_nguyen_khi_core_tra():
    """Khác đa số bản ghi CORE (thường không pmid), khi CoreClient trả pmid thật
    (trường 'pubmedId' của core.ac.uk) thì Candidate phải giữ đúng giá trị đó —
    để gan_do_tin_cay() kiểm rút bài được, không bị rơi vào nhóm 'chua_kiem' vĩnh viễn."""
    rec = _FakeCoreRecord(pmid="12345678", title="X", url="https://core.ac.uk/x")
    client = _FakeCoreClient(records=[rec])
    out = _SEARCH_CORE_LANE_GOC("q", 30, 10, client_factory=lambda: client)
    assert out[0].pmid == "12345678"


def test_search_core_lane_passes_since_date_and_capped_retmax():
    client = _FakeCoreClient(records=[])
    _SEARCH_CORE_LANE_GOC("q", days=10, retmax=999, client_factory=lambda: client)
    assert client.dieu_kien_da_goi["max_results"] == 20  # trần an toàn, không phải 999
    assert client.dieu_kien_da_goi["since_date"] is not None


def test_run_scan_merges_core_candidate_and_dedupes_by_pmid(monkeypatch):
    rec_trung = _FakeCoreRecord(pmid="777", title="Bản trùng", url="https://core/1")
    rec_moi = _FakeCoreRecord(pmid="", title="Bản mới từ CORE", url="https://core/2")
    monkeypatch.setattr(S, "search_core_lane",
                        lambda *a, **k: [S.Candidate(r.pmid, "2026", r.title, r.url,
                                                     source="CORE (core.ac.uk)",
                                                     tang="core_bo_sung")
                                        for r in (rec_trung, rec_moi)])

    def fake_search(_q, _d, _m):
        return ["777"]

    def fake_summary(_ids):
        return [S.Candidate("777", "2026", "Same paper", "https://pubmed.ncbi.nlm.nih.gov/777/")]

    report = S.run_scan([{"topic": "A", "query": "a"}], days=30, max_results=5,
                        search_fn=fake_search, summarize_fn=fake_summary)
    assert report["status"] == "PASS"
    titles = [c["title"] for c in report["topics"][0]["candidates"]]
    assert "Bản mới từ CORE" in titles
    assert titles.count("Bản trùng") == 0
    assert report["candidate_count"] == 2


def test_run_scan_core_lane_failure_does_not_fail_topic(monkeypatch):
    def loi(*a, **k):
        raise RuntimeError("lỗi mạng CORE")
    monkeypatch.setattr(S, "search_core_lane", loi)

    def fake_search(_q, _d, _m):
        return ["1"]

    def fake_summary(_ids):
        return [S.Candidate("1", "2026", "T", "https://pubmed.ncbi.nlm.nih.gov/1/")]

    report = S.run_scan([{"topic": "A", "query": "a"}], days=30, max_results=5,
                        search_fn=fake_search, summarize_fn=fake_summary)
    assert report["status"] == "PASS"
    assert "làn core lỗi" in report["topics"][0]["error"]
    assert "core" in report["topics"][0]["lan_phu_loi"]
    assert len(report["topics"][0]["candidates"]) == 1


# ════════════════════════════════════════════════════════════════════════════
# BẬC THANG DỰ PHÒNG (Consensus → SerpApi Scholar) — thêm 22/09/2026
# ════════════════════════════════════════════════════════════════════════════

class _FakeExtraRecord:
    """Đứng thay app.sources.base.RawRecord cho bản ghi TRẢ VỀ từ bậc thang."""

    def __init__(self, *, pmid="", title="", url="", doi="", publication_date="",
                journal_or_organization="", source="consensus"):
        self.pmid = pmid
        self.title = title
        self.url = url
        self.doi = doi
        self.publication_date = publication_date
        self.journal_or_organization = journal_or_organization
        self.source = source


def test_bo_sung_du_phong_lane_khong_goi_khi_bo_sung_fn_tra_rong():
    """Cổng đủ-chứng-cứ ĐÓNG (bo_sung_neu_thieu tự quyết định 'đủ rồi') ⇒ hàm
    này CHỈ truyền tiếp kết quả rỗng, không tự bịa thêm gì."""
    goi = {}

    def bo_sung_fn_gia(query, area, records, *, max_results):
        goi["query"] = query
        goi["so_ban_ghi_hien_co"] = len(records)
        return [], {}

    ra, ghi_chu = _BO_SUNG_DU_PHONG_LANE_GOC(
        "hf guideline", [S.Candidate("1", "2026", "T", "https://x", source="PubMed")],
        10, bo_sung_fn=bo_sung_fn_gia)
    assert ra == []
    assert ghi_chu == ""
    assert goi["query"] == "hf guideline"
    assert goi["so_ban_ghi_hien_co"] == 1  # đã CHUYỂN ĐÚNG unique_hien_co sang RawRecord


def test_bo_sung_du_phong_lane_map_ban_ghi_moi_dung_tang_va_nguon():
    rec = _FakeExtraRecord(title="Bài từ Consensus", url="https://doi.org/10.1/x",
                           source="consensus")

    def bo_sung_fn_gia(query, area, records, *, max_results):
        return [rec], {}

    ra, ghi_chu = _BO_SUNG_DU_PHONG_LANE_GOC("q", [], 10, bo_sung_fn=bo_sung_fn_gia)
    assert len(ra) == 1
    assert ra[0].title == "Bài từ Consensus"
    assert ra[0].tang == "du_phong_bac_thang"
    assert ra[0].source == "Dự phòng: consensus"
    assert ra[0].rut_bai == "chua_kiem"
    assert ghi_chu == ""


def test_bo_sung_du_phong_lane_bao_loi_noi_bo_qua_ghi_chu():
    """`tom_tat['loi_noi_bo']` (bo_sung_neu_thieu tự bắt exception nội bộ, KHÔNG
    raise) phải tới được ghi_chu để run_scan() ghi vào lan_phu_loi — nếu không,
    lỗi bậc thang sẽ CHÌM hoàn toàn, khác hẳn cách các làn khác báo lỗi."""
    def bo_sung_fn_gia(query, area, records, *, max_results):
        return [], {"loi_noi_bo": "RuntimeError"}

    ra, ghi_chu = _BO_SUNG_DU_PHONG_LANE_GOC("q", [], 10, bo_sung_fn=bo_sung_fn_gia)
    assert ra == []
    assert "RuntimeError" in ghi_chu


def test_run_scan_du_phong_lane_ket_qua_duoc_gop_va_dedupe(monkeypatch):
    rec_moi = _FakeExtraRecord(pmid="", title="Bài dự phòng mới", url="https://doi.org/10.1/y",
                               source="serpapi_scholar")
    monkeypatch.setattr(S, "bo_sung_du_phong_lane",
                        lambda *a, **k: ([S.Candidate("", "2026", rec_moi.title, rec_moi.url,
                                                      source=f"Dự phòng: {rec_moi.source}",
                                                      tang="du_phong_bac_thang")], ""))

    def fake_search(_q, _d, _m):
        return ["1"]

    def fake_summary(_ids):
        return [S.Candidate("1", "2026", "T", "https://pubmed.ncbi.nlm.nih.gov/1/")]

    report = S.run_scan([{"topic": "A", "query": "a"}], days=30, max_results=5,
                        search_fn=fake_search, summarize_fn=fake_summary)
    assert report["status"] == "PASS"
    titles = [c["title"] for c in report["topics"][0]["candidates"]]
    assert "Bài dự phòng mới" in titles
    assert report["candidate_count"] == 2


def test_run_scan_du_phong_lane_loi_khong_lam_hong_chu_de(monkeypatch):
    def loi(*a, **k):
        raise RuntimeError("lỗi bậc thang")
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", loi)

    def fake_search(_q, _d, _m):
        return ["1"]

    def fake_summary(_ids):
        return [S.Candidate("1", "2026", "T", "https://pubmed.ncbi.nlm.nih.gov/1/")]

    report = S.run_scan([{"topic": "A", "query": "a"}], days=30, max_results=5,
                        search_fn=fake_search, summarize_fn=fake_summary)
    assert report["status"] == "PASS"
    assert "làn du_phong_bac_thang lỗi" in report["topics"][0]["error"]
    assert "du_phong_bac_thang" in report["topics"][0]["lan_phu_loi"]


def test_markdown_report_core_va_du_phong_khong_bi_gan_nham_moi_vao_pubmed():
    """core_bo_sung/du_phong_bac_thang phải nằm trong danh sách «ngoài PubMed» của
    markdown_report — cùng luật đã áp cho scopus_bo_sung."""
    report = {
        "days": 30, "status": "PASS", "successful_topics": 1, "failed_topics": 0,
        "candidate_count": 2, "disclaimer": S.DISCLAIMER,
        "topics": [{
            "topic": "A", "query": "a", "status": "PASS", "error": "",
            "candidates": [
                S.asdict(S.Candidate(pmid="", publication_date="2026", title="Từ CORE",
                                     url="https://core/1", source="CORE (core.ac.uk)",
                                     tang="core_bo_sung")),
                S.asdict(S.Candidate(pmid="", publication_date="2026", title="Từ dự phòng",
                                     url="https://doi.org/10.1/z", source="Dự phòng: consensus",
                                     tang="du_phong_bac_thang")),
            ],
        }],
    }
    md = S.markdown_report(report)
    assert "mới vào PubMed" not in md


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


def test_detect_authority_source_uspstf_khong_bi_jama_che_khuat():
    """Vá 14/09/2026 (workflow kiểm tra toàn diện, xác nhận sống qua Europe PMC:
    14/15 USPSTF Recommendation Statement thật đăng trên JAMA): trước bản vá,
    detect_authority_source duyệt TRUSTED_SOURCE_ALIASES theo thứ tự dict và trả
    khớp ĐẦU TIÊN — "jama" đứng trước "uspstf" nên MỌI USPSTF Statement đăng trên
    JAMA (gần như toàn bộ từ 2017) luôn bị gán nhãn "JAMA", không bao giờ
    "USPSTF". Đồng thời alias cũ "u.s. preventive services task force" (có dấu
    chấm) không khớp cách viết thật "US..." (không dấu chấm) trên PubMed/JAMA."""
    titre_that = [
        "Screening for Breast Cancer: US Preventive Services Task Force Recommendation Statement",
        "Screening for Colorectal Cancer: US Preventive Services Task Force Recommendation Statement",
        "Screening for Syphilis Infection During Pregnancy: US Preventive Services Task Force Recommendation Statement",
    ]
    for t in titre_that:
        assert S.detect_authority_source("JAMA", t) == "USPSTF"
    # Tiêu đề không nhắc USPSTF thì JAMA vẫn phải là JAMA — không nới lỏng oan.
    assert S.detect_authority_source("JAMA", "Some random cardiology trial results") == "JAMA"


def test_detect_authority_source_to_chuc_uu_tien_truoc_tap_chi_da_nang():
    """Đối kháng: NEJM/Lancet/BMJ/Annals/Nature Medicine — mọi tạp chí trong
    _TAP_CHI_DA_NANG — cũng không được che khuất tổ chức thật sự phát hành, khi
    tiêu đề dẫn tên tổ chức đầy đủ (alias KHÔNG mơ hồ, so trên combined)."""
    assert S.detect_authority_source(
        "N Engl J Med",
        "A Statement From the American Heart Association on Heart Failure",
    ) == "ACC/AHA"
    assert S.detect_authority_source(
        "N Engl J Med", "NICE Guidance on Heart Failure Management",
    ) == "NICE"
    # Không nhắc tổ chức nào thì tạp chí đa năng vẫn phải trả đúng tên nó.
    assert S.detect_authority_source("N Engl J Med", "A trial of a new anticoagulant") == "NEJM"


def test_detect_authority_source_jama_neurology_khong_bi_gan_nham_aan():
    """Đối kháng: reordering ở trên không được làm "JAMA Neurology" (một tạp chí
    thuộc HỌ JAMA) bị alias mơ hồ "neurology" của AAN/Neurology giành mất — nếu
    không sẽ hồi quy đúng test_ba_nhan_tap_chi_bac_si_duyet_30_08 đã có từ trước."""
    assert S.detect_authority_source("JAMA Neurology", "BE-FAST validation") == "JAMA"


def test_search_europe_pmc_fallback_giu_dung_loc_thiet_ke(monkeypatch):
    """Vá 14/09/2026 (workflow kiểm tra toàn diện, tái hiện điều kiện lỗi THẬT —
    NCBI chặn IP dùng chung ngay trong lúc kiểm): search() rơi xuống
    search_europe_pmc() khi NCBI lỗi PHẢI chuyển tiếp loc_thiet_ke — thiếu dòng
    đó thì tầng "bắt cái mới nhất" (loc_thiet_ke=False, đúng tầng BH38 vá) im
    lặng biến thành tầng có lọc PUB_TYPE ngay khi đi qua đường dự phòng, tái
    diễn đúng lỗi BH38 (vứt bài chưa được MEDLINE gán publication type) qua một
    đường khác."""
    goi = {}

    def fake_fetch_json(_url):
        raise RuntimeError("simulate NCBI blocked")

    def fake_europe_pmc(query, days, retmax, loc_thiet_ke=True, mindate="", maxdate=""):
        goi["loc_thiet_ke"] = loc_thiet_ke
        goi["mindate"] = mindate
        goi["maxdate"] = maxdate
        return []

    monkeypatch.setattr(S, "search_europe_pmc", fake_europe_pmc)
    S.search("heart failure", 3, 10, fetch_json=fake_fetch_json,
             datetype="edat", loc_thiet_ke=False)
    assert goi == {"loc_thiet_ke": False, "mindate": "", "maxdate": ""}


def test_search_europe_pmc_ap_dung_dung_loc_thiet_ke_trong_truy_van():
    """search_europe_pmc(loc_thiet_ke=False) không được chèn cụm PUB_TYPE vào
    truy vấn gửi Europe PMC — trước bản vá, cụm này LUÔN có mặt vô điều kiện."""
    thay = {}

    def fake_fetch_json(url):
        thay["url"] = url
        return {"resultList": {"result": []}}

    S.search_europe_pmc("heart failure", 3, 10, fetch_json=fake_fetch_json, loc_thiet_ke=False)
    assert "PUB_TYPE" not in thay["url"]

    thay.clear()
    S.search_europe_pmc("heart failure", 3, 10, fetch_json=fake_fetch_json, loc_thiet_ke=True)
    assert "PUB_TYPE" in thay["url"]
