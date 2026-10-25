# -*- coding: utf-8 -*-
"""TLTK của đề tài nghiên cứu → EndNote (25/10/2026) — `tools/nap_endnote_de_tai.py` + tham số mới của `nap_chu_de`.

Bác sĩ giao: trích dẫn của đề tài vào EndNote ĐÚNG CHUẨN TRÍCH DẪN, KHÔNG tóm tắt như hệ cập nhật chứng cứ, NHƯNG phải đảm bảo
toàn văn. Đề cương C1a (đo 25/10/2026): 52 TLTK — 35 có PMID, 14 chỉ có DOI (9 bài tạp chí Việt Nam, 1 sách Wiley), 3 không
định danh (2 quyết định Bộ Y tế, 1 sách WHO). Ngoại tuyến hoàn toàn: EndNote giả, metadata giả, Unpaywall giả.
"""
from __future__ import annotations

import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


T = _nap("tools/nap_endnote_de_tai.py", "_nap_endnote_de_tai_test")
NE = T.NE


@pytest.fixture(autouse=True)
def _hang_cho_tam(tmp_path, monkeypatch):
    """Hàng chờ đưa vào nhóm luôn ở tmp_path — không bao giờ tệp thật trong thư mục nhà."""
    monkeypatch.setenv("EBM_ENDNOTE_CHO_VAO_NHOM", str(tmp_path / "cho-vao-nhom.json"))
    monkeypatch.setattr(NE, "_ngu", lambda _s: None)


DE_CUONG = """# 6. KẾ HOẠCH

1. Không phải TLTK — nằm trước mục tài liệu tham khảo.

# 7. TÀI LIỆU THAM KHẢO

1. Bộ Y tế. Quyết định số 56/QĐ-BYT ngày 08/01/2024 ban hành Hướng dẫn đo lường sự hài lòng. Hà Nội: Bộ Y tế; 2024.
2. Bull C, Byrnes J. A systematic review of the validity of patient-reported experience measures. Health Serv Res. \
2019;54(5):1023-1035. doi:10.1111/1475-6773.13187. PMID: 31218671.
3. Eldridge SM, Ashby D, Kerry S. Sample size for cluster randomized trials. Int J Epidemiol. 2006;35(5):1292-1300. \
doi:10.1093/ije/dyl129.
4. Lê Thị A. Hài lòng người bệnh tại khoa khám bệnh. Tạp chí Y học Cộng đồng. 2023;64(1):1-5.
   doi:10.52163/yhc.v64i1.573.
5. Lwanga SK, Lemeshow S. Sample size determination in health studies: a practical manual. Geneva: World Health \
Organization; 1991.
6. Một tài liệu không theo khuôn nào cả

# PHỤ LỤC A. BẢNG

1. Cũng không phải TLTK.
"""


def _de_tai(tmp_path: Path, noi_dung: str = DE_CUONG) -> tuple[Path, Path]:
    thu_muc = tmp_path / "exports" / "NC-THU"
    thu_muc.mkdir(parents=True)
    tep = thu_muc / "DE_CUONG_NOP_HOI_DONG_NC-THU.md"
    tep.write_text(noi_dung, encoding="utf-8", newline="\n")
    return thu_muc, tep


def _meta(pmid=None, doi=None, tieu_de=None, nam="2019", nguon="PubMed", rut=False):
    return {"pmid": pmid, "doi": doi, "loai_tl": "Journal Article", "tieu_de": tieu_de or f"Bài {pmid or doi}",
            "tac_gia": ["Bull, C"], "tap_chi": "Health Serv Res", "tap_chi_viet_tat": "", "nam": nam, "tap": "54",
            "so": "5", "trang": "1023-1035", "issn": "", "tom_tat": "Abstract gốc của nguồn.", "ngon_ngu": "eng",
            "pmcid": "", "da_rut": rut, "nguon_meta": nguon}


META = {
    "31218671": _meta("31218671", "10.1111/1475-6773.13187",
                      "A systematic review of the validity of patient-reported experience measures"),
    "16855282": _meta("16855282", "10.1093/ije/dyl129", "Sample size for cluster randomized trials", nam="2006"),
}
META_CR = {"10.52163/yhc.v64i1.573": _meta(None, "10.52163/yhc.v64i1.573", "Hài lòng người bệnh tại khoa khám bệnh",
                                            nam="2023", nguon="Crossref")}


def _pdf(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"%PDF-1.4 toan van")
    return p


class _EnGia:
    """EndNote giả: nhập XML thành bản ghi; tim_khop theo Accession Number/DOI/Title; nhóm đo theo tên (post vào tên ĐÃ có là
    lỗi phép thử — EndNote thật sinh nhóm trùng tên, BH170); trường «File Attachments» lưu chuỗi ngăn bằng \\r."""

    def __init__(self, thu_vien: Path, co_san=()):
        self.thu_vien = thu_vien
        self.ban_ghi: list[dict] = []
        self.nhom: dict[str, list[str]] = {}
        self.so_lan_nhap = 0
        self.lan_post = 0
        for bg in co_san:
            self._them(**bg)

    def _them(self, pmid="", doi="", tieu_de="", tep="", loai="Journal Article", nhan="", tu_khoa=(), abstract=""):
        rid = f'<RecordID database="2" recNum="{9000 + len(self.ban_ghi) + 1}" />'
        self.ban_ghi.append({"id": rid, "pmid": pmid or "", "doi": (doi or "").lower(), "tieu_de": tieu_de, "tep": tep,
                             "loai": loai, "nhan": nhan, "tu_khoa": list(tu_khoa), "abstract": abstract})
        return rid

    def _bg(self, ma):
        return next(b for b in self.ban_ghi if b["id"] == ma)

    def thung_rac(self):
        return {"doi": set(), "pmid": set()}

    def tim_khop(self, gia_tri, truong):
        khoa = {"Accession Number": "pmid", "DOI": "doi", "Title": "tieu_de"}[truong]
        return {v: [b["id"] for b in self.ban_ghi if b[khoa] and b[khoa].lower() == v.lower()] for v in gia_tri}

    def nhap(self, tep):
        self.so_lan_nhap += 1
        for r in ET.fromstring(Path(tep).read_bytes()).findall("records/record"):
            self._them(pmid=r.findtext("accession-num"), doi=r.findtext("electronic-resource-num"),
                       tieu_de=r.findtext("titles/title") or "", tep=r.findtext("urls/pdf-urls/url") or "",
                       loai=r.find("ref-type").get("name"), nhan=r.findtext("label") or "",
                       tu_khoa=[k.text for k in r.findall("keywords/keyword")], abstract=r.findtext("abstract") or "")

    def tep_dinh_kem(self, ids):
        return {b["id"]: len(b["tep"]) for b in self.ban_ghi if b["id"] in ids}

    def gan_tep(self, ma, url):
        self._bg(ma)["tep"] = url

    def them_tep(self, ma, url):
        b = self._bg(ma)
        b["tep"] = "\r".join([x for x in b["tep"].split("\r") if x] + [url])

    def doc_truong(self, ids, truong):
        k = {"File Attachments": "tep", "Reference Type": "loai"}[truong]
        return {b["id"]: b[k] for b in self.ban_ghi if b["id"] in ids}

    def nhom_theo_ten(self, ten):
        if ten not in self.nhom:
            return []
        rec = [int(re.search(r'recNum="(\d+)"', i).group(1)) for i in self.nhom[ten]]
        return [{"group_id": 1, "ten": ten, "so_ban_ghi": len(rec), "rec": rec}]

    def dang_vao_nhom(self, ids, ten):
        assert ten not in self.nhom, "post vào tên đã có nhóm ⇒ EndNote sinh nhóm trùng tên (BH170)"
        self.lan_post += 1
        self.nhom[ten] = list(ids)

    def ma(self, **k):
        return next(b["id"] for b in self.ban_ghi if all(b[x] == v for x, v in k.items()))


def _tim(doi):
    return ["16855282"] if doi == "10.1093/ije/dyl129" else []


def _chay(tmp_path, en, ap_dung=True, kho=None, noi_dung=DE_CUONG, **k):
    thu_muc, tep = _de_tai(tmp_path, noi_dung)
    k.setdefault("lay_pm", lambda pmids: {p: META[p] for p in pmids if p in META})
    k.setdefault("lay_cr", lambda doi: META_CR.get(doi))
    k.setdefault("lay_ep", lambda pmids: {})
    k.setdefault("tim_pmid", _tim)
    bc = T.chay([tep], "NC-THU", thu_muc, endnote=en, ap_dung=ap_dung, kho=kho, loai_tru=None, **k)
    return bc, thu_muc


# ── đọc mục TLTK ────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_doc_tltk_chi_lay_muc_tham_khao_noi_dong_va_tach_dinh_danh(tmp_path):
    _thu_muc, tep = _de_tai(tmp_path)
    ds = T.doc_tltk(tep)
    assert [r["so"] for r in ds] == [1, 2, 3, 4, 5, 6], "dừng ở đề mục kế tiếp, bỏ danh sách đánh số ngoài mục TLTK"
    assert ds[1]["pmid"] == "31218671" and ds[1]["doi"] == "10.1111/1475-6773.13187", "DOI bỏ dấu chấm cuối câu"
    assert ds[3]["doi"] == "10.52163/yhc.v64i1.573" and ds[3]["van_ban"].endswith("doi:10.52163/yhc.v64i1.573."), \
        "dòng xuống dòng nối vào TLTK đứng trước"
    assert ds[0]["pmid"] is None and ds[0]["doi"] is None


def test_khong_thay_muc_tltk_la_loi_khong_phai_khong_co_tltk(tmp_path):
    _thu_muc, tep = _de_tai(tmp_path, "# 1. ĐẶT VẤN ĐỀ\n\n1. a\n")
    with pytest.raises(ValueError, match="không thấy"):
        T.doc_tltk(tep)


def test_danh_so_dut_lap_va_trung_nguon_duoc_bao(tmp_path):
    _thu_muc, tep = _de_tai(tmp_path, "# TÀI LIỆU THAM KHẢO\n\n1. A. B. C. 2019. PMID: 11111111\n"
                                      "3. D. E. F. 2020. PMID: 11111111\n3. G. H. I. 2021. doi:10.1/x\n")
    ds, cb = T.gop_tai_lieu([tep])
    assert len(ds) == 2, "trùng PMID trong cùng danh mục chỉ nạp MỘT bản ghi"
    noi = " ".join(cb)
    assert "lặp [3]" in noi and "thiếu [2]" in noi and "TLTK 3 trùng nguồn với TLTK 1" in noi


# ── TLTK không định danh ────────────────────────────────────────────────────────────────────────────────────────────────

def test_tach_van_ban_nha_nuoc_va_sach_khu_hoi():
    m = T.tach_khong_dinh_danh("Bộ Y tế. Quyết định số 56/QĐ-BYT ngày 08/01/2024 ban hành Hướng dẫn. Hà Nội: Bộ Y tế; 2024.")
    assert m["loai_tl"] == "Government Document" and m["tac_gia"] == ["Bộ Y tế,"], "tác giả tập thể mang dấu phẩy cuối"
    assert (m["noi_xb"], m["nha_xb"], m["nam"]) == ("Hà Nội", "Bộ Y tế", "2024")
    s = T.tach_khong_dinh_danh("Lwanga SK, Lemeshow S. Sample size determination in health studies: a practical manual. "
                               "Geneva: World Health Organization; 1991.")
    assert s["loai_tl"] == "Book" and s["tac_gia"] == ["Lwanga, S. K.", "Lemeshow, S."]
    assert s["tieu_de"] == "Sample size determination in health studies: a practical manual"


@pytest.mark.parametrize("van", [
    "Một tài liệu không theo khuôn nào cả",
    "Rubin DB. Multiple imputation. New York: Wiley; 1987. doi:10.1002/9780470316696.",  # có định danh ⇒ không đi đường này
    "Tác giả. Tên sách. Nơi: NXB; năm không rõ.",
])
def test_khong_tach_duoc_thi_khong_doan(van):
    assert T.tach_khong_dinh_danh(van) is None


# ── PMID từ DOI ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_pmid_tu_doi_chi_nhan_khi_pubmed_xac_nhan_hai_chieu():
    ds = [{"so": 3, "pmid": None, "doi": "10.1093/ije/dyl129"}, {"so": 4, "pmid": None, "doi": "10.52163/yhc.v64i1.573"}]
    bc = T.phan_giai_pmid(ds, tim=_tim, lay_pm=lambda pmids: {p: META[p] for p in pmids})
    assert ds[0]["pmid"] == "16855282" and ds[0]["pmid_tu_doi"] and ds[1]["pmid"] is None
    assert bc["them"] == ["TLTK 3: DOI 10.1093/ije/dyl129 → PMID 16855282"]
    ds = [{"so": 3, "pmid": None, "doi": "10.1093/ije/dyl129"}]
    T.phan_giai_pmid(ds, tim=_tim, lay_pm=lambda pmids: {p: _meta(p, "10.9/khac") for p in pmids})
    assert ds[0]["pmid"] is None, "DOI của bản ghi PubMed khác DOI của TLTK ⇒ không gắn PMID"
    ds = [{"so": 3, "pmid": None, "doi": "10.1093/ije/dyl129"}]
    T.phan_giai_pmid(ds, tim=lambda d: ["1", "2"], lay_pm=lambda pmids: {p: _meta(p, d) for p, d in
                                                                          zip(pmids, ["10.1093/ije/dyl129"] * 2)})
    assert ds[0]["pmid"] is None, "hai PMID cho một DOI ⇒ mơ hồ, không chọn"


def test_ncbi_chan_khi_tra_pmid_la_khong_do_duoc():
    ds = [{"so": 3, "pmid": None, "doi": "10.1093/ije/dyl129"}]

    def chan(_d):
        raise NE.NcbiChan("chặn")
    bc = T.phan_giai_pmid(ds, tim=chan)
    assert ds[0]["pmid"] is None and bc["khong_do_duoc"] == ["TLTK 3 (NcbiChan)"]


# ── đối chiếu chuẩn trích dẫn ───────────────────────────────────────────────────────────────────────────────────────────

def test_doi_chieu_bat_tieu_de_nam_va_bai_rut():
    r = {"van_ban": "Bull C. A systematic review of the validity of patient-reported experience measures. "
                    "Health Serv Res. 2019;54(5):1023."}
    assert T.doi_chieu(r, META["31218671"]) == []
    sai = T.doi_chieu(r, _meta("1", tieu_de="Statins after myocardial infarction", nam="2021", rut=True))
    assert any("tiêu đề" in x for x in sai) and any("năm của nguồn 2021" in x for x in sai) and any("ĐÃ RÚT" in x for x in sai)
    dich = T.doi_chieu({"van_ban": "Iglesias-Puzas Á. Adaptación transcultural y validación al español del PSQ-18. "
                                   "J Healthc Qual Res. 2021;36(5):269-274."},
                       _meta("34053882", tieu_de="[Cross-cultural adaptation and Spanish validation of PSQ-18].", nam="2021"))
    assert len(dich) == 1 and "tiêu đề DỊCH" in dich[0], "tiêu đề dịch trong ngoặc vuông của PubMed được gọi đúng tên"


# ── toàn văn ────────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_chon_toan_van_dung_dinh_danh_va_chi_nhan_pdf_that(tmp_path):
    kho, tv = tmp_path / "kho", tmp_path / "tv"
    _pdf(kho / "PMID-1234_UPW.pdf")
    assert T.chon_toan_van({"so": 1, "pmid": "123"}, kho, tv) is None, "PMID-123 không bắt nhầm PMID-1234"
    assert T.chon_toan_van({"so": 1, "pmid": "1234"}, kho, tv)[0].name == "PMID-1234_UPW.pdf"
    _pdf(tv / "DOI-10.52163_yhc.v64i1.573.pdf")
    assert T.chon_toan_van({"so": 4, "pmid": None, "doi": "10.52163/yhc.v64i1.573"}, kho, tv)
    (tv / "TLTK-7.pdf").write_bytes(b"<html>trang loi</html>")
    assert T.chon_toan_van({"so": 7}, kho, tv) is None, "tệp không bắt đầu %PDF- không phải toàn văn"
    _pdf(tv / "TLTK-8.pdf")
    assert T.chon_toan_van({"so": 8}, kho, tv) and T.chon_toan_van({"so": 8, "pmid": "9"}, kho, tv) is None, \
        "tệp theo SỐ TLTK chỉ dành cho TLTK không định danh"


def test_co_toan_van_khong_tinh_pdf_tom_tat():
    assert T.co_toan_van("internal-pdf://1234567890/PMID-1.pdf")
    assert not T.co_toan_van("file:///x/TomTatChungCu/PMID-1_TomTatChungCu.pdf\rfile:///x/a.docx")
    assert not T.co_toan_van("")


def test_unpaywall_theo_doi_qua_cong_dieu_khoan_va_chi_luu_pdf(tmp_path):
    ghi = []
    gom = SimpleNamespace(
        _email_lich_su=lambda: "a@b.c",
        vi_tri_oa_duoc_luu=lambda uj, doi: (uj["urls"], uj.get("ly")),
        _ghi_nguyen_tu=lambda dich, du_lieu: (ghi.append(dich.name), dich.write_bytes(du_lieu)))
    tra = {"10.1/cam": {"urls": [], "ly": "cam_khong_uq: NXB cấm"}, "10.1/pdf": {"urls": ["u-pdf"]},
           "10.1/html": {"urls": ["u-html"]}}
    noi_dung = {"u-pdf": b"%PDF-1.7 x", "u-html": b"<html>"}

    def tai(url):
        if url.startswith("https://api.unpaywall.org/v2/"):
            return json.dumps(tra[url.split("/v2/")[1].split("?")[0]]).encode()
        return noi_dung[url]
    ds = [{"so": i, "pmid": None, "doi": d} for i, d in enumerate(tra, 1)] + [{"so": 9, "pmid": "1", "doi": "10.1/x"}]
    bc = T.gom_doi_unpaywall(ds, tmp_path / "tv", gom_mod=gom, tai=tai)
    assert ghi == ["DOI-10.1_pdf_UPW.pdf"] and bc["luu"] == ["TLTK 2"]
    assert any("NXB cấm" in x for x in bc["khong_luu"]) and any("HTML" in x for x in bc["khong_luu"])
    assert len(bc["khong_luu"]) == 2, "TLTK có PMID đi bộ gom kho chung, không đi làn DOI"


# ── lượt nạp đầy đủ ─────────────────────────────────────────────────────────────────────────────────────────────────────

def test_nap_that_dung_chuan_trich_dan_khong_tom_tat_va_mot_lan_post_nhom(tmp_path):
    tv_lib = tmp_path / "tv.enl"
    tv_lib.write_bytes(b"enl")
    en = _EnGia(tv_lib)
    kho = tmp_path / "kho"
    _pdf(kho / "PMID-31218671_UPW.pdf")
    bc, thu_muc = _chay(tmp_path, en, kho=kho)
    assert bc["nap"]["nhap_moi"] == 3 and bc["khong_dinh_danh"]["nhap_moi"] == 2
    b2 = en._bg(en.ma(pmid="31218671"))
    assert b2["nhan"] == "TLTK 2" and b2["tu_khoa"] == ["NC: NC-THU"]
    assert b2["abstract"] == "Abstract gốc của nguồn.", "KHÔNG ghi tóm tắt tiếng Việt — giữ abstract gốc"
    assert b2["tep"].startswith("internal-pdf://") and b2["tep"].endswith("/PMID-31218671.pdf")
    assert en.ma(pmid="16855282"), "DOI-only có PMID trên PubMed ⇒ nhập kèm PMID"
    assert en._bg(en.ma(tieu_de="Sample size determination in health studies: a practical manual"))["loai"] == "Book"
    vb = en._bg(en.ma(loai="Government Document"))
    assert vb["nhan"] == "TLTK 1" and vb["tu_khoa"] == ["NC: NC-THU"]
    assert en.lan_post == 1 and len(en.nhom["NC · NC-THU"]) == 5, "MỘT lượt post gồm cả TLTK không định danh (BH170)"
    assert bc["khong_tach_duoc"] and "TLTK 6" in bc["khong_tach_duoc"][0]
    assert bc["co_toan_van"] == 1 and len(bc["thieu_toan_van"]) == 5
    assert any("TLTK 4" in x and "DOI-10.52163_yhc.v64i1.573.pdf" in x for x in bc["thieu_toan_van"])
    assert T.ma_thoat(bc) == T.MA_MOT_PHAN


def test_chay_lai_khi_bac_si_da_dat_toan_van_thi_gan_va_them_vao_ban_ghi_chi_co_tom_tat(tmp_path):
    tv_lib = tmp_path / "tv.enl"
    tv_lib.write_bytes(b"enl")
    tom_tat = "file:///lib/TomTatChungCu/PMID-31218671_TomTatChungCu.pdf"
    en = _EnGia(tv_lib, co_san=[{"pmid": "31218671", "doi": "10.1111/1475-6773.13187", "tep": tom_tat}])
    thu_muc, _ = _de_tai(tmp_path)
    tv = thu_muc / "toan_van_tltk"
    for ten in ("PMID-31218671.pdf", "PMID-16855282.pdf", "DOI-10.52163_yhc.v64i1.573.pdf", "TLTK-1.pdf", "TLTK-5.pdf"):
        _pdf(tv / ten)
    bc = T.chay([thu_muc / "DE_CUONG_NOP_HOI_DONG_NC-THU.md"], "NC-THU", thu_muc, endnote=en, ap_dung=True, kho=None,
                lay_pm=lambda pmids: {p: META[p] for p in pmids if p in META}, lay_cr=lambda d: META_CR.get(d),
                lay_ep=lambda p: {}, tim_pmid=_tim)
    cu = en._bg(en.ma(pmid="31218671"))
    assert cu["tep"].split("\r")[0] == tom_tat and cu["tep"].split("\r")[1].endswith("/PMID-31218671.pdf"), \
        "THÊM toàn văn, giữ PDF tóm tắt đang có"
    assert bc["them_toan_van"] == ["TLTK 2"]
    assert bc["nap"]["pdf_dinh_kem"] == 2, "PDF ở thư mục đề tài đính NGAY lúc nhập (bộ chọn PDF của người gọi)"
    assert bc["co_toan_van"] == 5 and [x for x in bc["thieu_toan_van"] if "TLTK 6" not in x] == []
    assert en._bg(en.ma(loai="Government Document"))["tep"].endswith("/TLTK-1.pdf")


def test_chay_kho_khong_ghi_gi(tmp_path):
    tv_lib = tmp_path / "tv.enl"
    tv_lib.write_bytes(b"enl")
    en = _EnGia(tv_lib)
    bc, thu_muc = _chay(tmp_path, en, ap_dung=False)
    assert en.so_lan_nhap == 0 and en.nhom == {} and not (thu_muc / "toan_van_tltk").exists()
    assert len(bc["nap"]["ke_hoach_nhap"]) == 3 and len(bc["khong_dinh_danh"]["ke_hoach"]) == 2
    assert bc["cho_gan"] == 0
    kho = tmp_path / "kho"
    _pdf(kho / "PMID-31218671_BANIN.pdf")
    bc, _ = _chay(tmp_path / "lan2", en, ap_dung=False, kho=kho)
    assert bc["cho_gan"] == 1 and any("TLTK 2: có PDF sẵn" in x for x in bc["thieu_toan_van"])


def test_khong_co_endnote_chi_lap_ke_hoach_va_bao_khong_kiem_trung(tmp_path):
    bc, _ = _chay(tmp_path, None, ap_dung=False)
    assert not bc["kiem_trung"] and T.ma_thoat(bc) == T.MA_MOT_PHAN
    assert bc["co_toan_van_san"] == 0 and len(bc["thieu_toan_van"]) == 6


def test_ban_ghi_da_co_giu_nguyen_khong_nhap_lai(tmp_path):
    tv_lib = tmp_path / "tv.enl"
    tv_lib.write_bytes(b"enl")
    en = _EnGia(tv_lib, co_san=[{"pmid": "31218671", "nhan": "nhãn bác sĩ"},
                                {"tieu_de": "Sample size determination in health studies: a practical manual",
                                 "loai": "Book"}])
    bc, _ = _chay(tmp_path, en)
    assert bc["nap"]["da_co"] == 1 and bc["khong_dinh_danh"]["da_co"] == 1
    assert en._bg(en.ma(pmid="31218671"))["nhan"] == "nhãn bác sĩ", "bản ghi đã có không bị sửa nhãn"
    assert len(en.ban_ghi) == 2 + 3, "chỉ nhập 2 bài định danh mới + 1 văn bản nhà nước"


# ── lõi dùng chung: hành vi cũ không đổi, phần mới ─────────────────────────────────────────────────────────────────────

def test_crossref_sach_nhap_thanh_book_co_nha_xuat_ban():
    js = {"message": {"type": "book", "title": ["Multiple imputation for nonresponse in surveys"], "DOI": "10.1002/9780470316696",
                      "author": [{"family": "Rubin", "given": "Donald B."}], "issued": {"date-parts": [[1987]]},
                      "publisher": "Wiley", "publisher-location": "New York", "ISBN": ["9780471087052"],
                      "container-title": ["Wiley Series in Probability and Statistics"]}}
    m = NE.phan_tich_crossref(js)
    assert (m["loai_tl"], m["nha_xb"], m["noi_xb"], m["isbn"], m["tap_chi"]) == \
        ("Book", "Wiley", "New York", "9780471087052", "")
    x = NE.dung_xml([m])
    assert '<ref-type name="Book">6</ref-type>' in x and "<pub-location>New York</pub-location>" in x
    assert "<isbn>9780471087052</isbn>" in x
    bai = NE.phan_tich_crossref({"message": {"type": "journal-article", "title": ["T"], "container-title": ["J"],
                                             "publisher": "P"}})
    assert (bai["loai_tl"], bai["tap_chi"], bai["nha_xb"]) == ("Journal Article", "J", ""), "bài báo không đổi"


def test_dat_pdf_khong_pmid_giu_ten_nguon_an_toan(tmp_path):
    tv = tmp_path / "tv.enl"
    pdf = _pdf(tmp_path / "DOI-10.1_a b.pdf")
    url, tm = NE.dat_pdf_vao_thu_vien(tv, pdf, None)
    assert url.endswith("/DOI-10.1_a_b.pdf") and (tm / "DOI-10.1_a_b.pdf").is_file()
    url, _ = NE.dat_pdf_vao_thu_vien(tv, pdf, "123")
    assert url.endswith("/PMID-123.pdf")


class _EnMacGia(NE.EndNoteMac):
    """EndNoteMac thật với `_chay` giả — đo đúng mã `them_tep` sẽ chạy."""

    def __init__(self, cu: str, nuot: bool = False):
        self.cu, self.nuot, self.lenh = cu, nuot, []

    def _truoc_khi_ghi(self, ly_do):
        pass

    def doc_truong(self, ids, truong):
        return {ids[0]: self.cu}

    def _chay(self, than, *doi_so, **_k):
        self.lenh.append(doi_so)
        if "return field" in than:
            return doi_so[1].split("\r")[-1] if self.nuot else doi_so[1]
        return ""


def test_them_tep_giu_tep_cu_va_ghi_tra_khi_endnote_lam_mat():
    en = _EnMacGia("file:///a_TomTatChungCu.pdf")
    en.them_tep("R", "internal-pdf://1/PMID-1.pdf")
    assert en.lenh == [("R", "file:///a_TomTatChungCu.pdf\rinternal-pdf://1/PMID-1.pdf")]
    en = _EnMacGia("file:///a_TomTatChungCu.pdf", nuot=True)
    with pytest.raises(RuntimeError, match="ghi trả"):
        en.them_tep("R", "internal-pdf://1/PMID-1.pdf")
    assert en.lenh[-1] == ("R", "file:///a_TomTatChungCu.pdf"), "EndNote làm mất tệp cũ ⇒ ghi trả đúng trường cũ"


def test_main_chay_kho_tren_de_tai_va_ma_thoat(tmp_path, monkeypatch, capsys):
    thu_muc, _ = _de_tai(tmp_path)
    monkeypatch.setattr(NE, "_la_mac", lambda: False)
    monkeypatch.setattr(NE, "_tim_dash_goc", lambda: None)
    monkeypatch.setattr(NE, "doc_loai_tru", lambda *a: {"doi": {}, "pmid": {}})
    goc = T.chay

    def chay_gia(*a, **k):
        k.update(lay_pm=lambda pmids: {p: META[p] for p in pmids if p in META}, lay_cr=lambda d: META_CR.get(d),
                 lay_ep=lambda p: {}, tim_pmid=_tim)
        return goc(*a, **k)
    monkeypatch.setattr(T, "chay", chay_gia)
    ma = T.main(["--study", "NC-THU", "--thu-muc-de-tai", str(thu_muc)])
    ra = capsys.readouterr().out
    assert ma == T.MA_MOT_PHAN and "Chạy khô" in ra and "6 TLTK" in ra and not (thu_muc / "ENDNOTE_TLTK_NC-THU.json").exists()
    assert T.main(["--study", "../x"]) == T.MA_THAM_SO


def test_ban_ghi_da_co_chua_dinh_kem_duoc_gan_toan_van_tu_thu_muc_de_tai(tmp_path):
    tv_lib = tmp_path / "tv.enl"
    tv_lib.write_bytes(b"enl")
    en = _EnGia(tv_lib, co_san=[{"pmid": "31218671"}])
    thu_muc, tep = _de_tai(tmp_path)
    _pdf(thu_muc / "toan_van_tltk" / "PMID-31218671.pdf")
    bc = T.chay([tep], "NC-THU", thu_muc, endnote=en, ap_dung=True, kho=None,
                lay_pm=lambda pmids: {p: META[p] for p in pmids if p in META}, lay_cr=lambda d: META_CR.get(d),
                lay_ep=lambda p: {}, tim_pmid=_tim)
    assert bc["nap"]["gan_them_pdf"] == 1 and bc["them_toan_van"] == [], \
        "bản ghi chưa có tệp nào nhận toàn văn ở bước gắn của nap_chu_de (bộ chọn PDF truyền tới xet_toan_van)"
    assert en._bg(en.ma(pmid="31218671"))["tep"].endswith("/PMID-31218671.pdf")
