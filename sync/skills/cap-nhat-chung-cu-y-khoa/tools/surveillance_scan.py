#!/usr/bin/env python3
"""Quét PubMed định kỳ để tạo DANH SÁCH ỨNG VIÊN chứng cứ ngoại trú.

Đầu ra không phải khuyến cáo và không tự đổi thực hành. Mọi lỗi chủ đề được ghi
trong Markdown + JSON; mặc định PARTIAL/FAIL trả mã khác 0 để lịch nền không xanh giả.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import ssl
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field, fields, replace
from datetime import date, datetime, timedelta, timezone
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


class NCBIBiChan(RuntimeError):
    """NCBI trả trang chặn IP (HTTP 200 kèm HTML) — KHÔNG retry, KHÔNG coi là lỗi mạng thoáng qua."""


# Trạng thái theo TIẾN TRÌNH (một lượt quét = một tiến trình): đã bị NCBI chặn chưa, và các lần
# tìm kiếm rơi xuống dự phòng trong truy vấn hiện tại. `run_scan` đặt lại mỗi lượt / mỗi truy vấn.
_NCBI_CHAN: dict = {"bi_chan": False}
_SUY_GIAM: list[str] = []
# Truy vấn khớp NHIỀU hơn trần lấy (xem TRAN_LAY_MOI_TANG): chỉ GHI CHÚ, không làm chủ đề suy giảm.
_VUOT_TRAN: list[str] = []

# PHƯƠNG ÁN B — «lấy đủ rồi chọn mạnh nhất» (bác sĩ chọn 24/09/2026). Trước đây mỗi tầng chỉ lấy `--max`
# (6) ID MỚI NHẤT rồi trình nguyên: đo kỳ W39, 12/47 chủ đề có tầng bị cắt, 96 bài được trình trên 608 bài
# khớp — 512 bài không bao giờ tới tay bác sĩ, và thứ tự trình là «mới nhất» chứ không phải «mạnh nhất».
# Nay mỗi tầng lấy tới TRAN_LAY_MOI_TANG ID (vẫn MỘT lượt esearch), tóm tắt theo lô LO_TOM_TAT, xếp theo
# độ mạnh chứng cứ (xem khoa_manh_nhat) rồi mới cắt còn `--max` để trình; phần còn lại ghi vào
# TopicResult.khong_trinh — không bài nào bị bỏ IM LẶNG. Vượt trần chỉ ghi chú: sort theo ngày nên quét
# lại cũng chỉ trả lại đúng các bài mới nhất — giữ con trỏ đứng yên không thu hồi được gì mà chỉ làm chủ
# đề «suy giảm» mãi và làm quét lô dừng (luật 22/09 đã gây đúng lỗi đó).
TRAN_LAY_MOI_TANG = 300
LO_TOM_TAT = 100


def _la_trang_chan_ncbi(payload: str) -> bool:
    """Trang HTML chặn của NCBI ('WWW Error Blocked Diagnostic' / 'Access Denied ... abuse')."""
    return bool(re.search(r"blocked|access denied|misuse|abuse", payload[:6000], re.I))


def _la_host_ncbi(url: str) -> bool:
    """True khi URL trỏ vào host NCBI (eutils.ncbi.nlm.nih.gov).

    Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #2): `get_json` bị TÁI DÙNG cho
    ClinicalTrials.gov (search_trials_lane mặc định fetch_json=get_json). Một trang chặn
    Cloudflare của ClinicalTrials.gov ('Attention Required… blocked') khớp CÙNG regex
    _la_trang_chan_ncbi — nếu không tách theo host, nó gán nhầm cờ `_NCBI_CHAN['bi_chan']`
    (vốn chỉ nên bật khi CHÍNH NCBI chặn), khiến mọi chủ đề còn lại trong lượt quét bỏ
    qua NCBI oan và bị chẩn đoán sai 'NCBI đang chặn IP' trong khi NCBI vẫn hoạt động."""
    try:
        return "ncbi.nlm.nih.gov" in urllib.parse.urlparse(url).netloc
    except ValueError:
        return False


# ── DỊCH CÚ PHÁP PUBMED → EUROPE PMC (vá 21/09/2026) ────────────────────────────────────────────
# Truy vấn watchlist viết bằng thẻ PubMed ([pt] [ta] [ti] [ad] [tw] [tiab] [cn] [mh] [dp]). Europe PMC
# KHÔNG hiểu các thẻ đó: nhét thô vào thì mệnh đề AND với thẻ trở thành «chữ '[pt]' phải có mặt» và trả
# 0 GIẢ — đo 21/09: 12/12 truy vấn tầng guideline/tổng quan/RCT trả 0 qua đường dự phòng, trong khi cùng ý
# viết đúng cú pháp Europe PMC trả 31–269. Trước bản vá, khi NCBI chặn, 4 làn thẩm quyền và 3 tầng chứng
# cứ mạnh biến mất mà báo cáo vẫn ghi PASS (alerts 01/09, 07/09).
# Bộ dịch HỮU HẠN: gặp thẻ lạ thì RAISE (fail-closed, chủ đề FAIL rõ ràng) — không đoán, không bỏ thẻ.
_THE_EPMC_TRUONG = {"pt": "PUB_TYPE", "ptyp": "PUB_TYPE", "ta": "JOURNAL", "ti": "TITLE",
                    "title": "TITLE", "ad": "AFF", "cn": "AUTH", "mh": "MESH"}
_THE_EPMC_TIEU_DE_TOM_TAT = {"tiab", "tw"}
_RE_TOKEN_TRUY_VAN = re.compile(r'\s*("[^"]*"|\(|\)|\[[^\]]*\]|[^\s()\[\]"]+)')


def dich_pubmed_sang_europepmc(query: str) -> str:
    """Dịch một truy vấn viết theo thẻ PubMed sang cú pháp trường của Europe PMC.

    Thẻ gắn vào CỤM đứng ngay trước nó, tính từ toán tử/dấu ngoặc gần nhất (PubMed coi
    `randomized controlled trial[pt]` là một cụm). Ví dụ:
      practice guideline[pt]        → PUB_TYPE:"practice guideline"
      "Lancet"[ta]                  → JOURNAL:"Lancet"
      Standards[ti]                 → TITLE:Standards
      "NICE guideline"[tw]          → (TITLE:"NICE guideline" OR ABSTRACT:"NICE guideline")
      2026[dp]                      → PUB_YEAR:2026
    Đoạn không gắn thẻ giữ NGUYÊN (Europe PMC tìm toàn văn theo từ). Thẻ không có trong bảng ⇒ ValueError.
    """
    if (query or "").count('"') % 2 or (query or "").count("[") != (query or "").count("]") \
            or (query or "").count("(") != (query or "").count(")"):
        # Nháy/ngoặc lệch: bộ tách bỏ im lặng ký tự lệch (`x[pt` → `x pt`) ⇒ truy vấn méo mà không ai biết. Fail-closed.
        raise ValueError(f"truy vấn có nháy/ngoặc không cân: {(query or '')[:120]!r}")
    out: list[str] = []
    run: list[str] = []

    def flush() -> None:
        if run:
            out.append(" ".join(run))
            run.clear()

    for tok in _RE_TOKEN_TRUY_VAN.findall(query or ""):
        if tok in ("(", ")"):
            flush()
            out.append(tok)
        elif tok in ("AND", "OR", "NOT"):
            flush()
            out.append(tok)
        elif tok.startswith("["):
            the = tok[1:-1].strip().lower()
            if not run:
                raise ValueError(f"thẻ PubMed [{the}] không có cụm đứng trước trong truy vấn: {query[:120]!r}")
            if the == "dp" and len(run) > 1:
                # [dp] là thẻ NGÀY: chỉ áp cho từ cuối (năm); các từ đứng trước là chữ tìm bình thường
                # («drug safety alert recall guideline 2026[dp]»). Khác [pt]/[ta]: đó là CỤM nhiều từ.
                out.append(" ".join(run[:-1]))
                del run[:-1]
            cum = " ".join(run).strip()
            run.clear()
            if len(cum) >= 2 and cum[0] == '"' and cum[-1] == '"' and '"' not in cum[1:-1]:
                cum = cum[1:-1]
            if '"' in cum:
                # `"a b" c[ti]` = cụm hỗn hợp có nháy lồng ⇒ TITLE:""a b" c" là truy vấn hỏng; không đoán ý người viết.
                raise ValueError(f"cụm gắn thẻ [{the}] chứa nháy lồng: {cum!r}")
            if the in _THE_EPMC_TIEU_DE_TOM_TAT:
                q = f'"{cum}"' if " " in cum else cum
                out.append(f"(TITLE:{q} OR ABSTRACT:{q})")
            elif the == "dp":
                if not re.fullmatch(r"\d{4}", cum):
                    raise ValueError(f"thẻ [dp] chỉ hỗ trợ năm 4 chữ số, gặp {cum!r}")
                out.append(f"PUB_YEAR:{cum}")
            elif the in _THE_EPMC_TRUONG:
                q = f'"{cum}"' if (" " in cum or the in ("pt", "ptyp", "ta", "ad", "cn", "mh")) else cum
                out.append(f"{_THE_EPMC_TRUONG[the]}:{q}")
            else:
                raise ValueError(f"thẻ PubMed [{the}] chưa có bản dịch sang Europe PMC (truy vấn: {query[:120]!r})")
        else:
            run.append(tok)
    flush()
    ket = " ".join(out)
    if re.search(r"\[[A-Za-z ]+\]", ket):  # phòng thủ: còn sót thẻ ⇒ đừng gửi đi
        raise ValueError(f"còn thẻ PubMed chưa dịch trong: {ket[:160]!r}")
    return ket
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
    # Vá 14/09/2026 (workflow kiểm tra toàn diện): trang PubMed/JAMA thật viết
    # "US Preventive Services Task Force" — KHÔNG dấu chấm — nên alias cũ "u.s.
    # preventive services task force" (có dấu chấm) KHÔNG BAO GIỜ khớp; giữ cả
    # hai dạng, không bỏ dạng cũ (vài nguồn/thời kỳ khác có thể vẫn viết có chấm).
    "USPSTF": ("uspstf", "u.s. preventive services task force",
               "us preventive services task force"),
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

# Vá 14/09/2026 (workflow kiểm tra toàn diện, xác nhận sống qua Europe PMC:
# 14/15 USPSTF Recommendation Statement thật đăng trên JAMA). detect_authority_source()
# duyệt TRUSTED_SOURCE_ALIASES theo THỨ TỰ DICT và trả về khớp ĐẦU TIÊN — vì "JAMA"
# đứng trước "USPSTF" trong dict, MỌI USPSTF Statement đăng trên JAMA (gần như toàn
# bộ từ 2017) bị gán nhãn "JAMA", KHÔNG BAO GIỜ "USPSTF", dù alias "uspstf"/"u.s.
# preventive services task force" có mặt trong dict — chuỗi khớp tồn tại nhưng
# KHÔNG THỂ ĐƯỢC CHỌN vì lỗi thứ tự ưu tiên, không phải thiếu alias.
# Các tạp chí trong nhóm này là NƠI ĐĂNG CHUNG cho nhiều tổ chức khác nhau (một
# guideline JAMA có thể là của USPSTF, ACC/AHA, hoặc chính JAMA) nên chỉ được dùng
# làm nhãn DỰ PHÒNG — kiểm SAU khi không alias TỔ CHỨC nào khớp. Cochrane KHÔNG nằm
# trong nhóm này: "Cochrane Database of Systematic Reviews" là ấn phẩm CỦA CHÍNH
# Cochrane, không phải nơi tổ chức khác đăng nhờ.
_TAP_CHI_DA_NANG = frozenset({"NEJM", "The Lancet", "JAMA", "The BMJ", "Annals of Internal Medicine",
                              "Nature Medicine"})
# Tiền tố alias của CHÍNH các tạp chí đa năng — dùng để nhường vòng 1 khi tên
# tạp chí (primary) đã rõ ràng thuộc một họ tạp chí đa năng, vd "JAMA Neurology"
# bắt đầu bằng "jama". Không có nhường này thì alias MƠ HỒ của một tổ chức khác
# (vd "neurology" của AAN/Neurology, chỉ so trên `primary`) sẽ khớp CHÍNH primary
# đó ở vòng 1 trước khi vòng 2 kịp nhận đúng "JAMA Neurology" thuộc họ JAMA —
# bắt được thật khi test_ba_nhan_tap_chi_bac_si_duyet_30_08 đỏ sau bản vá đầu.
_TAP_CHI_DA_NANG_TIEN_TO = tuple(
    alias.casefold() for name in _TAP_CHI_DA_NANG for alias in TRUSTED_SOURCE_ALIASES[name]
)


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

    def __post_init__(self) -> None:
        # Vá 30/09/2026 — GỐC RỄ của lượt W40 sập (29/09): engine có nguồn chỉ trả NĂM kiểu số, và ba làn Scopus/CORE/
        # dự phòng chép thẳng `rec.publication_date` vào trường khai là `str` này ⇒ mọi nơi cắt chuỗi về sau nhận int.
        # Ép về chuỗi tại MỘT điểm nghẽn: mọi cách dựng ứng viên (làn mới, `replace()`, summarize_fn do caller tiêm)
        # đều đi qua đây — thay vì vá từng nơi tiêu thụ.
        ngay = self.publication_date
        if not isinstance(ngay, str):
            object.__setattr__(self, "publication_date", "" if ngay is None else str(ngay))


_TRUONG_UNG_VIEN = frozenset(f.name for f in fields(Candidate))
_TRUONG_CHUOI_UNG_VIEN = ("pmid", "publication_date", "title", "url", "source", "journal_or_organization",
                          "authority_source", "rut_bai")


def _ung_vien_tu_so(muc: object) -> Candidate | None:
    """Dựng lại một ứng viên dự phòng từ mục `cho_trinh` của sổ (30/09/2026). Sổ là tệp JSON nằm trong OneDrive — có
    thể bị sửa tay/ghi dở — nên mục hỏng (không phải dict, thiếu trường bắt buộc, sai kiểu, không có khoá pmid/url)
    trả `None` để bị BỎ, không làm sập lượt quét. Tầng luôn là `du_phong_bac_thang`: `main()` nhận diện bài còn chờ
    trình theo đúng nhãn này."""
    if not isinstance(muc, dict):
        return None
    du = {k: v for k, v in muc.items() if k in _TRUONG_UNG_VIEN}
    try:
        du["pubtype"] = tuple(str(x) for x in (du.get("pubtype") or ()))
        c = replace(Candidate(**du), tang="du_phong_bac_thang")
    except TypeError:
        return None
    if not all(isinstance(getattr(c, truong), str) for truong in _TRUONG_CHUOI_UNG_VIEN):
        return None
    return c if (c.pmid or c.url) else None


@dataclass(frozen=True)
class TopicResult:
    topic: str
    query: str
    status: str
    candidates: list[Candidate]
    error: str = ""
    # Các truy vấn phải rơi xuống dự phòng (NCBI lỗi/bị chặn): kết quả có thể THIẾU. Không rỗng ⇒ status
    # = "PASS_DEGRADED" và con trỏ KHÔNG tiến (xem run_scan) — trước đây vẫn "PASS" và mất cửa sổ vĩnh viễn.
    suy_giam: list[str] = field(default_factory=list)
    # Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #10): TRƯỜNG MÁY ĐỌC riêng cho làn phụ hỏng
    # (preprint/clinicaltrials/scopus) — trước đây thông tin này chỉ nằm trong `error` dạng CHUỖI TỰ
    # DO ("làn scopus lỗi: RuntimeError"), lẫn với suy_giam khi cả hai cùng xảy ra. Khi CẢ BA làn phụ
    # cùng hỏng, `status` vẫn "PASS" (làn phụ không dùng con trỏ nên không kéo chủ đề FAIL/DEGRADED),
    # nên JSON/mã thoát/alert đều "sạch" — bên tiêu thụ (uu_tien_cap_nhat, orchestrator) không có
    # cách nào phân biệt "0 ứng viên vì không có gì mới" với "0 ứng viên vì cả 3 làn phụ đều hỏng"
    # nếu không tự phân tích chuỗi `error`. Trường này liệt TÊN làn hỏng (không phải câu văn), rỗng
    # khi mọi làn phụ chạy được (kể cả khi chúng trả 0 kết quả — đó là tín hiệu THẬT, không phải lỗi).
    lan_phu_loi: list[str] = field(default_factory=list)
    # Phương án B (24/09/2026): ứng viên ĐÃ QUÉT nhưng KHÔNG trình (ngoài top `--max` của tầng sau khi xếp
    # theo độ mạnh) — ghi lại để không bài nào bị bỏ im lặng. Mỗi mục: pmid · tang · diem · pubtype · title ·
    # ngay · tap_chi.
    khong_trinh: list[dict] = field(default_factory=list)


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
    """Gan nhan nguon uy tin loi de loc queue; khong phai phe duyet ap dung.

    Vá 14/09/2026: kiểm alias TỔ CHỨC trước, alias TẠP CHÍ ĐA NĂNG
    (_TAP_CHI_DA_NANG) sau — xem chú thích tại _TAP_CHI_DA_NANG. Không đổi cách
    khớp từng alias (_alias_match/AMBIGUOUS_SHORT_ALIASES giữ nguyên), chỉ đổi
    THỨ TỰ DUYỆT để nhãn tổ chức đặc hiệu không bị nhãn tạp chí chung che khuất."""
    primary = str(journal_or_org or "")
    combined = " | ".join(part for part in (primary, str(title or "")) if part)
    if not combined:
        return ""
    primary_cf = primary.casefold()
    for name, aliases in TRUSTED_SOURCE_ALIASES.items():
        if name in _TAP_CHI_DA_NANG:
            continue
        for alias in aliases:
            if alias in AMBIGUOUS_SHORT_ALIASES:
                # Nhường vòng 2 khi chính tên tạp chí đã rõ ràng thuộc một họ tạp
                # chí đa năng (vd "JAMA Neurology" bắt đầu bằng "jama") — xem chú
                # thích tại _TAP_CHI_DA_NANG_TIEN_TO.
                if primary_cf and primary_cf.startswith(_TAP_CHI_DA_NANG_TIEN_TO):
                    continue
                blob = primary
            else:
                blob = combined
            if blob and _alias_match(alias, blob):
                return name
    for name in _TAP_CHI_DA_NANG:
        for alias in TRUSTED_SOURCE_ALIASES[name]:
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
            if payload.lstrip()[:1] == "<" and _la_trang_chan_ncbi(payload):
                if _la_host_ncbi(url):
                    # Trang chặn trả HTTP 200: retry chỉ tốn ~46 giây/truy vấn mà không bao giờ tự hết.
                    _NCBI_CHAN["bi_chan"] = True
                    raise NCBIBiChan("NCBI chặn IP (trang 'blocked/abuse'), không retry — liên hệ info@ncbi.nlm.nih.gov")
                # Nguồn KHÁC NCBI dùng chung get_json (vd ClinicalTrials.gov) — KHÔNG được lây
                # cờ NCBI sang các chủ đề khác; chỉ báo lỗi cho đúng làn đang gọi (không retry,
                # trang chặn không tự hết bằng cách hỏi lại).
                raise RuntimeError(f"Trang chặn/lỗi HTML từ nguồn không phải NCBI: {url[:90]}")
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
            if "hitCount" not in data and "resultList" not in data:
                # Europe PMC thi thoảng trả bản RỖNG chỉ có {"version": "6.9"} (đo 21/09: cùng một truy vấn lúc
                # trả stub, lúc trả 46.703 kết quả). Đọc stub là «0 kết quả» chính là 0 GIẢ — coi là LỖI để retry,
                # hết lượt thì báo lỗi rõ ràng (chủ đề FAIL) thay vì im lặng trả rỗng.
                raise ValueError("Europe PMC trả bản rỗng (chỉ có 'version') — không phải 0 kết quả thật")
            return data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
            last_exc = exc
            if attempt >= retries:
                break
        sleeper(_retry_wait(last_exc, attempt))
    detail = f"{last_exc.__class__.__name__}: {last_exc}" if last_exc else "unknown error"
    raise RuntimeError(f"Europe PMC fallback thất bại sau {retries + 1} lần: {detail}") from last_exc


def get_crossref_json(
    url: str,
    *,
    timeout: float = 20.0,
    retries: int = 2,
    opener: Callable[..., object] = _open_url,
    sleeper: Callable[[float], None] = time.sleep,
) -> dict:
    """GET JSON từ Crossref (tra quan hệ `is-preprint-of` cho làn preprint).

    Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #1 — HIGH, do chính bản vá làn
    preprint 15/08 gây ra). `search_preprint_lane` trước đây TÁI DÙNG `get_europe_pmc_json`
    (qua tham số `fetch_json` dùng chung) để gọi CẢ Europe PMC LẪN Crossref — nhưng guard
    "hitCount/resultList" của hàm đó chỉ đúng cho payload Europe PMC; payload Crossref luôn
    có dạng {status, message-type, message}, KHÔNG BAO GIỜ có hai khoá đó, nên MỌI lần tra
    is-preprint-of raise ValueError và bị `except Exception: pass` ở search_preprint_lane
    nuốt im lặng — nhãn "[✅ ĐÃ CÓ BẢN BÌNH DUYỆT]" biến mất ở MỌI preprint có DOI, cộng
    ~3 giây backoff + 2 lần gọi Crossref thừa mỗi preprint. Hàm riêng này không mang guard đó."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "medical-ebm-surveillance/1.0 (Crossref is-preprint-of lookup)",
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
    raise RuntimeError(f"Crossref request thất bại sau {retries + 1} lần: {detail}") from last_exc


def search(query: str, days: int, retmax: int, *,
           fetch_json: Callable[[str], dict] = get_json,
           datetype: str = "pdat", loc_thiet_ke: bool = True,
           mindate: str = "", maxdate: str = "",
           fallback_fetch_json: Callable[[str], dict] | None = None) -> list[str]:
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
    _kw_du_phong = {"fetch_json": fallback_fetch_json} if fallback_fetch_json else {}
    if fetch_json is get_json and _NCBI_CHAN["bi_chan"]:
        # Đã bị NCBI chặn trong lượt này: khỏi hỏi lại (mỗi lần hỏi lại là một lần chờ vô ích).
        _SUY_GIAM.append("NCBI đang chặn IP — truy vấn này chạy bằng Europe PMC dự phòng")
        return search_europe_pmc(query, days, retmax, loc_thiet_ke=loc_thiet_ke,
                                 mindate=mindate, maxdate=maxdate, **_kw_du_phong)
    try:
        _j = fetch_json(url)
        # NCBI đôi khi trả HTTP 200 kèm {"error": …} hoặc esearchresult.ERROR: bản cũ đọc thành «0 kết quả» (không suy giảm,
        # con trỏ vẫn tiến — phản biện 21/09). Bản lỗi là LỖI.
        if not isinstance(_j, dict) or _j.get("error") or not isinstance(_j.get("esearchresult"), dict) \
                or _j["esearchresult"].get("ERROR"):
            raise RuntimeError(f"NCBI trả bản lỗi/thiếu esearchresult: {str(_j)[:80]}")
        result = _j["esearchresult"]
        # Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #3): esearchresult THIẾU idlist/count
        # (vd {"header":{},"esearchresult":{}}) trước đây lọt qua — result.get("idlist", []) biến
        # khoá thiếu thành [] và bản trả về trông y hệt "0 kết quả thật". Đòi cả hai khoá có mặt.
        if "idlist" not in result or "count" not in result:
            raise RuntimeError(f"esearchresult thiếu idlist/count: {str(result)[:80]}")
        # errorlist.fieldsnotfound/phrasesnotfound: NCBI không nhận ra thẻ/cụm trong truy vấn (thẻ gõ
        # sai hoặc Europe PMC-only lọt vào) — trả 0 kết quả GIẢ, cùng họ với esearchresult.ERROR ở trên.
        _loi_truong = None
        for _khoa in ("errorlist", "warninglist"):
            _muc = result.get(_khoa)
            if isinstance(_muc, dict):
                _loi_truong = _muc.get("fieldsnotfound") or _muc.get("phrasesnotfound") or _loi_truong
        if _loi_truong:
            raise RuntimeError(f"NCBI không nhận ra thẻ/cụm trong truy vấn: {_loi_truong}")
    except RuntimeError as exc:
        # SUY GIẢM (21/09/2026): dự phòng là ĐÚNG khi NCBI lỗi nhưng kết quả có thể THIẾU (Europe PMC
        # không đánh chỉ mục/gán loại giống PubMed). Ghi lại để run_scan gắn cờ PASS_DEGRADED và KHÔNG
        # tiến con trỏ — không được để lượt quét suy giảm trông như lượt quét đầy đủ.
        # Vá 22/09/2026: giữ NGUYÊN VĂN lý do (không chỉ tên lớp exception) — "thiếu idlist/count"
        # và "không nhận ra thẻ/cụm" cần phân biệt được với lỗi mạng thường khi đọc lại _SUY_GIAM.
        _SUY_GIAM.append(f"NCBI lỗi ({exc}) — truy vấn này chạy bằng Europe PMC dự phòng"[:220])
        # Vá 14/09/2026: PHẢI chuyển tiếp loc_thiet_ke — thiếu dòng này thì tầng
        # "mới nhất" (loc_thiet_ke=False) im lặng biến thành tầng có lọc ngay khi
        # rơi xuống dự phòng, tái diễn đúng lỗi BH38 qua một đường khác.
        # Vá 04/09/2026 (workflow đối kháng đa-agent): cũng PHẢI chuyển tiếp
        # mindate/maxdate — thiếu chúng thì CON TRỎ TĂNG DẦN (K8, xem comment
        # ở đầu hàm) mất tác dụng ngay khi rơi xuống dự phòng: fallback quay về
        # cửa sổ `days`-lùi-từ-hôm-nay RỘNG HƠN NHIỀU thay vì cửa sổ HẸP mà
        # cursor đang quét, khiến ứng viên ĐÃ duyệt tái xuất vào hàng chờ mỗi
        # khi PubMed tình cờ lỗi.
        return search_europe_pmc(query, days, retmax, loc_thiet_ke=loc_thiet_ke,
                                 mindate=mindate, maxdate=maxdate, **_kw_du_phong)
    ids = result.get("idlist", [])
    # esearch khớp NHIỀU hơn `retmax` (sort=date desc ⇒ chỉ lấy `retmax` bản mới nhất). Luật 22/09 ghi việc
    # này vào _SUY_GIAM (PASS_DEGRADED, con trỏ đứng yên) — nhưng quét lại vẫn chỉ trả các bản MỚI NHẤT nên
    # không thu hồi được bản nào, chỉ làm chủ đề suy giảm mãi và quét lô dừng. Từ 24/09 (phương án B) run_scan
    # gọi với retmax = TRAN_LAY_MOI_TANG; vượt trần ⇒ GHI CHÚ minh bạch trong _VUOT_TRAN, không suy giảm.
    try:
        _tong = int(result.get("count", len(ids)))
    except (TypeError, ValueError):
        _tong = len(ids)
    if _tong > len(ids):
        _VUOT_TRAN.append(
            f"vượt trần lấy: đã quét {len(ids)}/{_tong} bản ghi mới nhất khớp truy vấn "
            "— truy vấn quá rộng, nên thu hẹp"
        )
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
    """Vá 14/09/2026 (workflow kiểm tra toàn diện): trước đây bộ lọc PUB_TYPE
    LUÔN áp dụng vô điều kiện, kể cả khi search() gọi hàm này làm DỰ PHÒNG cho
    tầng "bắt cái mới nhất" (loc_thiet_ke=False, datetype='edat' — chính tầng
    BH38 vá để không bỏ sót bài chưa được MEDLINE gán publication type). Đo sống
    14/09/2026: NCBI đang chặn IP dùng chung (xác nhận trực tiếp — esearch trả
    trang "Access Denied... blocked for possible abuse" thay vì JSON) — đúng
    điều kiện khiến search() rơi xuống dự phòng này; khi đó bài mới vào PubMed
    chưa kịp đánh chỉ mục bị Europe PMC lọc mất lần thứ hai, hoàn toàn im lặng
    (TopicResult vẫn status='PASS'). Nay nhận đúng cờ loc_thiet_ke như search()
    và chỉ áp PUB_TYPE khi True — tầng "mới nhất" giữ đúng ý nghĩa dù đi qua
    đường dự phòng nào.

    Vá 04/09/2026 (workflow đối kháng đa-agent): cũng nhận mindate/maxdate —
    thiếu chúng thì CON TRỎ TĂNG DẦN (K8, xem comment ở search()) mất tác dụng
    ngay khi rơi xuống nhánh dự phòng này, quay về cửa sổ `days`-lùi-từ-hôm-nay
    RỘNG hơn hẳn cửa sổ hẹp mà cursor đang quét — ứng viên ĐÃ duyệt tái xuất
    vào hàng chờ mỗi khi PubMed tình cờ lỗi.
    """
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
    loc = (
        ' AND (PUB_TYPE:"guideline" OR PUB_TYPE:"systematic review" OR PUB_TYPE:"meta-analysis" '
        'OR PUB_TYPE:"randomized controlled trial" OR TITLE:"guideline")'
        if loc_thiet_ke else ""
    )
    # VÁ 21/09/2026: dịch thẻ PubMed sang cú pháp Europe PMC (xem dich_pubmed_sang_europepmc) — trước đây
    # truyền THÔ nên tầng guideline/tổng quan/RCT và 4 làn thẩm quyền trả 0 giả qua đường dự phòng.
    query_epmc = dich_pubmed_sang_europepmc(query)
    term = (
        f'({query_epmc}) AND (SRC:MED OR HAS_FT:Y){loc} '
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
    if fetch_json is get_json and _NCBI_CHAN["bi_chan"]:
        _SUY_GIAM.append("esummary: NCBI đang chặn — tóm tắt ứng viên bằng Europe PMC")
        return summarize_europe_pmc(ids)
    try:
        _j = fetch_json(url)
        if not isinstance(_j, dict) or _j.get("error") or not isinstance(_j.get("result"), dict):
            raise RuntimeError(f"NCBI esummary trả bản lỗi/thiếu result: {str(_j)[:80]}")
        result = _j["result"]
    except RuntimeError as exc:
        _SUY_GIAM.append(f"esummary NCBI lỗi ({type(exc).__name__}) — tóm tắt ứng viên bằng Europe PMC")
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
    if len(candidates) < len(ids):
        _SUY_GIAM.append(f"esummary: {len(ids) - len(candidates)}/{len(ids)} PMID không có tóm tắt — ứng viên bị bỏ")
    return candidates


def _pubtype_europe_pmc(item: dict) -> tuple[str, ...]:
    """Loại thiết kế từ bản ghi Europe PMC: `pubTypeList.pubType` (core) hoặc `pubType` chuỗi «a; b» (lite).

    Trước đây đường dự phòng KHÔNG điền pubtype nên mọi ứng viên bị gắn «⚡ mới vào PubMed — CHƯA gán loại»
    dù đã có loại thật (Systematic Review, Practice Guideline…)."""
    lst = (item.get("pubTypeList") or {}).get("pubType")
    if isinstance(lst, list) and lst:
        return tuple(str(x).strip() for x in lst if str(x).strip())
    raw = item.get("pubType")
    if isinstance(raw, str) and raw.strip():
        return tuple(x.strip() for x in raw.split(";") if x.strip())
    return ()


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
            pubtype=_pubtype_europe_pmc(item),
        ))
    if len(candidates) < len(ids):
        # Europe PMC chưa lập chỉ mục bài mới trong vài ngày đầu ⇒ ứng viên MỚI NHẤT chính là thứ bị bỏ; không được im lặng.
        _SUY_GIAM.append(f"Europe PMC: {len(ids) - len(candidates)}/{len(ids)} PMID chưa có bản ghi — ứng viên bị bỏ")
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
        muc = {"topic": topic, "query": query, "queries": ds_tang}
        # `truy_van_du_phong` (tuỳ chọn, 27/09/2026) = truy vấn TIẾNG ANH ngôn ngữ tự nhiên cho bậc thang dự phòng
        # Consensus → SerpApi (tính phí). Thiếu thì chủ đề tên tiếng Việt KHÔNG leo thang — xem
        # `_co_nen_leo_thang_du_phong`. Phải chép qua đây: hàm này dựng lại từng mục, khoá không chép là mất.
        truy_van_du_phong = str(raw.get("truy_van_du_phong") or "").strip()
        if truy_van_du_phong:
            muc["truy_van_du_phong"] = truy_van_du_phong
        active.append(muc)
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


@contextlib.contextmanager
def _mutex_khoa(kp: Path):
    """Khoá loại trừ CẤP HỆ ĐIỀU HÀNH quanh thủ tục giành khoá (flock / msvcrt) — tự nhả khi tiến trình chết, không mồ côi.

    Đặt cạnh tệp khoá (không dùng thư mục tạm: TMPDIR khác nhau giữa tác vụ lịch và phiên tay sẽ làm mỗi bên một mutex)."""
    import os as _os
    mp = kp.with_name(kp.name + ".mutex")
    f = open(mp, "a+b")  # noqa: SIM115 — giữ mở suốt vùng găng
    try:
        if _os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            if _os.name == "nt":
                import msvcrt
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        f.close()


def gianh_khoa(han_phut: int = 30) -> tuple[bool, str]:
    """Khoá chống 2 máy/2 tiến trình cùng quét (OneDrive đồng bộ 2 máy — K3).

    Khoá cũ quá `han_phut` coi là MỒ CÔI (tiến trình chết giữa chừng) và được thay.
    Không giành được ⇒ caller phải FAIL RÕ RÀNG, không lặng lẽ chạy tiếp (I7).

    VÁ 02/10/2026 (F5, kiểm toàn diện): bản cũ «kiểm rồi mới ghi» (`exists()` rồi `write_text`) — đo 10 tiến trình cùng giành
    một mốc, 10 vòng: 10/10 vòng có > 1 tiến trình cùng «giành được» (5–10 tiến trình/vòng) ⇒ hai lượt quét cùng ghi con trỏ/sổ.
    Chỉ đổi sang `O_EXCL` vẫn hở khi đã có khoá MỒ CÔI (đo 8 tiến trình: 2–5 tiến trình/vòng cùng thay khoá mồ côi — đứa đến sau
    gỡ nhầm khoá mới, hoặc đọc phải khoá rỗng đang ghi dở). Nay: cả thủ tục đọc–gỡ–tạo chạy TRONG `_mutex_khoa` (khoá hệ điều
    hành, tuần tự hoá mọi tiến trình trên MỘT máy) và tệp khoá vẫn tạo bằng `O_EXCL` (phòng bản cũ chưa vá chạy song song).
    Giữa HAI MÁY vẫn chỉ dựa vào OneDrive đồng bộ tệp khoá (giới hạn cũ, không đổi).
    """
    kp = _khoa_path()
    try:
        return _gianh_trong_mutex(kp, han_phut)
    except OSError as e:  # không khoá được vùng găng (Windows LK_LOCK hết 10 lần thử, thư mục chỉ đọc…)
        return False, f"không khoá được vùng găng của khoá quét ({e.__class__.__name__}) — không chạy chồng"


def _gianh_trong_mutex(kp: Path, han_phut: int) -> tuple[bool, str]:
    import json as _j
    import os as _os
    import socket as _sk
    import time as _t
    with _mutex_khoa(kp):
        if kp.exists():
            try:
                d = _j.loads(kp.read_text(encoding="utf-8"))
                tuoi_phut = (_t.time() - float(d.get("luc", 0))) / 60
                if tuoi_phut < han_phut:
                    return False, (f"máy {d.get('may','?')} (pid {d.get('pid','?')}) đang quét "
                                   f"từ {tuoi_phut:.0f} phút trước — không chạy chồng")
            except (ValueError, OSError, AttributeError, TypeError):
                pass  # khoá hỏng định dạng → coi như mồ côi
            try:
                kp.unlink()
            except FileNotFoundError:
                pass
        try:
            fd = _os.open(str(kp), _os.O_CREAT | _os.O_EXCL | _os.O_WRONLY, 0o644)
        except FileExistsError:
            return False, "tranh chấp khoá quét (tiến trình khác vừa giành) — không chạy chồng"
        with _os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(_j.dumps({"pid": _os.getpid(), "may": _sk.gethostname(), "luc": _t.time()}))
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


def _du_phong_path() -> Path:
    return DEFAULT_WATCHLIST.parent / ".du-phong-trang-thai.json"


def _cho_trinh_hop_le(tho: object) -> dict:
    """Chuẩn hoá khoá `cho_trinh` đọc từ sổ: {chủ đề: {"ngay": ISO, "ung_vien": [dict ứng viên]}}; mục sai dạng bị bỏ."""
    ra: dict = {}
    if isinstance(tho, dict):
        for chu_de, muc in tho.items():
            if isinstance(muc, dict) and isinstance(muc.get("ung_vien"), list):
                bai = [u for u in muc["ung_vien"] if isinstance(u, dict)]
                if bai:
                    ra[str(chu_de)] = {"ngay": str(muc.get("ngay") or ""), "ung_vien": bai}
    return ra


def _doc_so_du_phong() -> tuple[dict, str]:
    """(sổ, lỗi) của bậc thang dự phòng TÍNH PHÍ. Sổ gồm `lan_cuoi_leo_thang` {chủ đề: ngày} để XOAY VÒNG và tính trần
    tuần, `da_trinh` {khoá bài: ngày} để không trình lại bài đã trình, `cho_trinh` {chủ đề: {ngay, ung_vien}} — bài ĐÃ
    LẤY (đã tốn hạn mức) mà báo cáo của lượt đó chưa tới nơi, lượt sau trình bù không gọi lại nguồn — và
    `leo_thang_loi` {chủ đề: ngày} — lần leo thang gần nhất LỖI nên được thử lại trong tuần.

    Tệp VẮNG ⇒ sổ rỗng hợp lệ (lỗi ""). Tệp CÓ mà không đọc được / không phải đối tượng JSON ⇒ (sổ rỗng, mô tả lỗi):
    nơi gọi phải TẮT làn dự phòng của lượt đó và KHÔNG ghi sổ (vá 30/09/2026). Trước đây mọi lỗi đọc đều thành «sổ
    rỗng, không mất gì» — đúng khi sổ chỉ là bộ nhớ xoay vòng, sai từ khi sổ giữ trần tuần và bài đã trả phí: một lần
    đọc lỗi (tệp OneDrive chưa tải về, ghi dở) rồi ghi đè là mất hàng chờ, mất mốc của mọi chủ đề và gọi lại nguồn."""
    import json as _j
    rong = {"lan_cuoi_leo_thang": {}, "da_trinh": {}, "cho_trinh": {}, "leo_thang_loi": {}}
    duong = _du_phong_path()
    # Lối thoát khi tệp ĐỌC ĐƯỢC nhưng HỎNG — phải nói ra, nếu không làn dự phòng tắt vô thời hạn mà không ai biết cách gỡ.
    loi_thoat = (" — khôi phục bản trước từ lịch sử phiên bản OneDrive, hoặc đổi tên tệp để bắt đầu sổ mới (hệ quả: "
                 "trần tuần tính lại từ 0, mất «đã trình» và hàng chờ)")
    try:
        so = _j.loads(duong.read_text(encoding="utf-8-sig"))   # utf-8-sig: sổ có BOM (trình soạn thảo Windows) vẫn hợp lệ
    except FileNotFoundError:
        return rong, ""
    except OSError as exc:
        return rong, (f"không đọc được sổ {duong.name} ({type(exc).__name__}) — kiểm OneDrive đã tải tệp về chưa, "
                      "có bản xung đột không, rồi chạy lại")
    except ValueError:
        return rong, f"sổ {duong.name} không phải JSON hợp lệ{loi_thoat}"
    if not isinstance(so, dict):
        return rong, f"sổ {duong.name} không phải đối tượng JSON{loi_thoat}"
    # Từng khoá: vắng/None ⇒ rỗng; CÓ mà không phải đối tượng ⇒ sổ hỏng (kể cả `[]`, `""`, `0` — không ép kiểu thành
    # rỗng rồi ghi đè; và không để `dict("x")` ném lỗi làm sập cả lượt quét).
    for khoa in rong:
        if so.get(khoa) is not None and not isinstance(so[khoa], dict):
            return rong, f"sổ {duong.name} có khoá «{khoa}» sai kiểu{loi_thoat}"
    return {"lan_cuoi_leo_thang": dict(so.get("lan_cuoi_leo_thang") or {}),
            "da_trinh": dict(so.get("da_trinh") or {}),
            "cho_trinh": _cho_trinh_hop_le(so.get("cho_trinh")),
            "leo_thang_loi": dict(so.get("leo_thang_loi") or {})}, ""


def doc_trang_thai_du_phong() -> dict:
    """Sổ dự phòng, bỏ qua lỗi đọc (rỗng khi vắng/hỏng) — cho nơi CHỈ ĐỌC. `main()` dùng `_doc_so_du_phong()` để
    phân biệt «vắng» với «không đọc được» trước khi ghi."""
    return _doc_so_du_phong()[0]


def ghi_trang_thai_du_phong(so: dict) -> None:
    import json as _j
    write_atomic(_du_phong_path(), _j.dumps(so, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


def ghi_alert(dong_md: list[str], ngay: str) -> Path | None:
    """Gom SỰ KIỆN KHẨN vào alerts/YYYY-MM-DD.md (K7). CHỈ sự kiện khẩn — trộn mức
    là dạy người đọc bỏ qua màu đỏ (bài học BH32).

    Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #9): dòng đã CÓ NGUYÊN VĂN trong file hôm
    nay thì KHÔNG ghi lại — trước đây `ghi_alert` luôn append vô điều kiện, nên chạy `main()`
    nhiều lần trong cùng ngày (orchestrator A2 chạy TỪNG chủ đề riêng, hoặc bác sĩ chạy tay lặp
    lại) làm file tích nhiều dòng GIỐNG HỆT nhau — đúng kiểu nhiễu dạy người đọc bỏ qua (BH32),
    và vi phạm yêu cầu "idempotent, không nhân đôi" của SKILL goi-duyet-tuan-ebm bước 6."""
    if not dong_md:
        return None
    d = DEFAULT_WATCHLIST.parent.parent / "alerts"
    d.mkdir(exist_ok=True)
    f = d / f"{ngay}.md"
    dau = not f.exists()
    da_co: set[str] = set()
    if not dau:
        try:
            da_co = set(f.read_text(encoding="utf-8").splitlines())
        except OSError:
            da_co = set()
    dong_moi = [d0 for d0 in dong_md if d0 not in da_co]
    if not dong_moi:
        return f if f.exists() else None
    with f.open("a", encoding="utf-8") as fh:
        if dau:
            fh.write(f"# CẢNH BÁO KHẨN — {ngay}\n\n(chỉ sự kiện khẩn: rút bài · cổng FAIL"
                     f" · guideline bị vượt. Cần bác sĩ kiểm chứng.)\n\n")
        fh.write("\n".join(dong_moi) + "\n")
    return f

def _tim_medical_ebm_automation() -> Path | None:
    """Đường dẫn tới `medical-ebm-automation/` — DÒ THEO CÂY THƯ MỤC, không dùng
    một chỉ số `parents[N]` cố định.

    VÁ 22/09/2026 (cùng đợt nối làn CORE): file này sống ở BA vị trí độ sâu khác
    nhau kể từ gốc repo — `EBM-Dashboards/tools/` (2 cấp) và hai bản vendor
    `sync/skills/*/tools/` (4 cấp). Bản cũ dùng `parents[2]` cố định — đúng cho
    vị trí đầu, nhưng SAI cho hai bản vendor (trỏ vào `sync/skills/`, nơi không
    có gì). Đo thực nghiệm: từ bản vendor, `parents[2] / "medical-ebm-automation"`
    không tồn tại dù `medical-ebm-automation/` là ANH EM của gốc repo thật —
    khiến làn Scopus VÀ kiểm rút bài qua RetractionChain im lặng trả `[]`/bỏ
    qua mỗi khi chạy từ bản vendor, giống hệt "chưa cấu hình" dù thực ra đã bật
    đủ. Dò lên tối đa 7 cấp, dừng ở thư mục ĐẦU TIÊN có
    `medical-ebm-automation/app/sources/` — tự đúng ở cả ba vị trí.
    """
    p = Path(__file__).resolve().parent
    for _ in range(7):
        ung = p / "medical-ebm-automation"
        if (ung / "app" / "sources").is_dir():
            return ung
        if p.parent == p:
            break
        p = p.parent
    return None


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
    mea = _tim_medical_ebm_automation()
    if mea and (mea / "app" / "sources" / "retraction_chain.py").exists():
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
                         fetch_crossref: Callable[[str], dict] = get_crossref_json,
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
                cr = fetch_crossref("https://api.crossref.org/works/"
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


def search_scopus_lane(topic: str, days: int, retmax: int,
                       *, client_factory: Callable[[], object] | None = None,
                       ) -> list[Candidate]:
    """LÀN SCOPUS (Elsevier) — thêm 13/09/2026, bác sĩ yêu cầu nối vào tầng giám
    sát lâm sàng ngay sau khi xác nhận key hoạt động thật ở tầng nghiên cứu.

    TÁI DÙNG `medical-ebm-automation/app/sources/scopus.py::ScopusClient` qua
    cross-import (CÙNG khuôn `gan_do_tin_cay()` đã dùng cho RetractionChain) —
    không viết lại logic gọi API/xử lý lỗi mạng/giới hạn PUBYEAR ở đây, vì bản
    đó đã có 14 test (mutation-tested) ở phía nghiên cứu. Import kéo theo
    `from app.config import settings`, có tác dụng phụ nạp `.env` qua
    `load_dotenv()` — nên `SCOPUS_API_KEY`/`ENABLE_SCOPUS` đọc đúng dù tiến
    trình gọi file này không tự set biến môi trường trước.

    BA MỨC "không có kết quả", CỐ Ý PHÂN BIỆT:
      • thiếu `app/sources/scopus.py` (bản sync/skills/* không có `../../tools`)
        hoặc `ENABLE_SCOPUS` chưa bật → trả `[]` NGAY, KHÔNG coi là lỗi (đúng ý
        "bác sĩ chưa bật thì im lặng", giống mọi cờ enable_* khác).
      • thiếu `SCOPUS_API_KEY` dù đã bật cờ → `ScopusClient.search()` tự ném
        RuntimeError rõ ràng (thiết kế fail-closed sẵn có) — hàm này CỐ Ý
        KHÔNG nuốt lỗi đó, để `run_scan()` ghi vào `ghi_chu_lan` cho bác sĩ
        thấy đây là CẤU HÌNH THIẾU, khác với "không có gì mới".
      • lỗi mạng/Cloudflare khi ĐÃ có key → `ScopusClient.search()` tự bắt và
        trả `[]` (đã kiểm ở tầng nghiên cứu) — lane này chỉ truyền nguyên vẹn,
        không thêm một lớp nuốt lỗi khác đè lên.

    `client_factory` CÓ SẴN (test truyền vào) bỏ qua toàn bộ 3 bước dò môi
    trường thật ở trên (đường dẫn/cờ bật/import) — ý định của việc truyền một
    factory là "giả lập Scopus sẵn sàng", không phải kiểm lại cổng đó.
    """
    if client_factory is None:
        mea = _tim_medical_ebm_automation()
        if mea is None or not (mea / "app" / "sources" / "scopus.py").exists():
            return []
        import sys as _sys  # noqa: PLC0415
        if str(mea) not in _sys.path:
            _sys.path.insert(0, str(mea))
        from app.config import settings  # noqa: PLC0415
        if not settings.enable_scopus:
            return []
        from app.sources.scopus import ScopusClient  # noqa: PLC0415
        client_factory = ScopusClient
    client = client_factory()
    client.use_mock = False
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    records = client.search(topic, max_results=min(retmax, 25), since_date=since)
    ra: list[Candidate] = []
    for rec in records:
        url = rec.url or (f"https://doi.org/{rec.doi}" if rec.doi else "")
        ra.append(Candidate(
            pmid=rec.pmid or "",
            publication_date=rec.publication_date or "",
            title=(rec.title or "")[:300],
            url=url,
            source="Scopus (Elsevier)",
            journal_or_organization=rec.journal_or_organization or "",
            tang="scopus_bo_sung",
            rut_bai="chua_kiem",  # gan_do_tin_cay() sẽ ghi đè nếu có pmid thật
        ))
    return ra


def search_core_lane(topic: str, days: int, retmax: int,
                     *, client_factory: Callable[[], object] | None = None,
                     ) -> list[Candidate]:
    """LÀN CORE (core.ac.uk) — thêm 22/09/2026, cùng khuôn `search_scopus_lane()`.

    CORE là nguồn PHỦ RỘNG (>452 triệu bản ghi, luận văn/báo cáo xám mà PubMed/
    Scopus không phủ) — bác sĩ đã bật `ENABLE_CORE=true` + `CORE_API_KEY` thật
    22/09/2026, kiểm sống qua `run.py test-live core` (count=5, is_mock:false).
    Trước bản vá này, CORE đã bật ở tầng nghiên cứu thủ công (research/manager.py,
    run.py test-live) nhưng KHÔNG có lane ở đây — 43 chủ đề theo dõi hằng tuần
    sẽ không tự nhận ứng viên từ CORE, chỉ dùng được khi tra cứu MỘT câu hỏi cụ
    thể. TÁI DÙNG `app/sources/core_api.py::CoreClient`, KHÔNG viết lại logic.

    Đặt TRƯỚC `gan_do_tin_cay()` (cùng vị trí Scopus, khác preprint/trials):
    `CoreClient` đôi khi trả `pmid` thật (trường `pubmedId` của core.ac.uk), nên
    phải được kiểm rút bài như ứng viên PubMed chính — không được mãi mãi
    "chua_kiem" như preprint/trials (cấu trúc của chúng không có pmid để tra).

    KHÁC Scopus ở một điểm: `CoreClient` KHÔNG raise khi thiếu key (CORE chạy
    được không khoá, ở nhịp thấp hơn) — nên hàm này không cần phân biệt "thiếu
    key" khỏi "lỗi mạng", cả hai đều đã được `CoreClient.search()` tự nuốt và
    trả `[]` (đã kiểm ở tầng nghiên cứu, 15 test `tests/test_core_api.py`)."""
    if client_factory is None:
        mea = _tim_medical_ebm_automation()
        if mea is None or not (mea / "app" / "sources" / "core_api.py").exists():
            return []
        import sys as _sys  # noqa: PLC0415
        if str(mea) not in _sys.path:
            _sys.path.insert(0, str(mea))
        from app.config import settings  # noqa: PLC0415
        if not settings.enable_core:
            return []
        from app.sources.core_api import CoreClient  # noqa: PLC0415
        client_factory = CoreClient
    client = client_factory()
    client.use_mock = False
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    records = client.search(topic, max_results=min(retmax, 20), since_date=since)
    ra: list[Candidate] = []
    for rec in records:
        url = rec.url or (f"https://doi.org/{rec.doi}" if rec.doi else "")
        ra.append(Candidate(
            pmid=rec.pmid or "",
            publication_date=rec.publication_date or "",
            title=(rec.title or "")[:300],
            url=url,
            source="CORE (core.ac.uk)",
            journal_or_organization=rec.journal_or_organization or "",
            tang="core_bo_sung",
            rut_bai="chua_kiem",  # gan_do_tin_cay() sẽ ghi đè nếu có pmid thật
        ))
    return ra


@dataclass
class _BanGhiToiThieu:
    """Thay thế NHẸ cho `app.sources.base.RawRecord` khi `medical-ebm-automation` không tới
    được (bản sao trần trên CI, hoặc caller/test tiêm sẵn `bo_sung_fn` để cô lập môi trường
    khỏi việc phải dò/`sys.path`). CHỈ dùng để DỰNG đầu vào cho `bo_sung_du_phong_lane()`
    khi `bo_sung_fn` đã được tiêm — KHÔNG dùng ở đường tự dò môi trường thật (ở đó vẫn bắt
    buộc RawRecord thật). Chỉ giữ đúng các trường hàm đó thực sự đọc/ghi."""
    source: str = ""
    title: str = ""
    journal_or_organization: str | None = None
    publication_date: str | None = None
    doi: str | None = None
    pmid: str | None = None
    url: str | None = None
    ingest_query: str | None = None


# Loại lỗi của engine mang nghĩa «hết hạn mức» — nguồn không (còn) tính tiền cho lời gọi đó và thử lại không giúp gì.
_DU_PHONG_HET_HAN_MUC = frozenset({"het_ngan_sach", "het_quota"})
# Một lần gọi LỖI được thử lại tối đa chừng này lần trong cùng tuần ISO (không biết lời gọi lỗi đã bị tính tiền chưa).
TRAN_THU_LAI_DU_PHONG = 1


class KetQuaDuPhong(tuple):
    """Kết quả làn dự phòng: vẫn là cặp `(ứng viên, ghi chú)` như trước, thêm `.so_goi` — số lời gọi nguồn TÍNH PHÍ
    đã thực hiện (đọc từ tóm tắt của engine). `0` = chắc chắn KHÔNG gọi (engine vắng · cờ tắt · engine thấy đã đủ
    chứng cứ · hết ngân sách); `None` = không rõ (hàm tiêm sẵn không báo) ⇒ nơi gọi coi như ĐÃ gọi. 30/09/2026: trước
    đó «được chọn leo thang» bị đồng nhất với «đã gọi nguồn» — máy không có engine vẫn tiêu suất tuần và mốc xoay vòng."""
    so_goi: int | None
    canh_bao: str   # lỗi MỘT PHẦN (một tầng hỏng nhưng vẫn có bài) — ghi chú cho chủ đề, không phải «lần gọi lỗi»

    def __new__(cls, ung_vien: list, ghi_chu: str, so_goi: int | None = None, canh_bao: str = "") -> "KetQuaDuPhong":
        ket_qua = super().__new__(cls, (ung_vien, ghi_chu))
        ket_qua.so_goi = so_goi
        ket_qua.canh_bao = canh_bao
        return ket_qua


def bo_sung_du_phong_lane(topic: str, unique_hien_co: Sequence[Candidate], retmax: int,
                          *, days: int | None = None,
                          bo_sung_fn: Callable[..., tuple] | None = None,
                          ) -> tuple[list[Candidate], str]:
    """BẬC THANG DỰ PHÒNG (Consensus → SerpApi Scholar) cho vòng quét tuần —
    thêm 22/09/2026, TÁI DÙNG `app/services/fallback_ladder.py::bo_sung_neu_thieu()`
    NGUYÊN VẸN (không viết lại cổng đủ-chứng-cứ/xác minh Crossref-PubMed/hạn mức).

    CỐ Ý KHÁC Scopus/CORE — KHÔNG phải một lane độc lập chạy vô điều kiện cho cả
    43 chủ đề. Consensus (Free 10 lượt/tháng) và SerpApi Scholar (Free 200
    lượt/tháng, khai 250 nhưng chừa biên) sẽ CẠN HẠN MỨC ngay trong MỘT lượt
    quét nếu gọi vô điều kiện cho từng chủ đề. `bo_sung_neu_thieu()` tự chấm cổng
    "đã đủ chứng cứ đáng tin chưa" (đọc `unique_hien_co` — mọi ứng viên PubMed/
    Europe PMC/Crossref/OpenAlex/Scopus/CORE đã tìm được cho chủ đề NÀY) và CHỈ
    gọi ra bậc thang khi thiếu — đúng nguyên tắc bác sĩ đã chốt 20/09/2026 "chỉ
    khi các nguồn khác chưa đủ chứng cứ đáng tin cậy mới xác minh và tìm thêm".

    Trả `([], "")` khi: `medical-ebm-automation` không tới được · cờ dự phòng
    tắt (`du_phong_dang_bat()` False) · cổng đủ-chứng-cứ đóng cho chủ đề này.
    Không raise cho các trường hợp trên — CHỈ raise khi lỗi thật ngoài dự kiến
    (import hỏng, lỗi lập trình), để `run_scan()` ghi vào `lan_phu_loi`.

    VÁ 22/09/2026 vòng 1 (bắt bằng kiểm đột biến — không phải suy đoán): bản đầu chỉ
    nối `mea` vào `sys.path` BÊN TRONG nhánh `if bo_sung_fn is None:`, nhưng
    `from app.sources.base import RawRecord` ở CUỐI hàm chạy VÔ ĐIỀU KIỆN — khi
    test/caller tiêm sẵn `bo_sung_fn` (bỏ qua nhánh dò môi trường, đúng ý định
    của tham số này — xem docstring `search_scopus_lane`), `sys.path` không hề
    được nối, và `import app...` ném `ModuleNotFoundError`.

    VÁ 22/09/2026 vòng 2 (bắt bởi CI thật trên bản sao TRẦN — PR #21, 4 job kiem-tinh đỏ):
    vòng 1 sửa quá tay — thêm `if mea is None: return [], ""` NGAY ĐẦU HÀM, khiến khi
    `medical-ebm-automation` không tồn tại (đúng CI của REPO GỐC — bare checkout, không có
    thư mục anh em đó) thì HÀM TRẢ VỀ RỖNG NGAY LẬP TỨC dù `bo_sung_fn` đã được tiêm sẵn —
    lại đúng cùng một lớp lỗi vòng 1 vừa vá (tham số tiêm sẵn không còn tác dụng bỏ qua môi
    trường). Nay tách hẳn: `RawRecord` chỉ BẮT BUỘC là lớp thật khi TỰ DÒ (`bo_sung_fn is
    None`, cần gọi `bo_sung_neu_thieu()` thật — hàm đó có thể trông cậy vào các trường/khả
    năng khác của RawRecord thật ngoài truy cập thuộc tính đơn giản). Khi CALLER đã tiêm
    `bo_sung_fn` (test hoặc caller khác), dùng `_BanGhiToiThieu` — lớp thay thế NHẸ, không
    cần `medical-ebm-automation` — vì `bo_sung_fn` khi đó là "hộp đen" do caller kiểm soát,
    chỉ cần đối tượng có ĐÚNG thuộc tính (Python duck-typing; đã soát `fallback_ladder.py`/
    `fallback_verification.py` không có `isinstance(rec, RawRecord)` nào chặn việc này).
    """
    mea = _tim_medical_ebm_automation()
    RawRecord = None
    if mea is not None and (mea / "app" / "sources" / "base.py").exists():
        import sys as _sys  # noqa: PLC0415
        if str(mea) not in _sys.path:
            _sys.path.insert(0, str(mea))
        from app.sources.base import RawRecord as _RawRecord_that  # noqa: PLC0415
        RawRecord = _RawRecord_that
    if bo_sung_fn is None:
        # Đường TỰ DÒ MÔI TRƯỜNG — bắt buộc cả mea LẪN RawRecord thật, không có đường lùi.
        if mea is None or RawRecord is None or not (mea / "app" / "services" / "fallback_ladder.py").exists():
            return KetQuaDuPhong([], "", 0)
        from app.services.fallback_ladder import bo_sung_neu_thieu, du_phong_dang_bat  # noqa: PLC0415
        if not du_phong_dang_bat():
            return KetQuaDuPhong([], "", 0)
        bo_sung_fn = bo_sung_neu_thieu
    if RawRecord is None:
        RawRecord = _BanGhiToiThieu
    ban_ghi_hien_co = [RawRecord(
        source=c.source or "surveillance", title=c.title, journal_or_organization=c.journal_or_organization,
        publication_date=c.publication_date, pmid=c.pmid or None, url=c.url, ingest_query=topic,
    ) for c in unique_hien_co]
    # Mốc ngày NHƯ các làn Scopus/CORE (hôm nay − `days`, UTC) — vá 27/09/2026: trước đây không truyền ⇒ Consensus/
    # SerpApi tìm MỌI năm ⇒ vòng quét TUẦN nhận lại bài cũ «liên quan nhất mọi thời» mỗi tuần, tốn hạn mức cho bài
    # không mới. Hai nguồn chỉ lọc theo NĂM (`year_min`/`as_ylo`) nên các tuần trong cùng năm vẫn chồng lấp.
    kw_ngay: dict[str, str] = {}
    if days is not None:
        kw_ngay["since_date"] = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    extra, tom_tat = bo_sung_fn(topic, None, ban_ghi_hien_co, max_results=min(retmax, 5), **kw_ngay)
    ra: list[Candidate] = []
    for rec in extra:
        url = rec.url or (f"https://doi.org/{rec.doi}" if rec.doi else "")
        ra.append(Candidate(
            pmid=rec.pmid or "",
            publication_date=rec.publication_date or "",
            title=(rec.title or "")[:300],
            url=url,
            source=f"Dự phòng: {rec.source}",
            journal_or_organization=rec.journal_or_organization or "",
            tang="du_phong_bac_thang",
            rut_bai="chua_kiem",
        ))
    ghi_chu = "" if not tom_tat.get("loi_noi_bo") else f"bậc thang dự phòng lỗi nội bộ: {tom_tat['loi_noi_bo']}"
    # Đọc tóm tắt TỪNG TẦNG của engine (`tang[<tên>]`: da_goi · so_loi · loi_cuoi · loi_chot) — 30/09/2026. Trước đó chỉ
    # `loi_noi_bo` mới thành ghi chú, nên lỗi của CHÍNH NGUỒN (timeout · 5xx · 401 khoá sai) trôi qua im lặng: chủ đề
    # bị coi là đã tra xong với 0 kết quả. «Hết hạn mức» (het_quota/het_ngan_sach) thì KHÔNG phải lỗi cần thử lại và
    # KHÔNG phải lời gọi tính tiền (engine vẫn đếm `da_goi` cho `het_quota` do cờ, dù không gửi request) ⇒ trừ ra.
    # Engine báo không hoạt động (`active` False: mock/không tầng nào bật) ⇒ 0 lời gọi; không có thông tin ⇒ None.
    tang = tom_tat.get("tang") if isinstance(tom_tat, dict) else None
    canh_bao = ""
    if isinstance(tang, dict) and tang:
        so_goi: int | None = 0
        tang_loi: list[str] = []
        for ten, t in tang.items():
            if not isinstance(t, dict):
                continue
            goi, loi = int(t.get("da_goi") or 0), int(t.get("so_loi") or 0)
            loai = str(t.get("loi_cuoi") or t.get("loi_chot") or "")
            if loi and loai in _DU_PHONG_HET_HAN_MUC:
                goi = max(0, goi - loi)
            elif loi:
                tang_loi.append(f"{ten}={loai or 'khac'}")
            so_goi += goi
        if tang_loi and not ghi_chu:
            cau = "nguồn dự phòng lỗi: " + "; ".join(tang_loi)
            if ra:
                canh_bao = f"bậc thang dự phòng: {cau} (tầng khác vẫn trả bài)"
            else:
                ghi_chu = f"bậc thang dự phòng: {cau}"
    else:
        so_goi = 0 if isinstance(tom_tat, dict) and tom_tat.get("active") is False else None
    return KetQuaDuPhong(ra, ghi_chu, so_goi, canh_bao)


# ── Xếp hạng «mạnh nhất» (phương án B, 24/09/2026) ─────────────────────────────────────────────────────────
# Loại xuất bản THẬT của PubMed → điểm độ mạnh chứng cứ; bài mang nhiều loại lấy điểm cao nhất.
_DIEM_LOAI_XUAT_BAN = {
    "practice guideline": 5, "guideline": 5, "consensus statement": 5,
    "consensus development conference, nih": 5,
    "systematic review": 4, "meta-analysis": 4, "network meta-analysis": 4,
    "randomized controlled trial": 3, "pragmatic clinical trial": 3, "equivalence trial": 3,
    "clinical trial, phase iii": 3,
    "clinical trial": 2, "controlled clinical trial": 2, "clinical trial, phase ii": 2,
    "multicenter study": 2, "observational study": 2, "comparative study": 2,
}
# Không phải chứng cứ để trình (thông báo rút bài / đính chính / bài đã bị rút) ⇒ điểm 0, xếp cuối.
_LOAI_KHONG_PHAI_CHUNG_CU = {"retracted publication", "retraction of publication",
                             "published erratum", "expression of concern"}
# CHỈ dùng khi bài CHƯA được gán loại (mới vào PubMed — MEDLINE gán loại sau vài tuần): suy từ TIÊU ĐỀ, và
# luôn xếp SAU bài cùng điểm mà có loại thật (xem khoa_manh_nhat). Tiêu đề không phải bằng chứng thiết kế.
_TIEU_DE_MANH = (
    (re.compile(r"\b(guidelines?|consensus|recommendations?)\b", re.I), 5),
    (re.compile(r"\b(systematic review|meta-?analys[ie]s|umbrella review)\b", re.I), 4),
    (re.compile(r"\brandomi[sz]ed\b", re.I), 3),
)


def diem_manh(c: Candidate) -> tuple[int, bool]:
    """(điểm độ mạnh 0–5, điểm có dựa trên loại xuất bản THẬT không)."""
    loai = [p.strip().lower() for p in c.pubtype if p and p.strip().lower() != "journal article"]
    if any(p in _LOAI_KHONG_PHAI_CHUNG_CU for p in loai):
        return 0, True
    if loai:
        return max(_DIEM_LOAI_XUAT_BAN.get(p, 1) for p in loai), True
    for mau, diem in _TIEU_DE_MANH:
        if mau.search(c.title or ""):
            return diem, False
    return 1, False


def khoa_manh_nhat(thu_tu: int, c: Candidate) -> tuple[int, int, int, int]:
    """Khoá sắp xếp «mạnh nhất trước»: điểm loại thiết kế → loại THẬT trước suy-từ-tiêu-đề → có nguồn thẩm
    quyền → thứ tự esearch (sort theo ngày ⇒ bài mới hơn đứng trước khi mọi thứ khác bằng nhau)."""
    diem, that = diem_manh(c)
    return (-diem, 0 if that else 1, 0 if c.authority_source else 1, thu_tu)


def chon_manh_nhat(ung_vien: Sequence[Candidate], so_trinh: int, trong_kho: set[str]
                   ) -> tuple[list[Candidate], list[Candidate], int]:
    """(được trình — mạnh nhất trước · đã quét không trình · số bài đã có trong kho bị bỏ qua).
    Bài đã có trong kho không chiếm chỗ trình: bác sĩ đã đọc nó rồi."""
    moi = [(i, c) for i, c in enumerate(ung_vien) if c.pmid not in trong_kho]
    da_co = len(ung_vien) - len(moi)
    moi.sort(key=lambda cap: khoa_manh_nhat(*cap))
    return [c for _, c in moi[:so_trinh]], [c for _, c in moi[so_trinh:]], da_co


def _ban_ghi_khong_trinh(c: Candidate, tang: str) -> dict:
    diem, that = diem_manh(c)
    return {"pmid": c.pmid, "tang": tang, "diem": diem,
            "diem_theo": "loai_xuat_ban" if that else "tieu_de",
            "pubtype": list(c.pubtype), "title": (c.title or "")[:200],
            "ngay": c.publication_date, "tap_chi": c.journal_or_organization}


# ── Cổng TRƯỚC khi leo thang dự phòng (vá 27/09/2026) ───────────────────────────────────────────────────────
# Ngưỡng bài MẠNH (loại xuất bản THẬT, điểm ≥ 3: guideline/tổng quan/gộp/RCT) để coi chủ đề đã đủ chứng cứ —
# cùng ngưỡng mặc định FALLBACK_MIN_TRUSTED (3) của engine.
NGUONG_BAI_MANH_KHONG_LEO_THANG = 3
_KY_TU_KHONG_ASCII = re.compile(r"[^\x00-\x7f]")
# XOAY VÒNG (27/09/2026; tính theo TUẦN ISO từ 29/09): mỗi tuần chỉ tối đa K chủ đề được leo thang dự phòng tính phí, chủ đề lâu chưa
# được xét đi trước. Có truy vấn tiếng Anh cho cả watchlist mà leo thang hết trong MỘT lượt thì trần Consensus
# (5/lượt · 10/tháng) cạn ngay tuần đầu và mọi chủ đề sau chỉ nhận lỗi «hết ngân sách». K=2/tuần ≈ 8–9 lượt/tháng.
TRAN_LEO_THANG_DU_PHONG_MAC_DINH = 2


def _co_nen_leo_thang_du_phong(row: dict, unique: Sequence[Candidate],
                               suy_giam: Sequence[str]) -> tuple[str, str]:
    """(khoá lý do KHÔNG leo thang — rỗng nếu nên leo thang, truy vấn cho bậc thang dự phòng).

    VÌ SAO CÓ (đo 27/09/2026, trước lượt quét tuần ĐẦU TIÊN có làn dự phòng — thêm 22/09):
      • cổng đủ-chứng-cứ của engine chấm lại ứng viên bằng `score_item`, nhưng bản ghi scanner chỉ mang tiêu đề ·
        tạp chí · ngày · PMID · URL (mất loại xuất bản) ⇒ 59/59 ứng viên thật của «hypertension guideline» ra
        tier C, điểm 0–6 (cần ≥ 60) ⇒ cổng LUÔN «thiếu» ⇒ MỌI chủ đề đều leo thang Consensus (10 lượt/tháng) +
        SerpApi (trả phí);
      • leo thang cả khi NCBI đang lỗi — trái nguyên tắc «nguồn lõi sập ⇒ chưa kết luận, không leo thang»;
      • truy vấn gửi đi là TÊN chủ đề tiếng Việt («Đái tháo đường type 2 — điều trị») cho nguồn tiếng Anh.
    Nay KHÔNG leo thang khi: (1) chủ đề suy giảm vì NCBI lỗi; (2) đã có ≥ NGUONG bài mạnh theo loại xuất bản
    thật; (3) không có truy vấn tiếng Anh — `truy_van_du_phong` trong watchlist, hoặc tên chủ đề thuần ASCII.
    """
    if suy_giam:
        return "ncbi_loi", ""
    so_manh = 0
    for c in unique:
        diem, loai_that = diem_manh(c)
        if loai_that and diem >= 3:
            so_manh += 1
    if so_manh >= NGUONG_BAI_MANH_KHONG_LEO_THANG:
        return "du_bai_manh", ""
    truy_van = str(row.get("truy_van_du_phong") or "").strip()
    if not truy_van:
        ten = str(row.get("topic") or "").strip()
        if ten and not _KY_TU_KHONG_ASCII.search(ten):
            truy_van = ten
    if not truy_van:
        return "chua_co_truy_van_tieng_anh", ""
    return "", truy_van


def run_scan(
    topics: Iterable[dict[str, str]],
    *,
    days: int,
    max_results: int,
    cursor: dict | None = None,
    search_fn: Callable[[str, int, int], list[str]] = search,
    summarize_fn: Callable[[Sequence[str]], list[Candidate]] = summarize,
    tran_leo_thang_du_phong: int | None = None,
    trang_thai_du_phong: dict | None = None,
    luu_so_du_phong: Callable[[dict], None] | None = None,
    du_phong_tat_vi: str = "",
) -> dict:
    """Chạy từng chủ đề độc lập; lỗi một chủ đề không bị nuốt và làm run PARTIAL.

    `tran_leo_thang_du_phong` (27/09/2026): tối đa bao nhiêu chủ đề được leo thang bậc thang dự phòng TÍNH PHÍ — None =
    không trần; có sổ thì là trần của cả TUẦN ISO (trừ số chủ đề sổ ghi đã leo thang trong tuần này, 29/09/2026). `trang_thai_du_phong` (sổ `doc_trang_thai_du_phong()`, SỬA TẠI CHỖ): có sổ thì xoay
    vòng theo ngày leo thang gần nhất và bỏ bài dự phòng đã trình ở lượt trước. `main()` bật cả hai; mặc định None giữ
    nguyên hành vi cũ cho mọi nơi gọi khác.
    """
    started = datetime.now(timezone.utc)
    topic_results: list[TopicResult] = []
    all_pmids: set[str] = set()
    du_phong_khong_leo: dict[str, int] = {}   # lý do KHÔNG leo thang dự phòng → số chủ đề (xem _co_nen_leo_thang_du_phong)
    cho_du_phong: list[tuple[int, str]] = []  # (chỉ số TopicResult, truy vấn tiếng Anh) — leo thang SAU vòng lặp
    _NCBI_CHAN["bi_chan"] = False   # mỗi lượt quét bắt đầu lại từ «NCBI chưa bị chặn»
    try:
        trong_kho = _pmid_da_co_trong_kho()   # đọc sổ cục bộ MỘT lần cho cả lượt (phương án B)
    except Exception:  # noqa: BLE001 — không đọc được sổ thì không loại bài nào (chỉ tốn chỗ trình)
        trong_kho = set()
    for row in topics:
        # Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #5): chụp all_pmids TRƯỚC khi xử lý
        # chủ đề này. Nếu chủ đề hỏng GIỮA CHỪNG (vd tầng 1 đã thêm PMID vào all_pmids rồi tầng 2
        # mới raise), PMID đó nằm "ma" trong all_pmids — chủ đề đang xử lý bị bỏ (candidates=[]) mà
        # PMID vẫn coi như "đã thấy" nên MỘT CHỦ ĐỀ KHÁC chia sẻ PMID đó (chạy sau) sẽ bị dedup mất
        # nó, dù chưa hề xuất hiện trong bất kỳ báo cáo nào. Hỏng ⇒ phục hồi đúng trạng thái trước đó.
        _pmid_truoc_luot = set(all_pmids)
        try:
            unique: list[Candidate] = []
            suy_giam: list[str] = []
            ghi_chu_tang: list[str] = []    # phương án B: «quét N · trình 6 mạnh nhất» + vượt trần (chỉ ghi chú)
            khong_trinh: list[dict] = []    # ứng viên đã quét nhưng không trình — ghi lại, không bỏ im lặng
            # Khử trùng GIỮA CÁC TẦNG của chủ đề này, gồm cả bài không trình. KHÔNG đưa bài không trình vào
            # all_pmids (dùng chung mọi chủ đề): bài xếp thấp ở chủ đề này có thể đứng đầu ở chủ đề khác.
            da_thay_chu_de: set[str] = set()
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
                        # Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #11): dùng UTC nhất
                        # quán với biên cửa sổ thật sự gửi cho NCBI/Europe PMC (search()/
                        # search_europe_pmc() đều tính `since`/`today` bằng
                        # datetime.now(timezone.utc)) — trước đây mốc "hôm nay" ở ĐÂY dùng
                        # date.today() theo GIỜ MÁY, lệch 1 ngày với UTC trong khoảng 00:00-07:00
                        # giờ Việt Nam (UTC+7), làm `mindate` gửi đi có thể chưa khớp đúng cửa sổ
                        # UTC mà chính lượt gọi API đang dùng.
                        tu = max(_dt.date.fromisoformat(cu) - _dt.timedelta(days=3),
                                 datetime.now(timezone.utc).date() - _dt.timedelta(days=days))
                        md = tu.strftime("%Y/%m/%d")
                    except ValueError:
                        md = ""
            for muc_tang in row.get("queries") or [{"tang": "chung", "query": row["query"]}]:
                # Tầng "moi_vao_pubmed" phải đi bằng edat + KHÔNG lọc loại thiết kế —
                # nếu không nó lại rơi vào đúng cái bẫy đang vá. Bộ tìm kiếm giả trong
                # test không nhận tham số phụ, nên lùi êm về chữ ký cũ.
                tang = muc_tang.get("tang", "chung")
                _SUY_GIAM.clear()
                _VUOT_TRAN.clear()
                # Phương án B: LẤY tới trần (một lượt esearch), không chỉ `max_results` bản mới nhất.
                tran_lay = max(max_results, TRAN_LAY_MOI_TANG)
                try:
                    ids = search_fn(muc_tang["query"], days, tran_lay,
                                    datetype=muc_tang.get("datetype", "pdat"),
                                    loc_thiet_ke=muc_tang.get("loc_thiet_ke", True),
                                    mindate=md)
                except TypeError:
                    ids = search_fn(muc_tang["query"], days, tran_lay)
                if _SUY_GIAM:
                    suy_giam.append(f"tầng {tang}: {_SUY_GIAM[-1]}")
                    _SUY_GIAM.clear()
                if _VUOT_TRAN:
                    ghi_chu_tang.append(f"⚠ tầng {tang}: {_VUOT_TRAN[-1]}")
                    _VUOT_TRAN.clear()
                # Tóm tắt THEO LÔ rồi CHỌN MẠNH NHẤT: trình `max_results` bài đầu theo khoa_manh_nhat, phần
                # còn lại ghi vào khong_trinh (không bỏ im lặng). Bài đã có trong kho không chiếm chỗ trình.
                ung_vien_tang: list[Candidate] = []
                for dau in range(0, len(ids), LO_TOM_TAT):
                    ung_vien_tang.extend(summarize_fn(ids[dau:dau + LO_TOM_TAT]))
                ung_vien_tang = [c for c in ung_vien_tang
                                 if c.pmid not in all_pmids and c.pmid not in da_thay_chu_de]
                da_thay_chu_de.update(c.pmid for c in ung_vien_tang)
                chon, bo, da_co = chon_manh_nhat(ung_vien_tang, max_results, trong_kho)
                for candidate in chon:
                    all_pmids.add(candidate.pmid)
                    unique.append(replace(candidate, tang=muc_tang["tang"]))
                khong_trinh.extend(_ban_ghi_khong_trinh(c, tang) for c in bo)
                if bo:
                    ghi_chu_tang.append(
                        f"tầng {tang}: quét {len(ung_vien_tang)} · trình {len(chon)} mạnh nhất · "
                        f"{len(bo)} ghi «đã quét, không trình»"
                        + (f" · {da_co} đã có trong kho" if da_co else ""))
                # Suy giảm ở KHÂU TÓM TẮT (esummary lỗi → Europe PMC, hoặc PMID không có bản ghi) cũng phải làm chủ đề
                # PASS_DEGRADED — bản trước chỉ đọc _SUY_GIAM sau search() nên khâu này im lặng mất ứng viên.
                if _SUY_GIAM:
                    suy_giam.append(f"tầng {muc_tang.get('tang', 'chung')}: {_SUY_GIAM[-1]}")
                    _SUY_GIAM.clear()
            # LÀN SCOPUS (Elsevier) — thêm 13/09/2026, bác sĩ yêu cầu nối vào tầng
            # giám sát lâm sàng sau khi đã tích hợp bên nghiên cứu. CHẠY TRƯỚC
            # gan_do_tin_cay() — khác preprint/trials ở dưới — vì ứng viên Scopus
            # THƯỜNG CÓ pmid thật (Scopus phần lớn trùng chỉ mục PubMed cho y văn
            # lâm sàng), nên phải được kiểm rút bài giống ứng viên PubMed chính,
            # không được mãi mãi "chua_kiem" như preprint/trials (cấu trúc không
            # có pmid để tra). FAIL-SOFT: thiếu key/thư viện/mạng lỗi đều không
            # được kéo cả chủ đề FAIL.
            ghi_chu_lan: list[str] = []
            lan_phu_loi: list[str] = []  # TÊN làn hỏng — trường máy đọc riêng (review:thu-nhan #10)
            try:
                for candidate in search_scopus_lane(row["topic"], days, max_results):
                    khoa_c = candidate.pmid or candidate.url
                    if khoa_c in all_pmids:
                        continue
                    all_pmids.add(khoa_c)
                    unique.append(candidate)
            except Exception as exc:  # noqa: BLE001 — làn phụ, ghi chú minh bạch
                ghi_chu_lan.append(f"làn scopus lỗi: {type(exc).__name__}")
                lan_phu_loi.append("scopus")
            # LÀN CORE (core.ac.uk) — thêm 22/09/2026, CÙNG vị trí Scopus (trước
            # gan_do_tin_cay) vì CoreClient đôi khi trả pmid thật (trường
            # 'pubmedId'). Xem docstring search_core_lane() cho lý do đầy đủ.
            try:
                for candidate in search_core_lane(row["topic"], days, max_results):
                    khoa_c = candidate.pmid or candidate.url
                    if khoa_c in all_pmids:
                        continue
                    all_pmids.add(khoa_c)
                    unique.append(candidate)
            except Exception as exc:  # noqa: BLE001 — làn phụ, ghi chú minh bạch
                ghi_chu_lan.append(f"làn core lỗi: {type(exc).__name__}")
                lan_phu_loi.append("core")
            unique = gan_do_tin_cay(unique)
            # HAI LÀN (nâng cấp C, 15/08/2026) — chạy SAU gan_do_tin_cay vì tự
            # khai nhãn riêng (preprint không có PMID để tra rút bài; NCT
            # không phải y văn). FAIL-SOFT TỪNG LÀN: làn phụ hỏng không được
            # kéo cả chủ đề FAIL — mất tín hiệu sớm không tệ bằng mất cả lượt
            # quét chính.
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
                    lan_phu_loi.append(ten_lan)
            # BẬC THANG DỰ PHÒNG (Consensus → SerpApi Scholar) — thêm 22/09/2026. CHẠY SAU
            # mọi lane chính (Scopus/CORE/preprint/trials): cổng đủ-chứng-cứ trong
            # bo_sung_du_phong_lane() cần `unique` ĐẦY ĐỦ nhất để chấm đúng "chủ đề này còn
            # thiếu chứng cứ đáng tin không" — chấm sớm hơn sẽ thấy thiếu OAN và gọi tốn hạn
            # mức Free (Consensus 10/tháng · SerpApi 200/tháng) một cách không cần thiết.
            # Cổng TRƯỚC khi leo thang (vá 27/09/2026): NCBI lỗi · đã đủ bài mạnh · thiếu truy vấn tiếng Anh ⇒ không gọi.
            # Chủ đề ĐỦ điều kiện chưa leo thang ngay: xếp hàng, leo thang SAU vòng lặp để xoay vòng trên toàn lượt.
            ly_do_khong_leo, truy_van_du_phong = _co_nen_leo_thang_du_phong(row, unique, suy_giam)
            if ly_do_khong_leo:
                du_phong_khong_leo[ly_do_khong_leo] = du_phong_khong_leo.get(ly_do_khong_leo, 0) + 1
                if ly_do_khong_leo == "ncbi_loi":
                    ghi_chu_lan.append("bậc thang dự phòng: KHÔNG leo thang — NCBI lỗi ở chủ đề này, chưa kết luận"
                                       " được đủ/thiếu (không đốt hạn mức Consensus/SerpApi)")
            # PASS_DEGRADED: có truy vấn rơi xuống dự phòng ⇒ kết quả có thể THIẾU. Con trỏ KHÔNG tiến để
            # lượt sau quét lại đúng cửa sổ này — trước đây vẫn tiến ⇒ cửa sổ 24/08–07/09 mất vĩnh viễn.
            trang_thai = "PASS_DEGRADED" if suy_giam else "PASS"
            ghi_chu = "; ".join(ghi_chu_tang + ghi_chu_lan)
            if suy_giam:
                ghi_chu = ("SUY GIẢM: " + " | ".join(suy_giam)
                           + (f" || {ghi_chu}" if ghi_chu else ""))
            topic_results.append(TopicResult(
                row["topic"], row["query"], trang_thai, unique, ghi_chu, suy_giam, lan_phu_loi,
                khong_trinh))
            if not ly_do_khong_leo:
                cho_du_phong.append((len(topic_results) - 1, truy_van_du_phong))
            if cursor is not None and trang_thai == "PASS":
                # Vá 22/09/2026 (review:thu-nhan #11): UTC — nhất quán với biên `since`/`today`
                # thật sự gửi tới NCBI/Europe PMC (xem chú thích ở khối tính `md` phía trên); con
                # trỏ này chính là `cu` mà lượt sau dùng để tính lại mindate UTC.
                cursor[row["topic"]] = datetime.now(timezone.utc).date().isoformat()
        except Exception as exc:  # noqa: BLE001 - lỗi được ghi vào audit, không nuốt
            all_pmids &= _pmid_truoc_luot  # gỡ PMID "ma" chủ đề này vừa thêm trước khi hỏng
            topic_results.append(TopicResult(
                row["topic"], row["query"], "FAIL", [],
                f"{exc.__class__.__name__}: {exc}"[:600],
            ))

    # BẬC THANG DỰ PHÒNG (Consensus → SerpApi Scholar), XOAY VÒNG trên toàn lượt — 27/09/2026. Chủ đề đủ điều kiện
    # được xét theo ngày leo thang gần nhất (chưa từng ⇒ trước), hoà thì theo thứ tự watchlist; chỉ `tran` chủ đề
    # đầu được gọi, số còn lại «chờ lượt». Có sổ thì bài dự phòng đã trình ở lượt trước không trình lại.
    # Có sổ thì `tran` là trần của cả TUẦN ISO (29/09/2026): lượt W40 đầu tiên quét HAI lần trong một phiên (lần đầu sập)
    # nên leo thang 4 chủ đề trong một ngày — trần theo lượt để mỗi lần chạy lại đốt thêm hạn mức Consensus (10/tháng).
    # `du_phong_tat_vi` (30/09/2026): `main()` không đọc được sổ ⇒ TẮT cả làn dự phòng lượt này (không leo thang, không
    # trình bù, không đụng sổ) thay vì coi sổ là rỗng rồi ghi đè.
    so = None if du_phong_tat_vi else trang_thai_du_phong
    lan_cuoi = so.setdefault("lan_cuoi_leo_thang", {}) if so is not None else {}
    da_trinh = so.setdefault("da_trinh", {}) if so is not None else {}
    cho_trinh = so.setdefault("cho_trinh", {}) if so is not None else {}
    leo_thang_loi = so.setdefault("leo_thang_loi", {}) if so is not None else {}
    hom_nay_d = datetime.now(timezone.utc).date()
    hom_nay = hom_nay_d.isoformat()

    def _cung_tuan(ngay: object) -> bool:
        try:
            return datetime.strptime(str(ngay)[:10], "%Y-%m-%d").date().isocalendar()[:2] == hom_nay_d.isocalendar()[:2]
        except ValueError:
            return False

    # HAI BẢN CỦA SỔ (30/09/2026). `so` là bản «báo cáo ĐÃ tới nơi» — `main()` chỉ ghi nó sau khi báo cáo được in/ghi
    # xong. Bản «CHƯA tới nơi» (`_luu_som`) được ghi NGAY sau mỗi lời gọi nguồn tính phí: mốc leo thang + dấu lỗi hiện
    # tại (hạn mức đã tiêu, trần tuần phải thấy), «đã trình» như TRƯỚC lượt này, và hàng chờ cũ + bài vừa lấy. Nhờ đó
    # lượt sập ở khâu sau — kể cả bị ngắt GIỮA hai lời gọi — không mất bài đã trả phí: lượt sau trình bù từ hàng chờ.
    da_trinh_truoc = dict(da_trinh)
    cho_trinh_truoc = dict(cho_trinh)
    vua_lay: dict[str, list[dict]] = {}

    def _luu_som() -> None:
        if so is None or luu_so_du_phong is None:
            return
        cho = dict(cho_trinh_truoc)
        for chu_de, bai in vua_lay.items():
            cu = cho.get(chu_de)
            cho[chu_de] = {"ngay": hom_nay,
                           "ung_vien": [u for u in (cu.get("ung_vien") if isinstance(cu, dict) else None) or []
                                        if isinstance(u, dict)] + bai}
        luu_so_du_phong({"lan_cuoi_leo_thang": dict(lan_cuoi), "da_trinh": dict(da_trinh_truoc), "cho_trinh": cho,
                         "leo_thang_loi": dict(leo_thang_loi)})

    # TRÌNH BÙ: bài dự phòng đã lấy ở lượt trước mà báo cáo chưa tới nơi nằm ở `cho_trinh` — đưa vào báo cáo lượt này,
    # KHÔNG gọi lại nguồn tính phí và không tính vào trần tuần (hạn mức đã trừ lúc lấy). Trước đó chúng chỉ trở lại khi
    # chủ đề tới lượt xoay vòng (~17–21 tuần), có thể không bao giờ. `tran == 0` = lượt này KHÔNG đụng làn dự phòng
    # (lượt ĐẾM ra thư mục tạm của `uu_tien_cap_nhat`) ⇒ cũng không trình bù, để nguyên sổ. Chủ đề FAIL không hiện ứng
    # viên trong báo cáo ⇒ giữ bài chờ cho lượt sau. Không phụ thuộc cổng «đủ bài mạnh»: bài đã trả phí thì phải trình.
    trinh_bu: dict[str, int] = {}
    if so is not None and tran_leo_thang_du_phong != 0:
        for i, tr in enumerate(topic_results):
            muc = cho_trinh.get(tr.topic)
            if muc is None or tr.status == "FAIL":
                continue
            so_bu = 0
            for tho in (muc.get("ung_vien") if isinstance(muc, dict) else None) or []:
                candidate = _ung_vien_tu_so(tho)
                khoa_c = (candidate.pmid or candidate.url) if candidate else ""
                if not khoa_c or khoa_c in all_pmids or khoa_c in da_trinh:
                    continue
                all_pmids.add(khoa_c)
                tr.candidates.append(candidate)
                da_trinh[khoa_c] = hom_nay
                so_bu += 1
            del cho_trinh[tr.topic]
            if so_bu:
                trinh_bu[tr.topic] = so_bu
                topic_results[i] = replace(tr, error="; ".join(x for x in (
                    tr.error, f"bậc thang dự phòng: trình bù {so_bu} bài đã lấy ở lượt trước mà báo cáo chưa tới nơi "
                              "(không gọi lại nguồn tính phí)") if x))

    da_dung_tuan = sum(1 for v in lan_cuoi.values() if _cung_tuan(v))
    con_lai = None if tran_leo_thang_du_phong is None else max(0, tran_leo_thang_du_phong - da_dung_tuan)
    # Chủ đề ĐÃ leo thang XONG trong tuần ISO này thì không gọi lại (30/09/2026). Trần tuần đếm số chủ đề KHÁC NHAU,
    # nên chạy lặp lượt một-chủ-đề (`--topic`, A2 của orchestrator, hay chạy lại sau lượt sập khi còn suất) từng gọi
    # nguồn tính phí thêm mỗi lần mà bộ đếm không nhúc nhích — đo: 3 lượt cùng chủ đề = 3 lời gọi, kết quả lần 2–3 bị
    # bỏ vì trùng. «Xong» = lần gần nhất KHÔNG lỗi, hoặc đã lỗi quá số lần thử lại cho phép. Lần lỗi (dấu
    # `leo_thang_loi` {chủ đề: {ngay, so_lan}}) chưa có kết quả nên được thử lại khi còn suất — nhưng chỉ
    # `TRAN_THU_LAI_DU_PHONG` lần: không giới hạn thì 5 lượt cùng lỗi = 5 lời gọi có thể đã bị tính tiền, trong khi
    # bộ đếm tuần vẫn đứng yên. Chỉ áp khi có trần (đường `main()`); gọi thư viện không trần giữ hành vi cũ.
    def _so_lan_loi_tuan_nay(chu_de: str) -> int:
        dau = leo_thang_loi.get(chu_de)
        if not isinstance(dau, dict) or not _cung_tuan(dau.get("ngay")):
            return 0
        try:
            return max(1, int(dau.get("so_lan") or 1))
        except (TypeError, ValueError):
            return 1

    def _xong_tuan_nay(chu_de: str) -> bool:
        return _cung_tuan(lan_cuoi.get(chu_de)) and not 0 < _so_lan_loi_tuan_nay(chu_de) <= TRAN_THU_LAI_DU_PHONG

    da_leo_tuan_nay = ({j for j, (i, _q) in enumerate(cho_du_phong) if _xong_tuan_nay(topic_results[i].topic)}
                       if so is not None and tran_leo_thang_du_phong is not None else set())
    thu_tu = [] if du_phong_tat_vi else sorted(
        (j for j in range(len(cho_du_phong)) if j not in da_leo_tuan_nay),
        key=lambda j: (str(lan_cuoi.get(topic_results[cho_du_phong[j][0]].topic, "")), j))
    da_leo_thang: list[str] = []
    du_phong_loi: list[str] = []
    du_phong_thu_lai: list[str] = []
    bo_trung_xuyen_tuan = 0
    ghi_them_theo: dict[int, list[str]] = {}
    da_xet: set[int] = set()
    so_suat_da_tieu = 0
    # Chọn theo ĐỢT: mỗi đợt lấy số chủ đề đầu hàng xoay vòng bằng số suất còn lại, gọi theo thứ tự watchlist. Chủ đề
    # được chọn mà nguồn KHÔNG được gọi (`so_goi == 0`: engine vắng · cờ tắt · engine thấy đã đủ chứng cứ · hết ngân
    # sách) không tiêu suất, không ghi mốc ⇒ đợt sau trao suất cho chủ đề kế tiếp. Trước đó «được chọn» = «đã tiêu»:
    # máy không có engine vẫn đốt 2 suất/tuần và đẩy chủ đề xuống cuối vòng xoay mà không gọi gì.
    while True:
        con = None if con_lai is None else con_lai - so_suat_da_tieu
        ung_cu = [j for j in thu_tu if j not in da_xet]
        chon = ung_cu if con is None else ung_cu[:max(0, con)]
        if not chon:
            break
        for j in sorted(chon):
            da_xet.add(j)
            i, truy_van = cho_du_phong[j]
            tr = topic_results[i]
            ghi_them = ghi_them_theo.setdefault(j, [])
            try:
                ket_qua = bo_sung_du_phong_lane(truy_van, tr.candidates, max_results, days=days)
                extra, ghi_chu_du_phong = ket_qua
                for candidate in extra:
                    khoa_c = candidate.pmid or candidate.url
                    if khoa_c in all_pmids:
                        continue
                    if so is not None and khoa_c in da_trinh:
                        bo_trung_xuyen_tuan += 1
                        continue
                    all_pmids.add(khoa_c)
                    tr.candidates.append(candidate)
                    if so is not None:
                        da_trinh[khoa_c] = hom_nay
                        vua_lay.setdefault(tr.topic, []).append(asdict(candidate))
                canh_bao_mot_phan = getattr(ket_qua, "canh_bao", "")
                if ghi_chu_du_phong:
                    ghi_them.append(ghi_chu_du_phong)
                    tr.lan_phu_loi.append("du_phong_bac_thang")
                    trang_thai_goi = "loi"
                elif canh_bao_mot_phan:
                    ghi_them.append(canh_bao_mot_phan)
                    tr.lan_phu_loi.append("du_phong_bac_thang")
                    trang_thai_goi = "da_goi"
                elif getattr(ket_qua, "so_goi", None) == 0 and not extra:
                    trang_thai_goi = "khong_goi"
                else:
                    trang_thai_goi = "da_goi"
            except Exception as exc:  # noqa: BLE001 — làn phụ, ghi chú minh bạch
                ghi_them.append(f"làn du_phong_bac_thang lỗi: {type(exc).__name__}")
                tr.lan_phu_loi.append("du_phong_bac_thang")
                trang_thai_goi = "loi"
            if trang_thai_goi == "khong_goi":
                du_phong_khong_leo["nguon_khong_goi"] = du_phong_khong_leo.get("nguon_khong_goi", 0) + 1
                ghi_them.append("bậc thang dự phòng: được chọn nhưng nguồn tính phí KHÔNG được gọi (engine vắng · cờ "
                                "tắt · engine thấy đã đủ chứng cứ · hết ngân sách) — không tính suất tuần")
                continue
            # Lỗi thì KHÔNG biết lời gọi đã tới nguồn chưa ⇒ vẫn tính suất (không đốt thêm ngoài ý muốn), nhưng đánh
            # dấu để lượt sau cùng tuần được thử lại: chưa có kết quả thì không được nói «đã tra».
            so_lan_loi_truoc = _so_lan_loi_tuan_nay(tr.topic)
            if so_lan_loi_truoc:
                du_phong_thu_lai.append(tr.topic)   # thử lại lần gọi lỗi: chủ đề đã được tính suất ở lần trước
            else:
                so_suat_da_tieu += 1
            da_leo_thang.append(tr.topic)
            if trang_thai_goi == "loi":
                du_phong_loi.append(tr.topic)
                if so_lan_loi_truoc >= TRAN_THU_LAI_DU_PHONG:
                    ghi_them.append(f"bậc thang dự phòng: đã lỗi {so_lan_loi_truoc + 1} lần trong tuần này — không thử lại "
                                    "nữa cho tới tuần sau")
            if so is not None:
                lan_cuoi[tr.topic] = hom_nay
                if trang_thai_goi == "loi":
                    leo_thang_loi[tr.topic] = {"ngay": hom_nay, "so_lan": so_lan_loi_truoc + 1}
                else:
                    leo_thang_loi.pop(tr.topic, None)
                _luu_som()
        if con is None:
            break
    for j, (i, _truy_van) in enumerate(cho_du_phong):
        ghi_them = ghi_them_theo.setdefault(j, [])
        if du_phong_tat_vi:
            du_phong_khong_leo["so_khong_doc_duoc"] = du_phong_khong_leo.get("so_khong_doc_duoc", 0) + 1
            ghi_them.append(f"bậc thang dự phòng: TẮT lượt này — {du_phong_tat_vi}")
        elif j in da_leo_tuan_nay and _so_lan_loi_tuan_nay(topic_results[i].topic):
            du_phong_khong_leo["loi_het_luot_thu_lai"] = du_phong_khong_leo.get("loi_het_luot_thu_lai", 0) + 1
            ghi_them.append(f"bậc thang dự phòng: đã lỗi {_so_lan_loi_tuan_nay(topic_results[i].topic)} lần trong tuần "
                            "này — không thử lại nữa cho tới tuần sau (chưa có kết quả)")
        elif j in da_leo_tuan_nay:
            du_phong_khong_leo["da_leo_thang_tuan_nay"] = du_phong_khong_leo.get("da_leo_thang_tuan_nay", 0) + 1
            ghi_them.append("bậc thang dự phòng: chủ đề đã leo thang trong tuần này — không gọi lại nguồn tính phí")
        elif j not in da_xet:
            du_phong_khong_leo["cho_luot_xoay_vong"] = du_phong_khong_leo.get("cho_luot_xoay_vong", 0) + 1
            ghi_them.append(f"bậc thang dự phòng: chờ lượt — mỗi tuần chỉ {tran_leo_thang_du_phong} chủ đề được leo "
                            f"thang (xoay vòng, chủ đề lâu chưa xét đi trước; tuần này đã dùng {da_dung_tuan})")
        if ghi_them:
            tr = topic_results[i]
            topic_results[i] = replace(tr, error="; ".join(x for x in (tr.error, *ghi_them) if x))
    if so is not None:
        # Sổ không phình mãi: quên bài đã trình quá 400 ngày (Consensus/SerpApi lọc theo NĂM — sang năm thứ hai bài
        # cũ không còn quay lại được nữa).
        moc = (datetime.now(timezone.utc) - timedelta(days=400)).date().isoformat()
        for khoa_c in [k for k, v in da_trinh.items() if str(v) < moc]:
            del da_trinh[khoa_c]
        for chu_de in [k for k, v in cho_trinh.items()
                       if isinstance(v, dict) and v.get("ngay") and str(v["ngay"]) < moc]:
            del cho_trinh[chu_de]  # chủ đề đã rời watchlist: bài chờ trình không bao giờ tới lượt
        for chu_de in [k for k in leo_thang_loi if not _so_lan_loi_tuan_nay(k)]:
            del leo_thang_loi[chu_de]  # dấu lỗi chỉ có nghĩa trong tuần nó xảy ra (dấu sai dạng cũng bị dọn)
    # Số chủ đề đã tiêu suất trong tuần SAU lượt này — con số mà lệnh nâng trần phải vượt qua.
    da_dung_tuan_sau_luot = (sum(1 for v in lan_cuoi.values() if _cung_tuan(v)) if so is not None
                             else da_dung_tuan + so_suat_da_tieu)

    success_count = sum(result.status == "PASS" for result in topic_results)
    degraded_count = sum(result.status == "PASS_DEGRADED" for result in topic_results)
    # failed_topics = KHÔNG PHẢI PASS (gồm cả suy giảm) — mọi nơi tiêu thụ cũ đọc failed_topics/status≠PASS
    # đều fail-closed đúng ý; `degraded_topics` tách riêng để người đọc biết đó là suy giảm chứ không phải lỗi.
    failure_count = len(topic_results) - success_count
    if not topic_results or (success_count + degraded_count) == 0:
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
        "degraded_topics": degraded_count,
        "failed_topics": failure_count,
        "candidate_count": len(all_pmids),
        # Số chủ đề KHÔNG leo thang dự phòng theo lý do (ncbi_loi · du_bai_manh · chua_co_truy_van_tieng_anh ·
        # cho_luot_xoay_vong · da_leo_thang_tuan_nay · loi_het_luot_thu_lai · nguon_khong_goi · so_khong_doc_duoc).
        "du_phong_khong_leo_thang": dict(sorted(du_phong_khong_leo.items())),
        # Xoay vòng (27/09/2026): chủ đề đã leo thang lượt này · trần mỗi lượt (None = không trần) · số bài dự phòng
        # bỏ vì đã trình ở lượt trước.
        "du_phong_da_leo_thang": da_leo_thang,     # chủ đề ĐÃ TIÊU một suất tuần (đã gọi nguồn, hoặc gọi mà lỗi)
        "du_phong_loi": du_phong_loi,              # trong số đó: lần gọi LỖI — chưa có kết quả (thử lại có giới hạn)
        "du_phong_thu_lai": du_phong_thu_lai,      # trong số đó: THỬ LẠI lần gọi lỗi của tuần này — không tính thêm suất
        "du_phong_da_dung_tuan_sau_luot": da_dung_tuan_sau_luot,
        "du_phong_tat_vi": du_phong_tat_vi,        # khác rỗng: cả làn dự phòng bị tắt lượt này (sổ không đọc được)
        "du_phong_tran_moi_luot": tran_leo_thang_du_phong,
        "du_phong_da_dung_tuan": da_dung_tuan,   # số chủ đề đã leo thang trong tuần ISO này TRƯỚC lượt này (theo sổ)
        "du_phong_bo_trung_xuyen_tuan": bo_trung_xuyen_tuan,
        # Trình bù (30/09/2026): {chủ đề: số bài} lấy ở lượt trước mà báo cáo chưa tới nơi, nay đưa vào báo cáo này.
        "du_phong_trinh_bu": dict(sorted(trinh_bu.items())),
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
        *([f"- 🟠 **QUÉT SUY GIẢM: {report['degraded_topics']}/{report['topic_count']} chủ đề có truy vấn không "
           f"lấy được đủ (NCBI lỗi/bị chặn phải dùng Europe PMC dự phòng, hoặc thiếu bản tóm tắt — lý do từng "
           f"chủ đề ở dưới) — kết quả có thể THIẾU. KHÔNG được đọc «không có ứng viên» là «không có gì mới». "
           f"Con trỏ chủ đề suy giảm KHÔNG tiến; chạy lại khi nguồn trả lời được.**"]
          if report.get("degraded_topics") else []),
        f"- Chủ đề PASS/FAIL: {report['successful_topics']}/{report['failed_topics']}"
        + (f" (trong đó {report['degraded_topics']} SUY GIẢM — xem dưới)" if report.get("degraded_topics") else ""),
        f"- Ứng viên không trùng: {report['candidate_count']}",
        (f"- Độ trễ phát hiện: trung vị {report['do_tre']['trung_vi_ngay']} ngày "
         f"({report['do_tre']['n_do_duoc']}/{report['do_tre']['n_tong']} đo được; "
         f"{report['do_tre']['qua_14_ngay']} mục quá ngưỡng 14 ngày)"
         if report.get("do_tre") else "- Độ trễ phát hiện: [CẦN BỔ SUNG] (ngày công bố không đủ chi tiết)"),
        *([f"- Bậc thang dự phòng tính phí (Consensus → SerpApi): leo thang {len(report['du_phong_da_leo_thang'])} "
           f"chủ đề ({', '.join(report['du_phong_da_leo_thang'])})"
           + (f" · {report['du_phong_khong_leo_thang']['cho_luot_xoay_vong']} chủ đề chờ lượt (xoay vòng "
              f"{report.get('du_phong_tran_moi_luot')}/tuần)"
              if report.get("du_phong_khong_leo_thang", {}).get("cho_luot_xoay_vong") else "")
           + (f" · bỏ {report['du_phong_bo_trung_xuyen_tuan']} bài đã trình ở lượt trước"
              if report.get("du_phong_bo_trung_xuyen_tuan") else "")]
          if report.get("du_phong_da_leo_thang") else []),
        *([f"- 🟠 **Bậc thang dự phòng TẮT lượt này: {report['du_phong_tat_vi']}** — không leo thang, không trình bù, "
           "KHÔNG ghi sổ (sổ giữ trần tuần và bài đã trả phí; coi nó là rỗng rồi ghi đè là mất). Kiểm "
           "`EBM-Dashboards/.du-phong-trang-thai.json` (OneDrive đã tải về chưa, có bản xung đột không) rồi chạy lại."]
          if report.get("du_phong_tat_vi") else []),
        *([f"- 🟠 Bậc thang dự phòng LỖI ở {len(report['du_phong_loi'])} chủ đề ({', '.join(report['du_phong_loi'])}) "
           f"— chưa có kết quả; suất tuần đã tính, chạy lại trong tuần sẽ thử lại tối đa {TRAN_THU_LAI_DU_PHONG} lần "
           "khi còn suất"]
          if report.get("du_phong_loi") else []),
        *([f"- Bậc thang dự phòng: trình BÙ {sum(report['du_phong_trinh_bu'].values())} bài đã lấy ở lượt trước mà báo "
           f"cáo chưa tới nơi ({', '.join(f'{k}: {v}' for k, v in report['du_phong_trinh_bu'].items())}) — không gọi "
           "lại nguồn tính phí"]
          if report.get("du_phong_trinh_bu") else []),
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
        if result["status"] == "FAIL":
            lines.append(f"- **KHÔNG QUÉT ĐƯỢC:** `{result['error']}`")
            lines.append("- Không được diễn giải là 'không có cập nhật'.")
        else:
            if result["status"] == "PASS_DEGRADED":
                lines.append(f"- 🟠 **SUY GIẢM:** {result['error']} — kết quả dưới đây có thể THIẾU; "
                             "không được đọc «không có ứng viên» là «không có gì mới».")
            elif result.get("error"):
                # Ghi chú (xếp hạng theo tầng «quét N · trình 6 mạnh nhất», vượt trần, làn phụ lỗi) — trước
                # đây chỉ in khi status≠PASS nên MẤT.
                lines.append(f"- ⚪ Ghi chú: `{result['error']}`")
        if result["status"] == "FAIL":
            pass
        elif not result["candidates"]:
            lines.append("- Không tìm thấy ứng viên trong cửa sổ đã quét (xem trạng thái ở trên).")
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
                                                    "thu_nghiem_dang_ky",
                                                    "scopus_bo_sung",
                                                    "core_bo_sung",       # thêm 22/09/2026
                                                    "du_phong_bac_thang")  # thêm 22/09/2026
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


def do_do_tre(report: dict, hom_nay: date | None = None) -> dict | None:
    """ĐO ĐỘ TRỄ (K4) — định nghĩa vận hành của «mới nhất» phải đo được. Chỉ đo khi ngày đủ chi tiết
    (`YYYY Mon DD`); thiếu thì [CẦN BỔ SUNG], không ước lượng. Không ứng viên nào đo được ⇒ `None`.

    Vá 29/09/2026: ngày kiểu int (chỉ có NĂM) ⇒ `int[:11]` ném TypeError làm SẬP cả lượt quét. Nay ép về chuỗi và
    coi mọi dạng không đọc được (số, None, thiếu khoá) là «không đo được». Hàm nhận báo cáo dạng dict (không chỉ từ
    `Candidate`) nên lớp phòng thủ này vẫn cần dù `Candidate` đã tự chuẩn hoá ngày."""
    hom_nay = hom_nay or date.today()
    tre: list[int] = []
    for chu_de in report.get("topics") or []:
        for ung_vien in chu_de.get("candidates") or []:
            try:
                d0 = datetime.strptime(str(ung_vien.get("publication_date") or "")[:11].strip(), "%Y %b %d").date()
            except ValueError:  # sau str() chỉ còn ValueError: ngày thiếu chi tiết/không đúng dạng
                continue
            tre.append((hom_nay - d0).days)
    if not tre:
        return None
    tre.sort()
    return {
        "n_do_duoc": len(tre), "n_tong": report.get("candidate_count"),
        "trung_vi_ngay": tre[len(tre) // 2],
        "qua_14_ngay": sum(1 for x in tre if x > 14),
        "ghi_chu": ("trễ = hôm_nay − ngày công bố; chỉ tính ứng viên có ngày đủ "
                    "chi tiết, phần còn lại [CẦN BỔ SUNG]"),
    }


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
    parser.add_argument("--tran-du-phong", type=int, default=TRAN_LEO_THANG_DU_PHONG_MAC_DINH,
                        help="tối đa bao nhiêu chủ đề được leo thang dự phòng TÍNH PHÍ mỗi TUẦN ISO (xoay vòng, chủ đề lâu "
                             f"chưa xét đi trước; 0 = không leo thang; mặc định {TRAN_LEO_THANG_DU_PHONG_MAC_DINH})")
    args = parser.parse_args(argv)
    if not 0 <= args.tran_du_phong <= 50:
        parser.error("--tran-du-phong phải trong khoảng 0..50")
    if not 1 <= args.days <= 3650:
        parser.error("--days phải trong khoảng 1..3650")
    if not 1 <= args.max <= 100:
        parser.error("--max phải trong khoảng 1..100")
    # Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #8): --since chưa từng được kiểm dạng ngày
    # — một chuỗi lạ (gõ nhầm) vẫn bị ghi thẳng vào con trỏ, làm hỏng mọi phép so sánh từ điển
    # (cu > since) ở các bước sau bằng một giá trị không phải ngày ISO.
    if args.since:
        try:
            import datetime as _dt_check
            _dt_check.date.fromisoformat(args.since)
        except ValueError:
            parser.error(f"--since phải đúng dạng YYYY-MM-DD, nhận được: {args.since!r}")

    # KHOÁ chống 2 máy/2 tiến trình cùng quét (K3) — FAIL rõ ràng, không chạy chồng.
    duoc, ly_do = gianh_khoa()
    if not duoc:
        print(f"🔴 KHÔNG QUÉT: {ly_do}")
        return 3
    try:
        # `--khong-cursor` = KHÔNG ĐỌC và KHÔNG GHI con trỏ dùng chung (quét trọn cửa sổ). Con trỏ cục bộ rỗng
        # vẫn cho phép `--since` hoạt động — trước đây `--since` kèm `--khong-cursor` bị BỎ QUA IM LẶNG
        # (vì cursor=None) nên cửa sổ quét bù rộng hơn người gõ tưởng.
        ghi_con_tro = not args.khong_cursor
        cursor = doc_cursor() if ghi_con_tro else {}
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
        con_tro_truoc = dict(cursor)
        if args.since:
            for t0 in topics:
                cursor[t0["topic"]] = args.since
        try:
            # search_fn=search, summarize_fn=summarize TƯỜNG MINH (khớp giá trị mặc định của
            # run_scan, KHÔNG đổi hành vi) — chỉ để test CLI monkeypatch được S.search/S.summarize;
            # tham số mặc định của run_scan() gắn với đối tượng hàm lúc ĐỊNH NGHĨA, monkeypatch
            # thuộc tính module sau đó không có tác dụng nếu gọi không truyền tường minh ở đây.
            so_du_phong, loi_doc_so = _doc_so_du_phong()
            so_du_phong_truoc = json.loads(json.dumps(so_du_phong))
            report = run_scan(topics, days=args.days, max_results=args.max, cursor=cursor,
                              search_fn=search, summarize_fn=summarize,
                              tran_leo_thang_du_phong=args.tran_du_phong, trang_thai_du_phong=so_du_phong,
                              luu_so_du_phong=ghi_trang_thai_du_phong, du_phong_tat_vi=loi_doc_so)
        except ValueError as exc:
            parser.error(str(exc))
        # Sổ dự phòng: `run_scan` đã tự ghi bản «báo cáo CHƯA tới nơi» ngay sau từng lời gọi nguồn tính phí (mốc leo
        # thang + bài vừa lấy vào hàng chờ `cho_trinh`, «đã trình» giữ như cũ). Bản «ĐÃ tới nơi» — `so_du_phong` — chỉ
        # được ghi ở cuối hàm, sau khi báo cáo được in/ghi xong.
        if ghi_con_tro:
            # HAI LUẬT RIÊNG, không được gộp làm một (phản biện vòng 2 22/09 bắt được: bản gộp đầu
            # tiên làm test PASS-hợp-lệ đỏ oan — run_scan CHỈ tiến cursor cho chủ đề PASS nên hai
            # luật này không bao giờ chồng lấn nhau trên cùng một chủ đề):
            #
            # Luật A (21/09, cho chủ đề PASS): --since HẸP hơn con trỏ CŨ ĐÃ CÓ (since > cu) nghĩa
            # là khoảng [cu, since) bị CHỦ Ý bỏ qua — dù chủ đề đạt PASS cho cửa sổ hẹp đó, KHÔNG
            # được để cursor tiến tới hôm nay (sẽ khiến khoảng bị bỏ qua trông như "đã quét"). Chủ
            # đề CHƯA từng có cursor (cu is None) thì không có khoảng nào bị bỏ qua — cursor tiến
            # bình thường.
            #
            # Luật B (22/09, review:thu-nhan #8, cho chủ đề KHÔNG PASS): phục hồi cursor về ĐÚNG
            # trạng thái TRƯỚC lượt này — kể cả khi trước đó CHƯA có cursor (revert về "chưa có",
            # không phải về since/hôm nay). Luật A (21/09) bỏ sót đúng ca này: `if cu and …` không
            # bao giờ đúng khi `cu` là None ⇒ chủ đề DEGRADED/FAIL chưa từng quét trước đó đi thẳng
            # từ "chưa quét" sang since/hôm nay, vi phạm bất biến "suy giảm KHÔNG tiến con trỏ".
            for t in report["topics"]:
                cu = con_tro_truoc.get(t["topic"])
                if t["status"] == "PASS":
                    if args.since and cu and args.since > cu:
                        cursor[t["topic"]] = cu
                elif cu is None:
                    cursor.pop(t["topic"], None)
                else:
                    cursor[t["topic"]] = cu
            # Ở đây chỉ TÍNH con trỏ mới; việc GHI dời xuống cuối hàm, sau khi báo cáo đã tới nơi (vá 30/09/2026).

        do_tre = do_do_tre(report)
        if do_tre:
            report["do_tre"] = do_tre

        # ALERTS (K7) — chỉ sự kiện KHẨN
        khan: list[str] = []
        # Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #9): nêu TÊN chủ đề suy giảm — dòng gộp
        # cũ chỉ có SỐ LƯỢNG ("1/1 chủ đề"), nên khi orchestrator A2 chạy TỪNG chủ đề riêng (mỗi
        # lần watchlist chỉ 1/1), nhiều lượt trong ngày sinh ra các dòng TRÔNG GIỐNG HỆT NHAU dù
        # là chủ đề khác nhau — không ai phân biệt được. Nêu tên vừa giải quyết việc đó, vừa cho
        # ghi_alert() (đã vá cùng đợt) dedup ĐÚNG: hai lượt cùng một chủ đề ⇒ dòng giống hệt ⇒ bị
        # lọc trùng; hai lượt khác chủ đề ⇒ dòng khác nhau ⇒ cả hai đều được giữ.
        suy_giam_ten = sorted(_t["topic"] for _t in report["topics"] if _t["status"] == "PASS_DEGRADED")
        if suy_giam_ten:
            khan.append(f"- 🟠 QUÉT SUY GIẢM: {len(suy_giam_ten)}/{report['topic_count']} chủ đề không lấy được "
                        f"đủ (NCBI lỗi/bị chặn phải dùng Europe PMC dự phòng, hoặc thiếu bản tóm tắt — lý do từng "
                        f"chủ đề ở báo cáo quét) — {', '.join(suy_giam_ten)}. Kết quả có thể THIẾU; con trỏ các "
                        "chủ đề này KHÔNG tiến, chạy lại khi nguồn trả lời được.")
        if report.get("du_phong_tat_vi"):
            # Không tự hết: tệp hỏng thì MỌI lượt sau đều tắt làn dự phòng (mã thoát vẫn 0) cho tới khi có người sửa.
            khan.append(f"- 🟠 BẬC THANG DỰ PHÒNG TẮT: {report['du_phong_tat_vi']}. Lượt này không leo thang, không "
                        "trình bù, không ghi sổ — và mọi lượt sau cũng vậy cho tới khi sổ đọc được.")
        for _t in report["topics"]:
            if _t["status"] == "FAIL":
                khan.append(f"- 🔴 CỔNG QUÉT FAIL: chủ đề «{_t['topic']}» — `{_t['error'][:90]}`")
            for _c in _t["candidates"]:
                if _c.get("rut_bai") == "retracted":
                    khan.append(f"- 🔴 ỨNG VIÊN ĐÃ BỊ RÚT lọt vào lượt quét: PMID {_c['pmid']} "
                                f"({_t['topic']}) — KHÔNG dùng")
                elif _c.get("rut_bai") == "expression_of_concern":
                    khan.append(f"- 🟠 EoC: PMID {_c['pmid']} ({_t['topic']}) — đọc lại trước khi dùng")
        f_alert = ghi_alert(khan, date.today().isoformat())
        if f_alert:
            # Không khẳng định "đã ghi N" — ghi_alert() có thể lọc bớt dòng TRÙNG đã có sẵn hôm
            # nay (vá cùng đợt), nên số dòng THẬT SỰ mới có thể ít hơn len(khan).
            print(f"[⚠ {len(khan)} cảnh báo khẩn được xét (mới hoặc đã có sẵn hôm nay): {f_alert}]")

        markdown = markdown_report(report)
        print(markdown)
        if args.report:
            write_atomic(Path(args.report), markdown)
            print(f"[Đã lưu báo cáo: {args.report}]")
        if args.json_report:
            write_atomic(Path(args.json_report), json.dumps(report, ensure_ascii=False, indent=2) + "\n")
            print(f"[Đã lưu audit JSON: {args.json_report}]")
        # `print` chỉ nạp bộ đệm (≈128 KB): stdout là ống đã đóng/đĩa đầy thì lỗi chỉ lộ lúc ĐẨY. Đẩy NGAY ở đây để lỗi
        # đó nổ TRƯỚC khi ghi «đã trình»/con trỏ — nếu không, 0 byte báo cáo rời tiến trình mà con trỏ vẫn tiến.
        _sys_utf8.stdout.flush()

        # BÁO CÁO ĐÃ TỚI NƠI ⇒ giờ mới ghi «đã trình» và tiến con trỏ (vá 30/09/2026). Lượt W40 ngày 29/09 sập ở bước
        # đo độ trễ SAU khi con trỏ đã tiến cho 47 chủ đề và TRƯỚC khi có báo cáo ⇒ cửa sổ «đã quét» mà không ai thấy
        # ứng viên nào — đúng kiểu mất im lặng mà con trỏ phải tránh. Nay mọi lỗi trước dòng này (đo trễ, cảnh báo,
        # dựng/in/ghi báo cáo) để NGUYÊN con trỏ ⇒ lượt sau quét lại đúng cửa sổ đó: cái giá là có thể trình lặp,
        # không phải bỏ sót (bài dự phòng tính phí đã lấy thì nằm ở `cho_trinh`, lượt sau trình bù). Vẫn nằm trong khoá.
        if so_du_phong != so_du_phong_truoc:
            ghi_trang_thai_du_phong(so_du_phong)
        # Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #7): CHỈ ghi khi NỘI DUNG con trỏ thật sự đổi (có ≥1 chủ
        # đề PASS tiến con trỏ). Trước đây ghi VÔ ĐIỀU KIỆN — một lượt quét lỗi toàn bộ vẫn làm mtime
        # .quet-cursor.json nhảy, và sources_health.lay_thanh_cong_that() đọc mtime đó thành «lượt quét THÀNH CÔNG
        # hôm nay» — sai: ngày ghi file không phải bằng chứng thành công khi nội dung file không hề đổi.
        if ghi_con_tro and cursor != con_tro_truoc:
            ghi_cursor(cursor)
    finally:
        tra_khoa()

    if report["status"] == "PASS" or args.allow_partial:
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
