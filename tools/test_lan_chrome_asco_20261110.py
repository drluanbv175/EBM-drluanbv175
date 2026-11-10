# -*- coding: utf-8 -*-
"""Cấu hình làn Chrome cho ASCO (ascopubs.org) — `tools/lan_chrome/cau_hinh.json`, đo thật 10/11/2026.

Đo trên PMID 34724392 (JCO, ASCO guideline 2021, DOI 10.1200/JCO.21.01440):
- Thân bài nằm ở #abstracts (1.867 ký tự) + #bodymatter (108.023 ký tự); bộ lưu dựng tệp ok:true với vùng 109.891 ký tự.
- /doi/pdf/<doi> trả trang XEM PDF dạng HTML (~164 KB, bắt đầu bằng xuống dòng, không phải %PDF-); /doi/pdfdirect/<doi> trả PDF
  thật (%PDF-, ~610 KB) — giống Neurology. Cấu hình phải trỏ pdfdirect, nếu không bộ lưu bỏ PDF và chỉ giữ HTML.
- Thanh trên của trang có chữ «Subscribe» ⇒ KHÔNG được đặt khoaTrang (sẽ chặn nhầm mọi bài đọc được).
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
URL = "https://ascopubs.org/doi/10.1200/JCO.21.01440"
DOI = "10.1200/JCO.21.01440"


def _danh_gia(t):
    # Dữ liệu qua stdin như test cấu hình 18/10 (thân bài dài vượt giới hạn tham số dòng lệnh trên CI).
    ma = ("const m=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);"
          "process.stdin.on('end',()=>process.stdout.write(JSON.stringify(m.danhGia(JSON.parse(s)))))")
    r = subprocess.run([NODE, "-e", ma, str(BO_LUU)], input=json.dumps(t), capture_output=True, text=True,
                       encoding="utf-8", timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_asco_khuon_hop_le_va_tim_dung_mien():
    assert L.kiem_cau_hinh(CAU_HINH) == []
    assert L.tim_nxb("ascopubs.org", CAU_HINH)[0] == "asco"
    # Không nuốt nhầm miền khác có chữ «ascopubs».
    assert L.tim_nxb("notascopubs.org", CAU_HINH)[0] is None


def test_asco_pdf_tro_pdfdirect_khong_tro_trang_xem_pdf():
    o = L.dien_cau_hinh(CAU_HINH["nxb"]["asco"], URL, DOI, CAU_HINH["dau_khong_quyen_url"])
    assert o["pdf"] == "/doi/pdfdirect/10.1200/JCO.21.01440"
    assert "/doi/pdf/" not in o["pdf"], "/doi/pdf/ của ASCO là trang XEM PDF dạng HTML"
    assert "khoaTrang" not in o, "thanh trên có chữ Subscribe — khoaTrang sẽ chặn nhầm bài đọc được"
    assert [s.strip() for s in o["chon"].split(",")] == ["#abstracts", "#bodymatter"]


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_asco_bai_doc_duoc_qua_bai_than_ngan_bi_chan():
    o = L.dien_cau_hinh(CAU_HINH["nxb"]["asco"], URL, DOI, CAU_HINH["dau_khong_quyen_url"])
    than = "Introduction Methods Results Recommendations " * 400  # ~18.000 ký tự > min 12.000
    doc_duoc = _danh_gia({"o": o, "href": URL, "soVung": 2, "doDai": len(than), "vung": than,
                          "trang": "Subscribe " + than[:200], "deMuc": []})
    assert doc_duoc["ok"] is True, doc_duoc
    # Bài khoá trên nền Atypon: #bodymatter gần như rỗng ⇒ min chặn, không tạo nút tải.
    khoa = _danh_gia({"o": o, "href": "https://ascopubs.org/doi/10.1200/JCO.99.99999", "soVung": 2,
                      "doDai": 1500, "vung": "Abstract " * 150, "trang": "Subscribe Get Access", "deMuc": []})
    assert khoa["ok"] is False and "ngắn" in khoa["ly"]
    # Chuỗi khoá chung của Atypon trong vùng thân bài vẫn chặn kể cả khi thân bài đủ dài.
    khoa2 = _danh_gia({"o": o, "href": URL, "soVung": 2, "doDai": len(than) + 30,
                       "vung": than + " Purchase this article", "trang": "", "deMuc": []})
    assert khoa2["ok"] is False and "khoá" in khoa2["ly"]
