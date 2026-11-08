# -*- coding: utf-8 -*-
"""Tóm tắt Word «áp dụng nhanh» (08/11/2026). Bác sĩ: «Tóm tắt tiếng việt đảm bảo đúng chuẩn,chính xác nhất và giúp áp dụng
nhanh cho thực hành lâm sàng». Kiểm: mục 2 của Word là «Áp dụng nhanh tại phòng khám» (trước 08/11 phần áp dụng nằm ở mục 10,
sau phương pháp/kết quả/RoB/GRADE), không còn mục áp dụng thứ hai ở cuối, vẫn đủ 11 mục; ô «bài là nguồn của khuyến cáo trên
dashboard» chỉ lấy phiên bản HIỆN HÀNH, mới nhất trước, không trùng, tối đa 3; bài ★ thiếu cả điều kiện lẫn theo dõi bị cổng chặn,
bài không ★ thì không; luật ★ là của gan_tag_endnote; hướng dẫn đọc có luật 11."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

_sp = importlib.util.spec_from_file_location("_ttcc_adn", Path(__file__).resolve().parent / "tom_tat_chung_cu_word.py")
T = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T)
_sp2 = importlib.util.spec_from_file_location("_ttcc_adn_goc", Path(__file__).resolve().parent / "test_tom_tat_chung_cu_word_20261019.py")
G = importlib.util.module_from_spec(_sp2)
_sp2.loader.exec_module(G)

CAN_DOCX = pytest.mark.skipif(importlib.util.find_spec("docx") is None, reason="thiếu python-docx (CI bản sao trần không cài)")


def _nc(*ngu_canh_dashboard) -> dict:
    nc = copy.deepcopy(G.NGU_CANH)
    nc["ngu_canh_dashboard"] = list(ngu_canh_dashboard)
    return nc


def _muc(decision="apply", grade="high", *, chu_de="Suy tim", muc="ITEM-04", tieu_de="Chẹn beta giảm tử vong ở HFrEF",
         ngay="18/07/2026", ban_cu=False, design="RCT", vai="muc"):
    return {"vai": vai, "decision": decision, "gradeLevel": grade, "design": design, "ban_cu": ban_cu, "chu_de": chu_de,
            "muc": muc, "tieu_de_muc": tieu_de, "ngay": ngay}


SAO = _nc(_muc())
KHONG_SAO = _nc(_muc("consider", "high"))


def _tt_khong_dieu_kien() -> dict:
    tt = G._hop_le()
    tt["goi_y_ap_dung"] = {"nen_lam": ["Dùng thuốc X cho người suy tim EF giảm."], "khong_nen": [], "dieu_kien": [],
                           "theo_doi": []}
    return tt


def test_bai_sao_thieu_dieu_kien_va_theo_doi_bi_chan():
    loi = T.kiem_tom_tat(_tt_khong_dieu_kien(), G.TRANG, SAO)
    assert any("bài ★ Áp dụng – tin cậy cao" in x and "dieu_kien" in x for x in loi)


@pytest.mark.parametrize("khoa", ["dieu_kien", "theo_doi"])
def test_bai_sao_co_dieu_kien_hoac_theo_doi_thi_dat(khoa):
    tt = _tt_khong_dieu_kien()
    tt["goi_y_ap_dung"][khoa] = ["Nội dung đúng như bài."]
    assert T.kiem_tom_tat(tt, G.TRANG, SAO) == []


@pytest.mark.parametrize("nc", [KHONG_SAO, _nc(_muc(ban_cu=True)), _nc(_muc(grade="low")), _nc()])
def test_bai_khong_sao_khong_doi_dieu_kien(nc):
    assert T.kiem_tom_tat(_tt_khong_dieu_kien(), G.TRANG, nc) == []


def test_la_sao_dung_luat_cua_gan_tag_endnote(monkeypatch):
    assert T.la_sao(SAO) and not T.la_sao(KHONG_SAO)
    assert T.la_sao(_nc(_muc(grade="na", design="Guideline ESC 2025")))
    assert not T.la_sao(_nc(_muc(grade="na", design="Consensus chuyên gia")))
    monkeypatch.setattr(T.mod("gte"), "dat_ap_dung_tin_cay", lambda nc: False)
    assert not T.la_sao(SAO), "đổi luật ở gan_tag_endnote thì cổng đổi theo — không có bản sao luật thứ hai"


def test_vi_tri_khuyen_cao_chi_ban_hien_hanh_moi_nhat_truoc_toi_da_3():
    nc = _nc(_muc(chu_de="A", muc="ITEM-01", ngay="01/02/2026"),
             _muc("consider", "mod", chu_de="B", muc="ITEM-02", ngay="05/11/2026"),
             _muc(chu_de="C", muc="ITEM-03", ngay="06/11/2026", ban_cu=True),          # bản cũ ⇒ bỏ
             _muc(chu_de="D", muc="ITEM-04", ngay="07/11/2026", vai="tham_khao"),       # chỉ tham khảo ⇒ bỏ
             _muc(chu_de="A", muc="ITEM-01", ngay="01/02/2026"),                        # trùng ⇒ bỏ
             _muc("apply", "na", chu_de="E", muc="ITEM-05", ngay="03/03/2025"),
             _muc(chu_de="F", muc="ITEM-06", ngay="02/01/2024"))
    vt = T.vi_tri_khuyen_cao(nc)
    assert len(vt) == 3
    assert vt[0].startswith("**CÂN NHẮC**") and "B (bản 05/11/2026)" in vt[0] and "trung bình" in vt[0]
    assert vt[1].startswith("**ÁP DỤNG**") and "A (bản 01/02/2026)" in vt[1] and "mức chứng cứ trên dashboard: cao" in vt[1]
    assert "E (bản 03/03/2025)" in vt[2] and "nguồn không dùng thang GRADE" in vt[2]
    assert T.vi_tri_khuyen_cao(_nc()) == []


@CAN_DOCX
def test_word_muc_2_la_ap_dung_nhanh_va_khong_lap_o_cuoi():
    tt = G._hop_le()
    tt["goi_y_ap_dung"] = {"nen_lam": ["Dùng thuốc X."], "khong_nen": ["Không dùng khi Y."], "dieu_kien": ["Chỉ khi Z."],
                           "theo_doi": ["Kali sau 1 tuần."]}
    doc = T.dung_word(tt, SAO)
    muc = [p.text for p in doc.paragraphs if p.style.name.startswith("Heading")]
    assert muc[0] == "1. Kết luận cho thực hành" and muc[1] == "2. Áp dụng nhanh tại phòng khám"
    assert len(muc) == 11 and not any("Áp dụng vào thực hành" in m for m in muc)
    van = "\n".join(p.text for p in doc.paragraphs)
    for nhan in ("NÊN LÀM", "KHÔNG NÊN", "THẬN TRỌNG / ĐIỀU KIỆN", "THEO DÕI"):
        assert van.count(nhan) == 1, f"{nhan} in đúng một lần"
    i_ap_dung, i_thong_tin = van.index("NÊN LÀM"), van.index("3. Thông tin trích dẫn")
    assert i_ap_dung < i_thong_tin, "phần áp dụng đứng TRƯỚC thông tin trích dẫn/phương pháp"
    o = [c.text for t in doc.tables for r in t.rows for c in r.cells]
    assert any("BÀI LÀ NGUỒN CỦA KHUYẾN CÁO TRÊN DASHBOARD" in x and "ÁP DỤNG" in x and "Chẹn beta" in x for x in o)


@CAN_DOCX
def test_word_khong_co_ngu_canh_dashboard_thi_khong_in_o_nguon():
    o = [c.text for t in T.dung_word(G._hop_le(), G.NGU_CANH).tables for r in t.rows for c in r.cells]
    assert not any("BÀI LÀ NGUỒN CỦA KHUYẾN CÁO" in x for x in o)


def test_huong_dan_doc_co_luat_ap_dung_nhanh():
    hd = T.huong_dan_doc()
    assert "11. ÁP DỤNG NHANH" in hd and "Áp dụng nhanh tại phòng khám" in hd and "can_xac_nhan" in hd


@CAN_DOCX
@pytest.mark.parametrize("tt_rb, nhan, mau", [
    ("dinh_chinh_bi_rut_da_ky", "bài gốc không bị rút", "cam"),
    ("khong_thay_rut", "không thấy thông báo rút", "la"),
    ("khong_thay_rut_rw", "không thấy (chỉ Retraction Watch)", "cam"),
    ("chua_kiem", "CHƯA KIỂM ĐƯỢC", "do"),
    ("trang_thai_la", "—", "do")])
def test_dau_trang_rut_bai_co_nhan_cho_moi_trang_thai(tt_rb, nhan, mau):
    """08/11/2026: PMID 41110921 (đính chính bị rút, bác sĩ đã ký) hiện «RÚT BÀI: —» đỏ ở đầu trang — thiếu nhãn."""
    ngc = copy.deepcopy(G.NGU_CANH)
    ngc["rut_bai"] = {"trang_thai": tt_rb, "luc": "2026-11-08T00:00:00", "nguon": "pubmed"}
    doc = T.dung_word(G._hop_le(), ngc)
    p = next(x for x in doc.paragraphs if x.text.startswith("RÚT BÀI:"))
    assert p.text.startswith(f"RÚT BÀI: {nhan}")
    assert str(p.runs[-1].font.color.rgb) == T.MAU_CHU[mau]
