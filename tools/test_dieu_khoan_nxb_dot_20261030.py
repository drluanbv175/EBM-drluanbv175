#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đợt đọc điều khoản NXB 30/10/2026 — AASM + Deutscher Ärzte-Verlag: 4 bài của gói Sleep Psychiatry (JCSM 33164742, 29852917,
38300818; Dtsch Arztebl 42535778) bị `phien_uy_quyen_chrome.py --kiem` từ chối «NXB của bài (chưa kiểm điều khoản) KHÔNG thuộc phạm vi».

Khoá:
  • tiền tố DOI 10.5664 và 10.3238 (Crossref /prefixes đọc 30/10/2026) cùng URL trên miền của NXB nhận đúng khoá;
  • JCSM đã chuyển sang Springer: trang bài link.springer.com vẫn mang khoá Springer Nature theo miền, bản PMC mang khoá AASM theo DOI;
  • hai mục mới đủ trường theo khuôn và «cam»; doctrine §2septies nêu tên + tiền tố, bắt được khi mất tên hoặc tiền tố;
  • Cambridge KHÔNG vào bảng (điều khoản cho phép TDM phi thương mại; bảng chỉ nhận «cấm»);
  • đi trọn đường thật: có uỷ quyền ⇒ `--kiem` của phiên nhận bài qua PMC; chưa có ⇒ vẫn từ chối.
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


DTV = _nap("_dtv_dot_20261030", "doc_toan_van_co_nguoi.py")
P = _nap("_puq_dot_20261030", "phien_uy_quyen_chrome.py")

AASM = "American Academy of Sleep Medicine (AASM)"
DAEV = "Deutscher Ärzte-Verlag (Deutsches Ärzteblatt)"


@pytest.mark.parametrize("doi, khoa", [("10.5664/jcsm.8986", AASM), ("10.5664/JCSM.7178", AASM), ("10.5664/jcsm.11030", AASM),
                                       ("10.3238/arztebl.m2026.0141", DAEV)])
def test_doi_tien_to_nhan_dung_khoa(doi, khoa) -> None:
    assert DTV.nxb_cua(doi=doi)[0] == khoa, doi


@pytest.mark.parametrize("url, khoa", [("https://jcsm.aasm.org/doi/10.5664/jcsm.8986", AASM),
                                       ("https://di.aerzteblatt.de/int/archive/article/252395", DAEV),
                                       ("https://www.aerzteblatt.de/impressum", DAEV)])
def test_url_tren_mien_nxb_nhan_dung_khoa(url, khoa) -> None:
    assert DTV.nxb_cua(url=url)[0] == khoa, url


def test_jcsm_tren_springer_mang_khoa_springer_ban_pmc_mang_khoa_aasm() -> None:
    doi = "10.5664/jcsm.8986"
    assert DTV.nxb_cua(doi=doi, url=f"https://link.springer.com/article/{doi}")[0] == "Springer Nature"
    assert DTV.nxb_cua(doi=doi, url="https://pmc.ncbi.nlm.nih.gov/articles/PMC7853203/")[0] == AASM


@pytest.mark.parametrize("khoa", [AASM, DAEV])
def test_muc_moi_du_truong_va_trich_ngan(khoa) -> None:
    d = DTV.DIEU_KHOAN_NXB[khoa]
    assert d["ket_luan"] == "cam", "NXB «không rõ» vẫn ghi «cam» — bảng chỉ nhận «cấm»"
    assert d["nguon"].startswith("https://") and d["doc_luc"] == "2026-10-30"
    assert d.get("duong_hop_le") and d.get("loai_nguon") and d["mien"]
    assert 0 < len(d["trich"].split()) <= 15, "trích nguyên văn tối đa 15 từ"


def test_cambridge_khong_vao_bang_vi_dieu_khoan_cho_phep_tdm() -> None:
    assert DTV.nxb_cua(doi="10.1192/bjp.2025.86", url="https://www.cambridge.org/core/journals/x") == (None, None)


def test_doctrine_khop_bang_va_bat_duoc_khi_mat_tien_to_hoac_ten() -> None:
    van_ban = DOCTRINE.read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
    assert any(AASM in x for x in DTV.lech_doctrine(van_ban.replace("`10.5664/`", "10.5664/")))
    assert any(DAEV in x for x in DTV.lech_doctrine(van_ban.replace("`10.3238/`", "10.3238/")))
    assert any(AASM in x for x in DTV.lech_doctrine(van_ban.replace("American Academy of Sleep Medicine", "AASM")))
    assert any(DAEV in x for x in DTV.lech_doctrine(van_ban.replace("Deutscher Ärzte-Verlag", "DÄV")))


T0 = datetime(2026, 10, 30, 19, 0, 0, tzinfo=timezone(timedelta(hours=7)))
CAN_CU = ("«uỷ quyền riêng cho Wiley như đã làm với J Rheumatol và cho tất cả các vấn đề tương tự khác không hỏi lại tôi nữa» "
          "(bác sĩ, 04/10/2026)")


@pytest.mark.parametrize("khoa, pmid, doi, url", [
    (AASM, "33164742", "10.5664/jcsm.8986", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7853203/"),
    (DAEV, "42535778", "10.3238/arztebl.m2026.0141", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13626306/")])
def test_co_uy_quyen_thi_kiem_cua_phien_nhan_ban_pmc(tmp_path, monkeypatch, khoa, pmid, doi, url) -> None:
    monkeypatch.setattr(DTV, "DASH", tmp_path)
    so = tmp_path / "state" / "phien.json"
    tep = tmp_path / DTV.TEN_TEP_UY_QUYEN
    tep.write_text(json.dumps({"muc": [{"nxb": "Elsevier", "ngay": "2026-10-03", "can_cu": "cho máy đọc toàn văn Elsevier"}]},
                              ensure_ascii=False), encoding="utf-8")
    assert P.mo("uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    ma, tb = P.kiem(pmid, url, doi, bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 3 and khoa in tb and "KHÔNG thuộc phạm vi" in tb    # đã kiểm điều khoản nhưng CHƯA có uỷ quyền ⇒ vẫn dừng
    tep.write_text(json.dumps({"muc": [{"nxb": khoa, "ngay": "2026-10-30", "can_cu": CAN_CU}]}, ensure_ascii=False),
                   encoding="utf-8")
    assert P.kiem(pmid, url, doi, bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    assert khoa in P.nxb_duoc_luu(DTV, T0.date())
