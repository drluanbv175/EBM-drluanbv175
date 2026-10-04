#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bộ rút metadata PubMed trong sync/skills phải trả DOI của CHÍNH bài, không phải DOI trong danh mục tham khảo (04/10/2026).

VÌ SAO CÓ. Cổng verify_dashboard.py mới so cặp PMID–DOI và bắt 10 cặp lệch trong kho; 5 mục mang PMID của một bài nhưng
DOI của một bài nằm trong danh mục tham khảo CỦA CHÍNH NÓ (BMJ 1999 trong bài ESC 2026, IPCC 2023 trong bài ESH, WAO 2020
trong guideline IAP…). Engine đã vá lớp lỗi này ngày 14/08 (`app/sources/pubmed.py::_own_article_doi`), nhưng bốn script
trong sync/skills vẫn duyệt `.//ArticleId` — trục hậu duệ quét cả `<ReferenceList>`:
  • nghien-cuu-ebm-tong-hop/scripts/pubmed_search.py GHI ĐÈ mỗi lần gặp DOI ⇒ trả DOI của tài liệu tham khảo CUỐI;
  • ba script K-Dense lấy DOI đầu tiên rồi dừng ⇒ đúng khi ArticleIdList có DOI, SAI khi bản ghi chỉ có DOI ở ELocationID.
Test chạy THẬT các hàm phân tích trên XML giả (không mạng) — bản cũ đỏ ở đúng các ca dưới.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
SK = REPO / "sync/skills"


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, SK / rel)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def _bai(own_ids: str = '<ArticleId IdType="doi">10.1093/eurheartj/ehag188</ArticleId>',
         eloc: str = "") -> str:
    """Một PubmedArticle tối thiểu; ReferenceList có HAI tài liệu mang DOI (đứng SAU ArticleIdList như XML thật)."""
    return f"""<PubmedArticle>
  <MedlineCitation Status="Publisher" Owner="NLM">
    <PMID Version="1">41967042</PMID>
    <Article PubModel="Print-Electronic">
      <Journal><Title>European heart journal</Title><JournalIssue><PubDate><Year>2026</Year></PubDate></JournalIssue></Journal>
      <ArticleTitle>Cardiac evaluation of paediatric athletes.</ArticleTitle>
      {eloc}
      <AuthorList><Author><LastName>Pieles</LastName><Initials>GE</Initials></Author></AuthorList>
      <PublicationTypeList><PublicationType UI="D016428">Journal Article</PublicationType></PublicationTypeList>
    </Article>
  </MedlineCitation>
  <PubmedData>
    <ArticleIdList><ArticleId IdType="pubmed">41967042</ArticleId>{own_ids}</ArticleIdList>
    <ReferenceList>
      <Reference><Citation>Ref 1</Citation><ArticleIdList><ArticleId IdType="doi">10.1136/bmj.319.7212.722</ArticleId></ArticleIdList></Reference>
      <Reference><Citation>Ref 2</Citation><ArticleIdList><ArticleId IdType="doi">10.1016/j.jacc.2019.04.046</ArticleId></ArticleIdList></Reference>
    </ReferenceList>
  </PubmedData>
</PubmedArticle>"""


def _tap(*bai: str) -> bytes:
    return ("<?xml version='1.0'?><PubmedArticleSet>" + "".join(bai) + "</PubmedArticleSet>").encode("utf-8")


ELOC_DUNG = '<ELocationID EIdType="doi" ValidYN="Y">10.1093/eurheartj/ehag188</ELocationID>'
ELOC_SAI = '<ELocationID EIdType="doi" ValidYN="N">10.9999/sai</ELocationID>'
OWN = "10.1093/eurheartj/ehag188"


class TestNghienCuuEbmTongHop(unittest.TestCase):
    """Script CỦA bác sĩ: lỗi ghi đè ⇒ bản cũ trả DOI tài liệu tham khảo CUỐI cho MỌI bài có ReferenceList."""

    def setUp(self):
        self.m = _nap("nghien-cuu-ebm-tong-hop/scripts/pubmed_search.py", "_pm_ncebm")

    def _efetch(self, xml: bytes):
        with mock.patch.object(self.m, "_get", return_value=xml):
            return self.m.efetch(["41967042"])

    def test_doi_cua_bai_khi_article_id_list_co_doi(self):
        self.assertEqual(self._efetch(_tap(_bai()))[0]["doi"], OWN)

    def test_du_phong_elocation_khi_article_id_list_khong_co_doi(self):
        self.assertEqual(self._efetch(_tap(_bai(own_ids="", eloc=ELOC_DUNG)))[0]["doi"], OWN)

    def test_elocation_valid_n_khong_dung_va_khong_lay_doi_tham_khao(self):
        self.assertEqual(self._efetch(_tap(_bai(own_ids="", eloc=ELOC_SAI)))[0]["doi"], "")


class TestKDense(unittest.TestCase):
    """Ba script K-Dense (bản sao nhà cung cấp trong sync/skills): ca bản ghi chỉ có DOI ở ELocationID."""

    @classmethod
    def setUpClass(cls):
        try:
            import requests  # noqa: F401 — script nhà cung cấp import ở đầu tệp
        except ImportError:
            raise unittest.SkipTest("thiếu requests trên lane này")
        cls.lit = _nap("literature-review-kdense/scripts/pubmed_lookup.py", "_pm_lit")
        cls.res = _nap("research-lookup-kdense/scripts/pubmed_lookup.py", "_pm_res")
        cls.srch = _nap("citation-management-kdense/scripts/search_pubmed.py", "_pm_srch")
        cls.ext = _nap("citation-management-kdense/scripts/extract_metadata.py", "_pm_ext")

    def _doi_ba_cach(self, bai: str):
        el = ET.fromstring(bai)
        lit = (self.lit.PubMedClient._parse(el) or {}).get("doi")
        res = (self.res.PubMedClient._parse(el) or {}).get("doi")
        srch = (self.srch.PubMedSearcher()._extract_metadata_from_xml(el) or {}).get("doi")
        ext_obj = self.ext.MetadataExtractor()
        phan_hoi = mock.Mock(status_code=200, content=_tap(bai))
        with mock.patch.object(ext_obj.session, "get", return_value=phan_hoi):
            ext = (ext_obj.extract_from_pmid("41967042") or {}).get("doi")
        return {"literature-review": lit, "research-lookup": res, "search_pubmed": srch, "extract_metadata": ext}

    def test_article_id_list_co_doi(self):
        for ten, doi in self._doi_ba_cach(_bai()).items():
            self.assertEqual(doi, OWN, ten)

    def test_chi_co_elocation_thi_khong_lay_doi_tham_khao(self):
        for ten, doi in self._doi_ba_cach(_bai(own_ids="", eloc=ELOC_DUNG)).items():
            self.assertEqual(doi, OWN, ten)

    def test_khong_co_doi_cua_bai_thi_khong_bia_tu_tham_khao(self):
        for ten, doi in self._doi_ba_cach(_bai(own_ids="", eloc=ELOC_SAI)).items():
            self.assertIn(doi, ("", None), ten)


class TestKhongConTrucHauDueArticleId(unittest.TestCase):
    """Không dòng THI HÀNH nào trong sync/skills và tools/ còn rút DOI bằng `.//ArticleId` (bình luận không tính)."""

    def test_quet_dong_thi_hanh(self):
        import re
        mau = re.compile(r"""find(?:all|text)?\(\s*['"]\.//ArticleId['"]""")
        vi_pham = []
        for goc in (SK, REPO / "tools"):
            for f in goc.rglob("*.py"):
                if "__pycache__" in f.parts or f.name.startswith("test_"):
                    continue
                for i, dong in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    ma = dong.split("#", 1)[0]
                    if mau.search(ma):
                        vi_pham.append(f"{f.relative_to(REPO)}:{i}")
        self.assertEqual(vi_pham, [], "còn rút DOI bằng trục hậu duệ .//ArticleId (quét cả ReferenceList)")


if __name__ == "__main__":
    unittest.main()
