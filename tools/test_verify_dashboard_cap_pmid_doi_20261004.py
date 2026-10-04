#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cổng verify_dashboard.py: PMID và DOI của CÙNG một mục phải trỏ CÙNG một bài (thêm 04/10/2026).

VÌ SAO CÓ. Đo 04/10/2026 trên 72 dashboard: 1164 mục ghi cả PMID lẫn DOI, 10 cặp trỏ HAI bài khác nhau (3 mục
`apply`) — ví dụ PMID guideline ESC 2026 đi cùng DOI một bài BMJ 1999, PMID một THƯ bạn đọc NEJM đi cùng DOI của chính
thử nghiệm. Cổng `--online` xác minh TỪNG định danh tồn tại (PubMed/Crossref) nên cả hai đều «✓»; không có bước nào
hỏi hai định danh có cùng một bài không. Test gọi THẬT các hàm của cổng (nạp theo đường dẫn nguồn chuẩn), mạng được
thay bằng `source_urlopen` giả — không có lượt gọi mạng thật nào.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py"


def _nap():
    sp = importlib.util.spec_from_file_location("_vd_cap_pmid_doi", NGUON)
    m = importlib.util.module_from_spec(sp)
    sys.modules["_vd_cap_pmid_doi"] = m
    sp.loader.exec_module(m)
    return m


vd = _nap()


class _PhanHoiGia:
    """Đủ cho `with source_urlopen(...) as r: r.read(); r.headers.get(...)`."""

    def __init__(self, than: str, loai: str = "application/json"):
        self._than = than.encode("utf-8")
        self.headers = {"content-type": loai}

    def read(self):
        return self._than

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _esummary(pmid: str, tieu_de: str, doi: str | None, loai=("Journal Article",), nam="2026 Mar 13"):
    ban_ghi = {"uid": pmid, "title": tieu_de, "pubdate": nam, "pubtype": list(loai),
               "articleids": [{"idtype": "pubmed", "value": pmid}]}
    if doi:
        ban_ghi["articleids"].append({"idtype": "doi", "value": doi})
    return json.dumps({"result": {"uids": [pmid], pmid: ban_ghi}})


def _bo_dinh_tuyen(ban_do: dict):
    """source_urlopen giả: chọn phản hồi theo chuỗi con đầu tiên khớp URL."""
    def _mo(url, timeout=None):
        for khoa, phan_hoi in ban_do.items():
            if khoa in url:
                return phan_hoi() if callable(phan_hoi) else phan_hoi
        raise AssertionError("URL không được giả lập: " + url)
    return _mo


class TestSoCapPmidDoi(unittest.TestCase):
    def test_khop_khong_phan_biet_hoa_thuong_va_tien_to_link(self):
        self.assertEqual(vd.so_cap_pmid_doi("10.1093/EURHEARTJ/ehag188", "https://doi.org/10.1093/eurheartj/ehag188"),
                         ("khop", ""))

    def test_pubmed_khong_ghi_doi_la_chua_so_duoc_khong_phai_khop(self):
        ket_luan, ghi_chu = vd.so_cap_pmid_doi("10.1000/abc", "")
        self.assertEqual(ket_luan, "khong_so_duoc")
        self.assertIn("không ghi DOI", ghi_chu)

    def test_hai_doi_khac_nhau_la_lech(self):
        self.assertEqual(vd.so_cap_pmid_doi("10.1136/bmj.319.7212.722", "10.1093/eurheartj/ehag188"), ("lech", ""))

    def test_pmid_tro_thu_ban_doc_noi_ro_pmid_sai(self):
        ket_luan, ghi_chu = vd.so_cap_pmid_doi("10.1056/NEJMoa1104623", "10.1056/nejmc1111248", ("Letter",))
        self.assertEqual(ket_luan, "lech")
        self.assertIn("thư bạn đọc", ghi_chu)
        self.assertIn("PMID sai", ghi_chu)

    def test_loai_journal_article_khong_them_ghi_chu(self):
        self.assertEqual(vd.so_cap_pmid_doi("10.1/a", "10.1/b", ("Journal Article", "Review")), ("lech", ""))

    def test_hai_phien_ban_cochrane_van_la_lech_co_ghi_chu(self):
        ket_luan, ghi_chu = vd.so_cap_pmid_doi("10.1002/14651858.CD012345.pub3", "10.1002/14651858.cd012345.pub2")
        self.assertEqual(ket_luan, "lech")
        self.assertIn("PHIÊN BẢN", ghi_chu)

    def test_hai_tong_quan_cochrane_khac_nhau_khong_goi_la_khac_phien_ban(self):
        self.assertEqual(vd.so_cap_pmid_doi("10.1002/14651858.CD012345.pub2", "10.1002/14651858.CD099999.pub2"),
                         ("lech", ""))


class TestRutDoiTuBanGhi(unittest.TestCase):
    def test_articleids_truoc(self):
        bg = {"articleids": [{"idtype": "pubmed", "value": "1"}, {"idtype": "doi", "value": "10.1/AbC"}],
              "elocationid": "doi: 10.9/khac"}
        self.assertEqual(vd._doi_tu_esummary(bg), "10.1/AbC")

    def test_elocationid_khi_articleids_khong_co_doi(self):
        self.assertEqual(vd._doi_tu_esummary({"articleids": [], "elocationid": "pii: S01. doi: 10.2/xyz"}), "10.2/xyz")

    def test_du_lieu_la_khong_nem_loi(self):
        self.assertEqual(vd._doi_tu_esummary("không phải dict"), "")
        self.assertEqual(vd._doi_tu_esummary({"articleids": ["x", None]}), "")

    def test_ghi_loai_chuoi_va_kieu_la(self):
        vd._ghi_doi_cua_pmid("111", "10.1/X", "letter; journal article")
        self.assertEqual(vd._DOI_CUA_PMID["111"], {"doi": "10.1/x", "loai": ("letter", "journal article")})
        vd._ghi_doi_cua_pmid("112", "10.1/Y", 7)
        self.assertEqual(vd._DOI_CUA_PMID["112"]["loai"], ())


class TestXacMinhPmidNhoDoi(unittest.TestCase):
    """Hàm xác minh THẬT (không thay) phải giữ nguyên kết quả cũ VÀ nhớ DOI mà nguồn ghi cho PMID."""

    def setUp(self):
        vd._DOI_CUA_PMID.clear()

    def test_ncbi_esummary(self):
        gia = _bo_dinh_tuyen({"esummary.fcgi": _PhanHoiGia(_esummary("41967042", "2026 ESC Guidelines", "10.1093/eurheartj/ehag188"))})
        with mock.patch.object(vd, "source_urlopen", gia):
            kq = vd.verify_pmid_online("41967042")
        self.assertEqual(kq, (True, "2026 ESC Guidelines", "2026 Mar 13"))
        self.assertEqual(vd._DOI_CUA_PMID["41967042"]["doi"], "10.1093/eurheartj/ehag188")

    def test_ncbi_chan_thi_lay_doi_tu_europe_pmc(self):
        epmc = json.dumps({"resultList": {"result": [{"pmid": "22150046", "id": "22150046", "title": "Azithromycin",
                                                      "pubYear": "2011", "doi": "10.1056/NEJMc1111248",
                                                      "pubType": "letter; comment"}]}})
        gia = _bo_dinh_tuyen({"esummary.fcgi": _PhanHoiGia("<html>Blocked Diagnostic</html>", "text/html"),
                              "europepmc": _PhanHoiGia(epmc)})
        with mock.patch.object(vd, "source_urlopen", gia):
            kq = vd.verify_pmid_online("22150046", retries=0)
        self.assertIs(kq[0], True)
        self.assertEqual(vd._DOI_CUA_PMID["22150046"], {"doi": "10.1056/nejmc1111248", "loai": ("letter", "comment")})


def _ch(pmid="41967042", doi="10.1093/eurheartj/ehag188", iid="ITEM-01"):
    return "{id:'%s', pmid:'%s', doi:'%s', gradeLevel:'high', decision:'apply'}" % (iid, pmid, doi)


class TestKiemCapTrongCong(unittest.TestCase):
    def setUp(self):
        vd._DOI_CUA_PMID.clear()
        vd._ghi_doi_cua_pmid("41967042", "10.1093/eurheartj/ehag188", ["Journal Article"])

    def _chay(self, chunk, strict, ok=True, pmid="41967042"):
        e, w, o = [], [], []
        vd.kiem_cap_pmid_doi([("ITEM-01", pmid, chunk, "2026")], {pmid: (ok, "tiêu đề", "2026")}, strict, e, w, o)
        return e, w, o

    def test_lech_strict_la_loi_cung_neu_ca_hai_doi(self):
        e, w, _ = self._chay(_ch(doi="10.1136/bmj.319.7212.722"), strict=True)
        self.assertEqual(len(e), 1, e)
        self.assertIn("10.1136/bmj.319.7212.722", e[0])
        self.assertIn("10.1093/eurheartj/ehag188", e[0])
        self.assertIn("Strict-sources", e[0])
        self.assertEqual(w, [])

    def test_lech_khong_strict_la_canh_bao(self):
        e, w, _ = self._chay(_ch(doi="10.1136/bmj.319.7212.722"), strict=False)
        self.assertEqual(e, [])
        self.assertEqual(len(w), 1)
        self.assertIn("trỏ HAI bản ghi", w[0])

    def test_khop_ghi_dong_dat(self):
        e, w, o = self._chay(_ch(doi="10.1093/EURHEARTJ/EHAG188"), strict=True)
        self.assertEqual((e, w), ([], []))
        self.assertTrue(any("Cặp PMID–DOI: 1/1" in x for x in o), o)

    def test_pmid_chua_xac_minh_thi_bo_qua(self):
        e, w, o = self._chay(_ch(doi="10.1136/bmj.319.7212.722"), strict=True, ok=None)
        self.assertEqual((e, w), ([], []))
        self.assertFalse(any("Cặp PMID–DOI" in x for x in o))

    def test_khong_co_ban_ghi_doi_la_chua_so_duoc_khong_xanh(self):
        e, w, o = self._chay(_ch(pmid="10023943", doi="10.1000/cu"), strict=True, pmid="10023943")
        self.assertEqual(e, [])
        self.assertEqual(len(w), 1)
        self.assertIn("CHƯA SO ĐƯỢC", w[0])
        self.assertFalse(any("Cặp PMID–DOI" in x for x in o))

    def test_doi_sai_dinh_dang_khong_so(self):
        e, w, o = self._chay(_ch(doi="khong-phai-doi"), strict=True)
        self.assertEqual((e, w, [x for x in o if "Cặp" in x]), ([], [], []))

    def test_thong_diep_lech_khong_bi_doc_thanh_loi_mang(self):
        e, _, _ = self._chay(_ch(doi="10.1136/bmj.319.7212.722"), strict=True)
        self.assertFalse(any(d in e[0] for d in vd._DAU_HIEU_LOI_MANG))


HTML = """<!doctype html><html><body><p>Cần bác sĩ kiểm chứng</p><script>
const DATA = {
  meta:{title:'Thử cặp PMID–DOI', date:'2026-10-04'},
  summary:{conclusion:'x', doNow:['x'], dontDo:['x'], redFlags:['x']},
  items:[
    {id:'ITEM-01', design:'Guideline', gradeLevel:'high', decision:'consider', source:'ESC', org:'ESC',
     dateVersion:'2026', pmid:'41967042', doi:'%s', references:['ESC 2026 Guidelines. Eur Heart J. 2026. PMID 41967042.']}
  ]
};
// HẾT KHỐI DATA
</script></body></html>
"""


class TestMainDauCuoi(unittest.TestCase):
    """Chạy main() thật của cổng trên một dashboard tối thiểu; mạng giả theo URL."""

    def _chay_main(self, doi_muc, *co):
        vd._DOI_CUA_PMID.clear()
        gia = _bo_dinh_tuyen({
            "esummary.fcgi": lambda: _PhanHoiGia(_esummary(
                "41967042", "2026 ESC Guidelines for the management of cardiovascular disease",
                "10.1093/eurheartj/ehag188")),
            "api.crossref.org": lambda: _PhanHoiGia(json.dumps({"message": {"title": ["Tiêu đề Crossref"]}})),
        })
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "WebDashboard_Thu.html"
            f.write_text(HTML % doi_muc, encoding="utf-8", newline="\n")
            ra = io.StringIO()
            with mock.patch.object(vd, "source_urlopen", gia), mock.patch.object(sys, "argv", ["vd", str(f), *co]), \
                    contextlib.redirect_stdout(ra):
                ma = vd.main()
        return ma, ra.getvalue()

    def test_lech_strict_hien_dong_loi_cung(self):
        ma, ra = self._chay_main("10.1136/bmj.319.7212.722", "--online", "--strict-sources")
        dong = [x for x in ra.splitlines() if "trỏ HAI bản ghi" in x]
        self.assertEqual(len(dong), 1, ra)
        self.assertTrue(dong[0].lstrip().startswith("✗"), dong[0])
        self.assertNotEqual(ma, 0)

    def test_lech_khong_strict_chi_canh_bao(self):
        _ma, ra = self._chay_main("10.1136/bmj.319.7212.722", "--online")
        dong = [x for x in ra.splitlines() if "trỏ HAI bản ghi" in x]
        self.assertEqual(len(dong), 1, ra)
        self.assertTrue(dong[0].lstrip().startswith("⚠"), dong[0])

    def test_khop_co_dong_dat_khong_co_dong_lech(self):
        _ma, ra = self._chay_main("10.1093/eurheartj/ehag188", "--online")
        self.assertIn("Cặp PMID–DOI: 1/1", ra)
        self.assertNotIn("trỏ HAI bản ghi", ra)

    def test_offline_khong_so_cap(self):
        _ma, ra = self._chay_main("10.1136/bmj.319.7212.722")
        self.assertNotIn("trỏ HAI bản ghi", ra)
        self.assertNotIn("Cặp PMID–DOI", ra)


class TestHaiBanTrongGitKhopByte(unittest.TestCase):
    def test_dark_analyst_dong_bo_byte(self):
        self.assertEqual(NGUON.read_bytes(), (REPO / "sync/skills/dark-analyst/tools/verify_dashboard.py").read_bytes())


if __name__ == "__main__":
    unittest.main()
