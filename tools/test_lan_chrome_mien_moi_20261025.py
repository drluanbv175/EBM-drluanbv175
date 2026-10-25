# -*- coding: utf-8 -*-
"""Cấu hình làn Chrome cho các miền đo thật 25/10/2026 (gói tuần W43) — `tools/lan_chrome/cau_hinh.json`.

Đo thật 25/10/2026 trên Chrome của bác sĩ (VPN bật, quyền qua Tufts):
- Ba tạp chí hội trên nền Elsevier (Resuscitation, NMCD, JHLT) cùng khuôn `elsevier_hoi`: linkinghub chuyển tới miền KHÔNG
  có www rồi về www.<miền>/article/<PII>/fulltext; lưu được PMID 42727699, 42476858, 42764189.
- AUA (www.auajournals.org, Journal of Urology): 5 bài đều «No Access» — <article> chỉ có Abstract + References
  (2.139–9.338 ký tự) ⇒ ngưỡng min phải chặn. Nhánh LƯU chưa kiểm được (chưa gặp bài đọc được).
- Lancet Diabetes Endocrinol không thuê bao: /fulltext về /abstract, <article> ~10.834 ký tự ⇒ min chặn.
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
    # Dữ liệu qua stdin: thân bài dài vượt giới hạn tham số dòng lệnh (giống test 18/10).
    ma = ("const m=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);"
          "process.stdin.on('end',()=>process.stdout.write(JSON.stringify(m.danhGia(JSON.parse(s)))))")
    r = subprocess.run([NODE, "-e", ma, str(BO_LUU)], input=json.dumps(t), capture_output=True, text=True,
                       encoding="utf-8", timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def _o(ten: str, url: str, doi: str) -> dict:
    return L.dien_cau_hinh(CAU_HINH["nxb"][ten], url, doi, CAU_HINH["dau_khong_quyen_url"])


def test_khuon_hop_le_va_mien_moi_tim_dung():
    assert L.kiem_cau_hinh(CAU_HINH) == []
    for host, ten in [("www.resuscitationjournal.com", "elsevier_hoi"), ("www.nmcd-journal.com", "elsevier_hoi"),
                      ("www.jhltonline.org", "elsevier_hoi"), ("www.auajournals.org", "aua")]:
        assert L.tim_nxb(host, CAU_HINH)[0] == ten, host


def test_aua_dien_pdf_theo_doi():
    o = _o("aua", "https://www.auajournals.org/doi/10.1097/JU.0000000000005098", "10.1097/JU.0000000000005098")
    assert o["pdf"] == "/doi/pdf/10.1097/JU.0000000000005098"


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_aua_bai_khong_quyen_bi_chan_boi_nguong_min():
    # Bài dài nhất trong 5 bài «No Access» đo 25/10 (PMID 42095468): <article> 9.338 ký tự = Abstract + References.
    url = "https://www.auajournals.org/doi/10.1097/JU.0000000000005099"
    o = _o("aua", url, "10.1097/JU.0000000000005099")
    kq = _danh_gia({"o": o, "href": url, "soVung": 1, "doDai": 9338, "vung": "Abstract Purpose: … REFERENCES",
                    "trang": "No Access Journal of Urology", "deMuc": ["Abstract", "REFERENCES"]})
    assert kq["ok"] is False and "ngắn" in kq["ly"]


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_elsevier_hoi_bai_perspectives_jhlt_doc_duoc_qua_buoc_1():
    # PMID 42764189 đo 25/10: <article> 14.504 ký tự, đọc được (quyền qua Tufts) — bước 1 phải cho qua.
    url = "https://www.jhltonline.org/article/S1053-2498(26)01947-9/fulltext"
    o = _o("elsevier_hoi", url, "10.1016/j.healun.2026.05.035")
    kq = _danh_gia({"o": o, "href": url, "soVung": 1, "doDai": 14504, "vung": "Key takeaways Conclusion",
                    "trang": "Subscribe Key takeaways Conclusion", "deMuc": ["Key takeaways", "Conclusion"]})
    assert kq["ok"] is True, kq


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_lancet_tap_chi_khong_thue_bao_bi_chan():
    # PMID 42628555 đo 25/10: /fulltext về /abstract, <article> 10.834 ký tự có đề mục «Get full text access».
    url = "https://www.thelancet.com/journals/landia/article/PIIS2213-8587(26)00160-9/abstract"
    o = _o("lancet", url, "10.1016/S2213-8587(26)00160-9")
    kq = _danh_gia({"o": o, "href": url, "soVung": 1, "doDai": 10834, "vung": "Summary Get full text access References",
                    "trang": "Summary Get full text access", "deMuc": ["Summary", "Get full text access", "References"]})
    assert kq["ok"] is False
