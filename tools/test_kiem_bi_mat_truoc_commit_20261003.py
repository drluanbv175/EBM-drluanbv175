#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy AN-06 (03/10/2026): chốt bí mật/PII trước commit. Token GIẢ được GHÉP lúc chạy (không nằm nguyên trên một dòng nguồn) để
chính tệp test này không bị chốt chặn. Kho git tạm, cấu hình git cô lập; không gọi mạng."""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location("_t_kbm", TOOLS / "kiem_bi_mat_truoc_commit.py")
K = importlib.util.module_from_spec(sp)
sys.modules["_t_kbm"] = K
sp.loader.exec_module(K)

GIA = {
    "anthropic": "sk-" + "ant-" + "api03-" + "A1b2C3d4" * 4,
    "github": "gh" + "p_" + "Z9y8X7w6" * 5,
    "aws": "AK" + "IA" + "ABCDEFGHIJ012345",
    "pem": "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
    "url": "post" + "gresql://bacsi:" + "matkhauthat" + "@db.benhvien.vn:5432/x",
}


@pytest.mark.parametrize("ten", list(GIA))
def test_chan_bi_mat_that(ten):
    chan, _cb = K.quet_dong("a.py", 3, f"KHOA = '{GIA[ten]}'")
    assert chan and chan[0][:2] == ("a.py", 3)


def test_mien_tru_tren_dung_dong():
    assert K.quet_dong("a.py", 1, f"x = '{GIA['aws']}'  # bimat-mien: khoá giả cho test")[0] == []


def test_url_mat_khau_may_cuc_bo_chi_canh_bao():
    for dong in ("DATABASE_URL: post" + "gresql://clinic_os:clinic_os@postgres:5432/db",
                 "HTTPS_PROXY=http://nguoidung:" + "MATKHAU@proxy.local:3128",
                 "redis://u:" + "pass1234@localhost:6379/0"):
        chan, cb = K.quet_dong("c.yml", 1, dong)
        assert chan == [] and any("CỤC BỘ" in x[2] for x in cb), dong


@pytest.mark.parametrize("dong, loai", [
    ("goi 0912345678 de hen", "số điện thoại VN"),
    ("CCCD 001204012345", "số 12 chữ (CCCD?)"),
    ("lien he nguyen.van.a@gmail.com", "email cá nhân"),
    ("api_key = '" + "abcdefghij" * 2 + "'", "gán khoá/mật khẩu dài"),
])
def test_pii_chi_canh_bao(dong, loai):
    chan, cb = K.quet_dong("b.md", 1, dong)
    assert chan == [] and any(x[2] == loai for x in cb)


def test_khong_bao_oan_mau_thuong_gap():
    for dong in ("doi:10.1016/j.jacc.2026.05.033", "PMID 42377292", "sha256 " + "ab" * 32, "NCT01234567", "CRD420261354386",
                 "ngày 2026-10-03T07:05:25", "https://pubmed.ncbi.nlm.nih.gov/42377292/"):
        chan, cb = K.quet_dong("x.md", 1, dong)
        assert chan == [] and cb == [], (dong, chan, cb)


@pytest.mark.parametrize("duong, chan", [
    ("config/gate_ed25519_pubkeys/G2.pub", False), ("config/gate_ed25519_pubkeys/G2", True),
    ("config/gate_ed25519_pubkeys/README.md", False), ("secrets/server.pem", True), ("ssh/id_rsa", True), ("id_ed25519.pub", False),
    ("app/.env", True), ("app/.env.example", False), ("x/gate_approval_key_PI", True), ("tools/token_helper.py", False),
])
def test_ten_tep_khoa(duong, chan):
    assert (K.tep_khoa(duong) is not None) is chan


@pytest.fixture()
def kho(tmp_path, monkeypatch):
    if shutil.which("git") is None:
        pytest.skip("cần git")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@t.invalid"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "t"], check=True)
    (tmp_path / "cu.py").write_text(f"CU = '{GIA['aws']}'\n", encoding="utf-8", newline="\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "cu.py"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "c"], check=True)
    return tmp_path


def test_chi_quet_dong_THEM_trong_phan_stage(kho, capsys):
    (kho / "cu.py").write_text(f"CU = '{GIA['aws']}'\nMOI = 1\n", encoding="utf-8", newline="\n")
    subprocess.run(["git", "-C", str(kho), "add", "cu.py"], check=True)
    assert K.main(["--repo", str(kho)]) == 0, "khoá có sẵn từ trước (không phải dòng thêm) không chặn commit mới"
    (kho / "moi.py").write_text(f"T = '{GIA['github']}'\n", encoding="utf-8", newline="\n")
    subprocess.run(["git", "-C", str(kho), "add", "moi.py"], check=True)
    assert K.main(["--repo", str(kho)]) == 1
    ra = capsys.readouterr().out
    assert "moi.py:1 · token GitHub" in ra and GIA["github"] not in ra, "không bao giờ in giá trị khớp"


def test_tep_khoa_trong_stage_bi_chan(kho):
    (kho / "khoa.pem").write_text("x\n", encoding="utf-8", newline="\n")
    subprocess.run(["git", "-C", str(kho), "add", "khoa.pem"], check=True)
    assert K.main(["--repo", str(kho)]) == 1


def test_tat_ca_quet_tep_da_track(kho):
    assert K.main(["--repo", str(kho), "--tat-ca"]) == 1


def test_pre_commit_goi_chot():
    hook = (TOOLS.parent / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    dong = [x for x in hook.splitlines() if "kiem_bi_mat_truoc_commit.py" in x and not x.lstrip().startswith("#")]
    assert dong, "pre-commit không gọi chốt bí mật"


# ---- 03/10/2026 (kiểm độc lập sau gộp): chốt tin vào định dạng HIỂN THỊ của `git diff` ⇒ bốn đường lọt NỘI DUNG ----
def _stage(kho: Path, ten: str, noi_dung: str) -> None:
    p = kho / ten
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(noi_dung.encode("utf-8"))
    subprocess.run(["git", "-C", str(kho), "add", "--", ten], check=True)


_TEN_DAC_BIET = ["thử_bí_mật.txt", "thư mục/có cách.txt"] + ([] if os.name == "nt" else ['nhay"kep.txt', "gach\\nguoc.txt"])


@pytest.mark.parametrize("ten", _TEN_DAC_BIET)
def test_ten_tep_khong_ascii_va_ky_tu_dac_biet_van_bi_quet(kho, capsys, ten):
    """core.quotepath mặc định bọc nháy tên tiếng Việt («+++ "b/th\\341…"») ⇒ bản đầu bỏ qua CẢ TỆP; tên có dấu cách thì
    git thêm TAB cuối tên. Phải chặn VÀ in đúng tên (không mã bát phân, không TAB)."""
    _stage(kho, ten, f"x\n{GIA['pem']}\n")
    assert K.main(["--repo", str(kho)]) == 1
    assert f"{ten}:2 · khối PRIVATE KEY" in capsys.readouterr().out


@pytest.mark.parametrize("khoa, gia_tri", [("diff.mnemonicPrefix", "true"), ("diff.noprefix", "true"), ("core.quotepath", "true")])
def test_cau_hinh_git_cua_nguoi_dung_khong_lam_mu_chot(kho, khoa, gia_tri):
    subprocess.run(["git", "-C", str(kho), "config", khoa, gia_tri], check=True)
    _stage(kho, "thử.py", f"T = '{GIA['github']}'\n")
    assert K.main(["--repo", str(kho)]) == 1, f"{khoa}={gia_tri} làm mù chốt"


def test_dong_them_gia_dang_dau_tep_van_bi_quet(kho, capsys):
    """Dòng THÊM có nội dung «++ …» hiện thành «+++ …» trong diff — không được đọc nhầm là dòng đầu tệp."""
    _stage(kho, "moi.md", f"++ {GIA['pem']}\nbinh thuong\n")
    assert K.main(["--repo", str(kho)]) == 1
    assert "moi.md:1 · khối PRIVATE KEY" in capsys.readouterr().out


@pytest.mark.parametrize("ngat", ["\r", " ", "\x0c", "\x1c"])
def test_ky_tu_ngat_dong_la_khong_giau_duoc_bi_mat(kho, ngat):
    """splitlines() cắt cả ở \\r, \\u2028… ⇒ phần sau ký tự đó mất dấu «+» và không được quét."""
    _stage(kho, "moi.txt", f"abc{ngat}{GIA['pem']}\n")
    assert K.main(["--repo", str(kho)]) == 1


def test_tep_sach_ten_tieng_viet_van_cho_qua(kho):
    _stage(kho, "ghi_chú_khám.md", "chỉ là ghi chú bình thường\n")
    assert K.main(["--repo", str(kho)]) == 0


def test_bo_nhay_c():
    assert K._bo_nhay_c('"th\\341\\273\\255.txt"') == "thử.txt"
    assert K._bo_nhay_c('"a\\"b\\\\c\\td"') == 'a"b\\c\td'
    assert K._bo_nhay_c("khong_nhay.txt") == "khong_nhay.txt"
