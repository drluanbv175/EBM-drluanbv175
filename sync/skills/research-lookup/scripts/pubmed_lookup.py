#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pubmed_lookup.py — Tra cứu y văn qua PubMed E-utilities (MIỄN PHÍ, không cần API key).

Thay thế cho các backend trả phí (parallel.ai / Perplexity / OpenRouter) trong
skill gốc. Tuân thủ quy ước EBM trong CLAUDE.md:
  - Mọi hàm gọi API có error handling + retry.
  - Không lưu thông tin định danh bệnh nhân (PII).
  - Kết quả luôn kèm PMID/DOI để truy nguồn, kèm disclaimer.

Cách dùng:
    python pubmed_lookup.py "metformin AND chronic kidney disease" --limit 20
    python pubmed_lookup.py "statin primary prevention elderly" \
        --types "Meta-Analysis,Systematic Review,Randomized Controlled Trial" \
        --years 2019-2026 --format markdown -o sources/statin.md

API key NCBI là TÙY CHỌN (đặt biến môi trường NCBI_API_KEY để tăng giới hạn lên
10 req/giây; không có key vẫn chạy ở 3 req/giây). Email khuyến nghị: NCBI_EMAIL.
"""

import argparse
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime

try:
    import requests
except ImportError:
    sys.exit("Thiếu thư viện 'requests'. Cài: pip install requests")

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
DISCLAIMER = "⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng."


class PubMedClient:
    """Client PubMed E-utilities với retry + giới hạn tốc độ."""

    def __init__(self, api_key=None, email=None, max_retries=3):
        self.api_key = api_key or os.getenv("NCBI_API_KEY", "")
        self.email = email or os.getenv("NCBI_EMAIL", "")
        self.max_retries = max_retries
        # NCBI: 10 req/s nếu có key, 3 req/s nếu không.
        self.delay = 0.11 if self.api_key else 0.34
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "EBM-Copilot/1.0 (research-lookup)"})

    def _params(self, extra):
        """Gắn email/api_key nếu có."""
        p = dict(extra)
        if self.email:
            p["email"] = self.email
        if self.api_key:
            p["api_key"] = self.api_key
        return p

    def _get(self, endpoint, params):
        """GET có retry với backoff lũy tiến; raise nếu thất bại hết số lần."""
        url = BASE_URL + endpoint
        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                r = self.session.get(url, params=self._params(params), timeout=60)
                r.raise_for_status()
                time.sleep(self.delay)
                return r
            except Exception as e:  # lỗi mạng / HTTP / timeout
                last_err = e
                wait = self.delay * attempt * 3
                print(f"[thử {attempt}/{self.max_retries}] lỗi: {e} → chờ {wait:.1f}s",
                      file=sys.stderr)
                time.sleep(wait)
        raise RuntimeError(f"PubMed {endpoint} thất bại sau {self.max_retries} lần: {last_err}")

    def search(self, query, limit=20, years=None, pub_types=None):
        """ESearch → trả về danh sách PMID. years='2019-2026', pub_types=list."""
        full = query
        if years:
            start, _, end = years.partition("-")
            start = start.strip() or "1900"
            end = (end.strip() or datetime.now().strftime("%Y"))
            full += f" AND {start}:{end}[Publication Date]"
        if pub_types:
            joined = " OR ".join(f'"{t.strip()}"[Publication Type]' for t in pub_types)
            full += f" AND ({joined})"

        print(f"Tìm PubMed: {full}", file=sys.stderr)
        r = self._get("esearch.fcgi", {
            "db": "pubmed", "term": full, "retmax": limit, "retmode": "json",
        })
        data = r.json()["esearchresult"]
        pmids = data.get("idlist", [])
        print(f"Tổng khớp: {data.get('count', '?')} — lấy {len(pmids)}", file=sys.stderr)
        return pmids

    def fetch(self, pmids):
        """EFetch XML → danh sách dict metadata (có PMID/DOI)."""
        if not pmids:
            return []
        out = []
        for i in range(0, len(pmids), 200):
            batch = pmids[i:i + 200]
            r = self._get("efetch.fcgi", {
                "db": "pubmed", "id": ",".join(batch),
                "retmode": "xml", "rettype": "abstract",
            })
            root = ET.fromstring(r.content)
            for art in root.findall(".//PubmedArticle"):
                m = self._parse(art)
                if m:
                    out.append(m)
        return out

    @staticmethod
    def _parse(article):
        """Trích metadata từ một phần tử PubmedArticle."""
        try:
            mc = article.find(".//MedlineCitation")
            art = mc.find(".//Article")
            journal = art.find(".//Journal")

            pmid = mc.findtext(".//PMID", "")

            doi = ""
            for aid in article.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text or ""
                    break

            authors = []
            al = art.find(".//AuthorList")
            if al is not None:
                for a in al.findall(".//Author"):
                    ln = a.findtext(".//LastName", "")
                    init = a.findtext(".//Initials", "")
                    if ln:
                        authors.append(f"{ln} {init}".strip())

            year = art.findtext(".//Journal/JournalIssue/PubDate/Year", "")
            if not year:
                md = art.findtext(".//Journal/JournalIssue/PubDate/MedlineDate", "")
                if md:
                    import re
                    mt = re.search(r"\d{4}", md)
                    year = mt.group() if mt else ""

            # Abstract có thể gồm nhiều phần (BACKGROUND/METHODS/...)
            parts = []
            for ab in art.findall(".//Abstract/AbstractText"):
                label = ab.get("Label")
                txt = "".join(ab.itertext()).strip()
                parts.append(f"{label}: {txt}" if label else txt)
            abstract = "\n".join(p for p in parts if p)

            return {
                "pmid": pmid,
                "doi": doi,
                "title": "".join(art.find(".//ArticleTitle").itertext()).strip()
                         if art.find(".//ArticleTitle") is not None else "",
                "authors": authors,
                "journal": journal.findtext(".//Title", "") if journal is not None else "",
                "year": year,
                "abstract": abstract,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            }
        except Exception as e:
            print(f"Lỗi parse 1 bài: {e}", file=sys.stderr)
            return None


def to_markdown(query, results):
    """Xuất Markdown có trích dẫn PMID/DOI + disclaimer EBM."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Kết quả tra cứu PubMed: {query}",
        "",
        f"*Ngày tra cứu: {now} · Nguồn: PubMed E-utilities (miễn phí) · Số bài: {len(results)}*",
        "",
        f"> {DISCLAIMER} Không tự ý dùng kết quả khi chưa đối chiếu toàn văn và bối cảnh người bệnh.",
        "",
    ]
    for i, r in enumerate(results, 1):
        authors = ", ".join(r["authors"][:3]) + (" et al." if len(r["authors"]) > 3 else "")
        lines.append(f"## {i}. {r['title']}")
        lines.append("")
        lines.append(f"- **Tác giả:** {authors or 'N/A'}")
        lines.append(f"- **Tạp chí/Năm:** {r['journal']} ({r['year'] or 'N/A'})")
        ids = [f"PMID: {r['pmid']}"]
        if r["doi"]:
            ids.append(f"DOI: [{r['doi']}](https://doi.org/{r['doi']})")
        lines.append(f"- **Định danh:** {' · '.join(ids)}")
        lines.append(f"- **Link:** {r['url']}")
        if r["abstract"]:
            lines.append("")
            lines.append(f"> {r['abstract']}")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Tra cứu y văn PubMed (E-utilities miễn phí, có retry)",
        epilog='Ví dụ: python pubmed_lookup.py "SGLT2 inhibitor heart failure" --limit 15',
    )
    ap.add_argument("query", help="Câu truy vấn theo cú pháp PubMed")
    ap.add_argument("--limit", type=int, default=20, help="Số kết quả tối đa (mặc định 20)")
    ap.add_argument("--years", help='Khoảng năm, ví dụ "2019-2026"')
    ap.add_argument("--types", help='Loại bài, vd "Meta-Analysis,Randomized Controlled Trial"')
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("-o", "--output", help="File đầu ra (mặc định: in ra màn hình)")
    ap.add_argument("--api-key", help="NCBI API key (hoặc đặt biến NCBI_API_KEY)")
    ap.add_argument("--email", help="Email Entrez (hoặc đặt biến NCBI_EMAIL)")
    args = ap.parse_args()

    pub_types = [t for t in args.types.split(",")] if args.types else None
    client = PubMedClient(api_key=args.api_key, email=args.email)

    try:
        pmids = client.search(args.query, limit=args.limit, years=args.years, pub_types=pub_types)
        results = client.fetch(pmids)
    except RuntimeError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        sys.exit(2)

    if not results:
        print("Không tìm thấy kết quả.", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        text = json.dumps({"query": args.query, "count": len(results),
                           "disclaimer": DISCLAIMER, "results": results},
                          ensure_ascii=False, indent=2)
    else:
        text = to_markdown(args.query, results)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Đã ghi {len(results)} bài vào {args.output}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
