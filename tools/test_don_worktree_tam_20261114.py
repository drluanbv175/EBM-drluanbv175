#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bộ kiểm cho `tools/don_worktree_tam.py` — mỗi mục chốt một LỖI CÓ THẬT đã gặp ngày 14/11/2026.

Nguyên tắc: kiểm HÀNH VI trên mã sống, ngoại tuyến, không cần mạng. Các mục có dấu ★ là chốt an toàn — đột biến ở đó phải làm đỏ."""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest


def _nap():
    sp = importlib.util.spec_from_file_location("_dwt_kiem", Path(__file__).resolve().parent / "don_worktree_tam.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


dwt = _nap()


def _dung_goc(tmp: Path, muc: list[tuple[str, bool]]) -> Path:
    """Dựng thư mục worktree giả: (tên, có .git hay không)."""
    g = tmp / "wt"
    g.mkdir()
    for ten, co_git in muc:
        d = g / ten
        d.mkdir()
        (d / "noi_dung.txt").write_text("x" * 128, encoding="utf-8")
        if co_git:
            (d / ".git").write_text("gitdir: /noi/khac/.git/worktrees/" + ten, encoding="utf-8")
    return g


def _gia_chay(trang_thai: dict[str, str | None], remove_ok: bool = True, nhat_ky: list | None = None):
    """Hàm git giả. Giá trị None = `git status` LỖI (chưa đo được); chuỗi rỗng = sạch; chuỗi có chữ = còn việc dở."""
    def chay(args, cwd, giay=60):
        ten = Path(cwd).name
        if nhat_ky is not None:
            nhat_ky.append((ten, tuple(args[:2])))
        if list(args[:2]) == ["status", "--porcelain"]:
            v = trang_thai.get(ten, "")
            return (1, "") if v is None else (0, v)
        if list(args[:2]) == ["worktree", "remove"]:
            if not remove_ok:
                return 1, ""
            shutil.rmtree(cwd, ignore_errors=True)
            return 0, ""
        return 0, ""
    return chay


# ───────────────────────── đếm nhanh ─────────────────────────

def test_quet_nhanh_dem_thu_muc_bo_tep_va_thu_muc_an(tmp_path):
    g = _dung_goc(tmp_path, [("a", True), ("b", True)])
    (g / "mot-tep.txt").write_text("x", encoding="utf-8")
    (g / ".an").mkdir()
    nh = dwt.quet_nhanh(g)
    assert nh["do_duoc"] is True
    assert nh["tong"] == 2 and nh["ten"] == ["a", "b"]


def test_goc_vang_la_chua_do_duoc_chu_khong_phai_khong_co_gi(tmp_path):
    """★ «Không đo được» ≠ «không có worktree nào» — nhầm hai cái này là báo xanh giả."""
    nh = dwt.quet_nhanh(tmp_path / "khong-ton-tai")
    assert nh["do_duoc"] is False and nh["tong"] == 0
    assert "không có thư mục" in nh["ly_do"]
    viec, chet = dwt.giac_quan(tmp_path / "khong-ton-tai", tep_so_do=tmp_path / "vang.json")
    assert viec == [] and len(chet) == 1


@pytest.mark.parametrize("ten", ["_saoluu_x", "ban-sao-luu-2026", "my_sao_luu", "BACKUP-endnote", "Sao-Luu-Lon"])
def test_la_sao_luu_bat_moi_bien_the(ten):
    assert dwt.la_sao_luu(ten) is True


@pytest.mark.parametrize("ten", ["feat-abc", "g1-thiet-ke", "worktree-thuong"])
def test_ten_thuong_khong_bi_coi_la_sao_luu(ten):
    assert dwt.la_sao_luu(ten) is False


# ───────────────────────── phân loại ─────────────────────────

def test_phan_loai_du_bon_nhom(tmp_path):
    g = _dung_goc(tmp_path, [("sach1", True), ("ban1", True), ("_saoluu_kho", True), ("thu-muc-thuong", False)])
    kq = dwt.quet_day_du(g, chay=_gia_chay({"sach1": "", "ban1": " M tep.py"}))
    assert kq["sach"] == ["sach1"]
    assert kq["ban"] == ["ban1"]
    assert kq["sao_luu"] == ["_saoluu_kho"]
    assert kq["khong_worktree"] == ["thu-muc-thuong"]
    assert kq["byte_sach"] > 0 and kq["byte_tong"] >= kq["byte_sach"]


def test_status_loi_khong_bao_gio_tinh_la_go_duoc(tmp_path):
    """★ Đọc trạng thái không được PHẢI vào «chưa đo được», không được rơi vào nhóm gỡ."""
    g = _dung_goc(tmp_path, [("hong", True), ("sach", True)])
    kq = dwt.quet_day_du(g, chay=_gia_chay({"hong": None, "sach": ""}))
    assert kq["chua_do"] == ["hong"]
    assert "hong" not in kq["sach"] and "hong" not in kq["ban"]


def test_sao_luu_du_sach_van_khong_bao_gio_bi_go(tmp_path):
    """★ Thư mục sao lưu sạch vẫn phải được giữ — mất bản sao lưu là mất dữ liệu thật."""
    g = _dung_goc(tmp_path, [("_saoluu_endnote", True)])
    nk: list = []
    kq = dwt.don(["_saoluu_endnote"], g, ap_dung=True, chay=_gia_chay({"_saoluu_endnote": ""}, nhat_ky=nk))
    assert kq["da"] == [] and kq["bo_qua"] and kq["bo_qua"][0][1] == "là bản sao lưu"
    assert (g / "_saoluu_endnote").is_dir()
    assert all(a != ("worktree", "remove") for _t, a in nk)


def test_khong_phai_worktree_thi_khong_go(tmp_path):
    """★ Thư mục không có .git không bao giờ bị đụng tới."""
    g = _dung_goc(tmp_path, [("thu-muc-la", False)])
    kq = dwt.don(["thu-muc-la"], g, ap_dung=True, chay=_gia_chay({"thu-muc-la": ""}))
    assert kq["da"] == [] and kq["bo_qua"][0][1] == "không phải worktree"
    assert (g / "thu-muc-la").is_dir()


# ───────────────────────── gỡ ─────────────────────────

def test_chay_kho_khong_goi_remove(tmp_path):
    """★ Mặc định là CHẠY KHÔ: liệt kê nhưng không được gọi `git worktree remove`."""
    g = _dung_goc(tmp_path, [("sach", True)])
    nk: list = []
    kq = dwt.don(["sach"], g, ap_dung=False, chay=_gia_chay({"sach": ""}, nhat_ky=nk))
    assert kq["da"] == ["sach"]
    assert (g / "sach").is_dir()
    assert all(a != ("worktree", "remove") for _t, a in nk)


def test_ap_dung_go_that(tmp_path):
    g = _dung_goc(tmp_path, [("sach", True)])
    kq = dwt.don(["sach"], g, ap_dung=True, chay=_gia_chay({"sach": ""}))
    assert kq["da"] == ["sach"] and not (g / "sach").exists()


def test_kiem_lai_ngay_truoc_khi_go_bat_thay_doi_moi(tmp_path):
    """★ Worktree quét lúc trước là sạch, nay vừa có thay đổi ⇒ PHẢI bỏ qua, không gỡ."""
    g = _dung_goc(tmp_path, [("vua-ban", True)])
    kq = dwt.don(["vua-ban"], g, ap_dung=True, chay=_gia_chay({"vua-ban": "?? moi.py"}))
    assert kq["da"] == []
    assert kq["bo_qua"][0][1] == "vừa có thay đổi chưa commit"
    assert (g / "vua-ban").is_dir()


def test_remove_that_bai_vao_nhom_loi_khong_bao_la_da_go(tmp_path):
    g = _dung_goc(tmp_path, [("sach", True)])
    kq = dwt.don(["sach"], g, ap_dung=True, chay=_gia_chay({"sach": ""}, remove_ok=False))
    assert kq["da"] == [] and kq["loi"] == ["sach"]


# ───────────────────────── giác quan ─────────────────────────

def _goc_nhieu(tmp_path, n: int) -> Path:
    return _dung_goc(tmp_path, [(f"w{i:03}", True) for i in range(n)])


def test_duoi_nguong_khong_bao_gi(tmp_path):
    viec, chet = dwt.giac_quan(_goc_nhieu(tmp_path, dwt.NGUONG_SO - 1), tep_so_do=tmp_path / "vang.json")
    assert viec == [] and chet == []


def test_dung_nguong_thi_bao_uu_tien_2(tmp_path):
    viec, chet = dwt.giac_quan(_goc_nhieu(tmp_path, dwt.NGUONG_SO), tep_so_do=tmp_path / "vang.json")
    assert chet == [] and len(viec) == 1
    uu, ai, dong, lenh = viec[0]
    assert uu == 2 and ai == "🛎"
    assert str(dwt.NGUONG_SO) in dong and "don_worktree_tam.py" in lenh


def test_vuot_nguong_gap_thi_uu_tien_1(tmp_path):
    viec, _ = dwt.giac_quan(_goc_nhieu(tmp_path, dwt.NGUONG_SO_GAP), tep_so_do=tmp_path / "vang.json")
    assert viec[0][0] == 1


def test_dung_luong_lon_bao_gap_du_so_worktree_thap(tmp_path):
    """★ Ít worktree nhưng rất nặng vẫn phải báo — ngưỡng là SỐ *hoặc* DUNG LƯỢNG."""
    so_do = tmp_path / "so-do.json"
    so_do.write_text(json.dumps({"do_luc": dt.datetime.now().isoformat(timespec="seconds"),
                                 "tong": 5, "so_sach": 5,
                                 "byte_tong": int(dwt.NGUONG_GB_GAP * (1 << 30)),
                                 "byte_sach": 0}), encoding="utf-8")
    viec, _ = dwt.giac_quan(_goc_nhieu(tmp_path, 5), tep_so_do=so_do)
    assert len(viec) == 1 and viec[0][0] == 1 and "GB" in viec[0][2]


def test_so_do_qua_han_khong_duoc_dung_de_noi_dung_luong(tmp_path):
    """★ Ảnh chụp cũ không được dùng làm số đo hôm nay."""
    cu = dt.datetime.now() - dt.timedelta(days=dwt.HAN_SO_DO_NGAY + 1)
    so_do = tmp_path / "so-do.json"
    so_do.write_text(json.dumps({"do_luc": cu.isoformat(timespec="seconds"), "tong": 5,
                                 "byte_tong": int(dwt.NGUONG_GB_GAP * (1 << 30)), "byte_sach": 0}), encoding="utf-8")
    viec, _ = dwt.giac_quan(_goc_nhieu(tmp_path, 5), tep_so_do=so_do)
    assert viec == []


def test_so_do_hong_khong_lam_vo_giac_quan(tmp_path):
    so_do = tmp_path / "so-do.json"
    so_do.write_text("{ hỏng", encoding="utf-8")
    viec, chet = dwt.giac_quan(_goc_nhieu(tmp_path, dwt.NGUONG_SO), tep_so_do=so_do)
    assert len(viec) == 1 and chet == [] and "GB" not in viec[0][2]


# ───────────────────────── git thật ─────────────────────────

@pytest.mark.skipif(shutil.which("git") is None, reason="máy không có git")
def test_git_that_phan_loai_dung(tmp_path):
    """Chốt đầu–cuối trên git THẬT: worktree sạch và worktree bẩn phải vào đúng nhóm."""
    repo = tmp_path / "repo"
    repo.mkdir()
    def g(*a, cwd=repo):
        subprocess.run(["git", *a], cwd=str(cwd), check=True, capture_output=True)
    g("init", "-q", "-b", "main")
    g("config", "user.email", "k@t.vn")
    g("config", "user.name", "kiem")
    (repo / "a.txt").write_text("1", encoding="utf-8")
    g("add", "-A")
    g("commit", "-qm", "đầu")
    goc = tmp_path / "wt"
    goc.mkdir()
    g("worktree", "add", "-q", "-b", "sach", str(goc / "sach"))
    g("worktree", "add", "-q", "-b", "ban", str(goc / "ban"))
    (goc / "ban" / "moi.txt").write_text("chưa commit", encoding="utf-8")
    kq = dwt.quet_day_du(goc)
    assert kq["do_duoc"] and kq["sach"] == ["sach"] and kq["ban"] == ["ban"]
    assert dwt.don(kq["sach"], goc, ap_dung=True)["da"] == ["sach"]
    assert not (goc / "sach").exists() and (goc / "ban").is_dir()


def test_ban_sao_luu_va_thu_muc_thuong_khong_tinh_vao_nguong(tmp_path):
    """★ Lỗi thật 14/11: ngưỡng đếm TỔNG thư mục làm cảm biến kêu oan (77 thư mục nhưng chỉ 5 cái gỡ được).

    Ngưỡng phải bám số ỨNG VIÊN — bản sao lưu và thư mục không phải worktree không bao giờ được tính vào."""
    muc = [(f"_saoluu_{i:03}", True) for i in range(dwt.NGUONG_SO_GAP)]
    muc += [(f"thuong{i:03}", False) for i in range(dwt.NGUONG_SO_GAP)]
    muc += [("that1", True), ("that2", True)]
    g = _dung_goc(tmp_path, muc)
    nh = dwt.quet_nhanh(g)
    assert nh["tong"] == 2 * dwt.NGUONG_SO_GAP + 2
    assert sorted(nh["ung_vien"]) == ["that1", "that2"]
    viec, chet = dwt.giac_quan(g, tep_so_do=tmp_path / "vang.json")
    assert viec == [] and chet == []


def test_dong_bao_noi_ro_tong_va_so_go_duoc(tmp_path):
    """Dòng nhắc phải phân biệt «gỡ được» với «tổng» — người đọc không được hiểu là xoá hết."""
    muc = [(f"w{i:03}", True) for i in range(dwt.NGUONG_SO)] + [("_saoluu_giu", True)]
    viec, _ = dwt.giac_quan(_dung_goc(tmp_path, muc), tep_so_do=tmp_path / "vang.json")
    assert len(viec) == 1
    dong = viec[0][2]
    assert f"{dwt.NGUONG_SO} worktree tạm có thể gỡ" in dong
    assert f"tổng {dwt.NGUONG_SO + 1}" in dong and "luôn được giữ" in dong
