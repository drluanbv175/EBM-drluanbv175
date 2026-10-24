"""Cảm biến «commit chưa đẩy» không đếm commit MERGE trên nhánh PR đã gộp squash — vá 24/10/2026.

Đo 24/10: hòm việc/Đài báo «Repo gốc: 3 commit chưa có trên remote» và «repo y khoa: 6» — cả 9 là commit
«Merge remote-tracking branch 'origin/…' into <nhánh PR>» (đồng bộ nhánh chính vào nhánh PR trước khi GitHub squash).
`git cherry` bỏ qua commit merge nên bộ lọc 09/10 không bao giờ thấy chúng; danh sách nhánh giữ chúng thì rỗng. Chiều an
toàn: commit merge mang nội dung riêng chưa lên nhánh chính (giải xung đột mới) vẫn phải bị đếm. Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_commit_merge", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

_TD = "feat(cong): bộ nhận diện ô còn trống dùng chung cho mười một cổng"


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
    tran = tmp_path / "remote.git"
    _g(tmp_path, "init", "--bare", "-q", "-b", "main", str(tran))
    cay = tmp_path / "cay"
    cay.mkdir()
    _g(cay, "init", "-q", "-b", "main")
    for c in (cay,):
        _g(c, "config", "user.email", "t@t")
        _g(c, "config", "user.name", "t")
    _commit(cay, "a.txt", "a\n", "goc", "2026-10-01T08:00:00+07:00")
    _g(cay, "remote", "add", "origin", str(tran))
    _g(cay, "push", "-q", "-u", "origin", "main")
    _g(cay, "remote", "set-head", "origin", "main")
    gh = tmp_path / "gh"
    _g(tmp_path, "clone", "-q", str(tran), str(gh))
    _g(gh, "config", "user.email", "g@g")
    _g(gh, "config", "user.name", "g")
    return cay, gh


def _nhanh_pr_co_merge(cay: Path, gh: Path) -> None:
    """Nhánh PR «phu»: một commit thật, rồi nhánh chính tiến lên và được merge VÀO nhánh PR (commit merge cục bộ)."""
    _g(cay, "switch", "-q", "-c", "phu")
    _commit(cay, "p1.txt", "1\n", _TD, "2026-10-03T12:00:00+07:00")
    _g(gh, "pull", "-q")
    _commit(gh, "khac.txt", "k\n", "fix: một PR khác gộp trước", "2026-10-03T14:00:00+07:00")
    _g(gh, "push", "-q", "origin", "main")
    _g(cay, "fetch", "-q", "origin")
    _g(cay, "merge", "-q", "--no-ff", "--no-edit", "origin/main", ngay="2026-10-03T15:00:00+07:00")
    _g(cay, "switch", "-q", "main")


def _gop_squash_pr(cay: Path, gh: Path) -> None:
    """GitHub squash PR một commit: tiêu đề = tiêu đề commit + «(#81)»."""
    _g(gh, "pull", "-q")
    (gh / "p1.txt").write_text("1\n", encoding="utf-8", newline="\n")
    _g(gh, "add", "p1.txt")
    _g(gh, "commit", "-q", "-m", f"{_TD} (#81)", ngay="2026-10-03T17:00:00+07:00")
    _g(gh, "push", "-q", "origin", "main")
    _g(cay, "fetch", "-q", "origin")


def test_commit_merge_tren_nhanh_da_squash_khong_con_bi_dem(tmp_path):
    cay, gh = _repo(tmp_path)
    _nhanh_pr_co_merge(cay, gh)
    assert M.dem_commit_chua_co_tren_remote(cay) == (2, ["phu"]), "trước khi gộp: commit thật + commit merge"
    _gop_squash_pr(cay, gh)
    ct: dict = {}
    assert M.dem_commit_chua_co_tren_remote(cay, ct) == (0, [])
    # commit thật được lớp ① (trùng bản vá) hoặc ② (squash) lọc; commit merge chỉ lớp ③ lọc được
    assert len(ct["trung_ban_va"]) + len(ct["gop_squash"]) == 1
    assert len(ct["merge_da_gop"]) == 1 and ct["nhanh_da_gop"] == ["phu"]


def test_commit_merge_mang_noi_dung_rieng_chua_len_van_bi_dem(tmp_path):
    """Giải xung đột/sửa trong commit merge mà nhánh chính KHÔNG có ⇒ vẫn đếm (thừa an toàn hơn thiếu)."""
    cay, gh = _repo(tmp_path)
    _nhanh_pr_co_merge(cay, gh)
    _g(cay, "switch", "-q", "phu")
    (cay / "rieng.txt").write_text("nội dung chỉ có trong commit merge\n", encoding="utf-8", newline="\n")
    _g(cay, "add", "rieng.txt")
    _g(cay, "commit", "-q", "--amend", "--no-edit")
    _g(cay, "switch", "-q", "main")
    _gop_squash_pr(cay, gh)
    ct: dict = {}
    n, _nhanh = M.dem_commit_chua_co_tren_remote(cay, ct)
    assert n == 1 and ct["merge_da_gop"] == []


def test_commit_merge_tren_nhanh_chua_gop_van_bi_dem(tmp_path):
    cay, gh = _repo(tmp_path)
    _nhanh_pr_co_merge(cay, gh)
    ct: dict = {}
    assert M.dem_commit_chua_co_tren_remote(cay, ct) == (2, ["phu"])
    assert ct["merge_da_gop"] == []


def test_merge_co_sua_tay_thuoc_pr_da_gop_thi_khong_con_bi_dem(tmp_path, monkeypatch):
    """Giải xung đột tay nằm trong PR đã gộp (GitHub ghi commit ↔ PR, tạo trước lúc gộp) ⇒ đã vào squash ⇒ không đếm."""
    cay, gh = _repo(tmp_path)
    _nhanh_pr_co_merge(cay, gh)
    _g(cay, "switch", "-q", "phu")
    (cay / "rieng.txt").write_text("giải xung đột tay\n", encoding="utf-8", newline="\n")
    _g(cay, "add", "rieng.txt")
    _g(cay, "commit", "-q", "--amend", "--no-edit")
    sha_merge = _g(cay, "rev-parse", "HEAD")
    _g(cay, "switch", "-q", "main")
    _gop_squash_pr(cay, gh)
    monkeypatch.setattr(M, "_pr_da_gop_chua_commit", lambda duong, sha: sha == sha_merge)
    ct: dict = {}
    assert M.dem_commit_chua_co_tren_remote(cay, ct) == (0, [])
    assert ct["merge_da_gop"] == [sha_merge]


def test_remote_khong_phai_github_thi_khong_tra_pr(tmp_path):
    """Remote là đường dẫn cục bộ ⇒ không gọi gh, trả False (không biết ≠ đã gộp)."""
    cay, gh = _repo(tmp_path)
    _nhanh_pr_co_merge(cay, gh)
    assert M._pr_da_gop_chua_commit(cay, _g(cay, "rev-parse", "phu")) is False


def test_merge_sach_false_khi_co_sua_tay(tmp_path):
    cay, gh = _repo(tmp_path)
    _nhanh_pr_co_merge(cay, gh)
    assert M._merge_sach(cay, _g(cay, "rev-parse", "phu")) is True
    _g(cay, "switch", "-q", "phu")
    (cay / "rieng.txt").write_text("x\n", encoding="utf-8", newline="\n")
    _g(cay, "add", "rieng.txt")
    _g(cay, "commit", "-q", "--amend", "--no-edit")
    assert M._merge_sach(cay, _g(cay, "rev-parse", "HEAD")) is False
