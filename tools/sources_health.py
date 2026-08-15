#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỨC KHOẺ SỔ NGUỒN — LÔ A PHA 4 (15/08/2026).

«Nguồn hỏng im lặng» là một trong bốn nguyên nhân gốc của bỏ sót (LÔ F), nên sổ
nguồn phải có máy đo riêng: nguồn nào sống, lần thành công gần nhất bao giờ,
nguồn nào hỏng quá 2 chu kỳ. Thuần stdlib, chạy được cả hai trình thông dịch.

Ba lớp kiểm, tách bạch (BH08 — không gộp «không biết» với «có vấn đề»):
  • active + access=api  → thăm sống THẬT (HEAD/GET nhỏ, host đã nằm trong danh
    sách egress được phê duyệt — chính là lý do chúng active được).
  • active + access=file → tuổi file so với scan_frequency.
  • not-covered          → KHÔNG thăm (P2/P5): chỉ đếm và in known_gap — khoảng
    trống phải HIỆN RA mỗi lần chạy, không được chìm.

Mã thoát: 0 = mọi nguồn active khoẻ · 1 = có degraded/broken · 2 = sổ hỏng.
`--im-khi-on` cho hook. Kết quả ghi ngược `last_success_at` (chỉ khi THÀNH CÔNG).
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
SO = GOC / "data" / "sources.json"
# Điểm thăm rẻ nhất của từng API (đều đã phê duyệt egress từ trước):
DIEM_THAM = {
    "SRC-001": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json",
    "SRC-002": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json",
    "SRC-004": "https://api.crossref.org/works?rows=0",
    "SRC-005": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMID:1&format=json&pageSize=1",
    "SRC-006": "https://api.fda.gov/drug/label.json?limit=1",
}
CHU_KY_NGAY = {"daily": 1, "weekly": 7, "monthly": 31, "quarterly": 92, "ad-hoc": 3650}


def _tham(url: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ebm-sources-health/1.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return 200 <= r.status < 400
    except (urllib.error.URLError, OSError, ValueError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Sức khoẻ sổ đăng ký nguồn")
    ap.add_argument("--im-khi-on", action="store_true")
    ap.add_argument("--khong-mang", action="store_true", help="bỏ thăm sống, chỉ đọc sổ")
    a = ap.parse_args()

    try:
        du = json.loads(SO.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"🔴 Sổ nguồn hỏng: {exc}")
        return 2

    hom_nay = date.today()
    loi: list[str] = []
    dong: list[str] = []
    for s in du["sources"]:
        if s["status"] == "not-covered":
            continue
        chu_ky = CHU_KY_NGAY.get(s["scan_frequency"], 31)
        # (1) thăm sống nguồn API
        if s["access"] == "api" and s["id"] in DIEM_THAM and not a.khong_mang:
            if _tham(DIEM_THAM[s["id"]]):
                s["last_success_at"] = hom_nay.isoformat()
                if s["status"] != "active":
                    dong.append(f"  ↺ {s['id']} hồi phục → active")
                s["status"] = "active"
            else:
                # hỏng 1 lần = degraded; quá 2 chu kỳ không thành công = broken
                s["status"] = "degraded"
        # (2) nguồn file: tuổi so với chu kỳ
        if s["access"] == "file" and s.get("endpoint_or_url"):
            f = GOC / s["endpoint_or_url"]
            if f.exists():
                tuoi = (datetime.now() - datetime.fromtimestamp(
                    max(p.stat().st_mtime for p in ([f] if f.is_file() else list(f.iterdir()) or [f])))).days
                if tuoi > chu_ky:
                    s["status"] = "degraded"
                    dong.append(f"  ⚠ {s['id']} file {tuoi} ngày tuổi > chu kỳ {chu_ky}ng — chạy làm mới")
            else:
                s["status"] = "broken"
        # (3) quá 2 chu kỳ kể từ last_success → broken (nguồn hỏng không được im)
        ls = s.get("last_success_at")
        if ls:
            try:
                tre = (hom_nay - date.fromisoformat(ls[:10])).days
                if tre > 2 * chu_ky and s["status"] != "active":
                    s["status"] = "broken"
            except ValueError:
                pass
        if s["status"] in ("degraded", "broken"):
            loi.append(f"{s['id']} {s['name'][:50]} → {s['status'].upper()}"
                       f" (thành công gần nhất: {s.get('last_success_at') or 'chưa từng'})")

    du["updated"] = hom_nay.isoformat()
    SO.write_text(json.dumps(du, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    n_active = sum(1 for s in du["sources"] if s["status"] == "active")
    n_nc = sum(1 for s in du["sources"] if s["status"] == "not-covered")
    if loi:
        print(f"🟠 SỔ NGUỒN: {n_active} active · {len(loi)} degraded/broken · {n_nc} not-covered")
        for x in loi:
            print("  ✗ " + x)
        for x in dong:
            print(x)
        print("  → nguồn hỏng = chuyên khoa đó đang MÙ; không được để im (LÔ F nguyên nhân gốc #4)")
        return 1
    if not a.im_khi_on:
        print(f"🟢 SỔ NGUỒN: {n_active} active khoẻ · {n_nc} not-covered (khoảng trống CÓ khai báo):")
        for s in du["sources"]:
            if s["status"] == "not-covered":
                print(f"  ◌ {s['id']} {s['name'][:58]} — {(s.get('known_gap') or '')[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
