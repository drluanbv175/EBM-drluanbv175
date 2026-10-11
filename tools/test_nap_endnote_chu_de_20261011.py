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
        self.ban_ghi: list[dict] = []          # {"id", "pmid", "doi"}
        self.nhom: dict[str, list[str]] = {}
        self.so_lan_nhap = 0
        self.loi_khi_nhap = False
        for pm, doi in co_san:
            self._them(pm, doi)

    def _them(self, pm, doi):
        rid = f'<RecordID database="2" recNum="{len(self.ban_ghi) + 1}" />'
        self.ban_ghi.append({"id": rid, "pmid": pm or "", "doi": (doi or "").lower()})

    def tim_khop(self, gia_tri, truong):
        khoa = "pmid" if truong == "Accession Number" else "doi"
        return {v: [b["id"] for b in self.ban_ghi if b[khoa] and b[khoa] == v.lower()] for v in gia_tri}

    def nhap(self, tep):
        self.so_lan_nhap += 1
        if self.loi_khi_nhap:
            raise RuntimeError("AppleScript lỗi: giả")
        goc = ET.fromstring(Path(tep).read_bytes())
        for r in goc.findall("records/record"):
            self._them(r.findtext("accession-num"), r.findtext("electronic-resource-num"))

    def thanh_vien_nhom(self, ten):
        return list(self.nhom.get(ten, []))

    def dang_vao_nhom(self, ids, ten):
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
