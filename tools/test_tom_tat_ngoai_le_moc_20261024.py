# -*- coding: utf-8 -*-
"""Ngoại lệ mốc «để nguyên» theo TẦNG (24/10/2026). Bác sĩ: «Hãy kiểm tra lại tất cả các trích dẫn trong Endnote giúp tôi,đảm bảo
đã được tải,đọc toàn văn và tóm tắt chứng cứ một cách chi tiết» → chọn «T1 + T2». Kiểm: không có tệp ngoại lệ ⇒ hàng chờ y như luật
19/10 (chỉ bản ghi MỚI); có ngoại lệ T1/T2 ⇒ thêm bản ghi CŨ đúng tầng, bỏ tầng khác và bản đã có Word; tệp hỏng/thiếu lời bác sĩ ⇒
không ngoại lệ; lọc theo dashboard áp cho cả hai nhóm; hòm việc tách hai số đếm."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOI = "Hãy kiểm tra lại tất cả các trích dẫn trong Endnote giúp tôi — chọn T1 + T2"


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T = _nap("_ttcc_nlm", "tom_tat_chung_cu_word.py")
tdxv = _nap("_tdxv_nlm", "tu_de_xuat_viec.py")


def _bg(rec: int, pmid: str, doi: str | None = None) -> dict:
    return {"rec": rec, "pmid": pmid, "doi": doi, "tieu_de": f"Bài {rec}", "khoa": f"PMID-{pmid}", "pdf": ["x.pdf"]}


# Ngữ cảnh dashboard giả: PMID → quyết định của mục mà bài là nguồn (None = chỉ tham khảo).
QUYET = {"111": "apply", "222": "consider", "333": "notyet", "444": None}


def _thu_vien(tmp_path, monkeypatch, ids=(1, 2, 3, 4)):
    tv = tmp_path / "EndNote" / "My.enl"
    tv.parent.mkdir(parents=True)

    def ket_noi(_tv):
        c = sqlite3.connect(":memory:")
        c.execute("create table refs (id integer)")
        c.executemany("insert into refs values (?)", [(i,) for i in ids])
        return c
    monkeypatch.setitem(T._MOD, "sk", types.SimpleNamespace(_ket_noi=ket_noi))
    assert T.ghi_moc(tv, "Bây giờ xây dựng cho những chứng cứ sau này, còn hiện tại hãy để nguyên") == 0
    monkeypatch.setattr(T, "ban_ghi_co_pdf",
                        lambda _tv: [_bg(1, "111"), _bg(2, "222"), _bg(3, "333"), _bg(4, "444"), _bg(9, "999")])
    monkeypatch.setattr(T, "ngu_canh_dashboard", lambda: {"pmid:gia": {}})  # có dashboard (rỗng ⇒ không đo được)
    monkeypatch.setattr(T, "_ngu_canh_cua", lambda ds, pmid, doi: (
        [{"vai": "muc", "decision": QUYET[pmid]}] if QUYET.get(pmid) else []))
    return tv


def test_khong_co_ngoai_le_giu_luat_moc(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    hc = T.hang_cho(tv)
    assert [x["rec"] for x in hc] == [9] and hc[0]["nguon_hang_cho"] == "moi"


def test_ngoai_le_t1_t2_them_ban_ghi_cu_dung_tang(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    assert T.ghi_ngoai_le_moc(tv, [2, 1], LOI) == 0
    hc = T.hang_cho(tv)
    assert [(x["rec"], x["nguon_hang_cho"]) for x in hc] == [(9, "moi"), (1, "ngoai_le_moc"), (2, "ngoai_le_moc")]
    assert [x.get("tang") for x in hc[1:]] == [1, 2]


def test_ban_ghi_cu_da_co_word_khong_vao_hang_cho(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    T.ghi_ngoai_le_moc(tv, [1, 2], LOI)
    T.tep_word(tv, "PMID-111").parent.mkdir(parents=True, exist_ok=True)
    T.tep_word(tv, "PMID-111").write_bytes(b"x")
    assert [x["rec"] for x in T.hang_cho(tv)] == [9, 2]


def test_ngoai_le_can_loi_bac_si_va_tang_hop_le(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    assert T.ghi_ngoai_le_moc(tv, [1], "ngắn") == 1 and not T.tep_ngoai_le(tv).exists()
    assert T.ghi_ngoai_le_moc(tv, [5], LOI) == 1 and not T.tep_ngoai_le(tv).exists()
    assert T.ghi_ngoai_le_moc(tv, [1], LOI) == 0 and T.doc_ngoai_le_moc(tv) == {1}


def test_tep_ngoai_le_hong_hoac_thieu_loi_la_khong_ngoai_le(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    for nd in ("{hỏng", json.dumps({"tang": [1, 2]}), json.dumps({"tang": "1", "loi_bac_si": LOI})):
        T.tep_ngoai_le(tv).write_text(nd, encoding="utf-8")
        assert T.doc_ngoai_le_moc(tv) == set()
        assert [x["rec"] for x in T.hang_cho(tv)] == [9]


def test_loc_dashboard_ap_cho_ca_ban_ghi_cu(tmp_path, monkeypatch):
    tv = _thu_vien(tmp_path, monkeypatch)
    T.ghi_ngoai_le_moc(tv, [1, 2], LOI)
    monkeypatch.setattr(T, "trich_dan_cua_dashboard", lambda d: ({"222"}, set()))
    assert [x["rec"] for x in T.hang_cho(tv, dashboard=Path("d.html"))] == [2]


def test_hom_viec_tach_moi_va_cu():
    kq = tdxv.giac_quan_tom_tat_word(lambda: [dict(_bg(9, "999"), nguon_hang_cho="moi"),
                                             dict(_bg(1, "111"), nguon_hang_cho="ngoai_le_moc"),
                                             dict(_bg(2, "222"), nguon_hang_cho="ngoai_le_moc")])
    assert len(kq) == 1 and "1 trích dẫn MỚI" in kq[0][1] and "2 bản ghi CŨ" in kq[0][1]
    kq = tdxv.giac_quan_tom_tat_word(lambda: [dict(_bg(1, "111"), nguon_hang_cho="ngoai_le_moc")])
    assert "MỚI" not in kq[0][1] and "1 bản ghi CŨ" in kq[0][1]


def test_co_ngoai_le_ma_khong_doc_duoc_dashboard_la_khong_do_duoc(tmp_path, monkeypatch):
    """Worktree/bản sao trần không có EBM-Dashboards ⇒ mọi bản ghi rơi vào T4 ⇒ «0 chờ» là XANH GIẢ — phải báo không đo được."""
    import pytest
    tv = _thu_vien(tmp_path, monkeypatch)
    T.ghi_ngoai_le_moc(tv, [1, 2], LOI)
    monkeypatch.setattr(T, "ngu_canh_dashboard", lambda: {})
    with pytest.raises(T.NgoaiLeKhongDoDuoc):
        T.hang_cho(tv)
    chet = []
    monkeypatch.setattr(tdxv, "_ghi_chet", lambda lenh, ly: chet.append(ly))
    assert tdxv.giac_quan_tom_tat_word(lambda: T.hang_cho(tv)) == [] and chet and "NgoaiLeKhongDoDuoc" in chet[0]
