#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RÀ ĐỊNH DANH KHO TOÀN VĂN — mỗi PDF ĐÃ nằm trong `EBM-Dashboards/toan_van_oa/` có đúng là bài mà tên tệp khai không (03/11/2026).

VÌ SAO CÓ. BH175 (`audit/nhat-ky/2026-11-02-unpaywall-pdf-sai-bai.md`) thêm cổng định danh vào tầng Unpaywall, nhưng cổng chỉ gác
tệp MỚI tải về. Tệp vào kho TRƯỚC đó chưa ai kiểm: đo 03/11 bằng tiêu đề lấy từ dashboard ra 2 tệp sai bài (39186635, 42701440) và
37 tệp không có dữ kiện để kiểm. Cổng BH161 (`verify_dashboard.co_toan_van_trong_kho`) coi mọi tệp đặt tên hợp lệ là «đã đọc toàn
văn», bước ⑧ gắn tệp vào EndNote — một tệp sai bài lặng lẽ thành «chứng cứ đã đọc» (`audit/nhat-ky/2026-11-03-ra-dinh-danh-kho-toan-van.md`).

LÀM GÌ. Với mỗi `PMID-<n>_<HẬU TỐ>.pdf` (mọi hậu tố có trong kho: UPW · CHR · WTDM · BANIN …) và `zenodo_hub_*/DOI-*.pdf`:
  1. Định danh lấy từ NGUỒN, không từ trí nhớ hay dashboard: PubMed esummary (tiêu đề tiếng Anh, tiêu đề nguyên ngữ, DOI); NCBI
     chặn/lỗi ⇒ Europe PMC. Tệp Zenodo đặt tên theo DOI: sổ tải `_tai_ve.json` ghi lúc tải (DOI + tiêu đề của Zenodo).
  2. Gọi ĐÚNG cổng `gom_toan_van_dashboard.kiem_dinh_danh_upw()` (BH175; luật `khop_dinh_danh` của bước ⑨) — trước bằng tiêu đề,
     sau bằng DOI. Khớp CHỈ nhờ DOI ⇒ đối chiếu DOI với Crossref (DOI PubMed có đúng là của bài này?). Lệch tiêu đề ⇒ thử tiêu đề
     nguyên ngữ và tiêu đề Crossref trước khi kết luận «sai bài».
  3. Bốn nhóm: KHỚP · SAI BÀI · KHÔNG KIỂM ĐƯỢC (PDF ảnh/hỏng, không có bản ghi/tiêu đề, DOI lệch Crossref) · KHÔNG ĐO ĐƯỢC (lỗi
     mạng, thiếu pypdf, không đọc được tệp). Lỗi mạng KHÔNG BAO GIỜ thành «khớp».
  4. In báo cáo + ghi `EBM-Dashboards/RA-DINH-DANH-KHO-TOAN-VAN.md` (cạnh kho; lượt chỉ rà một phần ghi `…-MOT-PHAN.md`). Tệp sai
     bài kèm đoạn đầu trang 1 (tệp thực ra là bài gì) và bản ghi EndNote đang gắn tệp đó — đọc BẢN SAO TẠM của `sdb.eni`
     (`endnote_suc_khoe.ban_sao_csdl`), so mã băm tệp đính kèm với tệp kho.

KHÔNG LÀM GÌ. Chạy khô (mặc định) không dời/sửa/xoá tệp nào. Không ghi EndNote (gỡ đính kèm là việc của bác sĩ). Không rà HTML/XML.
`--cach-ly --ap-dung` DỜI (không xoá) tệp bị kết luận SAI BÀI ở CHÍNH lượt này sang `EBM-Dashboards/_cach-ly-toan-van-sai-bai/`,
ghi lý do vào README.txt; bản in `_BANIN.pdf` sai bài ⇒ dời cả tệp nguồn ghi trên dải đầu trang (không thì lượt in sau in lại
đúng tệp sai). CHỈ chạy khi bác sĩ đã duyệt danh sách; `--pmid` giới hạn đúng các PMID đã duyệt.

Chạy:  python3 tools/ra_dinh_danh_kho_toan_van.py                              # rà cả kho, chạy khô
       python3 tools/ra_dinh_danh_kho_toan_van.py --hau-to UPW CHR WTDM         # chỉ vài hậu tố
       python3 tools/ra_dinh_danh_kho_toan_van.py --kho "<GỐC>/EBM-Dashboards/toan_van_oa"   # chạy từ worktree
       python3 tools/ra_dinh_danh_kho_toan_van.py --cach-ly                      # xem trước tệp sẽ dời
       python3 tools/ra_dinh_danh_kho_toan_van.py --cach-ly --ap-dung --pmid 39186635 42701440
Mã thoát: 0 mọi tệp kiểm được đều khớp · 1 có tệp SAI BÀI · 2 có tệp KHÔNG ĐO ĐƯỢC (không có tệp sai bài) hoặc thiếu kho ·
3 tham số sai. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import http.client
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CROSSREF = "https://api.crossref.org/works/"
UA = "EBM-ra-dinh-danh-kho/1.0 (https://github.com/drluanbv175)"
LO_NCBI = 150   # PMID mỗi lượt esummary (GET; 150 × 9 chữ số vẫn dưới trần độ dài URL)
LO_EPMC = 40    # PMID mỗi truy vấn Europe PMC (EXT_ID:a OR EXT_ID:b …)
NGHI_NCBI = 0.4  # giây giữa hai lượt NCBI khi không có khoá API (trần 3 lượt/giây)
NGUONG_TIEU_DE = 0.6  # cùng ngưỡng của `khop_dinh_danh` — dùng để so tiêu đề PubMed với tiêu đề Crossref
TEN_BAO_CAO = "RA-DINH-DANH-KHO-TOAN-VAN.md"
TEN_BAO_CAO_MOT_PHAN = "RA-DINH-DANH-KHO-TOAN-VAN-MOT-PHAN.md"
THU_MUC_CACH_LY = "_cach-ly-toan-van-sai-bai"
MAU_PMID = re.compile(r"^PMID-(\d{1,9})_([A-Za-z0-9]+)\.pdf$")
MAU_DOI_ZENODO = re.compile(r"^DOI-(10\.\d{4,9}_.+)\.pdf$")
MAU_NGUON_BAN_IN = re.compile(r"(PMID-\d{1,9}_[A-Za-z0-9]+\.(?:xml|html))")  # dải đầu trang của bản in: «nguồn: PMID-…_PMC….xml»
MAU_TEP_ENDNOTE = re.compile(r"^PMID-(\d{1,9})(?:[._-][^/]*)?\.pdf$", re.I)  # tên bước ⑧ đặt cho tệp gắn kho: PMID-<n>.pdf
TRAN_REC = 200_000  # trần rowid khi quét từng dòng mà không đọc được max(id)

KHOP, SAI_BAI, KHONG_KIEM_DUOC, KHONG_DO_DUOC = "khop", "sai_bai", "khong_kiem_duoc", "khong_do_duoc"
NHAN_NHOM = {KHOP: "✅ Khớp", SAI_BAI: "❌ Sai bài", KHONG_KIEM_DUOC: "⚪ Không kiểm được", KHONG_DO_DUOC: "🟡 Không đo được"}


def _nap(tep: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


g = _nap("gom_toan_van_dashboard.py", "_gom_ra_dinh_danh")  # cổng BH175 + định vị kho + email lịch sự


def _sk():
    """`endnote_suc_khoe` (bản sao tạm sdb.eni) — nạp khi cần: máy không có EndNote vẫn rà được kho."""
    return _nap("endnote_suc_khoe.py", "_sk_ra_dinh_danh")


class KetQua:
    """Kết luận cho MỘT tệp PDF của kho. Lớp thường, không dùng @dataclass: các công cụ nạp nhau qua importlib mà không đăng ký
    `sys.modules`, dataclass (Python 3.14) khi đó vỡ lúc nạp."""

    def __init__(self, tep: Path, hau_to: str, pmid: str | None = None, doi: str = ""):
        self.tep, self.hau_to, self.pmid, self.doi = tep, hau_to, pmid, doi
        self.tieu_de = self.nguon_dinh_danh = self.can_cu = self.ly_do = self.dau_trang = self.nguon_ban_in = ""
        self.nhom = KHONG_DO_DUOC
        self.ghi_chu: list[str] = []
        self.doi_trong_tep: list[str] = []
        self.endnote: list[dict] = []


# ───────────────────────── liệt kê kho ─────────────────────────

def liet_ke_pdf(kho: Path, hau_to: set[str] | None = None, pmids: set[str] | None = None) -> tuple[list[KetQua], list[Path]]:
    """Mọi PDF của kho: (tệp sẽ rà, PDF KHÔNG nhận dạng được tên — báo riêng, không lặng lẽ bỏ). Bản cách ly (`.pdf.SAI-BAI-…`)
    không còn đuôi `.pdf` nên không bị rà lại."""
    ra, la = [], []
    for p in sorted(kho.iterdir(), key=lambda x: x.name):
        if p.is_file() and p.suffix.lower() == ".pdf":
            m = MAU_PMID.match(p.name)
            if not m:
                la.append(p)
            elif (not hau_to or m.group(2).upper() in hau_to) and (not pmids or m.group(1) in pmids):
                ra.append(KetQua(tep=p, hau_to=m.group(2).upper(), pmid=m.group(1)))
        elif p.is_dir() and p.name.startswith("zenodo_hub_"):
            for q in sorted(p.glob("*.pdf"), key=lambda x: x.name):
                m = MAU_DOI_ZENODO.match(q.name)
                if not m:
                    la.append(q)
                elif (not hau_to or "ZENODO" in hau_to) and not pmids:
                    ra.append(KetQua(tep=q, hau_to="ZENODO", doi=m.group(1).replace("_", "/", 1)))
    return ra, la


# ───────────────────────── định danh từ nguồn ─────────────────────────

def _lay(url: str, *, timeout: int = 30, so_lan: int = 3) -> bytes:
    """GET có thử lại: lỗi mạng/5xx/429 thử 3 lần (nghỉ 1–2 giây); 400/404/410 ném ngay — đó là câu trả lời, không phải lỗi mạng."""
    for lan in range(so_lan):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as ph:
                return ph.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 404, 410) or lan + 1 >= so_lan:
                raise
        except (OSError, http.client.HTTPException) as exc:  # URLError, timeout, đứt kết nối, IncompleteRead
            if lan + 1 >= so_lan:
                raise exc if isinstance(exc, OSError) else OSError(f"{type(exc).__name__}: {exc}")
        time.sleep(2 ** lan)
    raise OSError("không lấy được " + url)  # không tới được — vòng lặp luôn trả hoặc ném


def _sach(s) -> str:
    """Tiêu đề từ API: bỏ thẻ (<i>…), giải mã thực thể, gộp khoảng trắng, bỏ dấu chấm cuối của PubMed."""
    s = html.unescape(re.sub(r"<[^>]+>", "", str(s or "")))
    return re.sub(r"\s+", " ", s).strip().rstrip(".").strip()


def _tu_pubmed(pmids: list[str], email: str, trang_thai: dict) -> dict[str, dict]:
    """esummary theo lô. Trả {pmid: định danh} cho PMID PubMed TRẢ LỜI được (có bản ghi hoặc báo không có). Lô lỗi mạng ⇒ bỏ trống
    (người gọi chuyển sang Europe PMC). Trang chặn của NCBI ⇒ dừng gọi NCBI cả lượt (`trang_thai["ncbi_chan"]`)."""
    ra: dict[str, dict] = {}
    for i in range(0, len(pmids), LO_NCBI):
        if trang_thai.get("ncbi_chan"):
            break
        lo = pmids[i:i + LO_NCBI]
        url = (f"{ESUMMARY}?db=pubmed&retmode=json&tool=ebm-ra-dinh-danh&email={urllib.parse.quote(email)}"
               f"&id={','.join(lo)}")
        try:
            b = _lay(url)
        except OSError as exc:
            trang_thai.setdefault("loi_ncbi", []).append(type(exc).__name__)
            continue
        if g.la_trang_chan_ncbi(b):
            trang_thai["ncbi_chan"] = True
            print("  ⚠ NCBI đang chặn IP này (trang «Blocked Diagnostic») — phần còn lại lấy qua Europe PMC", file=sys.stderr)
            break
        try:
            kq = json.loads(b)["result"]
        except (ValueError, KeyError, TypeError):
            trang_thai.setdefault("loi_ncbi", []).append("JSON hỏng")
            continue
        for pm in lo:
            m = kq.get(pm)
            if not isinstance(m, dict):
                continue
            if m.get("error"):
                ra[pm] = {"trang_thai": "khong_co", "nguon": "PubMed",
                          "ly_do": f"PubMed và Europe PMC không có bản ghi PMID này (PubMed: {m.get('error')})"}
                continue
            doi = next((str(x.get("value") or "") for x in m.get("articleids") or [] if x.get("idtype") == "doi"), "")
            ra[pm] = {"trang_thai": "ok", "nguon": "PubMed", "doi": doi.strip(), "tieu_de": _sach(m.get("title")),
                      "tieu_de_goc": _sach(m.get("vernaculartitle"))}
        time.sleep(NGHI_NCBI)
    return ra


def _tu_epmc(pmids: list[str]) -> dict[str, dict]:
    """Europe PMC (`EXT_ID:<pmid> AND SRC:MED`) theo lô. Lô trả lời được mà thiếu PMID ⇒ «khong_co»; lô lỗi mạng ⇒ bỏ trống."""
    ra: dict[str, dict] = {}
    for i in range(0, len(pmids), LO_EPMC):
        lo = pmids[i:i + LO_EPMC]
        q = "(" + " OR ".join(f"EXT_ID:{p}" for p in lo) + ") AND SRC:MED"
        url = f"{EPMC_SEARCH}?resultType=lite&format=json&pageSize=100&query={urllib.parse.quote(q)}"
        try:
            js = json.loads(_lay(url, timeout=40))
            hang = (js.get("resultList") or {}).get("result") or []
        except (OSError, ValueError, AttributeError):
            continue
        theo = {str(r.get("pmid") or r.get("id") or ""): r for r in hang if isinstance(r, dict)}
        for pm in lo:
            r = theo.get(pm)
            if r is None:
                ra[pm] = {"trang_thai": "khong_co", "nguon": "Europe PMC", "ly_do": "Europe PMC không có bản ghi"}
            else:
                ra[pm] = {"trang_thai": "ok", "nguon": "Europe PMC", "doi": str(r.get("doi") or "").strip(),
                          "tieu_de": _sach(r.get("title")), "tieu_de_goc": ""}
    return ra


def lay_dinh_danh(pmids: list[str], *, email: str | None = None) -> tuple[dict[str, dict], dict]:
    """Định danh của từng PMID: PubMed trước, Europe PMC cho phần PubMed không trả lời được hoặc báo không có. Hai nguồn đều lỗi
    mạng ⇒ {"trang_thai": "loi"} — KHÔNG ĐO ĐƯỢC, không bao giờ coi là khớp. Trả (định danh, trạng thái nguồn để báo cáo)."""
    email = email if email is not None else g._email_lich_su()
    trang_thai: dict = {}
    pmids = sorted(set(pmids), key=int)
    ra = _tu_pubmed(pmids, email, trang_thai) if email else {}
    if not email:
        trang_thai["ncbi_bo_qua"] = "thiếu email định danh (NCBI_EMAIL) — dùng Europe PMC"
    con = [p for p in pmids if ra.get(p, {}).get("trang_thai") != "ok"]
    if con:
        for pm, md in _tu_epmc(con).items():
            if md["trang_thai"] == "ok" or pm not in ra:
                ra[pm] = md
    for pm in pmids:
        ra.setdefault(pm, {"trang_thai": "loi", "nguon": "", "ly_do": "PubMed và Europe PMC đều không trả lời (lỗi mạng)"})
    return ra, trang_thai


def tieu_de_crossref(doi: str, email: str, bo_nho: dict) -> tuple[str, str]:
    """(tiêu đề, trạng thái ∈ ok · khong_co · loi) của một DOI trên Crossref; nhớ trong lượt."""
    if doi not in bo_nho:
        url = CROSSREF + urllib.parse.quote(doi, safe="/") + (f"?mailto={urllib.parse.quote(email)}" if email else "")
        try:
            msg = json.loads(_lay(url)).get("message") or {}
            t = msg.get("title") or []
            bo_nho[doi] = (_sach(t[0]), "ok") if t else ("", "khong_co")
        except urllib.error.HTTPError as exc:
            bo_nho[doi] = ("", "khong_co" if exc.code == 404 else "loi")
        except (OSError, ValueError, AttributeError):
            bo_nho[doi] = ("", "loi")
    return bo_nho[doi]


def dinh_danh_zenodo(tep: Path) -> dict:
    """Tiêu đề của tệp `DOI-*.pdf` từ sổ tải `_tai_ve.json` cùng thư mục (ghi từ API Zenodo lúc tải)."""
    try:
        so = json.loads((tep.parent / "_tai_ve.json").read_text(encoding="utf-8"))
        muc = next((m for m in so if isinstance(m, dict) and m.get("tep") == tep.name), None)
    except (OSError, ValueError, TypeError):
        muc = None
    if not muc:
        return {"trang_thai": "khong_co", "nguon": "sổ tải Zenodo", "ly_do": "sổ tải _tai_ve.json không có tệp này"}
    return {"trang_thai": "ok", "nguon": "sổ tải Zenodo", "doi": str(muc.get("doi") or ""), "tieu_de": _sach(muc.get("title")),
            "tieu_de_goc": ""}


# ───────────────────────── kiểm một tệp ─────────────────────────

def _tu(s: str) -> set[str]:
    tt = g._nap_ttcc()
    return {w for w in re.findall(r"[a-z0-9]+", tt._chuan_chu(s or "")) if len(w) >= 4}


def cung_tieu_de(a: str, b: str) -> bool:
    """Hai tiêu đề có phải của cùng một bài: ≥ 60% từ (≥ 4 chữ) của tiêu đề NGẮN HƠN có trong tiêu đề kia (cùng cách tách từ và
    ngưỡng của `khop_dinh_danh`; một bên có phụ đề, bên kia không — vẫn là một bài)."""
    ta, tb = _tu(a), _tu(b)
    if not ta or not tb:
        return False
    nho, lon = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return len(nho & lon) / len(nho) >= NGUONG_TIEU_DE


def _kiem(du_lieu: bytes, *, doi: str = "", tieu_de: str = "") -> tuple[str, str]:
    return g.kiem_dinh_danh_upw(du_lieu, loai="pdf", doi=doi, tieu_de=tieu_de)


def _xet_lai_truoc_sai_bai(kq: KetQua, du_lieu: bytes, md: dict) -> str:
    """Lý do HẠ «sai bài» xuống «không kiểm được», hoặc "" (giữ sai bài). Chỉ hạ, KHÔNG BAO GIỜ nâng lên «khớp». Hai ca đo 03/11:
    • bản in BANIN cụt: `PMID-32568065_BANIN.pdf` 1 trang chỉ in mục «Notes» của báo cáo HTA, trong khi tệp nguồn `_CHR.html` là
      toàn văn đúng bài (23 570 từ) — xét lại trên TỆP NGUỒN ghi ở dải đầu trang bằng cùng cổng BH175 (loai jats/html);
    • PDF quét có chân trang chữ: `PMID-2899840_CHR.pdf` (NEJM 1988) mỗi trang chỉ có dòng «Downloaded from nejm.org…» (28 từ) —
      đủ vượt ngưỡng «PDF ảnh» 50 từ của cổng nên bị kết luận sai bài. Bỏ các dòng lặp ở ≥ 2 trong 3 trang đầu rồi đếm lại."""
    try:
        trang = g._nap_ttcc().tach_trang(du_lieu)
    except Exception:  # noqa: BLE001 — cổng đã đọc được tệp này; lỗi ở đây chỉ làm mất phép xét lại
        return ""
    if kq.hau_to == "BANIN" and trang:
        m = MAU_NGUON_BAN_IN.search(trang[0])
        nguon = kq.tep.parent / m.group(1) if m else None
        try:
            b = nguon.read_bytes() if nguon and nguon.is_file() else None
        except OSError:
            b = None
        if b is not None:
            loai = "jats" if nguon.suffix.lower() == ".xml" else "html"
            for td, doi in [(t, "") for t in (kq.tieu_de, md.get("tieu_de_goc")) if t] + ([("", kq.doi)] if kq.doi else []):
                kl, ly = g.kiem_dinh_danh_upw(b, loai=loai, doi=doi, tieu_de=td)
                if kl == "dung":
                    return (f"bản in ({len(trang)} trang, {len(' '.join(trang).split())} từ) không mang tiêu đề/DOI ở 3 trang đầu "
                            f"nhưng tệp nguồn {nguon.name} KHỚP bài ({ly}) — bản in có thể cụt, nên in lại; tệp nguồn giữ nguyên")
    dau = trang[:3]
    if len(dau) >= 2:
        dong = [[" ".join(d.split()) for d in t.splitlines() if d.strip()] for t in dau]
        dem: dict[str, int] = {}
        for ds in dong:
            for d in set(ds):
                dem[d] = dem.get(d, 0) + 1
        rieng = " ".join(d for ds in dong for d in ds if dem[d] < 2)
        if len(rieng.split()) < g.SO_TU_TOI_THIEU_DINH_DANH:
            mau = next((d for ds in dong for d in ds), "")
            return (f"lớp chữ của 3 trang đầu chỉ có dòng lặp ở mọi trang («{mau[:70]}») — PDF quét, không đối chiếu được tiêu đề")
    return ""


def kiem_tep(kq: KetQua, md: dict, *, crossref) -> KetQua:
    """Kết luận cho một tệp. `md` = định danh từ nguồn; `crossref(doi) -> (tiêu đề, trạng thái)`. Chỉ đường «dung» của cổng
    BH175 dẫn tới KHỚP; lỗi mạng/thiếu công cụ dẫn tới KHÔNG ĐO ĐƯỢC. Thứ tự thử: tiêu đề PubMed → tiêu đề nguyên ngữ (PubMed) →
    DOI (đối chiếu Crossref) → tiêu đề Crossref (chỉ khi cùng bài với tiêu đề PubMed) → xét lại trước khi kết luận sai bài."""
    kq.nguon_dinh_danh = md.get("nguon", "")
    if md.get("trang_thai") == "loi":
        kq.nhom, kq.ly_do = KHONG_DO_DUOC, md.get("ly_do") or "chưa lấy được định danh (lỗi mạng)"
        return kq
    if md.get("trang_thai") != "ok":
        kq.nhom, kq.ly_do = KHONG_KIEM_DUOC, md.get("ly_do") or "không có bản ghi định danh"
        return kq
    kq.doi = md.get("doi") or kq.doi
    kq.tieu_de = md.get("tieu_de") or ""
    goc = md.get("tieu_de_goc") or ""
    ten_pubmed = [t for t in (kq.tieu_de, goc) if t]
    try:
        du_lieu = kq.tep.read_bytes()
    except OSError as exc:
        kq.nhom, kq.ly_do = KHONG_DO_DUOC, f"không đọc được tệp ({type(exc).__name__})"
        return kq
    if b"%PDF-" not in du_lieu[:1024]:
        kq.nhom, kq.ly_do = KHONG_KIEM_DUOC, f"tệp không phải PDF (đầu tệp {du_lieu[:12]!r})"
        return kq
    kl, ly = _kiem(du_lieu, tieu_de=kq.tieu_de)
    if kl == "thieu_cong_cu":
        kq.nhom, kq.ly_do = KHONG_DO_DUOC, ly
        return kq
    if kl == "dung":
        kq.nhom, kq.can_cu, kq.ly_do = KHOP, f"tiêu đề {kq.nguon_dinh_danh}", ly
        return kq
    if kl == "khong_kiem_duoc" and kq.tieu_de:  # có tiêu đề mà vẫn không kiểm được ⇒ PDF ảnh/hỏng — DOI cũng không cứu được
        kq.nhom, kq.ly_do = KHONG_KIEM_DUOC, ly
        return kq
    ly_tieu_de = ly
    # Bài không phải tiếng Anh: PubMed ghi tiêu đề DỊCH «[…]», PDF in tiêu đề nguyên ngữ (đo 03/11: 41494416, 42162485, 42809786).
    if goc and goc != kq.tieu_de:
        kl, ly = _kiem(du_lieu, tieu_de=goc)
        if kl == "dung":
            kq.nhom, kq.can_cu, kq.ly_do = KHOP, "tiêu đề nguyên ngữ", ly
            return kq
        if not kq.tieu_de:
            ly_tieu_de = f"tiêu đề nguyên ngữ: {ly}"
    ct, tt_cr = "", ""
    if kq.doi:
        kl2, ly2 = _kiem(du_lieu, doi=kq.doi)
        if kl2 == "thieu_cong_cu":
            kq.nhom, kq.ly_do = KHONG_DO_DUOC, ly2
            return kq
        ct, tt_cr = crossref(kq.doi)
        cung_bai = not ten_pubmed or tt_cr != "ok" or any(cung_tieu_de(t, ct) for t in ten_pubmed)
        if kl2 == "dung":
            if not cung_bai:
                kq.nhom = KHONG_KIEM_DUOC
                kq.ly_do = (f"DOI {kq.doi} có trong PDF nhưng tiêu đề lệch ({ly_tieu_de}) và Crossref ghi DOI này cho «{ct}» — "
                            "DOI của bản ghi có thể không thuộc bài này")
                return kq
            kq.nhom, kq.can_cu, kq.ly_do = KHOP, "chỉ DOI", f"{ly2}; tiêu đề: {ly_tieu_de}"
            if tt_cr == "ok":
                kq.ghi_chu.append("Crossref: DOI cùng tiêu đề" if ten_pubmed else f"Crossref: «{ct}»")
            else:
                kq.ghi_chu.append("Crossref: không có DOI này" if tt_cr == "khong_co" else "Crossref: KHÔNG ĐO ĐƯỢC (lỗi mạng)")
            return kq
        if ct and ct not in ten_pubmed:
            kl3, ly3 = _kiem(du_lieu, tieu_de=ct)
            if kl3 == "dung" and not cung_bai:
                # Tệp khớp bài mà Crossref ghi cho DOI này, nhưng bài đó KHÔNG phải bài PubMed ghi cho PMID: DOI của bản ghi
                # trỏ nhầm, hoặc tệp là bài kia — không bao giờ tính «khớp».
                kq.nhom = KHONG_KIEM_DUOC
                kq.ly_do = (f"tệp khớp «{ct}» — bài Crossref ghi cho DOI {kq.doi} — nhưng PubMed ghi PMID này cho «{kq.tieu_de}» "
                            f"({ly_tieu_de}); DOI của bản ghi hoặc tệp cần bác sĩ xem")
                return kq
            if kl3 == "dung":
                kq.nhom, kq.can_cu, kq.ly_do = KHOP, "tiêu đề Crossref", ly3
                if not ten_pubmed:
                    kq.ghi_chu.append("không có tiêu đề PubMed để đối chiếu tiêu đề Crossref")
                return kq
            if not ten_pubmed:
                ly_tieu_de = f"tiêu đề Crossref: {ly3}"
    if not ten_pubmed and not ct:
        kq.nhom, kq.ly_do = KHONG_KIEM_DUOC, "không có tiêu đề để đối chiếu và DOI không có trong PDF"
        return kq
    ha = _xet_lai_truoc_sai_bai(kq, du_lieu, md)
    if ha:
        kq.nhom, kq.ly_do = KHONG_KIEM_DUOC, ha
        return kq
    kq.nhom = SAI_BAI
    kq.ly_do = ly_tieu_de + ("; DOI không có trong PDF" if kq.doi else "; bản ghi không có DOI")
    if tt_cr == "loi":
        kq.ghi_chu.append("Crossref: KHÔNG ĐO ĐƯỢC (lỗi mạng) — chưa thử tiêu đề Crossref")
    return kq


def mo_ta_tep(kq: KetQua) -> None:
    """Tệp sai bài thực ra là gì: ~40 từ đầu trang 1, DOI thấy ở 2 trang đầu, tệp nguồn của bản in BANIN (dải đầu trang)."""
    try:
        trang = g._nap_ttcc().tach_trang(kq.tep.read_bytes())
    except Exception:  # noqa: BLE001 — chỉ là phần mô tả thêm; kết luận đã có
        return
    dau = " ".join(trang[:2])
    t1 = trang[0] if trang else ""
    if "phân phối lại" in t1:  # bản in BANIN: bỏ dải ghi nguồn để thấy chữ của chính bài
        t1 = t1.split("phân phối lại", 1)[1].lstrip(" .")
    kq.dau_trang = " ".join(t1.split()[:40])
    kq.doi_trong_tep = sorted({d.rstrip(".,;)") for d in re.findall(r"10\.\d{4,9}/[^\s\"<>]+", dau)})[:5]
    m = MAU_NGUON_BAN_IN.search(dau)
    if m:
        kq.nguon_ban_in = m.group(1)


# ───────────────────────── EndNote (chỉ đọc bản sao tạm) ─────────────────────────

def _sha(p: Path) -> str | None:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return None


def rec_theo_pmid(kn, pmids: set[str]) -> tuple[dict[str, list[tuple]], int]:
    """{pmid: [(rec, tiêu đề, thùng rác?)]} theo `accession_number`. Quét bảng lỗi (sdb.eni đang được EndNote ghi dở — đo 03/11:
    «database disk image is malformed» khi quét toàn bảng) ⇒ đọc từng dòng theo rowid, bỏ qua dòng lỗi. Trả (kết quả, số dòng lỗi)."""
    ra: dict[str, list[tuple]] = {}
    if not pmids:
        return ra, 0
    try:
        dau = ",".join("?" * len(pmids))
        for rec, acc, td, rac in kn.execute(
                f"select id, accession_number, title, trash_state from refs where accession_number in ({dau})", sorted(pmids)):
            ra.setdefault(str(acc).strip(), []).append((rec, td or "", bool(rac)))
        return ra, 0
    except sqlite3.DatabaseError:
        ra = {}
    tran = 0
    for q in ("select max(id) from refs", "select seq from sqlite_sequence where name = 'refs'"):  # đo 03/11: max(id) lỗi,
        try:                                                                                      # sqlite_sequence đọc được
            tran = int((kn.execute(q).fetchone() or [0])[0] or 0)
            break
        except (sqlite3.DatabaseError, TypeError, ValueError):
            continue
    loi, rong, rec = 0, 0, 0
    while rec < (tran or TRAN_REC) and (tran or rong < 5000):  # không biết max(id) ⇒ dừng sau 5000 rowid trống liền nhau
        rec += 1
        try:
            hang = kn.execute("select accession_number, title, trash_state from refs where id = ?", (rec,)).fetchone()
        except sqlite3.DatabaseError:
            loi += 1
            continue
        rong = rong + 1 if hang is None else 0
        if hang and str(hang[0] or "").strip() in pmids:
            ra.setdefault(str(hang[0]).strip(), []).append((rec, hang[1] or "", bool(hang[2])))
    return ra, loi


def tep_endnote_theo_ten(goc_pdf: Path, pmids: set[str]) -> dict[str, list[Path]]:
    """Tệp `PMID-<n>[._-…].pdf` trong thư mục PDF của EndNote (`<thư viện>.Data/PDF/<thư mục số>/`), theo PMID. Đường dự phòng KHÔNG
    phụ thuộc sdb.eni: đo 03/11 bản sao chép lúc EndNote đang mở đọc ra dòng rác (rec 7914 có accession «ed to pr»)."""
    ra: dict[str, list[Path]] = {}
    try:
        for p in sorted(goc_pdf.glob("*/PMID-*.pdf")):
            m = MAU_TEP_ENDNOTE.match(p.name)
            if m and m.group(1) in pmids:
                ra.setdefault(m.group(1), []).append(p)
    except OSError:
        pass
    return ra


def tra_endnote(ds_sai: list[KetQua], *, thu_vien: Path | None = None, ket_noi=None) -> str:
    """Gắn vào mỗi KetQua sai bài các bản ghi EndNote cùng PMID và tệp PDF đính kèm (cùng/khác mã băm với tệp kho), rồi dò thêm thư
    mục PDF của EndNote theo tên tệp (bản sao sdb.eni có thể đọc lỗi/rác khi EndNote đang mở). Không ghi gì vào EndNote. Trả ""
    khi đọc trọn, hoặc lý do ⚪ khi đọc thiếu."""
    ds = [kq for kq in ds_sai if kq.pmid]
    if not ds:
        return ""
    try:
        sk = _sk()
        thu_vien = thu_vien or sk.thu_vien_cau_hinh()
        ket_noi = ket_noi or sk.ban_sao_csdl
    except Exception as exc:  # noqa: BLE001
        return f"không nạp được endnote_suc_khoe ({type(exc).__name__})"
    if thu_vien is None:
        return "chưa khai thư viện EndNote (~/.ebm-endnote.json)"
    goc_pdf = Path(thu_vien).with_suffix(".Data") / "PDF"
    sha_kho = {kq.tep: _sha(kq.tep) for kq in ds}

    def _tep(rel: str, kq: KetQua) -> dict:
        sha = _sha(goc_pdf / rel)
        return {"duong_dan": rel, "cung_tep_kho": None if sha is None or sha_kho[kq.tep] is None else sha == sha_kho[kq.tep]}

    ghi_chu = ""
    try:
        with ket_noi(thu_vien) as kn:
            theo, loi = rec_theo_pmid(kn, {kq.pmid for kq in ds})
            for kq in ds:
                for rec, td, rac in theo.get(kq.pmid, []):
                    muc = {"rec": rec, "tieu_de": td, "thung_rac": rac, "tep": []}
                    try:
                        dk = [r[0] for r in kn.execute("select file_path from file_res where refs_id = ?", (rec,))]
                    except sqlite3.DatabaseError:
                        muc["loi"] = "không đọc được bảng tệp đính kèm của bản ghi này (sdb.eni đang ghi dở?)"
                        dk = []
                    muc["tep"] = [_tep(str(fp), kq) for fp in dk if str(fp).lower().endswith(".pdf")]
                    kq.endnote.append(muc)
        if loi:
            ghi_chu = f"{loi} dòng bảng refs không đọc được trên bản sao (EndNote đang ghi dở?) — danh sách bản ghi có thể thiếu"
    except (OSError, sqlite3.DatabaseError) as exc:
        ghi_chu = f"không đọc được bản sao sdb.eni ({type(exc).__name__}: {exc})"
    theo_ten = tep_endnote_theo_ten(goc_pdf, {kq.pmid for kq in ds})
    for kq in ds:
        da_co = {t["duong_dan"] for m in kq.endnote for t in m["tep"]}
        for p in theo_ten.get(kq.pmid, []):
            rel = p.relative_to(goc_pdf).as_posix()
            if rel not in da_co:
                kq.endnote.append({"rec": None, "tieu_de": "", "thung_rac": False, "tep": [_tep(rel, kq)]})
    return ghi_chu + (" — đã dò thêm thư mục PDF của EndNote theo tên tệp" if ghi_chu else "")


# ───────────────────────── cách ly ─────────────────────────

def _dich_cach_ly(thu_muc: Path, ten: str, hom_nay: date) -> Path:
    goc = thu_muc / f"{ten}.SAI-BAI-{hom_nay:%Y%m%d}"
    dich, n = goc, 1
    while dich.exists():
        n += 1
        dich = goc.with_name(f"{goc.name}-lan{n}")
    return dich


def cach_ly(ds_sai: list[KetQua], dash: Path, *, ap_dung: bool, hom_nay: date | None = None) -> list[str]:
    """DỜI (không xoá) từng tệp sai bài sang `_cach-ly-toan-van-sai-bai/` + nối README.txt. Bản in BANIN ⇒ dời cả tệp nguồn ghi trên
    dải đầu trang (in lại từ nguồn sai sẽ ra đúng tệp sai). Chạy khô ⇒ chỉ trả các dòng mô tả. Trả các dòng đã/sẽ làm."""
    hom_nay = hom_nay or date.today()
    thu_muc = dash / THU_MUC_CACH_LY
    dong, readme = [], []
    for kq in ds_sai:
        tep_doi = [kq.tep]
        if kq.nguon_ban_in and (kq.tep.parent / kq.nguon_ban_in).is_file():
            tep_doi.append(kq.tep.parent / kq.nguon_ban_in)
        for t in tep_doi:
            dich = _dich_cach_ly(thu_muc, t.name, hom_nay)
            ly = (f"{dich.name} — dời {hom_nay:%d/%m/%Y} bởi ra_dinh_danh_kho_toan_van.py: "
                  f"{'tệp nguồn của bản in ' + kq.tep.name + ' (bản in sai bài)' if t != kq.tep else 'sai bài'}; "
                  f"bài thật PMID {kq.pmid or '—'} «{kq.tieu_de}» (DOI {kq.doi or '—'}, nguồn {kq.nguon_dinh_danh}); "
                  f"tệp chứa: «{kq.dau_trang[:160]}»; lý do: {kq.ly_do}. Dời, không xoá.")
            if ap_dung:
                thu_muc.mkdir(exist_ok=True)
                shutil.move(str(t), str(dich))
                readme.append(ly)
            dong.append(("  ✓ đã dời " if ap_dung else "  · sẽ dời ") + f"{t.name} → {THU_MUC_CACH_LY}/{dich.name}")
            rec = [str(m["rec"] or "?") for m in kq.endnote if any(x["cung_tep_kho"] for x in m.get("tep", []))]
            if rec and t == kq.tep:
                dong.append(f"      EndNote rec {', '.join(rec)} vẫn gắn bản sao riêng của tệp này — bác sĩ gỡ đính kèm trong EndNote")
    if readme:
        with open(thu_muc / "README.txt", "a", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(readme) + "\n")
    return dong


# ───────────────────────── báo cáo ─────────────────────────

def _o(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def bao_cao_md(ds: list[KetQua], la: list[Path], *, kho: Path, trang_thai: dict, endnote: str, pham_vi: str,
               bat_dau: datetime) -> str:
    dem = {n: sum(kq.nhom == n for kq in ds) for n in NHAN_NHOM}
    hau = sorted({kq.hau_to for kq in ds})
    nguon = {}
    for kq in ds:
        if kq.nguon_dinh_danh:
            nguon[kq.nguon_dinh_danh] = nguon.get(kq.nguon_dinh_danh, 0) + 1
    d = [f"# Rà định danh kho toàn văn — {bat_dau:%d/%m/%Y %H:%M}", "",
         f"Kho: `{kho.as_posix()}` · phạm vi: {pham_vi} · **{len(ds)} tệp PDF** được rà"
         + (f" · {len(la)} PDF tên không nhận dạng (xem cuối)" if la else ""),
         "Cổng: `gom_toan_van_dashboard.kiem_dinh_danh_upw` (BH175; luật `khop_dinh_danh` của bước ⑨: DOI có trong PDF, hoặc ≥ 60% "
         "từ của tiêu đề có ở 3 trang đầu).",
         "Định danh: " + (", ".join(f"{k} {v} tệp" for k, v in sorted(nguon.items())) or "—")
         + (" · ⚠ NCBI chặn IP lượt này" if trang_thai.get("ncbi_chan") else "")
         + (f" · NCBI lỗi {len(trang_thai['loi_ncbi'])} lô" if trang_thai.get("loi_ncbi") else ""), "",
         "| Nhóm | Số tệp |", "|---|---:|"]
    d += [f"| {NHAN_NHOM[n]} | {dem[n]} |" for n in NHAN_NHOM]
    d += ["", "| Hậu tố | " + " | ".join(NHAN_NHOM[n] for n in NHAN_NHOM) + " |", "|---|" + "---:|" * len(NHAN_NHOM)]
    for h in hau:
        d.append(f"| {h} | " + " | ".join(str(sum(kq.hau_to == h and kq.nhom == n for kq in ds)) for n in NHAN_NHOM) + " |")
    sai = [kq for kq in ds if kq.nhom == SAI_BAI]
    d += ["", f"## ❌ Sai bài — {len(sai)} tệp, CHỜ BÁC SĨ DUYỆT", ""]
    if endnote:
        d += [f"⚪ EndNote: {endnote}", ""]
    for kq in sai:
        d += [f"### PMID {kq.pmid or '—'} — `{kq.tep.name}`", "",
              f"- Bài thật ({kq.nguon_dinh_danh}): «{kq.tieu_de}» · DOI {kq.doi or '—'}",
              f"- Tệp chứa (đầu trang 1): «{kq.dau_trang or '—'}»"
              + (f" · DOI thấy ở 2 trang đầu: {', '.join(kq.doi_trong_tep)}" if kq.doi_trong_tep else ""),
              f"- Lý do: {kq.ly_do}" + (f" · {'; '.join(kq.ghi_chu)}" if kq.ghi_chu else "")]
        if kq.nguon_ban_in:
            d.append(f"- Bản in từ `{kq.nguon_ban_in}` — tệp nguồn cũng là bài khác (dời cùng khi cách ly)")
        for m in kq.endnote:
            if m["rec"] is None:
                for t in m["tep"]:
                    cung = {True: "CÙNG nội dung tệp kho sai bài", False: "khác nội dung tệp kho",
                            None: "không so được mã băm"}[t["cung_tep_kho"]]
                    d.append(f"- Thư mục PDF của EndNote có `{t['duong_dan']}` — {cung}; chưa đọc được bản ghi nào gắn tệp này từ "
                             f"sdb.eni ⇒ tìm PMID {kq.pmid} trong EndNote" + (" rồi gỡ đính kèm" if t["cung_tep_kho"] else ""))
                continue
            if m.get("loi"):
                d.append(f"- EndNote rec {m['rec']}: ⚪ {m['loi']}")
            elif not m["tep"]:
                d.append(f"- EndNote rec {m['rec']}{' (thùng rác)' if m['thung_rac'] else ''}: không gắn PDF")
            for t in m["tep"]:
                cung = {True: "CÙNG nội dung tệp kho sai bài ⇒ bác sĩ gỡ đính kèm", False: "khác nội dung tệp kho",
                        None: "không so được mã băm"}[t["cung_tep_kho"]]
                d.append(f"- EndNote rec {m['rec']}{' (thùng rác)' if m['thung_rac'] else ''} gắn `{t['duong_dan']}` — {cung}")
        d.append("")
    if sai:
        pm = " ".join(sorted({kq.pmid for kq in sai if kq.pmid}, key=int))
        d += ["Sau khi bác sĩ duyệt (dời, không xoá):", "", "```bash",
              f"python3 tools/ra_dinh_danh_kho_toan_van.py --cach-ly --ap-dung --pmid {pm}", "```", ""]
    for nhom, tieu in ((KHONG_KIEM_DUOC, "⚪ Không kiểm được"), (KHONG_DO_DUOC, "🟡 Không đo được — chạy lại khi có mạng/công cụ")):
        nh = [kq for kq in ds if kq.nhom == nhom]
        d += [f"## {tieu} — {len(nh)} tệp", ""]
        if nh:
            d += ["| Tệp | Lý do |", "|---|---|"] + [f"| `{kq.tep.name}` | {_o(kq.ly_do)} |" for kq in nh]
        d.append("")
    doi = [kq for kq in ds if kq.nhom == KHOP and kq.can_cu == "chỉ DOI"]
    d += [f"## ✅ Khớp CHỈ nhờ DOI (tiêu đề < 60% ở 3 trang đầu) — {len(doi)} tệp, nên liếc lại", "",
          "Luật của bước ⑨ nhận DOI ở BẤT KỲ đâu trong PDF, kể cả danh mục tham khảo — bài khác TRÍCH bài cần tìm cũng qua.", ""]
    if doi:
        d += ["| Tệp | Tiêu đề thật | Ghi chú |", "|---|---|---|"]
        d += [f"| `{kq.tep.name}` | {_o(kq.tieu_de)} | {_o('; '.join(kq.ghi_chu) or kq.ly_do)} |" for kq in doi]
    d.append("")
    if la:
        d += [f"## PDF tên không nhận dạng — {len(la)} tệp (không rà; không gắn được với PMID/DOI)", ""]
        d += [f"- `{p.relative_to(kho).as_posix()}`" for p in la] + [""]
    d += [f"## Toàn bộ {len(ds)} tệp đã rà", "", "<details><summary>Mở bảng</summary>", "", "| Tệp | Nhóm | Căn cứ / lý do |",
          "|---|---|---|"]
    d += [f"| `{kq.tep.name}` | {NHAN_NHOM[kq.nhom]} | {_o(kq.can_cu or kq.ly_do)} |" for kq in ds]
    d += ["", "</details>", ""]
    d += ["## Giới hạn", "",
          "- Chỉ rà PDF; HTML (`_UPW.html`, `_CHR.html`) và XML JATS chưa rà ở công cụ này.",
          "- Tiêu đề chung chung (toàn từ phổ biến của chủ đề) có thể đạt 60% trên 3 trang đầu của một bài cùng chủ đề.",
          "- «Khớp» là phép so DOI/tiêu đề, không phải thẩm định nội dung.", "",
          "_Cần bác sĩ kiểm chứng._", ""]
    return "\n".join(d)


# ───────────────────────── chạy ─────────────────────────

_BO_NHO_CROSSREF: dict[str, dict] = {}  # {mã lượt: {doi: (tiêu đề, trạng thái)}} — nhớ trong MỘT lượt, không qua lượt sau


def _kiem_mot(tham_so: tuple) -> dict:
    """Việc của MỘT tệp, chạy được trong tiến trình con (tham số và kết quả đều pickle được): kiểm + mô tả tệp sai bài."""
    tep, hau_to, pmid, doi, md, email, ma_luot = tham_so
    kq = KetQua(Path(tep), hau_to, pmid, doi)
    bo_nho = _BO_NHO_CROSSREF.setdefault(ma_luot, {})
    kiem_tep(kq, md, crossref=lambda d: tieu_de_crossref(d, email, bo_nho))
    if kq.nhom == SAI_BAI:
        mo_ta_tep(kq)
    return {k: v for k, v in vars(kq).items() if k != "tep"}


def ra_kho(kho: Path, *, hau_to: set[str] | None = None, pmids: set[str] | None = None, email: str | None = None,
           doc_endnote: bool = True, thu_vien: Path | None = None, ket_noi=None,
           so_luong: int = 1) -> tuple[list[KetQua], list[Path], dict, str]:
    """Rà mọi PDF của kho (theo bộ lọc). `so_luong` > 1 ⇒ đọc PDF ở nhiều tiến trình (pypdf thuần Python: đo 03/11 tuần tự ~2,4
    giây/tệp, cả kho > 1 giờ) — chỉ dùng khi chạy như script (tiến trình con phải nạp lại được mô-đun). Trả (kết quả, PDF tên lạ,
    trạng thái nguồn, ghi chú EndNote)."""
    ds, la = liet_ke_pdf(kho, hau_to, pmids)
    email = email if email is not None else g._email_lich_su()
    dd, trang_thai = lay_dinh_danh([kq.pmid for kq in ds if kq.pmid], email=email)
    ma_luot = f"{os.getpid()}-{time.time_ns()}"
    viec = [(str(kq.tep), kq.hau_to, kq.pmid, kq.doi,
             (dd.get(kq.pmid) if kq.pmid else dinh_danh_zenodo(kq.tep)) or {"trang_thai": "loi"}, email, ma_luot) for kq in ds]
    ket: list[dict] | None = None
    if so_luong > 1 and len(viec) > 1:
        import concurrent.futures as _cf  # noqa: PLC0415
        try:
            ket = []
            with _cf.ProcessPoolExecutor(max_workers=so_luong) as ex:
                for i, d in enumerate(ex.map(_kiem_mot, viec, chunksize=4), 1):
                    ket.append(d)
                    if i % 100 == 0:
                        print(f"  … {i}/{len(viec)} tệp", file=sys.stderr, flush=True)
        except Exception as exc:  # noqa: BLE001 — nhóm tiến trình hỏng ⇒ làm lại tuần tự, không bỏ tệp nào
            print(f"  ⚠ chạy song song lỗi ({type(exc).__name__}: {exc}) — rà lại tuần tự", file=sys.stderr)
            ket = None
    if ket is None:
        ket = []
        for i, v in enumerate(viec, 1):
            ket.append(_kiem_mot(v))
            if i % 100 == 0:
                print(f"  … {i}/{len(viec)} tệp", file=sys.stderr, flush=True)
    _BO_NHO_CROSSREF.pop(ma_luot, None)
    for kq, d in zip(ds, ket):
        vars(kq).update(d)
    sai = [kq for kq in ds if kq.nhom == SAI_BAI]
    endnote = tra_endnote(sai, thu_vien=thu_vien, ket_noi=ket_noi) if doc_endnote and sai else ""
    return ds, la, trang_thai, endnote


def _ra_json(kq: KetQua) -> dict:
    return {"tep": kq.tep.name, "pmid": kq.pmid, "hau_to": kq.hau_to, "nhom": kq.nhom, "can_cu": kq.can_cu, "ly_do": kq.ly_do,
            "doi": kq.doi, "tieu_de": kq.tieu_de, "nguon": kq.nguon_dinh_danh, "ghi_chu": kq.ghi_chu, "dau_trang": kq.dau_trang,
            "doi_trong_tep": kq.doi_trong_tep, "nguon_ban_in": kq.nguon_ban_in, "endnote": kq.endnote}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rà định danh mọi PDF đã có trong kho toàn văn (chỉ đọc; dời tệp sai khi --cach-ly "
                                             "--ap-dung).")
    ap.add_argument("--kho", type=Path, default=None, help="thư mục kho (mặc định EBM-Dashboards/toan_van_oa định vị như "
                                                           "gom_toan_van_dashboard.py)")
    ap.add_argument("--hau-to", nargs="+", default=None, help="chỉ rà các hậu tố này (UPW CHR WTDM BANIN ZENODO …)")
    ap.add_argument("--pmid", nargs="+", default=None, help="chỉ rà/dời các PMID này")
    ap.add_argument("--khong-endnote", action="store_true", help="không đọc bản sao sdb.eni")
    ap.add_argument("--cach-ly", action="store_true", help="liệt kê (chạy khô) hoặc dời (--ap-dung) tệp SAI BÀI")
    ap.add_argument("--ap-dung", action="store_true", help="đi cùng --cach-ly: dời thật")
    ap.add_argument("--json", type=Path, default=None, help="ghi thêm kết quả dạng JSON")
    ap.add_argument("--so-luong", type=int, default=0, help="số tiến trình đọc PDF (mặc định: số lõi, tối đa 8)")
    a = ap.parse_args(argv)
    if a.ap_dung and not a.cach_ly:
        print("--ap-dung chỉ đi cùng --cach-ly (công cụ này không có việc ghi nào khác).", file=sys.stderr)
        return 3
    if a.ap_dung and not a.pmid:
        print("--cach-ly --ap-dung cần --pmid <các PMID bác sĩ đã duyệt> — không dời cả danh sách khi chưa ai duyệt.",
              file=sys.stderr)
        return 3
    if a.pmid and not all(re.fullmatch(r"\d{1,9}", p) for p in a.pmid):
        print("--pmid nhận số PMID.", file=sys.stderr)
        return 3
    kho = (a.kho or g.KHO).resolve()
    if not kho.is_dir():
        print(f"⚪ KHÔNG ĐO ĐƯỢC: không thấy kho {kho.as_posix()} (chạy từ worktree ⇒ --kho <GỐC>/EBM-Dashboards/toan_van_oa)")
        return 2
    hau_to = {h.upper() for h in a.hau_to} if a.hau_to else None
    pmids = set(a.pmid) if a.pmid else None
    bat_dau = datetime.now()
    print(f"Rà định danh kho {kho.as_posix()} …")
    # Song song chỉ khi chạy như script: tiến trình con nạp lại `__main__`; mô-đun nạp bằng importlib (test, chốt) thì không.
    so_luong = a.so_luong or (min(8, os.cpu_count() or 1) if __name__ == "__main__" else 1)
    ds, la, trang_thai, endnote = ra_kho(kho, hau_to=hau_to, pmids=pmids, doc_endnote=not a.khong_endnote, so_luong=so_luong)
    phan = (["hậu tố " + " ".join(sorted(hau_to))] if hau_to else []) + (["PMID " + " ".join(sorted(pmids, key=int))] if pmids else [])
    pham_vi = " · ".join(phan) or "cả kho"
    md = bao_cao_md(ds, la, kho=kho, trang_thai=trang_thai, endnote=endnote, pham_vi=pham_vi, bat_dau=bat_dau)
    dich_bc = kho.parent / (TEN_BAO_CAO if pham_vi == "cả kho" else TEN_BAO_CAO_MOT_PHAN)
    try:
        dich_bc.write_text(md, encoding="utf-8", newline="\n")
        ghi = f"báo cáo: {dich_bc.as_posix()}"
    except OSError as exc:
        ghi = f"⚪ chưa ghi được báo cáo ({type(exc).__name__})"
    if a.json:
        try:
            a.json.write_text(json.dumps([_ra_json(kq) for kq in ds], ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        except OSError as exc:
            print(f"⚪ chưa ghi được JSON ({type(exc).__name__})")
    dem = {n: sum(kq.nhom == n for kq in ds) for n in NHAN_NHOM}
    print(f"{len(ds)} tệp PDF · " + " · ".join(f"{NHAN_NHOM[n]} {dem[n]}" for n in NHAN_NHOM)
          + (f" · {len(la)} PDF tên lạ" if la else ""))
    for kq in ds:
        if kq.nhom == SAI_BAI:
            print(f"  ❌ {kq.tep.name}: bài thật «{kq.tieu_de[:90]}» — tệp chứa «{kq.dau_trang[:90]}»")
    if endnote:
        print(f"  ⚪ EndNote: {endnote}")
    print(ghi)
    sai = [kq for kq in ds if kq.nhom == SAI_BAI]
    if a.cach_ly:
        if not sai:
            print("Không có tệp sai bài để dời.")
        else:
            print("CÁCH LY " + ("(dời thật)" if a.ap_dung else "(chạy khô — thêm --ap-dung sau khi bác sĩ duyệt)") + ":")
            for dong in cach_ly(sai, kho.parent, ap_dung=a.ap_dung):
                print(dong)
            if a.ap_dung:
                print("Báo cáo trên là ảnh chụp TRƯỚC khi dời — chạy lại không cờ để làm mới.")
    print("Cần bác sĩ kiểm chứng.")
    if dem[SAI_BAI]:
        return 1
    return 2 if dem[KHONG_DO_DUOC] else 0


if __name__ == "__main__":
    sys.exit(main())
