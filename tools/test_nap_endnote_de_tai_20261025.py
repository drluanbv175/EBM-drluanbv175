# -*- coding: utf-8 -*-
"""EndNote: nạp trích dẫn của một ĐỀ TÀI nghiên cứu (`--de-tai`) · `_tai()` thử lại khi efetch đứt giữa chừng (25/10/2026).

Bối cảnh 25/10/2026: đề tài `btm-dtd2-ngoai-tru-BVQY175` cần 66 trích dẫn trong EndNote. Công cụ chỉ nhận dashboard nên phiên
trước phải nạp bằng kịch bản tạm gọi API `nap_nhieu` với `doc_data` dựng từ `DANH_MUC_TRICH_DAN_<mã>.json`; lượt đó còn vỡ vì
efetch PubMed cho 52 PMID đứt sau 1.160.011 byte — `http.client.IncompleteRead` không phải lớp con của URLError/OSError nên
`_tai()` không thử lại và lỗi lọt qua `lay_metadata` (chỉ bắt RuntimeError/ParseError/OSError) làm hỏng cả lượt.

Khoá: `--de-tai` đọc danh mục → nhóm mặc định «NC · <tên đề tài> (<mã>)», khoá chủ đề «DE-TAI_<mã>» (đúng khoá lượt tay đã ghi
nhớ ⇒ nhóm ghi nhớ thắng, không post nhóm thứ hai) · KHÔNG chạy bước tóm tắt tiếng Việt (bác sĩ dặn 25/10) và vì thế thiếu kho
không chặn ghi · không đoán `toan_van_oa` cạnh thư mục đang đứng · chạy khô không nhập · tham số xung đột/mã sai ⇒ 3 · danh mục
hỏng ⇒ 2. `_tai()` thử lại khi `IncompleteRead`, hết lượt ⇒ RuntimeError để `lay_metadata` lùi sang Europe PMC.
Ngoại tuyến: EndNote giả, mạng giả (urlopen thay trong test); mọi đường dẫn trong tmp_path.
"""
from __future__ import annotations

import http.client
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MA = "btm-thu-nghiem-BVQY175"
TEN_DE_TAI = "Bảo vệ thận ở người đái tháo đường típ 2 ngoại trú"


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


N = _nap("_nec_t1025", "nap_endnote_chu_de.py")


@pytest.fixture(autouse=True)
def _hang_cho_tam(tmp_path, monkeypatch):
    """Hàng chờ đưa vào nhóm luôn ở tmp_path — không bao giờ tệp thật trong thư mục nhà."""
    monkeypatch.setenv("EBM_ENDNOTE_CHO_VAO_NHOM", str(tmp_path / "cho-vao-nhom.json"))


# ── _tai(): thử lại khi gói tải đứt giữa chừng ─────────────────────────────────────────────────────

class _PhanHoi:
    def __init__(self, du_lieu: bytes | None):
        self.du_lieu = du_lieu

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self) -> bytes:
        if self.du_lieu is None:  # đo 25/10/2026: efetch 52 PMID đứt sau 1.160.011 byte
            raise http.client.IncompleteRead(b"x" * 1_160_011, 4096)
        return self.du_lieu


def _mang_gia(monkeypatch, *luot: bytes | None) -> list[str]:
    """urlopen giả trả lần lượt các phản hồi trong `luot` (None = đứt giữa chừng); lượt cuối lặp lại mãi."""
    goi: list[str] = []

    def urlopen(req, timeout=30):
        goi.append(req.full_url)
        return _PhanHoi(luot[min(len(goi), len(luot)) - 1])

    monkeypatch.setattr(N.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(N.time, "sleep", lambda s: None)
    return goi


def test_tai_thu_lai_khi_doc_dut_giua_chung(monkeypatch):
    goi = _mang_gia(monkeypatch, None, b"<ok/>")
    assert N._tai("https://eutils.example/efetch") == b"<ok/>"
    assert len(goi) == 2, "IncompleteRead phải được thử lại như lỗi mạng"


def test_tai_het_luot_thi_bao_runtime_error_khong_lot_incomplete_read(monkeypatch):
    goi = _mang_gia(monkeypatch, None)
    with pytest.raises(RuntimeError, match="không tải được sau 3 lần"):
        N._tai("https://eutils.example/efetch")
    assert len(goi) == 3


def test_efetch_dut_mai_thi_lay_metadata_lui_europepmc_khong_hong_ca_luot(monkeypatch):
    """Đường thật của lượt nạp: lay_pubmed → _tai đứt mãi ⇒ RuntimeError ⇒ lay_metadata lùi Europe PMC (không văng lỗi)."""
    _mang_gia(monkeypatch, None)
    monkeypatch.setattr(N, "_email", lambda: "")
    dd = [{"pmid": "111", "doi": None, "vai": "muc", "muc": "T01"}]
    co, thieu = N.lay_metadata(dd, lay_ep=lambda pmids: {p: {"pmid": p, "nguon_meta": "Europe PMC"} for p in pmids},
                               lay_cr=lambda doi: None)
    assert [m["nguon_meta"] for _, m in co] == ["Europe PMC"] and thieu == []


# ── đọc danh mục trích dẫn của đề tài ──────────────────────────────────────────────────────────────

def _de_tai(goc: Path, ma: str = MA, trich_dan=None, meta: dict | bool | None = None, study: str | None = MA) -> Path:
    """Dựng exports/<mã>/ giả; trả thư mục exports. `meta=False` = không có study_meta.json."""
    exports = goc / "exports"
    d = exports / ma
    d.mkdir(parents=True)
    dm = {"schema": "de_tai/danh_muc_trich_dan/v1", "ngay": "2026-10-25",
          "trich_dan": trich_dan if trich_dan is not None else [
              {"id": "T01", "pmid": "111", "doi": None, "vai": "nen_G0"},
              {"id": "T02", "pmid": 222, "doi": None},
              {"id": "V01", "pmid": None, "doi": "10.5555/VN.2025.01"},
          ]}
    if study is not None:
        dm["study"] = study
    (d / f"DANH_MUC_TRICH_DAN_{ma}.json").write_text(json.dumps(dm, ensure_ascii=False), encoding="utf-8", newline="\n")
    if meta is not False:
        (d / "study_meta.json").write_text(json.dumps(meta or {"title": TEN_DE_TAI}, ensure_ascii=False),
                                           encoding="utf-8", newline="\n")
    return exports


def test_doc_de_tai_dung_khoi_giong_dashboard_va_khoa_chu_de(tmp_path):
    data, gia = N.doc_de_tai(MA, _de_tai(tmp_path))
    assert data["meta"]["question"] == f"{TEN_DE_TAI} ({MA})"
    assert [(i["id"], i["pmid"], i["doi"]) for i in data["items"]] == [
        ("T01", "111", None), ("T02", 222, None), ("V01", None, "10.5555/VN.2025.01")]
    assert gia.name == f"DE-TAI_{MA}.json" and N.khoa_chu_de(gia) == f"DE-TAI_{MA}", "khoá lượt tay 25/10 đã ghi nhớ"
    dd = N.trich_dinh_danh(data)
    assert [(x["pmid"], x["doi"]) for x in dd] == [("111", None), ("222", None), (None, "10.5555/vn.2025.01")]


def test_ten_de_tai_gon_giu_ma_va_thieu_ten_thi_la_ma():
    dai = "Đề tài " * 40
    ten = N.ten_de_tai({"title": dai}, MA)
    assert len(ten) <= 100 and ten.endswith(f"… ({MA})")
    assert N.ten_de_tai({"topic": "  Chủ   đề\nhai dòng "}, MA) == f"Chủ đề hai dòng ({MA})"
    assert N.ten_de_tai(None, MA) == MA and N.ten_de_tai({"title": ""}, MA) == MA


@pytest.mark.parametrize("ma", ["../exports", "a/b", "", "-dau-gach", "x" * 81])
def test_doc_de_tai_ma_sai_khuon_bi_tu_choi(tmp_path, ma):
    with pytest.raises(ValueError, match="sai khuôn"):
        N.doc_de_tai(ma, tmp_path)


def test_doc_de_tai_danh_muc_hong_khong_nap(tmp_path):
    with pytest.raises(N.KhongChayDuoc, match="không thấy danh mục"):
        N.doc_de_tai(MA, tmp_path / "exports")
    with pytest.raises(N.KhongChayDuoc, match="sai khuôn"):
        N.doc_de_tai(MA, _de_tai(tmp_path / "a", trich_dan={"T01": "111"}))
    with pytest.raises(N.KhongChayDuoc, match="không phải"):
        N.doc_de_tai(MA, _de_tai(tmp_path / "b", study="de-tai-khac"))
    ex = _de_tai(tmp_path / "c")
    (ex / MA / f"DANH_MUC_TRICH_DAN_{MA}.json").write_text("{hỏng", encoding="utf-8")
    with pytest.raises(N.KhongChayDuoc, match="không đọc được"):
        N.doc_de_tai(MA, ex)


def test_doc_de_tai_thieu_study_meta_thi_ten_nhom_la_ma(tmp_path):
    data, _ = N.doc_de_tai(MA, _de_tai(tmp_path, meta=False))
    assert data["meta"]["question"] == MA


# ── main --de-tai với EndNote giả ──────────────────────────────────────────────────────────────────

class _EnGia:
    """EndNote giả đủ cho đường `nap_nhieu`: post vào tên ĐÃ có nhóm sinh nhóm MỚI cùng tên (đo 24/10/2026)."""
    hien_tai: "_EnGia | None" = None

    def __init__(self, ung_dung, thu_vien, co_san=(), nhom=None):
        self.ung_dung, self.thu_vien = ung_dung, Path(thu_vien)
        self.ban_ghi: list[dict] = []
        self.nhom: dict[str, list[str]] = {}
        self.nhom_trung: list[tuple[str, list[str]]] = []
        self.so_lan_nhap = 0
        for pm, doi in co_san:
            self._them(pm, doi)
        for ten, pmids in (nhom or {}).items():
            self.nhom[ten] = [b["id"] for b in self.ban_ghi if b["pmid"] in pmids]
        _EnGia.hien_tai = self

    def _them(self, pm, doi, tep=""):
        rid = f'<RecordID database="2" recNum="{len(self.ban_ghi) + 1}" />'
        self.ban_ghi.append({"id": rid, "pmid": pm or "", "doi": (doi or "").lower(), "tep": tep})

    def dang_mo_dung_thu_vien(self):
        return True

    def thung_rac(self):
        return {"pmid": set(), "doi": set()}

    def tim_khop(self, gia_tri, truong):
        khoa = "pmid" if truong == "Accession Number" else "doi"
        return {v: [b["id"] for b in self.ban_ghi if b[khoa] and b[khoa] == str(v).lower()] for v in gia_tri}

    def nhap(self, tep):
        self.so_lan_nhap += 1
        for r in ET.fromstring(Path(tep).read_bytes()).findall("records/record"):
            self._them(r.findtext("accession-num"), r.findtext("electronic-resource-num"),
                       r.findtext("urls/pdf-urls/url") or "")

    @staticmethod
    def _so(ids):
        return [int(re.search(r'recNum="(\d+)"', i).group(1)) for i in ids]

    def nhom_theo_ten(self, ten):
        ds = [(1, self.nhom[ten])] if ten in self.nhom else []
        ds += [(100 + k, ids) for k, (t, ids) in enumerate(self.nhom_trung) if t == ten]
        return [{"group_id": g, "ten": ten, "so_ban_ghi": len(ids), "rec": self._so(ids)} for g, ids in ds]

    def dang_vao_nhom(self, ids, ten):
        if ten in self.nhom:
            self.nhom_trung.append((ten, list(ids)))
        else:
            self.nhom[ten] = list(ids)

    def tep_dinh_kem(self, ids):
        return {b["id"]: len(b["tep"]) for b in self.ban_ghi if b["id"] in ids}

    def gan_tep(self, ma, url):
        next(b for b in self.ban_ghi if b["id"] == ma)["tep"] = url


def _meta(d: dict) -> dict:
    return {"pmid": d.get("pmid"), "doi": d.get("doi"), "loai_tl": "Journal Article", "tieu_de": "Bài thử",
            "tac_gia": ["Nguyễn, Văn A"], "tap_chi": "Tạp chí", "tap_chi_viet_tat": "", "nam": "2025", "tap": "1",
            "so": "2", "trang": "3-4", "issn": "", "tom_tat": "", "ngon_ngu": "vie", "pmcid": "", "da_rut": False,
            "nguon_meta": "PubMed" if d.get("pmid") else "Crossref"}


@pytest.fixture
def moi_truong(tmp_path, monkeypatch):
    """Đang ở Mac, thư viện đã cấu hình và đang mở; mạng/tóm tắt bị thay — tóm tắt mà chạy là lỗi của phép thử."""
    tv = tmp_path / "tv.enl"
    tv.write_bytes(b"enl")
    ch = tmp_path / "ebm-endnote.json"
    ch.write_text(json.dumps({"thu_vien": str(tv), "ung_dung": "EndNote 2025"}), encoding="utf-8", newline="\n")
    monkeypatch.setattr(N, "CAU_HINH", ch)
    monkeypatch.setattr(N, "_la_mac", lambda: True)
    monkeypatch.setattr(N, "EndNoteMac", _EnGia)
    monkeypatch.setattr(N, "_tim_dash_goc", lambda: None)
    exports = _de_tai(tmp_path / "y-khoa")
    monkeypatch.setattr(N, "_tim_exports", lambda: exports)
    monkeypatch.setattr(N, "_ngu", lambda s: None)
    monkeypatch.setattr(N, "lay_metadata", lambda dd, *a, **k: ([(d, _meta(d)) for d in dd], []))

    def cam_tom_tat(*_a, **_k):
        raise AssertionError("trích dẫn đề tài KHÔNG được ghi tóm tắt tiếng Việt (bác sĩ dặn 25/10/2026)")

    monkeypatch.setattr(N, "chay_tom_tat", cam_tom_tat)
    monkeypatch.chdir(tmp_path)
    _EnGia.hien_tai = None
    return tmp_path, ch


def test_de_tai_ap_dung_nap_vao_nhom_nc_ghi_nho_khoa_khong_tom_tat(moi_truong, capsys):
    goc, ch = moi_truong
    ma = N.main(["--de-tai", MA, "--ap-dung"])
    ra = capsys.readouterr().out
    en = _EnGia.hien_tai
    ten = f"NC · {TEN_DE_TAI} ({MA})"
    assert ma == 0, ra
    assert set(en.nhom) == {ten} and len(en.nhom[ten]) == 3 and en.nhom_trung == []
    assert {b["pmid"] for b in en.ban_ghi} == {"111", "222", ""} and en.so_lan_nhap == 1
    assert N.nhom_da_ghi(ch) == {f"DE-TAI_{MA}": ten}, "nhóm thật đã dựng ⇒ ghi nhớ theo khoá DE-TAI_<mã>"
    assert "Không thấy kho toàn văn" in ra, "thiếu kho chỉ cảnh báo — không chặn ghi vì không có bước tóm tắt"


def test_de_tai_khong_doan_kho_canh_thu_muc_dang_dung(moi_truong, capsys):
    """Tệp giả `DE-TAI_<mã>.json` không có thư mục thật: `toan_van_oa` cạnh thư mục đang đứng KHÔNG phải kho của đề tài."""
    goc, _ = moi_truong
    (goc / "toan_van_oa").mkdir()
    (goc / "toan_van_oa" / "PMID-111_UPW.pdf").write_bytes(b"%PDF-1.4 fake")
    assert N.main(["--de-tai", MA, "--ap-dung"]) == 0
    assert all(b["tep"] == "" for b in _EnGia.hien_tai.ban_ghi), "không được đính PDF từ kho đoán theo thư mục đang đứng"


def test_de_tai_kho_chi_dinh_thi_dinh_pdf(moi_truong, capsys):
    goc, _ = moi_truong
    kho = goc / "kho"
    kho.mkdir()
    (kho / "PMID-222_UPW.pdf").write_bytes(b"%PDF-1.4 fake")
    assert N.main(["--de-tai", MA, "--ap-dung", "--kho-toan-van", str(kho)]) == 0
    tep = {b["pmid"]: b["tep"] for b in _EnGia.hien_tai.ban_ghi}
    assert tep["222"].startswith("internal-pdf://") and tep["111"] == "", "PDF đúng PMID trong kho được đính nội bộ"


def test_de_tai_nhom_ghi_nho_thang_ten_mac_dinh_khong_post_nhom_thu_hai(moi_truong, monkeypatch, capsys):
    """Lượt tay 25/10 đã dựng «NC · Chăm sóc thận…» (group_id 133) — chạy lại phải về ĐÚNG nhóm đó, không post nhóm mới."""
    goc, ch = moi_truong
    cu = "NC · Tên nhóm bác sĩ đã dùng"
    N.ghi_nhom(f"DE-TAI_{MA}", cu, ch)

    def en_co_san(ung_dung, thu_vien):
        return _EnGia(ung_dung, thu_vien, co_san=[("111", None), ("222", None)], nhom={cu: {"111", "222"}})

    monkeypatch.setattr(N, "EndNoteMac", en_co_san)
    assert N.main(["--de-tai", MA, "--ap-dung"]) == 0
    en = _EnGia.hien_tai
    assert set(en.nhom) == {cu} and en.nhom_trung == [], "nhóm đã có ⇒ không post (post luôn sinh nhóm trùng tên)"
    assert len(en.ban_ghi) == 3, "chỉ bài còn thiếu (V01) được nhập — bài đã có không nhập lại"


def test_de_tai_chay_kho_khong_nhap_khong_dang_nhom(moi_truong, capsys):
    assert N.main(["--de-tai", MA]) == 0
    ra = capsys.readouterr().out
    en = _EnGia.hien_tai
    assert en.so_lan_nhap == 0 and en.nhom == {} and "Chạy khô" in ra and f"nhóm «NC · {TEN_DE_TAI}" in ra
    assert "sẽ bị từ chối" not in ra, "đề tài không có bước tóm tắt ⇒ thiếu kho không chặn --ap-dung, đừng báo sai"


def test_de_tai_xuat_xml_dung_danh_muc(moi_truong, capsys):
    goc, _ = moi_truong
    ra = goc / "ra.xml"
    assert N.main(["--de-tai", MA, "--xuat-xml", str(ra)]) == 0
    goc_xml = ET.fromstring(ra.read_bytes())
    assert len(goc_xml.findall("records/record")) == 3
    assert {"".join(k.itertext()) for k in goc_xml.iter("keyword")} == {f"EBM: DE-TAI_{MA}"}


@pytest.mark.parametrize("them", [["--file", "x.html"], ["--tat-ca"], ["--gan-kho"], ["--tom-tat-vi"],
                                  ["--tom-tat-thu-vien"], ["--loai-tru", "111", "--ly-do", "x"], ["--cho-vao-nhom"]])
def test_de_tai_xung_dot_tham_so_ma_3(moi_truong, them, capsys):
    assert N.main(["--de-tai", MA, *them]) == 3
    assert _EnGia.hien_tai is None, "tham số sai thì không chạm EndNote"


def test_de_tai_ma_sai_3_khong_thay_exports_hoac_danh_muc_2(moi_truong, monkeypatch, capsys):
    assert N.main(["--de-tai", "../thoat-ra", "--ap-dung"]) == 3
    assert N.main(["--de-tai", "de-tai-khong-co", "--ap-dung"]) == 2
    monkeypatch.setattr(N, "_tim_exports", lambda: None)
    assert N.main(["--de-tai", MA, "--ap-dung"]) == 2
    assert _EnGia.hien_tai is None
