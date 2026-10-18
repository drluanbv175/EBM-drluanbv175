# -*- coding: utf-8 -*-
"""Hồi quy tools/dong_bo_cong_cu_hub.py — chỉ tua nhanh, chỉ từ master sạch, sao lưu trước khi chép (18/10/2026).

Dựng một repo git TẠM (sync/ebm-master-tools/ + EBM_MASTER/tools/) — không đụng cây thật.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "dong_bo_cong_cu_hub.py"
NGUON = Path("sync") / "ebm-master-tools"


def _git(goc: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(goc), *args], check=True, capture_output=True)


def _ghi(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture()
def goc(tmp_path):
    """Repo tạm: nguồn ingest có HAI phiên bản trong git (v1 → v2), bản chạy đang là v1."""
    g = tmp_path / "goc"
    g.mkdir()
    _git(g, "init", "-q")
    _git(g, "checkout", "-q", "-b", "master")
    _git(g, "config", "user.email", "test@example.invalid")
    _git(g, "config", "user.name", "test")
    _ghi(g / NGUON / "ingest_dashboard.py", "# ban 1\n")
    _ghi(g / NGUON / "ledger_ids.py", "# ledger\n")
    _ghi(g / NGUON / "PHIEN-BAN-DA-BIET.json", "{}\n")
    _git(g, "add", "-A")
    _git(g, "commit", "-q", "-m", "v1")
    _ghi(g / NGUON / "ingest_dashboard.py", "# ban 2\n")
    _git(g, "commit", "-q", "-am", "v2")
    _ghi(g / "EBM_MASTER" / "tools" / "ingest_dashboard.py", "# ban 1\n")
    _ghi(g / "EBM_MASTER" / "tools" / "ledger_ids.py", "# ledger\n")
    return g


def _chay(g: Path, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-B", str(TOOL), "--goc", str(g), *args],
                          capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)


def _ban_chay(g: Path) -> str:
    return (g / "EBM_MASTER" / "tools" / "ingest_dashboard.py").read_text(encoding="utf-8")


def test_mac_dinh_chi_bao_khong_chep(goc):
    r = _chay(goc)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "tụt hậu" in r.stdout
    assert _ban_chay(goc) == "# ban 1\n"


def test_ap_dung_tua_nhanh_va_sao_luu(goc):
    r = _chay(goc, "--ap-dung")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _ban_chay(goc) == "# ban 2\n"
    sao_luu = list((goc / "EBM_MASTER" / "BACKUPS" / "tools").glob("ingest_dashboard_*_truoc-dong-bo.py"))
    assert len(sao_luu) == 1 and sao_luu[0].read_text(encoding="utf-8") == "# ban 1\n"
    assert _chay(goc, "--im-khi-on").returncode == 0


def test_ban_chay_sua_tay_bi_giu_lai(goc):
    _ghi(goc / "EBM_MASTER" / "tools" / "ingest_dashboard.py", "# ban 1\n# vá tay chưa hồi nguồn\n")
    r = _chay(goc, "--ap-dung")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "KHÁC mọi phiên bản" in r.stdout and "2 dòng không có ở nguồn" in r.stdout   # «# ban 1» + dòng vá
    assert _ban_chay(goc) == "# ban 1\n# vá tay chưa hồi nguồn\n"


def test_tu_choi_chep_khi_khong_o_master(goc):
    _git(goc, "checkout", "-q", "-b", "nhanh-tinh-nang")
    r = _chay(goc, "--ap-dung")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "không phải master/main" in r.stdout
    assert _ban_chay(goc) == "# ban 1\n"


def test_tu_choi_chep_khi_nguon_co_sua_chua_commit(goc):
    _ghi(goc / NGUON / "ingest_dashboard.py", "# ban 3 chưa commit\n")
    r = _chay(goc, "--ap-dung")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "CHƯA commit" in r.stdout
    assert _ban_chay(goc) == "# ban 1\n"


def test_moc_so_phien_ban_da_biet_cho_phep_tua_nhanh(goc):
    """Mốc nguyên trạng TRƯỚC khi nguồn vào git (gộp squash làm mất commit đó) nằm ở sổ JSON."""
    cu = "# ban goc ngoai git\n"
    sha = hashlib.sha256(cu.encode("utf-8").rstrip()).hexdigest()
    _ghi(goc / NGUON / "PHIEN-BAN-DA-BIET.json", json.dumps({"ingest_dashboard.py": [sha]}))
    _git(goc, "commit", "-q", "-am", "so phien ban")
    _ghi(goc / "EBM_MASTER" / "tools" / "ingest_dashboard.py", cu)
    r = _chay(goc, "--ap-dung")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _ban_chay(goc) == "# ban 2\n"


def test_khong_co_ebm_master_la_khong_do_duoc(tmp_path):
    g = tmp_path / "tran"
    _ghi(g / NGUON / "ingest_dashboard.py", "# x\n")
    r = _chay(g)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "không đo được" in r.stdout
