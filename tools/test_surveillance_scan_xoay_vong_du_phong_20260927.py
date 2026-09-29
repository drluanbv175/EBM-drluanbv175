"""Xoay vòng + khử trùng xuyên tuần cho bậc thang dự phòng TÍNH PHÍ của vòng quét tuần (vá 27/09/2026).

Có truy vấn tiếng Anh cho cả watchlist mà mọi chủ đề thiếu bài mạnh đều leo thang trong MỘT lượt thì trần Consensus
(5/lượt · 10/tháng) cạn ngay tuần đầu, chủ đề sau chỉ nhận lỗi «hết ngân sách». Consensus/SerpApi lọc theo NĂM nên bài
«liên quan nhất» quay lại mỗi tuần. Nay: tối đa K chủ đề mỗi TUẦN ISO khi có sổ (29/09/2026 — trước đó mỗi LƯỢT, lượt
W40 quét hai lần nên leo thang 4 chủ đề trong một ngày), chủ đề lâu chưa xét đi trước; bài đã trình không trình lại.
Test không gọi mạng: làn dự phòng là hàm theo dõi.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_xoay_vong_2709", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_xoay_vong_2709"] = S  # @dataclass tra sys.modules lúc dựng lớp — đăng ký TRƯỚC exec
_sp.loader.exec_module(S)

CHU_DE = [{"topic": t, "query": f"q {t}", "truy_van_du_phong": f"{t.lower()} treatment"}
          for t in ("Alpha", "Beta", "Gamma")]


@pytest.fixture()
def goi(monkeypatch):
    """Kín mạng; làn dự phòng trả MỘT bài cố định cho mỗi truy vấn và ghi lại thứ tự gọi."""
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
        return [S.Candidate(pmid="", publication_date="2026", title=f"Bài dự phòng {truy_van}",
                            url=f"https://doi.org/10.1/{truy_van.split()[0]}", tang="du_phong_bac_thang")], ""
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", theo_doi)
    return da_goi


def _chay(tran=None, so=None, chu_de=CHU_DE):
    dem = iter(range(100, 1000))

    def search_fn(query, days, retmax, **kw):
        return [str(next(dem))]

    def summarize_fn(ids):
        return [S.Candidate(pmid=p, publication_date="2026", title="Bài thường", pubtype=("Journal Article",),
                            url=f"https://pubmed.ncbi.nlm.nih.gov/{p}/") for p in ids]
    return S.run_scan(chu_de, days=30, max_results=6, cursor={}, search_fn=search_fn, summarize_fn=summarize_fn,
                      tran_leo_thang_du_phong=tran, trang_thai_du_phong=so)


def _lui_tuan(so: dict, ngay: int = 7) -> dict:
    """Giả lập «lượt tuần sau»: lùi mọi ngày leo thang trong sổ `ngay` ngày."""
    so["lan_cuoi_leo_thang"] = {k: (dt.date.fromisoformat(v) - dt.timedelta(days=ngay)).isoformat()
                                 for k, v in so.get("lan_cuoi_leo_thang", {}).items()}
    return so


def test_mac_dinh_khong_tran_giu_hanh_vi_cu(goi):
    rep = _chay()
    assert goi == ["alpha treatment", "beta treatment", "gamma treatment"]
    assert rep["du_phong_da_leo_thang"] == ["Alpha", "Beta", "Gamma"]
    assert all(any(c["tang"] == "du_phong_bac_thang" for c in t["candidates"]) for t in rep["topics"])


def test_tran_k_chi_leo_thang_k_chu_de_va_noi_ro_chu_de_cho_luot(goi):
    rep = _chay(tran=2, so={})
    assert goi == ["alpha treatment", "beta treatment"]
    assert rep["du_phong_khong_leo_thang"] == {"cho_luot_xoay_vong": 1}
    gamma = rep["topics"][2]
    assert "chờ lượt" in gamma["error"] and not any(c["tang"] == "du_phong_bac_thang" for c in gamma["candidates"])


def test_xoay_vong_chu_de_lau_chua_xet_di_truoc(goi):
    so = {"lan_cuoi_leo_thang": {"Alpha": "2026-09-20", "Beta": "2026-09-13"}, "da_trinh": {}}
    _chay(tran=2, so=so)
    assert goi == ["beta treatment", "gamma treatment"], "Gamma chưa từng xét, Beta xét lâu hơn Alpha ⇒ hai chủ đề này"
    assert so["lan_cuoi_leo_thang"]["Gamma"] == so["lan_cuoi_leo_thang"]["Beta"] > "2026-09-20"
    assert so["lan_cuoi_leo_thang"]["Alpha"] == "2026-09-20"


def test_ba_luot_lien_tiep_moi_chu_de_deu_den_luot(goi):
    so: dict = {}
    for _ in range(3):
        _chay(tran=1, so=so)
        _lui_tuan(so)
    assert sorted(goi) == ["alpha treatment", "beta treatment", "gamma treatment"]


def test_bai_du_phong_da_trinh_luot_truoc_khong_trinh_lai(goi):
    so: dict = {}
    _chay(tran=None, so=so, chu_de=CHU_DE[:1])
    rep2 = _chay(tran=None, so=so, chu_de=CHU_DE[:1])
    assert goi == ["alpha treatment", "alpha treatment"]
    assert not any(c["tang"] == "du_phong_bac_thang" for c in rep2["topics"][0]["candidates"])
    assert rep2["du_phong_bo_trung_xuyen_tuan"] == 1


def test_khong_so_thi_khong_khu_trung_xuyen_tuan(goi):
    _chay(chu_de=CHU_DE[:1])
    rep2 = _chay(chu_de=CHU_DE[:1])
    assert any(c["tang"] == "du_phong_bac_thang" for c in rep2["topics"][0]["candidates"])


def test_main_doc_ghi_so_canh_watchlist_va_mac_dinh_tran_2(goi, monkeypatch, tmp_path):
    wl = tmp_path / "watchlist.json"
    wl.write_text(json.dumps({"topics": CHU_DE}), encoding="utf-8", newline="\n")
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", wl)
    monkeypatch.setattr(S, "search", lambda query, days, retmax, **kw: ["555"])
    monkeypatch.setattr(S, "summarize", lambda ids: [S.Candidate(
        pmid=p, publication_date="2026", title="Bài thường", url=f"https://pubmed.ncbi.nlm.nih.gov/{p}/") for p in ids])
    monkeypatch.setattr(S, "ghi_alert", lambda *a, **k: None)
    S.main(["--watchlist", str(wl), "--allow-partial"])
    assert len(goi) == S.TRAN_LEO_THANG_DU_PHONG_MAC_DINH == 2
    so = json.loads((tmp_path / ".du-phong-trang-thai.json").read_text(encoding="utf-8"))
    assert sorted(so["lan_cuoi_leo_thang"]) == ["Alpha", "Beta"] and len(so["da_trinh"]) == 2
    (tmp_path / ".du-phong-trang-thai.json").write_text(json.dumps(_lui_tuan(so)), encoding="utf-8", newline="\n")
    S.main(["--watchlist", str(wl), "--allow-partial"])   # lượt TUẦN SAU
    # Lời gọi đi theo thứ tự watchlist; điều cần kiểm là Gamma (chưa từng xét) có trong 2 suất của lượt sau.
    assert len(goi) == 4 and "gamma treatment" in goi[2:], "lượt sau phải tới chủ đề chưa được xét"


def test_hai_luot_cung_tuan_khong_vuot_tran_tuan(goi):
    """29/09/2026: phiên gói tuần quét HAI lần (lần đầu sập) ⇒ trần theo lượt cho leo thang 4 chủ đề trong một ngày."""
    so: dict = {}
    _chay(tran=2, so=so)
    rep2 = _chay(tran=2, so=so)
    assert goi == ["alpha treatment", "beta treatment"], "lượt thứ hai CÙNG TUẦN vẫn đốt thêm hạn mức tính phí"
    assert rep2["du_phong_da_leo_thang"] == [] and rep2["du_phong_da_dung_tuan"] == 2
    assert all("tuần này đã dùng 2" in t["error"] for t in rep2["topics"])
