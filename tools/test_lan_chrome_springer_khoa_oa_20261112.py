"""Khoá trang «Access this article» của Springer không được khớp câu giấy phép Open Access (12/11/2026).

Sự cố thật 12/11/2026 (lượt 20, lô 3 làn Chrome): bài OA PMID 40838698 (J Clin Sleep Med, DOI 10.5664/jcsm.11864, nay đăng trên
link.springer.com) có câu «Open Access This article is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives
4.0…». Mẫu cũ `Access this article|Buy article PDF|Buy Now` (cờ i, không ranh giới) khớp «Access This article» nằm TRONG câu giấy
phép ⇒ bộ lưu báo «khoá trên trang» dù thân bài dài 68.629 ký tự; ghi «không truy cập» sẽ đánh dấu nhầm bài OA trong 90 ngày.
Khoá: câu giấy phép OA không còn khoá; tường phí thật của Springer («Access this article · Log in via an institution»,
PMID 42289039) và nút mua vẫn khoá. Phán quyết chạy bằng CHÍNH hàm `danhGia` của `tools/lan_chrome/bo_luu.js` qua node.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
BO_LUU = TOOLS / "lan_chrome" / "bo_luu.js"
NODE = shutil.which("node")
CAU_HINH = json.loads((TOOLS / "lan_chrome" / "cau_hinh.json").read_text(encoding="utf-8"))


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


LC = _nap("_lan_chrome_springer_khoa_oa_20261112", "lan_chrome.py")


def _danh_gia(t):
    """Gọi `danhGia` thuần của bo_luu.js (không DOM) — cùng mã chạy trên trang thật."""
    ma = ("const m=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);"
          "process.stdin.on('end',()=>process.stdout.write(JSON.stringify(m.danhGia(JSON.parse(s)))))")
    r = subprocess.run([NODE, "-e", ma, str(BO_LUU)], input=json.dumps(t), capture_output=True, text=True,
                       encoding="utf-8", timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@pytest.mark.skipif(NODE is None, reason="máy không có node")
@pytest.mark.parametrize("cau, khoa", [
    # PMID 40838698 — sự cố gốc: câu giấy phép CC của bài OA
    ("Open Access This article is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 "
     "International License.", False),
    ("This article is now published under an Open Access license. open access this article is licensed under CC BY.", False),
    # tường phí thật (PMID 42289039) và nút mua — vẫn phải khoá
    ("Access this article\nLog in via an institution\nSubscribe and save", True),
    ("Buy article PDF 39,95 €", True),
    ("Buy Now", True),
])
def test_springer_khoa_trang_khong_khop_cau_giay_phep_oa(cau, khoa):
    url = "https://link.springer.com/article/10.5664/jcsm.11864"
    o = LC.dien_cau_hinh(CAU_HINH["nxb"]["springer_link"], url, "10.5664/jcsm.11864", CAU_HINH["dau_khong_quyen_url"])
    than = "Introduction Methods Results Discussion " * 400
    kq = _danh_gia({"o": o, "href": url, "soVung": 1, "doDai": len(than), "vung": than,
                    "trang": "Sleep Medicine " + cau + " References", "deMuc": []})
    assert kq["ok"] is (not khoa), kq


def test_mau_springer_co_lookbehind_open_tren_dong_cau_hinh():
    """Khoá đúng DÒNG cấu hình đang dùng (không khớp cả tệp): mẫu Springer phải loại «Open » đứng trước."""
    assert CAU_HINH["nxb"]["springer_link"]["khoaTrang"].startswith("(?<!Open )")
