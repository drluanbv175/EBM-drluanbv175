# -*- coding: utf-8 -*-
"""Cấu hình NXB đã kiểm 17–18/10/2026 cho làn Chrome — `tools/lan_chrome/cau_hinh.json`.

Đo thật 18/10/2026:
- LWW/Ovid không quyền ⇒ chuyển sang www.ovid.com/jnls/<tạp chí>/abstract/…?redirectionsource=fulltextview (7 bài) — dấu URL
  này phải làm bộ lưu từ chối, kể cả khi trang abstract dài.
- SAGE: «Access options» là đầu mục khung phụ #core-collateral-fulltext-options nằm TRONG <article> cả khi bài đọc được
  (PMID 27521067, 316.673 ký tự thân bài) ⇒ vùng phải là #abstracts,#bodymatter; bài khoá (PMID 40884091) có #bodymatter
  ~100 ký tự ⇒ ngưỡng min chặn.
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


def _danh_gia(t):
    # Dữ liệu qua stdin: thân bài dài vượt giới hạn tham số dòng lệnh (Linux E2BIG ~128 KB/đối số, Windows 32 K — CI 18/10).
    ma = ("const m=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);"
          "process.stdin.on('end',()=>process.stdout.write(JSON.stringify(m.danhGia(JSON.parse(s)))))")
    r = subprocess.run([NODE, "-e", ma, str(BO_LUU)], input=json.dumps(t), capture_output=True, text=True,
                       encoding="utf-8", timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_khuon_hop_le_va_mien_moi_tim_dung():
    assert L.kiem_cau_hinh(CAU_HINH) == []
    for host, ten in [("journals.lww.com", "lww"), ("www.ovid.com", "lww"), ("gut.bmj.com", "bmj"),
                      ("pmc.ncbi.nlm.nih.gov", "pmc"), ("journal.chestnet.org", "elsevier_hoi"),
                      ("www.gastrojournal.org", "elsevier_hoi"), ("europepmc.org", "europepmc"),
                      ("www.thelancet.com", "lancet"), ("www.thieme-connect.de", "thieme")]:
        assert L.tim_nxb(host, CAU_HINH)[0] == ten, host


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_lww_chuyen_ve_abstract_la_khong_quyen():
    o = L.dien_cau_hinh(CAU_HINH["nxb"]["lww"], "https://journals.lww.com/x", "10.1097/HEP.0000000000001584",
                        CAU_HINH["dau_khong_quyen_url"])
    # Đo thật 18/10 (PMID 31241597): ở lại journals.lww.com nên mẫu «ovid.com/jnls/…/abstract/» cũ KHÔNG bắt được.
    href = ("https://journals.lww.com/greenjournal/abstract/2019/07000/migraine_and_other_headache_disorders.44.aspx"
            "?redirectionsource=fulltextview")
    kq = _danh_gia({"o": o, "href": href, "khongQuyenUrl": CAU_HINH["dau_khong_quyen_url"], "soVung": 1,
                    "doDai": 20000, "vung": "x" * 20000, "trang": "", "deMuc": []})
    assert kq["ok"] is False and "redirectionsource" in kq["ly"]


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_sage_khung_phu_access_options_khong_chan_bai_doc_duoc_bai_khoa_van_bi_chan():
    o = L.dien_cau_hinh(CAU_HINH["nxb"]["sage"], "https://journals.sagepub.com/doi/10.1089/thy.2016.0229",
                        "10.1089/thy.2016.0229", CAU_HINH["dau_khong_quyen_url"])
    assert "article" not in [s.strip() for s in o["chon"].split(",")], "khung «Access options» nằm trong <article>"
    than = "Introduction Methods Results " * 500  # 14.500 ký tự > min 12.000
    doc_duoc = _danh_gia({"o": o, "href": "https://journals.sagepub.com/doi/10.1089/thy.2016.0229", "soVung": 2,
                          "doDai": len(than), "vung": than, "trang": "Access options " + than[:200], "deMuc": []})
    assert doc_duoc["ok"] is True, doc_duoc
    khoa = _danh_gia({"o": o, "href": "https://journals.sagepub.com/doi/10.1177/17474930251377174", "soVung": 2,
                      "doDai": 99, "vung": "x" * 99, "trang": "Get full access", "deMuc": []})
    assert khoa["ok"] is False
