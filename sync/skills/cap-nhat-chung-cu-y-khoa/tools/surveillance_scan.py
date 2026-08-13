#!/usr/bin/env python3
"""Quét PubMed định kỳ để tạo DANH SÁCH ỨNG VIÊN chứng cứ ngoại trú.

Đầu ra không phải khuyến cáo và không tự đổi thực hành. Mọi lỗi chủ đề được ghi
trong Markdown + JSON; mặc định PARTIAL/FAIL trả mã khác 0 để lịch nền không xanh giả.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Callable, Iterable, Sequence

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
DESIGN = (
    '(Guideline[ptyp] OR "systematic review"[ptyp] OR meta-analysis[ptyp] '
    'OR "practice guideline"[ptyp] OR randomized controlled trial[ptyp])'
)
DISCLAIMER = "Cần bác sĩ kiểm chứng"
DEFAULT_WATCHLIST = Path(__file__).resolve().parents[1] / "watchlist.json"
TRUSTED_SOURCE_ALIASES = {
    "Cochrane": ("cochrane", "cochrane database"),
    "NEJM": ("nejm", "new england journal of medicine", "n engl j med"),
    "The Lancet": ("lancet",),
    "JAMA": ("jama",),
    "The BMJ": ("bmj", "british medical journal"),
    "Annals of Internal Medicine": ("ann intern med", "annals of internal medicine"),
    "Nature Medicine": ("nature medicine", "nat med"),
    "NICE": ("nice", "national institute for health and care excellence"),
    "USPSTF": ("uspstf", "u.s. preventive services task force"),
    "WHO": ("who", "world health organization"),
    "CDC": ("cdc", "mmwr", "centers for disease control"),
    "FDA": ("fda", "food and drug administration"),
    "EMA": ("ema", "european medicines agency"),
    "MHRA": ("mhra", "drug safety update"),
    "ACC/AHA": ("acc", "aha", "american college of cardiology", "american heart association", "jacc", "circulation"),
    "ESC": ("esc", "european society of cardiology", "european heart journal"),
    "ADA/EASD": ("ada", "easd", "american diabetes association", "diabetes care", "diabetologia"),
    "KDIGO": ("kdigo", "kidney international"),
    "GINA": ("gina", "global initiative for asthma"),
    "GOLD": ("gold", "global initiative for chronic obstructive"),
    "IDSA": ("idsa", "clinical infectious diseases"),
    "EULAR/ACR": ("eular", "acr", "american college of rheumatology", "annals of the rheumatic diseases"),
    "ACG/AGA/ASGE": ("acg", "aga", "asge", "american college of gastroenterology", "gastroenterology", "gut"),
    "AASLD/EASL": ("aasld", "easl", "hepatology", "journal of hepatology"),
    "ASH/ISTH": ("ash", "isth", "american society of hematology"),
    "AGS": ("ags", "american geriatrics society", "beers criteria"),
    "ATS/ERS/BTS": ("ats", "ers", "bts", "american thoracic society", "thorax"),
}
AMBIGUOUS_SHORT_ALIASES = {"who", "ada", "acc", "aha", "esc", "acr", "ema", "ash", "ags", "gold", "gut"}


def _tls_context() -> ssl.SSLContext:
    """Dùng CA bundle tin cậy, không bao giờ hạ cấp hoặc tắt xác minh TLS."""
    ca_file = os.getenv("SSL_CERT_FILE", "").strip()
    if not ca_file:
        try:
            import certifi
        except ImportError:
            ca_file = ""
        else:
            ca_file = certifi.where()
    return ssl.create_default_context(cafile=ca_file or None)


def _open_url(request: urllib.request.Request, *, timeout: float) -> object:
    return urllib.request.urlopen(request, timeout=timeout, context=_tls_context())


@dataclass(frozen=True)
class Candidate:
    pmid: str
    publication_date: str
    title: str
    url: str
    source: str = "PubMed E-utilities"
    journal_or_organization: str = ""
    authority_source: str = ""


@dataclass(frozen=True)
class TopicResult:
    topic: str
    query: str
    status: str
    candidates: list[Candidate]
    error: str = ""


def _retry_wait(exc: BaseException, attempt: int) -> float:
    """Ưu tiên Retry-After, giới hạn 30 giây để một nguồn lỗi không treo lịch nền."""
    if isinstance(exc, urllib.error.HTTPError):
        retry_after = exc.headers.get("Retry-After") if exc.headers else None
        if retry_after:
            try:
                return min(float(retry_after), 30.0)
            except ValueError:
                try:
                    dt = parsedate_to_datetime(retry_after)
                    return max(0.0, min((dt - datetime.now(dt.tzinfo)).total_seconds(), 30.0))
                except (TypeError, ValueError, OverflowError):
                    pass
    return min(2.0 ** attempt, 30.0)


def _alias_match(alias: str, blob: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(alias.casefold())}(?![a-z0-9])", blob.casefold()) is not None


def detect_authority_source(journal_or_org: str = "", title: str = "") -> str:
    """Gan nhan nguon uy tin loi de loc queue; khong phai phe duyet ap dung."""
    primary = str(journal_or_org or "")
    combined = " | ".join(part for part in (primary, str(title or "")) if part)
    if not combined:
        return ""
    for name, aliases in TRUSTED_SOURCE_ALIASES.items():
        for alias in aliases:
            blob = primary if alias in AMBIGUOUS_SHORT_ALIASES else combined
            if blob and _alias_match(alias, blob):
                return name
    return ""


def get_json(
    url: str,
    *,
    timeout: float = 20.0,
    retries: int = 2,
    opener: Callable[..., object] = _open_url,
    sleeper: Callable[[float], None] = time.sleep,
) -> dict:
    """GET JSON có User-Agent, retry 429/5xx/timeout và lỗi cuối rõ ràng."""
    email = os.getenv("NCBI_EMAIL", "").strip()
    agent = f"medical-ebm-surveillance/1.0 (mailto:{email or 'not-configured'})"
    request = urllib.request.Request(url, headers={"User-Agent": agent, "Accept": "application/json"})
    last_exc: BaseException | None = None
    for attempt in range(retries + 1):
        try:
            with opener(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
            data = json.loads(payload)
            if not isinstance(data, dict):
                raise ValueError("Payload JSON không phải object")
            return data
        except urllib.error.HTTPError as exc:
            last_exc = exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt >= retries:
                break
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
            last_exc = exc
            if attempt >= retries:
                break
        sleeper(_retry_wait(last_exc, attempt))
    detail = f"{last_exc.__class__.__name__}: {last_exc}" if last_exc else "unknown error"
    raise RuntimeError(f"PubMed request thất bại sau {retries + 1} lần: {detail}") from last_exc


def get_europe_pmc_json(
    url: str,
    *,
    timeout: float = 20.0,
    retries: int = 2,
    opener: Callable[..., object] = _open_url,
    sleeper: Callable[[float], None] = time.sleep,
) -> dict:
    """GET JSON từ Europe PMC như nguồn dự phòng đối chiếu PMID khi NCBI tạm lỗi."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "medical-ebm-surveillance/1.0 (EuropePMC fallback)",
            "Accept": "application/json",
        },
    )
    last_exc: BaseException | None = None
    for attempt in range(retries + 1):
        try:
            with opener(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
            data = json.loads(payload)
            if not isinstance(data, dict):
                raise ValueError("Payload JSON không phải object")
            return data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
            last_exc = exc
            if attempt >= retries:
                break
        sleeper(_retry_wait(last_exc, attempt))
    detail = f"{last_exc.__class__.__name__}: {last_exc}" if last_exc else "unknown error"
    raise RuntimeError(f"Europe PMC fallback thất bại sau {retries + 1} lần: {detail}") from last_exc


def search(query: str, days: int, retmax: int, *, fetch_json: Callable[[str], dict] = get_json) -> list[str]:
    term = f"({query}) AND {DESIGN}"
    params = {
        "db": "pubmed",
        "retmode": "json",
        "sort": "date",
        "reldate": str(days),
        "datetype": "pdat",
        "retmax": str(retmax),
        "term": term,
        "tool": "medical_ebm_surveillance",
    }
    url = EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(params)
    try:
        result = fetch_json(url).get("esearchresult", {})
    except RuntimeError:
        return search_europe_pmc(query, days, retmax)
    ids = result.get("idlist", [])
    return [str(pmid) for pmid in ids if str(pmid).isdigit()]


def search_europe_pmc(
    query: str,
    days: int,
    retmax: int,
    *,
    fetch_json: Callable[[str], dict] = get_europe_pmc_json,
) -> list[str]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    today = datetime.now(timezone.utc).date().isoformat()
    term = (
        f'({query}) AND (SRC:MED OR HAS_FT:Y) AND '
        '(PUB_TYPE:"guideline" OR PUB_TYPE:"systematic review" OR PUB_TYPE:"meta-analysis" '
        'OR PUB_TYPE:"randomized controlled trial" OR TITLE:"guideline") '
        f'AND FIRST_PDATE:[{since} TO {today}]'
    )
    params = {
        "query": term,
        "format": "json",
        "pageSize": str(retmax),
        "sort": "FIRST_PDATE_D desc",
    }
    url = EUROPE_PMC + "?" + urllib.parse.urlencode(params)
    result = fetch_json(url).get("resultList", {}).get("result", [])
    ids = [
        str(item.get("pmid") or item.get("id") or "")
        for item in result
        if str(item.get("pmid") or item.get("id") or "").isdigit()
    ]
    return ids[:retmax]


def summarize(ids: Sequence[str], *, fetch_json: Callable[[str], dict] = get_json) -> list[Candidate]:
    if not ids:
        return []
    params = {
        "db": "pubmed",
        "retmode": "json",
        "id": ",".join(ids),
        "tool": "medical_ebm_surveillance",
    }
    url = EUTILS + "esummary.fcgi?" + urllib.parse.urlencode(params)
    try:
        result = fetch_json(url).get("result", {})
    except RuntimeError:
        return summarize_europe_pmc(ids)
    candidates: list[Candidate] = []
    for pmid in result.get("uids", []):
        item = result.get(str(pmid), {})
        title = str(item.get("title") or "").strip()
        if not str(pmid).isdigit() or not title:
            continue
        journal = str(item.get("source") or "").strip()
        candidates.append(Candidate(
            pmid=str(pmid),
            publication_date=str(item.get("pubdate") or ""),
            title=title,
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            source="PubMed E-utilities",
            journal_or_organization=journal,
            authority_source=detect_authority_source(journal, title),
        ))
    return candidates


def summarize_europe_pmc(
    ids: Sequence[str],
    *,
    fetch_json: Callable[[str], dict] = get_europe_pmc_json,
) -> list[Candidate]:
    if not ids:
        return []
    quoted = " OR ".join(f"EXT_ID:{pmid}" for pmid in ids if str(pmid).isdigit())
    params = {
        "query": f"({quoted}) AND SRC:MED",
        "format": "json",
        "pageSize": str(len(ids)),
    }
    url = EUROPE_PMC + "?" + urllib.parse.urlencode(params)
    result = fetch_json(url).get("resultList", {}).get("result", [])
    by_id = {str(item.get("pmid") or item.get("id") or ""): item for item in result}
    candidates: list[Candidate] = []
    for pmid in ids:
        item = by_id.get(str(pmid), {})
        title = str(item.get("title") or "").strip()
        if not str(pmid).isdigit() or not title:
            continue
        journal = str(item.get("journalTitle") or item.get("bookOrReportDetails") or "").strip()
        candidates.append(Candidate(
            pmid=str(pmid),
            publication_date=str(item.get("firstPublicationDate") or item.get("pubYear") or ""),
            title=title,
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            source="Europe PMC fallback for PMID",
            journal_or_organization=journal,
            authority_source=detect_authority_source(journal, title),
        ))
    return candidates


def load_watchlist(path: Path) -> list[dict[str, str]]:
    """Kiểm schema, trùng chủ đề/query và chỉ trả chủ đề active."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Không đọc được watchlist {path}: {exc}") from exc
    topics = payload.get("topics") if isinstance(payload, dict) else None
    if not isinstance(topics, list):
        raise ValueError("watchlist phải có mảng topics")
    active: list[dict[str, str]] = []
    seen_topics: set[str] = set()
    seen_queries: set[str] = set()
    for index, raw in enumerate(topics, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"topics[{index}] không phải object")
        if raw.get("active", True) is False:
            continue
        topic = str(raw.get("topic") or "").strip()
        query = str(raw.get("query") or "").strip()
        if not topic or not query:
            raise ValueError(f"topics[{index}] thiếu topic/query")
        topic_key, query_key = topic.casefold(), query.casefold()
        if topic_key in seen_topics:
            raise ValueError(f"Trùng topic: {topic}")
        if query_key in seen_queries:
            raise ValueError(f"Trùng query: {query}")
        seen_topics.add(topic_key)
        seen_queries.add(query_key)
        active.append({"topic": topic, "query": query})
    if not active:
        raise ValueError("watchlist không có chủ đề active")
    if len(active) > 50:
        raise ValueError("watchlist có hơn 50 chủ đề active; cần thu hẹp để giảm nhiễu")
    return active


def run_scan(
    topics: Iterable[dict[str, str]],
    *,
    days: int,
    max_results: int,
    search_fn: Callable[[str, int, int], list[str]] = search,
    summarize_fn: Callable[[Sequence[str]], list[Candidate]] = summarize,
) -> dict:
    """Chạy từng chủ đề độc lập; lỗi một chủ đề không bị nuốt và làm run PARTIAL."""
    started = datetime.now(timezone.utc)
    topic_results: list[TopicResult] = []
    all_pmids: set[str] = set()
    for row in topics:
        try:
            ids = search_fn(row["query"], days, max_results)
            candidates = summarize_fn(ids)
            unique: list[Candidate] = []
            for candidate in candidates:
                if candidate.pmid in all_pmids:
                    continue
                all_pmids.add(candidate.pmid)
                unique.append(candidate)
            topic_results.append(TopicResult(row["topic"], row["query"], "PASS", unique))
        except Exception as exc:  # noqa: BLE001 - lỗi được ghi vào audit, không nuốt
            topic_results.append(TopicResult(
                row["topic"], row["query"], "FAIL", [],
                f"{exc.__class__.__name__}: {exc}"[:600],
            ))

    success_count = sum(result.status == "PASS" for result in topic_results)
    failure_count = len(topic_results) - success_count
    if not topic_results or success_count == 0:
        status = "FAIL"
    elif failure_count:
        status = "PARTIAL"
    else:
        status = "PASS"
    finished = datetime.now(timezone.utc)
    return {
        "kind": "outpatient_evidence_surveillance_scan",
        "status": status,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": finished.isoformat(timespec="seconds"),
        "days": days,
        "max_results_per_topic": max_results,
        "topic_count": len(topic_results),
        "successful_topics": success_count,
        "failed_topics": failure_count,
        "candidate_count": len(all_pmids),
        "topics": [asdict(result) for result in topic_results],
        "auto_apply": False,
        "next_state": "CANDIDATE_REVIEW_QUEUE",
        "disclaimer": f"{DISCLAIMER}. Ứng viên không phải khuyến cáo; cần thẩm định Track A.",
    }


def markdown_report(report: dict) -> str:
    lines = [
        f"# Giám sát định kỳ - chứng cứ mới ({report['days']} ngày gần đây)",
        "",
        f"- Trạng thái: **{report['status']}**",
        f"- Chủ đề PASS/FAIL: {report['successful_topics']}/{report['failed_topics']}",
        f"- Ứng viên không trùng: {report['candidate_count']}",
        "- Nguồn chính: PubMed E-utilities; dự phòng minh bạch: Europe PMC khi NCBI tạm lỗi",
        "- Trusted-source label: official guideline/regulator bodies, Cochrane, NEJM, Lancet, JAMA, BMJ, Annals, Nature Medicine, and core specialty societies/journals.",
        f"- **ỨNG VIÊN để thẩm định, KHÔNG phải khuyến cáo. {DISCLAIMER}.**",
        "",
    ]
    for result in report["topics"]:
        lines.append(f"## {result['topic']}")
        if result["status"] != "PASS":
            lines.append(f"- **KHÔNG QUÉT ĐƯỢC:** `{result['error']}`")
            lines.append("- Không được diễn giải là 'không có cập nhật'.")
        elif not result["candidates"]:
            lines.append("- Không tìm thấy ứng viên trong cửa sổ đã quét thành công.")
        else:
            for item in result["candidates"]:
                source_note = f" · nguồn: {item.get('source', 'PubMed E-utilities')}"
                journal_note = f" · journal/org: {item.get('journal_or_organization')}" if item.get("journal_or_organization") else ""
                authority_note = f" · authority: {item.get('authority_source')}" if item.get("authority_source") else ""
                lines.append(f"- **{item['publication_date']}** · PMID {item['pmid']} · {item['url']}{source_note}{journal_note}{authority_note}")
                lines.append(f"  - {item['title']}")
        lines.append("")
    lines.extend([
        "---",
        "Bước tiếp: chọn mục liên quan, xác minh nguồn chính và chạy Track A trước khi đề xuất thay đổi thực hành.",
        f"**{report['disclaimer']}**",
        "",
    ])
    return "\n".join(lines)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watchlist", default=str(DEFAULT_WATCHLIST))
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--max", type=int, default=6)
    parser.add_argument("--report")
    parser.add_argument("--json-report")
    parser.add_argument("--allow-partial", action="store_true", help="Chỉ dùng chẩn đoán; báo cáo vẫn giữ PARTIAL/FAIL.")
    args = parser.parse_args(argv)
    if not 1 <= args.days <= 3650:
        parser.error("--days phải trong khoảng 1..3650")
    if not 1 <= args.max <= 100:
        parser.error("--max phải trong khoảng 1..100")

    try:
        topics = load_watchlist(Path(args.watchlist))
        report = run_scan(topics, days=args.days, max_results=args.max)
    except ValueError as exc:
        parser.error(str(exc))

    markdown = markdown_report(report)
    print(markdown)
    if args.report:
        write_atomic(Path(args.report), markdown)
        print(f"[Đã lưu báo cáo: {args.report}]")
    if args.json_report:
        write_atomic(Path(args.json_report), json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(f"[Đã lưu audit JSON: {args.json_report}]")
    if report["status"] == "PASS" or args.allow_partial:
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
