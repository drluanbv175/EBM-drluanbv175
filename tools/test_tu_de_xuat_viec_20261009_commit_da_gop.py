"""Cảm biến «commit chưa đẩy» không được đếm commit mà NỘI DUNG đã vào nhánh chính remote — vá 09/10/2026.

Đo 09/10: 6 commit «chưa đẩy» ở hai repo thì 5 đã gộp (3 trùng bản vá sau rebase/cherry-pick, 2 gộp kiểu squash ở PR #78
repo y khoa) — hòm việc nhắc «soi rồi commit/push» mỗi phiên cho việc đã xong. Ngược lại commit dở THẬT phải vẫn bị đếm,
kể cả khi cùng tiêu đề với một dòng trong commit gộp nhưng được sửa SAU khi gộp. Ngoại tuyến: remote là repo trần tạm.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_commit_da_gop", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

_TD1 = "feat(cong): bộ nhận diện ô còn trống dùng chung cho mười một cổng"
_TD2 = "fix(g2): G2-AUTO-05 đếm cả ô mẫu chung sót từ khuôn sinh ICF"


def _g(cay: Path, *a: str, ngay: str | None = None) -> str:
    env = dict(os.environ)
    if ngay:
        env.update(GIT_AUTHOR_DATE=ngay, GIT_COMMITTER_DATE=ngay)
    return subprocess.run(["git", *a], cwd=cay, check=True, capture_output=True, text=True, env=env).stdout.strip()


def _commit(cay: Path, ten: str, noi_dung: str, thong_diep: str, ngay: str) -> None:
    (cay / ten).write_text(noi_dung, encoding="utf-8", newline="\n")
    _g(cay, "add", ten)
    _g(cay, "commit", "-q", "-m", thong_diep, ngay=ngay)


def _repo(tmp_path: Path) -> tuple[Path, Path]:
    """`main` đã đẩy, có origin/HEAD; trả (cây làm việc, bản sao thứ hai để «gộp trên GitHub»)."""
    tran = tmp_path / "remote.git"
    _g(tmp_path, "init", "--bare", "-q", "-b", "main", str(tran))
    cay = tmp_path / "cay"
    cay.mkdir()
    _g(cay, "init", "-q", "-b", "main")
    _g(cay, "config", "user.email", "t@t")
    _g(cay, "config", "user.name", "t")
    _commit(cay, "a.txt", "a\n", "goc", "2026-10-01T08:00:00+07:00")
    _g(cay, "remote", "add", "origin", str(tran))
    _g(cay, "push", "-q", "-u", "origin", "main")
    _g(cay, "remote", "set-head", "origin", "main")
    gh = tmp_path / "gh"
    _g(tmp_path, "clone", "-q", str(tran), str(gh))
    _g(gh, "config", "user.email", "g@g")
    _g(gh, "config", "user.name", "g")
    return cay, gh


def _bo_origin_head(cay: Path) -> None:
    """Xoá `origin/HEAD` và chặn git ≥ 2.48 tự dựng lại nó ở lần `fetch` sau (`remote.origin.followRemoteHEAD`)."""
    _g(cay, "config", "remote.origin.followRemoteHEAD", "never")
    _g(cay, "remote", "set-head", "origin", "--delete")


def _nhanh_hai_commit(cay: Path) -> None:
    _g(cay, "switch", "-q", "-c", "phu")
    _commit(cay, "p1.txt", "1\n", _TD1, "2026-10-03T12:00:00+07:00")
    _commit(cay, "p2.txt", "2\n", _TD2 + "\n\nthân commit", "2026-10-03T13:00:00+07:00")
    _g(cay, "switch", "-q", "main")


def _gop_squash(cay: Path, gh: Path, ngay: str) -> None:
    """Mô phỏng GitHub squash: một commit gộp p1+p2, thông điệp liệt kê «* <tiêu đề>»."""
    _g(gh, "pull", "-q")
    (gh / "p1.txt").write_text("1\n", encoding="utf-8", newline="\n")
    (gh / "p2.txt").write_text("2\n", encoding="utf-8", newline="\n")
    _g(gh, "add", "p1.txt", "p2.txt")
    _g(gh, "commit", "-q", "-m", f"Gộp PR (#78)\n\n* {_TD1}\n\nthân 1\n\n* {_TD2}\n\nthân 2", ngay=ngay)
    _g(gh, "push", "-q", "origin", "main")
    _g(cay, "fetch", "-q", "origin")


def test_gop_squash_khong_con_bi_dem_va_co_chi_tiet(tmp_path):
    cay, gh = _repo(tmp_path)
    _nhanh_hai_commit(cay)
    assert M.dem_commit_chua_co_tren_remote(cay) == (2, ["phu"]), "trước khi gộp: 2 commit chưa đẩy"
    _gop_squash(cay, gh, "2026-10-03T16:37:00+07:00")
    ct: dict = {}
    assert M.dem_commit_chua_co_tren_remote(cay, ct) == (0, [])
    assert ct["nen"] == "refs/remotes/origin/main"
    assert len(ct["gop_squash"]) == 2 and ct["trung_ban_va"] == [] and ct["nhanh_da_gop"] == ["phu"]


def test_trung_ban_va_sau_cherry_pick_khong_con_bi_dem(tmp_path):
    cay, gh = _repo(tmp_path)
    _nhanh_hai_commit(cay)
    _g(gh, "pull", "-q")
    _g(gh, "fetch", "-q", str(cay), "phu")
    _g(gh, "cherry-pick", "FETCH_HEAD~1", "FETCH_HEAD")   # SHA mới, bản vá y hệt
    _g(gh, "push", "-q", "origin", "main")
    _g(cay, "fetch", "-q", "origin")
    ct: dict = {}
    assert M.dem_commit_chua_co_tren_remote(cay, ct) == (0, [])
    assert len(ct["trung_ban_va"]) == 2 and ct["gop_squash"] == []


def test_commit_sua_sau_khi_gop_cung_tieu_de_van_bi_dem(tmp_path):
    """Commit cục bộ làm SAU commit gộp, giữ nguyên tiêu đề — nội dung mới chưa lên đâu cả ⇒ phải đếm."""
    cay, gh = _repo(tmp_path)
    _nhanh_hai_commit(cay)
    _gop_squash(cay, gh, "2026-10-03T16:37:00+07:00")
    _g(cay, "switch", "-q", "phu")
    _commit(cay, "p3.txt", "3\n", _TD1, "2026-10-04T09:00:00+07:00")
    _g(cay, "switch", "-q", "main")
    assert M.dem_commit_chua_co_tren_remote(cay) == (1, ["phu"])


def test_tieu_de_ngan_khong_dung_de_suy_gop(tmp_path):
    """«wip» trùng tình cờ một dòng «* wip» của commit gộp không đủ để coi là đã gộp."""
    cay, gh = _repo(tmp_path)
    _g(cay, "switch", "-q", "-c", "phu")
    _commit(cay, "w.txt", "w\n", "wip", "2026-10-03T12:00:00+07:00")
    _g(cay, "switch", "-q", "main")
    _g(gh, "pull", "-q")
    _commit(gh, "khac.txt", "k\n", "Gộp PR khác (#90)\n\n* wip", "2026-10-03T18:00:00+07:00")
    _g(gh, "push", "-q", "origin", "main")
    _g(cay, "fetch", "-q", "origin")
    assert M.dem_commit_chua_co_tren_remote(cay) == (1, ["phu"])


def test_nhanh_lan_commit_da_gop_va_commit_do_van_duoc_neu(tmp_path):
    cay, gh = _repo(tmp_path)
    _nhanh_hai_commit(cay)
    _gop_squash(cay, gh, "2026-10-03T16:37:00+07:00")
    _g(cay, "switch", "-q", "-c", "do", "phu")
    _commit(cay, "d.txt", "d\n", "feat: việc đang làm dở thật của một phiên khác", "2026-10-09T10:00:00+07:00")
    _g(cay, "switch", "-q", "main")
    ct: dict = {}
    assert M.dem_commit_chua_co_tren_remote(cay, ct) == (1, ["do"])
    assert ct["nhanh_da_gop"] == ["phu"]


def test_khong_do_duoc_nhanh_chinh_remote_thi_khong_loc(tmp_path):
    """Không có origin/HEAD và tên repo không nằm trong bảng khai báo ⇒ không có nền ⇒ báo như cũ (thừa an toàn hơn thiếu)."""
    cay, gh = _repo(tmp_path)
    _bo_origin_head(cay)
    _nhanh_hai_commit(cay)
    _gop_squash(cay, gh, "2026-10-03T16:37:00+07:00")
    ct: dict = {}
    assert M.dem_commit_chua_co_tren_remote(cay, ct) == (2, ["phu"])
    assert ct["nen"] == "" and ct["gop_squash"] == [] and ct["trung_ban_va"] == []


def test_khong_doan_main_khi_khong_co_khai_bao(tmp_path):
    """`origin/main` có mặt nhưng không ai khai nó là nhánh chính ⇒ không dùng (repo y khoa có origin/main là nhánh BỎ)."""
    cay, _gh = _repo(tmp_path)
    _bo_origin_head(cay)
    assert M._nen_nhanh_chinh_remote(cay) == ""


def test_squash_pr_mot_commit_tieu_de_kem_so_pr(tmp_path):
    """PR MỘT commit: GitHub lấy tiêu đề commit làm tiêu đề gộp, thêm «(#n)», thân là thân commit — không có dòng «* »."""
    cay, gh = _repo(tmp_path)
    _g(cay, "switch", "-q", "-c", "phu")
    _commit(cay, "p1.txt", "1\n", _TD1 + "\n\nthân", "2026-10-03T12:00:00+07:00")
    _g(cay, "switch", "-q", "main")
    _g(gh, "pull", "-q")
    _commit(gh, "p1.txt", "1\nsửa khi duyệt\n", f"{_TD1} (#80)\n\nthân", "2026-10-03T17:00:00+07:00")
    _g(gh, "push", "-q", "origin", "main")
    _g(cay, "fetch", "-q", "origin")
    ct: dict = {}
    assert M.dem_commit_chua_co_tren_remote(cay, ct) == (0, [])
    assert len(ct["gop_squash"]) == 1
