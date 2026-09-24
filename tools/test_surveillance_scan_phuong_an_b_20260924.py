"""Khoá PHƯƠNG ÁN B của khâu thu nhận (bác sĩ chọn 24/09/2026): «lấy đủ rồi chọn mạnh nhất».

Trước đây mỗi tầng chỉ lấy `--max` (6) ID mới nhất; luật 22/09 còn gắn «suy giảm» + đóng băng con trỏ khi
kết quả bị cắt — quét lại vẫn chỉ trả các bản mới nhất nên không thu hồi được gì (W39: 12/47 chủ đề, 96/608
bài được trình). Nay mỗi tầng lấy tới TRAN_LAY_MOI_TANG ID, tóm tắt theo lô, xếp theo độ mạnh chứng cứ, trình
`max_results` bài đầu; phần còn lại ghi `khong_trinh`; vượt trần chỉ ghi chú, không suy giảm.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_phuong_an_b", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_phuong_an_b"] = S  # @dataclass tra sys.modules lúc dựng lớp — phải đăng ký TRƯỚC exec
_sp.loader.exec_module(S)


@pytest.fixture(autouse=True)
def _kin(monkeypatch):
    """Kín mạng: chặn làn phụ, khâu tra rút bài (giữ nguyên ứng viên) và sổ «đã có trong kho»."""
    for ten in ("search_preprint_lane", "search_trials_lane", "search_scopus_lane", "search_core_lane"):
        monkeypatch.setattr(S, ten, lambda *a, **k: [])
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lambda *a, **k: ([], ""))
    monkeypatch.setattr(S, "gan_do_tin_cay", lambda ds: list(ds))
    monkeypatch.setattr(S, "_pmid_da_co_trong_kho", lambda: set())
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()
    S._VUOT_TRAN.clear()
    yield


def _uv(pmid, pubtype=(), title="A cohort study", authority=""):
    return S.Candidate(pmid=pmid, publication_date="2026", title=title,
                       url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", pubtype=tuple(pubtype),
                       authority_source=authority)


# ── Điểm độ mạnh ─────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("pubtype, diem", [
    (("Journal Article", "Practice Guideline"), 5),
    (("Consensus Statement",), 5),
    (("Journal Article", "Systematic Review"), 4),
    (("Meta-Analysis",), 4),
    (("Randomized Controlled Trial",), 3),
    (("Observational Study",), 2),
    (("Review",), 1),
    (("Journal Article", "Randomized Controlled Trial", "Retracted Publication"), 0),
])
def test_diem_manh_theo_loai_xuat_ban_that(pubtype, diem):
    assert S.diem_manh(_uv("1", pubtype)) == (diem, True)


def test_bai_chua_gan_loai_suy_tu_tieu_de_va_danh_dau_khong_phai_loai_that():
    assert S.diem_manh(_uv("1", ("Journal Article",), "A systematic review of X")) == (4, False)
    assert S.diem_manh(_uv("1", (), "Randomised trial of Y")) == (3, False)
    assert S.diem_manh(_uv("1", (), "Clinical course of Z")) == (1, False)


def test_chon_manh_nhat_xep_dung_va_bai_trong_kho_khong_chiem_cho():
    ds = [_uv("10"), _uv("11", ("Randomized Controlled Trial",)), _uv("12", ("Guideline",)),
          _uv("13", (), "Meta-analysis of W"), _uv("14", ("Systematic Review",)), _uv("15", ("Guideline",))]
    chon, bo, da_co = S.chon_manh_nhat(ds, 3, trong_kho={"15"})
    assert [c.pmid for c in chon] == ["12", "14", "13"], "guideline → SR loại thật → SR suy từ tiêu đề"
    assert [c.pmid for c in bo] == ["11", "10"]
    assert da_co == 1


def test_cung_diem_thi_nguon_tham_quyen_roi_moi_hon_truoc():
    ds = [_uv("20", ("Randomized Controlled Trial",)),
          _uv("21", ("Randomized Controlled Trial",), authority="NEJM"),
          _uv("22", ("Randomized Controlled Trial",))]
    chon, _, _ = S.chon_manh_nhat(ds, 3, set())
    assert [c.pmid for c in chon] == ["21", "20", "22"]


# ── run_scan: lấy tới trần, tóm tắt theo lô, trình mạnh nhất, ghi phần còn lại ─────────────────────────────
def _chay(n_id, max_results=6, pubtype_cua=None, topics=None):
    goi = {"retmax": [], "lo": []}

    def search_fn(query, days, retmax, **kw):
        goi["retmax"].append(retmax)
        return [str(1000 + i) for i in range(min(n_id, retmax))]

    def summarize_fn(ids):
        goi["lo"].append(len(ids))
        return [_uv(p, (pubtype_cua or {}).get(p, ("Journal Article",))) for p in ids]

    topics = topics or [{"topic": "T", "query": "q"}]
    cursor: dict = {}
    rep = S.run_scan(topics, days=30, max_results=max_results, cursor=cursor,
                     search_fn=search_fn, summarize_fn=summarize_fn)
    return rep, goi, cursor


def test_lay_toi_tran_va_tom_tat_theo_lo():
    rep, goi, _ = _chay(250)
    assert goi["retmax"] == [S.TRAN_LAY_MOI_TANG], "phải lấy tới trần, không chỉ max_results"
    assert goi["lo"] and max(goi["lo"]) <= S.LO_TOM_TAT and sum(goi["lo"]) == 250


def test_trinh_mạnh_nhat_ghi_phan_con_lai_va_khong_suy_giam():
    manh = {"1200": ("Practice Guideline",), "1100": ("Systematic Review",), "1050": ("Randomized Controlled Trial",)}
    rep, _, cursor = _chay(250, pubtype_cua=manh)
    t = rep["topics"][0]
    assert t["status"] == "PASS", "nhiều bài khớp KHÔNG phải suy giảm"
    assert "T" in cursor, "con trỏ phải tiến"
    assert [c["pmid"] for c in t["candidates"]][:3] == ["1200", "1100", "1050"], "mạnh nhất phải đứng đầu"
    assert len(t["candidates"]) == 6
    assert len(t["khong_trinh"]) == 244, "không bài nào bị bỏ im lặng"
    assert "trình 6 mạnh nhất" in t["error"] and "244 ghi «đã quét, không trình»" in t["error"]


def test_vuot_tran_chi_ghi_chu_con_tro_van_tien(monkeypatch):
    def search_fn(query, days, retmax, **kw):
        S._VUOT_TRAN.append(f"vượt trần lấy: đã quét {retmax}/412 bản ghi mới nhất khớp truy vấn")
        return [str(i) for i in range(retmax)]

    cursor: dict = {}
    rep = S.run_scan([{"topic": "T", "query": "q"}], days=30, max_results=6, cursor=cursor,
                     search_fn=search_fn, summarize_fn=lambda ids: [_uv(p) for p in ids])
    t = rep["topics"][0]
    assert t["status"] == "PASS" and "T" in cursor
    assert "vượt trần lấy" in t["error"]


def test_bai_khong_trinh_o_chu_de_nay_van_trinh_duoc_o_chu_de_khac():
    """Bộ khử trùng dùng chung mọi chủ đề chỉ chứa bài ĐÃ TRÌNH — bài xếp thấp ở A vẫn có thể đứng đầu ở B."""
    def search_fn(query, days, retmax, **kw):
        return ["1", "2", "3"] if query == "qa" else ["3"]

    rep = S.run_scan([{"topic": "A", "query": "qa"}, {"topic": "B", "query": "qb"}], days=30, max_results=2,
                     search_fn=search_fn, summarize_fn=lambda ids: [_uv(p) for p in ids])
    by = {t["topic"]: t for t in rep["topics"]}
    assert [c["pmid"] for c in by["A"]["candidates"]] == ["1", "2"]
    assert [x["pmid"] for x in by["A"]["khong_trinh"]] == ["3"]
    assert [c["pmid"] for c in by["B"]["candidates"]] == ["3"]


def test_it_bai_thi_khong_co_khong_trinh_va_khong_ghi_chu():
    rep, _, _ = _chay(4)
    t = rep["topics"][0]
    assert len(t["candidates"]) == 4 and t["khong_trinh"] == [] and "không trình" not in t["error"]
