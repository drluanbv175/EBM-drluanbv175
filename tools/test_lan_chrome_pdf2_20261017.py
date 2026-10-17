# -*- coding: utf-8 -*-
"""Bước PDF của bộ lưu làn Chrome chọn LIÊN KẾT THẬT trên trang, không tự dựng URL (17/10/2026) — `tools/lan_chrome/bo_luu.js`.

Đo thật 17/10/2026 (PMID 24331794, ScienceDirect): bản PR #194 dựng `https://www.sciencedirect.com/pii/<PII>/pdfft` từ khuôn cấu hình
— không phải liên kết NXB phát ra (liên kết thật: /science/article/pii/<PII>/pdfft?md5=…&pid=…). Cách đã kiểm 14–15/10 là tìm
liên kết có chứa đoạn `/pii/<PII>/pdfft` trên trang; phải chọn ĐÚNG PII (14/10 liên kết /pdfft đầu tiên là của tài liệu tham khảo).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BO_LUU = REPO / "tools" / "lan_chrome" / "bo_luu.js"
NODE = shutil.which("node")


def _chon(o, hrefs, meta=""):
    ma = ("const m=require(process.argv[1]);const a=JSON.parse(process.argv[2]);"
          "process.stdout.write(JSON.stringify(m.chonPdf2(a[0],a[1],a[2])))")
    r = subprocess.run([NODE, "-e", ma, str(BO_LUU), json.dumps([o, hrefs, meta])], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


THAT = "https://www.sciencedirect.com/science/article/pii/S1474442213702369/pdfft?md5=abc&pid=1-s2.0-S1474442213702369-main.pdf"
THAM_KHAO = "https://www.sciencedirect.com/science/article/pii/S0140673600000001/pdfft?md5=zzz&pid=1-s2.0-S0140673600000001-main.pdf"


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_chon_dung_lien_ket_that_cua_dung_pii():
    hrefs = ["https://www.sciencedirect.com/", THAM_KHAO, THAT]
    assert _chon({"pdf2": "/pii/S1474442213702369/pdfft"}, hrefs) == THAT, "liên kết tham khảo đứng trước vẫn không được chọn"


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_khong_thay_lien_ket_thi_rong_khong_tu_dung_url():
    assert _chon({"pdf2": "/pii/S1474442213702369/pdfft"}, [THAM_KHAO]) == ""
    assert _chon({}, [THAT]) == ""


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_meta_dung_meta():
    assert _chon({"pdf2": "meta"}, [THAT], "https://academic.oup.com/x.pdf") == "https://academic.oup.com/x.pdf"
    assert _chon({"pdf2": "meta"}, [THAT], "") == ""


def test_bo_luu_khong_con_tu_dung_url_pdf2():
    js = BO_LUU.read_text(encoding="utf-8")
    assert "new URL(o.pdf2" not in js, "URL tự dựng không phải liên kết NXB phát ra"
    assert "chonPdf2(o, Array.prototype.map.call(document.querySelectorAll('a[href]')" in js
