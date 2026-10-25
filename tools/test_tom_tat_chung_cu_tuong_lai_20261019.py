# -*- coding: utf-8 -*-
"""Chứng cứ SAU NÀY mới vào hàng chờ tóm tắt Word (19/10/2026, bác sĩ: «Bây giờ xây dựng cho những chứng cứ sau này, còn hiện
tại hãy để nguyên»). Kiểm: mốc «để nguyên» loại bản ghi cũ; thiếu/hỏng mốc ⇒ KHÔNG đoán (None); ⑨ của bộ năm chạy SAU ⑧;
giác quan hòm việc báo 🛎 khi hàng chờ còn mục và chết (⚪) khi chưa có mốc."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T = _nap("_ttcc_tl", "tom_tat_chung_cu_word.py")
tdxv = _nap("_tdxv_tl", "tu_de_xuat_viec.py")


def _bg(rec: int, pmid: str, doi: str | None = None) -> dict:
    return {"rec": rec, "pmid": pmid, "doi": doi, "tieu_de": f"Bài {rec}", "khoa": f"PMID-{pmid}", "pdf": ["x.pdf"]}


def _thu_vien_gia(tmp_path, monkeypatch, ids=(1, 2, 3)):
    """Thư viện giả: bảng refs trong sqlite bộ nhớ; `ban_ghi_co_pdf` thay bằng danh sách cố định."""
    tv = tmp_path / "EndNote" / "My.enl"
    tv.parent.mkdir(parents=True)

    def ket_noi(_tv):
        c = sqlite3.connect(":memory:")
        c.execute("create table refs (id integer)")
        c.executemany("insert into refs values (?)", [(i,) for i in ids])
        return c
    # Thư viện thật luôn có bảng nhóm; hàng chờ đọc nhóm để loại bài chỉ thuộc đề tài «NC · » (25/10/2026) — ở đây: chưa có nhóm.
    monkeypatch.setitem(T._MOD, "sk", types.SimpleNamespace(_ket_noi=ket_noi, doc_nhom=lambda _tv: [],
                                                            khoa_ten=_nap("_sk_tl", "endnote_suc_khoe.py").khoa_ten))
    return tv


def test_thieu_moc_khong_doan(tmp_path, monkeypatch):
    tv = _thu_vien_gia(tmp_path, monkeypatch)
    monkeypatch.setattr(T, "ban_ghi_co_pdf", lambda _tv: [_bg(9, "999")])
    assert T.hang_cho(tv) is None


def test_moc_loai_ban_ghi_cu_chi_giu_ban_ghi_moi_chua_co_word(tmp_path, monkeypatch):
    tv = _thu_vien_gia(tmp_path, monkeypatch, ids=(1, 2, 3))
    assert T.ghi_moc(tv, "Bây giờ xây dựng cho những chứng cứ sau này, còn hiện tại hãy để nguyên") == 0
    monkeypatch.setattr(T, "ban_ghi_co_pdf", lambda _tv: [_bg(2, "222"), _bg(4, "444"), _bg(5, "555")])
    T.tep_word(tv, "PMID-555").parent.mkdir(parents=True, exist_ok=True)
    T.tep_word(tv, "PMID-555").write_bytes(b"x")  # đã có Word ⇒ không chờ
    assert [x["rec"] for x in T.hang_cho(tv)] == [4]


def test_moc_khong_ghi_de_va_doi_loi_bac_si(tmp_path, monkeypatch):
    tv = _thu_vien_gia(tmp_path, monkeypatch)
    assert T.ghi_moc(tv, "ngắn") == 1 and not T.tep_moc(tv).exists()
    assert T.ghi_moc(tv, "hiện tại hãy để nguyên các bản ghi") == 0
    truoc = T.tep_moc(tv).read_text(encoding="utf-8")
    assert T.ghi_moc(tv, "một lời khác đủ dài để ghi") == 1
    assert T.tep_moc(tv).read_text(encoding="utf-8") == truoc


def test_moc_hong_hoac_rong_la_khong_co_moc(tmp_path, monkeypatch):
    tv = _thu_vien_gia(tmp_path, monkeypatch)
    T.tep_moc(tv).parent.mkdir(parents=True)
    for noi_dung in ("{hỏng", json.dumps({"rec": []}), json.dumps({"khac": 1})):
        T.tep_moc(tv).write_text(noi_dung, encoding="utf-8")
        assert T.doc_moc(tv) is None  # rỗng/hỏng KHÔNG được coi là «mốc rỗng» — sẽ đẩy cả thư viện vào hàng chờ


def test_loc_theo_dashboard(tmp_path, monkeypatch):
    tv = _thu_vien_gia(tmp_path, monkeypatch, ids=(1,))
    T.ghi_moc(tv, "hiện tại hãy để nguyên các bản ghi")
    monkeypatch.setattr(T, "ban_ghi_co_pdf", lambda _tv: [_bg(4, "444"), _bg(6, "666", "10.1/abc"), _bg(7, "777")])
    monkeypatch.setattr(T, "trich_dan_cua_dashboard", lambda d: ({"444"}, {"10.1/abc"}))
    assert [x["rec"] for x in T.hang_cho(tv, dashboard=Path("d.html"))] == [4, 6]


def test_bo_nam_chay_tom_tat_word_sau_endnote():
    """⑨ phải chạy SAU ⑧ (bài vừa nạp mới có mặt trong thư viện) và chỉ khi --online (gói đọc tra rút bài)."""
    src = (REPO / "tools" / "xuat_goi_cap_nhat.py").read_text(encoding="utf-8")
    than_main = src[src.index("def main() -> int:"):]
    i_en = than_main.index('print("⑧ EndNote…")')
    i_tt = than_main.index('print("⑨ Tóm tắt chứng cứ Word (trích dẫn mới có PDF)…")')
    assert i_en < i_tt
    doan = than_main[i_tt:]
    assert "buoc_tom_tat_word(py, dash)" in doan and "elif not a.online:" in doan[:doan.index("buoc_tom_tat_word(py, dash)")]
    xg = _nap("_xgcn_tl", "xuat_goi_cap_nhat.py")
    lenh = xg.lenh_tom_tat_word("py", Path("d.html"))
    assert lenh[2:] == ["hang-cho", "--dashboard", "d.html", "--chuan-bi"]


def test_giac_quan_hom_viec(monkeypatch):
    assert tdxv.giac_quan_tom_tat_word(lambda: []) == []
    kq = tdxv.giac_quan_tom_tat_word(lambda: [_bg(4, "444"), _bg(5, "555")])
    assert len(kq) == 1 and kq[0][0] == 2 and "2 trích dẫn MỚI" in kq[0][1] and "hang-cho" in kq[0][2]
    chet = []
    monkeypatch.setattr(tdxv, "_ghi_chet", lambda lenh, ly: chet.append(ly))
    assert tdxv.giac_quan_tom_tat_word(lambda: None) == [] and chet == ["chưa có mốc «để nguyên»"]


def test_hom_viec_goi_giac_quan_voi_nhan_chuong():
    src = (REPO / "tools" / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    assert 'for uu, dong, lenh in giac_quan_tom_tat_word():\n        de_xuat.append((uu, "🛎", dong, lenh))' in src


def test_skill_day_buoc_9():
    skill = (REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "SKILL.md").read_text(encoding="utf-8")
    for k in ("**⑨ Tóm tắt chứng cứ Word", "hang-cho", "kiem-cheo", "dung <mã> --gan-endnote --ap-dung", "ĐỘC LẬP",
              "để nguyên"):
        assert k in skill, k
