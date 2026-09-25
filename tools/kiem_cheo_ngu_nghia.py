#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIỂM CHÉO NGỮ NGHĨA — K3: MỆNH ĐỀ ĐIỀU KIỆN CÓ CÒN NGUYÊN KHI XUẤT KHÔNG? (25/09/2026)

VÌ SAO CÓ
=========
Thiết kế ở `audit/16-thiet-ke-kiem-cheo-ngu-nghia-apply_2026-09-25.md`. Bác sĩ duyệt ngày
25/09/2026: thi công **K3 trước**, **mức CẢNH BÁO** (chỉ cân nhắc chặn sau khi đo báo động giả
trên bộ vàng), **máy soạn ứng viên bộ vàng** để bác sĩ gắn nhãn.

Các cổng hiện có kiểm nguồn có thật và hiệu số HR. Không cổng nào kiểm một lỗi rất nguy hiểm
khi rút gọn: **rụng mệnh đề điều kiện**. DATA ghi «khởi trị SGLT2i *khi đã tối ưu nền tảng*»,
bản đọc/Word chỉ còn «khởi trị SGLT2i» — câu vẫn đúng ngữ pháp, nguồn vẫn thật, nhưng khuyến
cáo đã bị nới rộng ra ngoài quần thể được chứng minh.

CÁCH LÀM (ngoại tuyến, không gọi mạng)
======================================
1. Đọc khối DATA của dashboard; lấy các cụm điều kiện («nếu…», «trừ khi…», «chỉ khi…», «khi…»,
   «ngoài thai kỳ», «chống chỉ định…», «không dùng khi/cho…») từ `summary.conclusion`,
   `summary.doNow`, `summary.dontDo` và `action` của các mục `decision:'apply'`.
2. Tìm từng cụm (đã chuẩn hoá chữ thường, khoảng trắng, gạch nối, thẻ HTML) trong từng sản
   phẩm phái sinh được đưa vào (bản đọc, Word dạng HTML, bản tin chat).

BA MỨC — cố ý KHÔNG có mức «SAI»
================================
  ✓ CÒN      — cụm điều kiện có mặt nguyên văn trong sản phẩm đó.
  🟠 CẦN ĐỌC — sản phẩm có tồn tại nhưng không thấy cụm điều kiện nguyên văn (có thể bị viết
               lại bằng lời khác — máy không hiểu diễn đạt lại, nên chỉ nhắc ĐỌC LẠI).
  ⚪ CHƯA KIỂM — không có sản phẩm để đối chiếu.
Công cụ CHỈ BÁO: không sửa dashboard, không đổi `decision`, không chặn xuất.

K1 · K4 — ĐỐI CHIẾU VỚI TÓM TẮT NGUỒN (thêm 25/09/2026, cờ --nguon, cần mạng)
=============================================================================
Với mỗi mục `decision:'apply'` có PMID: tải tiêu đề + tóm tắt (PubMed efetch theo lô; PMID còn
thiếu lùi sang Europe PMC), rồi:
  K1 quần thể — (a) cặp LOẠI TRỪ NHAU HFrEF↔HFpEF · ĐTĐ típ 1↔típ 2 · người lớn↔trẻ em · trong↔
     ngoài thai kỳ · lọc máu↔chưa lọc máu: mục mang một vế, nguồn chỉ nêu vế kia (ở tiêu đề hoặc
     ≥ 2 câu phần phương pháp) ⇒ 🟠; (b) ngưỡng số DÍNH mỏ neo (EF, eGFR, tuổi, HbA1c, BMI, LDL-C,
     NT-proBNP, HBV DNA, CrCl): mâu thuẫn HAI CHIỀU ⇒ 🟠; (c) cỡ mẫu: chỉ ✓/⚪.
  K4 chiều khuyến cáo — mục khuyến cáo LÀM mà tiêu đề/kết luận nguồn nói «did not reduce», «no
     benefit»…, hoặc một câu bất kỳ nói «not recommended/recommend against» về ĐÚNG can thiệp ⇒ 🟠.
Cùng ba mức, cùng triết lý `kiem_so_lieu.py` (BH08): chỉ đọc TÓM TẮT nên vắng mặt ≠ sai.

Dùng:
    python tools/kiem_cheo_ngu_nghia.py DASH.html --ban-doc B.html --word-html W.html [--chat T.txt]
    python tools/kiem_cheo_ngu_nghia.py DASH.html --json
    python tools/kiem_cheo_ngu_nghia.py DASH.html --nguon [--ban-doc B.html …]   # K1/K4 (+ K3 nếu có sản phẩm)
    python tools/kiem_cheo_ngu_nghia.py --toan-kho                                # K1/K4 cả kho → logs/
    python tools/kiem_cheo_ngu_nghia.py --ung-vien-bo-vang [--so-muc 20] [--lam-giau]
    python tools/kiem_cheo_ngu_nghia.py --do-bo-vang                              # sau khi bác sĩ gắn nhãn

Mã thoát: 0 = không có 🟠 · 1 = có mục/cụm cần đọc lại · 2 = không đo được (không đọc được DATA,
không có sản phẩm để đối chiếu, không tải được tóm tắt nào, bộ vàng chưa có nhãn). «Không đo
được» không bao giờ là 0.
"""
from __future__ import annotations

import argparse
import html as _html
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
TEP_BO_VANG = REPO / "quality" / "eval" / "kiem-cheo-ngu-nghia" / "bo-vang.cho-duyet.json"

# Thứ tự quan trọng: cụm dài trước để «trừ khi»/«chỉ khi»/«sau khi» không bị «khi» ăn mất.
_DAU_DIEU_KIEN = (
    "không dùng khi", "không dùng cho", "với điều kiện", "chống chỉ định", "ngoài thai kỳ",
    "trong thai kỳ", "trừ khi", "chỉ khi", "sau khi", "trước khi", "nếu", "khi",
)
_MAU_DAU = re.compile(r"(?<!\w)(" + "|".join(re.escape(d) for d in _DAU_DIEU_KIEN) + r")(?!\w)")
_NGAT = re.compile(r"[.;,()\[\]\n—–:]| - ")
_TOI_DA = 90          # ký tự tối đa của một cụm điều kiện
_TU_TOI_THIEU = 2     # cụm phải có ít nhất 2 từ SAU dấu điều kiện (tránh «khi» trơ trọi)
# Dấu tự đứng một mình vẫn là điều kiện đủ nghĩa, không cần thêm từ phía sau.
_DAU_TU_DU = {"ngoài thai kỳ", "trong thai kỳ"}


def chuan_hoa(t: str) -> str:
    """Chữ thường + NFC + bỏ thẻ HTML/entity + gộp khoảng trắng + thống nhất gạch/nháy."""
    t = re.sub(r"<[^>]+>", " ", t or "")
    t = _html.unescape(t)
    t = unicodedata.normalize("NFC", t).lower()
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = t.replace("≤", "<=").replace("≥", ">=").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def trich_cum_dieu_kien(van_ban: str) -> list[str]:
    """Các cụm điều kiện trong một câu, đã chuẩn hoá. Rỗng nếu câu không có điều kiện."""
    t = chuan_hoa(van_ban)
    cum: list[str] = []
    for m in _MAU_DAU.finditer(t):
        dau = m.group(1)
        duoi = t[m.end():m.end() + _TOI_DA]
        cat = _NGAT.search(duoi)
        if cat:
            duoi = duoi[:cat.start()]
        duoi = duoi.strip()
        if dau not in _DAU_TU_DU and len(duoi.split()) < _TU_TOI_THIEU:
            continue
        c = (dau + (" " + duoi if duoi else "")).strip()
        if c not in cum and not any(c in x for x in cum):
            cum.append(c)
    return cum


def _nap_extract_data():
    """Dùng CHÍNH bộ đọc DATA của dây chuyền bản đọc (máy thật trước, bản vendor git sau)."""
    sp = importlib.util.spec_from_file_location("_bst_kcnn", REPO / "tools" / "ban_sao_tran.py")
    bst = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(bst)
    duong = bst.duong_cong_cu_pipeline("build_ban_doc_chung_cu.py", REPO)
    if duong is None:
        return None
    sp2 = importlib.util.spec_from_file_location("_bbd_kcnn", duong)
    mod = importlib.util.module_from_spec(sp2)
    sp2.loader.exec_module(mod)
    return mod.extract_data


def doc_data(dash: Path) -> dict | None:
    ex = _nap_extract_data()
    if ex is None:
        return None
    try:
        return ex(dash.read_text(encoding="utf-8", errors="replace"))
    except (SystemExit, OSError, ValueError):
        return None


def lay_nguon_dieu_kien(data: dict) -> list[dict]:
    """[{vi_tri, van_ban, cum:[…]}] — chỉ giữ câu CÓ điều kiện."""
    ra: list[dict] = []
    sm = data.get("summary") or {}

    def them(vi_tri: str, v) -> None:
        if isinstance(v, str) and v.strip():
            cum = trich_cum_dieu_kien(v)
            if cum:
                ra.append({"vi_tri": vi_tri, "van_ban": v, "cum": cum})

    them("summary.conclusion", sm.get("conclusion"))
    for k in ("doNow", "dontDo"):
        for i, v in enumerate(sm.get(k) or []):
            them(f"summary.{k}[{i}]", v)
    for it in data.get("items") or []:
        if isinstance(it, dict) and it.get("decision") == "apply":
            them(f"{it.get('id') or '?'}.action", it.get("action"))
    return ra


def doi_chieu(nguon: list[dict], dich: dict[str, str | None]) -> dict:
    """dich: {tên sản phẩm: văn bản đã đọc | None (không có)}."""
    da_chuan = {k: (chuan_hoa(v) if v is not None else None) for k, v in dich.items()}
    dong = []
    dem = {"con": 0, "can_doc": 0, "chua_kiem": 0}
    for n in nguon:
        for c in n["cum"]:
            kq = {}
            for ten, vb in da_chuan.items():
                if vb is None:
                    kq[ten] = "chua_kiem"
                elif c in vb:
                    kq[ten] = "con"
                else:
                    kq[ten] = "can_doc"
                dem[kq[ten]] += 1
            dong.append({"vi_tri": n["vi_tri"], "cum": c, "ket_qua": kq})
    return {"dong": dong, "dem": dem, "san_pham": {k: v is not None for k, v in dich.items()}}


def _doc_tep(p: str | None) -> str | None:
    if not p:
        return None
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


_KY_HIEU = {"con": "✓", "can_doc": "🟠", "chua_kiem": "⚪"}


def in_bao_cao(dash: Path, kq: dict) -> None:
    print(f"K3 — giữ mệnh đề điều kiện · {dash.name}")
    co = [k for k, v in kq["san_pham"].items() if v]
    vang = [k for k, v in kq["san_pham"].items() if not v]
    print(f"  sản phẩm đối chiếu: {', '.join(co) or '(không có)'}"
          + (f" · không có: {', '.join(vang)}" if vang else ""))
    for d in kq["dong"]:
        dau = " ".join(f"{_KY_HIEU[v]}{k}" for k, v in d["ket_qua"].items())
        print(f"  {dau}  [{d['vi_tri']}] «{d['cum']}»")
    e = kq["dem"]
    print(f"Tổng: {e['con']} ✓ còn · {e['can_doc']} 🟠 cần đọc lại · {e['chua_kiem']} ⚪ chưa kiểm")
    if e["can_doc"]:
        print("🟠 = không thấy NGUYÊN VĂN cụm điều kiện trong sản phẩm đó. Có thể đã bị viết lại "
              "bằng lời khác — đọc lại, KHÔNG phải kết luận «sai». Công cụ chỉ cảnh báo.")


# ══════════════════════════════════════════════════════════════════════════════════════
# K1 · K4 — ĐỐI CHIẾU MỤC `apply` VỚI TIÊU ĐỀ + TÓM TẮT NGUỒN (cần mạng; 25/09/2026)
# ══════════════════════════════════════════════════════════════════════════════════════
# Bác sĩ duyệt hướng ở audit/16: «K3 trước, rồi tới K1», MỨC CẢNH BÁO. K4 dùng chung
# đường lấy tóm tắt nên làm cùng lượt. Cùng triết lý `kiem_so_lieu.py` (BH08): chỉ đọc TÓM
# TẮT (toàn văn có bản quyền) ⇒ vắng mặt KHÔNG chứng minh trích sai ⇒ không có mức «SAI».
#   ✓ khớp · 🟠 cần đọc lại (kèm câu nguyên văn của nguồn) · ⚪ nguồn không nêu/không tải được
#   · «không áp» = mục không có gì để đối chiếu (không phải «khớp»).
# Mục nào trong K1/K4 cũng CHỈ BÁO: không sửa dashboard, không đổi `decision`.
import time  # noqa: E402
import urllib.parse  # noqa: E402
import urllib.request  # noqa: E402
import http.client  # noqa: E402
import os  # noqa: E402
from xml.etree import ElementTree as ET  # noqa: E402

EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
KHO_TV = DASH / "toan_van_oa"          # kho toàn văn OA đã gom sẵn (như kiem_so_lieu.py)
_UA = "EBM-Copilot/1.0 (kiem_cheo_ngu_nghia)"
_LO_PUBMED = 150
_LO_EPMC = 40
_NGU = time.sleep                      # test thay bằng hàm rỗng


def _email() -> str:
    e = os.environ.get("NCBI_EMAIL", "")
    if e:
        return e
    sec = Path.home() / ".ebm-secrets" / "medical-ebm-automation.env"
    try:
        for d in sec.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*NCBI_EMAIL\s*=\s*(\S+)", d)
            if m:
                return m.group(1).strip("'\"")
    except OSError:
        pass
    return ""


def _tai_url(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def _sach(t: str) -> str:
    t = re.sub(r"<[^>]+>", " ", t or "")
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()


def doc_xml_pubmed(xml_text: str) -> dict[str, dict]:
    """efetch XML → {pmid: {title, phan:[(nhãn, văn bản)], nguon:'pubmed'}} (cả PubmedBookArticle)."""
    goc = ET.fromstring(xml_text)
    ra: dict[str, dict] = {}

    def them(pmid: str, tieu_de_el, abstract_els) -> None:
        pmid = (pmid or "").strip()
        if not pmid:
            return
        tieu_de = _sach("".join(tieu_de_el.itertext())) if tieu_de_el is not None else ""
        phan = [((at.get("Label") or at.get("NlmCategory") or "").strip(), _sach("".join(at.itertext())))
                for at in abstract_els]
        ra[pmid] = {"title": tieu_de, "phan": [p for p in phan if p[1]], "nguon": "pubmed"}

    for art in goc.iter("PubmedArticle"):
        a = art.find("MedlineCitation/Article")
        if a is not None:
            them(art.findtext("MedlineCitation/PMID"), a.find("ArticleTitle"), a.findall("Abstract/AbstractText"))
    for bk in goc.iter("PubmedBookArticle"):
        d = bk.find("BookDocument")
        if d is not None:
            td = d.find("ArticleTitle") if d.find("ArticleTitle") is not None else d.find("Book/BookTitle")
            them(d.findtext("PMID"), td, d.findall("Abstract/AbstractText"))
    return ra


_NHAN_IN_HOA = re.compile(r"\b(BACKGROUND|INTRODUCTION|OBJECTIVES?|AIMS?|PURPOSE|METHODS?|DESIGN|SETTING|"
                          r"PARTICIPANTS|RESULTS?|FINDINGS|CONCLUSIONS?|INTERPRETATION|IMPLICATIONS?)\s*:")


def doc_json_epmc(raw: str) -> dict[str, dict]:
    """Europe PMC (resultType=core) → cùng dạng với doc_xml_pubmed; nhãn mục lấy từ <h4> hoặc «NHÃN:»."""
    d = json.loads(raw)
    ra: dict[str, dict] = {}
    for r in (d.get("resultList") or {}).get("result") or []:
        pmid = str(r.get("pmid") or "").strip()
        if not pmid:
            continue
        ab = r.get("abstractText") or ""
        phan: list[tuple[str, str]] = []
        manh = re.split(r"<h4>(.*?)</h4>", ab, flags=re.I | re.S)
        if len(manh) > 1:
            if _sach(manh[0]):
                phan.append(("", _sach(manh[0])))
            for i in range(1, len(manh) - 1, 2):
                phan.append((_sach(manh[i]), _sach(manh[i + 1])))
        elif _sach(ab):
            t = _sach(ab)
            cat = list(_NHAN_IN_HOA.finditer(t))
            if cat:
                if t[:cat[0].start()].strip():
                    phan.append(("", t[:cat[0].start()].strip()))
                for j, m in enumerate(cat):
                    cuoi = cat[j + 1].start() if j + 1 < len(cat) else len(t)
                    phan.append((m.group(1), t[m.end():cuoi].strip()))
            else:
                phan.append(("", t))
        ra[pmid] = {"title": _sach(r.get("title") or ""), "phan": [p for p in phan if p[1]], "nguon": "europepmc"}
    return ra


def tai_tom_tat(pmids: list[str], tai=None) -> tuple[dict[str, dict], list[str]]:
    """Lấy tiêu đề + tóm tắt theo LÔ: PubMed efetch XML trước, PMID còn thiếu lùi sang Europe PMC.

    Trả (kết quả, lỗi). PMID không lấy được KHÔNG có mặt trong kết quả ⇒ nơi gọi xếp ⚪ «không tải
    được», không bao giờ thành ✓. NCBI trả trang HTML (chặn IP/misuse) ⇒ coi là lỗi của lô đó.
    """
    tai = tai or _tai_url
    ds = sorted({p for p in pmids if p and re.fullmatch(r"\d{1,9}", p)})
    ket: dict[str, dict] = {}
    loi: list[str] = []
    email = _email()
    for i in range(0, len(ds), _LO_PUBMED):
        lo = ds[i:i + _LO_PUBMED]
        url = (f"{EFETCH}?db=pubmed&retmode=xml&tool=ebm-copilot"
               + (f"&email={urllib.parse.quote(email)}" if email else "") + "&id=" + ",".join(lo))
        for lan in range(3):
            try:
                t = tai(url).decode("utf-8", "replace")
                dau = t.lstrip()[:400].lower()
                if "<html" in dau or "misuse" in dau:
                    raise ValueError("NCBI trả trang HTML (có thể đang bị chặn)")
                ket.update({k: v for k, v in doc_xml_pubmed(t).items() if k in lo})
                break
            except (OSError, ValueError, http.client.HTTPException, ET.ParseError) as e:
                if lan == 2:
                    loi.append(f"PubMed lô {i // _LO_PUBMED + 1}: {type(e).__name__}: {str(e)[:120]}")
                else:
                    _NGU(1.5 * (lan + 1))
        _NGU(0.4)
    thieu = [p for p in ds if p not in ket]
    for i in range(0, len(thieu), _LO_EPMC):
        lo = thieu[i:i + _LO_EPMC]
        q = "(" + " OR ".join(f"EXT_ID:{p}" for p in lo) + ") AND SRC:MED"
        url = f"{EPMC}?query={urllib.parse.quote(q)}&resultType=core&format=json&pageSize={len(lo) + 5}"
        try:
            ket.update({k: v for k, v in doc_json_epmc(tai(url).decode("utf-8", "replace")).items() if k in lo})
        except (OSError, ValueError, http.client.HTTPException) as e:
            loi.append(f"Europe PMC lô {i // _LO_EPMC + 1}: {type(e).__name__}: {str(e)[:120]}")
        _NGU(0.3)
    return ket, loi


def _toan_van(pmid: str) -> str | None:
    """Toàn văn OA đã gom sẵn (không gọi mạng). Không có/hỏng ⇒ None = «chưa có toàn văn»."""
    for f in KHO_TV.glob(f"PMID-{pmid}_*.xml"):
        try:
            return re.sub(r"\s+", " ", " ".join(ET.fromstring(f.read_bytes()).itertext())) or None
        except (OSError, ET.ParseError):
            return None
    return None


# ── Chuẩn hoá số: tiếng Việt «200.000» / «2,5» ↔ tiếng Anh «200,000» / «2.5» ──────────
_MAU_SO = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)*)(?!\w)")
_DON_VI_BO = re.compile(r"(?:/|per)\s*1[.,]73\s*(?:m2|m²|m\^2|square met(?:er|re)s?)|\bmm\s?hg\b")


def _chuan_so(t: str) -> str:
    t = re.sub(r"(?<=\d)·(?=\d)", ".", t)
    t = t.replace("–", "-").replace("—", "-").replace("−", "-")
    t = re.sub(r"\b(\d{1,3})((?: \d{3})+)\b", lambda m: m.group(1) + m.group(2).replace(" ", ""), t)
    return _DON_VI_BO.sub(" ", t)


def _so(s: str, ngon_ngu: str) -> float | None:
    try:
        if ngon_ngu == "vi":
            if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
                return float(s.replace(".", ""))
            return float(s.replace(".", "").replace(",", ".")) if "," in s else float(s)
        if re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", s):
            return float(s.replace(",", ""))
        return float(s.replace(",", "."))
    except ValueError:
        return None


def _bang(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-6 * max(1.0, abs(a))


# ── K1a · Cặp quần thể LOẠI TRỪ NHAU (audit/16 §2) ─────────────────────────────────────
# (tên, nhãn vế A, nhãn vế B, VN-A, VN-B, EN-A, EN-B, VN-che, EN-che)
# «che» = cụm bị XOÁ trước khi dò vế A (dạng phủ định/dạng thứ ba), để «ngoài thai kỳ» không bị
# đọc thành «thai kỳ», «non-dialysis» không thành «dialysis», «mildly reduced EF» không thành HFrEF.
_CAP_LOAI_TRU = (
    ("suy tim EF giảm ↔ EF bảo tồn", "HFrEF", "HFpEF",
     (r"\bhfref\b", r"phân suất tống máu giảm", r"(?:\blvef\b|\bef\b)\s*(?:<=|<)\s*(?:35|40)\b"),
     (r"\bhfpef\b", r"phân suất tống máu bảo tồn", r"(?:\blvef\b|\bef\b)\s*(?:>=|>)\s*(?:40|45|50)\b"),
     (r"\bhfref\b", r"reduced (?:left[- ]ventricular )?ejection fraction",
      r"ejection fraction (?:\(l?v?ef\) )?(?:of )?(?:<=|<|less than )\s*(?:35|40)\b",
      r"ejection fraction (?:\(l?v?ef\) )?(?:of )?(?:35|40) ?% or (?:less|lower)"),
     (r"\bhfpef\b", r"preserved (?:left[- ]ventricular )?ejection fraction",
      r"ejection fraction (?:\(l?v?ef\) )?(?:of )?(?:>=|>|more than |greater than |at least )\s*(?:40|45|50)\b",
      r"ejection fraction (?:\(l?v?ef\) )?(?:of )?(?:40|45|50) ?% or (?:more|higher|greater|above)"),
     (r"phân suất tống máu giảm nhẹ", r"\bhfmref\b"),
     (r"mildly reduced (?:left[- ]ventricular )?ejection fraction", r"\bhfmref\b")),
    ("ĐTĐ típ 1 ↔ típ 2", "típ 1", "típ 2",
     (r"(?:đái tháo đường|đtđ|tiểu đường)\s*(?:típ|týp|type|loại)\s*1\b", r"\bt1dm?\b"),
     (r"(?:đái tháo đường|đtđ|tiểu đường)\s*(?:típ|týp|type|loại)\s*2\b", r"\bt2dm?\b"),
     (r"\btype 1 diabet", r"\bt1dm?\b", r"\binsulin-dependent diabet"),
     (r"\btype 2 diabet", r"\bt2dm?\b", r"\bnon-insulin-dependent diabet"),
     (), (r"\bnon-insulin-dependent diabet",)),
    ("người lớn ↔ trẻ em", "người lớn", "trẻ em",
     (r"người lớn", r"người trưởng thành"),
     (r"trẻ em", r"trẻ sơ sinh", r"trẻ nhỏ", r"bệnh nhi", r"\bnhi khoa\b", r"vị thành niên", r"thiếu niên"),
     (r"\badults?\b",),
     (r"\bchild(?:ren|hood)?\b", r"\bpa?ediatric", r"\binfants?\b", r"\bneonat", r"\bnewborns?\b", r"\badolescen"),
     (), ()),
    ("trong ↔ ngoài thai kỳ", "trong thai kỳ", "ngoài thai kỳ",
     (r"thai phụ", r"sản phụ", r"mang thai", r"có thai", r"thai kỳ"),
     (r"ngoài thai kỳ", r"không (?:mang|có) thai"),
     (r"pregnan", r"\bantenatal\b", r"\bprenatal\b", r"\bgestation"),
     (r"\bnon-?pregnant\b", r"\bnot pregnant\b"),
     (r"ngoài thai kỳ", r"không (?:mang|có) thai"),
     (r"\bnon-?pregnant\b", r"\bnot pregnant\b")),
    ("CKD lọc máu ↔ chưa lọc máu", "lọc máu", "chưa lọc máu",
     (r"lọc máu", r"thận nhân tạo", r"thẩm phân", r"lọc màng bụng"),
     (r"(?:chưa|không)(?: cần| phải| phụ thuộc)? lọc máu",),
     (r"dialysis", r"(?:kidney|renal) replacement therapy"),
     (r"\bnon-?dialysis", r"\bnot (?:on|requiring|receiving|yet on) (?:maintenance )?dialysis"),
     (r"(?:chưa|không)(?: cần| phải| phụ thuộc)? lọc máu",),
     (r"\bnon-?dialysis(?:-dependent)?", r"\bnot (?:on|requiring|receiving|yet on) (?:maintenance )?dialysis")),
)
# Câu nêu tiêu chuẩn LOẠI TRỪ không nói quần thể nghiên cứu là ai ⇒ bỏ khi dò vế trong nguồn.
_CAU_LOAI_TRU = re.compile(r"\bexclu\w*|\bineligible\b|\bnot eligible\b")
# Mục tóm tắt thuộc phần KẾT QUẢ/KẾT LUẬN — số ở đó thường là thay đổi/phân nhóm, không phải
# tiêu chuẩn chọn; chỉ dùng để XÁC NHẬN (✓), không dùng để tạo mâu thuẫn (🟠).
_NHAN_KET_QUA = re.compile(r"result|finding|conclusion|interpretation|implication|discussion", re.I)


def _co_ve(t: str, mau: tuple, che: tuple) -> bool:
    if che:
        t = re.sub("|".join(che), " ", t)
    return any(re.search(p, t) for p in mau)


def _cau_en(t: str) -> list[str]:
    return [c for c in re.split(r"(?<=[.!?])\s+", t) if c.strip()]


def _van_ban_nguon(nguon: dict) -> tuple[str, list[str], list[str]]:
    """(tiêu đề, câu phần PHƯƠNG PHÁP/đối tượng, mọi câu) — đã chuẩn hoá. Tóm tắt không cấu trúc
    ⇒ mọi câu đều tính là phần phương pháp (không tách được)."""
    tieu_de = chuan_hoa(nguon.get("title") or "")
    phan = nguon.get("phan") or []
    co_cau_truc = any(nhan for nhan, _ in phan)
    pp: list[str] = []
    tat_ca: list[str] = []
    for nhan, vb in phan:
        cau = _cau_en(chuan_hoa(vb))
        tat_ca += cau
        if not (co_cau_truc and _NHAN_KET_QUA.search(nhan or "")):
            pp += cau
    return tieu_de, pp, tat_ca


def k1_cap(vn: str, nguon: dict) -> list[dict]:
    """Mỗi cặp mà mục mang ĐÚNG MỘT vế:
      ✓ nguồn nêu cùng vế (tiêu đề hoặc bất kỳ câu nào);
      🟠 nguồn không nêu vế của mục mà nêu vế kia ở TIÊU ĐỀ hoặc ở ≥ 2 câu phần phương pháp;
      ⚪ nguồn không nêu, hoặc chỉ nhắc vế kia thoáng qua (1 câu) — guideline hay nhắc nhóm đặc biệt."""
    tieu_de, pp, tat_ca = _van_ban_nguon(nguon)
    loc = [c for c in tat_ca if not _CAU_LOAI_TRU.search(c)]
    loc_pp = [c for c in pp if not _CAU_LOAI_TRU.search(c)]
    ra = []
    for ten, na, nb, vi_a, vi_b, en_a, en_b, che_vi, che_en in _CAP_LOAI_TRU:
        m_a, m_b = _co_ve(vn, vi_a, che_vi), _co_ve(vn, vi_b, ())
        if m_a == m_b:
            continue                      # mục không nêu, hoặc nêu cả hai vế ⇒ không có gì để đối
        muc_ve, ve_kia = (na, nb) if m_a else (nb, na)
        cung = (en_a, che_en) if m_a else (en_b, ())
        kia = (en_b, ()) if m_a else (en_a, che_en)
        if _co_ve(tieu_de, *cung) or any(_co_ve(c, *cung) for c in loc):
            muc, ghi = "con", f"{ten}: mục «{muc_ve}», nguồn cũng nêu «{muc_ve}»"
        elif _co_ve(tieu_de, *kia) or sum(_co_ve(c, *kia) for c in loc_pp) >= 2:
            muc, ghi = "can_doc", f"{ten}: mục ghi «{muc_ve}» nhưng tóm tắt nguồn chỉ nêu «{ve_kia}»"
        elif any(_co_ve(c, *kia) for c in loc):
            muc, ghi = "chua_kiem", f"{ten}: mục ghi «{muc_ve}»; tóm tắt chỉ nhắc «{ve_kia}» thoáng qua"
        else:
            muc, ghi = "chua_kiem", f"{ten}: mục ghi «{muc_ve}», tóm tắt không nêu vế nào"
        ra.append({"loai": "cap", "muc": muc, "ghi_chu": ghi})
    return ra


# ── K1b · Ngưỡng số của quần thể (EF, eGFR, tuổi, HbA1c…) ───────────────────────────────
# Số phải DÍNH vào mỏ neo («EF ≤ 40%», «≥ 65 tuổi», «aged 65 years or older»). Bản đầu vét mọi số
# trong cửa sổ 45 ký tự ⇒ 9/18 cảnh báo 🟠 đo trên toàn kho 25/09 là cỡ mẫu/ĐLC/thời gian bị bắt
# nhầm. «Trung bình/trung vị» là số MÔ TẢ, tách khỏi NGƯỠNG và chỉ so cùng loại.
# (tên, mỏ neo VN, mỏ neo EN, được đọc số đứng TRƯỚC mỏ neo?)
_BIEN_SO = (
    ("EF", r"\blvef\b|\bef\b|phân suất tống máu", r"\blvef\b|\bef\b|ejection fraction", False),
    ("eGFR", r"\begfr\b|mức lọc cầu thận|\bmlct\b", r"\begfr\b|glomerular filtration rate|\bgfr\b", False),
    ("HbA1c", r"\bhba1c\b|\ba1c\b", r"\bhba1c\b|\ba1c\b|glyc(?:at|osyl)ed ha?emoglobin", False),
    ("BMI", r"\bbmi\b|chỉ số khối cơ thể", r"\bbmi\b|body[- ]mass index", False),
    ("LDL-C", r"\bldl(?:-c)?\b", r"\bldl(?:-c)?\b|low-density lipoprotein(?: cholesterol)?", False),
    ("NT-proBNP", r"nt-?probnp", r"nt-?probnp", False),
    ("HBV DNA", r"hbv[- ]?dna", r"hbv[- ]?dna", False),
    ("CrCl", r"\bcrcl\b|độ thanh thải creatinin", r"\bcrcl\b|creatinine clearance", False),
    ("tuổi", r"tuổi", r"\baged?\b|\bages\b|years? of age|years? old|or older|\bolder than\b", True),
)
_SO_G = r"(\d[\d.,]*\d|\d)"
_DON_VI = (r"(?:\s*(?:%|ml/min(?:ute)?|ml/phút|mmol/mol|mmol/l|mg/dl|mg/g|pg/ml|ng/l|iu/ml|kg/m2|kg/m²"
           r"|years?|yrs?|năm))?")
_TIEN_TO = (r"(?:\s|:|=|~|≈|<=|>=|<|>|\([a-z0-9-]{1,8}\)|của|là|từ|trên|dưới|khoảng|trung bình|trung vị"
            r"|tối thiểu|tối đa|ít nhất|lớn hơn|nhỏ hơn|không quá|mức|nồng độ|of|was|were|is|are|from|between"
            r"|over|under|above|below|at least|at most|less than|more than|greater than|lower than|higher than"
            r"|up to|mean|median|about|approximately|levels?|values?|concentrations?|an?)*")
_SAU_NEO = re.compile(r"^" + _TIEN_TO + _SO_G + _DON_VI
                      + r"(?:\s*(?:-|to|đến|tới|and|và)\s*(?:<=|>=|<|>|less than |more than )?" + _SO_G + r")?")
_TRUOC_NEO = re.compile(r"(?:" + _SO_G + r"\s*(?:-|to|đến|tới)\s*)?" + _SO_G + r"\s*(?:years?|yrs?)?\s*\+?\s*$")
_MO_TA = re.compile(r"mean|median|average|trung bình|trung vị")


def _so_dinh_neo(t: str, m: re.Match, truoc: bool, ngon: str) -> tuple[str, list[float]]:
    """(loại, các số) DÍNH vào mỏ neo m; loại = 'mo_ta' (trung bình/trung vị) | 'nguong'."""
    so: list[str] = []
    sau = _SAU_NEO.match(t[m.end():m.end() + 70])
    if sau:
        so += [g for g in sau.groups() if g]
    if truoc:
        tr = _TRUOC_NEO.search(t[max(0, m.start() - 25):m.start()])
        if tr:
            so = [g for g in tr.groups() if g] + so
    vung = t[max(0, m.start() - 15):m.start()] + (sau.group(0) if sau else "")
    loai = "mo_ta" if _MO_TA.search(vung) else "nguong"
    return loai, [x for x in (_so(s_, ngon) for s_ in so) if x is not None]


def _so_theo_bien(t: str, ngon: str) -> dict[tuple[str, str], list[float]]:
    """{(biến, loại): [số…]} — chỉ số dính mỏ neo."""
    t = _chuan_so(t)
    ra: dict[tuple[str, str], list[float]] = {}
    for ten, vi, en, truoc in _BIEN_SO:
        for m in re.finditer(vi if ngon == "vi" else en, t):
            loai, xs = _so_dinh_neo(t, m, truoc, ngon)
            for x in xs:
                ds = ra.setdefault((ten, loai), [])
                if not any(_bang(x, y) for y in ds):
                    ds.append(x)
    return {k: v for k, v in ra.items() if v}


def _fmt(xs) -> str:
    return ", ".join(f"{x:g}" for x in sorted(xs))


def _thuoc(x: float, ys) -> bool:
    return any(_bang(x, y) for y in ys)


def k1_nguong(vn: str, nguon: dict, toan_van: str | None) -> list[dict]:
    """Theo từng (biến, loại) mục có số:
      ✓ mọi số của mục có trong tóm tắt (bất kỳ phần nào) — hoặc trong TOÀN VĂN OA đã gom;
      🟠 MÂU THUẪN hai chiều: mục có số tóm tắt không có, VÀ phần phương pháp của tóm tắt có số
         mục không có (vd mục «eGFR ≥ 20», nguồn «eGFR 25–75»);
      ⚪ tóm tắt không nêu biến, hoặc chỉ nêu một phần số của mục mà không nêu số nào khác."""
    muc_so = _so_theo_bien(vn, "vi")
    if not muc_so:
        return []
    tieu_de, pp, tat_ca = _van_ban_nguon(nguon)
    so_tat_ca = _so_theo_bien(" ".join([tieu_de] + tat_ca), "en")
    so_pp = _so_theo_bien(" ".join([tieu_de] + pp), "en")
    so_tv = _so_theo_bien(chuan_hoa(toan_van), "en") if toan_van else {}
    ra = []
    for (bien, loai), xs in muc_so.items():
        nhan = bien + (" (trung bình/trung vị)" if loai == "mo_ta" else "")
        ys, ys_pp, ys_tv = so_tat_ca.get((bien, loai), []), so_pp.get((bien, loai), []), so_tv.get((bien, loai), [])
        thieu = [x for x in xs if not _thuoc(x, ys)]
        la = [y for y in ys_pp if not _thuoc(y, xs)]
        if not thieu:
            ra.append({"loai": "nguong", "muc": "con", "ghi_chu": f"{nhan} {_fmt(xs)} có trong tóm tắt"})
        elif la:
            ra.append({"loai": "nguong", "muc": "can_doc",
                       "ghi_chu": f"{nhan}: mục ghi {_fmt(xs)} nhưng tóm tắt nêu {_fmt(ys_pp)}"})
        elif ys_tv and all(_thuoc(x, ys_tv) for x in thieu):
            # số tóm tắt chưa xác nhận phải có trong toàn văn; toàn văn KHÔNG bao giờ tạo 🟠
            ra.append({"loai": "nguong", "muc": "con",
                       "ghi_chu": f"{nhan} {_fmt(xs)} có trong tóm tắt + TOÀN VĂN OA ({_fmt(thieu)})"})
        else:
            ra.append({"loai": "nguong", "muc": "chua_kiem",
                       "ghi_chu": f"{nhan} {_fmt(thieu)}: tóm tắt không nêu" + (f" (chỉ nêu {_fmt(ys)})" if ys else "")})
    return ra


# ── K2 rút gọn · cỡ mẫu (chỉ ✓/⚪: tóm tắt hay nêu nhiều con số, vắng ≠ sai) ──────────────
_CO_MAU_VN = (
    re.compile(r"\bn\s*=\s*(\d[\d.,]*\d|\d)"),
    re.compile(r"(\d[\d.,]*\d|\d)\s*(?:bệnh nhân|người bệnh|người tham gia|người|trẻ|phụ nữ|thai phụ|ca bệnh|ca)\b"),
    re.compile(r"(\d[\d.,]*\d|\d)\s*(?:nghiên cứu|thử nghiệm|rct)\b"),
)


def k2_co_mau(vn: str, en: str) -> list[dict]:
    so_muc = []
    t = _chuan_so(vn)
    for mau in _CO_MAU_VN:
        for m in mau.finditer(t):
            x = _so(m.group(1), "vi")
            if x is not None and x >= 10 and not any(_bang(x, y) for y in so_muc):
                so_muc.append(x)
    if not so_muc:
        return []
    so_nguon = [y for y in (_so(s, "en") for s in _MAU_SO.findall(_chuan_so(en))) if y is not None]
    ra = []
    for x in so_muc:
        thay = any(_bang(x, y) for y in so_nguon)
        ra.append({"loai": "co_mau", "muc": "con" if thay else "chua_kiem",
                   "ghi_chu": f"cỡ mẫu {x:g} " + ("có trong tóm tắt" if thay else "— tóm tắt không nêu con số này")})
    return ra


# ── K4 · Chiều khuyến cáo ─────────────────────────────────────────────────────────────
# Chỉ xét mục khuyến cáo LÀM. Mục «làm ÍT đi» (không dùng/ngừng/giảm liều/dừng sau N ngày…) nhận tín hiệu phủ định của nguồn
# là CÙNG chiều ⇒ «không áp». Chỉ xét CÂU ĐẦU của action (câu sau hay là lưu ý phụ như «đổi thuốc
# phải NGƯNG ACEi 36 giờ» — không đổi chiều khuyến cáo chính).
_MUC_LAM_IT = re.compile(
    r"^\W*(?:không|tránh|ngừng|ngưng|dừng|bỏ|hạn chế|chống chỉ định|thận trọng|cảnh giác)\b"
    r"|\b(?:không (?:dùng|kê|nên|khuyến cáo|cần|phối hợp|khởi trị|bắt đầu|được)|tránh (?:dùng|kê|phối hợp)"
    r"|ngừng|ngưng|dừng|giảm liều|giảm dần|giảm thuốc|cai|hạn chế dùng|chống chỉ định|bỏ thuốc)\b")
_NEG_KHUYEN_CAO = re.compile(
    r"\bnot (?:be )?recommended\b|\brecommend(?:s|ed|ation)? against\b|\bshould not be (?:routinely )?"
    r"(?:used|given|offered|prescribed|initiated|administered|considered)\b|\bis not indicated\b"
    r"|\bclass iii\b[^.;]{0,20}\b(?:harm|no benefit)\b")
_NEG_HIEU_QUA = re.compile(
    r"\b(?:did|does|do) not (?:significantly )?(?:reduce|improve|lower|decrease|prevent|prolong)\b"
    r"|\bno (?:statistically )?(?:significant |clinically (?:meaningful|important|relevant) |clear |additional "
    r"|overall )?(?:benefit|reduction|improvement)\b"
    r"|\b(?:was|were|is|are) not (?:superior|more effective|associated with (?:a )?(?:lower|reduced|improved|better))\b"
    r"|\bnot associated with (?:a )?(?:lower|reduced|improved|better|decreased)\b"
    r"|\bfailed to (?:reduce|improve|show|demonstrate|prevent)\b"
    r"|\bno evidence (?:of (?:a )?benefit|of efficacy|that|to support)\b")
_NEG_KHAC_BIET = re.compile(r"\bno (?:statistically )?significant difference\b")
_KHAC_BIET_AN_TOAN = re.compile(r"safety|adverse|harm|tolerab|side effect|non-?inferior|equivalen")
_KHONG_NEO = set("""ci hr rr or arr rrr nnt nnh rct rcts iu ml mg kg ef lvef egfr gfr hba1c a1c bmi ldl hdl
nyha esc aha acc ada easd kdigo gold gina nice who uspstf aasld easl idsa ats acr eular grade itt dna rna hbv hcv
hiv copd ckd hfref hfpef hfmref icu iv po mmol mmhg nt probnp kpa alt ast fev1 fvc hcc aki dka vte dvt acs cad pad
sle gerd ibs vs guideline guidelines consensus review systematic placebo control standard therapy treatment
patients meta analysis cohort trial trials class level strong weak recommendation recommendations update
statement practice clinical evidence expert panel task force group study studies network data outcome outcomes
risk primary secondary prevention screening management diagnosis care the and for with without plus versus dose
doses high low dual single first line early late long short term type ii iii iv sd iqr""".split())
# Chữ tiếng Việt viết HOA không dấu («KHUNG», «THAI», «VIEM») lọt qua bộ lọc ASCII — loại theo cấu
# trúc âm tiết; vài viết tắt y khoa trùng dạng âm tiết thì giữ đích danh.
_AM_TIET_VIET = re.compile(r"^(?:ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|[bcdghklmnprstvx])?[aeiouy]{1,3}"
                           r"(?:ch|ng|nh|[cmnpt])?$")
_NEO_GIU = {"doac", "noac", "mao"}


def neo_can_thiep(it: dict) -> list[str]:
    """Từ Latin (tên thuốc/viết tắt can thiệp) trong pico.I + title — mỏ neo để biết câu nào của
    nguồn nói về ĐÚNG can thiệp của mục. Từ tiếng Việt có dấu tự rơi ra vì không phải ASCII."""
    pico = it.get("pico") if isinstance(it.get("pico"), dict) else {}
    i = pico.get("I")
    nguon = " ".join([i[0] if isinstance(i, list) and i else (i if isinstance(i, str) else ""),
                      it.get("title") or ""])
    ra: list[str] = []
    for tok in re.split(r"[\s,;:()\[\]/+·—–\-.]+", nguon):
        if not tok.isascii() or not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", tok):
            continue
        if not (any(c.isupper() for c in tok[1:]) or any(c.isdigit() for c in tok) or len(tok) >= 6):
            continue
        n = tok.lower()
        if re.fullmatch(r"[a-z]+\d*i", n) and tok[-1] == "i" and tok[:-1].upper() == tok[:-1]:
            n = n[:-1]                    # SGLT2i → sglt2, DPP4i → dpp4, ACEi → ace
        if n not in _NEO_GIU and _AM_TIET_VIET.match(n):
            continue
        if len(n) >= 3 and n not in _KHONG_NEO and n not in ra:
            ra.append(n)
    return ra


def _co_neo(cau: str, neo: list[str]) -> bool:
    return any(re.search(r"\b" + re.escape(n) + (r"\b" if len(n) < 5 else ""), cau) for n in neo)


def k4_chieu(it: dict, nguon: dict | None) -> dict:
    """✓ không thấy tín hiệu ngược chiều · 🟠 có (kèm câu nguyên văn) · ⚪ không tải/không có tóm tắt.
    Phạm vi: câu HIỆU QUẢ phủ định («did not reduce», «no benefit»…) chỉ xét ở tiêu đề + mục KẾT LUẬN
    (không cấu trúc: 2 câu cuối); câu KHUYẾN CÁO phủ định («not recommended», «recommend against»…)
    xét ở mọi câu nhưng PHẢI nhắc đúng can thiệp của mục (mỏ neo) — tóm tắt guideline nêu nhiều
    khuyến cáo cho can thiệp khác."""
    action = chuan_hoa(it.get("action") or "")
    if _MUC_LAM_IT.search(re.split(r"(?<=[.;!?])\s+", action, maxsplit=1)[0]):
        return {"muc": "khong_ap", "ghi_chu": "mục là khuyến cáo KHÔNG làm/làm ít đi — K4 chỉ xét khuyến cáo làm"}
    if not nguon:
        return {"muc": "chua_kiem", "ghi_chu": "không tải được tiêu đề/tóm tắt nguồn"}
    neo = neo_can_thiep(it)
    cau: list[tuple[str, bool]] = [(chuan_hoa(nguon.get("title") or ""), True)]
    phan = nguon.get("phan") or []
    co_cau_truc = any(p[0] for p in phan)
    for nhan, vb in phan:
        ket_luan = bool(re.search(r"conclusion|interpretation|implication", nhan, re.I))
        for c in _cau_en(chuan_hoa(vb)):
            cau.append((c, ket_luan))
    if phan and not co_cau_truc:            # không cấu trúc ⇒ 2 câu cuối coi như kết luận
        cau = cau[:1] + [(c, k or j >= len(cau) - 2) for j, (c, k) in enumerate(cau[1:], 1)]
    for c, trong_pham_vi in cau:
        if not c:
            continue
        hieu_qua = _NEG_HIEU_QUA.search(c) or (_NEG_KHAC_BIET.search(c) and not _KHAC_BIET_AN_TOAN.search(c))
        khuyen_cao = _NEG_KHUYEN_CAO.search(c)
        if (trong_pham_vi and hieu_qua) or (khuyen_cao and neo and _co_neo(c, neo)):
            return {"muc": "can_doc", "ghi_chu": "nguồn có tín hiệu NGƯỢC CHIỀU với khuyến cáo làm",
                    "cau_nguon": c[:320]}
    if not phan:
        return {"muc": "chua_kiem", "ghi_chu": "nguồn không có tóm tắt — mới soát tiêu đề"}
    return {"muc": "con", "ghi_chu": "không thấy tín hiệu ngược chiều trong tiêu đề/kết luận"}


# ── Gộp theo mục ──────────────────────────────────────────────────────────────────────
def _pico_p(it: dict) -> str:
    pico = it.get("pico") if isinstance(it.get("pico"), dict) else {}
    p = pico.get("P")
    return p[0] if isinstance(p, list) and p and isinstance(p[0], str) else (p if isinstance(p, str) else "")


def pmid_cua(it: dict) -> str | None:
    m = re.search(r"\d{5,9}", str(it.get("pmid") or ""))
    return m.group(0) if m else None


def kiem_muc_nguon(it: dict, nguon: dict | None, toan_van: str | None = None) -> dict:
    """K1 (+ cỡ mẫu) và K4 cho MỘT mục `apply`. Mức gộp K1: 🟠 nếu có 🟠 · ✓ nếu có ✓ · ⚪ · không áp."""
    vn = chuan_hoa(" . ".join(x for x in (it.get("population") or "", _pico_p(it)) if x))
    if nguon:
        en = chuan_hoa(" ".join([nguon.get("title") or ""] + [vb for _, vb in nguon.get("phan") or []]))
        chi_tiet = k1_cap(vn, nguon) + k1_nguong(vn, nguon, toan_van) + k2_co_mau(vn, en)
    else:
        chi_tiet = []
    if not nguon:
        k1 = "chua_kiem"
    elif any(c["muc"] == "can_doc" for c in chi_tiet):
        k1 = "can_doc"
    elif any(c["muc"] == "con" for c in chi_tiet):
        k1 = "con"
    elif chi_tiet:
        k1 = "chua_kiem"
    else:
        k1 = "khong_ap"
    return {"k1": {"muc": k1, "chi_tiet": chi_tiet}, "k4": k4_chieu(it, nguon),
            "nguon_tom_tat": (nguon or {}).get("nguon")}


def kiem_nguon_dashboard(dash_ds: list[Path], tai=None) -> dict:
    """Chạy K1/K4 cho mọi mục `apply` có PMID của các dashboard. Một lượt tải theo lô cho cả kho."""
    muc: list[tuple[str, dict]] = []
    khong_doc = []
    for f in dash_ds:
        data = doc_data(f)
        if data is None:
            khong_doc.append(f.name)
            continue
        for it in data.get("items") or []:
            if isinstance(it, dict) and it.get("decision") == "apply":
                muc.append((f.name, it))
    pmids = [p for p in (pmid_cua(it) for _, it in muc) if p]
    tom_tat, loi = tai_tom_tat(pmids, tai=tai) if pmids else ({}, [])
    dong = []
    for fn, it in muc:
        pm = pmid_cua(it)
        if not pm:
            kq = {"k1": {"muc": "chua_kiem", "chi_tiet": []},
                  "k4": {"muc": "chua_kiem", "ghi_chu": "mục không có PMID (DOI/URL chưa đối chiếu được)"},
                  "nguon_tom_tat": None}
        else:
            kq = kiem_muc_nguon(it, tom_tat.get(pm), _toan_van(pm) if pm in tom_tat else None)
        dong.append({"dashboard": fn, "id": it.get("id"), "pmid": pm, "title": it.get("title"), **kq})
    dem = {k: {m: sum(1 for d in dong if d[k]["muc"] == m) for m in ("con", "can_doc", "chua_kiem", "khong_ap")}
           for k in ("k1", "k4")}
    return {"dong": dong, "dem": dem, "loi_tai": loi, "khong_doc_duoc": khong_doc,
            "so_muc_apply": len(muc), "so_pmid": len(set(pmids)), "tai_duoc": len(tom_tat)}


_KY = {"con": "✓", "can_doc": "🟠", "chua_kiem": "⚪", "khong_ap": "·"}


def in_bao_cao_nguon(kq: dict, chi_tiet: bool = True) -> None:
    print(f"K1/K4 — đối chiếu mục apply với tiêu đề + tóm tắt nguồn · {kq['so_muc_apply']} mục · "
          f"{kq['so_pmid']} PMID · tải được {kq['tai_duoc']}")
    for loi in kq["loi_tai"]:
        print(f"  ⚠ {loi}")
    if chi_tiet:
        for d in kq["dong"]:
            dong_in = []
            for c in d["k1"]["chi_tiet"]:
                if c["muc"] == "can_doc":
                    dong_in.append(f"    🟠 K1 {c['ghi_chu']}")
            if d["k4"]["muc"] == "can_doc":
                dong_in.append(f"    🟠 K4 {d['k4']['ghi_chu']}: «{d['k4'].get('cau_nguon', '')}»")
            if dong_in:
                print(f"  [{d['dashboard'].replace('WebDashboard_EBM_', '')[:60]} · {d['id']} · PMID {d['pmid']}]")
                for x in dong_in:
                    print(x)
    for k, ten in (("k1", "K1 quần thể"), ("k4", "K4 chiều khuyến cáo")):
        e = kq["dem"][k]
        print(f"Tổng {ten}: {e['con']} ✓ · {e['can_doc']} 🟠 cần đọc lại · {e['chua_kiem']} ⚪ chưa kiểm/không nêu"
              f" · {e['khong_ap']} không áp")
    if kq["dem"]["k1"]["can_doc"] or kq["dem"]["k4"]["can_doc"]:
        print("🟠 = tóm tắt nguồn nêu điều KHÁC mục (quần thể/ngưỡng khác, hoặc tín hiệu ngược chiều) — đọc lại "
              "nguồn gốc; KHÔNG phải kết luận «sai» (tóm tắt không nói hết bài). Công cụ chỉ cảnh báo.")


# ── Ứng viên bộ vàng (bác sĩ gắn nhãn; máy KHÔNG gắn) ─────────────────────────────
_NHAN_TRONG = {"dung_quan_the": None, "dung_chieu": None, "du_dieu_kien": None, "ghi_chu": None}


def _ung_vien_tu_muc(ten_dash: str, it: dict) -> dict:
    return {
        "dashboard": ten_dash, "id": it.get("id"), "title": it.get("title"),
        "population": it.get("population"), "pico": it.get("pico") if isinstance(it.get("pico"), dict) else None,
        "action": it.get("action"), "pmid": it.get("pmid"), "doi": it.get("doi"),
        "gradeLevel": it.get("gradeLevel"),
        "co_dieu_kien": bool(trich_cum_dieu_kien(it.get("action") or "")),
        "nhan_bac_si": dict(_NHAN_TRONG),
    }


def _vong_tron(theo_dash: list[list[dict]], so_muc: int, ra: list[dict]) -> list[dict]:
    theo_dash = [list(n) for n in theo_dash if n]
    while len(ra) < so_muc and theo_dash:
        for nhom in theo_dash:
            if len(ra) >= so_muc:
                break
            ra.append(nhom.pop(0))
        theo_dash = [n for n in theo_dash if n]
    return ra


def soan_ung_vien(dashboards: list[Path], so_muc: int, uu_tien: set | None = None) -> list[dict]:
    """Rút mục apply theo vòng tròn giữa các dashboard để bộ vàng đa dạng chủ đề.

    `uu_tien` = tập (tên dashboard, id) được K1/K4 báo 🟠: khi có, tối đa MỘT NỬA bộ vàng lấy từ
    đó (đo được độ chính xác của cảnh báo), phần còn lại vòng tròn như cũ (đo báo động giả và bỏ
    lọt). Tệp ghi ra cố ý KHÔNG đánh dấu mục nào được chọn vì cảnh báo — nhãn phải gắn mù."""
    uu, thuong = [], []
    for f in dashboards:
        data = doc_data(f)
        if not data:
            continue
        a, b = [], []
        for it in data.get("items") or []:
            if isinstance(it, dict) and it.get("decision") == "apply" and (it.get("pmid") or it.get("doi")):
                (a if uu_tien and (f.name, it.get("id")) in uu_tien else b).append(_ung_vien_tu_muc(f.name, it))
        uu.append(a)
        thuong.append(b)
    ra: list[dict] = []
    if uu_tien:
        _vong_tron(uu, so_muc // 2, ra)
    return _vong_tron(thuong, so_muc, ra)


def _da_co_nhan(p: Path) -> bool:
    try:
        cu = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return any(v is not None for m in cu.get("muc") or [] for v in (m.get("nhan_bac_si") or {}).values())


def ghi_ung_vien(ung_vien: list[dict], dich: Path, ghi_de: bool, lam_giau: bool = False) -> str:
    if dich.exists() and _da_co_nhan(dich):
        return f"✗ KHÔNG ghi: {dich} đã có nhãn của bác sĩ — không bao giờ ghi đè nhãn đã gắn."
    if dich.exists() and not ghi_de:
        return f"✗ KHÔNG ghi: {dich} đã tồn tại (thêm --ghi-de nếu muốn soạn lại, nhãn đang trống)."
    dich.parent.mkdir(parents=True, exist_ok=True)
    noi_dung = {
        "_mo_ta": "Ứng viên bộ vàng cho kiểm chéo ngữ nghĩa (audit/16). MÁY SOẠN, BÁC SĨ GẮN NHÃN: "
                  "điền nhan_bac_si.dung_quan_the / dung_chieu / du_dieu_kien = true|false cho từng mục. "
                  "Máy không tự gắn nhãn; khi nhãn còn null, mọi con số báo động giả là CHƯA ĐO.",
        "so_muc": len(ung_vien), "muc": ung_vien,
    }
    if lam_giau:
        noi_dung["cach_chon"] = ("làm giàu: tối đa một nửa số mục được chọn trong nhóm K1/K4 báo 🟠 (để đo độ chính "
                                 "xác của cảnh báo), phần còn lại chọn vòng tròn giữa các dashboard. Tệp cố ý KHÔNG "
                                 "ghi mục nào thuộc nhóm nào — gắn nhãn theo nguồn gốc, không theo cảnh báo.")
    dich.write_text(json.dumps(noi_dung, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
    return f"✓ Đã ghi {len(ung_vien)} ứng viên → {dich}"


def danh_gia_bo_vang(p: Path, tai=None) -> tuple[int, list[str]]:
    """Đo báo động giả / bỏ lọt của K1 (nhãn dung_quan_the) và K4 (nhãn dung_chieu) trên các mục
    ĐÃ có nhãn bác sĩ (audit/16 §4). Chưa có nhãn ⇒ mã 2 «chưa đo» — không bao giờ in «đạt»."""
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return 2, [f"⚪ Không đọc được bộ vàng {p}: {e}"]
    cap = (("dung_quan_the", "k1", "K1 quần thể"), ("dung_chieu", "k4", "K4 chiều khuyến cáo"))
    co_nhan = [m for m in d.get("muc") or []
               if any((m.get("nhan_bac_si") or {}).get(k) is not None for k, _, _ in cap)]
    if not co_nhan:
        return 2, ["⚪ Bộ vàng chưa có nhãn nào của bác sĩ (dung_quan_the/dung_chieu) — báo động giả và bỏ lọt "
                   "CHƯA ĐO. Không chuyển K1/K4 sang mức chặn khi chưa có số đo này."]
    tom_tat, loi = tai_tom_tat([x for x in (pmid_cua(m) for m in co_nhan) if x], tai=tai)
    kq_muc = [(m, kiem_muc_nguon(m, tom_tat.get(pmid_cua(m) or ""))) for m in co_nhan]
    dong = [f"Bộ vàng: {len(co_nhan)} mục có nhãn · tải được tóm tắt {len(tom_tat)}"] + [f"  ⚠ {x}" for x in loi]
    do_duoc = False
    for khoa, k, ten in cap:
        dung = [r[k]["muc"] for m, r in kq_muc if (m.get("nhan_bac_si") or {}).get(khoa) is True]
        sai = [r[k]["muc"] for m, r in kq_muc if (m.get("nhan_bac_si") or {}).get(khoa) is False]
        dung_do = [x for x in dung if x in ("con", "can_doc")]
        sai_do = [x for x in sai if x in ("con", "can_doc")]
        do_duoc = do_duoc or bool(dung_do or sai_do)
        dong.append(f"{ten}: bác sĩ nói ĐÚNG {len(dung)} (đo được {len(dung_do)}) · báo động giả "
                    f"{dung_do.count('can_doc')}/{len(dung_do)}  |  bác sĩ nói SAI {len(sai)} (đo được {len(sai_do)}) · "
                    f"bắt được {sai_do.count('can_doc')} · bỏ lọt {sai_do.count('con')}")
    dong.append("Mục ⚪/không áp không tính vào tỉ lệ (chưa đo ≠ khớp). Cỡ mẫu nhỏ ⇒ tỉ lệ còn bất định rộng.")
    return (0 if do_duoc else 2), dong


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm chéo ngữ nghĩa mục apply — K3 (ngoại tuyến) · K1/K4 (--nguon, cần "
                                             "mạng). Mọi phép chỉ CẢNH BÁO.")
    ap.add_argument("dashboard", nargs="?", help="WebDashboard_*.html")
    ap.add_argument("--ban-doc", help="bản đọc HTML")
    ap.add_argument("--word-html", help="bản Word dạng HTML")
    ap.add_argument("--chat", help="tệp văn bản bản tin chat")
    ap.add_argument("--nguon", action="store_true", help="K1/K4: đối chiếu mục apply với tóm tắt nguồn (cần mạng)")
    ap.add_argument("--toan-kho", action="store_true", help="K1/K4 cho mọi dashboard; lưu JSON vào logs/")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ung-vien-bo-vang", action="store_true", help="soạn ứng viên bộ vàng từ dashboard hiện có")
    ap.add_argument("--lam-giau", action="store_true",
                    help="(với --ung-vien-bo-vang) tối đa nửa bộ vàng lấy từ mục K1/K4 báo 🟠 — cần mạng")
    ap.add_argument("--so-muc", type=int, default=20)
    ap.add_argument("--dich", default=str(TEP_BO_VANG))
    ap.add_argument("--ghi-de", action="store_true")
    ap.add_argument("--do-bo-vang", action="store_true", help="đo báo động giả/bỏ lọt K1/K4 trên bộ vàng đã gắn nhãn")
    a = ap.parse_args(argv)

    if a.do_bo_vang:
        rc, dong = danh_gia_bo_vang(Path(a.dich))
        print("\n".join(dong))
        return rc

    if a.ung_vien_bo_vang:
        ds = [Path(a.dashboard)] if a.dashboard else sorted(DASH.glob("WebDashboard_*.html"))
        if not ds:
            print("⚪ Không thấy dashboard nào (EBM-Dashboards/ nằm ngoài git, vắng trên Cloud/CI) — "
                  "chưa soạn được ứng viên.")
            return 2
        uu_tien = None
        if a.lam_giau:
            kqn = kiem_nguon_dashboard(ds)
            if not kqn["tai_duoc"]:
                print("⚪ --lam-giau cần tóm tắt nguồn nhưng không tải được — chưa soạn (không lặng lẽ bỏ làm giàu).")
                return 2
            uu_tien = {(d["dashboard"], d["id"]) for d in kqn["dong"]
                       if "can_doc" in (d["k1"]["muc"], d["k4"]["muc"])}
        uv = soan_ung_vien(ds, a.so_muc, uu_tien)
        if not uv:
            print("⚪ Không có mục decision:'apply' nào đọc được — chưa soạn được ứng viên.")
            return 2
        thong_bao = ghi_ung_vien(uv, Path(a.dich), a.ghi_de, lam_giau=bool(uu_tien))
        print(thong_bao)
        return 0 if thong_bao.startswith("✓") else 2

    if a.toan_kho:
        ds = sorted(DASH.glob("WebDashboard_*.html"))
        if not ds:
            print("⚪ Không thấy dashboard nào — không đo được.")
            return 2
        kqn = kiem_nguon_dashboard(ds)
        in_bao_cao_nguon(kqn, chi_tiet=not a.json)
        luu = REPO / "logs" / f"kiem-cheo-ngu-nghia_toan-kho_{time.strftime('%Y%m%d')}.json"
        try:
            luu.parent.mkdir(parents=True, exist_ok=True)
            luu.write_text(json.dumps(kqn, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"JSON đầy đủ: {luu}")
        except OSError as e:
            print(f"⚠ Không lưu được JSON: {e}")
        if not kqn["tai_duoc"]:
            return 2
        return 1 if (kqn["dem"]["k1"]["can_doc"] or kqn["dem"]["k4"]["can_doc"]) else 0

    if not a.dashboard:
        ap.error("cần đường dẫn dashboard (hoặc --toan-kho / --ung-vien-bo-vang / --do-bo-vang)")
    dash = Path(a.dashboard)
    data = doc_data(dash)
    if data is None:
        print(f"⚪ Không đọc được khối DATA của {dash} — không đo được.")
        return 2
    ma: list[int] = []
    kq = None
    if a.ban_doc or a.word_html or a.chat or not a.nguon:
        nguon = lay_nguon_dieu_kien(data)
        dich = {"ban_doc": _doc_tep(a.ban_doc), "word_html": _doc_tep(a.word_html)}
        if a.chat:
            dich["chat"] = _doc_tep(a.chat)
        kq = doi_chieu(nguon, dich)
        kq["dashboard"] = str(dash)
        kq["so_cau_co_dieu_kien"] = len(nguon)
        if not a.json:
            in_bao_cao(dash, kq)
        ma.append(2 if not any(kq["san_pham"].values()) else (1 if kq["dem"]["can_doc"] else 0))
    kqn = None
    if a.nguon:
        kqn = kiem_nguon_dashboard([dash])
        if not a.json:
            in_bao_cao_nguon(kqn)
        ma.append(2 if not kqn["tai_duoc"] else
                  (1 if (kqn["dem"]["k1"]["can_doc"] or kqn["dem"]["k4"]["can_doc"]) else 0))
    if a.json:
        print(json.dumps(kq if kqn is None else {"k3": kq, "k1_k4": kqn}, ensure_ascii=False, indent=2))
    # Có 🟠 ở bất kỳ phép nào ⇒ 1; phần nào KHÔNG ĐO ĐƯỢC ⇒ 2 (không bao giờ thành 0); còn lại 0.
    return 1 if 1 in ma else (2 if 2 in ma else 0)


if __name__ == "__main__":
    raise SystemExit(main())
