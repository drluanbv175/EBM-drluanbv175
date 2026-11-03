# -*- coding: utf-8 -*-
"""Rà ĐỊNH DANH các PDF ĐÃ có trong kho toàn văn (03/11/2026 — `audit/nhat-ky/2026-11-03-ra-dinh-danh-kho-toan-van.md`).

Cổng BH175 chỉ gác tệp MỚI tải về; `tools/ra_dinh_danh_kho_toan_van.py` rà tệp CŨ bằng đúng cổng đó với định danh lấy từ PubMed /
Europe PMC / Crossref. Hai ca đối chứng có thật:
  • 39186635 — bài thật «Hypoxia-Inducible Factor Prolyl Hydroxylase Inhibitors in Kidney Disease» (NEJM Evid 2024); tệp kho là
    «Dapagliflozin and anemia in patients with chronic kidney disease» (Koshino et al.);
  • 42701440 — bài thật «Addressing Cardiopulmonary Risk in COPD: …» (Int J COPD 2026); tệp kho là NCHS Data Brief 521.
Khoá: hai ca bị bắt · lỗi mạng KHÔNG thành «khớp» · NCBI chặn ⇒ Europe PMC · chạy khô không dời gì · `--cach-ly --ap-dung --pmid`
chỉ dời đúng tệp sai bài đã duyệt (dời, không xoá) · EndNote chỉ đọc, kể cả khi bản sao sdb.eni đọc lỗi.
Ngoại tuyến hoàn toàn (urlopen giả, PDF giả hợp lệ dựng bằng `pdf_gia_kiem_thu.py`).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

pytest.importorskip("pypdf", reason="cổng định danh PDF cần pypdf (CI cài sẵn)")

REPO = Path(__file__).resolve().parents[1]


def _nap(tep: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


r = _nap("ra_dinh_danh_kho_toan_van.py", "_ra_dinh_danh_1103")
pdf_gia = _nap("pdf_gia_kiem_thu.py", "_pdf_gia_ra_1103")

EMAIL = "kiem-thu@example.org"
HIF, HIF_DOI = "39186635", "10.1056/EVIDoa2300189"
HIF_TIEU_DE = "Hypoxia-Inducible Factor Prolyl Hydroxylase Inhibitors in Kidney Disease."
COPD, COPD_DOI = "42701440", "10.2147/COPD.S596426"
COPD_TIEU_DE = ("Addressing Cardiopulmonary Risk in COPD: A Multidisciplinary Expert Opinion Framework for the United States "
                "Healthcare System.")
DUNG, DUNG_DOI = "11111111", "10.1000/dung.2025.1"
DUNG_TIEU_DE = "Sodium glucose cotransporter inhibitors and cardiovascular outcomes in heart failure."
CHI_DOI, CHI_DOI_DOI = "22222222", "10.1000/chidoi.7"
CHI_DOI_TIEU_DE = "KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease."
GOC, GOC_DOI = "55555555", "10.1000/goc.3"

# Hai tệp sai bài mô phỏng đúng ca thật: cùng chủ đề (thận / tử vong) nên vài từ của tiêu đề có mặt, nhưng dưới ngưỡng 60%.
PDF_DAPA = pdf_gia.pdf_co_chu(
    "1 Dapagliflozin and anemia in patients with chronic kidney disease Akihiko Koshino, Meir Schechter, Glenn M. Chertow. "
    "Background: anemia is common in patients with chronic kidney disease. " + "hemoglobin hematocrit dapagliflozin placebo " * 30,
    "Methods " + "trial participants randomized " * 60)
PDF_NCHS = pdf_gia.pdf_co_chu(
    "NCHS reports can be downloaded from cdc.gov. NCHS Data Brief No. 521 December 2024 Mortality in the United States, 2023. "
    "Sherry L. Murphy, Kenneth D. Kochanek. Key findings: life expectancy increased. " + "death rates age group leading causes " * 30)
PDF_DUNG = pdf_gia.pdf_co_chu(DUNG_TIEU_DE + " Original article. " + "randomized trial hospitalization endpoint " * 40)
PDF_CHI_DOI = pdf_gia.pdf_co_chu("Kidney International Supplements volume 105. https://doi.org/" + CHI_DOI_DOI + " "
                                 + "recommendation practice point evaluation " * 40)
PDF_GOC = pdf_gia.pdf_co_chu("Traitement de l'hypertension arterielle chez le sujet age: recommandations de la societe francaise. "
                             + "pression arterielle traitement patient " * 40)
PDF_ANH = pdf_gia.pdf_co_chu("")

PUBMED = {
    HIF: {"uid": HIF, "title": HIF_TIEU_DE, "vernaculartitle": "", "articleids": [{"idtype": "doi", "value": HIF_DOI}]},
    COPD: {"uid": COPD, "title": COPD_TIEU_DE, "vernaculartitle": "", "articleids": [{"idtype": "doi", "value": COPD_DOI}]},
    DUNG: {"uid": DUNG, "title": DUNG_TIEU_DE, "vernaculartitle": "", "articleids": [{"idtype": "doi", "value": DUNG_DOI}]},
    CHI_DOI: {"uid": CHI_DOI, "title": CHI_DOI_TIEU_DE, "vernaculartitle": "",
              "articleids": [{"idtype": "doi", "value": CHI_DOI_DOI}]},
    GOC: {"uid": GOC, "title": "[Treatment of hypertension in older adults: French society recommendations].",
          "vernaculartitle": "Traitement de l'hypertension arterielle chez le sujet age: recommandations de la societe francaise.",
          "articleids": [{"idtype": "doi", "value": GOC_DOI}]},
}
CROSSREF = {HIF_DOI: HIF_TIEU_DE, COPD_DOI: COPD_TIEU_DE, DUNG_DOI: DUNG_TIEU_DE, CHI_DOI_DOI: CHI_DOI_TIEU_DE}


class _Mang:
    """urlopen giả: PubMed esummary · Europe PMC · Crossref. `loi` = chuỗi trong URL ⇒ URLError; `ncbi_chan` ⇒ trang chặn."""

    def __init__(self, *, pubmed=None, epmc=None, crossref=None, loi=(), ncbi_chan=False):
        self.pubmed = PUBMED if pubmed is None else pubmed
        self.epmc = epmc or {}
        self.crossref = CROSSREF if crossref is None else crossref
        self.loi, self.ncbi_chan, self.goi = tuple(loi), ncbi_chan, []

    def __call__(self, req, timeout=None, context=None):
        url = req if isinstance(req, str) else req.full_url
        self.goi.append(url)
        if any(k in url for k in self.loi):
            raise urllib.error.URLError("mạng đứt (giả)")
        if "esummary.fcgi" in url:
            if self.ncbi_chan:
                return io.BytesIO(b"<html><title>NCBI - WWW Error Blocked Diagnostic</title></html>")
            ids = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["id"][0].split(",")
            kq = {"uids": ids}
            for i in ids:
                kq[i] = self.pubmed.get(i, {"uid": i, "error": "cannot get document summary"})
            return io.BytesIO(json.dumps({"result": kq}).encode())
        if "europepmc" in url:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["query"][0]
            hang = [dict(self.epmc[p], pmid=p) for p in re.findall(r"EXT_ID:(\d+)", q) if p in self.epmc]
            return io.BytesIO(json.dumps({"resultList": {"result": hang}}).encode())
        if "api.crossref.org" in url:
            doi = urllib.parse.unquote(url.split("/works/", 1)[1].split("?", 1)[0])
            if doi not in self.crossref:
                raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
            return io.BytesIO(json.dumps({"message": {"title": [self.crossref[doi]]}}).encode())
        raise AssertionError("URL ngoài kịch bản: " + url)


@pytest.fixture
def mang(monkeypatch):
    def _dat(**kw):
        m = _Mang(**kw)
        monkeypatch.setattr(urllib.request, "urlopen", m)
        return m
    monkeypatch.setattr(r.time, "sleep", lambda s: None)
    monkeypatch.setattr(r.g, "_email_lich_su", lambda: EMAIL)
    return _dat


def _kho(tmp_path: Path, tep: dict[str, bytes]) -> Path:
    kho = tmp_path / "EBM-Dashboards" / "toan_van_oa"
    kho.mkdir(parents=True)
    for ten, b in tep.items():
        (kho / ten).write_bytes(b)
    return kho


def _theo_ten(ds) -> dict:
    return {kq.tep.name: kq for kq in ds}


# ───────────────────────── hai ca đối chứng ─────────────────────────

def test_hai_ca_doi_chung_bi_bat_va_tep_dung_van_khop(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA, f"PMID-{COPD}_UPW.pdf": PDF_NCHS, f"PMID-{DUNG}_CHR.pdf": PDF_DUNG})
    ds, la, _tt, _en = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    kq = _theo_ten(ds)
    assert not la
    assert kq[f"PMID-{HIF}_UPW.pdf"].nhom == r.SAI_BAI
    assert kq[f"PMID-{COPD}_UPW.pdf"].nhom == r.SAI_BAI
    assert kq[f"PMID-{DUNG}_CHR.pdf"].nhom == r.KHOP and kq[f"PMID-{DUNG}_CHR.pdf"].can_cu == "tiêu đề PubMed"
    # tệp sai bài kèm chữ đầu trang 1 — bác sĩ thấy tệp thực ra là bài gì
    assert "Dapagliflozin and anemia" in kq[f"PMID-{HIF}_UPW.pdf"].dau_trang
    assert "Mortality in the United States" in kq[f"PMID-{COPD}_UPW.pdf"].dau_trang
    assert kq[f"PMID-{HIF}_UPW.pdf"].tieu_de.startswith("Hypoxia-Inducible Factor")  # định danh từ PubMed, không từ tên tệp


def test_tieu_de_crossref_duoc_thu_truoc_khi_ket_luan_sai_bai(tmp_path, mang):
    m = mang()
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA})
    r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert any("api.crossref.org" in u and "EVIDoa2300189" in u for u in m.goi)


# ───────────────────────── lỗi mạng không bao giờ thành khớp ─────────────────────────

def test_loi_mang_ca_hai_nguon_la_khong_do_duoc_khong_phai_khop(tmp_path, mang):
    mang(loi=("esummary.fcgi", "europepmc"))
    kho = _kho(tmp_path, {f"PMID-{DUNG}_CHR.pdf": PDF_DUNG, f"PMID-{HIF}_UPW.pdf": PDF_DAPA})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert {kq.nhom for kq in ds} == {r.KHONG_DO_DUOC}
    assert all("lỗi mạng" in kq.ly_do for kq in ds)


def test_ncbi_chan_thi_lay_qua_europe_pmc_va_khong_goi_ncbi_nua(tmp_path, mang):
    epmc = {DUNG: {"title": DUNG_TIEU_DE, "doi": DUNG_DOI}, HIF: {"title": HIF_TIEU_DE, "doi": HIF_DOI}}
    m = mang(ncbi_chan=True, epmc=epmc)
    kho = _kho(tmp_path, {f"PMID-{DUNG}_CHR.pdf": PDF_DUNG, f"PMID-{HIF}_UPW.pdf": PDF_DAPA})
    ds, _la, tt, _en = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    kq = _theo_ten(ds)
    assert tt.get("ncbi_chan")
    assert kq[f"PMID-{DUNG}_CHR.pdf"].nhom == r.KHOP and kq[f"PMID-{DUNG}_CHR.pdf"].nguon_dinh_danh == "Europe PMC"
    assert kq[f"PMID-{HIF}_UPW.pdf"].nhom == r.SAI_BAI
    assert sum("esummary.fcgi" in u for u in m.goi) == 1


def test_loi_crossref_khong_lam_sai_bai_thanh_khop(tmp_path, mang):
    mang(loi=("api.crossref.org",))
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert ds[0].nhom == r.SAI_BAI
    assert any("Crossref: KHÔNG ĐO ĐƯỢC" in c for c in ds[0].ghi_chu)


def test_pubmed_va_europe_pmc_khong_co_ban_ghi_la_khong_kiem_duoc(tmp_path, mang):
    mang(pubmed={})
    kho = _kho(tmp_path, {"PMID-99999999_UPW.pdf": PDF_DUNG})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert ds[0].nhom == r.KHONG_KIEM_DUOC and "không có bản ghi" in ds[0].ly_do


# ───────────────────────── các đường khớp / không kiểm được ─────────────────────────

def test_khop_chi_nho_doi_duoc_doi_chieu_crossref(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{CHI_DOI}_WTDM.pdf": PDF_CHI_DOI})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert ds[0].nhom == r.KHOP and ds[0].can_cu == "chỉ DOI"
    assert "Crossref: DOI cùng tiêu đề" in ds[0].ghi_chu


def test_doi_trong_pdf_nhung_crossref_ghi_bai_khac_thi_khong_kiem_duoc(tmp_path, mang):
    mang(crossref={CHI_DOI_DOI: "Effect of tea consumption on bone mineral density in postmenopausal women"})
    kho = _kho(tmp_path, {f"PMID-{CHI_DOI}_WTDM.pdf": PDF_CHI_DOI})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert ds[0].nhom == r.KHONG_KIEM_DUOC and "Crossref ghi DOI này" in ds[0].ly_do


def test_tieu_de_nguyen_ngu_cuu_bai_khong_phai_tieng_anh(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{GOC}_UPW.pdf": PDF_GOC})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert ds[0].nhom == r.KHOP and ds[0].can_cu == "tiêu đề nguyên ngữ"


def test_pdf_anh_va_tep_khong_phai_pdf_la_khong_kiem_duoc(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{DUNG}_CHR.pdf": PDF_ANH, f"PMID-{HIF}_CHR.pdf": b"<html><body>Access denied</body></html>"})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    kq = _theo_ten(ds)
    assert kq[f"PMID-{DUNG}_CHR.pdf"].nhom == r.KHONG_KIEM_DUOC and "không có chữ" in kq[f"PMID-{DUNG}_CHR.pdf"].ly_do
    assert kq[f"PMID-{HIF}_CHR.pdf"].nhom == r.KHONG_KIEM_DUOC and "không phải PDF" in kq[f"PMID-{HIF}_CHR.pdf"].ly_do


def test_thieu_pypdf_la_khong_do_duoc(tmp_path, mang, monkeypatch):
    mang()

    def _thieu(_b):
        raise ImportError("No module named 'pypdf'", name="pypdf")
    monkeypatch.setattr(r.g._nap_ttcc(), "tach_trang", _thieu)
    kho = _kho(tmp_path, {f"PMID-{DUNG}_CHR.pdf": PDF_DUNG})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert ds[0].nhom == r.KHONG_DO_DUOC and "pypdf" in ds[0].ly_do


def test_dung_chung_cong_bh175(tmp_path, mang, monkeypatch):
    """Kết luận phải đi qua `gom_toan_van_dashboard.kiem_dinh_danh_upw` — không có logic so khớp song song."""
    mang()
    goi = []
    goc = r.g.kiem_dinh_danh_upw

    def _boc(*a, **kw):
        goi.append(kw)
        return goc(*a, **kw)
    monkeypatch.setattr(r.g, "kiem_dinh_danh_upw", _boc)
    kho = _kho(tmp_path, {f"PMID-{DUNG}_CHR.pdf": PDF_DUNG})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert ds[0].nhom == r.KHOP and goi and goi[0]["loai"] == "pdf"


def test_zenodo_dat_ten_theo_doi_dung_so_tai(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {})
    z = kho / "zenodo_hub_20261018"
    z.mkdir()
    tieu_de = "What do the KDIGO guidelines recommend for anemia management?"
    (z / "DOI-10.5281_zenodo.20834906.pdf").write_bytes(pdf_gia.pdf_co_chu(tieu_de + " " + "answer evidence summary " * 40))
    (z / "_tai_ve.json").write_text(json.dumps([{"doi": "10.5281/zenodo.20834906", "title": tieu_de,
                                                 "tep": "DOI-10.5281_zenodo.20834906.pdf"}]), encoding="utf-8")
    (kho / "ghi-chu-la.pdf").write_bytes(PDF_DUNG)
    ds, la, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert [(kq.hau_to, kq.nhom, kq.doi) for kq in ds] == [("ZENODO", r.KHOP, "10.5281/zenodo.20834906")]
    assert [p.name for p in la] == ["ghi-chu-la.pdf"]  # PDF tên lạ được báo, không lặng lẽ bỏ


# ───────────────────────── chạy khô, báo cáo, cách ly ─────────────────────────

def test_chay_kho_khong_doi_gi_va_bao_cao_phu_moi_tep(tmp_path, mang):
    mang()
    tep = {f"PMID-{HIF}_UPW.pdf": PDF_DAPA, f"PMID-{COPD}_UPW.pdf": PDF_NCHS, f"PMID-{DUNG}_CHR.pdf": PDF_DUNG,
           f"PMID-{DUNG}_BANIN.pdf": PDF_DUNG}
    kho = _kho(tmp_path, tep)
    truoc = sorted(p.name for p in kho.iterdir())
    ma = r.main(["--kho", str(kho), "--khong-endnote", "--cach-ly"])
    assert ma == 1
    assert sorted(p.name for p in kho.iterdir()) == truoc
    assert not (kho.parent / r.THU_MUC_CACH_LY).exists()
    bc = (kho.parent / r.TEN_BAO_CAO).read_text(encoding="utf-8")
    for ten in tep:
        assert f"`{ten}`" in bc  # mọi PDF có mặt trong báo cáo
    assert f"--cach-ly --ap-dung --pmid {HIF} {COPD}" in bc


def test_ap_dung_can_cach_ly_va_pmid_da_duyet(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA})
    assert r.main(["--kho", str(kho), "--khong-endnote", "--ap-dung"]) == 3
    assert r.main(["--kho", str(kho), "--khong-endnote", "--cach-ly", "--ap-dung"]) == 3
    assert (kho / f"PMID-{HIF}_UPW.pdf").exists()


def test_cach_ly_chi_doi_tep_sai_bai_da_duyet_va_khong_xoa(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA, f"PMID-{COPD}_UPW.pdf": PDF_NCHS, f"PMID-{DUNG}_CHR.pdf": PDF_DUNG})
    ma = r.main(["--kho", str(kho), "--khong-endnote", "--cach-ly", "--ap-dung", "--pmid", HIF, DUNG])
    assert ma == 1
    cl = kho.parent / r.THU_MUC_CACH_LY
    doi = list(cl.glob(f"PMID-{HIF}_UPW.pdf.SAI-BAI-*"))
    assert len(doi) == 1 and doi[0].read_bytes() == PDF_DAPA  # dời nguyên vẹn, không xoá
    assert not (kho / f"PMID-{HIF}_UPW.pdf").exists()
    assert (kho / f"PMID-{COPD}_UPW.pdf").exists()  # sai bài nhưng CHƯA được duyệt ⇒ để nguyên
    assert (kho / f"PMID-{DUNG}_CHR.pdf").exists()  # được nêu trong --pmid nhưng KHỚP ⇒ không dời
    readme = (cl / "README.txt").read_text(encoding="utf-8")
    assert "Dapagliflozin and anemia" in readme and "Hypoxia-Inducible Factor" in readme and "không xoá" in readme
    # lượt hai cùng ngày: tên đích không đè bản đã cách ly
    (kho / f"PMID-{HIF}_UPW.pdf").write_bytes(PDF_DAPA)
    r.main(["--kho", str(kho), "--khong-endnote", "--cach-ly", "--ap-dung", "--pmid", HIF])
    assert len(list(cl.glob(f"PMID-{HIF}_UPW.pdf.SAI-BAI-*"))) == 2


def test_ban_in_sai_bai_doi_ca_tep_nguon(tmp_path, mang):
    mang()
    ban_in = pdf_gia.pdf_co_chu(f"BAN IN TU KHO TOAN VAN EBM PMID {HIF} nguon: PMID-{HIF}_PMC999.xml (XML JATS) "
                                "Dapagliflozin and anemia in patients with chronic kidney disease. "
                                + "hemoglobin hematocrit dapagliflozin placebo " * 30)
    kho = _kho(tmp_path, {f"PMID-{HIF}_BANIN.pdf": ban_in, f"PMID-{HIF}_PMC999.xml": b"<article/>"})
    assert r.main(["--kho", str(kho), "--khong-endnote", "--cach-ly", "--ap-dung", "--pmid", HIF]) == 1
    cl = kho.parent / r.THU_MUC_CACH_LY
    assert list(cl.glob(f"PMID-{HIF}_BANIN.pdf.SAI-BAI-*")) and list(cl.glob(f"PMID-{HIF}_PMC999.xml.SAI-BAI-*"))
    assert not (kho / f"PMID-{HIF}_PMC999.xml").exists()
    assert "tệp nguồn của bản in" in (cl / "README.txt").read_text(encoding="utf-8")


def test_ma_thoat_0_khi_moi_tep_khop_va_2_khi_khong_do_duoc(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{DUNG}_CHR.pdf": PDF_DUNG})
    assert r.main(["--kho", str(kho), "--khong-endnote"]) == 0
    mang(loi=("esummary.fcgi", "europepmc"))
    assert r.main(["--kho", str(kho), "--khong-endnote"]) == 2
    assert r.main(["--kho", str(tmp_path / "khong-co")]) == 2


# ───────────────────────── EndNote: chỉ đọc ─────────────────────────

def _thu_vien(tmp_path: Path, dong: list[tuple], tep_pdf: dict[str, bytes]) -> Path:
    tv = tmp_path / "EndNote" / "Thu vien.enl"
    (tv.with_suffix(".Data") / "sdb").mkdir(parents=True)
    kn = sqlite3.connect(tv.with_suffix(".Data") / "sdb" / "sdb.eni")
    kn.execute("create table refs (id integer primary key autoincrement, accession_number text, title text, trash_state int)")
    kn.execute("create table file_res (refs_id int, file_path text, file_type int, file_pos int)")
    for rec, acc, td, fp in dong:
        kn.execute("insert into refs values (?,?,?,0)", (rec, acc, td))
        if fp:
            kn.execute("insert into file_res values (?,?,1,0)", (rec, fp))
    kn.commit()
    kn.close()
    for rel, b in tep_pdf.items():
        p = tv.with_suffix(".Data") / "PDF" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    return tv


@contextlib.contextmanager
def _ket_noi(tv: Path):
    kn = sqlite3.connect((tv.with_suffix(".Data") / "sdb" / "sdb.eni").as_uri() + "?mode=ro", uri=True)
    try:
        yield kn
    finally:
        kn.close()


class _KnHong:
    """Bản sao sdb.eni đọc lỗi khi quét toàn bảng (đo 03/11: «database disk image is malformed») — chỉ đọc theo rowid được."""

    def __init__(self, kn):
        self.kn = kn

    def execute(self, q, tham_so=()):
        if "accession_number in" in q or "max(id)" in q:
            raise sqlite3.DatabaseError("database disk image is malformed")
        return self.kn.execute(q, tham_so)


def test_endnote_liet_ke_ban_ghi_gan_dung_tep_sai(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA})
    tv = _thu_vien(tmp_path, [(5, "123", "Bài khác", "1/PMID-123.pdf"), (6812, HIF, "Hypoxia-Inducible…", "2017/PMID-39186635.pdf")],
                   {"2017/PMID-39186635.pdf": PDF_DAPA, "1/PMID-123.pdf": PDF_DUNG})
    ds, _la, _tt, ghi_chu = r.ra_kho(kho, email=EMAIL, thu_vien=tv, ket_noi=_ket_noi)
    assert ghi_chu == ""
    assert ds[0].endnote == [{"rec": 6812, "tieu_de": "Hypoxia-Inducible…", "thung_rac": False,
                              "tep": [{"duong_dan": "2017/PMID-39186635.pdf", "cung_tep_kho": True}]}]


def test_endnote_ban_sao_doc_loi_van_tim_qua_rowid_va_thu_muc_pdf(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA, f"PMID-{COPD}_UPW.pdf": PDF_NCHS})
    tv = _thu_vien(tmp_path, [(6812, HIF, "Hypoxia-Inducible…", "2017/PMID-39186635.pdf"), (7305, "ed to pr", "rác", None)],
                   {"2017/PMID-39186635.pdf": PDF_DAPA, "3765/PMID-42701440.pdf": PDF_NCHS})

    @contextlib.contextmanager
    def _hong(t):
        with _ket_noi(t) as kn:
            yield _KnHong(kn)
    ds, _la, _tt, ghi_chu = r.ra_kho(kho, email=EMAIL, thu_vien=tv, ket_noi=_hong)
    kq = _theo_ten(ds)
    assert [m["rec"] for m in kq[f"PMID-{HIF}_UPW.pdf"].endnote] == [6812]  # quét từng rowid khi quét bảng lỗi
    # dòng của 42701440 đọc ra rác ⇒ thư mục PDF của EndNote vẫn chỉ ra tệp cần gỡ
    assert kq[f"PMID-{COPD}_UPW.pdf"].endnote == [{"rec": None, "tieu_de": "", "thung_rac": False,
                                                   "tep": [{"duong_dan": "3765/PMID-42701440.pdf", "cung_tep_kho": True}]}]
    assert ghi_chu == ""  # quét theo rowid không gặp dòng lỗi


def test_endnote_khong_doc_duoc_thi_bao_ro_khong_lam_hong_ket_luan(tmp_path, mang):
    mang()
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA})

    @contextlib.contextmanager
    def _mat(_t):
        raise OSError("sdb.eni đổi liên tục trong lúc chép")
        yield  # giữ dạng generator (không tới được)
    ds, _la, _tt, ghi_chu = r.ra_kho(kho, email=EMAIL, thu_vien=tmp_path / "x.enl", ket_noi=_mat)
    assert ds[0].nhom == r.SAI_BAI
    assert "không đọc được bản sao sdb.eni" in ghi_chu


# ───────────────────────── song song ─────────────────────────

def test_ket_qua_mot_tep_pickle_duoc_cho_tien_trinh_con(tmp_path, mang):
    import pickle
    mang()
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA})
    md = {"trang_thai": "ok", "nguon": "PubMed", "doi": HIF_DOI, "tieu_de": HIF_TIEU_DE, "tieu_de_goc": ""}
    d = r._kiem_mot((str(kho / f"PMID-{HIF}_UPW.pdf"), "UPW", HIF, "", md, EMAIL, "luot-1"))
    assert pickle.loads(pickle.dumps(d))["nhom"] == r.SAI_BAI and "tep" not in d


def test_song_song_hong_thi_ra_lai_tuan_tu_khong_bo_tep(tmp_path, mang, capsys):
    """Nạp bằng importlib (như test/chốt) thì tiến trình con không nạp lại được mô-đun ⇒ phải rà lại tuần tự, đủ mọi tệp."""
    mang()
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA, f"PMID-{DUNG}_CHR.pdf": PDF_DUNG})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False, so_luong=2)
    assert {kq.tep.name: kq.nhom for kq in ds} == {f"PMID-{HIF}_UPW.pdf": r.SAI_BAI, f"PMID-{DUNG}_CHR.pdf": r.KHOP}
    assert "rà lại tuần tự" in capsys.readouterr().err


def test_tieu_de_crossref_cua_bai_khac_khong_bao_gio_thanh_khop(tmp_path, mang):
    """DOI của bản ghi PubMed trỏ (trên Crossref) tới một bài KHÁC, và tệp kho chính là bài khác đó ⇒ không kiểm được, không khớp."""
    khac = "Dapagliflozin and anemia in patients with chronic kidney disease"
    mang(crossref={HIF_DOI: khac})
    kho = _kho(tmp_path, {f"PMID-{HIF}_UPW.pdf": PDF_DAPA})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert ds[0].nhom == r.KHONG_KIEM_DUOC and "Crossref ghi cho DOI" in ds[0].ly_do


def test_tieu_de_crossref_cung_bai_cuu_khac_biet_cach_viet(tmp_path, mang):
    """PubMed ghi tiêu đề kèm phụ đề dài mà PDF không in (dưới 60% ở 3 trang đầu); Crossref ghi đúng phần PDF in và cùng bài với
    tiêu đề PubMed ⇒ khớp qua tiêu đề Crossref."""
    dai = DUNG_TIEU_DE.rstrip(".") + (": protocol amendment, statistical reanalysis, sensitivity appendix, investigators "
                                      "consortium report.")
    mang(pubmed=dict(PUBMED, **{DUNG: dict(PUBMED[DUNG], title=dai)}))
    kho = _kho(tmp_path, {f"PMID-{DUNG}_CHR.pdf": PDF_DUNG})
    ds, *_ = r.ra_kho(kho, email=EMAIL, doc_endnote=False)
    assert ds[0].nhom == r.KHOP and ds[0].can_cu == "tiêu đề Crossref"
