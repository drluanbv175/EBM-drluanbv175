# -*- coding: utf-8 -*-
"""Cấu hình làn Chrome cho NIHR Journals Library — `tools/lan_chrome/cau_hinh.json`, đo thật 10/11/2026.

Đo trên PMID 40824117 (synopsis HTA 2025, DOI 10.3310/KGFA8471) và 42661570 (chuyên khảo HTA, DOI 10.3310/GJJS3014):
- Toàn văn nằm trong tab ẩn #full-report (82.945 / ~920.000 ký tự), tóm tắt ở #abstract — chọn `article` chỉ được ~5.000 ký tự
  vì innerText bỏ phần đang ẩn của trang hiển thị, còn khi chọn thẳng hai vùng thì đọc đủ.
- «Publication PDF» nằm ở njl-admin.nihr.ac.uk (khác nguồn) ⇒ fetch trong trang lỗi «Failed to fetch» (CORS) ⇒ KHÔNG đặt `pdf`,
  bộ lưu chỉ lưu HTML rồi `in_pdf_toan_van_kho.py` in BANIN.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import lan_chrome as L  # noqa: E402

BO_LUU = REPO / "tools" / "lan_chrome" / "bo_luu.js"
CAU_HINH = json.loads((REPO / "tools" / "lan_chrome" / "cau_hinh.json").read_text(encoding="utf-8"))
NODE = shutil.which("node")
URL = "https://www.journalslibrary.nihr.ac.uk/hta/published-articles/KGFA8471"
DOI = "10.3310/KGFA8471"


def _danh_gia(t):
    ma = ("const m=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);"
          "process.stdin.on('end',()=>process.stdout.write(JSON.stringify(m.danhGia(JSON.parse(s)))))")
    r = subprocess.run([NODE, "-e", ma, str(BO_LUU)], input=json.dumps(t), capture_output=True, text=True,
                       encoding="utf-8", timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_nihr_khuon_hop_le_va_tim_dung_mien():
    assert L.kiem_cau_hinh(CAU_HINH) == []
    assert L.tim_nxb("www.journalslibrary.nihr.ac.uk", CAU_HINH)[0] == "nihr"
    # Máy chủ PDF khác nguồn KHÔNG phải trang bài — không được khớp cấu hình.
    assert L.tim_nxb("njl-admin.nihr.ac.uk", CAU_HINH)[0] is None


def test_nihr_chon_tab_bao_cao_day_du_va_khong_tai_pdf_khac_nguon():
    o = L.dien_cau_hinh(CAU_HINH["nxb"]["nihr"], URL, DOI, CAU_HINH["dau_khong_quyen_url"])
    vung = [s.strip() for s in o["chon"].split(",")]
    assert "#full-report" in vung and "#abstract" in vung, "toàn văn ở tab ẩn #full-report"
    assert "article" not in vung
    assert not o.get("pdf") and not o.get("pdf2"), "PDF ở njl-admin.nihr.ac.uk — fetch khác nguồn bị CORS chặn"


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_nihr_bao_cao_day_du_qua_ban_chi_tom_tat_bi_chan():
    o = L.dien_cau_hinh(CAU_HINH["nxb"]["nihr"], URL, DOI, CAU_HINH["dau_khong_quyen_url"])
    than = "Introduction Methods Results Discussion " * 500
    assert _danh_gia({"o": o, "href": URL, "soVung": 2, "doDai": len(than), "vung": than, "trang": "",
                      "deMuc": []})["ok"] is True
    # Như bản PMC (876 từ): chỉ có tóm tắt ⇒ min chặn.
    tom_tat = "Background Methods Results Conclusions " * 100
    kq = _danh_gia({"o": o, "href": URL, "soVung": 1, "doDai": len(tom_tat), "vung": tom_tat, "trang": "", "deMuc": []})
    assert kq["ok"] is False and "ngắn" in kq["ly"]
