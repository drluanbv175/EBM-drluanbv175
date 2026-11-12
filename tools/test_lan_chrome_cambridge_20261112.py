#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cambridge University Press (Cambridge Core) vào làn Chrome lưu bản sao — bác sĩ ra lệnh trong chat 12/11/2026, nguyên văn:
«Thêm Cambridge vào làn Chrome».

Căn cứ: Terms of use của Cambridge Core («Last Updated: March 2025», mục «Machine Analysis (Text and Data Mining)», đọc trên Chrome
của bác sĩ 12/11/2026) cho phép tải, trích, lưu, đánh chỉ mục nội dung truy cập hợp pháp để TDM phi thương mại — kèm liên kết bài
gốc, xoá bản lưu khi dự án kết thúc, NXB có quyền giới hạn việc tải. Cambridge KHÔNG phải «cấm» ⇒ bảng RIÊNG `TDM_CHO_PHEP_LUU`.

Khoá:
  • nhận diện NXB theo tiền tố DOI (10.1017/ CUP · 10.1192/ BJP của RCPsych trên Cambridge Core) và theo miền cambridge.org — miền
    giả dạng hậu tố không khớp; `nxb_cua` (bảng «cấm», cổng `--nap`) vẫn trả «chưa kiểm»;
  • mục đủ trường, trích nguyên văn ≤ 15 từ, đủ bốn điều kiện của điều khoản, ghi lời bác sĩ + ngày;
  • Cambridge KHÔNG nằm trong DIEU_KHOAN_NXB, De Gruyter vẫn ngoài MỌI bảng;
  • phiên: `nxb_duoc_luu` có Cambridge mà không cần uỷ quyền; `kiem` trả 0 cho trang Cambridge, 3 cho miền lạ, 3 cho bản mang DOI
    Cambridge ở miền khác (kể cả miền nền tảng của cấu hình làn như PMC); trần/nhịp/miền cấm AI riêng giữ nguyên;
  • `hang-cho` hiện «✓» ở cột phạm vi cho www.cambridge.org;
  • cấu hình DOM (đo thật 12/11/2026 trên 4 bài trong hàng chờ): khuôn hợp lệ, bài có quyền qua, bài không quyền bị chặn bởi TỪNG
    lớp khoá; khoá «Article purchase» là cụm từ riêng (bài học PR #320 — «Purchase» trần khớp «purchased»);
  • doctrine §2septies nêu tên + tiền tố + tên bảng, bắt được khi mất tiền tố hoặc tên bảng.
Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
DOCTRINE = TOOLS.parent / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md"
BO_LUU = TOOLS / "lan_chrome" / "bo_luu.js"
NODE = shutil.which("node")


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


DTV = _nap("_dtv_cambridge_20261112", "doc_toan_van_co_nguoi.py")
P = _nap("_puq_cambridge_20261112", "phien_uy_quyen_chrome.py")
L = _nap("_lan_chrome_cambridge_20261112", "lan_chrome.py")
CAU_HINH = L.doc_cau_hinh()

CUP = "Cambridge University Press"
T0 = datetime(2026, 11, 12, 10, 0, 0, tzinfo=timezone(timedelta(hours=7)))
LOI = "uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay"
# URL thật đo 12/11/2026: trang /core/product/identifier/… chuyển về /article/<slug>/<mã> khi CÓ quyền, /article/abs/… khi KHÔNG.
URL_ID = "https://www.cambridge.org/core/product/identifier/S0007125026106515/type/journal_article"
URL_CO = ("https://www.cambridge.org/core/journals/the-british-journal-of-psychiatry/article/effectiveness-and-acceptability-of-"
          "different-psychotherapies-for-obsessivecompulsive-disorder-network-metaanalysis/A3ABA47238BCD8E8CEACE27B3E6C3490")
URL_KHONG = ("https://www.cambridge.org/core/journals/psychological-medicine/article/abs/suicide-rates-among-people-with-serious-"
             "mental-illness-a-systematic-review-and-metaanalysis/DD5137B66B5395509850E884131253E1")


# ───────────────────────── nhận diện NXB ─────────────────────────

@pytest.mark.parametrize("doi, url", [
    ("10.1192/bjp.2026.10651", ""), ("10.1017/S0033291721001549", ""), ("10.1017/s0033291726105881", ""),
    ("", URL_ID), ("", URL_KHONG), ("", "https://cambridge.org/core/journals/x/article/y/Z")])
def test_nhan_dien_doi_va_mien_cambridge(doi, url) -> None:
    ten, d = DTV.nxb_tdm_cho_phep(doi=doi, url=url)
    assert ten == CUP and d is DTV.TDM_CHO_PHEP_LUU[CUP], (doi, url)
    # Bảng «cấm» (và cổng `--nap` dựa trên nó) KHÔNG đổi: Cambridge vẫn là «chưa kiểm» ở đó.
    assert DTV.nxb_cua(doi=doi, url=url) == (None, None), (doi, url)


@pytest.mark.parametrize("url", ["https://www.cambridge.org.vi-du.org/core/x", "https://notcambridge.org/x",
                                 "https://archive.lstmed.ac.uk/14364/1/x.docx"])
def test_mien_gia_khong_khop_cambridge(url) -> None:
    assert DTV.nxb_tdm_cho_phep(url=url) == (None, None), url


def test_muc_cambridge_du_truong_va_trich_ngan() -> None:
    d = DTV.TDM_CHO_PHEP_LUU[CUP]
    assert d["doi"] == ("10.1017/", "10.1192/") and d["mien"] == ("cambridge.org",)
    assert d["nguon"] == "https://www.cambridge.org/core/legal-notices/terms" and d["doc_luc"] == "2026-11-12"
    assert 0 < len(d["trich"].split()) <= 15, "trích nguyên văn tối đa 15 từ"
    assert "store and index Content" in d["trich"] and "…" not in d["trich"], "trích phải là một đoạn NGUYÊN VĂN liền"
    dk = " ".join(d["dieu_kien"]).lower()
    for cum in ("phi thương mại", "liên kết", "xoá bản lưu", "giới hạn", "hợp pháp"):
        assert cum in dk, f"thiếu điều kiện «{cum}» của điều khoản"
    assert "«Thêm Cambridge vào làn Chrome»" in d["quyet_dinh"] and "12/11/2026" in d["quyet_dinh"]
    assert "ket_luan" not in d, "bảng TDM không mang «ket_luan» — Cambridge KHÔNG phải «cấm»"


def test_cambridge_ngoai_bang_cam_de_gruyter_ngoai_moi_bang() -> None:
    assert CUP not in DTV.DIEU_KHOAN_NXB and CUP not in DTV.GIAY_PHEP_MO_CAP_NXB
    assert all(d["ket_luan"] == "cam" for d in DTV.DIEU_KHOAN_NXB.values()), "DIEU_KHOAN_NXB vẫn chỉ nhận «cấm»"
    for doi, url in (("10.1515/dx-2024-0113", ""), ("", "https://www.degruyter.com/document/doi/10.1515/dx-2024-0113/html")):
        assert DTV.nxb_cua(doi=doi, url=url) == (None, None)
        assert DTV.nxb_tdm_cho_phep(doi=doi, url=url) == (None, None)
        assert DTV.giay_phep_mo_cap_nxb(url) == (None, None)
    for bang in (DTV.DIEU_KHOAN_NXB, DTV.GIAY_PHEP_MO_CAP_NXB, DTV.TDM_CHO_PHEP_LUU):
        assert not any("Gruyter" in ten for ten in bang)
    # Bảng TDM không chồng bảng «cấm»: một tiền tố/miền không được thuộc cả hai.
    cam_doi = {t for d in DTV.DIEU_KHOAN_NXB.values() for t in d["doi"]}
    cam_mien = {m for d in DTV.DIEU_KHOAN_NXB.values() for m in d["mien"]}
    for d in DTV.TDM_CHO_PHEP_LUU.values():
        assert not set(d["doi"]) & cam_doi and not set(d["mien"]) & cam_mien


# ───────────────────────── phiên lưu bản sao ─────────────────────────

@pytest.fixture()
def so(tmp_path, monkeypatch):
    """Sổ phiên tạm + kho quyết định uỷ quyền RỖNG (không bác sĩ nào uỷ quyền gì) ⇒ chỉ Cambridge thuộc phạm vi."""
    monkeypatch.setattr(DTV, "DASH", tmp_path)
    return tmp_path / "state" / "phien.json"


def test_nxb_duoc_luu_co_cambridge_khi_co_phien_khong_can_uy_quyen(so) -> None:
    assert P.nxb_duoc_luu(DTV, T0.date()) == [CUP], "chưa có uỷ quyền nào ⇒ chỉ còn NXB tự cho phép TDM"
    ma, tb = P.mo(LOI, bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 0 and CUP in tb, tb
    assert CUP in P.doc_phien(so)["nxb"]
    assert P.kiem("42112625", URL_ID, "10.1192/bjp.2026.10651", bay_gio=T0, tep=so, dtv=DTV)[0] == 0


def test_khong_bao_gio_van_loai_ca_khi_nam_trong_bang_tdm(so, monkeypatch) -> None:
    monkeypatch.setitem(DTV.TDM_CHO_PHEP_LUU, "EBSCO (DynaMed)", {"doi": (), "mien": ("dynamed.com",)})
    assert "EBSCO (DynaMed)" not in P.nxb_duoc_luu(DTV, T0.date())


@pytest.mark.parametrize("pmid, url, doi", [
    ("42112625", URL_ID, "10.1192/bjp.2026.10651"), ("42112625", URL_CO, "10.1192/bjp.2026.10651"),
    ("33952359", URL_ID.replace("S0007125026106515", "S0033291721001549"), ""),
    ("42765379", "https://www.cambridge.org/core/product/identifier/S0033291726105881/type/journal_article", "")])
def test_kiem_tra_0_cho_trang_cambridge(so, pmid, url, doi) -> None:
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    ma, tb = P.kiem(pmid, url, doi, bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 0 and CUP in tb and "TDM phi thương mại" in tb and "liên kết bài gốc" in tb, tb


@pytest.mark.parametrize("url, doi, can", [
    ("https://www.vi-du-nxb-la.org/article/1", "", "chưa kiểm điều khoản"),
    ("https://www.degruyter.com/document/doi/10.1515/dx-2024-0113/html", "10.1515/dx-2024-0113", "chưa kiểm điều khoản"),
    # DOI Cambridge nhưng TRANG ở nơi khác: quyền lưu để TDM chỉ áp cho nội dung trên nền tảng của chính NXB.
    ("https://archive.lstmed.ac.uk/14364/1/Sustained%20benefit_DW.docx", "10.1017/S003329172000046X", "KHÔNG thuộc miền của"),
    ("https://pmc.ncbi.nlm.nih.gov/articles/PMC0000001/", "10.1192/bjp.2021.1", "KHÔNG thuộc miền của"),
    ("https://www.cambridge.org.vi-du.org/core/x", "10.1017/S0033291721001549", "KHÔNG thuộc miền của")])
def test_kiem_tra_3_cho_mien_la_va_ban_ngoai_mien(so, url, doi, can) -> None:
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    ma, tb = P.kiem("41000001", url, doi, bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 3 and can in tb, tb


def test_luat_cu_giu_nguyen_khong_phien_nhip_tran_mien_cam_ai(so, monkeypatch) -> None:
    assert P.kiem("42112625", URL_ID, bay_gio=T0, tep=so, dtv=DTV)[0] == 3, "không có phiên ⇒ từ chối"
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    d = json.loads(so.read_text(encoding="utf-8"))
    d["lich_su"] = [{"luc": (T0 + timedelta(minutes=i)).isoformat(), "pmid": str(40000000 + i),
                     "url": URL_ID, "mien": "www.cambridge.org", "tep": f"PMID-{40000000 + i}_CHR.html"} for i in range(19)]
    so.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    cuoi = T0 + timedelta(minutes=18)
    ma, tb = P.kiem("42112625", URL_ID, bay_gio=cuoi + timedelta(seconds=30), tep=so, dtv=DTV)
    assert ma == 3 and "chưa đủ nhịp" in tb, tb
    assert P.kiem("42112625", URL_ID, bay_gio=cuoi + timedelta(seconds=61), tep=so, dtv=DTV)[0] == 0
    d["lich_su"].append({"luc": (cuoi + timedelta(minutes=1)).isoformat(), "pmid": "42112625", "url": URL_ID,
                         "mien": "www.cambridge.org", "tep": "PMID-42112625_CHR.html"})
    so.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    ma, tb = P.kiem("42765379", URL_ID, bay_gio=cuoi + timedelta(minutes=5), tep=so, dtv=DTV)
    assert ma == 3 and f"đã đủ {P.TRAN_MOI_MIEN} bài" in tb, tb
    monkeypatch.setitem(P.MIEN_CAM_AI_RIENG, "cambridge.org", "thử: miền cấm AI riêng xét TRƯỚC mọi bảng")
    ma, tb = P.kiem("42112625", URL_ID, bay_gio=cuoi + timedelta(minutes=5), tep=so, dtv=DTV)
    assert ma == 3 and "cấm dùng với AI" in tb, tb


def test_hang_cho_hien_dau_tich_cho_cambridge(so) -> None:
    duoc = set(P.nxb_duoc_luu(DTV, T0.date()))
    assert L.pham_vi_nhom(P, DTV, "www.cambridge.org", "10.1192/bjp.2026.10651", URL_ID, duoc) == "✓"
    assert L.pham_vi_nhom(P, DTV, "www.cambridge.org", "", URL_ID, duoc) == "✓"
    assert L.pham_vi_nhom(P, DTV, "archive.lstmed.ac.uk", "10.1017/S003329172000046X",
                          "https://archive.lstmed.ac.uk/14364/1/x.docx", duoc) == "✗ ngoài miền NXB"
    assert L.pham_vi_nhom(P, DTV, "www.vi-du-nxb-la.org", "", "https://www.vi-du-nxb-la.org/a", duoc) == "✗ chưa kiểm điều khoản"
    # NXB «cấm» chưa uỷ quyền vẫn «ngoài phạm vi» như trước.
    assert L.pham_vi_nhom(P, DTV, "www.sciencedirect.com", "10.1016/j.x", "https://www.sciencedirect.com/x", duoc) == \
        "✗ ngoài phạm vi"


# ───────────────────────── cấu hình DOM (đo thật 12/11/2026) ─────────────────────────

def test_cau_hinh_cambridge_khuon_hop_le() -> None:
    assert L.kiem_cau_hinh(CAU_HINH) == []
    assert L.tim_nxb("www.cambridge.org", CAU_HINH)[0] == "cambridge_core"
    assert L.tim_nxb("www.cambridge.org.vi-du.org", CAU_HINH)[0] is None
    c = CAU_HINH["nxb"]["cambridge_core"]
    vung = [s.strip() for s in c["chon"].split(",")]
    assert vung == [".abstract-content", ".content-box"]
    assert "#references-list" not in vung, "bài không quyền vẫn hiện tham khảo ~20 000 ký tự ⇒ vùng vượt min"
    assert c["min"] >= 12000 and c["pdf"] == "meta" and "Access options" in c["khoaDeMuc"]
    assert c["khoaTrang"].startswith("\\b") and c["khoaTrang"].endswith("\\b") and "purchase" in c["khoaTrang"].lower()
    assert c["kiem_lan_cuoi"].startswith("2026-11-12") and "CHƯA lưu" in c["kiem_lan_cuoi"]
    o = L.dien_cau_hinh(c, URL_CO, "10.1192/bjp.2026.10651", CAU_HINH["dau_khong_quyen_url"])
    assert o["chon"] == c["chon"] and o["pdf"] == "meta"


def test_dau_url_khong_quyen_cua_cambridge() -> None:
    import re
    mau = [m for m in CAU_HINH["dau_khong_quyen_url"] if "cambridge" in m]
    assert len(mau) == 1
    assert re.search(mau[0], URL_KHONG, re.I) and not re.search(mau[0], URL_CO, re.I)
    assert not re.search(mau[0], URL_ID, re.I), "trang /product/identifier/ chưa chuyển hướng — không được coi là không quyền"
    # Mẫu Cambridge không được bắt trang /abs/ của NXB khác.
    assert not re.search(mau[0], "https://academic.oup.com/journals/x/article/abs/1", re.I)


def _danh_gia(t):
    # Dữ liệu qua stdin như test cấu hình 18/10 (thân bài dài vượt giới hạn tham số dòng lệnh trên CI).
    ma = ("const m=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);"
          "process.stdin.on('end',()=>process.stdout.write(JSON.stringify(m.danhGia(JSON.parse(s)))))")
    r = subprocess.run([NODE, "-e", ma, str(BO_LUU)], input=json.dumps(t), capture_output=True, text=True,
                       encoding="utf-8", timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def _o(url: str = URL_CO) -> dict:
    return L.dien_cau_hinh(CAU_HINH["nxb"]["cambridge_core"], url, "10.1192/bjp.2026.10651", CAU_HINH["dau_khong_quyen_url"])


# Thân bài thật có thể có các chữ này (dịch vụ y tế, kinh tế học): «Purchase» trần hay «access options» theo chữ sẽ chặn nhầm.
THAN = ("Method Results Discussion. Medications were purchased over the counter; purchasers reported limited access options "
        "in rural clinics. ") * 140
TRANG_CO = "Login Alert Article contents You have Access Open access " + THAN + " References Cited by"
DE_MUC_CO = ["Login Alert", "Article contents", "Abstract", "Method", "Results", "Discussion", "References"]
DE_MUC_KHONG = ["Login Alert", "Article contents", "Abstract", "Keywords", "Information", "Access options", "Article purchase",
                "References"]
TRANG_KHONG = ("Get access Access options Get access to the full version of this content by using one of the access options below. "
               "Content may require purchase if you do not have access. Check access Institutional login Personal login Log in "
               "Article purchase Digital access for individuals US$41.00 Add to cart References")


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_bai_co_quyen_qua_ke_ca_than_bai_co_chu_purchased() -> None:
    kq = _danh_gia({"o": _o(), "href": URL_CO, "khongQuyenUrl": _o()["dauKhongQuyenUrl"], "soVung": 2, "doDai": len(THAN),
                    "vung": THAN, "trang": TRANG_CO, "deMuc": DE_MUC_CO})
    assert kq["ok"] is True, kq


@pytest.mark.skipif(NODE is None, reason="máy không có node")
def test_bai_khong_quyen_bi_chan_boi_tung_lop_khoa() -> None:
    o = _o(URL_KHONG)
    goc = {"o": o, "href": URL_KHONG, "khongQuyenUrl": o["dauKhongQuyenUrl"], "soVung": 2, "doDai": 1622, "vung": "Abstract " * 180,
           "trang": TRANG_KHONG, "deMuc": DE_MUC_KHONG}
    kq = _danh_gia(goc)
    assert kq["ok"] is False and "URL chuyển hướng" in kq["ly"], kq
    # Lớp 2 — min: URL không mang dấu (vd trang chưa chuyển hướng) ⇒ vùng chỉ có tóm tắt bị chặn.
    kq = _danh_gia(goc | {"href": URL_ID, "khongQuyenUrl": []})
    assert kq["ok"] is False and "ngắn" in kq["ly"], kq
    # Lớp 3 — đề mục «Access options»: vùng dài (giả sử bố cục đổi, lọt danh mục tham khảo vào vùng) vẫn bị chặn.
    dai = "Reference list entry. " * 1000
    kq = _danh_gia(goc | {"href": URL_ID, "khongQuyenUrl": [], "doDai": len(dai), "vung": dai})
    assert kq["ok"] is False and "Access options" in kq["ly"], kq
    # Lớp 4 — cụm «Article purchase» trên trang khi đề mục đổi tên.
    kq = _danh_gia(goc | {"href": URL_ID, "khongQuyenUrl": [], "doDai": len(dai), "vung": dai, "deMuc": ["Abstract"]})
    assert kq["ok"] is False and "Article purchase" in kq["ly"], kq


# ───────────────────────── doctrine ─────────────────────────

def test_doctrine_khop_bang_tdm_va_bat_duoc_khi_mat_tien_to_hoac_ten_bang() -> None:
    van_ban = DOCTRINE.read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
    assert any(CUP in x for x in DTV.lech_doctrine(van_ban.replace("`10.1017/`", "10.1017/")))
    assert any("TDM_CHO_PHEP_LUU" in x for x in DTV.lech_doctrine(van_ban.replace("`TDM_CHO_PHEP_LUU`", "bảng TDM")))
    i = van_ban.index("## 2septies. ")
    muc = van_ban[i:van_ban.index("\n## ", i + 5)]
    assert "«Thêm Cambridge vào làn Chrome»" in muc and "chưa có làn lưu bản sao" not in muc
