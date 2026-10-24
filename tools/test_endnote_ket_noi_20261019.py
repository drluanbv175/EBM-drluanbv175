# -*- coding: utf-8 -*-
"""Kết nối EndNote ↔ Claude (19/10/2026 — bác sĩ: «Hãy làm tất cả 6 việc giúp tôi»).

Khoá: sức khoẻ thư viện (bản sao xung đột, tệp chỉ còn trên mây, vị trí đồng bộ, nhóm chờ thùng rác đọc từ `sdb.eni`) · khoá
ghi (chờ khi bác sĩ đang thao tác, khoá giữa tiến trình) · mọi lệnh GHI của EndNoteMac đi qua khoá · máy chủ MCP không có công
cụ xoá và trả lỗi đúng giao thức · cài Claude Desktop giữ khoá khác · nút thùng rác chỉ báo «xong» khi bản ghi thật vào thùng
rác · giác quan hòm việc · KHÔNG chuỗi lệnh nào (ngoài docstring) chứa `delete record` (đo 19/10/2026: xoá HẲN). Ngoại tuyến.
"""
from __future__ import annotations

import ast
import importlib.util
import io
import json
import os
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


sk = _nap("_sk_t1019", "endnote_suc_khoe.py")
kg = _nap("_kg_t1019", "khoa_ghi_endnote.py")
nec = _nap("_nec_t1019", "nap_endnote_chu_de.py")
mcp = _nap("_mcp_t1019", "mcp/endnote_ebm_mcp.py")
cntr = _nap("_cntr_t1019", "chuyen_nhom_vao_thung_rac.py")
tdxv = _nap("_tdxv_t1019", "tu_de_xuat_viec.py")


def _thanh_vien(*rec: int) -> bytes:
    return b"\x00\x00\x00\x02" + len(rec).to_bytes(4, "little") + b"".join(r.to_bytes(4, "little") for r in rec)


@pytest.fixture
def thu_vien(tmp_path):
    """Thư viện giả: `.enl` + `.Data/sdb/sdb.eni` với refs, file_res, groups giống lược đồ đo 19/10/2026."""
    tv = tmp_path / "My EndNote Library.enl"
    tv.write_bytes(b"enl")
    sdb = tmp_path / "My EndNote Library.Data" / "sdb"
    sdb.mkdir(parents=True)
    kn = sqlite3.connect(sdb / "sdb.eni")
    kn.executescript("""
        CREATE TABLE refs (id INTEGER PRIMARY KEY, trash_state INTEGER, title TEXT, year TEXT, accession_number TEXT,
                           electronic_resource_number TEXT);
        CREATE TABLE file_res (refs_id INTEGER, file_path TEXT, file_type INTEGER, file_pos INTEGER);
        CREATE TABLE groups (group_id INTEGER, recs_stamp INTEGER, spec BLOB, members BLOB);
    """)
    kn.executemany("INSERT INTO refs VALUES (?,?,?,?,?,?)", [
        (10, 0, "Bài A", "2024", "111", "10.1/a"), (11, 1, "Bài B", "2023", "222", "10.1/B"),
        (12, 0, "Bài C", "2022", "", "10.1/c"), (13, 0, "Bài D", "2021", "444", "")])
    kn.execute("INSERT INTO file_res VALUES (10, 'x.pdf', 1, 0)")
    spec = '<?xml version="1.0"?><group version="1"><ids><name>{}</name></ids></group>'
    kn.executemany("INSERT INTO groups VALUES (?,?,?,?)", [
        (1, 0, spec.format("_Cho thung rac 18-10 (khong toan van)").encode(), _thanh_vien(10, 11)),
        (2, 0, spec.format("_Cho thung rac 18-10 (khong toan van)").encode(), _thanh_vien(12)),
        (3, 0, spec.format("EBM · Tim mạch &amp; thận").encode(), _thanh_vien(13))])
    kn.commit()
    kn.close()
    return tv


# ── sức khoẻ thư viện ────────────────────────────────────────────────────────────────────────────────────────────────────
def test_giai_thanh_vien_dung_khuon_do_thuc_va_tu_choi_khuon_la():
    assert sk.giai_thanh_vien(bytes.fromhex("00000002" "04000000" "89190000" "8a190000" "8b190000" "8c190000")) == [
        6537, 6538, 6539, 6540]
    for xau in (b"", b"\x00\x00\x00\x02", _thanh_vien(1, 2)[:-1]):
        with pytest.raises(ValueError):
            sk.giai_thanh_vien(xau)


def test_nhom_cho_thung_rac_gop_nhom_trung_ten_va_dem_ban_ghi_con_o_thu_vien(thu_vien):
    ds = sk.nhom_cho_thung_rac(thu_vien)
    assert ds == [{"ten": "_Cho thung rac 18-10 (khong toan van)", "so_nhom_cung_ten": 2, "tong": 3, "con_o_thu_vien": 2}]
    assert ("EBM · Tim mạch & thận", [13]) in sk.nhom_trong_csdl(thu_vien)


def test_kiem_thung_rac_phan_biet_thung_rac_thu_vien_va_xoa_han(thu_vien):
    assert sk.kiem_thung_rac(thu_vien, [10, 11, 99]) == {"da_vao_thung_rac": [11], "con_o_thu_vien": [10], "khong_con_hang": [99]}


def test_tra_dinh_danh_theo_pmid_va_doi_khong_phan_biet_hoa(thu_vien):
    kq = sk.tra_dinh_danh(thu_vien, ["111", "10.1/b", "https://doi.org/10.1/C", "999"])
    assert kq["111"][0]["rec"] == 10 and kq["111"][0]["so_tep"] == 1
    assert kq["10.1/b"][0]["thung_rac"] is True
    assert kq["https://doi.org/10.1/C"][0]["rec"] == 12 and kq["999"] == []


def test_ban_sao_xung_dot_bat_cac_kieu_onedrive_icloud(tmp_path):
    tv = tmp_path / "My EndNote Library.enl"
    tv.write_bytes(b"x")
    (tmp_path / "My EndNote Library.Data" / "sdb").mkdir(parents=True)
    for ten in ("My EndNote Library 2.enl", "My EndNote Library (1).Data", "My EndNote Library-MacBook Pro.enl",
                "My EndNote Library Backup.enl", "Thu vien khac 2.enl"):
        (tmp_path / ten).write_bytes(b"x")
    for ten in ("sdb 2.eni", "sdb.eni", "pdb-DESKTOP-ABC.eni"):
        (tmp_path / "My EndNote Library.Data" / "sdb" / ten).write_bytes(b"x")
    ten_bat = sorted(p.name for p in sk.ban_sao_xung_dot(tv))
    assert ten_bat == sorted(["My EndNote Library 2.enl", "My EndNote Library (1).Data", "My EndNote Library-MacBook Pro.enl",
                              "sdb 2.eni", "pdb-DESKTOP-ABC.eni"])


def test_vi_tri_dong_bo_onedrive_va_icloud_cung_inode(tmp_path):
    assert sk.vi_tri_dong_bo(Path("/home/x/Library/CloudStorage/OneDrive-Personal/EndNote/a.enl")) == "OneDrive"
    nha = tmp_path
    that = nha / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "Documents"
    that.mkdir(parents=True)
    (that / "a.enl").write_bytes(b"x")
    (nha / "Documents").symlink_to(that)
    assert sk.vi_tri_dong_bo(nha / "Documents" / "a.enl", nha=nha) == "iCloud"
    rieng = nha / "EndNote"
    rieng.mkdir()
    (rieng / "b.enl").write_bytes(b"x")
    assert sk.vi_tri_dong_bo(rieng / "b.enl", nha=nha) is None


def test_tep_chua_tai_dem_co_dataless(thu_vien, monkeypatch):
    if not hasattr(os.stat_result, "st_flags"):
        pytest.skip("không có st_flags trên nền tảng này")
    that = os.lstat

    class _St:
        def __init__(self, st, co):
            self.st_flags = (st.st_flags | sk.SF_DATALESS) if co else st.st_flags

    monkeypatch.setattr(sk.os, "lstat", lambda p: _St(that(p), str(p).endswith(".enl")))
    assert sk.tep_chua_tai(thu_vien) == 1


# ── khoá ghi ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_bac_si_dang_dung_chi_khi_endnote_o_truoc_va_vua_thao_tac():
    assert kg.bac_si_dang_dung("EndNote 2025", lambda: "EndNote 2025", lambda: 3.0) is True
    assert kg.bac_si_dang_dung("EndNote 2025", lambda: "EndNote 2025", lambda: 300.0) is False
    assert kg.bac_si_dang_dung("EndNote 2025", lambda: "Claude", lambda: 0.0) is False
    assert kg.bac_si_dang_dung("EndNote 2025", lambda: "EndNote 2025", lambda: None) is False


class _Gio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def ngu(self, s):
        self.t += s


def _reset_khoa():
    kg._DANG_GIU.update({"pid": None, "tep": None, "thong_bao": False, "pham_vi": 0, "tu_pham_vi": False})


def test_khoa_cho_bac_si_ranh_roi_moi_ghi_va_bao_mot_lan(tmp_path):
    _reset_khoa()
    gio, tb, ban = _Gio(), [], iter([True, True, False])
    kg.cho_phep_ghi_loi("EndNote 2025", "gắn tệp", tep=tmp_path / "k.json", dang_dung=lambda: next(ban), ngu=gio.ngu,
                        dong_ho=gio, thong_bao=tb.append)
    assert gio.t == 10 and tb == ["gắn tệp"]
    assert json.loads((tmp_path / "k.json").read_text())["pid"] == os.getpid()
    kg.cho_phep_ghi_loi("EndNote 2025", "lần hai", tep=tmp_path / "k.json", dang_dung=lambda: False, ngu=gio.ngu, dong_ho=gio,
                        thong_bao=tb.append)
    assert tb == ["gắn tệp"], "thông báo lặp mỗi lệnh ghi"


def test_khoa_bac_si_ban_qua_han_thi_bo_luot_ghi(tmp_path):
    _reset_khoa()
    gio = _Gio()
    with pytest.raises(kg.BacSiDangDungEndNote):
        kg.cho_phep_ghi_loi("EndNote 2025", "x", tep=tmp_path / "k.json", dang_dung=lambda: True, ngu=gio.ngu, dong_ho=gio,
                            thong_bao=lambda s: None)
    assert not (tmp_path / "k.json").exists()


def test_khoa_cua_tien_trinh_khac_con_song_thi_cho_roi_bo_khoa_chet_thi_bo_qua(tmp_path):
    _reset_khoa()
    import time as _t
    tep = tmp_path / "k.json"
    tep.write_text(json.dumps({"pid": os.getpid() + 999999, "luc_epoch": _t.time()}))
    gio = _Gio()
    with pytest.raises(kg.DangCoTienTrinhKhacGhi):
        kg.cho_phep_ghi_loi("EndNote 2025", "x", tep=tep, dang_dung=lambda: False, ngu=gio.ngu, dong_ho=gio,
                            thong_bao=lambda s: None, song=lambda pid: True)
    kg.cho_phep_ghi_loi("EndNote 2025", "x", tep=tep, dang_dung=lambda: False, ngu=gio.ngu, dong_ho=gio,
                        thong_bao=lambda s: None, song=lambda pid: False)
    assert json.loads(tep.read_text())["pid"] == os.getpid()


def test_moi_lenh_ghi_cua_endnotemac_qua_khoa_truoc_khi_chay():
    en = object.__new__(nec.EndNoteMac)
    en.ten, en.ung_dung, en._csdl = "Lib.enl", "EndNote 2025", "1"
    en.nhom_theo_ten = lambda ten: []  # tên nhóm mới — chốt nhóm đã có (24/10/2026) cho post
    nhat: list[str] = []
    en._truoc_khi_ghi = lambda ly_do: nhat.append("KHOA")
    en._chay = lambda than, *ds, **kw: (nhat.append("CHAY"), "internal-pdf://1/a.pdf" if "File Attachments" in than else "")[1]
    en.nhap(Path("/tmp/x.xml"))
    en.dang_vao_nhom(["<RecordID database=\"1\" recNum=\"1\" />"], "EBM · a")
    en.gan_tep("<RecordID database=\"1\" recNum=\"1\" />", "internal-pdf://1/a.pdf")
    en.ghi_truong([("<RecordID database=\"1\" recNum=\"1\" />", "x")], "Notes")
    assert nhat == ["KHOA", "CHAY"] * 4


# ── máy chủ MCP ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_mcp_khoi_tao_liet_ke_va_cong_cu_la_tra_loi_dung_giao_thuc():
    kq = mcp.xu_ly({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}})
    assert kq["result"]["protocolVersion"] == "2025-03-26" and kq["result"]["serverInfo"]["name"] == "endnote-ebm"
    assert mcp.xu_ly({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    ten = [t["name"] for t in mcp.xu_ly({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]]
    assert ten and all(not any(x in t for x in ("xoa", "delete", "remove", "empty")) for t in ten)
    la = mcp.xu_ly({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "endnote_xoa_ban_ghi"}})
    assert la["result"]["isError"] is True
    assert mcp.xu_ly({"jsonrpc": "2.0", "id": 4, "method": "abc"})["error"]["code"] == -32601


def test_mcp_cong_cu_ghi_chay_kho_mac_dinh_va_loi_tra_ve_isError(monkeypatch, thu_vien):
    goi = []

    class _En:
        def so_csdl(self):
            return "1"

        def dang_vao_nhom(self, ids, ten):
            goi.append((ids, ten))

        def thanh_vien_nhom(self, ten):
            return []

    # Thư viện giả THẬT (21/10/2026): công cụ ghi giờ đo nhóm trong sdb.eni trước cả khi chạy khô — đường dẫn không tồn tại
    # bị từ chối (fail-closed), không còn là fixture hợp lệ cho ca «chạy khô thành công».
    monkeypatch.setattr(mcp, "_endnote", lambda: (_En(), thu_vien))
    kq = mcp.xu_ly({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                    "params": {"name": "endnote_dua_vao_nhom", "arguments": {"rec_nums": [7], "ten_nhom": "EBM · a"}}})
    assert json.loads(kq["result"]["content"][0]["text"])["chay_kho"] is True and goi == []
    kq = mcp.xu_ly({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                    "params": {"name": "endnote_chuan_bi_thung_rac", "arguments": {"ten_nhom": "EBM · a"}}})
    assert kq["result"]["isError"] is True, "chuẩn bị thùng rác phải chỉ nhận nhóm «_Cho thung rac…»"


def test_mcp_vong_stdio_json_hong_va_lo(monkeypatch):
    vao = io.StringIO('khong phai json\n[{"jsonrpc":"2.0","id":1,"method":"ping"},{"jsonrpc":"2.0","method":"x"}]\n')
    ra = io.StringIO()
    mcp.chay(vao, ra)
    dong = [json.loads(x) for x in ra.getvalue().splitlines()]
    assert dong[0]["error"]["code"] == -32700 and dong[1] == {"jsonrpc": "2.0", "id": 1, "result": {}} and len(dong) == 2


def test_cai_claude_desktop_giu_khoa_khac_chay_kho_va_sao_luu(tmp_path):
    tep = tmp_path / "claude_desktop_config.json"
    tep.write_text(json.dumps({"mcpServers": {"khac": {"command": "x"}}, "theme": "dark"}))
    kq = mcp.cai_claude_desktop(False, tep)
    assert "da_ghi" not in kq and "endnote-ebm" not in json.loads(tep.read_text())["mcpServers"]
    kq = mcp.cai_claude_desktop(True, tep)
    moi = json.loads(tep.read_text())
    assert moi["theme"] == "dark" and moi["mcpServers"]["khac"] == {"command": "x"}
    assert moi["mcpServers"]["endnote-ebm"]["args"][0].endswith("endnote_ebm_mcp.py") and Path(kq["sao_luu"]).exists()
    assert mcp.cai_claude_desktop(True, tep)["khong_doi"] is True


# ── nút thùng rác ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_nut_thung_rac_chi_bao_xong_khi_moi_ban_ghi_vao_thung_rac():
    assert cntr.bao_cao({"da_vao_thung_rac": [1, 2], "con_o_thu_vien": [], "khong_con_hang": []})[0] == 0
    ma, dong = cntr.bao_cao({"da_vao_thung_rac": [1], "con_o_thu_vien": [5], "khong_con_hang": []})
    assert ma == 1 and "5" in dong
    assert cntr.nhom_cho(["EBM · a", "_Cho thung rac X", "_Cho thung rac X", "x _Cho thung rac"], "_Cho thung rac") == [
        "_Cho thung rac X"]


def test_nut_thung_rac_chi_hien_ban_ghi_khong_xoa():
    goi = []

    class _En:
        ten = "Lib.enl"

        def _chay(self, than, *ds):
            goi.append(than)

    cntr.hien_cho_bac_si(_En(), ["<RecordID database=\"1\" recNum=\"1\" />"])
    assert "show records in" in goi[0] and "delete" not in goi[0].lower()


# ── giác quan hòm việc ───────────────────────────────────────────────────────────────────────────────────────────────────
def test_giac_quan_endnote_canh_bao_va_nhom_cho_hay_chet_khi_khong_do_duoc(monkeypatch):
    kq = tdxv.giac_quan_endnote(lambda: {"do_duoc": True, "canh_bao": ["2 bản sao xung đột"],
                                         "nhom_cho_thung_rac": [{"ten": "_Cho thung rac A", "tong": 5, "con_o_thu_vien": 3}]})
    assert [u for u, _d, _l in kq] == [1, 2] and "3/5" in kq[1][1]
    chet = []
    monkeypatch.setattr(tdxv, "_ghi_chet", lambda lenh, ly: chet.append(ly))
    assert tdxv.giac_quan_endnote(lambda: {"do_duoc": False, "ly_do": "chưa khai"}) == [] and chet == ["chưa khai"]


# ── chốt nguồn: không lệnh nào chứa `delete record` ──────────────────────────────────────────────────────────────────────
def _chuoi_khong_phai_docstring(cay: ast.AST) -> list[str]:
    doc = set()
    for n in ast.walk(cay):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.body:
            dau = n.body[0]
            if isinstance(dau, ast.Expr) and isinstance(getattr(dau, "value", None), ast.Constant):
                doc.add(id(dau.value))
    return [n.value for n in ast.walk(cay) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc]


def test_khong_chuoi_lenh_nao_chua_delete_record():
    pham = []
    for p in sorted((REPO / "tools").rglob("*.py")):
        if p.name.startswith("test_") or "__pycache__" in p.parts:
            continue
        try:
            cay = ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        pham += [f"{p.relative_to(REPO)}: {s[:60]!r}" for s in _chuoi_khong_phai_docstring(cay) if "delete record" in s.lower()]
    assert not pham, "lệnh AppleScript `delete record` XOÁ HẲN bản ghi EndNote (đo 19/10/2026): " + "; ".join(pham)
