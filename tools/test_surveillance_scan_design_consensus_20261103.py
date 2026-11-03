"""BH176 (03/11/2026) — bộ lọc loại thiết kế của bộ quét phải nhận «Consensus Statement».

Mọi truy vấn tầng guideline trong watchlist đều tự khai `"consensus statement"[pt]` và
`khoa_manh_nhat` xếp loại này ngang guideline, nhưng hằng DESIGN mà `search()` AND thêm vào lại
thiếu nó ⇒ bản ghi chỉ mang «Consensus Statement» bị loại im lặng ở mọi chủ đề (đo 03/11/2026:
792 bản ghi/36 tháng trên 58 chủ đề). Test kiểm HÀNH VI: chuỗi `term` thật sự gửi tới NCBI và
truy vấn thật sự gửi tới Europe PMC (đường dự phòng), không chỉ đọc hằng số.
"""
from __future__ import annotations

import importlib.util
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_design_consensus_test", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_design_consensus_test"] = S
_sp.loader.exec_module(S)


def _tham_so(url: str) -> dict[str, str]:
    return {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).items()}


def test_term_gui_ncbi_co_consensus_statement_khi_loc_thiet_ke():
    da_goi: list[str] = []

    def fetch(url: str) -> dict:
        da_goi.append(url)
        return {"esearchresult": {"idlist": [], "count": "0"}}

    S.search("atrial fibrillation", 30, 5, fetch_json=fetch, loc_thiet_ke=True)
    term = _tham_so(da_goi[0])["term"]
    assert '"consensus statement"[ptyp]' in term, term
    # các loại cũ vẫn còn — không đổi nhầm sang bộ khác
    for loai in ("Guideline[ptyp]", '"practice guideline"[ptyp]', '"systematic review"[ptyp]',
                 "meta-analysis[ptyp]", "randomized controlled trial[ptyp]"):
        assert loai in term, loai


def test_term_khong_loc_thi_khong_them_design():
    da_goi: list[str] = []

    def fetch(url: str) -> dict:
        da_goi.append(url)
        return {"esearchresult": {"idlist": [], "count": "0"}}

    S.search("atrial fibrillation", 30, 5, fetch_json=fetch, loc_thiet_ke=False)
    assert _tham_so(da_goi[0])["term"] == "(atrial fibrillation)"


def test_du_phong_europe_pmc_co_pub_type_consensus_statement():
    da_goi: list[str] = []

    def fetch(url: str) -> dict:
        da_goi.append(url)
        return {"resultList": {"result": []}}

    S.search_europe_pmc("atrial fibrillation", 30, 5, fetch_json=fetch, loc_thiet_ke=True)
    q = _tham_so(da_goi[0])["query"]
    assert 'PUB_TYPE:"consensus statement"' in q, q
    S.search_europe_pmc("atrial fibrillation", 30, 5, fetch_json=fetch, loc_thiet_ke=False)
    assert "PUB_TYPE" not in _tham_so(da_goi[1])["query"]


def test_moi_loai_diem_cao_nhat_deu_qua_bo_loc():
    """Loại nào bảng xếp hạng coi là mạnh ngang guideline (điểm 5) thì bộ lọc không được loại nó —
    trừ nhãn NIH cũ đã bị NLM bỏ (`consensus development conference, nih`)."""
    da_bo = {"consensus development conference, nih"}
    cao_nhat = {k for k, v in S._DIEM_LOAI_XUAT_BAN.items() if v == 5} - da_bo
    thieu = {k for k in cao_nhat if f'"{k}"[ptyp]' not in S.DESIGN.lower() and f"{k}[ptyp]" not in S.DESIGN.lower()}
    assert not thieu, f"DESIGN loại im lặng loại điểm 5: {sorted(thieu)}"
