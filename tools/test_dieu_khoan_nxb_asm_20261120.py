#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Điều khoản NXB đọc 20/11/2026 — American Society for Microbiology (ASM Journals).

Bài Antimicrob Agents Chemother 2006 (PMID 17005808) là bằng chứng toàn văn DUY NHẤT của một mục «Áp dụng ngay»; tệp Unpaywall
cũ không giấy phép mở của nó bị giữ lại khi cách ly. ASM chưa có trong bảng ⇒ `phien_uy_quyen_chrome.py --kiem` từ chối. Điều
khoản: cá nhân lưu/in bản đơn lẻ dùng riêng; TDM chỉ cho cơ sở thuê bao; không có điều về AI ⇒ «không rõ ⇒ xử như cấm».

Khoá:
  • tiền tố 10.1128 và miền journals.asm.org nhận đúng khoá ASM; «asm.org» KHÔNG nuốt «aasm.org» (khoá AASM giữ nguyên);
  • mục đủ trường theo khuôn, trích ≤ 15 từ, ghi «cam»;
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


DTV = _nap("_dtv_asm_20261120", "doc_toan_van_co_nguoi.py")
P = _nap("_puq_asm_20261120", "phien_uy_quyen_chrome.py")

ASM = "American Society for Microbiology (ASM Journals)"
AASM = "American Academy of Sleep Medicine (AASM)"


@pytest.mark.parametrize("doi", ["10.1128/AAC.00251-06", "10.1128/aac.00251-06", "10.1128/mbio.01234-25"])
def test_tien_to_doi_nhan_dung_khoa(doi) -> None:
    assert DTV.nxb_cua(doi=doi)[0] == ASM, doi


@pytest.mark.parametrize("url, khoa", [
    ("https://journals.asm.org/doi/10.1128/aac.00251-06", ASM),
    ("https://asm.org/articles/2026/x", ASM),
    ("https://go.aasm.org/Terms.html", AASM),        # ranh giới dấu chấm: «asm.org» không nuốt «aasm.org»
    ("https://aasm.org/clinical-resources/", AASM)])
def test_mien_nhan_dung_khoa_va_khong_nuot_aasm(url, khoa) -> None:
    assert DTV.nxb_cua(url=url)[0] == khoa, url


def test_muc_moi_du_truong_va_trich_ngan() -> None:
    d = DTV.DIEU_KHOAN_NXB[ASM]
    assert d["ket_luan"] == "cam", "NXB «không rõ» vẫn ghi «cam» — bảng chỉ nhận «cấm»"
    assert d["nguon"] == "https://journals.asm.org/terms" and d["doc_luc"] == "2026-11-20"
    assert d.get("duong_hop_le") and d.get("loai_nguon") and d["mien"] and d["doi"] == ("10.1128/",)
    assert 0 < len(d["trich"].split()) <= 15, "trích nguyên văn tối đa 15 từ"


def test_doctrine_khop_bang_va_bat_duoc_khi_mat_tien_to_hoac_ten() -> None:
    van_ban = DOCTRINE.read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
    assert any(ASM in x for x in DTV.lech_doctrine(van_ban.replace("`10.1128/`", "10.1128/")))
    assert any(ASM in x for x in DTV.lech_doctrine(van_ban.replace("American Society for Microbiology", "ASM")))


T0 = datetime(2026, 11, 20, 11, 30, 0, tzinfo=timezone(timedelta(hours=7)))
CAN_CU = ("«uỷ quyền riêng cho Wiley như đã làm với J Rheumatol và cho tất cả các vấn đề tương tự khác không hỏi lại tôi nữa» "
          "(bác sĩ, 04/10/2026)")


def test_co_uy_quyen_thi_kiem_cua_phien_nhan_ban_pmc(tmp_path, monkeypatch) -> None:
    pmid, doi, url = "17005808", "10.1128/AAC.00251-06", "https://pmc.ncbi.nlm.nih.gov/articles/PMC1610069/"
    monkeypatch.setattr(DTV, "DASH", tmp_path)
    so = tmp_path / "state" / "phien.json"
    tep = tmp_path / DTV.TEN_TEP_UY_QUYEN
    tep.write_text(json.dumps({"muc": [{"nxb": "Elsevier", "ngay": "2026-10-03", "can_cu": "cho máy đọc toàn văn Elsevier"}]},
                              ensure_ascii=False), encoding="utf-8")
    assert P.mo("uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    ma, tb = P.kiem(pmid, url, doi, bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 3 and ASM in tb and "KHÔNG thuộc phạm vi" in tb    # đã kiểm điều khoản nhưng CHƯA có uỷ quyền ⇒ vẫn dừng
    tep.write_text(json.dumps({"muc": [{"nxb": ASM, "ngay": "2026-11-20", "can_cu": CAN_CU}]}, ensure_ascii=False),
                   encoding="utf-8")
    assert P.kiem(pmid, url, doi, bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    assert ASM in P.nxb_duoc_luu(DTV, T0.date())
