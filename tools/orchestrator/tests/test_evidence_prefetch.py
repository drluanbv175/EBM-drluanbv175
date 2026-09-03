#!/usr/bin/env python3
"""Kiểm biên lai xác minh trích dẫn deterministic, không gọi mạng."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator.evidence_prefetch import prefetch_citation_receipts  # noqa: E402


PUBMED_XML = b"""<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>41698208</PMID>
<Article><Journal><JournalIssue><PubDate><Year>2026</Year></PubDate></JournalIssue>
<Title>Annals of Internal Medicine</Title></Journal><ArticleTitle>QUADAS-3.</ArticleTitle>
<AuthorList><Author><LastName>Whiting</LastName><Initials>PF</Initials></Author></AuthorList>
<PublicationTypeList><PublicationType>Journal Article</PublicationType></PublicationTypeList>
</Article></MedlineCitation><PubmedData><ArticleIdList>
<ArticleId IdType="doi">10.7326/ANNALS-25-02104</ArticleId>
</ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>"""


class TestEvidencePrefetch(unittest.TestCase):
    def test_only_runs_for_citation_agent_with_explicit_identifier(self):
        self.assertIsNone(prefetch_citation_receipts("tra-cuu-chung-cu", "PMID 41698208"))
        self.assertIsNone(prefetch_citation_receipts("kiem-chung-trich-dan", "không có mã"))

    @patch("orchestrator.evidence_prefetch._canonical_retraction_results")
    @patch("orchestrator.evidence_prefetch._request_bytes")
    def test_pubmed_crossref_and_retraction_receipt(self, request_bytes, canonical):
        canonical.return_value = ({"41698208": {"status": "ok", "source": "fixture"}}, "")
        crossref = {
            "message": {
                "DOI": "10.7326/ANNALS-25-02104", "title": ["QUADAS-3."],
                "container-title": ["Annals of Internal Medicine"], "author": [],
                "type": "journal-article", "publisher": "ACP",
            }
        }
        esearch = {"esearchresult": {"idlist": []}}

        def response(url, **_kwargs):
            if "efetch.fcgi" in url:
                return PUBMED_XML
            if "esearch.fcgi" in url:
                return json.dumps(esearch).encode()
            return json.dumps(crossref).encode()

        request_bytes.side_effect = response
        receipt = prefetch_citation_receipts(
            "kiem-chung-trich-dan", "Kiểm chứng PMID 41698208"
        )
        self.assertIsNotNone(receipt)
        self.assertTrue(receipt["complete"])
        row = receipt["records"][0]
        self.assertEqual(row["pubmed"]["doi"], "10.7326/ANNALS-25-02104")
        self.assertEqual(row["retraction_check"]["status"], "ok")
        self.assertIn("check_citation_retraction.py", row["retraction_check"]["checked_with"])
        self.assertTrue(row["title_match_index_crossref"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
