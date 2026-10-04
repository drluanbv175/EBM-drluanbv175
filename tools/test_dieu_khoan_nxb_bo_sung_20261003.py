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
    assert D.nxb_cua("10.1093/eurheartj/x", "https://academic.oup.com/eurheartj/x", tieu_de) == (None, None)


def test_springer_nature_cam_theo_tien_to_bmc_khong() -> None:
    assert D.nxb_cua("10.1007/s00125-026-0001-1", "")[0] == "Springer Nature"
    assert D.nxb_cua("10.1038/s41591-026-0001-1", "")[0] == "Springer Nature"
    assert D.nxb_cua("10.1186/s12916-026-0001-1", "https://bmcmedicine.biomedcentral.com/articles/x") == (None, None), \
        "BMC toàn OA — không được chặn theo tiền tố"


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
