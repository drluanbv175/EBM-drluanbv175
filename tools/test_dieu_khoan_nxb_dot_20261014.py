#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đợt đọc điều khoản NXB 14/10/2026 — mười NXB có bài trong hàng chờ toàn văn bị `phien_uy_quyen_chrome.py --kiem` từ chối
«NXB của bài (chưa kiểm điều khoản) KHÔNG thuộc phạm vi phiên».

Khoá:
  • mỗi NXB nhận đúng khoá theo tiền tố DOI (DOI thật trong hàng chờ) và theo URL trang bài;
  • European Journal of Endocrinology (10.1530/EJE-…) mang khoá OUP — DOI nay phân giải sang academic.oup.com/ejendo — kể cả khi
    chỉ có DOI hoặc URL là miền cũ eje.bioscientifica.com; các tạp chí khác của 10.1530 mang khoá Bioscientifica;
  • mục mới đủ trường theo khuôn (nguồn https, ngày đọc 14/10, trích ≤ 15 từ, đường hợp lệ) và đều «cam» — NXB «không rõ» ghi
    «cam» (bảng chỉ nhận «cấm»: một giá trị khác sẽ được `kiem_ho_so` cho qua mà không đòi khai điều khoản);
  • doctrine §2septies nêu đủ tên + tiền tố DOI (`lech_doctrine`), và bắt được khi mất một tiền tố/tên;
  • đi trọn đường thật: tệp uỷ quyền có mục NXB mới ⇒ `--kiem` của phiên nhận bài NXB đó; không có ⇒ vẫn từ chối.
Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date, datetime, timedelta, timezone
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


DTV = _nap("_dtv_dot_20261014", "doc_toan_van_co_nguoi.py")
P = _nap("_puq_dot_20261014", "phien_uy_quyen_chrome.py")

TF = "Taylor & Francis (Informa UK)"
THIEME = "Thieme (Georg Thieme Verlag)"
ASH = "American Society of Hematology (Blood)"
KARGER = "Karger"
BIO = "Bioscientifica"
APA = "American Psychiatric Association (PsychiatryOnline)"
ERS = "European Respiratory Society"
MINERVA = "Edizioni Minerva Medica"
COPD = "COPD Foundation"
PCR = "Europa Group (PCR · EuroIntervention)"
OUP = "Oxford University Press"
MOI = (TF, THIEME, ASH, KARGER, BIO, APA, ERS, MINERVA, COPD, PCR)


@pytest.mark.parametrize("doi,ten", [
    ("10.1080/03007995.2026.2687640", TF), ("10.1080/13548506.2020.1764597", TF), ("10.3109/00365599.2012.1", TF),
    ("10.1055/a-2529-5025", THIEME), ("10.1055/s-0035-1562910", THIEME),
    ("10.1182/blood-2008-07-167155", ASH), ("10.1182/bloodadvances.2026019740", ASH),
    ("10.1159/000551858", KARGER),
    ("10.1530/EC-25-0625", BIO), ("10.1530/ETJ-26-0043", BIO),
    ("10.1530/EJE-16-0657", OUP), ("10.1530/EJE-12-0627", OUP),
    ("10.1176/appi.ajp.2011.11071009", APA),
    ("10.1183/13993003.00302-2022", ERS), ("10.1183/23120541.01091-2024", ERS),
    ("10.23736/S1973-9087.20.06185-7", MINERVA),
    ("10.15326/jcopdf.2024.0500", COPD),
    ("10.4244/EIJ-D-25-01274", PCR),
])
def test_doi_trong_hang_cho_nhan_dung_khoa(doi, ten) -> None:
    assert DTV.nxb_cua(doi=doi)[0] == ten, doi


@pytest.mark.parametrize("url,ten", [
    ("https://www.tandfonline.com/doi/full/10.1080/03007995.2026.2687640", TF),
    ("https://www.thieme-connect.de/products/ejournals/abstract/10.1055/a-2529-5025", THIEME),
    ("https://ashpublications.org/blood/article/145/3/257/525822", ASH),
    ("https://karger.com/kbr/article/doi/10.1159/000551858", KARGER),
    ("https://journals.bioscientifica.com/ec/article/15/1/e250625/75320", BIO),
    ("https://psychiatryonline.org/doi/10.1176/appi.ajp.2011.11071009", APA),
    ("https://publications.ersnet.org/content/erj/60/1/2200302", ERS),
    ("https://www.minervamedica.it/en/journals/europa-medicophysica/article.php?cod=R33Y2020N06A0123", MINERVA),
    ("https://journal.copdfoundation.org/jcopdf/id/1503", COPD),
    ("https://eurointervention.pcronline.com/article/impact-of-renal-function-on-edoxaban", PCR),
])
def test_url_trang_bai_nhan_dung_khoa(url, ten) -> None:
    assert DTV.nxb_cua(url=url)[0] == ten, url


def test_eje_mang_khoa_oup_ca_khi_url_la_mien_bioscientifica_cu() -> None:
    """EJE chuyển sang OUP (01/01/2023); DOI 10.1530/EJE-… phân giải sang academic.oup.com/ejendo (đo 14/10/2026). Khoá OUP đứng
    TRƯỚC khoá Bioscientifica trong bảng nên DOI thắng cả khi URL còn là miền cũ."""
    assert DTV.nxb_cua(doi="10.1530/EJE-16-0657", url="https://eje.bioscientifica.com/view/journals/eje/176/1/31.xml")[0] == OUP
    assert DTV.nxb_cua(url="https://academic.oup.com/ejendo/article-abstract/176/1/31/6655079")[0] == OUP
    ten = list(DTV.DIEU_KHOAN_NXB)
    assert ten.index(OUP) < ten.index(BIO), "đảo thứ tự ⇒ bài EJE (chỉ DOI) rơi vào khoá Bioscientifica"


@pytest.mark.parametrize("ten", MOI)
def test_muc_moi_du_truong_va_trich_ngan(ten) -> None:
    d = DTV.DIEU_KHOAN_NXB[ten]
    assert d["ket_luan"] == "cam", "NXB «không rõ» vẫn ghi «cam» — bảng chỉ nhận «cấm»"
    assert d["nguon"].startswith("https://") and d["doc_luc"] == "2026-10-14"
    assert d.get("duong_hop_le") and d.get("loai_nguon") and d["doi"]
    assert 0 < len(d["trich"].split()) <= 15, (ten, "trích nguyên văn tối đa 15 từ (dấu … tính là một từ)")


def test_ket_luan_khac_cam_se_mien_khai_dieu_khoan_nen_bang_khong_nhan() -> None:
    """Lý do NXB «không rõ» không được ghi một giá trị riêng: `kiem_ho_so` chỉ đòi khai điều khoản khi NXB VẮNG bảng, còn NXB có
    trong bảng mà không «cam» thì cho qua. Ca kiểm tái hiện: đổi tạm một mục thành «khong_ro» ⇒ hồ sơ không khai gì cũng lọt."""
    ho_so = {"pmid": "12345678", "tieu_de_bai": "Một bài kiểm cho cổng điều khoản", "url_doc": "https://karger.com/x/1",
             "tieu_de_trang": "Một bài kiểm cho cổng điều khoản | Karger"}
    loi_cam = DTV.kiem_ho_so(dict(ho_so), date(2026, 10, 14), tep_uy_quyen=TOOLS / "khong-ton-tai.json")[0]
    assert any("Karger" in x and "KHÔNG nạp" in x for x in loi_cam)
    goc = DTV.DIEU_KHOAN_NXB[KARGER]
    try:
        DTV.DIEU_KHOAN_NXB[KARGER] = dict(goc, ket_luan="khong_ro")
        loi_khong_ro = DTV.kiem_ho_so(dict(ho_so), date(2026, 10, 14), tep_uy_quyen=TOOLS / "khong-ton-tai.json")[0]
    finally:
        DTV.DIEU_KHOAN_NXB[KARGER] = goc
    assert not any("điều khoản" in x for x in loi_khong_ro), "nếu đỏ: kiem_ho_so đã đổi — xem lại luật «bảng chỉ nhận cấm»"


def test_doctrine_khop_bang_va_bat_duoc_khi_mat_tien_to_hoac_ten() -> None:
    van_ban = DOCTRINE.read_text(encoding="utf-8")
    assert DTV.lech_doctrine(van_ban) == []
    assert any(MINERVA in x for x in DTV.lech_doctrine(van_ban.replace("`10.23736/`", "10.23736")))
    assert any(OUP in x for x in DTV.lech_doctrine(van_ban.replace("`10.1530/eje-`", "10.1530/eje-")))
    # tên xuất hiện HAI lần trong mục (tên đậm + «COPD Foundation giữ bản quyền») ⇒ phải xoá mọi lần mới tái hiện được «mất tên»
    assert any(COPD in x for x in DTV.lech_doctrine(van_ban.replace("COPD Foundation", "JCOPDF")))


T0 = datetime(2026, 10, 14, 9, 0, 0, tzinfo=timezone(timedelta(hours=7)))
CAN_CU = ("«uỷ quyền riêng cho Wiley như đã làm với J Rheumatol và cho tất cả các vấn đề tương tự khác không hỏi lại tôi nữa» "
          "(bác sĩ, 04/10/2026)")


def test_tep_uy_quyen_co_nxb_moi_thi_kiem_cua_phien_nhan(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(DTV, "DASH", tmp_path)
    so = tmp_path / "state" / "phien.json"
    tep = tmp_path / DTV.TEN_TEP_UY_QUYEN
    tep.write_text(json.dumps({"muc": [{"nxb": "Elsevier", "ngay": "2026-10-03", "can_cu": "cho máy đọc toàn văn Elsevier"}]},
                              ensure_ascii=False), encoding="utf-8")
    assert P.mo("uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    url = "https://www.tandfonline.com/doi/full/10.1080/03007995.2026.2687640"
    ma, tb = P.kiem("41000001", url, "10.1080/03007995.2026.2687640", bay_gio=T0, tep=so, dtv=DTV)
    assert ma == 3 and TF in tb and "KHÔNG thuộc phạm vi" in tb      # đã kiểm điều khoản nhưng CHƯA có uỷ quyền ⇒ vẫn dừng
    tep.write_text(json.dumps({"muc": [{"nxb": TF, "ngay": "2026-10-14", "can_cu": CAN_CU}]}, ensure_ascii=False),
                   encoding="utf-8")
    assert P.kiem("41000001", url, "10.1080/03007995.2026.2687640", bay_gio=T0, tep=so, dtv=DTV)[0] == 0
    assert TF in P.nxb_duoc_luu(DTV, T0.date())
