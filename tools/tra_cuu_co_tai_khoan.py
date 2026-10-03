#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRA CỨU BẰNG TÀI KHOẢN CỦA BÁC SĨ — Scopus · Web of Science · DynaMed (02/10/2026, bác sĩ yêu cầu).

DYNAMED (thêm cùng ngày, bác sĩ đã đăng nhập trên khung trình duyệt của app): trang «Recent Alerts» liệt kê cảnh báo chứng cứ mới
(Evidence / Guideline Summary / Drug/Device Alert) kèm trích dẫn tạp chí dạng «(Ann Oncol 2026 May)» — KHÔNG có PMID/DOI (đo 02/10:
trang chủ đề có 169 liên kết, 0 liên kết PubMed/DOI). Claude đọc văn bản trang (get_page_text) vào tệp TẠM ngoài repo, rồi
`--dynamed-canh-bao <tệp>`: máy tách {loại, ngày, trích dẫn, chủ đề DynaMed, vài từ khoá} — KHÔNG lưu câu tóm tắt của DynaMed (nội
dung có bản quyền) —, gắn chủ đề watchlist khi tên chủ đề DynaMed trùng từ khoá của chủ đề đó, tra ngược trích dẫn ra PMID trên PubMed
(`"<tạp chí>"[ta] AND <năm>[dp] AND <từ khoá>`; CHỈ nhận khi đúng MỘT bài), rồi đi CÙNG luồng xác minh/ứng viên như Scopus/WoS.
Trích dẫn không phải tạp chí (FDA Product Information, NCCN…) ⇒ liệt kê riêng cho bác sĩ đọc, không tự thành ứng viên.

SCOPUS / WEB OF SCIENCE — máy soạn câu tìm, bác sĩ đăng nhập + export, máy nhập + xác minh.

VÌ SAO CÓ. Bác sĩ có tài khoản Scopus và Web of Science (WoS). Làn Scopus API của engine bị 403 khi VPN bật (đánh đổi đã chấp nhận,
CLAUDE.md §5) và WoS chưa có làn nào; 10/42 chủ đề watchlist từng «mù» trên PubMed (EV-02). Đây là làn KHÁM PHÁ bổ sung, có người:
  1. `--phieu`  : máy soạn câu tìm Advanced Search cho từng chủ đề (cú pháp Scopus `TITLE-ABS-KEY`, WoS `TS=`) + các bước bấm.
  2. Bác sĩ TỰ đăng nhập (máy không bao giờ gõ mật khẩu), dán câu, bấm Export (CSV/RIS của Scopus; Tab-delimited/Plain text/RIS
     của WoS) — chức năng xuất CHÍNH THỨC của hai trang. Máy KHÔNG tự cào trang kết quả: điều khoản Scopus/WoS cấm công cụ tự động
     thu thập; tệp export là đường hợp lệ và bền hơn đọc giao diện.
  3. `--nhap <tệp> --chu-de "<watchlist>"`: máy đọc tệp, bỏ trùng (trong tệp · đã có trong kho · đã nằm ở hàng ngoài-quét), xếp hạng
     (guideline/đồng thuận > tổng quan hệ thống/gộp > RCT > khác; mới hơn trước), XÁC MINH từng bản ghi bằng CHÍNH bộ xác minh của
     làn dự phòng (`medical-ebm-automation/app/services/fallback_verification.py`: Crossref/PubMed + cổng rút bài Crossref/Scite,
     fail-closed — không khớp/mơ hồ/lỗi mạng KHÔNG BAO GIỜ thành ứng viên), rồi (chỉ khi `--ghi`) nối ≤ `--toi-da` ứng viên vào
     `EBM-Dashboards/surveillance/ung-vien-ngoai-quet.jsonl` với `trang_thai: CANDIDATE` — gói duyệt tuần đọc tệp này (bước 1c),
     kiểm rút bài chuỗi 3 tầng ở bước 4, Cổng A/B nguyên vẹn. Mọi bản ghi (giữ hay bỏ, vì sao) ghi ở báo cáo phiên
     `EBM-Dashboards/surveillance/phien-web/<giờ>-<nguồn>.json` — không lọc im lặng.

    python3 tools/tra_cuu_co_tai_khoan.py --phieu --chu-de "Viêm khớp dạng thấp"      # phiếu câu tìm cho 1+ chủ đề
    python3 tools/tra_cuu_co_tai_khoan.py --phieu --mu                               # cho các chủ đề kiem_san_luong_giam_sat báo «mù»
    python3 tools/tra_cuu_co_tai_khoan.py --nhap ~/Downloads/scopus.csv --chu-de "Viêm khớp dạng thấp (RA)"        # chạy thử
    python3 tools/tra_cuu_co_tai_khoan.py --nhap ~/Downloads/savedrecs.txt --chu-de "Viêm khớp dạng thấp (RA)" --ghi

Mã thoát (--nhap): 0 có ứng viên mới · 1 không có ứng viên mới · 2 KHÔNG xác minh được (engine vắng/mọi lượt lỗi) — không ghi gì ·
3 tệp không đọc/không nhận dạng được hoặc chủ đề không có trong watchlist. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parent.parent
DASH = REPO / "EBM-Dashboards"
WATCHLIST = DASH / "watchlist.json"
HANG_NGOAI_QUET = DASH / "surveillance" / "ung-vien-ngoai-quet.jsonl"
BAO_CAO_PHIEN = DASH / "surveillance" / "phien-web"
SO_XAC_MINH = DASH / ".so-xac-minh-nguon.json"
SAN_LUONG = REPO / "state" / "san-luong-giam-sat-gan-nhat.json"
TOI_DA_MAC_DINH = 7          # cùng trần thẻ của gói tuần
HE_SO_XAC_MINH = 4           # chỉ xác minh tối đa toi_da × 4 bản ghi đứng đầu (mỗi bản ≤ 2 lời gọi cơ quan đăng ký)

_CUM_LOAI = '(guideline* OR consensus OR recommendation* OR "systematic review" OR meta-analys* OR randomi*)'

HUONG_DAN_SCOPUS = """SCOPUS (https://www.scopus.com) — bác sĩ tự đăng nhập bằng tài khoản của mình. Claude KHÔNG mở/đọc trang Scopus
(điều khoản website Elsevier, đọc 03/10/2026: không dùng Content «in combination with an artificial intelligence tool»); công cụ chỉ in
metadata lấy từ Crossref/PubMed — tiêu đề trong tệp export Scopus không được in ra hay lưu lại:
  1. Search → «Advanced document search» → dán câu tìm → Search.
  2. Sắp xếp «Date (newest)». Chọn «All» (hoặc tối đa 200 dòng đầu).
  3. Export → CSV → tick «Citation information» (thêm «Abstract & keywords» nếu muốn) → Export. Lưu ~/Downloads/scopus_<chủ-đề>.csv."""
HUONG_DAN_WOS = """WEB OF SCIENCE (https://www.webofscience.com) — bác sĩ tự đăng nhập bằng tài khoản của mình:
  1. «Advanced search» → dán câu tìm vào ô Query Preview → Search.
  2. Sắp xếp «Date: newest first».
  3. Export → «Tab delimited file» (hoặc «Plain text file» / «RIS») → Records 1–500 · Record content «Full Record» → Export.
     Tệp thường tên savedrecs.txt trong ~/Downloads."""
HUONG_DAN_DYNAMED = """DYNAMED — điều khoản EBSCO (đọc 03/10/2026): dùng công cụ AI với nội dung phải được EBSCO cho phép; khai thác
văn bản/dữ liệu (TDM) bị cấm ⇒ Claude KHÔNG mở, KHÔNG đọc trang DynaMed (kể cả trong khung trình duyệt của app) và KHÔNG đọc tệp bác sĩ chép.
  1. BÁC SĨ tự mở «Recent Alerts» → chép văn bản trang (Ctrl/Cmd+A, Ctrl/Cmd+C) vào một tệp ở máy, vd ~/Downloads/dynamed.txt.
  2. Chạy (bác sĩ, hoặc Claude chạy LỆNH mà không mở tệp):
       python3 tools/tra_cuu_co_tai_khoan.py --dynamed-canh-bao ~/Downloads/dynamed.txt          (chạy thử)
       python3 tools/tra_cuu_co_tai_khoan.py --dynamed-canh-bao ~/Downloads/dynamed.txt --ghi    (sau khi bác sĩ xem kết quả)
     Công cụ Python TẤT ĐỊNH (không phải AI) tách trích dẫn rồi tra PubMed; đầu ra CHỈ có số thứ tự cảnh báo, ngày, PMID và metadata
     PubMed/Crossref — không in, không lưu chữ nào của DynaMed (tên chủ đề, trích dẫn, câu tóm tắt).
  3. Xoá tệp chép sau khi chạy. Cảnh báo ngoài PubMed / ngoài watchlist được nêu theo SỐ THỨ TỰ để bác sĩ tra lại trong tệp của mình."""
HUONG_DAN_NHAP = ("Sau khi export, nói với Claude: «nhập tệp <đường dẫn> cho chủ đề <tên>». Claude chạy chạy thử trước "
                  "(`--nhap … ` không ghi), đọc kết quả xác minh với bác sĩ, rồi mới `--ghi`.")


# ── câu tìm ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def doc_watchlist(duong: Path | None = None) -> list[dict]:
    d = json.loads((duong or WATCHLIST).read_text(encoding="utf-8"))
    return [t for t in d.get("topics", []) if t.get("active", True)]


def cau_tim(muc: dict, nam: int) -> dict | None:
    """Câu Advanced Search cho Scopus và WoS từ `truy_van_du_phong` (cụm tiếng Anh thường của chủ đề). Thiếu ⇒ None (không đoán)."""
    q = " ".join(str(muc.get("truy_van_du_phong") or "").split())
    if not q or any(c in q for c in '[]"'):
        return None
    return {
        "scopus": f"TITLE-ABS-KEY({q}) AND PUBYEAR > {nam - 2} AND (DOCTYPE(re) OR TITLE{_CUM_LOAI})",
        "wos": f"TS=({q}) AND PY=({nam - 1}-{nam}) AND (DT=(Review) OR TI={_CUM_LOAI})",
    }


def _bo_dau(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").casefold()


def chon_chu_de(ds: list[dict], tu_khoa: list[str], mu: bool, san_luong: Path | None = None) -> list[dict]:
    ra = []
    if mu:
        try:
            ten_mu = set(json.loads((san_luong or SAN_LUONG).read_text(encoding="utf-8")).get("mu") or [])
        except (OSError, ValueError):
            ten_mu = set()
        ra += [t for t in ds if t.get("topic") in ten_mu]
    for k in tu_khoa:
        ra += [t for t in ds if _bo_dau(k) in _bo_dau(t.get("topic", "")) and t not in ra]
    return ra


def phieu(cac_chu_de: list[dict], nam: int) -> str:
    dong = [f"# PHIẾU TRA SCOPUS / WEB OF SCIENCE — {date.today():%d/%m/%Y}", "",
            "> Bác sĩ tự đăng nhập; máy KHÔNG gõ mật khẩu, KHÔNG tự cào trang kết quả (điều khoản Scopus/WoS). Kết quả export chỉ là",
            "> nguồn KHÁM PHÁ: mọi bản ghi qua xác minh Crossref/PubMed + rút bài trước khi thành ứng viên. Cần bác sĩ kiểm chứng.", "",
            HUONG_DAN_SCOPUS, "", HUONG_DAN_WOS, "", HUONG_DAN_NHAP, ""]
    for t in cac_chu_de:
        c = cau_tim(t, nam)
        dong.append(f"## {t.get('topic')}")
        if c is None:
            dong.append("- ⚪ chưa có `truy_van_du_phong` tiếng Anh trong watchlist — máy không tự đoán câu tìm; khai rồi chạy lại.")
        else:
            dong += [f"- Scopus: `{c['scopus']}`", f"- WoS:    `{c['wos']}`"]
        dong.append("")
    return "\n".join(dong)


# ── đọc tệp export ──────────────────────────────────────────────────────────────────────────────────────────────────────
def _doc_van_ban(duong: Path) -> str:
    b = duong.read_bytes()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16")
    return b.decode("utf-8-sig", errors="replace")


def _lam_sach_doi(x: str) -> str:
    x = (x or "").strip()
    x = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", x, flags=re.I)
    return x.lower() if x.startswith("10.") else ""


def _lam_sach_pmid(x: str) -> str:
    x = (x or "").strip()
    return x if x.isdigit() else ""


def _ban_ghi(title, year, journal, doi, pmid, loai, tac_gia="") -> dict | None:
    title = " ".join(str(title or "").split())
    if len(title) < 10:
        return None
    m = re.search(r"(19|20)\d{2}", str(year or ""))
    return {"title": title, "year": int(m.group(0)) if m else None, "journal": " ".join(str(journal or "").split()),
            "doi": _lam_sach_doi(doi), "pmid": _lam_sach_pmid(pmid), "loai": " ".join(str(loai or "").split()),
            "tac_gia": str(tac_gia or "").split(";")[0].split(",")[0].strip()}


def _doc_csv_scopus(vb: str) -> list[dict]:
    r = csv.DictReader(io.StringIO(vb))
    if not r.fieldnames:
        return []
    k = {f.strip().casefold(): f for f in r.fieldnames}

    def lay(dong, *ten):
        for t in ten:
            if t in k:
                return dong.get(k[t]) or ""
        return ""
    ra = []
    for d in r:
        b = _ban_ghi(lay(d, "title"), lay(d, "year"), lay(d, "source title"), lay(d, "doi"), lay(d, "pubmed id"),
                     lay(d, "document type"), lay(d, "authors", "author full names"))
        if b:
            ra.append(b)
    return ra


def _doc_wos_tab(vb: str) -> list[dict]:
    dong = vb.splitlines()
    tieu_de = dong[0].split("\t")
    ra = []
    for d in dong[1:]:
        if not d.strip():
            continue
        g = dict(zip(tieu_de, d.split("\t")))
        b = _ban_ghi(g.get("TI"), g.get("PY"), g.get("SO"), g.get("DI"), g.get("PM"), g.get("DT"), g.get("AU"))
        if b:
            ra.append(b)
    return ra


def _doc_the(vb: str, ket_thuc: str, tach: Callable[[str], tuple[str, str] | None]) -> list[dict]:
    """Định dạng có thẻ (RIS «TI  - x», WoS plain «TI x»): gom bản ghi tới dòng kết thúc; dòng tiếp nối nối vào thẻ trước."""
    ra, cur, the_truoc = [], {}, None
    for d in vb.splitlines():
        if d.strip() in (ket_thuc, f"{ket_thuc}  -", f"{ket_thuc}  - "):
            if cur:
                ra.append(cur)
            cur, the_truoc = {}, None
            continue
        t = tach(d)
        if t:
            the_truoc, gt = t
            cur[the_truoc] = (cur.get(the_truoc, "") + ("; " if the_truoc in cur else "") + gt.strip())
        elif the_truoc and d.startswith("   "):
            cur[the_truoc] += " " + d.strip()
    if cur:
        ra.append(cur)
    return ra


def _doc_ris(vb: str) -> list[dict]:
    def tach(d):
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", d)
        return (m.group(1), m.group(2)) if m else None
    ra = []
    for g in _doc_the(vb, "ER", tach):
        b = _ban_ghi(g.get("TI") or g.get("T1"), g.get("PY") or g.get("Y1") or g.get("DA"),
                     g.get("T2") or g.get("JO") or g.get("JF"), g.get("DO"), "", g.get("TY") or g.get("M3"), g.get("AU"))
        if b:
            ra.append(b)
    return ra


def _doc_wos_plain(vb: str) -> list[dict]:
    def tach(d):
        m = re.match(r"^([A-Z][A-Z0-9]) (.*)$", d)
        return (m.group(1), m.group(2)) if m else None
    ra = []
    for g in _doc_the(vb, "ER", tach):
        b = _ban_ghi(g.get("TI"), g.get("PY"), g.get("SO"), g.get("DI"), g.get("PM"), g.get("DT"), g.get("AU"))
        if b:
            ra.append(b)
    return ra


def doc_tep(duong: Path) -> tuple[str, list[dict]]:
    """(định dạng nhận ra, bản ghi). Không nhận dạng được ⇒ ("", [])."""
    vb = _doc_van_ban(duong)
    dau = next((d for d in vb.splitlines() if d.strip()), "")
    if duong.suffix.lower() == ".ris" or re.match(r"^TY  - ", dau):
        return "ris", _doc_ris(vb)
    if dau.startswith("PT\t") or "\tTI\t" in dau:
        return "wos_tab", _doc_wos_tab(vb)
    if dau.startswith("FN ") or re.match(r"^PT [A-Z]$", dau):
        return "wos_plain", _doc_wos_plain(vb)
    if "title" in dau.casefold() and "," in dau:
        return "scopus_csv", _doc_csv_scopus(vb)
    return "", []


# ── bỏ trùng · xếp hạng ─────────────────────────────────────────────────────────────────────────────────────────────────
def _khoa(b: dict) -> str:
    return b["doi"] or (f"pmid:{b['pmid']}" if b["pmid"] else "ti:" + re.sub(r"[^a-z0-9]", "", _bo_dau(b["title"]))[:120])


def da_co(so_xac_minh: Path | None = None, hang: Path | None = None) -> tuple[set[str], set[str]]:
    """(PMID, DOI) đã có trong kho (sổ xác minh nguồn — mục có dashboard trích) hoặc đã nằm ở hàng ngoài-quét."""
    pm, doi = set(), set()
    try:
        muc = (json.loads((so_xac_minh or SO_XAC_MINH).read_text(encoding="utf-8")) or {}).get("muc", {}) or {}
        for k, v in muc.items():
            if not (isinstance(v, dict) and v.get("cac_dashboard")):
                continue
            if k.startswith("pmid:"):
                pm.add(k.split(":", 1)[1])
            elif k.startswith("doi:"):
                doi.add(k.split(":", 1)[1].lower())
    except (OSError, ValueError, AttributeError):
        pass
    try:
        for d in (hang or HANG_NGOAI_QUET).read_text(encoding="utf-8").splitlines():
            try:
                x = json.loads(d)
            except ValueError:
                continue
            if x.get("pmid"):
                pm.add(str(x["pmid"]))
            if x.get("doi"):
                doi.add(str(x["doi"]).lower())
    except OSError:
        pass
    return pm, doi


_MANH = ((re.compile(r"\b(guidelines?|consensus|recommendations?|position statement)\b", re.I), 5),
         (re.compile(r"\b(systematic review|meta-?analys[ie]s|umbrella review)\b", re.I), 4),
         (re.compile(r"\brandomi[sz]ed\b", re.I), 3))


def diem(b: dict) -> int:
    d = max((s for p, s in _MANH if p.search(b["title"])), default=1)
    if d == 1 and re.search(r"\breview\b", b.get("loai") or "", re.I):
        d = 2
    return d


def chuan_bi(ban_ghi: list[dict], pm_kho: set[str], doi_kho: set[str]) -> tuple[list[dict], dict]:
    """Bỏ trùng trong tệp và với kho/hàng; xếp mạnh trước, mới trước. Trả (danh sách xếp hạng, bộ đếm bỏ)."""
    dem = {"trung_trong_tep": 0, "da_co_trong_kho_hoac_hang": 0}
    thay, ra = set(), []
    for b in ban_ghi:
        k = _khoa(b)
        if k in thay:
            dem["trung_trong_tep"] += 1
            continue
        thay.add(k)
        if (b["pmid"] and b["pmid"] in pm_kho) or (b["doi"] and b["doi"] in doi_kho):
            dem["da_co_trong_kho_hoac_hang"] += 1
            continue
        ra.append(b)
    ra.sort(key=lambda b: (-diem(b), -(b["year"] or 0)))
    return ra, dem


# ── DynaMed: đọc cảnh báo · tra ngược trích dẫn ra PMID ─────────────────────────────────────────────────────────────────────
_LOAI_CANH_BAO = ("Drug/Device Alert", "Evidence", "Guideline Summary", "Potentially Practice-Changing")
_THANG = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}
_TU_THUONG = set("""patients persons adults adult children people associated compared versus among with without within after before
during their there these those which while where about other study studies trial trials reduce reduced reduces increase increased
improve improves improved might could would should risk risks outcomes outcome years older younger first second third management
treatment therapy recommendations recommendation guideline guidelines update updated focused society national american european
world international similar addition receives expanded approval syndrome disease diseases disorder disorders acute chronic
receptor positive negative primary secondary adolescents infants pediatric care clinical evidence assessment network""".split())
_NGUON_NGOAI_PUBMED = re.compile(r"\b(FDA|EMA|MHRA|NCCN|Product Information|Prescribing Information|Label|press release)\b", re.I)


def doc_canh_bao_dynamed(van_ban: str) -> list[dict]:
    """Tách cảnh báo từ văn bản trang Recent Alerts. Mỗi cảnh báo: loại · ngày (ISO) · trích dẫn (ngoặc cuối) · chủ đề DynaMed
    («View in …») · ≤ 4 từ khoá đặc hiệu. KHÔNG giữ câu tóm tắt (nội dung có bản quyền của DynaMed)."""
    # Hai dạng văn bản đo được 02/10/2026: loại và ngày trên HAI dòng («Evidence» / «Updated 2 Oct 2026») hoặc DÍNH một dòng
    # («EvidenceUpdated 2 Oct 2026») tuỳ cách trang dựng DOM — gộp về một dạng trước khi tách.
    tho = re.sub(r"(?m)^(" + "|".join(re.escape(x) for x in _LOAI_CANH_BAO) + r")\s*\n\s*(Updated )", r"\1\2", van_ban or "")
    dong = [d.strip() for d in tho.splitlines()]
    mau_dau = re.compile(r"^(" + "|".join(re.escape(x) for x in _LOAI_CANH_BAO) + r")\s*Updated (\d{1,2}) (\w{3})\w* (\d{4})")
    ra, cur = [], None
    for d in dong:
        m = mau_dau.match(d)
        if m:
            cur = {"loai": m.group(1),
                   "ngay": f"{m.group(4)}-{_THANG.get(m.group(3).lower()[:3], 0):02d}-{int(m.group(2)):02d}"}
            continue
        if cur is None or not d:
            continue
        if d.startswith("View in "):
            cur["chu_de_dynamed"] = d[len("View in "):].strip()
            if cur.get("trich_dan"):
                cur["so_thu_tu"] = len(ra) + 1     # đầu ra nêu cảnh báo theo SỐ THỨ TỰ, không theo chữ của DynaMed
                ra.append(cur)
            cur = None
            continue
        if "trich_dan" not in cur and d.endswith((")", ").")):
            m = re.search(r"\(([^()]*)\)\.?$", d)
            if m:
                cur["trich_dan"] = m.group(1).strip()
                cau = d[:m.start()]
                tu = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9\-]{4,}", cau) if w.lower() not in _TU_THUONG]
                cur["tu_khoa"] = sorted(dict.fromkeys(tu), key=len, reverse=True)[:4]
    return ra


def tach_trich_dan(td: str) -> dict | None:
    """«Am J Obstet Gynecol 2026 Jul 14 early online» ⇒ {tap_chi, nam}. Nguồn ngoài tạp chí (FDA, NCCN…) ⇒ None."""
    if _NGUON_NGOAI_PUBMED.search(td or ""):
        return None
    m = re.match(r"^(.*?)\s+((?:19|20)\d{2})\b", (td or "").strip())
    if not m or len(m.group(1)) < 3:
        return None
    return {"tap_chi": m.group(1).strip(), "nam": int(m.group(2))}


def _tu_dac_hieu(van_ban: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z\-]{3,}", (van_ban or "").lower()) if w not in _TU_THUONG}


def gan_chu_de(chu_de_dynamed: str, ds: list[dict]) -> str | None:
    """Chủ đề watchlist khớp tên chủ đề DynaMed theo TỪ ĐẶC HIỆU (tiếng Anh của truy_van_du_phong/query). Nhận khi trùng ≥ 2 từ, hoặc
    tên DynaMed chỉ có đúng 1 từ đặc hiệu («Asthma», «Gout») và trùng từ đó; phải có DUY NHẤT một chủ đề điểm cao nhất. Ngược lại
    None — không đoán (đo 02/10: luật «trùng 1 từ bất kỳ» gắn «HR-positive metastatic breast cancer» vào chủ đề GLP-1 chỉ vì chữ
    «receptor»)."""
    tu_dm = _tu_dac_hieu(chu_de_dynamed)
    if not tu_dm:
        return None
    diem_ds = []
    for t in ds:
        trung = tu_dm & _tu_dac_hieu(f"{t.get('truy_van_du_phong') or ''} {t.get('query') or ''}")
        n = len(trung)
        if n >= 2 or (n == 1 and len(tu_dm) == 1):
            diem_ds.append((n, t.get("topic")))
    if not diem_ds:
        return None
    diem_ds.sort(reverse=True)
    if len(diem_ds) > 1 and diem_ds[0][0] == diem_ds[1][0]:
        return None
    return diem_ds[0][1]


def tao_tim_pubmed() -> Callable[[str], list[dict]]:
    """esearch + esummary (NCBI E-utilities, công khai). Trả [{pmid, title, journal, year, doi}] — tối đa 3 bài."""
    import urllib.parse  # noqa: PLC0415
    import urllib.request  # noqa: PLC0415
    import time  # noqa: PLC0415
    e = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def lay(url: str) -> dict:
        time.sleep(0.4)
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ebm-tra-cuu-co-tai-khoan/1"}),
                                    timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))

    def tim(term: str) -> list[dict]:
        ids = lay(e + "esearch.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "term": term, "retmax": 3, "retmode": "json",
                                                                 "tool": "ebm_tra_cuu_co_tai_khoan"}))["esearchresult"]["idlist"]
        if not ids:
            return []
        tom = lay(e + "esummary.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "json"}))["result"]
        ra = []
        for i in ids:
            x = tom.get(i) or {}
            doi = next((a.get("value", "") for a in x.get("articleids", []) if a.get("idtype") == "doi"), "")
            m = re.search(r"(19|20)\d{2}", x.get("pubdate", ""))
            ra.append({"pmid": i, "title": x.get("title", ""), "journal": x.get("fulljournalname", ""),
                       "year": int(m.group(0)) if m else None, "doi": doi.lower()})
        return ra
    return tim


def phan_giai_pubmed(cb: dict, tim: Callable[[str], list[dict]]) -> tuple[str, dict | None]:
    """(trạng thái, bài). Trạng thái: «mot» (đúng một bài) · «khong_thay» · «mo_ho» · «ngoai_pubmed» · «loi»."""
    td = tach_trich_dan(cb.get("trich_dan", ""))
    if td is None:
        return "ngoai_pubmed", None
    tk = cb.get("tu_khoa") or []
    if not tk:
        return "khong_thay", None
    goc = f'"{td["tap_chi"]}"[ta] AND {td["nam"]}[dp]'
    try:
        for n in (len(tk), 3, 2):            # nới dần số từ khoá; vẫn chỉ nhận khi ĐÚNG MỘT bài
            if n > len(tk) or n < 1:
                continue
            kq = tim(goc + "".join(f" AND {w}[tiab]" for w in tk[:n]))
            if len(kq) == 1:
                return "mot", kq[0]
            if len(kq) > 1:
                return "mo_ho", None
    except Exception:  # noqa: BLE001 — mạng/NCBI: không đoán
        return "loi", None
    return "khong_thay", None


def tu_canh_bao_dynamed(canh_bao: list[dict], ds_watch: list[dict], tim: Callable[[str], list[dict]], *,
                        tat_ca: bool = False) -> tuple[list[dict], dict]:
    """Cảnh báo ⇒ bản ghi để xác minh (chỉ cảnh báo gắn được chủ đề watchlist, trừ khi tat_ca) + báo cáo phân giải."""
    ban_ghi, bc = [], {"tong_canh_bao": len(canh_bao), "ngoai_watchlist": [], "ngoai_pubmed": [], "khong_phan_giai": []}
    for cb in canh_bao:
        chu_de = gan_chu_de(cb.get("chu_de_dynamed", ""), ds_watch)
        # Không mang chữ nào của DynaMed (tên chủ đề, trích dẫn, loại cảnh báo) — chỉ số thứ tự + ngày + chủ đề watchlist CỦA TA
        # (điều khoản EBSCO: không đưa nội dung vào công cụ AI; đầu ra này Claude đọc được).
        ngu_canh = (f"cảnh báo DynaMed #{cb.get('so_thu_tu', '?')} ({cb.get('ngay') or 'không rõ ngày'})"
                    + (f" → watchlist «{chu_de}»" if chu_de else ""))
        if chu_de is None and not tat_ca:
            bc["ngoai_watchlist"].append(ngu_canh)
            continue
        tt, bai = phan_giai_pubmed(cb, tim)
        if tt == "ngoai_pubmed":
            bc["ngoai_pubmed"].append(ngu_canh)
        elif tt != "mot" or not bai:
            bc["khong_phan_giai"].append(f"{ngu_canh} — {tt}")
        else:
            b = _ban_ghi(bai["title"], bai["year"], bai["journal"], bai["doi"], bai["pmid"], cb.get("loai", ""))
            if b:
                ban_ghi.append({**b, "chu_de": chu_de or "", "ngu_canh": ngu_canh})
    return ban_ghi, bc


# ── xác minh (engine) ───────────────────────────────────────────────────────────────────────────────────────────────────
def tao_xac_minh_engine() -> Callable[[dict], dict]:
    """Bộ xác minh THẬT của làn dự phòng; ném lỗi nếu engine vắng (người gọi trả mã 2, không ghi gì)."""
    mea = REPO / "medical-ebm-automation"
    if not (mea / "app" / "services" / "fallback_verification.py").exists():
        raise FileNotFoundError("không thấy medical-ebm-automation/app/services/fallback_verification.py")
    if str(mea) not in sys.path:
        sys.path.insert(0, str(mea))
    from app.services.fallback_verification import tao_bo_xac_minh  # noqa: PLC0415
    from app.sources.base import RawRecord  # noqa: PLC0415
    fn = tao_bo_xac_minh()

    def xm(b: dict) -> dict:
        rec = RawRecord(source=b["_nguon"], title=b["title"], authors=b.get("tac_gia") or None,
                        journal_or_organization=b["journal"] or None,
                        publication_date=str(b["year"]) if b["year"] else None, doi=b["doi"] or None,
                        pmid=b["pmid"] or None, document_type=b.get("loai") or None)
        kq = fn(rec)
        ra = {"ket_qua": kq.ket_qua, "ly_do": kq.ly_do}
        if kq.ban_ghi is not None:
            g = kq.ban_ghi
            ra.update(pmid=g.pmid or "", doi=(g.doi or "").lower(), title=g.title or b["title"],
                      journal=g.journal_or_organization or b["journal"], study_type=g.study_type or "",
                      co=list((g.raw or {}).get("co") or []))
        return ra
    return xm


def nhap(duong: Path, nguon: str, chu_de: str, *, toi_da: int, xac_minh: Callable[[dict], dict],
         pm_kho: set[str], doi_kho: set[str]) -> dict:
    """Đọc tệp export → `xu_ly`. Không ghi gì (hàm thuần trừ mạng)."""
    dang, ban_ghi = doc_tep(duong)
    return xu_ly(ban_ghi, nguon, duong.name, dang, chu_de, toi_da=toi_da, xac_minh=xac_minh, pm_kho=pm_kho, doi_kho=doi_kho)


def xu_ly(ban_ghi: list[dict], nguon: str, ten_tep: str, dang: str, chu_de: str, *, toi_da: int,
          xac_minh: Callable[[dict], dict], pm_kho: set[str], doi_kho: set[str]) -> dict:
    """Bỏ trùng → xếp hạng → xác minh (≤ toi_da × HE_SO_XAC_MINH) → chọn ≤ toi_da. Bản ghi có khoá `chu_de` riêng thì giữ chủ đề đó."""
    bao_cao = {"tep": ten_tep, "dinh_dang": dang, "nguon": nguon, "chu_de": chu_de, "doc_duoc": len(ban_ghi),
               "dem": {}, "chon": [], "bo": [], "rut_bai": [], "khong_xac_minh_vuot_tran": 0}
    if not dang:
        return bao_cao
    ds, dem = chuan_bi(ban_ghi, pm_kho, doi_kho)
    bao_cao["dem"] = dict(dem)
    tran = toi_da * HE_SO_XAC_MINH
    bao_cao["khong_xac_minh_vuot_tran"] = max(0, len(ds) - tran)
    for b in ds[:tran]:
        b = {**b, "_nguon": nguon}
        kq = xac_minh(b)
        # Scopus là nội dung Elsevier — điều khoản cấm dùng với công cụ AI ⇒ không mang tiêu đề export ra đầu ra/báo cáo phiên;
        # ứng viên được chọn nhận tiêu đề từ Crossref/PubMed (bước xác minh).
        hang = {"title": "" if nguon == "scopus" else b["title"], "doi": b["doi"], "pmid": b["pmid"], "year": b["year"],
                "loai_export": b["loai"],
                "ket_qua": kq["ket_qua"], "ly_do": kq.get("ly_do", ""), "chu_de": b.get("chu_de") or chu_de,
                **({"ngu_canh": b["ngu_canh"]} if b.get("ngu_canh") else {})}
        if kq["ket_qua"] == "bi_rut_bai":
            bao_cao["rut_bai"].append(hang)
        elif kq["ket_qua"] == "xac_minh_duoc" and len(bao_cao["chon"]) < toi_da:
            # Trường RỖNG của bản ghi cơ quan đăng ký không được xoá định danh đã biết (bản ghi Crossref không mang PMID — đo 02/10).
            bao_cao["chon"].append({**hang, **{k: kq[k] for k in ("pmid", "doi", "title", "journal", "study_type", "co") if kq.get(k)}})
        else:
            bao_cao["bo"].append(hang)
    bao_cao["dem"]["xac_minh_loi"] = sum(1 for h in bao_cao["bo"] if h["ket_qua"] == "loi_xac_minh")
    bao_cao["dem"]["da_xac_minh"] = min(len(ds), tran)
    return bao_cao


def dong_hang(bc: dict, hom_nay: date) -> list[dict]:
    """Dòng JSONL cho `ung-vien-ngoai-quet.jsonl` — cùng khoá với các dòng hiện có, thêm khối xác minh."""
    ten_nguon = {"scopus": "Scopus web", "wos": "Web of Science web", "dynamed": "DynaMed Recent Alerts"}.get(bc["nguon"], bc["nguon"])
    cach = "đọc trang cảnh báo" if bc["nguon"] == "dynamed" else "export"
    return [{"pmid": c.get("pmid", ""), "doi": c.get("doi", ""), "title": c["title"], "journal": c.get("journal", ""),
             "pubtype": c.get("study_type") or c.get("loai_export", ""), "chu_de": c.get("chu_de") or bc["chu_de"],
             "nguon_phat_hien": f"{ten_nguon} — bác sĩ đăng nhập, {cach} «{bc['tep']}», nhập {hom_nay:%d/%m/%Y}"
                                + (f" · {c['ngu_canh']}" if c.get("ngu_canh") else ""),
             "lien_quan": "", "trang_thai": "CANDIDATE", "ghi_luc": hom_nay.isoformat(),
             "xac_minh": {"ket_qua": c["ket_qua"], "ly_do": c.get("ly_do", ""), "co": c.get("co", [])},
             "rut_bai": "đã qua cổng rút bài Crossref/Scite lúc nhập — gói tuần kiểm lại chuỗi 3 tầng (bước 4)"}
            for c in bc["chon"]]


def ghi_ket_qua(bc: dict, hom_nay: date, hang: Path | None = None, thu_muc_bao_cao: Path | None = None) -> Path:
    hang, thu_muc_bao_cao = hang or HANG_NGOAI_QUET, thu_muc_bao_cao or BAO_CAO_PHIEN
    thu_muc_bao_cao.mkdir(parents=True, exist_ok=True)
    bc_tep = thu_muc_bao_cao / f"{datetime.now():%Y%m%d-%H%M%S}-{bc['nguon']}.json"
    tam = bc_tep.with_name(bc_tep.name + f".tmp{os.getpid()}")
    tam.write_text(json.dumps(bc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    os.replace(tam, bc_tep)
    if bc["chon"]:
        hang.parent.mkdir(parents=True, exist_ok=True)
        with hang.open("a", encoding="utf-8", newline="\n") as f:
            for d in dong_hang(bc, hom_nay):
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
    return bc_tep


def in_bao_cao(bc: dict, ghi: bool) -> None:
    print(f"NHẬP {bc['nguon'].upper()} — «{bc['tep']}» ({bc['dinh_dang'] or 'KHÔNG nhận dạng'}) · chủ đề «{bc['chu_de']}»")
    d = bc["dem"]
    print(f"  đọc {bc['doc_duoc']} · trùng trong tệp {d.get('trung_trong_tep', 0)} · đã có kho/hàng {d.get('da_co_trong_kho_hoac_hang', 0)}"
          f" · đã xác minh {d.get('da_xac_minh', 0)} · không xác minh (vượt trần {HE_SO_XAC_MINH}×) {bc['khong_xac_minh_vuot_tran']}")
    for c in bc["chon"]:
        print(f"  ✓ [{c.get('study_type') or c.get('loai_export') or '?'}] {c['title'][:95]} · PMID {c.get('pmid') or '—'} · DOI {c.get('doi') or '—'}")
    for r in bc["rut_bai"]:
        dinh_danh = " · ".join(x for x in (f"PMID {r['pmid']}" if r.get("pmid") else "", f"DOI {r['doi']}" if r.get("doi") else "") if x)
        print(f"  🔴 BỊ RÚT/THÔNG BÁO RÚT — KHÔNG đưa vào: {dinh_danh or r['title'][:90]} ({r['ly_do'][:80]})")
    bo = {}
    for h in bc["bo"]:
        bo[h["ket_qua"]] = bo.get(h["ket_qua"], 0) + 1
    if bo:
        print("  bỏ (không thành ứng viên): " + " · ".join(f"{k} {v}" for k, v in sorted(bo.items())))
    print(("  → ĐÃ GHI" if ghi else "  → CHẠY THỬ (chưa ghi; thêm --ghi để nối vào ung-vien-ngoai-quet.jsonl)") +
          f" {len(bc['chon'])} ứng viên CANDIDATE. Cần bác sĩ kiểm chứng.")


def _chay_dynamed(tep: Path, ds: list[dict], a) -> int:
    try:
        van_ban = tep.read_text(encoding="utf-8")
    except OSError as e:
        print(f"✗ Không đọc được {tep}: {e}")
        return 3
    canh_bao = doc_canh_bao_dynamed(van_ban)
    if not canh_bao:
        print("✗ Không tách được cảnh báo nào (văn bản không phải trang DynaMed Recent Alerts?) — không ghi gì.")
        return 3
    try:
        xm = tao_xac_minh_engine()
    except Exception as e:  # noqa: BLE001
        print(f"⚪ KHÔNG XÁC MINH ĐƯỢC — engine vắng/lỗi ({type(e).__name__}: {e}). Không ghi gì.")
        return 2
    ban_ghi, bcdm = tu_canh_bao_dynamed(canh_bao, ds, tao_tim_pubmed(), tat_ca=a.tat_ca)
    pm_kho, doi_kho = da_co()
    bc = xu_ly(ban_ghi, "dynamed", tep.name, "dynamed_canh_bao", "(theo từng cảnh báo)", toi_da=a.toi_da, xac_minh=xm,
               pm_kho=pm_kho, doi_kho=doi_kho)
    bc["dynamed"] = bcdm
    if a.ghi:
        print(f"  báo cáo phiên: {ghi_ket_qua(bc, date.today())}")
    in_bao_cao(bc, a.ghi)
    print(f"  DynaMed: {bcdm['tong_canh_bao']} cảnh báo · {len(bcdm['ngoai_watchlist'])} ngoài watchlist · "
          f"{len(bcdm['ngoai_pubmed'])} nguồn ngoài PubMed · {len(bcdm['khong_phan_giai'])} không phân giải được PMID")
    for nhan, k in (("👤 NGUỒN NGOÀI PUBMED (bác sĩ đọc trên DynaMed/cơ quan gốc)", "ngoai_pubmed"),
                    ("⚪ không phân giải được đúng MỘT PMID", "khong_phan_giai"),
                    ("ⓘ chủ đề DynaMed ngoài watchlist (dấu hiệu khoảng trống giám sát?)", "ngoai_watchlist")):
        if bcdm[k]:
            print(f"  {nhan}:")
            for x in bcdm[k][:12]:
                print(f"    - {x}")
            if len(bcdm[k]) > 12:
                print(f"    … và {len(bcdm[k]) - 12} mục nữa (đủ trong báo cáo phiên khi --ghi)")
    return 0 if bc["chon"] else 1


def main(argv: list[str] | None = None) -> int:
    for luong in (sys.stdout, sys.stderr):
        try:
            if "utf" not in (getattr(luong, "encoding", "") or "").lower() and hasattr(luong, "reconfigure"):
                luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Scopus/WoS qua tài khoản của bác sĩ: phiếu câu tìm + nhập tệp export")
    ap.add_argument("--phieu", action="store_true", help="in phiếu câu tìm + các bước bấm")
    ap.add_argument("--chu-de", action="append", default=[], help="tên (một phần) chủ đề watchlist; lặp được")
    ap.add_argument("--mu", action="store_true", help="(--phieu) thêm các chủ đề kiem_san_luong_giam_sat báo «mù»")
    ap.add_argument("--md", default="", help="(--phieu) ghi phiếu ra tệp Markdown này")
    ap.add_argument("--nhap", default="", help="tệp export (Scopus CSV/RIS · WoS tab/plain/RIS)")
    ap.add_argument("--nguon", choices=("scopus", "wos"), default=None, help="nguồn của tệp (mặc định suy từ định dạng)")
    ap.add_argument("--toi-da", type=int, default=TOI_DA_MAC_DINH)
    ap.add_argument("--ghi", action="store_true", help="(--nhap/--dynamed-canh-bao) nối ứng viên vào ung-vien-ngoai-quet.jsonl + báo cáo phiên")
    ap.add_argument("--dynamed-canh-bao", default="", help="tệp văn bản trang DynaMed Recent Alerts (Claude đọc bằng get_page_text)")
    ap.add_argument("--tat-ca", action="store_true", help="(--dynamed-canh-bao) tra cả cảnh báo không gắn được chủ đề watchlist")
    ap.add_argument("--huong-dan", action="store_true", help="in quy trình Scopus/WoS/DynaMed")
    a = ap.parse_args(argv)
    if a.huong_dan:
        print("\n\n".join((HUONG_DAN_SCOPUS, HUONG_DAN_WOS, HUONG_DAN_DYNAMED, HUONG_DAN_NHAP)))
        return 0
    try:
        ds = doc_watchlist()
    except (OSError, ValueError) as e:
        print(f"⚪ KHÔNG ĐỌC ĐƯỢC watchlist ({WATCHLIST}): {e}")
        return 3
    if a.phieu:
        chon = chon_chu_de(ds, a.chu_de, a.mu)
        if not chon:
            print("Chưa chọn chủ đề nào (dùng --chu-de \"<tên>\" và/hoặc --mu).")
            return 3
        vb = phieu(chon, date.today().year)
        print(vb)
        if a.md:
            Path(a.md).write_text(vb + "\n", encoding="utf-8", newline="\n")
        return 0
    if a.dynamed_canh_bao:
        return _chay_dynamed(Path(a.dynamed_canh_bao).expanduser(), ds, a)
    if not a.nhap:
        ap.print_help()
        return 3
    tep = Path(a.nhap).expanduser()
    chu_de = [t for t in ds if a.chu_de and any(_bo_dau(k) in _bo_dau(t.get("topic", "")) for k in a.chu_de)]
    if len(chu_de) != 1:
        print(f"✗ --chu-de phải khớp ĐÚNG MỘT chủ đề watchlist (khớp {len(chu_de)}): "
              + "; ".join(t.get("topic", "") for t in chu_de[:5]))
        return 3
    if not tep.exists():
        print(f"✗ Không thấy tệp {tep}")
        return 3
    dang, _ = doc_tep(tep)
    if not dang:
        print(f"✗ Không nhận dạng được định dạng tệp {tep.name} (cần Scopus CSV/RIS hoặc WoS tab/plain/RIS)")
        return 3
    nguon = a.nguon or ("scopus" if dang == "scopus_csv" else "wos" if dang.startswith("wos") else "")
    if not nguon:
        print("✗ Tệp RIS không tự nói nguồn — thêm --nguon scopus|wos")
        return 3
    try:
        xm = tao_xac_minh_engine()
    except Exception as e:  # noqa: BLE001
        print(f"⚪ KHÔNG XÁC MINH ĐƯỢC — engine vắng/lỗi ({type(e).__name__}: {e}). Không ghi gì: bản ghi chưa xác minh không bao "
              "giờ thành ứng viên.")
        return 2
    pm_kho, doi_kho = da_co()
    bc = nhap(tep, nguon, chu_de[0]["topic"], toi_da=a.toi_da, xac_minh=xm, pm_kho=pm_kho, doi_kho=doi_kho)
    if bc["dem"].get("da_xac_minh") and bc["dem"].get("xac_minh_loi") == bc["dem"]["da_xac_minh"]:
        in_bao_cao(bc, False)
        print("⚪ MỌI lượt xác minh đều LỖI (mạng/NCBI/Crossref) — không ghi gì; chạy lại khi mạng ổn. KHÔNG phải «không có bài».")
        return 2
    if a.ghi:
        p = ghi_ket_qua(bc, date.today())
        print(f"  báo cáo phiên: {p}")
    in_bao_cao(bc, a.ghi)
    return 0 if bc["chon"] else 1


if __name__ == "__main__":
    sys.exit(main())
