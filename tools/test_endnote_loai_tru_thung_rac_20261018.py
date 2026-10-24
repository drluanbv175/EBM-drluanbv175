# -*- coding: utf-8 -*-
"""Danh sách loại trừ của bác sĩ + thùng rác EndNote (18/10/2026) — `nap_endnote_chu_de.py`, `tom_tat_endnote_vi.py`.

Sự cố 18/10/2026: bước ⑧ của bộ năm (Viêm gan B) báo «24 trích dẫn · đã có 23 · nhập mới 1» — bản ghi nhập mới là DOI
10.1001/jamaoncol.2018.4070 mà bác sĩ ĐÃ CHỦ Ý bỏ vào thùng rác EndNote. `find` của EndNote không thấy bản ghi trong thùng rác
nên mỗi lượt đều nhập lại (đo trên bản chép thư viện: recNum 7249 và 7324 trong thùng rác, 7327 vừa nhập lại).

Ngoại tuyến hoàn toàn: EndNote là đối tượng giả, metadata là hàm giả, `sdb.eni` là tệp sqlite dựng trong tmp_path.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sqlite3
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


N = _nap("tools/nap_endnote_chu_de.py", "_nap_endnote_loai_tru")


@pytest.fixture(autouse=True)
def _hang_cho_tam(tmp_path, monkeypatch):
    """Hàng chờ đưa vào nhóm (24/10/2026) luôn ở tmp_path — không bao giờ tệp thật trong thư mục nhà."""
    monkeypatch.setenv("EBM_ENDNOTE_CHO_VAO_NHOM", str(tmp_path / "cho-vao-nhom.json"))
tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_loai_tru")

DOI_CHOI = "10.1001/jamaoncol.2018.4070"
MUC_CHOI = {"doi": DOI_CHOI, "ly_do": "Bác sĩ đã bỏ vào thùng rác EndNote — không nạp lại", "ngay": "2026-10-18"}


def _du_lieu():
    return {"meta": {"question": "Viêm gan B mạn — điều trị"}, "items": [
        {"id": "ITEM-01", "pmid": "11111111", "doi": "10.1000/aaa"},
        # Như dashboard thật: chỉ có DOI (bản ghi thật có «Accession Number» rỗng), viết hoa, kèm tiền tố URL.
        {"id": "ITEM-02", "pmid": "", "doi": "https://doi.org/10.1001/JAMAONCOL.2018.4070"},
        {"id": "ITEM-03", "pmid": "22222222", "doi": ""},
    ]}


def _meta(pmid=None, doi=None, nguon="PubMed"):
    return {"pmid": pmid, "doi": doi, "loai_tl": "Journal Article", "tieu_de": f"Bài {pmid or doi}",
            "tac_gia": ["Nguyễn, Văn A"], "tap_chi": "Tạp chí", "tap_chi_viet_tat": "", "nam": "2019",
            "tap": "1", "so": "2", "trang": "3-4", "issn": "", "tom_tat": "", "ngon_ngu": "eng",
            "pmcid": "", "da_rut": False, "nguon_meta": nguon}


def _cau_hinh(tmp_path: Path, bo_qua=None, **khac) -> Path:
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"enl")
    ch = {"thu_vien": str(tv), "ung_dung": "EndNote 2025", **khac}
    if bo_qua is not None:
        ch["bo_qua"] = bo_qua
    p = tmp_path / "ebm-endnote.json"
    p.write_text(json.dumps(ch, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return p


class _EnGia:
    """Mô phỏng EndNote như các test nạp trước: nhập lại sinh bản trùng; nhóm đọc theo group_id (`nhom_theo_ten`), post vào tên
    ĐÃ có nhóm là lỗi của phép thử (EndNote thật sinh nhóm trùng tên — đo 24/10/2026). `find` (tim_khop) KHÔNG thấy bản ghi
    trong thùng rác — đúng hành vi gây sự cố; thùng rác chỉ lộ qua `thung_rac()` (đọc sdb.eni)."""

    def __init__(self, thu_vien: Path, co_san=(), rac=None, rac_loi: Exception | None = None):
        self.thu_vien = thu_vien
        self.ban_ghi: list[dict] = []
        self.nhom: dict[str, list[str]] = {}
        self.so_lan_nhap = 0
        self.da_gan: list[str] = []
        self.goi_rac = 0
        self._rac = rac
        self._rac_loi = rac_loi
        for bg in co_san:
            self._them(*bg)

    def _them(self, pm, doi, tep=""):
        rid = f'<RecordID database="2" recNum="{7320 + len(self.ban_ghi) + 1}" />'
        self.ban_ghi.append({"id": rid, "pmid": pm or "", "doi": (doi or "").lower(), "tep": tep})
        return rid

    def thung_rac(self):
        self.goi_rac += 1
        if self._rac_loi is not None:
            raise self._rac_loi
        return self._rac or {"doi": set(), "pmid": set()}

    def tim_khop(self, gia_tri, truong):
        khoa = "pmid" if truong == "Accession Number" else "doi"
        return {v: [b["id"] for b in self.ban_ghi if b[khoa] and b[khoa] == v.lower()] for v in gia_tri}

    def nhap(self, tep):
        self.so_lan_nhap += 1
        for r in ET.fromstring(Path(tep).read_bytes()).findall("records/record"):
            self._them(r.findtext("accession-num"), r.findtext("electronic-resource-num"),
                       r.findtext("urls/pdf-urls/url") or "")

    def tep_dinh_kem(self, ids):
        return {b["id"]: len(b["tep"]) for b in self.ban_ghi if b["id"] in ids}

    def gan_tep(self, ma, url):
        self.da_gan.append(ma)
        next(b for b in self.ban_ghi if b["id"] == ma)["tep"] = url

    def nhom_theo_ten(self, ten):
        if ten not in self.nhom:
            return []
        rec = [int(re.search(r'recNum="(\d+)"', i).group(1)) for i in self.nhom[ten]]
        return [{"group_id": 1, "ten": ten, "so_ban_ghi": len(rec), "rec": rec}]

    def dang_vao_nhom(self, ids, ten):
        assert ten not in self.nhom, "post vào tên đã có nhóm ⇒ EndNote sinh nhóm trùng tên (đo 24/10/2026)"
        self.nhom[ten] = list(ids)

    def ma_cua(self, pm=None, doi=None) -> list[str]:
        return [b["id"] for b in self.ban_ghi if (pm and b["pmid"] == pm) or (doi and b["doi"] == doi)]


class _EnKhongRac(_EnGia):
    thung_rac = None  # lớp EndNote không đọc được thùng rác


NHOM = "EBM · Viêm gan B mạn — điều trị"


def _nap_cd(tmp_path, en, loai_tru=None, du_lieu=None, lay_pm=None, kho=None, ap_dung=True, goi_cr=None):
    dash = tmp_path / "WebDashboard_EBM_VanDeCuThe_ViemGanB_DieuTri_20260716.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    goi_cr = goi_cr if goi_cr is not None else []

    def lay_cr(doi):
        goi_cr.append(doi)
        return _meta(None, doi, nguon="Crossref")
    return N.nap_chu_de(dash, endnote=en, ap_dung=ap_dung, kho=kho, doc_data=lambda p: du_lieu or _du_lieu(),
                        lay_pm=lay_pm or (lambda pmids: {p: _meta(p) for p in pmids}), lay_ep=lambda pmids: {},
                        lay_cr=lay_cr, loai_tru=loai_tru)


# ── khuôn khoá `bo_qua` = một phần của «cấu hình dùng được» ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("bo_qua, chu", [
    ("10.1001/x", "không phải danh sách"),
    (["10.1001/x"], "không phải bảng"),
    ([{"ly_do": "x", "ngay": "2026-10-18"}], "thiếu «doi»/«pmid»"),
    ([{"doi": "không phải doi", "ly_do": "x", "ngay": "2026-10-18"}], "DOI sai khuôn"),
    ([{"pmid": "12ab", "ly_do": "x", "ngay": "2026-10-18"}], "PMID sai khuôn"),
    ([{"pmid": True, "ly_do": "x", "ngay": "2026-10-18"}], "PMID sai khuôn"),
    ([{"doi": DOI_CHOI, "ly_do": "  ", "ngay": "2026-10-18"}], "thiếu «ly_do»"),
    ([{"doi": DOI_CHOI, "ly_do": "x"}], "thiếu «ngay»"),
    ([{"doi": DOI_CHOI, "ly_do": "x", "ngay": "18/10/2026"}], "thiếu «ngay»"),
    ([MUC_CHOI, {"doi": DOI_CHOI, "pmid": "1x", "ly_do": "x", "ngay": "2026-10-18"}], "mục 2"),
])
def test_bo_qua_sai_khuon_la_cau_hinh_hong(tmp_path, bo_qua, chu):
    p = _cau_hinh(tmp_path, bo_qua)
    assert N.doc_cau_hinh(p) is None, "danh sách loại trừ sai khuôn ⇒ cấu hình không dùng được"
    ly = N.ly_do_cau_hinh_hong(p)
    assert ly and chu in ly, ly
    with pytest.raises(N.CauHinhHong):
        N.doc_loai_tru(p)


def test_bo_qua_dung_khuon_hoac_vang_thi_cau_hinh_dung_duoc(tmp_path):
    p = _cau_hinh(tmp_path, [MUC_CHOI, {"pmid": 30267080, "ly_do": "x", "ngay": "2026-10-18"},
                             {"doi": "https://doi.org/10.1000/AAA", "pmid": "11111111", "ly_do": "y", "ngay": "2026-10-18"}])
    assert N.ly_do_cau_hinh_hong(p) is None and N.doc_cau_hinh(p) is not None
    lt = N.doc_loai_tru(p)
    assert set(lt["doi"]) == {DOI_CHOI, "10.1000/aaa"} and set(lt["pmid"]) == {"30267080", "11111111"}
    assert N.muc_loai_tru(lt, None, "https://doi.org/10.1001/JAMAONCOL.2018.4070") is lt["doi"][DOI_CHOI]
    assert N.muc_loai_tru(lt, "99999999", None) is None
    assert N.doc_loai_tru(tmp_path / "vang.json") == {"doi": {}, "pmid": {}}, "tệp vắng ⇒ rỗng, không phải hỏng"
    assert N.ly_do_cau_hinh_hong(_cau_hinh(tmp_path)) is None, "không có khoá bo_qua ⇒ vẫn dùng được"


# ── nạp chủ đề ──────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_su_co_18_10_khong_nhap_lai_doi_bac_si_da_loai_bai_khac_van_nap(tmp_path):
    en = _EnGia(tmp_path / "tv.enl", co_san=[("11111111", "10.1000/aaa")])
    lt = N.doc_loai_tru(_cau_hinh(tmp_path, [MUC_CHOI]))
    goi_cr: list[str] = []
    for _ in range(2):  # sự cố: MỖI lượt bộ năm nhập lại
        bc = _nap_cd(tmp_path, en, lt, goi_cr=goi_cr)
        assert not en.ma_cua(doi=DOI_CHOI), "bản ghi bác sĩ đã loại không được nhập lại"
        assert [x["dinh_danh"] for x in bc["loai_tru"]] == [f"DOI {DOI_CHOI}"]
        assert bc["loai_tru"][0]["ly_do"] == MUC_CHOI["ly_do"] and bc["loai_tru"][0]["con_trong_thu_vien"] == []
    assert DOI_CHOI not in goi_cr, "loại trừ xét TRƯỚC khi tra metadata"
    assert en.ma_cua(pm="22222222"), "loại trừ không được chặn bài khác"
    assert sorted(en.nhom[NHOM]) == sorted(en.ma_cua(pm="11111111") + en.ma_cua(pm="22222222"))
    assert (bc["so_trich_dan"], bc["da_co"], bc["nhap_moi"]) == (3, 2, 0)


def test_khong_co_danh_sach_thi_hanh_vi_cu_nhap_nhu_truoc(tmp_path):
    en = _EnKhongRac(tmp_path / "tv.enl", co_san=[("11111111", "10.1000/aaa")])
    bc = _nap_cd(tmp_path, en, None)
    assert en.ma_cua(doi=DOI_CHOI) and bc["nhap_moi"] == 2 and bc["loai_tru"] == []


def test_ban_ghi_bi_loai_con_trong_thu_vien_thi_khong_dang_nhom_khong_gan_pdf_chi_bao(tmp_path, capsys):
    kho = tmp_path / "toan_van_oa"
    kho.mkdir()
    (kho / "PMID-11111111_UPW.pdf").write_bytes(b"%PDF-1.4 a")
    (kho / "PMID-22222222_UPW.pdf").write_bytes(b"%PDF-1.4 b")
    en = _EnGia(tmp_path / "tv.enl", co_san=[("11111111", "10.1000/aaa"), ("22222222", "")])
    lt = N.doc_loai_tru(_cau_hinh(tmp_path, [{"pmid": "11111111", "ly_do": "Bác sĩ không dùng", "ngay": "2026-10-18"}]))
    bc = _nap_cd(tmp_path, en, lt, kho=kho)
    bi_loai = en.ma_cua(pm="11111111")
    assert bc["loai_tru"][0]["con_trong_thu_vien"] == [N._so_ban_ghi(bi_loai[0])]
    assert not set(bi_loai) & set(en.nhom[NHOM]), "bản ghi bị loại không được đăng vào nhóm"
    assert not set(bi_loai) & set(en.da_gan), "bản ghi bị loại không được gắn PDF"
    assert en.ma_cua(pm="22222222")[0] in en.da_gan, "bản ghi khác vẫn được gắn PDF"
    assert len(en.ban_ghi) == 3, "công cụ không xoá bản ghi nào (chỉ thêm DOI Choi mới)"
    N._in_bao_cao(bc)
    out = capsys.readouterr().out
    assert "3 trích dẫn · bỏ qua 1 · đã có trong thư viện 1" in out
    assert "⊘ bỏ qua theo danh sách loại trừ của bác sĩ: PMID 11111111 · DOI 10.1000/aaa — «Bác sĩ không dùng»" in out
    assert f"recNum {N._so_ban_ghi(bi_loai[0])}" in out and "thao tác của bác sĩ" in out


def test_loai_tru_xet_lai_theo_dinh_danh_cua_metadata(tmp_path):
    """Dashboard chỉ ghi PMID mà bác sĩ loại theo DOI: DOI chỉ biết sau khi tra PubMed ⇒ phải xét lại trước khi nhập."""
    en = _EnGia(tmp_path / "tv.enl", co_san=[("11111111", "10.1000/aaa")])
    lt = N.doc_loai_tru(_cau_hinh(tmp_path, [{"doi": "10.1000/ccc", "ly_do": "x", "ngay": "2026-10-18"}]))
    bc = _nap_cd(tmp_path, en, lt, lay_pm=lambda pmids: {p: _meta(p, "10.1000/ccc" if p == "22222222" else None)
                                                         for p in pmids})
    assert not en.ma_cua(pm="22222222") and not en.ma_cua(doi="10.1000/ccc")
    assert [x["dinh_danh"] for x in bc["loai_tru"]] == ["PMID 22222222 · DOI 10.1000/ccc"]
    assert bc["loai_tru"][0]["con_trong_thu_vien"] is None, "chưa tra thư viện theo DOI của metadata ⇒ không khẳng định"
    assert bc["nhap_moi"] == 1 and en.ma_cua(doi=DOI_CHOI), "bài khác vẫn nhập"


def test_trong_thung_rac_thi_khong_nhap_lai_ke_ca_khi_chua_khai_loai_tru(tmp_path):
    en = _EnGia(tmp_path / "tv.enl", co_san=[("11111111", "10.1000/aaa")], rac={"doi": {DOI_CHOI}, "pmid": set()})
    goi_cr: list[str] = []
    bc = _nap_cd(tmp_path, en, None, goi_cr=goi_cr)
    assert not en.ma_cua(doi=DOI_CHOI) and bc["trong_thung_rac"] == [f"DOI {DOI_CHOI}"]
    assert bc["thung_rac_do_duoc"] is True and DOI_CHOI not in goi_cr
    assert en.ma_cua(pm="22222222") and bc["nhap_moi"] == 1


def test_thung_rac_xet_lai_theo_metadata(tmp_path):
    en = _EnGia(tmp_path / "tv.enl", co_san=[("11111111", "10.1000/aaa")], rac={"doi": {"10.1000/ccc"}, "pmid": set()})
    bc = _nap_cd(tmp_path, en, None, lay_pm=lambda pmids: {p: _meta(p, "10.1000/ccc") for p in pmids})
    assert not en.ma_cua(pm="22222222") and bc["trong_thung_rac"] == ["PMID 22222222 · DOI 10.1000/ccc"]


def test_co_ban_song_thi_ban_trong_thung_rac_khong_lam_gi(tmp_path):
    """Bác sĩ khôi phục (hoặc giữ) một bản sống: bản sống là của bác sĩ ⇒ «đã có», vẫn vào nhóm như cũ."""
    en = _EnGia(tmp_path / "tv.enl", co_san=[("11111111", "10.1000/aaa"), ("22222222", ""), (None, DOI_CHOI)],
                rac={"doi": {DOI_CHOI}, "pmid": set()})
    bc = _nap_cd(tmp_path, en, None)
    assert bc["da_co"] == 3 and bc["trong_thung_rac"] == [] and en.ma_cua(doi=DOI_CHOI)[0] in en.nhom[NHOM]
    assert en.goi_rac == 0 and bc["thung_rac_do_duoc"] is None, "không có bài mới ⇒ không cần đo thùng rác"


@pytest.mark.parametrize("en_tao", [
    lambda tv: _EnKhongRac(tv, co_san=[("11111111", "10.1000/aaa")]),
    lambda tv: _EnGia(tv, co_san=[("11111111", "10.1000/aaa")], rac_loi=sqlite3.OperationalError("no such column")),
    lambda tv: _EnGia(tv, co_san=[("11111111", "10.1000/aaa")], rac_loi=OSError("không thấy sdb.eni")),
])
def test_khong_do_duoc_thung_rac_thi_bao_ro_khong_coi_la_rong(tmp_path, capsys, en_tao):
    en = en_tao(tmp_path / "tv.enl")
    bc = _nap_cd(tmp_path, en, None)
    assert bc["thung_rac_do_duoc"] is False and bc["thung_rac_loi"]
    N._in_bao_cao(bc)
    assert "⚪ Chưa đo được thùng rác EndNote" in capsys.readouterr().out


def test_nap_nhieu_tu_doc_danh_sach_tu_cau_hinh_va_cau_hinh_hong_thi_khong_nhap(tmp_path, capsys):
    dash = tmp_path / "WebDashboard_EBM_VanDeCuThe_ViemGanB_DieuTri_20260716.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    en = _EnGia(tmp_path / "tv.enl", co_san=[("11111111", "10.1000/aaa")])
    lay = {"lay_pm": lambda pmids: {p: _meta(p) for p in pmids}, "lay_ep": lambda pmids: {},
           "lay_cr": lambda doi: _meta(None, doi, nguon="Crossref")}
    ch = _cau_hinh(tmp_path, [MUC_CHOI])
    N.nap_nhieu([dash], endnote=en, ap_dung=True, kho=None, doc_data=lambda p: _du_lieu(), cau_hinh=ch, **lay)
    assert not en.ma_cua(doi=DOI_CHOI)
    hong = _cau_hinh(tmp_path, [{"doi": "sai", "ly_do": "x", "ngay": "2026-10-18"}])
    truoc = len(en.ban_ghi)
    with pytest.raises(N.CauHinhHong):
        N.nap_nhieu([dash], endnote=en, ap_dung=True, kho=None, doc_data=lambda p: _du_lieu(), cau_hinh=hong, **lay)
    assert len(en.ban_ghi) == truoc and en.so_lan_nhap == 1, "cấu hình hỏng ⇒ không nhập gì"


# ── đọc thùng rác từ sdb.eni (chỉ đọc) ──────────────────────────────────────────────────────────────────────────────────

def _sdb(tv: Path, dong: list[tuple], co_cot_rac: bool = True) -> Path:
    sdb = tv.with_suffix(".Data") / "sdb" / "sdb.eni"
    sdb.parent.mkdir(parents=True)
    kn = sqlite3.connect(sdb)
    cot = "id INTEGER PRIMARY KEY, " + ("trash_state INTEGER, " if co_cot_rac else "") + \
          "accession_number TEXT, electronic_resource_number TEXT"
    kn.execute(f"CREATE TABLE refs ({cot})")
    for d in dong:
        kn.execute(f"INSERT INTO refs VALUES ({','.join('?' * len(d))})", d)
    kn.commit()
    kn.close()
    return sdb


def test_doc_thung_rac_chi_lay_ban_trong_thung_rac_chuan_hoa_va_khong_ghi_tep(tmp_path):
    tv = tmp_path / "Thư viện EBM #1.enl"   # khoảng trắng, dấu tiếng Việt, «#» — đường dẫn URI phải mã hoá đúng
    tv.write_bytes(b"enl")
    sdb = _sdb(tv, [(7249, 1, "", DOI_CHOI), (7324, 1, "", "https://doi.org/10.1001/JAMAONCOL.2018.4070"),
                    (7327, 0, "", DOI_CHOI), (7400, 1, " 33333333 ", ""), (7401, 0, "44444444", "10.1000/song")])
    bam = hashlib.sha256(sdb.read_bytes()).hexdigest()
    tep_truoc = sorted(p.name for p in sdb.parent.iterdir())
    rac = N.doc_thung_rac(tv)
    assert rac == {"doi": {DOI_CHOI}, "pmid": {"33333333"}}
    assert N.EndNoteMac.thung_rac(SimpleNamespace(thu_vien=tv)) == rac
    assert hashlib.sha256(sdb.read_bytes()).hexdigest() == bam, "không bao giờ ghi sdb.eni"
    assert sorted(p.name for p in sdb.parent.iterdir()) == tep_truoc, "không sinh tệp nhật ký/wal cạnh sdb.eni"


def test_doc_thung_rac_luoc_do_la_hoac_thieu_tep_thi_nem_loi(tmp_path):
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"enl")
    with pytest.raises(OSError):
        N.doc_thung_rac(tv)
    _sdb(tv, [(1, "", DOI_CHOI)], co_cot_rac=False)
    with pytest.raises(sqlite3.Error):
        N.doc_thung_rac(tv)
    rac, loi = N.doc_thung_rac_an_toan(SimpleNamespace(thung_rac=lambda: N.doc_thung_rac(tv)))
    assert rac is None and "OperationalError" in loi


# ── lệnh --loai-tru ─────────────────────────────────────────────────────────────────────────────────────────────────────

def test_them_loai_tru_chay_kho_roi_ap_dung_sao_luu_truoc(tmp_path):
    p = _cau_hinh(tmp_path, nhom_theo_chu_de={"EBM_X": "EBM · X"})
    goc = p.read_text(encoding="utf-8")
    kq = N.them_loai_tru("https://doi.org/10.1001/JAMAONCOL.2018.4070", "Đã bỏ vào thùng rác", ap_dung=False, tep=p,
                         hom_nay="2026-10-18")
    assert kq["trang_thai"] == "se_them" and p.read_text(encoding="utf-8") == goc, "chạy khô không ghi"
    kq = N.them_loai_tru(DOI_CHOI, "Đã bỏ vào thùng rác", ap_dung=True, tep=p, hom_nay="2026-10-18")
    assert kq["trang_thai"] == "da_them" and Path(kq["sao_luu"]).read_text(encoding="utf-8") == goc
    ch = json.loads(p.read_text(encoding="utf-8"))
    assert ch["bo_qua"] == [{"doi": DOI_CHOI, "ly_do": "Đã bỏ vào thùng rác", "ngay": "2026-10-18"}]
    assert ch["nhom_theo_chu_de"] == {"EBM_X": "EBM · X"}, "giữ nguyên phần còn lại của cấu hình"
    assert N.them_loai_tru(DOI_CHOI.upper(), "lần hai", ap_dung=True, tep=p)["trang_thai"] == "da_co"
    assert len(json.loads(p.read_text(encoding="utf-8"))["bo_qua"]) == 1
    kq = N.them_loai_tru("PMID: 30267080", "x", ap_dung=True, tep=p, hom_nay="2026-10-18")
    assert kq["muc"] == {"pmid": "30267080", "ly_do": "x", "ngay": "2026-10-18"}
    assert N.ly_do_cau_hinh_hong(p) is None, "tệp sau khi ghi vẫn đúng khuôn"


def test_them_loai_tru_tu_choi_tham_so_sai_va_cau_hinh_hong_hoac_vang(tmp_path):
    p = _cau_hinh(tmp_path)
    with pytest.raises(ValueError):
        N.them_loai_tru("không phải định danh", "x", ap_dung=True, tep=p)
    with pytest.raises(ValueError):
        N.them_loai_tru(DOI_CHOI, "   ", ap_dung=True, tep=p)
    hong = _cau_hinh(tmp_path, [{"doi": "sai", "ly_do": "x", "ngay": "2026-10-18"}])
    goc = hong.read_text(encoding="utf-8")
    with pytest.raises(N.CauHinhHong):
        N.them_loai_tru(DOI_CHOI, "x", ap_dung=True, tep=hong)
    assert hong.read_text(encoding="utf-8") == goc, "không bao giờ ghi vào tệp hỏng"
    with pytest.raises(N.KhongChayDuoc):
        N.them_loai_tru(DOI_CHOI, "x", ap_dung=True, tep=tmp_path / "vang.json")
    assert not (tmp_path / "vang.json").exists()


def test_main_loai_tru(tmp_path, monkeypatch, capsys):
    p = _cau_hinh(tmp_path)
    monkeypatch.setattr(N, "CAU_HINH", p)
    goc = p.read_text(encoding="utf-8")
    assert N.main(["--loai-tru", DOI_CHOI, "--ly-do", "Đã bỏ vào thùng rác"]) == 0
    assert p.read_text(encoding="utf-8") == goc and "Chạy khô" in capsys.readouterr().out
    assert N.main(["--loai-tru", DOI_CHOI, "--ly-do", "Đã bỏ vào thùng rác", "--ap-dung"]) == 0
    assert "✓ Đã thêm DOI 10.1001/jamaoncol.2018.4070" in capsys.readouterr().out
    assert json.loads(p.read_text(encoding="utf-8"))["bo_qua"][0]["doi"] == DOI_CHOI
    assert N.main(["--loai-tru", DOI_CHOI]) == 3, "thiếu --ly-do"
    assert N.main(["--ly-do", "x"]) == 3
    assert N.main(["--loai-tru", DOI_CHOI, "--ly-do", "x", "--file", str(tmp_path / "a.html")]) == 3


def test_ghi_cau_hinh_giu_danh_sach_loai_tru(tmp_path):
    p = _cau_hinh(tmp_path, [MUC_CHOI])
    tv2 = tmp_path / "tv2.enl"
    tv2.write_bytes(b"enl")
    N.ghi_cau_hinh(str(tmp_path / "tv.enl"), "EndNote 2025", tep=p)
    assert json.loads(p.read_text(encoding="utf-8"))["bo_qua"] == [MUC_CHOI]
    N.ghi_cau_hinh(str(tv2), "EndNote 2025", tep=p)
    assert json.loads(p.read_text(encoding="utf-8"))["bo_qua"] == [MUC_CHOI], "đổi thư viện vẫn giữ quyết định của bác sĩ"


# ── main: cấu hình hỏng ⇒ không nhập gì, không im lặng ─────────────────────────────────────────────────────────────────

def test_main_bo_qua_sai_khuon_thi_khong_cham_endnote(tmp_path, monkeypatch, capsys):
    p = _cau_hinh(tmp_path, [{"doi": "gõ sai", "ly_do": "x", "ngay": "2026-10-18"}])
    monkeypatch.setattr(N, "CAU_HINH", p)
    monkeypatch.setattr(N, "_la_mac", lambda: True)
    tao: list = []
    monkeypatch.setattr(N, "EndNoteMac", lambda *a, **k: tao.append(a) or pytest.fail("không được dựng EndNote"))
    dash = tmp_path / "WebDashboard_X_20261018.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    (tmp_path / "toan_van_oa").mkdir()
    assert N.main(["--file", str(dash), "--ap-dung"]) == 2
    assert "tệp cấu hình hỏng" in capsys.readouterr().out
    assert N.main(["--file", str(dash), "--ap-dung", "--im-khi-chua-cau-hinh"]) == 0
    out = capsys.readouterr().out
    assert "⚪ EndNote: bỏ qua — tệp cấu hình hỏng" in out and "bo_qua" in out
    assert tao == []


def test_main_cau_hinh_hong_giua_hai_lan_doc_thi_van_khong_nhap(tmp_path, monkeypatch, capsys):
    """Nhánh phòng thủ: tệp đọc được lúc kiểm cấu hình nhưng hỏng lúc đọc danh sách loại trừ (OneDrive đang ghi, bác sĩ
    đang sửa tay) ⇒ --ap-dung KHÔNG được nhập với danh sách rỗng."""
    monkeypatch.setattr(N, "CAU_HINH", _cau_hinh(tmp_path))
    monkeypatch.setattr(N, "_la_mac", lambda: True)

    class _EnMo:
        def __init__(self, ung_dung, thu_vien):
            self.thu_vien = thu_vien

        def dang_mo_dung_thu_vien(self):
            return True
    monkeypatch.setattr(N, "EndNoteMac", _EnMo)

    def hong(tep=None):
        raise N.CauHinhHong("tệp cấu hình hỏng — giả lập")
    monkeypatch.setattr(N, "doc_loai_tru", hong)
    monkeypatch.setattr(N, "nap_nhieu", lambda *a, **k: pytest.fail("không được nạp khi không đọc được danh sách"))
    dash = tmp_path / "WebDashboard_X_20261018.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    kho = tmp_path / "toan_van_oa"
    kho.mkdir()
    assert N.main(["--file", str(dash), "--ap-dung", "--kho-toan-van", str(kho)]) == 2
    assert "không nhập gì" in capsys.readouterr().out


def test_main_xuat_xml_ap_dung_loai_tru_va_tu_choi_cau_hinh_hong(tmp_path, monkeypatch, capsys):
    dash = tmp_path / "WebDashboard_EBM_VanDeCuThe_ViemGanB_DieuTri_20260716.html"
    dash.write_text("x", encoding="utf-8", newline="\n")
    monkeypatch.setattr(N, "_nap_doc_data", lambda: (lambda p: _du_lieu()))
    da_tra: list[dict] = []

    def lay_metadata(dd, *a):
        da_tra.extend(dd)
        # PubMed trả DOI cho PMID 22222222 mà dashboard không ghi ⇒ chỉ lớp xét-lại-theo-metadata bắt được.
        return [(d, _meta(d.get("pmid"), d.get("doi") or ("10.1000/ccc" if d.get("pmid") == "22222222" else None)))
                for d in dd], []
    monkeypatch.setattr(N, "lay_metadata", lay_metadata)
    monkeypatch.setattr(N, "CAU_HINH", _cau_hinh(tmp_path, [MUC_CHOI, {"doi": "10.1000/ccc", "ly_do": "x",
                                                                         "ngay": "2026-10-18"}]))
    ra = tmp_path / "ra.xml"
    assert N.main(["--file", str(dash), "--xuat-xml", str(ra)]) == 0
    xml = ra.read_text(encoding="utf-8")
    assert "11111111" in xml and DOI_CHOI not in xml.lower() and "22222222" not in xml
    assert not any(d.get("doi") == DOI_CHOI for d in da_tra), "loại trừ xét TRƯỚC khi tra metadata"
    assert "⊘ bỏ qua theo danh sách loại trừ của bác sĩ" in capsys.readouterr().out
    monkeypatch.setattr(N, "CAU_HINH", _cau_hinh(tmp_path, [{"pmid": "x", "ly_do": "x", "ngay": "2026-10-18"}]))
    ra2 = tmp_path / "ra2.xml"
    assert N.main(["--file", str(dash), "--xuat-xml", str(ra2)]) == 2 and not ra2.exists()


# ── bước tóm tắt tiếng Việt ─────────────────────────────────────────────────────────────────────────────────────────────

MUC_TT = {"id": "ITEM-01", "title": "Entecavir hay tenofovir", "source": "x", "design": "Cohort", "org": "",
          "dateVersion": "2019", "pmid": "31111111", "doi": "10.1016/aaa", "population": "VGB mạn",
          "pico": {"P": "VGB", "I": "TDF", "C": "ETV", "O": "HCC"}, "effectText": "x", "effect": {},
          "gradeLevel": "low", "gradeBy": "", "gradeSource": "", "decision": "consider", "action": "x", "monitoring": "",
          "vn": "", "flag": "", "safety": "",
          "references": ["Phụ lục: Smith J. PMID 32222222", "Chỉ DOI: doi:10.1093/bbb"]}


class _EnTomTat:
    def __init__(self, khop):
        self.khop = khop
        self.da_ghi: list[str] = []
        self.thu_vien = Path("/khong-ton-tai/tv.enl")

    def tim_khop(self, gia_tri, truong):
        return {v: self.khop[v] for v in gia_tri if v in self.khop}

    def doc_truong(self, ids, truong):
        return {m: "Original." for m in ids}

    def ghi_truong(self, cap, truong):
        self.da_ghi += [m for m, _ in cap]
        return {m: "" for m, _ in cap}


def _tom_tat(en, bo_qua):
    f = Path("/khong-ton-tai/WebDashboard_X_20260716.html")
    d = {"meta": {"question": "VGB"}, "items": [MUC_TT]}
    return tt.ghi_tom_tat(en, [f], kho=None, ap_dung=True, doc_data=lambda p: d, sao_luu=lambda: "/s", bo_qua=bo_qua)


def test_tom_tat_bo_qua_ban_bac_si_da_loai_khong_moi_nap_lai(tmp_path):
    lt = N.doc_loai_tru(_cau_hinh(tmp_path, [{"doi": "10.1093/bbb", "ly_do": "x", "ngay": "2026-10-18"},
                                             {"pmid": "32222222", "ly_do": "y", "ngay": "2026-10-18"}]))
    en = _EnTomTat({"31111111": ["r1"], "32222222": ["r2"]})
    bc = _tom_tat(en, N.ham_bo_qua(lt, None))
    assert bc["khong_co_ban_ghi"] == [], "bài bác sĩ đã loại không được mời «nạp chủ đề trước»"
    assert en.da_ghi == ["r1"], "bản ghi bị loại (r2) không được ghi khối; bản ghi khác vẫn ghi"
    assert len(bc["bo_qua_theo_bac_si"]) == 2


def test_tom_tat_thung_rac_chi_ap_khi_chua_co_ban_song(tmp_path):
    en = _EnTomTat({"31111111": ["r1"], "32222222": ["r2"]})
    bc = _tom_tat(en, N.ham_bo_qua(None, {"doi": {"10.1093/bbb"}, "pmid": {"31111111"}}))
    assert bc["khong_co_ban_ghi"] == [] and bc["bo_qua_theo_bac_si"] == ["DOI 10.1093/bbb (đang nằm trong thùng rác EndNote)"]
    assert sorted(en.da_ghi) == ["r1", "r2"], "PMID 31111111 có bản sống ⇒ vẫn ghi dù một bản khác nằm trong thùng rác"
    assert N.ham_bo_qua(None, None) is None and N.ham_bo_qua({"doi": {}, "pmid": {}}, {"doi": set(), "pmid": set()}) is None
