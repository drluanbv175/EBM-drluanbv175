#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đợt đọc điều khoản NXB 11/11/2026 — 23 bài có bản đọc miễn phí (Unpaywall 10/11) bị `phien_uy_quyen_chrome.py --kiem` từ chối
«NXB của bài (chưa kiểm điều khoản) KHÔNG thuộc phạm vi»; bác sĩ 11/11: «Kiểm điều khoản».

Khoá:
  • 8 tiền tố của tạp chí nay do NXB ĐÃ có trong bảng lưu trữ (Crossref works 11/11/2026) nhận đúng khoá cũ;
  • 4 NXB mới «cấm» (cấm rõ hoặc «không rõ ⇒ xử như cấm») đủ trường theo khuôn, trích ≤ 15 từ;
  • 3 NXB khai giấy phép mở cho MỌI nội dung trên miền ⇒ `GIAY_PHEP_MO_CAP_NXB` khớp theo MIỀN (không kéo theo miền khác cùng
    tiền tố — hkmj.org) và tầng 2 Unpaywall nhận bản không ghi giấy phép trên miền đó;
  • Cambridge và De Gruyter KHÔNG vào bảng (cho phép TDM phi thương mại);
  • doctrine §2septies nêu tên + tiền tố, bắt được khi mất tên hoặc tiền tố;
  • đi trọn đường thật: chưa có uỷ quyền ⇒ `--kiem` vẫn từ chối bản PMC; có uỷ quyền ⇒ nhận.
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


DTV = _nap("_dtv_dot_20261111", "doc_toan_van_co_nguoi.py")
P = _nap("_puq_dot_20261111", "phien_uy_quyen_chrome.py")
GOM = _nap("_gom_dot_20261111", "gom_toan_van_dashboard.py")

WK = "Wolters Kluwer Health (LWW · AHA journals · Neurology)"
BENTHAM = "Bentham Science Publishers"
CER = "Clinical and Experimental Rheumatology S.A.S."
AMCP = "Academy of Managed Care Pharmacy (AMCP — J Manag Care Spec Pharm)"
ABFM = "American Board of Family Medicine (ABFM — J Am Board Fam Med)"
MOI = (BENTHAM, CER, AMCP, ABFM)


@pytest.mark.parametrize("doi, khoa", [
    ("10.2215/CJN.0000000000000136", WK), ("10.11124/JBIES-24-00123", WK),
    ("10.5665/sleep.2554", "Oxford University Press"),
    ("10.1124/pharmrev.123.001087", "Elsevier"), ("10.4158/gl-2020-0524", "Elsevier"),
    ("10.1089/thy.2014.0028", "SAGE Publishing"), ("10.4997/jrcpe.2019.415", "SAGE Publishing"),
    ("10.2217/pgs-2023-0095", "Taylor & Francis (Informa UK)"),
    ("10.2174/187152712800672535", BENTHAM), ("10.55563/clinexprheumatol/0a1b2c", CER),
    ("10.18553/jmcp.2025.31.6.565", AMCP), ("10.3122/jabfm.2022.03.210334", ABFM)])
def test_tien_to_doi_nhan_dung_khoa(doi, khoa) -> None:
    assert DTV.nxb_cua(doi=doi)[0] == khoa, doi


@pytest.mark.parametrize("url, khoa", [
    ("https://www.eurekaselect.com/article/12345", BENTHAM), ("https://www.clinexprheumatol.org/abstract.asp?a=1", CER),
    ("https://www.jmcp.org/doi/10.18553/jmcp.2025.31.6.565", AMCP), ("https://www.jabfm.org/content/35/3/1", ABFM),
    ("https://www.liebertpub.com/doi/10.1089/thy.2014.0028", "SAGE Publishing"),
    ("https://pharmrev.aspetjournals.org/article/S0031-6997(24)00624-0/fulltext", "Elsevier")])
def test_url_tren_mien_nxb_nhan_dung_khoa(url, khoa) -> None:
    assert DTV.nxb_cua(url=url)[0] == khoa, url


@pytest.mark.parametrize("khoa", MOI)
def test_muc_moi_du_truong_va_trich_ngan(khoa) -> None:
    d = DTV.DIEU_KHOAN_NXB[khoa]
    assert d["ket_luan"] == "cam", "NXB «không rõ» vẫn ghi «cam» — bảng chỉ nhận «cấm»"
    assert d["nguon"].startswith("https://") and d["doc_luc"] == "2026-11-11"
    assert d.get("duong_hop_le") and d.get("loai_nguon") and d["mien"] and d["doi"]
    assert 0 < len(d["trich"].split()) <= 15, "trích nguyên văn tối đa 15 từ"


@pytest.mark.parametrize("doi", ["10.1192/bjp.2021.1", "10.1017/S0033291725000001", "10.1515/dx-2024-0113"])
def test_cambridge_va_de_gruyter_khong_vao_bang(doi) -> None:
    assert DTV.nxb_cua(doi=doi) == (None, None), "cho phép TDM phi thương mại — bảng chỉ nhận «cấm»"


@pytest.mark.parametrize("url, khoa, gp", [
    ("https://www.psychiatriapolska.pl/Article,1.html", "Psychiatria Polska (KRW PTP)", "cc-by"),
    ("https://www.easap.asia/index.php/find-issues/x", "Hong Kong Academy of Medicine Press (East Asian Arch Psychiatry)",
     "cc-by-nc-nd"),
    ("https://e-century.us/files/ajtr/18/1/ajtr0000001.pdf", "e-Century Publishing Corporation", "cc-by-nc"),
    ("https://www.ajtr.org/x", "e-Century Publishing Corporation", "cc-by-nc")])
def test_giay_phep_mo_cap_nxb_khop_theo_mien_va_tang_unpaywall_nhan(url, khoa, gp) -> None:
    ten, d = DTV.giay_phep_mo_cap_nxb(url)
    assert ten == khoa and d["giay_phep"] == (gp,) and d["doc_luc"] == "2026-11-11"
    assert 0 < len(d["trich"].split()) <= 20
    duoc, ly = GOM.quyet_dinh_unpaywall("10.12809/eaap2400", url, None, dtv=DTV)
    assert duoc is True and khoa in ly, ly


@pytest.mark.parametrize("url", ["https://www.hkmj.org/abstracts/v31n1/1.htm", "https://psychiatriapolska.pl.vi-du.org/x",
                                 "https://www.cdc.gov/mmwr/volumes/73/rr/rr7304a1.htm"])
def test_giay_phep_mo_khong_suy_rong_sang_mien_khac(url) -> None:
    assert DTV.giay_phep_mo_cap_nxb(url) == (None, None), url


def test_doctrine_khop_bang_va_bat_duoc_khi_mat_tien_to_hoac_ten() -> None:
    van_ban = DOCTRINE.read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
    assert any(BENTHAM in x for x in DTV.lech_doctrine(van_ban.replace("`10.2174/`", "10.2174/")))
    assert any(WK in x for x in DTV.lech_doctrine(van_ban.replace("`10.2215/`", "10.2215/")))
    assert any(ABFM in x for x in DTV.lech_doctrine(van_ban.replace("American Board of Family Medicine", "ABFM")))
    assert any(AMCP in x for x in DTV.lech_doctrine(van_ban.replace("Academy of Managed Care Pharmacy", "AMCP")))


T0 = datetime(2026, 11, 11, 19, 0, 0, tzinfo=timezone(timedelta(hours=7)))
CAN_CU = ("«uỷ quyền riêng cho Wiley như đã làm với J Rheumatol và cho tất cả các vấn đề tương tự khác không hỏi lại tôi nữa» "
          "(bác sĩ, 04/10/2026)")


@pytest.mark.parametrize("khoa, pmid, doi, url", [
    (ABFM, "35641040", "10.3122/jabfm.2022.03.210334", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9730343/"),
    (AMCP, "40443003", "10.18553/jmcp.2025.31.6.565", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12123200/")])
def test_co_uy_quyen_thi_kiem_cua_phien_nhan_ban_pmc(tmp_path, monkeypatch, khoa, pmid, doi, url) -> None:
    monkeypatch.setattr(DTV, "DASH", tmp_path)
    so = tmp_path / "state" / "phien.json"
    tep = tmp_path / DTV.TEN_TEP_UY_QUYEN
    tep.write_text(json.dumps({"muc": [{"nxb": "Elsevier", "ngay": "2026-10-03", "can_cu": "cho máy đọc toàn văn Elsevier"}]},
                              ensure_ascii=False), encoding="utf-8")
    assert P.mo("uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    ma, tb = P.kiem(pmid, url, doi, bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 3 and khoa in tb and "KHÔNG thuộc phạm vi" in tb    # đã kiểm điều khoản nhưng CHƯA có uỷ quyền ⇒ vẫn dừng
    tep.write_text(json.dumps({"muc": [{"nxb": khoa, "ngay": "2026-11-11", "can_cu": CAN_CU}]}, ensure_ascii=False),
                   encoding="utf-8")
    assert P.kiem(pmid, url, doi, bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    assert khoa in P.nxb_duoc_luu(DTV, T0.date())
