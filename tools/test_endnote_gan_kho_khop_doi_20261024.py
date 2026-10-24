# -*- coding: utf-8 -*-
"""`--gan-kho` khớp bản ghi KHÔNG mang PMID thuần số ở «Accession Number» (24/10/2026).

Sự cố đo 24/10/2026 trên thư viện thật: 144 bản ghi «chỉ có DOI»; 90 trong đó có PMID trên PubMed (esearch <doi>[doi] trả
đúng một PMID, esummary ghi lại đúng DOI) nhưng Accession Number là «WOS:…» (84 — nhập từ Web of Science) hoặc «PMID: n» (6).
`gan_kho` chỉ tìm Accession Number == PMID thuần số ⇒ gom về 57 toàn văn mà «0 có bản ghi trong thư viện · gắn thêm 0»; PDF
nằm im trong kho. Nay thêm hai bậc cho PMID còn thiếu: «PMID: n», rồi DOI của PMID với trường DOI — bỏ bản ghi có Accession
Number là MỘT PMID KHÁC; tra DOI lỗi ⇒ «không đo được», không gắn theo DOI lượt đó.
Ngoại tuyến; EndNote giả; mọi tệp trong tmp_path.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


N = _nap("_nec_gkd_t1024", "nap_endnote_chu_de.py")


class _EndNote:
    """Giả lập các lệnh `gan_kho` dùng: tìm KHỚP NGUYÊN (không phân biệt hoa/thường) như `EndNoteMac.tim_khop`, đọc trường,
    đếm tệp đính kèm, gắn tệp."""

    def __init__(self, thu_vien: Path, ban_ghi: list[tuple[str, str, str]]):
        self.thu_vien = thu_vien
        self.bg = [{"id": f'<RecordID database="1" recNum="{i + 1}" />', "acc": a, "doi": d, "tep": t}
                   for i, (a, d, t) in enumerate(ban_ghi)]
        self.doc_acc: list[list[str]] = []

    def _truong(self, truong):
        return {"Accession Number": "acc", "DOI": "doi"}[truong]

    def tim_khop(self, gia_tri, truong):
        k = self._truong(truong)
        return {v: [b["id"] for b in self.bg if b[k] and b[k].lower() == v.lower()] for v in gia_tri}

    def doc_truong(self, ids, truong):
        if truong == "Accession Number":
            self.doc_acc.append(list(ids))
        k = self._truong(truong)
        return {b["id"]: b[k] for b in self.bg if b["id"] in ids}

    def tep_dinh_kem(self, ids):
        return {b["id"]: len(b["tep"]) for b in self.bg if b["id"] in ids}

    def gan_tep(self, ma, url):
        next(b for b in self.bg if b["id"] == ma)["tep"] = url


@pytest.fixture
def kho_tv(tmp_path):
    kho = tmp_path / "kho"
    kho.mkdir()
    for pm in ("111", "222", "333", "444", "555"):
        (kho / f"PMID-{pm}_BANIN.pdf").write_bytes(b"%PDF-1.4 x")
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"")
    return kho, tv


def _doi(pmids):
    bang = {"222": "10.1000/AB.222", "333": "10.1000/ab.333", "444": "10.1000/ab.444", "555": "10.1000/ab.555"}
    return {p: N.chuan_doi(bang[p]) for p in pmids if p in bang}


def test_khop_pmid_tien_to_va_doi_cho_ban_ghi_wos(kho_tv):
    kho, tv = kho_tv
    en = _EndNote(tv, [
        ("111", "", ""),                              # PMID thuần số — như trước
        ("PMID: 222", "10.1000/ab.222", ""),          # «PMID: n» — đo trên thư viện thật (rec 6334…)
        ("WOS:001192610300001", "10.1000/AB.333", ""),  # nhập từ Web of Science: chỉ khớp được qua DOI
        ("999", "10.1000/ab.444", ""),                # DOI khớp nhưng Accession Number là PMID KHÁC ⇒ không gắn
        ("WOS:000000000000001", "10.1000/ab.555", "internal-pdf://1/cua-bac-si.pdf"),  # đã có tệp ⇒ không ghi đè
    ])
    bc = N.gan_kho(en, kho, None, True, doi_cua=_doi)
    assert (bc["khop_pmid_tien_to"], bc["khop_doi"]) == (1, 2), bc
    assert bc["co_ban_ghi"] == 4 and bc["gan_them_pdf"] == 3, bc
    tep = {b["acc"]: b["tep"] for b in en.bg}
    assert re.fullmatch(r"internal-pdf://\d{10}/PMID-111\.pdf", tep["111"])
    assert re.fullmatch(r"internal-pdf://\d{10}/PMID-222\.pdf", tep["PMID: 222"])
    assert re.fullmatch(r"internal-pdf://\d{10}/PMID-333\.pdf", tep["WOS:001192610300001"])
    assert tep["999"] == "", "Accession Number là PMID khác ⇒ định danh mâu thuẫn, không gắn theo DOI"
    assert tep["WOS:000000000000001"] == "internal-pdf://1/cua-bac-si.pdf", "không ghi đè tệp đã có"
    assert N.gan_kho(en, kho, None, True, doi_cua=_doi)["gan_them_pdf"] == 0, "chạy lại không gắn lần hai"


def test_chi_tra_doi_cho_pmid_con_thieu(kho_tv):
    kho, tv = kho_tv
    hoi: list[list[str]] = []
    en = _EndNote(tv, [("111", "", ""), ("PMID: 222", "", ""), ("WOS:1", "10.1000/ab.333", "")])
    N.gan_kho(en, kho, None, False, doi_cua=lambda ds: (hoi.append(list(ds)), _doi(ds))[1])
    assert hoi == [["333", "444", "555"]], "chỉ PMID chưa khớp ở hai bậc trước mới đi tra DOI"


def test_tra_doi_loi_la_khong_do_duoc_va_van_giu_bac_tien_to(kho_tv):
    kho, tv = kho_tv
    en = _EndNote(tv, [("PMID: 222", "", ""), ("WOS:1", "10.1000/ab.333", "")])

    def hong(_ds):
        raise OSError("NCBI và Europe PMC đều không trả lời")

    bc = N.gan_kho(en, kho, None, False, doi_cua=hong)
    assert "OSError" in bc["doi_khong_do_duoc"] and bc["khop_doi"] == 0
    assert bc["khop_pmid_tien_to"] == 1 and bc["se_gan_pdf"] == 1


def test_khong_doi_cua_thi_hanh_vi_cu(kho_tv):
    kho, tv = kho_tv
    en = _EndNote(tv, [("WOS:1", "10.1000/ab.333", "")])
    bc = N.gan_kho(en, kho, None, False)
    assert bc["khop_doi"] == 0 and bc["se_gan_pdf"] == 0 and en.doc_acc == []


def test_la_pmid_khac():
    assert N._la_pmid_khac("999", "333") and N._la_pmid_khac("PMID: 999", "333")
    assert not N._la_pmid_khac("333", "333") and not N._la_pmid_khac("PMID:333", "333")
    assert not N._la_pmid_khac("WOS:001192610300001", "333") and not N._la_pmid_khac("", "333")


def test_doi_cua_pmid_lui_sang_europe_pmc_va_chuan_hoa():
    def pm_hong(_ds):
        raise RuntimeError("NCBI chặn IP")

    ep = lambda ds: {"1": {"doi": "https://doi.org/10.1000/X.1"}, "2": {"doi": ""}, "3": {}}  # noqa: E731
    assert N.doi_cua_pmid(["1", "2", "3"], lay_pm=pm_hong, lay_ep=ep) == {"1": "10.1000/x.1"}


def test_main_gan_kho_truyen_tra_doi(monkeypatch, tmp_path, capsys):
    """CLI `--gan-kho` (mọi công cụ sinh PDF gọi qua đây) phải truyền `doi_cua_pmid` — không thì bậc DOI chết lặng."""
    nhan: dict = {}

    def gia(endnote, kho, pmids, ap_dung, doi_cua=None):
        nhan["doi_cua"] = doi_cua
        return {"kho_toan_van": True, "pdf_trong_kho": 1, "co_ban_ghi": 1, "se_gan_pdf": 1, "khop_doi": 1,
                "khop_pmid_tien_to": 0}

    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"")
    (tmp_path / "kho").mkdir()

    class _Mo:
        def __init__(self, ung_dung, thu_vien):
            self.thu_vien = thu_vien

        def dang_mo_dung_thu_vien(self):
            return True

    monkeypatch.setattr(N, "gan_kho", gia)
    monkeypatch.setattr(N, "doc_cau_hinh", lambda tep=None: {"thu_vien": str(tv), "ung_dung": "EndNote 2025"})
    monkeypatch.setattr(N, "EndNoteMac", _Mo)
    monkeypatch.setattr(N, "_la_mac", lambda: True)
    assert N.main(["--gan-kho", "--kho-toan-van", str(tmp_path / "kho")]) == 0
    assert nhan["doi_cua"] is N.doi_cua_pmid
    assert "khớp DOI 1" in capsys.readouterr().out
