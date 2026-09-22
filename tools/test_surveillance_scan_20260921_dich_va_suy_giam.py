"""Khâu THU NHẬN chứng cứ — vá 21/09/2026 (đánh giá hoàn thiện, việc #3).

Ba lỗi cùng họ «công cụ vẫn chạy, vẫn báo PASS, nhưng thứ cần kiểm không được kiểm»:
  1. Đường dự phòng Europe PMC nhận NGUYÊN cú pháp thẻ PubMed ([pt] [ta] [ti]…) ⇒ tầng guideline/tổng quan/RCT
     và 4 làn thẩm quyền trả 0 GIẢ. Đo sống: 0/131 truy vấn tầng 1–3 trả kết quả (thô) → 62/131 (sau dịch).
  2. Suy giảm một phần vẫn ra PASS và con trỏ vẫn tiến ⇒ cửa sổ quét mất vĩnh viễn.
  3. Europe PMC thi thoảng trả bản RỖNG {"version":"6.9"} — đọc thành «0 kết quả» là 0 giả.
Ngoại tuyến 100%: mạng luôn là hàm giả tiêm vào.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_dich_suy_giam", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_dich_suy_giam"] = S
_sp.loader.exec_module(S)

# Các truy vấn THẬT trích từ EBM-Dashboards/watchlist.json (đủ 10 thẻ PubMed đang dùng).
TRUY_VAN_THAT = [
    '((type 2 diabetes treatment guidelines) AND (practice guideline[pt] OR guideline[pt] OR consensus development conference[pt])) OR ((Standards[ti] AND Care[ti] AND Diabetes[ti]))',
    '(type 2 diabetes treatment guidelines) AND (systematic review[pt] OR meta-analysis[pt])',
    '(type 2 diabetes treatment guidelines) AND randomized controlled trial[pt] AND (multicenter study[pt] OR "Lancet"[ta] OR "N Engl J Med"[ta] OR "JAMA"[ta])',
    '(chronic coronary syndrome[Title] OR coronary artery disease[Title] OR acute coronary syndrome[Title])',
    '(NICE[ti] OR "National Institute for Health and Care Excellence"[ad] OR "NICE guideline"[tw]) AND (guideline[pt] OR practice guideline[pt])',
    '("World Health Organization"[cn] OR "World Health Organization"[ad] OR "WHO guideline"[tw]) AND (guideline[pt] OR review[pt])',
    'dengue[ti] AND (adult[mh] OR outpatient*[tiab] OR ambulatory[tiab])',
    'drug safety alert recall guideline 2026[dp]',
]


@pytest.fixture(autouse=True)
def _ngoai_tuyen(monkeypatch):
    for ten in ("search_preprint_lane", "search_trials_lane", "search_scopus_lane"):
        monkeypatch.setattr(S, ten, lambda *a, **k: [])
    monkeypatch.setattr(S, "gan_do_tin_cay", lambda c: list(c))
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()
    yield
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()


# ── 1. Bộ dịch cú pháp ────────────────────────────────────────────────────────────────────────────
def test_dich_tung_the():
    d = S.dich_pubmed_sang_europepmc
    assert d("practice guideline[pt]") == 'PUB_TYPE:"practice guideline"'
    assert d('"Lancet"[ta]') == 'JOURNAL:"Lancet"'
    assert d("Standards[ti]") == "TITLE:Standards"
    assert d("chronic coronary syndrome[Title]") == 'TITLE:"chronic coronary syndrome"'
    assert d('"NICE guideline"[tw]') == '(TITLE:"NICE guideline" OR ABSTRACT:"NICE guideline")'
    assert d("outpatient*[tiab]") == "(TITLE:outpatient* OR ABSTRACT:outpatient*)"
    assert d('"National Institute for Health and Care Excellence"[ad]') == 'AFF:"National Institute for Health and Care Excellence"'
    assert d('"World Health Organization"[cn]') == 'AUTH:"World Health Organization"'
    assert d("adult[mh]") == 'MESH:"adult"'


def test_cum_nhieu_tu_tinh_tu_toan_tu_gan_nhat():
    """`randomized controlled trial[pt]` là MỘT cụm (không phải chỉ «trial»); chữ đứng trước AND không dính vào."""
    o = S.dich_pubmed_sang_europepmc("(asthma guideline) AND randomized controlled trial[pt]")
    assert 'PUB_TYPE:"randomized controlled trial"' in o
    assert "asthma guideline" in o and 'PUB_TYPE:"asthma' not in o


def test_the_ngay_dp_chi_ap_cho_nam_cuoi():
    o = S.dich_pubmed_sang_europepmc("drug safety alert recall guideline 2026[dp]")
    assert o == "drug safety alert recall guideline PUB_YEAR:2026"
    with pytest.raises(ValueError):
        S.dich_pubmed_sang_europepmc("recall[dp]")  # không phải năm ⇒ fail-closed, không đoán


def test_the_la_va_the_khong_co_cum_bi_tu_choi():
    with pytest.raises(ValueError):
        S.dich_pubmed_sang_europepmc("foo[xyz]")
    with pytest.raises(ValueError):
        S.dich_pubmed_sang_europepmc("AND [pt]")


def test_moi_truy_van_that_dich_xong_khong_con_the_pubmed():
    for q in TRUY_VAN_THAT:
        o = S.dich_pubmed_sang_europepmc(q)
        assert not re.search(r"\[[A-Za-z ]+\]", o), (q, o)
        assert o.count("(") == o.count(")")


def test_toan_bo_watchlist_that_dich_duoc_neu_co_du_lieu():
    """Chạy trên TOÀN BỘ truy vấn watchlist thật khi máy có EBM-Dashboards (ngoài git); vắng ⇒ bỏ qua có ghi chú."""
    wl = ROOT / "EBM-Dashboards" / "watchlist.json"
    if not wl.exists():
        pytest.skip("EBM-Dashboards/watchlist.json ngoài git — máy này không có")
    d = json.loads(wl.read_text(encoding="utf-8"))
    n = 0
    for t in d["topics"]:
        for q in (t.get("queries") or [{"query": t["query"]}]):
            o = S.dich_pubmed_sang_europepmc(q["query"])
            assert not re.search(r"\[[A-Za-z ]+\]", o), (t["topic"], o)
            n += 1
    assert n >= 100


# ── 2. Europe PMC nhận truy vấn ĐÃ DỊCH ───────────────────────────────────────────────────────────────
def test_search_europe_pmc_gui_truy_van_da_dich():
    thay: list[str] = []

    def fake(url: str) -> dict:
        thay.append(url)
        return {"hitCount": 1, "resultList": {"result": [{"pmid": "111"}]}}

    ids = S.search_europe_pmc('(asthma) AND "Lancet"[ta] AND practice guideline[pt]', 60, 5, fetch_json=fake)
    assert ids == ["111"]
    import urllib.parse as up
    q = up.parse_qs(up.urlparse(thay[0]).query)["query"][0]
    assert 'JOURNAL:"Lancet"' in q and 'PUB_TYPE:"practice guideline"' in q
    assert "[ta]" not in q and "[pt]" not in q, "thẻ PubMed lọt sang Europe PMC ⇒ trả 0 giả"
    assert "SRC:MED OR HAS_FT:Y" in q


def test_ban_rong_chi_co_version_khong_duoc_doc_thanh_khong_ket_qua():
    goi = {"n": 0}

    class Opener:
        def __call__(self, request, timeout=0):
            goi["n"] += 1
            return self

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'{"version": "6.9"}'

    with pytest.raises(RuntimeError, match="bản rỗng"):
        S.get_europe_pmc_json("https://x/y", retries=2, opener=Opener(), sleeper=lambda s: None)
    assert goi["n"] == 3, "bản rỗng phải được RETRY (lỗi thoáng qua), không đọc thành 0 kết quả"


def test_ban_hop_le_co_hitcount_bang_khong_van_la_khong_that():
    class Opener:
        def __call__(self, request, timeout=0):
            return self

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'{"version": "6.9", "hitCount": 0, "resultList": {"result": []}}'

    d = S.get_europe_pmc_json("https://x/y", retries=0, opener=Opener(), sleeper=lambda s: None)
    assert d["hitCount"] == 0


# ── 3. NCBI chặn: nhận diện ngay, không retry, không hỏi lại ───────────────────────────────────────────
def test_trang_chan_ncbi_ne_khong_retry_va_bat_co_ngat_mach():
    goi = {"n": 0}

    class Opener:
        def __call__(self, request, timeout=0):
            goi["n"] += 1
            return self

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"<html><title>WWW Error Blocked Diagnostic</title>Your access has been blocked for possible abuse</html>"

    with pytest.raises(S.NCBIBiChan):
        S.get_json("https://eutils.ncbi.nlm.nih.gov/x", retries=3, opener=Opener(), sleeper=lambda s: None)
    assert goi["n"] == 1, "trang chặn trả HTTP 200 — retry chỉ tốn ~46s/truy vấn mà không bao giờ tự hết"
    assert S._NCBI_CHAN["bi_chan"] is True


def test_da_bi_chan_thi_search_khong_hoi_ncbi_nua_va_ghi_suy_giam():
    S._NCBI_CHAN["bi_chan"] = True
    thay: list[str] = []

    def epmc(url: str) -> dict:
        thay.append(url)
        return {"hitCount": 1, "resultList": {"result": [{"pmid": "222"}]}}

    ids = S.search("(x) AND guideline[pt]", 30, 5, fallback_fetch_json=epmc)   # fetch_json mặc định = get_json
    assert ids == ["222"] and thay
    assert any("chặn" in x for x in S._SUY_GIAM)


# ── 4. Suy giảm ⇒ PASS_DEGRADED, con trỏ KHÔNG tiến, báo cáo nói thẳng ─────────────────────────────────
def _tim_ung_vien(ids):
    return [S.Candidate(i, "2026 Sep 20", f"Bài {i}", f"https://pubmed.ncbi.nlm.nih.gov/{i}/") for i in ids]


def _search_ncbi_hong_roi_du_phong(query, days, retmax, **kw):
    def ncbi(_url):
        raise RuntimeError("NCBI timeout")

    def epmc(_url):
        return {"hitCount": 1, "resultList": {"result": [{"pmid": "333"}]}}

    return S.search(query, days, retmax, fetch_json=ncbi, fallback_fetch_json=epmc, **kw)


def test_chu_de_suy_giam_khong_tien_con_tro_va_bao_partial():
    cursor = {"Suy giảm": "2026-09-07", "Bình thường": "2026-09-07"}
    topics = [{"topic": "Suy giảm", "query": "hf guideline[pt]"}, {"topic": "Bình thường", "query": "copd"}]

    def search_fn(query, days, retmax, **kw):
        if query.startswith("hf"):
            return _search_ncbi_hong_roi_du_phong(query, days, retmax, **kw)
        return ["444"]

    rep = S.run_scan(topics, days=90, max_results=5, cursor=cursor, search_fn=search_fn,
                     summarize_fn=_tim_ung_vien)
    kq = {t["topic"]: t for t in rep["topics"]}
    assert kq["Suy giảm"]["status"] == "PASS_DEGRADED" and kq["Suy giảm"]["suy_giam"]
    assert kq["Bình thường"]["status"] == "PASS"
    assert rep["status"] == "PARTIAL" and rep["degraded_topics"] == 1 and rep["failed_topics"] == 1
    assert cursor["Suy giảm"] == "2026-09-07", "chủ đề suy giảm KHÔNG được tiến con trỏ (mất cửa sổ vĩnh viễn)"
    assert cursor["Bình thường"] != "2026-09-07", "chủ đề bình thường vẫn tiến"


def test_toan_bo_suy_giam_khong_phai_pass():
    """Tình huống W36/W37: mọi chủ đề qua dự phòng ⇒ tuyệt đối không PASS."""
    rep = S.run_scan([{"topic": "A", "query": "q[pt]"}], days=30, max_results=3, cursor={},
                     search_fn=_search_ncbi_hong_roi_du_phong, summarize_fn=_tim_ung_vien)
    assert rep["status"] != "PASS" and rep["degraded_topics"] == 1


def test_bao_cao_markdown_noi_thang_suy_giam_va_khong_dien_giai_rong_la_khong_co_gi_moi():
    rep = S.run_scan([{"topic": "A", "query": "q[pt]"}], days=30, max_results=3, cursor={},
                     search_fn=_search_ncbi_hong_roi_du_phong, summarize_fn=lambda ids: [])
    md = S.markdown_report(rep)
    assert "SUY GIẢM" in md and "KHÔNG được đọc" in md


def test_ghi_chu_lan_phu_khi_pass_van_duoc_in():
    """Trước đây `error` của chủ đề PASS (làn phụ lỗi) không bao giờ in ra ⇒ mất im lặng."""
    def scopus_hong(*a, **k):
        raise RuntimeError("scopus 403")

    S.search_scopus_lane = scopus_hong
    rep = S.run_scan([{"topic": "A", "query": "q"}], days=30, max_results=3, cursor={},
                     search_fn=lambda q, d, m, **k: ["1"], summarize_fn=_tim_ung_vien)
    assert rep["topics"][0]["status"] == "PASS"
    assert "làn scopus lỗi" in S.markdown_report(rep)


# ── 5. Loại thiết kế từ đường dự phòng ────────────────────────────────────────────────────────────
def test_pubtype_europe_pmc_ca_hai_dang():
    assert S._pubtype_europe_pmc({"pubTypeList": {"pubType": ["Journal Article", "Systematic Review"]}}) == ("Journal Article", "Systematic Review")
    assert S._pubtype_europe_pmc({"pubType": "Journal Article; Practice Guideline"}) == ("Journal Article", "Practice Guideline")
    assert S._pubtype_europe_pmc({}) == ()


def test_summarize_dp_dien_pubtype_de_khong_bi_gan_nhan_moi_vao_pubmed_sai():
    def epmc(_url):
        return {"hitCount": 1, "resultList": {"result": [{"pmid": "555", "title": "T", "journalTitle": "J",
                                                           "pubType": "Journal Article; Systematic Review"}]}}

    c = S.summarize_europe_pmc(["555"], fetch_json=epmc)
    assert c and "Systematic Review" in c[0].pubtype


# ── 6. --since kèm --khong-cursor không còn bị bỏ qua im lặng ───────────────────────────────────────────
def test_since_va_khong_cursor_cung_hoat_dong_va_khong_ghi_con_tro(monkeypatch):
    thay = {}
    monkeypatch.setattr(S, "gianh_khoa", lambda *a, **k: (True, ""))
    monkeypatch.setattr(S, "tra_khoa", lambda: None)
    monkeypatch.setattr(S, "load_watchlist", lambda p: [{"topic": "T", "query": "q"}])
    monkeypatch.setattr(S, "ghi_alert", lambda *a, **k: None)
    monkeypatch.setattr(S, "doc_cursor", lambda: (_ for _ in ()).throw(AssertionError("--khong-cursor không được ĐỌC con trỏ")))

    def ghi_spy(cur):
        thay["ghi"] = dict(cur)

    monkeypatch.setattr(S, "ghi_cursor", ghi_spy)

    def run_fake(topics, **kw):
        thay["cursor"] = dict(kw["cursor"])
        return {"kind": "x", "status": "PASS", "days": 90, "successful_topics": 1, "failed_topics": 0,
                "degraded_topics": 0, "topic_count": 1, "candidate_count": 0, "topics": [], "disclaimer": "d"}

    monkeypatch.setattr(S, "run_scan", run_fake)
    rc = S.main(["--since", "2026-08-21", "--khong-cursor"])
    assert rc == 0
    assert thay["cursor"] == {"T": "2026-08-21"}, "--since phải có hiệu lực kể cả khi --khong-cursor"
    assert "ghi" not in thay, "--khong-cursor tuyệt đối không ghi con trỏ dùng chung"


# ── 5. Vòng phản biện độc lập 21/09 (tái hiện được) ─────────────────────────────────────────────────────
def test_bo_dich_fail_closed_voi_nhay_ngoac_lech_va_nhay_long():
    for xau in ('x[pt', '"a b[pt]', '(a AND b[pt]', '"a b" c[ti]'):
        with pytest.raises(ValueError):
            S.dich_pubmed_sang_europepmc(xau)
    # ca đúng vẫn dịch được
    assert S.dich_pubmed_sang_europepmc('"a b"[ti]') == 'TITLE:"a b"'


def test_esearch_http200_mang_khoa_error_la_loi_khong_phai_0_ket_qua():
    for ban_loi in ({"error": "rate limit exceeded"}, {"esearchresult": {"ERROR": "Invalid db"}}, {"header": {}}, []):
        S._SUY_GIAM.clear()
        ids = S.search("x[pt]", 30, 5, fetch_json=lambda _u, b=ban_loi: b,
                       fallback_fetch_json=lambda _u: {"hitCount": 1, "resultList": {"result": [{"pmid": "777"}]}})
        assert ids == ["777"], f"bản lỗi {ban_loi!r} phải đi đường dự phòng, không thành []"
        assert S._SUY_GIAM, f"bản lỗi {ban_loi!r} phải ghi SUY GIẢM"


def test_esearch_hop_le_bang_khong_van_la_khong_that():
    S._SUY_GIAM.clear()
    ids = S.search("x[pt]", 30, 5, fetch_json=lambda _u: {"esearchresult": {"count": "0", "idlist": []}})
    assert ids == [] and not S._SUY_GIAM


def test_esummary_loi_ghi_suy_giam_va_dung_duong_du_phong(monkeypatch):
    goi = {}
    monkeypatch.setattr(S, "summarize_europe_pmc", lambda ids, **k: goi.setdefault("ids", list(ids)) and [])
    S._SUY_GIAM.clear()
    S.summarize(["111", "222"], fetch_json=lambda _u: {"error": "x"})
    assert goi["ids"] == ["111", "222"]
    assert any("esummary" in x for x in S._SUY_GIAM)


def test_europe_pmc_thieu_ban_ghi_bi_ghi_suy_giam_khong_im_lang():
    S._SUY_GIAM.clear()
    ra = S.summarize_europe_pmc(["111", "222"], fetch_json=lambda _u: {"resultList": {"result": [
        {"pmid": "111", "title": "Có bản ghi", "journalTitle": "J", "firstPublicationDate": "2026-09-20"}]}})
    assert [c.pmid for c in ra] == ["111"]
    assert any("1/2" in x and "Europe PMC" in x for x in S._SUY_GIAM), "PMID mới chưa được Europe PMC lập chỉ mục bị bỏ IM LẶNG"


def test_chu_de_esummary_suy_giam_thanh_pass_degraded_va_con_tro_dung_yen(monkeypatch):
    cursor = {"T": "2026-09-01"}

    def summarize_hong(ids):
        S._SUY_GIAM.append("esummary NCBI lỗi (RuntimeError) — tóm tắt ứng viên bằng Europe PMC")
        return []

    rep = S.run_scan([{"topic": "T", "query": "q"}], days=30, max_results=3, cursor=cursor,
                     search_fn=lambda q, d, m, **k: ["1", "2"], summarize_fn=summarize_hong)
    assert rep["topics"][0]["status"] == "PASS_DEGRADED"
    assert cursor["T"] == "2026-09-01", "mất ứng viên ở khâu tóm tắt mà con trỏ vẫn tiến ⇒ cửa sổ quét mất vĩnh viễn"


def test_since_hep_hon_con_tro_khong_duoc_day_con_tro_tien(monkeypatch):
    ghi = {}
    monkeypatch.setattr(S, "gianh_khoa", lambda *a, **k: (True, ""))
    monkeypatch.setattr(S, "tra_khoa", lambda: None)
    monkeypatch.setattr(S, "load_watchlist", lambda p: [{"topic": "T", "query": "q"}])
    monkeypatch.setattr(S, "ghi_alert", lambda *a, **k: None)
    monkeypatch.setattr(S, "doc_cursor", lambda: {"T": "2026-09-01", "Khác": "2026-08-01"})
    monkeypatch.setattr(S, "ghi_cursor", lambda cur: ghi.update(cur))

    def run_fake(topics, **kw):
        kw["cursor"]["T"] = "2026-09-21"      # mô phỏng chủ đề PASS ⇒ run_scan tiến con trỏ tới hôm nay
        return {"kind": "x", "status": "PASS", "days": 30, "successful_topics": 1, "failed_topics": 0,
                "degraded_topics": 0, "topic_count": 1, "candidate_count": 0, "topics": [], "disclaimer": "d"}

    monkeypatch.setattr(S, "run_scan", run_fake)
    assert S.main(["--since", "2026-09-20"]) == 0
    # Vá 22/09/2026 (review:thu-nhan #7): main() nay CHỈ gọi ghi_cursor khi nội dung thật sự đổi.
    # Ở kịch bản này "T" bị rollback về đúng 2026-09-01 (không đổi so với trước) và "Khác" không hề
    # chạm tới ⇒ cursor == con_tro_truoc ⇒ main() có thể bỏ qua ghi HOÀN TOÀN (đúng ý — tránh mtime
    # nhảy vô ích khi không có gì mới). Bất biến CỐT LÕI vẫn được giữ: NẾU có ghi thì "T" tuyệt đối
    # không được là "2026-09-21" (giá trị PASS_DEGRADED cũ mô phỏng); ghi_cursor không được gọi ở
    # đây là bằng chứng TỐT hơn, không phải hồi quy.
    assert ghi.get("T", "2026-09-01") == "2026-09-01", "--since hẹp hơn con trỏ bỏ qua [09-01, 09-20) — không được ghi tiến"
    assert ghi.get("Khác", "2026-08-01") == "2026-08-01", "chủ đề không thuộc lượt quét giữ nguyên"
    assert ghi == {}, "nội dung con trỏ không đổi ⇒ ghi_cursor không được gọi (chốt mtime bất biến)"
