#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đợt đọc điều khoản NXB 18/10/2026 — sáu NXB có bài «consider» trong hàng chờ toàn văn bị `phien_uy_quyen_chrome.py --kiem`
từ chối «NXB của bài (chưa kiểm điều khoản) KHÔNG thuộc phạm vi phiên».

Khoá:
  • mỗi NXB nhận đúng khoá theo tiền tố DOI (DOI thật trong hàng chờ) và theo URL trang bài;
  • TJPMR khớp tiền tố HẸP `10.5606/tftrd.` — 10.5606 là tiền tố chung của Baycinar Tibbi Yayincilik (Crossref 18/10/2026), nới
    thành `10.5606/` sẽ gán điều khoản TJPMR cho mọi tạp chí khác của nhà xuất bản đó;
  • CFP và Medscape không có tiền tố DOI ⇒ chỉ khớp theo miền; bản trên PMC (không DOI) KHÔNG khớp — hành vi có chủ ý, bác sĩ đọc
    trực tiếp hoặc đọc ở trang của chính NXB;
  • mục mới đủ trường theo khuôn (nguồn https, ngày đọc 18/10, trích ≤ 15 từ, đường hợp lệ) và đều «cam»;
  • doctrine §2septies nêu đủ tên + tiền tố DOI (`lech_doctrine`), và bắt được khi mất một tiền tố/tên;
  • đi trọn đường thật: tệp uỷ quyền có mục NXB mới ⇒ `--kiem` của phiên nhận bài NXB đó; không có ⇒ vẫn từ chối.
Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
DOCTRINE = TOOLS.parent / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md"


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


DTV = _nap("_dtv_dot_20261018", "doc_toan_van_co_nguoi.py")
P = _nap("_puq_dot_20261018", "phien_uy_quyen_chrome.py")

BPG = "Baishideng Publishing Group"
CFP = "College of Family Physicians of Canada (Canadian Family Physician)"
RCGP = "Royal College of General Practitioners (BJGP)"
NIHR = "NIHR Journals Library"
TJPMR = "Turkish Journal of Physical Medicine and Rehabilitation"
MEDSCAPE = "Medscape (WebMD)"
MOI = (BPG, CFP, RCGP, NIHR, TJPMR, MEDSCAPE)


@pytest.mark.parametrize("doi,ten", [
    ("10.3748/wjg.v17.i41.4596", BPG), ("10.4240/wjgs.v13.i1.1", BPG),
    ("10.3399/bjgp21X717425", RCGP), ("10.3399/BJGPO.2023.0116", RCGP),
    ("10.3310/hta24270", NIHR), ("10.3310/HTA24270", NIHR),
    ("10.5606/tftrd.2018.1618", TJPMR), ("10.5606/TFTRD.2018.1618", TJPMR),
])
def test_doi_trong_hang_cho_nhan_dung_khoa(doi, ten) -> None:
    assert DTV.nxb_cua(doi=doi)[0] == ten, doi


@pytest.mark.parametrize("url,ten", [
    ("https://www.wjgnet.com/1007-9327/full/v17/i41/4596.htm", BPG),
    ("https://www.cfp.ca/content/63/5/354", CFP),
    ("https://bjgp.org/content/71/712/489", RCGP),
    ("https://www.journalslibrary.nihr.ac.uk/hta/HTA24270", NIHR),
    ("https://www.ftrdergisi.com/copyright-and-licensing", TJPMR),
    ("https://www.medscape.com/viewarticle/495668", MEDSCAPE),
])
def test_url_trang_bai_nhan_dung_khoa(url, ten) -> None:
    assert DTV.nxb_cua(url=url)[0] == ten, url


@pytest.mark.parametrize("doi", ["10.5606/ArchRheumatol.2024.10517", "10.5606/tgkdc.dergisi.2020.18829"])
def test_tien_to_baycinar_cua_tap_chi_khac_khong_mang_khoa_tjpmr(doi) -> None:
    """10.5606 là tiền tố của Baycinar Tibbi Yayincilik (Crossref /prefixes/10.5606, đọc 18/10/2026), dùng cho nhiều tạp chí.
    Điều khoản đọc 18/10 là của TJPMR — tạp chí khác của cùng tiền tố phải còn «chưa kiểm»."""
    assert DTV.nxb_cua(doi=doi)[0] is None, doi


def test_ban_pmc_khong_doi_khong_khop_khoa_cfp_va_medscape() -> None:
    """Bản trên PMC KHÔNG kèm DOI (CFP cũ, MedGenMed của Medscape) không mang khoá nào — bảng khớp theo tiền tố DOI rồi miền,
    hành vi có chủ ý (đọc ở trang của chính NXB, hoặc bác sĩ đọc trực tiếp)."""
    assert DTV.nxb_cua(url="https://pmc.ncbi.nlm.nih.gov/articles/PMC5429051/")[0] is None
    assert DTV.nxb_cua(url="https://pmc.ncbi.nlm.nih.gov/articles/PMC1681414/")[0] is None
    assert DTV.DIEU_KHOAN_NXB[MEDSCAPE]["doi"] == ()


def test_bai_cfp_co_doi_doc_qua_pmc_mang_khoa_cfp() -> None:
    """28/10/2026: bài CFP từ khoảng 2021 có DOI tiền tố 10.46747/ (PMID 41844291 · doi 10.46747/cfp.7203173). Bảng chỉ khớp
    miền cfp.ca thì bản PMC của bài đó rơi về «chưa kiểm» — sai cả hai chiều: không áp được luật «cấm» của CFP, cũng không
    nhận được uỷ quyền bác sĩ đã ghi cho CFP. Có DOI ⇒ phải mang khoá CFP dù đọc ở PMC; DOI của NXB khác không bị kéo theo."""
    assert DTV.DIEU_KHOAN_NXB[CFP]["doi"] == ("10.46747/",)
    pmc = "https://pmc.ncbi.nlm.nih.gov/articles/PMC12995299/"
    assert DTV.nxb_cua(doi="10.46747/cfp.7203173", url=pmc)[0] == CFP
    assert DTV.nxb_cua(doi="10.3399/BJGP.2024.0369", url=pmc)[0] == RCGP


@pytest.mark.parametrize("ten", MOI)
def test_muc_moi_du_truong_va_trich_ngan(ten) -> None:
    d = DTV.DIEU_KHOAN_NXB[ten]
    assert d["ket_luan"] == "cam", "NXB «không rõ» vẫn ghi «cam» — bảng chỉ nhận «cấm»"
    assert d["nguon"].startswith("https://") and d["doc_luc"] == "2026-10-18"
    assert d.get("duong_hop_le") and d.get("loai_nguon") and d["mien"]
    assert 0 < len(d["trich"].split()) <= 15, (ten, "trích nguyên văn tối đa 15 từ (dấu … tính là một từ)")


def test_nihr_ghi_ro_nhan_cc_by_cua_unpaywall_la_sai() -> None:
    """Unpaywall gắn «cc-by» cho 10.3310/hta24270 nhưng dòng bản quyền của báo cáo là Crown copyright (đọc 18/10/2026) — mục
    bảng phải giữ lời cảnh báo này để lần sau không ai «sửa» thành giấy phép mở theo nhãn Unpaywall."""
    assert "Unpaywall" in DTV.DIEU_KHOAN_NXB[NIHR]["loai_nguon"]


def test_doctrine_khop_bang_va_bat_duoc_khi_mat_tien_to_hoac_ten() -> None:
    van_ban = DOCTRINE.read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
    assert any(NIHR in x for x in DTV.lech_doctrine(van_ban.replace("`10.3310/`", "10.3310/")))
    assert any(TJPMR in x for x in DTV.lech_doctrine(van_ban.replace("`10.5606/tftrd.`", "10.5606/tftrd.")))
    assert any(BPG in x for x in DTV.lech_doctrine(van_ban.replace("Baishideng Publishing Group", "BPG")))


T0 = datetime(2026, 10, 18, 9, 0, 0, tzinfo=timezone(timedelta(hours=7)))
CAN_CU = ("«uỷ quyền riêng cho Wiley như đã làm với J Rheumatol và cho tất cả các vấn đề tương tự khác không hỏi lại tôi nữa» "
          "(bác sĩ, 04/10/2026)")


def test_tep_uy_quyen_co_nxb_moi_thi_kiem_cua_phien_nhan(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(DTV, "DASH", tmp_path)
    so = tmp_path / "state" / "phien.json"
    tep = tmp_path / DTV.TEN_TEP_UY_QUYEN
    tep.write_text(json.dumps({"muc": [{"nxb": "Elsevier", "ngay": "2026-10-03", "can_cu": "cho máy đọc toàn văn Elsevier"}]},
                              ensure_ascii=False), encoding="utf-8")
    assert P.mo("uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8544154/"
    ma, tb = P.kiem("34711558", url, "10.3399/bjgp21X717425", bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 3 and RCGP in tb and "KHÔNG thuộc phạm vi" in tb    # đã kiểm điều khoản nhưng CHƯA có uỷ quyền ⇒ vẫn dừng
    tep.write_text(json.dumps({"muc": [{"nxb": RCGP, "ngay": "2026-10-18", "can_cu": CAN_CU}]}, ensure_ascii=False),
                   encoding="utf-8")
    assert P.kiem("34711558", url, "10.3399/bjgp21X717425", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    assert RCGP in P.nxb_duoc_luu(DTV, T0.date())
