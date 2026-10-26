#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""in_pdf_toan_van_kho.py — IN TOÀN VĂN HTML/XML ĐÃ ĐỌC trong kho thành PDF để EndNote gắn được (18/10/2026).

VÌ SAO CÓ. Bác sĩ báo 18/10/2026 «Các trích dẫn trong EndNote vẫn chưa đầy đủ về toàn văn». Đo cùng ngày trên 873 bản ghi của
60 nhóm «EBM · …»: 370 đã có tệp, nhưng **320 bản ghi có toàn văn THẬT trong kho dưới dạng XML JATS (PMC) hoặc HTML (Unpaywall,
phiên Chrome có uỷ quyền) mà EndNote vẫn trống** — `nap_endnote_chu_de.py` chỉ gắn `PMID-<n>_*.pdf`. Toàn văn đã đọc, đã qua cổng
nội dung, chỉ thiếu một bản PDF để đính kèm.

LÀM GÌ. Với mỗi PMID mà kho có toàn văn thật (`doc_toan_van_co_nguoi.tep_toan_van_that` — HTML phải qua cổng nội dung) nhưng
CHƯA có PDF nào: dựng HTML in (JATS → HTML tối giản; HTML lưu sẵn → bỏ script/ảnh/khung nhúng/tài nguyên ngoài), in bằng Chrome
headless (cùng cách `docx_sang_pdf_giu_mau.py`) ra `PMID-<n>_BANIN.pdf`. `nap_endnote_chu_de.py` nhận hậu tố `BANIN` với ưu tiên
THẤP NHẤT (PDF gốc của NXB/Unpaywall/TDM luôn thắng).

KHÔNG LÀM GÌ.
  • Không tạo toàn văn mới: `BANIN` KHÔNG khớp `TEN_TEP_TOAN_VAN` ⇒ sổ toàn văn (`bao_phu_cuc_bo`) và cổng BH161 không đếm nó —
    độ phủ chỉ tính từ tệp nguồn đã qua cổng.
  • Không in trang chỉ có tóm tắt/tường phí: HTML không qua cổng nội dung bị bỏ (fail-closed).
  • Không gọi mạng: mọi `<script>`, `<img>`, `<iframe>`, `<link>`, `<object>`, `<video>`, `<audio>`, `<source>` bị gỡ trước khi in
    (bản lưu phiên Chrome còn nhúng PDF base64 trong `<script>` — cũng gỡ).
  • Bản in từ `_CHR.html` là nội dung CÓ BẢN QUYỀN lưu trong phiên uỷ quyền của bác sĩ: dải đầu trang ghi rõ nguồn và «dùng nội
    bộ, không phân phối lại» (doctrine §2septies).

Chạy:  python3 tools/in_pdf_toan_van_kho.py                       # chạy khô: liệt kê bài sẽ in
       python3 tools/in_pdf_toan_van_kho.py --ap-dung             # in thật vào kho
       python3 tools/in_pdf_toan_van_kho.py --file <dashboard> --ap-dung   # chỉ PMID của một dashboard (bộ năm ⑧)
       python3 tools/in_pdf_toan_van_kho.py --pmid 123 456 --ap-dung
Sau khi in: `python3 tools/nap_endnote_chu_de.py --gan-kho --ap-dung` gắn PDF vào bản ghi chưa có tệp.
Mã thoát: 0 xong (hoặc không có gì để in) · 1 có bài in lỗi · 2 không đo được (thiếu kho/trình duyệt) · 3 tham số sai.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import html as _html
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

TOOLS = Path(__file__).resolve().parent
HAU_TO = "BANIN"
MA_OK, MA_LOI, MA_KHONG_DO, MA_THAM_SO = 0, 1, 2, 3
CO_TOI_THIEU = 2048            # PDF nhỏ hơn mức này coi như in hỏng (trang trắng)
THOI_GIAN_IN = 180

_TAG_GO = re.compile(r"<(script|style|iframe|object|video|audio|noscript|svg|template)\b[^>]*>.*?</\1\s*>", re.I | re.S)
_TAG_DON_GO = re.compile(r"<(img|link|source|embed|meta|base|input|iframe|script)\b[^>]*/?>", re.I)
_TAG_HTML_MO = re.compile(r"<\s*(html|head|body)\b[^>]*>", re.I)
_TAG_HTML_DONG = re.compile(r"<\s*/\s*(html|head|body)\s*>", re.I)
_DOCTYPE = re.compile(r"<!doctype[^>]*>", re.I)
_CHU_THICH_PHIEN = re.compile(r"<!--\s*ebm-phien:.*?-->", re.S)

CSS = """
@page { size: A4; margin: 14mm 13mm; }
body { font: 10.5pt/1.45 "Times New Roman", Georgia, serif; color: #111; }
.banin { font: 8.5pt/1.35 -apple-system, Helvetica, Arial, sans-serif; color: #444; border: 1px solid #bbb;
         background: #f4f4f4; padding: 6px 8px; margin-bottom: 12px; }
h1 { font-size: 15pt; line-height: 1.25; margin: 4px 0 6px; }
h2 { font-size: 12.5pt; margin: 14px 0 4px; }
h3 { font-size: 11pt; margin: 10px 0 3px; }
h4, h5, h6 { font-size: 10.5pt; margin: 8px 0 2px; }
.meta { font-size: 9pt; color: #333; margin: 2px 0; }
table { border-collapse: collapse; font-size: 8.5pt; margin: 6px 0; max-width: 100%; }
td, th { border: 1px solid #999; padding: 2px 4px; vertical-align: top; }
.bang, .hinh, .hop { margin: 8px 0; page-break-inside: avoid; }
.chu-thich { font-size: 9pt; }
ol.tltk { font-size: 8.5pt; }
blockquote { margin: 6px 18px; color: #333; }
"""


# ───────────────────────── nạp mô-đun anh em ─────────────────────────

def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


_DTV = None


def dtv():
    """Mô-đun `doc_toan_van_co_nguoi` — nguồn sự thật DUY NHẤT về «tệp toàn văn thật» và vị trí kho."""
    global _DTV
    if _DTV is None:
        _DTV = _nap("_dtv_in_pdf", "doc_toan_van_co_nguoi.py")
    return _DTV


# ───────────────────────── JATS → HTML ─────────────────────────

def _ten(el: ET.Element) -> str:
    """Tên thẻ bỏ không gian tên ({mml}math → math)."""
    return el.tag.rsplit("}", 1)[-1] if isinstance(el.tag, str) else ""


def _e(s: str | None) -> str:
    return _html.escape(s or "", quote=False)


_THE_NOI_TUYEN = {"italic": "i", "bold": "b", "sup": "sup", "sub": "sub", "underline": "u", "sc": "span", "monospace": "code"}
_BO_QUA = {"graphic", "inline-graphic", "media", "alternatives-graphic", "object-id", "permissions", "custom-meta-group",
           "funding-group", "history", "kwd-group", "counts", "article-categories", "self-uri", "related-article",
           "processing-meta"}
_THE_BANG = {"table", "thead", "tbody", "tfoot", "tr", "td", "th", "col", "colgroup"}


def _con(el: ET.Element, sau: int) -> str:
    """Nội dung bên trong một phần tử: text + từng con (kèm tail)."""
    out = [_e(el.text)]
    for c in el:
        out.append(_dung(c, sau))
        out.append(_e(c.tail))
    return "".join(out)


def _dung(el: ET.Element, sau: int = 2) -> str:
    """Một phần tử JATS → HTML (không gồm tail). `sau` = cấp đề mục cho tiêu đề phần kế tiếp."""
    t = _ten(el)
    if t in _BO_QUA:
        return ""
    if t in _THE_NOI_TUYEN:
        h = _THE_NOI_TUYEN[t]
        return f"<{h}>{_con(el, sau)}</{h}>"
    if t == "p":
        return f"<p>{_con(el, sau)}</p>"
    if t == "sec" or t == "app" or t == "ack":
        tieu_de = el.find("./{*}title") if el.find("./{*}title") is not None else el.find("title")
        cap = min(max(sau, 2), 6)
        dau = f"<h{cap}>{_con(tieu_de, sau + 1)}</h{cap}>" if tieu_de is not None else ""
        than = "".join(_dung(c, sau + 1) + _e(c.tail) for c in el if c is not tieu_de)
        return f"<div class='muc'>{dau}{than}</div>"
    if t == "title":
        cap = min(max(sau, 2), 6)
        return f"<h{cap}>{_con(el, sau)}</h{cap}>"
    if t in ("list",):
        loai = "ol" if (el.get("list-type") or "").startswith(("order", "alpha", "roman")) else "ul"
        return f"<{loai}>" + "".join(_dung(c, sau) for c in el if _ten(c) == "list-item") + f"</{loai}>"
    if t == "list-item":
        return f"<li>{_con(el, sau)}</li>"
    if t == "disp-quote":
        return f"<blockquote>{_con(el, sau)}</blockquote>"
    if t == "table-wrap":
        nhan = el.find("./{*}label") if el.find("./{*}label") is not None else el.find("label")
        tom = el.find("./{*}caption") if el.find("./{*}caption") is not None else el.find("caption")
        dau = (f"<b>{_con(nhan, sau)}</b> " if nhan is not None else "") + (_con(tom, sau) if tom is not None else "")
        bang = "".join(_dung(c, sau) for c in el.iter() if _ten(c) == "table")
        chan = "".join(f"<div class='chu-thich'>{_con(c, sau)}</div>" for c in el if _ten(c) == "table-wrap-foot")
        return f"<div class='bang'><div class='chu-thich'>{dau}</div>{bang}{chan}</div>"
    if t in _THE_BANG:
        thuoc = "".join(f' {k}="{_html.escape(v)}"' for k, v in el.attrib.items() if k in ("colspan", "rowspan"))
        return f"<{t}{thuoc}>{_con(el, sau)}</{t}>"
    if t == "fig":
        nhan = el.find("./{*}label") if el.find("./{*}label") is not None else el.find("label")
        tom = el.find("./{*}caption") if el.find("./{*}caption") is not None else el.find("caption")
        dau = (f"<b>{_con(nhan, sau)}</b> " if nhan is not None else "") + (_con(tom, sau) if tom is not None else "")
        return f"<div class='hinh chu-thich'>[Hình — chỉ giữ chú thích] {dau}</div>"
    if t == "boxed-text":
        return f"<div class='hop'>{_con(el, sau)}</div>"
    if t in ("label", "caption"):
        return _con(el, sau)
    if t in ("xref", "ext-link", "uri", "named-content", "styled-content", "abbrev", "email"):
        return _con(el, sau)
    if t in ("disp-formula", "inline-formula", "math"):
        return f"<span>{_e(''.join(el.itertext()))}</span>"
    if t in ("fn",):
        return f"<div class='chu-thich'>{_con(el, sau)}</div>"
    if t == "break":
        return "<br>"
    return _con(el, sau)


def _tim(goc: ET.Element, ten: str) -> ET.Element | None:
    for e in goc.iter():
        if _ten(e) == ten:
            return e
    return None


def _chu(e: ET.Element | None) -> str:
    return " ".join("".join(e.itertext()).split()) if e is not None else ""


def jats_sang_html(du_lieu: bytes) -> str:
    """XML JATS (PMC) → thân HTML in được: tiêu đề · tác giả · tạp chí/năm/định danh · Abstract · thân bài · tài liệu tham khảo.
    Không tải tài nguyên ngoài (hình chỉ giữ chú thích). XML hỏng ⇒ ValueError (người gọi bỏ bài đó, không in trang rỗng)."""
    try:
        goc = ET.fromstring(du_lieu)
    except ET.ParseError as e:
        raise ValueError(f"XML JATS hỏng: {e}") from e
    meta = _tim(goc, "article-meta")
    phan: list[str] = []
    tieu_de = _tim(meta, "article-title") if meta is not None else None
    if tieu_de is not None:
        phan.append(f"<h1>{_con(tieu_de, 2)}</h1>")
    if meta is not None:
        ten_tg = []
        for c in meta.iter():
            if _ten(c) == "contrib" and (c.get("contrib-type") in (None, "author")):
                ho = _chu(_tim(c, "surname"))
                ten = _chu(_tim(c, "given-names"))
                nhom = _chu(_tim(c, "collab"))
                if ho or ten or nhom:
                    ten_tg.append(nhom or f"{ten} {ho}".strip())
        if ten_tg:
            phan.append(f"<p class='meta'>{_e(', '.join(ten_tg))}</p>")
        tap_chi = _chu(_tim(goc, "journal-title"))
        nam = _chu(_tim(meta, "year"))
        tap = _chu(_tim(meta, "volume"))
        so = _chu(_tim(meta, "issue"))
        trang = "-".join(x for x in (_chu(_tim(meta, "fpage")), _chu(_tim(meta, "lpage"))) if x)
        dong = ", ".join(x for x in (tap_chi, nam, f"tập {tap}" if tap else "", f"số {so}" if so else "",
                                     f"tr. {trang}" if trang else "") if x)
        if dong:
            phan.append(f"<p class='meta'>{_e(dong)}</p>")
        dd = []
        for c in meta.iter():
            if _ten(c) == "article-id" and c.get("pub-id-type") in ("pmid", "pmc", "pmcid", "doi"):
                dd.append(f"{c.get('pub-id-type').upper()}: {_chu(c)}")
        if dd:
            phan.append(f"<p class='meta'>{_e(' · '.join(dd))}</p>")
        for c in meta:
            if _ten(c) == "abstract":
                tieu = c.get("abstract-type")
                co_tieu_de = any(_ten(x) == "title" for x in c)      # abstract tự có <title> ⇒ không thêm đề mục trùng
                dau = "" if co_tieu_de else f"<h2>Abstract{' (' + _e(tieu) + ')' if tieu else ''}</h2>"
                phan.append(f"{dau}{_con(c, 2 if co_tieu_de else 3)}")
    than = _tim(goc, "body")
    if than is not None:
        phan.append(_con(than, 2))
    sau_bai = _tim(goc, "back")
    if sau_bai is not None:
        for c in sau_bai:
            t = _ten(c)
            if t == "ref-list":
                refs = [f"<li>{_e(' '.join(''.join(r.itertext()).split()))}</li>" for r in c.iter() if _ten(r) == "ref"]
                phan.append("<h2>References</h2><ol class='tltk'>" + "".join(refs) + "</ol>")
            elif t in ("ack", "app-group", "fn-group", "sec", "notes", "glossary"):
                phan.append(_dung(c, 2))
    khai = _khai_bao_tac_gia(meta) if meta is not None else ""
    if khai:
        phan.append(khai)
    return "\n".join(phan)


def _khai_bao_tac_gia(meta: ET.Element) -> str:
    """Khai báo nằm trong `article-meta`: `author-notes/fn|p` (xung đột lợi ích, đóng góp, ghi chú tác giả) và `funding-group`
    (câu khai tài trợ, hoặc tên nhà tài trợ + mã tài trợ). Bỏ `corresp` (địa chỉ liên hệ).

    Đo 26/10/2026: trước bản vá hai khối này bị bỏ hẳn ⇒ 267/752 bản in từ JATS thiếu `author-notes/fn`, 288 thiếu
    `funding-group`; tóm tắt ⑨ đọc bản in nên ghi «bài không khai xung đột lợi ích» trong khi bài CÓ khai (PMID 42799440,
    42914541) — kéo theo chấm sai AMSTAR-2 mục 16 / AGREE II Miền 6."""
    muc: list[str] = []
    for c in meta:
        if _ten(c) == "author-notes":
            # `fn` (BMJ, Springer…) và `p` đặt thẳng trong author-notes (JAMA «Article Information»: COI, tài trợ, vai trò nhà
            # tài trợ — đo 27/10/2026: 22 XML trong kho); bỏ `corresp` (địa chỉ liên hệ) và `title` (đã có đề mục riêng).
            muc += [_dung(x, 3) for x in c if _ten(x) in ("fn", "p")]
    for fg in (c for c in meta if _ten(c) == "funding-group"):
        cau = [f"<p>{_con(x, 3)}</p>" for x in fg.iter() if _ten(x) == "funding-statement"]
        if not cau:
            for ag in (x for x in fg.iter() if _ten(x) == "award-group"):
                ten = " · ".join(_chu(x) for x in ag.iter() if _ten(x) == "funding-source" and _chu(x))
                ma = ", ".join(_chu(x) for x in ag.iter() if _ten(x) == "award-id" and _chu(x))
                if ten:
                    cau.append(f"<p>Funding: {_e(ten)}{' (' + _e(ma) + ')' if ma else ''}</p>")
        muc += cau
    if not muc:
        return ""
    return "<h2>Author notes and funding (article metadata)</h2>" + "".join(muc)


# ───────────────────────── HTML lưu sẵn → HTML in ─────────────────────────

def lam_sach_html(van_ban: str) -> str:
    """HTML lưu từ trang (Unpaywall/phiên Chrome) → THÂN HTML an toàn để in: gỡ mọi script/style/khung nhúng/ảnh/liên kết tài
    nguyên (không có lượt gọi mạng nào lúc in; PDF base64 nhúng trong `<script>` của bộ lưu Chrome cũng bị gỡ), gỡ vỏ
    html/head/body và chú thích dấu phiên."""
    s = _CHU_THICH_PHIEN.sub("", van_ban)
    s = _DOCTYPE.sub("", s)
    s = _TAG_GO.sub("", s)
    s = _TAG_DON_GO.sub("", s)
    s = re.sub(r"<head\b[^>]*>.*?</head\s*>", "", s, flags=re.I | re.S)
    s = _TAG_HTML_MO.sub("", s)
    s = _TAG_HTML_DONG.sub("", s)
    s = re.sub(r"\s(on[a-z]+)\s*=\s*(\"[^\"]*\"|'[^']*')", "", s, flags=re.I)          # bỏ trình xử lý sự kiện
    s = re.sub(r"\s(src|srcset|data-src)\s*=\s*(\"[^\"]*\"|'[^']*')", "", s, flags=re.I)  # bỏ mọi nguồn tải còn sót
    return s.strip()


def bao_trang(than: str, pmid: str, nguon: Path, hom_nay: date | None = None) -> str:
    """Bọc thân HTML thành trang in có dải ghi nguồn ở đầu trang."""
    hom_nay = hom_nay or date.today()
    loai = {"PMC": "XML JATS (PMC Open Access)", "UPW": "bản mang giấy phép mở (Unpaywall)",
            "CHR": "bản lưu trong phiên trình duyệt có uỷ quyền của bác sĩ — CÓ BẢN QUYỀN"}
    nhan = next((v for k, v in loai.items() if f"_{k}" in nguon.name), "kho toàn văn")
    dai = (f"<div class='banin'><b>BẢN IN TỪ KHO TOÀN VĂN EBM</b> · PMID {_e(pmid)} · nguồn: {_e(nguon.name)} ({_e(nhan)}) · "
           f"in ngày {hom_nay.strftime('%d/%m/%Y')} — không phải bản PDF của nhà xuất bản; hình không kèm; dùng nội bộ để đọc và "
           f"đối chiếu, không phân phối lại.</div>")
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>PMID {_e(pmid)}</title><style>{CSS}</style></head>"
            f"<body>{dai}{than}</body></html>")


# ───────────────────────── chọn bài ─────────────────────────

def chon_nguon(kho: Path, pmid: str) -> Path | None:
    """Tệp nguồn để in cho MỘT PMID, hoặc None khi: không có toàn văn thật · ĐÃ có PDF thật (EndNote gắn PDF đó) · đã có bản in.
    Ưu tiên: XML JATS của PMC > HTML Unpaywall > HTML phiên Chrome."""
    if (Path(kho) / f"PMID-{pmid}_{HAU_TO}.pdf").exists():
        return None
    that = dtv().tep_toan_van_that(Path(kho), str(pmid))
    if not that or any(q.suffix.lower() == ".pdf" for q in that):
        return None
    for mau in ("_PMC", "_UPW", "_CHR"):
        for q in that:
            if mau in q.name and q.suffix.lower() in (".xml", ".html"):
                return q
    return None


def pmid_trong_kho(kho: Path) -> list[str]:
    ra = set()
    for q in Path(kho).glob("PMID-*_*"):
        m = re.match(r"PMID-(\d{1,9})_", q.name)
        if m:
            ra.add(m.group(1))
    return sorted(ra, key=int)


def pmid_cua_dashboard(tep: Path) -> list[str]:
    """PMID của các mục trong khối DATA một dashboard (khoá `pmid:` của mục và mọi trường nguồn)."""
    s = Path(tep).read_text(encoding="utf-8", errors="replace")
    i = s.find("const DATA")
    j = s.find("HẾT KHỐI DATA", i) if i >= 0 else -1
    khoi = s[i:j if j > 0 else len(s)] if i >= 0 else ""
    return sorted(set(re.findall(r"pmid\s*:\s*['\"](\d{6,9})['\"]", khoi)), key=int)


def ung_vien(kho: Path, pmids: list[str] | None = None) -> list[tuple[str, Path]]:
    ds = pmids if pmids is not None else pmid_trong_kho(kho)
    ra = []
    for pm in ds:
        q = chon_nguon(kho, pm)
        if q is not None:
            ra.append((pm, q))
    return ra


# ───────────────────────── in ─────────────────────────

def html_in(pmid: str, nguon: Path) -> str:
    du_lieu = nguon.read_bytes()
    if nguon.suffix.lower() == ".xml":
        than = jats_sang_html(du_lieu)
    else:
        than = lam_sach_html(du_lieu.decode("utf-8", errors="replace"))
    if len(re.sub(r"<[^>]+>", " ", than).split()) < 300:
        raise ValueError("thân bài sau khi dựng quá ngắn (< 300 từ) — không in")
    return bao_trang(than, pmid, nguon)


def in_pdf(html: str, ra: Path, trinh_duyet: str) -> None:
    """In HTML ra PDF bằng Chrome headless; ghi NGUYÊN TỬ (tệp tạm → đổi tên). PDF hỏng/rỗng ⇒ RuntimeError, không để lại gì."""
    with tempfile.TemporaryDirectory() as tmp:
        nguon = Path(tmp) / "in.html"
        nguon.write_text(html, encoding="utf-8")
        tam = Path(tmp) / "ra.pdf"
        lenh = [trinh_duyet, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--print-background",
                "--disable-background-networking", "--disable-extensions", "--no-first-run",
                f"--user-data-dir={Path(tmp) / 'ho-so'}"]
        _euid = getattr(os, "geteuid", None)
        if _euid is not None and _euid() == 0:
            lenh.append("--no-sandbox")
        lenh += [f"--print-to-pdf={tam}", nguon.as_uri()]
        r = subprocess.run(lenh, capture_output=True, text=True, timeout=THOI_GIAN_IN, encoding="utf-8", errors="replace")
        if not tam.exists() or tam.stat().st_size < CO_TOI_THIEU or tam.read_bytes()[:5] != b"%PDF-":
            raise RuntimeError(f"Chrome không in được PDF hợp lệ: {(r.stderr or '').strip()[:160]}")
        ra_tam = ra.with_name(ra.name + ".dang-ghi")
        ra_tam.write_bytes(tam.read_bytes())
        os.replace(ra_tam, ra)


def tim_trinh_duyet() -> str | None:
    try:
        return _nap("_docx_pdf_tim", "docx_sang_pdf_giu_mau.py").tim_trinh_duyet()
    except Exception:  # noqa: BLE001
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--kho", type=Path, default=None, help="thư mục toan_van_oa (mặc định: kho của doc_toan_van_co_nguoi)")
    ap.add_argument("--file", nargs="*", type=Path, default=[], help="chỉ PMID của các dashboard này")
    ap.add_argument("--pmid", nargs="*", default=None, help="chỉ các PMID này")
    ap.add_argument("--gioi-han", type=int, default=0, help="in tối đa N bài mỗi lượt (0 = không giới hạn)")
    ap.add_argument("--ap-dung", action="store_true", help="in thật vào kho (mặc định chạy khô)")
    a = ap.parse_args(argv)
    if a.gioi_han < 0 or (a.pmid is not None and any(not re.fullmatch(r"\d{1,9}", p) for p in a.pmid)):
        print("✗ tham số sai: --gioi-han ≥ 0, --pmid chỉ gồm số")
        return MA_THAM_SO
    kho = a.kho or dtv().KHO
    if not Path(kho).is_dir():
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy kho {kho}")
        return MA_KHONG_DO
    pmids: list[str] | None = None
    if a.file or a.pmid is not None:
        pmids = sorted({p for f in a.file for p in pmid_cua_dashboard(f)} | set(a.pmid or []), key=int)
    ds = ung_vien(Path(kho), pmids)
    if a.gioi_han:
        ds = ds[:a.gioi_han]
    loai = {}
    for _, q in ds:
        k = "PMC" if "_PMC" in q.name else ("UPW" if "_UPW" in q.name else "CHR")
        loai[k] = loai.get(k, 0) + 1
    print(f"In toàn văn kho → PDF cho EndNote: {len(ds)} bài cần in "
          f"({', '.join(f'{k} {v}' for k, v in sorted(loai.items())) or 'không có'})")
    if not a.ap_dung:
        for pm, q in ds[:15]:
            print(f"  · PMID {pm} ← {q.name}")
        print("(chạy khô — thêm --ap-dung để in)")
        return MA_OK
    if not ds:
        return MA_OK
    td = tim_trinh_duyet()
    if not td:
        print("⚪ KHÔNG ĐO ĐƯỢC — không thấy Chrome/Edge/Chromium để in PDF")
        return MA_KHONG_DO
    tot, hong = 0, []
    for pm, q in ds:
        try:
            in_pdf(html_in(pm, q), Path(kho) / f"PMID-{pm}_{HAU_TO}.pdf", td)
            tot += 1
        except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as e:
            hong.append(f"PMID {pm} ({q.name}): {str(e)[:120]}")
    print(f"✓ đã in {tot}/{len(ds)} bài vào kho dạng PMID-<n>_{HAU_TO}.pdf")
    for h in hong[:20]:
        print(f"  ⚠ {h}")
    if tot:
        print("Tiếp: python3 tools/nap_endnote_chu_de.py --gan-kho --ap-dung   (gắn vào bản ghi EndNote chưa có tệp)")
    print("Cần bác sĩ kiểm chứng.")
    return MA_LOI if hong else MA_OK


if __name__ == "__main__":
    raise SystemExit(main())
