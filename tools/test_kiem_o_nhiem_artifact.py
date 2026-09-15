#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho kiem_o_nhiem_artifact.py (15/09/2026, workflow kiểm tra toàn diện).

Bối cảnh: dòng `_git("diff", "--cached" if a.staged else "", ...)` từng nhét CHUỖI
RỖNG làm một argument thật của `git diff` khi KHÔNG chạy với `--staged` — lệnh thành
`git diff "" --name-only ...`, git từ chối với "ambiguous argument ''" (exit 128).
Lỗi đó bị đọc nhầm thành "thiếu công cụ" nên nhánh gọi tay không cờ CHƯA TỪNG thực
sự soi được file nào thay đổi trong working tree — chỉ nhánh `--staged` (dùng trong
`.githooks/pre-commit`) còn hoạt động đúng.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`): (1) kiểm HÀNH VI thật qua
một repo git tạm, không đếm chuỗi; (2) mỗi ca gắn với rủi ro THẬT; (3) nhanh.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_o_nhiem_artifact as K  # noqa: E402


def _repo_git_tam(tmp_path: Path) -> Path:
    """Dựng một repo git tối giản dưới tmp_path, có 1 commit ban đầu."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    return repo


def _gan_repo_gia(monkeypatch, repo: Path) -> None:
    """Ép mọi lệnh git bên trong module chạy trên `repo` thay vì REPO thật.

    _git() bind mặc định `cay=REPO` NGAY LÚC ĐỊNH NGHĨA HÀM (kwdefault), nên chỉ
    monkeypatch K.REPO KHÔNG đủ — phải thay hẳn K._git bằng một wrapper trỏ đúng
    `repo`, để mọi lệnh gọi `_git(...)` không kèm `cay=` bên trong main() đều chạy
    trên repo tạm."""
    goc = K._git

    def _git_gia(*args, cay=None):
        return goc(*args, cay=repo)

    monkeypatch.setattr(K, "_git", _git_gia)
    monkeypatch.setattr(K, "REPO", repo)


def test_khong_co_staged_van_soi_duoc_thay_doi_that_trong_working_tree(monkeypatch, tmp_path, capsys):
    """Ca lỗi gốc: KHÔNG truyền --staged (cách gọi tay bình thường), sổ bằng chứng
    trong quality/eval/ bị hạ cấp retracted→unknown ở WORKING TREE (chưa git add) —
    trước bản vá, lệnh git diff rỗng-chuỗi crash và tool luôn thoát 0 im lặng, KHÔNG
    bao giờ chạm tới file này."""
    repo = _repo_git_tam(tmp_path)
    d = repo / "quality" / "eval" / "negative"
    d.mkdir(parents=True)
    f = d / "rut-bai.json"
    f.write_text('{"PMID:9500320": {"status": "retracted"}}', encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)

    # Hạ cấp ở WORKING TREE, KHÔNG stage.
    f.write_text('{"PMID:9500320": {"status": "unknown_mock_or_no_email"}}', encoding="utf-8")

    _gan_repo_gia(monkeypatch, repo)
    monkeypatch.setattr(sys, "argv", ["kiem_o_nhiem_artifact.py"])
    rc = K.main()
    out = capsys.readouterr().out
    assert rc == 1, f"phải CHẶN commit (rc=1), thực tế rc={rc}, out={out!r}"
    assert "ĐI LÙI" in out
    assert "retracted" in out and "unknown_mock_or_no_email" in out


def test_khong_co_thay_doi_gi_thi_sach(monkeypatch, tmp_path, capsys):
    """Đối chứng: repo sạch (không sửa gì) → không báo ô nhiễm, không crash."""
    repo = _repo_git_tam(tmp_path)
    d = repo / "quality" / "eval"
    d.mkdir(parents=True)
    (d / "x.json").write_text('{"a": {"status": "ok"}}', encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)

    _gan_repo_gia(monkeypatch, repo)
    monkeypatch.setattr(sys, "argv", ["kiem_o_nhiem_artifact.py"])
    rc = K.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "🟢" in out


def test_co_staged_van_hoat_dong_dung_nhu_truoc(monkeypatch, tmp_path, capsys):
    """Đối chứng: nhánh --staged (dùng trong pre-commit) không hồi quy — vẫn bắt
    được ca hạ cấp khi thay đổi đã git add."""
    repo = _repo_git_tam(tmp_path)
    d = repo / "exports" / "de-tai-that"
    d.mkdir(parents=True)
    f = d / "so.json"
    f.write_text('{"k": {"status": "retracted"}}', encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)

    f.write_text('{"k": {"status": "unknown"}}', encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)

    _gan_repo_gia(monkeypatch, repo)
    monkeypatch.setattr(sys, "argv", ["kiem_o_nhiem_artifact.py", "--staged"])
    rc = K.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "ĐI LÙI" in out


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
