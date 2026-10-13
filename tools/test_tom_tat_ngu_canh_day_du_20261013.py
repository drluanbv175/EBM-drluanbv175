# -*- coding: utf-8 -*-
"""Bước ⑧ của dây chuyền chỉ nạp MỘT dashboard — khối tóm tắt EndNote vẫn phải dựng từ ngữ cảnh ĐẦY ĐỦ (13/10/2026).

Đo 13/10: SELECT là mục chính (trích theo DOI) ở chủ đề CKM, là tham khảo (kèm PMID) ở chủ đề GLP-1. Chạy dây chuyền cho riêng
GLP-1 mà dựng ngữ cảnh chỉ từ GLP-1 ⇒ khối mục chính đã qua cổng bị ghi đè bằng khối «tham khảo». Ngoại tuyến hoàn toàn.
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


tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_ngu_canh")
N = _nap("tools/nap_endnote_chu_de.py", "_nap_ngu_canh")

DOI = "10.1056/nejmoa2307563"
SELECT = {"id": "S1", "title": "SELECT — semaglutide giảm MACE", "design": "RCT", "dateVersion": "2023", "doi": DOI,
          "pmid": None, "gradeLevel": "high", "decision": "apply", "action": "Dùng semaglutide", "references": []}
GLP = {"id": "G1", "title": "Mục GLP-1", "design": "SR", "pmid": "39999999", "gradeLevel": "mod", "decision": "consider",
       "action": "Cân nhắc", "references": [f"Lincoff AM. NEJM 2023. PMID 37952131. doi:{DOI}", "Khác: PMID 38888888"]}
A = Path("/khong-ton-tai/WebDashboard_A_CKM_20260628.html")       # chủ đề CKM: SELECT là MỤC CHÍNH (chỉ có DOI)
B = Path("/khong-ton-tai/WebDashboard_B_GLP1_20260701.html")      # chủ đề GLP-1: SELECT chỉ là THAM KHẢO (kèm PMID)
BANG = {A.name: {"meta": {"question": "CKM"}, "items": [SELECT]}, B.name: {"meta": {"question": "GLP-1"}, "items": [GLP]}}


def _doc(p):
    return BANG.get(Path(p).name)


class _EndNoteGia:
    """Bản ghi SELECT không có Accession Number — chỉ khớp được theo DOI (đúng như thư viện thật)."""

    def __init__(self):
        self.abstract = {"rSEL": "Original SELECT.", "rG": "Original GLP.", "r388": "Original 388."}
        self.thu_vien = Path("/khong-ton-tai/tv.enl")

    def tim_khop(self, gia_tri, truong):
        bang = {"Accession Number": {"39999999": ["rG"], "38888888": ["r388"]}, "DOI": {DOI: ["rSEL"]}}[truong]
        return {v: bang[v] for v in gia_tri if v in bang}

    def doc_truong(self, ids, truong):
        return {m: self.abstract[m] for m in ids}

    def ghi_truong(self, cap, truong):
        for m, gt in cap:
            self.abstract[m] = gt.replace("\n", "\r")
        return {m: "" for m, _ in cap}


def test_khoa_doi_gap_truoc_duoc_gop_vao_khoa_pmid_gap_sau():
    ds = tt.ngu_canh([A, B], _doc)
    assert f"doi:{DOI}" not in ds, "một bài chỉ được MỘT khoá — hai khoá cùng trỏ một bản ghi EndNote"
    vai = sorted(x["vai"] for x in ds["pmid:37952131"]["ngu_canh"])
    assert vai == ["muc", "tham_khao"] and ds["pmid:37952131"]["doi"] == DOI


def test_gop_khoa_doi_ten_ca_khoa_da_thay_cua_phien_ban_moi():
    """Bản MỚI của chủ đề CKM trích SELECT theo DOI; bản CŨ cùng chủ đề trích kèm PMID ⇒ gộp khoá, và bản cũ KHÔNG được
    thêm ngữ cảnh thứ hai (cùng chủ đề chỉ lấy bản mới nhất) — cần đổi tên khoá trong tập «đã thấy» của chủ đề."""
    moi = Path("/khong-ton-tai/WebDashboard_A_CKM_20260901.html")
    cu = Path("/khong-ton-tai/WebDashboard_A_CKM_20260101.html")
    bang = {moi.name: {"meta": {"question": "CKM"}, "items": [SELECT]},
            cu.name: {"meta": {"question": "CKM"}, "items": [dict(GLP, references=[f"PMID 37952131 doi:{DOI}"])]}}
    ds = tt.ngu_canh([moi, cu], lambda p: bang.get(Path(p).name))
    nc = ds["pmid:37952131"]["ngu_canh"]
    assert [(x["dashboard"], x["vai"]) for x in nc] == [(moi.name, "muc")], "bản cũ cùng chủ đề không thêm ngữ cảnh"


def test_chay_mot_dashboard_khong_ghi_de_muc_chinh_cua_chu_de_khac():
    en = _EndNoteGia()
    bc = tt.ghi_tom_tat(en, [B], kho=None, ap_dung=True, doc_data=_doc, sao_luu=lambda: "/s", tom_tat_abs={},
                        boi_canh=[A, B])
    sel = tt.chuan_dong(en.abstract["rSEL"])
    assert sel.startswith(f"{tt.MO_DAU} ✅ ÁP DỤNG NGAY") and "⭐ SELECT — semaglutide giảm MACE" in sel, \
        "bản ghi SELECT giữ khối MỤC CHÍNH (từ chủ đề CKM) dù dây chuyền chỉ chạy cho GLP-1"
    assert tt.NHAN_DONG["tham_khao"] not in sel and "PMID 37952131 · Toàn văn" in sel
    assert bc["trich_dan"] == 3, "chỉ ghi trích dẫn của dashboard đang chạy (GLP-1: mục + 2 tham khảo)"
    assert bc["tham_khao_chua_tom_tat"] == ["PMID 38888888"], "mục chính không bao giờ nằm trong danh sách thiếu tóm tắt máy"


def test_chi_ghi_trich_dan_cua_dashboard_dang_chay():
    en = _EndNoteGia()
    tt.ghi_tom_tat(en, [A], kho=None, ap_dung=True, doc_data=_doc, sao_luu=lambda: "/s", boi_canh=[A, B])
    assert en.abstract["rG"] == "Original GLP." and en.abstract["r388"] == "Original 388.", \
        "chạy cho CKM không được đụng bản ghi chỉ thuộc GLP-1"


def test_chay_tom_tat_truyen_moi_dashboard_cung_thu_muc_lam_boi_canh(tmp_path, capsys):
    for ten in ("WebDashboard_A_20260101.html", "WebDashboard_B_20260202.html", "ghi-chu.txt"):
        (tmp_path / ten).write_text("x", encoding="utf-8")
    nhan: dict = {}

    class _TT:
        TEP_TOM_TAT_ABS = tt.TEP_TOM_TAT_ABS

        @staticmethod
        def nap_tom_tat_abstract(dash):
            return {}

        @staticmethod
        def ghi_tom_tat(endnote, files, **kw):
            nhan.update(kw)
            return {"trich_dan": 1, "co_ban_ghi": 1, "da_ghi": 0, "se_ghi": 0, "khong_doi": 1, "khong_co_ban_ghi": [],
                    "loi": [], "tom_tat_may": 0, "tom_tat_lech_so": [], "tham_khao_chua_tom_tat": ["PMID 1"]}

    N._nap_doc_data = lambda: None
    N.chay_tom_tat(object(), [tmp_path / "WebDashboard_B_20260202.html"], None, False, tt=_TT)
    assert [p.name for p in nhan["boi_canh"]] == ["WebDashboard_A_20260101.html", "WebDashboard_B_20260202.html"]
    assert "CHƯA có tóm tắt máy: 1" in capsys.readouterr().out
