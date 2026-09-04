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
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Callable, Iterable, Sequence

# Windows: stdout mặc định là cp1252 → mọi print() tiếng Việt hoặc ký hiệu (✓ ⚠ →)
# ném UnicodeEncodeError và GIẾT tiến trình, thường SAU KHI công việc đã xong.
# Vá 14/08/2026: hai tool này bị bỏ sót vì chốt BH11 cũ chỉ liệt cứng 4 tên tool.
import sys as _sys_utf8
for _s in (_sys_utf8.stdout, _sys_utf8.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

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
    # Ba nhóm bác sĩ duyệt 30/08/2026 (audit/07 §3): kho đang có 2 dashboard thần
    # kinh (SNNOOP10 ở Neurology; HINTS/BE-FAST ở Stroke) + nguồn sụt cân ở AFP.
    # «neurology»/«stroke» là từ hay gặp trong TIÊU ĐỀ bài ⇒ phải nằm trong
    # AMBIGUOUS_SHORT_ALIASES để chỉ khớp trường tạp chí/tổ chức, không khớp title.
    "AAN/Neurology": ("american academy of neurology", "neurology"),
    "Stroke (AHA)": ("stroke",),
    "AAFP": ("american family physician", "am fam physician", "aafp"),
}
AMBIGUOUS_SHORT_ALIASES = {"who", "ada", "acc", "aha", "esc", "acr", "ema", "ash", "ags", "gold", "gut",
                           "stroke", "neurology"}


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
    # TẦNG chứng cứ mà truy vấn tìm ra ứng viên này (guideline / sr_ma / rct / chung).
    # Thêm 14/08/2026: trước đây một lượt quét trộn lẫn RCT nhỏ với guideline và trả
    # theo thứ tự PubMed, nên bác sĩ phải tự lọc lại đúng thứ hệ đáng lẽ làm hộ.
    tang: str = "chung"
    # ĐỘ TIN CẬY GẮN NGAY LÚC NHẬN (thêm 14/08/2026). Trước đây ứng viên tới tay bác sĩ
    # chỉ mang tiêu đề · tạp chí · ngày · nhãn thẩm quyền SUY TỪ TÊN TẠP CHÍ. Đo được:
    # 0 lần kiểm rút bài, 0 lần đọc loại thiết kế, 0 lần đối chiếu kho trong cả bộ quét.
    # Nghĩa là "mới nhất" và "tin cậy nhất" chưa bao giờ đi cùng nhau tại khâu thu thập.
    pubtype: tuple[str, ...] = ()      # loại thiết kế THẬT từ PubMed, không đoán theo tạp chí
    rut_bai: str = "chua_kiem"         # ok · retracted · expression_of_concern · chua_kiem
    da_co_trong_kho: bool = False      # đã được một dashboard trích rồi → khỏi trình lại
    chua_binh_duyet: bool = False      # preprint (medRxiv/bioRxiv) — chưa qua bình duyệt


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


def search(query: str, days: int, retmax: int, *,
           fetch_json: Callable[[str], dict] = get_json,
           datetype: str = "pdat", loc_thiet_ke: bool = True,
           mindate: str = "", maxdate: str = "") -> list[str]:
    """Tìm ứng viên. `loc_thiet_ke=False` + `datetype='edat'` = tầng BẮT CÁI MỚI NHẤT.

    VÌ SAO CÓ HAI CHẾ ĐỘ (đo thật 14/08/2026)
    ==========================================
    Bộ lọc `[ptyp]` loại bỏ **chính thứ mới nhất**, vì publication type do MEDLINE gán
    trong lúc lập chỉ mục — việc xảy ra HÀNG TUẦN ĐẾN HÀNG THÁNG SAU khi bài vào PubMed.
    Đo trên 40 bài mới vào PubMed 45 ngày (chủ đề suy tim): **30 bài chưa được gán loại
    nào ngoài "Journal Article"**, trong đó có PMID 42552200 — *"Prevalence of orthostatic
    hypotension in heart failure: a systematic review"* — một tổng quan hệ thống bị bộ lọc
    vứt đi chỉ vì chưa kịp đánh chỉ mục.

    Đếm theo chủ đề (45 ngày, `edat`): CÓ lọc 1 · 8 · 0 ứng viên — KHÔNG lọc 46 · 49 · 22.
    Riêng CKD trả **0** trong khi thực có 22 bản ghi mới; bác sĩ đọc "0 ứng viên" thành
    "không có gì mới", trong khi sự thật là bộ lọc đã giết hết.

    `pdat` (ngày công bố) cũng sai cho giám sát: một bài VÀO PubMed hôm nay nhưng mang
    ngày bìa cũ sẽ không lọt cửa sổ. `edat` là ngày bản ghi vào PubMed — đúng câu hỏi
    "có gì MỚI so với lần quét trước".

    Nên: giữ 3 tầng cũ (bắt tài liệu đã đánh chỉ mục, thứ bậc rõ) và THÊM tầng thứ tư
    không lọc để không bỏ sót cái mới. Loại thiết kế nay dùng để GẮN NHÃN và XẾP HẠNG
    (xem `gan_do_tin_cay`), KHÔNG dùng để loại bỏ.
    """
    term = f"({query}) AND {DESIGN}" if loc_thiet_ke else f"({query})"
    params = {
        "db": "pubmed",
        "retmode": "json",
        "sort": "date",
        "datetype": datetype,
        "retmax": str(retmax),
        "term": term,
        "tool": "medical_ebm_surveillance",
    }
    # CON TRỎ TĂNG DẦN (K8): có mindate ⇒ hỏi [mindate, maxdate] thay cho cửa sổ
    # reldate. mindate luôn lùi 3 ngày so với cursor để CHỐNG HỞ KHE (bản ghi vào
    # PubMed muộn quanh ranh giới); dedup phía sau chặn trùng nên lùi là rẻ.
    if mindate:
        params["mindate"] = mindate
        params["maxdate"] = maxdate or "3000"
    else:
        params["reldate"] = str(days)
    url = EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(params)
    try:
        result = fetch_json(url).get("esearchresult", {})
    except RuntimeError:
        # SỬA (vá "fallback Europe PMC bỏ tham số gốc", 2026-09-04): trước đây gọi
        # search_europe_pmc(query, days, retmax) TRƠN — bỏ mất mindate/maxdate/
        # loc_thiet_ke mà caller vừa truyền vào search() ở trên. Hai hậu quả thật:
        # (1) CON TRỎ TĂNG DẦN (K8, comment ở đầu hàm): mindate/maxdate mã hoá cửa
        #     sổ NGÀY HẸP mà cursor đang quét tới — bỏ chúng khiến fallback quay về
        #     cửa sổ `days`-lùi-từ-hôm-nay RỘNG HƠN NHIỀU, tái xuất ứng viên ĐÃ
        #     duyệt ở lượt quét trước vào hàng chờ mỗi khi PubMed tình cờ lỗi.
        # (2) tầng "moi_vao_pubmed" (loc_thiet_ke=False, xem comment run_scan()) —
        #     bỏ loc_thiet_ke khiến fallback ÂM THẦM lọc lại theo publication type,
        #     tái diễn ĐÚNG lỗi BH38 (bài mới chưa kịp gán loại bị vứt) mà tầng này
        #     sinh ra để tránh, chỉ khác là do PubMed lỗi thay vì do quên tham số.
        return search_europe_pmc(query, days, retmax, loc_thiet_ke=loc_thiet_ke,
                                 mindate=mindate, maxdate=maxdate)
    ids = result.get("idlist", [])
    return [str(pmid) for pmid in ids if str(pmid).isdigit()]


def search_europe_pmc(
    query: str,
    days: int,
    retmax: int,
    *,
    fetch_json: Callable[[str], dict] = get_europe_pmc_json,
    loc_thiet_ke: bool = True,
    mindate: str = "",
    maxdate: str = "",
) -> list[str]:
    # mindate/maxdate (khi có) đến từ search() theo khuôn PubMed "YYYY/MM/DD" —
    # Europe PMC cần ISO "YYYY-MM-DD". "3000" là sentinel PubMed dùng cho "không
    # có trần trên" (xem search()); ở đây đổi thành hôm nay vì tương lai không
    # có gì để tìm.
    if mindate:
        since = mindate.replace("/", "-")
        today = (maxdate.replace("/", "-") if maxdate and maxdate != "3000"
                 else datetime.now(timezone.utc).date().isoformat())
    else:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
        today = datetime.now(timezone.utc).date().isoformat()
    # loc_thiet_ke=False (tầng "moi_vao_pubmed") = KHÔNG lọc publication type —
    # đúng ngữ nghĩa của search() (xem BH38, comment ở search()); khớp bộ lọc
    # PUB_TYPE thay vì luôn áp nó vô điều kiện như bản trước bản vá này.
    pub_type_clause = (
        ' AND (PUB_TYPE:"guideline" OR PUB_TYPE:"systematic review" OR '
        'PUB_TYPE:"meta-analysis" OR PUB_TYPE:"randomized controlled trial" '
        'OR TITLE:"guideline")'
    ) if loc_thiet_ke else ""
    term = (
        f'({query}) AND (SRC:MED OR HAS_FT:Y){pub_type_clause} '
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
            pubtype=tuple(str(x) for x in (item.get("pubtype") or [])),
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
        # `queries` = danh sách theo THỨ BẬC chứng cứ. Bổ sung thuần: thiếu thì lùi về
        # `query` cũ, nên watchlist chưa nâng cấp vẫn chạy y như trước.
        tiers = raw.get("queries")
        ds_tang: list[dict[str, str]] = []
        if isinstance(tiers, list):
            for t in tiers:
                if isinstance(t, dict) and str(t.get("query") or "").strip():
                    ds_tang.append({"tang": str(t.get("tang") or "chung"),
                                    "query": str(t["query"]).strip(),
                                    "datetype": str(t.get("datetype") or "pdat"),
                                    "loc_thiet_ke": t.get("loc_thiet_ke", True)})
        if not ds_tang:
            ds_tang = [{"tang": "chung", "query": query,
                        "datetype": "pdat", "loc_thiet_ke": True}]
        active.append({"topic": topic, "query": query, "queries": ds_tang})
    if not active:
        raise ValueError("watchlist không có chủ đề active")
    if len(active) > 50:
        raise ValueError("watchlist có hơn 50 chủ đề active; cần thu hẹp để giảm nhiễu")
    return active




# ══ LÔ 1 KIỆN TOÀN 15/08/2026 (bác sĩ duyệt Q3) — khoá ghi · con trỏ · alerts ══
# Inline thay vì import chéo: file này sống ở 3 bản đồng bộ (EBM-Dashboards/tools ·
# sync/skills/*/tools) — bản trong runtime skill KHÔNG có ../../tools để import.

def _khoa_path() -> Path:
    return DEFAULT_WATCHLIST.parent / ".quet.lock"


def gianh_khoa(han_phut: int = 30) -> tuple[bool, str]:
    """Khoá chống 2 máy/2 tiến trình cùng quét (OneDrive đồng bộ 2 máy — K3).

    Khoá cũ quá `han_phut` coi là MỒ CÔI (tiến trình chết giữa chừng) và được thay.
    Không giành được ⇒ caller phải FAIL RÕ RÀNG, không lặng lẽ chạy tiếp (I7).
    """
    import json as _j
    import os as _os
    import socket as _sk
    import time as _t
    kp = _khoa_path()
    if kp.exists():
        try:
            d = _j.loads(kp.read_text(encoding="utf-8"))
            tuoi_phut = (_t.time() - float(d.get("luc", 0))) / 60
            if tuoi_phut < han_phut:
                return False, (f"máy {d.get('may','?')} (pid {d.get('pid','?')}) đang quét "
                               f"từ {tuoi_phut:.0f} phút trước — không chạy chồng")
        except (ValueError, OSError):
            pass  # khoá hỏng định dạng → coi như mồ côi
    kp.write_text(_j.dumps({"pid": _os.getpid(), "may": _sk.gethostname(),
                            "luc": _t.time()}), encoding="utf-8")
    return True, ""


def tra_khoa() -> None:
    try:
        _khoa_path().unlink(missing_ok=True)
    except OSError:
        pass


def _cursor_path() -> Path:
    return DEFAULT_WATCHLIST.parent / ".quet-cursor.json"


def doc_cursor() -> dict:
    import json as _j
    try:
        return _j.loads(_cursor_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def ghi_cursor(cur: dict) -> None:
    import json as _j
    _cursor_path().write_text(_j.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")


def ghi_alert(dong_md: list[str], ngay: str) -> Path | None:
    """Gom SỰ KIỆN KHẨN vào alerts/YYYY-MM-DD.md (K7). CHỈ sự kiện khẩn — trộn mức
    là dạy người đọc bỏ qua màu đỏ (bài học BH32)."""
    if not dong_md:
        return None
    d = DEFAULT_WATCHLIST.parent.parent / "alerts"
    d.mkdir(exist_ok=True)
    f = d / f"{ngay}.md"
    dau = not f.exists()
    with f.open("a", encoding="utf-8") as fh:
        if dau:
            fh.write(f"# CẢNH BÁO KHẨN — {ngay}\n\n(chỉ sự kiện khẩn: rút bài · cổng FAIL"
                     f" · guideline bị vượt. Cần bác sĩ kiểm chứng.)\n\n")
        fh.write("\n".join(dong_md) + "\n")
    return f

_CHUOI_RUT_BAI = None   # dựng một lần cho cả tiến trình (xem gan_do_tin_cay)


def _pmid_da_co_trong_kho() -> set[str]:
    """PMID đã được MỘT dashboard nào đó trích — đọc sổ xác minh nguồn, không gọi mạng.

    Trình lại thứ bác sĩ đã đọc là tiêu thời gian thật và làm loãng danh sách ứng viên,
    khiến thứ MỚI thật sự bị chôn giữa thứ cũ.
    """
    so = Path(__file__).resolve().parents[1] / ".so-xac-minh-nguon.json"
    if not so.exists():
        return set()
    try:
        muc = (json.loads(so.read_text(encoding="utf-8")) or {}).get("muc", {}) or {}
    except (OSError, json.JSONDecodeError):
        return set()
    return {k.split(":", 1)[1] for k, v in muc.items()
            if k.startswith("pmid:") and v.get("cac_dashboard")}


def gan_do_tin_cay(candidates: Sequence[Candidate]) -> list[Candidate]:
    """Gắn RÚT BÀI + ĐÃ CÓ TRONG KHO cho từng ứng viên, NGAY tại khâu nhận.

    VÌ SAO Ở ĐÂY (14/08/2026): chuỗi 3 tầng kiểm rút bài đã tồn tại từ trước, nhưng chỉ
    được gọi khi rà kho CŨ. Khâu THU THẬP — nơi chứng cứ mới đi vào hệ — chưa bao giờ
    hỏi câu đó. Hệ quả: một bài đã bị rút vẫn có thể vào thẳng hàng ứng viên trình cho
    bác sĩ, và nhãn "authority" suy từ tên tạp chí trông như một bảo đảm chất lượng.

    BẤT ĐỐI XỨNG giữ nguyên như mọi nơi khác: không kiểm được ⇒ `chua_kiem`, TUYỆT ĐỐI
    không mặc định thành "ok". Thiếu môi trường (chạy bằng python hệ thống, thiếu thư
    viện) cũng là `chua_kiem` — im lặng coi là sạch mới là lỗi.
    """
    if not candidates:
        return []
    trong_kho = _pmid_da_co_trong_kho()
    trang_thai: dict[str, str] = {}
    mea = Path(__file__).resolve().parents[2] / "medical-ebm-automation"
    if (mea / "app" / "sources" / "retraction_chain.py").exists():
        try:
            import sys as _sys  # noqa: PLC0415
            if str(mea) not in _sys.path:
                _sys.path.insert(0, str(mea))
            from app.sources.retraction_chain import RetractionChain  # noqa: PLC0415
            # DÙNG LẠI một instance cho cả lượt quét. Mỗi lần dựng mới sẽ nạp lại chỉ mục
            # Retraction Watch 30.851 dòng — đo được 4 lần nạp cho 4 chủ đề. Với watchlist
            # 43 chủ đề thì đó là 43 lần nạp thừa, đủ chậm để người ta tắt lịch nền đi.
            global _CHUOI_RUT_BAI  # noqa: PLW0603
            if _CHUOI_RUT_BAI is None:
                _CHUOI_RUT_BAI = RetractionChain()
            kq = _CHUOI_RUT_BAI.check([c.pmid for c in candidates]) or {}
            for pm, info in kq.items():
                tt = (info or {}).get("status", "")
                trang_thai[pm] = tt if tt in ("ok", "retracted", "expression_of_concern") \
                    else "chua_kiem"
        except Exception:  # noqa: BLE001 — không kiểm được thì để `chua_kiem`, không nuốt thành 'ok'
            trang_thai = {}
    return [replace(c,
                    rut_bai=trang_thai.get(c.pmid, "chua_kiem"),
                    da_co_trong_kho=c.pmid in trong_kho)
            for c in candidates]


def search_preprint_lane(topic: str, days: int, retmax: int,
                         *, fetch_json: Callable[[str], dict] = get_europe_pmc_json,
                         ) -> list[Candidate]:
    """LÀN PREPRINT (nâng cấp C, 15/08/2026 — bác sĩ duyệt sau khi nhãn tin cậy
    chạy ổn định, đúng điều kiện «chưa làm, có chủ ý» đặt ra 14/08).

    Đi qua Europe PMC `SRC:PPR` (medRxiv/bioRxiv/Research Square… — một cửa,
    có tìm theo từ khoá; API riêng của bioRxiv KHÔNG tìm từ khoá được). Mỗi ứng
    viên TỰ KHAI `chua_binh_duyet=True` + tầng riêng — tín hiệu SỚM NHẤT nhưng
    chưa qua bình duyệt, tuyệt đối không trộn lẫn với y văn đã duyệt."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    today = datetime.now(timezone.utc).date().isoformat()
    params = {
        "query": f'({topic}) AND SRC:PPR AND FIRST_PDATE:[{since} TO {today}]',
        "format": "json", "pageSize": str(min(retmax, 10)),
        "sort": "FIRST_PDATE_D desc",
    }
    url = EUROPE_PMC + "?" + urllib.parse.urlencode(params)
    ra: list[Candidate] = []
    for it in fetch_json(url).get("resultList", {}).get("result", []):
        doi = str(it.get("doi") or "")
        # PREPRINT → BẢN BÌNH DUYỆT (16/08, hoãn 2 lần vì giá — nay làn đã trần
        # ≤10 nên 1 call Crossref/preprint là rẻ): quan hệ `is-preprint-of` cho
        # biết bài ĐÃ có bản tạp chí — dán nhãn để bác sĩ trích BẢN ĐÓ, đừng
        # trích preprint khi bản bình duyệt tồn tại. Fail-soft từng bài.
        da_xuat_ban = ""
        if doi:
            try:
                cr = fetch_json("https://api.crossref.org/works/"
                                + urllib.parse.quote(doi))
                rel = ((cr.get("message") or {}).get("relation") or {})
                cua = rel.get("is-preprint-of") or []
                if cua and cua[0].get("id"):
                    da_xuat_ban = str(cua[0]["id"])
            except Exception:  # noqa: BLE001 — nhãn phụ, không giết làn
                pass
        ra.append(Candidate(
            pmid=str(it.get("pmid") or ""),
            publication_date=str(it.get("firstPublicationDate") or ""),
            title=((f"[✅ ĐÃ CÓ BẢN BÌNH DUYỆT — trích doi:{da_xuat_ban}] "
                    if da_xuat_ban else "")
                   + str(it.get("title") or ""))[:300],
            url=(f"https://doi.org/{doi}" if doi
                 else f"https://europepmc.org/article/PPR/{it.get('id', '')}"),
            source="Europe PMC (preprint)",
            journal_or_organization=str(it.get("bookOrReportDetails", {}).get("publisher")
                                        or it.get("journalTitle") or "preprint server"),
            tang="preprint_chua_binh_duyet",
            rut_bai="chua_kiem",
            chua_binh_duyet=True,
        ))
    return ra


def search_trials_lane(topic: str, days: int, retmax: int,
                       *, fetch_json: Callable[[str], dict] = get_json,
                       ) -> list[Candidate]:
    """LÀN THỬ NGHIỆM ĐĂNG KÝ (ClinicalTrials.gov API v2, không cần khoá).

    Trả lời câu «có ai ĐANG LÀM không» LIÊN TỤC cho cả watchlist lâm sàng lẫn
    đề tài nghiên cứu đang chạy — trước đây chỉ được hỏi đúng một lần lúc G0.
    Lọc theo LastUpdatePostDate phía client (API v2 sort được nhưng cú pháp
    filter khoảng-ngày rườm rà); ứng viên mang NCT trong tiêu đề + cờ đã-có-
    kết-quả. KHÔNG phải y văn — tầng riêng, không đếm vào nhóm bình duyệt."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    params = {
        "query.cond": topic, "pageSize": str(min(retmax, 15)),
        "sort": "LastUpdatePostDate:desc",
        "fields": ("NCTId|BriefTitle|OverallStatus|LastUpdatePostDate|HasResults"),
    }
    url = "https://clinicaltrials.gov/api/v2/studies?" + urllib.parse.urlencode(params)
    ra: list[Candidate] = []
    for st in fetch_json(url).get("studies", []):
        ps = st.get("protocolSection", {})
        nct = ps.get("identificationModule", {}).get("nctId", "")
        cap_nhat = (ps.get("statusModule", {})
                    .get("lastUpdatePostDateStruct", {}).get("date", ""))
        if not nct or (cap_nhat and cap_nhat < since):
            continue
        trang_thai = ps.get("statusModule", {}).get("overallStatus", "?")
        co_kq = " · ĐÃ ĐĂNG KẾT QUẢ" if st.get("hasResults") else ""
        ra.append(Candidate(
            pmid="",
            publication_date=cap_nhat,
            title=(f"[{nct} · {trang_thai}{co_kq}] "
                   f"{ps.get('identificationModule', {}).get('briefTitle', '')}")[:300],
            url=f"https://clinicaltrials.gov/study/{nct}",
            source="ClinicalTrials.gov v2",
            journal_or_organization="ClinicalTrials.gov",
            tang="thu_nghiem_dang_ky",
            rut_bai="chua_kiem",
        ))
    return ra


def run_scan(
    topics: Iterable[dict[str, str]],
    *,
    days: int,
    max_results: int,
    cursor: dict | None = None,
    search_fn: Callable[[str, int, int], list[str]] = search,
    summarize_fn: Callable[[Sequence[str]], list[Candidate]] = summarize,
) -> dict:
    """Chạy từng chủ đề độc lập; lỗi một chủ đề không bị nuốt và làm run PARTIAL."""
    started = datetime.now(timezone.utc)
    topic_results: list[TopicResult] = []
    all_pmids: set[str] = set()
    for row in topics:
        try:
            unique: list[Candidate] = []
            # Chạy THEO THỨ TỰ TẦNG: guideline → tổng quan/gộp → RCT. Ứng viên tầng cao
            # vào trước, nên bác sĩ đọc thứ mạnh nhất trước thay vì thứ PubMed trả trước.
            # CON TRỎ theo chủ đề (K8): quét từ max(cursor−3ng, hôm_nay−days) tới nay.
            # --days vẫn là TRẦN cửa sổ; xoá .quet-cursor.json là quay về cửa sổ thuần.
            md = ""
            if cursor is not None:
                cu = cursor.get(row["topic"])
                if cu:
                    import datetime as _dt
                    try:
                        tu = max(_dt.date.fromisoformat(cu) - _dt.timedelta(days=3),
                                 _dt.date.today() - _dt.timedelta(days=days))
                        md = tu.strftime("%Y/%m/%d")
                    except ValueError:
                        md = ""
            for muc_tang in row.get("queries") or [{"tang": "chung", "query": row["query"]}]:
                # Tầng "moi_vao_pubmed" phải đi bằng edat + KHÔNG lọc loại thiết kế —
                # nếu không nó lại rơi vào đúng cái bẫy đang vá. Bộ tìm kiếm giả trong
                # test không nhận tham số phụ, nên lùi êm về chữ ký cũ.
                try:
                    ids = search_fn(muc_tang["query"], days, max_results,
                                    datetype=muc_tang.get("datetype", "pdat"),
                                    loc_thiet_ke=muc_tang.get("loc_thiet_ke", True),
                                    mindate=md)
                except TypeError:
                    ids = search_fn(muc_tang["query"], days, max_results)
                for candidate in summarize_fn(ids):
                    if candidate.pmid in all_pmids:
                        continue
                    all_pmids.add(candidate.pmid)
                    unique.append(replace(candidate, tang=muc_tang["tang"]))
            unique = gan_do_tin_cay(unique)
            # HAI LÀN MỚI (nâng cấp C, 15/08/2026) — chạy SAU gan_do_tin_cay vì
            # tự khai nhãn riêng (preprint không có PMID để tra rút bài; NCT không
            # phải y văn). FAIL-SOFT TỪNG LÀN: làn phụ hỏng không được kéo cả chủ
            # đề FAIL — mất tín hiệu sớm không tệ bằng mất cả lượt quét chính.
            ghi_chu_lan: list[str] = []
            for lane_fn, ten_lan in ((search_preprint_lane, "preprint"),
                                     (search_trials_lane, "clinicaltrials")):
                try:
                    for candidate in lane_fn(row["topic"], days, max_results):
                        khoa_c = candidate.pmid or candidate.url
                        if khoa_c in all_pmids:
                            continue
                        all_pmids.add(khoa_c)
                        unique.append(candidate)
                except Exception as exc:  # noqa: BLE001 — làn phụ, ghi chú minh bạch
                    ghi_chu_lan.append(f"làn {ten_lan} lỗi: {type(exc).__name__}")
            topic_results.append(TopicResult(
                row["topic"], row["query"], "PASS", unique,
                "; ".join(ghi_chu_lan)))
            if cursor is not None:
                import datetime as _dt
                cursor[row["topic"]] = _dt.date.today().isoformat()
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
        (f"- Độ trễ phát hiện: trung vị {report['do_tre']['trung_vi_ngay']} ngày "
         f"({report['do_tre']['n_do_duoc']}/{report['do_tre']['n_tong']} đo được; "
         f"{report['do_tre']['qua_14_ngay']} mục quá ngưỡng 14 ngày)"
         if report.get("do_tre") else "- Độ trễ phát hiện: [CẦN BỔ SUNG] (ngày công bố không đủ chi tiết)"),
        "- Nguồn chính: PubMed E-utilities; dự phòng minh bạch: Europe PMC khi NCBI tạm lỗi",
        "- Trusted-source label: official guideline/regulator bodies, Cochrane, NEJM, Lancet, JAMA, BMJ, Annals, Nature Medicine, and core specialty societies/journals.",
        "- **Nhãn độ tin cậy gắn NGAY lúc nhận:** trạng thái rút bài (chuỗi 3 tầng) · loại "
        "thiết kế thật từ PubMed · đã có trong kho chưa · preprint chưa bình duyệt. "
        "`⚪ chưa kiểm rút bài` nghĩa là CHƯA BIẾT, không phải 'sạch'.",
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
                # NHÃN ĐỘ TIN CẬY phải hiện ngay dòng đầu. Nằm trong JSON mà không in ra
                # thì với người đọc nó không tồn tại — đúng bài học lớn nhất ngày 14/08.
                nhan = []
                rb = item.get("rut_bai", "chua_kiem")
                if rb == "retracted":
                    nhan.append("🔴 ĐÃ BỊ RÚT — KHÔNG dùng")
                elif rb == "expression_of_concern":
                    nhan.append("🟠 có quan ngại (EoC)")
                elif rb != "ok":
                    nhan.append("⚪ chưa kiểm rút bài")
                if item.get("chua_binh_duyet"):
                    nhan.append("⚠️ CHƯA BÌNH DUYỆT (preprint)")
                if item.get("da_co_trong_kho"):
                    nhan.append("↺ đã có trong kho")
                if item.get("tang") and item.get("tang") != "chung":
                    nhan.append(f"tầng: {item['tang']}")
                # Ứng viên từ 2 LÀN NGOÀI PubMed (preprint/NCT — 15/08) KHÔNG được
                # nhận chú «mới vào PubMed» (nói sai về một bản ghi không phải PubMed)
                # và không in «PMID <rỗng>».
                ngoai_pubmed = item.get("tang") in ("preprint_chua_binh_duyet",
                                                    "thu_nghiem_dang_ky")
                pts = [x for x in (item.get("pubtype") or []) if x != "Journal Article"]
                if pts:
                    nhan.append("loại: " + ", ".join(pts[:3]))
                elif not ngoai_pubmed:
                    # CHƯA gán loại = bài vừa vào PubMed, MEDLINE chưa lập chỉ mục. Đây là
                    # dấu hiệu MỚI, không phải khiếm khuyết — và chính nhóm này từng bị bộ
                    # lọc [ptyp] vứt sạch. Nói rõ để bác sĩ biết phải tự đọc loại thiết kế.
                    nhan.append("⚡ mới vào PubMed — CHƯA gán loại thiết kế, tự đọc để xếp tầng")
                nhan_note = ("  \n  - " + " · ".join(nhan)) if nhan else ""
                dinh_danh = f"PMID {item['pmid']}" if item.get("pmid") else "(không PMID — xem link)"
                lines.append(f"- **{item['publication_date']}** · {dinh_danh} · {item['url']}{source_note}{journal_note}{authority_note}")
                lines.append(f"  - {item['title']}{nhan_note}")
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
    parser.add_argument("--since", help="YYYY-MM-DD: ép quét từ ngày này (ghi đè cursor, --days vẫn là trần)")
    parser.add_argument("--topic", help="chỉ quét MỘT chủ đề (khớp tên không dấu, chuỗi con) — "
                                        "orchestrator LÔ 4 và chạy tay dùng; bỏ trống = cả watchlist")
    parser.add_argument("--khong-cursor", action="store_true",
                        help="bỏ qua con trỏ tăng dần, quét trọn cửa sổ --days")
    args = parser.parse_args(argv)
    if not 1 <= args.days <= 3650:
        parser.error("--days phải trong khoảng 1..3650")
    if not 1 <= args.max <= 100:
        parser.error("--max phải trong khoảng 1..100")

    # KHOÁ chống 2 máy/2 tiến trình cùng quét (K3) — FAIL rõ ràng, không chạy chồng.
    duoc, ly_do = gianh_khoa()
    if not duoc:
        print(f"🔴 KHÔNG QUÉT: {ly_do}")
        return 3
    try:
        cursor = None if args.khong_cursor else doc_cursor()
        try:
            topics = load_watchlist(Path(args.watchlist))
        except ValueError as exc:
            parser.error(str(exc))
        if args.topic:
            # Lọc MỘT chủ đề (orchestrator/chạy tay): khớp KHÔNG DẤU hai chiều —
            # «Suy tim» khớp «Suy tim mạn (HFrEF/HFpEF)». Không khớp gì thì phải
            # NỔ ngay chứ không lặng lẽ quét cả kho (im lặng ≠ an toàn).
            import unicodedata as _ud

            def _bo_dau(s: str) -> str:
                return "".join(c for c in _ud.normalize("NFD", s)
                               if _ud.category(c) != "Mn").lower()

            khoa = _bo_dau(args.topic)
            topics = [t for t in topics
                      if khoa in _bo_dau(t["topic"]) or _bo_dau(t["topic"]) in khoa]
            if not topics:
                parser.error(f"--topic không khớp chủ đề nào trong watchlist: {args.topic}")
        if args.since and cursor is not None:
            for t0 in topics:
                cursor[t0["topic"]] = args.since
        try:
            report = run_scan(topics, days=args.days, max_results=args.max, cursor=cursor)
        except ValueError as exc:
            parser.error(str(exc))
        if cursor is not None:
            ghi_cursor(cursor)

        # ĐO ĐỘ TRỄ (K4) — định nghĩa vận hành của "mới nhất" phải đo được. Chỉ đo
        # khi tóm tắt cho ngày đủ chi tiết; thiếu thì [CẦN BỔ SUNG], không ước lượng.
        import datetime as _dt
        tre: list[int] = []
        for _t in report["topics"]:
            for _c in _t["candidates"]:
                try:
                    d0 = _dt.datetime.strptime(_c["publication_date"][:11].strip(),
                                               "%Y %b %d").date()
                    tre.append((_dt.date.today() - d0).days)
                except ValueError:
                    pass
        if tre:
            tre.sort()
            report["do_tre"] = {
                "n_do_duoc": len(tre), "n_tong": report["candidate_count"],
                "trung_vi_ngay": tre[len(tre) // 2],
                "qua_14_ngay": sum(1 for x in tre if x > 14),
                "ghi_chu": ("trễ = hôm_nay − ngày công bố; chỉ tính ứng viên có ngày đủ "
                            "chi tiết, phần còn lại [CẦN BỔ SUNG]"),
            }

        # ALERTS (K7) — chỉ sự kiện KHẨN
        khan: list[str] = []
        for _t in report["topics"]:
            if _t["status"] != "PASS":
                khan.append(f"- 🔴 CỔNG QUÉT FAIL: chủ đề «{_t['topic']}» — `{_t['error'][:90]}`")
            for _c in _t["candidates"]:
                if _c.get("rut_bai") == "retracted":
                    khan.append(f"- 🔴 ỨNG VIÊN ĐÃ BỊ RÚT lọt vào lượt quét: PMID {_c['pmid']} "
                                f"({_t['topic']}) — KHÔNG dùng")
                elif _c.get("rut_bai") == "expression_of_concern":
                    khan.append(f"- 🟠 EoC: PMID {_c['pmid']} ({_t['topic']}) — đọc lại trước khi dùng")
        f_alert = ghi_alert(khan, _dt.date.today().isoformat())
        if f_alert:
            print(f"[⚠ Đã ghi {len(khan)} cảnh báo khẩn: {f_alert}]")
    finally:
        tra_khoa()

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
