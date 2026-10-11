#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NẠP TRÍCH DẪN CỦA MỘT CHỦ ĐỀ VÀO ENDNOTE — mỗi chủ đề một nhóm «EBM · <chủ đề>» (11/10/2026).

Bác sĩ yêu cầu 11/10/2026: mỗi vấn đề cập nhật chứng cứ thì trích dẫn được lưu vào EndNote, mỗi
chủ đề một «thư mục» (nhóm tự tạo — custom group), kèm toàn văn khi có. Bác sĩ chọn thư viện
chính và ghi vào cấu hình RIÊNG MÁY `~/.ebm-endnote.json` (ngoài OneDrive, ngoài git — repo này
công khai, không ghi đường dẫn máy vào mã).

ĐO TRỰC TIẾP trên EndNote 2025 (bản 22.4) ngày 11/10/2026, trên một THƯ VIỆN THỬ NGHIỆM (bản chép
từ bản sao lưu cũ), không đụng thư viện thật:
  • AppleScript `import` nhận chuỗi XML của EndNote (RSXML) — đọc tệp bằng «class utf8» thì dấu
    tiếng Việt và ký tự như «Ș» giữ nguyên.
  • `find` tìm CHUỖI CON trong mọi thư viện đang mở và trả mã bản ghi dạng
    `<RecordID database="N" recNum="M" />` ⇒ phải lọc đúng `database` của thư viện đích và so
    KHỚP NGUYÊN trường (PMID 8 chữ số có thể là chuỗi con của số khác).
  • `post records in … as "<tên>" of type "CUSTOM"` tạo nhóm nếu chưa có và CỘNG THÊM vào nhóm đã
    có; đăng lại bản ghi đã nằm trong nhóm thì nhóm bị NHÂN ĐÔI (3 → 5) ⇒ chỉ đăng bản ghi chưa có.
  • `retrieve "all" records in document …` chạy với `document`; lệnh nhóm chạy với `window`.
  • Nhập lại cùng XML tạo bản ghi TRÙNG ⇒ tra PMID («Accession Number») và DOI trước khi nhập.
  • PDF đính NỘI BỘ: `internal-pdf://<số>/<tệp>` trỏ tới `<thư viện>.Data/PDF/<số>/<tệp>` (đúng
    dạng thư viện thật đang dùng); đường dẫn `file://` chỉ là liên kết ngoài, không đồng bộ theo
    tài khoản EndNote.
  • Nhập qua AppleScript KHÔNG kích «Find Full Text» tự động (chờ 45 giây, bài truy cập mở vẫn
    không có PDF); AppleScript của EndNote không có lệnh Find Full Text ⇒ phần toàn văn còn thiếu
    do BÁC SĨ bấm: chọn nhóm → References → Find Full Text (dùng quyền truy cập của chính bác sĩ).
  • `set field "File Attachments" of record … to "internal-pdf://…"` gắn PDF vào bản ghi ĐÃ có
    (bảng `file_res` của thư viện nhận đúng dòng đính kèm nội bộ). Lệnh `close document` làm EndNote
    SẬP (SIGSEGV, đo 11/10) ⇒ công cụ KHÔNG BAO GIỜ đóng thư viện.

Toàn văn đính kèm: CHỈ PDF đã có hợp lệ trong kho chung `EBM-Dashboards/toan_van_oa/` cho đúng PMID
(Unpaywall giấy phép mở · Wiley TDM · bản lưu trong phiên trình duyệt có uỷ quyền của bác sĩ). Công
cụ KHÔNG tải bài thuê bao, KHÔNG đọc nội dung PDF. Metadata lấy lại từ PubMed (efetch) hoặc Crossref
— không chép từ chuỗi tham khảo trong dashboard. Không lấy được metadata ⇒ KHÔNG nhập bản ghi đó.
Toàn văn thường về SAU trích dẫn (gom OA/Unpaywall, Wiley TDM, phiên Chrome uỷ quyền của bác sĩ) ⇒
mỗi lượt `--ap-dung` còn GẮN PDF mới có vào bản ghi của chủ đề CHƯA có tệp đính kèm nào — tệp bác sĩ
đã gắn không bao giờ bị ghi đè — rồi liệt kê bản ghi còn thiếu toàn văn cho làn kế tiếp:
  1. `python3 tools/gom_toan_van_dashboard.py --file <dashboard> --unpaywall`   (bản truy cập mở)
  2. `python3 tools/doc_toan_van_co_nguoi.py --pmid <PMID…>`                     (bài thuê bao: phiếu
     làn Chrome có uỷ quyền — Wiley · ScienceDirect · NEJM · JAMA…; bác sĩ tự đăng nhập/vượt chặn)
  3. `python3 tools/doc_sau_toan_van.py --dashboard <dashboard>`                  (bản đọc sâu)
  4. chạy lại công cụ này với `--ap-dung` ⇒ PDF mới vào đúng nhóm EndNote.

Dùng:
  python3 tools/nap_endnote_chu_de.py --ghi-cau-hinh "<đường dẫn .enl>" [--ung-dung "EndNote 2025"]
  python3 tools/nap_endnote_chu_de.py --file EBM-Dashboards/WebDashboard_X.html            # chạy khô
  python3 tools/nap_endnote_chu_de.py --file EBM-Dashboards/WebDashboard_X.html --ap-dung  # nạp thật
  python3 tools/nap_endnote_chu_de.py --tat-ca [--ap-dung]
  python3 tools/nap_endnote_chu_de.py --file … --xuat-xml ra.xml   # tệp nhập tay (Windows)
Mã thoát: 0 xong · 1 có trích dẫn không lấy được metadata (phần còn lại vẫn nạp) ·
          2 không chạy được (không phải Mac, chưa cấu hình, thư viện chưa mở/lệch) · 3 tham số sai.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
# Cấu hình RIÊNG MÁY (ngoài OneDrive, ngoài git). Biến môi trường chỉ để trỏ sang thư viện THỬ NGHIỆM.
CAU_HINH = Path(os.environ.get("EBM_ENDNOTE_CAU_HINH") or (Path.home() / ".ebm-endnote.json"))
UNG_DUNG_MAC_DINH = "EndNote 2025"
TIEN_TO_NHOM = "EBM · "
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CROSSREF = "https://api.crossref.org/works/"
LO_EFETCH = 150
# Nguồn của PDF trong kho chung, theo hậu tố tên tệp — thứ tự là thứ tự ƯU TIÊN khi một PMID có nhiều bản.
NGUON_PDF = (
    ("UPW", "Unpaywall — bản mang giấy phép mở"),
    ("WTDM", "Wiley TDM"),
    ("CHR", "bản lưu trong phiên trình duyệt có uỷ quyền của bác sĩ"),
)
MA_OK, MA_MOT_PHAN, MA_KHONG_CHAY, MA_THAM_SO = 0, 1, 2, 3
_TEN_UNG_DUNG = re.compile(r"^[\w .\-]{1,60}$")


class KhongChayDuoc(RuntimeError):
    """Không làm được ở máy/trạng thái này (không phải Mac, chưa cấu hình, thư viện chưa mở…)."""


# ── cấu hình riêng máy ──────────────────────────────────────────────────────────────────────────────

def doc_cau_hinh(tep: Path | None = None) -> dict | None:
    try:
        ch = json.loads((tep or CAU_HINH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(ch, dict) or not ch.get("thu_vien"):
        return None
    ch.setdefault("ung_dung", UNG_DUNG_MAC_DINH)
    return ch


def ghi_cau_hinh(thu_vien: str, ung_dung: str, tep: Path | None = None) -> dict:
    p = Path(thu_vien).expanduser()
    if p.suffix.lower() != ".enl" or not p.is_file():
        raise ValueError(f"không thấy thư viện EndNote (.enl): {p}")
    if not _TEN_UNG_DUNG.match(ung_dung):
        raise ValueError(f"tên ứng dụng không hợp lệ: {ung_dung!r}")
    ch = {"thu_vien": str(p.resolve()), "ung_dung": ung_dung}
    (tep or CAU_HINH).write_text(json.dumps(ch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return ch


# ── đọc dashboard ──────────────────────────────────────────────────────────────────────────────────

def _nap_doc_data():
    sp = importlib.util.spec_from_file_location("_kcnn_endnote", ROOT / "tools" / "kiem_cheo_ngu_nghia.py")
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.doc_data


def ten_chu_de(data: dict, dash: Path) -> str:
    """Tên nhóm: câu hỏi lâm sàng của dashboard, gọn một dòng, ≤ 100 ký tự; không có thì tên tệp."""
    cau_hoi = str(((data or {}).get("meta") or {}).get("question") or "").strip()
    ten = re.sub(r"\s+", " ", cau_hoi) or dash.stem
    return ten if len(ten) <= 100 else ten[:99].rstrip() + "…"


def khoa_chu_de(dash: Path) -> str:
    """Khoá bền qua các phiên bản: tên tệp bỏ tiền tố WebDashboard_ và đuôi ngày _YYYYMMDD."""
    return re.sub(r"_\d{8}$", "", re.sub(r"^WebDashboard_", "", dash.stem))


def chuan_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    d = str(doi).strip()
    d = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", d, flags=re.I)
    d = d.rstrip(".,;)]")
    return d.lower() if re.match(r"^10\.\d{4,9}/\S+$", d) else None


_PMID_THAM_KHAO = re.compile(r"PMID[:\s]*(\d{6,9})")
_DOI_THAM_KHAO = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)")


def trich_dinh_danh(data: dict) -> list[dict]:
    """Mọi trích dẫn của dashboard: định danh chính của từng mục + PMID/DOI ghi rõ trong `references`.

    Khử trùng theo PMID (rồi DOI). Chỉ nhận định danh đúng khuôn — chữ khác bị bỏ, không đoán."""
    ra: list[dict] = []
    da_thay: set[str] = set()

    def them(pmid: str | None, doi: str | None, vai: str, muc: str) -> None:
        pmid = pmid if pmid and re.fullmatch(r"\d{1,9}", pmid) else None
        doi = chuan_doi(doi)
        if not pmid and not doi:
            return
        khoa = f"pmid:{pmid}" if pmid else f"doi:{doi}"
        if khoa in da_thay or (doi and f"doi:{doi}" in da_thay):
            return
        da_thay.add(khoa)
        if doi:
            da_thay.add(f"doi:{doi}")
        ra.append({"pmid": pmid, "doi": doi, "vai": vai, "muc": muc})

    for it in (data or {}).get("items") or []:
        if not isinstance(it, dict):
            continue
        muc = str(it.get("id") or "?")
        them(str(it.get("pmid") or "").strip() or None, it.get("doi"), "muc", muc)
    for it in (data or {}).get("items") or []:
        if not isinstance(it, dict):
            continue
        muc = str(it.get("id") or "?")
        for tk in it.get("references") or []:
            tk = str(tk)
            m_pm = _PMID_THAM_KHAO.search(tk)
            m_doi = _DOI_THAM_KHAO.search(tk)
            them(m_pm.group(1) if m_pm else None, m_doi.group(1) if m_doi else None, "tham_khao", muc)
    return ra


# ── metadata: PubMed / Crossref ────────────────────────────────────────────────────────────────────

def _email() -> str:
    try:
        sp = importlib.util.spec_from_file_location("_tdd_endnote", ROOT / "tools" / "tra_dinh_danh.py")
        mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
        return mod.email_lien_he()
    except Exception:  # noqa: BLE001 — thiếu email chỉ làm mất «polite pool», không làm hỏng việc
        return ""


def _tai(url: str, lan_thu: int = 3, cho: float = 2.0) -> bytes:
    """GET có thử lại (lỗi mạng, 429, 5xx). Lỗi 4xx khác thì ném ngay — thử lại vô ích."""
    loi: Exception | None = None
    for i in range(lan_thu):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EBM-Copilot-EndNote/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
            loi = e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            loi = e
        if i < lan_thu - 1:
            time.sleep(cho * (i + 1))
    raise RuntimeError(f"không tải được sau {lan_thu} lần: {loi}")


def _chu(n: ET.Element | None) -> str:
    return re.sub(r"\s+", " ", "".join(n.itertext())).strip() if n is not None else ""


def _nam(s: str) -> str:
    m = re.search(r"(1[89]\d\d|20\d\d)", s or "")
    return m.group(1) if m else ""


def phan_tich_pubmed_xml(du_lieu: bytes) -> dict[str, dict]:
    """XML efetch của PubMed → {pmid: metadata}. Bài báo và tài liệu sách (Bookshelf) đều nhận."""
    goc = ET.fromstring(du_lieu)
    ra: dict[str, dict] = {}
    for bai in goc.findall("PubmedArticle"):
        mc = bai.find("MedlineCitation")
        pmid = _chu(mc.find("PMID")) if mc is not None else ""
        art = mc.find("Article") if mc is not None else None
        if not pmid or art is None:
            continue
        tac_gia = []
        for a in art.findall("AuthorList/Author"):
            if a.find("CollectiveName") is not None:
                tac_gia.append(_chu(a.find("CollectiveName")))
            elif a.find("LastName") is not None:
                ten = _chu(a.find("ForeName")) or _chu(a.find("Initials"))
                tac_gia.append(_chu(a.find("LastName")) + (f", {ten}" if ten else ""))
        ji = art.find("Journal/JournalIssue")
        nam = _chu(ji.find("PubDate/Year")) if ji is not None else ""
        if not nam and ji is not None:
            nam = _nam(_chu(ji.find("PubDate/MedlineDate")))
        tom_tat = []
        for t in art.findall("Abstract/AbstractText"):
            nhan = t.get("Label")
            tom_tat.append((f"{nhan}: " if nhan else "") + _chu(t))
        ids = {i.get("IdType"): _chu(i) for i in bai.findall("PubmedData/ArticleIdList/ArticleId")}
        doi = ids.get("doi") or next((_chu(e) for e in art.findall("ELocationID")
                                       if e.get("EIdType") == "doi"), "")
        loai = [_chu(p) for p in art.findall("PublicationTypeList/PublicationType")]
        ra[pmid] = {
            "pmid": pmid, "doi": chuan_doi(doi), "loai_tl": "Journal Article",
            "tieu_de": _chu(art.find("ArticleTitle")).rstrip(), "tac_gia": [t for t in tac_gia if t],
            "tap_chi": _chu(art.find("Journal/Title")), "tap_chi_viet_tat": _chu(art.find("Journal/ISOAbbreviation")),
            "nam": nam, "tap": _chu(ji.find("Volume")) if ji is not None else "",
            "so": _chu(ji.find("Issue")) if ji is not None else "", "trang": _chu(art.find("Pagination/MedlinePgn")),
            "issn": _chu(art.find("Journal/ISSN")), "tom_tat": "\n".join(x for x in tom_tat if x),
            "ngon_ngu": _chu(art.find("Language")), "pmcid": ids.get("pmc", ""),
            "da_rut": "Retracted Publication" in loai, "nguon_meta": "PubMed",
        }
    for sach in goc.findall("PubmedBookArticle"):
        bd = sach.find("BookDocument")
        pmid = _chu(bd.find("PMID")) if bd is not None else ""
        if not pmid:
            continue
        tac_gia = []
        for a in bd.findall("AuthorList/Author"):
            if a.find("LastName") is not None:
                ten = _chu(a.find("ForeName")) or _chu(a.find("Initials"))
                tac_gia.append(_chu(a.find("LastName")) + (f", {ten}" if ten else ""))
            elif a.find("CollectiveName") is not None:
                tac_gia.append(_chu(a.find("CollectiveName")))
        ids = {i.get("IdType"): _chu(i) for i in sach.findall("PubmedBookData/ArticleIdList/ArticleId")}
        ra[pmid] = {
            "pmid": pmid, "doi": chuan_doi(ids.get("doi")), "loai_tl": "Book Section",
            "tieu_de": _chu(bd.find("ArticleTitle")) or _chu(bd.find("Book/BookTitle")),
            "tac_gia": [t for t in tac_gia if t], "tap_chi": _chu(bd.find("Book/BookTitle")),
            "tap_chi_viet_tat": "", "nam": _nam(_chu(bd.find("Book/PubDate"))), "tap": "", "so": "", "trang": "",
            "issn": "", "nha_xb": _chu(bd.find("Book/Publisher/PublisherName")),
            "tom_tat": "\n".join(_chu(t) for t in bd.findall("Abstract/AbstractText")),
            "ngon_ngu": _chu(bd.find("Language")), "pmcid": "", "da_rut": False, "nguon_meta": "PubMed",
        }
    return ra


class NcbiChan(RuntimeError):
    """NCBI trả trang chặn IP («WWW Error Blocked Diagnostic») — chặn phía máy chủ, thử lại vô ích."""


def la_trang_chan_ncbi(du_lieu: bytes) -> bool:
    dau = du_lieu[:4000].lower()
    return b"blocked diagnostic" in dau or b"blocked for possible abuse" in dau


def lay_pubmed(pmids: list[str], tai=_tai) -> dict[str, dict]:
    ra: dict[str, dict] = {}
    mail = _email()
    for i in range(0, len(pmids), LO_EFETCH):
        lo = pmids[i:i + LO_EFETCH]
        url = (f"{EUTILS}/efetch.fcgi?db=pubmed&retmode=xml&tool=ebm-copilot&id={','.join(lo)}"
               + (f"&email={urllib.parse.quote(mail)}" if mail else ""))
        du_lieu = tai(url)
        if la_trang_chan_ncbi(du_lieu):
            # Đo 11/10/2026: NCBI trả HTTP 200 kèm trang HTML này — không bắt thì ParseError mù mờ.
            raise NcbiChan("NCBI đang chặn IP mạng này (trang «Blocked Diagnostic») — lùi sang Europe PMC")
        ra.update(phan_tich_pubmed_xml(du_lieu))
        if i + LO_EFETCH < len(pmids):
            time.sleep(0.4)  # ≤ 3 lượt/giây khi không có khoá NCBI
    return ra


EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
LO_EUROPEPMC = 80


def _bo_the_html(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def phan_tich_europepmc(js: dict) -> dict[str, dict]:
    """Kết quả `resultType=core` của Europe PMC (nguồn MED) → {pmid: metadata} cùng khuôn với PubMed."""
    ra: dict[str, dict] = {}
    for r in ((js or {}).get("resultList") or {}).get("result") or []:
        pmid = str(r.get("pmid") or "").strip()
        if not pmid or not r.get("title"):
            continue
        tac_gia = []
        for a in ((r.get("authorList") or {}).get("author")) or []:
            if a.get("lastName"):
                ten = a.get("firstName") or a.get("initials") or ""
                tac_gia.append(a["lastName"] + (f", {ten}" if ten else ""))
            elif a.get("collectiveName"):
                tac_gia.append(a["collectiveName"])
        ji = r.get("journalInfo") or {}
        tc = ji.get("journal") or {}
        loai = ((r.get("pubTypeList") or {}).get("pubType")) or []
        ra[pmid] = {
            "pmid": pmid, "doi": chuan_doi(r.get("doi")), "loai_tl": "Journal Article",
            "tieu_de": _bo_the_html(r["title"]), "tac_gia": tac_gia, "tap_chi": tc.get("title") or "",
            "tap_chi_viet_tat": tc.get("isoabbreviation") or tc.get("medlineAbbreviation") or "",
            "nam": str(ji.get("yearOfPublication") or r.get("pubYear") or ""), "tap": ji.get("volume") or "",
            "so": ji.get("issue") or "", "trang": r.get("pageInfo") or "",
            "issn": tc.get("issn") or tc.get("essn") or "",
            "tom_tat": _bo_the_html(r.get("abstractText") or ""), "ngon_ngu": r.get("language") or "",
            "pmcid": r.get("pmcid") or "", "da_rut": "Retracted Publication" in loai,
            "nguon_meta": "Europe PMC",
        }
    return ra


def lay_europepmc(pmids: list[str], tai=_tai) -> dict[str, dict]:
    ra: dict[str, dict] = {}
    for i in range(0, len(pmids), LO_EUROPEPMC):
        lo = pmids[i:i + LO_EUROPEPMC]
        q = f"EXT_ID:({' OR '.join(lo)}) AND SRC:MED"
        url = f"{EUROPEPMC}?query={urllib.parse.quote(q)}&resultType=core&format=json&pageSize={len(lo) + 5}"
        ra.update(phan_tich_europepmc(json.loads(tai(url))))
    return ra


def phan_tich_crossref(js: dict) -> dict | None:
    m = (js or {}).get("message") or {}
    tieu_de = " ".join(m.get("title") or []).strip()
    if not tieu_de:
        return None
    tac_gia = []
    for a in m.get("author") or []:
        if a.get("family"):
            tac_gia.append(a["family"] + (f", {a['given']}" if a.get("given") else ""))
        elif a.get("name"):
            tac_gia.append(a["name"])
    phan = ((m.get("issued") or {}).get("date-parts") or [[None]])[0]
    loai = m.get("type") or ""
    return {
        "pmid": None, "doi": chuan_doi(m.get("DOI")),
        "loai_tl": "Book Section" if loai in ("book-chapter", "book-section") else "Journal Article",
        "tieu_de": tieu_de, "tac_gia": tac_gia, "tap_chi": " ".join(m.get("container-title") or []),
        "tap_chi_viet_tat": " ".join(m.get("short-container-title") or []),
        "nam": str(phan[0]) if phan and phan[0] else "", "tap": m.get("volume") or "", "so": m.get("issue") or "",
        "trang": m.get("page") or "", "issn": (m.get("ISSN") or [""])[0], "tom_tat": "",
        "ngon_ngu": m.get("language") or "", "pmcid": "", "da_rut": False, "nguon_meta": "Crossref",
    }


def lay_crossref(doi: str, tai=_tai) -> dict | None:
    mail = _email()
    url = CROSSREF + urllib.parse.quote(doi, safe="/") + (f"?mailto={urllib.parse.quote(mail)}" if mail else "")
    try:
        return phan_tich_crossref(json.loads(tai(url)))
    except (RuntimeError, urllib.error.HTTPError, ValueError):
        return None


# ── toàn văn có sẵn trong kho chung ────────────────────────────────────────────────────────────────

def chon_pdf(kho: Path | None, pmid: str | None) -> tuple[Path, str] | None:
    """PDF của ĐÚNG PMID này trong kho (PMID-123 không được bắt nhầm PMID-1234…), theo thứ tự ưu tiên."""
    if not kho or not pmid or not kho.is_dir():
        return None
    co: dict[str, Path] = {}
    for p in kho.iterdir():
        m = re.fullmatch(rf"PMID-{re.escape(pmid)}_([A-Za-z]+)\.pdf", p.name, flags=re.I)
        if m and p.is_file():
            co[m.group(1).upper()] = p
    for hau_to, nhan in NGUON_PDF:
        if hau_to in co:
            return co[hau_to], nhan
    return None


def dat_pdf_vao_thu_vien(thu_vien: Path, pdf: Path, pmid: str) -> tuple[str, Path]:
    """Chép PDF vào `<thư viện>.Data/PDF/<số 10 chữ số>/` — đúng chỗ EndNote cất đính kèm nội bộ.
    Trả (url internal-pdf, thư mục vừa tạo) để người gọi dọn nếu bước nhập hỏng."""
    goc = thu_vien.with_suffix(".Data") / "PDF"
    goc.mkdir(parents=True, exist_ok=True)
    for _ in range(50):
        so = str(1_000_000_000 + secrets.randbelow(8_999_999_999))
        thu_muc = goc / so
        if not thu_muc.exists():
            break
    else:  # pragma: no cover — 50 lần trùng liên tiếp gần như không thể
        raise RuntimeError("không chọn được thư mục đính kèm còn trống")
    thu_muc.mkdir()
    ten = f"PMID-{pmid}.pdf"
    shutil.copyfile(pdf, thu_muc / ten)
    return f"internal-pdf://{so}/{ten}", thu_muc


# ── dựng XML nhập của EndNote ──────────────────────────────────────────────────────────────────────

_MA_LOAI = {"Journal Article": 17, "Book Section": 5}


def _the(ten: str, gia_tri: str) -> str:
    return f"<{ten}>{escape(gia_tri)}</{ten}>" if gia_tri else ""


def dung_xml(ban_ghi: list[dict]) -> str:
    """Danh sách metadata (kèm `tu_khoa`, `ghi_chu`, `pdf_url` tuỳ chọn) → chuỗi XML nhập của EndNote."""
    phan = ['<?xml version="1.0" encoding="UTF-8"?><xml><records>']
    for m in ban_ghi:
        loai = m.get("loai_tl") or "Journal Article"
        phan.append(f'<record><ref-type name="{escape(loai)}">{_MA_LOAI.get(loai, 17)}</ref-type>')
        if m.get("tac_gia"):
            phan.append("<contributors><authors>" + "".join(_the("author", a) for a in m["tac_gia"])
                        + "</authors></contributors>")
        phan.append("<titles>" + _the("title", m.get("tieu_de", "")) + _the("secondary-title", m.get("tap_chi", ""))
                    + "</titles>")
        if m.get("tap_chi"):
            phan.append("<periodical>" + _the("full-title", m["tap_chi"])
                        + _the("abbr-1", m.get("tap_chi_viet_tat", "")) + "</periodical>")
        for ten, khoa in (("pages", "trang"), ("volume", "tap"), ("number", "so")):
            phan.append(_the(ten, m.get(khoa, "")))
        if m.get("tu_khoa"):
            phan.append("<keywords>" + "".join(_the("keyword", k) for k in m["tu_khoa"]) + "</keywords>")
        if m.get("nam"):
            phan.append("<dates>" + _the("year", m["nam"]) + "</dates>")
        phan.append(_the("publisher", m.get("nha_xb", "")))
        phan.append(_the("isbn", m.get("issn", "")))
        phan.append(_the("accession-num", m.get("pmid") or ""))
        phan.append(_the("electronic-resource-num", m.get("doi") or ""))
        phan.append(_the("abstract", m.get("tom_tat", "")))
        phan.append(_the("notes", m.get("ghi_chu", "")))
        phan.append(_the("label", m.get("nhan", "")))
        url = (f"https://pubmed.ncbi.nlm.nih.gov/{m['pmid']}/" if m.get("pmid")
               else (f"https://doi.org/{m['doi']}" if m.get("doi") else ""))
        if url or m.get("pdf_url"):
            phan.append("<urls>" + ("<related-urls>" + _the("url", url) + "</related-urls>" if url else "")
                        + ("<pdf-urls>" + _the("url", m["pdf_url"]) + "</pdf-urls>" if m.get("pdf_url") else "")
                        + "</urls>")
        if m.get("nguon_meta") in ("PubMed", "Europe PMC"):
            phan.append(_the("remote-database-name", m["nguon_meta"])
                        + _the("remote-database-provider", "NLM" if m["nguon_meta"] == "PubMed" else "EMBL-EBI"))
        phan.append(_the("language", m.get("ngon_ngu", "")))
        phan.append("</record>")
    phan.append("</records></xml>")
    return "".join(phan)


# ── điều khiển EndNote trên Mac (AppleScript) ──────────────────────────────────────────────────────

class EndNoteMac:
    """Bọc các lệnh AppleScript đã đo của EndNote. Mọi lệnh đi qua `_chay` (dễ thay khi test)."""

    def __init__(self, ung_dung: str, thu_vien: Path) -> None:
        if sys.platform != "darwin":
            raise KhongChayDuoc("tự nhập vào EndNote chỉ chạy trên macOS (AppleScript); "
                                "máy này dùng --xuat-xml rồi nhập tay (File → Import, bộ lọc «EndNote generated XML»)")
        if os.environ.get("PYTEST_CURRENT_TEST") and not os.environ.get("EBM_ENDNOTE_CHO_PHEP_TRONG_TEST"):
            raise KhongChayDuoc("đang chạy dưới pytest — không bao giờ điều khiển EndNote thật")
        if not _TEN_UNG_DUNG.match(ung_dung):
            raise KhongChayDuoc(f"tên ứng dụng không hợp lệ: {ung_dung!r}")
        self.ung_dung = ung_dung
        self.thu_vien = thu_vien
        self.ten = thu_vien.name
        self._csdl: str | None = None

    def _chay(self, than: str, *doi_so: str, cho: int = 600) -> str:
        kich_ban = f'on run argv\ntell application "{self.ung_dung}"\n{than}\nend tell\nend run'
        kq = subprocess.run(["osascript", "-", *doi_so], input=kich_ban, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=cho)
        if kq.returncode != 0:
            raise RuntimeError(f"AppleScript lỗi: {kq.stderr.strip()[:300]}")
        return kq.stdout.rstrip("\n")

    def dang_mo_dung_thu_vien(self) -> bool:
        try:
            # `POSIX path of (file of d)` báo lỗi -1700 (đo 11/10) — phải ép sang chuỗi HFS trước.
            ds = self._chay('set out to ""\nrepeat with d in documents\n'
                            'set out to out & (POSIX path of ((file of d) as text)) & linefeed\n'
                            'end repeat\nreturn out')
        except RuntimeError:
            return False
        dich = os.path.realpath(self.thu_vien)
        return any(os.path.realpath(d.strip()) == dich for d in ds.splitlines() if d.strip())

    def mo_thu_vien(self, cho_giay: int = 40) -> None:
        subprocess.run(["open", "-a", self.ung_dung, str(self.thu_vien)], check=False, capture_output=True)
        het = time.monotonic() + cho_giay
        while time.monotonic() < het:
            if self.dang_mo_dung_thu_vien():
                return
            time.sleep(2)
        raise KhongChayDuoc(f"EndNote chưa mở được thư viện {self.thu_vien} sau {cho_giay} giây")

    def so_csdl(self) -> str:
        if self._csdl is None:
            ids = self._chay('set ids to retrieve "all" records in document (item 1 of argv)\n'
                             'if ids is missing value or (count of ids) is 0 then return ""\n'
                             'return item 1 of ids', self.ten)
            m = re.search(r'database="(\d+)"', ids)
            if not m:
                raise KhongChayDuoc("thư viện đích rỗng — chưa xác định được mã cơ sở dữ liệu của nó")
            self._csdl = m.group(1)
        return self._csdl

    def tim_khop(self, gia_tri: list[str], truong: str) -> dict[str, list[str]]:
        """{giá trị: [mã bản ghi]} — chỉ bản ghi của thư viện đích, trường KHỚP NGUYÊN (không phân biệt hoa/thường)."""
        if not gia_tri:
            return {}
        than = (
            'set db to "database=\\"" & (item 1 of argv) & "\\""\nset truong to item 2 of argv\nset out to ""\n'
            'repeat with i from 3 to count of argv\nset v to item i of argv\nset ids to find v in field truong\n'
            'set khop to ""\nif ids is not missing value then\nrepeat with r in ids\n'
            'if (r as text) contains db then\nif (field truong of record (r as text)) is v then '
            'set khop to khop & tab & (r as text)\nend if\nend repeat\nend if\n'
            'set out to out & v & khop & linefeed\nend repeat\nreturn out')
        ra: dict[str, list[str]] = {}
        for i in range(0, len(gia_tri), 200):
            for dong in self._chay(than, self.so_csdl(), truong, *gia_tri[i:i + 200]).splitlines():
                phan = dong.split("\t")
                if phan and phan[0]:
                    ra[phan[0]] = [x for x in phan[1:] if x]
        return ra

    def nhap(self, tep_xml: Path) -> None:
        self._chay('set x to read (POSIX file (item 1 of argv)) as «class utf8»\n'
                   'import x into document (item 2 of argv)', str(tep_xml), self.ten)

    def thanh_vien_nhom(self, ten_nhom: str) -> list[str]:
        out = self._chay('set ids to get records in (item 1 of argv) of type "CUSTOM" in window (item 2 of argv)\n'
                         'if ids is missing value then return ""\nset AppleScript\'s text item delimiters to tab\n'
                         'return ids as text', ten_nhom, self.ten)
        return [x for x in out.split("\t") if x.strip()]

    def dang_vao_nhom(self, ids: list[str], ten_nhom: str) -> None:
        if ids:
            self._chay('set ids to items 3 thru -1 of argv\n'
                       'post records in ids in window (item 2 of argv) as (item 1 of argv) of type "CUSTOM"',
                       ten_nhom, self.ten, *ids)

    def tep_dinh_kem(self, ids: list[str]) -> dict[str, int]:
        """{mã bản ghi: số ký tự trường «File Attachments»} — 0 = chưa gắn tệp nào.
        Chỉ trả ĐỘ DÀI: trường có nhiều tệp ngăn bằng xuống dòng, đọc nguyên văn sẽ vỡ dòng kết quả."""
        ra: dict[str, int] = {}
        than = ('set out to ""\nrepeat with i from 1 to count of argv\nset r to item i of argv\n'
                'set out to out & r & tab & (count of (field "File Attachments" of record r)) & linefeed\n'
                'end repeat\nreturn out')
        for i in range(0, len(ids), 200):
            for dong in self._chay(than, *ids[i:i + 200]).splitlines():
                ma, _, so = dong.rpartition("\t")
                if ma and so.strip().isdigit():
                    ra[ma] = int(so)
        return ra

    def gan_tep(self, ma: str, url: str) -> None:
        """Gắn MỘT tệp vào bản ghi rồi đọc lại — không khớp ⇒ lỗi (không im lặng coi là đã gắn)."""
        doc_lai = self._chay('set field "File Attachments" of record (item 1 of argv) to (item 2 of argv)\n'
                             'return field "File Attachments" of record (item 1 of argv)', ma, url)
        if doc_lai.strip() != url:
            raise RuntimeError(f"EndNote không nhận tệp đính kèm cho {ma}: đọc lại {doc_lai[:120]!r}")


# ── điều phối một chủ đề ───────────────────────────────────────────────────────────────────────────

def lay_metadata(dd: list[dict], lay_pm=lay_pubmed, lay_cr=lay_crossref,
                 lay_ep=lay_europepmc) -> tuple[list[tuple[dict, dict]], list[str]]:
    """[(định danh, metadata)] cho các trích dẫn lấy được; danh sách nhãn của trích dẫn KHÔNG lấy được.

    PubMed trước (theo lô). PubMed lỗi hoặc NCBI chặn IP (gặp thật 11/10/2026 khi VPN bảo trì) ⇒ Europe PMC
    (độc lập NCBI) cho các PMID còn thiếu. Vẫn thiếu mà có DOI ⇒ Crossref, giữ nguyên PMID của dashboard."""
    pmids = [d["pmid"] for d in dd if d.get("pmid")]
    meta_pm: dict[str, dict] = {}
    if pmids:
        try:
            meta_pm = dict(lay_pm(pmids))
        except (RuntimeError, ET.ParseError, OSError):
            meta_pm = {}
        thieu_pm = [p for p in pmids if p not in meta_pm]
        if thieu_pm:
            try:
                meta_pm.update(lay_ep(thieu_pm))
            except (RuntimeError, ValueError, OSError):
                pass
    co: list[tuple[dict, dict]] = []
    thieu: list[str] = []
    for d in dd:
        m = meta_pm.get(d["pmid"]) if d.get("pmid") else None
        if m is None and d.get("doi"):
            m = lay_cr(d["doi"])
            if m is not None and d.get("pmid"):
                m = dict(m, pmid=d["pmid"])
        if m is None:
            thieu.append(f"PMID {d['pmid']}" if d.get("pmid") else f"doi:{d['doi']}")
        else:
            co.append((d, dict(m)))
    return co, thieu


def xet_toan_van(endnote, cap: list[tuple[dict, str]], kho: Path | None) -> tuple[list[tuple], list[str]]:
    """(trích dẫn, mã bản ghi) → ([(mã, PMID, (pdf, nhãn))] cần gắn, [định danh còn thiếu toàn văn]).

    Bản ghi ĐÃ có tệp đính kèm (bác sĩ gắn, Find Full Text, lượt trước) bị bỏ qua — không bao giờ ghi đè.
    Bản ghi không đọc được trường đính kèm cũng bỏ qua: «không đo được» không phải «chưa có»."""
    tep = endnote.tep_dinh_kem([r for _, r in cap]) if cap else {}
    can_gan: list[tuple] = []
    thieu: list[str] = []
    for d, r in cap:
        if tep.get(r) != 0:
            continue
        pdf = chon_pdf(kho, d.get("pmid"))
        if pdf:
            can_gan.append((r, d["pmid"], pdf))
        else:
            thieu.append(f"PMID {d['pmid']}" if d.get("pmid") else f"DOI {d['doi']}")
    return can_gan, thieu


def _gan_pdf(endnote, can_gan: list[tuple]) -> None:
    """Đặt từng PDF vào `.Data/PDF/` rồi gắn vào bản ghi; gắn hỏng ⇒ dọn đúng thư mục vừa đặt rồi ném lỗi."""
    for r, pmid, (pdf, _nhan) in can_gan:
        url, tm = dat_pdf_vao_thu_vien(endnote.thu_vien, pdf, pmid)
        try:
            endnote.gan_tep(r, url)
        except Exception:
            shutil.rmtree(tm, ignore_errors=True)  # gắn hỏng ⇒ không để PDF mồ côi
            raise


def gan_kho(endnote, kho: Path | None, pmids: list[str] | None, ap_dung: bool) -> dict:
    """PDF trong kho → bản ghi CÓ SẴN trong thư viện cùng PMID («Accession Number»), không cần dashboard.

    Toàn văn về SAU trích dẫn (phiên Chrome uỷ quyền, Unpaywall, Wiley TDM) ⇒ công cụ sinh PDF gọi chế độ này để PDF vào
    ngay mọi nhóm đang chứa bản ghi. Cùng luật với lượt nạp chủ đề: chỉ bản ghi CHƯA có tệp nào; bản trùng PMID trong thư
    viện chỉ gắn bản đầu (giống lúc đăng nhóm)."""
    bc: dict = {"kho_toan_van": bool(kho and kho.is_dir()), "pdf_trong_kho": 0, "co_ban_ghi": 0, "ap_dung": ap_dung}
    if not bc["kho_toan_van"]:
        return bc
    co_pdf: set[str] = set()
    for p in kho.iterdir():
        m = re.fullmatch(r"PMID-(\d{1,9})_[A-Za-z]+\.pdf", p.name, flags=re.I)
        if m and p.is_file():
            co_pdf.add(m.group(1))
    pm = sorted(co_pdf if pmids is None else co_pdf & set(pmids))
    bc["pdf_trong_kho"] = len(pm)
    theo_pm = endnote.tim_khop(pm, "Accession Number") if pm else {}
    cap: list[tuple[dict, str]] = []
    thay: set[str] = set()
    for p in pm:
        for r in (theo_pm.get(p) or [])[:1]:
            if r not in thay:
                thay.add(r)
                cap.append(({"pmid": p}, r))
    bc["co_ban_ghi"] = len(cap)
    can_gan, _ = xet_toan_van(endnote, cap, kho)
    if ap_dung:
        _gan_pdf(endnote, can_gan)
        bc["gan_them_pdf"] = len(can_gan)
    else:
        bc["se_gan_pdf"] = len(can_gan)
    return bc


def nap_chu_de(dash: Path, *, endnote, ap_dung: bool, kho: Path | None, doc_data=None,
               lay_pm=lay_pubmed, lay_cr=lay_crossref, lay_ep=lay_europepmc, ten_nhom: str | None = None) -> dict:
    """Một dashboard → một nhóm EndNote. `endnote` None = chỉ lập kế hoạch, không kiểm trùng được."""
    doc_data = doc_data or _nap_doc_data()
    data = doc_data(dash)
    if not data:
        return {"dashboard": dash.name, "loi": "không đọc được khối DATA"}
    nhom = ten_nhom or TIEN_TO_NHOM + ten_chu_de(data, dash)
    khoa = khoa_chu_de(dash)
    dd = trich_dinh_danh(data)
    bc: dict = {"dashboard": dash.name, "nhom": nhom, "so_trich_dan": len(dd), "da_co": 0, "nhap_moi": 0,
                "pdf_dinh_kem": 0, "khong_lay_duoc": [], "chua_toan_van": 0, "dang_vao_nhom": 0,
                "kiem_trung": endnote is not None, "ap_dung": ap_dung,
                # Không thấy kho ⇒ CHƯA XÉT được PDF — khác hẳn «không có toàn văn» (lượt 11/10 từ worktree báo
                # «đính PDF 0» trong khi kho có sẵn PDF Wiley TDM của chủ đề).
                "kho_toan_van": bool(kho and kho.is_dir())}

    def ma_cua(d: dict, theo_pm: dict, theo_doi: dict) -> list[str]:
        return (theo_pm.get(d["pmid"]) if d.get("pmid") else None) or \
               (theo_doi.get(d["doi"]) if d.get("doi") else None) or []

    def cap_ban_ghi(theo_pm: dict, theo_doi: dict) -> list[tuple[dict, str]]:
        """Mỗi trích dẫn ↔ bản ghi ĐẦU TIÊN khớp (bản trùng sẵn có trong thư viện: chỉ dùng một), không lặp mã."""
        cap: list[tuple[dict, str]] = []
        thay: set[str] = set()
        for d in dd:
            for r in ma_cua(d, theo_pm, theo_doi)[:1]:
                if r not in thay:
                    thay.add(r)
                    cap.append((d, r))
        return cap

    theo_pm = endnote.tim_khop([d["pmid"] for d in dd if d.get("pmid")], "Accession Number") if endnote else {}
    theo_doi = endnote.tim_khop([d["doi"] for d in dd if d.get("doi")], "DOI") if endnote else {}
    moi = [d for d in dd if not ma_cua(d, theo_pm, theo_doi)]
    bc["da_co"] = len(dd) - len(moi)

    co, bc["khong_lay_duoc"] = lay_metadata(moi, lay_pm, lay_cr, lay_ep) if moi else ([], [])
    hom_nay = date.today().isoformat()
    can_nhap: list[dict] = []
    for d, m in co:
        m["tu_khoa"] = [f"EBM: {khoa}"]
        m["ghi_chu"] = (f"Nạp tự động bởi EBM Copilot ngày {hom_nay} từ {dash.name} "
                        f"({'mục ' + d['muc'] if d['vai'] == 'muc' else 'tham khảo của ' + d['muc']}). "
                        f"Metadata: {m['nguon_meta']}.")
        if m.get("da_rut"):
            m["nhan"] = "ĐÃ RÚT (PubMed)"
            m["ghi_chu"] += " CẢNH BÁO: PubMed gắn «Retracted Publication»."
        m["_pdf"] = chon_pdf(kho, m.get("pmid"))
        can_nhap.append(m)
    bc["nhap_moi"] = len(can_nhap)
    bc["pdf_dinh_kem"] = sum(1 for m in can_nhap if m["_pdf"])
    bc["chua_toan_van"] = len(can_nhap) - bc["pdf_dinh_kem"]
    if not ap_dung or endnote is None:
        bc["ke_hoach_nhap"] = [m.get("pmid") or m.get("doi") for m in can_nhap]
        if endnote is not None:  # chạy khô vẫn ĐỌC được trường đính kèm của bản ghi đã có (chỉ đọc)
            bc["se_gan_pdf"] = len(xet_toan_van(endnote, cap_ban_ghi(theo_pm, theo_doi), kho)[0])
        return bc

    thu_muc_moi: list[Path] = []
    try:
        for m in can_nhap:
            if m["_pdf"]:
                url, tm = dat_pdf_vao_thu_vien(endnote.thu_vien, m["_pdf"][0], m["pmid"])
                thu_muc_moi.append(tm)
                m["pdf_url"] = url
                m["ghi_chu"] += f" Toàn văn đính kèm: {m['_pdf'][1]}."
        if can_nhap:
            with tempfile.TemporaryDirectory(prefix="ebm-endnote-") as tam:
                tep = Path(tam) / "nhap.xml"
                tep.write_text(dung_xml(can_nhap), encoding="utf-8", newline="\n")
                endnote.nhap(tep)
    except Exception:
        for tm in thu_muc_moi:  # bước nhập hỏng ⇒ không để PDF mồ côi trong thư viện
            shutil.rmtree(tm, ignore_errors=True)
        raise

    theo_pm = endnote.tim_khop([d["pmid"] for d in dd if d.get("pmid")], "Accession Number")
    theo_doi = endnote.tim_khop([d["doi"] for d in dd if d.get("doi")], "DOI")
    cap = cap_ban_ghi(theo_pm, theo_doi)
    da_trong_nhom = set(endnote.thanh_vien_nhom(nhom))
    can_dang = [r for _, r in cap if r not in da_trong_nhom]
    endnote.dang_vao_nhom(can_dang, nhom)
    bc["dang_vao_nhom"] = len(can_dang)
    bc["trong_nhom_sau"] = len(da_trong_nhom) + len(can_dang)

    # Toàn văn về SAU khi trích dẫn đã nằm trong EndNote ⇒ gắn vào bản ghi chưa có tệp đính kèm nào.
    can_gan, bc["thieu_toan_van"] = xet_toan_van(endnote, cap, kho)
    _gan_pdf(endnote, can_gan)
    bc["gan_them_pdf"] = len(can_gan)
    return bc


def _in_bao_cao(bc: dict) -> None:
    if bc.get("loi"):
        print(f"✗ {bc['dashboard']}: {bc['loi']}")
        return
    dau = "✓" if not bc["khong_lay_duoc"] else "◐"
    print(f"{dau} {bc['dashboard']} → nhóm «{bc['nhom']}»")
    if not bc["kiem_trung"]:
        print("   (chưa mở EndNote nên CHƯA kiểm được bài nào đã có trong thư viện)")
    print(f"   {bc['so_trich_dan']} trích dẫn · đã có trong thư viện {bc['da_co']} · "
          f"{'nhập mới' if bc['ap_dung'] else 'sẽ nhập mới'} {bc['nhap_moi']} "
          f"(đính PDF {bc['pdf_dinh_kem']}, chưa có toàn văn {bc['chua_toan_van']})")
    if not bc["kho_toan_van"]:
        print("   ⚠ Không thấy kho toàn văn — CHƯA XÉT PDF (không phải «không có»); chỉ đường bằng --kho-toan-van")
    if bc.get("se_gan_pdf"):
        print(f"   Sẽ gắn toàn văn cho bản ghi đã có: {bc['se_gan_pdf']}")
    if bc["ap_dung"] and bc["kiem_trung"]:
        print(f"   Đăng thêm vào nhóm: {bc['dang_vao_nhom']} · nhóm hiện có {bc.get('trong_nhom_sau', '?')} bản ghi")
        print(f"   Gắn thêm toàn văn cho bản ghi đã có: {bc.get('gan_them_pdf', 0)}")
        thieu = bc.get("thieu_toan_van") or []
        if thieu:
            print(f"   Còn thiếu toàn văn trong EndNote: {len(thieu)} — {', '.join(thieu[:12])}"
                  f"{' …' if len(thieu) > 12 else ''}")
    if bc["khong_lay_duoc"]:
        print(f"   ⚠ Không lấy được metadata (KHÔNG nhập): {', '.join(bc['khong_lay_duoc'][:10])}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--file", nargs="*", default=[], help="dashboard WebDashboard_*.html")
    ap.add_argument("--tat-ca", action="store_true", help="mọi dashboard trong EBM-Dashboards/")
    ap.add_argument("--ap-dung", action="store_true", help="nạp thật vào EndNote (mặc định chạy khô)")
    ap.add_argument("--ten-nhom", help="đặt tên nhóm thay cho câu hỏi lâm sàng (chỉ khi một --file)")
    ap.add_argument("--xuat-xml", help="chỉ ghi tệp XML để nhập tay (máy không phải Mac)")
    ap.add_argument("--kho-toan-van", help="thư mục toan_van_oa (mặc định EBM-Dashboards/toan_van_oa)")
    ap.add_argument("--ghi-cau-hinh", metavar="THU_VIEN_ENL", help="ghi thư viện chính vào ~/.ebm-endnote.json")
    ap.add_argument("--ung-dung", default=UNG_DUNG_MAC_DINH, help="tên ứng dụng EndNote (đi cùng --ghi-cau-hinh)")
    ap.add_argument("--im-khi-chua-cau-hinh", action="store_true",
                    help="máy chưa cấu hình/không phải Mac thì in một dòng ⚪ và trả 0 (dùng trong bộ năm)")
    ap.add_argument("--gan-kho", action="store_true",
                    help="gắn PDF trong kho vào bản ghi ĐÃ có trong thư viện cùng PMID (không cần dashboard)")
    ap.add_argument("--pmid", nargs="*", help="cùng --gan-kho: chỉ xét các PMID này")
    ap.add_argument("--chi-khi-dang-mo", action="store_true",
                    help="EndNote chưa mở đúng thư viện thì in ⚪ và trả 0 — KHÔNG tự mở EndNote (công cụ khác gọi)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.ghi_cau_hinh:
        try:
            ch = ghi_cau_hinh(a.ghi_cau_hinh, a.ung_dung)
        except ValueError as e:
            print(f"✗ {e}")
            return MA_THAM_SO
        print(f"✓ Đã ghi {CAU_HINH}: thư viện {ch['thu_vien']} · ứng dụng {ch['ung_dung']}")
        return MA_OK

    bst_sp = importlib.util.spec_from_file_location("_bst_endnote", ROOT / "tools" / "ban_sao_tran.py")
    bst = importlib.util.module_from_spec(bst_sp)
    bst_sp.loader.exec_module(bst)
    dash_goc = bst.duong_goc("EBM-Dashboards", ROOT)
    files = [Path(f) for f in a.file]
    if a.tat_ca:
        if dash_goc is None:
            print("✗ không thấy thư mục EBM-Dashboards/ (bản sao trần?) — dùng --file")
            return MA_KHONG_CHAY
        files += sorted(dash_goc.glob("WebDashboard_*.html"))
    if not files and not a.gan_kho:
        ap.print_usage()
        return MA_THAM_SO
    if a.gan_kho and (files or a.xuat_xml):
        print("✗ --gan-kho không đi cùng --file/--tat-ca/--xuat-xml")
        return MA_THAM_SO
    if a.ten_nhom and len(files) != 1:
        print("✗ --ten-nhom chỉ dùng với đúng một --file")
        return MA_THAM_SO
    kho = Path(a.kho_toan_van) if a.kho_toan_van else (dash_goc / "toan_van_oa" if dash_goc else None)

    if a.xuat_xml:
        # Đường cho máy không phải Mac: một tệp XML để nhập tay; không đính PDF (không có đường vào thư viện).
        doc = _nap_doc_data()
        tat_ca: list[dict] = []
        thieu: list[str] = []
        for f in files:
            co, th = lay_metadata(trich_dinh_danh(doc(f) or {}))
            thieu += th
            tat_ca += [dict(m, tu_khoa=[f"EBM: {khoa_chu_de(f)}"], ghi_chu=f"Từ {f.name}.") for _, m in co]
        Path(a.xuat_xml).write_text(dung_xml(tat_ca), encoding="utf-8", newline="\n")
        print(f"✓ Đã ghi {a.xuat_xml}: {len(tat_ca)} bản ghi — EndNote: File → Import → «EndNote generated XML»."
              " Nhóm theo chủ đề: tạo Smart Group theo từ khoá «EBM: …».")
        if thieu:
            print(f"⚠ Không lấy được metadata (không ghi vào tệp): {', '.join(thieu[:10])}")
        return MA_MOT_PHAN if thieu else MA_OK

    ch = doc_cau_hinh()
    endnote = None
    try:
        if ch is None:
            raise KhongChayDuoc("chưa cấu hình thư viện EndNote — chạy --ghi-cau-hinh "
                                f"\"<đường dẫn .enl>\" ({CAU_HINH})")
        thu_vien = Path(ch["thu_vien"])
        if not thu_vien.is_file():
            raise KhongChayDuoc(f"thư viện đã cấu hình không còn tồn tại: {thu_vien}")
        endnote = EndNoteMac(ch["ung_dung"], thu_vien)
        if not endnote.dang_mo_dung_thu_vien():
            if a.chi_khi_dang_mo:  # công cụ khác gọi giữa chừng: không bao giờ tự bật EndNote lên màn hình bác sĩ
                print(f"⚪ EndNote chưa mở thư viện {thu_vien.name} — bỏ qua, lần nạp sau sẽ gắn.")
                return MA_OK
            if a.ap_dung:
                endnote.mo_thu_vien()
            else:
                print(f"⚪ EndNote chưa mở thư viện {thu_vien.name} — chạy khô không kiểm được bài đã có.")
                endnote = None
    except KhongChayDuoc as e:
        if a.im_khi_chua_cau_hinh:
            print(f"⚪ EndNote: bỏ qua — {e}")
            return MA_OK
        if a.ap_dung:
            print(f"✗ {e}")
            return MA_KHONG_CHAY
        print(f"⚪ {e} — chỉ lập kế hoạch.")
        endnote = None

    if a.gan_kho:
        if endnote is None:
            print("⚪ --gan-kho cần EndNote đang mở đúng thư viện — chưa gắn gì.")
            return MA_OK if a.chi_khi_dang_mo else MA_KHONG_CHAY
        try:
            bc = gan_kho(endnote, kho, a.pmid, a.ap_dung)
        except (RuntimeError, OSError) as e:
            print(f"✗ gắn toàn văn từ kho: {type(e).__name__}: {e}"[:300])
            return MA_KHONG_CHAY
        if not bc["kho_toan_van"]:
            print("⚠ Không thấy kho toàn văn — CHƯA XÉT PDF; chỉ đường bằng --kho-toan-van")
        else:
            gan = bc.get("gan_them_pdf", bc.get("se_gan_pdf", 0))
            print(f"✓ EndNote · kho: {bc['pdf_trong_kho']} PMID có PDF · {bc['co_ban_ghi']} có bản ghi trong thư viện · "
                  f"{'gắn thêm' if a.ap_dung else 'sẽ gắn'} {gan}")
        if a.json:
            print(json.dumps(bc, ensure_ascii=False, indent=2))
        return MA_OK

    doc = _nap_doc_data()
    ket_qua = []
    for f in files:
        try:
            bc = nap_chu_de(f, endnote=endnote, ap_dung=a.ap_dung, kho=kho, doc_data=doc, ten_nhom=a.ten_nhom)
        except (RuntimeError, OSError) as e:
            bc = {"dashboard": f.name, "loi": f"{type(e).__name__}: {e}"[:300]}
        ket_qua.append(bc)
        _in_bao_cao(bc)
    if a.ap_dung and endnote is not None and any(b.get("thieu_toan_van") for b in ket_qua):
        print("Toàn văn còn thiếu — làn kế tiếp, rồi chạy lại lệnh này để gắn PDF mới vào nhóm:\n"
              "  1. python3 tools/gom_toan_van_dashboard.py --file <dashboard> --unpaywall   (bản truy cập mở)\n"
              "  2. python3 tools/doc_toan_van_co_nguoi.py --pmid <PMID…>   (bài thuê bao: làn Chrome có uỷ quyền,\n"
              "     bác sĩ tự đăng nhập/vượt chặn; công cụ này không tải bài thuê bao)\n"
              "  3. hoặc trong EndNote: chọn nhóm «EBM · …» → References → Find Full Text (quyền truy cập của bác sĩ).")
    if not a.ap_dung:
        print("Chạy khô — chưa nhập gì. Thêm --ap-dung để nạp thật.")
    if a.json:
        print(json.dumps(ket_qua, ensure_ascii=False, indent=2, default=str))
    if any(b.get("loi") for b in ket_qua):
        return MA_KHONG_CHAY
    return MA_MOT_PHAN if any(b.get("khong_lay_duoc") for b in ket_qua) else MA_OK


if __name__ == "__main__":
    sys.exit(main())
