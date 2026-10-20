# -*- coding: utf-8 -*-
"""Tóm tắt MÁY từ TOÀN VĂN PMC TRUY CẬP MỞ khi bài KHÔNG có abstract (20/10/2026) — `tom_tat_endnote_vi.py`.

Bác sĩ: «Mở PR cho phép tóm tắt máy từ toàn văn PMC truy cập mở khi bài không có abstract, giữ chốt kiểm con số so với toàn
văn». Mục kho khai `"nguon": "toan_van_pmc"` ⇒ văn bản đối chiếu số là JATS XML `PMID-<n>_PMC<id>.xml` trong kho; bài CÓ
abstract mà khai nguồn này, hoặc kho không có tệp PMC ⇒ không in (fail-closed). Ngoại tuyến hoàn toàn.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_may_pmc")

MUC = {"id": "ITEM-01", "title": "Mục chính", "source": "Nguồn chính 2025", "design": "Guideline", "dateVersion": "2025",
       "pmid": "31111111", "doi": "10.1000/chinh", "pico": {"P": ["Người lớn", "match"], "I": ["Can thiệp", "match"],
                                                            "C": "Chuẩn", "O": ["Kết cục", "match"]},
       "gradeLevel": "na", "decision": "consider", "action": "Hành động của nguồn chính",
       "references": ["Nguồn chính. PMID 31111111", "Bình luận không có abstract. PMID 32222222"]}
# Bảng JATS: hai ô «12» và «3» liền nhau — nối chữ không có dấu cách sẽ sinh «123» giả.
XML = ("<?xml version='1.0' encoding='utf-8'?><article><front><article-meta><title-group><article-title>Bình luận"
       "</article-title></title-group></article-meta></front><body><sec><p>Among 1,234 adults the rate was 9·1% vs 12·0%"
       " (HR 0·85).</p><table-wrap><table><tr><td>12</td><td>3</td></tr></table></table-wrap></sec></body></article>")
TOM_TAT = {"thiet_ke": "Bài bình luận", "P": "1234 người lớn", "I": "Can thiệp", "C": "Chuẩn", "O": "Kết cục",
           "ket_qua": "9.1% so với 12.0%; HR 0.85", "nguon": "toan_van_pmc"}


def _muc():
    f = Path("/khong-ton-tai/WebDashboard_X_20261019.html")
    d = {"meta": {"question": "THA"}, "items": [MUC]}
    return tt.ngu_canh([f], lambda p: {f.name: d}.get(Path(p).name))["pmid:32222222"]


def _kho(tmp_path: Path, ten: str = "PMID-32222222_PMC9999999.xml", noi_dung: str = XML) -> Path:
    (tmp_path / ten).write_text(noi_dung, encoding="utf-8")
    return tmp_path


def test_khong_abstract_nguon_pmc_in_tom_tat_voi_nhan_va_dong_chan_dung_nguon(tmp_path):
    kho = _kho(tmp_path)
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": TOM_TAT}, "", kho)
    assert lech == [] and tom is TOM_TAT
    dong = tt.khoi_tieng_viet(_muc(), kho, tom).splitlines()
    assert f"{tt.NHAN_DONG['may_pmc']} (chưa qua cổng dashboard — không phải khuyến nghị):" in dong
    assert tt.NHAN_DONG["may"] + " (" not in "\n".join(dong), "không được gắn nhãn «từ abstract» cho tóm tắt từ toàn văn"
    assert dong[-1] == tt.CHAN_MAY_PMC
    assert not any("toan_van_pmc" in d for d in dong), "siêu dữ liệu «nguon» không bao giờ in nguyên văn"


def test_dong_giu_cho_khong_abstract_cua_luot_truoc_van_tinh_la_khong_co_abstract(tmp_path):
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": TOM_TAT}, tt.KHONG_ABSTRACT, _kho(tmp_path))
    assert lech == [] and tom is TOM_TAT


def test_so_khong_co_trong_toan_van_thi_khong_in(tmp_path):
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": dict(TOM_TAT, ket_qua="HR 0.77")}, "", _kho(tmp_path))
    assert tom is None and lech == ["0.77"]


def test_hai_o_bang_lien_nhau_khong_ghep_thanh_so_gia(tmp_path):
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": dict(TOM_TAT, ket_qua="123 người")}, "", _kho(tmp_path))
    assert tom is None and lech == ["123"], "nối mẩu chữ JATS không dấu cách sẽ biến «12»+«3» thành «123» khớp giả"


def test_bai_co_abstract_khai_nguon_pmc_bi_tu_choi(tmp_path):
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": TOM_TAT}, "Background: 1,234 adults; 9·1% vs 12·0%; HR 0·85.",
                               _kho(tmp_path))
    assert tom is None and len(lech) == 1 and lech[0].startswith("⛔") and "CÓ abstract" in lech[0]


def test_kho_chi_co_ban_chrome_khong_phai_pmc_thi_tu_choi(tmp_path, monkeypatch):
    # Bản lưu phiên Chrome (_CHR, có bản quyền) dù là XHTML hợp lệ, đã qua cổng nội dung và mang đủ số: KHÔNG phải nguồn
    # «toan_van_pmc». Giả lập nguồn sự thật trả đúng tệp đó để chốt lọc tên PMC là thứ duy nhất chặn.
    chr_ = _kho(tmp_path, "PMID-32222222_CHR.html", "<html><body>" + XML.split("?>", 1)[1] + "</body></html>") \
        / "PMID-32222222_CHR.html"

    class _Gia:
        @staticmethod
        def tep_toan_van_that(kho, pm):
            return [chr_]

    monkeypatch.setattr(tt, "_dtv", lambda: _Gia)
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": TOM_TAT}, "", tmp_path)
    assert tom is None and lech and lech[0].startswith("⛔") and "PMC" in lech[0]


def test_khong_co_kho_thi_tu_choi(tmp_path):
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": TOM_TAT}, "", None)
    assert tom is None and lech and lech[0].startswith("⛔")


def test_xml_hong_thi_tu_choi(tmp_path):
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": TOM_TAT}, "", _kho(tmp_path, noi_dung="<article><p>1234"))
    assert tom is None and lech and lech[0].startswith("⛔")


def test_mac_dinh_van_doi_chieu_abstract_khong_doi_hanh_vi_cu(tmp_path):
    cu = {k: v for k, v in TOM_TAT.items() if k != "nguon"}
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": cu}, "", _kho(tmp_path))
    assert tom is None and lech == sorted(["0.85", "1234", "12.0", "9.1"]), "không khai nguồn ⇒ vẫn đối chiếu abstract (trống)"


def test_kiem_kho_bao_nguon_la_va_nhan_nguon_hop_le():
    assert tt.kiem_kho_tom_tat({"PMID 32222222": TOM_TAT}) == []
    loi = tt.kiem_kho_tom_tat({"PMID 32222222": dict(TOM_TAT, nguon="toan_van_chrome")})
    assert len(loi) == 1 and "«nguon»" in loi[0]
    tom, lech = tt.tom_tat_cho(_muc(), {"PMID 32222222": dict(TOM_TAT, nguon="toan_van_chrome")}, "", None)
    assert tom is None and lech[0].startswith("⛔")


def test_nhan_moi_nam_trong_bmp():
    for s in (tt.NHAN_DONG["may_pmc"], tt.CHAN_MAY_PMC):
        assert all(ord(c) <= 0xFFFF for c in s), "EndNote đổi ký tự ngoài BMP thành «?»"
