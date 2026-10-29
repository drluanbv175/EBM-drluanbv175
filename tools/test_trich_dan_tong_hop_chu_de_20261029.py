# -*- coding: utf-8 -*-
"""Trích dẫn TỰ TẠO tổng hợp chủ đề trong nhóm EndNote (bác sĩ yêu cầu 29/10/2026) — `tools/trich_dan_tong_hop_chu_de.py`.

Khoá: nội dung CHÉP NGUYÊN từ dashboard (cờ đỏ · làm ngay · không nên đứng trước; mục theo quyết định kèm PMID/DOI; không cắt
câu; chỉ ký tự trong BMP) · chân nói ĐÚNG trạng thái cổng (sidecar băm DATA + câu PASS của bản Word) · MỘT bản ghi mỗi chủ đề
(khoá `EBM-TT:` ở Accession Number, không link PubMed) — chạy lại không đổi thì không ghi, đổi thì ghi đè tại chỗ, nhập hụt thì
dọn PDF · PDF chỉ THAY khi mọi tệp đang gắn là của công cụ · bước ⑧ đưa mã bản ghi vào CÙNG lượt đăng nhóm, chỉ cho bản dashboard
MỚI NHẤT, lỗi của nó không chặn đăng nhóm. Ngoại tuyến, EndNote giả; không đường dẫn máy thật.
"""
from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


N = _nap("_nec_t1029", "nap_endnote_chu_de.py")
TH = _nap("_th_t1029", "trich_dan_tong_hop_chu_de.py")
TH.dat_nec(N)
XG = _nap("_xg_t1029", "xuat_goi_cap_nhat.py")

HANH_DONG_DAI = "Khởi thuốc phối hợp hai nhóm " + "và theo dõi điện giải sau hai tuần, " * 30 + "ghi rõ đích huyết áp."
DATA = {
    "meta": {"question": "Tăng huyết áp ngoại trú — chẩn đoán và điều trị", "updated": "2026-10-19"},
    "summary": {"conclusion": "Xác nhận chẩn đoán bằng HA ngoài phòng khám.",
                "doNow": ["Đo HA tại nhà 7 ngày.", "Khởi phối hợp 2 thuốc khi ≥140/90."],
                "dontDo": ["Không phối hợp ƯCMC với CTTA."],
                "redFlags": ["🔴 HA ≥180/110 kèm tổn thương cơ quan đích: chuyển cấp cứu."]},
    "items": [
        {"id": "ITEM-01", "title": "HA ngoài phòng khám", "decision": "apply", "pmid": "39210715", "action": HANH_DONG_DAI},
        {"id": "ITEM-02", "title": "AHA/ACC 2025 đặt cạnh", "decision": "consider", "pmid": "40811497",
         "action": "KHÔNG được in cho mục cân nhắc"},
        {"id": "ITEM-03", "title": "Chỉ có DOI", "decision": "consider", "doi": "https://doi.org/10.1000/ABC.1"},
        {"id": "ITEM-04", "title": "Thuốc mới chưa đủ", "decision": "notyet", "pmid": "40888730"},
    ],
}


def _nd(xac_minh=True, data=DATA, dash=Path("WebDashboard_EBM_VanDeCuThe_THA_20261019.html")):
    return TH.dung_noi_dung(data, dash, xac_minh=xac_minh, so_trich_dan=4)


# ── nội dung ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_noi_dung_chep_nguyen_dung_thu_tu_va_dinh_danh():
    nd = _nd()
    t = nd["tom_tat"]
    assert nd["tieu_de"] == "★ TÓM TẮT THỰC HÀNH · Tăng huyết áp ngoại trú — chẩn đoán và điều trị" and nd["nam"] == "2026"
    thu_tu = ["⛔ CỜ ĐỎ", "✅ LÀM NGAY", "✖️ KHÔNG NÊN LÀM", "⭐ VẤN ĐỀ CHÍNH", "✅ ÁP DỤNG NGAY — 1 mục",
              "⚠️ CÂN NHẮC CHỌN LỌC — 2 mục", "⏸️ CHƯA ĐỦ THAY ĐỔI — 1 mục", "ℹ️ NGUỒN"]
    vi_tri = [t.index(x) for x in thu_tu]
    assert vi_tri == sorted(vi_tri), "cờ đỏ và việc cần làm phải đứng trước, mục theo quyết định sau"
    for cau in ("Đo HA tại nhà 7 ngày.", "Khởi phối hợp 2 thuốc khi ≥140/90.", "Không phối hợp ƯCMC với CTTA.",
                "Xác nhận chẩn đoán bằng HA ngoài phòng khám.", "HA ≥180/110 kèm tổn thương cơ quan đích: chuyển cấp cứu."):
        assert cau in t
    assert "▶️ THỰC HÀNH: " + TH._tt()._gon(HANH_DONG_DAI) in t, "hành động mục áp dụng phải chép NGUYÊN, không cắt câu"
    assert "KHÔNG được in cho mục cân nhắc" not in t
    assert "• ITEM-01 · HA ngoài phòng khám — PMID 39210715" in t
    assert "• ITEM-03 · Chỉ có DOI — doi:10.1000/abc.1" in t
    assert "1 áp dụng · 2 cân nhắc · 1 chưa đủ" in t and t.startswith(TH.MO_DAU)


def test_chi_ky_tu_trong_bmp():
    nd = _nd()
    assert not [c for c in nd["tom_tat"] + nd["tieu_de"] if ord(c) > 0xFFFF], "EndNote đổi ký tự ngoài BMP thành «?»"
    assert "●đỏ" in nd["tom_tat"]


def test_chan_noi_dung_trang_thai_cong():
    da, chua = _nd(True)["tom_tat"], _nd(False)["tom_tat"]
    assert TH._tt().CHAN in da and N.DONG_CHUA_XAC_MINH not in da
    assert N.DONG_CHUA_XAC_MINH in chua and N.CHAN_CHUA_XAC_MINH in chua and "đã qua cổng" not in chua


def test_muc_van_ban_co_quan_ghi_nguon_va_url():
    d = {"meta": {}, "summary": {}, "items": [
        {"id": "ITEM-01", "title": "Finasteride — cảnh báo tâm thần", "decision": "apply", "pmid": None, "doi": None,
         "source": "MHRA Drug Safety Update vol 19, issue 10", "url": "https://www.gov.uk/drug-safety-update/x"}]}
    t = TH.dung_noi_dung(d, Path("WebDashboard_EBM_X_20261020.html"), xac_minh=True, so_trich_dan=0)["tom_tat"]
    assert "• ITEM-01 · Finasteride — cảnh báo tâm thần — MHRA Drug Safety Update vol 19, issue 10 · " \
           "https://www.gov.uk/drug-safety-update/x" in t
    assert "dashboard không có trích dẫn PMID/DOI" in t and "dashboard có 0 trích dẫn" not in t


def test_summary_mot_chuoi_va_thieu_khoa_khong_vo():
    d = {"meta": {}, "summary": {"doNow": "Một câu duy nhất."}, "items": []}
    t = _nd(data=d)["tom_tat"]
    assert "• Một câu duy nhất." in t and "⛔ CỜ ĐỎ" not in t and "ÁP DỤNG NGAY" not in t


# ── trạng thái phái sinh của bộ năm ──────────────────────────────────────────────────────────────────────────────────────
def _dash_that(tmp_path: Path, data_js: str = "{a:1}") -> Path:
    d = tmp_path / "WebDashboard_EBM_VanDeCuThe_THA_20261019.html"
    d.write_text(f"<script>const DATA = {data_js};\n// ===== HẾT KHỐI DATA =====\n</script>", encoding="utf-8", newline="\n")
    (tmp_path / "derivatives").mkdir()
    return d


def _phai_sinh(dash: Path, *, bam: str, pass_: bool, pdf: bool = True) -> None:
    g = dash.parent / "derivatives" / "THA_20261019_TaiLieuChiTiet"
    g.with_suffix(".data-sha256").write_text(bam + "\n", encoding="utf-8")
    g.with_suffix(".html").write_text(TH.CAU_PASS if pass_ else "PMID/DOI CẦN được xác minh", encoding="utf-8")
    if pdf:
        g.with_suffix(".pdf").write_bytes(b"%PDF-1.4 gia")


def test_bam_data_dung_khoi_const_data(tmp_path):
    dash = _dash_that(tmp_path)
    html = dash.read_text(encoding="utf-8")
    khoi = html[html.index("const DATA"):html.index("HẾT KHỐI DATA")]
    assert TH.bam_data(dash) == hashlib.sha256(khoi.encode("utf-8")).hexdigest()


def test_trang_thai_phai_sinh_tuoi_va_xac_minh(tmp_path):
    dash = _dash_that(tmp_path)
    _phai_sinh(dash, bam=TH.bam_data(dash), pass_=True)
    tt = TH.trang_thai_phai_sinh(dash)
    assert tt["tuoi"] and tt["xac_minh"] and tt["pdf"].name == "THA_20261019_TaiLieuChiTiet.pdf"


def test_word_khong_pass_thi_chua_xac_minh(tmp_path):
    dash = _dash_that(tmp_path)
    _phai_sinh(dash, bam=TH.bam_data(dash), pass_=False)
    tt = TH.trang_thai_phai_sinh(dash)
    assert tt["tuoi"] and not tt["xac_minh"] and tt["pdf"] is not None


def test_dashboard_sua_sau_luot_xuat_thi_khong_khang_dinh(tmp_path):
    dash = _dash_that(tmp_path)
    _phai_sinh(dash, bam=TH.bam_data(dash), pass_=True)
    dash.write_text(dash.read_text(encoding="utf-8").replace("{a:1}", "{a:2}"), encoding="utf-8", newline="\n")
    tt = TH.trang_thai_phai_sinh(dash)
    assert tt == {"tuoi": False, "xac_minh": False, "pdf": None}, "PDF/câu PASS của bản cũ không được gán cho DATA mới"


def test_thieu_phai_sinh_la_chua_xac_minh(tmp_path):
    assert TH.trang_thai_phai_sinh(_dash_that(tmp_path)) == {"tuoi": False, "xac_minh": False, "pdf": None}


# ── XML nhập ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_xml_report_khoa_rieng_khong_link_pubmed():
    nd = _nd()
    x = N.dung_xml([TH.ban_ghi_xml(nd, "EBM-TT:EBM_VanDeCuThe_THA", "EBM_VanDeCuThe_THA", "dấu abc",
                                   "internal-pdf://1/THA_TaiLieuChiTiet.pdf")])
    r = ET.fromstring(x).find("records/record")
    assert r.find("ref-type").get("name") == "Report" and r.find("ref-type").text == "27"
    assert r.find("accession-num").text == "EBM-TT:EBM_VanDeCuThe_THA"
    assert r.find("label").text == TH.NHAN and r.find("abstract").text == nd["tom_tat"]
    assert "pubmed" not in x and r.find("urls/pdf-urls/url").text == "internal-pdf://1/THA_TaiLieuChiTiet.pdf"
    assert [k.text for k in r.findall("keywords/keyword")] == ["EBM: EBM_VanDeCuThe_THA", TH.TU_KHOA_LOAI]


def test_xml_ban_ghi_thuong_van_dung_pmid():
    x = N.dung_xml([{"tieu_de": "x", "pmid": "123"}])
    assert "<accession-num>123</accession-num>" in x and "pubmed.ncbi.nlm.nih.gov/123/" in x


# ── vòng ghi với EndNote giả ─────────────────────────────────────────────────────────────────────────────────────────────
class _EnGia:
    """EndNote giả: bản ghi là dict trường; `nhap` đọc đúng XML do công cụ dựng."""

    def __init__(self, tv: Path, hut: bool = False, loi_ghi: str = ""):
        self.thu_vien, self.ten, self.hut, self.loi_ghi = tv, tv.name, hut, loi_ghi
        self.ban_ghi: dict[str, dict] = {}
        self.goi: list[tuple] = []

    def tim_khop(self, gia_tri, truong):
        return {v: [r for r, f in self.ban_ghi.items() if f.get(truong) == v] for v in gia_tri}

    def nhap(self, tep):
        self.goi.append(("nhap",))
        if self.hut:
            return
        r = ET.fromstring(Path(tep).read_text(encoding="utf-8")).find("records/record")
        rid = f'<RecordID database="2" recNum="{100 + len(self.ban_ghi)}" />'
        url = r.find("urls/pdf-urls/url")
        self.ban_ghi[rid] = {"Accession Number": r.find("accession-num").text, "Notes": r.find("notes").text,
                             "Title": r.find("titles/title").text, "Abstract": r.find("abstract").text,
                             "File Attachments": url.text if url is not None else ""}

    def doc_truong(self, ids, truong):
        return {i: self.ban_ghi[i].get(truong, "") for i in ids if i in self.ban_ghi}

    def ghi_truong(self, cap, truong):
        self.goi.append(("ghi", truong))
        if truong == self.loi_ghi:
            return {m: "đọc lại không khớp" for m, _ in cap}
        for m, gt in cap:
            self.ban_ghi[m][truong] = gt
        return {m: "" for m, _ in cap}

    def gan_tep(self, ma, url):
        self.goi.append(("gan_tep", url))
        self.ban_ghi[ma]["File Attachments"] = url

    def them_tep(self, ma, url):
        self.goi.append(("them_tep", url))
        self.ban_ghi[ma]["File Attachments"] += "\r" + url


@pytest.fixture
def moi_truong(tmp_path, monkeypatch):
    tv = tmp_path / "Thu vien.enl"
    tv.write_bytes(b"enl")
    pdf = tmp_path / "THA_20261019_TaiLieuChiTiet.pdf"
    pdf.write_bytes(b"%PDF-1.4 ban 1")
    tt = {"tuoi": True, "xac_minh": True, "pdf": pdf}
    monkeypatch.setattr(TH, "trang_thai_phai_sinh", lambda d: dict(tt))
    monkeypatch.setattr(TH, "_ngu", lambda s: None)
    dash = tmp_path / "WebDashboard_EBM_VanDeCuThe_THA_20261019.html"
    return tv, dash, pdf, tt


def _pdf_trong_thu_vien(tv: Path) -> list[Path]:
    return sorted((tv.with_suffix(".Data") / "PDF").rglob("*.pdf"))


def test_tao_moi_roi_chay_lai_khong_ghi(moi_truong):
    tv, dash, _pdf, _tt = moi_truong
    en = _EnGia(tv)
    rid, bc = TH.dam_bao_ban_ghi(en, dash, DATA, "EBM · THA", True)
    assert bc["trang_thai"] == "da_tao" and rid in en.ban_ghi and en.goi == [("nhap",)]
    f = en.ban_ghi[rid]
    assert f["Accession Number"] == "EBM-TT:EBM_VanDeCuThe_THA" and f"dấu {bc['dau']}" in f["Notes"]
    assert f["File Attachments"].startswith("internal-pdf://") and len(_pdf_trong_thu_vien(tv)) == 1
    en.goi.clear()
    rid2, bc2 = TH.dam_bao_ban_ghi(en, dash, DATA, "EBM · THA", True)
    assert rid2 == rid and bc2["trang_thai"] == "khong_doi" and en.goi == [], "không đổi nội dung thì không ghi gì"


def test_noi_dung_doi_thi_ghi_de_tai_cho_notes_cuoi(moi_truong):
    tv, dash, _pdf, _tt = moi_truong
    en = _EnGia(tv)
    rid, _ = TH.dam_bao_ban_ghi(en, dash, DATA, "EBM · THA", True)
    en.goi.clear()
    moi = {**DATA, "summary": {**DATA["summary"], "conclusion": "Kết luận MỚI của bản nối tiếp."}}
    rid2, bc = TH.dam_bao_ban_ghi(en, dash, moi, "EBM · THA", True)
    assert rid2 == rid and bc["trang_thai"] == "da_cap_nhat" and len(en.ban_ghi) == 1, "không bao giờ nhập bản thứ hai"
    assert [g for g in en.goi if g[0] == "ghi"] == [("ghi", "Title"), ("ghi", "Year"), ("ghi", "Abstract"), ("ghi", "Notes")]
    assert "Kết luận MỚI của bản nối tiếp." in en.ban_ghi[rid]["Abstract"] and f"dấu {bc['dau']}" in en.ban_ghi[rid]["Notes"]
    assert not [g for g in en.goi if g[0] in ("gan_tep", "them_tep")], "PDF không đổi thì không gắn lại"


def test_ghi_hong_giu_dau_cu_de_luot_sau_lam_lai(moi_truong):
    tv, dash, _pdf, _tt = moi_truong
    en = _EnGia(tv)
    rid, bc1 = TH.dam_bao_ban_ghi(en, dash, DATA, "EBM · THA", True)
    en.loi_ghi = "Abstract"
    moi = {**DATA, "summary": {**DATA["summary"], "conclusion": "Khác."}}
    _rid, bc = TH.dam_bao_ban_ghi(en, dash, moi, "EBM · THA", True)
    assert bc["trang_thai"] == "loi_ghi" and "Abstract" in bc["loi"]
    assert f"dấu {bc1['dau']}" in en.ban_ghi[rid]["Notes"] and ("ghi", "Notes") not in en.goi


def test_chay_kho_khong_ghi_gi(moi_truong):
    tv, dash, _pdf, _tt = moi_truong
    en = _EnGia(tv)
    rid, bc = TH.dam_bao_ban_ghi(en, dash, DATA, "EBM · THA", False)
    assert rid is None and bc["trang_thai"] == "se_tao" and en.goi == [] and _pdf_trong_thu_vien(tv) == []
    _, bc0 = TH.dam_bao_ban_ghi(None, dash, DATA, "EBM · THA", True)
    assert bc0["trang_thai"] == "ke_hoach"


def test_nhap_hut_don_pdf_va_bao_loi(moi_truong):
    tv, dash, _pdf, _tt = moi_truong
    en = _EnGia(tv, hut=True)
    rid, bc = TH.dam_bao_ban_ghi(en, dash, DATA, "EBM · THA", True)
    assert rid is None and bc["trang_thai"] == "nhap_hut" and bc.get("loi")
    assert _pdf_trong_thu_vien(tv) == [], "PDF vừa đặt cho bản ghi không vào thư viện phải được dọn"


@pytest.mark.parametrize("dang_gan, ham", [("internal-pdf://11/THA_20261019_TaiLieuChiTiet.pdf", "gan_tep"),
                                          ("internal-pdf://11/THA_20261019_TaiLieuChiTiet.pdf\rinternal-pdf://12/ban-bs.pdf",
                                           "them_tep")])
def test_pdf_moi_chi_thay_khi_moi_tep_la_cua_cong_cu(moi_truong, dang_gan, ham):
    tv, dash, pdf, _tt = moi_truong
    en = _EnGia(tv)
    rid, _ = TH.dam_bao_ban_ghi(en, dash, DATA, "EBM · THA", True)
    en.ban_ghi[rid]["File Attachments"] = dang_gan
    en.goi.clear()
    pdf.write_bytes(b"%PDF-1.4 ban 2 khac")
    _, bc = TH.dam_bao_ban_ghi(en, dash, DATA, "EBM · THA", True)
    assert bc["trang_thai"] == "da_cap_nhat" and bc.get("pdf_moi")
    assert [g[0] for g in en.goi if g[0] in ("gan_tep", "them_tep")] == [ham]


def test_chua_xac_minh_thang_trang_thai_phai_sinh(moi_truong):
    tv, dash, _pdf, _tt = moi_truong
    en = _EnGia(tv)
    rid, bc = TH.dam_bao_ban_ghi(en, dash, DATA, "EBM · THA", True, chua_xac_minh=True)
    assert bc["xac_minh"] is False and N.DONG_CHUA_XAC_MINH in en.ban_ghi[rid]["Abstract"]


# ── bước ⑧: nap_chu_de / nap_nhieu / lệnh ───────────────────────────────────────────────────────────────────────────────
class _EnNap:
    def __init__(self, tv: Path, pmid_rec: dict[str, int]):
        self.thu_vien, self.ten, self.pmid_rec = tv, tv.name, pmid_rec

    def tim_khop(self, gia_tri, truong):
        if truong != "Accession Number":
            return {v: [] for v in gia_tri}
        return {v: ([f'<RecordID database="2" recNum="{self.pmid_rec[v]}" />'] if v in self.pmid_rec else [])
                for v in gia_tri}

    def tep_dinh_kem(self, ids):
        return {i: 9 for i in ids}


def _nap_chu_de(tmp_path, monkeypatch, tong_hop, ap_dung=True):
    xep: list[list[str]] = []
    monkeypatch.setattr(N, "xep_vao_nhom", lambda en, nhom, ids, **kw: xep.append(list(ids)) or {"dang_vao_nhom": len(ids)})
    dash = tmp_path / "WebDashboard_EBM_VanDeCuThe_THA_20261019.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    en = _EnNap(tmp_path / "Lib.enl", {"39210715": 30, "40811497": 31, "40888730": 32})
    bc = N.nap_chu_de(dash, endnote=en, ap_dung=ap_dung, kho=None, doc_data=lambda p: DATA, ten_nhom="EBM · THA",
                      loai_tru={"doi": {}, "pmid": {}}, lay_pm=lambda x: {}, lay_ep=lambda x: {}, lay_cr=lambda d: None,
                      tong_hop=tong_hop)
    return bc, xep


def test_buoc_8_dua_ban_ghi_tong_hop_vao_cung_luot_dang_nhom(tmp_path, monkeypatch):
    goi: list[bool] = []

    def tong_hop(en, dash, data, nhom, ap_dung):
        goi.append(ap_dung)
        return '<RecordID database="2" recNum="900" />', {"trang_thai": "da_tao", "xac_minh": True}
    bc, xep = _nap_chu_de(tmp_path, monkeypatch, tong_hop)
    assert goi == [True] and len(xep) == 1 and xep[0][-1] == '<RecordID database="2" recNum="900" />'
    assert '<RecordID database="2" recNum="30" />' in xep[0] and bc["tong_hop"]["trang_thai"] == "da_tao"


def test_buoc_8_loi_ban_ghi_tong_hop_khong_chan_dang_nhom(tmp_path, monkeypatch):
    def tong_hop(*_a):
        raise RuntimeError("AppleScript lỗi: giả")
    bc, xep = _nap_chu_de(tmp_path, monkeypatch, tong_hop)
    assert "AppleScript lỗi" in bc["tong_hop"]["loi"] and len(xep) == 1 and len(xep[0]) == 3


def test_buoc_8_chay_kho_chi_lap_ke_hoach(tmp_path, monkeypatch):
    goi: list[bool] = []
    bc, xep = _nap_chu_de(tmp_path, monkeypatch, lambda en, d, data, n, ap: goi.append(ap) or (None, {"trang_thai": "se_tao"}),
                          ap_dung=False)
    assert goi == [False] and xep == [] and bc["tong_hop"] == {"trang_thai": "se_tao"}


def test_nap_nhieu_chi_ban_moi_nhat_cua_moi_chu_de(tmp_path, monkeypatch):
    nhan: list[tuple[str, bool]] = []
    monkeypatch.setattr(N, "nap_chu_de", lambda f, **kw: nhan.append((f.name, kw["tong_hop"] is not None))
                        or {"dashboard": f.name, "loi": "giả"})
    monkeypatch.setattr(N, "_in_bao_cao", lambda bc: None)
    files = [tmp_path / f"WebDashboard_EBM_VanDeCuThe_THA_{d}.html" for d in ("20261001", "20261019", "20261010")]
    N.nap_nhieu(files, endnote=None, ap_dung=False, kho=None, loai_tru={"doi": {}, "pmid": {}}, cau_hinh=tmp_path / "c.json",
                tong_hop=lambda *a: (None, {}))
    assert nhan[0] == ("WebDashboard_EBM_VanDeCuThe_THA_20261019.html", True)
    assert [x[1] for x in nhan[1:]] == [False, False], "bản cũ không được ghi đè bản ghi tổng hợp bằng nội dung cũ"


def test_lenh_buoc_8_luon_kem_tong_hop(tmp_path):
    dash = tmp_path / "WebDashboard_X_20261029.html"
    for verified in (True, False):
        assert "--kem-tong-hop" in XG.lenh_endnote("py", dash, verified=verified)


def test_kem_tong_hop_khong_di_cung_de_tai(capsys):
    assert N.main(["--de-tai", "abc", "--kem-tong-hop"]) == N.MA_THAM_SO
    assert "--kem-tong-hop" in capsys.readouterr().out


def test_tat_ca_chi_chu_de_da_co_nhom_ban_moi_nhat(tmp_path):
    for ten in ("THA_20261001", "THA_20261019", "COPD_20261020", "DaLieu_20261022"):
        (tmp_path / f"WebDashboard_EBM_VanDeCuThe_{ten}.html").write_text("x", encoding="utf-8")
    ra = TH.chu_de_moi_nhat(tmp_path, {"EBM_VanDeCuThe_THA": "EBM · THA", "EBM_VanDeCuThe_COPD": "EBM · COPD",
                                       "DE-TAI_abc": "NC · abc"})
    assert sorted(f.name for f in ra) == ["WebDashboard_EBM_VanDeCuThe_COPD_20261020.html",
                                          "WebDashboard_EBM_VanDeCuThe_THA_20261019.html"]


def test_khoa_khong_bi_nham_la_pmid():
    assert not re.fullmatch(r"(?:PMID:\s*)?(\d{1,9})", TH.khoa_ban_ghi("EBM_VanDeCuThe_THA"))
    assert not N._la_pmid_khac(TH.khoa_ban_ghi("EBM_VanDeCuThe_THA"), "123")
