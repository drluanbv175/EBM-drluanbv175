# -*- coding: utf-8 -*-
"""Nhóm EndNote trùng tên đo THEO group_id (21/10/2026, BH167).

Sự cố: thư viện có 2 nhóm «EBM · Biến chứng thần kinh ở bệnh nhân đái tháo đường — …» (group_id 114: 5 bài, 162: 4 bài)
nhưng MCP `endnote_nhom` báo 1 nhóm 9 bài — AppleScript `get records in "<tên>"` trả HỢP mọi nhóm cùng tên ⇒ tưởng đã gộp.
`post … as "<tên>"` vào tên đã có nhóm từng TẠO NHÓM MỚI (đo 18/10/2026).

Khoá: đọc `groups` trên BẢN SAO TẠM của sdb.eni (kể cả -wal) · số bài TỪNG nhóm + cờ trùng tên · `endnote_nhom` với tên trùng
trả từng nhóm riêng, không cộng · `endnote_dua_vao_nhom` từ chối (fail-closed) khi tên đích có ≥2 nhóm hoặc không đo được,
ghi xong đo lại theo group_id · `endnote_trang_thai` có danh sách nhóm trùng tên. Ngoại tuyến, sqlite giả tạo trong test.
"""
from __future__ import annotations

import html
import importlib.util
import json
import sqlite3
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


sk = _nap("_sk_t1021", "endnote_suc_khoe.py")
mcp = _nap("_mcp_t1021", "mcp/endnote_ebm_mcp.py")

TEN_DTD = "EBM · Biến chứng thần kinh ở bệnh nhân đái tháo đường — tầm soát & dự phòng"
TEN_MMN = "EBM · Bệnh lý mạch máu não — hợp nhất"


def _spec(ten: str, kieu: int = 3) -> bytes:
    """`groups.spec` đúng khuôn đo 21/10/2026 (TYPE;3 = nhóm tự tạo, TYPE;6 = nhóm tìm trực tuyến)."""
    return ('<?xml version="1.0" encoding="UTF-8"?><group version="1"><ids><id>X</id><name>' + html.escape(ten, quote=False)
            + f"</name></ids><rules><rule>TYPE;{kieu}</rule></rules></group>").encode()


def _thanh_vien(*rec: int) -> bytes:
    return b"\x00\x00\x00\x02" + len(rec).to_bytes(4, "little") + b"".join(r.to_bytes(4, "little") for r in rec)


def _tao_thu_vien(goc: Path, nhom: list[tuple], wal: bool = False):
    """Thư viện giả `<goc>/My EndNote Library.enl` + sdb.eni. `nhom` = [(group_id, tên, kiểu, members)].
    wal=True: trả về kết nối GHI đang mở (chế độ WAL) để test chèn dữ liệu chỉ nằm trong -wal."""
    tv = goc / "My EndNote Library.enl"
    tv.write_bytes(b"enl")
    d = goc / "My EndNote Library.Data" / "sdb"
    d.mkdir(parents=True)
    kn = sqlite3.connect(d / "sdb.eni")
    if wal:
        kn.execute("PRAGMA journal_mode=WAL")
        kn.execute("PRAGMA wal_autocheckpoint=0")
    kn.executescript("""
        CREATE TABLE refs (id INTEGER PRIMARY KEY, trash_state INTEGER, title TEXT, year TEXT, accession_number TEXT,
                           electronic_resource_number TEXT);
        CREATE TABLE file_res (refs_id INTEGER, file_path TEXT, file_type INTEGER, file_pos INTEGER);
        CREATE TABLE groups (group_id INTEGER PRIMARY KEY, recs_stamp INTEGER NOT NULL DEFAULT 0, spec BLOB NOT NULL DEFAULT "",
                             members BLOB NOT NULL DEFAULT "");
    """)
    kn.executemany("INSERT INTO refs VALUES (?,?,?,?,?,?)",
                   [(r, 1 if r == 24 else 0, f"Bài {r}", "2024", str(1000 + r), "") for r in (20, 21, 22, 23, 24, 30, 31, 32, 33, 40)])
    kn.executemany("INSERT INTO file_res VALUES (?, 'x.pdf', 1, 0)", [(20,), (30,), (31,)])
    kn.executemany("INSERT INTO groups (group_id, spec, members) VALUES (?,?,?)",
                   [(g, _spec(t, k), m) for g, t, k, m in nhom])
    kn.commit()
    if wal:
        kn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        return tv, kn
    kn.close()
    return tv


NHOM_CHUAN = [(5, "Jisc Library Hub Discover", 6, _thanh_vien()),
              (114, TEN_DTD, 3, _thanh_vien(20, 21, 22, 23, 24)),
              (162, TEN_DTD, 3, _thanh_vien(30, 31, 32, 33)),
              (171, TEN_MMN, 3, _thanh_vien(40))]


@pytest.fixture
def thu_vien(tmp_path):
    return _tao_thu_vien(tmp_path, NHOM_CHUAN)


def _goi(ten: str, doi: dict) -> dict:
    return mcp.xu_ly({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": ten, "arguments": doi}})["result"]


def _json(kq: dict) -> dict:
    assert kq["isError"] is False, kq["content"][0]["text"]
    return json.loads(kq["content"][0]["text"])


class _EnGia:
    """EndNote giả: `post` ghi thẳng một nhóm vào sdb giả — `tao_moi=True` mô phỏng post sinh nhóm MỚI cùng tên (đo 18/10)."""

    def __init__(self, tv: Path, tao_moi: bool = False):
        self.tv, self.tao_moi, self.goi = tv, tao_moi, []

    def so_csdl(self):
        return "1"

    def dang_vao_nhom(self, ids, ten):
        self.goi.append((ids, ten))
        rec = [sk.so_rec(i) for i in ids]
        kn = sqlite3.connect(sk.sdb(self.tv))
        try:
            cu = [g for g, s in kn.execute("SELECT group_id, spec FROM groups") if sk._giai_spec(s)[0] == ten]
            if cu and not self.tao_moi:
                mem = kn.execute("SELECT members FROM groups WHERE group_id = ?", (cu[0],)).fetchone()[0]
                kn.execute("UPDATE groups SET members = ? WHERE group_id = ?",
                           (_thanh_vien(*sk.giai_thanh_vien(mem), *rec), cu[0]))
            else:
                kn.execute("INSERT INTO groups (group_id, spec, members) VALUES (?,?,?)", (200 + len(cu), _spec(ten), _thanh_vien(*rec)))
            kn.commit()
        finally:
            kn.close()

    def thanh_vien_nhom(self, ten):
        raise AssertionError("không được đo nhóm theo TÊN qua AppleScript (trả HỢP nhóm trùng tên)")

    def ten_cac_nhom(self):
        raise AssertionError("không được liệt kê nhóm qua AppleScript")


# ── đọc nhóm theo group_id ───────────────────────────────────────────────────────────────────────────────────────────────
def test_doc_nhom_theo_group_id_so_bai_tung_nhom_va_loai(thu_vien):
    ds = sk.doc_nhom(thu_vien)
    assert [(n["group_id"], n["ten"], n["loai"], n["so_ban_ghi"]) for n in ds] == [
        (5, "Jisc Library Hub Discover", "online", 0), (114, TEN_DTD, "custom", 5), (162, TEN_DTD, "custom", 4),
        (171, TEN_MMN, "custom", 1)]
    assert ds[2]["rec"] == [30, 31, 32, 33]


def test_thanh_vien_hong_la_khong_do_duoc_khong_phai_nhom_rong(tmp_path):
    tv = _tao_thu_vien(tmp_path, [(7, "EBM · Hỏng", 3, b"\x00\x00\x00\x02\x05\x00\x00\x00")])
    n = sk.doc_nhom(tv)[0]
    assert n["so_ban_ghi"] is None and n["rec"] is None and "KHÔNG ĐO ĐƯỢC" in n["loi"]
    with pytest.raises(ValueError):
        sk.nhom_trong_csdl(tv)


def test_nhom_trung_ten_tach_tung_nhom_khong_phan_biet_hoa_thuong_va_nfc():
    ds = [{"group_id": 1, "ten": unicodedata.normalize("NFD", "Biến chứng"), "so_ban_ghi": 2},
          {"group_id": 2, "ten": " BIẾN CHỨNG ", "so_ban_ghi": 1},
          {"group_id": 3, "ten": "Khác", "so_ban_ghi": 0}, {"group_id": 4, "ten": "", "so_ban_ghi": 0},
          {"group_id": 5, "ten": "", "so_ban_ghi": 0}]
    assert sk.nhom_trung_ten(ds) == [{"ten": ds[0]["ten"], "so_nhom": 2,
                                      "nhom": [{"group_id": 1, "so_ban_ghi": 2}, {"group_id": 2, "so_ban_ghi": 1}]}]


def test_ban_sao_doc_ca_du_lieu_chi_nam_trong_wal(tmp_path):
    tv, kn = _tao_thu_vien(tmp_path, NHOM_CHUAN[:2], wal=True)
    try:
        kn.execute("INSERT INTO groups (group_id, spec, members) VALUES (?,?,?)", (162, _spec(TEN_DTD), _thanh_vien(30, 31)))
        kn.commit()
        assert Path(str(sk.sdb(tv)) + "-wal").stat().st_size > 0, "dữ liệu thử phải còn nằm trong -wal"
        assert [n["group_id"] for n in sk.nhom_theo_ten(tv, TEN_DTD)] == [114, 162]
    finally:
        kn.close()


def test_ban_sao_khong_mo_tep_that_va_khong_sinh_tep_canh_thu_vien(thu_vien, monkeypatch):
    thu_muc = sk.sdb(thu_vien).parent
    truoc = sorted(p.name for p in thu_muc.iterdir())
    that, uri = sqlite3.connect, []
    monkeypatch.setattr(sk.sqlite3, "connect", lambda d, *a, **k: (uri.append(unquote(str(d))), that(d, *a, **k))[1])
    sk.doc_nhom(thu_vien)
    assert uri and all(str(thu_muc) not in u and "mode=ro" in u for u in uri), uri
    assert sorted(p.name for p in thu_muc.iterdir()) == truoc


def test_ban_sao_chep_lai_khi_tep_goc_doi_va_bo_cuoc_thanh_khong_do_duoc(thu_vien, monkeypatch):
    that, dem, ngu = sk._dau_tep, [0], []

    def doi_lan_dau(goc):
        dem[0] += 1
        return (("", -1, -1),) if dem[0] == 1 else that(goc)

    monkeypatch.setattr(sk, "_dau_tep", doi_lan_dau)
    with sk.ban_sao_csdl(thu_vien, ngu=ngu.append) as kn:
        assert kn.execute("SELECT count(*) FROM groups").fetchone()[0] == 4
    assert len(ngu) == 1, "tệp gốc đổi trong lúc chép phải chép lại đúng một lần"
    monkeypatch.setattr(sk, "_dau_tep", lambda goc: (dem.append(0), (("", len(dem), 0),))[1])
    ngu.clear()
    with pytest.raises(OSError, match="KHÔNG ĐO ĐƯỢC"):
        with sk.ban_sao_csdl(thu_vien, so_lan=3, ngu=ngu.append):
            pass
    assert len(ngu) == 2, "3 lượt chép ⇒ nghỉ giữa các lượt, không nghỉ sau lượt cuối"


# ── MCP: endnote_nhom ────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def may_chu(thu_vien, monkeypatch):
    monkeypatch.setattr(mcp, "_thu_vien", lambda: thu_vien)
    monkeypatch.setattr(mcp.mod("sk"), "thu_vien_cau_hinh", lambda tep=None: thu_vien)
    return thu_vien


def test_endnote_nhom_liet_ke_theo_group_id_co_co_trung_ten_khong_can_endnote(may_chu, monkeypatch):
    monkeypatch.setattr(mcp, "_endnote", lambda: (_ for _ in ()).throw(AssertionError("không cần EndNote mở")))
    kq = _json(_goi("endnote_nhom", {}))
    assert [(n["group_id"], n["so_ban_ghi"], n["trung_ten"]) for n in kq["nhom"]] == [
        (5, 0, False), (114, 5, True), (162, 4, True), (171, 1, False)]
    assert kq["nhom_trung_ten"] == [{"ten": TEN_DTD, "so_nhom": 2,
                                     "nhom": [{"group_id": 114, "so_ban_ghi": 5}, {"group_id": 162, "so_ban_ghi": 4}]}]
    assert "canh_bao" in kq
    loc = _json(_goi("endnote_nhom", {"loc": "mạch MÁU"}))
    assert [n["group_id"] for n in loc["nhom"]] == [171] and loc["nhom_trung_ten"] == [] and "canh_bao" not in loc


def test_endnote_nhom_ten_trung_tra_tung_nhom_rieng_khong_cong(may_chu):
    kq = _json(_goi("endnote_nhom", {"ten_nhom": TEN_DTD}))
    assert kq["so_nhom"] == 2 and kq["trung_ten"] is True
    assert [(n["group_id"], n["so_ban_ghi"], [b["rec"] for b in n["ban_ghi"]]) for n in kq["nhom"]] == [
        (114, 5, [20, 21, 22, 23, 24]), (162, 4, [30, 31, 32, 33])]
    assert "so_ban_ghi" not in kq, "không được có số đếm gộp ở cấp ngoài (9 bài từng làm tưởng đã gộp)"
    assert "2 nhóm RIÊNG" in kq["canh_bao"] and "114" in kq["canh_bao"] and "162" in kq["canh_bao"]
    n114 = kq["nhom"][0]
    assert n114["chua_co_tep"] == 4 and n114["ban_ghi"][4]["thung_rac"] is True  # chỉ rec 20 có tệp
    mot = _json(_goi("endnote_nhom", {"ten_nhom": TEN_MMN}))
    assert mot["so_nhom"] == 1 and mot["trung_ten"] is False and "canh_bao" not in mot
    khong = _json(_goi("endnote_nhom", {"ten_nhom": "EBM · không có"}))
    assert khong["so_nhom"] == 0 and khong["nhom"] == [] and "ghi_chu" in khong


# ── MCP: endnote_dua_vao_nhom ────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("ap_dung", [False, True])
def test_dua_vao_nhom_tu_choi_khi_ten_dich_co_hai_nhom(may_chu, monkeypatch, ap_dung):
    en = _EnGia(may_chu)
    monkeypatch.setattr(mcp, "_endnote", lambda: (en, may_chu))
    kq = _goi("endnote_dua_vao_nhom", {"rec_nums": [40], "ten_nhom": TEN_DTD.upper(), "ap_dung": ap_dung})
    assert kq["isError"] is True and en.goi == []
    chu = kq["content"][0]["text"]
    assert chu.startswith("NhomTrungTen") and "TỪ CHỐI" in chu and "114" in chu and "162" in chu


def test_dua_vao_nhom_khong_do_duoc_sdb_thi_khong_ghi(may_chu, monkeypatch):
    en = _EnGia(may_chu)
    monkeypatch.setattr(mcp, "_endnote", lambda: (en, may_chu))
    monkeypatch.setattr(mcp.mod("sk"), "ban_sao_csdl", lambda tv: (_ for _ in ()).throw(sqlite3.DatabaseError("hỏng")))
    kq = _goi("endnote_dua_vao_nhom", {"rec_nums": [40], "ten_nhom": TEN_MMN, "ap_dung": True})
    assert kq["isError"] is True and en.goi == [] and kq["content"][0]["text"].startswith("KhongDoDuocNhom")


def test_dua_vao_nhom_ten_moi_tao_dung_mot_nhom_va_dem_theo_group_id(may_chu, monkeypatch):
    en = _EnGia(may_chu)
    monkeypatch.setattr(mcp, "_endnote", lambda: (en, may_chu))
    kho = _json(_goi("endnote_dua_vao_nhom", {"rec_nums": [30, 31], "ten_nhom": "EBM · mới"}))
    assert kho["chay_kho"] is True and kho["nhom_hien_co"] == [] and en.goi == []
    kq = _json(_goi("endnote_dua_vao_nhom", {"rec_nums": [30, 31], "ten_nhom": "EBM · mới", "ap_dung": True}))
    assert kq["nhom_moi_tao"] == [200] and kq["da_dang"] == 2 and "canh_bao" not in kq


def test_dua_vao_nhom_post_sinh_nhom_moi_cung_ten_thi_bao_va_lan_sau_tu_choi(may_chu, monkeypatch):
    en = _EnGia(may_chu, tao_moi=True)
    monkeypatch.setattr(mcp, "_endnote", lambda: (en, may_chu))
    kho = _json(_goi("endnote_dua_vao_nhom", {"rec_nums": [30], "ten_nhom": TEN_MMN}))
    assert kho["nhom_hien_co"] == [{"group_id": 171, "so_ban_ghi": 1}] and "TẠO NHÓM MỚI" in kho["luu_y"]
    kq = _json(_goi("endnote_dua_vao_nhom", {"rec_nums": [30], "ten_nhom": TEN_MMN, "ap_dung": True}))
    assert kq["nhom_moi_tao"] == [201] and "da_dang" not in kq and "≥2 nhóm" in kq["canh_bao"]
    assert [(n["group_id"], n["co_ban_ghi_yeu_cau"]) for n in kq["nhom_sau"]] == [(171, 0), (201, 1)]
    lan_sau = _goi("endnote_dua_vao_nhom", {"rec_nums": [31], "ten_nhom": TEN_MMN, "ap_dung": True})
    assert lan_sau["isError"] is True and len(en.goi) == 1


# ── trạng thái ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_trang_thai_co_danh_sach_nhom_trung_ten(may_chu, monkeypatch):
    monkeypatch.setattr(mcp, "_endnote", lambda: (_ for _ in ()).throw(RuntimeError("EndNote chưa mở")))
    kq = _json(_goi("endnote_trang_thai", {}))
    assert kq["nhom_trung_ten"] == [{"ten": TEN_DTD, "so_nhom": 2,
                                     "nhom": [{"group_id": 114, "so_ban_ghi": 5}, {"group_id": 162, "so_ban_ghi": 4}]}]


def test_trang_thai_khong_do_duoc_nhom_la_none_va_canh_bao(tmp_path):
    tv = tmp_path / "Lib.enl"
    tv.write_bytes(b"enl")
    kq = sk.tinh_trang(tv)
    assert kq["nhom_trung_ten"] is None and any("danh sách nhóm" in c for c in kq["canh_bao"])
