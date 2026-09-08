from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lien_ket_da_nen as LK  # noqa: E402


def test_tro_dung_true_when_symlink_points_correctly(tmp_path):
    nguon = tmp_path / "src"
    nguon.mkdir()
    link = tmp_path / "link"
    link.symlink_to(nguon, target_is_directory=True)

    assert LK.tro_dung(link, nguon)


def test_tro_dung_false_when_symlink_points_elsewhere(tmp_path):
    nguon = tmp_path / "src"
    nguon.mkdir()
    khac = tmp_path / "khac"
    khac.mkdir()
    link = tmp_path / "link"
    link.symlink_to(khac, target_is_directory=True)

    assert not LK.tro_dung(link, nguon)


def test_tro_dung_false_when_symlink_is_dangling(tmp_path):
    nguon = tmp_path / "src"
    nguon.mkdir()
    link = tmp_path / "link"
    link.symlink_to(tmp_path / "khong-ton-tai")

    assert not LK.tro_dung(link, nguon)


def test_tro_dung_uses_samefile_not_resolved_string_equality(tmp_path):
    r"""Tai hien dung lop bug do that tren GitHub Actions windows-latest
    (06/09/2026, workflow kiem-tinh-da-nen chay tren commit a7b8b30): cung MOT
    thu muc that, hai lan goi Path.resolve() doc lap (mot trong dich_cua(),
    mot o noi goi) ra HAI CHUOI KHAC NHAU (mot ben mang tien to duong dan mo
    rong \\?\, mot ben khong) -- ham cu so chuoi resolve() nen bao SAI la
    khong khop du lien ket tro DUNG. Tren Linux khong tai hien duoc chinh xac
    kieu lech chuoi cua Windows, nhung hard link la mot cach THAT (khong gia
    lap) de dung hai chuoi duong dan KHAC NHAU cung tro toi MOT file -- dung
    de kiem dinh rang tro_dung() phai nhan dien "cung mot file that" bang
    os.path.samefile(), khong duoc chi so chuoi da resolve()."""
    that = tmp_path / "noi-dung-that.txt"
    that.write_text("du lieu", encoding="utf-8")
    ten_khac = tmp_path / "ten-khac-nhung-cung-file.txt"
    os.link(that, ten_khac)

    assert os.path.samefile(that, ten_khac)
    assert that.resolve() != ten_khac.resolve()  # tien de: hai CHUOI that su khac nhau

    link = tmp_path / "link"
    link.symlink_to(ten_khac)

    assert LK.tro_dung(link, that)


def test_tro_dung_false_when_samefile_raises_for_nonexistent_source(tmp_path):
    """nguon (nguon skill) khong ton tai la mot loi cau hinh o noi goi, khong
    phai loi cua tro_dung() -- ham phai tra False chu khong duoc nem loi."""
    nguon = tmp_path / "khong-ton-tai"
    thuc = tmp_path / "thuc"
    thuc.mkdir()
    link = tmp_path / "link"
    link.symlink_to(thuc, target_is_directory=True)

    assert not LK.tro_dung(link, nguon)


def _stat_voi_st_mode(st_mode):
    trong = (st_mode,) + (0,) * 9
    return os.stat_result(trong)


def test_go_rmdir_khi_lstat_bao_thu_muc_tren_windows(tmp_path, monkeypatch):
    r"""Tai hien dung bug do that tren GitHub Actions windows-latest/Python
    3.11 (06/09/2026, workflow kiem-tinh-da-nen commit 1ed2487): mot lien ket
    TREO (dich khong con ton tai) nhung duoc TAO la loai thu muc phai go bang
    os.rmdir(), khong duoc go bang p.unlink() -- Windows tu choi unlink() tren
    reparse point loai thu muc. Ban cu dung Path.is_dir() (theo lien ket toi
    dich) + la_junction() (fallback readlink tren 3.9-3.11 coi NHAM moi lien
    ket doc duoc la junction) -- ca hai deu sai voi lien ket TREO. Gia lap
    WINDOWS=True + os.lstat vi khong tao duoc reparse point that cua Windows
    tren Linux.

    VA 08/09/2026: tren Python 3.12+ (may nay: 3.14), la_junction() di qua
    nhanh os.path.isjunction() that cua thu vien chuan -- ham nay TU CHOI
    tra True tren POSIX bat ke os.lstat bi gia lap the nao (junction la khai
    niem rieng cua Windows, CPython hardcode `return False` tren nen khac).
    Gia mao os.lstat khong du -- phai gia mao ca os.path.isjunction() de mo
    phong dung "Windows bao day la mot junction". Thieu dong nay, la_lien_ket()
    tra False (vi is_symlink() cung bi keo theo False boi cung mot os.lstat
    gia mao dung chung), go() tu choi cung o buoc dau tien, chua bao gio toi
    duoc nhanh rmdir/unlink can kiem."""
    p = tmp_path / "link"
    p.symlink_to(tmp_path / "khong-ton-tai")

    monkeypatch.setattr(LK, "WINDOWS", True)
    monkeypatch.setattr(LK.os, "lstat", lambda path: _stat_voi_st_mode(stat.S_IFDIR))
    monkeypatch.setattr(LK.os.path, "isjunction", lambda path: True)
    calls = []
    monkeypatch.setattr(LK.os, "rmdir", lambda path: calls.append("rmdir"))
    monkeypatch.setattr(Path, "unlink", lambda self, *a, **kw: calls.append("unlink"))

    LK.go(p)

    assert calls == ["rmdir"]


def test_go_unlink_khi_lstat_bao_file_tren_windows(tmp_path, monkeypatch):
    """Doi xung voi test tren: lien ket TREO loai FILE phai go bang unlink(),
    khong duoc go bang os.rmdir() (Windows tu choi rmdir tren reparse point
    loai file).

    VA 08/09/2026: mot symlink Windows THAT tro toi file (khac junction) duoc
    os.lstat() bao S_IFLNK, KHONG PHAI S_IFREG -- windows chi dung S_IFDIR cho
    junction, con symlink (ca loai file lan thu muc) luon mang bit S_ISLNK.
    Ban cu gia mao S_IFREG vo tinh lam is_symlink() tra False (vi is_symlink()
    doc lai chinh os.lstat da bi gia mao dung chung), khien la_lien_ket() tra
    False va go() tu choi cung o buoc dau tien -- chua bao gio toi duoc nhanh
    can kiem (unlink, khong phai rmdir). Doi sang S_IFLNK vua dung that voi
    Windows vua giu is_symlink()==True, ma stat.S_ISDIR(S_IFLNK) van False nen
    go() van di dung nhanh unlink()."""
    p = tmp_path / "link"
    p.symlink_to(tmp_path / "khong-ton-tai")

    monkeypatch.setattr(LK, "WINDOWS", True)
    monkeypatch.setattr(LK.os, "lstat", lambda path: _stat_voi_st_mode(stat.S_IFLNK))
    calls = []
    monkeypatch.setattr(LK.os, "rmdir", lambda path: calls.append("rmdir"))
    monkeypatch.setattr(Path, "unlink", lambda self, *a, **kw: calls.append("unlink"))

    LK.go(p)

    assert calls == ["unlink"]
