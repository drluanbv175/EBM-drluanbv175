#!/usr/bin/env python3
"""Tra trước PMID/DOI cho agent kiểm trích dẫn bằng API công khai, chỉ đọc.

Module không ghi dữ liệu, không đọc ``.env`` và không nhận toàn bộ ca lâm sàng. Nó chỉ
chạy khi yêu cầu kiểm trích dẫn chứa định danh PMID/DOI rõ ràng, rồi tạo biên lai có
provenance để LLM không phải suy đoán metadata hoặc trạng thái rút bài.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PUBMED_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
CROSSREF_WORK = "https://api.crossref.org/works/"
EUROPEPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
USER_AGENT = "EBM-Orchestrator-Citation-Resolver/1.0"

_PMID_RE = re.compile(r"\bPMID\s*[:#]?\s*(\d{6,9})\b", re.IGNORECASE)
_DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
ROOT = Path(__file__).resolve().parents[2]
CANONICAL_RETRACTION_TOOL = ROOT / "medical-ebm-automation" / "tools" / "check_citation_retraction.py"


def _request_bytes(url: str, *, timeout: int = 20, attempts: int = 2) -> bytes:
    """GET có retry hữu hạn; lỗi cuối được đẩy lên để caller ghi trạng thái unknown."""

    last: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 — URL hằng
                return response.read()
        except Exception as exc:  # noqa: BLE001 — lỗi mạng/HTTP/XML được báo có kiểm soát
            last = exc
            if attempt + 1 < attempts:
                time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(str(last or "lỗi mạng không xác định"))


def _text(node: ET.Element | None) -> str:
    return "" if node is None else "".join(node.itertext()).strip()


def _pubmed_record(pmid: str) -> dict[str, Any]:
    url = PUBMED_EFETCH + "?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "retmode": "xml", "rettype": "abstract"}
    )
    root = ET.fromstring(_request_bytes(url))
    article = root.find(".//PubmedArticle")
    if article is None:
        raise RuntimeError(f"PubMed không trả bài cho PMID {pmid}")
    article_node = article.find(".//Article")
    if article_node is None:
        raise RuntimeError(f"PubMed thiếu Article cho PMID {pmid}")
    identifiers: dict[str, str] = {"pmid": pmid}
    for item in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
        id_type = str(item.attrib.get("IdType") or "").lower()
        value = _text(item)
        if id_type and value:
            identifiers[id_type] = value
    pubtypes = [_text(item) for item in article_node.findall(".//PublicationTypeList/PublicationType")]
    authors: list[str] = []
    for author in article_node.findall(".//AuthorList/Author"):
        collective = _text(author.find("CollectiveName"))
        family = _text(author.find("LastName"))
        initials = _text(author.find("Initials"))
        name = collective or " ".join(part for part in (family, initials) if part)
        if name:
            authors.append(name)
    pubdate = article_node.find(".//Journal/JournalIssue/PubDate")
    return {
        "pmid": pmid,
        "doi": identifiers.get("doi", ""),
        "pmcid": identifiers.get("pmc", ""),
        "title": _text(article_node.find("ArticleTitle")),
        "journal": _text(article_node.find(".//Journal/Title")),
        "publication_date": " ".join(
            value for value in (
                _text(pubdate.find("Year")) if pubdate is not None else "",
                _text(pubdate.find("Month")) if pubdate is not None else "",
                _text(pubdate.find("Day")) if pubdate is not None else "",
            ) if value
        ) or (_text(pubdate.find("MedlineDate")) if pubdate is not None else ""),
        "authors": authors,
        "publication_types": pubtypes,
        "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
    }


def _retraction_status(pmid: str) -> dict[str, Any]:
    term = (
        f"{pmid}[PMID] AND (Retracted Publication[PT] OR Retraction of Publication[PT] "
        "OR Expression of Concern[PT])"
    )
    url = PUBMED_ESEARCH + "?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": term, "retmode": "json", "retmax": "5"}
    )
    payload = json.loads(_request_bytes(url).decode("utf-8"))
    ids = payload.get("esearchresult", {}).get("idlist", [])
    return {
        "status": "flagged" if ids else "not_flagged_by_pubmed_query",
        "matched_pmids": [str(value) for value in ids],
        "checked_with": "PubMed publication-type query",
    }


def _crossref_record(doi: str) -> dict[str, Any]:
    url = CROSSREF_WORK + urllib.parse.quote(doi, safe="")
    payload = json.loads(_request_bytes(url).decode("utf-8"))
    message = payload.get("message") or {}
    title = message.get("title") or []
    container = message.get("container-title") or []
    authors = [
        " ".join(part for part in (row.get("family", ""), row.get("given", "")) if part)
        for row in (message.get("author") or [])
    ]
    return {
        "doi": str(message.get("DOI") or doi),
        "title": str(title[0] if title else ""),
        "journal": str(container[0] if container else ""),
        "authors": [name for name in authors if name],
        "type": str(message.get("type") or ""),
        "publisher": str(message.get("publisher") or ""),
        "source_url": f"https://doi.org/{doi}",
    }


def _europepmc_record(pmid: str) -> dict[str, Any]:
    """Fallback chính thống khi NCBI chặn IP/runtime; Europe PMC ánh xạ PMID qua EXT_ID."""

    url = EUROPEPMC_SEARCH + "?" + urllib.parse.urlencode(
        {
            "query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json",
            "resultType": "core", "pageSize": "1",
        }
    )
    payload = json.loads(_request_bytes(url).decode("utf-8"))
    rows = payload.get("resultList", {}).get("result", [])
    if not rows:
        raise RuntimeError(f"Europe PMC không trả bài cho PMID {pmid}")
    row = rows[0]
    return {
        "pmid": str(row.get("pmid") or pmid),
        "doi": str(row.get("doi") or ""),
        "pmcid": str(row.get("pmcid") or ""),
        "title": str(row.get("title") or ""),
        "journal": str(row.get("journalTitle") or ""),
        "publication_date": str(row.get("firstPublicationDate") or row.get("pubYear") or ""),
        "authors": str(row.get("authorString") or ""),
        "publication_types": (row.get("pubTypeList") or {}).get("pubType", []),
        "is_retracted": row.get("isRetracted"),
        "source_url": f"https://europepmc.org/article/MED/{pmid}",
    }


def _europepmc_retraction_status(pmid: str) -> dict[str, Any]:
    term = (
        f'EXT_ID:{pmid} AND SRC:MED AND (PUB_TYPE:"Retracted Publication" '
        'OR PUB_TYPE:"Expression of Concern")'
    )
    url = EUROPEPMC_SEARCH + "?" + urllib.parse.urlencode(
        {"query": term, "format": "json", "pageSize": "5"}
    )
    payload = json.loads(_request_bytes(url).decode("utf-8"))
    rows = payload.get("resultList", {}).get("result", [])
    return {
        "status": "flagged" if rows else "not_flagged_by_europe_pmc_query",
        "matched_ids": [str(row.get("id") or row.get("pmid") or "") for row in rows],
        "checked_with": "Europe PMC publication-type query",
    }


def _canonical_retraction_results(pmids: list[str]) -> tuple[dict[str, Any], str]:
    """Chạy đúng tool A12 canonical; không truyền request tự do và không ghi receipt đề tài."""

    if not pmids or not CANONICAL_RETRACTION_TOOL.exists():
        return {}, "không tìm thấy tool A12 canonical"
    candidates = [
        Path.home() / ".ebm-venv" / "bin" / "python",
        Path.home() / ".ebm-venv" / "Scripts" / "python.exe",
    ]
    python = next((str(path) for path in candidates if path.exists()), sys.executable)
    cmd = [python, str(CANONICAL_RETRACTION_TOOL), "--pmids", ",".join(pmids), "--json"]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        proc = subprocess.run(
            cmd, cwd=str(CANONICAL_RETRACTION_TOOL.parents[1]), env=env,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {}, str(exc)[:300]
    # Logger của dependency có thể đi trước JSON; lấy object ngoài cùng cuối stdout.
    output = proc.stdout or ""
    start = output.find("{")
    try:
        payload = json.loads(output[start:]) if start >= 0 else {}
    except json.JSONDecodeError as exc:
        return {}, f"không đọc được JSON A12: {exc}; stderr={(proc.stderr or '')[-160:]}"
    return (payload if isinstance(payload, dict) else {}), ""


def _normalized_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def prefetch_citation_receipts(agent: str, request: str) -> dict[str, Any] | None:
    """Trả biên lai khi đúng agent và có PMID/DOI; nếu không thì trả ``None``."""

    if agent != "kiem-chung-trich-dan":
        return None
    pmids = list(dict.fromkeys(_PMID_RE.findall(request or "")))[:20]
    dois = [value.rstrip(".,;)") for value in _DOI_RE.findall(request or "")]
    dois = list(dict.fromkeys(dois))[:20]
    if not pmids and not dois:
        return None

    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    derived_dois: list[str] = []
    canonical_retraction, canonical_error = _canonical_retraction_results(pmids)
    for pmid in pmids:
        row: dict[str, Any] = {"identifier": f"PMID:{pmid}"}
        pubmed_error = ""
        try:
            pubmed = _pubmed_record(pmid)
            row["pubmed"] = pubmed
            if pubmed.get("doi"):
                derived_dois.append(str(pubmed["doi"]))
        except Exception as exc:  # noqa: BLE001 — đưa vào receipt, không bịa PASS
            pubmed_error = str(exc)[:300]
        if "pubmed" not in row:
            try:
                epmc = _europepmc_record(pmid)
                row["europe_pmc"] = epmc
                if epmc.get("doi"):
                    derived_dois.append(str(epmc["doi"]))
                warnings.append({
                    "identifier": f"PMID:{pmid}", "source": "PubMed",
                    "warning": f"NCBI không dùng được; đã fallback Europe PMC: {pubmed_error}",
                })
            except Exception as exc:  # noqa: BLE001
                errors.append({
                    "identifier": f"PMID:{pmid}", "source": "PubMed + Europe PMC",
                    "error": f"PubMed={pubmed_error}; EuropePMC={str(exc)[:220]}",
                })
        canonical = canonical_retraction.get(pmid)
        if isinstance(canonical, dict):
            row["retraction_check"] = {
                **canonical,
                "checked_with": "medical-ebm-automation/tools/check_citation_retraction.py",
            }
            if canonical.get("status") in {
                "unresolved", "unknown_mock_or_no_email", "unknown_fetch_error",
            }:
                errors.append({
                    "identifier": f"PMID:{pmid}", "source": "A12 retraction chain",
                    "error": str(canonical.get("reason") or canonical.get("status"))[:300],
                })
        else:
            try:
                row["retraction_check"] = _retraction_status(pmid)
            except Exception as exc:  # noqa: BLE001
                epmc = row.get("europe_pmc") or {}
                if epmc:
                    try:
                        row["retraction_check"] = _europepmc_retraction_status(pmid)
                    except Exception as fallback_exc:  # noqa: BLE001
                        row["retraction_check"] = {"status": "unknown", "error": str(fallback_exc)[:300]}
                        errors.append({
                            "identifier": f"PMID:{pmid}", "source": "retraction",
                            "error": f"PubMed={str(exc)[:140]}; EuropePMC={str(fallback_exc)[:140]}",
                        })
                    warnings.append({
                        "identifier": f"PMID:{pmid}", "source": "PubMed retraction",
                        "warning": f"PubMed query không dùng được; đã fallback Europe PMC: {str(exc)[:220]}",
                    })
                else:
                    row["retraction_check"] = {"status": "unknown", "error": str(exc)[:300]}
                    errors.append({"identifier": f"PMID:{pmid}", "source": "retraction", "error": str(exc)[:300]})
            if canonical_error:
                warnings.append({
                    "identifier": f"PMID:{pmid}", "source": "A12 canonical tool",
                    "warning": f"Tool canonical không dùng được; đã fallback REST: {canonical_error}",
                })
        records.append(row)

    all_dois = list(dict.fromkeys(dois + derived_dois))[:20]
    crossref_by_doi: dict[str, dict[str, Any]] = {}
    for doi in all_dois:
        try:
            crossref_by_doi[doi.casefold()] = _crossref_record(doi)
        except Exception as exc:  # noqa: BLE001
            errors.append({"identifier": f"DOI:{doi}", "source": "Crossref", "error": str(exc)[:300]})
            if doi in dois:
                records.append({"identifier": f"DOI:{doi}"})

    existing_dois = {
        str((row.get("pubmed") or row.get("europe_pmc") or {}).get("doi") or "").casefold()
        for row in records
    }
    for doi in dois:
        if doi.casefold() not in existing_dois and doi.casefold() in crossref_by_doi:
            records.append({"identifier": f"DOI:{doi}", "crossref": crossref_by_doi[doi.casefold()]})

    for row in records:
        metadata = row.get("pubmed") or row.get("europe_pmc") or {}
        doi = str(metadata.get("doi") or row.get("identifier", "").removeprefix("DOI:"))
        crossref = crossref_by_doi.get(doi.casefold()) if doi else None
        if crossref:
            row["crossref"] = crossref
            if metadata.get("title"):
                row["title_match_index_crossref"] = (
                    _normalized_title(metadata["title"]) == _normalized_title(crossref["title"])
                )

    return {
        "kind": "citation_resolution_receipt",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "records": records,
        "errors": errors,
        "warnings": warnings,
        "executed_tools": [
            "citation-resolve",
            *(["citation-retraction"] if canonical_retraction else []),
        ],
        "complete": bool(records) and not errors,
        "provenance": ["NCBI PubMed E-utilities", "Europe PMC REST API", "Crossref REST API"],
        "limitations": (
            "Biên lai xác minh metadata và cờ PubMed tại thời điểm chạy; không tự chứng minh "
            "trích dẫn hỗ trợ đúng câu khẳng định và không thay kiểm tra toàn văn/chuyên gia."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", default="kiem-chung-trich-dan")
    parser.add_argument("request", nargs="?")
    args = parser.parse_args()
    request = args.request if args.request is not None else input()
    receipt = prefetch_citation_receipts(args.agent, request)
    print(json.dumps(receipt or {"kind": "not_applicable"}, ensure_ascii=False, indent=2))
    return 0 if receipt and receipt.get("records") else 2


if __name__ == "__main__":
    raise SystemExit(main())
