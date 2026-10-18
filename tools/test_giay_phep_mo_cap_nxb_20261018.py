# -*- coding: utf-8 -*-
"""Giấy phép mở khai ở CẤP NXB cho tầng 2 Unpaywall (18/10/2026 — bác sĩ: «Sửa cổng để chấp nhận giấy phép CC khai ở cấp NXB
khi đã đọc trang điều khoản»).

Ca thật: PMID 33798049 (*Heart Surgery Forum* 2021, DOI 10.1532/hsf.3547) — Unpaywall có bản OA nhưng KHÔNG ghi giấy phép ⇒ cổng
trả «chua_kiem». Trang Copyright & License của IMR Press khai CC BY 4.0; trang bài ghi số HSF cũ do NXB trước đăng theo CC BY-NC,
IMR Press lưu hộ. Tiền tố 10.1532 trên Crossref là của Carden Jennings Publishing ⇒ khớp theo MIỀN của bản OA, không theo DOI.

Khoá:
  • bản OA trên imrpress.com (cả miền con storage.) không ghi giấy phép ⇒ ĐƯỢC lưu, lý do ghi «cấp NXB»;
  • cùng DOI nhưng bản ở kho khác (Europe PMC) hoặc miền giả «imrpress.com.<khác>» ⇒ KHÔNG;
  • NXB «cấm» không bao giờ hưởng nhánh này (xét sau nhánh «cấm»);
  • mục trong bảng phải có nguồn https + ngày đọc + trích, mọi giấy phép liệt kê đều là giấy phép mở; DIEU_KHOAN_NXB vẫn chỉ «cam»
    và không chứa NXB của bảng mới (không miễn khai `dieu_khoan` ở `--nap`);
  • doctrine §2septies dạy agent bảng mới.
Ngoại tuyến hoàn toàn.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


g = _nap("_gom_cc_nxb_20261018", "gom_toan_van_dashboard.py")
D = _nap("_dtv_cc_nxb_20261018", "doc_toan_van_co_nguoi.py")


@pytest.mark.parametrize("url", ["https://storage.imrpress.com/imr/journal/HSF/article/518393/1752874295424.pdf",
                                 "https://www.imrpress.com/journal/HSF/24/2/10.1532/hsf.3547"])
def test_ban_oa_tren_mien_nxb_khong_ghi_giay_phep_duoc_luu(url):
    duoc, ly = g.quyet_dinh_unpaywall("10.1532/hsf.3547", url, None, dtv=D)
    assert duoc, ly
    assert "cấp NXB IMR Press" in ly and "cc-by-nc" in ly


@pytest.mark.parametrize("url", ["https://europepmc.org/article/MED/33798049",
                                 "https://imrpress.com.vi-du.org/hsf.pdf",
                                 "https://fakeimrpress.com/hsf.pdf",
                                 ""])
def test_ban_o_kho_khac_hoac_mien_gia_khong_duoc_luu(url):
    duoc, ly = g.quyet_dinh_unpaywall("10.1532/hsf.3547", url, None, dtv=D)
    assert not duoc and ly.startswith("chua_kiem"), ly


def test_nxb_cam_khong_huong_nhanh_cap_nxb(monkeypatch):
    # Giả lập một NXB «cấm» có bản nằm trên miền trùng bảng mới: nhánh «cấm» phải thắng.
    monkeypatch.setitem(D.DIEU_KHOAN_NXB, "NXB cấm thử", {"ket_luan": "cam", "doi": ("10.99998/",), "mien": ()})
    duoc, ly = g.quyet_dinh_unpaywall("10.99998/x", "https://storage.imrpress.com/x.pdf", None, dtv=D)
    assert not duoc and ly.startswith("cam_")


def test_muc_khai_giay_phep_khong_mo_thi_khong_duoc_luu(monkeypatch):
    # Một mục khai lẫn giấy phép đóng ⇒ cả mục không được dùng (mọi giấy phép phải mở, không chỉ một).
    monkeypatch.setitem(D.GIAY_PHEP_MO_CAP_NXB, "NXB thử", {"mien": ("vi-du-nxb.org",), "giay_phep": ("cc-by", "all-rights-reserved"),
                                                          "nguon": "https://vi-du-nxb.org/license", "doc_luc": "2026-10-18",
                                                          "trich": "thử", "ghi_chu": ""})
    duoc, ly = g.quyet_dinh_unpaywall("10.99997/x", "https://vi-du-nxb.org/x.pdf", None, dtv=D)
    assert not duoc and ly.startswith("chua_kiem"), ly


def test_giay_phep_ghi_tren_ban_van_thang_truoc():
    duoc, ly = g.quyet_dinh_unpaywall("10.1532/hsf.3547", "https://europepmc.org/x", "cc-by-nc", dtv=D)
    assert duoc and ly.startswith("giấy phép mở (cc-by-nc)")


def test_muc_bang_cap_nxb_hop_le_va_tach_khoi_dieu_khoan_cam():
    assert D.GIAY_PHEP_MO_CAP_NXB, "bảng rỗng"
    for ten, m in D.GIAY_PHEP_MO_CAP_NXB.items():
        assert re.match(r"https://", m["nguon"]), ten
        assert date.fromisoformat(m["doc_luc"]) <= date.today(), ten
        assert 0 < len(m["trich"].split()) <= 15, f"{ten}: trích ≤ 15 từ"
        assert m["mien"] and all("/" not in x and "." in x for x in m["mien"]), ten
        assert m["giay_phep"] and all(g.la_giay_phep_mo(x) for x in m["giay_phep"]), f"{ten}: mọi giấy phép phải mở"
        assert ten not in D.DIEU_KHOAN_NXB, f"{ten} không được nằm trong DIEU_KHOAN_NXB (bảng chỉ «cấm»)"
    assert all(d["ket_luan"] == "cam" for d in D.DIEU_KHOAN_NXB.values())


def test_doctrine_day_agent_bang_cap_nxb():
    vb = (REPO / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md").read_text(encoding="utf-8")
    i = vb.find("## 2septies. ")
    muc = vb[i:vb.find("\n## ", i + 5)]
    assert "`GIAY_PHEP_MO_CAP_NXB`" in muc and "MIỀN CỦA CHÍNH NXB" in muc
    for ten in D.GIAY_PHEP_MO_CAP_NXB:
        assert ten in muc, ten
