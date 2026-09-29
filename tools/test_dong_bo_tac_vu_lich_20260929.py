"""Đồng bộ tác vụ lịch nguồn git → bản chạy của app — vá 29/09/2026.

Đo 29/09: 13/14 bản chạy SKILL.md trên Mac tụt hậu nguồn git (phần lớn bản 17/08) suốt 6 tuần, và tác vụ mới
`kiem-rut-bai-kho-thang` chưa từng được tạo — không có gì đối chiếu. Test dựng một repo git tạm có hai phiên bản SKILL.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "dong_bo_tac_vu_lich.py"


@pytest.fixture()
def M():
    sp = importlib.util.spec_from_file_location("dbtvl_20260929", _TEP)
    mod = importlib.util.module_from_spec(sp)
    sys.modules["dbtvl_20260929"] = mod
    sp.loader.exec_module(mod)
    return mod


def _git(repo: Path, *lenh: str) -> None:
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org",
                    "-c", "commit.gpgsign=false", *lenh], check=True, capture_output=True)


def _ghi(p: Path, noi_dung: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(noi_dung, encoding="utf-8", newline="\n")


@pytest.fixture()
def moi_truong(tmp_path):
    """Repo git có 4 tác vụ kỳ vọng; SKILL của mỗi tác vụ có bản v1 (cũ) rồi v2 (hiện tại)."""
    repo, ban_chay = tmp_path / "repo", tmp_path / "scheduled-tasks"
    ma = ["tut-hau", "khop", "sua-rieng", "chua-tao"]
    _ghi(repo / "sync" / "lich-nen-ky-vong.json", json.dumps({"tac_vu": [{"id": m} for m in ma]}))
    _git(repo.parent, "init", "-q", str(repo))
    for ban in ("v1", "v2"):
        for m in ma:
            _ghi(repo / "sync" / "scheduled-tasks" / m / "SKILL.md", f"{m} {ban}\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", ban)
    _ghi(ban_chay / "tut-hau" / "SKILL.md", "tut-hau v1\n")
    _ghi(ban_chay / "khop" / "SKILL.md", "khop v2\n")
    _ghi(ban_chay / "sua-rieng" / "SKILL.md", "sua-rieng v1 + dòng bác sĩ tự thêm\n")
    return repo, ban_chay


def test_phan_loai_du_bon_truong_hop(M, moi_truong):
    repo, ban_chay = moi_truong
    assert M.phan_loai(repo, ban_chay) == {"tut-hau": "tut_hau", "khop": "khop",
                                           "sua-rieng": "khac_rieng", "chua-tao": "chua_tao"}


def test_ap_dung_chi_chep_tac_vu_tut_hau_va_sao_luu_truoc(M, moi_truong):
    repo, ban_chay = moi_truong
    da_chep, sao_luu = M.ap_dung(repo, ban_chay, M.phan_loai(repo, ban_chay))
    assert da_chep == ["tut-hau"]
    assert (ban_chay / "tut-hau" / "SKILL.md").read_text(encoding="utf-8") == "tut-hau v2\n"
    assert (ban_chay / "sua-rieng" / "SKILL.md").read_text(encoding="utf-8").endswith("dòng bác sĩ tự thêm\n"), \
        "bản chạy có sửa riêng bị chép đè — mất sửa của bác sĩ"
    assert not (ban_chay / "chua-tao").exists(), "máy KHÔNG được tự tạo tác vụ"
    assert (sao_luu / "tut-hau" / "SKILL.md").read_text(encoding="utf-8") == "tut-hau v1\n"


def test_ma_thoat_theo_che_do(M, moi_truong, monkeypatch, capsys):
    repo, ban_chay = moi_truong
    monkeypatch.setattr(M, "REPO", repo)
    monkeypatch.setenv("EBM_TAC_VU_LICH_DIR", str(ban_chay))
    for argv, ma in ((["x"], 1), (["x", "--can-bac-si"], 1), (["x", "--ap-dung"], 0)):
        monkeypatch.setattr(sys, "argv", argv)
        assert M.main() == ma, argv
    out = capsys.readouterr().out
    assert "chưa tạo trong app" in out and "sửa riêng" in out


def test_khong_co_thu_muc_ban_chay_thi_khong_do_duoc(M, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("EBM_TAC_VU_LICH_DIR", str(tmp_path / "khong-co"))
    monkeypatch.setattr(sys, "argv", ["x"])
    assert M.main() == 0 and "không đo được" in capsys.readouterr().out


def test_chi_co_tac_vu_chua_tao_van_la_viec_cua_bac_si(M, moi_truong, monkeypatch):
    """Ca thật 29/09: `kiem-rut-bai-kho-thang` có nguồn mà chưa tạo trong app — một mình nó cũng phải được nhắc."""
    repo, ban_chay = moi_truong
    _ghi(ban_chay / "sua-rieng" / "SKILL.md", "sua-rieng v2\n")
    _ghi(ban_chay / "tut-hau" / "SKILL.md", "tut-hau v2\n")
    monkeypatch.setattr(M, "REPO", repo)
    monkeypatch.setenv("EBM_TAC_VU_LICH_DIR", str(ban_chay))
    monkeypatch.setattr(sys, "argv", ["x", "--can-bac-si", "--im-khi-on"])
    assert M.main() == 1
    monkeypatch.setattr(sys, "argv", ["x", "--im-khi-on"])
    assert M.main() == 0, "tác vụ chưa tạo không phải việc máy tự sửa được — không được làm lệnh kiểm tụt hậu đỏ"


def test_app_ghi_thieu_dong_trong_cuoi_van_la_khop(M, moi_truong):
    """29/09: app tạo tác vụ ghi SKILL.md không có dòng trống cuối — so thô báo «sửa riêng» giả."""
    repo, ban_chay = moi_truong
    _ghi(ban_chay / "khop" / "SKILL.md", "khop v2")
    _ghi(ban_chay / "tut-hau" / "SKILL.md", "tut-hau v1\r\n")
    loai = M.phan_loai(repo, ban_chay)
    assert loai["khop"] == "khop" and loai["tut-hau"] == "tut_hau"
