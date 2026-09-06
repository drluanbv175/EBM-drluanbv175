from __future__ import annotations

import os
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
