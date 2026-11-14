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
   SO THEO TỪNG MỤC (14/11/2026): với sản phẩm in theo từng mục (Word — «ITEM-xx. <tiêu đề>»),
   cụm lấy từ `action` của một mục chỉ được tìm trong ĐOẠN của chính mục đó — đoạn mở ở mốc
   «ITEM-xx. <tiêu đề>», đóng ở mốc của mục kế tiếp. Trước đây cụm được tìm trong cả tài liệu, nên cụm
   rụng khỏi mục A mà còn ở mục B (cụm chung như «khi eGFR ≥ 30») vẫn ✓. Bản đọc (sắp lại theo chủ
   đề, không in định danh) hoặc mục không định vị được ⇒ so cả tài liệu như cũ, ghi
   `pham_vi: tai_lieu`. Cụm của `summary.*` luôn so cả tài liệu.

BA MỨC — cố ý KHÔNG có mức «SAI»
================================
  ✓ CÒN      — cụm điều kiện có mặt nguyên văn trong sản phẩm đó.
  🟠 CẦN ĐỌC — sản phẩm có tồn tại nhưng không thấy cụm điều kiện nguyên văn (có thể bị viết
               lại bằng lời khác — máy không hiểu diễn đạt lại, nên chỉ nhắc ĐỌC LẠI).
  ⚪ CHƯA KIỂM — không có sản phẩm để đối chiếu.
Công cụ CHỈ BÁO: không sửa dashboard, không đổi `decision`, không chặn xuất.

Dùng:
    python tools/kiem_cheo_ngu_nghia.py DASH.html --ban-doc B.html --word-html W.html [--chat T.txt]
    python tools/kiem_cheo_ngu_nghia.py DASH.html --json
    python tools/kiem_cheo_ngu_nghia.py --ung-vien-bo-vang [--so-muc 20]   # soạn ứng viên bộ vàng

Mã thoát: 0 = không có 🟠 · 1 = có cụm cần đọc lại · 2 = không đo được (không đọc được DATA,
không có sản phẩm nào để đối chiếu). «Không đo được» không bao giờ là 0.
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


# Thẻ HTML THẬT (vá 14/11/2026, đo ở quality/eval/kiem-cheo-ngu-nghia/do-nhay-dot-bien-20261114): «<» liền tên thẻ (chữ
# cái, có thể sau «/», «!», «?») và tên thẻ kết thúc bằng khoảng trắng, «/» hoặc «>»; chú thích «<!-- … -->». Trước đây mọi
# đoạn «<…>» đều bị coi là thẻ ⇒ trong văn bản THUẦN «<» so sánh («risk < 3 %», «p<0.05», «eGFR <30») xoá mất chữ tới dấu «>»
# kế tiếp (7/298 tóm tắt bị cắt, có câu «not recommended» mà K4 cần thấy).
_THE_HTML = re.compile(r"<!--.*?-->|<[!?]?/?[a-zA-Z][a-zA-Z0-9:-]*(?:\s[^<>]*)?/?>", re.S)
# Văn bản THUẦN (tóm tắt PubMed dạng text): chỉ bỏ thẻ định dạng nội dòng mà bản XML/HTML của PubMed có thể mang theo.
_THE_DINH_DANG = re.compile(r"</?(?:i|b|u|em|strong|sup|sub|sc|span|p|br|mml:[a-z]+)(?:\s[^<>]*)?/?>", re.I)


def chuan_hoa(t: str, html: bool = True) -> str:
    """Chữ thường + NFC + bỏ thẻ HTML/entity + gộp khoảng trắng + thống nhất gạch/nháy.

    html=True (DATA, bản đọc, Word HTML): bỏ mọi thẻ HTML THẬT. html=False (tóm tắt nguồn — văn bản thuần): chỉ bỏ thẻ định
    dạng nội dòng, mọi «<»/«>» khác là dấu so sánh và được GIỮ."""
    t = (_THE_HTML if html else _THE_DINH_DANG).sub(" ", t or "")
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
    """[{vi_tri, van_ban, cum:[…], ma_muc?}] — chỉ giữ câu CÓ điều kiện; câu của một mục mang `ma_muc` (id mục)."""
    ra: list[dict] = []
    sm = data.get("summary") or {}

    def them(vi_tri: str, v, ma_muc: str | None = None) -> None:
        if isinstance(v, str) and v.strip():
            cum = trich_cum_dieu_kien(v)
            if cum:
                ra.append({"vi_tri": vi_tri, "van_ban": v, "cum": cum, **({"ma_muc": ma_muc} if ma_muc else {})})

    them("summary.conclusion", sm.get("conclusion"))
    for k in ("doNow", "dontDo"):
        for i, v in enumerate(sm.get(k) or []):
            them(f"summary.{k}[{i}]", v)
    for it in data.get("items") or []:
        if isinstance(it, dict) and it.get("decision") == "apply":
            them(f"{it.get('id') or '?'}.action", it.get("action"), str(it.get("id") or "") or None)
    return ra


# ── So theo TỪNG MỤC (14/11/2026) ──────────────────────────────────────────────────────────────
_DAU_TIEU_DE = 40   # số ký tự đầu của tiêu đề dùng làm mốc (bản xuất có thể cắt/ngắt dòng tiêu đề dài)


def neo_muc(data: dict) -> list[dict]:
    """[{id, tieu_de}] cho MỌI mục theo thứ tự DATA (kể cả consider/notyet — bản xuất in cả chúng, chúng cũng là mốc ĐÓNG
    đoạn của mục đứng trước)."""
    ra = []
    for it in data.get("items") or []:
        if isinstance(it, dict):
            ra.append({"id": str(it.get("id") or ""), "tieu_de": chuan_hoa(str(it.get("title") or ""))})
    return ra


def _mau_dinh_danh(ma: str) -> re.Pattern:
    return re.compile(rf"(?<![\w-]){re.escape(ma.lower())}(?!\d)")


def _moc_muc(vb: str, n: dict) -> list[int]:
    """Vị trí «ITEM-xx. <tiêu đề>» — định danh đi LIỀN tiêu đề của chính mục (Word in mỗi mục như vậy). Định danh đứng một mình
    («(item-47, item-48)» trong bản đọc) là TRÍCH DẪN chéo, không phải đầu mục ⇒ không tính."""
    if not (n.get("id") and n.get("tieu_de")):
        return []
    dau = re.escape(n["tieu_de"][:_DAU_TIEU_DE].strip())
    return [m.start() for m in re.finditer(rf"(?<![\w-]){re.escape(n['id'].lower())}(?!\d)\W{{0,4}}{dau}", vb)]


def co_cau_truc_muc(vb: str, neo: list[dict]) -> bool:
    """Sản phẩm in theo TỪNG MỤC khi ít nhất một nửa số mục có mốc «ITEM-xx. <tiêu đề>». Bản đọc sắp lại nội dung theo chủ đề
    (cờ đỏ, việc cần làm…) và chỉ trích định danh mục trong ngoặc ⇒ cắt theo mục ở đó sinh báo động giả (đo 14/11/2026 trên 115
    dashboard: mọi dòng chuyển ✓→🟠 khi cắt theo tiêu đề đơn thuần đều ở bản đọc, Word 0) ⇒ so cả tài liệu."""
    co_ma = [n for n in neo if n.get("id")]
    return bool(co_ma) and sum(1 for n in co_ma if _moc_muc(vb, n)) * 2 >= len(co_ma)


# Tiêu đề phần ĐUÔI mà EBM-Dashboards/tools/build_dashboard_docx.py in ngay sau mục cuối (add_part_heading «NGUỒN VÀ LIÊM
# CHÍNH DỮ LIỆU»). Đo 14/11/2026 trên 303 Word HTML thật: có mặt ở 303/303, đúng một lần, luôn SAU mốc mục cuối, không lần nào
# trước đó. «Tài liệu tham khảo»/«Phụ lục» KHÔNG dùng được làm mốc: chúng nằm trong bảng của từng mục (299 và 29 tệp).
_MOC_KET_THUC = ("nguồn và liêm chính dữ liệu",)


def doan_cua_muc(vb: str, neo: list[dict]) -> dict[str, list[tuple[int, int]]]:
    """{id mục: [(đầu, cuối), …]} trên văn bản sản phẩm ĐÃ chuẩn hoá. Mỗi mốc «ITEM-xx. <tiêu đề>» mở một đoạn; đoạn đóng ở
    mốc kế tiếp của một mục KHÁC. Đoạn của mục CUỐI đóng ở tiêu đề phần đuôi đầu tiên sau nó (`_MOC_KET_THUC`, sửa sau thẩm
    định PR #359 — trước đây nó kéo tới hết tài liệu, nên cụm rụng khỏi mục cuối mà còn ở phần đuôi vẫn ✓). GIỚI HẠN: sản
    phẩm không có tiêu đề đuôi đó (bộ dựng khác, tệp cũ) thì đoạn mục cuối vẫn kéo tới cuối tài liệu. Mục không có mốc, hoặc
    sản phẩm không in theo từng mục (`co_cau_truc_muc`) ⇒ vắng trong kết quả (người gọi so cả tài liệu)."""
    if not co_cau_truc_muc(vb, neo):
        return {}
    theo_vi_tri: dict[int, set[str]] = {}
    for n in neo:
        for p in _moc_muc(vb, n):
            theo_vi_tri.setdefault(p, set()).add(n["id"])
    moc = sorted(theo_vi_tri.items())
    if not moc:
        return {}
    cuoi = min((i for i in (vb.find(x, moc[-1][0]) for x in _MOC_KET_THUC) if i >= 0), default=len(vb))
    ra: dict[str, list[tuple[int, int]]] = {}
    for i, (p, ids) in enumerate(moc):
        het = next((q for q, ids2 in moc[i + 1:] if ids2 - ids), cuoi)
        for ma in ids:
            ra.setdefault(ma, []).append((p, het))
    return ra


def doi_chieu(nguon: list[dict], dich: dict[str, str | None], neo: list[dict] | None = None) -> dict:
    """dich: {tên sản phẩm: văn bản đã đọc | None (không có)}. neo (từ `neo_muc`) ⇒ cụm của một mục chỉ tìm trong ĐOẠN của
    mục đó; không có neo hoặc không định vị được mục ⇒ tìm trong cả tài liệu (pham_vi «tai_lieu»)."""
    da_chuan = {k: (chuan_hoa(v) if v is not None else None) for k, v in dich.items()}
    doan = {k: (doan_cua_muc(vb, neo) if (vb is not None and neo) else {}) for k, vb in da_chuan.items()}
    dong = []
    dem = {"con": 0, "can_doc": 0, "chua_kiem": 0}
    for n in nguon:
        ma = n.get("ma_muc")
        for c in n["cum"]:
            kq, pham_vi = {}, {}
            for ten, vb in da_chuan.items():
                if vb is None:
                    kq[ten] = "chua_kiem"
                    dem[kq[ten]] += 1
                    continue
                khoang = doan[ten].get(ma) if ma else None
                if khoang:
                    pham_vi[ten] = "muc"
                    thay = any(c in vb[a:b] for a, b in khoang)
                else:
                    pham_vi[ten] = "tai_lieu"
                    thay = c in vb
                kq[ten] = "con" if thay else "can_doc"
                dem[kq[ten]] += 1
            dong.append({"vi_tri": n["vi_tri"], "cum": c, "ket_qua": kq, "pham_vi": pham_vi})
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
        ca_tl = [k for k, v in (d.get("pham_vi") or {}).items() if v == "tai_lieu" and d["vi_tri"].endswith(".action")]
        print(f"  {dau}  [{d['vi_tri']}] «{d['cum']}»"
              + (f" (không định vị được mục trong {', '.join(ca_tl)} — so cả tài liệu)" if ca_tl else ""))
    e = kq["dem"]
    print(f"Tổng: {e['con']} ✓ còn · {e['can_doc']} 🟠 cần đọc lại · {e['chua_kiem']} ⚪ chưa kiểm")
    if e["can_doc"]:
        print("🟠 = không thấy NGUYÊN VĂN cụm điều kiện trong sản phẩm đó. Có thể đã bị viết lại "
              "bằng lời khác — đọc lại, KHÔNG phải kết luận «sai». Công cụ chỉ cảnh báo.")


# ── Ứng viên bộ vàng (bác sĩ gắn nhãn; máy KHÔNG gắn) ─────────────────────────────
_NHAN_TRONG = {"dung_quan_the": None, "dung_chieu": None, "du_dieu_kien": None, "ghi_chu": None}


def soan_ung_vien(dashboards: list[Path], so_muc: int) -> list[dict]:
    """Rút mục apply theo vòng tròn giữa các dashboard để bộ vàng đa dạng chủ đề."""
    theo_dash: list[list[dict]] = []
    for f in dashboards:
        data = doc_data(f)
        if not data:
            continue
        muc = []
        for it in data.get("items") or []:
            if isinstance(it, dict) and it.get("decision") == "apply" and (it.get("pmid") or it.get("doi")):
                muc.append({
                    "dashboard": f.name, "id": it.get("id"), "title": it.get("title"),
                    "population": it.get("population"), "action": it.get("action"),
                    "pmid": it.get("pmid"), "doi": it.get("doi"), "gradeLevel": it.get("gradeLevel"),
                    "co_dieu_kien": bool(trich_cum_dieu_kien(it.get("action") or "")),
                    "nhan_bac_si": dict(_NHAN_TRONG),
                })
        if muc:
            theo_dash.append(muc)
    ra: list[dict] = []
    while len(ra) < so_muc and theo_dash:
        for nhom in theo_dash:
            if len(ra) >= so_muc:
                break
            ra.append(nhom.pop(0))
        theo_dash = [n for n in theo_dash if n]
    return ra


def _da_co_nhan(p: Path) -> bool:
    try:
        cu = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return any(v is not None for m in cu.get("muc") or [] for v in (m.get("nhan_bac_si") or {}).values())


def ghi_ung_vien(ung_vien: list[dict], dich: Path, ghi_de: bool) -> str:
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
    dich.write_text(json.dumps(noi_dung, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
    return f"✓ Đã ghi {len(ung_vien)} ứng viên → {dich}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="K3 — kiểm giữ mệnh đề điều kiện khi xuất (chỉ cảnh báo)")
    ap.add_argument("dashboard", nargs="?", help="WebDashboard_*.html")
    ap.add_argument("--ban-doc", help="bản đọc HTML")
    ap.add_argument("--word-html", help="bản Word dạng HTML")
    ap.add_argument("--chat", help="tệp văn bản bản tin chat")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ung-vien-bo-vang", action="store_true", help="soạn ứng viên bộ vàng từ dashboard hiện có")
    ap.add_argument("--so-muc", type=int, default=20)
    ap.add_argument("--dich", default=str(TEP_BO_VANG))
    ap.add_argument("--ghi-de", action="store_true")
    a = ap.parse_args(argv)

    if a.ung_vien_bo_vang:
        ds = [Path(a.dashboard)] if a.dashboard else sorted(DASH.glob("WebDashboard_*.html"))
        if not ds:
            print("⚪ Không thấy dashboard nào (EBM-Dashboards/ nằm ngoài git, vắng trên Cloud/CI) — "
                  "chưa soạn được ứng viên.")
            return 2
        uv = soan_ung_vien(ds, a.so_muc)
        if not uv:
            print("⚪ Không có mục decision:'apply' nào đọc được — chưa soạn được ứng viên.")
            return 2
        thong_bao = ghi_ung_vien(uv, Path(a.dich), a.ghi_de)
        print(thong_bao)
        return 0 if thong_bao.startswith("✓") else 2

    if not a.dashboard:
        ap.error("cần đường dẫn dashboard (hoặc --ung-vien-bo-vang)")
    dash = Path(a.dashboard)
    data = doc_data(dash)
    if data is None:
        print(f"⚪ Không đọc được khối DATA của {dash} — không đo được.")
        return 2
    nguon = lay_nguon_dieu_kien(data)
    dich = {"ban_doc": _doc_tep(a.ban_doc), "word_html": _doc_tep(a.word_html)}
    if a.chat:
        dich["chat"] = _doc_tep(a.chat)
    kq = doi_chieu(nguon, dich, neo_muc(data))
    kq["dashboard"] = str(dash)
    kq["so_cau_co_dieu_kien"] = len(nguon)
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=2))
    else:
        in_bao_cao(dash, kq)
    if not any(kq["san_pham"].values()):
        return 2
    return 1 if kq["dem"]["can_doc"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
