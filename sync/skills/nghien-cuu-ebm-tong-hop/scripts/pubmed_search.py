#!/usr/bin/env python3
"""Tìm PubMed qua NCBI E-utilities (MIỄN PHÍ, không cần API key).

Chỉ dùng thư viện chuẩn (urllib) — không phụ thuộc ngoài, chạy được ngay.
Có retry + xử lý lỗi. KHÔNG bịa: chỉ in những gì NCBI trả về (PMID, tiêu đề, tạp chí, năm, DOI).

Dùng:
    python pubmed_search.py "atrial fibrillation anticoagulation guideline" --max 10
    NCBI_EMAIL=you@example.com NCBI_API_KEY=xxxx python pubmed_search.py "sepsis qSOFA" --max 20

Lưu ý EBM: kết quả CẦN bác sĩ kiểm chứng; ưu tiên guideline/SR/RCT; ghi PMID/DOI khi trích dẫn.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EMAIL = os.getenv("NCBI_EMAIL", "")
API_KEY = os.getenv("NCBI_API_KEY", "")


def _get(url: str, retries: int = 3, backoff: float = 1.5) -> bytes:
    """GET có retry/backoff. Tôn trọng giới hạn NCBI (~3 req/s khi không key)."""
    last = None
    for i in range(retries):
        try:
            time.sleep(0.34 if not API_KEY else 0.11)  # etiquette rate-limit
            req = urllib.request.Request(url, headers={"User-Agent": "nghien-cuu-ebm/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001 - in lỗi, thử lại
            last = exc
            time.sleep(backoff * (2 ** i))
    raise RuntimeError(f"Gọi NCBI thất bại sau {retries} lần: {last}")


def _common_params() -> str:
    p = {"db": "pubmed", "retmode": "xml"}
    if EMAIL:
        p["email"] = EMAIL
    if API_KEY:
        p["api_key"] = API_KEY
    return urllib.parse.urlencode(p)


def esearch(query: str, retmax: int) -> list[str]:
    url = (f"{EUTILS}/esearch.fcgi?{_common_params()}"
           f"&term={urllib.parse.quote(query)}&retmax={retmax}&sort=relevance")
    root = ET.fromstring(_get(url))
    return [e.text for e in root.findall(".//IdList/Id") if e.text]


def efetch(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    url = f"{EUTILS}/efetch.fcgi?{_common_params()}&id={','.join(pmids)}"
    root = ET.fromstring(_get(url))
    out = []
    for art in root.findall(".//PubmedArticle"):
        pmid = art.findtext(".//PMID") or ""
        title = (art.findtext(".//ArticleTitle") or "").strip()
        journal = art.findtext(".//Journal/Title") or ""
        year = art.findtext(".//JournalIssue/PubDate/Year") or \
            art.findtext(".//JournalIssue/PubDate/MedlineDate") or ""
        doi = ""
        for idn in art.findall(".//ArticleId"):
            if idn.get("IdType") == "doi":
                doi = (idn.text or "").strip()
        ptypes = [pt.text for pt in art.findall(".//PublicationType") if pt.text]
        out.append({"pmid": pmid, "title": title, "journal": journal,
                    "year": year, "doi": doi, "types": ptypes})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Tìm PubMed (E-utilities, miễn phí)")
    ap.add_argument("query", help="Chuỗi tìm kiếm (cú pháp PubMed)")
    ap.add_argument("--max", type=int, default=10, help="Số kết quả tối đa")
    ap.add_argument("--json", action="store_true", help="Xuất JSON")
    args = ap.parse_args()

    pmids = esearch(args.query, args.max)
    records = efetch(pmids)

    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        if not records:
            print("Không có kết quả (hoặc lỗi mạng). Thử nới chuỗi tìm kiếm.")
        for r in records:
            tag = "/".join(r["types"][:2])
            print(f"- [{r['year']}] {r['title']}")
            print(f"    {r['journal']} · PMID: {r['pmid']}"
                  + (f" · DOI: {r['doi']}" if r['doi'] else "") + (f" · {tag}" if tag else ""))
        print(f"\n{len(records)} bài. ⚠️ Cần bác sĩ kiểm chứng; ưu tiên guideline/SR/RCT.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
