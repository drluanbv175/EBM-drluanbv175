# -*- coding: utf-8 -*-
"""Tóm tắt tiếng Việt CHI TIẾT trong Abstract cho chứng cứ chưa đạt chuẩn (24/10/2026) — `tom_tat_endnote_vi.py`.

Bác sĩ: «với những chứng cứ chưa đạt chuẩn thì hãy tóm tắt tiếng việt một cách chi tiết vào phần Abstract của trích dẫn»,
chọn «Từ abstract gốc, có cổng số liệu». Ba thay đổi được khoá ở đây:
  1. Kho tóm tắt máy thêm HẠN CHẾ và KẾT LUẬN CỦA TÁC GIẢ — cùng chốt số (số không có nguyên văn trong abstract ⇒ không in).
  2. `ghi_thu_vien`: bài trong thư viện KHÔNG thuộc dashboard nào cũng nhận khối tóm tắt máy; bài thuộc dashboard để cho
     `ghi_tom_tat` (khối dashboard thắng); lệch số ⇒ không ghi; danh sách loại trừ của bác sĩ ⇒ không ghi.
  3. `--tom-tat-thu-vien` chạy riêng, chạy khô mặc định.
Ngoại tuyến hoàn toàn: dashboard là dict giả, EndNote là đối tượng giả.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_chi_tiet")
N = _nap("tools/nap_endnote_chu_de.py", "_nap_tt_chi_tiet")

MUC = {"id": "ITEM-01", "title": "Colchicine dự phòng thứ phát", "source": "CONVINCE · Lancet 2024", "design": "RCT",
       "dateVersion": "2024", "pmid": "31111111", "doi": "10.1016/aaa",
       "pico": {"P": ["Đột quỵ", "match"], "I": ["Colchicine", "match"], "C": "Chuẩn", "O": ["Tái phát", "match"]},
       "gradeLevel": "mod", "decision": "notyet", "action": "CHƯA thêm colchicine thường quy",
       "references": ["Kelly P. Lancet 2024. PMID 31111111", "Phụ lục: Smith J. Stroke 2020. PMID 32222222"]}
GOC = ("Background: Inflammation drives recurrence. Methods: We randomly assigned 1,234 adults aged 40 years or older "
       "to drug or placebo. Findings: The primary outcome occurred in 9·1% vs 12·0% (HR 0·85, 95% CI 0·71–0·93). "
       "Limitations: open-label design. Interpretation: the drug reduced recurrence.")
TOM_TAT = {"thiet_ke": "RCT, n = 1234", "P": "Người lớn ≥ 40 tuổi", "I": "Thuốc", "C": "Giả dược", "O": "Kết cục chính",
           "ket_qua": "9.1% so với 12.0%; HR 0.85 (KTC 95% 0.71–0.93)", "han_che": "Thiết kế nhãn mở",
           "ket_luan": "Tác giả kết luận thuốc giảm tái phát"}
F = Path("/khong-ton-tai/WebDashboard_X_20260614.html")


def _doc(f):
    return {"meta": {"question": "Đột quỵ"}, "items": [MUC]} if Path(f).name == F.name else None


class _EndNoteGia:
    def __init__(self, abstract: dict[str, str], khop: dict[str, list[str]]):
        self.abstract = dict(abstract)
        self.khop = khop
        self.da_ghi: list[str] = []
        self.thu_vien = Path("/khong-ton-tai/tv.enl")

    def tim_khop(self, gia_tri, truong):
        return {v: self.khop[v] for v in gia_tri if v in self.khop}

    def doc_truong(self, ids, truong):
        return {m: self.abstract.get(m, "") for m in ids}

    def ghi_truong(self, cap, truong):
        for m, gt in cap:
            self.abstract[m] = gt.replace("\n", "\r")
            self.da_ghi.append(m)
        return {m: "" for m, _ in cap}


def test_hai_truong_moi_in_dung_nhan_va_chiu_chot_so(tmp_path):
    ds = tt.ngu_canh([F], _doc)
    muc = ds["pmid:32222222"]
    dung, lech = tt.tom_tat_cho(muc, {"PMID 32222222": TOM_TAT}, GOC)
    assert lech == [] and dung is TOM_TAT
    dong = tt.khoi_tieng_viet(muc, tmp_path, dung).splitlines()
    assert "   HẠN CHẾ: Thiết kế nhãn mở" in dong and "   KẾT LUẬN CỦA TÁC GIẢ: Tác giả kết luận thuốc giảm tái phát" in dong
    for truong in ("han_che", "ket_luan"):
        assert tt.tom_tat_cho(muc, {"PMID 32222222": dict(TOM_TAT, **{truong: "giảm 77%"})}, GOC) == (None, ["77"]), \
            f"«{truong}» phải chịu cùng chốt số với các trường khác"
    assert tt.kiem_kho_tom_tat({"PMID 32222222": TOM_TAT}) == [], "hai trường mới là trường hợp lệ của kho"


def test_ghi_thu_vien_chi_ghi_bai_ngoai_dashboard_va_giu_abstract_goc(tmp_path):
    en = _EndNoteGia({"r1": GOC, "r9": GOC, "r8": GOC.replace("0·85", "0·91"), "r7": GOC},
                     {"31111111": ["r1"], "40000001": ["r9"], "40000002": ["r8"], "40000004": ["r7"]})
    kho_tt = {"PMID 31111111": TOM_TAT, "PMID 40000001": TOM_TAT, "PMID 40000002": TOM_TAT, "PMID 40000003": TOM_TAT,
              "PMID 40000004": TOM_TAT, "DOI 10.1/ghi-chu": {"bo_qua": "trường Abstract là ghi chú của bác sĩ"}}

    def bo_qua(pmid, doi, co_ban_ghi):
        return "danh sách loại trừ của bác sĩ" if pmid == "40000004" else None

    kho_chay = tt.ghi_thu_vien(en, dashboards=[F], kho=tmp_path, ap_dung=False, doc_data=_doc, tom_tat_abs=kho_tt,
                               bo_qua=bo_qua, sao_luu=lambda: pytest.fail("chạy khô không sao lưu"))
    assert kho_chay["se_ghi"] == 1 and en.da_ghi == [], "chạy khô chỉ đếm"
    bc = tt.ghi_thu_vien(en, dashboards=[F], kho=tmp_path, ap_dung=True, doc_data=_doc, tom_tat_abs=kho_tt,
                         bo_qua=bo_qua, sao_luu=lambda: "/s")
    assert en.da_ghi == ["r9"], "chỉ bài ngoài dashboard, có bản ghi, đúng số, không bị bác sĩ loại"
    assert bc["thuoc_dashboard"] == 1 and bc["bo_qua_kho"] == 1 and bc["khong_co_ban_ghi"] == ["PMID 40000003"]
    assert len(bc["bo_qua_theo_bac_si"]) == 1 and "40000004" in bc["bo_qua_theo_bac_si"][0]
    assert len(bc["tom_tat_lech_so"]) == 1 and "r8" in bc["tom_tat_lech_so"][0], "lệch số ⇒ không ghi, có báo"
    moi = tt.chuan_dong(en.abstract["r9"])
    assert moi.startswith(f"{tt.MO_DAU} {tt.NHAN_DONG['thu_vien']}") and moi.endswith(GOC), "abstract gốc giữ dưới phân cách"
    assert tt.CHAN_MAY in moi and tt.CHAN not in moi, "bài thư viện không mang chân «chép từ dashboard đã qua cổng»"
    for chu in ("ÁP DỤNG", "Chứng cứ:", "THỰC HÀNH:"):
        assert chu not in moi, f"khối thư viện không có mức chứng cứ/khuyến nghị: {chu}"
    assert en.abstract["r1"] == GOC and en.abstract["r8"] == GOC.replace("0·85", "0·91")
    bc2 = tt.ghi_thu_vien(en, dashboards=[F], kho=tmp_path, ap_dung=True, doc_data=_doc, tom_tat_abs=kho_tt,
                          bo_qua=bo_qua, sao_luu=lambda: pytest.fail("không đổi thì không ghi"))
    assert bc2["se_ghi"] == 0 and bc2["khong_doi"] == 1, "chạy lại: thay khối cũ bằng khối giống hệt ⇒ không ghi"


def test_cli_tom_tat_thu_vien_chay_rieng():
    assert N.main(["--tom-tat-thu-vien", "--file", str(F)]) == N.MA_THAM_SO
    assert N.main(["--tom-tat-thu-vien", "--tom-tat-vi"]) == N.MA_THAM_SO


def test_chay_tom_tat_thu_vien_chay_kho_khong_in_dau_xong(capsys):
    class _TT:
        @staticmethod
        def nap_tom_tat_abstract(dash):
            return {}

        @staticmethod
        def ghi_thu_vien(endnote, **kw):
            return {"muc_kho": 3, "thuoc_dashboard": 1, "co_ban_ghi": 2, "khong_co_ban_ghi": [], "khong_doi": 0, "se_ghi": 2,
                    "da_ghi": 0, "loi": [], "sao_luu": None, "tom_tat_lech_so": [], "bo_qua_theo_bac_si": []}

    N._nap_doc_data = lambda: None
    bc = N.chay_tom_tat_thu_vien(object(), Path("/khong-ton-tai"), None, False, tt=_TT)
    ra = capsys.readouterr().out
    assert bc is not None and ra.startswith("ℹ Chạy khô ·") and "sẽ ghi 2" in ra and "✓" not in ra
