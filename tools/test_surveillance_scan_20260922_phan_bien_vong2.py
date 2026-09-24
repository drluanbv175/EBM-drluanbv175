"""Khâu THU NHẬN chứng cứ — vá 22/09/2026, theo 5 phát hiện MEDIUM/HIGH của vòng phản biện đối kháng
vòng 2 (dimension review:thu-nhan). Ngoại tuyến 100%: mạng luôn là hàm giả tiêm vào.

  1. HIGH  — làn preprint tra Crossref bằng CHÍNH fetch_json của Europe PMC (guard
     hitCount/resultList) ⇒ MỌI lần tra `is-preprint-of` thất bại, nhãn "ĐÃ CÓ BẢN BÌNH DUYỆT"
     biến mất. Sửa: hàm `get_crossref_json` riêng, không mang guard đó.
  2. MEDIUM — trang chặn Cloudflare của ClinicalTrials.gov bị đọc nhầm thành NCBI chặn (dùng
     chung get_json), lây cờ toàn cục sang mọi chủ đề khác trong lượt quét. Sửa: `_la_host_ncbi`.
  3/4. MEDIUM — esearchresult thiếu idlist/count, hoặc bị NCBI cắt ở retmax, không được phát hiện.
  5. MEDIUM — chủ đề hỏng giữa chừng (sau khi đã thêm PMID vào all_pmids) làm PMID đó bị coi là
     "đã thấy" cho một chủ đề KHÁC chia sẻ PMID, dù chủ đề đầu chưa từng báo cáo nó ở đâu.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_phan_bien_v2", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_phan_bien_v2"] = S
_sp.loader.exec_module(S)

# Giữ tham chiếu HÀM GỐC trước khi fixture autouse _sach monkeypatch S.search_preprint_lane/
# search_trials_lane/search_scopus_lane thành lambda: []. Test kiểm HÀNH VI THẬT của các hàm
# này phải gọi tham chiếu GỐC, không phải S.search_preprint_lane (đã bị chặn cho mọi test).
_SEARCH_PREPRINT_LANE_GOC = S.search_preprint_lane


@pytest.fixture(autouse=True)
def _sach(monkeypatch):
    # run_scan có 3 làn phụ gọi MẠNG THẬT (preprint/ClinicalTrials.gov/Scopus) khi không được
    # tiêm search_fn riêng cho chúng — chặn ở mọi test trong file này (khuôn theo
    # test_evidence_surveillance_scan.py::_chan_lan_goi_mang), muốn kiểm riêng một làn thì
    # test đó tự gọi thẳng hàm, không qua run_scan().
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    # 22/09/2026: chặn nốt hai làn mới — có thể gọi mạng thật/tốn hạn mức tháng nếu máy
    # chạy test đã bật ENABLE_CORE/ENABLE_CONSENSUS/ENABLE_SERPAPI_SCHOLAR thật.
    monkeypatch.setattr(S, "search_core_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lambda *a, **k: ([], ""))
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()
    yield
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()


class _Opener:
    """Opener giả trả một body cố định, đếm số lần gọi."""

    def __init__(self, body: bytes):
        self.body = body
        self.n = 0

    def __call__(self, request, timeout=0):
        self.n += 1
        self.request = request
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self.body


# ── 1. Crossref không còn dùng chung guard hitCount/resultList của Europe PMC ──────────────────
def test_crossref_dung_ham_rieng_khong_bi_guard_europe_pmc_chan():
    """Payload Crossref THẬT ({status, message-type, message}) không bao giờ có
    hitCount/resultList — get_crossref_json không được đòi hai khoá đó."""
    body = (b'{"status":"ok","message-type":"work","message":'
            b'{"relation":{"is-preprint-of":[{"id":"10.1001/jama.2026.1"}]}}}')
    op = _Opener(body)
    d = S.get_crossref_json("https://api.crossref.org/works/10.1101/x", retries=0, opener=op,
                             sleeper=lambda s: None)
    assert d["message"]["relation"]["is-preprint-of"][0]["id"] == "10.1001/jama.2026.1"
    assert op.n == 1, "payload hợp lệ, không được retry"


def test_search_preprint_lane_gan_nhan_da_xuat_ban_qua_fetch_crossref_rieng():
    def epmc(_url):
        return {"resultList": {"result": [
            {"id": "PPR1", "doi": "10.1101/2026.09.01.x", "title": "Preprint X",
             "firstPublicationDate": "2026-09-01"},
        ]}}

    goi_crossref = {"n": 0}

    def crossref(url):
        goi_crossref["n"] += 1
        assert "10.1101" in url
        return {"message": {"relation": {"is-preprint-of": [{"id": "10.1001/jama.2026.1"}]}}}

    ra = _SEARCH_PREPRINT_LANE_GOC("heart failure", 30, 6, fetch_json=epmc, fetch_crossref=crossref)
    assert len(ra) == 1
    assert "ĐÃ CÓ BẢN BÌNH DUYỆT" in ra[0].title
    assert "10.1001/jama.2026.1" in ra[0].title
    assert goi_crossref["n"] == 1, "chỉ 1 lần gọi Crossref/preprint, không retry thừa"


def test_search_preprint_lane_khong_qua_fetch_json_khi_tra_crossref():
    """Đưa fetch_json (Europe PMC) một guard chặt sẽ raise nếu bị gọi nhầm cho Crossref —
    xác nhận đường gọi Crossref hoàn toàn tách khỏi fetch_json."""
    def epmc(_url):
        return {"resultList": {"result": [
            {"id": "PPR2", "doi": "10.1101/x", "title": "Preprint Y",
             "firstPublicationDate": "2026-09-01"},
        ]}}

    def crossref_rong(_url):
        return {"message": {}}  # không có relation ⇒ không gắn nhãn, nhưng KHÔNG raise

    ra = _SEARCH_PREPRINT_LANE_GOC("x", 30, 6, fetch_json=epmc, fetch_crossref=crossref_rong)
    assert len(ra) == 1
    assert "ĐÃ CÓ BẢN BÌNH DUYỆT" not in ra[0].title
    assert ra[0].title == "Preprint Y"


# ── 2. Trang chặn của nguồn KHÁC NCBI (ClinicalTrials.gov) không lây cờ toàn cục ────────────────
def test_trang_chan_clinicaltrials_khong_duoc_gan_co_ncbi():
    op = _Opener(b"<html><title>Attention Required!</title>Sorry, you have been blocked</html>")
    with pytest.raises(RuntimeError) as exc_info:
        S.get_json("https://clinicaltrials.gov/api/v2/studies?query.cond=x",
                    retries=2, opener=op, sleeper=lambda s: None)
    assert not isinstance(exc_info.value, S.NCBIBiChan)
    assert S._NCBI_CHAN["bi_chan"] is False, (
        "trang chặn của ClinicalTrials.gov không được lây cờ NCBI sang các chủ đề khác"
    )
    assert op.n == 1, "trang chặn không tự hết bằng cách hỏi lại — không retry, dù không phải NCBI"


def test_trang_chan_ncbi_that_van_gan_co_dung_nhu_cu():
    op = _Opener(b"<html>Access Denied ... possible abuse</html>")
    with pytest.raises(S.NCBIBiChan):
        S.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?x",
                    retries=2, opener=op, sleeper=lambda s: None)
    assert S._NCBI_CHAN["bi_chan"] is True


def test_chan_clinicaltrials_khong_lam_chu_de_sau_bo_qua_ncbi(monkeypatch):
    """Kịch bản đúng finding: chủ đề A dùng ClinicalTrials.gov (qua get_json, đúng chữ ký thật của
    search_trials_lane) bị chặn Cloudflare; chủ đề B (chạy SAU trong cùng lượt) vẫn phải hỏi được
    NCBI thật, không bị chẩn đoán sai «NCBI đang chặn IP»."""
    def fake_trials_lane(topic, days, retmax):
        op = _Opener(b"<html>Attention Required! Sorry, you have been blocked</html>")
        S.get_json("https://clinicaltrials.gov/api/v2/studies?query.cond=x", retries=0, opener=op,
                   sleeper=lambda s: None)
        return []  # không tới đây — get_json raise trước

    monkeypatch.setattr(S, "search_trials_lane", fake_trials_lane)

    def search_fn(query, days, retmax, **kw):
        return ["111"] if query == "qB" else []

    def summarize_fn(ids):
        return [S.Candidate(i, "2026-09-20", f"Bài {i}", f"https://pubmed.ncbi.nlm.nih.gov/{i}/") for i in ids]

    topics = [{"topic": "A", "query": "qA"}, {"topic": "B", "query": "qB"}]
    rep = S.run_scan(topics, days=30, max_results=6, search_fn=search_fn, summarize_fn=summarize_fn)
    by_topic = {t["topic"]: t for t in rep["topics"]}
    assert "làn clinicaltrials lỗi" in by_topic["A"]["error"]
    # B phải hỏi được NCBI thật (không bị fallback oan do cờ NCBI bị A lây nhầm)
    assert [c["pmid"] for c in by_topic["B"]["candidates"]] == ["111"]
    assert S._NCBI_CHAN["bi_chan"] is False


# ── 3/4. esearchresult thiếu idlist/count, hoặc bị cắt ở retmax ─────────────────────────────────
def test_esearchresult_rong_khong_co_idlist_count_roi_xuong_du_phong():
    def ncbi_rong(_url):
        return {"header": {}, "esearchresult": {}}

    def epmc(_url):
        return {"hitCount": 1, "resultList": {"result": [{"pmid": "999"}]}}

    ids = S.search("x", 30, 5, fetch_json=ncbi_rong, fallback_fetch_json=epmc)
    assert ids == ["999"], "esearchresult thiếu idlist/count phải rơi xuống dự phòng, không phải []"
    assert any("thiếu idlist/count" in x for x in S._SUY_GIAM)


def test_esearchresult_errorlist_fieldsnotfound_roi_xuong_du_phong():
    def ncbi_loi_truong(_url):
        return {"esearchresult": {"count": "0", "idlist": [],
                                   "errorlist": {"fieldsnotfound": ["pt"]}}}

    def epmc(_url):
        return {"hitCount": 1, "resultList": {"result": [{"pmid": "888"}]}}

    ids = S.search("x[pt]", 30, 5, fetch_json=ncbi_loi_truong, fallback_fetch_json=epmc)
    assert ids == ["888"]
    assert any("không nhận ra thẻ" in x for x in S._SUY_GIAM)


def test_esearchresult_hop_le_khong_co_errorlist_khong_bi_anh_huong():
    """Đối chứng: esearchresult hợp lệ, không errorlist/warninglist — vẫn PASS bình thường."""
    def ncbi_ok(_url):
        return {"esearchresult": {"count": "1", "idlist": ["777"]}}

    ids = S.search("x", 30, 5, fetch_json=ncbi_ok)
    assert ids == ["777"]
    assert S._SUY_GIAM == []


def test_esearch_vuot_tran_chi_ghi_chu_khong_suy_giam():
    """ĐỔI 24/09/2026 (phương án B, bác sĩ chọn): luật 22/09 ghi «bị cắt ở retmax» vào _SUY_GIAM ⇒ chủ đề
    suy giảm + con trỏ đứng yên. Quét lại vẫn chỉ trả các bản MỚI NHẤT nên không thu hồi được gì — chỉ làm
    chủ đề suy giảm mãi (12/47 chủ đề ở W39) và quét lô dừng. Nay vượt trần chỉ GHI CHÚ (_VUOT_TRAN)."""
    S._VUOT_TRAN.clear()

    def ncbi_cat(_url):
        return {"esearchresult": {"count": "57", "idlist": ["1", "2", "3", "4", "5", "6"]}}

    ids = S.search("x", 45, 6, fetch_json=ncbi_cat)
    assert ids == ["1", "2", "3", "4", "5", "6"], "vẫn trả đủ id nhận được, chỉ THÊM ghi chú"
    assert any("vượt trần lấy" in x and "6/57" in x for x in S._VUOT_TRAN)
    assert S._SUY_GIAM == [], "vượt trần KHÔNG được làm chủ đề suy giảm"


def test_esearch_khong_cat_thi_khong_ghi_suy_giam():
    S._VUOT_TRAN.clear()

    def ncbi_du(_url):
        return {"esearchresult": {"count": "2", "idlist": ["1", "2"]}}

    ids = S.search("x", 45, 6, fetch_json=ncbi_du)
    assert ids == ["1", "2"]
    assert S._SUY_GIAM == []
    assert S._VUOT_TRAN == []


# ── 5. Chủ đề hỏng giữa chừng không được để lại PMID "ma" chiếm chỗ chủ đề khác ────────────────
def test_pmid_ma_khong_lam_mat_ung_vien_chu_de_khac():
    def fake_search(query, days, retmax, **kw):
        if query == "q1":
            return ["111"]
        if query == "q2":
            raise RuntimeError("tầng 2 hỏng — không phải TypeError nên không lùi chữ ký cũ")
        if query == "qb":
            return ["111"]
        return []

    def fake_summarize(ids):
        return [S.Candidate(i, "2026-09-20", f"Bài {i}", "") for i in ids]

    topics = [
        {"topic": "A", "query": "q1", "queries": [
            {"tang": "t1", "query": "q1"},
            {"tang": "t2", "query": "q2"},
        ]},
        {"topic": "B", "query": "qb"},
    ]
    rep = S.run_scan(topics, days=30, max_results=10, search_fn=fake_search, summarize_fn=fake_summarize)
    by_topic = {t["topic"]: t for t in rep["topics"]}
    assert by_topic["A"]["status"] == "FAIL"
    assert by_topic["A"]["candidates"] == []
    assert [c["pmid"] for c in by_topic["B"]["candidates"]] == ["111"], (
        "PMID 111 chưa hề xuất hiện trong báo cáo nào (A hỏng) — B phải nhận được nó, "
        "không bị dedup bởi một chủ đề đã FAIL"
    )
    assert rep["candidate_count"] == 1, "candidate_count không được thổi phồng bởi PMID ma của A"


def test_chu_de_thanh_cong_van_dedup_binh_thuong_giua_hai_chu_de():
    """Đối chứng: khi CẢ HAI chủ đề đều thành công và chia sẻ PMID, dedup vẫn phải hoạt động —
    bản vá #5 chỉ phục hồi PMID của chủ đề HỎNG, không được làm mất dedup của chủ đề thường."""
    def fake_search(query, days, retmax, **kw):
        return ["222"]

    def fake_summarize(ids):
        return [S.Candidate(i, "2026-09-20", f"Bài {i}", "") for i in ids]

    topics = [{"topic": "A", "query": "qa"}, {"topic": "B", "query": "qb"}]
    rep = S.run_scan(topics, days=30, max_results=10, search_fn=fake_search, summarize_fn=fake_summarize)
    by_topic = {t["topic"]: t for t in rep["topics"]}
    assert [c["pmid"] for c in by_topic["A"]["candidates"]] == ["222"]
    assert by_topic["B"]["candidates"] == [], "B thấy PMID 222 đã có (A thành công thật) ⇒ dedup đúng"
    assert rep["candidate_count"] == 1
