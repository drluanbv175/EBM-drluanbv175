#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LÀN ĐỐI CHIẾU OPENALEX — đề xuất #6, bác sĩ duyệt 15/08/2026.

Vì sao: PubMed-lane chỉ thấy thứ đã vào PubMed/MEDLINE. OpenAlex (miễn phí,
không khoá, lớp corpus 250M+ công trình của AnswerThis-class tools) thấy thêm
lớp Crossref-nhanh — bài vừa có DOI, CHƯA/không vào PubMed. Làn này CHỈ ĐỐI
CHIẾU: ứng viên mang nhãn nguồn riêng, dedup theo DOI/PMID với những gì hệ đã
biết, và tuyệt đối không thay PubMed-lane (không đụng cursor/khoá của A2).

Trung thực dữ liệu:
  • Mục KHÔNG có trong sổ/kho → nhãn «⚡ chỉ-OpenAlex» (giá trị riêng của làn).
  • Rút bài: kiểm qua tầng Crossref cho tối đa 10 DOI/chủ đề; mục chưa kiểm ghi
    «chưa kiểm rút bài» — không bao giờ mặc định ok (BH08/27).
  • Ứng viên dừng ở hàng ứng viên — bác sĩ duyệt (Cổng A/B nguyên vẹn).

Dùng:  python3 tools/doi_chieu_openalex.py --topic "Suy tim"
       python3 tools/doi_chieu_openalex.py --toan-bo --ngay 45
Mã thoát: 0 = chạy sạch không ứng viên mới · 1 = CÓ ứng viên cần đọc · 2 = lỗi.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
DASH = GOC / "EBM-Dashboards"
MAILTO = "bsluanbv175@gmail.com"  # polite pool OpenAlex — chỉ email liên hệ, không phải secret
API = "https://api.openalex.org/works"


def _bo_dau(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def _thuat_ngu(q: str) -> str:
    """Truy vấn watchlist (cú pháp PubMed) → chuỗi search thường cho OpenAlex."""
    q = re.sub(r"\[[a-z ]+\]", " ", q)          # bỏ [ti]/[pt]/[ptyp]…
    q = re.sub(r"\b(AND|OR|NOT)\b", " ", q)
    q = re.sub(r"[()\"]", " ", q)
    return re.sub(r"\s+", " ", q).strip()[:160]


def _da_biet() -> set[str]:
    """Mọi định danh hệ ĐÃ biết (sổ xác minh + kho dashboard) — để dedup."""
    biet: set[str] = set()
    try:
        so = json.loads((DASH / ".so-xac-minh-nguon.json").read_text(encoding="utf-8"))
        for k in so.get("muc", {}):
            biet.add(k.split(":", 1)[-1].lower())
    except (OSError, ValueError):
        pass
    for f in DASH.glob("WebDashboard_*.html"):
        try:
            nd = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        biet.update(m.lower() for m in re.findall(r"10\.\d{4,9}/[^\s'\"<>]+", nd))
        biet.update(re.findall(r"pmid['\"]?\s*:\s*['\"](\d{6,9})", nd, re.I))
    return biet


def _goi(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": f"EBM-doi-chieu/1.0 ({MAILTO})"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _nap_rut_bai():
    """Tầng Crossref updated-by (stdlib) — primitive ĐÚNG cho tra-theo-DOI.

    Bài học 15/08 (vòng «tiếp tục hoàn thiện»): bản đầu gọi nhầm
    `so_xac_minh_nguon.kiem_rut_bai_theo_doi` — đó là hàm NỘI BỘ ghi sổ, 3 tham
    số — và nhãn «lỗi mạng» dán cho mọi exception đã CHE một TypeError. Lỗi sai
    hợp đồng mà đọc thành lỗi mạng là đúng lớp «không biết bị báo thành thứ
    khác» (BH08/BH34).
    """
    sys.path.insert(0, str(GOC / "medical-ebm-automation"))
    try:
        from app.sources.crossref_retraction import CrossrefRetraction  # noqa: PLC0415
        return CrossrefRetraction().check
    except Exception:  # noqa: BLE001
        return None


def quet_chu_de(t: dict, ngay: int, toi_da: int, biet: set[str], kiem_doi) -> list[str]:
    tu = _thuat_ngu(t.get("query") or t["topic"])
    tu_ngay = (date.today() - timedelta(days=ngay)).isoformat()
    u = (f"{API}?search={urllib.parse.quote(tu)}"
         f"&filter=from_publication_date:{tu_ngay},type:article|review"
         f"&per-page={toi_da}&sort=publication_date:desc&mailto={MAILTO}")
    ket = _goi(u)
    dong: list[str] = []
    da_kiem_rut = 0
    for w in ket.get("results", []):
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        pmid = ((w.get("ids") or {}).get("pmid") or "").rsplit("/", 1)[-1]
        if (doi and doi in biet) or (pmid and pmid in biet):
            continue  # hệ đã biết — dedup, không trình lại
        chi_oa = "" if pmid else " · **⚡ chỉ-OpenAlex (chưa/không vào PubMed)**"
        rut = "chưa kiểm rút bài"
        if doi and kiem_doi and da_kiem_rut < 10:
            da_kiem_rut += 1
            try:
                kq = kiem_doi([doi]) or {}
                tt = (kq.get(doi) or {}).get("status", "")
                rut = ("🔴 " + tt) if tt in ("retracted", "expression_of_concern") \
                    else ("ok (Crossref)" if tt == "ok" else "chưa kiểm rút bài")
            except Exception as exc:  # noqa: BLE001 — không giết cả lượt, nhưng
                # nhãn phải nói ĐÚNG loại lỗi — «lỗi mạng» từng che một TypeError.
                rut = f"chưa kiểm rút bài ({type(exc).__name__})"
        venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "")
        dong.append(f"- **{w.get('publication_date','?')}** · {w.get('type','?')} · "
                    f"{venue[:40]} · DOI {doi or '—'} · PMID {pmid or '—'}{chi_oa}\n"
                    f"  - {(w.get('display_name') or '')[:150]}\n  - rút bài: {rut}")
        time.sleep(0.15)
    return dong


def main() -> int:
    ap = argparse.ArgumentParser(description="Làn đối chiếu OpenAlex (đề xuất #6)")
    ap.add_argument("--topic", help="một chủ đề watchlist (khớp không dấu)")
    ap.add_argument("--toan-bo", action="store_true")
    ap.add_argument("--ngay", type=int, default=45)
    ap.add_argument("--max", type=int, default=25, dest="toi_da")
    a = ap.parse_args()
    try:
        w = json.loads((DASH / "watchlist.json").read_text(encoding="utf-8"))["topics"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"🔴 watchlist hỏng: {exc}")
        return 2
    if a.topic:
        khoa = _bo_dau(a.topic)
        w = [t for t in w if khoa in _bo_dau(t["topic"]) or _bo_dau(t["topic"]) in khoa]
        if not w:
            print(f"🔴 --topic không khớp chủ đề nào: {a.topic}")
            return 2
    elif not a.toan_bo:
        print("Cần --topic hoặc --toan-bo")
        return 2

    biet = _da_biet()
    kiem_doi = _nap_rut_bai()
    print(f"Đối chiếu OpenAlex — {len(w)} chủ đề · cửa sổ {a.ngay} ngày · "
          f"đã biết {len(biet)} định danh (dedup)")
    khoi: list[str] = []
    tong = 0
    for t in w:
        try:
            dong = quet_chu_de(t, a.ngay, a.toi_da, biet, kiem_doi)
        except Exception as exc:  # noqa: BLE001
            print(f"  ✗ {t['topic'][:40]}: LỖI {exc} — chủ đề này CHƯA đối chiếu được")
            continue
        print(f"  {t['topic'][:44]:<46} +{len(dong)} ứng viên NGOÀI những gì hệ đã biết")
        if dong:
            tong += len(dong)
            khoi.append(f"## {t['topic']}\n\n" + "\n".join(dong))
    if khoi:
        ra = DASH / "surveillance" / f"openalex-{date.today().isoformat()}.md"
        ra.parent.mkdir(exist_ok=True)
        ra.write_text(
            f"# ĐỐI CHIẾU OPENALEX — {date.today().isoformat()} (làn #6, bác sĩ duyệt 15/08)\n\n"
            "> Làn ĐỐI CHIẾU bên cạnh PubMed-lane — dedup với sổ/kho; «⚡ chỉ-OpenAlex» là\n"
            "> giá trị riêng của làn (bài chưa/không vào PubMed). Ứng viên dừng ở hàng ứng\n"
            "> viên; «chưa kiểm rút bài» đúng nghĩa đen. Cần bác sĩ kiểm chứng.\n\n"
            + "\n\n".join(khoi) + "\n", encoding="utf-8")
        print(f"→ {ra.relative_to(GOC)} ({tong} ứng viên)")
    return 1 if tong else 0


if __name__ == "__main__":
    raise SystemExit(main())
