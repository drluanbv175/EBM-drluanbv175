# -*- coding: utf-8 -*-
"""Giao dịch ghi EndNote TREO — giác quan 🔴, khoá ghi từ chối, sao lưu cuộn lại nhật ký (BH177, 03/11/2026).

Sự cố có thật 02–03/11/2026: EndNote giữ MỘT giao dịch ghi chưa commit từ 19:00:59 ngày 02/11 tới 16:56 ngày 03/11 (~22 giờ).
`sdb.nal` là rollback journal của SQLite (tên lạ nên SQLite đọc từ ngoài không coi là nhật ký nóng). Suốt thời gian đó: không giác
quan nào đo tuổi giao dịch; các phiên Claude vẫn ghi tiếp vào giao dịch dở; mọi bản sao lưu `sao_luu_thu_vien` (backup() chỉ đọc
sdb.eni) là ảnh chụp giữa giao dịch («malformed» ⇒ một phiên kết luận nhầm «thư viện hỏng»). EndNote khởi động lại ⇒ cuộn lại hết;
chỉ cứu được nhờ bản EndNote online (Sync), kèm 88 bản ghi trùng.

Khoá: `giao_dich_treo` đo tuổi theo giờ tạo nhật ký (≥ NGUONG_TREO_GIAY ⇒ treo) · `tinh_trang` để khoá riêng `giao_dich_mo`,
`main` in 🔴 và mã 1 · hòm việc xếp ưu tiên 0 · `cho_phep_ghi_loi` ném `GiaoDichEndNoteTreo` TRƯỚC khi chờ/lấy khoá · EndNoteMac
truyền đúng thư viện · `sao_luu_thu_vien` có giao dịch ⇒ chép kèm nhật ký rồi CUỘN LẠI (bản sao lưu = trạng thái đã commit,
quick_check lành), không có giao dịch ⇒ như cũ. Fixture dùng một giao dịch SQLite THẬT bị tràn bộ đệm (trang dở đã xuống đĩa),
nhật ký đổi tên thành `sdb.nal` như EndNote. Ngoại tuyến, chạy được Mac/Windows/Linux.
"""
from __future__ import annotations

import importlib.util
import shutil
import sqlite3
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


SK = _nap("_sk_gdt_1103", "endnote_suc_khoe.py")
KG = _nap("_kg_gdt_1103", "khoa_ghi_endnote.py")
TV = _nap("_tv_gdt_1103", "tom_tat_endnote_vi.py")
DONG_DA_COMMIT = 300


@pytest.fixture(autouse=True)
def _hang_cho_tam(tmp_path, monkeypatch):
    """Hàng chờ đưa vào nhóm luôn ở tmp_path — không bao giờ tệp thật trong thư mục nhà."""
    monkeypatch.setenv("EBM_ENDNOTE_CHO_VAO_NHOM", str(tmp_path / "cho-vao-nhom.json"))


def _thu_vien_rong(tmp_path) -> Path:
    tv = tmp_path / "EndNote" / "My.enl"
    tv.parent.mkdir(parents=True)
    tv.write_bytes(b"enl")
    SK.sdb(tv).parent.mkdir(parents=True)
    return tv


@pytest.fixture
def thu_vien_giua_giao_dich(tmp_path) -> Path:
    """sdb.eni + sdb.nal chụp GIỮA một giao dịch SQLite thật: 300 dòng đã commit, giao dịch dở sửa mọi dòng thành «doi» và tràn
    bộ đệm (trang dở đã ghi xuống tệp db) — đúng tình trạng EndNote 02–03/11/2026."""
    tv = _thu_vien_rong(tmp_path)
    goc = tmp_path / "goc" / "sdb.eni"
    goc.parent.mkdir()
    kn = sqlite3.connect(goc, isolation_level=None)
    kn.execute("CREATE TABLE refs(id INTEGER PRIMARY KEY, title TEXT)")
    kn.execute("BEGIN")
    kn.executemany("INSERT INTO refs(title) VALUES (?)", [(f"bai {i} " + "y" * 300,) for i in range(DONG_DA_COMMIT)])
    kn.execute("COMMIT")
    kn.execute("PRAGMA cache_size=5")
    kn.execute("BEGIN IMMEDIATE")
    kn.executemany("INSERT INTO refs(title) VALUES (?)", [("x" * 2000,) for _ in range(400)])
    kn.execute("UPDATE refs SET title = 'doi'")
    shutil.copyfile(goc, SK.sdb(tv))
    shutil.copyfile(str(goc) + "-journal", SK.tep_nhat_ky(tv))
    kn.execute("ROLLBACK")
    kn.close()
    return tv


def _dong_doi(db: Path) -> int:
    kn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return kn.execute("SELECT count(*) FROM refs WHERE title = 'doi'").fetchone()[0]
    finally:
        kn.close()


# ─────────────────────────── giác quan ───────────────────────────

def test_giao_dich_treo_khong_co_hoac_da_commit_la_none(tmp_path):
    tv = _thu_vien_rong(tmp_path)
    assert SK.giao_dich_treo(tv) is None, "không có sdb.nal"
    SK.tep_nhat_ky(tv).write_bytes(b"\x00" * 64)
    assert SK.giao_dich_treo(tv) is None, "header đã xoá = giao dịch đã commit"


def test_giao_dich_treo_tinh_tuoi_theo_gio_mo(thu_vien_giua_giao_dich):
    tv, bay_gio = thu_vien_giua_giao_dich, time.time()
    ngan = SK.giao_dich_treo(tv, bay_gio=bay_gio, luc_mo=lambda p: bay_gio - 90)
    assert ngan and ngan["treo"] is False and ngan["phut"] == 1, "giao dịch mở 90 giây (EndNote đang ghi) không phải treo"
    dai = SK.giao_dich_treo(tv, bay_gio=bay_gio, luc_mo=lambda p: bay_gio - (22 * 3600 + 5 * 60))
    assert dai["treo"] is True and dai["phut"] == 22 * 60 + 5
    assert "CHƯA HOÀN TẤT" in dai["mo_ta"] and "22 giờ 5 phút" in dai["mo_ta"] and "Sync TRƯỚC" in dai["mo_ta"]
    bien = SK.giao_dich_treo(tv, bay_gio=bay_gio, luc_mo=lambda p: bay_gio - SK.NGUONG_TREO_GIAY)
    assert bien["treo"] is True, "đúng ngưỡng là treo"


def test_luc_mo_nhat_ky_doc_duoc_tep_that(thu_vien_giua_giao_dich):
    mo = SK.luc_mo_nhat_ky(SK.tep_nhat_ky(thu_vien_giua_giao_dich))
    assert time.time() - 3600 < mo <= time.time() + 5


def test_tinh_trang_va_main_bao_do_khi_treo(thu_vien_giua_giao_dich, monkeypatch, capsys):
    tv = thu_vien_giua_giao_dich
    monkeypatch.setattr(SK, "thu_vien_cau_hinh", lambda tep=None: tv)
    monkeypatch.setattr(SK, "luc_mo_nhat_ky", lambda p: time.time() - 3 * 3600)
    kq = SK.tinh_trang(tv)
    assert kq["giao_dich_mo"]["treo"] is True
    assert not any("CHƯA HOÀN TẤT" in c for c in kq["canh_bao"]), "treo là khoá riêng 🔴, không lẫn vào cảnh báo 🟠"
    assert SK.main([]) == 1
    ra = capsys.readouterr().out
    assert "🔴 EndNote giữ một giao dịch ghi CHƯA HOÀN TẤT" in ra and "không có giao dịch ghi treo" not in ra


def test_tinh_trang_giao_dich_ngan_khong_bao(thu_vien_giua_giao_dich, monkeypatch):
    monkeypatch.setattr(SK, "luc_mo_nhat_ky", lambda p: time.time() - 30)
    gd = SK.tinh_trang(thu_vien_giua_giao_dich)["giao_dich_mo"]
    assert gd and gd["treo"] is False


def test_hom_viec_xep_giao_dich_treo_uu_tien_0():
    tdxv = _nap("_tdxv_gdt_1103", "tu_de_xuat_viec.py")
    kq = {"do_duoc": True, "canh_bao": ["1 bản sao xung đột"], "giao_dich_mo": {"treo": True, "mo_ta": "EndNote giữ … TREO"}}
    ra = tdxv.giac_quan_endnote(tinh_trang=lambda: kq)
    assert ra[0][0] == 0 and "TREO" in ra[0][2], ra
    kq["giao_dich_mo"] = {"treo": False, "mo_ta": "mở 1 phút"}
    assert all(r[0] != 0 for r in tdxv.giac_quan_endnote(tinh_trang=lambda: kq))


# ─────────────────────────── khoá ghi ───────────────────────────

def test_khoa_ghi_tu_choi_khi_treo_truoc_khi_lay_khoa(tmp_path):
    tep = tmp_path / "khoa.json"

    def treo():
        KG.kiem_giao_dich_treo(Path("x.enl"), sk=SimpleNamespace(
            thu_vien_cau_hinh=lambda: None, giao_dich_treo=lambda tv, bay_gio=None: {"treo": True, "mo_ta": "treo 22 giờ"}))

    with pytest.raises(KG.GiaoDichEndNoteTreo, match="treo 22 giờ"):
        KG.cho_phep_ghi_loi("EndNote 2025", "nhập", tep=tep, dang_dung=lambda: False, thong_bao=lambda s: None,
                            kiem_giao_dich=treo)
    assert not tep.exists(), "đã lấy khoá dù giao dịch treo"
    KG.cho_phep_ghi_loi("EndNote 2025", "nhập", tep=tep, dang_dung=lambda: False, thong_bao=lambda s: None,
                        kiem_giao_dich=lambda: None)
    assert tep.exists()
    KG._tha_khoa(tep)


def test_kiem_giao_dich_treo_tren_thu_vien_that(thu_vien_giua_giao_dich, monkeypatch, capsys):
    tv = thu_vien_giua_giao_dich
    sk = KG._sk()
    monkeypatch.setattr(sk, "luc_mo_nhat_ky", lambda p: time.time() - 2 * 3600)
    with pytest.raises(KG.GiaoDichEndNoteTreo):
        KG.kiem_giao_dich_treo(tv)
    monkeypatch.setattr(sk, "luc_mo_nhat_ky", lambda p: time.time() - 10)
    KG.kiem_giao_dich_treo(tv)  # mở 10 giây: EndNote đang ghi, không chặn
    def doc_hong(*a, **k):
        raise PermissionError("không đọc được sdb.nal")

    KG.kiem_giao_dich_treo(None, sk=SimpleNamespace(thu_vien_cau_hinh=lambda: tv, giao_dich_treo=doc_hong))  # cho qua, nói ra
    assert "chưa kiểm được giao dịch ghi treo" in capsys.readouterr().err


def test_endnotemac_truyen_thu_vien_cho_khoa_ghi(monkeypatch, tmp_path):
    nap = _nap("_nap_gdt_1103", "nap_endnote_chu_de.py")
    goi = []
    monkeypatch.setattr(nap, "nap_khoa_ghi", lambda: SimpleNamespace(cho_phep_ghi=lambda *a: goi.append(a)))
    en = object.__new__(nap.EndNoteMac)
    en.ung_dung, en.thu_vien = "EndNote 2025", tmp_path / "My.enl"
    en._truoc_khi_ghi("thử")
    assert goi == [("EndNote 2025", "thử", tmp_path / "My.enl")]


# ─────────────────────────── sao lưu ───────────────────────────

def test_fixture_tai_hien_anh_chup_giua_giao_dich(thu_vien_giua_giao_dich):
    assert SK.giao_dich_mo(thu_vien_giua_giao_dich)
    assert _dong_doi(SK.sdb(thu_vien_giua_giao_dich)) > 0, "fixture không tái hiện được trang dở trên đĩa"


def test_sao_luu_giua_giao_dich_cuon_lai_ve_trang_thai_da_commit(thu_vien_giua_giao_dich, tmp_path):
    d = TV.sao_luu_thu_vien(thu_vien_giua_giao_dich, tmp_path / "sl")
    db = d / "sdb.eni"
    assert _dong_doi(db) == 0, "bản sao lưu mang dữ liệu CHƯA commit (ảnh chụp giữa giao dịch)"
    kn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        assert kn.execute("SELECT count(*) FROM refs").fetchone()[0] == DONG_DA_COMMIT
        assert kn.execute("PRAGMA quick_check").fetchone()[0] == "ok"
    finally:
        kn.close()
    assert (d / "GIAO-DICH-MO.txt").is_file() and not (d / "sdb.eni-journal").exists()
    assert SK.tep_nhat_ky(thu_vien_giua_giao_dich).exists(), "sao lưu không được đụng nhật ký của thư viện thật"


def test_sao_luu_khong_giao_dich_nhu_cu(thu_vien_giua_giao_dich, tmp_path):
    SK.tep_nhat_ky(thu_vien_giua_giao_dich).unlink()
    d = TV.sao_luu_thu_vien(thu_vien_giua_giao_dich, tmp_path / "sl")
    assert not (d / "GIAO-DICH-MO.txt").exists() and (d / "My.enl").is_file()


def test_sao_luu_tep_doi_lien_tuc_thi_nem(thu_vien_giua_giao_dich, tmp_path, monkeypatch):
    monkeypatch.setattr(TV, "_chep_kem_nhat_ky", lambda *a: False)
    with pytest.raises(OSError, match="đổi liên tục"):
        TV.sao_luu_thu_vien(thu_vien_giua_giao_dich, tmp_path / "sl", ngu=lambda s: None)
