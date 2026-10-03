"""Bảng DIEU_KHOAN_NXB bổ sung 03/10/2026 (đọc lại điều khoản gốc cùng ngày): Scopus · Clarivate (WoS) · ESC · Springer Nature.

Luật giữ: bảng CHỈ nhận mục «cấm» (một mục «cho phép» sẽ miễn khai `dieu_khoan` cho mọi bài của NXB đó) — WHO/Frontiers/openFDA
chỉ là hướng dẫn khai theo từng bài trong doctrine; NICE/MDPI chưa đọc được ⇒ vẫn «chưa kiểm».
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("dtv_bo_sung_t", TOOLS / "doc_toan_van_co_nguoi.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
ESC = "ESC (European Society of Cardiology)"


def test_bang_chi_co_muc_cam_va_cau_trich_toi_da_15_tu() -> None:
    for ten, d in D.DIEU_KHOAN_NXB.items():
        assert d["ket_luan"] == "cam", f"{ten}: bảng chỉ nhận «cấm» — mục khác sẽ miễn khai điều khoản cho mọi bài"
        assert d.get("nguon", "").startswith("https://") and d.get("doc_luc") and d.get("duong_hop_le"), ten
        if d["trich"].startswith("CHƯA XÁC MINH NGUYÊN VĂN"):
            continue  # ADA: trang trả 403 cho máy — trường ghi rõ CHƯA có câu nguyên văn (không phải câu trích)
        so_tu = len([w for w in d["trich"].replace("…", " ").split() if w])
        assert 0 < so_tu <= 15, (ten, so_tu)


def test_muc_chua_co_cau_nguyen_van_phai_noi_ro() -> None:
    assert D.DIEU_KHOAN_NXB["ADA (American Diabetes Association)"]["trich"].startswith("CHƯA XÁC MINH NGUYÊN VĂN")


@pytest.mark.parametrize("tieu_de", [
    "2023 ESC Guidelines for the management of cardiomyopathies",
    "2026 ESC/EAS Guidelines for the management of dyslipidaemias",
    "ESC Clinical Practice Guidelines on heart failure",
])
def test_guideline_esc_dang_o_oup_hay_wiley_van_cam(tieu_de) -> None:
    assert D.nxb_cua("10.1093/eurheartj/ehad194", "https://academic.oup.com/eurheartj/article/44/37/3503/7246608", tieu_de)[0] == ESC
    assert D.nxb_cua("10.1002/ejhf.3000", "https://onlinelibrary.wiley.com/doi/10.1002/ejhf.3000", tieu_de)[0] == ESC


@pytest.mark.parametrize("tieu_de", ["Guidelines from the ESC Congress were discussed", "A trial of ESC inhibitors",
                                     "Escape guidelines for rural clinics", ""])
def test_tieu_de_khong_phai_guideline_esc_khong_bi_cam(tieu_de) -> None:
    """Không phải guideline ESC ⇒ không mang khoá ESC; từ 03/10/2026 bài trên OUP mang khoá OUP (OUP vào bảng)."""
    assert D.nxb_cua("10.1093/eurheartj/x", "https://academic.oup.com/eurheartj/x", tieu_de)[0] == "Oxford University Press"
    assert D.nxb_cua("10.9999/x", "https://example.org/x", tieu_de) == (None, None)


def test_springer_nature_cam_theo_tien_to_bmc_khong() -> None:
    assert D.nxb_cua("10.1007/s00125-026-0001-1", "")[0] == "Springer Nature"
    assert D.nxb_cua("10.1038/s41591-026-0001-1", "")[0] == "Springer Nature"
    assert D.nxb_cua("10.1186/s12916-026-0001-1", "https://bmcmedicine.biomedcentral.com/articles/x") == (None, None), \
        "BMC toàn OA — không được chặn theo tiền tố"


@pytest.mark.parametrize("doi,ten", [
    ("10.1093/jcem/dgad001", "Oxford University Press"), ("10.1210/jc.2015-1710", "Oxford University Press"),
    ("10.1164/rccm.202301-0001OC", "Oxford University Press"), ("10.1056/NEJMoa2400001", "Massachusetts Medical Society (NEJM)"),
    ("10.1001/jama.2026.1", "American Medical Association (JAMA Network)"), ("10.1542/peds.2026-1", "American Academy of Pediatrics"),
    ("10.1177/0333102418754880", "SAGE Publishing"), ("10.1136/gutjnl-2021-324598", "BMJ Publishing Group"),
    ("10.7326/M23-0001", "American College of Physicians (Annals)"),
    ("10.1161/CIR.0000000000001001", "Wolters Kluwer Health (LWW · AHA journals · Neurology)"),
    ("10.1212/WNL.0000000000200001", "Wolters Kluwer Health (LWW · AHA journals · Neurology)"),
    ("10.1097/HJH.0000000000003001", "Wolters Kluwer Health (LWW · AHA journals · Neurology)"),
])
def test_dot_doc_dieu_khoan_03_10_nhan_dung_khoa(doi, ten) -> None:
    """Đợt đọc điều khoản 03/10/2026 (phủ hiệp hội/tạp chí uy tín cho làn Chrome): tám NXB «cấm»/«không rõ ⇒ xử như cấm»."""
    assert D.nxb_cua(doi, "")[0] == ten, doi


def test_guideline_esc_tren_oup_van_mang_khoa_esc_khong_phai_oup() -> None:
    """Thứ tự trong `nxb_cua`: tiêu đề ESC xét TRƯỚC tiền tố — đảo lại thì guideline ESC thành «OUP» và mất đường cấp phép ESC."""
    assert D.nxb_cua("10.1093/eurheartj/ehag100", "https://academic.oup.com/eurheartj/x",
                     "2026 ESC Guidelines for the management of heart failure")[0] == ESC


def test_ban_tdm_cua_nxb_tinh_la_may_co_toan_van_nhung_khong_phai_oa(tmp_path) -> None:
    """PDF Wiley TDM (`PMID-<n>_WTDM.pdf`, token của bác sĩ) ⇒ «tdm_nxb»: máy có toàn văn, KHÔNG gọi là OA."""
    (tmp_path / "PMID-111_WTDM.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "PMID-222_UPW.pdf").write_bytes(b"%PDF-1.4")
    tt = D.bao_phu_cuc_bo(["111", "222", "333"], kho=tmp_path)
    assert tt == {"111": "tdm_nxb", "222": "oa_khac", "333": "chua_co"}, tt
    assert "tdm_nxb" in D.TRANG_THAI_MAY_CO_TOAN_VAN


def test_nice_mdpi_who_frontiers_van_chua_kiem() -> None:
    for url in ("https://www.nice.org.uk/guidance/ng28", "https://www.mdpi.com/2077-0383/15/11/4218",
                "https://iris.who.int/handle/10665/1", "https://www.frontiersin.org/articles/10.3389/x"):
        assert D.nxb_cua("", url) == (None, None), url


def test_ho_so_guideline_esc_tren_oup_bi_tu_choi(tmp_path) -> None:
    """Cổng `kiem_ho_so` dùng tiêu đề hồ sơ: guideline ESC đăng trên OUP (NXB chưa kiểm) không được lọt nhờ khai «cho_phep»."""
    hs = {"tieu_de_bai": "2023 ESC Guidelines for the management of cardiomyopathies",
          "tieu_de_trang": "2023 ESC Guidelines for the management of cardiomyopathies | European Heart Journal | Oxford Academic",
          "doi": "10.1093/eurheartj/ehad194", "url_doc": "https://academic.oup.com/eurheartj/article/44/37/3503/7246608",
          "dieu_khoan": {"url": "https://academic.oup.com/pages/terms", "doc_luc": "2026-10-03", "ket_luan": "cho_phep", "trich": "x"}}
    loi, _cb, _tt = D.kiem_ho_so(hs, D.date(2026, 10, 3), None, tmp_path / "khong-co.json")
    assert any("ESC" in x and "cấm" in x for x in loi), loi


def test_nhanh_xuat_ban_elsevier_nhan_dung_khoa() -> None:
    """03/10/2026: Gastroenterology/AJKD mang DOI 10.1053 (Saunders — Crossref xác nhận Elsevier BV) từng rơi vào «chưa kiểm»."""
    for doi in ("10.1053/j.gastro.2026.01.001", "10.1053/j.ajkd.2026.01.001", "10.1067/j.cpcardiol.2026.1", "10.1054/x",
                "10.1006/x", "10.1078/x", "10.1383/x", "10.1157/x"):
        assert D.nxb_cua(doi, "")[0] == "Elsevier", doi
    assert D.nxb_cua("", "https://www.gastrojournal.org/article/x")[0] == "Elsevier"
