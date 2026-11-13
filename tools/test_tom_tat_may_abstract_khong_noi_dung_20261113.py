# -*- coding: utf-8 -*-
"""Tóm tắt MÁY từ toàn văn PMC cho bài CÓ abstract nhưng abstract không nêu nội dung (13/11/2026) — `tom_tat_endnote_vi.py`.

Bác sĩ: «Luật tóm tắt máy: có mở rộng cho abstract guideline». Abstract của guideline hiệp hội (vd ADA Standards of Care
2026 chương 5, PMID 41358898) chỉ là đoạn mô tả chung, không chứa khuyến cáo ⇒ tóm tắt rút từ abstract vô dụng. Mục kho khai
`"nguon": "toan_van_pmc"` + `"abstract_khong_noi_dung": "<lý do>"` ⇒ soạn và chốt số theo toàn văn PMC truy cập mở; không khai
lý do ⇒ vẫn từ chối như luật 20/10. Ngoại tuyến hoàn toàn.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_may_abs_rong")

MUC = {"id": "ITEM-01", "title": "Mục chính", "source": "Nguồn chính 2026", "design": "Guideline", "dateVersion": "2026",
       "pmid": "31111111", "doi": "10.1000/chinh", "pico": {"P": ["Người lớn", "match"], "I": ["Can thiệp", "match"],
                                                            "C": "Chuẩn", "O": ["Kết cục", "match"]},
       "gradeLevel": "na", "decision": "consider", "action": "Hành động của nguồn chính",
       "references": ["Nguồn chính. PMID 31111111", "Guideline hiệp hội, abstract mô tả chung. PMID 32222222"]}
# Abstract kiểu ADA: mô tả chung, có vài con số «năm/tổ chức» nhưng không có khuyến cáo.
ABSTRACT = ("The American Diabetes Association (ADA) Standards of Care in Diabetes includes the ADA's current clinical "
            "practice recommendations. Members of the Professional Practice Committee update the Standards annually, "
            "or more frequently as warranted. Grading system ... 2026.")
XML = ("<?xml version='1.0' encoding='utf-8'?><article><front><article-meta><title-group><article-title>Facilitating"
       "</article-title></title-group></article-meta></front><body><sec><p>5.1 Adults should engage in 150 min or more of "
       "moderate-intensity aerobic activity per week (A). Weight loss of 5% is recommended.</p></sec></body></article>")
LY_DO = "abstract guideline chỉ mô tả chung, không nêu khuyến cáo"
TOM_TAT = {"thiet_ke": "Guideline ADA", "P": "Người lớn đái tháo đường", "I": "Vận động ≥150 phút/tuần",
           "C": "Không nêu", "O": "Kiểm soát đường huyết",
           "ket_qua": "Khuyến cáo 5.1: ≥150 phút/tuần hoạt động thể lực vừa (mức A); giảm 5% cân nặng",
           "nguon": "toan_van_pmc", "abstract_khong_noi_dung": LY_DO}


def _muc():
    f = Path("/khong-ton-tai/WebDashboard_X_20261113.html")
    d = {"meta": {"question": "ĐTĐ"}, "items": [MUC]}
    return tt.ngu_canh([f], lambda p: {f.name: d}.get(Path(p).name))["pmid:32222222"]


def _kho(tmp_path: Path, ten: str = "PMID-32222222_PMC9999999.xml", noi_dung: str = XML) -> Path:
    (tmp_path / ten).write_text(noi_dung, encoding="utf-8")
    return tmp_path


def test_co_abstract_khai_ly_do_thi_in_tu_toan_van_voi_nhan_rieng(tmp_path):
    kho = _kho(tmp_path)
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": TOM_TAT}, ABSTRACT, kho)
    assert lech == [] and tom is TOM_TAT
    dong = tt.khoi_tieng_viet(_muc(), kho, tom).splitlines()
    assert f"{tt.NHAN_DONG['may_pmc_abs']} (chưa qua cổng dashboard — không phải khuyến nghị):" in dong
    van = "\n".join(dong)
    assert tt.NHAN_DONG["may"] + " (" not in van and tt.NHAN_DONG["may_pmc"] + " (" not in van
    assert dong[-1] == tt.CHAN_MAY_PMC_ABS
    assert LY_DO not in van and "abstract_khong_noi_dung" not in van, "siêu dữ liệu không bao giờ in nguyên văn"


def test_co_abstract_khong_khai_ly_do_van_tu_choi(tmp_path):
    cu = {k: v for k, v in TOM_TAT.items() if k != "abstract_khong_noi_dung"}
    for muc_kho in (cu, dict(TOM_TAT, abstract_khong_noi_dung="  ")):
        tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": muc_kho}, ABSTRACT, _kho(tmp_path))
        assert tom is None and len(lech) == 1 and lech[0].startswith("⛔") and "CÓ abstract" in lech[0]


def test_so_doi_chieu_voi_toan_van_khong_phai_abstract(tmp_path):
    # «2026» có trong abstract nhưng KHÔNG có trong toàn văn ⇒ lệch: chốt số đi theo toàn văn PMC.
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": dict(TOM_TAT, thiet_ke="Guideline ADA 2026")}, ABSTRACT,
                               _kho(tmp_path))
    assert tom is None and lech == ["2026"]


def test_kho_thieu_tep_pmc_thi_tu_choi(tmp_path):
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": TOM_TAT}, ABSTRACT, tmp_path)
    assert tom is None and lech and lech[0].startswith("⛔") and "PMC" in lech[0]


def test_kiem_kho_bao_ly_do_rong_hoac_sai_nguon():
    assert tt.kiem_kho_tom_tat({"PMID 32222222": TOM_TAT}) == []
    rong = tt.kiem_kho_tom_tat({"PMID 32222222": dict(TOM_TAT, abstract_khong_noi_dung="")})
    assert len(rong) == 1 and "rỗng" in rong[0]
    sai = tt.kiem_kho_tom_tat({"PMID 32222222": {k: v for k, v in TOM_TAT.items() if k != "nguon"}})
    assert len(sai) == 1 and "toan_van_pmc" in sai[0]


def test_bai_khong_abstract_khong_khai_ly_do_giu_nhan_cu(tmp_path):
    cu = {k: v for k, v in TOM_TAT.items() if k != "abstract_khong_noi_dung"}
    kho = _kho(tmp_path)
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": cu}, "", kho)
    assert lech == [] and tom is cu
    assert tt.khoi_tieng_viet(_muc(), kho, tom).splitlines()[-1] == tt.CHAN_MAY_PMC


def test_nhan_moi_nam_trong_bmp():
    for s in (tt.NHAN_DONG["may_pmc_abs"], tt.CHAN_MAY_PMC_ABS):
        assert all(ord(c) <= 0xFFFF for c in s), "EndNote đổi ký tự ngoài BMP thành «?»"
