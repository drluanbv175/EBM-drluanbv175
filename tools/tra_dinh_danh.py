#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRA ĐỊNH DANH THƯ MỤC — sinh dòng Vancouver CHUẨN từ PubMed, không đoán (20/08/2026).

VÌ SAO CÓ
=========
19/08 tối, khi tự tay điền tập/số/trang cho mục Nguồn, **trí nhớ sai 2/7 trường**
(Am J Hematol 98(7):E165–E167 bị ghi 98(8):E184; Diabetes Obes Metab 24(12) ghi
24(11)) — máy tra esummary mới bắt được. Skill v1.2 vì thế cấm điền từ trí nhớ.
Tool này là CÁCH THI HÀNH lệnh cấm đó: một lệnh ra đúng dòng Vancouver.

Thêm `--abstract` để lấy TÓM TẮT NGUYÊN VĂN — dùng khi cần trích con số: chỉ được
trích những gì có trong văn bản này, không nhớ hộ nguồn.

Dùng:  python3 tools/tra_dinh_danh.py --pmids 38490803,35081280
       python3 tools/tra_dinh_danh.py --pmids 35081280 --abstract
       python3 tools/tra_dinh_danh.py --pmids ... --json
Mã thoát: 0 · 1 thiếu đối số · 2 không tra được bản ghi nào (KHÔNG tự bịa dòng trích
dẫn thay thế). Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _email() -> str:
    import os
    e = os.environ.get("NCBI_EMAIL")
    if e:
        return e
    sec = Path.home() / ".ebm-secrets" / "medical-ebm-automation.env"
    if sec.exists():
        for d in sec.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*NCBI_EMAIL\s*=\s*(\S+)", d)
            if m:
                return m.group(1).strip("'\"")
    return ""


def _tai(url: str) -> bytes:
    return urllib.request.urlopen(url, timeout=25).read()


def ban_ghi(pmids: list[str]) -> list[dict]:
    ds = ",".join(pmids)
    mail = _email()
    hau = f"&email={mail}" if mail else ""
    js = json.loads(_tai(f"{EUTILS}/esummary.fcgi?db=pubmed&retmode=json&id={ds}{hau}"))["result"]
    ra = []
    for pm in pmids:
        r = js.get(pm)
        if not r or "title" not in r:
            ra.append({"pmid": pm, "loi": "không tra được bản ghi"})
            continue
        tac_gia = [a["name"] for a in r.get("authors", []) if a.get("authtype") == "Author"]
        if len(tac_gia) > 3:
            ten_tg = ", ".join(tac_gia[:3]) + ", và cs."
        elif tac_gia:
            ten_tg = ", ".join(tac_gia) + "."
        else:
            ten_tg = ""
        doi = next((x["value"] for x in r.get("articleids", [])
                    if x.get("idtype") == "doi"), "")
        nam = (r.get("pubdate") or "")[:4]
        tap, so, tr = r.get("volume", ""), r.get("issue", ""), r.get("pages", "")
        vt = f"{nam}"
        if tap:
            vt += f";{tap}" + (f"({so})" if so else "")
            if tr:
                vt += f":{tr}"
        van = (f"{ten_tg} {r['title'].rstrip('.')}. *{r['source']}* {vt}."
               f" PMID {pm}" + (f" · doi:{doi}" if doi else "")).strip()
        ra.append({"pmid": pm, "tieu_de": r["title"], "tap_chi": r["source"],
                   "nam": nam, "tap": tap, "so": so, "trang": tr, "doi": doi,
                   "vancouver": van})
    return ra


def tom_tat(pmids: list[str]) -> dict[str, str]:
    ds = ",".join(pmids)
    vb = _tai(f"{EUTILS}/efetch.fcgi?db=pubmed&rettype=abstract&retmode=text&id={ds}").decode(
        "utf-8", errors="replace")
    ra: dict[str, str] = {}
    for doan in vb.split("\n\n\n"):
        m = re.search(r"PMID: (\d+)", doan)
        if m:
            ra[m.group(1)] = re.sub(r"\s+", " ", doan).strip()
    return ra


def main() -> int:
    ap = argparse.ArgumentParser(description="Tra định danh thư mục chuẩn Vancouver từ PubMed")
    ap.add_argument("--pmids", required=True, help="PMID cách nhau bởi dấu phẩy/khoảng trắng")
    ap.add_argument("--abstract", action="store_true", help="in tóm tắt nguyên văn kèm theo")
    ap.add_argument("--json", action="store_true", help="xuất JSON máy đọc")
    a = ap.parse_args()
    pmids = [x for x in re.split(r"[,\s]+", a.pmids.strip()) if re.fullmatch(r"\d{6,9}", x)]
    if not pmids:
        print("✗ Không có PMID hợp lệ.")
        return 1
    try:
        bg = ban_ghi(pmids)
    except Exception as exc:  # noqa: BLE001
        print(f"🔴 Không gọi được PubMed ({type(exc).__name__}) — KHÔNG tự dựng dòng "
              "trích dẫn từ trí nhớ; thử lại hoặc để «chưa tra được».")
        return 2
    tt = {}
    if a.abstract:
        try:
            tt = tom_tat(pmids)
        except Exception as exc:  # noqa: BLE001
            print(f"⚠ Không lấy được tóm tắt ({type(exc).__name__}) — phần định danh vẫn dùng được.")
    if a.json:
        for r in bg:
            if a.abstract:
                r["tom_tat"] = tt.get(r["pmid"], "")
        print(json.dumps(bg, ensure_ascii=False, indent=2))
        return 0
    for r in bg:
        if r.get("loi"):
            print(f"PMID {r['pmid']}: 🔴 {r['loi']} — KHÔNG trích khi chưa tra được.")
            continue
        print(f"\n■ PMID {r['pmid']}")
        print(f"  {r['vancouver']}")
        if a.abstract:
            vb = tt.get(r["pmid"], "")
            print(f"  ── TÓM TẮT NGUYÊN VĂN ({len(vb.split())} từ) ──")
            print("  " + (vb if vb else "(không lấy được tóm tắt)"))
    print("\nChỉ trích số liệu CÓ TRONG văn bản trên. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
