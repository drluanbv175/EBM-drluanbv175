"""Cảm biến «commit chưa đẩy» nhận commit MERGE sạch đã gộp — vá 24/10/2026.

Đo 24/10: hòm việc báo «3 commit chưa có trên remote» (repo gốc) và «6» (repo y khoa) — CẢ 9 là merge «Merge origin/master vào
nhánh X», kéo nhánh chính về trước khi PR được gộp kiểu squash. `git cherry` không xét merge, khớp tiêu đề squash cũng không ⇒
đếm mãi. Khoá: merge sạch (combined diff rỗng) mà mọi cha đã ở remote hoặc đã gộp ⇒ không đếm; merge tự thêm nội dung (giải
xung đột) hoặc merge đứng trên commit dở THẬT ⇒ vẫn đếm. Ngoại tuyến: remote là repo trần tạm.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_merge_sach", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

_TD = "feat(hom-viec): một tính năng đủ dài để khớp tiêu đề gộp squash"


def _g(cay: Path, *a: str, ngay: str | None = None) -> str:
    env = dict(os.environ)
    if ngay:
        env.update(GIT_AUTHOR_DATE=ngay, GIT_COMMITTER_DATE=ngay)
    return subprocess.run(["git", *a], cwd=cay, check=True, capture_output=True, text=True, env=env,
                          encoding="utf-8", errors="replace").stdout.strip()


def _commit(cay: Path, ten: str, noi_dung: str, thong_diep: str, ngay: str) -> None:
    (cay / ten).write_text(noi_dung, encoding="utf-8", newline="\n")
    _g(cay, "add", ten)
    _g(cay, "commit", "-q", "-m", thong_diep, ngay=ngay)


def _repo(tmp_path: Path) -> tuple[Path, Path]:
    """`main` đã đẩy (có origin/HEAD); trả (cây làm việc, bản sao thứ hai đóng vai GitHub)."""
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


def _dung_kich_ban(tmp_path: Path, giai_xung_dot_them: bool = False) -> Path:
    """Nhánh `phu` có một commit; nhánh chính tiến lên trên GitHub; `phu` kéo origin/main về bằng MERGE; rồi GitHub gộp PR
    kiểu squash. `giai_xung_dot_them` ⇒ merge tự thêm một dòng không có ở cha nào (nội dung riêng của merge)."""
    cay, gh = _repo(tmp_path)
    _g(cay, "switch", "-q", "-c", "phu")
    _commit(cay, "p.txt", "p\n", _TD, "2026-10-03T12:00:00+07:00")
    _commit(gh, "m.txt", "m\n", "chore: nhánh chính tiến lên", "2026-10-04T09:00:00+07:00")
    _g(gh, "push", "-q", "origin", "main")
    _g(cay, "fetch", "-q", "origin")
    _g(cay, "merge", "-q", "--no-ff", "--no-edit", "origin/main", ngay="2026-10-05T10:00:00+07:00")
    if giai_xung_dot_them:
        (cay / "p.txt").write_text("p\nthêm trong merge\n", encoding="utf-8", newline="\n")
        _g(cay, "add", "p.txt")
        _g(cay, "commit", "-q", "--amend", "--no-edit", ngay="2026-10-05T10:00:00+07:00")
    _g(gh, "pull", "-q")
    (gh / "p.txt").write_text("p\n", encoding="utf-8", newline="\n")
    _g(gh, "add", "p.txt")
    _g(gh, "commit", "-q", "-m", f"{_TD} (#9)", ngay="2026-10-06T08:00:00+07:00")
    _g(gh, "push", "-q", "origin", "main")
    _g(cay, "fetch", "-q", "origin")
    return cay


def test_merge_sach_tren_nhanh_da_gop_squash_khong_dem(tmp_path):
    cay = _dung_kich_ban(tmp_path)
    ct: dict = {}
    assert M.dem_commit_chua_co_tren_remote(cay, ct) == (0, [])
    assert len(ct["gop_merge"]) == 1, "merge sạch phải được nhận là đã gộp"
    assert len(ct["trung_ban_va"]) + len(ct["gop_squash"]) == 1, "commit thường của PR được nhận qua trùng bản vá/squash"


def test_merge_tu_them_noi_dung_van_dem(tmp_path):
    cay = _dung_kich_ban(tmp_path, giai_xung_dot_them=True)
    ct: dict = {}
    so, _ = M.dem_commit_chua_co_tren_remote(cay, ct)
    assert so == 1 and ct["gop_merge"] == [], "merge có dòng riêng (không có ở cha nào) phải vẫn bị đếm là chưa đẩy"


def test_merge_dung_tren_commit_do_that_van_dem(tmp_path):
    """Cha thứ nhất là commit dở THẬT (chưa gộp) ⇒ merge cũng chưa gộp."""
    cay, gh = _repo(tmp_path)
    _g(cay, "switch", "-q", "-c", "phu")
    _commit(cay, "p.txt", "p\n", _TD, "2026-10-03T12:00:00+07:00")
    _commit(gh, "m.txt", "m\n", "chore: nhánh chính tiến lên", "2026-10-04T09:00:00+07:00")
    _g(gh, "push", "-q", "origin", "main")
    _g(cay, "fetch", "-q", "origin")
    _g(cay, "merge", "-q", "--no-ff", "--no-edit", "origin/main", ngay="2026-10-05T10:00:00+07:00")
    ct: dict = {}
    so, nhanh = M.dem_commit_chua_co_tren_remote(cay, ct)
    assert so == 2 and ct["gop_merge"] == [] and nhanh == ["phu"]


def test_merge_sach_loi_git_thi_khong_nhan(tmp_path):
    """SHA không tồn tại / không phải merge ⇒ không nhận (không đoán)."""
    cay = _dung_kich_ban(tmp_path)
    gia = "0" * 40
    thuong = _g(cay, "rev-parse", "origin/main")
    assert M._commit_merge_sach(cay, {gia, thuong}, {gia, thuong}, set()) == set()
