# -*- coding: utf-8 -*-
"""Kiểm tools/nap_endnote_chu_de.py — nạp trích dẫn của một chủ đề vào EndNote (11/10/2026).

Không gọi mạng, không điều khiển EndNote thật: EndNote được thay bằng `_EndNoteGia` mô phỏng ĐÚNG các
hành vi đã đo trên EndNote 2025 (tìm theo chuỗi con nhưng ta lọc khớp nguyên; nhóm CỘNG THÊM và nhân đôi
khi đăng lại; nhập lại cùng XML sinh bản trùng). Mọi đường dẫn đều nằm trong tmp_path.
"""
from __future__ import annotations

import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

DUONG = Path(__file__).resolve().parent / "nap_endnote_chu_de.py"


@pytest.fixture(scope="module")
def N():
    sp = importlib.util.spec_from_file_location("nap_endnote_chu_de_test", DUONG)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def _du_lieu():
    return {
        "meta": {"question": "Suy tim và   bệnh lý nội tiết"},
        "items": [
            {"id": "ITEM-01", "pmid": "27811932", "doi": "10.1038/NRCARDIO.2016.174",
             "references": ["Jabbar A. … PMID 27811932. doi:10.1038/nrcardio.2016.174",
                            "McDonagh TA. 2021 ESC Guidelines. Eur Heart J. PMID 34447992.",
                            "Ross DS. 2016 ATA guidelines. doi:10.1089/thy.2016.0229."]},
            {"id": "ITEM-02", "pmid": "", "doi": "https://doi.org/10.1530/EJE-12-0627"},
            {"id": "ITEM-03", "pmid": "None", "doi": None, "references": ["không có định danh nào"]},
            {"id": "ITEM-04", "pmid": "34447992", "doi": ""},
        ],
    }


def _meta(pmid=None, doi=None, nguon="PubMed"):
    return {"pmid": pmid, "doi": doi, "loai_tl": "Journal Article", "tieu_de": f"Bài {pmid or doi}",
            "tac_gia": ["Nguyễn, Văn A"], "tap_chi": "Tạp chí", "tap_chi_viet_tat": "", "nam": "2020",
            "tap": "1", "so": "2", "trang": "3-4", "issn": "", "tom_tat": "", "ngon_ngu": "eng",
            "pmcid": "", "da_rut": False, "nguon_meta": nguon}


# ── định danh ──────────────────────────────────────────────────────────────────────────────────────

def test_chuan_doi(N):
    assert N.chuan_doi("https://doi.org/10.1530/EJE-12-0627") == "10.1530/eje-12-0627"
    assert N.chuan_doi("doi: 10.1089/thy.2016.0229.") == "10.1089/thy.2016.0229"
    assert N.chuan_doi("không phải doi") is None
    assert N.chuan_doi(None) is None


def test_trich_dinh_danh_gom_muc_va_tham_khao_khu_trung(N):
    dd = N.trich_dinh_danh(_du_lieu())
    khoa = [(d["pmid"], d["doi"], d["vai"]) for d in dd]
    assert khoa == [
        ("27811932", "10.1038/nrcardio.2016.174", "muc"),
        (None, "10.1530/eje-12-0627", "muc"),
        ("34447992", None, "muc"),
        (None, "10.1089/thy.2016.0229", "tham_khao"),
    ], "trùng PMID/DOI giữa mục và tham khảo phải gộp; «None» và chữ không phải định danh bị bỏ"


def test_ten_va_khoa_chu_de(N):
    dash = Path("WebDashboard_EBM_VanDeCuThe_SuyTim_NoiTiet_20260630.html")
    assert N.ten_chu_de(_du_lieu(), dash) == "Suy tim và bệnh lý nội tiết"
    assert N.khoa_chu_de(dash) == "EBM_VanDeCuThe_SuyTim_NoiTiet"
    dai = {"meta": {"question": "x" * 150}}
    assert len(N.ten_chu_de(dai, dash)) == 100
    assert N.ten_chu_de({}, dash) == dash.stem


# ── metadata ───────────────────────────────────────────────────────────────────────────────────────

_PUBMED_XML = """<?xml version="1.0"?><PubmedArticleSet>
<PubmedArticle><MedlineCitation><PMID>111</PMID><Article>
<Journal><ISSN>1234-5678</ISSN><JournalIssue><Volume>9</Volume><Issue>2</Issue>
<PubDate><MedlineDate>2019 Jan-Feb</MedlineDate></PubDate></JournalIssue>
<Title>Journal &amp; Co</Title><ISOAbbreviation>J Co</ISOAbbreviation></Journal>
<ArticleTitle>Heart <i>failure</i> trial.</ArticleTitle><Pagination><MedlinePgn>1-9</MedlinePgn></Pagination>
<Abstract><AbstractText Label="BACKGROUND">Nền.</AbstractText><AbstractText>Kết quả.</AbstractText></Abstract>
<AuthorList><Author><LastName>Trần</LastName><ForeName>Văn B</ForeName></Author>
<Author><CollectiveName>ABC Investigators</CollectiveName></Author></AuthorList>
<Language>eng</Language>
<PublicationTypeList><PublicationType>Journal Article</PublicationType>
<PublicationType>Retracted Publication</PublicationType></PublicationTypeList>
</Article></MedlineCitation>
<PubmedData><ArticleIdList><ArticleId IdType="pubmed">111</ArticleId><ArticleId IdType="doi">10.1234/ABC</ArticleId>
<ArticleId IdType="pmc">PMC99</ArticleId></ArticleIdList></PubmedData></PubmedArticle>
<PubmedBookArticle><BookDocument><PMID>222</PMID><ArticleTitle>Chapter</ArticleTitle>
<Book><Publisher><PublisherName>NCBI Bookshelf</PublisherName></Publisher><BookTitle>Book T</BookTitle>
<PubDate><Year>2021</Year></PubDate></Book></BookDocument><PubmedBookData><ArticleIdList/></PubmedBookData>
</PubmedBookArticle></PubmedArticleSet>""".encode("utf-8")


def test_phan_tich_pubmed_xml(N):
    r = N.phan_tich_pubmed_xml(_PUBMED_XML)
    a = r["111"]
    assert a["tieu_de"] == "Heart failure trial."
    assert a["tac_gia"] == ["Trần, Văn B", "ABC Investigators"]
    assert (a["nam"], a["tap"], a["so"], a["trang"], a["issn"]) == ("2019", "9", "2", "1-9", "1234-5678")
    assert a["doi"] == "10.1234/abc" and a["pmcid"] == "PMC99"
    assert a["tom_tat"] == "BACKGROUND: Nền.\nKết quả."
    assert a["da_rut"] is True
    b = r["222"]
    assert (b["loai_tl"], b["nam"], b["nha_xb"]) == ("Book Section", "2021", "NCBI Bookshelf")


_TRANG_CHAN = (b"<!DOCTYPE html><html><head><title>NCBI - WWW Error Blocked Diagnostic</title></head>"
               b"<body><p>unclosed</body></html>")


def test_ncbi_chan_bao_ro_khong_parse_mu(N):
    assert N.la_trang_chan_ncbi(_TRANG_CHAN)
    assert not N.la_trang_chan_ncbi(_PUBMED_XML)
    with pytest.raises(N.NcbiChan):
        N.lay_pubmed(["111"], tai=lambda url: _TRANG_CHAN)


def test_phan_tich_europepmc(N):
    js = {"resultList": {"result": [{
        "pmid": "333", "doi": "10.2345/X", "title": "Tiêu đề <i>nghiêng</i>", "pubYear": "2018",
        "authorList": {"author": [{"lastName": "Lê", "firstName": "Thị C"}, {"collectiveName": "Nhóm D"}]},
        "journalInfo": {"volume": "5", "issue": "1", "yearOfPublication": 2018,
                        "journal": {"title": "J", "isoabbreviation": "J Abb", "issn": "1111-2222"}},
        "pageInfo": "10-20", "abstractText": "<h4>Bối cảnh</h4> nội dung", "pmcid": "PMC1",
        "pubTypeList": {"pubType": ["Retracted Publication"]}}]}}
    a = N.phan_tich_europepmc(js)["333"]
    assert a["tieu_de"] == "Tiêu đề nghiêng" and a["tom_tat"] == "Bối cảnh nội dung"
    assert a["tac_gia"] == ["Lê, Thị C", "Nhóm D"]
    assert (a["nam"], a["tap"], a["so"], a["trang"], a["doi"]) == ("2018", "5", "1", "10-20", "10.2345/x")
    assert a["da_rut"] is True and a["nguon_meta"] == "Europe PMC"


def test_lay_metadata_lui_europepmc_roi_crossref(N):
    dd = [{"pmid": "1", "doi": None}, {"pmid": "2", "doi": "10.9/b"}, {"pmid": None, "doi": "10.9/c"},
          {"pmid": "4", "doi": None}]

    def pm_chan(pmids):
        raise N.NcbiChan("chặn")

    def ep(pmids):
        assert pmids == ["1", "2", "4"], "PubMed hỏng cả lô ⇒ Europe PMC nhận đủ các PMID"
        return {"1": _meta("1", nguon="Europe PMC")}

    def cr(doi):
        return _meta(None, doi, nguon="Crossref") if doi in ("10.9/b", "10.9/c") else None

    co, thieu = N.lay_metadata(dd, pm_chan, cr, ep)
    assert [(d["pmid"], m["nguon_meta"], m["pmid"]) for d, m in co] == [
        ("1", "Europe PMC", "1"), ("2", "Crossref", "2"), (None, "Crossref", None)]
    assert thieu == ["PMID 4"], "không lấy được ở đâu ⇒ báo, không bịa bản ghi"


# ── XML nhập và toàn văn ───────────────────────────────────────────────────────────────────────────

def test_dung_xml_hop_le_thoat_ky_tu_va_giu_unicode(N):
    m = _meta("111", "10.1/a")
    m.update(tieu_de="A & B < C — Ș ữ", tu_khoa=["EBM: khoa"], ghi_chu="ghi <chú>",
             pdf_url="internal-pdf://1234567890/PMID-111.pdf", nhan="ĐÃ RÚT (PubMed)")
    xml = N.dung_xml([m, _meta(None, "10.2/b", nguon="Crossref")])
    goc = ET.fromstring(xml.encode("utf-8"))
    rec = goc.findall("records/record")
    assert len(rec) == 2
    assert rec[0].findtext("titles/title") == "A & B < C — Ș ữ"
    assert rec[0].findtext("accession-num") == "111"
    assert rec[0].findtext("electronic-resource-num") == "10.1/a"
    assert rec[0].findtext("keywords/keyword") == "EBM: khoa"
    assert rec[0].findtext("urls/pdf-urls/url") == "internal-pdf://1234567890/PMID-111.pdf"
    assert rec[0].findtext("urls/related-urls/url") == "https://pubmed.ncbi.nlm.nih.gov/111/"
    assert rec[0].findtext("label") == "ĐÃ RÚT (PubMed)"
    assert rec[1].find("urls/pdf-urls") is None, "không có PDF thì không bịa đính kèm"
    assert rec[1].findtext("urls/related-urls/url") == "https://doi.org/10.2/b"


def test_chon_pdf_dung_pmid_va_uu_tien(N, tmp_path):
    kho = tmp_path / "toan_van_oa"
    kho.mkdir()
    for ten in ("PMID-123_CHR.pdf", "PMID-123_UPW.pdf", "PMID-1234_UPW.pdf", "PMID-123_UPW.html",
                "PMID-77_CHR.pdf", "PMID-77_WTDM.pdf", "PMID-5_PMC9.xml"):
        (kho / ten).write_bytes(b"%PDF-1.4")
    p, nhan = N.chon_pdf(kho, "123")
    assert p.name == "PMID-123_UPW.pdf" and "giấy phép mở" in nhan
    assert N.chon_pdf(kho, "77")[0].name == "PMID-77_WTDM.pdf"
    assert N.chon_pdf(kho, "12") is None, "PMID-12 không được bắt nhầm PMID-123/PMID-1234"
    assert N.chon_pdf(kho, "5") is None, "chỉ PDF — XML/HTML không đính"
    assert N.chon_pdf(None, "123") is None


def test_dat_pdf_vao_thu_vien(N, tmp_path):
    tv = tmp_path / "Thu vien.enl"
    tv.write_bytes(b"")
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF-1.4 x")
    url, thu_muc = N.dat_pdf_vao_thu_vien(tv, pdf, "123")
    m = re.fullmatch(r"internal-pdf://(\d{10})/PMID-123\.pdf", url)
    assert m, url
    assert thu_muc == tmp_path / "Thu vien.Data" / "PDF" / m.group(1)
    assert (thu_muc / "PMID-123.pdf").read_bytes() == b"%PDF-1.4 x"


# ── điều phối với EndNote mô phỏng ─────────────────────────────────────────────────────────────────

class _EndNoteGia:
    """Mô phỏng hành vi đã đo của EndNote 2025: nhập lại sinh bản trùng, nhóm cộng thêm và nhân đôi."""

    def __init__(self, thu_vien: Path, co_san=()):
        self.thu_vien = thu_vien
        self.ban_ghi: list[dict] = []          # {"id", "pmid", "doi", "tep"}
        self.nhom: dict[str, list[str]] = {}
        self.so_lan_nhap = 0
        self.loi_khi_nhap = False
        self.loi_khi_gan = False
        self.doc_duoc_dinh_kem = True
        for bg in co_san:
            self._them(*bg)

    def _them(self, pm, doi, tep=""):
        rid = f'<RecordID database="2" recNum="{len(self.ban_ghi) + 1}" />'
        self.ban_ghi.append({"id": rid, "pmid": pm or "", "doi": (doi or "").lower(), "tep": tep})

    def tep_dinh_kem(self, ids):
        if not self.doc_duoc_dinh_kem:
            return {}
        return {b["id"]: len(b["tep"]) for b in self.ban_ghi if b["id"] in ids}

    def gan_tep(self, ma, url):
        if self.loi_khi_gan:
            raise RuntimeError("AppleScript lỗi: giả")
        next(b for b in self.ban_ghi if b["id"] == ma)["tep"] = url

    def tim_khop(self, gia_tri, truong):
        khoa = "pmid" if truong == "Accession Number" else "doi"
        return {v: [b["id"] for b in self.ban_ghi if b[khoa] and b[khoa] == v.lower()] for v in gia_tri}

    def nhap(self, tep):
        self.so_lan_nhap += 1
        if self.loi_khi_nhap:
            raise RuntimeError("AppleScript lỗi: giả")
        goc = ET.fromstring(Path(tep).read_bytes())
        for r in goc.findall("records/record"):
            self._them(r.findtext("accession-num"), r.findtext("electronic-resource-num"),
                       r.findtext("urls/pdf-urls/url") or "")

    # Đo 11/10 trên thư viện thật: nhóm vừa tạo chưa vào danh sách nhóm vài giây; đăng cùng tên lúc đó ⇒ nhóm THỨ HAI.
    tre_dang_ky = 0                              # số lần hỏi danh sách nhóm mà nhóm mới còn «vô hình»
    nhom_trung: list = []                        # tên các nhóm trùng tên EndNote đã sinh ra

    def thanh_vien_nhom(self, ten):
        return list(self.nhom.get(ten, []))

    def ten_cac_nhom(self):
        if not hasattr(self, "_an"):
            self._an = {}
        ra = [n for n in self.nhom if self._an.get(n, 0) == 0] + list(self.nhom_trung)
        for n in self._an:
            self._an[n] = max(0, self._an[n] - 1)
        return ra

    def dang_vao_nhom(self, ids, ten):
        if not hasattr(self, "_an"):
            self._an = {}
        if ten in self.nhom and (self._an.get(ten, 0) > 0 or getattr(self, "sinh_trung_ten", False)):
            self.nhom_trung = [*self.nhom_trung, ten]   # nhóm cũ chưa đăng ký ⇒ EndNote tạo nhóm mới cùng tên
            return
        if ten not in self.nhom:
            self._an[ten] = self.tre_dang_ky
        self.nhom.setdefault(ten, []).extend(ids)   # đăng lại = nhân đôi, như đo thật


def _chay(N, tmp_path, en, ap_dung=True, lay_pm=None, lay_ep=None, lay_cr=None, kho=None):
    dash = tmp_path / "WebDashboard_EBM_Thu_20261011.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    return N.nap_chu_de(
        dash, endnote=en, ap_dung=ap_dung, kho=kho, doc_data=lambda p: _du_lieu(),
        lay_pm=lay_pm or (lambda pmids: {p: _meta(p) for p in pmids}),
        lay_ep=lay_ep or (lambda pmids: {}),
        lay_cr=lay_cr or (lambda doi: _meta(None, doi, nguon="Crossref")))


def test_chay_hai_lan_khong_nhap_trung_khong_dang_trung(N, tmp_path):
    en = _EndNoteGia(tmp_path / "tv.enl", co_san=[("34447992", None)])
    bc = _chay(N, tmp_path, en)
    assert (bc["so_trich_dan"], bc["da_co"], bc["nhap_moi"]) == (4, 1, 3)
    nhom = "EBM · Suy tim và bệnh lý nội tiết"
    assert len(en.nhom[nhom]) == 4 and len(set(en.nhom[nhom])) == 4
    assert len(en.ban_ghi) == 4
    bc2 = _chay(N, tmp_path, en)
    assert (bc2["da_co"], bc2["nhap_moi"], bc2["dang_vao_nhom"]) == (4, 0, 0)
    assert en.so_lan_nhap == 1, "không còn gì mới thì không gọi nhập"
    assert len(en.ban_ghi) == 4 and len(en.nhom[nhom]) == 4


def test_ban_ghi_co_san_theo_doi_khong_nhap_lai(N, tmp_path):
    en = _EndNoteGia(tmp_path / "tv.enl", co_san=[("", "10.1038/nrcardio.2016.174")])
    bc = _chay(N, tmp_path, en)
    assert bc["da_co"] == 1 and bc["nhap_moi"] == 3
    assert sum(1 for b in en.ban_ghi if b["doi"] == "10.1038/nrcardio.2016.174") == 1


def test_chay_kho_khong_nhap_khong_dang(N, tmp_path):
    en = _EndNoteGia(tmp_path / "tv.enl")
    bc = _chay(N, tmp_path, en, ap_dung=False)
    assert bc["nhap_moi"] == 4 and bc["ke_hoach_nhap"]
    assert en.so_lan_nhap == 0 and en.nhom == {}


def test_khong_lay_duoc_metadata_thi_khong_nhap(N, tmp_path):
    en = _EndNoteGia(tmp_path / "tv.enl")
    bc = _chay(N, tmp_path, en, lay_pm=lambda pmids: {}, lay_cr=lambda doi: None)
    assert bc["nhap_moi"] == 0 and len(bc["khong_lay_duoc"]) == 4
    assert en.ban_ghi == [] and en.so_lan_nhap == 0


def test_nhap_hong_thi_don_pdf_vua_dat(N, tmp_path):
    kho = tmp_path / "kho"
    kho.mkdir()
    (kho / "PMID-27811932_UPW.pdf").write_bytes(b"%PDF-1.4")
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"")
    en = _EndNoteGia(tv)
    en.loi_khi_nhap = True
    with pytest.raises(RuntimeError):
        _chay(N, tmp_path, en, kho=kho)
    assert not any((tmp_path / "tv.Data" / "PDF").iterdir()), "PDF mồ côi phải được dọn"


def test_pdf_co_san_duoc_dinh_noi_bo(N, tmp_path):
    kho = tmp_path / "kho"
    kho.mkdir()
    (kho / "PMID-27811932_UPW.pdf").write_bytes(b"%PDF-1.4 a")
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"")
    en = _EndNoteGia(tv)
    bc = _chay(N, tmp_path, en, kho=kho)
    assert bc["pdf_dinh_kem"] == 1 and bc["chua_toan_van"] == 3
    tep = list((tmp_path / "tv.Data" / "PDF").glob("*/PMID-27811932.pdf"))
    assert len(tep) == 1 and tep[0].read_bytes() == b"%PDF-1.4 a"
    assert bc["gan_them_pdf"] == 0, "bản ghi vừa nhập đã mang PDF — không gắn lần hai"


# ── toàn văn về SAU khi trích dẫn đã nằm trong EndNote ─────────────────────────────────────────────

def _kho_tv(tmp_path, *ten):
    kho = tmp_path / "kho"
    kho.mkdir(exist_ok=True)
    for t in ten:
        (kho / t).write_bytes(b"%PDF-1.4 sau")
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"")
    return kho, tv


def _thu_muc_pdf(tmp_path):
    goc = tmp_path / "tv.Data" / "PDF"
    return sorted(goc.iterdir()) if goc.is_dir() else []


def test_pdf_ve_sau_duoc_gan_vao_ban_ghi_da_co_va_chay_lai_khong_gan_lai(N, tmp_path):
    kho, tv = _kho_tv(tmp_path, "PMID-34447992_CHR.pdf")
    en = _EndNoteGia(tv, co_san=[("34447992", None, "")])
    bc = _chay(N, tmp_path, en, kho=kho)
    assert bc["gan_them_pdf"] == 1
    bg = next(b for b in en.ban_ghi if b["pmid"] == "34447992")
    assert re.fullmatch(r"internal-pdf://\d{10}/PMID-34447992\.pdf", bg["tep"]), bg["tep"]
    assert len(_thu_muc_pdf(tmp_path)) == 1
    bc2 = _chay(N, tmp_path, en, kho=kho)
    assert bc2["gan_them_pdf"] == 0 and len(_thu_muc_pdf(tmp_path)) == 1, "chạy lại không chép PDF lần hai"


def test_khong_bao_gio_ghi_de_tep_bac_si_da_gan(N, tmp_path):
    kho, tv = _kho_tv(tmp_path, "PMID-34447992_UPW.pdf")
    cua_bac_si = "internal-pdf://0304089167/Ban cua bac si.pdf"
    en = _EndNoteGia(tv, co_san=[("34447992", None, cua_bac_si)])
    bc = _chay(N, tmp_path, en, kho=kho)
    assert bc["gan_them_pdf"] == 0
    assert next(b for b in en.ban_ghi if b["pmid"] == "34447992")["tep"] == cua_bac_si
    assert _thu_muc_pdf(tmp_path) == []


def test_khong_doc_duoc_truong_dinh_kem_thi_khong_gan_khong_bao_thieu(N, tmp_path):
    kho, tv = _kho_tv(tmp_path, "PMID-34447992_UPW.pdf")
    en = _EndNoteGia(tv, co_san=[("34447992", None, "")])
    en.doc_duoc_dinh_kem = False
    bc = _chay(N, tmp_path, en, kho=kho)
    assert bc["gan_them_pdf"] == 0 and bc["thieu_toan_van"] == [], "«không đo được» không phải «chưa có»"
    assert next(b for b in en.ban_ghi if b["pmid"] == "34447992")["tep"] == ""
    assert _thu_muc_pdf(tmp_path) == []


def test_liet_ke_ban_ghi_con_thieu_toan_van(N, tmp_path):
    kho, tv = _kho_tv(tmp_path, "PMID-27811932_UPW.pdf")
    en = _EndNoteGia(tv)
    bc = _chay(N, tmp_path, en, kho=kho)
    assert bc["thieu_toan_van"] == ["DOI 10.1530/eje-12-0627", "PMID 34447992", "DOI 10.1089/thy.2016.0229"]


def test_gan_hong_thi_don_pdf_vua_dat(N, tmp_path):
    kho, tv = _kho_tv(tmp_path, "PMID-34447992_WTDM.pdf")
    en = _EndNoteGia(tv, co_san=[("34447992", None, "")])
    en.loi_khi_gan = True
    with pytest.raises(RuntimeError):
        _chay(N, tmp_path, en, kho=kho)
    assert _thu_muc_pdf(tmp_path) == [], "PDF mồ côi phải được dọn"


def test_chay_kho_bao_se_gan_ma_khong_cham_thu_vien(N, tmp_path):
    kho, tv = _kho_tv(tmp_path, "PMID-34447992_CHR.pdf")
    en = _EndNoteGia(tv, co_san=[("34447992", None, "")])
    bc = _chay(N, tmp_path, en, ap_dung=False, kho=kho)
    assert bc["se_gan_pdf"] == 1
    assert en.ban_ghi[0]["tep"] == "" and _thu_muc_pdf(tmp_path) == []


def test_hai_trich_dan_cung_mot_ban_ghi_chi_dang_va_gan_mot_lan(N, tmp_path):
    """Mục ghi PMID, tham khảo khác ghi DOI của CÙNG bài ⇒ hai trích dẫn, một bản ghi trong thư viện."""
    kho, tv = _kho_tv(tmp_path, "PMID-555_UPW.pdf")
    en = _EndNoteGia(tv, co_san=[("555", "10.5555/x", "")])
    dash = tmp_path / "WebDashboard_EBM_Thu_20261011.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    du_lieu = {"meta": {"question": "Q"}, "items": [{"id": "A", "pmid": "555", "doi": ""},
                                                    {"id": "B", "pmid": "", "doi": "10.5555/X"}]}
    bc = N.nap_chu_de(dash, endnote=en, ap_dung=True, kho=kho, doc_data=lambda p: du_lieu,
                      lay_pm=lambda pmids: {}, lay_ep=lambda pmids: {}, lay_cr=lambda doi: None)
    assert bc["dang_vao_nhom"] == 1 and en.nhom["EBM · Q"] == [en.ban_ghi[0]["id"]]
    assert bc["gan_them_pdf"] == 1 and len(_thu_muc_pdf(tmp_path)) == 1


def test_khong_thay_kho_bao_chua_xet_khong_phai_khong_co(N, tmp_path, capsys):
    en = _EndNoteGia(tmp_path / "tv.enl")
    bc = _chay(N, tmp_path, en, kho=None)
    assert bc["kho_toan_van"] is False
    bc_co = _chay(N, tmp_path, _EndNoteGia(tmp_path / "tv2.enl"), kho=_kho_tv(tmp_path)[0])
    assert bc_co["kho_toan_van"] is True
    N._in_bao_cao(bc)
    assert "CHƯA XÉT PDF" in capsys.readouterr().out


def _endnote_mac_gia(N, tra_ve):
    """EndNoteMac bỏ qua hàm dựng (hàm dựng chặn pytest và máy không phải Mac); `_chay` trả chuỗi cho sẵn."""
    en = object.__new__(N.EndNoteMac)
    en.goi = []

    def _chay(than, *doi_so, cho=600):
        en.goi.append((than, doi_so))
        return tra_ve(than, doi_so)
    en._chay = _chay
    return en


def test_gan_tep_doc_lai_khong_khop_thi_bao_loi(N):
    url = "internal-pdf://1234567890/PMID-1.pdf"
    tot = _endnote_mac_gia(N, lambda than, ds: ds[1])
    tot.gan_tep('<RecordID database="1" recNum="9" />', url)
    assert 'set field "File Attachments"' in tot.goi[0][0]
    xau = _endnote_mac_gia(N, lambda than, ds: "")
    with pytest.raises(RuntimeError):
        xau.gan_tep('<RecordID database="1" recNum="9" />', url)


def test_tep_dinh_kem_phan_tich_ma_co_dau_cach_va_bo_dong_rac(N):
    a, b = '<RecordID database="1" recNum="9" />', '<RecordID database="1" recNum="10" />'
    en = _endnote_mac_gia(N, lambda than, ds: f"{a}\t0\n{b}\t57\nrác không có tab\n{a}x\tkhông-số\n")
    assert en.tep_dinh_kem([a, b]) == {a: 0, b: 57}


# ── --gan-kho: PDF trong kho → bản ghi có sẵn, không cần dashboard ─────────────────────────────────

def test_gan_kho_chi_gan_ban_ghi_co_san_chua_co_tep(N, tmp_path):
    kho, tv = _kho_tv(tmp_path, "PMID-555_CHR.pdf", "PMID-777_UPW.pdf", "PMID-1555_UPW.pdf")
    (kho / "PMID-888_UPW.html").write_text("x", encoding="utf-8", newline="\n")
    cua_bac_si = "internal-pdf://0304089167/Cua bac si.pdf"
    en = _EndNoteGia(tv, co_san=[("555", None, ""), ("555", None, ""), ("1555", None, cua_bac_si), ("999", None, "")])
    bc = N.gan_kho(en, kho, None, True)
    assert (bc["pdf_trong_kho"], bc["co_ban_ghi"], bc["gan_them_pdf"]) == (3, 2, 1)
    assert re.fullmatch(r"internal-pdf://\d{10}/PMID-555\.pdf", en.ban_ghi[0]["tep"])
    assert en.ban_ghi[1]["tep"] == "", "bản trùng PMID trong thư viện: chỉ gắn bản đầu"
    assert en.ban_ghi[2]["tep"] == cua_bac_si and en.ban_ghi[3]["tep"] == ""
    assert len(_thu_muc_pdf(tmp_path)) == 1
    assert N.gan_kho(en, kho, None, True)["gan_them_pdf"] == 0, "chạy lại không gắn lần hai"


def test_gan_kho_loc_theo_pmid_va_chay_kho(N, tmp_path):
    kho, tv = _kho_tv(tmp_path, "PMID-555_CHR.pdf", "PMID-556_CHR.pdf")
    en = _EndNoteGia(tv, co_san=[("555", None, ""), ("556", None, "")])
    bc = N.gan_kho(en, kho, ["556"], False)
    assert (bc["pdf_trong_kho"], bc["se_gan_pdf"]) == (1, 1)
    assert [b["tep"] for b in en.ban_ghi] == ["", ""] and _thu_muc_pdf(tmp_path) == []
    assert N.gan_kho(en, None, None, True)["kho_toan_van"] is False


class _EndNoteMacDong:
    """EndNoteMac giả: thư viện CHƯA mở; mở EndNote là lỗi của phép thử."""

    def __init__(self, ung_dung, thu_vien):
        self.thu_vien = thu_vien

    def dang_mo_dung_thu_vien(self):
        return False

    def mo_thu_vien(self, cho_giay=40):
        raise AssertionError("--chi-khi-dang-mo mà vẫn tự mở EndNote")


def test_gan_kho_chi_khi_dang_mo_khong_tu_bat_endnote(N, tmp_path, monkeypatch, capsys):
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"")
    monkeypatch.setattr(N, "doc_cau_hinh", lambda tep=None: {"thu_vien": str(tv), "ung_dung": "EndNote 2025"})
    monkeypatch.setattr(N, "EndNoteMac", _EndNoteMacDong)
    # Giả lập ĐANG Ở MAC (15/10: phép kiểm nền tảng nay đứng trước phép kiểm cấu hình — DN-02).
    monkeypatch.setattr(N, "_la_mac", lambda: True)
    ma = N.main(["--gan-kho", "--pmid", "555", "--kho-toan-van", str(tmp_path), "--ap-dung", "--chi-khi-dang-mo"])
    assert ma == 0 and "⚪ EndNote chưa mở" in capsys.readouterr().out
    assert N.main(["--gan-kho", "--file", str(tv)]) == 3, "--gan-kho không đi cùng --file"


# ── một chủ đề = một nhóm qua mọi phiên bản dashboard ──────────────────────────────────────────────

def test_sap_xep_phien_ban_moi_nhat_truoc_giu_thu_tu_chu_de(N):
    f = [Path(p) for p in ("WebDashboard_A_20260101.html", "WebDashboard_B_20260301.html", "WebDashboard_A_20260601.html",
                           "WebDashboard_A.html")]
    assert [x.name for x in N.sap_xep_phien_ban(f)] == [
        "WebDashboard_A_20260601.html", "WebDashboard_A_20260101.html", "WebDashboard_A.html", "WebDashboard_B_20260301.html"]


def _hai_phien_ban(tmp_path):
    cu, moi = tmp_path / "WebDashboard_EBM_SuyTim_20260804.html", tmp_path / "WebDashboard_EBM_SuyTim_20260914.html"
    for f in (cu, moi):
        f.write_text("x", encoding="utf-8", newline="\n")
    du = {cu.name: {"meta": {"question": "Suy tim — câu hỏi bản cũ"}, "items": [{"id": "1", "pmid": "111", "doi": ""},
                                                                                 {"id": "2", "pmid": "222", "doi": ""}]},
          moi.name: {"meta": {"question": "Suy tim — câu hỏi bản mới"}, "items": [{"id": "1", "pmid": "111", "doi": ""},
                                                                                  {"id": "3", "pmid": "333", "doi": ""}]}}
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"")
    ch = tmp_path / "ch.json"
    N_ghi = json.dumps({"thu_vien": str(tv), "ung_dung": "EndNote 2025"})
    ch.write_text(N_ghi, encoding="utf-8", newline="\n")
    return [cu, moi], (lambda p: du[p.name]), tv, ch


def _nap_nhieu(N, files, doc, en, ch, ap_dung=True):
    return N.nap_nhieu(files, endnote=en, ap_dung=ap_dung, kho=None, doc_data=doc, cau_hinh=ch,
                       lay_pm=lambda pmids: {p: _meta(p) for p in pmids}, lay_ep=lambda pmids: {}, lay_cr=lambda doi: None)


def test_nhieu_phien_ban_vao_mot_nhom_ten_ban_moi_nhat_va_ghi_nho(N, tmp_path):
    files, doc, tv, ch = _hai_phien_ban(tmp_path)
    en = _EndNoteGia(tv, co_san=[("111", None, "")])
    kq = _nap_nhieu(N, files, doc, en, ch)
    assert [b["dashboard"] for b in kq] == [files[1].name, files[0].name], "bản mới nhất chạy trước, đặt tên nhóm"
    assert set(en.nhom) == {"EBM · Suy tim — câu hỏi bản mới"}, "một chủ đề chỉ một nhóm"
    assert len(en.nhom["EBM · Suy tim — câu hỏi bản mới"]) == 3, "bổ sung phần thiếu của bản cũ (222), không lặp 111"
    assert len(en.ban_ghi) == 3, "bản ghi đã có (111) giữ nguyên, không nhập lại"
    assert N.nhom_da_ghi(ch) == {"EBM_SuyTim": "EBM · Suy tim — câu hỏi bản mới"}


def test_nhom_da_ghi_nho_thang_cau_hoi_moi(N, tmp_path):
    files, doc, tv, ch = _hai_phien_ban(tmp_path)
    N.ghi_nhom("EBM_SuyTim", "EBM · Suy tim (nhóm cũ)", ch)
    en = _EndNoteGia(tv)
    _nap_nhieu(N, files[1:], doc, en, ch)
    assert set(en.nhom) == {"EBM · Suy tim (nhóm cũ)"}, "chủ đề đã có nhóm ⇒ vào đúng nhóm cũ dù câu hỏi đổi chữ"


def test_doi_nhom_moi_dang_ky_roi_moi_dang_ban_ke_tiep(N, tmp_path, monkeypatch):
    """Ca thật 11/10: «Tiên lượng suy tim» bị tách hai nhóm cùng tên vì bản cũ đăng ngay sau khi bản mới tạo nhóm."""
    ngu: list[float] = []
    monkeypatch.setattr(N, "_ngu", ngu.append)
    files, doc, tv, ch = _hai_phien_ban(tmp_path)
    en = _EndNoteGia(tv)
    en.tre_dang_ky = 3
    kq = _nap_nhieu(N, files, doc, en, ch)
    assert en.nhom_trung == [], "đăng bản kế tiếp khi nhóm chưa đăng ký ⇒ EndNote sinh nhóm trùng tên"
    assert len(en.nhom["EBM · Suy tim — câu hỏi bản mới"]) == 3 and ngu, "phải đợi nhóm đăng ký"
    assert not any(b.get("nhom_trung_ten") for b in kq)


def test_endnote_sinh_nhom_trung_ten_thi_bao_ro(N, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(N, "_ngu", lambda s: None)
    files, doc, tv, ch = _hai_phien_ban(tmp_path)
    en = _EndNoteGia(tv)
    _nap_nhieu(N, files[1:], doc, en, ch)
    en.sinh_trung_ten = True
    kq = _nap_nhieu(N, files[:1], doc, en, ch)
    assert kq[0]["nhom_trung_ten"] == 2
    assert "nhóm cùng tên này — gộp tay" in capsys.readouterr().out


def test_cho_nhom_co_tran_thoi_gian(N, monkeypatch):
    ngu: list[float] = []
    monkeypatch.setattr(N, "_ngu", ngu.append)
    en = type("E", (), {"ten_cac_nhom": lambda self: []})()
    assert N.cho_nhom_dang_ky(en, "EBM · X", 1) == 0
    assert len(ngu) == N.CHO_NHOM_GIAY, "không đợi vô hạn khi EndNote không bao giờ liệt kê nhóm"


def test_chay_kho_khong_ghi_bang_nhom(N, tmp_path):
    files, doc, tv, ch = _hai_phien_ban(tmp_path)
    kq = _nap_nhieu(N, files, doc, _EndNoteGia(tv), ch, ap_dung=False)
    assert {b["nhom"] for b in kq} == {"EBM · Suy tim — câu hỏi bản mới"}, "chạy khô vẫn báo đúng một nhóm"
    assert N.nhom_da_ghi(ch) == {}


def test_khai_lai_cung_thu_vien_giu_bang_nhom_doi_thu_vien_thi_bo(N, tmp_path):
    _, _, tv, ch = _hai_phien_ban(tmp_path)
    N.ghi_nhom("EBM_SuyTim", "EBM · X", ch)
    N.ghi_cau_hinh(str(tv), "EndNote 2025", tep=ch)
    assert N.nhom_da_ghi(ch) == {"EBM_SuyTim": "EBM · X"}
    tv2 = tmp_path / "khac.enl"
    tv2.write_bytes(b"")
    N.ghi_cau_hinh(str(tv2), "EndNote 2025", tep=ch)
    assert N.nhom_da_ghi(ch) == {}, "bảng nhóm thuộc về MỘT thư viện"


# ── rào an toàn & cấu hình ─────────────────────────────────────────────────────────────────────────

def test_khong_bao_gio_dieu_khien_endnote_that_duoi_pytest(N, tmp_path, monkeypatch):
    monkeypatch.delenv("EBM_ENDNOTE_CHO_PHEP_TRONG_TEST", raising=False)
    with pytest.raises(N.KhongChayDuoc):
        N.EndNoteMac("EndNote 2025", tmp_path / "tv.enl")


def test_ten_ung_dung_khong_hop_le_bi_tu_choi(N, tmp_path):
    with pytest.raises(ValueError):
        tv = tmp_path / "tv.enl"
        tv.write_bytes(b"")
        N.ghi_cau_hinh(str(tv), 'EndNote" to do shell script "x', tep=tmp_path / "ch.json")


def test_ghi_va_doc_cau_hinh(N, tmp_path):
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"")
    ch_tep = tmp_path / "ch.json"
    N.ghi_cau_hinh(str(tv), "EndNote 2025", tep=ch_tep)
    assert json.loads(ch_tep.read_text(encoding="utf-8"))["thu_vien"] == str(tv.resolve())
    assert N.doc_cau_hinh(ch_tep)["ung_dung"] == "EndNote 2025"
    with pytest.raises(ValueError):
        N.ghi_cau_hinh(str(tmp_path / "khong-co.enl"), "EndNote 2025", tep=ch_tep)
    assert N.doc_cau_hinh(tmp_path / "vang.json") is None


def test_bo_nam_chua_cau_hinh_thi_im_lang_ma_0(N, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(N, "CAU_HINH", tmp_path / "vang.json")
    dash = tmp_path / "WebDashboard_X_20261011.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    assert N.main(["--file", str(dash), "--ap-dung", "--im-khi-chua-cau-hinh"]) == 0
    assert "⚪ EndNote: bỏ qua" in capsys.readouterr().out
    assert N.main(["--file", str(dash), "--ap-dung"]) == 2, "gọi tay mà chưa cấu hình ⇒ không chạy được, không im"


# ── NHẬP HỤT (19/10/2026): `import` của EndNote trả về KHÔNG lỗi mà thư viện không có bài ─────────────
# Ca thật: gói THA ngoại trú — bước ⑧ in «nhập mới 17», tra lại theo PMID lẫn DOI ra 0/17, nhóm không tồn tại; lúc đó
# EndNote mở hai cửa sổ «Libraries Preferences» và «EndNote™ Preferences». Công cụ phải đếm theo thư viện THẬT.

class _EndNoteNhapImLang(_EndNoteGia):
    """`tre` None ⇒ lệnh nhập im lặng không làm gì; `tre`=n ⇒ bài vào thư viện sau n lượt tra lại (EndNote ghi chậm)."""

    def __init__(self, thu_vien, tre=None):
        super().__init__(thu_vien)
        self.tre = tre
        self._cho = None
        self._dem = 0

    def nhap(self, tep):
        self.so_lan_nhap += 1
        if self.tre is not None:
            self._cho = Path(tep).read_bytes()

    def tim_khop(self, gia_tri, truong):
        if self._cho is not None:
            self._dem += 1
            if self._dem > 2 * self.tre:  # mỗi lượt tra gọi tim_khop hai lần (PMID rồi DOI)
                for r in ET.fromstring(self._cho).findall("records/record"):
                    self._them(r.findtext("accession-num"), r.findtext("electronic-resource-num"),
                               r.findtext("urls/pdf-urls/url") or "")
                self._cho = None
        return super().tim_khop(gia_tri, truong)

    def ten_cua_so(self):
        return ["tv.enl", "Libraries Preferences", "EndNote™ Preferences"]


def _kho_mot_pdf(tmp_path):
    kho = tmp_path / "kho"
    kho.mkdir()
    (kho / "PMID-27811932_UPW.pdf").write_bytes(b"%PDF-1.4 a")
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"")
    return kho, tv


def test_nhap_im_lang_bao_nhap_hut_khong_bao_so_du_dinh(N, tmp_path, monkeypatch, capsys):
    ngu = []
    monkeypatch.setattr(N, "_ngu", ngu.append)
    kho, tv = _kho_mot_pdf(tmp_path)
    en = _EndNoteNhapImLang(tv)
    bc = _chay(N, tmp_path, en, kho=kho)
    assert en.so_lan_nhap == 1
    assert (bc["nhap_moi"], bc["nhap_thuc"], len(bc["nhap_hut"])) == (4, 0, 4)
    assert len(ngu) == N.CHO_NHAP_GIAY, "tra lại có giới hạn rồi mới kết luận hụt"
    assert bc["dang_vao_nhom"] == 0 and en.nhom == {}
    assert not any((tmp_path / "tv.Data" / "PDF").iterdir()), "PDF đặt cho bài không vào thư viện phải được dọn"
    assert N.ma_thoat_nap([bc]) == N.MA_KHONG_CHAY
    N._in_bao_cao(bc)
    out = capsys.readouterr().out
    assert "nhập mới 0/4" in out and "NHẬP HỤT: 4/4" in out
    assert "EndNote™ Preferences" in out and "tv.enl" not in out.split("Cửa sổ EndNote đang mở:")[1].splitlines()[0]
    assert "nhập mới 4 " not in out, "không bao giờ in số DỰ ĐỊNH như số đã nhập"


def test_endnote_ghi_cham_van_dem_du_khong_bao_hut(N, tmp_path, monkeypatch):
    ngu = []
    monkeypatch.setattr(N, "_ngu", ngu.append)
    kho, tv = _kho_mot_pdf(tmp_path)
    en = _EndNoteNhapImLang(tv, tre=2)
    bc = _chay(N, tmp_path, en, kho=kho)
    assert (bc["nhap_thuc"], bc.get("nhap_hut")) == (4, None)
    assert len(ngu) == 2, "chỉ đợi tới khi bài vào thư viện"
    assert bc["dang_vao_nhom"] == 4
    assert len(list((tmp_path / "tv.Data" / "PDF").glob("*/PMID-27811932.pdf"))) == 1, "bài đã vào thì giữ PDF"
    assert N.ma_thoat_nap([bc]) == N.MA_OK


def test_nhap_binh_thuong_khong_doi_va_khong_ngu(N, tmp_path, monkeypatch):
    ngu = []
    monkeypatch.setattr(N, "_ngu", ngu.append)
    bc = _chay(N, tmp_path, _EndNoteGia(tmp_path / "tv.enl"))
    assert (bc["nhap_moi"], bc["nhap_thuc"], bc.get("nhap_hut")) == (4, 4, None) and ngu == []


def test_ma_thoat_nap(N):
    assert N.ma_thoat_nap([{}]) == N.MA_OK
    assert N.ma_thoat_nap([{"khong_lay_duoc": ["PMID 1"]}]) == N.MA_MOT_PHAN
    assert N.ma_thoat_nap([{"khong_lay_duoc": ["PMID 1"]}, {"nhap_hut": ["PMID 2"]}]) == N.MA_KHONG_CHAY
    assert N.ma_thoat_nap([{"loi": "x"}]) == N.MA_KHONG_CHAY


def test_ten_cua_so_chi_doc_va_loi_thi_rong(N):
    en = object.__new__(N.EndNoteMac)
    en.ung_dung = "EndNote 2025"
    gui = []

    def chay(than, *a, **k):
        gui.append(than)
        return "My EndNote Library.enl\nEndNote™ Preferences\n"
    en._chay = chay
    assert en.ten_cua_so() == ["My EndNote Library.enl", "EndNote™ Preferences"]
    # 19/10: EndNote giữ cửa sổ Preferences đã đóng như đối tượng ẨN (visible=false) — lệnh gửi đi phải lọc cửa sổ hiển thị
    assert "whose visible is true" in gui[0]

    def hong(*a, **k):
        raise RuntimeError("AppleScript lỗi: giả")
    en._chay = hong
    assert en.ten_cua_so() == [], "không đo được thì không kết luận"
