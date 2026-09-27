"""Email liên hệ gửi kèm API công khai lấy từ CẤU HÌNH, không viết cứng — vá 27/09/2026.

Repo công khai từng chứa email cá nhân của bác sĩ trong 3 công cụ (URL NCBI `email=` của de_xuat_gradeby, `MAILTO` của
doi_chieu_openalex, điểm thăm OpenAlex của sources_health). Nay cả ba dùng `tra_dinh_danh.email_lien_he()` (NCBI_EMAIL
từ biến môi trường → kho secrets ngoài git); rỗng thì BỎ tham số. Ngoại tuyến: HOME trỏ thư mục tạm, mạng giả.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
_THU_CA_NHAN = re.compile(
    r"[A-Za-z0-9._%+-]+@(?:gmail|googlemail|yahoo|ymail|hotmail|outlook|live|msn|icloud|me|aol|proton|protonmail|gmx"
    r"|yandex|zoho)\.[A-Za-z]{2,}")
_DUOI_MA = (".py", ".sh", ".command", ".js", ".mjs", ".ts", ".toml", ".yml", ".yaml", ".ps1", ".bat", ".cmd")


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, GOC / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


@pytest.fixture()
def khong_cau_hinh(tmp_path, monkeypatch):
    """Máy/CI không khai NCBI_EMAIL và không có kho secrets."""
    monkeypatch.delenv("NCBI_EMAIL", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))


def test_khong_cau_hinh_thi_khong_co_email_du_phong(khong_cau_hinh):
    assert _nap("ttd_email_20260927", "tra_dinh_danh.py").email_lien_he() == ""


def test_diem_tham_openalex_theo_cau_hinh(khong_cau_hinh, monkeypatch):
    assert "mailto" not in _nap("sh_email_20260927_a", "sources_health.py").DIEM_THAM["SRC-007"]
    monkeypatch.setenv("NCBI_EMAIL", "tester@example.org")
    assert _nap("sh_email_20260927_b", "sources_health.py").DIEM_THAM["SRC-007"].endswith(
        "&mailto=tester@example.org")


@pytest.mark.parametrize("email,ky_vong", [("", None), ("tester@example.org", "&mailto=tester@example.org")])
def test_doi_chieu_openalex_mailto_theo_cau_hinh(khong_cau_hinh, monkeypatch, email, ky_vong):
    if email:
        monkeypatch.setenv("NCBI_EMAIL", email)
    m = _nap(f"doa_email_20260927_{bool(email)}", "doi_chieu_openalex.py")
    url: list[str] = []
    monkeypatch.setattr(m, "_goi", lambda u: url.append(u) or {"results": []})
    assert m.quet_chu_de({"topic": "heart failure"}, 30, 5, set(), None) == []
    assert (ky_vong in url[0]) if ky_vong else ("mailto" not in url[0])


def test_khong_email_ca_nhan_viet_cung_trong_ma():
    """Quét mã được theo dõi (không kể test — nơi địa chỉ giả dùng để thử bộ lọc PII là hợp lệ)."""
    tep = subprocess.run(["git", "-C", str(GOC), "ls-files"], capture_output=True, text=True, check=True).stdout
    vi_pham = []
    for rel in tep.splitlines():
        p = Path(rel)
        if p.suffix not in _DUOI_MA or p.name.startswith("test_") or "tests" in p.parts:
            continue
        try:
            noi_dung = (GOC / p).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue  # tệp được theo dõi nhưng vắng trên bản sao này — không phải vi phạm
        for so, dong in enumerate(noi_dung.splitlines(), 1):
            if _THU_CA_NHAN.search(dong):
                vi_pham.append(f"{rel}:{so}")
    assert not vi_pham, f"email cá nhân viết cứng trong mã (repo công khai) — dùng tra_dinh_danh.email_lien_he(): {vi_pham}"
