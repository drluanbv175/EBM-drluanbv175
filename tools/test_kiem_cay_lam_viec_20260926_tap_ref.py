"""Chốt «cây lạc hậu» (CLAUDE.md §0.3) so với TẬP ref + soi repo y khoa ANH EM — 26/09/2026.

Bổ sung các ca ⑤–⑧ cho BH93 (bộ chốt bài học giữ ①–④; tệp này là test riêng, không sửa
chot_hoi_quy_bai_hoc.py):
  ⑤ bố cục ANH EM (gốc và medical-ebm-automation cạnh nhau) ⇒ repo y khoa ĐƯỢC soi;
  ⑥ repo y khoa bằng nhánh chính khai báo, cạnh một origin/main cũ «tiến» 3 commit ⇒ KHÔNG đỏ;
  ⑦ nhánh làm việc tự theo dõi CHÍNH NÓ (bằng nhau) trong khi nhánh chính tiến 2 ⇒ ĐỎ, đúng 2
    (bắt kiểu vá «xét @{u} trước rồi dừng» — xanh giả);
  ⑧ ref khai báo vắng ⇒ CHƯA KIỂM ĐƯỢC, không đỏ, KHÔNG lùi về origin/main;
  + không có lịch sử chung (clone nông/lịch sử rời) ⇒ CHƯA KIỂM ĐƯỢC, không đỏ.

Ngoại tuyến: mọi repo dựng trong thư mục tạm; không fetch mạng.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "kiem_cay_lam_viec.py"
_sp = importlib.util.spec_from_file_location("kiem_cay_lam_viec_tap_ref", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

NHANH_YK = "feat/r1-1-2-design-gap-remediation"


def _g(cay: Path, *a: str) -> str:
    r = subprocess.run(["git", *a], cwd=cay, capture_output=True, text=True, timeout=30,
                       encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"git {' '.join(a)} hỏng: {r.stderr}"
    return r.stdout.strip()


def _init(cay: Path, nhanh: str) -> Path:
    cay.mkdir(parents=True, exist_ok=True)
    _g(cay, "init", "-q", "-b", nhanh)
    _g(cay, "config", "user.email", "t@t.t")
    _g(cay, "config", "user.name", "t")
    _g(cay, "config", "commit.gpgsign", "false")
    return cay


def _commit(cay: Path, noi_dung: str) -> None:
    (cay / "a.txt").write_text(noi_dung, encoding="utf-8")
    _g(cay, "add", "-A")
    _g(cay, "commit", "-qm", noi_dung)


def _clone(nguon: Path, dich: Path) -> Path:
    _g(nguon.parent, "clone", "-q", str(nguon), str(dich))
    _g(dich, "config", "user.email", "t@t.t")
    _g(dich, "config", "user.name", "t")
    _g(dich, "config", "commit.gpgsign", "false")
    return dich


def _nguon_y_khoa(td: Path) -> Path:
    """Repo «remote» tên medical-ebm-automation (tên repo suy từ URL remote = khoá khai báo),
    nhánh chính khai báo có 1 commit."""
    src = _init(td / "remote" / "medical-ebm-automation", NHANH_YK)
    _commit(src, "c1")
    return src


def test_nhanh_chinh_khop_claude_md():
    """Tên nhánh chính khai báo KHÔNG được trôi khỏi CLAUDE.md §4 (nguồn nhánh mặc định)."""
    claude = (_TEP.parents[1] / "CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(r"Nhánh mặc định: `([^`]+)`", claude)
    assert m, "CLAUDE.md §4 không còn dòng «Nhánh mặc định: `…`» — cập nhật test/khai báo cùng lúc"
    assert M.NHANH_CHINH["medical-ebm-automation"] == m.group(1)
    assert M.NHANH_CHINH["EBM-drluanbv175"] == "master"


@pytest.mark.parametrize("url, ten", [
    ("https://github.com/chu/medical-ebm-automation.git", "medical-ebm-automation"),
    ("git@github.com:chu/EBM-drluanbv175.git", "EBM-drluanbv175"),
    ("http://local_proxy@127.0.0.1:41000/git/chu/EBM-drluanbv175", "EBM-drluanbv175"),
])
def test_ten_repo_tu_remote(tmp_path, url, ten):
    cay = _init(tmp_path / "Claude AI", "master")  # thư mục gốc trên Mac/Windows mang tên khác
    _g(cay, "remote", "add", "origin", url)
    assert M.ten_repo(cay) == ten


def test_5_bo_cuc_anh_em_repo_y_khoa_duoc_soi(tmp_path):
    goc = _init(tmp_path / "EBM-drluanbv175", "master")
    _commit(goc, "g1")
    yk = _init(tmp_path / "medical-ebm-automation", NHANH_YK)
    _commit(yk, "y1")
    cac = M.cac_cay_can_soi(goc)
    assert yk.resolve() in cac, "bố cục anh em: repo y khoa phải được soi (chốt §0.3 hai repo)"
    assert cac[0] == goc


def test_5_main_in_ca_repo_y_khoa_anh_em(tmp_path, monkeypatch, capsys):
    goc = _init(tmp_path / "EBM-drluanbv175", "master")
    _commit(goc, "g1")
    _init(tmp_path / "medical-ebm-automation", NHANH_YK)
    _commit(tmp_path / "medical-ebm-automation", "y1")
    monkeypatch.setattr(M, "REPO", goc)
    M.main([])
    assert "medical-ebm-automation" in capsys.readouterr().out


def test_6_bang_nhanh_chinh_canh_origin_main_cu_khong_do(tmp_path):
    src = _nguon_y_khoa(tmp_path)
    # origin/main cũ «tiến» 3 commit (nhánh bỏ, lịch sử có chung gốc) — y hệt ca Cloud
    _g(src, "checkout", "-q", "-b", "main")
    for i in range(3):
        _commit(src, f"main{i}")
    _g(src, "checkout", "-q", NHANH_YK)
    ban = _clone(src, tmp_path / "ban")
    _g(ban, "remote", "set-head", "origin", "-d")   # Cloud: origin/HEAD không phải symbolic ref
    assert _g(ban, "rev-list", "--count", "HEAD..origin/main") == "3"  # fixture đúng ca đỏ giả
    kq = M.soi_mot_cay(ban)
    assert not kq["do"], kq["canh_bao"]
    assert kq["thieu_bao_nhieu"] == 0
    assert all(d["ref"] != "origin/main" for d in kq["cac_ref_so"]), "không được so với origin/main"
    assert kq["goc_so"] == f"origin/{NHANH_YK}"


def test_7_nhanh_tu_theo_doi_chinh_no_van_do_khi_nhanh_chinh_tien(tmp_path):
    src = _nguon_y_khoa(tmp_path)
    ban = _clone(src, tmp_path / "ban")
    _g(ban, "checkout", "-q", "-b", "claude/xyz")
    _g(ban, "push", "-q", "-u", "origin", "claude/xyz")
    assert _g(ban, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}") == "origin/claude/xyz"
    _g(src, "checkout", "-q", NHANH_YK)
    _commit(src, "c2")
    _commit(src, "c3")
    _g(ban, "fetch", "-q", "origin")
    kq = M.soi_mot_cay(ban)
    assert kq["do"], "nhánh chính tiến 2 commit mà không đỏ — xanh giả kiểu «@{u} rồi dừng»"
    assert kq["thieu_bao_nhieu"] == 2
    refs = {d["ref"]: d["thieu"] for d in kq["cac_ref_so"]}
    assert refs == {f"origin/{NHANH_YK}": 2, "origin/claude/xyz": 0}


def test_8_ref_khai_bao_vang_chua_kiem_duoc_khong_lui_origin_main(tmp_path):
    src = _init(tmp_path / "remote" / "medical-ebm-automation", "main")
    _commit(src, "c1")
    ban = _clone(src, tmp_path / "ban")
    _g(ban, "checkout", "-q", "-b", "work")          # không upstream
    _commit(src, "c2")
    _commit(src, "c3")
    _g(ban, "fetch", "-q", "origin")
    assert _g(ban, "rev-list", "--count", "HEAD..origin/main") == "2"  # bản cũ sẽ đỏ ở đây
    kq = M.soi_mot_cay(ban)
    assert not kq["do"], kq["canh_bao"]
    assert kq["thieu_bao_nhieu"] is None
    assert any("CHƯA KIỂM ĐƯỢC" in c and NHANH_YK in c for c in kq["canh_bao"])
    assert all(d["ref"] != "origin/main" for d in kq["cac_ref_so"])


def test_khong_co_lich_su_chung_la_chua_kiem_duoc(tmp_path):
    src = _nguon_y_khoa(tmp_path)
    _commit(src, "c2")
    ban = _clone(src, tmp_path / "ban")
    _g(ban, "checkout", "-q", "--orphan", "roi")
    _commit(ban, "x1")
    kq = M.soi_mot_cay(ban)
    assert not kq["do"], "không có merge-base mà đỏ — con số lạc hậu vô nghĩa (đỏ giả)"
    assert any("CHƯA KIỂM ĐƯỢC" in c and "lịch sử chung" in c for c in kq["canh_bao"])


def test_repo_khong_khai_bao_van_lui_ref_mac_dinh(tmp_path):
    """Repo lạ (không có khai báo) vẫn giữ hành vi BH93 ①: lạc hậu so với origin/master ⇒ đỏ."""
    src = _init(tmp_path / "remote" / "repo-la", "master")
    _commit(src, "c1")
    ban = _clone(src, tmp_path / "ban")
    _g(ban, "checkout", "-q", "-b", "work")
    _commit(src, "c2")
    _g(ban, "fetch", "-q", "origin")
    kq = M.soi_mot_cay(ban)
    assert kq["do"] and kq["thieu_bao_nhieu"] == 1
    assert kq["goc_so"] == "origin/master"
