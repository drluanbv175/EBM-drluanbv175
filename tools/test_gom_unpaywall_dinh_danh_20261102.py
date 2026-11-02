# -*- coding: utf-8 -*-
"""Cổng ĐỊNH DANH của tầng 2 Unpaywall (02/11/2026 — `audit/nhat-ky/2026-11-02-unpaywall-pdf-sai-bai.md`).

Ca thật: PMID 38099896 (ISHLT 2023 «Assessing and managing frailty in advanced heart failure», doi 10.1016/j.healun.2023.09.013)
— vị trí OA duy nhất qua cổng điều khoản là kho KU Leuven (Lirias, cc-by), trả PDF của một bài JMIR khác hẳn («Mapping the
Cardiometabolic Patient Experience…»). Tầng này chỉ kiểm 5 byte «%PDF-» nên tệp sai vào kho `PMID-38099896_UPW.pdf`, bị gắn vào
EndNote, và MỖI lượt bộ năm ⑦ tải lại đúng tệp đó. Khoá:
  • PDF/HTML/JATS sai bài KHÔNG được ghi; lý do vào SAI_BAI_UNPAYWALL; in một dòng ⚠;
  • URL sai bài vào sổ `upw-sai-bai.json` trong kho, lượt sau KHÔNG tải lại tới khi hết hạn;
  • luật là của bước ⑨ (`tom_tat_chung_cu_word.khop_dinh_danh`), không phải logic song song;
  • thiếu pypdf ⇒ không lưu nhưng KHÔNG ghi sổ (lỗi máy, lượt sau thử lại); PDF không có chữ ⇒ không lưu.
Ngoại tuyến hoàn toàn (urlopen giả, PDF giả hợp lệ dựng bằng `pdf_gia_kiem_thu.py`).
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(tep: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


g = _nap("gom_toan_van_dashboard.py", "_gom_dinh_danh_1102")
pdf_gia = _nap("pdf_gia_kiem_thu.py", "_pdf_gia_dinh_danh_1102")
ttcc = _nap("tom_tat_chung_cu_word.py", "_ttcc_dinh_danh_1102")

PMID, DOI = "38099896", "10.1016/j.healun.2023.09.013"
TIEU_DE = ("Assessing and managing frailty in advanced heart failure: An International Society for Heart and Lung "
           "Transplantation consensus statement")
LIRIAS = "https://lirias.kuleuven.be/retrieve/02fa7fe0-272c-4b10-9a64-47c74fcd6ed9"
KHO_KHAC = "https://repo.example/ishlt-frailty.pdf"
# Bài KHÁC chung chủ đề tim mạch (giống ca thật: «heart», «failure» có mặt) — tiêu đề lệch, không có DOI của bài cần tìm.
PDF_SAI = pdf_gia.pdf_co_chu(
    "Original Paper. Mapping the Cardiometabolic Patient Experience and Self-Care Behaviors to Inform Design, Implementation, "
    "and Persistent Use of Digital Health Care Solutions: Mixed Methods Study. Patients with heart failure and diabetes "
    "described self-care routines. " + "digital health interview theme " * 40,
    "Methods. Semi-structured interviews. " + "participant quote coding " * 50)
PDF_DUNG = pdf_gia.pdf_co_chu(TIEU_DE + ". doi:" + DOI + ". " + "frailty assessment heart failure " * 40, "Results " * 80)
PDF_CHI_DOI = pdf_gia.pdf_co_chu("Journal of Heart and Lung Transplantation. https://doi.org/" + DOI + " " + "text " * 80)
PDF_ANH = pdf_gia.pdf_co_chu("")


def _html(tieu_de: str) -> bytes:
    than = "".join(f"<h2>{d}</h2><p>{' '.join(f'{d.lower()}{i % 97}' for i in range(900))}</p>"
                   for d in ("Introduction", "Methods", "Results", "Discussion"))
    return f"<!doctype html><html><body><article><h1>{tieu_de}</h1>{than}</article></body></html>".encode()


class _PhanHoi(io.BytesIO):
    def __init__(self, du_lieu: bytes, url: str):
        super().__init__(du_lieu)
        self._url = url

    def geturl(self):
        return self._url


def _mang(monkeypatch, tmp_path, vi_tri: list[str], noi_dung: dict, da_goi: list):
    def urlopen(req, timeout=None, context=None):
        url = req if isinstance(req, str) else req.full_url
        da_goi.append(url)
        if "esummary.fcgi" in url:
            return _PhanHoi(json.dumps({"result": {PMID: {"articleids": [{"idtype": "doi", "value": DOI}]}}}).encode(), url)
        if "api.unpaywall.org" in url:
            locs = [{"url": u, "license": "cc-by"} for u in vi_tri]
            return _PhanHoi(json.dumps({"is_oa": True, "title": TIEU_DE, "best_oa_location": locs[0],
                                        "oa_locations": locs}).encode(), url)
        return _PhanHoi(noi_dung[url], url)
    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    monkeypatch.setattr(g, "_email_lich_su", lambda: "test@example.org")
    monkeypatch.setattr(g.time, "sleep", lambda s: None)
    monkeypatch.setattr(g, "KHO", tmp_path)


def _so(tmp_path) -> dict:
    return json.loads((tmp_path / g.SO_URL_SAI_BAI).read_text(encoding="utf-8"))


def test_ca_that_pdf_bai_khac_khong_luu_ghi_so_va_bao(monkeypatch, tmp_path, capsys):
    da_goi: list[str] = []
    _mang(monkeypatch, tmp_path, [LIRIAS], {LIRIAS: PDF_SAI}, da_goi)
    moi, thieu = g.tang_unpaywall([PMID])
    assert moi == 0 and thieu == [PMID] and not list(tmp_path.glob("PMID-*")), "PDF sai bài vào kho với tên hợp lệ"
    assert len(g.SAI_BAI_UNPAYWALL) == 1 and g.SAI_BAI_UNPAYWALL[0][:3] == (PMID, DOI, LIRIAS)
    assert g.SAI_BAI_UNPAYWALL[0][3].startswith("sai_bai")
    muc = _so(tmp_path)[PMID][LIRIAS]
    assert muc["loai"] == "sai_bai" and muc["ngay"] == date.today().isoformat() and muc["doi"] == DOI
    ra = capsys.readouterr().out
    assert "⚠ Unpaywall 38099896" in ra and "KHÔNG phải bài này" in ra


def test_luot_sau_khong_tai_lai_url_trong_so(monkeypatch, tmp_path, capsys):
    da_goi: list[str] = []
    _mang(monkeypatch, tmp_path, [LIRIAS], {LIRIAS: PDF_SAI}, da_goi)
    g.tang_unpaywall([PMID])
    da_goi.clear()
    moi, thieu = g.tang_unpaywall([PMID])
    assert moi == 0 and thieu == [PMID]
    assert LIRIAS not in da_goi, "URL đã biết sai bài bị tải lại (mỗi lượt bộ năm ⑦ từng tải lại tệp sai)"
    assert g.SAI_BAI_UNPAYWALL and "đã ghi sổ" in g.SAI_BAI_UNPAYWALL[0][3]
    assert "⏭ Unpaywall 38099896" in capsys.readouterr().out


def test_so_het_han_thi_thu_lai(monkeypatch, tmp_path):
    da_goi: list[str] = []
    _mang(monkeypatch, tmp_path, [LIRIAS], {LIRIAS: PDF_DUNG}, da_goi)
    cu = (date.today() - timedelta(days=g.HAN_URL_SAI_BAI)).isoformat()
    (tmp_path / g.SO_URL_SAI_BAI).write_text(json.dumps({PMID: {LIRIAS: {"ngay": cu, "loai": "sai_bai", "ly_do": "x", "doi": DOI}}}),
                                             encoding="utf-8")
    moi, _ = g.tang_unpaywall([PMID])
    assert LIRIAS in da_goi and moi == 1 and (tmp_path / f"PMID-{PMID}_UPW.pdf").exists(), "sổ hết hạn vẫn gác cửa"


def test_sai_bai_o_vi_tri_dau_thi_thu_vi_tri_ke(monkeypatch, tmp_path):
    da_goi: list[str] = []
    _mang(monkeypatch, tmp_path, [LIRIAS, KHO_KHAC], {LIRIAS: PDF_SAI, KHO_KHAC: PDF_DUNG}, da_goi)
    moi, thieu = g.tang_unpaywall([PMID])
    assert moi == 1 and thieu == [] and (tmp_path / f"PMID-{PMID}_UPW.pdf").read_bytes() == PDF_DUNG
    assert list(_so(tmp_path)[PMID]) == [LIRIAS]


@pytest.mark.parametrize("ban", [PDF_DUNG, PDF_CHI_DOI], ids=["tieu_de", "chi_doi"])
def test_pdf_dung_bai_duoc_luu(monkeypatch, tmp_path, ban):
    da_goi: list[str] = []
    _mang(monkeypatch, tmp_path, [LIRIAS], {LIRIAS: ban}, da_goi)
    assert g.tang_unpaywall([PMID])[0] == 1 and (tmp_path / f"PMID-{PMID}_UPW.pdf").exists()
    assert not g.SAI_BAI_UNPAYWALL and not (tmp_path / g.SO_URL_SAI_BAI).exists()


def test_html_toan_van_cua_bai_khac_khong_luu(monkeypatch, tmp_path):
    da_goi: list[str] = []
    _mang(monkeypatch, tmp_path, [LIRIAS], {LIRIAS: _html("Mapping the Cardiometabolic Patient Experience: Mixed Methods Study")},
          da_goi)
    assert g.la_toan_van_html(_html("x").decode())[0], "fixture phải là toàn văn thật — chỉ cổng định danh được chặn nó"
    moi, _ = g.tang_unpaywall([PMID])
    assert moi == 0 and not (tmp_path / f"PMID-{PMID}_UPW.html").exists()
    assert _so(tmp_path)[PMID][LIRIAS]["ly_do"].startswith("HTML")


def test_html_dung_bai_duoc_luu(monkeypatch, tmp_path):
    da_goi: list[str] = []
    _mang(monkeypatch, tmp_path, [LIRIAS], {LIRIAS: _html(TIEU_DE)}, da_goi)
    assert g.tang_unpaywall([PMID])[0] == 1 and (tmp_path / f"PMID-{PMID}_UPW.html").exists()


def test_jats_pmc_cua_bai_khac_khong_luu_xet_tiep_trang(monkeypatch, tmp_path):
    """Trang tải về có liên kết /articles/PMC999/ (bài liên quan) ⇒ JATS PMC999 của bài khác không được ghi làm toàn văn của PMID
    này; chính trang (đúng bài) vẫn được xét và lưu."""
    da_goi: list[str] = []
    trang = _html(TIEU_DE).replace(b"<article>", b'<article><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC999/">x</a>')
    _mang(monkeypatch, tmp_path, [LIRIAS], {LIRIAS: trang}, da_goi)
    jats = (b'<article><front><article-meta><article-id pub-id-type="doi">10.2196/khac</article-id><title-group><article-title>'
            b"Mapping the Cardiometabolic Patient Experience</article-title></title-group></article-meta></front><body>"
            + b"noi dung " * 300 + b"</body></article>")

    class _Gom:
        def tai_toan_van(self, pmcid):
            return jats
    moi, _ = g.tang_unpaywall([PMID], gom=_Gom())
    assert moi == 1 and not list(tmp_path.glob("*.xml")) and (tmp_path / f"PMID-{PMID}_UPW.html").exists()


def test_thieu_pypdf_khong_luu_khong_ghi_so(monkeypatch, tmp_path, capsys):
    da_goi: list[str] = []
    _mang(monkeypatch, tmp_path, [LIRIAS], {LIRIAS: PDF_DUNG}, da_goi)
    monkeypatch.setitem(sys.modules, "pypdf", None)  # import pypdf ⇒ ImportError
    moi, _ = g.tang_unpaywall([PMID])
    assert moi == 0 and not list(tmp_path.glob("PMID-*")), "không kiểm được định danh mà vẫn lưu (fail-open)"
    assert not (tmp_path / g.SO_URL_SAI_BAI).exists(), "lỗi MÁY bị ghi sổ như URL sai bài — lượt sau không thử lại"
    assert g.SAI_BAI_UNPAYWALL[0][3].startswith("thieu_cong_cu")
    assert "không kiểm được định danh trên máy này" in capsys.readouterr().out


def test_pdf_khong_co_chu_khong_luu(monkeypatch, tmp_path):
    da_goi: list[str] = []
    _mang(monkeypatch, tmp_path, [LIRIAS], {LIRIAS: PDF_ANH}, da_goi)
    assert g.tang_unpaywall([PMID])[0] == 0 and not list(tmp_path.glob("PMID-*"))
    assert _so(tmp_path)[PMID][LIRIAS]["loai"] == "khong_kiem_duoc"


def test_dung_chung_luat_buoc_9(tmp_path):
    """Cổng của tầng Unpaywall cho cùng kết luận với `khop_dinh_danh` của bước ⑨ trên cùng văn bản (không logic song song)."""
    for ban in (PDF_SAI, PDF_DUNG, PDF_CHI_DOI):
        q = tmp_path / "x.pdf"
        q.write_bytes(ban)
        assert ttcc.tach_trang(ban) == ttcc.tach_trang(q), "tach_trang(bytes) lệch tach_trang(đường dẫn)"
        ky_vong = ttcc.khop_dinh_danh(ttcc.tach_trang(q), DOI, TIEU_DE)
        assert (g.kiem_dinh_danh_upw(ban, loai="pdf", doi=DOI, tieu_de=TIEU_DE)[0] == "dung") is ky_vong[0]


def test_so_hong_thi_coi_nhu_rong_va_ghi_lai(tmp_path):
    (tmp_path / g.SO_URL_SAI_BAI).write_text("{hỏng", encoding="utf-8")
    assert g.doc_so_url_sai_bai(tmp_path) == {}
    g.ghi_url_sai_bai(tmp_path, PMID, LIRIAS, doi=DOI, loai="sai_bai", ly_do="x")
    assert g.url_sai_bai_con_han(g.doc_so_url_sai_bai(tmp_path), PMID, LIRIAS)
    assert not g.url_sai_bai_con_han(g.doc_so_url_sai_bai(tmp_path), PMID, LIRIAS,
                                     hom_nay=date.today() + timedelta(days=g.HAN_URL_SAI_BAI))
