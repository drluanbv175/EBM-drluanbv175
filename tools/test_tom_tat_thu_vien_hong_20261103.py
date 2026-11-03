# -*- coding: utf-8 -*-
"""⑨ tóm tắt Word + sức khoẻ EndNote khi sdb.eni đọc lỗi — chẩn đoán bằng quick_check, không traceback, không nuốt lỗi (03/11/2026).

Bối cảnh đo thật 03/11/2026: bước ⑨ của bộ năm (`tom_tat_chung_cu_word.py hang-cho`) sập bằng traceback trần
«sqlite3.OperationalError: Could not decode to UTF-8 column 'accession_number' with text ' ung th…'». Một phiên khác dò ra gốc:
sdb.eni HỎNG CẤU TRÚC từ 02/11 ~19:01 (quick_check 101 dòng «invalid page number», «2nd reference to page»); lỗi giải mã chỉ là
triệu chứng — trường đọc được có thể là dữ liệu bản ghi khác. Còn `endnote_suc_khoe.py` chỉ báo «không đọc được cơ sở dữ liệu:
DatabaseError», không nói là hỏng cấu trúc, trong khi các phiên vẫn tiếp tục ghi EndNote.

Khoá: `kiem_cau_truc` chạy quick_check trên BẢN SAO với collation thay thế ENCIN_Base (thiếu nó quick_check không chạy được) —
lành ⇒ [], «malformed» hoặc dòng lỗi ⇒ danh sách, lỗi khác ⇒ ném ra (KHÔNG ĐO ĐƯỢC ≠ lành) · ⑨ đọc lỗi trên thư viện hỏng ⇒ mã 3
kèm «HỎNG CẤU TRÚC … KHÔNG ghi EndNote», không traceback · lỗi giải mã khi cấu trúc lành ⇒ mã 2 (đo lại), KHÔNG giải mã «thay thế» rồi
trả hàng chờ · `tinh_trang` nói rõ hỏng cấu trúc. Ngoại tuyến: thư viện giả trong tmp_path.
"""
from __future__ import annotations

import contextlib
import importlib.util
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


TT = _nap("_ttcc_t1103", "tom_tat_chung_cu_word.py")
SK = TT.mod("sk")
LOI_MOC = "Bây giờ xây dựng cho những chứng cứ sau này, còn hiện tại hãy để nguyên"


@pytest.fixture(autouse=True)
def _hang_cho_tam(tmp_path, monkeypatch):
    """Hàng chờ đưa vào nhóm luôn ở tmp_path — không bao giờ tệp thật trong thư mục nhà."""
    monkeypatch.setenv("EBM_ENDNOTE_CHO_VAO_NHOM", str(tmp_path / "cho-vao-nhom.json"))


def _so_sanh(a, b):
    return (a > b) - (a < b)


@pytest.fixture
def thu_vien(tmp_path, monkeypatch):
    """Thư viện EndNote giả: 400 bản ghi có PDF, cột tiêu đề mang collation riêng ENCIN_Base như sdb.eni thật."""
    tv = tmp_path / "EndNote" / "My.enl"
    tv.parent.mkdir(parents=True)
    tv.write_bytes(b"enl")
    db = SK.sdb(tv)
    db.parent.mkdir(parents=True)
    c = sqlite3.connect(db)
    c.create_collation("ENCIN_Base", _so_sanh)
    c.execute("create table refs (id integer primary key, trash_state integer, accession_number text, "
              "electronic_resource_number text, title text collate ENCIN_Base, year text, author text, secondary_title text)")
    c.execute("create index refs_title on refs(title collate ENCIN_Base)")
    c.execute("create table file_res (refs_id integer, file_path text, file_pos integer)")
    for i in range(1, 401):
        c.execute("insert into refs values (?,?,?,?,?,?,?,?)",
                  (i, 0, str(30000000 + i), None, "Tiêu đề " + "x" * 200 + str(i), "2024", "Tác giả", "Tạp chí"))
        c.execute("insert into file_res values (?,?,?)", (i, f"{i}/bai.pdf", 0))
    c.commit()
    c.close()
    monkeypatch.setattr(SK, "thu_vien_cau_hinh", lambda *a, **k: tv)
    return tv


def _lam_hong(tv: Path) -> None:
    """Ghi rác vào đầu các trang giữa tệp — sqlite báo «database disk image is malformed» như sdb.eni 02–03/11."""
    db = SK.sdb(tv)
    b = bytearray(db.read_bytes())
    for trang in range(3, len(b) // 4096 // 2):
        b[trang * 4096:trang * 4096 + 64] = b"\xff" * 64
    db.write_bytes(bytes(b))


def test_kiem_cau_truc_thu_vien_lanh_co_collation_endnote(thu_vien):
    c = sqlite3.connect(SK.sdb(thu_vien))
    with pytest.raises(sqlite3.OperationalError, match="ENCIN_Base"):
        c.execute("pragma quick_check").fetchall()  # đối chứng: thiếu collation thay thế thì quick_check không chạy được
    c.close()
    assert SK.kiem_cau_truc(thu_vien) == []


def test_kiem_cau_truc_bao_hong_khi_sqlite_bao_malformed(thu_vien):
    _lam_hong(thu_vien)
    loi = SK.kiem_cau_truc(thu_vien)
    assert loi and "malformed" in loi[0]


def test_kiem_cau_truc_tra_dong_loi_quick_check(thu_vien, monkeypatch):
    class _Kn:
        def create_collation(self, *_):
            pass

        def execute(self, sql):
            assert sql.startswith("PRAGMA quick_check")
            return [("*** in database main ***",), ("Page 7001: invalid page number 7001",)]

    monkeypatch.setattr(SK, "ban_sao_csdl", lambda _tv: contextlib.nullcontext(_Kn()))
    assert SK.kiem_cau_truc(thu_vien) == ["*** in database main ***", "Page 7001: invalid page number 7001"]


def test_kiem_cau_truc_khong_chep_duoc_la_khong_do_duoc(thu_vien, monkeypatch):
    def hong(_tv):
        raise OSError("sdb.eni đổi liên tục trong lúc chép (EndNote đang ghi)")

    monkeypatch.setattr(SK, "ban_sao_csdl", hong)
    with pytest.raises(OSError):
        SK.kiem_cau_truc(thu_vien)  # KHÔNG ĐO ĐƯỢC ≠ lành ([])


def test_hang_cho_thu_vien_hong_cau_truc_ma_3_khong_traceback(thu_vien, capsys):
    assert TT.ghi_moc(thu_vien, LOI_MOC) == 0
    _lam_hong(thu_vien)
    with pytest.raises(TT.ThuVienKhongDoc) as kq:
        TT.hang_cho(thu_vien)
    assert kq.value.ma == 3
    capsys.readouterr()
    assert TT.main(["hang-cho"]) == 3
    ra = capsys.readouterr()
    assert "HỎNG CẤU TRÚC" in ra.out and "KHÔNG ghi EndNote" in ra.out and "Recover Library" in ra.out
    assert "Traceback" not in ra.out + ra.err


def test_loi_giai_ma_utf8_khi_cau_truc_lanh_ma_2_khong_nuot_loi(thu_vien, capsys):
    assert TT.ghi_moc(thu_vien, LOI_MOC) == 0
    c = sqlite3.connect(SK.sdb(thu_vien))
    c.execute("update refs set accession_number = cast(x'20756e67207468e1' as text) where id = 7")  # « ung th\xe1» như 03/11
    c.commit()
    c.close()
    with pytest.raises(TT.ThuVienKhongDoc) as kq:
        TT.ban_ghi_co_pdf(thu_vien)  # không giải mã «thay thế» rồi trả danh sách
    assert kq.value.ma == 2 and "Could not decode" in str(kq.value) and "quick_check lành" in str(kq.value)
    capsys.readouterr()
    assert TT.main(["hang-cho"]) == 2
    assert "Traceback" not in capsys.readouterr().err


def test_suc_khoe_noi_ro_hong_cau_truc(thu_vien):
    _lam_hong(thu_vien)
    canh_bao = " ".join(SK.tinh_trang(thu_vien)["canh_bao"])
    assert "không đọc được cơ sở dữ liệu: DatabaseError" in canh_bao and "HỎNG CẤU TRÚC" in canh_bao
