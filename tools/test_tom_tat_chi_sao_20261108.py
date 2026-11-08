# -*- coding: utf-8 -*-
"""Chính sách «chỉ ★» của hàng chờ tóm tắt Word (08/11/2026). Bác sĩ: «tóm tắt Word tiếng Việt chỉ với các chứng cứ áp dụng cho
thực hành lâm sàng với độ tin cậy cao và mới nhất». Kiểm: không có tệp chính sách ⇒ hàng chờ y như luật 19/10 + ngoại lệ 24/10;
bật ⇒ chỉ bản ghi đạt luật ★ của `gan_tag_endnote.dat_ap_dung_tin_cay` (một nguồn sự thật cho tag lẫn hàng chờ), áp cho cả bản ghi
MỚI lẫn bản ghi CŨ của ngoại lệ mốc, xếp năm xuất bản giảm dần; không đọc được dashboard ⇒ không đo được (không «0 chờ»); tệp hỏng/
thiếu lời bác sĩ/`bat` sai ⇒ không lọc; hòm việc ghi rõ ★."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
LOI = "tóm tắt Word tiếng Việt chỉ với các chứng cứ áp dụng cho thực hành lâm sàng với độ tin cậy cao và mới nhất"


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T = _nap("_ttcc_cs", "tom_tat_chung_cu_word.py")
tdxv = _nap("_tdxv_cs", "tu_de_xuat_viec.py")


def _muc(decision, grade, design="RCT", ban_cu=False):
    return {"vai": "muc", "decision": decision, "gradeLevel": grade, "design": design, "ban_cu": ban_cu}


# PMID → ngữ cảnh dashboard. ★ = 101 (apply/high), 102 (apply/moderate), 105 (na + guideline), 108 (ban cũ low + bản mới high).
NGU_CANH = {
    "101": [_muc("apply", "high")],
    "102": [_muc("apply", "moderate")],
    "103": [_muc("apply", "low")],                                  # apply nhưng chứng cứ thấp
    "104": [_muc("consider", "high")],                              # cân nhắc
    "105": [_muc("apply", "na", "Guideline ESC 2025")],             # guideline không chấm GRADE
    "106": [_muc("apply", "na", "Consensus chuyên gia")],           # consensus không bao giờ đạt
    "107": [_muc("apply", "high", ban_cu=True)],                    # chỉ còn ở bản cũ
    "108": [_muc("apply", "low", ban_cu=True), _muc("apply", "high")],
    "109": [{"vai": "tham_khao", "decision": "apply", "gradeLevel": "high"}],  # chỉ là tham khảo
}
NAM = {"101": "2019", "102": "2025 Mar", "103": "2024", "104": "2026", "105": "2025", "106": "2023", "107": "2026",
       "108": "", "109": "2026", "201": "2022", "202": "2021"}


def _bg(rec: int, pmid: str) -> dict:
    return {"rec": rec, "pmid": pmid, "doi": None, "tieu_de": f"Bài {rec}", "khoa": f"PMID-{pmid}", "pdf": ["x.pdf"],
            "nam": NAM.get(pmid, "")}


def _thu_vien(tmp_path, monkeypatch, *, moi=range(101, 110), cu=()):
    """Mốc gồm recNum 1–5 (bản ghi CŨ); bản ghi MỚI có recNum = PMID (101…); `cu` = [(rec, pmid)] bản ghi cũ có PDF."""
    tv = tmp_path / "EndNote" / "My.enl"
    tv.parent.mkdir(parents=True)
    tv.write_bytes(b"enl")

    def ket_noi(_tv):
        c = sqlite3.connect(":memory:")
        c.execute("create table refs (id integer)")
        c.executemany("insert into refs values (?)", [(i,) for i in range(1, 6)])
        return c
    monkeypatch.setitem(T._MOD, "sk", types.SimpleNamespace(_ket_noi=ket_noi, doc_nhom=lambda _tv: [],
                                                            khoa_ten=_nap("_sk_cs", "endnote_suc_khoe.py").khoa_ten,
                                                            thu_vien_cau_hinh=lambda: tv))
    monkeypatch.setattr(T, "THU_MUC_DE_TAI", tmp_path / "exports")  # không đọc danh mục đề tài thật của máy
    assert T.ghi_moc(tv, "Bây giờ xây dựng cho những chứng cứ sau này, còn hiện tại hãy để nguyên") == 0
    ban_ghi = [_bg(int(p), str(p)) for p in moi] + [_bg(r, p) for r, p in cu]
    monkeypatch.setattr(T, "ban_ghi_co_pdf", lambda _tv: [dict(b) for b in ban_ghi])
    monkeypatch.setattr(T, "ngu_canh_dashboard", lambda: {"pmid:gia": {}})
    monkeypatch.setattr(T, "_ngu_canh_cua", lambda ds, pmid, doi: NGU_CANH.get(pmid, []))
    return tv


def test_khong_co_chinh_sach_giu_hang_cho_cu(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    assert not T.doc_chi_sao(tv)
    hc = T.hang_cho(tv)
    assert [x["rec"] for x in hc] == list(range(101, 110)), "chưa bật ⇒ mọi trích dẫn mới có PDF, xếp theo recNum"
    assert not any("sao" in x for x in hc)


def test_bat_chi_sao_chi_giu_ban_ghi_dat_luat_sao(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    assert T.ghi_chi_sao(tv, LOI) == 0 and T.doc_chi_sao(tv)
    hc = T.hang_cho(tv)
    assert {x["rec"] for x in hc} == {101, 102, 105, 108}
    assert all(x["sao"] is True and x["nguon_hang_cho"] == "moi" for x in hc)


def test_xep_moi_nhat_truoc_nam_roi_recnum(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    T.ghi_chi_sao(tv, LOI)
    assert [x["rec"] for x in T.hang_cho(tv)] == [105, 102, 101, 108], "2025 (rec lớn trước) → 2019 → không rõ năm cuối"
    assert T.nam_xuat_ban({"nam": "2025 Mar"}) == 2025 and T.nam_xuat_ban({"nam": "in press"}) == 0


def test_chi_sao_ap_ca_ban_ghi_cu_ngoai_le_moc(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch, moi=(101,), cu=[(1, "201"), (2, "202"), (3, "104")])
    NGU_CANH_CU = dict(NGU_CANH, **{"201": [_muc("apply", "high")], "202": [_muc("apply", "low")]})
    monkeypatch.setattr(T, "_ngu_canh_cua", lambda ds, pmid, doi: NGU_CANH_CU.get(pmid, []))
    assert T.ghi_ngoai_le_moc(tv, [1, 2], "Hãy kiểm tra lại tất cả các trích dẫn — chọn T1 + T2") == 0
    truoc = [(x["rec"], x["nguon_hang_cho"]) for x in T.hang_cho(tv)]
    assert truoc == [(101, "moi"), (1, "ngoai_le_moc"), (2, "ngoai_le_moc"), (3, "ngoai_le_moc")]
    T.ghi_chi_sao(tv, LOI)
    sau = [(x["rec"], x["nguon_hang_cho"]) for x in T.hang_cho(tv)]
    assert sau == [(1, "ngoai_le_moc"), (101, "moi")], "T1 thấp (rec 2) và T2 (rec 3) bị loại; 2022 xếp trước 2019"


def test_luat_sao_la_cua_gan_tag_endnote_mot_nguon(tmp_path, monkeypatch):
    """Hàng chờ gọi ĐÚNG hàm luật của gan_tag_endnote — đổi luật ở đó thì hàng chờ đổi theo (không có bản sao luật thứ hai)."""
    tv = _thu_vien(tmp_path, monkeypatch)
    T.ghi_chi_sao(tv, LOI)
    gte = T.mod("gte")
    monkeypatch.setattr(gte, "dat_ap_dung_tin_cay", lambda nc: any(x.get("decision") == "consider" for x in nc))
    assert [x["rec"] for x in T.hang_cho(tv)] == [104]


def test_bat_ma_khong_doc_duoc_dashboard_la_khong_do_duoc(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    T.ghi_chi_sao(tv, LOI)
    monkeypatch.setattr(T, "ngu_canh_dashboard", lambda: {})
    with pytest.raises(T.ChiSaoKhongDoDuoc):
        T.hang_cho(tv)
    chet = []
    monkeypatch.setattr(tdxv, "_ghi_chet", lambda lenh, ly: chet.append(ly))
    assert tdxv.giac_quan_tom_tat_word(lambda: T.hang_cho(tv)) == [] and chet, "cảm biến chết (⚪), không phải «0 chờ»"


def test_bat_ma_hang_cho_rong_khong_can_dashboard(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch, moi=())
    T.ghi_chi_sao(tv, LOI)
    monkeypatch.setattr(T, "ngu_canh_dashboard", lambda: {})
    assert T.hang_cho(tv) == [], "không có ứng viên thì không cần đọc dashboard"


@pytest.mark.parametrize("nd", ["{hỏng", json.dumps({"bat": True}), json.dumps({"bat": True, "loi_bac_si": "ngắn"}),
                                json.dumps({"bat": "true", "loi_bac_si": LOI}), json.dumps([1, 2])])
def test_tep_hong_hoac_thieu_loi_la_khong_loc(tmp_path, monkeypatch, nd):
    tv = _thu_vien(tmp_path, monkeypatch)
    T.tep_chi_sao(tv).parent.mkdir(parents=True, exist_ok=True)
    T.tep_chi_sao(tv).write_text(nd, encoding="utf-8")
    assert not T.doc_chi_sao(tv)
    assert len(T.hang_cho(tv)) == 9


def test_ghi_can_loi_bac_si_va_tat_duoc(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    assert T.ghi_chi_sao(tv, "ngắn") == 1 and not T.tep_chi_sao(tv).exists()
    assert T.ghi_chi_sao(tv, LOI) == 0 and T.doc_chi_sao(tv)
    assert T.ghi_chi_sao(tv, "bác sĩ tắt chính sách chỉ ★ để tóm tắt lại mọi bài", tat=True) == 0
    assert not T.doc_chi_sao(tv) and len(T.hang_cho(tv)) == 9


def test_hom_viec_ghi_ro_sao(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    T.ghi_chi_sao(tv, LOI)
    kq = tdxv.giac_quan_tom_tat_word(lambda: T.hang_cho(tv))
    assert len(kq) == 1 and "4 trích dẫn MỚI" in kq[0][1] and "★ Áp dụng – tin cậy cao" in kq[0][1]
    kq = tdxv.giac_quan_tom_tat_word(lambda: [dict(_bg(9, "999"), nguon_hang_cho="moi")])
    assert "★" not in kq[0][1], "hàng chờ chưa lọc ★ thì không được ghi ★"


def test_cli_hang_cho_va_tien_do_bao_chinh_sach(tmp_path, monkeypatch, capsys):
    tv = _thu_vien(tmp_path, monkeypatch)
    monkeypatch.setattr(T, "_thu_vien", lambda: tv)
    assert T.main(["chi-sao", "--loi", LOI]) == 0
    capsys.readouterr()
    assert T.main(["hang-cho"]) == 0
    ra = capsys.readouterr().out
    assert "🛎 4 trích dẫn ★ Áp dụng – tin cậy cao" in ra and "mới nhất trước" in ra
    assert ra.index("PMID-105") < ra.index("PMID-101") < ra.index("PMID-108")
    monkeypatch.setattr(T, "liet_ke", lambda _tv, **k: [])
    assert T.main(["tien-do"]) == 0
    assert "CHỈ ★ Áp dụng – tin cậy cao" in capsys.readouterr().out
