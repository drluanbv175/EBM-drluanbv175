"""Cổng TRƯỚC khi leo thang dự phòng Consensus → SerpApi của vòng quét tuần (vá 27/09/2026).

Đo trước lượt quét tuần đầu tiên có làn dự phòng: cổng đủ-chứng-cứ của engine chấm ứng viên scanner (chỉ tiêu đề ·
tạp chí · ngày · PMID · URL) ra tier C, điểm 0–6 ⇒ LUÔN «thiếu» ⇒ mọi chủ đề leo thang, kể cả khi NCBI lỗi, và gửi TÊN
chủ đề tiếng Việt cho nguồn tiếng Anh. Test không gọi mạng: làn dự phòng là hàm theo dõi.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_leo_thang_2709", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_leo_thang_2709"] = S  # @dataclass tra sys.modules lúc dựng lớp — đăng ký TRƯỚC exec
_sp.loader.exec_module(S)


@pytest.fixture()
def goi(monkeypatch):
    """Kín mạng + ghi lại MỌI lần làn dự phòng được gọi (đối số đầu = truy vấn gửi đi)."""
    for ten in ("search_preprint_lane", "search_trials_lane", "search_scopus_lane", "search_core_lane"):
        monkeypatch.setattr(S, ten, lambda *a, **k: [])
    monkeypatch.setattr(S, "gan_do_tin_cay", lambda ds: list(ds))
    monkeypatch.setattr(S, "_pmid_da_co_trong_kho", lambda: set())
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()
    S._VUOT_TRAN.clear()
    da_goi: list[str] = []

    def theo_doi(truy_van, unique, retmax, **kw):
        da_goi.append(truy_van)
        return [], ""
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", theo_doi)
    return da_goi


def _uv(pmid, pubtype=()):
    return S.Candidate(pmid=pmid, publication_date="2026", title="Một bài báo", pubtype=tuple(pubtype),
                       url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")


def _chay(topic: dict, pubtype_cua: dict | None = None, suy_giam: bool = False):
    def search_fn(query, days, retmax, **kw):
        if suy_giam:
            S._SUY_GIAM.append("NCBI lỗi (HTTP 500) — truy vấn này chạy bằng Europe PMC dự phòng")
        return ["11", "12", "13"]

    def summarize_fn(ids):
        return [_uv(p, (pubtype_cua or {}).get(p, ("Journal Article",))) for p in ids]
    return S.run_scan([topic], days=30, max_results=6, cursor={}, search_fn=search_fn, summarize_fn=summarize_fn)


def test_ncbi_loi_thi_khong_leo_thang_va_noi_ro(goi):
    rep = _chay({"topic": "Hypertension", "query": "q", "truy_van_du_phong": "hypertension treatment"}, suy_giam=True)
    assert goi == [], "NCBI lỗi mà vẫn gọi Consensus/SerpApi — nguồn lõi sập thì phải CHƯA KẾT LUẬN, không leo thang"
    assert "KHÔNG leo thang" in rep["topics"][0]["error"]
    assert rep["du_phong_khong_leo_thang"] == {"ncbi_loi": 1}


def test_du_bai_manh_theo_loai_xuat_ban_that_thi_khong_leo_thang(goi):
    manh = {"11": ("Practice Guideline",), "12": ("Systematic Review",), "13": ("Randomized Controlled Trial",)}
    rep = _chay({"topic": "Hypertension", "query": "q", "truy_van_du_phong": "hypertension treatment"}, manh)
    assert goi == []
    assert rep["du_phong_khong_leo_thang"] == {"du_bai_manh": 1}


def test_ten_tieng_viet_khong_co_truy_van_tieng_anh_thi_khong_leo_thang(goi):
    rep = _chay({"topic": "Đái tháo đường type 2 — điều trị", "query": "q"})
    assert goi == [], "gửi tên chủ đề tiếng Việt cho nguồn tiếng Anh là đốt hạn mức vô ích"
    assert rep["du_phong_khong_leo_thang"] == {"chua_co_truy_van_tieng_anh": 1}


def test_thieu_bai_manh_va_co_truy_van_tieng_anh_thi_leo_thang_bang_truy_van_do(goi):
    _chay({"topic": "Đái tháo đường type 2 — điều trị", "query": "q", "truy_van_du_phong": "type 2 diabetes treatment"})
    assert goi == ["type 2 diabetes treatment"], "phải gửi TRUY VẤN tiếng Anh, không phải tên chủ đề"


def test_ten_ascii_van_leo_thang_nhu_cu_khi_thieu(goi):
    """Tương thích ngược: chủ đề tên thuần ASCII (không khai truy_van_du_phong) vẫn leo thang khi thiếu."""
    _chay({"topic": "Hypertension", "query": "q"})
    assert goi == ["Hypertension"]


def test_truy_van_du_phong_khai_trong_watchlist_toi_duoc_cong(goi, tmp_path):
    """Đường SẢN XUẤT: watchlist → `load_watchlist` → `run_scan`. Hàm nạp dựng lại từng mục — khoá không chép là mất."""
    wl = tmp_path / "watchlist.json"
    wl.write_text(json.dumps({"topics": [
        {"topic": "Tăng huyết áp — điều trị", "query": "q1", "truy_van_du_phong": "  hypertension treatment  "},
        {"topic": "Gút", "query": "q2", "truy_van_du_phong": "   "},
    ]}, ensure_ascii=False), encoding="utf-8")
    chu_de = S.load_watchlist(wl)
    assert chu_de[0]["truy_van_du_phong"] == "hypertension treatment"
    assert "truy_van_du_phong" not in chu_de[1], "chuỗi trắng không phải truy vấn — không được khai là có"
    _chay(chu_de[0])
    assert goi == ["hypertension treatment"]


def test_hai_bai_manh_chua_du_nguong_van_leo_thang(goi):
    manh = {"11": ("Practice Guideline",), "12": ("Meta-Analysis",)}
    _chay({"topic": "Hypertension", "query": "q", "truy_van_du_phong": "hypertension treatment"}, manh)
    assert goi == ["hypertension treatment"], f"chỉ 2 < {S.NGUONG_BAI_MANH_KHONG_LEO_THANG} bài mạnh — vẫn phải leo thang"


def test_lan_du_phong_mang_moc_ngay_nhu_cac_lan_khac(monkeypatch):
    """Vá 27/09 (lượt 2): làn dự phòng gọi Consensus/SerpApi KHÔNG kèm mốc ngày ⇒ tìm MỌI năm ⇒ vòng quét tuần nhận lại
    bài cũ «liên quan nhất mọi thời» mỗi tuần. Đi đường thật run_scan → bo_sung_du_phong_lane → bo_sung_fn: phải mang
    since_date = hôm nay − days (UTC), như làn Scopus/CORE."""
    for ten in ("search_preprint_lane", "search_trials_lane", "search_scopus_lane", "search_core_lane"):
        monkeypatch.setattr(S, ten, lambda *a, **k: [])
    monkeypatch.setattr(S, "gan_do_tin_cay", lambda ds: list(ds))
    monkeypatch.setattr(S, "_pmid_da_co_trong_kho", lambda: set())
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()
    S._VUOT_TRAN.clear()
    nhan: list[dict] = []

    def bo_sung_gia(query, area, records, *, max_results, since_date=None):
        nhan.append({"query": query, "since_date": since_date})
        return [], {}
    lan_goc = S.bo_sung_du_phong_lane
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lambda *a, **k: lan_goc(*a, bo_sung_fn=bo_sung_gia, **k))
    _chay({"topic": "Hypertension", "query": "q", "truy_van_du_phong": "hypertension treatment"})
    mong = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
    assert nhan == [{"query": "hypertension treatment", "since_date": mong}], \
        f"làn dự phòng phải mang mốc ngày của cửa sổ quét (days=30 ⇒ {mong}); nhận {nhan}"
