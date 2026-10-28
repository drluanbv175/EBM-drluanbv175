# -*- coding: utf-8 -*-
"""Bài tổng thuật → EndNote (28/10/2026) — `nap_endnote_chu_de.py --tong-thuat`.

Bác sĩ hỏi bài tổng thuật suy tim «đã có sự kết nối với Endnote chưa»: chưa — công cụ nạp chỉ nhận dashboard (khối DATA) và
đề tài (DANH_MUC_TRICH_DAN). Bài tổng thuật (skill tong-thuat-chung-cu) mang danh mục Vancouver đánh số dưới «## Nguồn», mỗi
dòng có PMID và/hoặc doi. Ngoại tuyến hoàn toàn: không EndNote, metadata giả.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


NE = _nap("tools/nap_endnote_chu_de.py", "_nap_endnote_tong_thuat_test")

BAI = """# Suy tim ở người lớn: tiếp cận chẩn đoán, điều trị và tiên lượng

Thân bài trích [1] và [2]; dòng «1. PMID 99999999» trong thân bài KHÔNG phải nguồn.

1. PMID 99999999 · doi:10.9999/khong-phai-nguon

Cần bác sĩ kiểm chứng.

## Nguồn

1. Køber L, Adamo M, và cs. 2026 ESC Guidelines for the management of heart failure. *Eur Heart J* 2026;47(38):5346-5457. \
PMID 42661420 · doi:10.1093/eurheartj/ehag100
2. Damman K, và cs. 2026 ESC Guidelines CKD. *Eur Heart J* 2026 [bản điện tử trước in]. doi:10.1093/eurheartj/ehag098
3. Tổ chức X. Một tài liệu không định danh. 2026.
4. Bavendiek U, và cs. Digitoxin in HFrEF. *N Engl J Med* 2025;393(12):1155-1165. PMID 40879434

Ghi chú thẩm định: đoạn này nằm sau danh mục, không bắt đầu bằng số thứ tự.
"""


def _bai(tmp_path: Path, ten: str = "TT_suy-tim-toan-dien_20261028.md", noi_dung: str = BAI) -> Path:
    tep = tmp_path / ten
    tep.write_text(noi_dung, encoding="utf-8", newline="\n")
    return tep


def test_chi_doc_muc_nguon_va_tach_pmid_doi(tmp_path):
    data, gia = NE.doc_tong_thuat(_bai(tmp_path))
    assert data["meta"]["question"] == "Suy tim ở người lớn: tiếp cận chẩn đoán, điều trị và tiên lượng"
    assert data["items"] == [
        {"id": "TT-1", "pmid": "42661420", "doi": "10.1093/eurheartj/ehag100"},
        {"id": "TT-2", "pmid": None, "doi": "10.1093/eurheartj/ehag098"},
        {"id": "TT-4", "pmid": "40879434", "doi": None},
    ], "dòng không định danh bị bỏ, dòng trong thân bài không bị lấy"
    assert gia == Path("TONG-THUAT_suy-tim-toan-dien.json")
    assert NE.khoa_chu_de(gia) == "TONG-THUAT_suy-tim-toan-dien", "khoá bền qua các bản cập nhật của cùng bài"


def test_dinh_danh_qua_trich_dinh_danh_chuan_hoa_doi(tmp_path):
    data, _ = NE.doc_tong_thuat(_bai(tmp_path))
    dd = NE.trich_dinh_danh(data)
    assert [(d["pmid"], d["doi"]) for d in dd] == [
        ("42661420", "10.1093/eurheartj/ehag100"), (None, "10.1093/eurheartj/ehag098"), ("40879434", None)]


def test_khong_co_muc_nguon_la_loi_khong_nap(tmp_path):
    with pytest.raises(NE.KhongChayDuoc, match="Nguồn"):
        NE.doc_tong_thuat(_bai(tmp_path, noi_dung="# Bài\n\nThân bài không có danh mục.\n"))


def test_muc_nguon_khong_dinh_danh_nao_la_loi(tmp_path):
    with pytest.raises(NE.KhongChayDuoc, match="PMID/DOI"):
        NE.doc_tong_thuat(_bai(tmp_path, noi_dung="# Bài\n\n## Nguồn\n\n1. Sách không định danh. 2020.\n"))


def test_thieu_tep_la_loi(tmp_path):
    with pytest.raises(NE.KhongChayDuoc, match="không thấy"):
        NE.doc_tong_thuat(tmp_path / "TT_khong-co_20261028.md")


def test_lap_ke_hoach_nhom_tt_khong_can_endnote(tmp_path):
    data, gia = NE.doc_tong_thuat(_bai(tmp_path))

    def meta(pmid=None, doi=None):
        return {"pmid": pmid, "doi": doi, "loai_tl": "Journal Article", "tieu_de": f"Bài {pmid or doi}", "tac_gia": ["A, B"],
                "tap_chi": "Eur Heart J", "tap_chi_viet_tat": "", "nam": "2026", "tap": "47", "so": "38", "trang": "1",
                "issn": "", "tom_tat": "", "ngon_ngu": "eng", "pmcid": "", "da_rut": False, "nguon_meta": "PubMed"}

    bc = NE.nap_chu_de(gia, endnote=None, ap_dung=False, kho=None, doc_data=lambda _p: data,
                       tien_to=NE.TIEN_TO_NHOM_TONG_THUAT,
                       lay_pm=lambda pmids, **_: {p: meta(pmid=p) for p in pmids},
                       lay_cr=lambda doi, **_: meta(doi=doi),
                       lay_ep=lambda pmids, **_: {})
    assert bc["nhom"] == "TT · Suy tim ở người lớn: tiếp cận chẩn đoán, điều trị và tiên lượng"
    assert bc["so_trich_dan"] == 3
    assert bc["kiem_trung"] is False and bc["ap_dung"] is False


def test_main_tong_thuat_khong_di_cung_file_hoac_de_tai(tmp_path, capsys):
    tep = str(_bai(tmp_path))
    assert NE.main(["--tong-thuat", tep, "--file", "x.html"]) == NE.MA_THAM_SO
    assert NE.main(["--tong-thuat", tep, "--de-tai", "NC-THU"]) == NE.MA_THAM_SO
    assert "--tong-thuat không đi cùng" in capsys.readouterr().out


def test_main_tong_thuat_tep_hong_tra_khong_chay(tmp_path, capsys):
    tep = _bai(tmp_path, noi_dung="# Bài không có danh mục\n")
    assert NE.main(["--tong-thuat", str(tep)]) == NE.MA_KHONG_CHAY
    assert "Nguồn" in capsys.readouterr().out
