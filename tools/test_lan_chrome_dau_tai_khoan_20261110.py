# -*- coding: utf-8 -*-
"""Mẫu dò «dấu giao diện tài khoản» của bộ lưu làn Chrome phải CÙNG ranh giới từ với cổng nhận tệp (10/11/2026).

Sự cố thật 10/11/2026: bản PMC của PMID 39482474 (JGIM) có câu «…symptom or sign outside of the following…». Mẫu cũ của
`tools/lan_chrome/bo_luu.js` (`/sign out|log ?out|my account/i`, không ranh giới) khớp «sign out» nằm trong «sign outside» ⇒
bộ lưu báo «CÓ DẤU TÀI KHOẢN — đừng bấm, báo bác sĩ», bài dừng chờ bác sĩ; cổng `phien_uy_quyen_chrome._DAU_TAI_KHOAN` (có \\b)
thì nhận tệp bình thường. Khoá:
  • hàm thuần `coDauTaiKhoan` không báo nhầm chuỗi con giữa từ, vẫn bắt dấu tài khoản thật (kể cả tiếng Việt);
  • bộ lưu và cổng phán GIỐNG NHAU trên cùng bảng mẫu, và cùng danh sách cụm;
  • dòng THI HÀNH của bộ lưu gọi hàm đó (không còn mẫu trần).
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
BO_LUU = TOOLS / "lan_chrome" / "bo_luu.js"
NODE = shutil.which("node")

# (văn bản, có phải dấu giao diện tài khoản không)
MAU = [
    ("Any symptom or sign outside of the following was considered atypical", False),  # PMID 39482474 — sự cố gốc
    ("study design outcomes were prespecified", False),
    ("the catalog output was reviewed", False),
    ("log output of the device", False),          # mẫu cũ khớp «log out» + «put»
    ("blogout", False),
    ("my accounts of the illness", False),
    ("Sign out", True),
    ("Welcome back | SIGN OUT | Help", True),
    ("(sign out)", True),
    ("Log out", True),
    ("Logout", True),
    ("My Account", True),
    ("Đăng xuất", True),
    ("Xin chào — Tài khoản của tôi", True),
    ("", False),
]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


PUQ = _nap("_puq_dau_tai_khoan_20261110", "phien_uy_quyen_chrome.py")


def _js(ds: list[str]) -> list[bool]:
    ma = ("const m=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);"
          "process.stdin.on('end',()=>process.stdout.write(JSON.stringify(JSON.parse(s).map(x=>m.coDauTaiKhoan(x)))))")
    r = subprocess.run([NODE, "-e", ma, str(BO_LUU)], input=json.dumps(ds), capture_output=True, text=True,
                       encoding="utf-8", timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_bo_luu_khong_bao_nham_chuoi_con_va_van_bat_dau_tai_khoan_that():
    kq = _js([t for t, _ in MAU])
    sai = [(t, co, mong) for (t, mong), co in zip(MAU, kq) if co != mong]
    assert not sai, sai


def test_cong_nhan_tep_phan_dung_bang_mau():
    sai = [(t, mong) for t, mong in MAU if bool(PUQ._DAU_TAI_KHOAN.search(t)) != mong]
    assert not sai, sai


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_bo_luu_va_cong_phan_giong_nhau():
    ds = [t for t, _ in MAU]
    assert _js(ds) == [bool(PUQ._DAU_TAI_KHOAN.search(t)) for t in ds]


def _dong_thi_hanh() -> list[str]:
    """Dòng mã của bo_luu.js, bỏ dòng chú thích (//, /* … */, dòng « * …») — chốt khớp dòng thi hành, không khớp chú thích."""
    ra, trong_khoi = [], False
    for d in BO_LUU.read_text(encoding="utf-8").splitlines():
        s = d.strip()
        if trong_khoi:
            trong_khoi = "*/" not in s
            continue
        if s.startswith("/*"):
            trong_khoi = "*/" not in s
            continue
        if s.startswith("//") or not s:
            continue
        ra.append(s)
    return ra


def test_cung_danh_sach_cum_voi_cong_va_dong_thi_hanh_goi_ham():
    dong = _dong_thi_hanh()
    khai = [d for d in dong if d.startswith("var DAU_TAI_KHOAN =")]
    assert len(khai) == 1, khai
    m = re.search(r"\]\)\(([^)]+)\)\(\?!", khai[0])
    assert m, "không tách được danh sách cụm khỏi mẫu của bộ lưu"
    cong = re.search(r"\\b\(([^)]+)\)\\b", PUQ._DAU_TAI_KHOAN.pattern).group(1)
    assert m.group(1).split("|") == cong.split("|"), "bộ lưu và cổng phải dò cùng danh sách cụm"
    assert "var taiKhoan = coDauTaiKhoan(c.innerText);" in dong, "dòng thi hành phải gọi hàm có ranh giới từ"
    assert not [d for d in dong if "/sign out|log ?out|my account/i" in d], "còn mẫu trần không ranh giới ở dòng thi hành"
    assert [d for d in dong if "module.exports" in d and "coDauTaiKhoan: coDauTaiKhoan" in d], "hàm phải xuất để test bằng node"


# ── Khoá «Purchase» của Cochrane (11/11/2026) ─────────────────────────────────────────────────────────────────────────
# Đo thật 10–11/11/2026: «Purchase» trần (cờ i) khớp «purchased» / «purchasers of healthcare» trong thân bài ⇒ 4 bài Cochrane
# đọc được (PMID 27103611, 30699470, 26068955, 25062018 — có đủ Background→Discussion và PDF) bị báo «khoá trong thân bài».

CAU_HINH = json.loads((TOOLS / "lan_chrome" / "cau_hinh.json").read_text(encoding="utf-8"))
LC = _nap("_lan_chrome_dau_tai_khoan_20261111", "lan_chrome.py")


def _danh_gia(t):
    ma = ("const m=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);"
          "process.stdin.on('end',()=>process.stdout.write(JSON.stringify(m.danhGia(JSON.parse(s)))))")
    r = subprocess.run([NODE, "-e", ma, str(BO_LUU)], input=json.dumps(t), capture_output=True, text=True,
                       encoding="utf-8", timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@pytest.mark.skipif(NODE is None, reason="máy không có node")
@pytest.mark.parametrize("cau, khoa", [
    ("Participants purchased their own medication.", False),          # PMID 30699470, 25062018
    ("Decisions by purchasers of healthcare were considered.", False),  # PMID 26068955, 27103611
    ("Purchase this review to read the full text.", True),
    ("Sign in to read the full review.", True),
])
def test_cochrane_purchase_chi_khop_tu_rieng(cau, khoa):
    url = "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000001.pub2/full"
    o = LC.dien_cau_hinh(CAU_HINH["nxb"]["cochrane_library"], url, "10.1002/14651858.CD000001.pub2",
                         CAU_HINH["dau_khong_quyen_url"])
    than = "Background Objectives Search methods Selection criteria Main results Discussion " * 200 + " " + cau
    kq = _danh_gia({"o": o, "href": url, "soVung": 1, "doDai": len(than), "vung": than, "trang": "", "deMuc": []})
    assert kq["ok"] is (not khoa), kq
