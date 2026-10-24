# -*- coding: utf-8 -*-
"""EndNote: KHÔNG post vào nhóm đã có — post luôn sinh nhóm MỚI cùng tên (24/10/2026, BH170).

Sự cố 24/10/2026: bước ⑧ của bộ năm (`nap_endnote_chu_de.py --file … --ap-dung`) post vào nhóm «EBM · <câu hỏi>» đã có ⇒
sinh nhóm trùng cho «Tiên lượng suy tim…» (group 133: 3 bài · 145: 14 bài) và «Viêm khớp dạng thấp (VKDT)…» (135 · 150).
Đo lại trên BẢN SAO thư viện (EndNote 22.4.1): post vào tên đã có nhóm — kể cả nhóm vừa tạo trong cùng phiên — LUÔN sinh nhóm
mới (171 → +146 → +158; tên mới 159 → +160); EndNote.sdef không có lệnh thêm vào nhóm đã có.

Khoá: `EndNoteMac.dang_vao_nhom` đo sdb.eni theo group_id TRƯỚC khi post — đã có ⇒ NhomDaCo, không đo được ⇒ KhongDoDuocNhom,
không post · `nap_chu_de` đưa bài thiếu vào HÀNG CHỜ cho bác sĩ, `nhom_trung_ten` trước = sau · hàng chờ tự dọn bài bác sĩ đã
kéo vào nhóm · `--cho-vao-nhom` liệt kê/hiện bài · trạng thái và hòm việc thấy hàng chờ · dưới pytest không ghi tệp thật.
Ngoại tuyến, sqlite giả tạo trong test; không đường dẫn máy thật.
"""
from __future__ import annotations

import html
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


N = _nap("_nec_t1024", "nap_endnote_chu_de.py")
sk = _nap("_sk_t1024", "endnote_suc_khoe.py")
tdxv = _nap("_tdxv_t1024", "tu_de_xuat_viec.py")

TEN = "EBM · Tiên lượng suy tim: yếu tố quyết định"
TEN_KHAC = "EBM · Viêm khớp dạng thấp"


def _spec(ten: str) -> bytes:
    return ('<?xml version="1.0" encoding="UTF-8"?><group version="1"><ids><id>X</id><name>' + html.escape(ten, quote=False)
            + "</name></ids><rules><rule>TYPE;3</rule></rules></group>").encode()


def _thanh_vien(*rec: int) -> bytes:
    return b"\x00\x00\x00\x02" + len(rec).to_bytes(4, "little") + b"".join(r.to_bytes(4, "little") for r in rec)


def _tao_thu_vien(goc: Path, nhom: list[tuple]) -> Path:
    """Thư viện giả + sdb.eni; `nhom` = [(group_id, tên, members bytes)]."""
    tv = goc / "Thu vien.enl"
    tv.write_bytes(b"enl")
    d = goc / "Thu vien.Data" / "sdb"
    d.mkdir(parents=True)
    kn = sqlite3.connect(d / "sdb.eni")
    kn.executescript("""
        CREATE TABLE refs (id INTEGER PRIMARY KEY, trash_state INTEGER, title TEXT);
        CREATE TABLE file_res (refs_id INTEGER, file_path TEXT);
        CREATE TABLE groups (group_id INTEGER PRIMARY KEY, recs_stamp INTEGER NOT NULL DEFAULT 0, spec BLOB NOT NULL DEFAULT "",
                             members BLOB NOT NULL DEFAULT "");
    """)
    kn.executemany("INSERT INTO refs VALUES (?, 0, 'x')", [(r,) for r in (30, 31, 32, 40, 41)])
    kn.executemany("INSERT INTO groups (group_id, spec, members) VALUES (?,?,?)", [(g, _spec(t), m) for g, t, m in nhom])
    kn.commit()
    kn.close()
    return tv


def _them_nhom(tv: Path, ten: str, rec: list[int]) -> int:
    """Hành vi đo 24/10/2026: post vào bất kỳ tên nào cũng CHÈN nhóm mới (không bao giờ cộng vào nhóm cùng tên)."""
    kn = sqlite3.connect(sk.sdb(tv))
    try:
        gid = (kn.execute("SELECT max(group_id) FROM groups").fetchone()[0] or 0) + 1
        kn.execute("INSERT INTO groups (group_id, spec, members) VALUES (?,?,?)", (gid, _spec(ten), _thanh_vien(*rec)))
        kn.commit()
    finally:
        kn.close()
    return gid


def _rid(r: int) -> str:
    return f'<RecordID database="2" recNum="{r}" />'


class _EnSdb:
    """EndNote giả trên sdb.eni sqlite: dùng NGUYÊN chốt `EndNoteMac.nhom_theo_ten`/`dang_vao_nhom`; lệnh AppleScript (`_chay`)
    mô phỏng post đúng như đo 24/10/2026 — luôn sinh nhóm mới."""
    nhom_theo_ten = N.EndNoteMac.nhom_theo_ten
    dang_vao_nhom = N.EndNoteMac.dang_vao_nhom
    _truoc_khi_ghi = N.EndNoteMac._truoc_khi_ghi

    def __init__(self, tv: Path, pmid_rec: dict[str, int] | None = None):
        self.thu_vien, self.ten, self.ung_dung = tv, tv.name, "EndNote 2025"
        self.pmid_rec = pmid_rec or {}
        self.post: list[tuple[str, list[int]]] = []

    def _chay(self, than: str, *doi_so: str, **_kw) -> str:
        assert "post records" in than, than
        ten, _cua_so, *ids = doi_so
        rec = [int(sk.so_rec(i)) for i in ids]
        self.post.append((ten, rec))
        _them_nhom(self.thu_vien, ten, rec)
        return ""

    def tim_khop(self, gia_tri, truong):
        if truong != "Accession Number":
            return {v: [] for v in gia_tri}
        return {v: ([_rid(self.pmid_rec[v])] if v in self.pmid_rec else []) for v in gia_tri}

    def tep_dinh_kem(self, ids):
        return {i: 9 for i in ids}  # đã có tệp ⇒ không gắn PDF


@pytest.fixture
def cho(tmp_path, monkeypatch):
    tep = tmp_path / "cho-vao-nhom.json"
    monkeypatch.setenv("EBM_ENDNOTE_CHO_VAO_NHOM", str(tep))
    monkeypatch.setattr(N, "_ngu", lambda s: None)
    return tep


@pytest.fixture
def tv(tmp_path):
    return _tao_thu_vien(tmp_path, [(171, TEN, _thanh_vien(40)), (5, "Jisc Library Hub Discover", _thanh_vien())])


def _mac(tv: Path):
    """EndNoteMac THẬT (dựng không qua __init__ — chạy được cả ngoài macOS), `_chay` ghi lại lệnh AppleScript."""
    en = object.__new__(N.EndNoteMac)
    en.ung_dung, en.thu_vien, en.ten, en._csdl = "EndNote 2025", tv, tv.name, None
    en.lenh = []
    en._chay = lambda than, *doi_so, **kw: en.lenh.append((than, doi_so)) or ""
    return en


# ── chốt trung tâm: EndNoteMac.dang_vao_nhom ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("ten", [TEN, TEN.upper(), " " + TEN + " "])
def test_endnote_mac_khong_post_vao_ten_da_co_nhom(tv, ten):
    en = _mac(tv)
    with pytest.raises(N.NhomDaCo) as loi:
        en.dang_vao_nhom([_rid(30)], ten)
    assert loi.value.group_id == [171] and en.lenh == [], "đã có nhóm mà vẫn gửi post ⇒ EndNote sinh nhóm trùng tên"


def test_endnote_mac_khong_do_duoc_sdb_thi_khong_post(tmp_path):
    tv = tmp_path / "Lib.enl"
    tv.write_bytes(b"enl")
    en = _mac(tv)
    with pytest.raises(N.KhongDoDuocNhom):
        en.dang_vao_nhom([_rid(30)], TEN)
    assert en.lenh == []


def test_endnote_mac_thanh_vien_hong_la_khong_do_duoc(tmp_path):
    tv = _tao_thu_vien(tmp_path, [(171, TEN, b"\x00\x00\x00\x02\x09\x00\x00\x00")])
    en = _mac(tv)
    with pytest.raises(N.KhongDoDuocNhom):
        en.dang_vao_nhom([_rid(30)], TEN)
    assert en.lenh == []


def test_endnote_mac_ten_moi_post_dung_mot_lan(tv):
    en = _mac(tv)
    en.dang_vao_nhom([_rid(30), _rid(31)], TEN_KHAC)
    assert len(en.lenh) == 1 and "post records" in en.lenh[0][0]
    assert en.lenh[0][1] == (TEN_KHAC, "Thu vien.enl", _rid(30), _rid(31))
    en.dang_vao_nhom([], TEN)
    assert len(en.lenh) == 1, "không có bản ghi thì không gửi gì"


# ── nap_chu_de (bước ⑧ bộ năm) ───────────────────────────────────────────────────────────────────────────────────────────
def _nap(en, tmp_path, ten_nhom: str, pmids: list[str]) -> dict:
    dash = tmp_path / "WebDashboard_EBM_TienLuongSuyTim_20261024.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    data = {"meta": {"question": ten_nhom[len("EBM · "):]}, "items": [{"id": f"I{k}", "pmid": p} for k, p in enumerate(pmids)]}
    return N.nap_chu_de(dash, endnote=en, ap_dung=True, kho=None, doc_data=lambda p: data, ten_nhom=ten_nhom,
                        loai_tru={"doi": {}, "pmid": {}}, lay_pm=lambda x: {}, lay_ep=lambda x: {}, lay_cr=lambda d: None)


def test_nap_vao_nhom_da_co_khong_sinh_nhom_trung_ma_ghi_hang_cho(tv, tmp_path, cho, capsys):
    en = _EnSdb(tv, {"111": 30, "222": 31, "333": 40})
    truoc = sk.nhom_trung_ten(sk.doc_nhom(tv))
    bc = _nap(en, tmp_path, TEN, ["111", "222", "333"])
    assert en.post == [], "nhóm đã có mà bước ⑧ vẫn post ⇒ nhóm trùng tên (sự cố 24/10/2026)"
    assert sk.nhom_trung_ten(sk.doc_nhom(tv)) == truoc == []
    assert [(n["group_id"], n["rec"]) for n in sk.nhom_theo_ten(tv, TEN)] == [(171, [40])]
    assert bc["dang_vao_nhom"] == 0 and bc["cho_vao_nhom_moi"] == [30, 31] and bc["nhom_da_co"] == [{"group_id": 171, "so_ban_ghi": 1}]
    hang = json.loads(cho.read_text(encoding="utf-8"))["thu_vien"][sk.khoa_thu_vien(tv)][TEN]
    assert hang["rec"] == [30, 31] and hang["group_id"] == [171] and hang["dashboard"] == ["WebDashboard_EBM_TienLuongSuyTim_20261024.html"]
    N._in_bao_cao(bc)
    ra = capsys.readouterr().out
    assert "🛎 Nhóm đã có (group_id 171: 1 bài) — KHÔNG post" in ra and "recNum 30, 31" in ra and "--cho-vao-nhom" in ra


def test_nap_ten_moi_tao_dung_mot_nhom(tv, tmp_path, cho):
    en = _EnSdb(tv, {"111": 30, "222": 31})
    bc = _nap(en, tmp_path, TEN_KHAC, ["111", "222"])
    assert en.post == [(TEN_KHAC, [30, 31])] and bc["dang_vao_nhom"] == 2
    assert [n["rec"] for n in sk.nhom_theo_ten(tv, TEN_KHAC)] == [[30, 31]] and bc["nhom_sau"][0]["so_ban_ghi"] == 2
    assert sk.nhom_trung_ten(sk.doc_nhom(tv)) == [] and not cho.exists()
    bc2 = _nap(en, tmp_path, TEN_KHAC, ["111", "222"])  # chạy lại: nhóm đã đủ ⇒ không post, hàng chờ trống
    assert len(en.post) == 1 and bc2["cho_vao_nhom_moi"] == [] and not cho.exists()


def test_hang_cho_tu_don_bai_bac_si_da_keo_vao_nhom(tv, tmp_path, cho):
    en = _EnSdb(tv, {"111": 30, "222": 31, "333": 40})
    _nap(en, tmp_path, TEN, ["111", "222", "333"])
    kn = sqlite3.connect(sk.sdb(tv))
    kn.execute("UPDATE groups SET members = ? WHERE group_id = 171", (_thanh_vien(40, 30),))  # bác sĩ kéo 30 vào nhóm
    kn.commit()
    kn.close()
    assert [n["rec"] for n in sk.cho_vao_nhom_con_lai(tv)] == [[31]]
    bc = _nap(en, tmp_path, TEN, ["111", "222", "333"])
    assert bc["cho_vao_nhom"] == [31] and en.post == []
    assert json.loads(cho.read_text(encoding="utf-8"))["thu_vien"][sk.khoa_thu_vien(tv)][TEN]["rec"] == [31]


def test_ghi_hang_cho_duoi_pytest_khong_cham_tep_that(tmp_path, monkeypatch):
    monkeypatch.delenv("EBM_ENDNOTE_CHO_VAO_NHOM", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))  # lỡ chốt hỏng thì cũng chỉ ghi vào thư mục tạm
    with pytest.raises(N.KhongChayDuoc):
        N.ghi_cho_vao_nhom(tmp_path / "Lib.enl", TEN, them=[30], da_vao=set(), group_id=[171])
    assert not (tmp_path / ".ebm-endnote-cho-vao-nhom.json").exists()


# ── đọc hàng chờ · trạng thái · hòm việc · --cho-vao-nhom ────────────────────────────────────────────────────────────────
def test_doc_hang_cho_vang_la_rong_hong_la_loi(tmp_path):
    assert sk.doc_cho_vao_nhom(tmp_path / "khong-co.json") == {"thu_vien": {}}
    hong = tmp_path / "hong.json"
    hong.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError):
        sk.doc_cho_vao_nhom(hong)
    hong.write_text(json.dumps({"thu_vien": {"x": {"t": {"rec": ["30"]}}}}), encoding="utf-8")
    with pytest.raises(ValueError):
        sk.doc_cho_vao_nhom(hong)


def test_trang_thai_va_hom_viec_thay_hang_cho(tv, cho, monkeypatch):
    N.ghi_cho_vao_nhom(tv, TEN, them=[30, 40], da_vao=set(), group_id=[171])
    kq = sk.tinh_trang(tv)
    assert kq["cho_vao_nhom"] == [{"ten": TEN, "rec": [30], "group_id": [171], "so_nhom": 1, "dashboard": []}], \
        "40 đã nằm trong nhóm 171 ⇒ không còn chờ"
    viec = tdxv.giac_quan_endnote(lambda: {**kq, "nhom_trung_ten": [{"ten": TEN_KHAC, "so_nhom": 2,
                                                                       "nhom": [{"group_id": 1, "so_ban_ghi": 3},
                                                                                {"group_id": 2, "so_ban_ghi": 14}]}]})
    assert (2, f"1 bản ghi EndNote chờ bác sĩ kéo vào nhóm «{TEN}»",
            f"python3 tools/nap_endnote_chu_de.py --cho-vao-nhom \"{TEN}\"") in viec
    assert any("tách 2 nhóm cùng tên (3 + 14 bài)" in d for _u, d, _l in viec)
    monkeypatch.setattr(sk, "ban_sao_csdl", lambda tv_: (_ for _ in ()).throw(sqlite3.DatabaseError("hỏng")))
    kq2 = sk.tinh_trang(tv)
    assert kq2["cho_vao_nhom"] is None and any("hàng chờ đưa vào nhóm" in c for c in kq2["canh_bao"])


class _EnCli:
    hien: list = []

    def __init__(self, ung_dung, thu_vien):
        self.thu_vien = thu_vien

    def dang_mo_dung_thu_vien(self):
        return True

    def hien_ban_ghi(self, rec):
        _EnCli.hien = [*_EnCli.hien, rec]


def test_cli_cho_vao_nhom_liet_ke_don_va_hien(tv, tmp_path, cho, monkeypatch, capsys):
    ch = tmp_path / "ch.json"
    ch.write_text(json.dumps({"thu_vien": str(tv), "ung_dung": "EndNote 2025"}), encoding="utf-8")
    monkeypatch.setattr(N, "CAU_HINH", ch)
    N.ghi_cho_vao_nhom(tv, TEN, them=[30, 31], da_vao=set(), group_id=[171])
    kn = sqlite3.connect(sk.sdb(tv))
    kn.execute("UPDATE groups SET members = ? WHERE group_id = 171", (_thanh_vien(40, 31),))
    kn.commit()
    kn.close()
    assert N.chay_cho_vao_nhom("") == N.MA_OK
    ra = capsys.readouterr().out
    assert f"👤 «{TEN}» (group_id 171) — 1 bản ghi chờ bác sĩ đưa vào nhóm: recNum 30" in ra
    assert json.loads(cho.read_text(encoding="utf-8"))["thu_vien"][sk.khoa_thu_vien(tv)][TEN]["rec"] == [30], "31 đã vào nhóm ⇒ dọn"
    _EnCli.hien = []
    assert N.chay_cho_vao_nhom(TEN.lower(), endnote_cls=_EnCli) == N.MA_OK and _EnCli.hien == [[30]]
    assert N.chay_cho_vao_nhom("EBM · không có", endnote_cls=_EnCli) == N.MA_THAM_SO
    assert N.main(["--cho-vao-nhom", "--file", "x.html"]) == N.MA_THAM_SO


def test_hang_cho_khop_ten_theo_khoa_va_nhom_tao_lai_thi_don(tv, tmp_path, cho):
    N.ghi_cho_vao_nhom(tv, TEN, them=[30], da_vao=set(), group_id=[171])
    N.ghi_cho_vao_nhom(tv, TEN.upper(), them=[31], da_vao=set(), group_id=[171])
    bang = json.loads(cho.read_text(encoding="utf-8"))["thu_vien"][sk.khoa_thu_vien(tv)]
    assert list(bang) == [TEN] and bang[TEN]["rec"] == [30, 31], "tên khác hoa/thường là CÙNG nhóm với EndNote"
    N.ghi_cho_vao_nhom(tv, TEN_KHAC, them=[30, 31], da_vao=set(), group_id=[])  # bài chờ của một nhóm bác sĩ đã xoá
    en = _EnSdb(tv, {"111": 30, "222": 31})
    bc = _nap(en, tmp_path, TEN_KHAC, ["111", "222"])  # chưa có nhóm ⇒ post tạo lại với đủ bài
    assert en.post == [(TEN_KHAC, [30, 31])] and bc["dang_vao_nhom"] == 2
    assert TEN_KHAC not in json.loads(cho.read_text(encoding="utf-8"))["thu_vien"][sk.khoa_thu_vien(tv)], \
        "bài đã vào nhóm vừa tạo lại phải được dọn khỏi hàng chờ"
